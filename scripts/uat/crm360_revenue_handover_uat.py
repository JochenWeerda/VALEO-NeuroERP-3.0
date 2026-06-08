"""Persistent CRM360 revenue handover UAT.

Runs only with --execute. The script seeds one marked customer, drives the
public API from offer to order, delivery and docflow invoice, then removes all
created rows directly by their recorded IDs.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.config import settings
from app.core.database import SessionLocal


TENANT_ID = os.getenv("VALEO_CRM360_UAT_TENANT_ID", settings.DEFAULT_TENANT_ID)
API_BASE_URL = os.getenv("VALEO_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_TIMEOUT_SECONDS = float(os.getenv("VALEO_CRM360_UAT_TIMEOUT_SECONDS", "90"))


class UatFailure(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID,
    }
    token = os.getenv("VALEO_CRM360_UAT_TOKEN") or os.getenv("VALEO_API_TOKEN")
    if not token and settings.APP_ENV.lower() in {"dev", "development", "local"}:
        token = "dev-token"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def request_json(method: str, path: str, payload: dict[str, Any] | None = None, expected: set[int] | None = None) -> Any:
    expected = expected or ({204} if method == "DELETE" else {200, 201})
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(f"{API_BASE_URL}{path}", data=body, headers=_headers(), method=method)
    try:
        with urlopen(req, timeout=API_TIMEOUT_SECONDS) as response:  # noqa: S310 - explicit local/API UAT target
            status = response.status
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise UatFailure(f"{method} {path} failed with HTTP {exc.code}: {raw}") from exc
    except URLError as exc:
        raise UatFailure(f"{method} {path} failed: {exc}") from exc
    if status not in expected:
        raise UatFailure(f"{method} {path} returned HTTP {status}, expected {sorted(expected)}: {raw}")
    if status == 204 or not raw:
        return None
    return json.loads(raw)


def seed_customer(db, customer_id: str, customer_number: str, customer_name: str) -> None:
    db.execute(
        text(
            """
            INSERT INTO domain_crm.customers
            (id, tenant_id, customer_number, company_name, contact_person, email,
             phone, address, city, postal_code, country, is_active, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :customer_number, :company_name, 'UAT', :email,
             '+49 555 360', 'UAT-Strasse 1', 'Aurich', '26603', 'DE', TRUE, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": customer_id,
            "tenant_id": TENANT_ID,
            "customer_number": customer_number,
            "company_name": customer_name,
            "email": f"{customer_number.lower()}@example.invalid",
        },
    )
    db.commit()


