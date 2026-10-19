"""
User API endpoints
RESTful API for user management and authentication
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.repositories import UserRepository
from ....core.dependency_container import container
from ....auth.deps_oidc import get_current_user as authenticated_user, User as OIDCUser
from app.auth.deps import require_roles
from app.core.tenant import get_tenant_id
from app.infrastructure.models import User as Profile
from sqlalchemy import or_
import json
from ..schemas.shared import (
    UserCreate, UserUpdate, User,
    UserLogin, ChangePasswordRequest
)
from ..schemas.base import PaginatedResponse

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.users_schemas import UsersOut


router = APIRouter(tags=["users"])


def _profile_output(profile: Profile) -> User:
    values = {name: getattr(profile, name) for name in User.model_fields}
    if not isinstance(values['roles'], (str, type(None))):
        values['roles'] = json.dumps(values['roles'])
    return User.model_validate(values)



@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED, summary="User anlegen")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user.

    This endpoint allows creating a new user account in the system.
    The user will be associated with a specific tenant.
    """
    try:
        user_repo = container.resolve(UserRepository)

        # Check if username or email already exists
        existing_by_username = await user_repo.get_by_username(user_data.username, user_data.tenant_id)
        if existing_by_username:
            raise HTTPException(status_code=400, detail="Username already exists")

        existing_by_email = await user_repo.get_by_email(user_data.email, user_data.tenant_id)
        if existing_by_email:
            raise HTTPException(status_code=400, detail="Email already exists")

        user = await user_repo.create(user_data.model_dump(), user_data.tenant_id)
        return User.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.get("/me", response_model=User, summary="Current user abrufen")
async def get_current_user(
    oidc_user: OIDCUser = Depends(authenticated_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.

    Returns the profile information of the currently authenticated user.
    """
    try:
        user = db.query(Profile).filter(
            Profile.tenant_id == tenant_id, Profile.is_active.is_(True),
            or_(Profile.id == oidc_user['sub'], Profile.keycloak_id == oidc_user['sub']),
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return _profile_output(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve current user")


@router.get("/{user_id}", response_model=User, summary="User abrufen")
async def get_user(
    user_id: str,
    oidc_user: OIDCUser = Depends(authenticated_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get user by ID.

    Retrieve detailed information about a specific user.
    """
    try:
        user = db.query(Profile).filter(Profile.id == user_id,
                                       Profile.tenant_id == tenant_id,
                                       Profile.is_active.is_(True)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if 'admin' not in oidc_user.get('roles', []) and oidc_user['sub'] not in {user.id, user.keycloak_id}:
            raise HTTPException(status_code=403, detail="Not authorized for this profile")
        return _profile_output(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve user")


@router.get("/", response_model=PaginatedResponse[User], summary="Users auflisten")
async def list_users(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    oidc_user: OIDCUser = Depends(authenticated_user),
    effective_tenant_id: str = Depends(get_tenant_id),
    directory_admin: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):
    """
    List users with pagination.

    Retrieve a paginated list of users, optionally filtered by tenant.
    """
    try:
        query = db.query(Profile).filter(Profile.tenant_id == effective_tenant_id, Profile.is_active.is_(True))
        total = query.count()
        users = query.order_by(Profile.id).offset(skip).limit(limit).all()

        return PaginatedResponse[User](
            items=[_profile_output(user) for user in users],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list users")


@router.put("/{user_id}", response_model=User, summary="User aktualisieren")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    oidc_user: OIDCUser = Depends(authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Update user information.

    Modify user details such as email, name, or roles.
    """
    try:
        user_repo = container.resolve(UserRepository)

        # Extract tenant from OIDC claims
        tenant_id = oidc_user.get("raw", {}).get("tenant_id", "system")

        # Check for email conflicts if email is being updated
        if user_data.email:
            existing = await user_repo.get_by_email(user_data.email, tenant_id)
            if existing and existing.id != user_id:
                raise HTTPException(status_code=400, detail="Email already exists")

        user = await user_repo.update(user_id, user_data.model_dump(exclude_unset=True), tenant_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return User.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="User löschen",
    response_model=None
)
async def delete_user(
    user_id: str,
    oidc_user: OIDCUser = Depends(authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Delete user (soft delete).

    Mark a user as inactive. This is a soft delete operation.
    """
    try:
        user_repo = container.resolve(UserRepository)

        # Extract tenant from OIDC claims
        tenant_id = oidc_user.get("raw", {}).get("tenant_id", "system")

        success = await user_repo.delete(user_id, tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


@router.post("/login", response_model=UsersOut, summary="Anmelden")
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login.

    Note: This system uses OIDC authentication. Direct login is handled by the OIDC provider.
    This endpoint provides information about the authentication flow.
    """
    return {
        "message": "OIDC Authentication Required",
        "info": "This system uses OpenID Connect (OIDC) for authentication. Please use the OIDC provider login flow.",
        "oidc_provider": "Keycloak",
        "login_url": "/auth/login",  # Placeholder - actual URL would be configured
        "status": "redirect_required"
    }


@router.post("/change-password", summary="Password change",
    response_model=UsersOut
)
async def change_password(
    password_data: ChangePasswordRequest,
    oidc_user: OIDCUser = Depends(authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.

    Note: Password changes are handled by the OIDC provider (Keycloak).
    This endpoint provides information about the password change flow.
    """
    return {
        "message": "OIDC Password Change Required",
        "info": "Password changes must be performed through the OIDC provider (Keycloak) interface.",
        "user_id": oidc_user["sub"],
        "oidc_provider": "Keycloak",
        "change_url": "/auth/account",  # Placeholder - actual URL would be configured
        "status": "external_action_required"
    }
