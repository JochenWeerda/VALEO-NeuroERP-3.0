"""COV-RATCHET-007 — Unit Tests fuer WfCockpitNatsProjector.

Alle Tests laufen ohne echte NATS-Verbindung (MagicMock fuer persist_service).
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.wf_cockpit_nats_projector import WfCockpitNatsProjector, _map_event_kind


def _projector() -> tuple[WfCockpitNatsProjector, MagicMock]:
    svc = MagicMock()
    svc.upsert_from_event = AsyncMock()
    svc.append_event = AsyncMock()
    return WfCockpitNatsProjector(persist_service=svc), svc


def _msg(subject: str, data: dict) -> MagicMock:
    msg = MagicMock()
    msg.subject = subject
    msg.data = json.dumps(data).encode()
    return msg


class TestMapEventKind:
    def test_known_types(self):
        assert _map_event_kind("created") == "created"
        assert _map_event_kind("status_changed") == "status_changed"
        assert _map_event_kind("blocker_added") == "external_gate"
        assert _map_event_kind("blocker_resolved") == "domain_event"
        assert _map_event_kind("completed") == "status_changed"
        assert _map_event_kind("failed") == "status_changed"
        assert _map_event_kind("retry_requested") == "retry_requested"

    def test_unknown_type_falls_back_to_domain_event(self):
        assert _map_event_kind("something_unknown") == "domain_event"
        assert _map_event_kind("") == "domain_event"


class TestHandleWorkflow:
    @pytest.mark.asyncio
    async def test_routes_created_event(self):
        projector, svc = _projector()
        msg = _msg(
            "workflow.O2C.created",
            {
                "tenant_id": "t-1",
                "process_instance_id": "pid-1",
                "status": "running",
                "correlation_id": "corr-1",
            },
        )
        await projector._handle_workflow(msg)
        svc.upsert_from_event.assert_awaited_once()
        call_kwargs = svc.upsert_from_event.call_args.kwargs
        assert call_kwargs["process_key"] == "O2C"
        assert call_kwargs["event_kind"] == "created"
        assert call_kwargs["tenant_id"] == "t-1"
        assert call_kwargs["process_instance_id"] == "pid-1"

    @pytest.mark.asyncio
    async def test_ignores_event_without_instance_id(self):
        projector, svc = _projector()
        msg = _msg("workflow.O2C.created", {"tenant_id": "t-1", "status": "running"})
        await projector._handle_workflow(msg)
        svc.upsert_from_event.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_blocker_added_maps_to_external_gate(self):
        projector, svc = _projector()
        msg = _msg(
            "workflow.CON.blocker_added",
            {"tenant_id": "t-2", "process_instance_id": "pid-2", "status": "blocked"},
        )
        await projector._handle_workflow(msg)
        call_kwargs = svc.upsert_from_event.call_args.kwargs
        assert call_kwargs["event_kind"] == "external_gate"

    @pytest.mark.asyncio
    async def test_falls_back_to_correlation_id_when_missing(self):
        projector, svc = _projector()
        msg = _msg(
            "workflow.O2C.status_changed",
            {"tenant_id": "t-3", "process_instance_id": "pid-3", "status": "completed"},
        )
        await projector._handle_workflow(msg)
        call_kwargs = svc.upsert_from_event.call_args.kwargs
        assert call_kwargs["correlation_id"] == "pid-3"

    @pytest.mark.asyncio
    async def test_swallows_exception_without_raising(self):
        projector, svc = _projector()
        svc.upsert_from_event.side_effect = RuntimeError("db error")
        msg = _msg(
            "workflow.O2C.created",
            {"tenant_id": "t-1", "process_instance_id": "pid-1", "status": "running"},
        )
        await projector._handle_workflow(msg)  # must not raise


class TestHandleDomain:
    @pytest.mark.asyncio
    async def test_routes_domain_event_with_instance_id(self):
        projector, svc = _projector()
        msg = _msg(
            "domain.inventory.stock_movement",
            {"tenant_id": "t-5", "process_instance_id": "pid-5", "qty": 100},
        )
        await projector._handle_domain(msg)
        svc.append_event.assert_awaited_once()
        call_kwargs = svc.append_event.call_args.kwargs
        assert call_kwargs["kind"] == "domain_event"
        assert call_kwargs["process_instance_id"] == "pid-5"

    @pytest.mark.asyncio
    async def test_ignores_domain_event_without_instance_id(self):
        projector, svc = _projector()
        msg = _msg("domain.inventory.stock_movement", {"tenant_id": "t-6", "qty": 100})
        await projector._handle_domain(msg)
        svc.append_event.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_accepts_workflow_instance_id_key(self):
        projector, svc = _projector()
        msg = _msg(
            "domain.crm.contact_updated",
            {"tenant_id": "t-7", "workflow_instance_id": "wid-7"},
        )
        await projector._handle_domain(msg)
        call_kwargs = svc.append_event.call_args.kwargs
        assert call_kwargs["process_instance_id"] == "wid-7"

    @pytest.mark.asyncio
    async def test_swallows_exception_without_raising(self):
        projector, svc = _projector()
        svc.append_event.side_effect = RuntimeError("db error")
        msg = _msg(
            "domain.crm.contact_updated",
            {"tenant_id": "t-8", "process_instance_id": "pid-8"},
        )
        await projector._handle_domain(msg)  # must not raise


class TestStartStop:
    @pytest.mark.asyncio
    async def test_start_noop_when_nats_unavailable(self):
        projector, _ = _projector()
        with patch("app.services.wf_cockpit_nats_projector._NATS_AVAILABLE", False):
            await projector.start("nats://localhost:4222")
        assert not projector._running

    @pytest.mark.asyncio
    async def test_stop_noop_when_no_connection(self):
        projector, _ = _projector()
        await projector.stop()
        assert not projector._running
