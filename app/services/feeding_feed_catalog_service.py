"""Application service for the canonical, versioned feeding feed catalog."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.feed_catalog import (
    FeedApprovalStatus,
    FeedKind,
    build_solver_feed,
    validate_feed,
)
from app.agrar.rations.master_audit import record_master_data_audit
from app.core.uuid7 import uuid7


class FeedCatalogNotFound(LookupError):
    pass


class FeedCatalogConflict(ValueError):
    pass


class FeedingFeedCatalogService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    def _head(self, feed_id: str, *, lock: bool = False) -> dict[str, Any]:
        suffix = " FOR UPDATE" if lock else ""
        row = self.db.execute(text("""
          SELECT * FROM domain_shared.futtermittel_einzelfutter
          WHERE tenant_id=:tenant_id AND id=:feed_id
        """ + suffix), {"tenant_id": self.tenant_id, "feed_id": feed_id}).mappings().first()
        if not row:
            raise FeedCatalogNotFound("Futtermittel nicht gefunden.")
        return dict(row)

    def list_feeds(self, *, search: str | None = None, include_inactive: bool = False) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT id,tenant_id,artikel_nummer,name,art,feed_kind,species_scope,
                 approval_status,valid_from,valid_until,revision,trockensubstanz,
                 preis_pro_t,aktiv,updated_at
          FROM domain_shared.futtermittel_einzelfutter
          WHERE tenant_id=:tenant_id AND (:include_inactive OR aktiv=TRUE)
            AND (:search IS NULL OR name ILIKE '%' || :search || '%'
                 OR artikel_nummer ILIKE '%' || :search || '%')
          ORDER BY name
        """), {"tenant_id": self.tenant_id, "search": search, "include_inactive": include_inactive}).mappings().all()
        return [dict(row) for row in rows]

    def list_reference_values(self, feed_id: str) -> list[dict[str, Any]]:
        self._head(feed_id)
        rows = self.db.execute(text("""
          SELECT v.*,n.display_name AS nutrient_name
          FROM domain_agrar.feeding_feed_reference_values v
          LEFT JOIN LATERAL (
            SELECT display_name FROM domain_agrar.feeding_nutrient_definitions nd
            WHERE nd.code=v.nutrient_code AND (nd.tenant_id IS NULL OR nd.tenant_id=v.tenant_id)
            ORDER BY (nd.tenant_id IS NOT NULL) DESC,nd.revision DESC LIMIT 1
          ) n ON TRUE
          WHERE v.tenant_id=:tenant_id AND v.feed_id=:feed_id
          ORDER BY v.nutrient_code,v.valid_from DESC,v.priority DESC,v.created_at DESC
        """), {"tenant_id": self.tenant_id, "feed_id": feed_id}).mappings().all()
        return [dict(row) for row in rows]

    def list_products(self, feed_id: str) -> list[dict[str, Any]]:
        self._head(feed_id)
        rows = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_feed_products
          WHERE tenant_id=:tenant_id AND feed_id=:feed_id
          ORDER BY active DESC,valid_from DESC,display_name
        """), {"tenant_id": self.tenant_id, "feed_id": feed_id}).mappings().all()
        return [dict(row) for row in rows]

    def get_feed(self, feed_id: str) -> dict[str, Any]:
        head = self._head(feed_id)
        values = self.list_reference_values(feed_id)
        products = self.list_products(feed_id)
        current_values: dict[str, dict[str, Any]] = {}
        today = date.today()
        for value in values:
            if value["valid_from"] <= today and (value["valid_until"] is None or value["valid_until"] >= today):
                current_values.setdefault(value["nutrient_code"], value)
        preferred_product = next((product for product in products if product["active"]
                                  and product["valid_from"] <= today
                                  and (product["valid_until"] is None or product["valid_until"] >= today)), None)
        solver_head = dict(head)
        if preferred_product and preferred_product.get("price_eur_t") is not None:
            solver_head["price_eur_t"] = (
                preferred_product["price_eur_t"] + (preferred_product.get("freight_eur_t") or Decimal("0"))
            )
        head["reference_values"] = values
        head["products"] = products
        head["solver_feed"] = build_solver_feed(solver_head, current_values.values())
        return head

    def create_feed(self, payload: dict[str, Any]) -> dict[str, Any]:
        values = validate_feed(
            FeedKind(payload.get("feed_kind", "other")),
            FeedApprovalStatus(payload.get("approval_status", "draft")),
            payload.get("valid_from"), payload.get("valid_until"), payload.get("trockensubstanz"),
        )
        feed_id = str(payload.get("id") or uuid7())
        try:
            self.db.execute(text("""
              INSERT INTO domain_shared.futtermittel_einzelfutter
                (id,tenant_id,artikel_nummer,name,art,herkunft,lieferant,protein,energie,
                 faser,fett,asche,trockensubstanz,gvo_status,qs_milch,gmp_plus,bio_zertifiziert,
                 verfuegbar_t,einheit,min_bestand_t,preis_pro_t,aktiv,feed_kind,species_scope,
                 conservation_method,approval_status,valid_from,valid_until,revision,created_by,updated_by)
              VALUES
                (:id,:tenant_id,:artikel_nummer,:name,:art,:herkunft,:lieferant,:protein,:energie,
                 :faser,:fett,:asche,:trockensubstanz,:gvo_status,:qs_milch,:gmp_plus,:bio_zertifiziert,
                 :verfuegbar_t,:einheit,:min_bestand_t,:preis_pro_t,:aktiv,:feed_kind,:species_scope,
                 :conservation_method,:approval_status,:valid_from,:valid_until,1,:actor,:actor)
            """), {
                **{key: payload.get(key) for key in (
                    "artikel_nummer","name","art","herkunft","lieferant","protein","energie","faser",
                    "fett","asche","trockensubstanz","gvo_status","species_scope","conservation_method",
                    "valid_until","min_bestand_t","preis_pro_t",
                )},
                "id": feed_id, "tenant_id": self.tenant_id, "actor": self.actor,
                "qs_milch": bool(payload.get("qs_milch", False)), "gmp_plus": bool(payload.get("gmp_plus", False)),
                "bio_zertifiziert": bool(payload.get("bio_zertifiziert", False)),
                "verfuegbar_t": payload.get("verfuegbar_t", 0), "einheit": payload.get("einheit", "t"),
                "aktiv": bool(payload.get("aktiv", True)), "feed_kind": values["feed_kind"],
                "approval_status": values["approval_status"], "valid_from": values["valid_from"] or date.today(),
            })
            self._append_revision(feed_id, 1, "Anlage")
            record_master_data_audit(
                self.db, tenant_id=self.tenant_id, actor=self.actor,
                entity_type="feed", entity_id=feed_id, event_type="created",
                delta={"name": payload.get("name"),
                       "artikel_nummer": payload.get("artikel_nummer"),
                       "feed_kind": values["feed_kind"],
                       "approval_status": values["approval_status"]})
            self.db.commit()
            return self.get_feed(feed_id)
        except Exception:
            self.db.rollback()
            raise

    def update_feed(self, feed_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        head = self._head(feed_id, lock=True)
        expected = int(payload.pop("expected_revision"))
        reason = str(payload.pop("reason"))
        if int(head["revision"]) != expected:
            raise FeedCatalogConflict(f"Versionskonflikt: erwartet {expected}, aktuell {head['revision']}.")
        merged = {**head, **{key: value for key, value in payload.items() if value is not None}}
        validate_feed(FeedKind(merged["feed_kind"]), FeedApprovalStatus(merged["approval_status"]),
                      merged.get("valid_from"), merged.get("valid_until"), merged.get("trockensubstanz"))
        allowed = {"artikel_nummer","name","art","herkunft","lieferant","protein","energie","faser",
                   "fett","asche","trockensubstanz","gvo_status","qs_milch","gmp_plus","bio_zertifiziert",
                   "verfuegbar_t","einheit","min_bestand_t","preis_pro_t","feed_kind","species_scope",
                   "conservation_method","approval_status","valid_from","valid_until","aktiv"}
        changes = {key: value for key, value in payload.items() if key in allowed}
        if changes:
            assignments = ",".join(f"{key}=:{key}" for key in changes)
            self.db.execute(text(f"""UPDATE domain_shared.futtermittel_einzelfutter
              SET {assignments},revision=revision+1,updated_by=:actor,updated_at=now()
              WHERE tenant_id=:tenant_id AND id=:feed_id"""),  # nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)  # noqa: S608
              {**changes, "actor": self.actor, "tenant_id": self.tenant_id, "feed_id": feed_id})
        revision = expected + 1
        self._append_revision(feed_id, revision, reason)
        record_master_data_audit(
            self.db, tenant_id=self.tenant_id, actor=self.actor,
            entity_type="feed", entity_id=feed_id, event_type="updated",
            delta={"name": merged.get("name"), "revision": revision,
                   "changed_fields": sorted(changes)}, reason=reason)
        self.db.commit()
        return self.get_feed(feed_id)

    def _append_revision(self, feed_id: str, revision: int, reason: str) -> None:
        self.db.execute(text("""INSERT INTO domain_agrar.feeding_feed_revisions
          (id,tenant_id,feed_id,revision,snapshot,reason,changed_by)
          SELECT :id,:tenant_id,id,:revision,to_jsonb(f),:reason,:actor
          FROM domain_shared.futtermittel_einzelfutter f
          WHERE tenant_id=:tenant_id AND id=:feed_id
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id, "feed_id": feed_id,
                 "revision": revision, "reason": reason, "actor": self.actor})

    def history(self, feed_id: str) -> list[dict[str, Any]]:
        self._head(feed_id)
        rows = self.db.execute(text("""SELECT id,feed_id,revision,snapshot,reason,changed_by,changed_at
          FROM domain_agrar.feeding_feed_revisions
          WHERE tenant_id=:tenant_id AND feed_id=:feed_id ORDER BY revision DESC"""),
          {"tenant_id": self.tenant_id, "feed_id": feed_id}).mappings().all()
        return [dict(row) for row in rows]

    def add_reference_value(self, feed_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._head(feed_id)
        if payload.get("valid_until") and payload["valid_until"] < payload["valid_from"]:
            raise FeedCatalogConflict("Gueltigkeitsende darf nicht vor dem Beginn liegen.")
        definition = self.db.execute(text("""SELECT minimum_value,maximum_value,canonical_unit_code
          FROM domain_agrar.feeding_nutrient_definitions
          WHERE code=:code AND active=TRUE AND (tenant_id IS NULL OR tenant_id=:tenant_id)
          ORDER BY (tenant_id IS NOT NULL) DESC,revision DESC LIMIT 1"""),
          {"code": payload["nutrient_code"], "tenant_id": self.tenant_id}).mappings().first()
        if not definition:
            raise FeedCatalogConflict("Unbekannte Naehrstoffdefinition.")
        if payload["unit_code"] != definition["canonical_unit_code"]:
            raise FeedCatalogConflict(
                f"Einheit muss der kanonischen Einheit {definition['canonical_unit_code']} entsprechen."
            )
        value = Decimal(str(payload["value"]))
        if definition["minimum_value"] is not None and value < definition["minimum_value"]:
            raise FeedCatalogConflict("Naehrstoffwert unterschreitet den definierten Mindestwert.")
        if definition["maximum_value"] is not None and value > definition["maximum_value"]:
            raise FeedCatalogConflict("Naehrstoffwert ueberschreitet den definierten Hoechstwert.")
        value_id = str(payload.get("id") or uuid7())
        row = self.db.execute(text("""INSERT INTO domain_agrar.feeding_feed_reference_values
          (id,tenant_id,feed_id,nutrient_code,value,unit_code,basis,value_status,source_type,
           source_ref,valid_from,valid_until,priority,created_by)
          VALUES (:id,:tenant_id,:feed_id,:nutrient_code,:value,:unit_code,:basis,:value_status,:source_type,
                  :source_ref,:valid_from,:valid_until,:priority,:actor)
          RETURNING *"""), {**payload, "id": value_id, "tenant_id": self.tenant_id, "feed_id": feed_id,
                             "actor": self.actor}).mappings().one()
        record_master_data_audit(
            self.db, tenant_id=self.tenant_id, actor=self.actor,
            entity_type="analysis", entity_id=feed_id, event_type="reference_value_added",
            delta={"nutrient_code": payload["nutrient_code"],
                   "value": str(payload["value"]), "unit_code": payload["unit_code"],
                   "source_type": payload.get("source_type"),
                   "source_ref": payload.get("source_ref")})
        self.db.commit()
        return dict(row)

    def add_product(self, feed_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._head(feed_id)
        if payload.get("valid_until") and payload["valid_until"] < payload["valid_from"]:
            raise FeedCatalogConflict("Gueltigkeitsende darf nicht vor dem Beginn liegen.")
        product_id = str(payload.get("id") or uuid7())
        row = self.db.execute(text("""INSERT INTO domain_agrar.feeding_feed_products
          (id,tenant_id,feed_id,supplier_partner_id,sku,display_name,packaging_unit,package_size,
           minimum_order_qty,price_eur_t,freight_eur_t,valid_from,valid_until,active,created_by,updated_by)
          VALUES (:id,:tenant_id,:feed_id,:supplier_partner_id,:sku,:display_name,:packaging_unit,:package_size,
                  :minimum_order_qty,:price_eur_t,:freight_eur_t,:valid_from,:valid_until,:active,:actor,:actor)
          ON CONFLICT (tenant_id,feed_id,sku) DO UPDATE SET
            display_name=EXCLUDED.display_name,price_eur_t=EXCLUDED.price_eur_t,freight_eur_t=EXCLUDED.freight_eur_t,
            valid_from=EXCLUDED.valid_from,valid_until=EXCLUDED.valid_until,
            revision=feeding_feed_products.revision+1,updated_by=:actor,updated_at=now()
          RETURNING *"""), {**payload, "id": product_id, "tenant_id": self.tenant_id, "feed_id": feed_id,
                             "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)
