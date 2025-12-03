from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv
import os
import google.generativeai as genai
from functools import lru_cache
import json
from sqlalchemy.orm import Session
from models import SymptomQuery, create_tables, get_db

# Load environment variables
load_dotenv()

# Create tables
create_tables()

app = FastAPI(
    title="Healthcare Symptom Checker API",
    description="API for checking symptoms and getting possible conditions",
    version="1.0.0"
)

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

class SymptomRequest(BaseModel):
    symptoms: str

class ConditionResponse(BaseModel):
    condition: str
    description: str
    likelihood: str  # Low, Medium, High
    next_steps: List[str]

class SymptomCheckResponse(BaseModel):
    symptoms: str
    possible_conditions: List[ConditionResponse]
    disclaimer: str

class QueryHistoryResponse(BaseModel):
    id: int
    symptoms: str
    created_at: str

def get_llm_response(symptoms: str) -> SymptomCheckResponse:
    """
    Get response from LLM for symptom analysis
    """
    if not model:
        # Fallback to mock data if no API key is provided
        return get_mock_response(symptoms)
    
    prompt = f"""
    Based on these symptoms: "{symptoms}", suggest possible medical conditions and next steps.
    
    Please provide your response in the following JSON format:
    {{
        "possible_conditions": [
            {{
                "condition": "Medical condition name",
                "description": "Brief description of the condition",
                "likelihood": "High/Medium/Low",
                "next_steps": ["Step 1", "Step 2", "Step 3"]
            }}
        ]
    }}
    
    Guidelines:
    1. Provide 2-4 possible conditions
    2. Include a brief, accurate description for each condition
    3. Assess likelihood as High, Medium, or Low
    4. Provide practical next steps for each condition
    5. Focus on educational value, not diagnosis
    6. Do not include any severe/emergency conditions unless specifically indicated by symptoms
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
        )
        
        # Extract and parse the response
        content = response.text
        # Handle JSON extraction from response
        try:
            # Try to find JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                result = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except:
            # Fallback to mock data if parsing fails
            result = {
                "possible_conditions": [
                    {
                        "condition": "Common Cold",
                        "description": "A viral infection of your nose and throat (upper respiratory tract).",
                        "likelihood": "High",
                        "next_steps": [
                            "Rest and stay hydrated",
                            "Use over-the-counter cold medications",
                            "Monitor symptoms for 2-3 days"
                        ]
                    }
                ]
            }
        
        disclaimer = (
            "DISCLAIMER: This tool provides educational information only and is not a substitute for professional medical advice. "
            "Always consult with a qualified healthcare provider for diagnosis and treatment. "
            "Results are based on general medical knowledge and may not apply to your specific situation."
        )
        
        conditions = [
            ConditionResponse(**cond) for cond in result["possible_conditions"]
        ]
        
        return SymptomCheckResponse(
            symptoms=symptoms,
            possible_conditions=conditions,
            disclaimer=disclaimer
        )
        
    except Exception as e:
        # Fallback to mock data if API call fails
        print(f"Error calling LLM: {e}")
        return get_mock_response(symptoms)

def get_mock_response(symptoms: str) -> SymptomCheckResponse:
    """
    Get mock response when LLM is not available
    """
    disclaimer = (
        "DISCLAIMER: This tool provides educational information only and is not a substitute for professional medical advice. "
        "Always consult with a qualified healthcare provider for diagnosis and treatment. "
        "Results are based on general medical knowledge and may not apply to your specific situation."
    )
    
    mock_conditions = [
        ConditionResponse(
            condition="Common Cold",
            description="A viral infection of your nose and throat (upper respiratory tract).",
            likelihood="High",
            next_steps=[
                "Rest and stay hydrated",
                "Use over-the-counter cold medications",
                "Monitor symptoms for 2-3 days"
            ]
        ),
        ConditionResponse(
            condition="Allergic Rhinitis",
            description="An allergic response causing inflammation of the nasal airways.",
            likelihood="Medium",
            next_steps=[
                "Identify and avoid allergens",
                "Consider antihistamines",
                "Consult a doctor if symptoms persist"
            ]
        )
    ]
    
    return SymptomCheckResponse(
        symptoms=symptoms,
        possible_conditions=mock_conditions,
        disclaimer=disclaimer
    )

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "Healthcare Symptom Checker API"}

@app.post("/check_symptoms/", response_model=SymptomCheckResponse)
async def check_symptoms(request: SymptomRequest, db: Session = Depends(get_db)):
    """
    Check symptoms and return possible conditions using LLM analysis.
    Stores the query and response in the database.
    """
    response = get_llm_response(request.symptoms)
    
    # Store in database
    query_record = SymptomQuery(
        symptoms=request.symptoms,
        response=json.dumps({
            "symptoms": response.symptoms,
            "possible_conditions": [cond.dict() for cond in response.possible_conditions],
            "disclaimer": response.disclaimer
        })
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)
    
    return response

@app.get("/history/", response_model=List[QueryHistoryResponse])
async def get_history(db: Session = Depends(get_db)):
    """
    Get history of symptom checks
    """
    queries = db.query(SymptomQuery).order_by(SymptomQuery.created_at.desc()).limit(20).all()
    return [
        QueryHistoryResponse(
            id=query.id,
            symptoms=query.symptoms,
            created_at=query.created_at.isoformat()
        ) 
        for query in queries
    ]

if __name__ == "__main__":
    print("Starting Uvicorn server on port 8080...")
    uvicorn.run(app, host="127.0.0.1", port=8080)