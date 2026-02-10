"""
JWT Token Utilities
Token-Erstellung und -Validierung mit PyJWT
"""

from __future__ import annotations
import os
import time
import jwt
from typing import List, TypedDict

# Environment Configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-insecure-change-me")
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_EXPIRE_MIN = int(os.environ.get("JWT_EXPIRE_MIN", "60"))


class Claims(TypedDict, total=False):
    """JWT Claims Structure"""
    sub: str  # Subject (User ID)
    roles: List[str]  # User Roles
    exp: int  # Expiration Time
    iat: int  # Issued At
    iss: str  # Issuer


def create_access_token(
    sub: str, roles: List[str], expires_min: int | None = None
) -> str:
    """
    Erstellt JWT Access Token

    Args:
        sub: User ID / Username
        roles: Liste der User-Rollen (z.B. ["admin", "manager"])
        expires_min: Optionale Ablaufzeit in Minuten (Default: JWT_EXPIRE_MIN)

    Returns:
        JWT Token als String
    """
    now = int(time.time())
    exp = now + 60 * (expires_min if expires_min is not None else JWT_EXPIRE_MIN)

    payload: Claims = {
        "sub": sub,
        "roles": roles,
        "iat": now,
        "exp": exp,
        "iss": "valeo-neuroerp",
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> Claims:
    """
    Dekodiert und validiert JWT Token

    Args:
        token: JWT Token String

    Returns:
        Claims-Objekt

    Raises:
        jwt.ExpiredSignatureError: Token abgelaufen
        jwt.InvalidTokenError: Token ungültig
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])

