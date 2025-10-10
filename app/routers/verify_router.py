"""
Public Document Verification Router
QR-Code-basierte Beleg-Verifikation (ohne Authentifizierung)
"""

from fastapi import APIRouter, HTTPException
from typing import Literal
import hashlib
import logging

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
        # TODO: Fetch document from database
        # For now, mock response
        
        # In production: Calculate hash from actual document
        # expected_hash = calculate_hash(domain, number, document.content)
        
        # Mock verification (always valid for demo)
        is_valid = True  # expected_hash == hash
        
        return {
            "valid": is_valid,
            "domain": domain,
            "number": number,
            "status": "posted" if is_valid else "unknown",
            "date": "2025-10-09",
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
        # TODO: Fetch document from database
        
        return {
            "exists": True,
            "domain": domain,
            "number": number,
            "status": "posted",
            "date": "2025-10-09",
            "message": "Document exists"
        }
    
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
