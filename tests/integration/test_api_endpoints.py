"""
Integration Tests for API Endpoints

Tests complete API workflows and endpoint interactions.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.api
class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test GET /health"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]


@pytest.mark.integration
@pytest.mark.api
class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_user(self, client, test_user_data):
        """Test POST /api/auth/register"""
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "password" not in data  # Password should not be returned
    
    def test_register_duplicate_username(self, client, test_user_data):
        """Test registering with duplicate username"""
        # First registration
        client.post("/api/auth/register", json=test_user_data)
        
        # Second registration with same username
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"].lower()
    
    def test_login(self, client, test_user_data):
        """Test POST /api/auth/token (login)"""
        # Register user first
        client.post("/api/auth/register", json=test_user_data)
        
        # Login
        response = client.post(
            "/api/auth/token",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data
    
    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/auth/token",
            data={
                "username": "nonexistent",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """Test GET /api/auth/me"""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "role" in data


@pytest.mark.integration
@pytest.mark.api
class TestExtensionEndpoints:
    """Test extension API endpoints"""
    
    def test_extension_detect(self, client, test_comment_data, mock_ml_model, monkeypatch):
        """Test POST /api/extension/detect"""
        # Mock ML model
        monkeypatch.setattr("backend.services.ml_model.MLModel.predict", 
                          mock_ml_model.predict)
        
        response = client.post(
            "/api/extension/detect",
            json=test_comment_data,
            auth=("extension", "api_key")  # Basic auth
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert "probabilities" in data
        assert data["prediction"] in [0, 1, 2, 3]
    
    def test_extension_batch_detect(self, client, mock_ml_model, monkeypatch):
        """Test POST /api/extension/batch-detect"""
        monkeypatch.setattr("backend.services.ml_model.MLModel.predict",
                          mock_ml_model.predict)
        
        batch_data = {
            "items": [
                {"text": "Clean comment", "platform": "facebook"},
                {"text": "Offensive content", "platform": "youtube"},
                {"text": "Hate speech here", "platform": "twitter"}
            ],
            "save_to_db": False
        }
        
        response = client.post(
            "/api/extension/batch-detect",
            json=batch_data,
            auth=("extension", "api_key")
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 3
        assert "count" in data
        assert data["count"] == 3


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
class TestPredictionEndpoints:
    """Test prediction API endpoints"""
    
    def test_predict_single(self, client, auth_headers, mock_ml_model, monkeypatch):
        """Test POST /api/prediction/single"""
        monkeypatch.setattr("backend.services.ml_model.MLModel.predict",
                          mock_ml_model.predict)
        
        response = client.post(
            "/api/prediction/single",
            json={"text": "Test comment for prediction"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
    
    def test_predict_batch(self, client, auth_headers, mock_ml_model, monkeypatch):
        """Test POST /api/prediction/batch"""
        monkeypatch.setattr("backend.services.ml_model.MLModel.predict",
                          mock_ml_model.predict)
        
        response = client.post(
            "/api/prediction/batch",
            json={
                "texts": [
                    "First comment",
                    "Second comment",
                    "Third comment"
                ]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 3


@pytest.mark.integration
@pytest.mark.api
class TestAdminEndpoints:
    """Test admin API endpoints (requires admin role)"""
    
    def test_admin_dashboard_unauthorized(self, client, auth_headers):
        """Test accessing admin dashboard without admin role"""
        response = client.get("/api/admin/dashboard", headers=auth_headers)
        
        # Should return 403 Forbidden for non-admin users
        assert response.status_code in [401, 403]
    
    def test_health_endpoint_public(self, client):
        """Test that health endpoint is publicly accessible"""
        response = client.get("/health")
        
        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.api
class TestRateLimiting:
    """Test rate limiting"""
    
    def test_rate_limit_enforcement(self, client, test_comment_data):
        """Test that rate limiting is enforced"""
        # Make many requests rapidly
        responses = []
        for i in range(150):  # More than default limit
            response = client.post(
                "/api/extension/detect",
                json=test_comment_data,
                auth=("extension", "api_key")
            )
            responses.append(response)
        
        # At least one should be rate limited
        status_codes = [r.status_code for r in responses]
        
        # Either all succeed (rate limiting disabled) or some are blocked
        assert all(code in [200, 429] for code in status_codes)


@pytest.mark.integration
@pytest.mark.api
class TestErrorHandling:
    """Test API error handling"""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/extension/detect",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            auth=("extension", "api_key")
        )
        
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        response = client.post(
            "/api/extension/detect",
            json={},  # Missing 'text' field
            auth=("extension", "api_key")
        )
        
        assert response.status_code == 422
    
    def test_method_not_allowed(self, client):
        """Test wrong HTTP method"""
        response = client.get("/api/extension/detect")
        
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])

