from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class SymptomQuery(Base):
    __tablename__ = 'symptom_queries'
    
    id = Column(Integer, primary_key=True, index=True)
    symptoms = Column(Text, nullable=False)
    response = Column(Text, nullable=False)  # JSON string of the response
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SymptomQuery(id={self.id}, symptoms='{self.symptoms[:50]}...')>"

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./symptom_checker.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()