def cleanup(db, ids: dict[str, str]) -> None:
    doc_ids = [ids.get("invoice_doc_id"), ids.get("delivery_id")]
    doc_ids = [doc_id for doc_id in doc_ids if doc_id]
    if doc_ids:
        db.execute(
            text("DELETE FROM domain_docflow.command_idempotency_keys WHERE tenant_id = :tenant_id AND resource_id = ANY(:ids)"),
            {"tenant_id": TENANT_ID, "ids": doc_ids},
        )
        db.execute(
            text("DELETE FROM domain_docflow.create_request_idempotency WHERE tenant_id = :tenant_id AND doc_id = ANY(:ids)"),
            {"tenant_id": TENANT_ID, "ids": doc_ids},
        )
        db.execute(
            text("DELETE FROM domain_docflow.document_links WHERE tenant_id = :tenant_id AND (from_header_id = ANY(:ids) OR to_header_id = ANY(:ids))"),
            {"tenant_id": TENANT_ID, "ids": doc_ids},
        )
        db.execute(
            text("DELETE FROM domain_docflow.document_header_links WHERE tenant_id = :tenant_id AND (from_header_id = ANY(:ids) OR to_header_id = ANY(:ids))"),
            {"tenant_id": TENANT_ID, "ids": doc_ids},
        )
        db.execute(
            text("DELETE FROM domain_docflow.document_postings WHERE tenant_id = :tenant_id AND header_id = ANY(:ids)"),
            {"tenant_id": TENANT_ID, "ids": doc_ids},
        )
        db.execute(
            text("DELETE FROM domain_docflow.document_items WHERE tenant_id = :tenant_id AND header_id = ANY(:ids)"),
            {"tenant_id": TENANT_ID, "ids": doc_ids},
        )
        db.execute(
            text("DELETE FROM domain_docflow.document_headers WHERE tenant_id = :tenant_id AND id = ANY(:ids)"),
            {"tenant_id": TENANT_ID, "ids": doc_ids},
        )
        db.execute(
            text("DELETE FROM outbox_events WHERE tenant_id = :tenant_id AND aggregate_id = ANY(:ids)"),
            {"tenant_id": TENANT_ID, "ids": doc_ids},
        )
    if ids.get("delivery_id"):
        db.execute(text("DELETE FROM domain_sales.delivery_note_positions WHERE delivery_note_id = :id"), {"id": ids["delivery_id"]})
        db.execute(text("DELETE FROM domain_sales.delivery_notes WHERE tenant_id = :tenant_id AND id = :id"), {"tenant_id": TENANT_ID, "id": ids["delivery_id"]})
    if ids.get("order_id"):
        db.execute(text("DELETE FROM domain_crm.sales_order_items WHERE tenant_id = :tenant_id AND order_id = :id"), {"tenant_id": TENANT_ID, "id": ids["order_id"]})
        db.execute(text("DELETE FROM domain_crm.sales_orders WHERE tenant_id = :tenant_id AND id = :id"), {"tenant_id": TENANT_ID, "id": ids["order_id"]})
    if ids.get("offer_id"):
        db.execute(text("DELETE FROM domain_crm.sales_offer_items WHERE tenant_id = :tenant_id AND offer_id = :id"), {"tenant_id": TENANT_ID, "id": ids["offer_id"]})
        db.execute(text("DELETE FROM domain_crm.sales_offers WHERE tenant_id = :tenant_id AND id = :id"), {"tenant_id": TENANT_ID, "id": ids["offer_id"]})
    if ids.get("customer_id"):
        db.execute(text("DELETE FROM domain_crm.customers WHERE tenant_id = :tenant_id AND id = :id"), {"tenant_id": TENANT_ID, "id": ids["customer_id"]})
    db.commit()


def assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise UatFailure(f"{label}: expected {expected!r}, got {actual!r}")


def fetch_docflow_header(doc_id: str) -> dict[str, Any] | None:
    with SessionLocal() as verification_db:
        row = verification_db.execute(
            text(
                """
                SELECT id, tenant_id, doc_type, source_ref, customer_id, deleted_at
                FROM domain_docflow.document_headers
                WHERE id = :id
                """
            ),
            {"id": doc_id},
        ).mappings().first()
        return dict(row) if row else None


