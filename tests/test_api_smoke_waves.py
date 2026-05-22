"""API-smoke tests for the accepted Fachliche Vertiefung Wave 1-13 surface.

These tests do not replace DB integration tests. They verify that the routed
FastAPI contracts remain importable, that central Wave 10-13 routes are wired, and
that validation/error paths do not require a running PostgreSQL instance.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient


def _client(router, *, existing_row: bool = False, rowcount: int = 1) -> TestClient:
    app = FastAPI()

    def _db():
        db = MagicMock()
        result = MagicMock()
        result.fetchall.return_value = []
        result.fetchone.return_value = MagicMock() if existing_row else None
        result.rowcount = rowcount
        db.execute.return_value = result
        yield db

    from app.core.database import get_db
    from app.core.dependencies import get_tenant_id

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_tenant_id] = lambda: "test-tenant"
    app.include_router(router)
    return TestClient(app)


def test_wave_routers_import_through_api_module():
    import app.api.v1.api as api

    registered_paths = {route.path for route in api.api_router.routes}
    assert "/stammdaten/warengruppen" in registered_paths
    assert "/fibu/erloeskennziffern" in registered_paths
    assert "/fibu/zahlungsbedingungen" in registered_paths
    assert "/lager/partien" in registered_paths
    assert "/fibu/forderungsgruppen" in registered_paths
    assert "/fibu/periodische-buchungen" in registered_paths
    assert "/preise/zu-abschlaege/gruppen" in registered_paths
    assert "/fibu/stammdaten/zahlungsformulare" in registered_paths


class TestWarengruppenSmoke:
    base = "/stammdaten/warengruppen"

    def test_list_haupt_200(self):
        from app.api.v1.endpoints.warengruppen import router

        response = _client(router).get(f"{self.base}/haupt")
        assert response.status_code == 200
        assert response.json() == []

    def test_duplicate_haupt_returns_409(self):
        from app.api.v1.endpoints.warengruppen import router

        response = _client(router, existing_row=True).post(
            f"{self.base}/haupt",
            json={"gruppe_nr": "G01", "bezeichnung": "Getreide"},
        )
        assert response.status_code == 409

    def test_update_haupt_missing_returns_404(self):
        from app.api.v1.endpoints.warengruppen import router

        response = _client(router, rowcount=0).put(
            f"{self.base}/haupt/G99",
            json={"gruppe_nr": "G99", "bezeichnung": "Neu"},
        )
        assert response.status_code == 404

    def test_delete_haupt_returns_204(self):
        from app.api.v1.endpoints.warengruppen import router

        response = _client(router).delete(f"{self.base}/haupt/G01")
        assert response.status_code == 204


class TestErloeskennziffernSmoke:
    base = "/fibu/erloeskennziffern"

    def test_list_200(self):
        from app.api.v1.endpoints.erloeskennziffern import router

        response = _client(router).get(self.base)
        assert response.status_code == 200

    def test_duplicate_returns_409(self):
        from app.api.v1.endpoints.erloeskennziffern import router

        response = _client(router, existing_row=True).post(
            self.base,
            json={"ekz_nr": "EKZ-01", "bezeichnung": "Standard"},
        )
        assert response.status_code == 409

    def test_lookup_missing_returns_404(self):
        from app.api.v1.endpoints.erloeskennziffern import router

        response = _client(router).get(f"{self.base}/lookup?ekz_nr=NOTEXIST")
        assert response.status_code == 404

    def test_update_missing_returns_404(self):
        from app.api.v1.endpoints.erloeskennziffern import router

        response = _client(router, rowcount=0).put(
            f"{self.base}/EKZ-99",
            json={"ekz_nr": "EKZ-99", "bezeichnung": "Neu"},
        )
        assert response.status_code == 404


class TestZahlungsbedingungenSmoke:
    base = "/fibu/zahlungsbedingungen"

    def test_list_200(self):
        from app.api.v1.endpoints.zahlungsbedingungen import router

        response = _client(router).get(self.base)
        assert response.status_code == 200

    def test_invalid_zahlungsart_returns_422(self):
        from app.api.v1.endpoints.zahlungsbedingungen import router

        response = _client(router).post(
            self.base,
            json={"zabd_nr": "X", "bezeichnung": "Test", "zahlungsart": "invalid"},
        )
        assert response.status_code == 422

    def test_update_missing_returns_404(self):
        from app.api.v1.endpoints.zahlungsbedingungen import router

        response = _client(router, rowcount=0).put(
            f"{self.base}/30T",
            json={"zabd_nr": "30T", "bezeichnung": "30 Tage netto"},
        )
        assert response.status_code == 404

    def test_delete_returns_204(self):
        from app.api.v1.endpoints.zahlungsbedingungen import router

        response = _client(router).delete(f"{self.base}/30T")
        assert response.status_code == 204


class TestWave11Smoke:
    def test_partiestamm_list_200(self):
        from app.api.v1.endpoints.partiestamm import router

        response = _client(router).get("/lager/partien")
        assert response.status_code == 200

    def test_forderungsgruppen_missing_returns_404(self):
        from app.api.v1.endpoints.forderungsgruppen import router

        response = _client(router).get("/fibu/forderungsgruppen/NOTEXIST")
        assert response.status_code == 404

    def test_periodische_buchungen_faellig_200(self):
        from app.api.v1.endpoints.periodische_buchungen import router

        response = _client(router).get("/fibu/periodische-buchungen/faellig")
        assert response.status_code == 200


class TestWave12Smoke:
    def test_zu_abschlaggruppen_list_200(self):
        from app.api.v1.endpoints.zu_abschlaggruppen import router

        response = _client(router).get("/preise/zu-abschlaege/gruppen")
        assert response.status_code == 200

    def test_zu_abschlaggruppen_invalid_richtung_returns_422(self):
        from app.api.v1.endpoints.zu_abschlaggruppen import router

        response = _client(router).post(
            "/preise/zu-abschlaege/gruppen",
            json={"gruppe_nr": "ZAG-X", "bezeichnung": "Test", "richtung": "export"},
        )
        assert response.status_code == 422


class TestWave13Smoke:
    def test_zahlungsformulare_list_200(self):
        from app.api.v1.endpoints.fibu_stammdaten import router

        response = _client(router).get("/fibu/stammdaten/zahlungsformulare")
        assert response.status_code == 200

    def test_zinsgruppen_invalid_method_returns_422(self):
        from app.api.v1.endpoints.fibu_stammdaten import router

        response = _client(router).post(
            "/fibu/stammdaten/zinsgruppen",
            json={"gruppe_nr": "ZG-X", "bezeichnung": "Test", "zinssatz": 5, "zinsmethode": "monatlich"},
        )
        assert response.status_code == 422
