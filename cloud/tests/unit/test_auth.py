import pytest
import base64
import json
from cloud.src.api.sync import extract_tenant_from_auth


def create_mock_token(payload: dict) -> str:
    payload_str = json.dumps(payload)
    return base64.b64encode(payload_str.encode("utf-8")).decode("utf-8")


def test_extract_tenant_from_auth_valid():
    token = create_mock_token({"tenant_id": "tenant-123", "exp": 9999999999})
    auth_header = f"Bearer {token}"
    assert extract_tenant_from_auth(auth_header) == "tenant-123"


def test_extract_tenant_from_auth_missing_header():
    with pytest.raises(ValueError):
        extract_tenant_from_auth(None)
    with pytest.raises(ValueError):
        extract_tenant_from_auth("")


def test_extract_tenant_from_auth_invalid_bearer():
    with pytest.raises(ValueError):
        extract_tenant_from_auth("Token something")


def test_extract_tenant_from_auth_missing_tenant_id():
    token = create_mock_token({"uuid": "user-123"})
    auth_header = f"Bearer {token}"
    with pytest.raises(ValueError):
        extract_tenant_from_auth(auth_header)


def test_extract_tenant_from_auth_malformed_base64():
    auth_header = "Bearer !@#$%^&*()"
    with pytest.raises(ValueError):
        extract_tenant_from_auth(auth_header)


def test_extract_tenant_from_auth_malformed_json():
    bad_json_b64 = base64.b64encode(b"{bad-json").decode("utf-8")
    auth_header = f"Bearer {bad_json_b64}"
    with pytest.raises(ValueError):
        extract_tenant_from_auth(auth_header)


def test_extract_tenant_from_auth_invalid_utf8():
    invalid_utf8_bytes = b"\xff\xfe"
    invalid_utf8_b64 = base64.b64encode(invalid_utf8_bytes).decode("utf-8")
    auth_header = f"Bearer {invalid_utf8_b64}"
    with pytest.raises(ValueError):
        extract_tenant_from_auth(auth_header)
