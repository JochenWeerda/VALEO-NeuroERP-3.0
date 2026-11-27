"""Service layer for compat einkauf domain routes."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.akteur import bekannter_nutzer
from app.core.business_time import business_date_after, business_today
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import AuditLog
from app.services.compat_helpers import (
    cache_key,
    enqueue_event,
    list_docs,
    now_iso,
    doc_repo,
    safe_float,
)

logger = logging.getLogger(__name__)

_RECHNUNG_TRANSITIONS = {
    "ENTWURF": "GEPRUEFT",
    "ERFASST": "GEPRUEFT",
    "OFFEN": "GEPRUEFT",
    "GEPRUEFT": "FREIGEGEBEN",
    "FREIGEGEBEN": "VERBUCHT",
}


#: Die Tabelle heisst ``angebotsnummer``/``gesamtbetrag``; Artikel und Lieferzeit stehen
#: an den Positionen. Bis 07.10.2026 las jeder Angebots-Weg Spalten, die keine
#: Migration anlegt, und ein ``except`` machte "nicht gefunden" daraus.
#: ``notizen`` traegt erweiterte Konditionen (mindestabnahme, Zahlungsbedingungen, Incoterms)
#: als JSON — Paritaet zur Legacy-ObjectPage ohne Schema-Migration.
_ANGEBOT_FELDER = (
    "a.id, a.angebotsnummer AS angebots_nummer, a.anfrage_id, a.lieferant_id, a.lieferant_name, "
    "(SELECT p.bezeichnung FROM einkauf_angebote_positionen p WHERE p.angebot_id = a.id "
    " ORDER BY p.pos_nr, p.id LIMIT 1) AS artikel_name, "
    "(SELECT p.artikel_nr FROM einkauf_angebote_positionen p WHERE p.angebot_id = a.id "
    " ORDER BY p.pos_nr, p.id LIMIT 1) AS artikel_nr, "
    "(SELECT p.menge FROM einkauf_angebote_positionen p WHERE p.angebot_id = a.id "
    " ORDER BY p.pos_nr, p.id LIMIT 1) AS menge, "
    "(SELECT p.einheit FROM einkauf_angebote_positionen p WHERE p.angebot_id = a.id "
    " ORDER BY p.pos_nr, p.id LIMIT 1) AS einheit, "
    "(SELECT p.einheitspreis FROM einkauf_angebote_positionen p WHERE p.angebot_id = a.id "
    " ORDER BY p.pos_nr, p.id LIMIT 1) AS einheitspreis, "
    "a.gesamtbetrag AS netto_summe, a.waehrung, a.gueltig_bis, a.status, a.notizen, "
    "(SELECT MAX(p.lieferzeit_tage) FROM einkauf_angebote_positionen p WHERE p.angebot_id = a.id) "
    "AS lieferzeit_tage, a.created_at"
)

#: Ein Angebot in diesen Zustaenden wird nicht (noch einmal) bestellt.
_NICHT_BESTELLBAR = {"IN_BESTELLUNG", "BESTELLT", "ABGELEHNT"}
#: Spalten des Avis wie in der Migration ``einkauf_missing_tables_20260305``.
#: Fahrzeug/Positionen/Bemerkungen liegen in ``notizen`` (JSON) — Paritaet zur Legacy-ObjectPage.
_AVIS_FELDER = (
    "id, avis_nummer, bestell_nr AS bestellung_id, lieferant_id, lieferant_name, status, "
    "erwartetes_datum AS geplantes_anliefer_datum, notizen, created_at"
)


class EinkaufCompatService:
    def __init__(self, db: Session, tenant_id: str, actor: str | None = None) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.actor = actor

    def _invalidate(self) -> None:
        try:
            from app.core.cache import cache_delete_prefix
            cache_delete_prefix(cache_key("procurement", self.tenant_id))
        except Exception:  # noqa: BLE001 — Cache-Invalidierung fehlgeschlagen; nächste Anfrage lädt frisch
            pass

    # ── Lieferanten ──────────────────────────────────────────────────────────

    def list_suppliers(
        self,
        *,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> dict:
        from sqlalchemy import text
        q = "SELECT * FROM einkauf_lieferanten WHERE tenant_id = :tid"
        params: dict[str, Any] = {"tid": self.tenant_id}
        if search:
            q += " AND (name ILIKE :s OR lieferanten_nummer ILIKE :s)"
            params["s"] = f"%{search}%"
        if is_active is not None:
            q += " AND is_active = :active"
            params["active"] = is_active
        q += " ORDER BY name LIMIT :lim OFFSET :skip"
        params["lim"] = limit
        params["skip"] = skip
        rows = self.db.execute(text(q), params).fetchall()
        return {"items": [dict(r._mapping) for r in rows], "total": len(rows)}

    # ── Field mapping helpers ─────────────────────────────────────────────────

    @staticmethod
    def _anfrage_row_to_dict(m: Any) -> dict:
        return {
            "id": str(m.get("id")),
            "anfrageNummer": m.get("anfrage_nummer") or str(m.get("id")),
            "typ": m.get("typ") or "",
            "anforderer": m.get("anforderer") or "",
            "artikel": m.get("artikel") or "",
            "menge": float(m.get("menge") or 0),
            "prioritaet": m.get("prioritaet") or "normal",
            "status": m.get("status") or "offen",
            "faelligkeit": m.get("datum").isoformat()[:10] if m.get("datum") else None,
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    @staticmethod
    def _parse_notizen(raw: Any) -> dict[str, Any]:
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str) and raw.strip():
            try:
                import json
                parsed = json.loads(raw)
                return parsed if isinstance(parsed, dict) else {}
            except Exception:  # noqa: BLE001 — Notizen-Text ohne JSON bleibt Freitext
                return {"bemerkungen": raw}
        return {}

    @classmethod
    def _angebot_row_to_dict(cls, m: Any) -> dict:
        extra = cls._parse_notizen(m.get("notizen"))
        preis = float(m.get("netto_summe") or m.get("einheitspreis") or 0)
        return {
            "id": str(m.get("id")),
            "angebotNummer": m.get("angebots_nummer") or str(m.get("id")),
            "anfrage": str(m.get("anfrage_id") or ""),
            "anfrageId": str(m.get("anfrage_id") or "") or None,
            "lieferant": m.get("lieferant_name") or "",
            "lieferantId": str(m.get("lieferant_id") or "") or None,
            "lieferant_id": str(m.get("lieferant_id") or "") or None,
            "artikel": m.get("artikel_name") or m.get("artikel_nr") or extra.get("artikel") or "",
            "menge": float(m.get("menge") or extra.get("menge") or 0) or None,
            "einheit": m.get("einheit") or extra.get("einheit") or None,
            "preis": preis,
            "waehrung": m.get("waehrung") or "EUR",
            "gueltigBis": m.get("gueltig_bis").isoformat()[:10] if m.get("gueltig_bis") else None,
            "status": m.get("status") or "offen",
            "lieferzeit": (
                int(m["lieferzeit_tage"]) if m.get("lieferzeit_tage") is not None
                else extra.get("lieferzeit")
            ),
            "mindestabnahme": extra.get("mindestabnahme"),
            "zahlungsbedingungen": extra.get("zahlungsbedingungen") or "",
            "incoterms": extra.get("incoterms") or "",
            "bemerkungen": extra.get("bemerkungen") or "",
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    @classmethod
    def _anlieferavis_row_to_dict(cls, m: Any) -> dict:
        extra = cls._parse_notizen(m.get("notizen"))
        fahrzeug = extra.get("fahrzeug") if isinstance(extra.get("fahrzeug"), dict) else {}
        if not fahrzeug and (extra.get("kennzeichen") or extra.get("fahrer") or extra.get("telefon")):
            fahrzeug = {
                "kennzeichen": extra.get("kennzeichen") or "",
                "fahrer": extra.get("fahrer") or "",
                "telefon": extra.get("telefon") or "",
            }
        datum = m.get("geplantes_anliefer_datum")
        return {
            "id": str(m.get("id")),
            "avisNummer": m.get("avis_nummer") or str(m.get("id")),
            "bestellung": str(m.get("bestellung_id") or ""),
            "bestellungId": str(m.get("bestellung_id") or "") or None,
            "lieferant": m.get("lieferant_name") or "",
            "lieferantId": str(m.get("lieferant_id") or "") or None,
            "status": m.get("status") or "offen",
            "geplantesAnlieferDatum": datum.isoformat() if datum else None,
            "kennzeichen": fahrzeug.get("kennzeichen") or extra.get("kennzeichen") or "",
            "fahrer": fahrzeug.get("fahrer") or "",
            "telefon": fahrzeug.get("telefon") or "",
            "fahrzeug": fahrzeug,
            "positionen": extra.get("positionen") if isinstance(extra.get("positionen"), list) else [],
            "bemerkungen": extra.get("bemerkungen") or "",
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    #: Spalten der Tabelle aus ``einkauf_missing_tables_20260305`` (``ab_nummer``, ``bestell_nr``). Bis 19.10.2026
    #: fragte der Dienst ``bestaetigungs_nummer``/``bestellung_id`` ab, die keine Migration anlegt; der Fehler wurde
    #: geschluckt, Liste und Einzelansicht waren in jeder Datenbank leer bzw. 404.
    _AB_SPALTEN = ("id, ab_nummer AS bestaetigungs_nummer, bestell_nr AS bestellung_id, lieferant_name, status, "
                   "created_at")

    @staticmethod
    def _auftragsbestaetigung_row_to_dict(m: Any) -> dict:
        return {
            "id": str(m.get("id")),
            "bestaetigungsNummer": m.get("bestaetigungs_nummer") or str(m.get("id")),
            "bestellung": str(m.get("bestellung_id") or ""),
            "lieferant": m.get("lieferant_name") or "",
            "status": m.get("status") or "offen",
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    @staticmethod
    def _rechnung_row_to_dict(m: Any) -> dict:
        return {
            "id": str(m.get("id")),
            "rechnungsNummer": m.get("rechnungs_nummer") or str(m.get("id")),
            "lieferant": m.get("lieferant_name") or "",
            "bestellung": str(m.get("bestellung_id") or ""),
            "wareneingang": str(m.get("wareneingang_id") or ""),
            "status": m.get("status") or "OFFEN",
            "bruttoBetrag": float(m.get("brutto_betrag") or 0),
            "rechnungsDatum": m.get("rechnungs_datum").isoformat()[:10]
                if m.get("rechnungs_datum") else None,
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    # ── Goods Receipts ────────────────────────────────────────────────────────

    def list_goods_receipts(self) -> list:
        from sqlalchemy import text
        # Bis 27.10.2026 verband die Abfrage docs_store (gibt es in keiner Datenbank) und fiel dann auf
        # Spalten zurueck, die einkauf_wareneingaenge nicht hat: die Liste war immer leer, ohne Mandantenfilter.
        rows = self.db.execute(text(
            """
            SELECT we.id, we.delivery_note_number AS nummer, we.received_date AS datum,
                   we.quality_inspection_status AS status, '' AS lieferant, 0 AS betrag
            FROM einkauf_wareneingaenge we
            WHERE we.tenant_id = :tid
            ORDER BY we.created_at DESC LIMIT 500
            """
        ), {"tid": self.tenant_id}).fetchall()
        return [
            {
                "id": str(r._mapping.get("id")),
                "nummer": r._mapping.get("nummer") or str(r._mapping.get("id")),
                "datum": r._mapping.get("datum").isoformat()[:10] if r._mapping.get("datum") else None,
                "status": r._mapping.get("status") or "offen",
                "lieferant": r._mapping.get("lieferant") or "",
                "betrag": float(r._mapping.get("betrag") or 0),
            }
            for r in rows
        ]

    # ── Anfragen ──────────────────────────────────────────────────────────────

    def list_anfragen(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, anfrage_nummer, typ, anforderer, artikel, menge, einheit, prioritaet, "
                "status, datum, created_at FROM einkauf_anfragen "
                "WHERE tenant_id = :tid ORDER BY created_at DESC LIMIT 500"
            ), {"tid": self.tenant_id}).fetchall()
        except Exception:
            return []
        return [self._anfrage_row_to_dict(r._mapping) for r in rows]

    def get_anfrage(self, anfrage_id: str) -> dict:
        row = self._load_anfrage_raw_row(anfrage_id)  # mit Mandant (vorher: jede Anfrage jedes Mandanten)
        if row is None:
            raise EntityNotFoundError("Anfrage", anfrage_id)
        return self._anfrage_row_to_dict(row._mapping)

    def _load_anfrage_raw_row(self, anfrage_id: str) -> Any:
        from sqlalchemy import text
        try:
            return self.db.execute(text(
                "SELECT id, anfrage_nummer, typ, anforderer, artikel, menge, einheit, prioritaet, "
                "status, datum, created_at FROM einkauf_anfragen "
                "WHERE (id = :fid OR anfrage_nummer = :fid) AND tenant_id = :tid "
                "ORDER BY created_at DESC LIMIT 1"
            ), {"fid": anfrage_id, "tid": self.tenant_id}).fetchone()
        except Exception:
            self.db.rollback()  # sonst ist die Transaktion tot fuer alles Folgende
            return None

    async def convert_anfrage_to_order(self, anfrage_id: str) -> dict:
        """Bestellentwurf in DocFlow aus der Anfrage (BELEG-052; vorher ein weiterer Bestellspeicher).

        Anfragestatus und Entwurf gelten zusammen: Die Anlage committet beides, scheitert sie, bleibt die Anfrage.
        """
        from sqlalchemy import text
        from app.services.beleg_anlage import Position, lege_beleg_an
        row = self._load_anfrage_raw_row(anfrage_id)
        if row is None:
            raise EntityNotFoundError("Anfrage", anfrage_id)
        m = row._mapping
        nummer = str(m.get("anfrage_nummer") or m.get("id"))
        self.db.execute(text(
            "UPDATE einkauf_anfragen SET status = 'BESTELLT', updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id AND tenant_id = :tid"
        ), {"id": m.get("id"), "tid": self.tenant_id})
        entwurf = lege_beleg_an(
            self.db, self.tenant_id, "purchase_order", partner_id=None,
            positionen=[Position(artikel_nr=str(m.get("artikel") or "Bedarfsposition"),
                                 bezeichnung=m.get("artikel") or "Bedarfsposition",
                                 menge=float(m.get("menge") or 0), einheit=m.get("einheit") or "Stk")],
            quelle="anfrage", referenz=nummer, entwurf_nr=f"ANF-{nummer}", akteur="einkauf",
            idempotenz=f"anfrage-bestellung-{m.get('id')}")
        self._invalidate()
        return {"message": "Anfrage in Bestellung ueberfuehrt",
                "purchaseOrderId": entwurf,
                "purchaseOrderNumber": self._entwurfsnummer(entwurf),
                "status": "BESTELLT"}

    def _entwurfsnummer(self, beleg_id: str) -> str | None:
        from sqlalchemy import text
        return self.db.execute(text(
            "SELECT doc_number FROM domain_docflow.document_headers WHERE id = :id AND tenant_id = :tid"
        ), {"id": beleg_id, "tid": self.tenant_id}).scalar()

    def list_bids(self, anfrage_id: str) -> list:
        from sqlalchemy import text
        rows = self.db.execute(text(
            f"SELECT {_ANGEBOT_FELDER} FROM einkauf_angebote a "  # nosec B608  # reviewed-safe: Feldliste ist ein Code-Literal
            "WHERE a.anfrage_id = :fid AND a.tenant_id = :tid ORDER BY a.created_at DESC LIMIT 500"
        ), {"fid": anfrage_id, "tid": self.tenant_id}).fetchall()
        return [
            {
                "id": str(r._mapping.get("id")),
                "nummer": r._mapping.get("angebots_nummer") or str(r._mapping.get("id")),
                "lieferant": r._mapping.get("lieferant_name") or "",
                "preis": float(r._mapping.get("netto_summe") or 0),
                "waehrung": r._mapping.get("waehrung") or "EUR",
                "status": r._mapping.get("status") or "offen",
                "createdAt": r._mapping.get("created_at").isoformat() if r._mapping.get("created_at") else None,
            }
            for r in rows
        ]

    # ── Angebote ──────────────────────────────────────────────────────────────

    def list_angebote(self) -> list:
        from sqlalchemy import text
        rows = self.db.execute(text(
            f"SELECT {_ANGEBOT_FELDER} FROM einkauf_angebote a "  # nosec B608  # reviewed-safe: Feldliste ist ein Code-Literal
            "WHERE a.tenant_id = :tid ORDER BY a.created_at DESC LIMIT 500"
        ), {"tid": self.tenant_id}).fetchall()
        return [self._angebot_row_to_dict(r._mapping) for r in rows]

    def get_angebot(self, angebot_id: str) -> dict:
        row = self._load_angebot_raw_row(angebot_id)
        if row is None:
            raise EntityNotFoundError("Angebot", angebot_id)
        return self._angebot_row_to_dict(row._mapping)

    def _angebot_notizen_payload(self, payload: dict[str, Any]) -> str | None:
        import json
        body = {
            "mindestabnahme": payload.get("mindestabnahme"),
            "zahlungsbedingungen": payload.get("zahlungsbedingungen") or "",
            "incoterms": payload.get("incoterms") or "",
            "bemerkungen": payload.get("bemerkungen") or payload.get("notizen") or "",
            "lieferzeit": payload.get("lieferzeit"),
            "artikel": payload.get("artikel"),
            "menge": payload.get("menge"),
            "einheit": payload.get("einheit"),
        }
        if not any(v not in (None, "", []) for v in body.values()):
            return None
        return json.dumps(body, ensure_ascii=False)

    def create_angebot(self, payload: dict[str, Any]) -> dict:
        """Legt ein Angebot inkl. Kopf-/Positions-/Konditionsfeldern der Legacy-Maske an."""
        from sqlalchemy import text
        new_id = uuid7()
        nummer = str(payload.get("angebotNummer") or payload.get("angebotsnummer") or f"ANG-{new_id[:8].upper()}")
        lieferant_name = str(payload.get("lieferant") or payload.get("lieferant_name") or "").strip() or None
        lieferant_id = payload.get("lieferantId") or payload.get("lieferant_id")
        anfrage_id = payload.get("anfrageId") or payload.get("anfrage_id") or payload.get("anfrage")
        gueltig_bis = payload.get("gueltigBis") or payload.get("gueltig_bis")
        waehrung = str(payload.get("waehrung") or payload.get("currency") or "EUR")
        menge = safe_float(payload.get("menge") or 0)
        preis = safe_float(payload.get("preis") or payload.get("gesamtbetrag") or 0)
        gesamt = preis * menge if menge and preis and not payload.get("gesamtbetrag") else preis
        status = str(payload.get("status") or "ERFASST")
        notizen = self._angebot_notizen_payload(payload)
        self.db.execute(text("""
            INSERT INTO einkauf_angebote
                (id, tenant_id, anfrage_id, angebotsnummer, lieferant_id, lieferant_name,
                 gesamtbetrag, waehrung, gueltig_bis, status, notizen, created_at, updated_at)
            VALUES
                (:id, :tid, :anfrage, :nr, :lid, :lname, :betrag, :whr, :gueltig, :status, :notizen,
                 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {
            "id": new_id, "tid": self.tenant_id, "anfrage": str(anfrage_id) if anfrage_id else None,
            "nr": nummer, "lid": str(lieferant_id) if lieferant_id else None,
            "lname": lieferant_name, "betrag": gesamt, "whr": waehrung, "gueltig": gueltig_bis,
            "status": status, "notizen": notizen,
        })
        artikel = str(payload.get("artikel") or "").strip()
        if artikel or menge or preis:
            pos_id = uuid7()
            einheit = str(payload.get("einheit") or "Stk")
            lieferzeit = payload.get("lieferzeit")
            try:
                lieferzeit_tage = int(lieferzeit) if lieferzeit not in (None, "") else None
            except (TypeError, ValueError):
                lieferzeit_tage = None
            self.db.execute(text("""
                INSERT INTO einkauf_angebote_positionen
                    (id, angebot_id, pos_nr, artikel_nr, bezeichnung, menge, einheit,
                     einheitspreis, gesamtpreis, lieferzeit_tage)
                VALUES
                    (:id, :aid, 1, :art, :bez, :menge, :einheit, :preis, :gesamt, :lt)
            """), {
                "id": pos_id, "aid": new_id, "art": artikel or None, "bez": artikel or None,
                "menge": menge, "einheit": einheit, "preis": preis, "gesamt": gesamt,
                "lt": lieferzeit_tage,
            })
        self.db.commit()
        self._invalidate()
        return self.get_angebot(new_id)

    def update_angebot(self, angebot_id: str, payload: dict[str, Any]) -> dict:
        """Aktualisiert Kopf-/Konditionsfelder — gleicher Vertrag wie Create (Human/CI/MCP)."""
        from sqlalchemy import text
        row = self._load_angebot_raw_row(angebot_id)
        if row is None:
            raise EntityNotFoundError("Angebot", angebot_id)
        m = row._mapping
        entity_id = str(m.get("id"))
        lieferant_id = payload.get("lieferantId") or payload.get("lieferant_id")
        if lieferant_id is None:
            lieferant_id = m.get("lieferant_id")
        lieferant_name = payload.get("lieferant") if "lieferant" in payload else m.get("lieferant_name")
        anfrage_id = payload.get("anfrageId") or payload.get("anfrage_id") or payload.get("anfrage")
        if anfrage_id is None and "anfrageId" not in payload and "anfrage" not in payload:
            anfrage_id = m.get("anfrage_id")
        gueltig_bis = payload.get("gueltigBis") if "gueltigBis" in payload else (
            m.get("gueltig_bis").isoformat()[:10] if m.get("gueltig_bis") else None
        )
        waehrung = str(payload.get("waehrung") or m.get("waehrung") or "EUR")
        status = str(payload.get("status") or m.get("status") or "ERFASST")
        nummer = str(payload.get("angebotNummer") or m.get("angebots_nummer") or entity_id)
        notizen = self._angebot_notizen_payload(payload)
        if notizen is None and m.get("notizen"):
            notizen = m.get("notizen") if isinstance(m.get("notizen"), str) else None
        menge = safe_float(payload.get("menge") if "menge" in payload else (m.get("menge") or 0))
        preis = safe_float(payload.get("preis") if "preis" in payload else (m.get("netto_summe") or 0))
        gesamt = preis * menge if menge and preis and "gesamtbetrag" not in payload else preis
        self.db.execute(text("""
            UPDATE einkauf_angebote SET
                angebotsnummer = :nr, anfrage_id = :anfrage, lieferant_id = :lid,
                lieferant_name = :lname, gesamtbetrag = :betrag, waehrung = :whr,
                gueltig_bis = :gueltig, status = :status, notizen = :notizen,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id AND tenant_id = :tid
        """), {
            "id": entity_id, "tid": self.tenant_id, "nr": nummer,
            "anfrage": str(anfrage_id) if anfrage_id else None,
            "lid": str(lieferant_id) if lieferant_id else None,
            "lname": lieferant_name, "betrag": gesamt, "whr": waehrung,
            "gueltig": gueltig_bis, "status": status, "notizen": notizen,
        })
        if any(k in payload for k in ("artikel", "menge", "einheit", "preis", "lieferzeit")):
            artikel = str(payload.get("artikel") or m.get("artikel_name") or m.get("artikel_nr") or "").strip()
            einheit = str(payload.get("einheit") or m.get("einheit") or "Stk")
            try:
                lieferzeit_tage = int(payload.get("lieferzeit")) if payload.get("lieferzeit") not in (None, "") else m.get("lieferzeit_tage")
            except (TypeError, ValueError):
                lieferzeit_tage = m.get("lieferzeit_tage")
            existing = self.db.execute(text(
                "SELECT id FROM einkauf_angebote_positionen WHERE angebot_id = :aid ORDER BY pos_nr, id LIMIT 1"
            ), {"aid": entity_id}).fetchone()
            if existing:
                self.db.execute(text("""
                    UPDATE einkauf_angebote_positionen SET
                        artikel_nr = :art, bezeichnung = :bez, menge = :menge, einheit = :einheit,
                        einheitspreis = :preis, gesamtpreis = :gesamt, lieferzeit_tage = :lt
                    WHERE id = :id
                """), {
                    "id": existing[0], "art": artikel or None, "bez": artikel or None,
                    "menge": menge, "einheit": einheit, "preis": preis, "gesamt": gesamt,
                    "lt": lieferzeit_tage,
                })
            elif artikel or menge or preis:
                self.db.execute(text("""
                    INSERT INTO einkauf_angebote_positionen
                        (id, angebot_id, pos_nr, artikel_nr, bezeichnung, menge, einheit,
                         einheitspreis, gesamtpreis, lieferzeit_tage)
                    VALUES (:id, :aid, 1, :art, :bez, :menge, :einheit, :preis, :gesamt, :lt)
                """), {
                    "id": uuid7(), "aid": entity_id, "art": artikel or None, "bez": artikel or None,
                    "menge": menge, "einheit": einheit, "preis": preis, "gesamt": gesamt,
                    "lt": lieferzeit_tage,
                })
        self.db.commit()
        self._invalidate()
        return self.get_angebot(entity_id)

    def _load_angebot_raw_row(self, angebot_id: str) -> Any:
        from sqlalchemy import text
        return self.db.execute(text(
            f"SELECT {_ANGEBOT_FELDER} FROM einkauf_angebote a "  # nosec B608  # reviewed-safe: Feldliste ist ein Code-Literal
            "WHERE (a.id = :aid OR a.angebotsnummer = :aid) AND a.tenant_id = :tid "
            "ORDER BY a.created_at DESC LIMIT 1"
        ), {"aid": angebot_id, "tid": self.tenant_id}).fetchone()

    def update_angebot_status(
        self, angebot_id: str, new_status: str, change_type: str
    ) -> dict:
        from sqlalchemy import text
        row = self._load_angebot_raw_row(angebot_id)
        if row is None:
            raise EntityNotFoundError("Angebot", angebot_id)
        m = row._mapping
        self.db.execute(text(
            "UPDATE einkauf_angebote SET status = :status, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id AND tenant_id = :tid"
        ), {"status": new_status, "id": m.get("id"), "tid": self.tenant_id})
        self.db.commit()
        self._invalidate()
        return {"message": f"Angebot {change_type.lower()}", "status": new_status,
                "id": str(m.get("id")),
                "angebotNummer": m.get("angebots_nummer") or str(m.get("id"))}

    async def convert_angebot_to_order(self, angebot_id: str) -> dict:
        """Macht aus dem Angebot **eine** Bestellung — mit seinen Positionen.

        Bestellung und Angebotsstatus entstehen in **einem** Commit. Ein Angebot ohne
        Positionen wird nicht bestellt (vorher: eine erfundene Sammelposition), ein
        bereits bestelltes nicht noch einmal (Zeilensperre gegen Doppelklick).
        """
        from sqlalchemy import text
        from app.services.beleg_anlage import lege_beleg_an, position_in_preiseinheit
        row = self._load_angebot_raw_row(angebot_id)
        if row is None:
            raise EntityNotFoundError("Angebot", angebot_id)
        m = row._mapping
        aktuell = self.db.execute(text(
            "SELECT status FROM einkauf_angebote WHERE id = :id AND tenant_id = :tid FOR UPDATE"
        ), {"id": m.get("id"), "tid": self.tenant_id}).scalar()
        if str(aktuell or "").upper() in _NICHT_BESTELLBAR:
            raise ConflictError(f"Angebot {m.get('angebots_nummer') or m.get('id')} ist {aktuell} und wird nicht bestellt.")
        positionen = self.db.execute(text(
            "SELECT pos_nr, artikel_nr, bezeichnung, menge, einheit, einheitspreis "
            "FROM einkauf_angebote_positionen WHERE angebot_id = :id ORDER BY pos_nr, id LIMIT 500"
        ), {"id": m.get("id")}).fetchmany(500)
        if not positionen:
            raise ValidationFailedError("Ein Angebot ohne Positionen wird nicht bestellt.")
        try:
            lieferant = uuid.UUID(str(m.get("lieferant_id") or ""))
        except ValueError:
            lieferant = None
        if lieferant is None or not self.db.execute(text(
            "SELECT 1 FROM domain_einkauf.lieferanten WHERE id = CAST(:id AS uuid) AND tenant_id = :tid"
        ), {"id": str(lieferant), "tid": self.tenant_id}).scalar():
            raise ValidationFailedError("Ein Angebot ohne Lieferanten dieses Mandanten wird nicht bestellt.")
        nummer = str(m.get("angebots_nummer") or m.get("id"))
        try:
            # Kanonisch ist DocFlow (BELEG-052): ein Bestellentwurf, freigegeben wird in der Belegmaske. Der
            # Angebotsstatus steht vorher in derselben Transaktion; die Anlage committet beides.
            self.db.execute(text(
                "UPDATE einkauf_angebote SET status = 'IN_BESTELLUNG', updated_at = CURRENT_TIMESTAMP "
                "WHERE id = :id AND tenant_id = :tid"
            ), {"id": m.get("id"), "tid": self.tenant_id})
            entwurf = lege_beleg_an(
                self.db, self.tenant_id, "purchase_order", partner_id=str(lieferant),
                positionen=[position_in_preiseinheit(
                    artikel_nr=z.artikel_nr or f"Position {z.pos_nr}", menge=z.menge or 0, einheit=z.einheit or "Stk",
                    einzelpreis=z.einheitspreis or 0, preis_einheit=z.einheit or "Stk",
                    bezeichnung=z.bezeichnung or z.artikel_nr) for z in positionen],
                quelle="angebot", referenz=nummer, entwurf_nr=f"ANG-{nummer}", akteur="einkauf",
                idempotenz=f"angebot-bestellung-{m.get('id')}")
        except Exception:
            self.db.rollback()
            raise
        self._invalidate()
        return {"message": "Angebot in Bestellung ueberfuehrt",
                "purchaseOrderId": entwurf,
                "purchaseOrderNumber": self._entwurfsnummer(entwurf),
                "status": "IN_BESTELLUNG"}

    # ── Anlieferavis ──────────────────────────────────────────────────────────

    def list_anlieferavis(self) -> list:
        from sqlalchemy import text
        # Bis 20.10.2026 las die Abfrage Spalten, die keine Migration anlegt, und verschluckte den Fehler:
        # Liste immer leer, Objektmaske immer 404.
        rows = self.db.execute(text(
            f"SELECT {_AVIS_FELDER} FROM einkauf_anlieferavis "  # nosec B608  # reviewed-safe: Feldliste ist ein Code-Literal
            "WHERE tenant_id = :tid ORDER BY created_at DESC LIMIT 500"
        ), {"tid": self.tenant_id}).fetchall()
        return [self._anlieferavis_row_to_dict(r._mapping) for r in rows]

    def get_anlieferavis(self, avis_id: str) -> dict:
        from sqlalchemy import text
        row = self.db.execute(text(
            f"SELECT {_AVIS_FELDER} FROM einkauf_anlieferavis "  # nosec B608  # reviewed-safe: Feldliste ist ein Code-Literal
            "WHERE (id = :aid OR avis_nummer = :aid) AND tenant_id = :tid "
            "ORDER BY created_at DESC LIMIT 1"
        ), {"aid": avis_id, "tid": self.tenant_id}).fetchone()
        if row is None:
            raise EntityNotFoundError("Anlieferavis", avis_id)
        return self._anlieferavis_row_to_dict(row._mapping)

    def _avis_notizen_payload(self, payload: dict[str, Any]) -> str | None:
        import json
        fahrzeug_in = payload.get("fahrzeug") if isinstance(payload.get("fahrzeug"), dict) else {}
        fahrzeug = {
            "kennzeichen": (
                payload.get("kennzeichen")
                or fahrzeug_in.get("kennzeichen")
                or payload.get("fahrzeug.kennzeichen")
                or ""
            ),
            "fahrer": (
                payload.get("fahrer")
                or fahrzeug_in.get("fahrer")
                or payload.get("fahrzeug.fahrer")
                or ""
            ),
            "telefon": (
                payload.get("telefon")
                or fahrzeug_in.get("telefon")
                or payload.get("fahrzeug.telefon")
                or ""
            ),
        }
        body = {
            "fahrzeug": fahrzeug,
            "kennzeichen": fahrzeug["kennzeichen"],
            "fahrer": fahrzeug["fahrer"],
            "telefon": fahrzeug["telefon"],
            "bemerkungen": payload.get("bemerkungen") or "",
            "positionen": payload.get("positionen") if isinstance(payload.get("positionen"), list) else [],
        }
        if not any([
            body["kennzeichen"], body["fahrer"], body["telefon"], body["bemerkungen"], body["positionen"],
        ]):
            return None
        return json.dumps(body, ensure_ascii=False)

    def create_anlieferavis(self, payload: dict[str, Any]) -> dict:
        """Legt einen Anlieferavis inkl. Fahrzeug-/Positionsfeldern der Legacy-Maske an."""
        from sqlalchemy import text
        new_id = uuid7()
        nummer = str(payload.get("avisNummer") or payload.get("avis_nummer") or f"AVIS-{new_id[:8].upper()}")
        lieferant_name = str(payload.get("lieferant") or payload.get("lieferant_name") or "").strip() or None
        lieferant_id = payload.get("lieferantId") or payload.get("lieferant_id")
        bestell_nr = (
            payload.get("bestellungId") or payload.get("bestellung")
            or payload.get("bestell_nr") or payload.get("bestellung_id")
        )
        erwartetes = payload.get("geplantesAnlieferDatum") or payload.get("erwartetes_datum")
        if isinstance(erwartetes, str) and "T" in erwartetes:
            erwartetes = erwartetes[:10]
        status = str(payload.get("status") or "GESENDET")
        notizen = self._avis_notizen_payload(payload)
        self.db.execute(text("""
            INSERT INTO einkauf_anlieferavis
                (id, tenant_id, avis_nummer, bestell_nr, lieferant_id, lieferant_name,
                 erwartetes_datum, status, notizen, created_at, updated_at)
            VALUES
                (:id, :tid, :nr, :bestell, :lid, :lname, :datum, :status, :notizen,
                 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {
            "id": new_id, "tid": self.tenant_id, "nr": nummer,
            "bestell": str(bestell_nr) if bestell_nr else None,
            "lid": str(lieferant_id) if lieferant_id else None,
            "lname": lieferant_name, "datum": erwartetes, "status": status, "notizen": notizen,
        })
        self.db.commit()
        self._invalidate()
        return self.get_anlieferavis(new_id)

    def update_anlieferavis(self, avis_id: str, payload: dict[str, Any]) -> dict:
        """Aktualisiert Avis-Felder — gleicher Vertrag wie Create (Human/CI/MCP)."""
        from sqlalchemy import text
        current = self.get_anlieferavis(avis_id)
        entity_id = current["id"]
        nummer = str(payload.get("avisNummer") or current.get("avisNummer") or entity_id)
        bestell_nr = (
            payload.get("bestellungId") if "bestellungId" in payload
            else payload.get("bestellung") if "bestellung" in payload
            else current.get("bestellungId") or current.get("bestellung")
        )
        lieferant_name = payload.get("lieferant") if "lieferant" in payload else current.get("lieferant")
        lieferant_id = (
            payload.get("lieferantId") if "lieferantId" in payload
            else current.get("lieferantId")
        )
        erwartetes = (
            payload.get("geplantesAnlieferDatum") if "geplantesAnlieferDatum" in payload
            else current.get("geplantesAnlieferDatum")
        )
        if isinstance(erwartetes, str) and "T" in erwartetes:
            erwartetes = erwartetes[:10]
        status = str(payload.get("status") or current.get("status") or "GESENDET")
        merged = {**current, **payload}
        if "fahrzeug" not in payload and any(k in payload for k in ("kennzeichen", "fahrer", "telefon")):
            merged["fahrzeug"] = {
                "kennzeichen": payload.get("kennzeichen", current.get("kennzeichen")),
                "fahrer": payload.get("fahrer", current.get("fahrer")),
                "telefon": payload.get("telefon", current.get("telefon")),
            }
        notizen = self._avis_notizen_payload(merged)
        self.db.execute(text("""
            UPDATE einkauf_anlieferavis SET
                avis_nummer = :nr, bestell_nr = :bestell, lieferant_id = :lid,
                lieferant_name = :lname, erwartetes_datum = :datum, status = :status,
                notizen = :notizen, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id AND tenant_id = :tid
        """), {
            "id": entity_id, "tid": self.tenant_id, "nr": nummer,
            "bestell": str(bestell_nr) if bestell_nr else None,
            "lid": str(lieferant_id) if lieferant_id else None,
            "lname": lieferant_name, "datum": erwartetes, "status": status, "notizen": notizen,
        })
        self.db.commit()
        self._invalidate()
        return self.get_anlieferavis(entity_id)

    def transition_anlieferavis(self, avis_id: str, action: str) -> dict:
        from sqlalchemy import text
        status_map = {"send": "GESENDET", "confirm": "BESTAETIGT", "cancel": "STORNIERT"}
        if action not in status_map:
            raise ValidationFailedError(f"Unknown action: {action}")
        try:
            row = self.db.execute(text(
                "SELECT id, avis_nummer FROM einkauf_anlieferavis "
                "WHERE (id = :aid OR avis_nummer = :aid) AND tenant_id = :tid "
                "ORDER BY created_at DESC LIMIT 1"
            ), {"aid": avis_id, "tid": self.tenant_id}).fetchone()
        except Exception:
            row = None
        if row is None:
            raise EntityNotFoundError("Anlieferavis", avis_id)
        new_status = status_map[action]
        self.db.execute(text(
            "UPDATE einkauf_anlieferavis SET status = :status, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id AND tenant_id = :tid"
        ), {"status": new_status, "id": row._mapping.get("id"), "tid": self.tenant_id})
        self.db.commit()
        self._invalidate()
        return {"message": f"Anlieferavis {action}", "status": new_status,
                "id": str(row._mapping.get("id")),
                "avisNummer": row._mapping.get("avis_nummer") or str(row._mapping.get("id"))}

    # ── Auftragsbestaetigungen ────────────────────────────────────────────────

    def list_auftragsbestaetigungen(self) -> list:
        from sqlalchemy import text
        rows = self.db.execute(text(
            f"SELECT {self._AB_SPALTEN} FROM einkauf_auftragsbestaetigungen "
            "WHERE tenant_id = :tid ORDER BY created_at DESC LIMIT 500"  # nosec B608  # feste Spaltenliste
        ), {"tid": self.tenant_id}).fetchall()
        return [self._auftragsbestaetigung_row_to_dict(r._mapping) for r in rows]

    def get_auftragsbestaetigung(self, bestaetigung_id: str) -> dict:
        from sqlalchemy import text
        row = self.db.execute(text(
            f"SELECT {self._AB_SPALTEN} FROM einkauf_auftragsbestaetigungen "
            "WHERE (id = :aid OR ab_nummer = :aid) AND tenant_id = :tid ORDER BY created_at DESC LIMIT 1"  # nosec B608
        ), {"aid": bestaetigung_id, "tid": self.tenant_id}).fetchone()
        if row is None:
            raise EntityNotFoundError("Auftragsbestaetigung", bestaetigung_id)
        return self._auftragsbestaetigung_row_to_dict(row._mapping)

    def transition_auftragsbestaetigung(self, bestaetigung_id: str, action: str) -> dict:
        from sqlalchemy import text
        status_map = {"review": "GEPRUEFT", "confirm": "BESTAETIGT"}
        if action not in status_map:
            raise ValidationFailedError(f"Unknown action: {action}")
        row = self.db.execute(text(
            "SELECT id, ab_nummer AS bestaetigungs_nummer FROM einkauf_auftragsbestaetigungen "
            "WHERE (id = :bid OR ab_nummer = :bid) AND tenant_id = :tid ORDER BY created_at DESC LIMIT 1"
        ), {"bid": bestaetigung_id, "tid": self.tenant_id}).fetchone()
        if row is None:
            raise EntityNotFoundError("Auftragsbestaetigung", bestaetigung_id)
        new_status = status_map[action]
        self.db.execute(text(
            "UPDATE einkauf_auftragsbestaetigungen SET status = :status, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id AND tenant_id = :tid"
        ), {"status": new_status, "id": row._mapping.get("id"), "tid": self.tenant_id})
        self.db.commit()
        self._invalidate()
        return {"message": f"Auftragsbestaetigung {action}", "status": new_status,
                "id": str(row._mapping.get("id")),
                "bestaetigungsNummer": row._mapping.get("bestaetigungs_nummer") or str(row._mapping.get("id"))}

    # ── Rechnungseingaenge (GoBD) ─────────────────────────────────────────────

    def list_rechnungseingaenge(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, rechnungs_nummer, lieferant_name, bestellung_id, wareneingang_id, "
                "status, brutto_betrag, rechnungs_datum, created_at "
                "FROM einkauf_rechnungseingaenge WHERE tenant_id = :tid ORDER BY created_at DESC LIMIT 500"
            ), {"tid": self.tenant_id}).fetchall()
        except Exception:
            return []
        return [self._rechnung_row_to_dict(r._mapping) for r in rows]

    def _get_rechnung_id_status(self, rechnung_id: str) -> Optional[tuple[str, str]]:
        from sqlalchemy import text
        row = self.db.execute(text(
            "SELECT id, status FROM einkauf_rechnungseingaenge "
            "WHERE (id = :id OR rechnungs_nummer = :id) AND tenant_id = :tid"
        ), {"id": rechnung_id, "tid": self.tenant_id}).mappings().first()
        if not row:
            return None
        return (str(row["id"]), (row.get("status") or "").upper())

    def _write_rechnung_audit(
        self, rid: str, action: str, old_status: str, new_status: str, actor: str
    ) -> None:
        from datetime import datetime as _dt
        from app.core.logging import get_correlation_id
        from sqlalchemy import text
        user_id = bekannter_nutzer(self.db, actor, tenant_id=self.tenant_id)
        row = self.db.execute(text(
            "SELECT email FROM domain_shared.users WHERE id = :id AND tenant_id = :tid"
        ), {"id": user_id, "tid": self.tenant_id}).mappings().one()
        user_email = str((row.get("email") or "unknown")[:100])
        entry = AuditLog(
            id=uuid7(),
            timestamp=_dt.utcnow(),
            user_id=user_id,
            user_email=user_email,
            tenant_id=self.tenant_id,
            action=action,
            entity_type="rechnungseingang",
            entity_id=rid,
            changes={"old": {"status": old_status}, "new": {"status": new_status}},
            ip_address=None,
            user_agent=None,
            correlation_id=get_correlation_id(),
        )
        self.db.add(entry)

    def _transition_rechnung(self, rechnung_id: str, action: str, actor: str | None) -> dict:
        from sqlalchemy import text
        allowed = {
            "pruefen": ({"ENTWURF", "ERFASST", "OFFEN"}, "GEPRUEFT",
                        "Prüfen nur möglich bei Status Entwurf/Erfasst/Offen"),
            "freigeben": ({"GEPRUEFT"}, "FREIGEGEBEN",
                          "Freigeben nur möglich bei Status GEPRUEFT"),
            "verbuchen": ({"FREIGEGEBEN"}, "VERBUCHT",
                          "Verbuchen nur möglich bei Status FREIGEGEBEN"),
        }
        valid_statuses, new_status, err_msg = allowed[action]
        pair = self._get_rechnung_id_status(rechnung_id)
        if not pair:
            raise EntityNotFoundError("Rechnungseingang", rechnung_id)
        rid, old_status = pair
        if old_status not in valid_statuses:
            raise ValidationFailedError(f"{err_msg}. Aktuell: {old_status}")
        try:
            self._write_rechnung_audit(rid, action, old_status, new_status, self.actor if actor is None else actor)
            self.db.execute(text(
                "UPDATE einkauf_rechnungseingaenge SET status = :ns, updated_at = now() WHERE id = :id AND tenant_id = :tid"
            ), {"ns": new_status, "id": rid, "tid": self.tenant_id})
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self._invalidate()

        # Belegbruch schließen: bei Verbuchung Kreditoren-OP anlegen
        if action == "verbuchen":
            try:
                import uuid as _uuid
                rech_row = self.db.execute(text(
                    "SELECT rechnungs_nummer, brutto_betrag, rechnungs_datum FROM einkauf_rechnungseingaenge "
                    "WHERE id = :id AND tenant_id = :tid"
                ), {"id": rid, "tid": self.tenant_id}).fetchone()
                if rech_row and rech_row[1]:
                    business_day = business_today()
                    today = business_day.isoformat()
                    due_in_30 = business_date_after(30, from_date=business_day).isoformat()
                    self.db.execute(text("""
                        INSERT INTO domain_erp.offene_posten
                            (id, tenant_id, konto_typ, rechnungsnr, rechnungsdatum, datum, faelligkeit,
                             betrag, offen, op_status)
                        VALUES (:id, :tid, 'kreditoren', :rnr, :rdat, :dat, :faell, :betrag, :betrag, 'offen')
                        ON CONFLICT DO NOTHING
                    """), {
                        "id": str(_uuid.uuid4()), "tid": self.tenant_id,
                        "rnr": rech_row[0] or rid,
                        "rdat": (rech_row[2].isoformat() if rech_row[2] else today),
                        "dat": today, "faell": due_in_30,
                        "betrag": float(rech_row[1]),
                    })
                    self.db.commit()
            except Exception:  # noqa: BLE001 — OP-Anlage nicht kritisch für Buchungs-Workflow
                pass

        return {"message": f"Rechnungseingang {action}t", "status": new_status}

    def pruefen_rechnung(self, rechnung_id: str, actor: str | None = None) -> dict:
        return self._transition_rechnung(rechnung_id, "pruefen", actor)

    def freigeben_rechnung(self, rechnung_id: str, actor: str | None = None) -> dict:
        return self._transition_rechnung(rechnung_id, "freigeben", actor)

    def verbuchen_rechnung(self, rechnung_id: str, actor: str | None = None) -> dict:
        return self._transition_rechnung(rechnung_id, "verbuchen", actor)

    # ── Supplier Ratings & Reports ────────────────────────────────────────────

    async def get_supplier_ratings(self) -> dict:
        ratings = list_docs(self.db, "supplier_rating", tenant_id=self.tenant_id)
        return {"items": ratings, "total": len(ratings)}

    def upsert_supplier_rating(self, supplier_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        existing = repo.get("supplier_rating", supplier_id)
        doc = {**(existing or {}), **payload,
               "id": supplier_id, "tenantId": self.tenant_id, "updated_at": now_iso()}
        if not existing:
            doc["created_at"] = now_iso()
        repo.save("supplier_rating", supplier_id, doc)
        self._invalidate()
        return doc

    async def get_reports(self) -> dict:
        return {"lieferantenLeistung": [], "bestellvolumen": [], "generated_at": now_iso()}

    async def get_reports_standard(self) -> dict:
        orders = list_docs(self.db, "purchase_order", tenant_id=self.tenant_id)
        total = sum(safe_float(o.get("total_amount")) for o in orders)
        return {"totalOrders": len(orders), "totalAmount": total,
                "currency": "EUR", "generated_at": now_iso()}

    # ── Retouren ──────────────────────────────────────────────────────────────

    def list_retouren(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, retouren_nummer, grund, status, created_at, lieferant_name "
                "FROM einkauf_retouren ORDER BY created_at DESC LIMIT 500"
            )).fetchall()
        except Exception:
            return []
        return [
            {
                "id": str(r._mapping.get("id")),
                "nummer": r._mapping.get("retouren_nummer") or str(r._mapping.get("id")),
                "grund": r._mapping.get("grund") or "",
                "status": r._mapping.get("status") or "offen",
                "datum": r._mapping.get("created_at").isoformat()[:10] if r._mapping.get("created_at") else None,
                "lieferant": r._mapping.get("lieferant_name") or "",
            }
            for r in rows
        ]

    def get_retoure(self, retour_id: str) -> dict:
        for r in self.list_retouren():
            if str(r.get("id")) == retour_id or str(r.get("nummer")) == retour_id:
                return r
        raise EntityNotFoundError("Retoure", retour_id)

    async def create_retoure(self, payload: dict) -> dict:
        from sqlalchemy import text
        from datetime import datetime as _dt
        retour_id = uuid7()
        nummer = payload.get("nummer") or f"RET-{_dt.utcnow().strftime('%Y%m%d%H%M%S')}"
        try:
            self.db.execute(text(
                "INSERT INTO einkauf_retouren (id, retouren_nummer, grund, status, lieferant_name, created_at) "
                "VALUES (:id, :nr, :grund, :status, :lieferant, now())"
            ), {
                "id": retour_id, "nr": nummer,
                "grund": payload.get("returnReason") or payload.get("grund") or "",
                "status": payload.get("status") or "offen",
                "lieferant": payload.get("supplierName") or "",
            })
        except Exception:
            self.db.rollback()
        await enqueue_event(self.db, event_type="procurement.return.created",
                            aggregate_id=str(retour_id),
                            payload={"nummer": nummer,
                                     "returnReason": payload.get("returnReason") or payload.get("grund"),
                                     "goodsReceiptId": payload.get("goodsReceiptId"),
                                     "createdAt": now_iso()},
                            tenant_id=self.tenant_id)
        self._invalidate()
        return {"id": str(retour_id), "nummer": nummer, "message": "Retoure erfasst"}

    def patch_retoure(self, retour_id: str, payload: dict) -> dict:
        from sqlalchemy import text
        try:
            self.db.execute(text(
                "UPDATE einkauf_retouren SET status = :status, grund = COALESCE(:grund, grund), "
                "updated_at = now() WHERE id = :id OR retouren_nummer = :id"
            ), {"id": retour_id, "status": payload.get("status", "offen"), "grund": payload.get("grund")})
            self.db.commit()
        except Exception:
            self.db.rollback()
        self._invalidate()
        return {"id": retour_id, "status": payload.get("status", "offen"), "ok": True}

    # ── Service Entry Sheets ──────────────────────────────────────────────────

    def list_service_entry_sheets(self, status: Optional[str] = None) -> dict:
        all_ses = list_docs(self.db, "service_entry_sheet", tenant_id=self.tenant_id)
        if status:
            all_ses = [s for s in all_ses if s.get("status") == status]
        return {"items": all_ses, "total": len(all_ses)}

    async def create_service_entry_sheet(self, payload: dict) -> dict:
        from datetime import datetime as _dt
        number = payload.get("number") or f"SES-{_dt.utcnow().strftime('%Y%m%d%H%M%S')}"
        qty = safe_float(payload.get("quantity"))
        unit_price = safe_float(payload.get("unitPrice"))
        doc = {
            "id": uuid7(),
            "number": number,
            "supplierId": payload.get("supplierId"),
            "purchaseOrderId": payload.get("purchaseOrderId"),
            "serviceDate": payload.get("serviceDate") or now_iso()[:10],
            "description": payload.get("description") or "",
            "quantity": qty,
            "unitPrice": unit_price,
            "amount": round(qty * unit_price, 2),
            "status": payload.get("status") or "ERFASST",
            "tenantId": self.tenant_id,
            "createdAt": now_iso(),
            **{k: v for k, v in payload.items()
               if k not in ("number", "supplierId", "purchaseOrderId", "serviceDate",
                            "description", "quantity", "unitPrice", "status")},
        }
        repo = doc_repo(self.db)
        repo.save("service_entry_sheet", number, doc)
        await enqueue_event(self.db, event_type="service_entry_sheet.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        self._invalidate()
        return doc

    def _find_ses(self, ses_id: str) -> Optional[dict]:
        all_ses = list_docs(self.db, "service_entry_sheet", tenant_id=self.tenant_id)
        for s in all_ses:
            if str(s.get("id")) == ses_id or str(s.get("number")) == ses_id:
                return s
        return None

    def update_service_entry_sheet(self, ses_id: str, payload: dict) -> dict:
        target = self._find_ses(ses_id)
        if target is None:
            raise EntityNotFoundError("Service Entry Sheet", ses_id)
        target.update({k: v for k, v in payload.items() if v is not None})
        target["updatedAt"] = now_iso()
        repo = doc_repo(self.db)
        repo.save("service_entry_sheet", target["number"], target)
        self._invalidate()
        return target

    # ── EDI ───────────────────────────────────────────────────────────────────

    def list_edi_messages(self) -> dict:
        msgs = list_docs(self.db, "edi_message", tenant_id=self.tenant_id)
        return {"items": msgs, "total": len(msgs)}

    async def create_edi_message(self, payload: dict) -> dict:
        from datetime import datetime as _dt
        msg_id = uuid7()
        number = payload.get("number") or f"EDI-{_dt.utcnow().strftime('%Y%m%d%H%M%S')}"
        doc = {
            "id": msg_id,
            "number": number,
            "direction": payload.get("direction") or "outbound",
            "partner": payload.get("partner") or "",
            "messageType": payload.get("messageType") or "ORDERS",
            "status": payload.get("status") or "QUEUED",
            "payload": payload.get("payload") or {},
            "tenantId": self.tenant_id,
            "createdAt": now_iso(),
        }
        repo = doc_repo(self.db)
        repo.save("edi_message", number, doc)
        await enqueue_event(self.db, event_type="procurement.edi.message.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        self._invalidate()
        return doc

    async def ack_edi_message(self, msg_id: str) -> dict:
        all_msgs = list_docs(self.db, "edi_message", tenant_id=self.tenant_id)
        target = next((m for m in all_msgs
                       if str(m.get("id")) == msg_id or str(m.get("number")) == msg_id), None)
        if target is None:
            raise EntityNotFoundError("EDI message", msg_id)
        target["status"] = "ACKNOWLEDGED"
        target["ackAt"] = now_iso()
        repo = doc_repo(self.db)
        repo.save("edi_message", target["number"], target)
        await enqueue_event(self.db, event_type="procurement.edi.message.ack",
                            aggregate_id=target["id"], payload=target, tenant_id=self.tenant_id)
        self._invalidate()
        return target

    # ── Audit Trail & Supplier Documents ─────────────────────────────────────

    def get_audit_trail(self, doc_type: str, doc_id: str) -> dict:
        from sqlalchemy import text
        rows = self.db.execute(
            text("SELECT * FROM audit_logs WHERE entity_type = :et AND entity_id = :eid "
                 "AND tenant_id = :tid ORDER BY created_at DESC"),
            {"et": doc_type, "eid": doc_id, "tid": self.tenant_id},
        ).fetchall()
        return {"items": [dict(r._mapping) for r in rows]}

    def list_supplier_documents(self, supplier_id: str) -> list:
        all_docs = list_docs(self.db, "supplier_document", tenant_id=self.tenant_id)
        return [d for d in all_docs if d.get("supplier_id") == supplier_id]

    def create_supplier_document(self, supplier_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "supplier_id": supplier_id, "tenantId": self.tenant_id,
               "created_at": now_iso(), **payload}
        repo.save("supplier_document", doc["id"], doc)
        return doc

    def delete_supplier_document(self, supplier_id: str, doc_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("supplier_document", doc_id)
        if doc is None or doc.get("supplier_id") != supplier_id:
            raise EntityNotFoundError("Document", doc_id)
        repo.delete("supplier_document", doc_id)
        return {"deleted": True, "id": doc_id}
