"""
Business Insights Endpoint
Generiert AI-basierte Insights und Prognosen
"""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class Insight(BaseModel):
    """Single business insight"""
    title: str
    description: str
    impact: str = Field(..., description="high, medium, low")
    category: str = Field(..., description="revenue, cost, risk, opportunity")
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_actions: List[str] = Field(default_factory=list)


class InsightsRequest(BaseModel):
    """Request for insights"""
    domain: str = Field(..., description="sales, finance, procurement, agrar, etc.")
    entity_id: Optional[str] = Field(None, description="Spezifische Entity (Kunde, Artikel, etc.)")
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class InsightsResponse(BaseModel):
    """Insights response"""
    insights: List[Insight]
    summary: str


@router.post("/generate", response_model=InsightsResponse)
async def generate_insights(request: InsightsRequest) -> InsightsResponse:
    """
    Generiert AI-Insights für Domain/Entity
    
    Beispiele:
    - Kunden mit sinkenden Umsätzen
    - Artikel mit ungewöhnlichem Preisverfall
    - Lieferanten mit steigenden Lieferzeiten
    - Feldschläge mit sinkenden Erträgen
    """
    
    insights = []
    
    # Mock insights based on domain
    if request.domain == "sales":
        insights.append(Insight(
            title="Umsatzrückgang bei Top-Kunde",
            description="Kunde 'Müller Landwirtschaft' hat 35% weniger bestellt im Vergleich zu Q3 2024",
            impact="high",
            category="revenue",
            confidence=0.91,
            recommended_actions=[
                "Persönliches Gespräch vereinbaren",
                "Sonderangebot erstellen"
            ]
        ))
    
    elif request.domain == "procurement":
        insights.append(Insight(
            title="Lieferverzug bei Hauptlieferant",
            description="Lieferant 'Agro Supplies' liefert seit 4 Wochen 5-7 Tage verspätet",
            impact="medium",
            category="risk",
            confidence=0.84,
            recommended_actions=[
                "Alternative Lieferanten evaluieren",
                "Sicherheitsbestand erhöhen"
            ]
        ))
    
    elif request.domain == "agrar":
        insights.append(Insight(
            title="Ernteprognose überdurchschnittlich",
            description="Feldschlag 'Nordfeld A' zeigt 18% höheren Ertrag als Durchschnitt der letzten 3 Jahre",
            impact="medium",
            category="opportunity",
            confidence=0.76,
            recommended_actions=[
                "Vertriebsstrategie für Mehrertrag planen",
                "Anbaumethode auf andere Schläge übertragen"
            ]
        ))
    
    summary = f"Gefunden: {len(insights)} relevante Insights für {request.domain}"
    
    return InsightsResponse(
        insights=insights,
        summary=summary
    )


@router.get("/customer/{customer_id}")
async def get_customer_insights(customer_id: str) -> InsightsResponse:
    """Spezifische Insights für einen Kunden"""
    return InsightsResponse(
        insights=[
            Insight(
                title="Kaufverhalten-Muster erkannt",
                description=f"Kunde {customer_id} bestellt regelmäßig Montags. Durchschnittliche Bestellmenge: 850kg.",
                impact="low",
                category="opportunity",
                confidence=0.72,
                recommended_actions=["Montag-Vormittag Verfügbarkeit sicherstellen"]
            )
        ],
        summary=f"1 Insight für Kunde {customer_id}"
    )


@router.get("/forecast/{domain}")
async def get_forecast(
    domain: str,
    horizon_days: int = 30
) -> dict:
    """
    Prognose für Domain
    
    Beispiel: Umsatzprognose, Lagerbestandsprognose, Ernteerträge
    """
    return {
        "domain": domain,
        "forecast": {
            "next_30_days": {
                "expected_value": 125000.0,
                "confidence_interval": [110000.0, 140000.0],
                "confidence": 0.78
            },
            "trend": "increasing",
            "factors": [
                "Saisonaler Anstieg (Frühjahr)",
                "3 neue Großkunden seit Q4 2024"
            ]
        }
    }

