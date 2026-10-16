import json

def test_health_endpoint_healthy(client):
    """Verify that /health returns 200 OK and valid JSON with service status."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['service'] == "ContactHub"
    assert data['status'] == "healthy"
    assert data['database'] == "connected"
    assert 'version' in data
    assert 'timestamp' in data

def test_homepage_loads(client):
    """Verify that landing page loads successfully for anonymous users."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"ContactHub" in response.data
    assert b"BCA College Microproject" in response.data
