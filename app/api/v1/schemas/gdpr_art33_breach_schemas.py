"""Pydantic schemas for the gdpr art33 breach domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class BreachIn(BaseModel):
    """Eingabe-Schema für eine Datenpanne (Art. 33 Abs. 3 DSGVO)."""

    # a) Art der Verletzung
    breach_type: str = Field(
        ...,
        description="VERTRAULICHKEIT / INTEGRITAET / VERFUEGBARKEIT",
    )
    description: str = Field(..., max_length=2000, description="Beschreibung der Datenpanne")

    # Betroffene Personen und Datensätze
    data_categories: list[str] = Field(
        default_factory=list,
        description="Kategorien betroffener personenbezogener Daten",
    )
    persons_count_approx: int = Field(
        default=0,
        ge=0,
        description="Ungefähre Anzahl betroffener Personen",
    )
    records_count_approx: int = Field(
        default=0,
        ge=0,
        description="Ungefähre Anzahl betroffener Datensätze",
    )

    # b) DSB-Kontakt
    dpo_name: str = Field(default="", max_length=200, description="Name des Datenschutzbeauftragten")
    dpo_contact: str = Field(default="", max_length=500, description="Kontaktdaten DSB (E-Mail / Tel.)")

    # c) Wahrscheinliche Folgen
    likely_consequences: str = Field(
        default="",
        max_length=2000,
        description="Wahrscheinliche Folgen der Verletzung (Art. 33 Abs. 3 lit. c)",
    )

    # d) Maßnahmen
    measures_taken: str = Field(
        default="",
        max_length=2000,
        description="Ergriffene / vorgeschlagene Abhilfemaßnahmen (Art. 33 Abs. 3 lit. d)",
    )

    # Metadaten
    discovered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Zeitpunkt der Entdeckung (Fristbeginn für 72h-Meldepflicht)",
    )
    status: str = Field(
        default="ENTDECKT",
        description="ENTDECKT / IN_BEARBEITUNG / GEMELDET / ABGESCHLOSSEN",
    )
    internal_reference: str = Field(
        default="",
        max_length=100,
        description="Internes Aktenzeichen / Ticket-Nummer",
    )


class BreachOut(BreachIn):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    notified_at: Optional[datetime] = None
    notified_by: Optional[str] = None
    authority_reference: Optional[str] = None


class NotifyIn(BaseModel):
    notified_by: str = Field(..., max_length=200, description="Name / E-Mail der meldenden Person")
    authority_reference: str = Field(
        default="",
        max_length=200,
        description="Aktenzeichen der Datenschutzbehörde (falls bereits vergeben)",
    )

