"""Tests for password policy, hashing, verification, and token creation."""

import pytest
from fastapi import HTTPException

from app.auth import (
    create_token,
    decode_token,
    hash_password,
    validate_password_policy,
    verify_password,
)


class TestPasswordPolicy:
    def test_valid_password_8_chars(self):
        validate_password_policy("Abc12345")

    def test_valid_password_12_chars(self):
        validate_password_policy("Abcdefgh1234")

    def test_too_short(self):
        with pytest.raises(HTTPException) as exc:
            validate_password_policy("Ab1")
        assert exc.value.status_code == 400

    def test_too_long(self):
        with pytest.raises(HTTPException) as exc:
            validate_password_policy("Abcdefgh12345")
        assert exc.value.status_code == 400

    def test_missing_uppercase(self):
        with pytest.raises(HTTPException) as exc:
            validate_password_policy("abcdefg1")
        assert exc.value.status_code == 400

    def test_missing_lowercase(self):
        with pytest.raises(HTTPException) as exc:
            validate_password_policy("ABCDEFG1")
        assert exc.value.status_code == 400

    def test_missing_number(self):
        with pytest.raises(HTTPException) as exc:
            validate_password_policy("Abcdefgh")
        assert exc.value.status_code == 400


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pw = "Test1234"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("RightPass1")
        assert not verify_password("WrongPass1", hashed)


class TestTokens:
    def test_create_and_decode(self):
        token = create_token("user-1", {"type": "tenant_user"})
        payload = decode_token(token)
        assert payload["sub"] == "user-1"
        assert payload["type"] == "tenant_user"

    def test_invalid_token(self):
        with pytest.raises(HTTPException) as exc:
            decode_token("not.a.valid.token")
        assert exc.value.status_code == 401
