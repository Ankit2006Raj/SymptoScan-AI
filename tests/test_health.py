import pytest
import os
import json
from app import create_app

@pytest.fixture
def client():
    # Set testing config
    os.environ['FLASK_CONFIG'] = 'testing'
    os.environ['OPENAI_API_KEY'] = 'test-key'
    
    app = create_app('default')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_startup_health(client):
    # The create_app function runs startup checks
    # If the app initializes without crashing, the checks passed or logged warnings safely
    assert client is not None

def test_analyze_symptoms_validation(client):
    # Test that validation catches bad age
    payload = {
        "symptoms": "Headache",
        "age": 150, # invalid age
        "severity": 5
    }
    response = client.post('/api/analyze-symptoms', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Age must be between 0 and 120"

def test_analyze_symptoms_missing_symptoms(client):
    payload = {
        "age": 30,
        "severity": 5
    }
    response = client.post('/api/analyze-symptoms', 
                           data=json.dumps(payload),
                           content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 400
    assert "error" in data
    assert data["error"] == "Symptoms are required"
