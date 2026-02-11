"""Shared authentication & authorization for all VALEO-NeuroERP Python services."""

from .middleware import AuthMiddleware
from .dependencies import (
    get_current_user,
    get_optional_user,
    require_role,
    require_scope,
    CurrentUser,
)
from .config import AuthConfig

__all__ = [
    "AuthMiddleware",
    "AuthConfig",
    "get_current_user",
    "get_optional_user",
    "require_role",
    "require_scope",
    "CurrentUser",
]

