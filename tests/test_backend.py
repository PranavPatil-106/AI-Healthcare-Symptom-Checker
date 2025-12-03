import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient
from backend.main import app
from backend.models import create_tables

# Create tables for testing
create_tables()

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Healthcare Symptom Checker API"

def test_symptom_check_valid_input():
    """Test symptom checking with valid input."""
    symptom_data = {
        "symptoms": "Headache and fever"
    }
    
    response = client.post("/check_symptoms/", json=symptom_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "symptoms" in data
    assert "possible_conditions" in data
    assert "disclaimer" in data
    assert len(data["possible_conditions"]) > 0
    
    # Check structure of conditions
    condition = data["possible_conditions"][0]
    assert "condition" in condition
    assert "description" in condition
    assert "likelihood" in condition
    assert "next_steps" in condition

def test_symptom_check_empty_input():
    """Test symptom checking with empty input."""
    symptom_data = {
        "symptoms": ""
    }
    
    response = client.post("/check_symptoms/", json=symptom_data)
    # Should still return a response even with empty symptoms
    assert response.status_code == 200

def test_history_endpoint():
    """Test the history endpoint."""
    # First add a symptom check
    symptom_data = {
        "symptoms": "Test symptom for history"
    }
    client.post("/check_symptoms/", json=symptom_data)
    
    # Then check history
    response = client.get("/history/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "id" in item
        assert "symptoms" in item
        assert "created_at" in item

def test_models_import():
    """Test that models can be imported without errors."""
    try:
        from backend.models import SymptomQuery, create_tables, get_db
        assert SymptomQuery is not None
        assert create_tables is not None
        assert get_db is not None
    except ImportError:
        pytest.fail("Failed to import models")

if __name__ == "__main__":
    pytest.main([__file__])