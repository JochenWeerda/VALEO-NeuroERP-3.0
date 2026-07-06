"""HRM-ABWESENHEIT-ANTRAG-001 — Unit Tests fuer HrmAbwesenheitService."""
from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from main import app
from app.services.hrm_abwesenheit_service import (
    AbwesenheitKonfliktError,
    AbwesenheitStatus,
    AbwesenheitTyp,
    AntragNichtGefundenError,
    HrmAbwesenheitService,
    UngueltigerStatusUebergangError,
    _svc_cache,
)


_client = TestClient(app, raise_server_exceptions=False)
_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}


@pytest.fixture(autouse=True)
def clear_abwesenheit_cache():
    _svc_cache.clear()
    yield
    _svc_cache.clear()


@pytest.fixture()
def svc() -> HrmAbwesenheitService:
    s = HrmAbwesenheitService(tenant_id="test")
    s.reset()
    return s


def _antrag(svc: HrmAbwesenheitService, *, von: str = "2026-07-01", bis: str = "2026-07-05"):
    return svc.antrag_stellen(
        mitarbeiter_nr="MA-001",
        typ=AbwesenheitTyp.URLAUB,
        von_datum=date.fromisoformat(von),
        bis_datum=date.fromisoformat(bis),
        beantragt_von="MA-001",
    )


class TestAntragStellen:
    def test_erstellt_antrag_mit_status_beantragt(self, svc):
        a = _antrag(svc)
        assert a.status == AbwesenheitStatus.BEANTRAGT
        assert a.antrag_id

    def test_arbeitstage_werden_berechnet(self, svc):
        # Mo 2026-07-06 bis Fr 2026-07-10 = 5 Werktage
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-001",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 6),
            bis_datum=date(2026, 7, 10),
            beantragt_von="MA-001",
        )
        assert a.arbeitstage == 5

    def test_wochenende_wird_nicht_gezaehlt(self, svc):
        # Sa-So = 0 Werktage
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-002",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 4),  # Samstag
            bis_datum=date(2026, 7, 5),  # Sonntag
            beantragt_von="MA-002",
        )
        assert a.arbeitstage == 0

    def test_bis_vor_von_raises(self, svc):
        with pytest.raises(ValueError):
            svc.antrag_stellen(
                mitarbeiter_nr="MA-001",
                typ=AbwesenheitTyp.URLAUB,
                von_datum=date(2026, 7, 10),
                bis_datum=date(2026, 7, 5),
                beantragt_von="MA-001",
            )

    def test_konflikt_mit_bestehendem_antrag_raises(self, svc):
        _antrag(svc, von="2026-07-01", bis="2026-07-05")
        with pytest.raises(AbwesenheitKonfliktError):
            _antrag(svc, von="2026-07-03", bis="2026-07-08")

    def test_kein_konflikt_bei_anderem_mitarbeiter(self, svc):
        _antrag(svc)
        a2 = svc.antrag_stellen(
            mitarbeiter_nr="MA-002",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 1),
            bis_datum=date(2026, 7, 5),
            beantragt_von="MA-002",
        )
        assert a2.status == AbwesenheitStatus.BEANTRAGT

    def test_to_dict_enthaelt_pflichtfelder(self, svc):
        a = _antrag(svc)
        d = a.to_dict()
        for k in ("antrag_id", "mitarbeiter_nr", "typ", "status", "arbeitstage",
                  "von_datum", "bis_datum", "eau_pflicht", "abgeschlossen"):
            assert k in d

    def test_krank_hat_eau_pflicht(self, svc):
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-001",
            typ=AbwesenheitTyp.KRANK,
            von_datum=date(2026, 7, 1),
            bis_datum=date(2026, 7, 3),
            beantragt_von="MA-001",
        )
        assert a.to_dict()["eau_pflicht"] is True

    def test_urlaub_keine_eau_pflicht(self, svc):
        a = _antrag(svc)
        assert a.to_dict()["eau_pflicht"] is False


class TestGenehmigung:
    def test_genehmigen_setzt_status(self, svc):
        a = _antrag(svc)
        g = svc.genehmigen(a.antrag_id, genehmigt_von="HR-LEITER")
        assert g.status == AbwesenheitStatus.GENEHMIGT
        assert g.genehmigt_von == "HR-LEITER"

    def test_doppeltes_genehmigen_raises(self, svc):
        a = _antrag(svc)
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        with pytest.raises(UngueltigerStatusUebergangError):
            svc.genehmigen(a.antrag_id, genehmigt_von="HR")

    def test_ablehnen_setzt_status_und_grund(self, svc):
        a = _antrag(svc)
        ab = svc.ablehnen(a.antrag_id, abgelehnt_von="HR", grund="Kein Vertreter verfuegbar")
        assert ab.status == AbwesenheitStatus.ABGELEHNT
        assert ab.ablehnung_grund == "Kein Vertreter verfuegbar"

    def test_ablehnen_ohne_grund_raises(self, svc):
        a = _antrag(svc)
        with pytest.raises(ValueError):
            svc.ablehnen(a.antrag_id, abgelehnt_von="HR", grund="  ")

    def test_ablehnen_nach_genehmigung_raises(self, svc):
        a = _antrag(svc)
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        with pytest.raises(UngueltigerStatusUebergangError):
            svc.ablehnen(a.antrag_id, abgelehnt_von="HR", grund="Zu spaet")


