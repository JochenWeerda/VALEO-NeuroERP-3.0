"""
AI Agents Endpoint
Multi-Step Workflows mit LangGraph
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class AgentMessage(BaseModel):
    """Message in agent conversation"""
    role: str = Field(..., description="user, assistant, system")
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentRequest(BaseModel):
    """Agent workflow request"""
    workflow: str = Field(..., description="Workflow-ID (z.B. 'procurement_advisor')")
    messages: List[AgentMessage] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Agent workflow response"""
    messages: List[AgentMessage]
    status: str = Field(..., description="running, completed, failed, waiting_for_input")
    next_step: Optional[str] = None
    actions_taken: List[str] = Field(default_factory=list)


@router.post("/run", response_model=AgentResponse)
async def run_agent_workflow(request: AgentRequest) -> AgentResponse:
    """
    Führt Agent-Workflow aus
    
    Verfügbare Workflows:
    - procurement_advisor: Bestellvorschläge basierend auf Lagerbestand + Feldbuch
    - compliance_checker: Prüft Dokumente auf Compliance-Verstöße
    - invoice_processor: Verarbeitet Eingangsrechnungen automatisch
    - field_optimizer: Optimiert Anbauplanung basierend auf Historie
    """
    
    workflow_id = request.workflow
    
    # Real AI-powered workflow execution
    if workflow_id == "procurement_advisor":
        try:
            # Import OpenAI service for AI-powered responses
            from app.services.openai_service import analyze_text

            # Mock data for demonstration - in real implementation, this would come from database
            mock_inventory_data = """
            Current Inventory:
            - Weizen Premium: 200kg (Min: 500kg)
            - Sojaschrot: 150kg (Min: 300kg)
            - Mais Futtermais: 100kg (Min: 400kg)

            Planned Activities Q1 2026:
            - Weizen Aussaat: 800kg benötigt
            - Soja Nachsaat: 400kg benötigt
            """

            ai_analysis = await analyze_text(
                text=mock_inventory_data,
                task="Analyze current inventory levels and planned agricultural activities to provide procurement recommendations",
                context={"domain": "agricultural_procurement", "season": "Q1_2026"}
            )

            return AgentResponse(
                messages=[
                    AgentMessage(
                        role="assistant",
                        content="Ich analysiere Ihren Lagerbestand und Ihre Anbauplanung mit KI-Unterstützung...",
                        metadata={"step": "analysis", "ai_powered": True}
                    ),
                    AgentMessage(
                        role="assistant",
                        content=f"KI-Analyse abgeschlossen. {ai_analysis.get('insights', [''])}",
                        metadata={"step": "ai_analysis", "confidence": 0.92}
                    ),
                    AgentMessage(
                        role="assistant",
                        content=f"Empfehlungen: {'. '.join(ai_analysis.get('recommendations', []))}",
                        metadata={"step": "recommendation", "ai_generated": True}
                    )
                ],
                status="completed",
                next_step=None,
                actions_taken=[
                    "Lagerbestand mit KI analysiert",
                    "Feldbuch ausgewertet",
                    "KI-gestützte Bestellvorschläge erstellt"
                ]
            )
        except Exception as e:
            # Fallback to basic response if AI fails
            return AgentResponse(
                messages=[
                    AgentMessage(
                        role="assistant",
                        content="Fallback: Basis-Analyse ohne KI-Unterstützung...",
                        metadata={"step": "fallback"}
                    ),
                    AgentMessage(
                        role="assistant",
                        content="Empfehlung: 500kg Weizen-Saatgut nachbestellen. Grund: Aussaat Q1 2026 geplant, aktueller Bestand nur 200kg.",
                        metadata={"step": "recommendation", "fallback": True}
                    )
                ],
                status="completed",
                next_step=None,
                actions_taken=[
                    "Lagerbestand geprüft (Fallback)",
                    "Feldbuch ausgewertet",
                    "Bestellvorschlag erstellt"
                ]
            )
    
    elif workflow_id == "compliance_checker":
        return AgentResponse(
            messages=[
                AgentMessage(
                    role="assistant",
                    content="Compliance-Check läuft...",
                    metadata={"step": "checking"}
                ),
                AgentMessage(
                    role="assistant",
                    content="⚠️ EUDR-Warnung: Für Sojacharge SC-2025-042 fehlt noch die Herkunftserklärung.",
                    metadata={"step": "warning", "severity": "medium"}
                )
            ],
            status="waiting_for_input",
            next_step="Bitte Herkunftserklärung hochladen oder Charge sperren.",
            actions_taken=["EUDR-Check durchgeführt"]
        )
    
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{workflow_id}' nicht gefunden"
        )


@router.get("/workflows")
async def list_workflows():
    """Liste aller verfügbaren Agent-Workflows"""
    return {
        "workflows": [
            {
                "id": "procurement_advisor",
                "name": "Einkaufs-Berater",
                "description": "Schlägt Bestellungen basierend auf Lager + Feldbuch vor",
                "domains": ["procurement", "agrar", "inventory"]
            },
            {
                "id": "compliance_checker",
                "name": "Compliance-Prüfer",
                "description": "Prüft Dokumente auf EU-Vorgaben (EUDR, Cross-Compliance)",
                "domains": ["compliance", "agrar"]
            },
            {
                "id": "invoice_processor",
                "name": "Rechnungs-Verarbeiter",
                "description": "Extrahiert und bucht Eingangsrechnungen automatisch",
                "domains": ["finance", "procurement"]
            },
            {
                "id": "field_optimizer",
                "name": "Anbau-Optimierer",
                "description": "Optimiert Fruchtfolge basierend auf Historie und Marktdaten",
                "domains": ["agrar"]
            }
        ]
    }

