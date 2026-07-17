"""Bidirektionaler Kundenrezeptur-Kreislauf (FEED-RECIPE-052).

Hinweg: Der Kunde buendelt ausgewaehlte Zeilen (Mehle/Schrote/Mineral) seiner
Ration zu einer Bestellrezeptur mit eigener Artikelnummer; Versionen sind
append-only, Freigabe markiert die Optimal-Rezeptur.

Bestellung: fixiert IMMER die juengste freigegebene Version am Auftrag
(recipe_version_id) — dadurch kann kein Drift entstehen.

Rueckweg: Die tatsaechliche Mischung (Mahl-/Mischwagen) laeuft mit ihren
Mengenabweichungen als Nachkalkulation gegen die FIXIERTE Version zurueck; die
naechste Bestellung geht wieder von der Optimal-Rezeptur aus, nie vom Ist.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


class RecipeNotFound(LookupError):
    pass


class RecipeConflict(RuntimeError):
    pass


class RecipeValidationError(ValueError):
    pass


def _round(value: float, digits: int = 3) -> float:
    return round(float(value), digits)


class FeedingRecipeService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    # ── Rezeptur + Versionen (Hinweg) ───────────────────────────────────────

    def _components_payload(self, components: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not components:
            raise RecipeValidationError("Eine Rezeptur braucht mindestens eine Komponente.")
        cleaned: list[dict[str, Any]] = []
        seen: set[str] = set()
        for component in components:
            name = str(component.get("name") or "").strip()
            if not name:
                raise RecipeValidationError("Jede Komponente braucht einen Namen.")
            if name in seen:
                raise RecipeValidationError(f"Komponente '{name}' ist doppelt in der Rezeptur.")
            seen.add(name)
            kg_per_t = float(component.get("kg_per_t") or 0)
            if kg_per_t <= 0:
                raise RecipeValidationError(f"Komponente '{name}' braucht kg_per_t > 0.")
            cleaned.append({"name": name, "kg_per_t": _round(kg_per_t),
                            "feed_id": component.get("feed_id")})
        return cleaned

    def create_recipe(self, payload: dict[str, Any]) -> dict[str, Any]:
        components = self._components_payload(payload["components"])
        recipe_id = str(uuid7())
        exists = self.db.execute(text("""
          SELECT 1 FROM domain_agrar.feeding_customer_recipes
          WHERE tenant_id=:tenant_id AND customer_ref=:customer_ref AND artikel_nr=:artikel_nr
        """), {"tenant_id": self.tenant_id, "customer_ref": payload["customer_ref"],
               "artikel_nr": payload["artikel_nr"]}).first()
        if exists:
            raise RecipeConflict(
                f"Kunden-Artikelnummer {payload['artikel_nr']} ist fuer diesen Kunden "
                "bereits vergeben.")
        self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_customer_recipes
            (id,tenant_id,customer_ref,artikel_nr,name,source_ration_ref,created_by)
          VALUES (:id,:tenant_id,:customer_ref,:artikel_nr,:name,:source_ration_ref,:actor)
        """), {"id": recipe_id, "tenant_id": self.tenant_id,
               "customer_ref": payload["customer_ref"], "artikel_nr": payload["artikel_nr"],
               "name": payload["name"], "source_ration_ref": payload.get("source_ration_ref"),
               "actor": self.actor})
        self._insert_version(recipe_id, 1, components)
        self.db.commit()
        return self.get_recipe(recipe_id)

    def _insert_version(self, recipe_id: str, version_no: int,
                        components: list[dict[str, Any]]) -> str:
        version_id = str(uuid7())
        self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_recipe_versions
            (id,tenant_id,recipe_id,version_no,components,created_by)
          VALUES (:id,:tenant_id,:recipe_id,:version_no,CAST(:components AS jsonb),:actor)
        """), {"id": version_id, "tenant_id": self.tenant_id, "recipe_id": recipe_id,
               "version_no": version_no,
               "components": json.dumps(components, ensure_ascii=False), "actor": self.actor})
        return version_id

    def add_version(self, recipe_id: str, *, expected_latest_version_no: int,
                    components: list[dict[str, Any]]) -> dict[str, Any]:
        self._recipe_row(recipe_id)
        cleaned = self._components_payload(components)
        latest = int(self.db.execute(text("""
          SELECT COALESCE(MAX(version_no),0) FROM domain_agrar.feeding_recipe_versions
          WHERE tenant_id=:tenant_id AND recipe_id=:recipe_id
        """), {"tenant_id": self.tenant_id, "recipe_id": recipe_id}).scalar_one())
        if latest != expected_latest_version_no:
            raise RecipeConflict(
                f"Rezeptur wurde zwischenzeitlich geaendert (erwartet v{expected_latest_version_no}, "
                f"aktuell v{latest}).")
        self._insert_version(recipe_id, latest + 1, cleaned)
        self.db.commit()
        return self.get_recipe(recipe_id)

    def approve(self, recipe_id: str, version_no: int) -> dict[str, Any]:
        self._recipe_row(recipe_id)
        version = self.db.execute(text("""
          SELECT id FROM domain_agrar.feeding_recipe_versions
          WHERE tenant_id=:tenant_id AND recipe_id=:recipe_id AND version_no=:version_no
        """), {"tenant_id": self.tenant_id, "recipe_id": recipe_id,
               "version_no": version_no}).first()
        if not version:
            raise RecipeNotFound(f"Rezepturversion {version_no} nicht gefunden.")
        self.db.execute(text("""
          UPDATE domain_agrar.feeding_customer_recipes
          SET approved_version_id=:version_id, updated_at=now()
          WHERE tenant_id=:tenant_id AND id=:recipe_id
        """), {"version_id": version[0], "tenant_id": self.tenant_id, "recipe_id": recipe_id})
        self.db.commit()
        return self.get_recipe(recipe_id)

    def _recipe_row(self, recipe_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_customer_recipes
          WHERE tenant_id=:tenant_id AND id=:recipe_id
        """), {"tenant_id": self.tenant_id, "recipe_id": recipe_id}).mappings().first()
        if not row:
            raise RecipeNotFound("Rezeptur nicht gefunden.")
        return dict(row)

    def _version_map(self, recipe_id: str) -> dict[int, dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT id, version_no, components FROM domain_agrar.feeding_recipe_versions
          WHERE tenant_id=:tenant_id AND recipe_id=:recipe_id ORDER BY version_no
        """), {"tenant_id": self.tenant_id, "recipe_id": recipe_id}).mappings().all()
        return {int(r["version_no"]): dict(r) for r in rows}

    def get_recipe(self, recipe_id: str) -> dict[str, Any]:
        recipe = self._recipe_row(recipe_id)
        versions = self._version_map(recipe_id)
        latest_no = max(versions) if versions else 0
        approved_no = next((no for no, v in versions.items()
                            if v["id"] == recipe.get("approved_version_id")), None)
        return {
            "id": recipe["id"], "customer_ref": recipe["customer_ref"],
            "artikel_nr": recipe["artikel_nr"], "name": recipe["name"],
            "source_ration_ref": recipe["source_ration_ref"],
            "latest_version_no": latest_no,
            "approved_version_no": approved_no,
            "latest_components": versions[latest_no]["components"] if latest_no else [],
        }

    def list_recipes(self, *, customer_ref: str | None = None) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT id FROM domain_agrar.feeding_customer_recipes
          WHERE tenant_id=:tenant_id AND (:customer_ref IS NULL OR customer_ref=:customer_ref)
          ORDER BY name
        """), {"tenant_id": self.tenant_id, "customer_ref": customer_ref}).mappings().all()
        return [self.get_recipe(row["id"]) for row in rows]

    # ── Bestellung (fixiert die Optimal-Version — Drift-Schutz) ──────────────

    def create_order(self, recipe_id: str, *, menge_t: float,
                     idempotency_key: str) -> dict[str, Any]:
        recipe = self._recipe_row(recipe_id)
        existing = self.db.execute(text("""
          SELECT id FROM domain_agrar.feeding_recipe_orders
          WHERE tenant_id=:tenant_id AND idempotency_key=:key
        """), {"tenant_id": self.tenant_id, "key": idempotency_key}).first()
        if existing:
            return self.get_order(existing[0])

        approved_version_id = recipe.get("approved_version_id")
        if not approved_version_id:
            raise RecipeConflict(
                "Diese Rezeptur ist noch nicht freigegeben. Erst eine Optimal-Version "
                "freigeben, dann bestellen.")
        version = self.db.execute(text("""
          SELECT version_no, components FROM domain_agrar.feeding_recipe_versions
          WHERE tenant_id=:tenant_id AND id=:version_id
        """), {"tenant_id": self.tenant_id, "version_id": approved_version_id}).mappings().one()
        # Soll = kg_per_t x Menge (t); immer aus der freigegebenen Version, nie aus Ist.
        soll = [{"name": c["name"], "feed_id": c.get("feed_id"),
                 "soll_kg": _round(float(c["kg_per_t"]) * float(menge_t))}
                for c in version["components"]]
        order_id = str(uuid7())
        self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_recipe_orders
            (id,tenant_id,recipe_id,recipe_version_id,menge_t,soll_components,idempotency_key,created_by)
          VALUES (:id,:tenant_id,:recipe_id,:version_id,:menge_t,CAST(:soll AS jsonb),:key,:actor)
        """), {"id": order_id, "tenant_id": self.tenant_id, "recipe_id": recipe_id,
               "version_id": approved_version_id, "menge_t": menge_t,
               "soll": json.dumps(soll, ensure_ascii=False),
               "key": idempotency_key, "actor": self.actor})
        self.db.commit()
        return self.get_order(order_id)

    def get_order(self, order_id: str) -> dict[str, Any]:
        order = self.db.execute(text("""
          SELECT o.*, v.version_no AS recipe_version_no
          FROM domain_agrar.feeding_recipe_orders o
          JOIN domain_agrar.feeding_recipe_versions v
            ON v.id=o.recipe_version_id AND v.tenant_id=o.tenant_id
          WHERE o.tenant_id=:tenant_id AND o.id=:order_id
        """), {"tenant_id": self.tenant_id, "order_id": order_id}).mappings().first()
        if not order:
            raise RecipeNotFound("Bestellung nicht gefunden.")
        delivery = self.db.execute(text("""
          SELECT source, nachkalkulation, created_at FROM domain_agrar.feeding_recipe_deliveries
          WHERE tenant_id=:tenant_id AND order_id=:order_id
        """), {"tenant_id": self.tenant_id, "order_id": order_id}).mappings().first()
        return {
            "id": order["id"], "recipe_id": order["recipe_id"],
            "recipe_version_id": order["recipe_version_id"],
            "recipe_version_no": int(order["recipe_version_no"]),
            "menge_t": _round(float(order["menge_t"])),
            "soll_components": order["soll_components"],
            "delivery": dict(delivery) if delivery else None,
        }

    # ── Ruecklauf (Ist-Mischung + Nachkalkulation gegen fixierte Version) ────

    def record_delivery(self, order_id: str, *, source: str, idempotency_key: str,
                        components: list[dict[str, Any]]) -> dict[str, Any]:
        order = self.get_order(order_id)
        existing = self.db.execute(text("""
          SELECT order_id FROM domain_agrar.feeding_recipe_deliveries
          WHERE tenant_id=:tenant_id AND idempotency_key=:key
        """), {"tenant_id": self.tenant_id, "key": idempotency_key}).first()
        if existing:
            return self.get_order(existing[0])

        soll_by_name = {c["name"]: float(c["soll_kg"]) for c in order["soll_components"]}
        nachkalkulation: list[dict[str, Any]] = []
        for component in components:
            name = str(component.get("name") or "").strip()
            if name not in soll_by_name:
                raise RecipeValidationError(
                    f"Komponente '{name}' ist nicht Teil der bestellten Rezeptur — "
                    "Ist-Mischung kann nicht zugeordnet werden.")
            ist_kg = float(component.get("ist_kg") or 0)
            soll_kg = soll_by_name[name]
            delta_kg = _round(ist_kg - soll_kg)
            delta_pct = _round((delta_kg / soll_kg) * 100.0) if soll_kg > 0 else None
            nachkalkulation.append({
                "name": name, "soll_kg": _round(soll_kg), "ist_kg": _round(ist_kg),
                "delta_kg": delta_kg, "delta_pct": delta_pct,
            })
        self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_recipe_deliveries
            (id,tenant_id,order_id,source,nachkalkulation,idempotency_key,created_by)
          VALUES (:id,:tenant_id,:order_id,:source,CAST(:calc AS jsonb),:key,:actor)
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id, "order_id": order_id,
               "source": source, "calc": json.dumps(nachkalkulation, ensure_ascii=False),
               "key": idempotency_key, "actor": self.actor})
        self.db.commit()
        result = self.get_order(order_id)
        result["nachkalkulation"] = nachkalkulation
        return result
