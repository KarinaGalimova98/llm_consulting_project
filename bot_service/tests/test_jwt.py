import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


def test_decode_and_validate_ok():
    token = jwt.encode(
        {"sub": "1", "role": "user", "exp": 9999999999},
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )
    payload = decode_and_validate(token)
    assert payload["sub"] == "1"


def test_decode_and_validate_invalid():
    with pytest.raises(ValueError):
        decode_and_validate("trash_token")