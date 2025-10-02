"""
CRM Contact management endpoints
RESTful API for contact management with clean architecture
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.repositories import ContactRepository
from ....core.dependency_container import container
from ..schemas.crm import (
    ContactCreate, ContactUpdate, Contact
)
from ..schemas.base import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=Contact, status_code=201)
async def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new contact.

    This endpoint allows creating a new contact associated with a customer.
    """
    try:
        contact_repo = container.resolve(ContactRepository)
        contact = await contact_repo.create(contact_data.model_dump(), "system")  # TODO: tenant context
        return Contact.model_validate(contact)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create contact: {str(e)}")


@router.get("/", response_model=PaginatedResponse[Contact])
async def list_contacts(
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List contacts with pagination and filtering.

    Retrieve a paginated list of contacts, optionally filtered by customer.
    """
    try:
        contact_repo = container.resolve(ContactRepository)

        contacts = await contact_repo.get_all("system", skip, limit, customer_id)  # TODO: tenant context
        total = await contact_repo.count("system", customer_id)  # TODO: tenant context

        return PaginatedResponse[Contact](
            items=[Contact.model_validate(contact) for contact in contacts],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list contacts: {str(e)}")


@router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: str,
    db: Session = Depends(get_db)
):
    """
    Get contact by ID.

    Retrieve detailed information about a specific contact.
    """
    try:
        contact_repo = container.resolve(ContactRepository)
        contact = await contact_repo.get_by_id(contact_id, "system")  # TODO: tenant context
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return Contact.model_validate(contact)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve contact: {str(e)}")


@router.put("/{contact_id}", response_model=Contact)
async def update_contact(
    contact_id: str,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db)
):
    """
    Update contact information.

    Modify contact details such as name, email, or position.
    """
    try:
        contact_repo = container.resolve(ContactRepository)
        contact = await contact_repo.update(contact_id, contact_data.model_dump(exclude_unset=True), "system")  # TODO: tenant context
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return Contact.model_validate(contact)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update contact: {str(e)}")


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete contact (soft delete).

    Mark a contact as inactive. This is a soft delete operation.
    """
    try:
        contact_repo = container.resolve(ContactRepository)
        success = await contact_repo.delete(contact_id, "system")  # TODO: tenant context
        if not success:
            raise HTTPException(status_code=404, detail="Contact not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete contact: {str(e)}")