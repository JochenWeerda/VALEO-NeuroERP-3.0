"""
Test for the health endpoint
"""

def test_health_check(client_no_auth):
    """Test the health check endpoint (no auth required)"""
    response = client_no_auth.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Service is healthy"
    assert "timestamp" in data or "timestamp" in str(data)

def test_health_check_with_auth(client):
    """Test the health check works with API key too"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Service is healthy"