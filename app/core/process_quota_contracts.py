from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class QuotaTyp(str, Enum):
    API_ANFRAGEN = "API_ANFRAGEN"
    SPEICHER_MB = "SPEICHER_MB"
    BENUTZER = "BENUTZER"
    DOKUMENTE = "DOKUMENTE"
    WORKFLOW_INSTANZEN = "WORKFLOW_INSTANZEN"


class QuotaStatus(str, Enum):
    NORMAL = "NORMAL"           # < 80%
    WARNUNG = "WARNUNG"         # >= 80% and < 95%
    KRITISCH = "KRITISCH"       # >= 95% and < 100%
    ERSCHOEPFT = "ERSCHOEPFT"   # >= 100%


class QuotaAktionsBei(str, Enum):
    WARNUNG = "WARNUNG"         # Notify at warning threshold
    KRITISCH = "KRITISCH"       # Restrict at critical
    ERSCHOEPFT = "ERSCHOEPFT"   # Block at exhausted


@dataclass
class QuotaRegel:
    regel_id: str
    quota_typ: QuotaTyp
    limit: float
    warnung_schwelle_pct: float = 80.0
    kritisch_schwelle_pct: float = 95.0
    aktion_bei: QuotaAktionsBei = QuotaAktionsBei.KRITISCH
    beschreibung: str = ""

    def berechne_status(self, verbrauch: float) -> QuotaStatus:
        """
        pct = verbrauch / limit * 100 (0.0 if limit == 0).
        >= 100 → ERSCHOEPFT
        >= kritisch_schwelle_pct → KRITISCH
        >= warnung_schwelle_pct → WARNUNG
        else → NORMAL
        """
        if self.limit <= 0:
            return QuotaStatus.NORMAL
        pct = (verbrauch / self.limit) * 100
        if pct >= 100:
            return QuotaStatus.ERSCHOEPFT
        elif pct >= self.kritisch_schwelle_pct:
            return QuotaStatus.KRITISCH
        elif pct >= self.warnung_schwelle_pct:
            return QuotaStatus.WARNUNG
        return QuotaStatus.NORMAL

    def verfuegbar(self, verbrauch: float) -> float:
        """Returns max(0.0, limit - verbrauch)."""
        return max(0.0, self.limit - verbrauch)


@dataclass
class TenantQuotaVerbrauch:
    tenant_id: str
    quota_typ: QuotaTyp
    verbrauch: float
    gemessen_am: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QuotaUebersicht:
    uebersicht_id: str
    tenant_id: str
    verbraeuche: list = field(default_factory=list)   # list[TenantQuotaVerbrauch]
    regeln: list = field(default_factory=list)        # list[QuotaRegel]

    def status_fuer_typ(self, quota_typ: QuotaTyp) -> QuotaStatus:
        """
        Finds matching Regel and Verbrauch for quota_typ.
        Returns NORMAL if no regel found.
        """
        regel = next((r for r in self.regeln if r.quota_typ == quota_typ), None)
        if regel is None:
            return QuotaStatus.NORMAL
        verbrauch_obj = next((v for v in self.verbraeuche if v.quota_typ == quota_typ), None)
        verbrauch = verbrauch_obj.verbrauch if verbrauch_obj else 0.0
        return regel.berechne_status(verbrauch)

    def kritische_quotas(self) -> list:
        """Returns quota_types where status is KRITISCH or ERSCHOEPFT."""
        return [
            qt for qt in QuotaTyp
            if self.status_fuer_typ(qt) in (QuotaStatus.KRITISCH, QuotaStatus.ERSCHOEPFT)
        ]


def get_default_quota_uebersicht() -> QuotaUebersicht:
    now = datetime(2026, 3, 16, 10, 0, 0)
    uebersicht = QuotaUebersicht("QU-001", "TENANT-A")
    uebersicht.regeln = [
        QuotaRegel("QR-001", QuotaTyp.API_ANFRAGEN, 10000.0, 80.0, 95.0, QuotaAktionsBei.KRITISCH, "API-Limit/Tag"),
        QuotaRegel("QR-002", QuotaTyp.SPEICHER_MB, 51200.0, 80.0, 95.0, QuotaAktionsBei.WARNUNG, "50GB Speicher"),
        QuotaRegel("QR-003", QuotaTyp.BENUTZER, 50.0, 80.0, 95.0, QuotaAktionsBei.ERSCHOEPFT, "Lizenz-Benutzer"),
        QuotaRegel("QR-004", QuotaTyp.DOKUMENTE, 100000.0, 80.0, 95.0, QuotaAktionsBei.KRITISCH, "Dokumente"),
        QuotaRegel("QR-005", QuotaTyp.WORKFLOW_INSTANZEN, 1000.0, 80.0, 95.0, QuotaAktionsBei.KRITISCH, "Workflow-Instanzen"),
    ]
    uebersicht.verbraeuche = [
        TenantQuotaVerbrauch("TENANT-A", QuotaTyp.API_ANFRAGEN, 7500.0, now),      # 75% → NORMAL
        TenantQuotaVerbrauch("TENANT-A", QuotaTyp.SPEICHER_MB, 42000.0, now),      # 82% → WARNUNG
        TenantQuotaVerbrauch("TENANT-A", QuotaTyp.BENUTZER, 48.0, now),            # 96% → KRITISCH
        TenantQuotaVerbrauch("TENANT-A", QuotaTyp.DOKUMENTE, 100500.0, now),       # >100% → ERSCHOEPFT
        TenantQuotaVerbrauch("TENANT-A", QuotaTyp.WORKFLOW_INSTANZEN, 500.0, now), # 50% → NORMAL
    ]
    return uebersicht
