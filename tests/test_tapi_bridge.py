"""Unit-Tests für den FRITZ!Box-Callmonitor-Parser der TAPI-Bridge."""

import importlib.util
import pathlib

import pytest

# Bridge liegt außerhalb des app-Pakets (eigenständiges Tool) → direkt laden.
_BRIDGE = pathlib.Path(__file__).resolve().parents[1] / "tools" / "tapi-bridge" / "tapi_bridge.py"
_spec = importlib.util.spec_from_file_location("tapi_bridge", _BRIDGE)
tapi_bridge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tapi_bridge)

parse = tapi_bridge.parse_fritzbox_line

pytestmark = pytest.mark.unit


def test_ring_eingehend_wird_geparst():
    line = "17.06.26 09:15:03;RING;0;049417360;026912345;SIP0;"
    evt = parse(line)
    assert evt == {"caller": "049417360", "called": "026912345", "conn_id": "0"}


def test_ausgehender_call_wird_ignoriert():
    line = "17.06.26 09:16:00;CALL;1;10;026912345;049417360;SIP0;"
    assert parse(line) is None


def test_connect_und_disconnect_ignoriert():
    assert parse("17.06.26 09:15:10;CONNECT;0;10;049417360;") is None
    assert parse("17.06.26 09:20:00;DISCONNECT;0;120;") is None


def test_anonymer_anrufer():
    evt = parse("17.06.26 09:15:03;RING;2;;026912345;SIP0;")
    assert evt is not None
    assert evt["caller"] == "anonym"
    assert evt["called"] == "026912345"


def test_unvollstaendige_zeile_ist_none():
    assert parse("") is None
    assert parse("nur;zwei") is None
    assert parse("17.06.26;RING;0") is None


def test_called_leer_wird_none():
    evt = parse("17.06.26 09:15:03;RING;5;049417360;;SIP0;")
    assert evt["called"] is None


# ── API-Vertrag: /pending-Endpoints liefern Listen ───────────────────────────
# Regression: response_model war faelschlich dict[str, Any], obwohl die Handler
# eine Liste zurueckgeben -> FastAPI ResponseValidationError (HTTP 500) bei jeder
# Antwort (auch der leeren Liste). Der Poller im Frontend feuert auf jeder Seite,
# daher trat der 500er global auf.
def _list_routes():
    from typing import get_args, get_origin

    from app.api.v1.endpoints import tapi as tapi_endpoints

    return tapi_endpoints.router.routes, get_origin, get_args


def test_pending_endpoint_response_model_is_list():
    routes, get_origin, _ = _list_routes()
    pending = [r for r in routes if getattr(r, "path", "").endswith("/tapi/pending")]
    assert pending, "pending-Route nicht gefunden"
    assert get_origin(pending[0].response_model) is list


def test_dial_pending_endpoint_response_model_is_list():
    routes, get_origin, _ = _list_routes()
    dial = [r for r in routes if getattr(r, "path", "").endswith("/tapi/dial/pending")]
    assert dial, "dial/pending-Route nicht gefunden"
    assert get_origin(dial[0].response_model) is list
