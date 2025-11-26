"""
Public Document Verification Router
QR-Code-basierte Beleg-Verifikation (ohne Authentifizierung)
"""

from fastapi import APIRouter, HTTPException
from typing import Literal
import hashlib
import logging
from app.repositories.document_repository import DocumentRepository
from app.core.dependency_container import container

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/verify", tags=["verification"])


def calculate_hash(domain: str, number: str, content: str) -> str:
    """Calculate SHA256 hash for document verification"""
    data = f"{domain}:{number}:{content}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


@router.get("/{domain}/{number}/{hash}")
async def verify_document(
    domain: Literal["sales", "purchase", "invoice", "delivery"],
    number: str,
    hash: str
):
    """
    Public endpoint for document verification via QR code

    Args:
        domain: Document type
        number: Document number
        hash: SHA256 hash (first 16 chars)

    Returns:
        Verification result with document metadata
    """
    try:
        # Get DocumentRepository from container
        doc_repo = container.resolve(DocumentRepository)

        # Fetch document from database
        doc_header = doc_repo.get_by_number(domain, number)
        if not doc_header:
            return {
                "valid": False,
                "domain": domain,
                "number": number,
                "status": "not_found",
                "hash": hash,
                "message": "Document not found"
            }

        # Convert to dict for hash calculation
        doc_dict = doc_repo.to_dict(doc_header)

        # Calculate hash from document content
        # Use document data as content for hash calculation
        import json
        content = json.dumps(doc_dict, sort_keys=True)
        expected_hash = calculate_hash(domain, number, content)

        is_valid = expected_hash == hash

        return {
            "valid": is_valid,
            "domain": domain,
            "number": number,
            "status": doc_header.status,
            "date": doc_header.date.isoformat() if doc_header.date else None,
            "hash": hash,
            "message": "Document is valid and authentic" if is_valid else "Document verification failed"
        }
    
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{domain}/{number}")
async def verify_document_simple(
    domain: Literal["sales", "purchase", "invoice", "delivery"],
    number: str
):
    """
    Simple verification without hash (checks if document exists)

    Args:
        domain: Document type
        number: Document number

    Returns:
        Document existence and basic metadata
    """
    try:
        # Get DocumentRepository from container
        doc_repo = container.resolve(DocumentRepository)

        # Check if document exists
        doc_header = doc_repo.get_by_number(domain, number)

        if doc_header:
            return {
                "exists": True,
                "domain": domain,
                "number": number,
                "status": doc_header.status,
                "date": doc_header.date.isoformat() if doc_header.date else None,
                "message": "Document exists"
            }
        else:
            return {
                "exists": False,
                "domain": domain,
                "number": number,
                "status": "not_found",
                "message": "Document not found"
            }
    
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
