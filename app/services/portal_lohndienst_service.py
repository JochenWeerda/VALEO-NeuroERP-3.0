"""PORTAL-LOHNDIENST-001 — Lohndienstleistungs-Auftraege, persistent in PostgreSQL (PORTAL-CONTEXT-001).

Unterstuetzte Dienstleistungen:
  - lohn_spritz:     Pflanzenschutz-Applikation auf Schlaegen des Kunden
  - mahl_misch:      Mahl- und Mischwagen (TMR-Erstellung auf dem Hof)
  - lohn_mahlen:     Lohnmahlen (Getreide zu Schrot/Mehl)
  - tmr_wagon:       TMR-Mischwagenservice ohne Mahlen
  - lohn_saatbett:   Lohnsaat / Saatbett-Bereitung
  - lohn_ernte:      Lohndrusch

Statusmaschine (deterministisch, jede Aktion genau ein Uebergang):
  anlegen       -> angefragt
  bestaetigen   angefragt  -> bestaetigt      (Freigabe durch den Innendienst)
  einplanen     bestaetigt -> eingeplant      (Termin Pflicht, Lohndienstleister optional)
  abschliessen  eingeplant -> abgeschlossen
  stornieren    angefragt | bestaetigt | eingeplant -> storniert

Bis 14.10.2026 lagen die Auftraege nur im Arbeitsspeicher eines Prozesses. Jetzt gilt:

* **Idempotenz** — jede Aenderung traegt einen Schluessel (eindeutig je Mandant). Dieselbe Anfrage mit demselben
  Schluessel liefert das gespeicherte Ergebnis, statt ein zweites Mal zu wirken; derselbe Schluessel fuer eine andere
  Anfrage ist ein Konflikt.
* **Optimistische Version** — ein Statuswechsel nennt die Version, die er gesehen hat; hat ein anderer Prozess den
  Auftrag inzwischen fortgeschrieben, wird abgewiesen statt ueberschrieben.
* **Historie** — jede statusrelevante Aenderung steht in ``lohndienst_ereignisse`` (nur fortschreibbar).

Wer was darf (Portalrolle, Innendienst, Lohndienstleister), entscheidet der Router; dieser Dienst prueft Mandant,
Kunde, Statusmaschine, Version und Idempotenz.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


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


class Aktion(str, Enum):
    BESTAETIGEN = "bestaetigen"
    EINPLANEN = "einplanen"
    ABSCHLIESSEN = "abschliessen"
    STORNIEREN = "stornieren"


# Aktion -> (zulaessige Ausgangsstatus, Zielstatus)
UEBERGAENGE: dict[Aktion, tuple[frozenset[LohndienstStatus], LohndienstStatus]] = {
    Aktion.BESTAETIGEN: (frozenset({LohndienstStatus.ANGEFRAGT}), LohndienstStatus.BESTAETIGT),
    Aktion.EINPLANEN: (frozenset({LohndienstStatus.BESTAETIGT}), LohndienstStatus.EINGEPLANT),
    Aktion.ABSCHLIESSEN: (frozenset({LohndienstStatus.EINGEPLANT}), LohndienstStatus.ABGESCHLOSSEN),
    Aktion.STORNIEREN: (
        frozenset({LohndienstStatus.ANGEFRAGT, LohndienstStatus.BESTAETIGT, LohndienstStatus.EINGEPLANT}),
        LohndienstStatus.STORNIERT,
    ),
}


class UngueltigerStatusFehler(Exception):
    """Die Aktion passt nicht zum Status des Auftrags."""


class AuftragNichtGefundenFehler(Exception):
    """Kein Auftrag dieser ID im Mandanten (und ggf. Kundenkonto)."""


class VersionsKonflikt(Exception):
    """Der Auftrag wurde inzwischen fortgeschrieben; ``aktuelle_version`` nennt den Stand."""

    def __init__(self, aktuelle_version: int) -> None:
        super().__init__(f"Auftrag wurde inzwischen geaendert (Version {aktuelle_version})")
        self.aktuelle_version = aktuelle_version


class IdempotenzKonflikt(Exception):
    """Der Idempotenzschluessel gehoert zu einer anderen Anfrage."""


_FELDER = (
    "schlag_ids", "schlag_beschreibung", "flaeche_ha", "wunsch_datum", "getreide_art", "menge_dt", "tierart",
    "tiere_anzahl", "psm_mittel", "kultur", "anmerkung",
)
_SPALTEN = (
    "a.id, a.tenant_id, a.customer_id, c.customer_number, a.typ, a.status, a.schlag_ids, a.schlag_beschreibung, "
    "a.flaeche_ha, a.wunsch_datum, a.geplant_datum, a.getreide_art, a.menge_dt, a.tierart, a.tiere_anzahl, "
    "a.psm_mittel, a.kultur, a.anmerkung, a.innendienst_notiz, a.preis_indikativ_eur, a.dienstleister_subject, "
    "a.version, a.angelegt_von, a.angelegt_am, a.geaendert_von, a.geaendert_am"
)
_FROM = "FROM domain_portal.lohndienst_auftraege a JOIN domain_crm.customers c ON c.id = a.customer_id"


def _json(wert: Any) -> Any:
    if isinstance(wert, Decimal):
        return float(wert)
    if isinstance(wert, date):
        return wert.isoformat()
    return wert


def _hash(inhalt: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(inhalt, sort_keys=True, default=_json).encode()).hexdigest()


def _zeile(z: Any) -> dict[str, Any]:
    d = {k: _json(v) for k, v in dict(z._mapping).items()}
    d["auftrag_id"] = d["id"]
    d["kunden_nr"] = d.pop("customer_number")
    typ = LohndienstTyp(d["typ"])
    d["typ_bezeichnung"] = LOHNDIENST_BEZEICHNUNGEN[typ]
    d["abgeschlossen"] = LohndienstStatus(d["status"]) in TERMINAL
    d["erstellt_am"] = d["angelegt_am"]
    d["aktualisiert_am"] = d["geaendert_am"]
    return d


class LohndienstService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        if not tenant_id:
            raise ValueError("Lohndienst ohne Mandant")
        self.db = db
        self.tenant_id = tenant_id

    # ── Lesen ────────────────────────────────────────────────────────────────

    def get_auftrag(self, auftrag_id: str, *, customer_id: Optional[str] = None,
                    dienstleister: Optional[str] = None) -> dict[str, Any]:
        sql = f"SELECT {_SPALTEN} {_FROM} WHERE a.id = :id AND a.tenant_id = :t"
        werte: dict[str, Any] = {"id": auftrag_id, "t": self.tenant_id}
        if customer_id is not None:
            sql += " AND a.customer_id = :c"
            werte["c"] = customer_id
        if dienstleister is not None:
            sql += " AND a.dienstleister_subject = :d"
            werte["d"] = dienstleister
        z = self.db.execute(text(sql), werte).first()
        if z is None:
            raise AuftragNichtGefundenFehler(f"Auftrag {auftrag_id!r} nicht gefunden")
        return _zeile(z)

    def list_auftraege(self, *, customer_id: Optional[str] = None, dienstleister: Optional[str] = None,
                       typ: Optional[LohndienstTyp] = None, status: Optional[LohndienstStatus] = None,
                       limit: int = 500) -> list[dict[str, Any]]:
        sql = f"SELECT {_SPALTEN} {_FROM} WHERE a.tenant_id = :t"
        werte: dict[str, Any] = {"t": self.tenant_id, "l": limit}
        if customer_id is not None:
            sql += " AND a.customer_id = :c"
            werte["c"] = customer_id
        if dienstleister is not None:
            sql += " AND a.dienstleister_subject = :d"
            werte["d"] = dienstleister
        if typ is not None:
            sql += " AND a.typ = :typ"
            werte["typ"] = typ.value
        if status is not None:
            sql += " AND a.status = :st"
            werte["st"] = status.value
        return [_zeile(z) for z in self.db.execute(text(sql + " ORDER BY a.angelegt_am DESC, a.id LIMIT :l"), werte)]

    def historie(self, auftrag_id: str) -> list[dict[str, Any]]:
        zeilen = self.db.execute(text(
            "SELECT id, aktion, von_status, nach_status, version, akteur, kanal, erfasst_am "
            "FROM domain_portal.lohndienst_ereignisse WHERE tenant_id = :t AND auftrag_id = :a ORDER BY version"),
            {"t": self.tenant_id, "a": auftrag_id}).all()
        return [{k: _json(v) for k, v in dict(z._mapping).items()} for z in zeilen]

    def schlaege(self, auftrag: dict[str, Any]) -> list[dict[str, Any]]:
        """Die fuer die Ausfuehrung noetigen Angaben der Schlaege des Auftrags (nur Schlaege dieses Kunden)."""
        ids = list(auftrag.get("schlag_ids") or [])
        if not ids:
            return []
        zeilen = self.db.execute(text(
            "SELECT id, name, flaeche, flik, kultur, gemarkung, geometry_geojson FROM domain_agrar.feldbuch_schlaege "
            "WHERE tenant_id = :t AND customer_id = :c AND id = ANY(:ids) ORDER BY name"),
            {"t": self.tenant_id, "c": auftrag["customer_id"], "ids": ids}).all()
        return [dict(z._mapping) for z in zeilen]

    # ── Idempotenz ───────────────────────────────────────────────────────────

    def _wiederholung(self, schluessel: str, akteur: str, anfrage_hash: str) -> Optional[dict[str, Any]]:
        z = self.db.execute(text(
            "SELECT auftrag_id, akteur, anfrage_hash, daten FROM domain_portal.lohndienst_ereignisse "
            "WHERE tenant_id = :t AND idempotenz_schluessel = :k"), {"t": self.tenant_id, "k": schluessel}).first()
        if z is None:
            return None
        if z.akteur != akteur or z.anfrage_hash != anfrage_hash:
            raise IdempotenzKonflikt("Idempotenzschluessel gehoert zu einer anderen Anfrage")
        return {**z.daten, "wiederholung": True}

    def _ereignis(self, *, auftrag: dict[str, Any], aktion: str, von: Optional[str], akteur: str, kanal: str,
                  schluessel: str, anfrage_hash: str) -> None:
        self.db.execute(text("""
            INSERT INTO domain_portal.lohndienst_ereignisse (id, tenant_id, auftrag_id, aktion, von_status,
              nach_status, version, akteur, kanal, idempotenz_schluessel, anfrage_hash, daten)
            VALUES (:id, :t, :a, :ak, :von, :nach, :v, :akteur, :kanal, :k, :h, CAST(:d AS jsonb))
        """), {"id": str(uuid.uuid4()), "t": self.tenant_id, "a": auftrag["id"], "ak": aktion, "von": von,
               "nach": auftrag["status"], "v": auftrag["version"], "akteur": akteur, "kanal": kanal,
               "k": schluessel, "h": anfrage_hash, "d": json.dumps(auftrag, default=_json)})

    def _ausfuehren(self, schluessel: str, akteur: str, anfrage_hash: str, arbeit) -> dict[str, Any]:
        """Wiederholung erkennen, sonst ``arbeit`` in einer Transaktion; ein paralleler Gewinner wird wiederholt."""
        if not schluessel or not schluessel.strip():
            raise ValueError("Idempotenzschluessel fehlt")
        vorher = self._wiederholung(schluessel, akteur, anfrage_hash)
        if vorher is not None:
            return vorher
        try:
            ergebnis = arbeit()
            self.db.commit()
            return ergebnis
        except (IntegrityError, VersionsKonflikt):
            # Ein anderer Prozess war schneller — mit derselben Anfrage (dann ist sie hiermit wiederholt) oder mit
            # einer anderen (dann bleibt es beim Konflikt).
            self.db.rollback()
            vorher = self._wiederholung(schluessel, akteur, anfrage_hash)
            if vorher is not None:
                return vorher
            raise
        except Exception:
            self.db.rollback()
            raise

    # ── Schreiben ────────────────────────────────────────────────────────────

    def auftrag_anlegen(self, *, customer_id: str, typ: LohndienstTyp, akteur: str, kanal: str,
                        idempotenz_schluessel: str, **felder: Any) -> dict[str, Any]:
        unbekannt = set(felder) - set(_FELDER)
        if unbekannt:
            raise ValueError(f"Unbekannte Felder: {sorted(unbekannt)}")
        daten = {k: felder.get(k) for k in _FELDER}
        daten["schlag_ids"] = list(daten["schlag_ids"] or [])
        daten["psm_mittel"] = list(daten["psm_mittel"] or [])
        daten["schlag_beschreibung"] = daten["schlag_beschreibung"] or ""
        anfrage_hash = _hash({"aktion": "anlegen", "customer_id": customer_id, "typ": typ.value, **daten})

        def arbeit() -> dict[str, Any]:
            if daten["schlag_ids"]:
                fremd = set(daten["schlag_ids"]) - {s["id"] for s in self.schlaege(
                    {"customer_id": customer_id, "schlag_ids": daten["schlag_ids"]})}
                if fremd:
                    raise ValueError(f"Schlaege gehoeren nicht zum Kundenkonto: {sorted(fremd)}")
            auftrag_id = str(uuid.uuid4())
            self.db.execute(text("""
                INSERT INTO domain_portal.lohndienst_auftraege (id, tenant_id, customer_id, typ, schlag_ids,
                  schlag_beschreibung, flaeche_ha, wunsch_datum, getreide_art, menge_dt, tierart, tiere_anzahl,
                  psm_mittel, kultur, anmerkung, angelegt_von, geaendert_von)
                VALUES (:id, :t, :c, :typ, CAST(:schlag_ids AS jsonb), :schlag_beschreibung, :flaeche_ha,
                  :wunsch_datum, :getreide_art, :menge_dt, :tierart, :tiere_anzahl, CAST(:psm_mittel AS jsonb),
                  :kultur, :anmerkung, :akteur, :akteur)
            """), {**daten, "id": auftrag_id, "t": self.tenant_id, "c": customer_id, "typ": typ.value,
                   "akteur": akteur, "schlag_ids": json.dumps(daten["schlag_ids"]),
                   "psm_mittel": json.dumps(daten["psm_mittel"])})
            auftrag = self.get_auftrag(auftrag_id)
            self._ereignis(auftrag=auftrag, aktion="anlegen", von=None, akteur=akteur, kanal=kanal,
                           schluessel=idempotenz_schluessel, anfrage_hash=anfrage_hash)
            return auftrag

        return self._ausfuehren(idempotenz_schluessel, akteur, anfrage_hash, arbeit)

    def status_wechsel(self, *, auftrag_id: str, aktion: Aktion, erwartete_version: int, akteur: str, kanal: str,
                       idempotenz_schluessel: str, customer_id: Optional[str] = None,
                       dienstleister: Optional[str] = None, geplant_datum: Optional[date] = None,
                       innendienst_notiz: Optional[str] = None, preis_indikativ_eur: Optional[float] = None,
                       dienstleister_subject: Optional[str] = None) -> dict[str, Any]:
        anfrage_hash = _hash({
            "aktion": aktion.value, "auftrag_id": auftrag_id, "erwartete_version": erwartete_version,
            "geplant_datum": geplant_datum, "innendienst_notiz": innendienst_notiz,
            "preis_indikativ_eur": preis_indikativ_eur, "dienstleister_subject": dienstleister_subject,
        })
        von_erlaubt, ziel = UEBERGAENGE[aktion]

        def arbeit() -> dict[str, Any]:
            vorher = self.get_auftrag(auftrag_id, customer_id=customer_id, dienstleister=dienstleister)
            if vorher["version"] != erwartete_version:
                raise VersionsKonflikt(vorher["version"])
            if LohndienstStatus(vorher["status"]) not in von_erlaubt:
                raise UngueltigerStatusFehler(f"{aktion.value} ist im Status {vorher['status']} nicht moeglich")
            if aktion is Aktion.EINPLANEN and geplant_datum is None and vorher["geplant_datum"] is None:
                raise UngueltigerStatusFehler("Einplanen braucht ein Datum")
            z = self.db.execute(text("""
                UPDATE domain_portal.lohndienst_auftraege SET
                  status = :ziel, version = version + 1, geaendert_von = :akteur, geaendert_am = now(),
                  geplant_datum = coalesce(:geplant, geplant_datum),
                  innendienst_notiz = coalesce(:notiz, innendienst_notiz),
                  preis_indikativ_eur = coalesce(:preis, preis_indikativ_eur),
                  dienstleister_subject = coalesce(:dl, dienstleister_subject)
                WHERE id = :id AND tenant_id = :t AND version = :v AND status = :von
                RETURNING id
            """), {"ziel": ziel.value, "akteur": akteur, "geplant": geplant_datum, "notiz": innendienst_notiz,
                   "preis": preis_indikativ_eur, "dl": dienstleister_subject, "id": auftrag_id,
                   "t": self.tenant_id, "v": erwartete_version, "von": vorher["status"]}).first()
            if z is None:  # ein anderer Prozess hat zwischen Lesen und Schreiben fortgeschrieben
                raise VersionsKonflikt(self.get_auftrag(auftrag_id)["version"])
            nachher = self.get_auftrag(auftrag_id)
            self._ereignis(auftrag=nachher, aktion=aktion.value, von=vorher["status"], akteur=akteur, kanal=kanal,
                           schluessel=idempotenz_schluessel, anfrage_hash=anfrage_hash)
            return nachher

        return self._ausfuehren(idempotenz_schluessel, akteur, anfrage_hash, arbeit)
