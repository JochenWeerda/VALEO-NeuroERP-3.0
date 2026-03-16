from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta


class EinwilligungsTyp(str, Enum):
    DATENVERARBEITUNG = "DATENVERARBEITUNG"
    MARKETING = "MARKETING"
    ANALYSE = "ANALYSE"
    DRITTANBIETER = "DRITTANBIETER"
    NOTWENDIG = "NOTWENDIG"         # Always required, cannot be withdrawn


class EinwilligungsStatus(str, Enum):
    ERTEILT = "ERTEILT"
    WIDERRUFEN = "WIDERRUFEN"
    AUSSTEHEND = "AUSSTEHEND"
    ABGELAUFEN = "ABGELAUFEN"


class RechtsgrundlageTyp(str, Enum):
    EINWILLIGUNG = "EINWILLIGUNG"                    # Art. 6(1)(a) DSGVO
    VERTRAG = "VERTRAG"                               # Art. 6(1)(b)
    RECHTLICHE_PFLICHT = "RECHTLICHE_PFLICHT"        # Art. 6(1)(c)
    BERECHTIGTES_INTERESSE = "BERECHTIGTES_INTERESSE"  # Art. 6(1)(f)


@dataclass
class Einwilligung:
    einwilligungs_id: str
    subjekt_id: str              # person/customer ID
    tenant_id: str
    typ: EinwilligungsTyp
    rechtsgrundlage: RechtsgrundlageTyp
    status: EinwilligungsStatus = EinwilligungsStatus.AUSSTEHEND
    erteilt_am: Optional[datetime] = None
    widerrufen_am: Optional[datetime] = None
    gueltig_bis: Optional[datetime] = None   # None = no expiry

    def ist_aktiv(self, jetzt: datetime) -> bool:
        """
        True if status==ERTEILT and (gueltig_bis is None or jetzt < gueltig_bis).
        NOTWENDIG type is always active if status==ERTEILT.
        """
        if self.status != EinwilligungsStatus.ERTEILT:
            return False
        if self.gueltig_bis is not None and jetzt >= self.gueltig_bis:
            return False
        return True

    def aktueller_status(self, jetzt: datetime) -> EinwilligungsStatus:
        """Returns ABGELAUFEN if ERTEILT but past gueltig_bis, else current status."""
        if (self.status == EinwilligungsStatus.ERTEILT
                and self.gueltig_bis is not None
                and jetzt >= self.gueltig_bis):
            return EinwilligungsStatus.ABGELAUFEN
        return self.status


@dataclass
class VerarbeitungsProtokoll:
    protokoll_id: str
    einwilligungs_id: str
    zweck: str
    verarbeitet_am: datetime
    verarbeitet_von: str         # system/service name
    datenkategorien: list = field(default_factory=list)  # list[str]


@dataclass
class EinwilligungsRegister:
    register_id: str
    tenant_id: str
    einwilligungen: list = field(default_factory=list)  # list[Einwilligung]

    def aktive_einwilligungen(self, jetzt: datetime) -> list:
        return [e for e in self.einwilligungen if e.ist_aktiv(jetzt)]

    def einwilligungen_nach_typ(self, typ: EinwilligungsTyp, jetzt: datetime) -> list:
        return [e for e in self.einwilligungen if e.typ == typ and e.ist_aktiv(jetzt)]

    def hat_gueltige_einwilligung(self, subjekt_id: str, typ: EinwilligungsTyp, jetzt: datetime) -> bool:
        return any(
            e for e in self.einwilligungen
            if e.subjekt_id == subjekt_id and e.typ == typ and e.ist_aktiv(jetzt)
        )


def get_default_einwilligungs_register() -> EinwilligungsRegister:
    now = datetime(2026, 3, 16, 10, 0, 0)
    register = EinwilligungsRegister("ER-001", "TENANT-A")
    register.einwilligungen = [
        Einwilligung("EW-001", "KUNDE-001", "TENANT-A", EinwilligungsTyp.DATENVERARBEITUNG,
                     RechtsgrundlageTyp.EINWILLIGUNG, EinwilligungsStatus.ERTEILT,
                     now - timedelta(days=30), None, now + timedelta(days=335)),
        Einwilligung("EW-002", "KUNDE-001", "TENANT-A", EinwilligungsTyp.MARKETING,
                     RechtsgrundlageTyp.EINWILLIGUNG, EinwilligungsStatus.WIDERRUFEN,
                     now - timedelta(days=60), now - timedelta(days=10), None),
        Einwilligung("EW-003", "KUNDE-002", "TENANT-A", EinwilligungsTyp.NOTWENDIG,
                     RechtsgrundlageTyp.VERTRAG, EinwilligungsStatus.ERTEILT,
                     now - timedelta(days=90), None, None),
        Einwilligung("EW-004", "KUNDE-002", "TENANT-A", EinwilligungsTyp.ANALYSE,
                     RechtsgrundlageTyp.BERECHTIGTES_INTERESSE, EinwilligungsStatus.ERTEILT,
                     now - timedelta(days=400), None, now - timedelta(days=35)),  # expired
        Einwilligung("EW-005", "KUNDE-003", "TENANT-A", EinwilligungsTyp.DATENVERARBEITUNG,
                     RechtsgrundlageTyp.RECHTLICHE_PFLICHT, EinwilligungsStatus.AUSSTEHEND,
                     None, None, None),
    ]
    return register
