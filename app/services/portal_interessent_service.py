"""PORTAL-INTERESSENT-001 — Interessenten-Onboarding und Lead-Management.

Statusmaschine:
  INTERESSENT -> QUALIFIZIERT -> KUNDE | ABGELEHNT | INAKTIV

Interessent = Selbstregistrierung im Portal (public, kein JWT noetig)
Qualifiziert = Innendienst hat Erstgespraech bestaetigt
Kunde = Umwandlung in echten Kunden (Kunden-Nr vergeben)
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from enum import Enum
from typing import Any


class InteressentStatus(str, Enum):
    INTERESSENT = "interessent"
    QUALIFIZIERT = "qualifiziert"
    KUNDE = "kunde"
    ABGELEHNT = "abgelehnt"
    INAKTIV = "inaktiv"


class BetriebsTyp(str, Enum):
    ACKERBAU = "ackerbau"
    GEMISCHT = "gemischt"
    VIEHHALTUNG = "viehhaltung"
    SONDERKULTUREN = "sonderkulturen"
    LOHNUNTERNEHMEN = "lohnunternehmen"
    HAENDLER = "haendler"
    SONSTIGE = "sonstige"


ERLAUBTE_UEBERGAENGE: dict[InteressentStatus, set[InteressentStatus]] = {
    InteressentStatus.INTERESSENT: {
        InteressentStatus.QUALIFIZIERT,
        InteressentStatus.ABGELEHNT,
        InteressentStatus.INAKTIV,
    },
    InteressentStatus.QUALIFIZIERT: {
        InteressentStatus.KUNDE,
        InteressentStatus.ABGELEHNT,
        InteressentStatus.INAKTIV,
    },
    InteressentStatus.KUNDE: set(),
    InteressentStatus.ABGELEHNT: {InteressentStatus.INTERESSENT},
    InteressentStatus.INAKTIV: {InteressentStatus.INTERESSENT},
}


@dataclass
class Interessent:
    interessent_id: str
    tenant_id: str
    status: InteressentStatus
    # Kontaktdaten
    vorname: str
    nachname: str
    email: str
    telefon: str | None
    # Betrieb
    betrieb_name: str | None
    betrieb_typ: BetriebsTyp | None
    flaeche_ha: float | None
    hauptkulturen: list[str]        # z.B. ["Winterweizen", "Raps"]
    tiere_anzahl: int | None
    tierart: str | None             # z.B. "Milchkühe"
    plz: str | None
    ort: str | None
    # Interesse
    interesse_themen: list[str]     # z.B. ["Getreidehandel", "Lohnspritz", "Saatgut"]
    anmerkung: str | None
    # CRM
    zugewiesen_an: str | None       # Mitarbeiter-Nr Innendienst/Außendienst
    kunden_nr: str | None           # Nach Konvertierung
    qualifiziert_am: datetime | None
    konvertiert_am: datetime | None
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    aktualisiert_am: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["betrieb_typ"] = self.betrieb_typ.value if self.betrieb_typ else None
        for ts in ("qualifiziert_am", "konvertiert_am", "erstellt_am", "aktualisiert_am"):
            v = getattr(self, ts)
            d[ts] = v.isoformat() if v else None
        d["vollname"] = f"{self.vorname} {self.nachname}"
        return d


class UngueltigerUebergangFehler(Exception):
    pass


class InteressentNichtGefundenFehler(Exception):
    pass


_STORE: dict[str, list[Interessent]] = {}

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class PortalInteressentService:
    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        if tenant_id not in _STORE:
            _STORE[tenant_id] = []

    def _store(self) -> list[Interessent]:
        return _STORE[self.tenant_id]

    def _get(self, interessent_id: str) -> Interessent:
        for i in self._store():
            if i.interessent_id == interessent_id:
                return i
        raise InteressentNichtGefundenFehler(f"Interessent {interessent_id!r} nicht gefunden")

    def registrieren(
        self,
        vorname: str,
        nachname: str,
        email: str,
        telefon: str | None = None,
        betrieb_name: str | None = None,
        betrieb_typ: BetriebsTyp | None = None,
        flaeche_ha: float | None = None,
        hauptkulturen: list[str] | None = None,
        tiere_anzahl: int | None = None,
        tierart: str | None = None,
        plz: str | None = None,
        ort: str | None = None,
        interesse_themen: list[str] | None = None,
        anmerkung: str | None = None,
    ) -> Interessent:
        if not vorname.strip() or not nachname.strip():
            raise ValueError("Vor- und Nachname sind Pflicht")
        if not _EMAIL_RE.match(email):
            raise ValueError(f"Ungültige E-Mail-Adresse: {email!r}")
        # Doppelregistrierung verhindern
        for existing in self._store():
            if existing.email.lower() == email.lower() and existing.status != InteressentStatus.INAKTIV:
                raise ValueError(f"E-Mail {email!r} ist bereits registriert")
        i = Interessent(
            interessent_id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            status=InteressentStatus.INTERESSENT,
            vorname=vorname.strip(),
            nachname=nachname.strip(),
            email=email.lower().strip(),
            telefon=telefon,
            betrieb_name=betrieb_name,
            betrieb_typ=betrieb_typ,
            flaeche_ha=flaeche_ha,
            hauptkulturen=hauptkulturen or [],
            tiere_anzahl=tiere_anzahl,
            tierart=tierart,
            plz=plz,
            ort=ort,
            interesse_themen=interesse_themen or [],
            anmerkung=anmerkung,
            zugewiesen_an=None,
            kunden_nr=None,
            qualifiziert_am=None,
            konvertiert_am=None,
        )
        self._store().append(i)
        return i

    def status_wechsel(
        self,
        interessent_id: str,
        neuer_status: InteressentStatus,
        zugewiesen_an: str | None = None,
        kunden_nr: str | None = None,
    ) -> Interessent:
        i = self._get(interessent_id)
        if neuer_status not in ERLAUBTE_UEBERGAENGE[i.status]:
            raise UngueltigerUebergangFehler(
                f"Übergang {i.status.value}→{neuer_status.value} nicht erlaubt"
            )
        if neuer_status == InteressentStatus.KUNDE and not kunden_nr:
            raise ValueError("Kunden-Nr ist bei Konvertierung zu Kunde Pflicht")
        i.status = neuer_status
        i.aktualisiert_am = datetime.utcnow()
        if zugewiesen_an:
            i.zugewiesen_an = zugewiesen_an
        if neuer_status == InteressentStatus.QUALIFIZIERT:
            i.qualifiziert_am = datetime.utcnow()
        if neuer_status == InteressentStatus.KUNDE:
            i.kunden_nr = kunden_nr
            i.konvertiert_am = datetime.utcnow()
        return i

    def list_interessenten(
        self,
        status: InteressentStatus | None = None,
        betrieb_typ: BetriebsTyp | None = None,
        zugewiesen_an: str | None = None,
    ) -> list[dict[str, Any]]:
        result = self._store()
        if status:
            result = [i for i in result if i.status == status]
        if betrieb_typ:
            result = [i for i in result if i.betrieb_typ == betrieb_typ]
        if zugewiesen_an:
            result = [i for i in result if i.zugewiesen_an == zugewiesen_an]
        return [i.to_dict() for i in sorted(result, key=lambda x: x.erstellt_am, reverse=True)]

    def get(self, interessent_id: str) -> dict[str, Any]:
        return self._get(interessent_id).to_dict()


_SVC_CACHE: dict[str, PortalInteressentService] = {}


def get_interessent_service(tenant_id: str) -> PortalInteressentService:
    if tenant_id not in _SVC_CACHE:
        _SVC_CACHE[tenant_id] = PortalInteressentService(tenant_id)
    return _SVC_CACHE[tenant_id]
