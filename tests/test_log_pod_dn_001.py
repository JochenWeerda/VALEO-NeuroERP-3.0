"""LOG-POD-DN-001 — POD ABGELIEFERT → delivery_notes.status = 'delivered'."""
from __future__ import annotations

from unittest.mock import MagicMock, call

import pytest


TENANT = "00000000-0000-0000-0000-000000000001"
TOUR_ID = "TOUR-001"
STOP_ID = "STOP-001"


class DictMapping(dict):
    """dict subclass that also supports .get() and mapping protocol for SQLAlchemy mock rows."""


def _make_stop_row(dn_ref: str | None = "LS-2026-001") -> DictMapping:
    return DictMapping({
        "id": STOP_ID,
        "tour_id": TOUR_ID,
        "delivery_note_ref": dn_ref,
        "status": "ABGELIEFERT",
        "pod_data": {},
    })


class TestLogPodDnBelegbruch:
    def _call_save_pod(self, db, dn_ref: str | None = "LS-2026-001"):
        from app.api.v1.endpoints.logistics_tours import save_pod

        body = MagicMock()
        body.model_dump.return_value = {"signature": "ok"}

        stop_row = _make_stop_row(dn_ref)
        mappings_mock = MagicMock()
        mappings_mock.first.return_value = stop_row
        execute_result = MagicMock()
        execute_result.mappings.return_value = mappings_mock
        db.execute.return_value = execute_result

        return save_pod(
            tour_id=TOUR_ID,
            stop_id=STOP_ID,
            body=body,
            x_tenant_id=TENANT,
            db=db,
        )

    def test_lieferschein_wird_auf_delivered_gesetzt(self):
        """Wenn Stopp delivery_note_ref hat → delivery_notes UPDATE ausgeführt."""
        db = MagicMock()
        self._call_save_pod(db, dn_ref="LS-2026-001")

        all_sqls = [str(c.args[0]) for c in db.execute.call_args_list]
        dn_updates = [s for s in all_sqls if "delivery_notes" in s and "delivered" in s]
        assert len(dn_updates) > 0, "delivery_notes UPDATE wurde nicht ausgeführt"

    def test_kein_update_ohne_delivery_note_ref(self):
        """Wenn Stopp kein delivery_note_ref hat → kein delivery_notes UPDATE."""
        db = MagicMock()
        self._call_save_pod(db, dn_ref=None)

        all_sqls = [str(c.args[0]) for c in db.execute.call_args_list]
        dn_updates = [s for s in all_sqls if "delivery_notes" in s and "delivered" in s]
        assert len(dn_updates) == 0
