"""Service layer for Einkauf/Procurement domain."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from sqlalchemy import func as sqlfunc, text as sqltext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.business_time import business_today
from app.core.exceptions import ConflictError, EntityNotFoundError
from app.core.uuid7 import uuid7
from app.infrastructure.models.einkauf_models import (
    ArtikelLagerParameter,
    EinkaufBestellvorschlag,
    EinkaufKontrakt,
    EinkaufKontraktPosition,
    EinkaufLieferant,
    FremdwarenEinlagerung,
    LagerKontenzuordnung,
    PalettenKontoBuchung,
    PfandKontoBuchung,
)
from modules.einkauf.services.bestellvorschlag_service import (
    engine_bedarf,
    engine_lager,
    engine_rohware,
    engine_verkauf,
    save_vorschlag,
    vorschlag_zu_bestellungen,
)


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


def _query_one(db: Session, sql: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """Eine Zeile als Dict — oder None."""
    zeile = db.execute(sqltext(sql), params).mappings().first()
    return dict(zeile) if zeile is not None else None


def _query_many(db: Session, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    """Alle Zeilen als Dicts."""
    return [dict(z) for z in db.execute(sqltext(sql), params).mappings().all()]


def _im_mandanten(tenant_id: str):
    """Mandantenkontext fuer Schreibvorgaenge; ein schon gesetzter Kontext desselben Mandanten bleibt."""
    from contextlib import nullcontext

    from app.core.tenant_context import current_tenant_or_none, tenant_scope

    if current_tenant_or_none() == tenant_id:
        return nullcontext()
    return tenant_scope(tenant_id, "ProcurementService schreibt Positionen")


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

    def freigebe_vorschlag(self, vorschlag_id: str, freigegeben_von: str = "system") -> dict:
        try:
            orders = vorschlag_zu_bestellungen(self.db, vorschlag_id=vorschlag_id,
                                               tenant_id=self.tenant_id, freigegeben_von=freigegeben_von)
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

    def create_lieferant(self, data: dict, rollenfelder: Optional[dict] = None) -> dict:
        # Keine Datenbankregel haelt die Nummer eindeutig (Stand 20.10.2026); doppelte Lieferanten-Nummern im
        # Mandanten waren moeglich.
        vorhanden = self.db.query(EinkaufLieferant.id).filter(
            EinkaufLieferant.tenant_id == self.tenant_id,
            EinkaufLieferant.lieferantennummer == data.get("lieferantennummer"),
        ).first()
        if vorhanden:
            raise ConflictError("Lieferantennummer existiert bereits.")
        # Partnerbruecke (Stufe 1): jeder neue Lieferant haengt an einem Geschaeftspartner des Mandanten.
        from app.services.business_partner_service import BusinessPartnerService

        data = {**data, "partner_id": BusinessPartnerService(self.db, self.tenant_id).partner_fuer_rolle(
            "lieferant",
            name=data.get("firmenname") or "",
            vat_id=data.get("ust_id"),
            street=data.get("strasse"),
            postal_code=data.get("plz"),
            city=data.get("ort"),
            country=data.get("land"),
            email=data.get("email"),
            phone=data.get("telefon"),
            partner_id=data.get("partner_id") or None,
            rollenfelder=rollenfelder,
        )}
        lf = EinkaufLieferant(id=uuid7(), tenant_id=self.tenant_id, **data)
        self.db.add(lf)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Lieferantennummer existiert bereits.") from exc
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

    # ── Innovations-Nachschau ─────────────────────────────────────────────────

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
            -- DocFlow (BELEG-052): Probebestellung = Bestellfall innovation im Baustein bestellfall.
            SELECT b.id::text        AS bestellung_id,
                   b.doc_number      AS bestellnummer,
                   b.document_date::date AS bestelldatum,
                   b.bausteine #>> '{bestellfall,hinweis}' AS innovationshinweis,
                   p.article_number  AS artikel_nr,
                   p.description     AS artikel_bezeichnung,
                   a.id::text        AS article_id,
                   p.quantity        AS testmenge,
                   p.unit            AS einheit
            FROM domain_docflow.document_headers b
            JOIN domain_docflow.document_items p ON p.header_id = b.id AND p.tenant_id = b.tenant_id
            LEFT JOIN domain_inventory.articles a ON a.tenant_id = p.tenant_id AND a.article_number = p.article_number
            WHERE b.tenant_id = :tid
              AND b.doc_type = 'purchase_order'
              AND b.deleted_at IS NULL
              AND b.status NOT IN ('draft', 'cancelled', 'reversed')
              AND b.bausteine #>> '{bestellfall,bestellfall}' = 'innovation'
            ORDER BY b.document_date DESC NULLS LAST, p.line_number
            LIMIT 2000
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
