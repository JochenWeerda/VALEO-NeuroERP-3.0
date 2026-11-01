"""
COV-INV-002: Tests for Waage API endpoints.

Covers /api/v1/waage — Waagen CRUD + Wiegungen CRUD.

Unit-Tests (kein DB) für Helper + alle Endpoint-Pfade via Repo-Mocks.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.waage import _serialize_value, _to_list, router as waage_router
from app.core.database import get_db
from app.auth.tenant import get_verified_tenant_id
from testgrenze import ALLE_FACHROLLEN, ersetze_nutzer

_NOW = datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Repo fakes
# ---------------------------------------------------------------------------

def _fw(wid: str = "W-1", status: str = "aktiv") -> MagicMock:
    w = MagicMock()
    w.id = wid
    w.standort = "Halle A"
    w.typ = "LKW"
    w.max_kapazitaet = 50.0
    w.status = status
    w.created_at = _NOW
    w.updated_at = _NOW
    return w


def _fwg(wgid: str = "WG-1") -> MagicMock:
    w = MagicMock()
    w.id = wgid
    w.kennzeichen = "HB-1"
    w.artikel = "Mais"
    w.brutto = 30.0
    w.tara = 10.0
    w.netto = 20.0
    w.created_at = _NOW
    return w


class _WaageRepo:
    def __init__(self, items=None):
        self._items = list(items or [])

    def get_all(self, tenant_id, skip=0, limit=100):
        return self._items[skip: skip + limit]

    def get_by_status(self, tenant_id, status, skip=0, limit=100):
        return [i for i in self._items if i.status == status][skip:skip + limit]

    def get_by_id(self, tenant_id, eid):
        return next((i for i in self._items if i.id == eid), None)

    def create(self, tenant_id, data):
        if data.get("_raise"):
            raise ValueError("boom")
        return _fw("W-new")

    def update(self, tenant_id, eid, data):
        return next((i for i in self._items if i.id == eid), None)

    def delete(self, tenant_id, eid):
        return any(i.id == eid for i in self._items)


class _WiegungRepo:
    def __init__(self, items=None):
        self._items = list(items or [])
        self.last_data: dict = {}

    def get_all(self, skip=0, limit=100):
        return self._items

    def get_by_waage(self, _wid):
        return []

    def get_by_kennzeichen(self, kz):
        return [i for i in self._items if i.kennzeichen == kz]

    def get_by_id(self, eid):
        return next((i for i in self._items if i.id == eid), None)

    def create(self, data):
        self.last_data = dict(data)
        w = _fwg("WG-new")
        w.netto = data.get("netto", data.get("brutto", 0) - data.get("tara", 0))
        return w

    def delete(self, eid):
        return any(i.id == eid for i in self._items)


from unittest.mock import patch as _mock_patch
import contextlib


_WAAGE_ATTRS = ("id", "standort", "typ", "max_kapazitaet", "status", "created_at", "updated_at")
_WIEGUNG_ATTRS = ("id", "kennzeichen", "artikel", "brutto", "tara", "netto", "created_at")


def _mock_to_dict(model):
    """Replacement for _to_dict that works with MagicMock (no sa_inspect)."""
    if model is None:
        return {}
    attrs = _WIEGUNG_ATTRS if hasattr(model, "kennzeichen") else _WAAGE_ATTRS
    return {a: _serialize_value(getattr(model, a, None)) for a in attrs}


@contextlib.contextmanager
def _client_ctx(waagen=None, wiegungen=None, prefix=""):
    """Context manager that keeps repo patches alive for the lifetime of the client."""
    wr = _WaageRepo(waagen)
    wgr = _WiegungRepo(wiegungen)
    with _mock_patch("app.api.v1.endpoints.waage.WaageRepository", lambda db: wr), \
         _mock_patch("app.api.v1.endpoints.waage.WiegungRepository", lambda db: wgr, create=True), \
         _mock_patch("app.api.v1.endpoints.waage._to_dict", _mock_to_dict):
        _app = FastAPI()
        _app.include_router(waage_router, prefix=prefix)
        ersetze_nutzer(_app, *ALLE_FACHROLLEN)  # Schreibwege pruefen die Bereichsrolle (19.10.2026)
        _app.dependency_overrides[get_db] = lambda: MagicMock()
        _app.dependency_overrides[get_verified_tenant_id] = lambda: "test-tenant"
        yield TestClient(_app), wgr


def _client(waagen=None, wiegungen=None):
    """Returns (client, wgr) with patches already entered (used inside `with` blocks in tests)."""
    wr = _WaageRepo(waagen)
    wgr = _WiegungRepo(wiegungen)
    patcher_w = _mock_patch("app.api.v1.endpoints.waage.WaageRepository", lambda db: wr)
    patcher_wg = _mock_patch("app.api.v1.endpoints.waage.WiegungRepository", lambda db: wgr, create=True)
    patcher_w.start()
    patcher_wg.start()
    _app = FastAPI()
    _app.include_router(waage_router)
    ersetze_nutzer(_app, *ALLE_FACHROLLEN)  # Schreibwege pruefen die Bereichsrolle (19.10.2026)
    _app.dependency_overrides[get_db] = lambda: MagicMock()
    _app.dependency_overrides[get_verified_tenant_id] = lambda: "test-tenant"
    c = TestClient(_app)
    # Stop after client creation so patches stay active through requests made on c
    # (TestClient is synchronous — requests happen when .get/.post is called, not here)
    # We need patches to stay active, so we DON'T stop them. Tests must call
    # patcher_w.stop() / patcher_wg.stop() — handled via _client_ctx in unit tests.
    # For backward compat: store stoppers on the client object.
    c._stop_patches = lambda: (patcher_w.stop(), patcher_wg.stop())
    return c, wgr

client = None


@pytest.fixture(autouse=True)
def _explicit_prefixed_transport(request, monkeypatch):
    """HTTP contracts use an explicit mini-app; persistence is tested with rollback.

    These old dev-token tests previously wrote to whichever database app.main
    selected. The dedicated PostgreSQL contract now owns real SQL verification.
    """
    classes = {'TestWaagenList', 'TestWaagenCRUD', 'TestWiegungenList', 'TestWiegungenCRUD'}
    if request.cls and request.cls.__name__ in classes:
        import sys
        with _client_ctx(prefix='/api/v1') as (transport, _):
            monkeypatch.setattr(sys.modules[__name__], 'client', transport)
            yield
    else:
        yield
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


# ── Waagen ──────────────────────────────────────────────────────


class TestWaagenList:
    """GET /waage/waagen"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/waage/waagen", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_with_pagination(self):
        r = client.get("/api/v1/waage/waagen?skip=0&limit=5", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_filter_by_status(self):
        r = client.get("/api/v1/waage/waagen?status=aktiv", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestWaagenCRUD:
    """POST/GET/PATCH/DELETE /waage/waagen"""

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/waage/waagen/NONEXISTENT-WAAGE", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_create_waage(self):
        payload = {
            "id": "WAAGE-TEST-001",
            "waage_name": "Testwaage COV-INV-002",
            "standort": "Hauptlager",
            "status": "aktiv",
            "max_kapazitaet": 60000,
        }
        r = client.post("/api/v1/waage/waagen", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        assert r.status_code == 422  # identity and unknown body fields are rejected

    def test_patch_nonexistent_404(self):
        r = client.patch(
            "/api/v1/waage/waagen/NONEXISTENT-WAAGE",
            headers=AUTH,
            json={"status": "inaktiv"},
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_nonexistent_404(self):
        r = client.delete("/api/v1/waage/waagen/NONEXISTENT-WAAGE", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


# ── Wiegungen ───────────────────────────────────────────────────


class TestWiegungenList:
    """GET /waage/wiegungen"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/waage/wiegungen", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 410
        assert "abgeloest" in r.json()["detail"]

    def test_list_with_pagination(self):
        r = client.get("/api/v1/waage/wiegungen?skip=0&limit=10", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 410

    def test_list_filter_by_waage_id(self):
        r = client.get("/api/v1/waage/wiegungen?waage_id=WAAGE-001", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 410

    def test_list_filter_by_kennzeichen(self):
        r = client.get("/api/v1/waage/wiegungen?kennzeichen=AB-CD-1234", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 410


class TestWiegungenCRUD:
    """POST/GET/DELETE /waage/wiegungen"""

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/waage/wiegungen/NONEXISTENT-WIEGUNG", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 410

    def test_create_wiegung(self):
        payload = {
            "id": "WIEG-TEST-001",
            "waage_id": "WAAGE-001",
            "kennzeichen": "AB-CD-1234",
            "brutto": 25000,
            "tara": 12000,
        }
        r = client.post("/api/v1/waage/wiegungen", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        assert r.status_code == 410

    def test_delete_nonexistent_404(self):
        r = client.delete("/api/v1/waage/wiegungen/NONEXISTENT-WIEGUNG", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 410


# ---------------------------------------------------------------------------
# Helper unit tests (kein DB)
# ---------------------------------------------------------------------------

class TestSerializeValue:
    def test_datetime(self):
        assert "2026-05-05" in _serialize_value(_NOW)

    def test_decimal(self):
        assert _serialize_value(Decimal("3.14")) == pytest.approx(3.14)

    def test_string(self):
        assert _serialize_value("hello") == "hello"

    def test_none(self):
        assert _serialize_value(None) is None

    def test_int(self):
        assert _serialize_value(7) == 7


class TestToList:
    def test_empty(self):
        assert _to_list([]) == []


# ---------------------------------------------------------------------------
# Waage Unit-Tests via Repo-Mock
# ---------------------------------------------------------------------------

class TestWaagenUnit:
    def test_list_empty(self):
        with _client_ctx() as (c, _):
            assert c.get("/waage/waagen").status_code == 200
            assert c.get("/waage/waagen").json() == []

    def test_list_status_filter(self):
        with _client_ctx(waagen=[_fw("W-1", "aktiv"), _fw("W-2", "inaktiv")]) as (c, _):
            assert c.get("/waage/waagen?status=aktiv").status_code == 200

    def test_get_not_found(self):
        with _client_ctx() as (c, _):
            assert c.get("/waage/waagen/W-miss").status_code == 404

    def test_get_found(self):
        with _client_ctx(waagen=[_fw("W-1")]) as (c, _):
            assert c.get("/waage/waagen/W-1").status_code == 200

    def test_create_ok(self):
        with _client_ctx() as (c, _):
            assert c.post("/waage/waagen", json={"standort": "A", "typ": "LKW", "max_kapazitaet": 10}).status_code == 201

    def test_create_invalid_payload_422(self):
        with _client_ctx() as (c, _):
            assert c.post("/waage/waagen", json={"_raise": True}).status_code == 422

    def test_update_not_found(self):
        with _client_ctx() as (c, _):
            assert c.patch("/waage/waagen/W-miss", json={"standort": "X"}).status_code == 404

    def test_update_found(self):
        with _client_ctx(waagen=[_fw("W-1")]) as (c, _):
            assert c.patch("/waage/waagen/W-1", json={"standort": "X"}).status_code == 200

    def test_delete_not_found(self):
        with _client_ctx() as (c, _):
            assert c.delete("/waage/waagen/W-miss").status_code == 404

    def test_delete_found(self):
        with _client_ctx(waagen=[_fw("W-1")]) as (c, _):
            assert c.delete("/waage/waagen/W-1").status_code == 204


class TestWiegungenUnit:
    @pytest.mark.parametrize('method,path,body', [
        ('get', '/waage/wiegungen', None), ('get', '/waage/wiegungen/WG-1', None),
        ('post', '/waage/wiegungen', {'kennzeichen': 'HB-1', 'brutto': 30, 'tara': 10}),
        ('delete', '/waage/wiegungen/WG-1', None)])
    def test_legacy_source_retired_without_mutation(self, method, path, body):
        with _client_ctx() as (client, repository):
            result = client.request(method, path, json=body)
            assert result.status_code == 410
            assert repository.last_data == {}


class TestWaageLiveUnit:
    def test_partiepflicht_config_and_check_fallbacks(self):
        from app.api.v1.endpoints.waage import (
            PartiepflichtCheckRequest,
            check_partiepflicht,
            get_partiepflicht_config,
        )

        db = MagicMock()
        db.execute.side_effect = Exception("no metadata")
        cfg = asyncio.run(get_partiepflicht_config(db=db))
        assert cfg["config_source"] == "default"

        invalid = asyncio.run(
            check_partiepflicht(
                payload=PartiepflichtCheckRequest(artikel_id="A1", wiegetyp="ROHWARE"),
                db=db,
            )
        )
        assert invalid["valid"] is False
        valid = asyncio.run(
            check_partiepflicht(
                payload=PartiepflichtCheckRequest(artikel_id="A1", wiegetyp="SONST", partie_id="P1"),
                db=db,
            )
        )
        assert valid["valid"] is True

    def test_parse_ascii_lines_and_import_error_queue(self):
        from app.services.waage_import_service import parse_record, split_records
        raw = "W;WG1;2026-01-01;08:00;1000;400;600;HB1;L1;;S1;P1;SILO;14.5;78;1.2;X"
        record = parse_record(split_records(raw + "\nQ;WG1;Protein;11.5;%")[0])
        assert record['net_weight'] == 600
        assert record['quality_data']['additional'][0]['parameter'] == 'Protein'


    def test_fehlerqueue_retry_delete_and_404(self):
        from app.services import waage_import_service as service
        from fastapi import HTTPException
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as denied:
            service.queue_entry(db, 'tenant-a', 'foreign-entry')
        assert denied.value.status_code == 404
        db.commit.assert_not_called()


    def test_kalibrierung_status_get_update_paths(self):
        from types import SimpleNamespace
        from app.api.v1.endpoints import waage
        scale = SimpleNamespace(id='own', letzte_eichung=_NOW, naechste_eichung=_NOW, eichamt='Amt', zertifikat_nr='Z')
        with _mock_patch.object(waage, 'WaageRepository') as repo:
            repo.return_value.get_by_id.return_value = scale
            result = asyncio.run(waage.get_kalibrierung('own', db=MagicMock(), tenant_id='t-1'))
        assert result['letztes_eichdatum'] == '2026-05-05'
        assert result['eichamt'] == 'Amt'


    def test_dual_wiegung_schreibt_den_kanonischen_schein(self):
        """Vorher prueffte dieser Test den JSONB-Rueckfall als Erfolgsfall.

        Schlug der erste INSERT fehl, schrieb der Weg die ganze Wiegung als
        undurchsichtigen Klumpen in ``extended_data`` — ohne Gewicht, ohne Waage
        — und antwortete ``201 created``. Ein Wiegeschein ohne Gewicht in einer
        Spalte ist nicht abrechenbar und nicht pruefbar. Der Rueckfall ist weg.
        """
        import asyncio
        from app.api.v1.endpoints.waage import (
            WiegungErweitert,
            WiegescheinMitDoppelwiegung,
            create_dual_wiegung,
        )

        db = MagicMock()
        db.execute.return_value.scalar.side_effect = [2026, 41]
        payload = WiegescheinMitDoppelwiegung(
            waage_id="WA-1",
            wiegung_erweitert=WiegungErweitert(waage_id="WA-1", brutto_kg=1000, tara_kg=400, gosse=2),
            kfz_kennzeichen="HB-1",
        )
        created = asyncio.run(
            create_dual_wiegung(payload=payload, tenant_id="t-1", db=db)
        )
        assert created["netto_kg"] == pytest.approx(600)
        assert created["brutto_kg"] == pytest.approx(1000)
        assert created["tara_kg"] == pytest.approx(400)
        assert created["gosse"] == 2
        assert created["ticket_number"] == "WS-2026-000042"
        # Keine zweite Schreibrunde als Rueckfall, und geschrieben wird das
        # kanonische Rueckgrat. ``TextClause`` druckt sich nicht aus, also wird
        # der SQL-Text selbst gelesen.
        anweisungen = " ".join(
            str(aufruf.args[0]) for aufruf in db.execute.call_args_list if aufruf.args
        )
        assert "extended_data" not in anweisungen
        assert "domain_inventory.weighing_tickets" in anweisungen
        assert "domain_agrar.wiegungen" not in anweisungen

    def test_import_ascii_success_quality_and_strict_parse_error(self):
        from fastapi import HTTPException
        from app.services.waage_import_service import parse_record, split_records
        good = "W;WG1;2026-01-01;08:00;1000;400;600;HB1;L1;;S1;P1;SILO;14.5;78;1.2;X"
        assert parse_record(good)['net_weight'] == 600
        with pytest.raises((ValueError, HTTPException)):
            parse_record(good.replace(';600;', ';999;'))
        with pytest.raises(HTTPException):
            split_records(good + '\n' + good)


    def test_kalibrierung_update_db_error_and_extended_errors(self):
        import asyncio
        from fastapi import HTTPException
        from app.api.v1.endpoints import waage

        db_update_error = MagicMock()
        db_update_error.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc:
            asyncio.run(waage.update_kalibrierung('foreign', waage.WaageCalibrationUpdate(eichamt='Amt'), db=db_update_error, tenant_id='t-1', user={'sub': 'user'}))
        assert exc.value.status_code == 404
        db_update_error.commit.assert_not_called()

        db_extended_missing = MagicMock()
        db_extended_missing.execute.return_value.mappings.return_value.first.return_value = None
        with pytest.raises(HTTPException) as missing:
            asyncio.run(waage.get_wiegung_extended("missing", tenant_id="t-1", db=db_extended_missing))
        assert missing.value.status_code == 404

        db_extended_error = MagicMock()
        db_extended_error.execute.side_effect = Exception("relation missing")
        with pytest.raises(HTTPException) as db_exc:
            asyncio.run(waage.get_wiegung_extended("WG-1", tenant_id="t-1", db=db_extended_error))
        assert db_exc.value.status_code == 503

    def test_dual_wiegung_fehlerwege_und_ausgewiesenes_netto(self):
        import asyncio
        from fastapi import HTTPException
        from app.api.v1.endpoints.waage import (
            WiegungErweitert,
            WiegescheinMitDoppelwiegung,
            create_dual_wiegung,
        )

        db = MagicMock()
        db.execute.return_value.scalar.side_effect = [2026, None]
        payload = WiegescheinMitDoppelwiegung(
            wiegung_erweitert=WiegungErweitert(
                waage_id="WA-1", netto_kg=123.0, zielschein_typ="VL", handwiegung=True
            ),
        )
        created = asyncio.run(create_dual_wiegung(payload=payload, tenant_id="t-1", db=db))
        assert created["netto_kg"] == pytest.approx(123.0)
        assert created["richtung"] == "out"
        assert created["handwiegung"] is True

        # Ein Schreibfehler ist ein 503 mit Hinweis — und kein stiller Rueckfall.
        db_bad = MagicMock()
        db_bad.execute.side_effect = Exception("permission denied")
        with pytest.raises(HTTPException) as exc:
            asyncio.run(create_dual_wiegung(payload=payload, tenant_id="t-1", db=db_bad))
        assert exc.value.status_code == 503
        assert "migration_hint" in str(exc.value.detail)
        db_bad.rollback.assert_called()