class TestZurueckziehen:
    def test_zurueckziehen_eigener_antrag(self, svc):
        a = _antrag(svc)
        z = svc.zurueckziehen(a.antrag_id, mitarbeiter_nr="MA-001")
        assert z.status == AbwesenheitStatus.ZURUECKGEZOGEN

    def test_zurueckziehen_fremder_antrag_raises(self, svc):
        a = _antrag(svc)
        with pytest.raises(PermissionError):
            svc.zurueckziehen(a.antrag_id, mitarbeiter_nr="MA-999")

    def test_zurueckziehen_nach_genehmigung_raises(self, svc):
        a = _antrag(svc)
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        with pytest.raises(UngueltigerStatusUebergangError):
            svc.zurueckziehen(a.antrag_id, mitarbeiter_nr="MA-001")


class TestListUndGet:
    def test_not_found_raises(self, svc):
        with pytest.raises(AntragNichtGefundenError):
            svc.get("nicht-vorhanden")

    def test_list_alle(self, svc):
        _antrag(svc, von="2026-07-01", bis="2026-07-05")
        svc.antrag_stellen(
            mitarbeiter_nr="MA-002",
            typ=AbwesenheitTyp.KRANK,
            von_datum=date(2026, 8, 1),
            bis_datum=date(2026, 8, 3),
            beantragt_von="MA-002",
        )
        result = svc.list_antraege()
        assert len(result) == 2

    def test_list_filter_mitarbeiter(self, svc):
        _antrag(svc)
        svc.antrag_stellen(
            mitarbeiter_nr="MA-002",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 8, 1),
            bis_datum=date(2026, 8, 5),
            beantragt_von="MA-002",
        )
        result = svc.list_antraege(mitarbeiter_nr="MA-001")
        assert all(a.mitarbeiter_nr == "MA-001" for a in result)

    def test_list_filter_status(self, svc):
        a = _antrag(svc)
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        result = svc.list_antraege(status=AbwesenheitStatus.GENEHMIGT)
        assert all(a.status == AbwesenheitStatus.GENEHMIGT for a in result)

    def test_tenant_isolation(self, svc):
        _antrag(svc)
        andere = HrmAbwesenheitService(tenant_id="other-tenant")
        assert len(andere.list_antraege()) == 0


class TestUrlaubskonto:
    def test_urlaubskonto_leer(self, svc):
        konto = svc.urlaubskonto("MA-001", 2026)
        assert konto["verbraucht_tage"] == 0
        assert konto["resturlaub_tage"] == 30

    def test_urlaubskonto_mit_genehmigtem_urlaub(self, svc):
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-001",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 6),
            bis_datum=date(2026, 7, 10),
            beantragt_von="MA-001",
        )
        svc.genehmigen(a.antrag_id, genehmigt_von="HR")
        konto = svc.urlaubskonto("MA-001", 2026)
        assert konto["verbraucht_tage"] == 5
        assert konto["resturlaub_tage"] == 25

    def test_abgelehnter_urlaub_zaehlt_nicht(self, svc):
        a = svc.antrag_stellen(
            mitarbeiter_nr="MA-001",
            typ=AbwesenheitTyp.URLAUB,
            von_datum=date(2026, 7, 6),
            bis_datum=date(2026, 7, 10),
            beantragt_von="MA-001",
        )
        svc.ablehnen(a.antrag_id, abgelehnt_von="HR", grund="Kein Vertreter")
        konto = svc.urlaubskonto("MA-001", 2026)
        assert konto["verbraucht_tage"] == 0


def _create_request(*, mitarbeiter: str = "MA-100", von: str = "2026-07-06", bis: str = "2026-07-10", typ: str = "urlaub"):
    return _client.post(
        "/api/v1/personal/abwesenheit/antraege",
        headers=_HEADERS,
        json={
            "mitarbeiter_nr": mitarbeiter,
            "typ": typ,
            "von_datum": von,
            "bis_datum": bis,
            "beantragt_von": mitarbeiter,
            "kommentar": "Sommerurlaub",
            "vertretung_durch": "MA-200",
        },
    )


