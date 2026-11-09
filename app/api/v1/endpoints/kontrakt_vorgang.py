"""Kontrakt-Vorgang: Lese- und Kommandowege der Maskenfamilien ``kontrakt`` und ``kontrakt-liste`` (08.11.2026).

Vier handgebaute Seiten (Engagement, Erfuellung, Fixierung, Settlement) und drei Platzhalter (Kontraktuebersicht,
Alarm-Dashboard, contracts-v2) werden zu zwei Maskenfamilien mit Varianten. Die Fachlogik bleibt in den Diensten
(``contract_*_service``); hier stehen:

* **Lesewege mit Zeilenform** je Tabelle, damit der Feldvertrag die Spalten der Masken prueft (vorher
  ``TypedObjectOut`` bzw. ein Kopf mit eingebetteten Listen, den keine Studio-Tabelle lesen kann).
* **Alarme serverseitig.** Das Alarm-Dashboard rechnete sie im Browser aus der Kontraktliste; CLI und MCP sahen sie
  nie. Dieselben Regeln stehen jetzt in ``kontrakt_alarme``.
* **Kommandowege** ``…/actions/<key>`` ueber ``run_delegated_mask_action`` (Pruefung in jedem Modus, Audit, Outbox,
  Wiederholungsschutz): derselbe Weg fuer Maske, CLI und MCP. Der Bearbeiter kommt aus dem Token; die alten Wege
  schrieben ``bediener or "KIM"`` aus dem Rumpf.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.schemas.kontrakt_vorgang_schemas import (
    EngagementArtikelListe,
    EngagementParteiListe,
    KontraktAlarmListe,
    KontraktBewegungListe,
    KontraktErfuellungListe,
    KontraktFixierungListe,
    KontraktLueckeListe,
    KontraktMahnkandidatListe,
    KontraktMahnungListe,
    KontraktPositionListe,
    KontraktUebersichtListe,
    KontraktVorgangKopf,
)
from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import User, get_current_user
from app.core.akteur import gepruefter_akteur
from app.core.business_time import business_today
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.contract_engagement_service import ContractEngagementService
from app.services.contract_fixing_service import ContractFixingService
from app.services.contract_fulfillment_service import ContractFulfillmentService
from app.services.contract_settlement_service import ContractSettlementService
from app.services.kontrakte_adapters import PartyLookupAdapter
from app.services.kontrakte_service import KontraktSecurityService
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(prefix="/kontrakt-vorgang", tags=["kontrakte", "kontrakt-vorgang"])

_LESEN = (KontraktSecurityService.ROLE_LESEN, KontraktSecurityService.ROLE_BEARBEITEN,
          KontraktSecurityService.ROLE_ADMIN)


def _lesen(user: User) -> None:
    if not KontraktSecurityService.has_any_role(user.get("roles") or [], *_LESEN):
        raise HTTPException(status_code=403, detail=f"Insufficient role. Required any of {_LESEN}")


def _iso(wert: Any) -> Optional[str]:
    if isinstance(wert, (date, datetime)):
        return wert.isoformat()
    return wert if wert is None else str(wert)


def _datum(wert: Any) -> Optional[date]:
    if isinstance(wert, datetime):
        return wert.date()
    if isinstance(wert, date):
        return wert
    if isinstance(wert, str) and wert:
        try:
            return date.fromisoformat(wert[:10])
        except ValueError:
            return None
    return None


def _liste(items: list[dict]) -> dict:
    return {"items": items, "total": len(items)}


class _Partner:
    """Partnernamen einmal je Anfrage nachschlagen (die Listen tragen nur ``party_id``)."""

    def __init__(self, db: Session) -> None:
        self._adapter = PartyLookupAdapter(db)
        self._cache: dict[str, Optional[str]] = {}

    def name(self, party_id: Optional[str]) -> Optional[str]:
        if not party_id:
            return None
        if party_id not in self._cache:
            self._cache[party_id] = self._adapter.get_name(party_id)
        return self._cache[party_id]


def _kontrakt_ids(db: Session, tenant_id: str, nummern: set[str]) -> dict[str, str]:
    """contract_no -> contract_id fuer genau die Nummern einer Liste (die Dienste liefern Nummern, die Maske braucht
    die stabile Kennung)."""
    if not nummern:
        return {}
    rows = db.execute(
        text("SELECT contract_no, contract_id::text AS cid FROM domain_ops.kon_contract "
             "WHERE tenant_id = :t AND contract_no = ANY(:n) LIMIT :lim"),
        {"t": tenant_id, "n": sorted(nummern), "lim": len(nummern)},
    ).mappings().fetchmany(len(nummern))
    return {r["contract_no"]: r["cid"] for r in rows}


def _kontrakt(db: Session, tenant_id: str, ref: str) -> dict:
    row = db.execute(
        text("SELECT contract_id::text AS id, contract_no, party_id FROM domain_ops.kon_contract "
             "WHERE tenant_id = :t AND (contract_id::text = :v OR contract_no = :v) LIMIT 1"),
        {"t": tenant_id, "v": ref},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Kontrakt nicht gefunden.")
    return dict(row)


# ── Listen (Familie kontrakt-liste) ────────────────────────────────────────────

async def _offene_kontrakte(db: Session, tenant_id: str, user: User, *, include_done: bool) -> list[dict]:
    from app.api.v1.endpoints.kontrakte import list_kontrakte

    antwort = await list_kontrakte(status=None, contract_type=None, party_id=None, article_id=None,
                                   valid_from=None, valid_to=None, query=None, include_done=include_done,
                                   skip=0, limit=500, db=db, tenant_id=tenant_id, user=user)
    return antwort["items"]


def kontrakt_alarme(item: dict, heute: date) -> list[dict]:
    """Alarmregeln des frueheren Alarm-Dashboards (im Browser gerechnet), jetzt eine Quelle fuer alle Zugaenge."""
    if (item.get("status") or "").upper() != "OFFEN":
        return []
    steuerung = item.get("steering") or {}
    einheit = item.get("unit") or ""
    alarme: list[tuple[str, int, str, Optional[int]]] = []
    ablauf = _datum(item.get("valid_to"))
    tage = (ablauf - heute).days if ablauf else None
    if tage is not None and 0 <= tage <= 30:
        alarme.append(("ablauf", 0, "Läuft heute ab" if tage == 0 else f"Läuft in {tage} Tagen ab", tage))
    if steuerung.get("dunning_candidate"):
        grund = steuerung.get("dunning_reason")
        alarme.append(("mahnung", 1, "Kontraktmahnung fällig" + (f": {grund}" if grund else ""), None))
    if (steuerung.get("hedge_gap_pct") or 0) > 0:
        alarme.append(("absicherung", 2, f"Absicherungslücke von {steuerung['hedge_gap_pct']:.1f} % zum Hedge-Ziel",
                       None))
    if (steuerung.get("market_valuation_eur") or 0) < 0:
        alarme.append(("marktbewertung", 3, f"Negative Marktbewertung {steuerung['market_valuation_eur']:.2f} EUR",
                       None))
    if steuerung.get("writeoff_candidate"):
        grund = steuerung.get("washout_reason")
        alarme.append(("washout", 4, "Washout/Abschreibung vorgemerkt" + (f": {grund}" if grund else ""), None))
    if not steuerung.get("print_ready"):
        alarme.append(("druck", 5, "Drucksteuerung unvollständig (Vorlage oder Kanal fehlt)", None))
    if (item.get("pricing_model") or "").lower() == "matif" and not (item.get("first_unit_price") or 0) > 0:
        alarme.append(("matif", 6, "MATIF-Preisfixierung ausstehend", None))
    gesamt = float(item.get("total_quantity") or 0)
    rest = float(item.get("rest_quantity") or 0)
    if gesamt > 0 and 0 < rest and rest / gesamt * 100 <= 10:
        alarme.append(("restmenge", 7, f"Nur noch {rest:g} {einheit} ({rest / gesamt * 100:.1f} %) Rest", None))
    return [{"id": f"{item['contract_id']}:{art}", "kontrakt_id": str(item["contract_id"]),
             "contract_no": item.get("contract_no"), "partner_name": item.get("party_name"), "alarm": art,
             "prioritaet": prio, "text": meldung, "tage_bis_ablauf": tage_bis, "valid_to": _iso(item.get("valid_to")),
             "rest_quantity": rest, "unit": item.get("unit")}
            for art, prio, meldung, tage_bis in alarme]


@router.get("/uebersicht", response_model=KontraktUebersichtListe, summary="Kontrakte mit Restmenge und Alarmzahl")
async def uebersicht(include_done: bool = Query(True),
                     preismodell: Optional[str] = Query(None, max_length=40, description="z. B. matif"),
                     db: Session = Depends(get_db),
                     tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    heute = business_today()
    zeilen = []
    for item in await _offene_kontrakte(db, tenant_id, user, include_done=include_done):
        if preismodell and (item.get("pricing_model") or "").lower() != preismodell.lower():
            continue
        zeilen.append({
            "id": str(item["contract_id"]), "contract_no": item.get("contract_no"),
            "contract_type": item.get("contract_type"), "party_id": item.get("party_id"),
            "partner_name": item.get("party_name"), "contract_date": _iso(item.get("contract_date")),
            "valid_from": _iso(item.get("valid_from")), "valid_to": _iso(item.get("valid_to")),
            "total_quantity": item.get("total_quantity") or 0, "rest_quantity": item.get("rest_quantity") or 0,
            "unit": item.get("unit"), "status": item.get("status"), "pricing_model": item.get("pricing_model"),
            "artikel": item.get("first_article_desc") or item.get("first_article_id"),
            "preis": item.get("first_unit_price"), "alarme": len(kontrakt_alarme(item, heute)),
        })
    return _liste(zeilen)


@router.get("/alarme", response_model=KontraktAlarmListe, summary="Alarme offener Kontrakte (Ablauf, Mahnung, Hedge …)")
async def alarme(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                 user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    heute = business_today()
    zeilen = [alarm for item in await _offene_kontrakte(db, tenant_id, user, include_done=False)
              for alarm in kontrakt_alarme(item, heute)]
    zeilen.sort(key=lambda z: (z["prioritaet"], z["tage_bis_ablauf"] if z["tage_bis_ablauf"] is not None else 999))
    return _liste(zeilen)


@router.get("/erfuellungsstand", response_model=KontraktErfuellungListe,
            summary="Kontrakte mit Erfuellungsgrad (kontrahiert gegen abgerufen)")
def erfuellungsstand(typ: str = Query("alle", pattern="^(alle|einkauf|verkauf|EINKAUF|VERKAUF)$"),
                     db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                     user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    vertraege = ContractFulfillmentService(db, tenant_id).list_contracts(typ=typ, limit=500)
    ids = _kontrakt_ids(db, tenant_id, {row["contract_no"] for row in vertraege})
    partner = _Partner(db)
    zeilen = []
    for row in vertraege:
        kontrakt_id = ids.get(row["contract_no"])
        if kontrakt_id is None:
            continue
        menge, ab = row.get("menge_kontrakt"), row.get("abgerufen")
        zeilen.append({**row, "id": kontrakt_id, "partner_name": partner.name(row.get("party_id")),
                       "offen": (menge or 0) - (ab or 0) if menge is not None else None})
    return _liste(zeilen)


@router.get("/mahnkandidaten", response_model=KontraktMahnkandidatListe,
            summary="Ueberfaellige, untererfuellte Kontrakte (Kontraktmahnung)")
def mahnkandidaten(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                   user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    kandidaten = ContractEngagementService(db, tenant_id).dunning_candidates()
    ids = _kontrakt_ids(db, tenant_id, {row["contract_no"] for row in kandidaten})
    partner = _Partner(db)
    zeilen = [{**row, "id": ids[row["contract_no"]], "partner_name": partner.name(row.get("party_id"))}
              for row in kandidaten if row["contract_no"] in ids]
    return _liste(zeilen)


@router.get("/engagement/artikel", response_model=EngagementArtikelListe,
            summary="Offene Kontraktmenge je Artikel (Netto Einkauf gegen Verkauf)")
def engagement_artikel(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                       user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    rows = ContractEngagementService(db, tenant_id).engagement()["by_article"]
    return _liste([{**row, "id": str(row["artikel"]), "artikel": str(row["artikel"])} for row in rows])


@router.get("/engagement/partei", response_model=EngagementParteiListe,
            summary="Offene Kontraktmenge je Geschaeftspartner")
def engagement_partei(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                      user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    partner = _Partner(db)
    rows = ContractEngagementService(db, tenant_id).engagement()["by_party"]
    return _liste([{**row, "id": str(row["party_id"]), "party_id": str(row["party_id"]),
                    "partner_name": partner.name(row["party_id"])} for row in rows])


# ── Vorgang je Kontrakt (Familie kontrakt) ─────────────────────────────────────

@router.get("/{kontrakt}", response_model=KontraktVorgangKopf,
            summary="Kopf eines Kontrakts mit Erfuellungs-, Fixier- und Abrechnungsstand")
def kopf(kontrakt: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
         user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    stamm = _kontrakt(db, tenant_id, kontrakt)
    erf = ContractFulfillmentService(db, tenant_id).detail(stamm["id"])
    fix = ContractFixingService(db, tenant_id).workspace(stamm["id"])
    abr = ContractSettlementService(db, tenant_id).settlement_status(stamm["id"])
    if not (erf.get("found") and fix.get("found") and abr.get("found")):
        raise HTTPException(status_code=404, detail="Kontrakt nicht gefunden.")
    preis = erf.get("pricing") or {}
    e, f, a = erf.get("summary") or {}, fix.get("summary") or {}, abr.get("summary") or {}
    return {
        "id": stamm["id"], "contract_no": erf["contract_no"], "contract_type": erf.get("contract_type"),
        "party_id": erf.get("party_id"), "partner_name": _Partner(db).name(erf.get("party_id")),
        "status": erf.get("status"), "einheit": erf.get("einheit"), "valid_from": erf.get("valid_from"),
        "valid_to": erf.get("valid_to"), "ueberfaellig": bool(erf.get("ueberfaellig")),
        "preismodell": preis.get("modell"), "praemie_typ": preis.get("praemie_typ"),
        "praemie_wert": preis.get("praemie_wert"), "mindestpreis": preis.get("mindestpreis"),
        "basis": preis.get("basis"),
        "menge_kontrakt": e.get("menge_kontrakt") or 0, "abgerufen": e.get("abgerufen") or 0,
        "offen": e.get("offen") or 0, "erfuellung_pct": e.get("erfuellung_pct") or 0,
        "erfuellung_status": e.get("status"), "offene_luecken": e.get("offene_luecken") or 0,
        "fixiert": f.get("fixiert") or 0, "offen_zu_fixieren": f.get("offen_zu_fixieren") or 0,
        "fixierungsgrad_pct": f.get("fixierungsgrad_pct") or 0, "bewertbar": bool(f.get("bewertbar")),
        "bewertung_fixiert_eur": f.get("bewertung_fixiert_eur"), "marktwert_offen_eur": f.get("marktwert_offen_eur"),
        "abgerechnet": a.get("abgerechnet") or 0, "offen_abruf": a.get("offen_abruf") or 0,
        "fixiert_aktiv": a.get("fixiert_aktiv") or 0,
    }


@router.get("/{kontrakt}/positionen", response_model=KontraktPositionListe,
            summary="Positionen mit Erfuellung und Fixierung")
def positionen(kontrakt: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
               user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    stamm = _kontrakt(db, tenant_id, kontrakt)
    erf = ContractFulfillmentService(db, tenant_id).detail(stamm["id"])
    fix = {p["position_no"]: p for p in ContractFixingService(db, tenant_id).workspace(stamm["id"]).get("positionen") or []}
    zeilen = []
    for p in erf.get("positionen") or []:
        f = fix.get(p["position_no"], {})
        notierung = f.get("notierung") or {}
        zeilen.append({
            "id": f.get("line_id") or f"{stamm['id']}:{p['position_no']}", "position_no": p["position_no"],
            "artikel": p.get("artikel"), "bezeichnung": p.get("bezeichnung"), "is_matif": bool(p.get("is_matif")),
            "menge_kontrakt": p.get("menge_kontrakt"), "abgerufen": p.get("abgerufen"), "offen": p.get("offen"),
            "erfuellung_status": p.get("status"), "erfuellung_pct": p.get("erfuellung_pct") or 0,
            "abweichung": bool(p.get("abweichung")), "fixiert": f.get("fixiert"),
            "offen_zu_fixieren": f.get("offen_zu_fixieren"), "fixierungsgrad_pct": f.get("fixierungsgrad_pct") or 0,
            "avg_fixpreis_effektiv": f.get("avg_fixpreis_effektiv"), "symbol": f.get("symbol"),
            "notierung_preis": notierung.get("preis"), "notierung_datum": notierung.get("datum"),
            "markt_effektiv": notierung.get("markt_effektiv"), "bewertung_fixiert_eur": f.get("bewertung_fixiert_eur"),
            "marktwert_offen_eur": f.get("marktwert_offen_eur"), "einheit": erf.get("einheit"),
        })
    return _liste(zeilen)


@router.get("/{kontrakt}/luecken", response_model=KontraktLueckeListe, summary="Erfuellungsluecken eines Kontrakts")
def luecken(kontrakt: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
            user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    stamm = _kontrakt(db, tenant_id, kontrakt)
    rows = ContractFulfillmentService(db, tenant_id).detail(stamm["id"]).get("luecken") or []
    return _liste([{"id": f"{stamm['id']}:{i}", "schwere": r["schwere"], "text": r["text"]}
                   for i, r in enumerate(rows, start=1)])


@router.get("/{kontrakt}/fixierungen", response_model=KontraktFixierungListe,
            summary="Fixierungen eines Kontrakts mit Preis, Status und Storno")
def fixierungen(kontrakt: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    stamm = _kontrakt(db, tenant_id, kontrakt)
    abr = ContractSettlementService(db, tenant_id).settlement_status(stamm["id"])
    details: dict[int, dict] = {}
    for p in ContractFixingService(db, tenant_id).workspace(stamm["id"]).get("positionen") or []:
        for f in p.get("fixings") or []:
            details[f["fixing_no"]] = {**f, "position_no": p["position_no"]}
    zeilen = []
    for f in abr.get("fixierungen") or []:
        d = details.get(f["fixing_no"], {})
        zeilen.append({
            "id": f["fixing_id"], "fixing_no": f["fixing_no"], "position_no": d.get("position_no"),
            "menge": f.get("menge"), "matif_price": d.get("matif_price"), "praemie": d.get("praemie"),
            "effektiv_preis": f.get("effektiv_preis"), "datum": d.get("datum"), "referenz": d.get("referenz"),
            "notiz": d.get("notiz"), "bediener": d.get("bediener"), "status": f.get("status") or "aktiv",
            "storno_grund": f.get("storno_grund"), "einheit": abr.get("einheit"),
        })
    return _liste(zeilen)


@router.get("/{kontrakt}/bewegungen", response_model=KontraktBewegungListe,
            summary="Abrufbewegungen eines Kontrakts mit Abrechnungsstand")
def bewegungen(kontrakt: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
               user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    stamm = _kontrakt(db, tenant_id, kontrakt)
    abr = ContractSettlementService(db, tenant_id).settlement_status(stamm["id"])
    return _liste([{"id": b["movement_id"], "menge": b.get("menge"), "datum": b.get("datum"), "status": b["status"],
                    "invoice_no": b.get("invoice_no"), "settled_at": b.get("settled_at"),
                    "storno_grund": b.get("storno_grund"), "einheit": abr.get("einheit")}
                   for b in abr.get("bewegungen") or []])


@router.get("/{kontrakt}/mahnungen", response_model=KontraktMahnungListe, summary="Mahnungen eines Kontrakts")
def mahnungen(kontrakt: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
              user: User = Depends(get_current_user)) -> dict:
    _lesen(user)
    stamm = _kontrakt(db, tenant_id, kontrakt)
    rows = ContractEngagementService(db, tenant_id).list_reminders(stamm["id"])
    return _liste([{**r, "id": f"{stamm['id']}:{r['mahnstufe']}:{r.get('datum') or i}"}
                   for i, r in enumerate(rows, start=1)])


# ── Kommandowege (Maske, CLI, MCP) ─────────────────────────────────────────────

def _zahl(payload: dict, key: str, *, pflicht: bool = False) -> Optional[float]:
    wert = payload.get(key)
    if wert in (None, ""):
        if pflicht:
            raise ValueError(f"{key} fehlt.")
        return None
    try:
        return float(wert)
    except (TypeError, ValueError) as fehler:
        raise ValueError(f"{key} ist keine Zahl.") from fehler


def _blockiert(meldung: str, feld: str = "_entity") -> list[dict]:
    return [{"field": feld, "message": meldung, "severity": "blocking"}]


def _kontrakt_da(session: Session, tid: str, eid: str) -> Optional[list[dict]]:
    gefunden = session.execute(
        text("SELECT 1 FROM domain_ops.kon_contract WHERE tenant_id = :t AND contract_id::text = :v"),
        {"t": tid, "v": eid},
    ).scalar()
    return None if gefunden else _blockiert("Kontrakt nicht gefunden.")


async def _aktion(db: Session, *, key: str, entity_type: str, entity_id: str, tenant_id: str, body: dict,
                  pruefen, ausfuehren, ereignis: str, grund_pflicht: bool = False) -> MaskActionResult:
    return await run_delegated_mask_action(
        db, action_key=key, entity_type=entity_type, entity_id=entity_id, tenant_id=tenant_id, body=body,
        check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type=ereignis, require_audit_reason=grund_pflicht)


def _fixier_pruefung(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
    fehlt = _kontrakt_da(session, tid, eid)
    if fehlt:
        return fehlt
    try:
        menge = _zahl(payload, "menge", pflicht=True)
        preis = _zahl(payload, "matif_preis", pflicht=True)
        _zahl(payload, "praemie")
    except ValueError as fehler:
        return _blockiert(str(fehler), "_input")
    if (menge or 0) <= 0:
        return _blockiert("Fixiermenge muss größer 0 sein.", "menge")
    if (preis or 0) <= 0:
        return _blockiert("MATIF-Preis muss größer 0 sein.", "matif_preis")
    return []


@router.post("/{entity_id}/actions/fixieren", response_model=MaskActionResult,
             summary="Teilfixierung anlegen (Menge zu MATIF-Preis und Praemie)", dependencies=SCHREIBEN["KONTRAKT"])
async def aktion_fixieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                          db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                          user: User = Depends(get_current_user)) -> MaskActionResult:
    akteur = gepruefter_akteur(user)

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        ergebnis = ContractFixingService(session, tid).create_fixing(
            contract_ref=eid, line_ref=(str(payload["position"]) if payload.get("position") not in (None, "") else None),
            quantity=_zahl(payload, "menge", pflicht=True), matif_price=_zahl(payload, "matif_preis", pflicht=True),
            premium=_zahl(payload, "praemie"), matif_reference=payload.get("matif_referenz") or None,
            note=payload.get("notiz") or None, bediener=akteur)
        return (f"Fixierung {ergebnis['fixing_no']} angelegt: {ergebnis['menge']:g} zu {ergebnis['effektiv_preis']:g} "
                f"(offen danach {ergebnis['offen_nach']:g}).")

    return await _aktion(db, key="fixieren", entity_type="kontrakt", entity_id=entity_id, tenant_id=tenant_id,
                         body=body, pruefen=_fixier_pruefung, ausfuehren=ausfuehren, ereignis="kontrakt.fixiert")


@router.post("/{entity_id}/actions/notierung_erfassen", response_model=MaskActionResult,
             summary="MATIF-Notierung erfassen (Bewertungsbasis)", dependencies=SCHREIBEN["KONTRAKT"])
async def aktion_notierung(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                           db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                           user: User = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(user)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        fehlt = _kontrakt_da(session, tid, eid)
        if fehlt:
            return fehlt
        if not str(payload.get("symbol") or "").strip():
            return _blockiert("Symbol fehlt.", "symbol")
        try:
            if (_zahl(payload, "preis", pflicht=True) or 0) <= 0:
                return _blockiert("Preis muss größer 0 sein.", "preis")
        except ValueError as fehler:
            return _blockiert(str(fehler), "preis")
        if payload.get("datum") and _datum(str(payload["datum"])) is None:
            return _blockiert("Ungültiges Datum (erwartet JJJJ-MM-TT).", "datum")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        ergebnis = ContractFixingService(session, tid).upsert_quote(
            symbol=str(payload["symbol"]).strip(), quote_date=_datum(str(payload.get("datum") or "")),
            price=_zahl(payload, "preis", pflicht=True), unit=payload.get("einheit") or None, source="manual")
        return f"Notierung {ergebnis.get('symbol')} zu {ergebnis.get('price')} erfasst."

    return await _aktion(db, key="notierung_erfassen", entity_type="kontrakt", entity_id=entity_id,
                         tenant_id=tenant_id, body=body, pruefen=pruefen, ausfuehren=ausfuehren,
                         ereignis="kontrakt.notierung_erfasst")


@router.post("/{entity_id}/actions/abrechnung_uebergeben", response_model=MaskActionResult,
             summary="Alle offenen Abrufbewegungen an die Abrechnung uebergeben", dependencies=SCHREIBEN["KONTRAKT"])
async def aktion_abrechnung(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                            db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                            user: User = Depends(get_current_user)) -> MaskActionResult:
    akteur = gepruefter_akteur(user)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        fehlt = _kontrakt_da(session, tid, eid)
        if fehlt:
            return fehlt
        offen = session.execute(
            text("SELECT count(*) FROM domain_ops.kon_contract_movement WHERE tenant_id = :t "
                 "AND contract_id::text = :c AND is_invoiced = false AND COALESCE(is_storniert,false) = false"),
            {"t": tid, "c": eid},
        ).scalar()
        return [] if offen else _blockiert("Keine offenen Bewegungen zur Übergabe.")

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        ergebnis = ContractSettlementService(session, tid).handover(
            contract_ref=eid, invoice_no=payload.get("rechnung_nr") or None, bediener=akteur)
        return f"{ergebnis['uebergeben']} Bewegung(en) an die Abrechnung übergeben."

    return await _aktion(db, key="abrechnung_uebergeben", entity_type="kontrakt", entity_id=entity_id,
                         tenant_id=tenant_id, body=body, pruefen=pruefen, ausfuehren=ausfuehren,
                         ereignis="kontrakt.abrechnung_uebergeben")


@router.post("/{entity_id}/actions/mahnen", response_model=MaskActionResult,
             summary="Kontraktmahnung erfassen (naechste Stufe)", dependencies=SCHREIBEN["KONTRAKT"])
async def aktion_mahnen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                        db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                        user: User = Depends(get_current_user)) -> MaskActionResult:
    akteur = gepruefter_akteur(user)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        fehlt = _kontrakt_da(session, tid, eid)
        if fehlt:
            return fehlt
        kandidaten = ContractEngagementService(session, tid).dunning_candidates()
        ids = _kontrakt_ids(session, tid, {row["contract_no"] for row in kandidaten})
        faellig = {ids.get(row["contract_no"]) for row in kandidaten}
        if eid not in faellig:
            return _blockiert("Kontrakt ist nicht überfällig oder vollständig erfüllt — keine Mahnung nötig.")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        ergebnis = ContractEngagementService(session, tid).create_reminder(
            contract_ref=eid, text_body=payload.get("text") or None, bediener=akteur)
        return f"Mahnung Stufe {ergebnis['mahnstufe']} erfasst (offen {ergebnis['offen']:g})."

    return await _aktion(db, key="mahnen", entity_type="kontrakt", entity_id=entity_id, tenant_id=tenant_id,
                         body=body, pruefen=pruefen, ausfuehren=ausfuehren, ereignis="kontrakt.gemahnt")


def _bewegung(session: Session, tid: str, eid: str) -> Optional[dict]:
    row = session.execute(
        text("SELECT movement_id::text AS id, contract_id::text AS kontrakt, is_invoiced, "
             "COALESCE(is_storniert,false) AS is_storniert FROM domain_ops.kon_contract_movement "
             "WHERE tenant_id = :t AND movement_id::text = :v"),
        {"t": tid, "v": eid},
    ).mappings().first()
    return dict(row) if row else None


@router.post("/bewegungen/{entity_id}/actions/abrechnen", response_model=MaskActionResult,
             summary="Eine Abrufbewegung an die Abrechnung uebergeben", dependencies=SCHREIBEN["KONTRAKT"])
async def aktion_bewegung_abrechnen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                                    user: User = Depends(get_current_user)) -> MaskActionResult:
    akteur = gepruefter_akteur(user)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        b = _bewegung(session, tid, eid)
        if not b:
            return _blockiert("Bewegung nicht gefunden.")
        if b["is_storniert"]:
            return _blockiert("Stornierte Bewegung kann nicht abgerechnet werden.")
        if b["is_invoiced"]:
            return _blockiert("Bewegung ist bereits abgerechnet.")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        b = _bewegung(session, tid, eid) or {}
        ContractSettlementService(session, tid).handover(
            contract_ref=b.get("kontrakt") or "", movement_id=eid, invoice_no=payload.get("rechnung_nr") or None,
            bediener=akteur)
        return "Bewegung an die Abrechnung übergeben."

    return await _aktion(db, key="abrechnen", entity_type="kontrakt_bewegung", entity_id=entity_id,
                         tenant_id=tenant_id, body=body, pruefen=pruefen, ausfuehren=ausfuehren,
                         ereignis="kontrakt.bewegung_abgerechnet")


@router.post("/bewegungen/{entity_id}/actions/stornieren", response_model=MaskActionResult,
             summary="Abrufbewegung mit Begruendung stornieren", dependencies=SCHREIBEN["KONTRAKT"])
async def aktion_bewegung_stornieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                     db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                                     user: User = Depends(get_current_user)) -> MaskActionResult:
    akteur = gepruefter_akteur(user)
    grund = str(body.get("_auditReason") or "").strip()

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        b = _bewegung(session, tid, eid)
        if not b:
            return _blockiert("Bewegung nicht gefunden.")
        if b["is_storniert"]:
            return _blockiert("Bewegung ist bereits storniert.")
        if b["is_invoiced"]:
            return _blockiert("Bewegung ist bereits abgerechnet — bitte zuerst die Abrechnung stornieren.")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        ergebnis = ContractSettlementService(session, tid).storno_movement(eid, grund, akteur)
        return f"Bewegung storniert; {ergebnis['frei_menge']:g} wieder abrufbar."

    return await _aktion(db, key="stornieren", entity_type="kontrakt_bewegung", entity_id=entity_id,
                         tenant_id=tenant_id, body=body, pruefen=pruefen, ausfuehren=ausfuehren,
                         ereignis="kontrakt.bewegung_storniert", grund_pflicht=True)


@router.post("/fixierungen/{entity_id}/actions/stornieren", response_model=MaskActionResult,
             summary="Fixierung mit Begruendung stornieren", dependencies=SCHREIBEN["KONTRAKT"])
async def aktion_fixierung_stornieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                      db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                                      user: User = Depends(get_current_user)) -> MaskActionResult:
    akteur = gepruefter_akteur(user)
    grund = str(body.get("_auditReason") or "").strip()

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        storniert = session.execute(
            text("SELECT COALESCE(is_storniert,false) FROM domain_ops.kon_contract_fixing "
                 "WHERE tenant_id = :t AND fixing_id::text = :v"),
            {"t": tid, "v": eid},
        ).first()
        if storniert is None:
            return _blockiert("Fixierung nicht gefunden.")
        return _blockiert("Fixierung ist bereits storniert.") if storniert[0] else []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        ergebnis = ContractSettlementService(session, tid).storno_fixing(eid, grund, akteur)
        return f"Fixierung storniert; {ergebnis['frei_menge']:g} wieder zu fixieren."

    return await _aktion(db, key="stornieren", entity_type="kontrakt_fixierung", entity_id=entity_id,
                         tenant_id=tenant_id, body=body, pruefen=pruefen, ausfuehren=ausfuehren,
                         ereignis="kontrakt.fixierung_storniert", grund_pflicht=True)
