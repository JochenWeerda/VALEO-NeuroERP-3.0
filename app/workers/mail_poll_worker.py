"""Mail-Poll-Worker — server-seitiger IMAP-Abruf je aktivem Mandant.

Iteriert alle Tenants mit aktivierter IMAP-Connector-Konfiguration (Admin-Suite,
`domain_shared.tenants.settings` → `connectors.imap.enabled`) und ruft pro Tenant
``MailIngestService.poll_once()`` auf. Neue Mails werden als Kontakte erfasst
(Auto-Capture), idempotent über Message-ID + UID-State je Ordner — ein häufiger
Lauf ist daher gefahrlos.

Konsistent mit den übrigen Workern (kein In-Process-Scheduler im App-Core): per
OS-Cron / Windows-Aufgabenplanung oder als Dauer-Daemon betreiben.

    # Einzel-Sweep (für Cron, z.B. alle 5 Min):
    python -m app.workers.mail_poll_worker

    # Dauerbetrieb (eigener Prozess), Intervall in Sekunden:
    python -m app.workers.mail_poll_worker --loop --interval 120

    # Nur ein Mandant:
    python -m app.workers.mail_poll_worker --tenant 00000000-0000-0000-0000-000000000001
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from typing import Any, Optional

from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.connector_config import load_imap_config
from app.services.mail_ingest_service import MailIngestService

logger = logging.getLogger("mail.poll.worker")


def _active_imap_tenants(db, only_tenant: Optional[str] = None) -> list[str]:
    """Alle Tenants mit aktiviertem/konfiguriertem IMAP-Connector.

    Filtert in Python über load_imap_config (robust gegenüber JSON/JSONB-Spalte
    und ENV-Fallback)."""
    if only_tenant:
        ids = [only_tenant]
    else:
        try:
            rows = db.execute(text("SELECT id FROM domain_shared.tenants")).fetchall()
            ids = [str(r[0]) for r in rows]
        except Exception as exc:  # noqa: BLE001 — ohne Tenant-Tabelle kein Abruf
            logger.error("Tenant-Liste nicht lesbar: %s", exc)
            return []
    return [tid for tid in ids if load_imap_config(db, tid).configured]


def poll_all_tenants(only_tenant: Optional[str] = None) -> dict[str, Any]:
    """Führt einen Abruf-Sweep über alle aktiven Mandanten aus (eigene Session)."""
    db = SessionLocal()
    result: dict[str, Any] = {"success": True, "tenants": 0, "processed": 0, "created": 0, "details": []}
    try:
        tenants = _active_imap_tenants(db, only_tenant)
        result["tenants"] = len(tenants)
        for tid in tenants:
            try:
                res = MailIngestService(db, tid).poll_once()
            except Exception as exc:  # noqa: BLE001 — ein Mandant darf den Sweep nicht stoppen
                db.rollback()
                logger.error("[MAIL POLL] Tenant %s fehlgeschlagen: %s", tid, exc)
                result["details"].append({"tenant": tid, "ok": False, "detail": str(exc)})
                continue
            result["processed"] += int(res.get("processed", 0))
            result["created"] += int(res.get("created", 0))
            result["details"].append({"tenant": tid, **res})
            if res.get("processed"):
                logger.info("[MAIL POLL] Tenant %s: %s", tid, res.get("detail"))
    except Exception as exc:  # noqa: BLE001
        result["success"] = False
        result["error"] = str(exc)
        logger.error("[MAIL POLL] Sweep-Fehler: %s", exc)
    finally:
        db.close()
    return result


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    p = argparse.ArgumentParser(description="Mail-Poll-Worker — IMAP-Abruf je aktivem Mandant.")
    p.add_argument("--tenant", default=None, help="Nur diesen Tenant abrufen (Default: alle aktiven)")
    p.add_argument("--loop", action="store_true", help="Dauerbetrieb statt Einzel-Sweep")
    p.add_argument("--interval", type=int, default=120, help="Intervall (Sek.) im --loop-Modus (Default 120)")
    args = p.parse_args(argv)

    if not args.loop:
        outcome = poll_all_tenants(args.tenant)
        print(json.dumps(outcome, indent=2, ensure_ascii=False, default=str))
        return 0 if outcome.get("success") else 1

    logger.info("Mail-Poll-Daemon gestartet (Intervall %ds).", args.interval)
    try:
        while True:
            outcome = poll_all_tenants(args.tenant)
            if not outcome.get("success"):
                logger.warning("Sweep mit Fehler: %s", outcome.get("error"))
            time.sleep(max(15, args.interval))
    except KeyboardInterrupt:
        logger.info("Beendet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
