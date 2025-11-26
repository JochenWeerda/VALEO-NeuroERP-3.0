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
from ....auth.deps_oidc import get_current_user, User as OIDCUser
from ..schemas.shared import (
    UserCreate, UserUpdate, User,
    UserLogin, TokenResponse, ChangePasswordRequest
)
from ..schemas.base import PaginatedResponse

router = APIRouter(tags=["users"])


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
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


@router.get("/me", response_model=User)
async def get_current_user(
    oidc_user: OIDCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.

    Returns the profile information of the currently authenticated user.
    """
    try:
        user_repo = container.resolve(UserRepository)

        # Get user by ID (sub from OIDC token)
        user = await user_repo.get_by_id(oidc_user["sub"], "system")  # TODO: Extract tenant from token
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return User.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve current user: {str(e)}")


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    oidc_user: OIDCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID.

    Retrieve detailed information about a specific user.
    """
    try:
        user_repo = container.resolve(UserRepository)

        # Extract tenant from OIDC claims (assuming tenant is in custom claims)
        tenant_id = oidc_user.get("raw", {}).get("tenant_id", "system")

        user = await user_repo.get_by_id(user_id, tenant_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return User.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user: {str(e)}")


@router.get("/", response_model=PaginatedResponse[User])
async def list_users(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    oidc_user: OIDCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List users with pagination.

    Retrieve a paginated list of users, optionally filtered by tenant.
    """
    try:
        user_repo = container.resolve(UserRepository)

        # Use provided tenant_id or extract from authenticated user
        effective_tenant_id = tenant_id or oidc_user.get("raw", {}).get("tenant_id", "system")

        users = await user_repo.get_all(effective_tenant_id, skip, limit)
        total = await user_repo.count(effective_tenant_id)

        return PaginatedResponse[User](
            items=[User.model_validate(user) for user in users],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    oidc_user: OIDCUser = Depends(get_current_user),
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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    oidc_user: OIDCUser = Depends(get_current_user),
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


@router.post("/login", response_model=dict)
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


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    oidc_user: OIDCUser = Depends(get_current_user),
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