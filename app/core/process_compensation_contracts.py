"""
Process Compensation Contracts — Wave 42
Saga-Pattern für verteilte Prozesse: Kompensations-Transaktionen,
Rollback-Ketten und Fehlerbehebungs-Workflows bei Prozessabbruch.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class KompensationsStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    NICHT_ERFORDERLICH = "NICHT_ERFORDERLICH"


class KompensationsTyp(str, Enum):
    RUECKGAENGIG = "RUECKGAENGIG"        # Aktion vollständig rückgängig machen
    AUSGLEICH = "AUSGLEICH"              # Ausgleichsbuchung / Gegenbuchung
    BENACHRICHTIGUNG = "BENACHRICHTIGUNG"  # Betroffene Parteien informieren
    MANUELL = "MANUELL"                  # Manueller Eingriff erforderlich


class SagaStatus(str, Enum):
    AKTIV = "AKTIV"
    KOMPENSIEREND = "KOMPENSIEREND"  # Kompensation läuft
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"


# ---------------------------------------------------------------------------
# Kompensations-Schritt
# ---------------------------------------------------------------------------

@dataclass
class KompensationsSchritt:
    """Ein einzelner Schritt in einer Kompensationskette."""
    schritt_id: str
    workflow_instanz_id: str
    aktion_id: str               # Ausgeführte Aktion, die rückgängig gemacht werden soll
    kompensations_aktion: str    # Bezeichnung der Kompensationsmaßnahme
    kompensations_typ: KompensationsTyp
    reihenfolge: int             # Ausführungsreihenfolge (aufsteigend)
    status: KompensationsStatus = KompensationsStatus.AUSSTEHEND
    fehlermeldung: str = ""
    ausgefuehrt_am: datetime | None = None

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.status in {
            KompensationsStatus.ABGESCHLOSSEN,
            KompensationsStatus.NICHT_ERFORDERLICH,
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "schritt_id": self.schritt_id,
            "workflow_instanz_id": self.workflow_instanz_id,
            "aktion_id": self.aktion_id,
            "kompensations_aktion": self.kompensations_aktion,
            "kompensations_typ": self.kompensations_typ.value,
            "reihenfolge": self.reihenfolge,
            "status": self.status.value,
            "ist_abgeschlossen": self.ist_abgeschlossen,
            "fehlermeldung": self.fehlermeldung,
            "ausgefuehrt_am": self.ausgefuehrt_am.isoformat() if self.ausgefuehrt_am else None,
        }


# ---------------------------------------------------------------------------
# Kompensationskette
# ---------------------------------------------------------------------------

@dataclass
class KompensationsKette:
    """
    Geordnete Kette von Kompensationsschritten für eine Workflow-Instanz.

    Kompensation wird in umgekehrter Ausführungsreihenfolge abgearbeitet
    (höchste reihenfolge zuerst).
    """
    kette_id: str
    workflow_instanz_id: str
    tenant_id: str
    ausgeloest_am: datetime
    schritte: list[KompensationsSchritt] = field(default_factory=list)

    @property
    def ist_vollstaendig(self) -> bool:
        """True wenn alle Schritte abgeschlossen oder nicht erforderlich sind."""
        if not self.schritte:
            return True
        return all(s.ist_abgeschlossen for s in self.schritte)

    @property
    def naechster_schritt(self) -> KompensationsSchritt | None:
        """Nächster ausstehender Schritt (höchste reihenfolge unter AUSSTEHEND)."""
        ausstehend = [
            s for s in self.schritte
            if s.status == KompensationsStatus.AUSSTEHEND
        ]
        if not ausstehend:
            return None
        return max(ausstehend, key=lambda s: s.reihenfolge)

    @property
    def fehlgeschlagene_schritte(self) -> list[KompensationsSchritt]:
        return [s for s in self.schritte if s.status == KompensationsStatus.FEHLGESCHLAGEN]

    @property
    def saga_status(self) -> SagaStatus:
        if self.ist_vollstaendig and not self.fehlgeschlagene_schritte:
            return SagaStatus.ABGESCHLOSSEN
        if self.fehlgeschlagene_schritte:
            return SagaStatus.FEHLGESCHLAGEN
        if any(s.status == KompensationsStatus.LAUFEND for s in self.schritte):
            return SagaStatus.KOMPENSIEREND
        return SagaStatus.AKTIV

    def as_dict(self) -> dict[str, Any]:
        return {
            "kette_id": self.kette_id,
            "workflow_instanz_id": self.workflow_instanz_id,
            "tenant_id": self.tenant_id,
            "ausgeloest_am": self.ausgeloest_am.isoformat(),
            "schritte_anzahl": len(self.schritte),
            "ist_vollstaendig": self.ist_vollstaendig,
            "fehlgeschlagene_anzahl": len(self.fehlgeschlagene_schritte),
            "saga_status": self.saga_status.value,
            "schritte": [s.as_dict() for s in self.schritte],
        }


# ---------------------------------------------------------------------------
# Saga-Definition
# ---------------------------------------------------------------------------

@dataclass
class SagaDefinition:
    """
    Vorlage für eine Kompensationskette eines bestimmten Workflow-Typs.

    schritte_vorlage: geordnete Liste von {aktion_id, kompensations_aktion, typ}
    """
    saga_id: str
    saga_name: str
    workflow_typ: str
    schritte_vorlage: list[dict[str, str]] = field(default_factory=list)
    beschreibung: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "saga_id": self.saga_id,
            "saga_name": self.saga_name,
            "workflow_typ": self.workflow_typ,
            "schritte_anzahl": len(self.schritte_vorlage),
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def erstelle_kompensations_kette(
    workflow_instanz_id: str,
    saga: SagaDefinition,
    tenant_id: str,
    ausgeloest_am: datetime | None = None,
) -> KompensationsKette:
    """
    Erstellt eine Kompensationskette aus einer Saga-Definition.

    Schritte werden in der Reihenfolge der Vorlage nummeriert;
    Kompensation erfolgt dann in umgekehrter Reihenfolge (naechster_schritt).
    """
    if ausgeloest_am is None:
        ausgeloest_am = datetime.utcnow()

    schritte = []
    for i, vorlage in enumerate(saga.schritte_vorlage, start=1):
        schritt = KompensationsSchritt(
            schritt_id=f"{workflow_instanz_id}-KS-{i:03d}",
            workflow_instanz_id=workflow_instanz_id,
            aktion_id=vorlage.get("aktion_id", f"AKTION-{i}"),
            kompensations_aktion=vorlage.get("kompensations_aktion", f"Kompensation-{i}"),
            kompensations_typ=KompensationsTyp(
                vorlage.get("typ", KompensationsTyp.RUECKGAENGIG.value)
            ),
            reihenfolge=i,
        )
        schritte.append(schritt)

    return KompensationsKette(
        kette_id=f"KK-{workflow_instanz_id}",
        workflow_instanz_id=workflow_instanz_id,
        tenant_id=tenant_id,
        ausgeloest_am=ausgeloest_am,
        schritte=schritte,
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_saga_definitionen() -> list[SagaDefinition]:
    """Gibt 3 Standard-Saga-Definitionen zurück."""
    return [
        SagaDefinition(
            saga_id="SAGA-001",
            saga_name="Kontrakt-Storno",
            workflow_typ="kontrakt_annahme",
            beschreibung="Stornierung eines bereits freigegebenen Kontrakts mit GoBD-Gegenbuchung",
            schritte_vorlage=[
                {
                    "aktion_id": "FREIGABE_ERTEILT",
                    "kompensations_aktion": "Freigabe widerrufen und Storno-Protokoll anlegen",
                    "typ": KompensationsTyp.RUECKGAENGIG.value,
                },
                {
                    "aktion_id": "SETTLEMENT_ERSTELLT",
                    "kompensations_aktion": "Settlement-Gegenbuchung erzeugen",
                    "typ": KompensationsTyp.AUSGLEICH.value,
                },
                {
                    "aktion_id": "BELEG_ARCHIVIERT",
                    "kompensations_aktion": "Stornobeleg im DMS archivieren",
                    "typ": KompensationsTyp.RUECKGAENGIG.value,
                },
                {
                    "aktion_id": "LIEFERANT_BENACHRICHTIGT",
                    "kompensations_aktion": "Lieferant über Storno informieren",
                    "typ": KompensationsTyp.BENACHRICHTIGUNG.value,
                },
            ],
        ),
        SagaDefinition(
            saga_id="SAGA-002",
            saga_name="Settlement-Rueckbuchung",
            workflow_typ="settlement_freigabe",
            beschreibung="Rückbuchung eines fehlerhaften Settlements nach 4-Augen-Fehler",
            schritte_vorlage=[
                {
                    "aktion_id": "ZAHLUNG_AUSGEFUEHRT",
                    "kompensations_aktion": "Rückbuchungsauftrag an Bank übermitteln",
                    "typ": KompensationsTyp.AUSGLEICH.value,
                },
                {
                    "aktion_id": "BUCHUNG_ERSTELLT",
                    "kompensations_aktion": "Gegenbuchung im Journal anlegen",
                    "typ": KompensationsTyp.AUSGLEICH.value,
                },
                {
                    "aktion_id": "FREIGABE_PROTOKOLL",
                    "kompensations_aktion": "Freigabe-Protokoll korrigieren (manuell)",
                    "typ": KompensationsTyp.MANUELL.value,
                },
            ],
        ),
        SagaDefinition(
            saga_id="SAGA-003",
            saga_name="AP-Rechnung-Ablehnung",
            workflow_typ="ap_approval",
            beschreibung="Ablehnung einer AP-Rechnung im Genehmigungsworkflow",
            schritte_vorlage=[
                {
                    "aktion_id": "RECHNUNG_ERFASST",
                    "kompensations_aktion": "Rechnung auf Status ABGELEHNT setzen",
                    "typ": KompensationsTyp.RUECKGAENGIG.value,
                },
                {
                    "aktion_id": "KOSTENSTELLE_BELASTET",
                    "kompensations_aktion": "Kostenstellenreservierung freigeben",
                    "typ": KompensationsTyp.AUSGLEICH.value,
                },
                {
                    "aktion_id": "LIEFERANT_KONTAKTIERT",
                    "kompensations_aktion": "Lieferant über Ablehnung benachrichtigen",
                    "typ": KompensationsTyp.BENACHRICHTIGUNG.value,
                },
            ],
        ),
    ]
