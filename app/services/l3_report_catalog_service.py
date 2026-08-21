"""Fixed L3 report catalog with shared sums, export and document drilldown."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


@dataclass(frozen=True)
class ReportSpec:
    report_id: str
    title: str
    dimension_id: str
    dimension_name: str
    fact_types: tuple[str, ...]


REPORT_SPECS: dict[str, ReportSpec] = {
    spec.report_id: spec
    for spec in (
        ReportSpec(
            "sales-by-representative",
            "Umsatz nach Vertreter",
            "representative_id",
            "representative_name",
            ("sale",),
        ),
        ReportSpec(
            "sales-by-customer",
            "Umsatz nach Kunde",
            "customer_id",
            "customer_name",
            ("sale",),
        ),
        ReportSpec(
            "sales-by-article",
            "Umsatz nach Artikel",
            "article_id",
            "article_name",
            ("sale",),
        ),
        ReportSpec(
            "sales-by-article-group",
            "Umsatz nach Artikelgruppe",
            "article_group_id",
            "article_group_name",
            ("sale",),
        ),
        ReportSpec(
            "inventory-by-batch",
            "Bewegung nach Charge",
            "batch_id",
            "batch_name",
            ("inventory_movement", "sale"),
        ),
        ReportSpec(
            "harvest-performance",
            "Ernte nach Annahme",
            "harvest_id",
            "harvest_name",
            ("harvest",),
        ),
        ReportSpec(
            "route-performance",
            "Leistung nach Strecke",
            "route_id",
            "route_name",
            ("route", "sale"),
        ),
    )
}
FILTER_COLUMNS = frozenset(
    {
        "representative_id",
        "customer_id",
        "article_id",
        "article_group_id",
        "batch_id",
        "harvest_id",
        "route_id",
        "currency",
    }
)


class ReportCatalogError(ValueError):
    pass


class L3ReportCatalogService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "id": spec.report_id,
                "title": spec.title,
                "dimension": spec.dimension_id,
                "parameters": ["from_date", "to_date", *sorted(FILTER_COLUMNS)],
                "sums": ["document_count", "quantity", "net_amount", "gross_amount"],
                "export_formats": ["csv"],
                "drilldown": True,
            }
            for spec in REPORT_SPECS.values()
        ]

    def project_fact(self, payload: dict[str, Any]) -> dict[str, Any]:
        for required in (
            "source_type",
            "source_ref",
            "source_route",
            "occurred_on",
            "fact_type",
        ):
            if not payload.get(required):
                raise ReportCatalogError(f"Pflichtfeld fehlt: {required}")
        if not str(payload["source_route"]).startswith("/"):
            raise ReportCatalogError("Quellenroute muss intern sein")
        canonical = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        fact_id = str(uuid7())
        columns = [
            "representative_id",
            "representative_name",
            "customer_id",
            "customer_name",
            "article_id",
            "article_name",
            "article_group_id",
            "article_group_name",
            "batch_id",
            "batch_name",
            "harvest_id",
            "harvest_name",
            "route_id",
            "route_name",
            "quantity",
            "net_amount",
            "gross_amount",
            "currency",
        ]
        params = {key: payload.get(key) for key in columns}
        params.update(
            id=fact_id,
            tid=self.tenant_id,
            source_type=payload["source_type"],
            source_ref=payload["source_ref"],
            source_number=payload.get("source_number"),
            source_route=payload["source_route"],
            occurred_on=payload["occurred_on"],
            fact_type=payload["fact_type"],
            payload_hash=digest,
        )
        self.db.execute(
            text(f"""
          INSERT INTO domain_reporting.l3_report_facts
            (id,tenant_id,source_type,source_ref,source_number,source_route,occurred_on,fact_type,{",".join(columns)},payload_hash)
          VALUES (:id,:tid,:source_type,:source_ref,:source_number,:source_route,:occurred_on,:fact_type,{",".join(":" + c for c in columns)},:payload_hash)
          ON CONFLICT (tenant_id,source_type,source_ref,fact_type) DO UPDATE SET
            source_number=EXCLUDED.source_number,source_route=EXCLUDED.source_route,occurred_on=EXCLUDED.occurred_on,
            {",".join(c + "=EXCLUDED." + c for c in columns)},payload_hash=EXCLUDED.payload_hash
        """),
            params,
        )
        self.db.commit()
        return {"id": fact_id, "payload_hash": digest}

    def run(
        self,
        report_id: str,
        *,
        from_date: date,
        to_date: date,
        filters: dict[str, str] | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        spec = REPORT_SPECS.get(report_id)
        if spec is None:
            raise ReportCatalogError("Bericht ist nicht freigegeben")
        if to_date < from_date:
            raise ReportCatalogError("Enddatum liegt vor Startdatum")
        where = [
            "tenant_id=:tid",
            "occurred_on BETWEEN :from_date AND :to_date",
            "fact_type = ANY(:fact_types)",
            f"{spec.dimension_id} IS NOT NULL",
        ]
        params: dict[str, Any] = {
            "tid": self.tenant_id,
            "from_date": from_date,
            "to_date": to_date,
            "fact_types": list(spec.fact_types),
        }
        for key, value in (filters or {}).items():
            if key not in FILTER_COLUMNS:
                raise ReportCatalogError(f"Filter ist nicht freigegeben: {key}")
            if value:
                where.append(f"{key}=:{key}")
                params[key] = value
        where_sql = " AND ".join(where)
        total_groups = self.db.execute(
            text(
                f"SELECT COUNT(DISTINCT {spec.dimension_id}) FROM domain_reporting.l3_report_facts WHERE {where_sql}"
            ),
            params,
        ).scalar_one()
        sums = (
            self.db.execute(
                text(
                    f"SELECT COUNT(*) document_count,COALESCE(SUM(quantity),0) quantity,COALESCE(SUM(net_amount),0) net_amount,COALESCE(SUM(gross_amount),0) gross_amount FROM domain_reporting.l3_report_facts WHERE {where_sql}"
                ),
                params,
            )
            .mappings()
            .one()
        )
        params.update(limit=page_size, offset=(page - 1) * page_size)
        rows = (
            self.db.execute(
                text(f"""
          SELECT {spec.dimension_id} dimension_id,COALESCE({spec.dimension_name},{spec.dimension_id}) dimension_name,
                 COUNT(*) document_count,COALESCE(SUM(quantity),0) quantity,
                 COALESCE(SUM(net_amount),0) net_amount,COALESCE(SUM(gross_amount),0) gross_amount,
                 MIN(currency) currency
            FROM domain_reporting.l3_report_facts WHERE {where_sql}
           GROUP BY {spec.dimension_id},{spec.dimension_name}
           ORDER BY gross_amount DESC,dimension_name LIMIT :limit OFFSET :offset
        """),
                params,
            )
            .mappings()
            .all()
        )
        return {
            "report_id": report_id,
            "title": spec.title,
            "items": [dict(row) for row in rows],
            "totals": dict(sums),
            "total": int(total_groups),
            "page": page,
            "page_size": page_size,
            "parameters": {
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat(),
                **(filters or {}),
            },
        }

    def drilldown(
        self,
        report_id: str,
        dimension_value: str,
        *,
        from_date: date,
        to_date: date,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        spec = REPORT_SPECS.get(report_id)
        if spec is None:
            raise ReportCatalogError("Bericht ist nicht freigegeben")
        rows = (
            self.db.execute(
                text(f"""
          SELECT source_type,source_ref,source_number,source_route,occurred_on,fact_type,
                 quantity,net_amount,gross_amount,currency,payload_hash
            FROM domain_reporting.l3_report_facts
           WHERE tenant_id=:tid AND occurred_on BETWEEN :from_date AND :to_date
             AND fact_type = ANY(:fact_types) AND {spec.dimension_id}=:dimension_value
           ORDER BY occurred_on DESC,source_number LIMIT :limit
        """),
                {
                    "tid": self.tenant_id,
                    "from_date": from_date,
                    "to_date": to_date,
                    "fact_types": list(spec.fact_types),
                    "dimension_value": dimension_value,
                    "limit": min(limit, 500),
                },
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def export_csv(
        self,
        report_id: str,
        *,
        from_date: date,
        to_date: date,
        filters: dict[str, str] | None,
        actor: str,
        reason: str,
    ) -> str:
        result = self.run(
            report_id,
            from_date=from_date,
            to_date=to_date,
            filters=filters,
            page=1,
            page_size=5000,
        )
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "dimension_id",
                "dimension_name",
                "document_count",
                "quantity",
                "net_amount",
                "gross_amount",
                "currency",
            ],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(result["items"])
        digest = hashlib.sha256(
            json.dumps(result["parameters"], sort_keys=True).encode()
        ).hexdigest()
        self.db.execute(
            text(
                "INSERT INTO domain_reporting.l3_report_audit (id,tenant_id,report_id,action,actor,reason,parameter_hash) VALUES (:id,:tid,:report_id,'exported',:actor,:reason,:hash)"
            ),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "report_id": report_id,
                "actor": actor,
                "reason": reason,
                "hash": digest,
            },
        )
        self.db.commit()
        return output.getvalue()
