"""
Document Classification Endpoint
Klassifiziert Dokumente (PDFs, E-Mails, Bilder) automatisch
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel, Field

router = APIRouter()


class ClassificationResult(BaseModel):
    """Classification result"""
    document_type: str = Field(..., description="Erkannter Dokumenttyp")
    confidence: float = Field(..., ge=0.0, le=1.0)
    extracted_data: dict = Field(default_factory=dict)
    suggested_actions: list[str] = Field(default_factory=list)


@router.post("/document", response_model=ClassificationResult)
async def classify_document(
    file: UploadFile = File(...),
    context: Optional[str] = None
) -> ClassificationResult:
    """
    Klassifiziert hochgeladene Dokumente
    
    Erkennt automatisch:
    - Rechnungen (mit Beträgen, Lieferanten)
    - Lieferscheine
    - Analyseberichte
    - Zertifikate
    - Feldbuch-Einträge
    """
    
    # Mock implementation
    filename = file.filename.lower() if file.filename else ""
    
    if "rechnung" in filename or "invoice" in filename:
        return ClassificationResult(
            document_type="invoice",
            confidence=0.92,
            extracted_data={
                "invoice_number": "RE-2025-001",
                "amount": 1250.00,
                "supplier": "Agro Supplies GmbH",
                "date": "2025-10-14"
            },
            suggested_actions=[
                "In Kreditorenbuchhaltung erfassen",
                "Zahlungsfreigabe anfordern"
            ]
        )
    elif "lieferschein" in filename or "delivery" in filename:
        return ClassificationResult(
            document_type="delivery_note",
            confidence=0.88,
            extracted_data={
                "delivery_number": "LS-2025-042",
                "articles": ["Weizen A", "Gerste B"],
                "date": "2025-10-13"
            },
            suggested_actions=[
                "Wareneingang erfassen",
                "Qualitätsprüfung durchführen"
            ]
        )
    else:
        return ClassificationResult(
            document_type="unknown",
            confidence=0.45,
            extracted_data={},
            suggested_actions=["Manuell prüfen"]
        )


@router.post("/text", response_model=ClassificationResult)
async def classify_text(
    text: str,
    domain: Optional[str] = None
) -> ClassificationResult:
    """
    Klassifiziert Text (z.B. E-Mail-Inhalt)
    """
    text_lower = text.lower()
    
    # Einfache Keyword-Klassifizierung (später: LLM)
    if any(word in text_lower for word in ["bestellung", "order", "bestell"]):
        return ClassificationResult(
            document_type="purchase_order",
            confidence=0.75,
            extracted_data={"intent": "ordering"},
            suggested_actions=["Neue Bestellung anlegen"]
        )
    elif any(word in text_lower for word in ["reklamation", "complaint", "problem"]):
        return ClassificationResult(
            document_type="complaint",
            confidence=0.80,
            extracted_data={"intent": "complaint"},
            suggested_actions=["Ticket erstellen", "Vertrieb informieren"]
        )
    else:
        return ClassificationResult(
            document_type="general",
            confidence=0.60,
            extracted_data={},
            suggested_actions=[]
        )

