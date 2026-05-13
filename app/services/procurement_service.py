"""Service layer for Einkauf/Procurement domain."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from sqlalchemy import func as sqlfunc
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

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
    engine_lager,
    engine_rohware,
    engine_verkauf,
    save_vorschlag,
    vorschlag_zu_bestellungen,
)
from modules.einkauf.services.versand_service import versende_bestellung


def _model_cols(obj) -> dict[str, Any]:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns
            if c.name not in ("created_at", "updated_at")}


class ProcurementService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Bestellvorschlag engines ──────────────────────────────────────────────

    def compute_vorschlag_lager(self, niederlassung_id, artikelgruppe, artikel_nr, warehouse_id, nur_unter_meldebestand) -> list[dict]:
        return engine_lager(self.db, tenant_id=self.tenant_id, niederlassung_id=niederlassung_id,
                            artikelgruppe=artikelgruppe, artikel_nr=artikel_nr,
                            warehouse_id=warehouse_id, nur_unter_meldebestand=nur_unter_meldebestand)

    def compute_vorschlag_verkauf(self, niederlassung_id, artikelgruppe, von_datum, bis_datum) -> list[dict]:
        return engine_verkauf(self.db, tenant_id=self.tenant_id, niederlassung_id=niederlassung_id,
                              artikelgruppe=artikelgruppe, von_datum=von_datum, bis_datum=bis_datum)

    def compute_vorschlag_rohware(self, stichtag, niederlassung_id) -> list[dict]:
        return engine_rohware(self.db, tenant_id=self.tenant_id, stichtag=stichtag, niederlassung_id=niederlassung_id)

    # ── Bestellvorschläge CRUD ────────────────────────────────────────────────

    def list_vorschlaege(self, vorschlag_typ=None, status=None, von=None, bis=None) -> list[dict]:
        q = self.db.query(EinkaufBestellvorschlag).filter(EinkaufBestellvorschlag.tenant_id == self.tenant_id)
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
        q = self.db.query(EinkaufBestellung).filter(EinkaufBestellung.tenant_id == self.tenant_id)
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

    def create_bestellung(self, data: dict) -> dict:
        ts = datetime.now().strftime("%y%m%d%H%M%S")
        bestellung = EinkaufBestellung(
            id=uuid7(), tenant_id=self.tenant_id, bestellnummer=f"EK-{ts}",
            **{k: v for k, v in data.items() if k != "positionen"},
        )
        self.db.add(bestellung)
        self.db.flush()
        for i, pos_data in enumerate(data.get("positionen", []), start=1):
            pos = EinkaufBestellungPosition(
                id=uuid7(), bestellung_id=bestellung.id, pos_nr=i,
                artikel_nr=pos_data.get("artikel_nr", ""),
                artikel_bezeichnung=pos_data.get("artikel_bezeichnung", ""),
                article_id=pos_data.get("article_id"),
                menge=pos_data.get("menge", 0), menge_geliefert=0,
                menge_offen=pos_data.get("menge", 0),
                einheit=pos_data.get("einheit", "t"),
                einzelpreis=pos_data.get("einzelpreis"),
                preis_einheit=pos_data.get("preis_einheit", "100kg"),
            )
            self.db.add(pos)
        self.db.commit()
        self.db.refresh(bestellung)
        return {"id": str(bestellung.id), "bestellnummer": bestellung.bestellnummer}

    def get_bestellung(self, bestellung_id: str) -> dict:
        b = self.db.query(EinkaufBestellung).filter(
            EinkaufBestellung.id == bestellung_id, EinkaufBestellung.tenant_id == self.tenant_id,
        ).first()
        if not b:
            raise EntityNotFoundError("EinkaufBestellung", bestellung_id)
        return {
            "id": str(b.id), "bestellnummer": b.bestellnummer, "lieferant_id": str(b.lieferant_id),
            "lieferant_name": b.lieferant.firmenname if b.lieferant else None,
            "bestelldatum": b.bestelldatum.isoformat() if b.bestelldatum else None,
            "lieferdatum_wunsch": b.lieferdatum_wunsch.isoformat() if b.lieferdatum_wunsch else None,
            "lieferdatum_zugesagt": b.lieferdatum_zugesagt.isoformat() if b.lieferdatum_zugesagt else None,
            "status": b.status, "versand_art": b.versand_art,
            "netto_summe": float(b.netto_summe) if b.netto_summe else None,
            "mwst_betrag": float(b.mwst_betrag) if b.mwst_betrag else None,
            "brutto_summe": float(b.brutto_summe) if b.brutto_summe else None,
            "unsere_referenz": b.unsere_referenz, "ihre_referenz": b.ihre_referenz,
            "freitext_kopf": b.freitext_kopf, "freitext_fuss": b.freitext_fuss, "notiz": b.notiz,
            "positionen": [
                {"id": str(p.id), "pos_nr": p.pos_nr, "article_id": p.article_id,
                 "artikel_nr": p.artikel_nr, "artikel_bezeichnung": p.artikel_bezeichnung,
                 "lieferanten_artnr": p.lieferanten_artnr, "menge": float(p.menge),
                 "menge_geliefert": float(p.menge_geliefert or 0),
                 "menge_offen": float(p.menge_offen or p.menge),
                 "einheit": p.einheit, "einzelpreis": float(p.einzelpreis) if p.einzelpreis else None,
                 "preis_einheit": p.preis_einheit,
                 "netto_betrag": float(p.netto_betrag) if p.netto_betrag else None, "status": p.status}
                for p in b.positionen
            ],
        }

    def update_bestellung(self, bestellung_id: str, data: dict) -> dict:
        b = self.db.query(EinkaufBestellung).filter(
            EinkaufBestellung.id == bestellung_id, EinkaufBestellung.tenant_id == self.tenant_id,
        ).first()
        if not b:
            raise EntityNotFoundError("EinkaufBestellung", bestellung_id)
        for field in ("status", "lieferdatum_zugesagt", "lieferdatum_wunsch",
                      "notiz", "freitext_kopf", "freitext_fuss", "unsere_referenz", "ihre_referenz"):
            if field in data:
                setattr(b, field, data[field])
        self.db.commit()
        return {"id": str(b.id), "status": b.status}

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
        self.db.commit()
        return {"bestellung_id": str(b.id), "bestellnummer": b.bestellnummer, "status": b.status}

    def storniere_bestellung(self, bestellung_id: str) -> dict:
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
        self.db.commit()
        return {"bestellung_id": str(b.id), "bestellnummer": b.bestellnummer, "status": b.status}

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
