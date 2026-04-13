import binascii
import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt

JWT_ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRATION_MINUTES = 30
REFRESH_TOKEN_EXPIRATION_DAYS = 30
REFRESH_COOKIE_NAME = "refresh_token"

_PRIVATE_KEY_PATH = os.getenv("JWT_PRIVATE_KEY_PATH", "keys/jwt_private.pem")
_PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH", "keys/jwt_private.pem.pub")

_private_key: str = Path(_PRIVATE_KEY_PATH).read_text()
_public_key: str = Path(_PUBLIC_KEY_PATH).read_text()


def hash_password(password: str) -> str:
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")

    password_hash = hashlib.pbkdf2_hmac(
        "sha512", password.encode("utf-8"), salt, 100000
    )

    password_hash = binascii.hexlify(password_hash)

    return (salt + password_hash).decode("ascii")


def check_password(password: str, password_hash: str) -> None:
    salt = password_hash[:64]
    password_hash = password_hash[64:]

    current_password_hash = hashlib.pbkdf2_hmac(
        "sha512", password.encode("utf-8"), salt.encode("ascii"), 100000
    )

    current_password_hash = binascii.hexlify(current_password_hash).decode(
        "ascii"
    )

    if not current_password_hash == password_hash:
        raise ValueError("Incorrect password")


def _encode_token(user_id: uuid.UUID, token_type: str, expires_delta: timedelta) -> str:
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _private_key, algorithm=JWT_ALGORITHM)


def _decode_token(token: str, expected_type: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, _public_key, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            raise ValueError("Wrong token type")
        return uuid.UUID(payload["sub"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, ValueError) as e:
        raise ValueError("Invalid or expired token") from e


def create_access_token(user_id: uuid.UUID) -> str:
    return _encode_token(user_id, "access", timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES))


def create_refresh_token(user_id: uuid.UUID) -> str:
    return _encode_token(user_id, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS))


def decode_access_token(token: str) -> uuid.UUID:
    return _decode_token(token, "access")


def decode_refresh_token(token: str) -> uuid.UUID:
    return _decode_token(token, "refresh")
