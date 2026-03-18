from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class TemplateTyp(str, Enum):
    STANDARD = "STANDARD"
    SAISONAL = "SAISONAL"
    TENANT_SPEZIFISCH = "TENANT_SPEZIFISCH"
    REGULATORISCH = "REGULATORISCH"


class TemplateStatus(str, Enum):
    ENTWURF = "ENTWURF"
    AKTIV = "AKTIV"
    ARCHIVIERT = "ARCHIVIERT"
    VERALTET = "VERALTET"


class InstanzierungsStatus(str, Enum):
    ERFOLGREICH = "ERFOLGREICH"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    VALIDIERUNGSFEHLER = "VALIDIERUNGSFEHLER"


@dataclass
class ProzessSchritt_Template:
    schritt_id: str
    name: str
    pflicht: bool = True            # mandatory step
    reihenfolge: int = 0
    standarddauer_minuten: int = 0


@dataclass
class ProzessTemplate:
    template_id: str
    name: str
    workflow_typ: str
    template_typ: TemplateTyp
    status: TemplateStatus = TemplateStatus.ENTWURF
    version: str = "1.0.0"
    schritte: list = field(default_factory=list)   # list[ProzessSchritt_Template]
    pflicht_parameter: list = field(default_factory=list)  # list[str] — required keys
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    tenant_id: Optional[str] = None

    def ist_verwendbar(self) -> bool:
        """True only if status == AKTIV."""
        return self.status == TemplateStatus.AKTIV

    def pflicht_schritte(self) -> list:
        """Returns steps where pflicht==True, sorted by reihenfolge."""
        return sorted([s for s in self.schritte if s.pflicht], key=lambda s: s.reihenfolge)

    def geschaetzte_gesamtdauer_minuten(self) -> int:
        """Sum of standarddauer_minuten for all pflicht steps."""
        return sum(s.standarddauer_minuten for s in self.schritte if s.pflicht)


@dataclass
class InstanzierungsErgebnis:
    template_id: str
    status: InstanzierungsStatus
    workflow_instanz_id: Optional[str] = None
    fehler_nachricht: str = ""
    fehlende_parameter: list = field(default_factory=list)


def instanziere_template(
    template: ProzessTemplate,
    parameter: dict,
    neue_instanz_id: str,
) -> InstanzierungsErgebnis:
    """
    Validates template and parameters, returns InstanzierungsErgebnis.
    - Not AKTIV → FEHLGESCHLAGEN, "Template nicht aktiv"
    - Missing pflicht_parameter → VALIDIERUNGSFEHLER, lists missing keys
    - All ok → ERFOLGREICH, workflow_instanz_id set
    """
    if not template.ist_verwendbar():
        return InstanzierungsErgebnis(template.template_id, InstanzierungsStatus.FEHLGESCHLAGEN,
                                       fehler_nachricht="Template nicht aktiv")
    fehlend = [p for p in template.pflicht_parameter if p not in parameter]
    if fehlend:
        return InstanzierungsErgebnis(template.template_id, InstanzierungsStatus.VALIDIERUNGSFEHLER,
                                       fehlende_parameter=fehlend)
    return InstanzierungsErgebnis(template.template_id, InstanzierungsStatus.ERFOLGREICH,
                                   workflow_instanz_id=neue_instanz_id)


def get_default_templates() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)
    t1 = ProzessTemplate("PT-001", "Kontrakt-Standardprozess", "kontrakt_freigabe",
                          TemplateTyp.STANDARD, TemplateStatus.AKTIV, "2.1.0",
                          pflicht_parameter=["lieferant_id", "menge_tonnen", "preis_eur_t"])
    t1.schritte = [
        ProzessSchritt_Template("S1", "Erfassen", True, 1, 15),
        ProzessSchritt_Template("S2", "Validieren", True, 2, 10),
        ProzessSchritt_Template("S3", "Preisfreigabe", True, 3, 30),
        ProzessSchritt_Template("S4", "Dokumentieren", False, 4, 5),
        ProzessSchritt_Template("S5", "Archivieren", True, 5, 5),
    ]

    t2 = ProzessTemplate("PT-002", "Settlement-Schnellprozess", "settlement_ausfuehren",
                          TemplateTyp.STANDARD, TemplateStatus.AKTIV, "1.0.0",
                          pflicht_parameter=["kontrakt_id", "menge_ist"])
    t2.schritte = [
        ProzessSchritt_Template("S1", "Berechnen", True, 1, 20),
        ProzessSchritt_Template("S2", "Buchen", True, 2, 10),
        ProzessSchritt_Template("S3", "Benachrichtigen", False, 3, 2),
    ]

    t3 = ProzessTemplate("PT-003", "Altes Formular", "kontrakt_freigabe",
                          TemplateTyp.STANDARD, TemplateStatus.VERALTET, "1.0.0")

    return [t1, t2, t3]
