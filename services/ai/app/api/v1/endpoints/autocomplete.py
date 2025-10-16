"""
AI-Powered Autocomplete API
Provides intelligent autocomplete suggestions for ERP forms and inputs
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class AutocompleteRequest(BaseModel):
    """Request for autocomplete suggestions."""
    query: str = Field(..., description="Current input text")
    context: str = Field(..., description="Context information (field name, form type, etc.)")
    domain: str = Field("general", description="Domain context (procurement, inventory, finance, etc.)")
    max_suggestions: int = Field(5, description="Maximum number of suggestions to return")
    user_context: Optional[dict] = Field(None, description="Additional user context")


class AutocompleteSuggestion(BaseModel):
    """Autocomplete suggestion response."""
    text: str = Field(..., description="Suggested completion text")
    confidence: float = Field(..., description="Confidence score 0-1")
    category: str = Field(..., description="Suggestion category")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class AutocompleteResponse(BaseModel):
    """Response containing autocomplete suggestions."""
    suggestions: List[AutocompleteSuggestion]
    query: str
    context: str
    domain: str
    processing_time_ms: float


@router.post("/suggest", response_model=AutocompleteResponse)
async def get_autocomplete_suggestions(request: AutocompleteRequest) -> AutocompleteResponse:
    """
    Get AI-powered autocomplete suggestions.

    This endpoint provides intelligent suggestions based on:
    - Current query text
    - Domain context (procurement, inventory, etc.)
    - User context and history
    - ERP-specific terminology and patterns
    """
    import time
    start_time = time.time()

    try:
        # Import here to avoid circular imports
        from app.services.openai_service import suggest_autocomplete

        # Get suggestions from OpenAI service
        raw_suggestions = await suggest_autocomplete(
            query=request.query,
            context=request.context,
            domain=request.domain,
            max_suggestions=request.max_suggestions
        )

        # Format suggestions
        suggestions = []
        for i, suggestion in enumerate(raw_suggestions):
            suggestions.append(AutocompleteSuggestion(
                text=suggestion,
                confidence=max(0.1, 1.0 - (i * 0.1)),  # Decreasing confidence
                category=request.domain,
                metadata={
                    "position": i,
                    "domain": request.domain,
                    "context": request.context
                }
            ))

        processing_time = (time.time() - start_time) * 1000

        return AutocompleteResponse(
            suggestions=suggestions,
            query=request.query,
            context=request.context,
            domain=request.domain,
            processing_time_ms=processing_time
        )

    except Exception as e:
        # Fallback to basic suggestions if AI fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Autocomplete failed: {e}")

        # Provide basic fallback suggestions based on domain
        fallback_suggestions = _get_fallback_suggestions(
            request.query, request.domain, request.max_suggestions
        )

        processing_time = (time.time() - start_time) * 1000

        return AutocompleteResponse(
            suggestions=fallback_suggestions,
            query=request.query,
            context=request.context,
            domain=request.domain,
            processing_time_ms=processing_time
        )


def _get_fallback_suggestions(query: str, domain: str, max_suggestions: int) -> List[AutocompleteSuggestion]:
    """Provide fallback suggestions when AI is unavailable."""
    suggestions = []

    # Domain-specific fallback suggestions
    domain_suggestions = {
        "procurement": [
            "Weizen Premium Qualität",
            "Sojaschrot proteinreich",
            "Mais Futtermais",
            "Gerste Braugerste",
            "Rapsöl Kaltpressung"
        ],
        "inventory": [
            "Lagerbestand prüfen",
            "Mindestbestand auffüllen",
            "Inventur durchführen",
            "Wareneingang buchen",
            "Warenausgang verbuchen"
        ],
        "finance": [
            "Rechnung prüfen",
            "Zahlung freigeben",
            "Skonto nutzen",
            "Mahnung versenden",
            "Kostenstelle zuordnen"
        ],
        "general": [
            "Bestellung anlegen",
            "Lieferschein erstellen",
            "Rechnung buchen",
            "Kunden anlegen",
            "Artikel suchen"
        ]
    }

    base_suggestions = domain_suggestions.get(domain, domain_suggestions["general"])

    # Filter suggestions that start with query (case-insensitive)
    query_lower = query.lower()
    filtered = [s for s in base_suggestions if s.lower().startswith(query_lower)]

    # If no matches, return general suggestions
    if not filtered:
        filtered = base_suggestions[:max_suggestions]

    for i, suggestion in enumerate(filtered[:max_suggestions]):
        suggestions.append(AutocompleteSuggestion(
            text=suggestion,
            confidence=max(0.1, 0.8 - (i * 0.1)),
            category=domain,
            metadata={"fallback": True, "position": i}
        ))

    return suggestions


@router.get("/domains")
async def get_supported_domains():
    """Get list of supported autocomplete domains."""
    return {
        "domains": [
            {
                "id": "procurement",
                "name": "Einkauf & Beschaffung",
                "description": "Artikel, Lieferanten, Bestellungen"
            },
            {
                "id": "inventory",
                "name": "Lager & Inventur",
                "description": "Bestandsverwaltung, Warenbewegungen"
            },
            {
                "id": "finance",
                "name": "Finanzen & Buchhaltung",
                "description": "Rechnungen, Zahlungen, Kostenstellen"
            },
            {
                "id": "sales",
                "name": "Verkauf & Kunden",
                "description": "Kunden, Angebote, Aufträge"
            },
            {
                "id": "production",
                "name": "Produktion & Qualität",
                "description": "Fertigung, Qualitätskontrolle"
            },
            {
                "id": "general",
                "name": "Allgemein",
                "description": "Allgemeine ERP-Funktionen"
            }
        ]
    }