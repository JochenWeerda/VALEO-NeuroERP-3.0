"""PORTAL-INTERESSENT-001 — Interessenten-Onboarding und Lead-Management.

Statusmaschine:
  INTERESSENT -> QUALIFIZIERT -> KUNDE | ABGELEHNT | INAKTIV

Interessent = Selbstregistrierung im Portal
Qualifiziert = Innendienst hat Erstgespraech bestaetigt
Kunde = Umwandlung in echten Kunden (Kunden-Nr vergeben)

Bis 20.10.2026 lagen Registrierungen (Name, E-Mail, Telefon, Betrieb) nur im Arbeitsspeicher; ein Neustart verlor
jeden Interessenten. Jetzt ``domain_shared.portal_interessenten`` (Migration ``portal_interessenten_preise_20261020``).
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


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
    erstellt_am: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    aktualisiert_am: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

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


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_SPALTEN = (
    "interessent_id, tenant_id, status, vorname, nachname, email, telefon, betrieb_name, betrieb_typ, flaeche_ha, "
    "hauptkulturen, tiere_anzahl, tierart, plz, ort, interesse_themen, anmerkung, zugewiesen_an, kunden_nr, "
    "qualifiziert_am, konvertiert_am, erstellt_am, aktualisiert_am"
)


def _aus_zeile(row: Any) -> Interessent:
    d = dict(row)
    return Interessent(
        interessent_id=d["interessent_id"], tenant_id=d["tenant_id"], status=InteressentStatus(d["status"]),
        vorname=d["vorname"], nachname=d["nachname"], email=d["email"], telefon=d["telefon"],
        betrieb_name=d["betrieb_name"], betrieb_typ=BetriebsTyp(d["betrieb_typ"]) if d["betrieb_typ"] else None,
        flaeche_ha=float(d["flaeche_ha"]) if d["flaeche_ha"] is not None else None,
        hauptkulturen=list(d["hauptkulturen"] or []), tiere_anzahl=d["tiere_anzahl"], tierart=d["tierart"],
        plz=d["plz"], ort=d["ort"], interesse_themen=list(d["interesse_themen"] or []), anmerkung=d["anmerkung"],
        zugewiesen_an=d["zugewiesen_an"], kunden_nr=d["kunden_nr"], qualifiziert_am=d["qualifiziert_am"],
        konvertiert_am=d["konvertiert_am"], erstellt_am=d["erstellt_am"], aktualisiert_am=d["aktualisiert_am"],
    )


class PortalInteressentService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def _get(self, interessent_id: str, *, sperren: bool = False) -> Interessent:
        sql = (f"SELECT {_SPALTEN} FROM domain_shared.portal_interessenten "  # nosec B608 - feste Spaltenliste
               "WHERE tenant_id = :tid AND interessent_id = :id" + (" FOR UPDATE" if sperren else ""))
        row = self.db.execute(text(sql), {"tid": self.tenant_id, "id": interessent_id}).mappings().first()
        if not row:
            raise InteressentNichtGefundenFehler(f"Interessent {interessent_id!r} nicht gefunden")
        return _aus_zeile(row)

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
        neu = uuid.uuid4().hex
        try:
            self.db.execute(text("""
                INSERT INTO domain_shared.portal_interessenten
                    (interessent_id, tenant_id, status, vorname, nachname, email, telefon, betrieb_name, betrieb_typ,
                     flaeche_ha, hauptkulturen, tiere_anzahl, tierart, plz, ort, interesse_themen, anmerkung)
                VALUES (:id, :tid, 'interessent', :vorname, :nachname, :email, :telefon, :betrieb_name, :betrieb_typ,
                        :flaeche_ha, CAST(:kulturen AS jsonb), :tiere, :tierart, :plz, :ort,
                        CAST(:themen AS jsonb), :anmerkung)
            """), {
                "id": neu, "tid": self.tenant_id, "vorname": vorname.strip(), "nachname": nachname.strip(),
                "email": email.lower().strip(), "telefon": telefon, "betrieb_name": betrieb_name,
                "betrieb_typ": betrieb_typ.value if betrieb_typ else None, "flaeche_ha": flaeche_ha,
                "kulturen": json.dumps(hauptkulturen or []), "tiere": tiere_anzahl, "tierart": tierart,
                "plz": plz, "ort": ort, "themen": json.dumps(interesse_themen or []), "anmerkung": anmerkung,
            })
            self.db.commit()
        except IntegrityError:
            # Eindeutigkeit (Mandant, E-Mail) fuer aktive Registrierungen haelt die Datenbank, auch bei Gleichzeitigkeit.
            self.db.rollback()
            raise ValueError(f"E-Mail {email!r} ist bereits registriert") from None
        return self._get(neu)

    def status_wechsel(
        self,
        interessent_id: str,
        neuer_status: InteressentStatus,
        zugewiesen_an: str | None = None,
        kunden_nr: str | None = None,
    ) -> Interessent:
        try:
            i = self._get(interessent_id, sperren=True)
            if neuer_status not in ERLAUBTE_UEBERGAENGE[i.status]:
                raise UngueltigerUebergangFehler(
                    f"Übergang {i.status.value}→{neuer_status.value} nicht erlaubt"
                )
            if neuer_status == InteressentStatus.KUNDE and not kunden_nr:
                raise ValueError("Kunden-Nr ist bei Konvertierung zu Kunde Pflicht")
            self.db.execute(text("""
                UPDATE domain_shared.portal_interessenten SET status = :status, aktualisiert_am = NOW(),
                    zugewiesen_an = COALESCE(:zugewiesen, zugewiesen_an),
                    qualifiziert_am = CASE WHEN :status = 'qualifiziert' THEN NOW() ELSE qualifiziert_am END,
                    kunden_nr = CASE WHEN :status = 'kunde' THEN :kunden_nr ELSE kunden_nr END,
                    konvertiert_am = CASE WHEN :status = 'kunde' THEN NOW() ELSE konvertiert_am END
                WHERE tenant_id = :tid AND interessent_id = :id
            """), {"status": neuer_status.value, "zugewiesen": zugewiesen_an or None, "kunden_nr": kunden_nr,
                   "tid": self.tenant_id, "id": interessent_id})
            self.db.commit()
        except IntegrityError:
            # Reaktivierung, waehrend dieselbe E-Mail schon wieder aktiv registriert ist.
            self.db.rollback()
            raise UngueltigerUebergangFehler("E-Mail ist bereits erneut registriert") from None
        except Exception:
            self.db.rollback()
            raise
        return self._get(interessent_id)

    def list_interessenten(
        self,
        status: InteressentStatus | None = None,
        betrieb_typ: BetriebsTyp | None = None,
        zugewiesen_an: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = self.db.execute(text(
            f"SELECT {_SPALTEN} FROM domain_shared.portal_interessenten WHERE tenant_id = :tid "  # nosec B608
            "AND (CAST(:status AS text) IS NULL OR status = :status) "
            "AND (CAST(:typ AS text) IS NULL OR betrieb_typ = :typ) "
            "AND (CAST(:zug AS text) IS NULL OR zugewiesen_an = :zug) "
            "ORDER BY erstellt_am DESC LIMIT 1000"
        ), {"tid": self.tenant_id, "status": status.value if status else None,
            "typ": betrieb_typ.value if betrieb_typ else None, "zug": zugewiesen_an}).mappings().all()
        return [_aus_zeile(r).to_dict() for r in rows]

    def get(self, interessent_id: str) -> dict[str, Any]:
        return self._get(interessent_id).to_dict()


def get_interessent_service(db: Session, tenant_id: str) -> PortalInteressentService:
    return PortalInteressentService(db, tenant_id)
