"""
Authentication & Authorization Package
JWT-basierte Auth mit Rollen-Management
"""

from .jwt import create_access_token, decode_token, Claims
from .deps import get_current_user, require_roles, User

__all__ = [
    "create_access_token",
    "decode_token",
    "Claims",
    "get_current_user",
    "require_roles",
    "User",
]

