"""
Prozess-Benachrichtigungs-Contracts — Wave 39
Workflow-Notification, Alert-Subscriptions, Kanal-Routing
und Eskalations-Contracts für den Process-Kernel.

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

class NotifikationsKanal(str, Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    WEBHOOK = "WEBHOOK"
    PUSH = "PUSH"
    SLACK = "SLACK"
    TEAMS = "TEAMS"


class NotifikationsAusloeser(str, Enum):
    WORKFLOW_SCHRITT = "WORKFLOW_SCHRITT"
    SLA_VERLETZUNG = "SLA_VERLETZUNG"
    FREIGABE_ERFORDERLICH = "FREIGABE_ERFORDERLICH"
    FREIGABE_ERTEILT = "FREIGABE_ERTEILT"
    FEHLER_AUFGETRETEN = "FEHLER_AUFGETRETEN"
    ABSCHLUSS = "ABSCHLUSS"
    ABWEICHUNGSALARM = "ABWEICHUNGSALARM"
    DEADLINE_NAEHERT_SICH = "DEADLINE_NAEHERT_SICH"
    ESKALATION = "ESKALATION"


class NotifikationsPrioritaet(str, Enum):
    KRITISCH = "KRITISCH"    # Sofortige Zustellung auf allen Kanälen
    HOCH = "HOCH"            # Zustellung < 5 min
    NORMAL = "NORMAL"        # Zustellung < 30 min (Batch)
    NIEDRIG = "NIEDRIG"      # Tägliche Digest-Zusammenfassung


class NotifikationsStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    ZUGESTELLT = "ZUGESTELLT"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    GELESEN = "GELESEN"
    IGNORIERT = "IGNORIERT"


class EskalationsGrund(str, Enum):
    KEINE_REAKTION = "KEINE_REAKTION"
    SLA_UEBERSCHRITTEN = "SLA_UEBERSCHRITTEN"
    FEHLERHAEUFT_SICH = "FEHLERHAEUFT_SICH"
    MANUELL = "MANUELL"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class NotifikationsAbonnement:
    """
    Abonnement: Wer will bei welchem Auslöser auf welchen Kanälen
    benachrichtigt werden?
    """
    abo_id: str
    empfaenger_rolle: str          # "sachbearbeiter", "leiter", "admin" etc.
    empfaenger_id: str             # user_id oder "*" für alle der Rolle
    ausloeser: list[NotifikationsAusloeser]
    kanaele: list[NotifikationsKanal]
    min_prioritaet: NotifikationsPrioritaet = NotifikationsPrioritaet.NORMAL
    domain: str = ""               # "" = alle Domains
    prozess_typ: str = ""          # "" = alle Prozesstypen
    aktiv: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "abo_id": self.abo_id,
            "empfaenger_rolle": self.empfaenger_rolle,
            "empfaenger_id": self.empfaenger_id,
            "ausloeser": [a.value for a in self.ausloeser],
            "kanaele": [k.value for k in self.kanaele],
            "min_prioritaet": self.min_prioritaet.value,
            "domain": self.domain,
            "prozess_typ": self.prozess_typ,
            "aktiv": self.aktiv,
        }


@dataclass
class NotifikationsNachricht:
    """Eine erzeugte Benachrichtigung."""
    nachricht_id: str
    ausloeser: NotifikationsAusloeser
    titel: str
    inhalt: str
    empfaenger_ids: list[str]
    kanaele: list[NotifikationsKanal]
    prioritaet: NotifikationsPrioritaet
    erstellt_am: datetime
    prozess_id: str = ""
    status: NotifikationsStatus = NotifikationsStatus.AUSSTEHEND
    metadaten: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "nachricht_id": self.nachricht_id,
            "ausloeser": self.ausloeser.value,
            "titel": self.titel,
            "inhalt": self.inhalt,
            "empfaenger_ids": self.empfaenger_ids,
            "kanaele": [k.value for k in self.kanaele],
            "prioritaet": self.prioritaet.value,
            "erstellt_am": self.erstellt_am.isoformat(),
            "prozess_id": self.prozess_id,
            "status": self.status.value,
            "metadaten": self.metadaten,
        }


@dataclass
class EskalationsRegel:
    """Regel für automatische Eskalation wenn keine Reaktion."""
    regel_id: str
    ausloeser: NotifikationsAusloeser
    wartezeit_minuten: int
    eskalations_grund: EskalationsGrund
    eskalations_empfaenger_rolle: str   # z.B. "leiter"
    eskalations_kanal: NotifikationsKanal = NotifikationsKanal.EMAIL
    max_eskalationen: int = 2

    def as_dict(self) -> dict[str, Any]:
        return {
            "regel_id": self.regel_id,
            "ausloeser": self.ausloeser.value,
            "wartezeit_minuten": self.wartezeit_minuten,
            "eskalations_grund": self.eskalations_grund.value,
            "eskalations_empfaenger_rolle": self.eskalations_empfaenger_rolle,
            "eskalations_kanal": self.eskalations_kanal.value,
            "max_eskalationen": self.max_eskalationen,
        }


@dataclass
class NotifikationsRoutingErgebnis:
    """Ergebnis des Routing-Checks: Wer bekommt diese Nachricht auf welchen Kanälen?"""
    ausloeser: NotifikationsAusloeser
    prioritaet: NotifikationsPrioritaet
    abonnenten: list[NotifikationsAbonnement]
    effektive_kanaele: list[NotifikationsKanal]
    eskalations_regel: EskalationsRegel | None

    @property
    def anzahl_empfaenger(self) -> int:
        return len(self.abonnenten)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ausloeser": self.ausloeser.value,
            "prioritaet": self.prioritaet.value,
            "anzahl_empfaenger": self.anzahl_empfaenger,
            "abonnenten": [a.as_dict() for a in self.abonnenten],
            "effektive_kanaele": [k.value for k in self.effektive_kanaele],
            "eskalations_regel": self.eskalations_regel.as_dict() if self.eskalations_regel else None,
        }


# ---------------------------------------------------------------------------
# Routing-Logik
# ---------------------------------------------------------------------------

# Prioritäts-Mapping nach Auslöser
_AUSLOESER_PRIORITAET: dict[NotifikationsAusloeser, NotifikationsPrioritaet] = {
    NotifikationsAusloeser.ESKALATION: NotifikationsPrioritaet.KRITISCH,
    NotifikationsAusloeser.SLA_VERLETZUNG: NotifikationsPrioritaet.KRITISCH,
    NotifikationsAusloeser.FEHLER_AUFGETRETEN: NotifikationsPrioritaet.HOCH,
    NotifikationsAusloeser.FREIGABE_ERFORDERLICH: NotifikationsPrioritaet.HOCH,
    NotifikationsAusloeser.ABWEICHUNGSALARM: NotifikationsPrioritaet.HOCH,
    NotifikationsAusloeser.DEADLINE_NAEHERT_SICH: NotifikationsPrioritaet.NORMAL,
    NotifikationsAusloeser.WORKFLOW_SCHRITT: NotifikationsPrioritaet.NORMAL,
    NotifikationsAusloeser.FREIGABE_ERTEILT: NotifikationsPrioritaet.NORMAL,
    NotifikationsAusloeser.ABSCHLUSS: NotifikationsPrioritaet.NIEDRIG,
}

# Prioritäts-Rangordnung
_PRIO_RANG: dict[NotifikationsPrioritaet, int] = {
    NotifikationsPrioritaet.KRITISCH: 3,
    NotifikationsPrioritaet.HOCH: 2,
    NotifikationsPrioritaet.NORMAL: 1,
    NotifikationsPrioritaet.NIEDRIG: 0,
}


def berechne_prioritaet(ausloeser: NotifikationsAusloeser) -> NotifikationsPrioritaet:
    """Gibt die Standard-Priorität für einen Auslöser zurück."""
    return _AUSLOESER_PRIORITAET.get(ausloeser, NotifikationsPrioritaet.NORMAL)


def route_benachrichtigung(
    ausloeser: NotifikationsAusloeser,
    domain: str = "",
    prozess_typ: str = "",
    abonnements: list[NotifikationsAbonnement] | None = None,
    eskalationsregeln: list[EskalationsRegel] | None = None,
) -> NotifikationsRoutingErgebnis:
    """
    Bestimmt Empfänger und Kanäle für einen Benachrichtigungs-Auslöser.

    Routing-Logik:
    1. Priorität aus Auslöser-Mapping
    2. Abonnements filtern: aktiv + ausloeser in abo.ausloeser
    3. Domain/Prozess-Filter: "" = alle; oder exakter Match
    4. Prioritäts-Filter: abo.min_prioritaet <= nachricht_prioritaet
    5. Effektive Kanäle = Union aller Kanal-Listen der Abonnenten
    6. Eskalationsregel suchen (erster passender Auslöser)
    """
    if abonnements is None:
        abonnements = get_default_abonnements()
    if eskalationsregeln is None:
        eskalationsregeln = get_default_eskalationsregeln()

    prioritaet = berechne_prioritaet(ausloeser)
    prio_rang = _PRIO_RANG[prioritaet]

    passende_abos: list[NotifikationsAbonnement] = []
    for abo in abonnements:
        if not abo.aktiv:
            continue
        if ausloeser not in abo.ausloeser:
            continue
        if abo.domain and domain and abo.domain != domain:
            continue
        if abo.prozess_typ and prozess_typ and abo.prozess_typ != prozess_typ:
            continue
        if _PRIO_RANG[abo.min_prioritaet] > prio_rang:
            continue
        passende_abos.append(abo)

    # Effektive Kanäle (Union)
    kanaele_set: set[NotifikationsKanal] = set()
    for abo in passende_abos:
        kanaele_set.update(abo.kanaele)
    effektive_kanaele = sorted(kanaele_set, key=lambda k: k.value)

    # Eskalationsregel
    esk_regel = next(
        (r for r in eskalationsregeln if r.ausloeser == ausloeser),
        None,
    )

    return NotifikationsRoutingErgebnis(
        ausloeser=ausloeser,
        prioritaet=prioritaet,
        abonnenten=passende_abos,
        effektive_kanaele=effektive_kanaele,
        eskalations_regel=esk_regel,
    )


def erstelle_benachrichtigung(
    nachricht_id: str,
    ausloeser: NotifikationsAusloeser,
    titel: str,
    inhalt: str,
    prozess_id: str = "",
    routing: NotifikationsRoutingErgebnis | None = None,
    jetzt: datetime | None = None,
) -> NotifikationsNachricht:
    """Erzeugt eine vollständige Benachrichtigung aus Routing-Ergebnis."""
    if jetzt is None:
        jetzt = datetime.utcnow()
    if routing is None:
        routing = route_benachrichtigung(ausloeser)

    empfaenger_ids = [a.empfaenger_id for a in routing.abonnenten]

    return NotifikationsNachricht(
        nachricht_id=nachricht_id,
        ausloeser=ausloeser,
        titel=titel,
        inhalt=inhalt,
        empfaenger_ids=empfaenger_ids,
        kanaele=routing.effektive_kanaele,
        prioritaet=routing.prioritaet,
        erstellt_am=jetzt,
        prozess_id=prozess_id,
    )


# ---------------------------------------------------------------------------
# Standard-Daten
# ---------------------------------------------------------------------------

def get_default_abonnements() -> list[NotifikationsAbonnement]:
    """Gibt 8 Standard-Abonnements zurück."""
    return [
        NotifikationsAbonnement(
            "ABO-001", "leiter", "*",
            ausloeser=[NotifikationsAusloeser.FREIGABE_ERFORDERLICH, NotifikationsAusloeser.ESKALATION,
                       NotifikationsAusloeser.SLA_VERLETZUNG],
            kanaele=[NotifikationsKanal.IN_APP, NotifikationsKanal.EMAIL],
            min_prioritaet=NotifikationsPrioritaet.HOCH,
        ),
        NotifikationsAbonnement(
            "ABO-002", "sachbearbeiter", "*",
            ausloeser=[NotifikationsAusloeser.WORKFLOW_SCHRITT, NotifikationsAusloeser.FREIGABE_ERTEILT,
                       NotifikationsAusloeser.ABSCHLUSS],
            kanaele=[NotifikationsKanal.IN_APP],
            min_prioritaet=NotifikationsPrioritaet.NORMAL,
            domain="agrar",
        ),
        NotifikationsAbonnement(
            "ABO-003", "buchhaltung", "*",
            ausloeser=[NotifikationsAusloeser.FREIGABE_ERFORDERLICH, NotifikationsAusloeser.FEHLER_AUFGETRETEN],
            kanaele=[NotifikationsKanal.IN_APP, NotifikationsKanal.EMAIL],
            min_prioritaet=NotifikationsPrioritaet.HOCH,
            domain="finance",
        ),
        NotifikationsAbonnement(
            "ABO-004", "admin", "*",
            ausloeser=list(NotifikationsAusloeser),
            kanaele=[NotifikationsKanal.IN_APP, NotifikationsKanal.EMAIL, NotifikationsKanal.WEBHOOK],
            min_prioritaet=NotifikationsPrioritaet.NIEDRIG,
        ),
        NotifikationsAbonnement(
            "ABO-005", "leiter", "*",
            ausloeser=[NotifikationsAusloeser.ABWEICHUNGSALARM, NotifikationsAusloeser.DEADLINE_NAEHERT_SICH],
            kanaele=[NotifikationsKanal.IN_APP, NotifikationsKanal.TEAMS],
            min_prioritaet=NotifikationsPrioritaet.NORMAL,
        ),
        NotifikationsAbonnement(
            "ABO-006", "sachbearbeiter", "*",
            ausloeser=[NotifikationsAusloeser.ABWEICHUNGSALARM],
            kanaele=[NotifikationsKanal.IN_APP],
            min_prioritaet=NotifikationsPrioritaet.HOCH,
            domain="agrar",
            prozess_typ="wareneingang",
        ),
        NotifikationsAbonnement(
            "ABO-007", "agent_system", "agent-001",
            ausloeser=[NotifikationsAusloeser.ESKALATION, NotifikationsAusloeser.SLA_VERLETZUNG,
                       NotifikationsAusloeser.FEHLER_AUFGETRETEN],
            kanaele=[NotifikationsKanal.WEBHOOK],
            min_prioritaet=NotifikationsPrioritaet.KRITISCH,
        ),
        NotifikationsAbonnement(
            "ABO-008", "leiter", "*",
            ausloeser=[NotifikationsAusloeser.ABSCHLUSS],
            kanaele=[NotifikationsKanal.IN_APP],
            min_prioritaet=NotifikationsPrioritaet.NIEDRIG,
            domain="finance",
            prozess_typ="zahlungslauf",
        ),
    ]


def get_default_eskalationsregeln() -> list[EskalationsRegel]:
    """Gibt 5 Standard-Eskalationsregeln zurück."""
    return [
        EskalationsRegel(
            "ESK-001", NotifikationsAusloeser.FREIGABE_ERFORDERLICH,
            wartezeit_minuten=30,
            eskalations_grund=EskalationsGrund.KEINE_REAKTION,
            eskalations_empfaenger_rolle="leiter",
            eskalations_kanal=NotifikationsKanal.EMAIL,
        ),
        EskalationsRegel(
            "ESK-002", NotifikationsAusloeser.SLA_VERLETZUNG,
            wartezeit_minuten=0,   # Sofort
            eskalations_grund=EskalationsGrund.SLA_UEBERSCHRITTEN,
            eskalations_empfaenger_rolle="admin",
            eskalations_kanal=NotifikationsKanal.TEAMS,
            max_eskalationen=3,
        ),
        EskalationsRegel(
            "ESK-003", NotifikationsAusloeser.FEHLER_AUFGETRETEN,
            wartezeit_minuten=15,
            eskalations_grund=EskalationsGrund.FEHLERHAEUFT_SICH,
            eskalations_empfaenger_rolle="admin",
            eskalations_kanal=NotifikationsKanal.EMAIL,
        ),
        EskalationsRegel(
            "ESK-004", NotifikationsAusloeser.ABWEICHUNGSALARM,
            wartezeit_minuten=60,
            eskalations_grund=EskalationsGrund.KEINE_REAKTION,
            eskalations_empfaenger_rolle="leiter",
            eskalations_kanal=NotifikationsKanal.EMAIL,
        ),
        EskalationsRegel(
            "ESK-005", NotifikationsAusloeser.DEADLINE_NAEHERT_SICH,
            wartezeit_minuten=120,
            eskalations_grund=EskalationsGrund.KEINE_REAKTION,
            eskalations_empfaenger_rolle="leiter",
            eskalations_kanal=NotifikationsKanal.IN_APP,
            max_eskalationen=1,
        ),
    ]
