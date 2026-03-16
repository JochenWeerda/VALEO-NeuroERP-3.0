from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import hashlib
import json
from datetime import datetime


class AuditAktionsTyp(str, Enum):
    ERSTELLT = "ERSTELLT"
    GEAENDERT = "GEAENDERT"
    FREIGEGEBEN = "FREIGEGEBEN"
    ABGELEHNT = "ABGELEHNT"
    GELOESCHT = "GELOESCHT"
    EXPORTIERT = "EXPORTIERT"
    ANGEMELDET = "ANGEMELDET"


class AuditIntegritaetsStatus(str, Enum):
    GUELTIG = "GUELTIG"
    UNGUELTIG = "UNGUELTIG"     # Hash mismatch
    UNBEKANNT = "UNBEKANNT"     # Cannot verify


@dataclass
class AuditEintrag:
    eintrag_id: str
    workflow_instanz_id: str
    aktion: AuditAktionsTyp
    ausgefuehrt_von: str
    zeitstempel: datetime
    nutzlast: dict = field(default_factory=dict)
    vorgaenger_hash: str = ""   # hash of previous entry ("" for first)
    eintrag_hash: str = ""      # computed hash of this entry

    def berechne_hash(self) -> str:
        """
        Computes SHA256 of:
        f"{eintrag_id}|{workflow_instanz_id}|{aktion}|{ausgefuehrt_von}|{zeitstempel.isoformat()}|{vorgaenger_hash}|{json.dumps(nutzlast, sort_keys=True)}"
        Returns hex digest.
        """
        inhalt = (
            f"{self.eintrag_id}|{self.workflow_instanz_id}|{self.aktion}|"
            f"{self.ausgefuehrt_von}|{self.zeitstempel.isoformat()}|"
            f"{self.vorgaenger_hash}|{json.dumps(self.nutzlast, sort_keys=True)}"
        )
        return hashlib.sha256(inhalt.encode("utf-8")).hexdigest()

    def ist_hash_gueltig(self) -> bool:
        """Returns True if eintrag_hash == berechne_hash()."""
        return self.eintrag_hash == self.berechne_hash()


@dataclass
class AuditTrail:
    trail_id: str
    eintraege: list = field(default_factory=list)  # list[AuditEintrag], ordered by zeitstempel

    def pruefe_integritaet(self) -> AuditIntegritaetsStatus:
        """
        Verifies entire chain:
        - First entry must have vorgaenger_hash == ""
        - Each entry's eintrag_hash must equal berechne_hash()
        - Each entry's vorgaenger_hash must equal previous entry's eintrag_hash
        Returns GUELTIG if all checks pass, UNGUELTIG if any fail, UNBEKANNT if empty.
        """
        if not self.eintraege:
            return AuditIntegritaetsStatus.UNBEKANNT
        sortiert = sorted(self.eintraege, key=lambda e: e.zeitstempel)
        for i, eintrag in enumerate(sortiert):
            if not eintrag.ist_hash_gueltig():
                return AuditIntegritaetsStatus.UNGUELTIG
            if i == 0:
                if eintrag.vorgaenger_hash != "":
                    return AuditIntegritaetsStatus.UNGUELTIG
            else:
                if eintrag.vorgaenger_hash != sortiert[i - 1].eintrag_hash:
                    return AuditIntegritaetsStatus.UNGUELTIG
        return AuditIntegritaetsStatus.GUELTIG

    def letzter_eintrag(self) -> Optional[object]:
        if not self.eintraege:
            return None
        return max(self.eintraege, key=lambda e: e.zeitstempel)


def erstelle_audit_eintrag(
    eintrag_id: str,
    workflow_instanz_id: str,
    aktion: AuditAktionsTyp,
    ausgefuehrt_von: str,
    zeitstempel: datetime,
    nutzlast: dict,
    vorgaenger_hash: str = "",
) -> AuditEintrag:
    """Creates AuditEintrag and computes its hash."""
    eintrag = AuditEintrag(
        eintrag_id=eintrag_id,
        workflow_instanz_id=workflow_instanz_id,
        aktion=aktion,
        ausgefuehrt_von=ausgefuehrt_von,
        zeitstempel=zeitstempel,
        nutzlast=nutzlast,
        vorgaenger_hash=vorgaenger_hash,
    )
    eintrag.eintrag_hash = eintrag.berechne_hash()
    return eintrag


def get_default_audit_trail() -> AuditTrail:
    """Returns a valid AuditTrail with 4 entries for workflow WI-K-001."""
    now = datetime(2026, 3, 16, 10, 0, 0)
    from datetime import timedelta
    trail = AuditTrail("AT-001")
    e1 = erstelle_audit_eintrag("AE-001", "WI-K-001", AuditAktionsTyp.ERSTELLT, "user-001", now, {"kontrakt_nr": "K-001"})
    e2 = erstelle_audit_eintrag("AE-002", "WI-K-001", AuditAktionsTyp.GEAENDERT, "user-001", now + timedelta(minutes=5), {"feld": "menge"}, e1.eintrag_hash)
    e3 = erstelle_audit_eintrag("AE-003", "WI-K-001", AuditAktionsTyp.FREIGEGEBEN, "user-002", now + timedelta(minutes=10), {"kommentar": "OK"}, e2.eintrag_hash)
    e4 = erstelle_audit_eintrag("AE-004", "WI-K-001", AuditAktionsTyp.EXPORTIERT, "system", now + timedelta(minutes=15), {"format": "PDF"}, e3.eintrag_hash)
    trail.eintraege = [e1, e2, e3, e4]
    return trail
