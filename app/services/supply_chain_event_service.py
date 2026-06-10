"""Append-only Ketten-Ereignis-Log + kanonischer Übergabestatus (DOM-SUPPLY-004.2).

Revisionsfest: der Service schreibt ausschließlich INSERT (kein UPDATE/DELETE).
Aus den Ereignissen wird der kanonische Lieferketten-Status abgeleitet:

    erfasst → freigegeben → eingelagert → abgerechnet   (storniert überschreibt)

`sync_from_state` erzeugt idempotent (source='backfill') die Ereignisse aus dem
aktuellen Ist-Zustand der Stufen-Tabellen, damit bestehende Lieferungen sofort
einen Status + Zeitstrahl haben. Künftige Stufenübergänge/Korrekturen werden per
`record(...)` angehängt (source='auto'|'manual').
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

# Kanonischer Lebenszyklus + Rang (höher = weiter fortgeschritten).
_STATUS_RANG = {"erfasst": 1, "freigegeben": 2, "eingelagert": 3, "abgerechnet": 4}
# Lifecycle-Event-Typen tragen denselben Namen wie der erreichte Status.
_LIFECYCLE_EVENTS = set(_STATUS_RANG)
_COLS = (
    "id, ticket_id, stage, ref_type, ref_id, ref_label, event_type, status_from, "
    "status_to, menge_kg, abweichung_grund, payload, bediener, source, occurred_at, created_at"
)


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


class SupplyChainEventService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _row(self, r) -> dict:
        d = dict(r)
        d["id"] = str(d["id"])
        for k in ("occurred_at", "created_at"):
            if d.get(k) is not None:
                d[k] = d[k].isoformat()
        if d.get("menge_kg") is not None:
            d["menge_kg"] = _f(d["menge_kg"])
        return d

    # ── Append ────────────────────────────────────────────────────────────────
    def record(
        self,
        *,
        ticket_id: Optional[str],
        stage: str,
        event_type: str,
        ref_type: Optional[str] = None,
        ref_id: Optional[str] = None,
        ref_label: Optional[str] = None,
        status_from: Optional[str] = None,
        status_to: Optional[str] = None,
        menge_kg: Optional[float] = None,
        abweichung_grund: Optional[str] = None,
        payload: Optional[dict] = None,
        bediener: Optional[str] = None,
        source: str = "manual",
        occurred_at: Optional[str] = None,
    ) -> dict:
        import json

        new_id = str(uuid.uuid4())
        self.db.execute(
            text(
                """
                INSERT INTO domain_inventory.supply_chain_events
                    (id, tenant_id, ticket_id, stage, ref_type, ref_id, ref_label,
                     event_type, status_from, status_to, menge_kg, abweichung_grund,
                     payload, bediener, source, occurred_at)
                VALUES
                    (:id, :t, :ticket_id, :stage, :ref_type, :ref_id, :ref_label,
                     :event_type, :status_from, :status_to, :menge_kg, :abweichung_grund,
                     CAST(:payload AS JSONB), :bediener, :source, COALESCE(:occurred_at, now()))
                """
            ),
            {
                "id": new_id, "t": self.tenant_id, "ticket_id": ticket_id, "stage": stage,
                "ref_type": ref_type, "ref_id": ref_id, "ref_label": ref_label,
                "event_type": event_type, "status_from": status_from, "status_to": status_to,
                "menge_kg": menge_kg, "abweichung_grund": abweichung_grund,
                "payload": json.dumps(payload) if payload is not None else None,
                "bediener": bediener, "source": source, "occurred_at": occurred_at,
            },
        )
        self.db.commit()
        r = self.db.execute(
            text(f"SELECT {_COLS} FROM domain_inventory.supply_chain_events WHERE id = :id"),
            {"id": new_id},
        ).mappings().first()
        return self._row(r)

    def _record_backfill(self, **kw) -> None:
        """Idempotenter Backfill-Insert (ON CONFLICT auf partiellem Unique-Index)."""
        import json

        kw.setdefault("ref_type", None)
        self.db.execute(
            text(
                """
                INSERT INTO domain_inventory.supply_chain_events
                    (id, tenant_id, ticket_id, stage, ref_type, ref_id, ref_label,
                     event_type, status_to, menge_kg, payload, source, occurred_at)
                VALUES
                    (:id, :t, :ticket_id, :stage, :ref_type, :ref_id, :ref_label,
                     :event_type, :status_to, :menge_kg, CAST(:payload AS JSONB),
                     'backfill', COALESCE(:occurred_at, now()))
                ON CONFLICT (tenant_id, stage, ref_id, event_type)
                    WHERE source = 'backfill' DO NOTHING
                """
            ),
            {
                "id": str(uuid.uuid4()), "t": self.tenant_id,
                "ticket_id": kw.get("ticket_id"), "stage": kw["stage"],
                "ref_type": kw.get("ref_type"), "ref_id": kw.get("ref_id"),
                "ref_label": kw.get("ref_label"), "event_type": kw["event_type"],
                "status_to": kw.get("status_to"), "menge_kg": kw.get("menge_kg"),
                "payload": json.dumps(kw["payload"]) if kw.get("payload") is not None else None,
                "occurred_at": kw.get("occurred_at"),
            },
        )

    # ── Lesen ─────────────────────────────────────────────────────────────────
    def timeline(self, ticket_id: str) -> list[dict]:
        rows = self.db.execute(
            text(
                f"SELECT {_COLS} FROM domain_inventory.supply_chain_events "
                "WHERE tenant_id = :t AND ticket_id = :tk "
                "ORDER BY CASE stage WHEN 'wiegung' THEN 1 WHEN 'annahme' THEN 2 "
                "WHEN 'lager' THEN 3 WHEN 'abrechnung' THEN 4 ELSE 5 END, occurred_at, created_at"
            ),
            {"t": self.tenant_id, "tk": ticket_id},
        ).mappings().all()
        return [self._row(r) for r in rows]

    def derive_status(self, ticket_id: str) -> dict:
        """Kanonischer Status aus den Ereignissen (höchste erreichte Stufe;
        Storno überschreibt)."""
        rows = self.db.execute(
            text(
                "SELECT event_type FROM domain_inventory.supply_chain_events "
                "WHERE tenant_id = :t AND ticket_id = :tk"
            ),
            {"t": self.tenant_id, "tk": ticket_id},
        ).fetchall()
        types = {r[0] for r in rows}
        if "storniert" in types:
            return {"status": "storniert", "rang": 0}
        best, rang = "offen", 0
        for et in types:
            if et in _STATUS_RANG and _STATUS_RANG[et] > rang:
                best, rang = et, _STATUS_RANG[et]
        return {"status": best, "rang": rang}

    # ── Backfill aus Ist-Zustand ────────────────────────────────────────────────
    def sync_from_state(self, ticket_id: str) -> dict:
        """Erzeugt idempotent die Lifecycle-Ereignisse aus dem aktuellen Ist-Zustand
        der Kette (für vorhandene Lieferungen ohne Ereignis-Historie)."""
        from app.services.supply_chain_trace_service import SupplyChainTraceService

        chain = SupplyChainTraceService(self.db, self.tenant_id).trace(ticket=ticket_id)
        if not chain.get("found"):
            return {"synced": 0, "detail": "Ticket nicht auflösbar."}
        tid = chain["ticket_id"]
        before = len(self.timeline(tid))
        for node in chain.get("kette", []):
            stage = node["stage"]
            if stage == "wiegung":
                self._record_backfill(ticket_id=tid, stage="wiegung", ref_type="weighing_ticket",
                                      ref_id=node["ref_id"], ref_label=node["ref"],
                                      event_type="erfasst", status_to="erfasst",
                                      menge_kg=node.get("menge_kg"), occurred_at=node.get("zeitpunkt"))
            elif stage == "annahme" and node.get("status") == "released":
                self._record_backfill(ticket_id=tid, stage="annahme", ref_type="harvest_acceptance",
                                      ref_id=node["ref_id"], ref_label=node["ref"],
                                      event_type="freigegeben", status_to="freigegeben",
                                      occurred_at=node.get("zeitpunkt"))
            elif stage == "lager" and node.get("status") in ("active", "aktiv"):
                self._record_backfill(ticket_id=tid, stage="lager", ref_type="silo_lot",
                                      ref_id=node["ref_id"], ref_label=node["ref"],
                                      event_type="eingelagert", status_to="eingelagert",
                                      menge_kg=node.get("menge_kg"), occurred_at=node.get("zeitpunkt"))
            elif stage == "abrechnung" and node.get("status") in ("posted", "gebucht"):
                self._record_backfill(ticket_id=tid, stage="abrechnung", ref_type="settlement",
                                      ref_id=node["ref_id"], ref_label=node["ref"],
                                      event_type="abgerechnet", status_to="abgerechnet",
                                      menge_kg=node.get("menge_kg"), occurred_at=node.get("zeitpunkt"))
        # Mengen-Abweichung als Ereignis festhalten (revisionsrelevant).
        for chk in chain.get("mengen_konsistenz", []):
            if chk.get("abweichung"):
                self._record_backfill(
                    ticket_id=tid, stage="kette", ref_type="mengencheck",
                    ref_id=f"{tid}:{chk['von']}->{chk['nach']}",
                    ref_label=f"{chk['von']}→{chk['nach']}", event_type="abweichung",
                    menge_kg=chk.get("differenz_kg"),
                    payload={"differenz_pct": chk.get("differenz_pct"), "hinweis": chk.get("hinweis")},
                )
        self.db.commit()
        after = len(self.timeline(tid))
        return {"synced": after - before, "total": after, "ticket_id": tid}