class TestAbwesenheitEndpoint:
    def test_antrag_stellen_endpoint_created(self):
        resp = _create_request()
        assert resp.status_code == 201
        body = resp.json()
        assert body["mitarbeiter_nr"] == "MA-100"
        assert body["status"] == "beantragt"
        assert body["arbeitstage"] == 5
        assert body["vertretung_durch"] == "MA-200"

    def test_antrag_stellen_conflict_returns_409(self):
        assert _create_request().status_code == 201
        resp = _create_request(von="2026-07-08", bis="2026-07-13")
        assert resp.status_code == 409
        assert "Konflikt" in resp.json()["detail"]

    def test_antrag_stellen_invalid_type_returns_422(self):
        resp = _create_request(typ="gibt-es-nicht")
        assert resp.status_code == 422

    def test_antrag_stellen_invalid_date_range_returns_422(self):
        resp = _create_request(von="2026-07-10", bis="2026-07-06")
        assert resp.status_code == 422

    def test_list_antraege_filters(self):
        first = _create_request(mitarbeiter="MA-100", von="2026-07-06", bis="2026-07-10").json()
        second = _create_request(mitarbeiter="MA-101", typ="krank", von="2026-08-03", bis="2026-08-04").json()
        approve = _client.post(
            f"/api/v1/personal/abwesenheit/antraege/{first['antrag_id']}/genehmigen",
            headers=_HEADERS,
            json={"genehmigt_von": "HR"},
        )
        assert approve.status_code == 200

        by_employee = _client.get("/api/v1/personal/abwesenheit/antraege?mitarbeiter_nr=MA-101", headers=_HEADERS)
        assert by_employee.status_code == 200
        assert [item["antrag_id"] for item in by_employee.json()["items"]] == [second["antrag_id"]]

        by_status = _client.get("/api/v1/personal/abwesenheit/antraege?status=genehmigt", headers=_HEADERS)
        assert by_status.status_code == 200
        assert [item["antrag_id"] for item in by_status.json()["items"]] == [first["antrag_id"]]

        by_type_and_date = _client.get(
            "/api/v1/personal/abwesenheit/antraege?typ=krank&von_ab=2026-08-01",
            headers=_HEADERS,
        )
        assert by_type_and_date.status_code == 200
        assert [item["antrag_id"] for item in by_type_and_date.json()["items"]] == [second["antrag_id"]]

    def test_get_antrag_endpoint_200_and_404(self):
        created = _create_request().json()
        resp = _client.get(f"/api/v1/personal/abwesenheit/antraege/{created['antrag_id']}", headers=_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["antrag_id"] == created["antrag_id"]

        missing = _client.get("/api/v1/personal/abwesenheit/antraege/missing", headers=_HEADERS)
        assert missing.status_code == 404

    def test_genehmigen_endpoint_happy_path_and_status_error(self):
        created = _create_request().json()
        resp = _client.post(
            f"/api/v1/personal/abwesenheit/antraege/{created['antrag_id']}/genehmigen",
            headers=_HEADERS,
            json={"genehmigt_von": "HR", "kommentar": "ok"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "genehmigt"

        again = _client.post(
            f"/api/v1/personal/abwesenheit/antraege/{created['antrag_id']}/genehmigen",
            headers=_HEADERS,
            json={"genehmigt_von": "HR"},
        )
        assert again.status_code == 409

    def test_ablehnen_endpoint_happy_path_and_errors(self):
        created = _create_request().json()
        resp = _client.post(
            f"/api/v1/personal/abwesenheit/antraege/{created['antrag_id']}/ablehnen",
            headers=_HEADERS,
            json={"abgelehnt_von": "HR", "grund": "Vertretung fehlt"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "abgelehnt"

        missing = _client.post(
            "/api/v1/personal/abwesenheit/antraege/missing/ablehnen",
            headers=_HEADERS,
            json={"abgelehnt_von": "HR", "grund": "x"},
        )
        assert missing.status_code == 404

        no_reason = _client.post(
            f"/api/v1/personal/abwesenheit/antraege/{created['antrag_id']}/ablehnen",
            headers=_HEADERS,
            json={"abgelehnt_von": "HR", "grund": " "},
        )
        assert no_reason.status_code == 409

    def test_zurueckziehen_endpoint_happy_path_and_permission_error(self):
        created = _create_request(mitarbeiter="MA-100").json()
        foreign = _client.post(
            f"/api/v1/personal/abwesenheit/antraege/{created['antrag_id']}/zurueckziehen",
            headers=_HEADERS,
            json={"mitarbeiter_nr": "MA-999"},
        )
        assert foreign.status_code == 409

        resp = _client.post(
            f"/api/v1/personal/abwesenheit/antraege/{created['antrag_id']}/zurueckziehen",
            headers=_HEADERS,
            json={"mitarbeiter_nr": "MA-100"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "zurueckgezogen"

    def test_urlaubskonto_endpoint(self):
        created = _create_request().json()
        _client.post(
            f"/api/v1/personal/abwesenheit/antraege/{created['antrag_id']}/genehmigen",
            headers=_HEADERS,
            json={"genehmigt_von": "HR"},
        )
        resp = _client.get("/api/v1/personal/abwesenheit/urlaubskonto/MA-100?jahr=2026", headers=_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["verbraucht_tage"] == 5
        assert resp.json()["resturlaub_tage"] == 25

    def test_missing_tenant_header_returns_400(self):
        resp = _client.get(
            "/api/v1/personal/abwesenheit/antraege",
            headers={"Authorization": "Bearer dev-token"},
        )
        assert resp.status_code in {400, 422}
