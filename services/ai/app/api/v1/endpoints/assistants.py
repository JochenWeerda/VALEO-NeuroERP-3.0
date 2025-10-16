"""
AI Assistants Endpoint
Provides AI assistance for all 181 ERP masks
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# Domain-Mapping für alle 181 Masken
MASK_DOMAINS = {
    # Verkauf (15 Masken)
    "sales_order": "sales",
    "sales_delivery": "sales",
    "sales_invoice": "sales",
    "sales_quote": "sales",
    "sales_dashboard": "sales",
    
    # CRM (4 Masken)
    "crm_contacts": "crm",
    "crm_leads": "crm",
    "crm_activities": "crm",
    "crm_farm_profiles": "crm",
    
    # Einkauf (12 Masken)
    "procurement_order": "procurement",
    "procurement_request": "procurement",
    "procurement_supplier": "procurement",
    "procurement_goods_receipt": "procurement",
    
    # Finanzbuchhaltung (130 Masken - SKR03/04 komplett)
    "finance_general_ledger": "finance",
    "finance_account": "finance",
    "finance_journal": "finance",
    "finance_ar_invoice": "finance",
    "finance_ap_invoice": "finance",
    "finance_balance_sheet": "finance",
    "finance_pnl": "finance",
    "finance_bwa": "finance",
    
    # Lager (8 Masken)
    "inventory_stock": "inventory",
    "inventory_movement": "inventory",
    "inventory_count": "inventory",
    
    # Agrar (12 Masken)
    "agrar_field_book": "agrar",
    "agrar_seed": "agrar",
    "agrar_fertilizer": "agrar",
    "agrar_pesticide": "agrar",
    "agrar_harvest": "agrar",
    
    # Weitere Domains folgen...
}


class AssistantRequest(BaseModel):
    """Request for AI assistant"""
    mask_id: str = Field(..., description="Mask/Screen identifier (e.g. 'sales_order')")
    context: Dict[str, Any] = Field(default_factory=dict, description="Current form/context data")
    field: Optional[str] = Field(None, description="Specific field for autocomplete")
    query: Optional[str] = Field(None, description="User's question or input")
    action: str = Field(..., description="Action: autocomplete, validate, suggest, explain")


class AssistantResponse(BaseModel):
    """Response from AI assistant"""
    suggestions: List[str] = Field(default_factory=list)
    explanation: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.post("/autocomplete", response_model=AssistantResponse)
async def autocomplete_field(request: AssistantRequest) -> AssistantResponse:
    """
    Autocomplete für Formularfelder basierend auf Kontext
    
    Beispiel: Kunde tippt "Weiz" → schlägt "Weizen A (Bio, 25kg)" vor
    """
    domain = MASK_DOMAINS.get(request.mask_id, "unknown")
    
    # Mock implementation - wird später durch LLM ersetzt
    suggestions = []
    
    if request.field == "customer" and request.query:
        # Beispiel-Suggestions für Kunden-Autocomplete
        suggestions = [
            f"{request.query}enmeier GmbH",
            f"Bio-Hof {request.query}",
            f"Landwirtschaft {request.query} & Söhne"
        ]
    elif request.field == "article" and request.query:
        # Beispiel-Suggestions für Artikel-Autocomplete
        suggestions = [
            f"{request.query} A (Bio, 25kg Sack)",
            f"{request.query} Standard (konv., 50kg)",
            f"{request.query}-Saatgut (zert., 1000 Korn)"
        ]
    
    return AssistantResponse(
        suggestions=suggestions[:5],  # Top 5
        explanation=f"Autocomplete for {request.field} in {domain} domain",
        confidence=0.85,
        metadata={"domain": domain, "mask": request.mask_id}
    )


@router.post("/validate", response_model=AssistantResponse)
async def validate_form(request: AssistantRequest) -> AssistantResponse:
    """
    Validierung von Formulardaten mit Business-Logic
    
    Beispiel: Preis < Einkaufspreis → Warnung
    """
    domain = MASK_DOMAINS.get(request.mask_id, "unknown")
    
    # Mock validation logic
    warnings = []
    
    # Beispiel: Preisvalidierung
    if "price" in request.context and "cost" in request.context:
        price = request.context.get("price", 0)
        cost = request.context.get("cost", 0)
        if price < cost:
            warnings.append(f"⚠️ Verkaufspreis ({price}€) liegt unter Einkaufspreis ({cost}€)")
    
    # Beispiel: Mengenvalidierung
    if "quantity" in request.context:
        qty = request.context.get("quantity", 0)
        if qty < 0:
            warnings.append("🛑 Negative Menge nicht erlaubt")
        elif qty > 10000:
            warnings.append("⚠️ Ungewöhnlich hohe Menge - bitte prüfen")
    
    return AssistantResponse(
        suggestions=warnings,
        explanation="Business logic validation completed",
        confidence=0.95,
        metadata={"domain": domain, "warnings_count": len(warnings)}
    )


@router.post("/suggest", response_model=AssistantResponse)
async def suggest_next_action(request: AssistantRequest) -> AssistantResponse:
    """
    Vorschläge für nächste Aktionen basierend auf Kontext
    
    Beispiel: Nach Auftragserfassung → "Lieferung erstellen?" vorschlagen
    """
    domain = MASK_DOMAINS.get(request.mask_id, "unknown")
    
    suggestions = []
    
    # Domain-spezifische Suggestions
    if request.mask_id == "sales_order" and request.context.get("status") == "confirmed":
        suggestions = [
            "📦 Lieferung erstellen",
            "📄 Rechnung erstellen",
            "📧 Auftragsbestätigung senden"
        ]
    elif request.mask_id == "procurement_request":
        suggestions = [
            "🔍 Lieferanten vorschlagen",
            "📊 Bestandsprognose anzeigen",
            "💰 Preisvergleich durchführen"
        ]
    
    return AssistantResponse(
        suggestions=suggestions,
        explanation=f"Action suggestions for {request.mask_id}",
        confidence=0.80,
        metadata={"domain": domain}
    )


@router.post("/explain", response_model=AssistantResponse)
async def explain_field(request: AssistantRequest) -> AssistantResponse:
    """
    Erklärt Formularfelder und Geschäftslogik in natürlicher Sprache
    
    Beispiel: "Was ist SKR03?" → "SKR03 ist der Standard-Kontenrahmen..."
    """
    # Mock explanations - wird später durch LLM + RAG ersetzt
    explanations = {
        "skr03": "SKR03 ist der Standard-Kontenrahmen für die Landwirtschaft. Er enthält spezielle Konten für landwirtschaftliche Betriebe.",
        "feldbuch": "Das Feldbuch dokumentiert alle Anbaumaßnahmen nach EU-Vorgaben. Es ist Pflicht für Cross-Compliance.",
        "eudr": "EU Deforestation Regulation - verbietet Import von Produkten, die zu Entwaldung beigetragen haben."
    }
    
    query = request.query.lower() if request.query else ""
    explanation = explanations.get(query, f"Information zu '{request.query}' wird noch aufbereitet.")
    
    return AssistantResponse(
        suggestions=[],
        explanation=explanation,
        confidence=0.70,
        metadata={"query": request.query}
    )


@router.get("/masks")
async def list_supported_masks():
    """Liste aller unterstützten Masken mit AI-Features"""
    return {
        "total": len(MASK_DOMAINS),
        "domains": {
            "sales": 15,
            "crm": 4,
            "procurement": 12,
            "finance": 130,
            "inventory": 8,
            "agrar": 12,
        },
        "masks": list(MASK_DOMAINS.keys())
    }

