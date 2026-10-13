import pytest
from app.main import app, calculate_checksum

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_endpoint(client):
    """Test standard root endpoint response and metadata"""
    response = client.get('/')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'online'
    assert json_data['author'] == 'Jinesh Gandhi'
    assert 'version' in json_data

def test_healthz_endpoint(client):
    """Test Kubernetes readiness/liveness probe target"""
    response = client.get('/healthz')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'
    assert json_data['checks']['security_guardrails'] == 'enforced'

def test_api_data_endpoint(client):
    """Test data retrieval endpoint"""
    response = client.get('/api/v1/data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data['data']) == 5
    assert json_data['data'][0]['passed'] is True

def test_checksum_utility():
    """Test cryptographic hash calculation unit function"""
    checksum = calculate_checksum("DevSecOps-Jinesh-Gandhi")
    assert isinstance(checksum, str)
    assert len(checksum) == 64
