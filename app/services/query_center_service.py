"""Safe query center over explicitly approved reporting read models."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.read_model_persistence import ReadModelSnapshotStore
from app.core.reporting_layer import (
    ReportDefinition,
    build_default_data_products,
    run_report,
)
from app.core.uuid7 import uuid7


READ_MODEL_ALLOWLIST: dict[str, dict[str, frozenset[str]]] = {
    "finance-ap-invoice-cockpit": {
        "fields": frozenset(
            {
                "invoice_id",
                "invoice_number",
                "vendor_id",
                "vendor_name",
                "status",
                "due_date",
                "gross_amount",
                "currency",
                "blocked",
            }
        ),
        "sum_fields": frozenset({"gross_amount"}),
    },
    "finance-payment-run-cockpit": {
        "fields": frozenset(
            {
                "run_id",
                "run_number",
                "status",
                "execution_date",
                "total_amount",
                "currency",
                "payment_count",
            }
        ),
        "sum_fields": frozenset({"total_amount", "payment_count"}),
    },
    "finance-process-observation": {
        "fields": frozenset(
            {
                "process_id",
                "process_type",
                "status",
                "started_at",
                "completed_at",
                "duration_seconds",
                "exception_count",
            }
        ),
        "sum_fields": frozenset({"duration_seconds", "exception_count"}),
    },
}


class QueryCenterError(ValueError):
    pass


class QueryCenterService:
    def __init__(
        self, db: Session, tenant_id: str, *, signing_key: str | None = None
    ) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.signing_key = signing_key

    def catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "id": product_id,
                "fields": sorted(spec["fields"]),
                "aggregations": [
                    "count",
                    *[f"sum:{field}" for field in sorted(spec["sum_fields"])],
                ],
            }
            for product_id, spec in READ_MODEL_ALLOWLIST.items()
        ]

    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        product_id = str(payload.get("data_product_id") or "")
        spec = READ_MODEL_ALLOWLIST.get(product_id)
        if spec is None:
            raise QueryCenterError(
                "Datenprodukt ist nicht fuer Anwenderabfragen freigegeben"
            )
        fields = list(payload.get("selected_fields") or [])
        if not fields or len(fields) > 30 or not set(fields).issubset(spec["fields"]):
            raise QueryCenterError("Feldliste enthaelt nicht freigegebene Felder")
        filters = dict(payload.get("filter_spec") or {})
        if len(filters) > 12 or not set(filters).issubset(spec["fields"]):
            raise QueryCenterError("Filter enthaelt nicht freigegebene Felder")
        aggregations = list(payload.get("aggregations") or [])
        allowed_aggregations = {
            "count",
            *[f"sum:{field}" for field in spec["sum_fields"]],
        }
        if len(aggregations) > 10 or not set(aggregations).issubset(
            allowed_aggregations
        ):
            raise QueryCenterError("Aggregation ist nicht freigegeben")
        return {
            "name": str(payload.get("name") or "Unbenannte Abfrage")[:160],
            "data_product_id": product_id,
            "selected_fields": fields,
            "filter_spec": filters,
            "aggregations": aggregations,
            "is_favorite": bool(payload.get("is_favorite", False)),
        }

    def preview(self, payload: dict[str, Any], *, limit: int = 100) -> dict[str, Any]:
        definition = self.validate(payload)
        limit = min(max(limit, 1), 200)
        store = ReadModelSnapshotStore(db_session=self.db)
        product = build_default_data_products(store, self.tenant_id).get(
            definition["data_product_id"], self.tenant_id
        )
        if product is None:
            raise QueryCenterError("Freigegebenes Datenprodukt ist nicht verfuegbar")
        result = run_report(
            ReportDefinition(
                report_id="query-center-preview",
                titel=definition["name"],
                datenprodukt_id=definition["data_product_id"],
                filter_spec=definition["filter_spec"],
                aggregationen=definition["aggregations"],
            ),
            product,
            store,
        )
        rows = result.rows[:limit]
        if not definition["aggregations"]:
            rows = [
                {field: row.get(field) for field in definition["selected_fields"]}
                for row in rows
            ]
        return {
            "items": rows,
            "total": result.total_rows,
            "limit": limit,
            "truncated": result.total_rows > limit,
        }

    def save(
        self, payload: dict[str, Any], *, actor: str, reason: str
    ) -> dict[str, Any]:
        definition = self.validate(payload)
        definition_id = str(payload.get("id") or uuid7())
        params = {
            "id": definition_id,
            "tid": self.tenant_id,
            "owner": actor,
            **definition,
        }
        self.db.execute(
            text("""
            INSERT INTO domain_reporting.query_definitions
              (id,tenant_id,owner_id,name,data_product_id,selected_fields,filter_spec,aggregations,is_favorite)
            VALUES (:id,:tid,:owner,:name,:data_product_id,CAST(:selected_fields AS jsonb),
                    CAST(:filter_spec AS jsonb),CAST(:aggregations AS jsonb),:is_favorite)
            ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name,data_product_id=EXCLUDED.data_product_id,
              selected_fields=EXCLUDED.selected_fields,filter_spec=EXCLUDED.filter_spec,
              aggregations=EXCLUDED.aggregations,is_favorite=EXCLUDED.is_favorite,updated_at=NOW()
            WHERE query_definitions.tenant_id=:tid AND query_definitions.owner_id=:owner
            """),
            {
                **params,
                "selected_fields": json.dumps(definition["selected_fields"]),
                "filter_spec": json.dumps(definition["filter_spec"]),
                "aggregations": json.dumps(definition["aggregations"]),
            },
        )
        self._audit(definition_id, "saved", actor, reason, self._hash(definition))
        self.db.commit()
        return {"id": definition_id, **definition}

    def list_page(
        self,
        *,
        owner_id: str,
        page: int = 1,
        page_size: int = 50,
        favorite: bool | None = None,
    ) -> dict[str, Any]:
        where = ["tenant_id=:tid", "owner_id=:owner"]
        params: dict[str, Any] = {"tid": self.tenant_id, "owner": owner_id}
        if favorite is not None:
            where.append("is_favorite=:favorite")
            params["favorite"] = favorite
        where_sql = " AND ".join(where)
        total = self.db.execute(
            text(
                f"SELECT COUNT(*) FROM domain_reporting.query_definitions WHERE {where_sql}"
            ),
            params,
        ).scalar_one()
        params.update(limit=page_size, offset=(page - 1) * page_size)
        rows = (
            self.db.execute(
                text(f"""
          SELECT id,name,data_product_id,selected_fields,filter_spec,aggregations,is_favorite,created_at,updated_at
            FROM domain_reporting.query_definitions WHERE {where_sql}
           ORDER BY is_favorite DESC,updated_at DESC LIMIT :limit OFFSET :offset
        """),
                params,
            )
            .mappings()
            .all()
        )
        return {
            "items": [dict(row) for row in rows],
            "total": int(total),
            "page": page,
            "page_size": page_size,
        }

    def export_signed(
        self, definition_id: str, *, actor: str, reason: str
    ) -> dict[str, Any]:
        if not self.signing_key:
            raise QueryCenterError("Signierschluessel ist nicht konfiguriert")
        definition = self._load(definition_id, actor)
        payload = {"schema_version": 1, "definition": definition}
        canonical = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=str
        )
        signature = hmac.new(
            self.signing_key.encode(), canonical.encode(), hashlib.sha256
        ).hexdigest()
        self._audit(
            definition_id,
            "exported",
            actor,
            reason,
            hashlib.sha256(canonical.encode()).hexdigest(),
        )
        self.db.commit()
        return {**payload, "algorithm": "HMAC-SHA256", "signature": signature}

    def import_signed(
        self, bundle: dict[str, Any], *, actor: str, reason: str
    ) -> dict[str, Any]:
        if not self.signing_key:
            raise QueryCenterError("Signierschluessel ist nicht konfiguriert")
        signature = str(bundle.get("signature") or "")
        payload = {
            "schema_version": bundle.get("schema_version"),
            "definition": bundle.get("definition"),
        }
        canonical = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=str
        )
        expected = hmac.new(
            self.signing_key.encode(), canonical.encode(), hashlib.sha256
        ).hexdigest()
        if payload["schema_version"] != 1 or not hmac.compare_digest(
            expected, signature
        ):
            raise QueryCenterError("Signatur der Abfragedefinition ist ungueltig")
        imported = dict(payload["definition"] or {})
        imported.pop("id", None)
        imported["name"] = f"{imported.get('name', 'Abfrage')} (Import)"
        return self.save(imported, actor=actor, reason=reason)

    def _load(self, definition_id: str, owner_id: str) -> dict[str, Any]:
        row = (
            self.db.execute(
                text("""
          SELECT id,name,data_product_id,selected_fields,filter_spec,aggregations,is_favorite
            FROM domain_reporting.query_definitions
           WHERE id=:id AND tenant_id=:tid AND owner_id=:owner
        """),
                {"id": definition_id, "tid": self.tenant_id, "owner": owner_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            raise LookupError("Abfragedefinition nicht gefunden")
        return dict(row)

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()

    def _audit(
        self,
        definition_id: str | None,
        action: str,
        actor: str,
        reason: str,
        payload_hash: str | None,
    ) -> None:
        self.db.execute(
            text("""
          INSERT INTO domain_reporting.query_center_audit
            (id,tenant_id,definition_id,action,actor,reason,payload_hash)
          VALUES (:id,:tid,:definition_id,:action,:actor,:reason,:payload_hash)
        """),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "definition_id": definition_id,
                "action": action,
                "actor": actor,
                "reason": reason,
                "payload_hash": payload_hash,
            },
        )
