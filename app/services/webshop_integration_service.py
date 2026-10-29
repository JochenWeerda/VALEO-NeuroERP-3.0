"""Service layer for B2B webshop order imports.

Bis 20.10.2026 hielt der Dienst Konfigurationen und Bestellungen ersatzweise im Arbeitsspeicher (keine Migration legte
die Tabellen an), und "verarbeiten" meldete "Auftrag im ERP angelegt" mit erfundener Nummer — auch fuer unbekannte
Bestellungen und obwohl das Anlegen des Auftrags ohne Kunde jedes Mal scheiterte (Fehler verschluckt). Jetzt: Tabellen
(``webshop_tabellen_20261020``), Kunde ueber die E-Mail im Mandanten, Auftrag in derselben Transaktion.
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session


class WebshopBestellungUnbekannt(LookupError):
    """Die Bestellnummer gibt es im Mandanten nicht."""


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _money(value: Any) -> Decimal:
    try:
        return Decimal(str(value or 0)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return Decimal("0.00")


_BESTELLSPALTEN = ("id, externe_bestellnr, shop_system, kunde_email, kunde_name, artikel_positionen, "
                   "gesamtbetrag_brutto, bestelldatum, status, blockers, imported_at, erp_order_number, processed_at")


class WebshopIntegrationService:
    """Coordinates external B2B webshop orders with ERP-visible order state."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def list_configurations(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            text(
                "SELECT id, shop_url, shop_system, sync_interval_minutes, is_active "
                "FROM domain_shared.webshop_configs WHERE tenant_id = :tid ORDER BY created_at LIMIT 200"
            ),
            {"tid": self.tenant_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def create_configuration(self, payload: dict[str, Any]) -> dict[str, Any]:
        config_id = str(uuid4())
        record = {
            "id": config_id,
            "shop_url": payload["shop_url"],
            "shop_system": payload["shop_system"],
            "sync_interval_minutes": int(payload.get("sync_interval_minutes") or 15),
            "is_active": bool(payload.get("is_active", True)),
        }
        self.db.execute(
            text(
                "INSERT INTO domain_shared.webshop_configs "
                "(id, tenant_id, shop_url, api_key_masked, shop_system, sync_interval_minutes, is_active) "
                "VALUES (:id, :tid, :url, :key, :sys, :interval, :active)"
            ),
            {
                "id": config_id,
                "tid": self.tenant_id,
                "url": record["shop_url"],
                "key": self._mask_api_key(str(payload.get("api_key") or "")),
                "sys": record["shop_system"],
                "interval": record["sync_interval_minutes"],
                "active": record["is_active"],
            },
        )
        self.db.commit()
        return record

    def delete_configuration(self, config_id: str) -> None:
        self.db.execute(
            text("DELETE FROM domain_shared.webshop_configs WHERE id = :id AND tenant_id = :tid"),
            {"id": config_id, "tid": self.tenant_id},
        )
        self.db.commit()

    def list_orders(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            text(
                f"SELECT {_BESTELLSPALTEN} FROM domain_shared.webshop_bestellungen "  # nosec B608  # reviewed-safe: Spaltenliste ist ein Code-Literal
                "WHERE tenant_id = :tid ORDER BY imported_at DESC LIMIT 200"
            ),
            {"tid": self.tenant_id},
        ).mappings().all()
        return [self._normalize_db_order(dict(row)) for row in rows]

    def get_order(self, external_order_no: str) -> dict[str, Any] | None:
        row = self.db.execute(
            text(
                f"SELECT {_BESTELLSPALTEN} FROM domain_shared.webshop_bestellungen "  # nosec B608  # reviewed-safe: Spaltenliste ist ein Code-Literal
                "WHERE tenant_id = :tid AND externe_bestellnr = :external_order_no"
            ),
            {"tid": self.tenant_id, "external_order_no": external_order_no},
        ).mappings().first()
        return self._normalize_db_order(dict(row)) if row is not None else None

    def import_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        imported: list[str] = []
        duplicates: list[str] = []
        blocked: list[dict[str, Any]] = []
        shop_system = orders[0].get("shop_system") if orders else "CUSTOM"

        for payload in orders:
            external_no = str(payload.get("externe_bestellnr") or "").strip()
            blockers = self._validate_order(payload)
            if not external_no:
                # Ohne externe Nummer nicht eindeutig speicherbar: gemeldet, nicht gespeichert.
                blocked.append({"externe_bestellnr": "", "blockers": blockers})
                continue
            if self.get_order(external_no):
                duplicates.append(external_no)
                continue

            status = "FEHLER" if blockers else str(payload.get("status") or "NEU")
            record = self._build_order_record(payload, status=status, blockers=blockers)
            self._persist_order(record)
            imported.append(record["externe_bestellnr"])
            if blockers:
                blocked.append({"externe_bestellnr": record["externe_bestellnr"], "blockers": blockers})

        self._protokoll(shop_system or "CUSTOM", "IMPORT",
                        f"{len(imported)} neu, {len(duplicates)} Duplikate, {len(blocked)} mit Blockern",
                        erfolgreich=not blocked)
        self.db.commit()
        return {
            "sync_id": str(uuid4()),
            "shop_system": shop_system or "CUSTOM",
            "neue_bestellungen": len(imported),
            "fehler": len(blocked),
            "verarbeitete_ids": imported + duplicates,
            "duplikate": duplicates,
            "blockierte_bestellungen": blocked,
            "sync_zeitpunkt": _now_iso(),
        }

    def process_order(self, external_order_no: str) -> dict[str, Any]:
        order = self.get_order(external_order_no)
        if not order:
            raise WebshopBestellungUnbekannt(external_order_no)
        if order.get("erp_order_number"):
            return {"verarbeitet": True, "auftrag_nr": order["erp_order_number"],
                    "hinweis": "Bereits als Auftrag im ERP angelegt"}
        blockers = list(order.get("blockers") or [])
        kunde_id = self._kunde_zur_email(order.get("kunde_email") or "")
        if kunde_id is None:
            blockers.append("KUNDE_NICHT_ZUGEORDNET")
        if blockers:
            return {
                "verarbeitet": False,
                "auftrag_nr": None,
                "hinweis": "Webshop-Bestellung hat fachliche Blocker",
                "blockers": blockers,
            }
        erp_order_no = self._erp_order_number()
        total = sum(_money(p.get("menge")) * _money(p.get("preis_brutto"))
                    for p in (order.get("artikel_positionen") or []))
        # Auftrag und Verarbeitungsstand in einer Transaktion: kein "angelegt" ohne Auftrag.
        self.db.execute(text("""
            INSERT INTO domain_crm.sales_orders
                (id, tenant_id, order_number, customer_id, customer_name, subject, description, total_amount,
                 currency, status, notes, created_at, updated_at, version)
            VALUES (:id, :tid, :on, :cid, :cname, :subj, :descr, :total, 'EUR', 'open', :notes, NOW(), NOW(), 1)
        """), {
            "id": str(uuid4()), "tid": self.tenant_id, "on": erp_order_no, "cid": kunde_id,
            "cname": order.get("kunde_name") or None,
            "subj": f"Webshop-Import {order.get('externe_bestellnr', '')}",
            "descr": f"Webshop-Bestellung {order.get('externe_bestellnr', '')} vom {order.get('bestelldatum', '')}",
            "total": float(total),
            "notes": f"Webshop: {order.get('shop_system', '')} | ExtNr: {order.get('externe_bestellnr', '')}",
        })
        self.db.execute(text(
            "UPDATE domain_shared.webshop_bestellungen SET status = 'VERARBEITET', erp_order_number = :nr, "
            "processed_at = NOW() WHERE tenant_id = :tid AND externe_bestellnr = :enr"
        ), {"nr": erp_order_no, "tid": self.tenant_id, "enr": external_order_no})
        self._protokoll(order.get("shop_system") or "CUSTOM", "AUFTRAG",
                        f"Bestellung {external_order_no} -> Auftrag {erp_order_no}", erfolgreich=True)
        self.db.commit()
        return {"verarbeitet": True, "auftrag_nr": erp_order_no, "hinweis": "Auftrag im ERP angelegt"}

    def get_sync_log(self) -> list[dict[str, Any]]:
        """Return last 50 sync events from the log table."""
        rows = self.db.execute(
            text(
                "SELECT id, shop_system, ereignis, details, erfolgreich, zeitpunkt "
                "FROM domain_shared.webshop_sync_log WHERE tenant_id = :tid "
                "ORDER BY zeitpunkt DESC LIMIT 50"
            ),
            {"tid": self.tenant_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def sync_status(self) -> dict[str, Any]:
        active_configs = sum(1 for config in self.list_configurations() if config.get("is_active"))
        orders = self.list_orders()
        open_blockers = sum(1 for order in orders if order.get("status") == "FEHLER" or order.get("blockers"))
        return {
            "status": "BEREIT" if open_blockers == 0 else "BLOCKER",
            "letzter_sync": max((order.get("imported_at") for order in orders if order.get("imported_at")), default=None),
            "konfigurationen_aktiv": active_configs,
            "offene_blocker": open_blockers,
            "hinweis": "Webshop-Connector bereit; produktive Provider-Signaturen extern konfigurieren",
        }

    def _kunde_zur_email(self, email: str) -> str | None:
        if not email.strip():
            return None
        return self.db.execute(
            text("SELECT id FROM domain_crm.customers WHERE tenant_id = :tid AND lower(email) = lower(:mail) "
                 "AND deleted_at IS NULL LIMIT 1"),
            {"tid": self.tenant_id, "mail": email.strip()},
        ).scalar()

    def _protokoll(self, shop_system: str, ereignis: str, details: str, *, erfolgreich: bool) -> None:
        self.db.execute(text(
            "INSERT INTO domain_shared.webshop_sync_log (id, tenant_id, shop_system, ereignis, details, erfolgreich) "
            "VALUES (:id, :tid, :sys, :ereignis, :details, :ok)"
        ), {"id": str(uuid4()), "tid": self.tenant_id, "sys": shop_system, "ereignis": ereignis,
            "details": details, "ok": erfolgreich})

    def _persist_order(self, record: dict[str, Any]) -> None:
        self.db.execute(
            text(
                "INSERT INTO domain_shared.webshop_bestellungen "
                "(id, tenant_id, externe_bestellnr, shop_system, kunde_email, kunde_name, "
                "artikel_positionen, gesamtbetrag_brutto, bestelldatum, status, blockers) "
                "VALUES (:id, :tid, :enr, :sys, :email, :name, CAST(:pos AS jsonb), :betrag, :datum, :status, "
                "CAST(:blockers AS jsonb))"
            ),
            {
                "id": record["id"],
                "tid": self.tenant_id,
                "enr": record["externe_bestellnr"],
                "sys": record["shop_system"],
                "email": record["kunde_email"],
                "name": record["kunde_name"],
                "pos": json.dumps(record["artikel_positionen"]),
                "betrag": record["gesamtbetrag_brutto"],
                "datum": record["bestelldatum"],
                "status": record["status"],
                "blockers": json.dumps(record["blockers"]),
            },
        )

    @staticmethod
    def _mask_api_key(api_key: str) -> str:
        return f"{api_key[:4]}****" if len(api_key) >= 4 else "****"

    @staticmethod
    def _erp_order_number() -> str:
        return f"WS-{uuid4().hex[:8].upper()}"

    @staticmethod
    def _normalize_db_order(row: dict[str, Any]) -> dict[str, Any]:
        def zeit(wert: Any) -> str | None:
            return wert.isoformat() if hasattr(wert, "isoformat") else (str(wert) if wert else None)

        return {
            "id": str(row.get("id")),
            "externe_bestellnr": row.get("externe_bestellnr"),
            "shop_system": row.get("shop_system"),
            "kunde_email": row.get("kunde_email"),
            "kunde_name": row.get("kunde_name"),
            "artikel_positionen": row.get("artikel_positionen") or [],
            "gesamtbetrag_brutto": float(row.get("gesamtbetrag_brutto") or 0),
            "bestelldatum": str(row.get("bestelldatum") or ""),
            "status": row.get("status") or "NEU",
            "blockers": row.get("blockers") or [],
            "imported_at": zeit(row.get("imported_at")),
            "erp_order_number": row.get("erp_order_number"),
            "processed_at": zeit(row.get("processed_at")),
        }

    def _build_order_record(self, payload: dict[str, Any], *, status: str, blockers: list[str]) -> dict[str, Any]:
        return {
            "id": str(uuid4()),
            "tenantId": self.tenant_id,
            "externe_bestellnr": str(payload.get("externe_bestellnr") or "").strip(),
            "shop_system": str(payload.get("shop_system") or "CUSTOM").strip() or "CUSTOM",
            "kunde_email": str(payload.get("kunde_email") or "").strip(),
            "kunde_name": str(payload.get("kunde_name") or "").strip(),
            "artikel_positionen": [dict(position) for position in payload.get("artikel_positionen") or []],
            "gesamtbetrag_brutto": float(_money(payload.get("gesamtbetrag_brutto"))),
            "bestelldatum": str(payload.get("bestelldatum") or "")[:32],
            "status": status,
            "blockers": blockers,
            "imported_at": _now_iso(),
        }

    def _validate_order(self, payload: dict[str, Any]) -> list[str]:
        blockers: list[str] = []
        if not str(payload.get("externe_bestellnr") or "").strip():
            blockers.append("EXTERNAL_ORDER_NO_MISSING")
        if not str(payload.get("kunde_email") or "").strip() and not str(payload.get("kunde_name") or "").strip():
            blockers.append("CUSTOMER_CONTEXT_MISSING")
        positions = payload.get("artikel_positionen") or []
        if not positions:
            blockers.append("ORDER_LINES_MISSING")

        calculated = Decimal("0.00")
        for index, position in enumerate(positions, start=1):
            article_no = str(position.get("artikel_nr") or "").strip()
            quantity = _money(position.get("menge"))
            gross_price = _money(position.get("preis_brutto"))
            if not article_no:
                blockers.append(f"LINE_{index}_ARTICLE_NO_MISSING")
            if quantity <= 0:
                blockers.append(f"LINE_{index}_QUANTITY_INVALID")
            if gross_price < 0:
                blockers.append(f"LINE_{index}_PRICE_INVALID")
            calculated += quantity * gross_price

        provided_total = _money(payload.get("gesamtbetrag_brutto"))
        if positions and abs(calculated - provided_total) > Decimal("0.02"):
            blockers.append("ORDER_TOTAL_MISMATCH")
        return blockers
