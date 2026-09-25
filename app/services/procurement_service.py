"""Service layer for Einkauf/Procurement domain."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from sqlalchemy import func as sqlfunc, text as sqltext
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session, selectinload

from app.core.business_time import business_today
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models.einkauf_models import (
    ArtikelLagerParameter,
    EinkaufBestellvorschlag,
    EinkaufBestellung,
    EinkaufBestellungPosition,
    EinkaufKontrakt,
    EinkaufKontraktPosition,
    EinkaufLieferant,
    FremdwarenEinlagerung,
    LagerKontenzuordnung,
    PalettenKontoBuchung,
    PfandKontoBuchung,
)
from modules.einkauf.services.bestellvorschlag_service import (
    _current_stock,
    _preferred_supplier,
    engine_bedarf,
    engine_lager,
    engine_rohware,
    engine_verkauf,
    save_vorschlag,
    vorschlag_zu_bestellungen,
)
from modules.einkauf.services.versand_service import versende_bestellung
from app.services.finance_transaction_service import FinanceTransactionService


def _model_cols(obj) -> dict[str, Any]:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns
            if c.name not in ("created_at", "updated_at")}


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _num(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _bool(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(value)


BESTELLUNG_HEADER_KEYS = frozenset({
    "lieferant_id", "vorschlag_id", "niederlassung_id", "bestelldatum",
    "lieferdatum_wunsch", "lieferdatum_zugesagt", "lieferdatum_ist",
    "status", "versand_art", "netto_summe", "mwst_betrag", "brutto_summe",
    "waehrung", "zahlungsziel_tage", "skonto_prozent", "skonto_frist_tage",
    "unsere_referenz", "ihre_referenz", "kontrakt_id", "freitext_kopf",
    "freitext_fuss", "notiz", "bestellfall", "ansprechpartner", "kreditor_konto",
    "lieferant_nr", "kostenstelle", "kommission", "ladetermin", "ladetermin_ab",
    "lade_datum", "incoterms", "lieferadresse", "zahlungsbedingung",
    "skonto1_tage", "skonto1_prozent", "skonto2_tage", "skonto2_prozent",
    "netto_tage", "fremdwaehrung", "umrechnungsfaktor", "anfrage_nr",
    "angebot_nr", "auftrag_nr", "abverkauf_horizont", "bedarfsmenge",
    "mindestbestellmenge", "maximalbestellmenge", "artikelgruppe",
    "lagerplatz_opt", "fracht_opt", "opportunitaetskostensatz",
    "palettenstellplatz_kosten", "lagerkosten_satz", "verkaufsbeleg_id",
    "kunden_id", "direktlieferung", "ueberschlag_lager", "neuer_artikel",
    "innovationshinweis", "erstellt_von",
})

BESTELLUNG_UPDATE_KEYS = BESTELLUNG_HEADER_KEYS - {"lieferant_id"}

POSITION_CREATE_KEYS = frozenset({
    "article_id", "artikel_nr", "artikel_bezeichnung", "lieferanten_artnr",
    "menge", "einheit", "einzelpreis", "preis_einheit", "rabatt_prozent",
    "netto_betrag", "mwst_satz", "mwst_betrag", "brutto_betrag",
    "kontrakt_pos_id", "lieferdatum", "lagerort", "notiz",
    "gebinde_menge", "gebinde_einheit", "gebinde_schluessel", "gewicht_kg",
    "kontrakt_nr", "lagerhalle", "lagerfach", "mindestmenge", "maximalmenge",
})


def _query_one(db: Session, sql: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """Eine Zeile als Dict — oder None."""
    zeile = db.execute(sqltext(sql), params).mappings().first()
    return dict(zeile) if zeile is not None else None


def _query_many(db: Session, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    """Alle Zeilen als Dicts."""
    return [dict(z) for z in db.execute(sqltext(sql), params).mappings().all()]


def _clean_fields(data: dict[str, Any], allowed: frozenset[str]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in data.items():
        if key not in allowed:
            continue
        if value == "":
            value = None
        cleaned[key] = value
    return cleaned


def _summen_rechnen(bestellung: Any, mwst_satz: float = 19.0) -> None:
    """Netto, Steuer und Brutto aus den Positionen setzen.

    Gerechnet wurde das nie: Eine Bestellung mit Positionen stand auf 0,00 —
    im Beleg, in der Liste und in jeder Auswertung. Aufgefallen ist es erst,
    als die Compat-Anlage auf diesen Weg gelegt wurde und eine frisch
    angelegte Bestellung ueber zehn Sack Grassaat einen Betrag von null
    zurueckmeldete.

    Der Steuersatz ist eine Annahme (19 %), solange die Position keinen
    eigenen fuehrt. Das ist besser als keine Zahl, aber es bleibt eine
    Annahme — ein ermaessigter Satz gehoert an die Position.
    """
    netto = Decimal("0")
    for pos in bestellung.positionen or []:
        menge = Decimal(str(pos.menge or 0))
        preis = Decimal(str(pos.einzelpreis or 0))
        rabatt = Decimal(str(pos.rabatt_prozent or 0))
        betrag = (menge * preis * (Decimal("100") - rabatt) / Decimal("100")).quantize(
            Decimal("0.01")
        )
        if pos.netto_betrag in (None, 0):
            pos.netto_betrag = betrag
        satz = Decimal(str(pos.mwst_satz if pos.mwst_satz is not None else mwst_satz))
        pos.mwst_betrag = (betrag * satz / Decimal("100")).quantize(Decimal("0.01"))
        pos.brutto_betrag = betrag + pos.mwst_betrag
        netto += Decimal(str(pos.netto_betrag))

    steuer = (netto * Decimal(str(mwst_satz)) / Decimal("100")).quantize(Decimal("0.01"))
    bestellung.netto_summe = netto
    bestellung.mwst_betrag = steuer
    bestellung.brutto_summe = netto + steuer


def bestellung_to_mask(b: EinkaufBestellung) -> dict[str, Any]:
    """Kopf und Positionen in der Sprache der fuehrenden Maske."""
    return {
        "id": str(b.id),
        "bestellnummer": b.bestellnummer,
        "lieferant_id": str(b.lieferant_id) if b.lieferant_id else None,
        "lieferant_name": b.lieferant.firmenname if b.lieferant else None,
        "bestelldatum": _iso(b.bestelldatum),
        "lieferdatum_wunsch": _iso(b.lieferdatum_wunsch),
        "lieferdatum_zugesagt": _iso(b.lieferdatum_zugesagt),
        "lieferdatum_ist": _iso(b.lieferdatum_ist),
        "status": b.status,
        "versand_art": b.versand_art,
        "netto_summe": _num(b.netto_summe),
        "mwst_betrag": _num(b.mwst_betrag),
        "brutto_summe": _num(b.brutto_summe),
        "waehrung": b.waehrung,
        "zahlungsziel_tage": b.zahlungsziel_tage,
        "skonto_prozent": _num(b.skonto_prozent),
        "skonto_frist_tage": b.skonto_frist_tage,
        "unsere_referenz": b.unsere_referenz,
        "ihre_referenz": b.ihre_referenz,
        "kontrakt_id": str(b.kontrakt_id) if b.kontrakt_id else None,
        "freitext_kopf": b.freitext_kopf,
        "freitext_fuss": b.freitext_fuss,
        "notiz": b.notiz,
        "niederlassung_id": b.niederlassung_id,
        "bestellfall": b.bestellfall or "bestand_abgleich",
        "ansprechpartner": b.ansprechpartner,
        "kreditor_konto": b.kreditor_konto,
        "lieferant_nr": b.lieferant_nr,
        "kostenstelle": b.kostenstelle,
        "kommission": b.kommission,
        "ladetermin": _iso(b.ladetermin),
        "ladetermin_ab": _iso(b.ladetermin_ab),
        "lade_datum": _iso(b.lade_datum),
        "incoterms": b.incoterms,
        "lieferadresse": b.lieferadresse,
        "zahlungsbedingung": b.zahlungsbedingung,
        "skonto1_tage": b.skonto1_tage,
        "skonto1_prozent": _num(b.skonto1_prozent),
        "skonto2_tage": b.skonto2_tage,
        "skonto2_prozent": _num(b.skonto2_prozent),
        "netto_tage": b.netto_tage,
        "fremdwaehrung": b.fremdwaehrung,
        "umrechnungsfaktor": _num(b.umrechnungsfaktor),
        "anfrage_nr": b.anfrage_nr,
        "angebot_nr": b.angebot_nr,
        "auftrag_nr": b.auftrag_nr,
        "abverkauf_horizont": b.abverkauf_horizont,
        "bedarfsmenge": _num(b.bedarfsmenge),
        "mindestbestellmenge": _num(b.mindestbestellmenge),
        "maximalbestellmenge": _num(b.maximalbestellmenge),
        "artikelgruppe": b.artikelgruppe,
        "lagerplatz_opt": _bool(b.lagerplatz_opt),
        "fracht_opt": _bool(b.fracht_opt),
        "opportunitaetskostensatz": _num(b.opportunitaetskostensatz),
        "palettenstellplatz_kosten": _num(b.palettenstellplatz_kosten),
        "lagerkosten_satz": _num(b.lagerkosten_satz),
        "verkaufsbeleg_id": b.verkaufsbeleg_id,
        "kunden_id": b.kunden_id,
        "direktlieferung": _bool(b.direktlieferung),
        "ueberschlag_lager": _bool(b.ueberschlag_lager),
        "neuer_artikel": _bool(b.neuer_artikel),
        "innovationshinweis": b.innovationshinweis,
        "erstellt_von": b.erstellt_von,
        "positionen": [position_to_mask(p) for p in b.positionen],
    }


def position_to_mask(p: EinkaufBestellungPosition) -> dict[str, Any]:
    menge = _num(p.menge) or 0
    geliefert = _num(p.menge_geliefert) or 0
    return {
        "id": str(p.id),
        "pos_nr": p.pos_nr,
        "article_id": p.article_id,
        "artikel_nr": p.artikel_nr,
        "artikel_bezeichnung": p.artikel_bezeichnung,
        "bezeichnung": p.artikel_bezeichnung,
        "lieferanten_artnr": p.lieferanten_artnr,
        "menge": menge,
        "menge_geliefert": geliefert,
        "menge_offen": _num(p.menge_offen) if p.menge_offen is not None else menge - geliefert,
        "einheit": p.einheit,
        "einzelpreis": _num(p.einzelpreis),
        "preis_einheit": p.preis_einheit,
        "netto_betrag": _num(p.netto_betrag),
        "betrag": _num(p.netto_betrag),
        "status": p.status,
        "lagerort": p.lagerort,
        "lager": p.lagerort,
        "gebinde_menge": _num(p.gebinde_menge),
        "gebinde_einheit": p.gebinde_einheit,
        "gebinde_schluessel": p.gebinde_schluessel,
        "gewicht_kg": _num(p.gewicht_kg),
        "kontrakt_nr": p.kontrakt_nr,
        "lagerhalle": p.lagerhalle,
        "lagerfach": p.lagerfach,
        "mindestmenge": _num(p.mindestmenge),
        "maximalmenge": _num(p.maximalmenge),
        "lieferdatum": _iso(p.lieferdatum),
        "notiz": p.notiz,
    }


class ProcurementService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Bestellvorschlag engines ──────────────────────────────────────────────

    def compute_vorschlag_lager(self, niederlassung_id, artikelgruppe, artikel_nr, warehouse_id, nur_unter_meldebestand) -> list[dict]:
        return engine_lager(self.db, tenant_id=self.tenant_id, niederlassung_id=niederlassung_id,
                            artikelgruppe=artikelgruppe, artikel_nr=artikel_nr,
                            warehouse_id=warehouse_id, nur_unter_meldebestand=nur_unter_meldebestand)

    def compute_vorschlag_bedarf(
        self, horizont, stichtag=None, niederlassung_id=None, artikelgruppe=None,
        artikel_nr=None, warehouse_id=None, lagerkosten_satz=None,
        frachtkosten_fix=None, nur_mit_bedarf=True,
    ) -> list[dict]:
        """Bestand gegen Abverkauf statt gegen einen gepflegten Sollbestand."""
        return engine_bedarf(
            self.db, tenant_id=self.tenant_id, horizont=horizont, stichtag=stichtag,
            niederlassung_id=niederlassung_id, artikelgruppe=artikelgruppe,
            artikel_nr=artikel_nr, warehouse_id=warehouse_id,
            lagerkosten_satz=lagerkosten_satz, frachtkosten_fix=frachtkosten_fix,
            nur_mit_bedarf=nur_mit_bedarf,
        )

    def compute_vorschlag_verkauf(self, niederlassung_id, artikelgruppe, von_datum, bis_datum) -> list[dict]:
        return engine_verkauf(self.db, tenant_id=self.tenant_id, niederlassung_id=niederlassung_id,
                              artikelgruppe=artikelgruppe, von_datum=von_datum, bis_datum=bis_datum)

    def compute_vorschlag_rohware(self, stichtag, niederlassung_id) -> list[dict]:
        return engine_rohware(self.db, tenant_id=self.tenant_id, stichtag=stichtag, niederlassung_id=niederlassung_id)

    # ── Bestellvorschläge CRUD ────────────────────────────────────────────────

    def list_vorschlaege(self, vorschlag_typ=None, status=None, von=None, bis=None) -> list[dict]:
        q = self.db.query(EinkaufBestellvorschlag).options(
            selectinload(EinkaufBestellvorschlag.positionen)
        ).filter(EinkaufBestellvorschlag.tenant_id == self.tenant_id)
        if vorschlag_typ:
            q = q.filter(EinkaufBestellvorschlag.vorschlag_typ == vorschlag_typ)
        if status:
            q = q.filter(EinkaufBestellvorschlag.status == status)
        if von:
            q = q.filter(EinkaufBestellvorschlag.datum >= von)
        if bis:
            q = q.filter(EinkaufBestellvorschlag.datum <= bis)
        return [
            {"id": str(v.id), "vorschlag_typ": v.vorschlag_typ, "bezeichnung": v.bezeichnung,
             "datum": v.datum.isoformat() if v.datum else None, "status": v.status,
             "niederlassung_id": v.niederlassung_id, "erstellt_von": v.erstellt_von,
             "positionen_anz": len(v.positionen), "created_at": v.created_at.isoformat() if v.created_at else None}
            for v in q.order_by(EinkaufBestellvorschlag.datum.desc()).all()
        ]

    def get_vorschlag(self, vorschlag_id: str) -> dict:
        v = self.db.query(EinkaufBestellvorschlag).filter(
            EinkaufBestellvorschlag.id == vorschlag_id,
            EinkaufBestellvorschlag.tenant_id == self.tenant_id,
        ).first()
        if not v:
            raise EntityNotFoundError("EinkaufBestellvorschlag", vorschlag_id)
        return {
            "id": str(v.id), "vorschlag_typ": v.vorschlag_typ, "bezeichnung": v.bezeichnung,
            "datum": v.datum.isoformat() if v.datum else None, "status": v.status,
            "parameter": v.parameter, "niederlassung_id": v.niederlassung_id,
            "erstellt_von": v.erstellt_von,
            "freigegeben_von": v.freigegeben_von,
            "freigegeben_am": v.freigegeben_am.isoformat() if v.freigegeben_am else None,
            "positionen": [
                {"id": str(p.id), "pos_nr": p.pos_nr, "article_id": p.article_id,
                 "artikel_nr": p.artikel_nr, "artikel_bezeichnung": p.artikel_bezeichnung,
                 "artikel_gruppe": p.artikel_gruppe, "einheit": p.einheit,
                 "ist_bestand": float(p.ist_bestand or 0), "offene_auftraege": float(p.offene_auftraege or 0),
                 "bedarf": float(p.bedarf or 0), "vorschlag_menge": float(p.vorschlag_menge),
                 "bestell_menge": float(p.bestell_menge or p.vorschlag_menge),
                 "lieferant_id": str(p.lieferant_id) if p.lieferant_id else None,
                 "lieferant_name": p.lieferant_name, "letzter_preis": float(p.letzter_preis) if p.letzter_preis else None,
                 "preis_einheit": p.preis_einheit, "status": p.status}
                for p in v.positionen
            ],
        }

    def create_vorschlag(self, vorschlag_typ, positionen, parameter, niederlassung_id, bezeichnung=None) -> dict:
        v = save_vorschlag(self.db, tenant_id=self.tenant_id, vorschlag_typ=vorschlag_typ,
                           positionen=positionen, parameter=parameter, niederlassung_id=niederlassung_id)
        if bezeichnung:
            v.bezeichnung = bezeichnung
        self.db.commit()
        self.db.refresh(v)
        return {"id": str(v.id), "status": v.status, "positionen_anz": len(v.positionen)}

    def update_vorschlag(self, vorschlag_id: str, data: dict) -> dict:
        v = self.db.query(EinkaufBestellvorschlag).filter(
            EinkaufBestellvorschlag.id == vorschlag_id,
            EinkaufBestellvorschlag.tenant_id == self.tenant_id,
        ).first()
        if not v:
            raise EntityNotFoundError("EinkaufBestellvorschlag", vorschlag_id)
        for field in ("bezeichnung", "status", "notiz"):
            if field in data:
                setattr(v, field, data[field])
        if "positionen" in data:
            pos_map = {str(p.id): p for p in v.positionen}
            for pos_data in data["positionen"]:
                pos = pos_map.get(str(pos_data.get("id", "")))
                if pos:
                    for f in ("bestell_menge", "lieferant_id", "lieferant_name", "letzter_preis", "status"):
                        if f in pos_data:
                            setattr(pos, f, pos_data[f])
        self.db.commit()
        return {"id": str(v.id), "status": v.status}

    def delete_vorschlag(self, vorschlag_id: str) -> None:
        v = self.db.query(EinkaufBestellvorschlag).filter(
            EinkaufBestellvorschlag.id == vorschlag_id,
            EinkaufBestellvorschlag.tenant_id == self.tenant_id,
        ).first()
        if not v:
            raise EntityNotFoundError("EinkaufBestellvorschlag", vorschlag_id)
        self.db.delete(v)
        self.db.commit()

    def freigebe_vorschlag(self, vorschlag_id: str) -> dict:
        try:
            orders = vorschlag_zu_bestellungen(self.db, vorschlag_id=vorschlag_id,
                                               tenant_id=self.tenant_id, freigegeben_von="system")
            self.db.commit()
            return {"bestellungen": orders, "anzahl": len(orders)}
        except ValueError as exc:
            raise EntityNotFoundError("EinkaufBestellvorschlag", vorschlag_id) from exc

    # ── ArtikelLagerParameter CRUD ────────────────────────────────────────────

    def list_artikel_lager_parameter(self, article_id=None, warehouse_id=None, niederlassung_id=None) -> list[dict]:
        q = self.db.query(ArtikelLagerParameter).filter(ArtikelLagerParameter.tenant_id == self.tenant_id)
        if article_id:
            q = q.filter(ArtikelLagerParameter.article_id == article_id)
        if warehouse_id:
            q = q.filter(ArtikelLagerParameter.warehouse_id == warehouse_id)
        if niederlassung_id:
            q = q.filter(ArtikelLagerParameter.niederlassung_id == niederlassung_id)
        return [
            {"id": str(p.id), "article_id": p.article_id, "warehouse_id": p.warehouse_id,
             "niederlassung_id": p.niederlassung_id, "mindestbestand": float(p.mindestbestand or 0),
             "maximalbestand": float(p.maximalbestand or 0), "meldebestand": float(p.meldebestand or 0),
             "soll_bestand": float(p.soll_bestand or 0),
             "std_lieferant_id": str(p.std_lieferant_id) if p.std_lieferant_id else None,
             "std_bestellmenge": float(p.std_bestellmenge) if p.std_bestellmenge else None,
             "std_einheit": p.std_einheit, "wiederbeschaffungs_tage": p.wiederbeschaffungs_tage,
             "durchschnitt_verbrauch_tag": float(p.durchschnitt_verbrauch_tag) if p.durchschnitt_verbrauch_tag else None,
             "reichweite_tage": float(p.reichweite_tage) if p.reichweite_tage else None,
             "aktiv": p.aktiv, "notiz": p.notiz}
            for p in q.all()
        ]

    def create_artikel_lager_parameter(self, data: dict) -> dict:
        existing = self.db.query(ArtikelLagerParameter).filter(
            ArtikelLagerParameter.tenant_id == self.tenant_id,
            ArtikelLagerParameter.article_id == data["article_id"],
            ArtikelLagerParameter.warehouse_id == data.get("warehouse_id"),
        ).first()
        if existing:
            raise ConflictError("Parameter für diesen Artikel/Lager bereits vorhanden")
        param = ArtikelLagerParameter(id=uuid7(), tenant_id=self.tenant_id, **data)
        self.db.add(param)
        self.db.commit()
        self.db.refresh(param)
        return {"id": str(param.id), "article_id": param.article_id}

    def update_artikel_lager_parameter(self, param_id: str, data: dict) -> dict:
        p = self.db.query(ArtikelLagerParameter).filter(
            ArtikelLagerParameter.id == param_id, ArtikelLagerParameter.tenant_id == self.tenant_id,
        ).first()
        if not p:
            raise EntityNotFoundError("ArtikelLagerParameter", param_id)
        for field, value in data.items():
            setattr(p, field, value)
        self.db.commit()
        return {"id": str(p.id)}

    def delete_artikel_lager_parameter(self, param_id: str) -> None:
        p = self.db.query(ArtikelLagerParameter).filter(
            ArtikelLagerParameter.id == param_id, ArtikelLagerParameter.tenant_id == self.tenant_id,
        ).first()
        if not p:
            raise EntityNotFoundError("ArtikelLagerParameter", param_id)
        self.db.delete(p)
        self.db.commit()

    # ── Lieferanten CRUD ──────────────────────────────────────────────────────

    def list_lieferanten(self, suche=None, aktiv=None) -> list[dict]:
        q = self.db.query(EinkaufLieferant).filter(EinkaufLieferant.tenant_id == self.tenant_id)
        if aktiv is not None:
            q = q.filter(EinkaufLieferant.aktiv == aktiv)
        if suche:
            q = q.filter(EinkaufLieferant.firmenname.ilike(f"%{suche}%"))
        return [
            {"id": str(lf.id), "lieferantennummer": lf.lieferantennummer, "firmenname": lf.firmenname,
             "ort": lf.ort, "plz": lf.plz, "email": lf.email, "telefon": lf.telefon,
             "partner_id": lf.partner_id, "zahlungsbedingungen": lf.zahlungsbedingungen,
             "lieferzeit_tage": lf.lieferzeit_tage, "bewertung": lf.bewertung, "aktiv": lf.aktiv}
            for lf in q.order_by(EinkaufLieferant.firmenname).all()
        ]

    def create_lieferant(self, data: dict) -> dict:
        lf = EinkaufLieferant(id=uuid7(), tenant_id=self.tenant_id, **data)
        self.db.add(lf)
        self.db.commit()
        self.db.refresh(lf)
        return {"id": str(lf.id), "lieferantennummer": lf.lieferantennummer, "firmenname": lf.firmenname}

    def get_lieferant(self, lieferant_id: str) -> dict:
        lf = self.db.query(EinkaufLieferant).filter(
            EinkaufLieferant.id == lieferant_id, EinkaufLieferant.tenant_id == self.tenant_id,
        ).first()
        if not lf:
            raise EntityNotFoundError("EinkaufLieferant", lieferant_id)
        return _model_cols(lf)

    def update_lieferant(self, lieferant_id: str, data: dict) -> dict:
        lf = self.db.query(EinkaufLieferant).filter(
            EinkaufLieferant.id == lieferant_id, EinkaufLieferant.tenant_id == self.tenant_id,
        ).first()
        if not lf:
            raise EntityNotFoundError("EinkaufLieferant", lieferant_id)
        for field, value in data.items():
            setattr(lf, field, value)
        self.db.commit()
        return {"id": str(lf.id)}

    # ── Kontrakte CRUD ────────────────────────────────────────────────────────

    def list_kontrakte(self, lieferant_id=None, status=None) -> list[dict]:
        q = self.db.query(EinkaufKontrakt).filter(EinkaufKontrakt.tenant_id == self.tenant_id)
        if lieferant_id:
            q = q.filter(EinkaufKontrakt.lieferant_id == lieferant_id)
        if status:
            q = q.filter(EinkaufKontrakt.status == status)
        return [
            {"id": str(k.id), "kontraktnummer": k.kontraktnummer, "lieferant_id": str(k.lieferant_id),
             "bezeichnung": k.bezeichnung,
             "gueltig_von": k.gueltig_von.isoformat() if k.gueltig_von else None,
             "gueltig_bis": k.gueltig_bis.isoformat() if k.gueltig_bis else None,
             "status": k.status, "kontrakt_typ": k.kontrakt_typ,
             "gesamtmenge": float(k.gesamtmenge) if k.gesamtmenge else None,
             "offene_menge": float(k.offene_menge) if k.offene_menge else None}
            for k in q.order_by(EinkaufKontrakt.gueltig_bis.desc()).all()
        ]

    def create_kontrakt(self, data: dict) -> dict:
        k = EinkaufKontrakt(id=uuid7(), tenant_id=self.tenant_id, **data)
        self.db.add(k)
        self.db.commit()
        self.db.refresh(k)
        return {"id": str(k.id), "kontraktnummer": k.kontraktnummer}

    def get_kontrakt(self, kontrakt_id: str) -> dict:
        k = self.db.query(EinkaufKontrakt).filter(
            EinkaufKontrakt.id == kontrakt_id, EinkaufKontrakt.tenant_id == self.tenant_id,
        ).first()
        if not k:
            raise EntityNotFoundError("EinkaufKontrakt", kontrakt_id)
        return {
            "id": str(k.id), "kontraktnummer": k.kontraktnummer, "lieferant_id": str(k.lieferant_id),
            "bezeichnung": k.bezeichnung,
            "gueltig_von": k.gueltig_von.isoformat() if k.gueltig_von else None,
            "gueltig_bis": k.gueltig_bis.isoformat() if k.gueltig_bis else None,
            "status": k.status, "kontrakt_typ": k.kontrakt_typ,
            "gesamtmenge": float(k.gesamtmenge) if k.gesamtmenge else None,
            "offene_menge": float(k.offene_menge) if k.offene_menge else None,
            "positionen": [
                {"id": str(p.id), "pos_nr": p.pos_nr, "article_id": p.article_id,
                 "artikel_bezeichnung": p.artikel_bezeichnung, "menge": float(p.menge),
                 "offene_menge": float(p.offene_menge) if p.offene_menge else None,
                 "einheit": p.einheit, "preis": float(p.preis) if p.preis else None,
                 "preis_einheit": p.preis_einheit, "preisbindung": p.preisbindung,
                 "gueltig_von": p.gueltig_von.isoformat() if p.gueltig_von else None,
                 "gueltig_bis": p.gueltig_bis.isoformat() if p.gueltig_bis else None}
                for p in k.positionen
            ],
        }

    def update_kontrakt(self, kontrakt_id: str, data: dict) -> dict:
        k = self.db.query(EinkaufKontrakt).filter(
            EinkaufKontrakt.id == kontrakt_id, EinkaufKontrakt.tenant_id == self.tenant_id,
        ).first()
        if not k:
            raise EntityNotFoundError("EinkaufKontrakt", kontrakt_id)
        for field, value in data.items():
            setattr(k, field, value)
        self.db.commit()
        return {"id": str(k.id)}

    def add_kontrakt_position(self, kontrakt_id: str, data: dict) -> dict:
        k = self.db.query(EinkaufKontrakt).filter(
            EinkaufKontrakt.id == kontrakt_id, EinkaufKontrakt.tenant_id == self.tenant_id,
        ).first()
        if not k:
            raise EntityNotFoundError("EinkaufKontrakt", kontrakt_id)
        pos = EinkaufKontraktPosition(id=uuid7(), kontrakt_id=kontrakt_id, **data)
        self.db.add(pos)
        self.db.commit()
        return {"id": str(pos.id)}

    # ── Bestellungen CRUD ─────────────────────────────────────────────────────

    def list_bestellungen(self, lieferant_id=None, status=None, von=None, bis=None) -> list[dict]:
        q = self.db.query(EinkaufBestellung).options(
            selectinload(EinkaufBestellung.positionen),
            selectinload(EinkaufBestellung.lieferant),
        ).filter(EinkaufBestellung.tenant_id == self.tenant_id)
        if lieferant_id:
            q = q.filter(EinkaufBestellung.lieferant_id == lieferant_id)
        if status:
            q = q.filter(EinkaufBestellung.status == status)
        if von:
            q = q.filter(EinkaufBestellung.bestelldatum >= von)
        if bis:
            q = q.filter(EinkaufBestellung.bestelldatum <= bis)
        return [
            {"id": str(b.id), "bestellnummer": b.bestellnummer, "lieferant_id": str(b.lieferant_id),
             "lieferant_name": b.lieferant.firmenname if b.lieferant else None,
             "bestelldatum": b.bestelldatum.isoformat() if b.bestelldatum else None,
             "lieferdatum_wunsch": b.lieferdatum_wunsch.isoformat() if b.lieferdatum_wunsch else None,
             "status": b.status, "versand_art": b.versand_art,
             "versandt_am": b.versandt_am.isoformat() if b.versandt_am else None,
             "netto_summe": float(b.netto_summe) if b.netto_summe else None,
             "brutto_summe": float(b.brutto_summe) if b.brutto_summe else None,
             "positionen_anz": len(b.positionen)}
            for b in q.order_by(EinkaufBestellung.bestelldatum.desc()).all()
        ]

    #: Ab wann eine Probe etwas aussagt und wann sie entschieden ist.
    #:
    #: Die Schwellen sind eine Verabredung, keine Wahrheit — deshalb stehen sie
    #: hier benannt und nicht verstreut im Code. Wer sie anders will, aendert
    #: sie hier und sieht sofort, was davon abhaengt.
    INNOVATION_FENSTER_TAGE = 90
    INNOVATION_MINDESTTAGE = 14      # darunter ist jedes Urteil verfrueht
    INNOVATION_QUOTE_GUT = 0.7       # so viel der Probe verkauft -> aufnehmen
    INNOVATION_QUOTE_SCHWACH = 0.3   # darunter, nach der Haelfte -> auslisten

    def innovationen_bewerten(self, fenster_tage: int | None = None) -> list[dict]:
        """Wie laufen die Artikel, die zur Probe bestellt wurden?

        Ein neuer Artikel hat keine Historie — genau deshalb ist er ein eigener
        Bestellfall und keine Bedarfsrechnung. Was er stattdessen braucht, ist
        eine Nachschau: Was wurde zur Probe bestellt, was ist davon verkauft,
        und reicht das fuer eine Entscheidung?

        Gerechnet wird ab der **ersten Lieferung**, nicht ab der Bestellung:
        Solange die Ware nicht da ist, kann sie sich nicht verkaufen, und ein
        Urteil waere unfair. Vor ``INNOVATION_MINDESTTAGE`` gibt es deshalb
        keine Empfehlung, sondern die Auskunft, dass es zu frueh ist.

        Die Empfehlung ist ein Vorschlag, keine Buchung: Ob ein Artikel ins
        Sortiment kommt, entscheidet der Vertrieb, nicht eine Quote.
        """
        fenster = fenster_tage or self.INNOVATION_FENSTER_TAGE
        heute = business_today()

        zeilen = _query_many(
            self.db,
            """
            SELECT b.id::text        AS bestellung_id,
                   b.bestellnummer,
                   b.bestelldatum,
                   b.innovationshinweis,
                   p.artikel_nr,
                   p.artikel_bezeichnung,
                   p.article_id::text AS article_id,
                   p.menge            AS testmenge,
                   p.einheit
            FROM domain_einkauf.bestellungen b
            JOIN domain_einkauf.bestellung_positionen p ON p.bestellung_id = b.id
            WHERE b.tenant_id = :tid
              AND b.neuer_artikel IS TRUE
              AND COALESCE(b.status, '') <> 'storniert'
            ORDER BY b.bestelldatum DESC NULLS LAST, p.pos_nr
            """,
            {"tid": self.tenant_id},
        )

        ergebnis: list[dict] = []
        for zeile in zeilen:
            testmenge = Decimal(str(zeile.get("testmenge") or 0))
            article_id = zeile.get("article_id")

            erste_lieferung = None
            verkauft = Decimal("0")
            if article_id:
                erste_lieferung = _query_one(
                    self.db,
                    """
                    SELECT MIN(movement_date) AS datum
                    FROM domain_inventory.inventory_stock_movements
                    WHERE article_id::text = :aid
                      AND tenant_id = :tid
                      AND lower(movement_type) IN ('in', 'wareneingang', 'einlagerung')
                      AND (:ab IS NULL OR movement_date >= :ab)
                    """,
                    {"aid": article_id, "tid": self.tenant_id, "ab": zeile.get("bestelldatum")},
                )
                erste_lieferung = (erste_lieferung or {}).get("datum")

            if erste_lieferung:
                gemessen = _query_one(
                    self.db,
                    """
                    SELECT COALESCE(SUM(quantity), 0) AS menge
                    FROM domain_inventory.inventory_stock_movements
                    WHERE article_id::text = :aid
                      AND tenant_id = :tid
                      AND lower(movement_type) = 'out'
                      AND movement_date >= :ab
                    """,
                    {"aid": article_id, "tid": self.tenant_id, "ab": erste_lieferung},
                )
                verkauft = Decimal(str(abs((gemessen or {}).get("menge") or 0)))

            tage = (heute - erste_lieferung).days if erste_lieferung else 0
            quote = float(verkauft / testmenge) if testmenge > 0 else 0.0
            pro_tag = float(verkauft / tage) if tage > 0 else 0.0

            if not erste_lieferung:
                stand, empfehlung = "wartet_auf_lieferung", (
                    "Die Probe ist noch nicht angekommen — bis dahin gibt es nichts zu messen."
                )
            elif tage < self.INNOVATION_MINDESTTAGE:
                stand, empfehlung = "zu_frueh", (
                    f"Erst {tage} Tage im Regal. Ein Urteil vor "
                    f"{self.INNOVATION_MINDESTTAGE} Tagen sagt mehr ueber den Zufall "
                    f"als ueber den Artikel."
                )
            elif quote >= self.INNOVATION_QUOTE_GUT:
                stand, empfehlung = "aufnehmen", (
                    f"{quote:.0%} der Probe verkauft, {pro_tag:.2f} je Tag — "
                    f"das traegt eine Listung."
                )
            elif quote < self.INNOVATION_QUOTE_SCHWACH and tage >= fenster / 2:
                stand, empfehlung = "auslisten", (
                    f"Nach {tage} Tagen erst {quote:.0%} verkauft. Der Artikel bindet "
                    f"Platz, den ein laufender braucht."
                )
            else:
                stand, empfehlung = "beobachten", (
                    f"{quote:.0%} nach {tage} Tagen — noch keine Entscheidung, "
                    f"weiter beobachten."
                )

            ergebnis.append({
                "bestellung_id": zeile["bestellung_id"],
                "bestellnummer": zeile.get("bestellnummer"),
                "artikel_nr": zeile.get("artikel_nr"),
                "artikel_bezeichnung": zeile.get("artikel_bezeichnung"),
                "einheit": zeile.get("einheit"),
                "hinweis": zeile.get("innovationshinweis"),
                "bestelldatum": (
                    zeile["bestelldatum"].isoformat() if zeile.get("bestelldatum") else None
                ),
                "erste_lieferung": erste_lieferung.isoformat() if erste_lieferung else None,
                "tage_im_regal": tage,
                "testmenge": float(testmenge),
                "verkauft": float(verkauft),
                "abverkaufsquote": round(quote, 4),
                "abverkauf_pro_tag": round(pro_tag, 3),
                "stand": stand,
                "empfehlung": empfehlung,
            })

        return ergebnis

    def bestellung_aus_auftrag(
        self,
        auftrag_id: str,
        *,
        ueberschlag_lager: bool = False,
        lieferant_id: str | None = None,
        lieferdatum: date | None = None,
    ) -> dict:
        """Aus einem Verkaufsauftrag eine Bestellung machen.

        Zwei Wege, und der Unterschied ist nicht kosmetisch:

        **Ohne Ueberschlag** geht die Ware vom Lieferanten direkt zum Kunden.
        Bestellt wird die volle Auftragsmenge — der eigene Bestand hilft nicht,
        er liegt am falschen Ort. Die Lieferadresse ist die des Kunden.

        **Mit Ueberschlag** laeuft die Ware ueber den eigenen Hof. Dann deckt
        der vorhandene Bestand einen Teil, und bestellt wird nur die Fehlmenge;
        die Lieferadresse bleibt die eigene. Eine Position, die der Bestand
        voll deckt, entsteht gar nicht erst.

        Der Auftrag bleibt am Beleg stehen (``verkaufsbeleg_id``,
        ``kunden_id``, Kommission = Auftragsnummer). Ohne diesen Rueckverweis
        weiss spaeter niemand mehr, fuer wen die Ware kam — und bei einer
        Direktlieferung steht sie nie im eigenen Lager, wo man nachsehen
        koennte.
        """
        kopf = _query_one(
            self.db,
            """
            SELECT id::text AS id, order_number, customer_id::text AS customer_id,
                   customer_name, delivery_address, delivery_date, status
            FROM domain_crm.sales_orders
            WHERE id::text = :aid AND tenant_id::text = :tid AND deleted_at IS NULL
            """,
            {"aid": auftrag_id, "tid": self.tenant_id},
        )
        if kopf is None:
            raise EntityNotFoundError("SalesOrder", auftrag_id)

        zeilen = _query_many(
            self.db,
            """
            SELECT line_number, article_number, description, quantity, unit, ek_price
            FROM domain_crm.sales_order_items
            WHERE order_id::text = :aid AND tenant_id::text = :tid
            ORDER BY line_number
            """,
            {"aid": auftrag_id, "tid": self.tenant_id},
        )
        if not zeilen:
            raise ValidationFailedError(
                f"Auftrag {kopf.get('order_number') or auftrag_id} hat keine Positionen."
            )

        positionen: list[dict] = []
        uebersprungen: list[str] = []
        for zeile in zeilen:
            artikel_nr = zeile.get("article_number")
            menge = Decimal(str(zeile.get("quantity") or 0))
            if menge <= 0 or not artikel_nr:
                continue

            artikel = _query_one(
                self.db,
                """
                SELECT id::text AS id, gebinde_einheit
                FROM domain_inventory.articles
                WHERE article_number = :nr AND tenant_id::text = :tid
                LIMIT 1
                """,
                {"nr": artikel_nr, "tid": self.tenant_id},
            )

            zu_bestellen = menge
            gedeckt = Decimal("0")
            if ueberschlag_lager and artikel:
                # Nur beim Ueberschlag hilft der eigene Bestand: Bei einer
                # echten Direktlieferung liegt er am falschen Ort.
                bestand = _current_stock(self.db, artikel["id"], self.tenant_id)
                gedeckt = min(bestand, menge)
                zu_bestellen = max(menge - bestand, Decimal("0"))

            if zu_bestellen <= 0:
                uebersprungen.append(
                    f"{artikel_nr}: {menge} durch Bestand gedeckt"
                )
                continue

            positionen.append({
                "article_id": artikel["id"] if artikel else None,
                "artikel_nr": artikel_nr,
                "artikel_bezeichnung": zeile.get("description") or artikel_nr,
                "menge": float(zu_bestellen),
                "einheit": zeile.get("unit") or (artikel or {}).get("gebinde_einheit") or "t",
                "einzelpreis": float(zeile.get("ek_price") or 0),
                "notiz": (
                    f"Auftrag {kopf.get('order_number')} Pos. {zeile.get('line_number')}"
                    + (f", {gedeckt} aus Bestand" if gedeckt > 0 else "")
                ),
            })

        if not positionen:
            raise ValidationFailedError(
                "Der Bestand deckt den Auftrag vollstaendig — es ist nichts zu bestellen. "
                + "; ".join(uebersprungen)
            )

        # Ohne Lieferant gibt es keine Bestellung — die Spalte ist zu Recht
        # NOT NULL. Ist keiner genannt, wird der bevorzugte Lieferant des ersten
        # Artikels genommen; gibt es auch den nicht, wird gefragt statt geraten.
        if not lieferant_id:
            for pos in positionen:
                if not pos.get("article_id"):
                    continue
                gefunden, _name, _preis = _preferred_supplier(
                    self.db, pos["article_id"], self.tenant_id
                )
                if gefunden:
                    lieferant_id = gefunden
                    break
        if not lieferant_id:
            raise ValidationFailedError(
                "Kein Lieferant: Weder wurde einer genannt, noch ist an den Artikeln "
                "ein bevorzugter Lieferant gepflegt."
            )

        daten = {
            "bestellfall": "direktlieferung",
            "direktlieferung": not ueberschlag_lager,
            "ueberschlag_lager": ueberschlag_lager,
            "verkaufsbeleg_id": kopf["id"],
            "kunden_id": kopf.get("customer_id"),
            # Die Kommission traegt die Auftragsnummer: Daran erkennt der
            # Wareneingang, wofuer die Ware kam.
            "kommission": kopf.get("order_number"),
            "lieferdatum_wunsch": lieferdatum or kopf.get("delivery_date"),
            "positionen": positionen,
        }
        daten["lieferant_id"] = lieferant_id
        if not ueberschlag_lager:
            # Direkt zum Kunden — ohne Adresse faehrt der Lieferant zu uns.
            daten["lieferadresse"] = (
                kopf.get("delivery_address")
                or kopf.get("customer_name")
                or ""
            )

        ergebnis = self.create_bestellung(daten)
        ergebnis["aus_auftrag"] = kopf.get("order_number")
        if uebersprungen:
            ergebnis["uebersprungen"] = uebersprungen
        return ergebnis

    def create_bestellung(self, data: dict) -> dict:
        ts = datetime.now().strftime("%y%m%d%H%M%S")
        header = _clean_fields(data, BESTELLUNG_HEADER_KEYS)
        if not header.get("bestelldatum"):
            header["bestelldatum"] = datetime.now().date()
        if not header.get("bestellfall"):
            header["bestellfall"] = "bestand_abgleich"
        if header.get("bestellfall") == "direktlieferung":
            header.setdefault("direktlieferung", True)
        if header.get("bestellfall") == "innovation":
            header.setdefault("neuer_artikel", True)
        bestellung = EinkaufBestellung(
            id=uuid7(), tenant_id=self.tenant_id, bestellnummer=f"EK-{ts}",
            **header,
        )
        self.db.add(bestellung)
        self.db.flush()
        for i, pos_data in enumerate(data.get("positionen", []), start=1):
            pos_fields = _clean_fields(pos_data, POSITION_CREATE_KEYS)
            menge = pos_fields.get("menge", 0)
            pos_fields.setdefault("preis_einheit", "100kg")
            pos = EinkaufBestellungPosition(
                id=uuid7(), bestellung_id=bestellung.id, pos_nr=i,
                artikel_nr=pos_fields.get("artikel_nr") or "",
                artikel_bezeichnung=pos_fields.get("artikel_bezeichnung") or "",
                menge=menge,
                menge_geliefert=0,
                menge_offen=menge,
                einheit=pos_fields.get("einheit") or "t",
                **{k: v for k, v in pos_fields.items() if k not in {
                    "artikel_nr", "artikel_bezeichnung", "menge", "einheit",
                }},
            )
            self.db.add(pos)
        self.db.flush()
        _summen_rechnen(bestellung)
        self.db.commit()
        self.db.refresh(bestellung)
        return {
            "id": str(bestellung.id),
            "bestellnummer": bestellung.bestellnummer,
            "netto_summe": float(bestellung.netto_summe or 0),
            "brutto_summe": float(bestellung.brutto_summe or 0),
        }

    def get_bestellung(self, bestellung_id: str) -> dict:
        b = self.db.query(EinkaufBestellung).filter(
            EinkaufBestellung.id == bestellung_id, EinkaufBestellung.tenant_id == self.tenant_id,
        ).first()
        if not b:
            raise EntityNotFoundError("EinkaufBestellung", bestellung_id)
        return bestellung_to_mask(b)

    def update_bestellung(self, bestellung_id: str, data: dict) -> dict:
        b = self.db.query(EinkaufBestellung).filter(
            EinkaufBestellung.id == bestellung_id, EinkaufBestellung.tenant_id == self.tenant_id,
        ).first()
        if not b:
            raise EntityNotFoundError("EinkaufBestellung", bestellung_id)
        for field, value in _clean_fields(data, BESTELLUNG_UPDATE_KEYS).items():
            setattr(b, field, value)
        if b.bestellfall == "direktlieferung" and "direktlieferung" not in data:
            b.direktlieferung = True
        if b.bestellfall == "innovation" and "neuer_artikel" not in data:
            b.neuer_artikel = True
        self.db.commit()
        return {"id": str(b.id), "status": b.status, "bestellfall": b.bestellfall}

    def versende_bestellung_svc(self, bestellung_id: str, versand_art: str, empfaenger=None) -> dict:
        b = self.db.query(EinkaufBestellung).filter(
            EinkaufBestellung.id == bestellung_id, EinkaufBestellung.tenant_id == self.tenant_id,
        ).first()
        if not b:
            raise EntityNotFoundError("EinkaufBestellung", bestellung_id)
        result = versende_bestellung(self.db, b, versand_art=versand_art, empfaenger_override=empfaenger)
        self.db.commit()
        return {"bestellung_id": str(b.id), "bestellnummer": b.bestellnummer, "versand": result}

    def freigebe_bestellung(self, bestellung_id: str) -> dict:
        try:
            b = self.db.query(EinkaufBestellung).filter(
                EinkaufBestellung.id == bestellung_id, EinkaufBestellung.tenant_id == self.tenant_id,
            ).first()
        except DataError:
            raise EntityNotFoundError("EinkaufBestellung", bestellung_id)
        if not b:
            raise EntityNotFoundError("EinkaufBestellung", bestellung_id)
        if b.status not in ("entwurf", "draft"):
            raise ValidationFailedError(f"Bestellung hat Status '{b.status}' — nur Entwürfe können freigegeben werden")
        b.status = "freigegeben"
        self._book_bestellung_obligo(b)
        self.db.commit()
        return {"bestellung_id": str(b.id), "bestellnummer": b.bestellnummer, "status": b.status}

    def _book_bestellung_obligo(self, b: EinkaufBestellung) -> None:
        """Create a commitment (Obligo) JournalEntry when a Bestellung is approved."""
        netto = Decimal(str(b.netto_summe or 0))
        if netto == 0:
            return
        entry_date = b.bestelldatum or business_today()
        fin = FinanceTransactionService(self.db, self.tenant_id)
        fin.create(
            entry_number=f"OBLIGO-{b.bestellnummer}",
            description=f"Bestellobligo {b.bestellnummer}",
            entry_date=entry_date,
            lines=[
                {"account_id": "6000", "debit_amount": float(netto), "credit_amount": 0,
                 "description": "Warenaufwand Bestellung"},
                {"account_id": "1600", "debit_amount": 0, "credit_amount": float(netto),
                 "description": "Verbindlichkeiten Lieferant"},
            ],
            reference=b.bestellnummer,
            source="procurement",
            document_type="bestellung",
            period=str(entry_date)[:7],
        )

    def storniere_bestellung(self, bestellung_id: str, grund: str | None = None) -> dict:
        """Eine Bestellung stornieren — mit dem Grund, warum.

        Die Maske fragt danach, der Beleg hielt ihn bisher nicht fest. Ein
        Storno ohne Grund ist spaeter nicht mehr zu erklaeren: Weder der
        Lieferant noch die Revision koennen nachvollziehen, ob storniert wurde,
        weil falsch erfasst, weil nicht lieferbar oder weil der Kunde absprang.
        Der Grund wird an die Notiz gehaengt, nicht in sie hinein — was vorher
        dastand, bleibt stehen.
        """

        try:
            b = self.db.query(EinkaufBestellung).filter(
                EinkaufBestellung.id == bestellung_id, EinkaufBestellung.tenant_id == self.tenant_id,
            ).first()
        except DataError:
            raise EntityNotFoundError("EinkaufBestellung", bestellung_id)
        if not b:
            raise EntityNotFoundError("EinkaufBestellung", bestellung_id)
        if b.status in ("storniert", "abgeschlossen"):
            raise ValidationFailedError(f"Bestellung hat Status '{b.status}' und kann nicht storniert werden")
        b.status = "storniert"
        if grund and grund.strip():
            vermerk = f"Storniert: {grund.strip()}"
            b.notiz = f"{b.notiz}\n{vermerk}" if b.notiz else vermerk
        self.db.commit()
        return {
            "bestellung_id": str(b.id),
            "bestellnummer": b.bestellnummer,
            "status": b.status,
            "grund": grund,
        }

    # ── LagerKontenzuordnung CRUD ─────────────────────────────────────────────

    def list_lager_konten(self, artikelgruppe=None) -> list[dict]:
        q = self.db.query(LagerKontenzuordnung).filter(LagerKontenzuordnung.tenant_id == self.tenant_id)
        if artikelgruppe:
            q = q.filter(LagerKontenzuordnung.artikelgruppe == artikelgruppe)
        return [_model_cols(lk) for lk in q.order_by(LagerKontenzuordnung.artikelgruppe).all()]

    def create_lager_konto(self, data: dict) -> dict:
        lk = LagerKontenzuordnung(id=uuid7(), tenant_id=self.tenant_id, **data)
        self.db.add(lk)
        self.db.commit()
        self.db.refresh(lk)
        return {"id": str(lk.id), "artikelgruppe": lk.artikelgruppe, "bestandskonto": lk.bestandskonto}

    def update_lager_konto(self, konto_id: str, data: dict) -> dict:
        lk = self.db.query(LagerKontenzuordnung).filter(
            LagerKontenzuordnung.id == konto_id, LagerKontenzuordnung.tenant_id == self.tenant_id,
        ).first()
        if not lk:
            raise EntityNotFoundError("LagerKontenzuordnung", konto_id)
        for field, value in data.items():
            setattr(lk, field, value)
        self.db.commit()
        return {"id": str(lk.id)}

    # ── Paletten-Konto ────────────────────────────────────────────────────────

    def get_paletten_saldo(self, partner_id: str, paletten_typ=None) -> dict:
        q = self.db.query(PalettenKontoBuchung).filter(
            PalettenKontoBuchung.tenant_id == self.tenant_id,
            PalettenKontoBuchung.partner_id == partner_id,
        ).order_by(PalettenKontoBuchung.buchungsdatum.desc())
        if paletten_typ:
            q = q.filter(PalettenKontoBuchung.paletten_typ == paletten_typ)
        buchungen = q.all()
        letzter_saldo = buchungen[0].saldo_nachher if buchungen else 0
        return {"partner_id": partner_id, "paletten_typ": paletten_typ or "alle",
                "saldo": letzter_saldo, "buchungen_anz": len(buchungen),
                "letzte_buchung": buchungen[0].buchungsdatum.isoformat() if buchungen else None}

    def create_paletten_buchung(self, data: dict) -> dict:
        last = self.db.query(PalettenKontoBuchung).filter(
            PalettenKontoBuchung.tenant_id == self.tenant_id,
            PalettenKontoBuchung.partner_id == data["partner_id"],
            PalettenKontoBuchung.paletten_typ == data["paletten_typ"],
        ).order_by(PalettenKontoBuchung.buchungsdatum.desc()).first()
        saldo_vorher = last.saldo_nachher if last else 0
        buchungsart = data.get("buchungsart")
        menge = data["menge"]
        if buchungsart in ("ausgabe", "verkauf"):
            saldo_neu = saldo_vorher - menge
        elif buchungsart in ("ruecknahme", "kauf"):
            saldo_neu = saldo_vorher + menge
        else:
            saldo_neu = saldo_vorher
        buchung = PalettenKontoBuchung(id=uuid7(), tenant_id=self.tenant_id,
                                       saldo_vorher=saldo_vorher, saldo_nachher=saldo_neu, **data)
        self.db.add(buchung)
        self.db.commit()
        return {"id": str(buchung.id), "saldo_nachher": saldo_neu}

    # ── Pfand-Konto ───────────────────────────────────────────────────────────

    def get_pfand_saldo(self, partner_id: str, gebinde_typ=None) -> list[dict]:
        q = (
            self.db.query(
                PfandKontoBuchung.gebinde_typ,
                sqlfunc.max(PfandKontoBuchung.saldo_menge).label("saldo_menge"),
                sqlfunc.max(PfandKontoBuchung.saldo_wert).label("saldo_wert"),
                sqlfunc.max(PfandKontoBuchung.buchungsdatum).label("letzte_buchung"),
            )
            .filter(PfandKontoBuchung.tenant_id == self.tenant_id, PfandKontoBuchung.partner_id == partner_id)
            .group_by(PfandKontoBuchung.gebinde_typ)
        )
        if gebinde_typ:
            q = q.filter(PfandKontoBuchung.gebinde_typ == gebinde_typ)
        return [{"gebinde_typ": r[0], "saldo_menge": float(r[1] or 0),
                 "saldo_wert": float(r[2] or 0),
                 "letzte_buchung": r[3].isoformat() if r[3] else None}
                for r in q.all()]

    def create_pfand_buchung(self, data: dict) -> dict:
        last = self.db.query(PfandKontoBuchung).filter(
            PfandKontoBuchung.tenant_id == self.tenant_id,
            PfandKontoBuchung.partner_id == data["partner_id"],
            PfandKontoBuchung.gebinde_typ == data["gebinde_typ"],
        ).order_by(PfandKontoBuchung.buchungsdatum.desc()).first()
        saldo_menge_vorher = float(last.saldo_menge or 0) if last else 0.0
        saldo_wert_vorher = float(last.saldo_wert or 0) if last else 0.0
        delta = float(data["menge"])
        pfandwert = float(data.get("pfandwert_je_einheit") or 0) * delta
        buchungsart = data.get("buchungsart")
        if buchungsart == "ausgabe":
            saldo_menge_neu, saldo_wert_neu = saldo_menge_vorher - delta, saldo_wert_vorher - pfandwert
        elif buchungsart == "ruecknahme":
            saldo_menge_neu, saldo_wert_neu = saldo_menge_vorher + delta, saldo_wert_vorher + pfandwert
        else:
            saldo_menge_neu, saldo_wert_neu = saldo_menge_vorher, saldo_wert_vorher
        buchung = PfandKontoBuchung(id=uuid7(), tenant_id=self.tenant_id,
                                    gesamtpfandwert=pfandwert,
                                    saldo_menge=saldo_menge_neu, saldo_wert=saldo_wert_neu, **data)
        self.db.add(buchung)
        self.db.commit()
        return {"id": str(buchung.id), "saldo_menge": saldo_menge_neu, "saldo_wert": saldo_wert_neu}

    # ── Fremdwaren-Einlagerung CRUD ───────────────────────────────────────────

    def list_fremdwaren(self, eigentuemer_id=None, status=None, warehouse_id=None) -> list[dict]:
        q = self.db.query(FremdwarenEinlagerung).filter(FremdwarenEinlagerung.tenant_id == self.tenant_id)
        if eigentuemer_id:
            q = q.filter(FremdwarenEinlagerung.eigentuemer_id == eigentuemer_id)
        if status:
            q = q.filter(FremdwarenEinlagerung.status == status)
        if warehouse_id:
            q = q.filter(FremdwarenEinlagerung.warehouse_id == warehouse_id)
        return [
            {"id": str(fw.id), "einlagerungs_nr": fw.einlagerungs_nr, "eigentuemer_id": fw.eigentuemer_id,
             "eigentuemer_name": fw.eigentuemer_name, "artikel_bezeichnung": fw.artikel_bezeichnung,
             "charge": fw.charge, "einlagerungstyp": fw.einlagerungstyp,
             "menge_eingelagert": float(fw.menge_eingelagert), "menge_aktuell": float(fw.menge_aktuell),
             "einheit": fw.einheit,
             "einlagerungsdatum": fw.einlagerungsdatum.isoformat() if fw.einlagerungsdatum else None,
             "geplante_auslagerung": fw.geplante_auslagerung.isoformat() if fw.geplante_auslagerung else None,
             "gebuehr_pro_tag": float(fw.gebuehr_pro_tag) if fw.gebuehr_pro_tag else None,
             "status": fw.status}
            for fw in q.order_by(FremdwarenEinlagerung.einlagerungsdatum.desc()).all()
        ]

    def create_fremdwaren(self, data: dict) -> dict:
        fw = FremdwarenEinlagerung(id=uuid7(), tenant_id=self.tenant_id,
                                   menge_aktuell=data["menge_eingelagert"], **data)
        self.db.add(fw)
        self.db.commit()
        self.db.refresh(fw)
        return {"id": str(fw.id), "einlagerungs_nr": fw.einlagerungs_nr}

    def update_fremdwaren(self, einlagerung_id: str, data: dict) -> dict:
        fw = self.db.query(FremdwarenEinlagerung).filter(
            FremdwarenEinlagerung.id == einlagerung_id, FremdwarenEinlagerung.tenant_id == self.tenant_id,
        ).first()
        if not fw:
            raise EntityNotFoundError("FremdwarenEinlagerung", einlagerung_id)
        for field in ("menge_aktuell", "status", "auslagerungsdatum",
                      "geplante_auslagerung", "notiz", "lagerort"):
            if field in data:
                setattr(fw, field, data[field])
        self.db.commit()
        return {"id": str(fw.id), "status": fw.status}
