"""HRM-ABWESENHEIT-ANTRAG-001 — Abwesenheitsantrag-Workflow.

Urlaubsantrag -> Genehmigung/Ablehnung -> ESS-Self-Service fuer Mitarbeitende.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import text


class AbwesenheitTyp(str, Enum):
    URLAUB = "urlaub"
    GLEITZEITAUSGLEICH = "gleitzeitausgleich"
    SONDERURLAUB = "sonderurlaub"
    ELTERNZEIT = "elternzeit"
    KRANK = "krank"
    FORTBILDUNG = "fortbildung"
    KURZARBEIT = "kurzarbeit"


class AbwesenheitStatus(str, Enum):
    BEANTRAGT = "beantragt"
    GENEHMIGT = "genehmigt"
    ABGELEHNT = "abgelehnt"
    ZURUECKGEZOGEN = "zurueckgezogen"


TERMINAL_STATUSES = {
    AbwesenheitStatus.GENEHMIGT,
    AbwesenheitStatus.ABGELEHNT,
    AbwesenheitStatus.ZURUECKGEZOGEN,
}
EAU_REQUIRED_TYPES = {AbwesenheitTyp.KRANK}
DEFAULT_URLAUBSANSPRUCH_TAGE = 30
ABWESENHEIT_TYPEN = {
    "URLAUB",
    "KRANKHEIT",
    "SONDERURLAUB",
    "ELTERNZEIT",
    "FORTBILDUNG",
    "KURZARBEIT",
    "GLEITZEITAUSGLEICH",
}
VALID_ABWESENHEIT_TRANSITIONS = {
    ("BEANTRAGT", "GENEHMIGT"),
    ("BEANTRAGT", "ABGELEHNT"),
    ("BEANTRAGT", "ZURUECKGEZOGEN"),
}


class AbwesenheitError(Exception):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uid() -> str:
    return str(uuid4())


@dataclass
class AbwesenheitAntrag:
    antrag_id: str
    tenant_id: str
    mitarbeiter_nr: str
    typ: AbwesenheitTyp
    von_datum: date
    bis_datum: date
    arbeitstage: int
    status: AbwesenheitStatus
    beantragt_von: str
    beantragt_am: datetime
    kommentar: str | None = None
    genehmigt_von: str | None = None
    genehmigt_am: datetime | None = None
    ablehnung_grund: str | None = None
    eau_nachweis_id: str | None = None
    vertretung_durch: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "antrag_id": self.antrag_id,
            "tenant_id": self.tenant_id,
            "mitarbeiter_nr": self.mitarbeiter_nr,
            "typ": self.typ.value,
            "von_datum": self.von_datum.isoformat(),
            "bis_datum": self.bis_datum.isoformat(),
            "arbeitstage": self.arbeitstage,
            "status": self.status.value,
            "beantragt_von": self.beantragt_von,
            "beantragt_am": self.beantragt_am.isoformat(),
            "kommentar": self.kommentar,
            "genehmigt_von": self.genehmigt_von,
            "genehmigt_am": self.genehmigt_am.isoformat() if self.genehmigt_am else None,
            "ablehnung_grund": self.ablehnung_grund,
            "eau_nachweis_id": self.eau_nachweis_id,
            "vertretung_durch": self.vertretung_durch,
            "eau_pflicht": self.typ in EAU_REQUIRED_TYPES,
            "abgeschlossen": self.status in TERMINAL_STATUSES,
        }


class AntragNichtGefundenError(LookupError):
    pass


class UngueltigerStatusUebergangError(ValueError):
    pass


class AbwesenheitKonfliktError(ValueError):
    pass


class HrmAbwesenheitService:

    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        self._antraege: dict[tuple[str, str], AbwesenheitAntrag] = {}

    def reset(self) -> None:
        self._antraege.clear()

    def _key(self, antrag_id: str) -> tuple[str, str]:
        return (self.tenant_id, antrag_id)

    def _get_or_raise(self, antrag_id: str) -> AbwesenheitAntrag:
        a = self._antraege.get(self._key(antrag_id))
        if not a:
            raise AntragNichtGefundenError(f"Antrag nicht gefunden: {antrag_id}")
        return a

    def _arbeitstage_berechnen(self, von: date, bis: date) -> int:
        if bis < von:
            return 0
        days = 0
        current = von
        while current <= bis:
            if current.weekday() < 5:
                days += 1
            current = current + timedelta(days=1)
        return days

    def _pruefe_konflikt(self, mitarbeiter_nr: str, von: date, bis: date, *, exclude_id: str | None = None) -> None:
        for antrag in self._antraege.values():
            if antrag.tenant_id != self.tenant_id:
                continue
            if antrag.mitarbeiter_nr != mitarbeiter_nr:
                continue
            if antrag.status not in (AbwesenheitStatus.BEANTRAGT, AbwesenheitStatus.GENEHMIGT):
                continue
            if exclude_id and antrag.antrag_id == exclude_id:
                continue
            if von <= antrag.bis_datum and bis >= antrag.von_datum:
                raise AbwesenheitKonfliktError(
                    f"Konflikt mit Antrag {antrag.antrag_id} ({antrag.von_datum}--{antrag.bis_datum})"
                )

    def antrag_stellen(
        self,
        *,
        mitarbeiter_nr: str,
        typ: AbwesenheitTyp | str,
        von_datum: date,
        bis_datum: date,
        beantragt_von: str,
        kommentar: str | None = None,
        vertretung_durch: str | None = None,
    ) -> AbwesenheitAntrag:
        typ_val = AbwesenheitTyp(typ)
        if bis_datum < von_datum:
            raise ValueError("bis_datum muss >= von_datum sein")
        self._pruefe_konflikt(mitarbeiter_nr, von_datum, bis_datum)
        antrag = AbwesenheitAntrag(
            antrag_id=_uid(),
            tenant_id=self.tenant_id,
            mitarbeiter_nr=mitarbeiter_nr,
            typ=typ_val,
            von_datum=von_datum,
            bis_datum=bis_datum,
            arbeitstage=self._arbeitstage_berechnen(von_datum, bis_datum),
            status=AbwesenheitStatus.BEANTRAGT,
            beantragt_von=beantragt_von,
            beantragt_am=_now(),
            kommentar=kommentar,
            vertretung_durch=vertretung_durch,
        )
        self._antraege[self._key(antrag.antrag_id)] = antrag
        return antrag

    def genehmigen(self, antrag_id: str, *, genehmigt_von: str, kommentar: str | None = None) -> AbwesenheitAntrag:
        antrag = self._get_or_raise(antrag_id)
        if antrag.status != AbwesenheitStatus.BEANTRAGT:
            raise UngueltigerStatusUebergangError(f"Nur BEANTRAGT kann genehmigt werden, ist: {antrag.status.value}")
        antrag.status = AbwesenheitStatus.GENEHMIGT
        antrag.genehmigt_von = genehmigt_von
        antrag.genehmigt_am = _now()
        if kommentar:
            antrag.kommentar = (antrag.kommentar or "") + f" | Genehmigt: {kommentar}"
        return antrag

    def ablehnen(self, antrag_id: str, *, abgelehnt_von: str, grund: str) -> AbwesenheitAntrag:
        antrag = self._get_or_raise(antrag_id)
        if antrag.status != AbwesenheitStatus.BEANTRAGT:
            raise UngueltigerStatusUebergangError(f"Nur BEANTRAGT kann abgelehnt werden, ist: {antrag.status.value}")
        if not grund.strip():
            raise ValueError("Ablehnungsgrund ist Pflichtfeld")
        antrag.status = AbwesenheitStatus.ABGELEHNT
        antrag.genehmigt_von = abgelehnt_von
        antrag.genehmigt_am = _now()
        antrag.ablehnung_grund = grund
        return antrag

    def zurueckziehen(self, antrag_id: str, *, mitarbeiter_nr: str) -> AbwesenheitAntrag:
        antrag = self._get_or_raise(antrag_id)
        if antrag.mitarbeiter_nr != mitarbeiter_nr:
            raise PermissionError("Nur eigene Antraege koennen zurueckgezogen werden")
        if antrag.status != AbwesenheitStatus.BEANTRAGT:
            raise UngueltigerStatusUebergangError(f"Status {antrag.status.value} kann nicht zurueckgezogen werden")
        antrag.status = AbwesenheitStatus.ZURUECKGEZOGEN
        return antrag

    def get(self, antrag_id: str) -> AbwesenheitAntrag:
        return self._get_or_raise(antrag_id)

    def list_antraege(
        self,
        *,
        mitarbeiter_nr: str | None = None,
        status: AbwesenheitStatus | str | None = None,
        typ: AbwesenheitTyp | str | None = None,
        von_ab: date | None = None,
    ) -> list[AbwesenheitAntrag]:
        result = [a for a in self._antraege.values() if a.tenant_id == self.tenant_id]
        if mitarbeiter_nr:
            result = [a for a in result if a.mitarbeiter_nr == mitarbeiter_nr]
        if status:
            s = AbwesenheitStatus(status) if isinstance(status, str) else status
            result = [a for a in result if a.status == s]
        if typ:
            t = AbwesenheitTyp(typ) if isinstance(typ, str) else typ
            result = [a for a in result if a.typ == t]
        if von_ab:
            result = [a for a in result if a.von_datum >= von_ab]
        return sorted(result, key=lambda a: a.von_datum, reverse=True)

    def urlaubskonto(self, mitarbeiter_nr: str, jahr: int) -> dict[str, Any]:
        genehmigte = [
            a for a in self._antraege.values()
            if a.tenant_id == self.tenant_id
            and a.mitarbeiter_nr == mitarbeiter_nr
            and a.typ == AbwesenheitTyp.URLAUB
            and a.status == AbwesenheitStatus.GENEHMIGT
            and a.von_datum.year == jahr
        ]
        verbraucht = sum(a.arbeitstage for a in genehmigte)
        return {
            "mitarbeiter_nr": mitarbeiter_nr,
            "jahr": jahr,
            "anspruch_tage": DEFAULT_URLAUBSANSPRUCH_TAGE,
            "verbraucht_tage": verbraucht,
            "resturlaub_tage": max(0, DEFAULT_URLAUBSANSPRUCH_TAGE - verbraucht),
            "genehmigte_antraege": len(genehmigte),
        }


_svc_cache: dict[str, HrmAbwesenheitService] = {}


def get_abwesenheit_service(tenant_id: str) -> HrmAbwesenheitService:
    if tenant_id not in _svc_cache:
        _svc_cache[tenant_id] = HrmAbwesenheitService(tenant_id=tenant_id)
    return _svc_cache[tenant_id]


def create_abwesenheitsantrag(
    db: Any,
    tenant_id: str,
    mitarbeiter_id: str,
    typ: str,
    von_datum: str,
    bis_datum: str,
    tage: int,
    operator: str = "system",
) -> dict[str, Any]:
    """Legacy DOM-HRM-004 DB helper kept for existing workflow tests."""
    if typ not in ABWESENHEIT_TYPEN:
        raise AbwesenheitError(f"Unbekannter Abwesenheitstyp: {typ}")
    if tage <= 0:
        raise AbwesenheitError("Tage muessen > 0 sein")

    antrag_id = _uid()
    db.execute(
        text("""
            INSERT INTO domain_hrm.hrm_abwesenheiten
                (id, tenant_id, mitarbeiter_id, typ, von_datum, bis_datum,
                 tage, status, operator, created_at)
            VALUES (:id, :tenant_id, :mitarbeiter_id, :typ, :von_datum,
                    :bis_datum, :tage, 'BEANTRAGT', :operator, NOW())
        """),
        {
            "id": antrag_id,
            "tenant_id": tenant_id,
            "mitarbeiter_id": mitarbeiter_id,
            "typ": typ,
            "von_datum": von_datum,
            "bis_datum": bis_datum,
            "tage": tage,
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hrm.hrm_abwesenheiten WHERE id = :id"),
        {"id": antrag_id},
    ).mappings().first()
    return dict(row) if row else {"id": antrag_id, "status": "BEANTRAGT", "typ": typ}


def transition_abwesenheit(
    db: Any,
    antrag_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
) -> dict[str, Any]:
    rec = db.execute(
        text("""
            SELECT * FROM domain_hrm.hrm_abwesenheiten
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": antrag_id, "tid": tenant_id},
    ).mappings().first()
    if not rec:
        raise AbwesenheitError(f"Abwesenheitsantrag {antrag_id} nicht gefunden")

    old_status = rec["status"]
    if (old_status, new_status) not in VALID_ABWESENHEIT_TRANSITIONS:
        raise AbwesenheitError(f"Ungueltiger Uebergang {old_status} -> {new_status}")

    db.execute(
        text("""
            UPDATE domain_hrm.hrm_abwesenheiten
            SET status = :new_status, operator = :operator, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),
        {
            "new_status": new_status,
            "operator": operator,
            "id": antrag_id,
            "tid": tenant_id,
        },
    )
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_hrm.hrm_abwesenheiten WHERE id = :id"),
        {"id": antrag_id},
    ).mappings().first()
    return dict(updated)
