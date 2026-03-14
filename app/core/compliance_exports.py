from __future__ import annotations

from collections import defaultdict
from typing import Optional


def extract_hazard_export_rows(deliveries: list[dict], year: Optional[int] = None) -> list[dict]:
    rows: list[dict] = []
    for d in deliveries:
        date_str = str(d.get("date") or "")
        if year and not date_str.startswith(f"{year}-"):
            continue
        doc_compliance = d.get("psmCompliance") or {}
        for line in d.get("lines") or []:
            has_psm = any([line.get("bvlZulassungsnummer"), line.get("hazardHinweise"), line.get("sdsReference")])
            if not has_psm:
                continue
            rows.append(
                {
                    "deliveryNumber": d.get("number") or d.get("id"),
                    "deliveryDate": date_str[:10] if len(date_str) >= 10 else None,
                    "supplierName": d.get("supplierName"),
                    "customerId": d.get("customerId"),
                    "article": line.get("article"),
                    "bvlZulassungsnummer": line.get("bvlZulassungsnummer"),
                    "hazardHinweise": line.get("hazardHinweise"),
                    "sdsReference": line.get("sdsReference"),
                    "sachkundeStatus": doc_compliance.get("sachkundeStatus"),
                    "sdsMitgeliefert": doc_compliance.get("sdsMitgeliefert"),
                    "adrPunkte": float(d.get("adrPunkte") or doc_compliance.get("adrPunkte") or 0),
                    "compliant": bool(doc_compliance.get("compliant", False)),
                }
            )
    return rows


def compute_nutrient_stream(deliveries: list[dict], year: int) -> dict:
    by_month: dict[str, dict[str, float]] = defaultdict(lambda: {"deliveries": 0.0, "n_kg": 0.0, "p2o5_kg": 0.0})
    total_n = 0.0
    total_p2o5 = 0.0
    count = 0

    for d in deliveries:
        date_str = str(d.get("date") or "")
        if not date_str.startswith(f"{year}-"):
            continue
        month = date_str[:7]
        n_kg = float(d.get("totalNutrientNKg") or 0.0)
        p2o5_kg = float(d.get("totalNutrientP2o5Kg") or 0.0)

        by_month[month]["deliveries"] += 1
        by_month[month]["n_kg"] += n_kg
        by_month[month]["p2o5_kg"] += p2o5_kg
        total_n += n_kg
        total_p2o5 += p2o5_kg
        count += 1

    return {
        "year": year,
        "deliveryCount": count,
        "totalNutrientNKg": round(total_n, 3),
        "totalNutrientP2o5Kg": round(total_p2o5, 3),
        "byMonth": {
            k: {
                "deliveries": int(v["deliveries"]),
                "n_kg": round(v["n_kg"], 3),
                "p2o5_kg": round(v["p2o5_kg"], 3),
            }
            for k, v in sorted(by_month.items())
        },
    }


def build_lot_trace_report(lot, deliveries: list[dict]) -> dict:
    events = [
        {"type": "charge_created", "date": lot.eingang.isoformat() if lot.eingang else None, "note": "Wareneingang erfasst"},
        {"type": "charge_updated", "date": lot.updated_at.isoformat() if lot.updated_at else None, "note": "Letzte Aktualisierung"},
    ]
    linked_deliveries = []
    for d in deliveries:
        for line in d.get("lines") or []:
            if (line.get("batchNumber") and str(line.get("batchNumber")) == str(lot.chargen_id)) or (
                line.get("articleId") and str(line.get("articleId")) == str(lot.artikel_id)
            ):
                linked_deliveries.append(
                    {
                        "deliveryNumber": d.get("number") or d.get("id"),
                        "deliveryDate": str(d.get("date") or "")[:10],
                        "article": line.get("article"),
                        "quantity": float(line.get("qty") or 0),
                        "customerId": d.get("customerId"),
                    }
                )
                break

    return {
        "lot": {
            "id": lot.id,
            "lotId": lot.chargen_id,
            "article": lot.artikel,
            "articleId": lot.artikel_id,
            "quantity": float(lot.menge or 0),
            "location": lot.lagerort,
            "status": lot.status,
            "qualityStatus": lot.qualitaetsstatus,
            "origin": lot.herkunft,
        },
        "events": events,
        "linkedDeliveries": linked_deliveries,
        "deliveryCount": len(linked_deliveries),
    }
