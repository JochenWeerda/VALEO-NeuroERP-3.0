"""PORTAL-LOHNDIENST-001 — Lohndienstleistungs-Auftragsmanagement.

Unterstuetzte Dienstleistungen:
  - lohn_spritz:     Pflanzenschutz-Applikation auf Schlaegen des Kunden
  - mahl_misch:      Mahl- und Mischwagen (TMR-Erstellung auf dem Hof)
  - lohn_mahlen:     Lohnmahlen (Getreide zu Schrot/Mehl)
  - tmr_wagon:       TMR-Mischwagenservice ohne Mahlen
  - lohn_saatbett:   Lohnsaat / Saatbett-Bereitung
  - lohn_ernte:      Lohndrusch

Statusmaschine:
  ANGEFRAGT -> BESTAETIGT -> EINGEPLANT -> ABGESCHLOSSEN | STORNIERT
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from enum import Enum
from typing import Any


class LohndienstTyp(str, Enum):
    LOHN_SPRITZ = "lohn_spritz"
    MAHL_MISCH = "mahl_misch"
    LOHN_MAHLEN = "lohn_mahlen"
    TMR_WAGON = "tmr_wagon"
    LOHN_SAATBETT = "lohn_saatbett"
    LOHN_ERNTE = "lohn_ernte"


LOHNDIENST_BEZEICHNUNGEN: dict[LohndienstTyp, str] = {
    LohndienstTyp.LOHN_SPRITZ: "Lohnspritzen",
    LohndienstTyp.MAHL_MISCH: "Mahl- und Mischwagen (TMR)",
    LohndienstTyp.LOHN_MAHLEN: "Lohnmahlen (Schrot/Mehl)",
    LohndienstTyp.TMR_WAGON: "TMR-Mischwagenservice",
    LohndienstTyp.LOHN_SAATBETT: "Lohnsaat / Saatbett",
    LohndienstTyp.LOHN_ERNTE: "Lohndrusch",
}


class LohndienstStatus(str, Enum):
    ANGEFRAGT = "angefragt"
    BESTAETIGT = "bestaetigt"
    EINGEPLANT = "eingeplant"
    ABGESCHLOSSEN = "abgeschlossen"
    STORNIERT = "storniert"


TERMINAL = {LohndienstStatus.ABGESCHLOSSEN, LohndienstStatus.STORNIERT}

ERLAUBTE_UEBERGAENGE: dict[LohndienstStatus, set[LohndienstStatus]] = {
    LohndienstStatus.ANGEFRAGT: {LohndienstStatus.BESTAETIGT, LohndienstStatus.STORNIERT},
    LohndienstStatus.BESTAETIGT: {LohndienstStatus.EINGEPLANT, LohndienstStatus.STORNIERT},
    LohndienstStatus.EINGEPLANT: {LohndienstStatus.ABGESCHLOSSEN, LohndienstStatus.STORNIERT},
    LohndienstStatus.ABGESCHLOSSEN: set(),
    LohndienstStatus.STORNIERT: set(),
}


@dataclass
class LohndienstAuftrag:
    auftrag_id: str
    tenant_id: str
    kunden_nr: str
    typ: LohndienstTyp
    status: LohndienstStatus
    # Fachliche Felder
    schlag_ids: list[str]           # Betroffene Schlaege (aus Schlagkartei)
    schlag_beschreibung: str        # Freitext wenn kein Schlag-ID
    flaeche_ha: float | None        # Betroffene Flaeche
    wunsch_datum: date | None       # Kundenwunsch-Datum
    geplant_datum: date | None      # Eingeplantest Datum (Innendienst)
    # Mahl/Misch spezifisch
    getreide_art: str | None        # z.B. "Winterweizen eigener Anbau"
    menge_dt: float | None          # Zu mahlende / mischende Menge in dt
    tierart: str | None             # Zieltierkategorie (z.B. "Milchkühe")
    tiere_anzahl: int | None
    # PSM spezifisch
    psm_mittel: list[str]           # PSM-Mittel-Namen / Artikel-IDs
    kultur: str | None              # Zu behandelnde Kultur
    # Allgemein
    anmerkung: str | None
    innendienst_notiz: str | None
    preis_indikativ_eur: float | None
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    aktualisiert_am: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["typ"] = self.typ.value
        d["typ_bezeichnung"] = LOHNDIENST_BEZEICHNUNGEN[self.typ]
        d["status"] = self.status.value
        d["wunsch_datum"] = self.wunsch_datum.isoformat() if self.wunsch_datum else None
        d["geplant_datum"] = self.geplant_datum.isoformat() if self.geplant_datum else None
        d["erstellt_am"] = self.erstellt_am.isoformat()
        d["aktualisiert_am"] = self.aktualisiert_am.isoformat()
        d["abgeschlossen"] = self.status in TERMINAL
        return d


class UngueltigerStatusFehler(Exception):
    pass


class AuftragNichtGefundenFehler(Exception):
    pass


_STORE: dict[str, list[LohndienstAuftrag]] = {}


class LohndienstService:
    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        if tenant_id not in _STORE:
            _STORE[tenant_id] = []

    def _store(self) -> list[LohndienstAuftrag]:
        return _STORE[self.tenant_id]

    def _get(self, auftrag_id: str) -> LohndienstAuftrag:
        for a in self._store():
            if a.auftrag_id == auftrag_id:
                return a
        raise AuftragNichtGefundenFehler(f"Auftrag {auftrag_id!r} nicht gefunden")

    def auftrag_anlegen(
        self,
        kunden_nr: str,
        typ: LohndienstTyp,
        schlag_ids: list[str] | None = None,
        schlag_beschreibung: str = "",
        flaeche_ha: float | None = None,
        wunsch_datum: date | None = None,
        getreide_art: str | None = None,
        menge_dt: float | None = None,
        tierart: str | None = None,
        tiere_anzahl: int | None = None,
        psm_mittel: list[str] | None = None,
        kultur: str | None = None,
        anmerkung: str | None = None,
    ) -> LohndienstAuftrag:
        a = LohndienstAuftrag(
            auftrag_id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            kunden_nr=kunden_nr,
            typ=typ,
            status=LohndienstStatus.ANGEFRAGT,
            schlag_ids=schlag_ids or [],
            schlag_beschreibung=schlag_beschreibung,
            flaeche_ha=flaeche_ha,
            wunsch_datum=wunsch_datum,
            geplant_datum=None,
            getreide_art=getreide_art,
            menge_dt=menge_dt,
            tierart=tierart,
            tiere_anzahl=tiere_anzahl,
            psm_mittel=psm_mittel or [],
            kultur=kultur,
            anmerkung=anmerkung,
            innendienst_notiz=None,
            preis_indikativ_eur=None,
        )
        self._store().append(a)
        return a

    def status_wechsel(
        self,
        auftrag_id: str,
        neuer_status: LohndienstStatus,
        geplant_datum: date | None = None,
        innendienst_notiz: str | None = None,
        preis_indikativ_eur: float | None = None,
    ) -> LohndienstAuftrag:
        a = self._get(auftrag_id)
        if neuer_status not in ERLAUBTE_UEBERGAENGE[a.status]:
            raise UngueltigerStatusFehler(
                f"Übergang {a.status.value}→{neuer_status.value} nicht erlaubt"
            )
        a.status = neuer_status
        a.aktualisiert_am = datetime.utcnow()
        if geplant_datum:
            a.geplant_datum = geplant_datum
        if innendienst_notiz:
            a.innendienst_notiz = innendienst_notiz
        if preis_indikativ_eur is not None:
            a.preis_indikativ_eur = preis_indikativ_eur
        return a

    def list_auftraege(
        self,
        kunden_nr: str | None = None,
        typ: LohndienstTyp | None = None,
        status: LohndienstStatus | None = None,
    ) -> list[dict[str, Any]]:
        result = self._store()
        if kunden_nr:
            result = [a for a in result if a.kunden_nr == kunden_nr]
        if typ:
            result = [a for a in result if a.typ == typ]
        if status:
            result = [a for a in result if a.status == status]
        return [a.to_dict() for a in sorted(result, key=lambda x: x.erstellt_am, reverse=True)]

    def get_auftrag(self, auftrag_id: str) -> dict[str, Any]:
        return self._get(auftrag_id).to_dict()


_SVC_CACHE: dict[str, LohndienstService] = {}


def get_lohndienst_service(tenant_id: str) -> LohndienstService:
    if tenant_id not in _SVC_CACHE:
        _SVC_CACHE[tenant_id] = LohndienstService(tenant_id)
    return _SVC_CACHE[tenant_id]
