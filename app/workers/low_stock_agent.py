"""Autonomer Low-Stock-Agent — reagiert auf NATS-Events und erstellt Bestellvorschläge.

Architektur:
  NATS JetStream Subject: erp.lager.bestand_unterschritten
  Event-Payload: { tenant_id, artikel_id, artikel_name, bestand, mindestbestand }

  Der Agent prüft den Lagerbestand, berechnet eine empfohlene Bestellmenge (EOQ-Heuristik)
  und legt automatisch einen Bestellvorschlag in domain_einkauf.bestellvorschlaege an.

Konfiguration:
  NATS_URL — Standard: nats://localhost:4222
  LOW_STOCK_AGENT_ENABLED — "1" aktiviert den Agent (Standard: deaktiviert)

Starten:
  python -m app.workers.low_stock_agent
  oder über BaseWorker-Scheduler (täglich + on-demand via NATS).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
AGENT_ENABLED = os.getenv("LOW_STOCK_AGENT_ENABLED", "0") == "1"

# Safety cap: agent never orders more than this factor × Mindestbestand
MAX_ORDER_FACTOR = 5.0


@dataclass
class LowStockEvent:
    tenant_id: str
    artikel_id: str
    artikel_name: str
    bestand: float
    mindestbestand: float
    einheit: str = "Stk"
    lieferant_id: Optional[str] = None
    durchschnittlicher_verbrauch_pro_tag: Optional[float] = None


@dataclass
class BestellvorschlagResult:
    vorschlag_id: Optional[str]
    artikel_id: str
    empfohlene_menge: float
    begruendung: str
    erfolg: bool
    fehler: Optional[str] = None


def _eoq_menge(
    bedarf_jaehrlich: float,
    bestellkosten: float = 25.0,
    lagerkosten_satz: float = 0.20,
    einheitspreis: float = 10.0,
) -> float:
    """Wilson EOQ: sqrt(2 * D * K / (h * p)) — Mindestbestellmenge."""
    if einheitspreis <= 0 or lagerkosten_satz <= 0:
        return max(1.0, bedarf_jaehrlich / 12)
    h = lagerkosten_satz * einheitspreis
    if h <= 0:
        return max(1.0, bedarf_jaehrlich / 12)
    return ((2 * bedarf_jaehrlich * bestellkosten) / h) ** 0.5


def berechne_empfohlene_menge(event: LowStockEvent) -> float:
    """Berechnet empfohlene Bestellmenge per EOQ-Heuristik."""
    if event.durchschnittlicher_verbrauch_pro_tag:
        jahresbedarf = event.durchschnittlicher_verbrauch_pro_tag * 365
    else:
        # Fallback: Mindestbestand × 3 als Jahresschätzung
        jahresbedarf = event.mindestbestand * 3

    eoq = _eoq_menge(jahresbedarf)
    fehlbedarf = max(0.0, event.mindestbestand - event.bestand)
    # Mindestens den Fehlbedarf decken, maximal den Safety-Cap
    menge = max(fehlbedarf, eoq)
    return min(menge, event.mindestbestand * MAX_ORDER_FACTOR)


async def _create_bestellvorschlag_db(event: LowStockEvent, menge: float, db) -> Optional[str]:
    """Legt Bestellvorschlag in domain_einkauf an. Gibt vorschlag_id zurück."""
    try:
        from sqlalchemy import text
        stmt = text("""
            INSERT INTO domain_einkauf.bestellvorschlaege
                (tenant_id, artikel_id, artikel_name, empfohlene_menge, einheit,
                 lieferant_id, grund, erstellt_am, status)
            VALUES
                (:tenant_id, :artikel_id, :artikel_name, :menge, :einheit,
                 :lieferant_id, :grund, :erstellt_am, 'offen')
            RETURNING id::text
        """)
        result = db.execute(stmt, {
            "tenant_id": event.tenant_id,
            "artikel_id": event.artikel_id,
            "artikel_name": event.artikel_name,
            "menge": menge,
            "einheit": event.einheit,
            "lieferant_id": event.lieferant_id,
            "grund": f"Automatisch erstellt: Bestand {event.bestand} < Mindestbestand {event.mindestbestand}",
            "erstellt_am": datetime.utcnow().isoformat(),
        })
        db.commit()
        row = result.fetchone()
        return row[0] if row else None
    except Exception as exc:
        logger.warning("bestellvorschlag_db_error (non-fatal): %s", exc)
        db.rollback()
        return None


async def handle_low_stock_event(event: LowStockEvent, db=None) -> BestellvorschlagResult:
    """Verarbeitet ein Low-Stock-Event und erstellt einen Bestellvorschlag."""
    logger.info(
        "low_stock_event artikel=%s bestand=%.2f mindest=%.2f tenant=%s",
        event.artikel_id, event.bestand, event.mindestbestand, event.tenant_id,
    )

    menge = berechne_empfohlene_menge(event)
    menge = round(menge, 2)

    vorschlag_id = None
    if db is not None:
        vorschlag_id = await _create_bestellvorschlag_db(event, menge, db)

    begruendung = (
        f"Bestand {event.bestand:.2f} {event.einheit} liegt unter Mindestbestand "
        f"{event.mindestbestand:.2f} {event.einheit}. "
        f"EOQ-Bestellmenge: {menge:.2f} {event.einheit}."
    )

    logger.info(
        "bestellvorschlag_erstellt artikel=%s menge=%.2f id=%s",
        event.artikel_id, menge, vorschlag_id,
    )

    return BestellvorschlagResult(
        vorschlag_id=vorschlag_id,
        artikel_id=event.artikel_id,
        empfohlene_menge=menge,
        begruendung=begruendung,
        erfolg=True,
    )


async def run_nats_subscriber() -> None:
    """NATS JetStream Subscriber — lauscht auf erp.lager.bestand_unterschritten."""
    try:
        import nats  # type: ignore[import-untyped]
    except ImportError:
        logger.error("nats-py nicht installiert — pip install nats-py")
        return

    from app.core.database import get_db

    nc = await nats.connect(NATS_URL)
    js = nc.jetstream()

    try:
        await js.add_stream(name="erp_lager", subjects=["erp.lager.*"])
    except Exception:
        pass  # Stream exists

    sub = await js.subscribe("erp.lager.bestand_unterschritten", durable="low_stock_agent")
    logger.info("low_stock_agent gestartet — wartet auf erp.lager.bestand_unterschritten")

    async for msg in sub.messages:
        try:
            payload: Dict[str, Any] = json.loads(msg.data.decode())
            event = LowStockEvent(
                tenant_id=payload.get("tenant_id", "default"),
                artikel_id=payload.get("artikel_id", ""),
                artikel_name=payload.get("artikel_name", ""),
                bestand=float(payload.get("bestand", 0)),
                mindestbestand=float(payload.get("mindestbestand", 0)),
                einheit=payload.get("einheit", "Stk"),
                lieferant_id=payload.get("lieferant_id"),
                durchschnittlicher_verbrauch_pro_tag=payload.get("verbrauch_pro_tag"),
            )
            db = next(get_db())
            try:
                await handle_low_stock_event(event, db)
            finally:
                db.close()
            await msg.ack()
        except Exception as exc:
            logger.exception("low_stock_event_fehler: %s", exc)
            await msg.nak()


async def run_batch_scan(tenant_id: str = "default") -> list[BestellvorschlagResult]:
    """Batch-Scan: prüft alle Artikel eines Mandanten auf Unterdeckung."""
    try:
        from app.core.database import get_db
        from sqlalchemy import text

        db = next(get_db())
        try:
            rows = db.execute(text("""
                SELECT
                    la.artikel_id::text,
                    a.name AS artikel_name,
                    la.menge AS bestand,
                    la.mindestbestand,
                    la.einheit,
                    la.lieferant_id::text
                FROM domain_lager.lager_artikel la
                JOIN domain_shared.artikel a ON a.id = la.artikel_id
                WHERE la.tenant_id = :tenant_id
                  AND la.menge < la.mindestbestand
                  AND la.mindestbestand > 0
                LIMIT 200
            """), {"tenant_id": tenant_id}).fetchall()
        finally:
            db.close()
    except Exception as exc:
        logger.warning("batch_scan_db_error (non-fatal): %s", exc)
        rows = []

    results = []
    for row in rows:
        event = LowStockEvent(
            tenant_id=tenant_id,
            artikel_id=str(row[0]),
            artikel_name=str(row[1]),
            bestand=float(row[2]),
            mindestbestand=float(row[3]),
            einheit=str(row[4]) if row[4] else "Stk",
            lieferant_id=str(row[5]) if row[5] else None,
        )
        result = await handle_low_stock_event(event)
        results.append(result)

    logger.info("batch_scan_abgeschlossen vorschlaege=%d tenant=%s", len(results), tenant_id)
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if AGENT_ENABLED:
        asyncio.run(run_nats_subscriber())
    else:
        logger.info("LOW_STOCK_AGENT_ENABLED nicht gesetzt — einmaliger Batch-Scan")
        asyncio.run(run_batch_scan())
