from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import timedelta
import uvicorn
from dotenv import load_dotenv
import os
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import User, SymptomQuery, create_tables, get_db
from auth import verify_password, get_password_hash, create_access_token, decode_access_token
from groq import Groq

# Load environment variables
load_dotenv()

# Create tables
create_tables()

app = FastAPI(
    title="Healthcare Symptom Checker API (Rewrite)",
    description="Strict AI Symptom Checker",
    version="2.0.0"
)

# Initialize OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
    model = "llama-3.3-70b-versatile"

# Pydantic models
class SymptomRequest(BaseModel):
    symptoms: str

class StructuredSymptomResponse(BaseModel):
    summary: str
    possible_common_causes: List[str]
    severity_estimate: str
    self_care_tips: List[str]
    red_flags: List[str]
    consultation_timing: str
    disclaimer: str

class QueryHistoryResponse(BaseModel):
    id: int
    symptoms: str
    created_at: str
    summary: str
    possible_common_causes: List[str]
    severity_estimate: str
    self_care_tips: List[str]
    red_flags: List[str]

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

import re

# ... (Previous imports)

# ... (Models)

# Auth Helpers
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Try finding by username first (legacy) then email
    user = db.query(User).filter(User.username == username).first()
    if not user:
         user = db.query(User).filter(User.email == username).first()
         
    if user is None:
        raise credentials_exception
    return user

# Endpoints
@app.post("/register/", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Validate Email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    # 2. Validate Password
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    # 3. Check Email Uniqueness (Username can be duplicate)
    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(id=new_user.id, username=new_user.username, email=new_user.email)

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate using Email (passed as username field in OAuth2 form)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Store email in token subject for consistency, or username. 
    # Let's store username to keep "Welcome (username)" easy, or store email and fetch user.
    # Storing username in sub is standard for this app so far.
    access_token = create_access_token(data={"sub": user.username}) 
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/check_symptoms/", response_model=StructuredSymptomResponse)
async def check_symptoms(request: SymptomRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not client:
        raise HTTPException(status_code=500, detail="LLM Service Unavailable: Missing API Key.")

    prompt = f"""
    You are an AI-powered Healthcare Symptom Checker designed for informational and educational purposes only.
    You are NOT a medical professional, and you must NEVER provide a diagnosis, medication names, or treatment dosage.

    Your role is to analyze the user's symptoms: "{request.symptoms}"
    
    Provide possible common explanations, supportive guidance, and safe recommendations while maintaining a responsible tone.

    Every response must ALWAYS follow the exact structure below, regardless of the input:

    ----------------------------------------------------
    RESPONSE TEMPLATE (STRICT FORMAT):

    📝 Summary:
    Rewrite the user’s symptoms in simple, clear language.

    🔍 Possible Common Causes (not a diagnosis):
    List 2–5 possible common causes. Use phrasing like:
    - "This may be related to..."
    - "Sometimes symptoms like this are associated with..."
    Do NOT sound certain. Avoid any definitive diagnosis.

    🎯 Severity Estimate:
    Classify as one of the following, based on impact on daily activities:
    - Low Concern
    - Moderate Concern
    - High Concern

    💡 Helpful Self-Care Tips:
    Suggest only safe, general, non-medical advice such as:
    - Rest
    - Warm compress
    - Gentle stretching
    - Good hydration
    - Ergonomic posture
    Avoid medication, prescriptions, or exercises that could worsen injury.

    🚩 Seek Medical Care If You Notice:
    Provide 3–6 red flag warnings relevant to symptoms.
    Examples:
    - Numbness or weakness
    - Difficulty breathing
    - Severe or worsening pain
    - Loss of bladder/bowel control

    📅 When to Consider Consultation:
    Give a general timeframe such as:
    - If symptoms last more than a few days
    - If symptoms interfere with walking or daily life
    - If symptoms suddenly worsen

    ⚠️ Disclaimer (MANDATORY):
    “This response is for educational purposes only and is not a medical diagnosis or professional medical advice. If you are worried about your symptoms or they worsen, please consult a licensed healthcare professional.”
    ----------------------------------------------------

    ADDITIONAL RULES:
    - NEVER claim certainty.
    - NEVER mention medications, side effects, or treatment steps.
    - NEVER ask for personal information.
    - Maintain a calm, helpful, and non-alarming tone.
    - If symptoms indicate any emergency pattern, classify severity as HIGH and politely encourage urgent professional help.

    Return the response as a valid JSON object matching this structure:
    {{
        "summary": "...",
        "possible_common_causes": ["...", "..."],
        "severity_estimate": "...",
        "self_care_tips": ["...", "..."],
        "red_flags": ["...", "..."],
        "consultation_timing": "...",
        "disclaimer": "..."
    }}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        response_content = chat_completion.choices[0].message.content
        data = json.loads(response_content)
        
        response_obj = StructuredSymptomResponse(**data)
        
        # Save to DB
        query = SymptomQuery(
            user_id=current_user.id,
            symptoms=request.symptoms,
            response=response_content
        )
        db.add(query)
        db.commit()
        
        return response_obj
        
    except Exception as e:
        print(f"LLM Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing symptoms: {str(e)}")

@app.get("/history/", response_model=List[QueryHistoryResponse])
async def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    queries = db.query(SymptomQuery).filter(SymptomQuery.user_id == current_user.id).order_by(SymptomQuery.created_at.desc()).limit(20).all()
    history = []
    for q in queries:
        try:
            data = json.loads(q.response)
            # Default values if parsing fails or old data
            summary = data.get("summary", "Analysis available")
            causes = data.get("possible_common_causes", [])
            severity = data.get("severity_estimate", "Unknown")
            tips = data.get("self_care_tips", [])
            red_flags = data.get("red_flags", [])
            
            # Fallback for old data format
            if not summary and "possible_conditions" in data:
                 first_cond = data.get("possible_conditions", [{}])[0].get("condition", "Unknown")
                 summary = f"Possible: {first_cond}"

        except:
            summary = "Analysis available"
            causes = []
            severity = "Unknown"
            tips = []
            red_flags = []
            
        history.append(QueryHistoryResponse(
            id=q.id,
            symptoms=q.symptoms,
            created_at=q.created_at.strftime("%d %b %Y"), # Formatted date
            summary=summary,
            possible_common_causes=causes,
            severity_estimate=severity,
            self_care_tips=tips,
            red_flags=red_flags
        ))
    return history

@app.delete("/history/{query_id}")
async def delete_history(query_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(SymptomQuery).filter(SymptomQuery.id == query_id, SymptomQuery.user_id == current_user.id).first()
    if not query:
        raise HTTPException(status_code=404, detail="History item not found")
    
    db.delete(query)
    db.commit()
    return {"message": "Deleted successfully"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 9002))
    uvicorn.run(app, host="127.0.0.1", port=port)