def run() -> dict[str, Any]:
    marker = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    ids: dict[str, str] = {
        "customer_id": f"crm360-uat-customer-{marker}",
    }
    customer_number = f"UAT360-{marker}"
    customer_name = f"CRM360 UAT Kunde {marker}"
    offer_number = f"UAT-ANG-{marker}"

    db = SessionLocal()
    try:
        seed_customer(db, ids["customer_id"], customer_number, customer_name)
        offer = request_json(
            "POST",
            "/api/v1/sales/offers/",
            {
                "offer_number": offer_number,
                "customer_id": ids["customer_id"],
                "customer_name": customer_name,
                "subject": "CRM360 UAT Revenue Handover",
                "description": "Automatischer CRM360-UAT-Durchstich",
                "items": [{
                    "article_number": "UAT-SAAT-360",
                    "description": "CRM360 UAT Saatgut",
                    "quantity": 2,
                    "unit": "Stk",
                    "unit_price": 10,
                    "discount_percent": 0,
                }],
            },
        )
        ids["offer_id"] = offer["id"]
        assert_equal(offer["items"][0]["line_total"], 20.0, "offer item total")

        conversion = request_json("POST", f"/api/v1/sales/offers/{ids['offer_id']}/convert-to-order")
        ids["order_id"] = conversion["created_order_id"]
        order = request_json("GET", f"/api/v1/sales/orders/{ids['order_id']}")
        assert_equal(order["sales_offer_id"], ids["offer_id"], "order sales_offer_id")
        assert_equal(order["items"][0]["article_number"], "UAT-SAAT-360", "order item article")

        delivery_result = request_json("POST", f"/api/v1/sales/orders/{ids['order_id']}/create-delivery-note")
        ids["delivery_id"] = delivery_result["delivery_note_id"]
        delivery = request_json("GET", f"/api/v1/sales/delivery-notes/{ids['delivery_id']}")
        assert_equal(delivery["customer_id"], ids["customer_id"], "delivery customer")
        assert_equal(delivery["status"], "draft", "delivery status")
        assert_equal(delivery["positionen"][0]["artikel_nr"], "UAT-SAAT-360", "delivery item article")

        docflow_delivery = request_json("GET", f"/api/v1/docflow/{ids['delivery_id']}?tenant_id={TENANT_ID}")
        assert_equal(docflow_delivery["doc_type"], "sales_delivery", "docflow source type")
        assert_equal(docflow_delivery["customer_id"], ids["customer_id"], "docflow delivery customer")

        conversion_to_invoice = request_json(
            "POST",
            f"/api/v1/docflow/{ids['delivery_id']}/convert?tenant_id={TENANT_ID}",
            {
                "target_doc_type": "sales_invoice",
                "idempotency_key": f"crm360-uat-{marker}",
                "created_by": "crm360-uat",
            },
        )
        ids["invoice_doc_id"] = conversion_to_invoice["target_doc_id"]
        persisted_invoice = fetch_docflow_header(ids["invoice_doc_id"])
        if not persisted_invoice:
            raise UatFailure(
                f"docflow conversion returned target {ids['invoice_doc_id']} that was not persisted"
            )
        assert_equal(persisted_invoice["tenant_id"], TENANT_ID, "persisted invoice tenant")
        assert_equal(persisted_invoice["deleted_at"], None, "persisted invoice deleted_at")
        invoice = request_json("GET", f"/api/v1/docflow/{ids['invoice_doc_id']}?tenant_id={TENANT_ID}")
        assert_equal(invoice["doc_type"], "sales_invoice", "invoice doc type")
        assert_equal(invoice["source_ref"], ids["delivery_id"], "invoice source_ref")
        assert_equal(invoice["customer_id"], ids["customer_id"], "invoice customer")
        assert_equal(invoice["items"][0]["article_number"], "UAT-SAAT-360", "invoice item article")

        result = {
            "status": "passed",
            "tenant_id": TENANT_ID,
            "offer_id": ids["offer_id"],
            "order_id": ids["order_id"],
            "delivery_id": ids["delivery_id"],
            "invoice_doc_id": ids["invoice_doc_id"],
            "invoice_number": invoice["doc_number"],
        }
        request_json(
            "DELETE",
            f"/api/v1/docflow/{ids['invoice_doc_id']}?tenant_id={TENANT_ID}",
        )
        deleted_invoice = fetch_docflow_header(ids["invoice_doc_id"])
        if not deleted_invoice:
            raise UatFailure("deleted invoice draft disappeared instead of being soft-deleted")
        if deleted_invoice["deleted_at"] is None:
            raise UatFailure("invoice draft cleanup did not set deleted_at")
        return result
    finally:
        cleanup(db, ids)
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Run against the configured API and database.")
    args = parser.parse_args()
    if not args.execute:
        print("SKIPPED: pass --execute to run the persistent CRM360 revenue UAT.")
        return 0
    if settings.APP_ENV.lower() in {"prod", "production"}:
        print("REFUSED: persistent UAT must not run in production.", file=sys.stderr)
        return 2
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
