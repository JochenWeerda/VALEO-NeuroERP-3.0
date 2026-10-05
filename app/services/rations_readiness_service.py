"""Read model over existing feed inventory, lab and supplier-price sources."""
from __future__ import annotations
from datetime import date
from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.agrar.rations.readiness import evaluate_material, summarize
from app.services.feeding_plan_service import FeedingPlanService

class RationsReadinessService:
    def __init__(self, db: Session, tenant_id: str):
        self.db, self.tenant_id = db, tenant_id

    def _catalog(self) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT ef.id,ef.artikel_nummer,ef.inventory_article_id,ef.name,ef.art,
                 (ef.verfuegbar_t * 1000)::float AS stock_kg,
                 COALESCE(ps.purchase_price,ef.preis_pro_t)::float AS price_eur_t,
                 ps.price_valid_from,ps.price_valid_to,
                 COALESCE(ps.updated_at,ef.updated_at,ef.created_at) AS price_updated_at,
                 ga.id AS analysis_id,ga.analyse_datum AS analysis_date
          FROM domain_shared.futtermittel_einzelfutter ef
          LEFT JOIN LATERAL (
            SELECT s.purchase_price,s.price_valid_from,s.price_valid_to,s.updated_at
            FROM domain_inventory.article_suppliers s WHERE s.article_id=ef.inventory_article_id
            ORDER BY s.is_preferred DESC,s.updated_at DESC NULLS LAST,s.created_at DESC LIMIT 1
          ) ps ON TRUE
          LEFT JOIN LATERAL (
            SELECT g.id,g.analyse_datum FROM domain_shared.grundfutter_analysen g
            WHERE g.tenant_id=ef.tenant_id AND g.verifiziert=TRUE
              AND (lower(g.probenart)=lower(ef.name) OR lower(g.bezeichnung)=lower(ef.name))
            ORDER BY g.analyse_datum DESC NULLS LAST,g.created_at DESC LIMIT 1
          ) ga ON TRUE
          WHERE ef.tenant_id=:tenant_id AND ef.aktiv=TRUE ORDER BY ef.name
        """), {"tenant_id": self.tenant_id}).mappings().all()
        return [dict(row) for row in rows]

    @staticmethod
    def _components(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        mobile = snapshot.get("mobile") if isinstance(snapshot, dict) else None
        items = mobile.get("components") if isinstance(mobile, dict) else None
        return [item for item in (items or []) if isinstance(item, dict)]

    def evaluate(self, snapshot: dict[str, Any], *, as_of: date | None = None) -> dict[str, Any]:
        day, catalog, rows = as_of or date.today(), self._catalog(), []
        for component in self._components(snapshot):
            feed_id, name = str(component.get("feed_id") or ""), str(component.get("name") or "Unbekannt")
            match = next((item for item in catalog if feed_id in {str(item["id"]), str(item["artikel_nummer"]), str(item["inventory_article_id"] or "")}), None)
            if match is None:
                match = next((item for item in catalog if item["name"].casefold() == name.casefold()), None)
            forage = any(token in f"{match.get('art', '') if match else ''} {name}".casefold() for token in ("silage", "heu", "gras", "mais", "grundfutter"))
            rows.append(evaluate_material(feed_id=feed_id or None, name=name,
                daily_kg=float(component.get("soll_kg") or 0), stock_kg=match.get("stock_kg") if match else None,
                forage=forage, analysis_id=match.get("analysis_id") if match else None,
                analysis_date=match.get("analysis_date") if match else None,
                selected_analysis_id=component.get("analysis_id"),
                price_eur_t=match.get("price_eur_t") if match else component.get("price_eur_t"),
                price_valid_from=match.get("price_valid_from") if match else None,
                price_valid_to=match.get("price_valid_to") if match else None,
                price_updated_at=match.get("price_updated_at") if match else None, as_of=day))
        return summarize(rows, day)

    def active_materials(self, *, subject: str = "", unrestricted: bool = False,
                         as_of: date | None = None) -> list[dict[str, Any]]:
        """Evaluate immutable current plan instructions, never editor/mobile snapshots."""
        plans = FeedingPlanService(self.db, self.tenant_id, subject or "unknown").list_current(
            subject=subject, unrestricted=unrestricted,
        )
        components = [
            {
                "feed_id": instruction["feed_id"],
                "name": instruction.get("feed_name") or instruction["feed_id"],
                "soll_kg": instruction.get("target_batch_kg") or 0,
            }
            for plan in plans
            for instruction in plan["instructions"]
        ]
        return self.evaluate({"mobile": {"components": components}}, as_of=as_of)["materials"]
