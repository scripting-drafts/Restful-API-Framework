from api.endpoints import create_token
from utils.validation import validate_schema

def test_create_token():
    resp = create_token("admin", "password123")
    assert resp.status_code == 200
    body = resp.json()
    assert "token" in body
    validate_schema(body, "auth_token_response")
