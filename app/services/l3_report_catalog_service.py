"""Fixed L3 report catalog with shared sums, export and document drilldown."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
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
    category: str = "Basis"
    description: str = ""
    legacy_menu: str = "AUSWERTUNGEN"


REPORT_SPECS: dict[str, ReportSpec] = {
    spec.report_id: spec
    for spec in (
        ReportSpec(
            "sales-by-representative",
            "Umsatz nach Vertreter",
            "representative_id",
            "representative_name",
            ("sale",),
            "Umsatz",
        ),
        ReportSpec(
            "sales-by-customer",
            "Umsatz nach Kunde",
            "customer_id",
            "customer_name",
            ("sale",),
            "Kunden",
        ),
        ReportSpec(
            "sales-by-article",
            "Umsatz nach Artikel",
            "article_id",
            "article_name",
            ("sale",),
            "Artikel",
        ),
        ReportSpec(
            "sales-by-article-group",
            "Umsatz nach Artikelgruppe",
            "article_group_id",
            "article_group_name",
            ("sale",),
            "Artikel",
        ),
        ReportSpec(
            "inventory-by-batch",
            "Bewegung nach Charge",
            "batch_id",
            "batch_name",
            ("inventory_movement", "sale"),
            "Chargen",
        ),
        ReportSpec(
            "harvest-performance",
            "Ernte nach Annahme",
            "harvest_id",
            "harvest_name",
            ("harvest",),
            "Ernte",
        ),
        ReportSpec(
            "route-performance",
            "Leistung nach Strecke",
            "route_id",
            "route_name",
            ("route", "sale"),
            "Strecke",
        ),
        ReportSpec(
            "article-account",
            "Artikel-Konto",
            "article_id",
            "article_name",
            ("inventory_movement", "purchase", "sale"),
            "Artikel",
            "Periodisches Artikelkonto mit Bewegungen und Beleg-Drilldown.",
            "FAVORITEN > Artikel-Konto",
        ),
        ReportSpec(
            "article-account-print",
            "Artikel-Konto drucken",
            "article_id",
            "article_name",
            ("inventory_movement", "purchase", "sale"),
            "Artikel",
            "Druck- und Exportansicht des Artikelkontos.",
            "AUSWERTUNGEN > Artikel > Artikel-Konto drucken",
        ),
        ReportSpec(
            "article-group-management",
            "Chefauswertung Artikel-Gruppen",
            "article_group_id",
            "article_group_name",
            ("sale", "purchase"),
            "Artikel",
            "Verdichtete Mengen- und Wertanalyse je Artikelgruppe.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "warehouse-transfer-price",
            "Verrechnungspreis-Lagerauswertung",
            "article_id",
            "article_name",
            ("inventory_movement", "transfer_price"),
            "Artikel",
            "Bestands- und Verrechnungspreisbewegungen je Artikel.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "purchase-price-changes",
            "Aenderungen Einkaufspreise",
            "article_id",
            "article_name",
            ("purchase_price_change",),
            "Artikel",
            "Nachweis geaenderter Einkaufspreise mit Quelldokumenten.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "article-promotions",
            "Aktions-Auswertung",
            "article_id",
            "article_name",
            ("promotion", "sale"),
            "Artikel",
            "Mengen und Erloese aus Artikelaktionen.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "article-movements",
            "Uebersicht Artikelbewegungen",
            "article_id",
            "article_name",
            ("inventory_movement",),
            "Artikel",
            "Lagerbewegungen mit Beleg-Drilldown.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "warehouse-disposition",
            "Lager-Disposition",
            "article_id",
            "article_name",
            ("inventory_movement", "purchase", "sale"),
            "Disposition",
            "Verbrauch, Zugang und Dispositionsbasis je Artikel.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "search-offer",
            "Suche/Biete",
            "article_id",
            "article_name",
            ("offer", "demand"),
            "Disposition",
            "Angebots- und Bedarfslage je Artikel.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "grain-notification",
            "Getreidemeldung",
            "article_id",
            "article_name",
            ("grain_notification", "inventory_movement"),
            "Meldungen",
            "Getreidemengen fuer das freigegebene Meldeverfahren.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "mvo-notification",
            "MVO-Meldung",
            "article_id",
            "article_name",
            ("mvo_notification", "inventory_movement"),
            "Meldungen",
            "MVO-relevante Mengen nach Artikel.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "daily-close-journal",
            "Tagesabschluss-Journal",
            "article_id",
            "article_name",
            ("inventory_movement", "sale", "purchase"),
            "Journal",
            "Taegliche Artikelbewegungen und Werte.",
            "AUSWERTUNGEN > Artikel > Weitere",
        ),
        ReportSpec(
            "batch-number-register",
            "Auswertung Chargen-Nummern",
            "batch_id",
            "batch_name",
            ("inventory_movement", "production", "sale"),
            "Chargen",
            "Chargenregister mit Mengen und Quelldokumenten.",
            "AUSWERTUNGEN > Lager > Weitere",
        ),
        ReportSpec(
            "batch-stock-valuation",
            "Bestandsbewertung pro Chargen-Nummer",
            "batch_id",
            "batch_name",
            ("inventory_movement", "valuation"),
            "Chargen",
            "Mengen- und Wertbestand je Charge.",
            "AUSWERTUNGEN > Lager > Weitere",
        ),
        ReportSpec(
            "batch-use-trace",
            "Rueckverfolgung Chargen: Verwendung",
            "batch_id",
            "batch_name",
            ("inventory_movement", "production", "sale"),
            "Chargen",
            "Verwendungsnachweis mit Beleg-Drilldown.",
            "AUSWERTUNGEN > Lager > Weitere",
        ),
        ReportSpec(
            "customer-order-disposition",
            "Auftrag-Disposition",
            "customer_id",
            "customer_name",
            ("order", "sale"),
            "Kunden",
            "Offene und disponierte Auftragsmengen je Kunde.",
            "AUSWERTUNGEN > Kunden > Weitere",
        ),
        ReportSpec(
            "customer-offer-order-overview",
            "Angebots-/Auftrags-Uebersicht",
            "customer_id",
            "customer_name",
            ("offer", "order"),
            "Kunden",
            "Angebote und Auftraege im Periodenvergleich.",
            "AUSWERTUNGEN > Kunden > Weitere",
        ),
        ReportSpec(
            "customer-article-overview",
            "Kunden-Artikel",
            "customer_id",
            "customer_name",
            ("sale", "order"),
            "Kunden",
            "Kundenspezifische Artikelbewegungen.",
            "AUSWERTUNGEN > Kunden > Weitere",
        ),
        ReportSpec(
            "customer-certificates",
            "Kunden-Bescheinigungen",
            "customer_id",
            "customer_name",
            ("certificate",),
            "Kunden",
            "Ausgestellte und faellige Bescheinigungen.",
            "AUSWERTUNGEN > Kunden > Weitere",
        ),
        ReportSpec(
            "customer-gifts",
            "Kunden-Praesente",
            "customer_id",
            "customer_name",
            ("customer_gift",),
            "Kunden",
            "Praesente und Compliance-Nachweis je Kunde.",
            "AUSWERTUNGEN > Kunden > Weitere",
        ),
        ReportSpec(
            "fertilizer-quantities",
            "Duengemittelmengen",
            "customer_id",
            "customer_name",
            ("fertilizer_application",),
            "Agrar",
            "N/P/K-Mengen je Kunde und Periode.",
            "AUSWERTUNGEN > Weitere",
        ),
        ReportSpec(
            "bonus-by-customer",
            "Bonus an Kunden",
            "customer_id",
            "customer_name",
            ("bonus_eligible_sale",),
            "Bonus",
            "Bonusfaehige Umsaetze je Kunde und Periode.",
            "AUSWERTUNGEN > Weitere > Bonus-Berechnung",
        ),
        ReportSpec(
            "bonus-by-article-group",
            "Bonus nach Artikelgruppe",
            "article_group_id",
            "article_group_name",
            ("bonus_eligible_sale", "bonus_eligible_purchase"),
            "Bonus",
            "Bonusfaehige Werte je Artikelgruppe.",
            "AUSWERTUNGEN > Weitere > Bonus-Berechnung",
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
                "category": spec.category,
                "description": spec.description,
                "legacy_menu": spec.legacy_menu,
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

    def list_bonus_runs(self) -> dict[str, Any]:
        rows = (
            self.db.execute(
                text("""SELECT id, report_id, from_date, to_date, rate_pct, status,
                           total_basis, total_bonus, currency, correction_of,
                           reason, actor, created_at
                      FROM domain_reporting.l3_bonus_runs
                     WHERE tenant_id=:tid ORDER BY created_at DESC LIMIT 500"""),
                {"tid": self.tenant_id},
            )
            .mappings()
            .all()
        )
        items = [dict(row) for row in rows]
        return {
            "items": items,
            "total": len(items),
            "calculated": sum(1 for row in items if row["status"] == "calculated"),
            "corrections": sum(1 for row in items if row["status"] == "correction"),
            "total_bonus": sum(Decimal(str(row["total_bonus"] or 0)) for row in items),
        }

    def create_bonus_run(
        self,
        *,
        report_id: str,
        from_date: date,
        to_date: date,
        rate_pct: Decimal,
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        if report_id not in {"bonus-by-customer", "bonus-by-article-group"}:
            raise ReportCatalogError(
                "Nur freigegebene Bonusberichte duerfen berechnet werden"
            )
        if rate_pct <= 0 or rate_pct > 100:
            raise ReportCatalogError("Bonussatz muss zwischen 0 und 100 Prozent liegen")
        result = self.run(
            report_id, from_date=from_date, to_date=to_date, page=1, page_size=5000
        )
        run_id = str(uuid7())
        lines: list[dict[str, Any]] = []
        total_basis = Decimal("0")
        total_bonus = Decimal("0")
        for index, row in enumerate(result["items"]):
            basis = Decimal(str(row.get("gross_amount") or 0))
            bonus = (basis * rate_pct / Decimal("100")).quantize(Decimal("0.01"))
            total_basis += basis
            total_bonus += bonus
            lines.append(
                {
                    "id": str(uuid7()),
                    "run_id": run_id,
                    "line_no": index + 1,
                    "dimension_id": row["dimension_id"],
                    "dimension_name": row["dimension_name"],
                    "document_count": row["document_count"],
                    "basis_amount": basis,
                    "bonus_amount": bonus,
                    "currency": row.get("currency") or "EUR",
                }
            )
        self.db.execute(
            text("""INSERT INTO domain_reporting.l3_bonus_runs
                (id,tenant_id,report_id,from_date,to_date,rate_pct,status,total_basis,total_bonus,currency,reason,actor)
                VALUES (:id,:tid,:report_id,:from_date,:to_date,:rate_pct,'calculated',:total_basis,:total_bonus,'EUR',:reason,:actor)"""),
            {
                "id": run_id,
                "tid": self.tenant_id,
                "report_id": report_id,
                "from_date": from_date,
                "to_date": to_date,
                "rate_pct": rate_pct,
                "total_basis": total_basis,
                "total_bonus": total_bonus,
                "reason": reason,
                "actor": actor,
            },
        )
        for line in lines:
            self.db.execute(
                text("""INSERT INTO domain_reporting.l3_bonus_run_lines
                    (id,tenant_id,run_id,line_no,dimension_id,dimension_name,document_count,basis_amount,bonus_amount,currency)
                    VALUES (:id,:tid,:run_id,:line_no,:dimension_id,:dimension_name,:document_count,:basis_amount,:bonus_amount,:currency)"""),
                {**line, "tid": self.tenant_id},
            )
        self.db.commit()
        return {
            "id": run_id,
            "status": "calculated",
            "lines": len(lines),
            "total_basis": total_basis,
            "total_bonus": total_bonus,
        }

    def correct_bonus_run(
        self, run_id: str, *, amount: Decimal, actor: str, reason: str
    ) -> dict[str, Any]:
        source = (
            self.db.execute(
                text(
                    "SELECT report_id,from_date,to_date,currency FROM domain_reporting.l3_bonus_runs WHERE id=:id AND tenant_id=:tid"
                ),
                {"id": run_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if source is None:
            raise ReportCatalogError("Bonuslauf wurde nicht gefunden")
        correction_id = str(uuid7())
        self.db.execute(
            text("""INSERT INTO domain_reporting.l3_bonus_runs
                (id,tenant_id,report_id,from_date,to_date,rate_pct,status,total_basis,total_bonus,currency,correction_of,reason,actor)
                VALUES (:id,:tid,:report_id,:from_date,:to_date,0,'correction',0,:amount,:currency,:source,:reason,:actor)"""),
            {
                "id": correction_id,
                "tid": self.tenant_id,
                "report_id": source["report_id"],
                "from_date": source["from_date"],
                "to_date": source["to_date"],
                "amount": amount,
                "currency": source["currency"],
                "source": run_id,
                "reason": reason,
                "actor": actor,
            },
        )
        self.db.commit()
        return {
            "id": correction_id,
            "status": "correction",
            "correction_of": run_id,
            "total_bonus": amount,
        }

    def export_bonus_run(self, run_id: str, *, actor: str, reason: str) -> str:
        header = (
            self.db.execute(
                text(
                    "SELECT * FROM domain_reporting.l3_bonus_runs WHERE id=:id AND tenant_id=:tid"
                ),
                {"id": run_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if header is None:
            raise ReportCatalogError("Bonuslauf wurde nicht gefunden")
        rows = (
            self.db.execute(
                text("""SELECT line_no,dimension_id,dimension_name,document_count,basis_amount,bonus_amount,currency
                      FROM domain_reporting.l3_bonus_run_lines
                     WHERE tenant_id=:tid AND run_id=:id ORDER BY line_no"""),
                {"id": run_id, "tid": self.tenant_id},
            )
            .mappings()
            .all()
        )
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "line_no",
                "dimension_id",
                "dimension_name",
                "document_count",
                "basis_amount",
                "bonus_amount",
                "currency",
            ],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(dict(row) for row in rows)
        self.db.execute(
            text(
                "INSERT INTO domain_reporting.l3_report_audit (id,tenant_id,report_id,action,actor,reason,parameter_hash) VALUES (:id,:tid,:report_id,'bonus_exported',:actor,:reason,:hash)"
            ),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "report_id": header["report_id"],
                "actor": actor,
                "reason": reason,
                "hash": hashlib.sha256(run_id.encode()).hexdigest(),
            },
        )
        self.db.commit()
        return output.getvalue()
