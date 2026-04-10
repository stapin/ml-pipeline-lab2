from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_endpoint_success():
    response = client.post(
        "/predict",
        json={
            "full_text": "Amazing beauty product, highly recommend!"
        }
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert "predicted_rating" in data
    assert isinstance(data["predicted_rating"], int)
    assert 1 <= data["predicted_rating"] <= 5

def test_predict_endpoint_validation_error():
    response = client.post(
        "/predict",
        json={
            "text": "Excellent!"
        }
    )
    
    # 422 Unprocessable Entity
    assert response.status_code == 422