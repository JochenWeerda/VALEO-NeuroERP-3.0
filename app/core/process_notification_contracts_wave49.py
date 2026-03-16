"""
Process Notification Contracts — Wave 49
Benachrichtigungsvorlagen, Kanal-Routing und Zustellverfolgung
fuer Workflow-Ereignisse.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NotifikationsKanal(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    IN_APP = "IN_APP"
    WEBHOOK = "WEBHOOK"


class NotifikationsPrioritaet(str, Enum):
    NIEDRIG = "NIEDRIG"
    NORMAL = "NORMAL"
    HOCH = "HOCH"
    KRITISCH = "KRITISCH"


class ZustellStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    VERSENDET = "VERSENDET"
    ZUGESTELLT = "ZUGESTELLT"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    GEDROSSELT = "GEDROSSELT"


@dataclass
class NotifikationsVorlage:
    """Vorlage fuer eine Workflow-Benachrichtigung."""
    vorlage_id: str
    vorlage_name: str
    kanal: NotifikationsKanal
    prioritaet: NotifikationsPrioritaet
    betreff_template: str
    nachricht_template: str
    platzhalter: list[str] = field(default_factory=list)
    beschreibung: str = ""

    def render(self, kontext: dict[str, Any]) -> tuple[str, str]:
        """Rendert Betreff und Nachricht. Unbekannte Platzhalter bleiben unveraendert."""
        betreff = self.betreff_template
        nachricht = self.nachricht_template
        for key, value in kontext.items():
            placeholder = "{{" + key + "}}"
            betreff = betreff.replace(placeholder, str(value))
            nachricht = nachricht.replace(placeholder, str(value))
        return betreff, nachricht

    def as_dict(self) -> dict[str, Any]:
        return {
            "vorlage_id": self.vorlage_id,
            "vorlage_name": self.vorlage_name,
            "kanal": self.kanal.value,
            "prioritaet": self.prioritaet.value,
            "betreff_template": self.betreff_template,
            "nachricht_template": self.nachricht_template,
            "platzhalter": self.platzhalter,
            "beschreibung": self.beschreibung,
        }


@dataclass
class NotifikationsZustellung:
    """Zustellprotokoll fuer eine einzelne Benachrichtigung."""
    zustellung_id: str
    vorlage_id: str
    empfaenger_id: str
    kanal: NotifikationsKanal
    prioritaet: NotifikationsPrioritaet
    betreff: str
    nachricht: str
    status: ZustellStatus
    versuch_anzahl: int = 0
    fehlermeldung: str = ""
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    zugestellt_am: datetime | None = None

    @property
    def ist_zugestellt(self) -> bool:
        return self.status == ZustellStatus.ZUGESTELLT

    @property
    def ist_fehlgeschlagen(self) -> bool:
        return self.status == ZustellStatus.FEHLGESCHLAGEN

    def as_dict(self) -> dict[str, Any]:
        return {
            "zustellung_id": self.zustellung_id,
            "vorlage_id": self.vorlage_id,
            "empfaenger_id": self.empfaenger_id,
            "kanal": self.kanal.value,
            "prioritaet": self.prioritaet.value,
            "betreff": self.betreff,
            "nachricht": self.nachricht,
            "status": self.status.value,
            "versuch_anzahl": self.versuch_anzahl,
            "fehlermeldung": self.fehlermeldung,
            "ist_zugestellt": self.ist_zugestellt,
            "ist_fehlgeschlagen": self.ist_fehlgeschlagen,
            "erstellt_am": self.erstellt_am.isoformat(),
            "zugestellt_am": self.zugestellt_am.isoformat() if self.zugestellt_am else None,
        }


@dataclass
class ZustellStatistik:
    """Aggregierte Zustellstatistik fuer einen Kanal."""
    kanal: NotifikationsKanal
    gesamt: int
    zugestellt: int
    fehlgeschlagen: int
    ausstehend: int

    @property
    def erfolgsrate_pct(self) -> float:
        if self.gesamt == 0:
            return 0.0
        return round(self.zugestellt / self.gesamt * 100, 2)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kanal": self.kanal.value,
            "gesamt": self.gesamt,
            "zugestellt": self.zugestellt,
            "fehlgeschlagen": self.fehlgeschlagen,
            "ausstehend": self.ausstehend,
            "erfolgsrate_pct": self.erfolgsrate_pct,
        }


def erstelle_zustellung(
    zustellung_id: str,
    vorlage: NotifikationsVorlage,
    empfaenger_id: str,
    kontext: dict[str, Any],
    erstellt_am: datetime | None = None,
) -> NotifikationsZustellung:
    """Erzeugt eine neue Zustellung auf Basis einer Vorlage."""
    betreff, nachricht = vorlage.render(kontext)
    return NotifikationsZustellung(
        zustellung_id=zustellung_id,
        vorlage_id=vorlage.vorlage_id,
        empfaenger_id=empfaenger_id,
        kanal=vorlage.kanal,
        prioritaet=vorlage.prioritaet,
        betreff=betreff,
        nachricht=nachricht,
        status=ZustellStatus.AUSSTEHEND,
        erstellt_am=erstellt_am or datetime.utcnow(),
    )


def berechne_zustellstatistik(
    zustellungen: list[NotifikationsZustellung],
    kanal: NotifikationsKanal,
) -> ZustellStatistik:
    """Aggregiert Zustellstatistik fuer einen bestimmten Kanal."""
    relevant = [z for z in zustellungen if z.kanal == kanal]
    return ZustellStatistik(
        kanal=kanal,
        gesamt=len(relevant),
        zugestellt=sum(1 for z in relevant if z.status == ZustellStatus.ZUGESTELLT),
        fehlgeschlagen=sum(1 for z in relevant if z.status == ZustellStatus.FEHLGESCHLAGEN),
        ausstehend=sum(1 for z in relevant if z.status == ZustellStatus.AUSSTEHEND),
    )


def get_default_notifikations_vorlagen() -> list[NotifikationsVorlage]:
    """Gibt 5 Standard-Benachrichtigungsvorlagen zurueck."""
    return [
        NotifikationsVorlage(
            vorlage_id="NV-001",
            vorlage_name="Kontrakt-Freigabe-Anfrage",
            kanal=NotifikationsKanal.EMAIL,
            prioritaet=NotifikationsPrioritaet.HOCH,
            betreff_template="Freigabe erforderlich: Kontrakt {{kontrakt_id}}",
            nachricht_template=(
                "Sehr geehrte/r {{empfaenger_name}},\n\n"
                "Kontrakt {{kontrakt_id}} ueber {{betrag_eur}} EUR erfordert Ihre Freigabe.\n"
                "Bitte pruefen Sie innerhalb von {{frist_stunden}} Stunden."
            ),
            platzhalter=["kontrakt_id", "empfaenger_name", "betrag_eur", "frist_stunden"],
            beschreibung="E-Mail-Anfrage zur Kontrakt-Freigabe",
        ),
        NotifikationsVorlage(
            vorlage_id="NV-002",
            vorlage_name="Timeout-Warnung Push",
            kanal=NotifikationsKanal.PUSH,
            prioritaet=NotifikationsPrioritaet.HOCH,
            betreff_template="Frist laeuft ab: {{aufgabe_name}}",
            nachricht_template="Aufgabe {{aufgabe_name}} laeuft in {{verbleibend_min}} Minuten ab.",
            platzhalter=["aufgabe_name", "verbleibend_min"],
            beschreibung="Push-Warnung bei nahender Timeout-Grenze",
        ),
        NotifikationsVorlage(
            vorlage_id="NV-003",
            vorlage_name="Settlement-Eskalation SMS",
            kanal=NotifikationsKanal.SMS,
            prioritaet=NotifikationsPrioritaet.KRITISCH,
            betreff_template="ESKALATION Settlement {{settlement_id}}",
            nachricht_template="Settlement {{settlement_id}} ({{tenant_id}}) eskaliert an {{eskalations_ziel}}.",
            platzhalter=["settlement_id", "tenant_id", "eskalations_ziel"],
            beschreibung="SMS-Eskalation bei ueberfaelligem Settlement",
        ),
        NotifikationsVorlage(
            vorlage_id="NV-004",
            vorlage_name="Batch-Abschluss In-App",
            kanal=NotifikationsKanal.IN_APP,
            prioritaet=NotifikationsPrioritaet.NORMAL,
            betreff_template="Batch-Job abgeschlossen: {{batch_name}}",
            nachricht_template=(
                "Batch-Job {{batch_name}} abgeschlossen. "
                "{{erfolgreiche_chunks}} von {{gesamt_chunks}} Chunks erfolgreich."
            ),
            platzhalter=["batch_name", "erfolgreiche_chunks", "gesamt_chunks"],
            beschreibung="In-App-Meldung nach Batch-Job-Abschluss",
        ),
        NotifikationsVorlage(
            vorlage_id="NV-005",
            vorlage_name="Compliance-Alarm Webhook",
            kanal=NotifikationsKanal.WEBHOOK,
            prioritaet=NotifikationsPrioritaet.KRITISCH,
            betreff_template="COMPLIANCE-ALARM: {{regel_id}}",
            nachricht_template='{"alarm":"{{regel_id}}","tenant":"{{tenant_id}}","ts":"{{zeitstempel}}"}',
            platzhalter=["regel_id", "tenant_id", "zeitstempel"],
            beschreibung="Webhook-Alarm bei Compliance-Verstoss",
        ),
    ]
