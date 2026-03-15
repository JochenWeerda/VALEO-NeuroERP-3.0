"""
Wave-38 Contract Tests: Nachhaltigkeit/CO2-Reporting + Branchenbenchmarking
Gap 046 (sustainability_reporting) + Gap 047 (benchmark_cockpit)

60 Tests total:
  TestEmissionsPositionDataclass       4
  TestCO2BilanzProperties              5
  TestESGKennzahlZielerreichung        5
  TestESGBerichtScore                  4
  TestTransportCO2Berechnung           5
  TestEnergieCO2Berechnung             4
  TestBeispielDaten                    3
  TestBenchmarkKennzahlPerzentil       6
  TestBenchmarkTrend                   5
  TestBranchenperzentile               3
  TestExampleBenchmarkReport           4
  TestSustainabilityEndpoints          4
  TestCO2BerechnenEndpoint             4
  TestBenchmarkEndpoints               4
                               total: 60
"""
from __future__ import annotations

import math
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api
from app.core.sustainability_reporting import (
    CO2Bilanz,
    ESGBericht,
    ESGBewertung,
    ESGKennzahl,
    EmissionsKategorie,
    EmissionsPosition,
    EmissionsScope,
    NachhaltigkeitsZiel,
    BerichtsTyp,
    berechne_energie_co2e,
    berechne_transport_co2e,
    erstelle_beispiel_co2_bilanz,
    erstelle_beispiel_esg_bericht,
)
from app.core.benchmark_cockpit import (
    BenchmarkKategorie,
    BenchmarkKennzahl,
    BenchmarkReport,
    BenchmarkTrend,
    BenchmarkTrendPunkt,
    PerzentilStufe,
    ReportFrequenz,
    berechne_branchenperzentile,
    berechne_trend,
    get_example_benchmark_report,
)


# ---------------------------------------------------------------------------
# Shared helpers / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    return TestClient(app)


def _make_co2_bilanz(positionen: list[EmissionsPosition]) -> CO2Bilanz:
    return CO2Bilanz(
        bilanz_id="TEST-BIL",
        tenant_id="T-01",
        zeitraum_von=date(2026, 1, 1),
        zeitraum_bis=date(2026, 12, 31),
        positionen=positionen,
    )


def _make_kz(ist: float, ziel: float, gewichtung: float = 1.0) -> ESGKennzahl:
    return ESGKennzahl(
        kennzahl_id="K1",
        ziel=NachhaltigkeitsZiel.CO2_REDUKTION,
        bezeichnung="Test",
        ist_wert=ist,
        ziel_wert=ziel,
        einheit="t",
        gewichtung=gewichtung,
    )


# ===========================================================================
# TestEmissionsPositionDataclass  (4 tests)
# ===========================================================================

class TestEmissionsPositionDataclass:

    def test_as_dict_contains_co2e_t(self):
        pos = EmissionsPosition(
            positions_id="P-1",
            scope=EmissionsScope.SCOPE_1,
            kategorie=EmissionsKategorie.TRANSPORT_LKW,
            menge=100.0,
            einheit="t*km",
            co2e_kg=620.0,
        )
        d = pos.as_dict()
        assert "co2e_t" in d
        assert abs(d["co2e_t"] - 0.62) < 1e-6

    def test_as_dict_co2e_t_equals_kg_div_1000(self):
        pos = EmissionsPosition("P-2", EmissionsScope.SCOPE_2, EmissionsKategorie.ENERGIE_STROM,
                                500.0, "kWh", 190.0)
        d = pos.as_dict()
        assert abs(d["co2e_t"] - d["co2e_kg"] / 1000) < 1e-9

    def test_as_dict_has_all_keys(self):
        pos = EmissionsPosition("P-3", EmissionsScope.SCOPE_3, EmissionsKategorie.TRANSPORT_BAHN,
                                200.0, "t*km", 3.6, "Bahn-Test")
        d = pos.as_dict()
        for key in ("positions_id", "scope", "kategorie", "menge", "einheit", "co2e_kg", "co2e_t", "beschreibung"):
            assert key in d

    def test_beschreibung_default_is_empty_string(self):
        pos = EmissionsPosition("P-4", EmissionsScope.SCOPE_1, EmissionsKategorie.TROCKNUNG,
                                50.0, "t", 425.0)
        assert pos.beschreibung == ""
        assert pos.as_dict()["beschreibung"] == ""


# ===========================================================================
# TestCO2BilanzProperties  (6 tests)
# ===========================================================================

class TestCO2BilanzProperties:

    def _bilanz_with_scopes(self) -> CO2Bilanz:
        p1 = EmissionsPosition("P-S1", EmissionsScope.SCOPE_1, EmissionsKategorie.TRANSPORT_LKW,
                               100.0, "t*km", 1000.0)
        p2 = EmissionsPosition("P-S2", EmissionsScope.SCOPE_2, EmissionsKategorie.ENERGIE_STROM,
                               200.0, "kWh", 2000.0)
        p3 = EmissionsPosition("P-S3a", EmissionsScope.SCOPE_3, EmissionsKategorie.LANDWIRTSCHAFT,
                               300.0, "t", 3000.0)
        p4 = EmissionsPosition("P-S3b", EmissionsScope.SCOPE_3, EmissionsKategorie.TRANSPORT_SCHIFF,
                               400.0, "t*km", 4000.0)
        return _make_co2_bilanz([p1, p2, p3, p4])

    def test_gesamt_co2e_kg(self):
        b = self._bilanz_with_scopes()
        assert abs(b.gesamt_co2e_kg - 10000.0) < 1e-6

    def test_gesamt_co2e_t(self):
        b = self._bilanz_with_scopes()
        assert abs(b.gesamt_co2e_t - 10.0) < 1e-6

    def test_scope1_co2e_kg(self):
        b = self._bilanz_with_scopes()
        assert abs(b.scope1_co2e_kg - 1000.0) < 1e-6

    def test_scope2_co2e_kg(self):
        b = self._bilanz_with_scopes()
        assert abs(b.scope2_co2e_kg - 2000.0) < 1e-6

    def test_five_positionen_in_beispiel(self):
        bilanz = erstelle_beispiel_co2_bilanz()
        assert len(bilanz.positionen) == 5


# ===========================================================================
# TestESGKennzahlZielerreichung  (5 tests)
# ===========================================================================

class TestESGKennzahlZielerreichung:

    def test_exact_target_is_100_pct(self):
        kz = _make_kz(ist=100.0, ziel=100.0)
        assert abs(kz.zielerreichung_pct - 100.0) < 1e-6

    def test_ist_greater_than_ziel_is_below_100(self):
        # Reduction goal: ist_wert > ziel_wert means underperforming
        kz = _make_kz(ist=120.0, ziel=100.0)
        # min(100, 100/120 * 100) = min(100, 83.33) = 83.33
        expected = 100.0 / 120.0 * 100.0
        assert abs(kz.zielerreichung_pct - expected) < 1e-4

    def test_ist_less_than_ziel_is_capped_at_100(self):
        # Over-performing: ist_wert < ziel_wert → min(100, >100) = 100
        kz = _make_kz(ist=50.0, ziel=100.0)
        assert abs(kz.zielerreichung_pct - 100.0) < 1e-6

    def test_ziel_wert_zero_ist_zero_returns_100(self):
        kz = _make_kz(ist=0.0, ziel=0.0)
        assert abs(kz.zielerreichung_pct - 100.0) < 1e-6

    def test_gewichtung_stored_correctly(self):
        kz = _make_kz(ist=80.0, ziel=100.0, gewichtung=2.5)
        assert abs(kz.gewichtung - 2.5) < 1e-9


# ===========================================================================
# TestESGBerichtScore  (5 tests)
# ===========================================================================

class TestESGBerichtScore:

    def _bericht(self, kennzahlen: list[ESGKennzahl]) -> ESGBericht:
        return ESGBericht(
            bericht_id="ESG-T",
            tenant_id="T-01",
            zeitraum_von=date(2026, 1, 1),
            zeitraum_bis=date(2026, 12, 31),
            kennzahlen=kennzahlen,
        )

    def test_score_weighted_average(self):
        # kz1: zielerreichung=100 (ziel==ist), gewichtung=1
        # kz2: zielerreichung=50 (ist=200, ziel=100 → min(100, 50)=50), gewichtung=1
        # score = (100*1 + 50*1) / 2 = 75
        kz1 = _make_kz(ist=100.0, ziel=100.0, gewichtung=1.0)
        kz2 = _make_kz(ist=200.0, ziel=100.0, gewichtung=1.0)
        b = self._bericht([kz1, kz2])
        assert abs(b.esg_score - 75.0) < 1e-4

    def test_bewertung_sehr_gut(self):
        kz = _make_kz(ist=100.0, ziel=100.0)  # 100 %
        b = self._bericht([kz])
        assert b.bewertung == ESGBewertung.SEHR_GUT

    def test_bewertung_ausreichend(self):
        # score=50: ist=200, ziel=100 → 50
        kz = _make_kz(ist=200.0, ziel=100.0)
        b = self._bericht([kz])
        assert b.bewertung == ESGBewertung.AUSREICHEND

    def test_empty_kennzahlen_score_is_zero(self):
        b = self._bericht([])
        assert b.esg_score == 0.0
        assert b.bewertung == ESGBewertung.MANGELHAFT


# ===========================================================================
# TestTransportCO2Berechnung  (6 tests)
# ===========================================================================

class TestTransportCO2Berechnung:

    def test_lkw_factor(self):
        pos = berechne_transport_co2e("T-1", EmissionsKategorie.TRANSPORT_LKW, 10.0, 100.0)
        # 10 t * 100 km * 0.062 = 62 kg
        assert abs(pos.co2e_kg - 62.0) < 1e-6
        assert pos.einheit == "t*km"

    def test_bahn_factor(self):
        pos = berechne_transport_co2e("T-2", EmissionsKategorie.TRANSPORT_BAHN, 10.0, 100.0)
        # 10 * 100 * 0.018 = 18 kg
        assert abs(pos.co2e_kg - 18.0) < 1e-6

    def test_schiff_factor(self):
        pos = berechne_transport_co2e("T-3", EmissionsKategorie.TRANSPORT_SCHIFF, 10.0, 100.0)
        # 10 * 100 * 0.010 = 10 kg
        assert abs(pos.co2e_kg - 10.0) < 1e-6

    def test_raises_value_error_menge_zero(self):
        with pytest.raises(ValueError):
            berechne_transport_co2e("T-4", EmissionsKategorie.TRANSPORT_LKW, 0.0, 100.0)

    def test_raises_value_error_distanz_negative(self):
        with pytest.raises(ValueError):
            berechne_transport_co2e("T-5", EmissionsKategorie.TRANSPORT_LKW, 10.0, -1.0)



# ===========================================================================
# TestEnergieCO2Berechnung  (4 tests)
# ===========================================================================

class TestEnergieCO2Berechnung:

    def test_strom_factor(self):
        pos = berechne_energie_co2e("E-1", EmissionsKategorie.ENERGIE_STROM, 1000.0)
        # 1000 kWh * 0.380 = 380 kg
        assert abs(pos.co2e_kg - 380.0) < 1e-6
        assert pos.einheit == "kWh"

    def test_waerme_factor(self):
        pos = berechne_energie_co2e("E-2", EmissionsKategorie.ENERGIE_WAERME, 1000.0)
        # 1000 * 0.210 = 210 kg
        assert abs(pos.co2e_kg - 210.0) < 1e-6

    def test_raises_value_error_kwh_zero(self):
        with pytest.raises(ValueError):
            berechne_energie_co2e("E-3", EmissionsKategorie.ENERGIE_STROM, 0.0)

    def test_raises_value_error_wrong_kategorie(self):
        # TRANSPORT_LKW is not in _EMISSIONSFAKTOR_KWH
        with pytest.raises(ValueError):
            berechne_energie_co2e("E-4", EmissionsKategorie.TRANSPORT_LKW, 500.0)


# ===========================================================================
# TestBeispielDaten  (3 tests)
# ===========================================================================

class TestBeispielDaten:

    def test_beispiel_co2_bilanz_has_five_positionen(self):
        bilanz = erstelle_beispiel_co2_bilanz()
        assert len(bilanz.positionen) == 5

    def test_beispiel_esg_bericht_has_five_kennzahlen(self):
        bericht = erstelle_beispiel_esg_bericht()
        assert len(bericht.kennzahlen) == 5

    def test_beispiel_esg_bericht_has_co2_bilanz(self):
        bericht = erstelle_beispiel_esg_bericht()
        assert bericht.co2_bilanz is not None
        assert isinstance(bericht.co2_bilanz, CO2Bilanz)


# ===========================================================================
# TestBenchmarkKennzahlPerzentil  (6 tests)
# ===========================================================================

class TestBenchmarkKennzahlPerzentil:

    def _kz_hoeher(self, eigenwert: float) -> BenchmarkKennzahl:
        return BenchmarkKennzahl(
            kennzahl_id="BK-H",
            bezeichnung="Test",
            kategorie=BenchmarkKategorie.LOGISTIK,
            eigenwert=eigenwert,
            einheit="t/h",
            branche_mittelwert=7.0,
            branche_p25=5.5,
            branche_p75=8.0,
            branche_p90=9.5,
            hoeher_ist_besser=True,
        )

    def _kz_niedriger(self, eigenwert: float) -> BenchmarkKennzahl:
        # Lower is better: p25=17, p75=13, p90=11 (costs)
        return BenchmarkKennzahl(
            kennzahl_id="BK-L",
            bezeichnung="Lagerkosten",
            kategorie=BenchmarkKategorie.FINANZEN,
            eigenwert=eigenwert,
            einheit="€/t",
            branche_mittelwert=14.80,
            branche_p25=17.00,
            branche_p75=13.00,
            branche_p90=11.00,
            hoeher_ist_besser=False,
        )

    def test_hoeher_top10_at_p90(self):
        kz = self._kz_hoeher(9.5)
        assert kz.perzentil_stufe == PerzentilStufe.TOP_10

    def test_hoeher_top25_between_p75_and_p90(self):
        kz = self._kz_hoeher(8.2)  # >= p75=8.0, < p90=9.5
        assert kz.perzentil_stufe == PerzentilStufe.TOP_25

    def test_lower_is_better_top10_at_or_below_p90(self):
        # eigenwert <= p90(=11) → TOP_10
        kz = self._kz_niedriger(10.0)
        assert kz.perzentil_stufe == PerzentilStufe.TOP_10

    def test_lower_is_better_top25_between_p90_and_p75(self):
        # eigenwert <= p75(=13) but > p90(=11) → TOP_25
        kz = self._kz_niedriger(12.50)
        assert kz.perzentil_stufe == PerzentilStufe.TOP_25

    def test_lower_is_better_mittelfeld(self):
        # eigenwert <= p25(=17) but > p75(=13) → MITTELFELD
        kz = self._kz_niedriger(15.0)
        assert kz.perzentil_stufe == PerzentilStufe.MITTELFELD

    def test_abweichung_vom_mittel_pct_positive(self):
        kz = self._kz_hoeher(8.4)  # (8.4 - 7.0) / 7.0 * 100 = 20
        assert abs(kz.abweichung_vom_mittel_pct - 20.0) < 1e-4


# ===========================================================================
# TestBenchmarkTrend  (5 tests)
# ===========================================================================

class TestBenchmarkTrend:

    def test_stark_verbessernd(self):
        # [100, 110]: n_basis=1, basis=[100], aktuell=110, change=+10% > 5%
        result = berechne_trend([100.0, 110.0])
        assert result == BenchmarkTrend.STARK_VERBESSERND

    def test_verbessernd(self):
        # basis avg = (100+100)/2=100, last=103 → +3% → VERBESSERND
        result = berechne_trend([100.0, 100.0, 103.0])
        assert result == BenchmarkTrend.VERBESSERND

    def test_stabil(self):
        # basis avg = 100, last=100.5 → +0.5% → STABIL
        result = berechne_trend([100.0, 100.0, 100.5])
        assert result == BenchmarkTrend.STABIL

    def test_verschlechternd(self):
        # basis avg = 100, last=97 → -3% → VERSCHLECHTERND
        result = berechne_trend([100.0, 100.0, 97.0])
        assert result == BenchmarkTrend.VERSCHLECHTERND

    def test_single_value_returns_stabil(self):
        result = berechne_trend([42.0])
        assert result == BenchmarkTrend.STABIL


# ===========================================================================
# TestBranchenperzentile  (4 tests)
# ===========================================================================

class TestBranchenperzentile:

    def test_five_values_has_all_keys(self):
        result = berechne_branchenperzentile([10.0, 20.0, 30.0, 40.0, 50.0])
        for key in ("p25", "p50", "p75", "p90", "mittelwert"):
            assert key in result

    def test_mittelwert_correct(self):
        result = berechne_branchenperzentile([10.0, 20.0, 30.0, 40.0, 50.0])
        assert abs(result["mittelwert"] - 30.0) < 1e-4

    def test_empty_raises_value_error(self):
        with pytest.raises(ValueError):
            berechne_branchenperzentile([])


# ===========================================================================
# TestExampleBenchmarkReport  (4 tests)
# ===========================================================================

class TestExampleBenchmarkReport:

    def test_six_kennzahlen(self):
        report = get_example_benchmark_report()
        assert len(report.kennzahlen) == 6

    def test_gesamtbewertung_score_in_range(self):
        report = get_example_benchmark_report()
        score = report.gesamtbewertung_score
        assert 0.0 <= score <= 100.0

    def test_trend_daten_has_two_series(self):
        report = get_example_benchmark_report()
        assert len(report.trend_daten) == 2

    def test_top10_and_verbesserungspotenzial_partitioned(self):
        report = get_example_benchmark_report()
        top10_ids = {k.kennzahl_id for k in report.top10_kennzahlen}
        verbes_ids = {k.kennzahl_id for k in report.verbesserungspotenzial}
        # No overlap between top10 and improvement potential
        assert top10_ids.isdisjoint(verbes_ids)


# ===========================================================================
# TestSustainabilityEndpoints  (4 tests)
# ===========================================================================

class TestSustainabilityEndpoints:

    def test_get_esg_bericht_default_returns_200(self, client: TestClient):
        resp = client.get("/process/sustainability/esg-bericht")
        assert resp.status_code == 200
        data = resp.json()
        assert "esg_score" in data
        assert "bewertung" in data

    def test_get_esg_bericht_with_params(self, client: TestClient):
        resp = client.get("/process/sustainability/esg-bericht?tenant_id=T-99&jahr=2025")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == "T-99"

    def test_get_esg_bericht_bad_jahr_returns_422(self, client: TestClient):
        resp = client.get("/process/sustainability/esg-bericht?jahr=1800")
        assert resp.status_code == 422

    def test_post_co2_berechnen_transport_returns_200(self, client: TestClient):
        body = {
            "positions_id": "P-API-1",
            "typ": "TRANSPORT",
            "kategorie": "TRANSPORT_LKW",
            "menge": 10.0,
            "distanz_km": 100.0,
        }
        resp = client.post("/process/sustainability/co2-berechnen", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert "co2e_kg" in data
        assert abs(data["co2e_kg"] - 62.0) < 1e-4


# ===========================================================================
# TestCO2BerechnenEndpoint  (4 tests)
# ===========================================================================

class TestCO2BerechnenEndpoint:

    def test_transport_ok(self, client: TestClient):
        body = {
            "positions_id": "P-T1",
            "typ": "TRANSPORT",
            "kategorie": "TRANSPORT_BAHN",
            "menge": 5.0,
            "distanz_km": 200.0,
        }
        resp = client.post("/process/sustainability/co2-berechnen", json=body)
        assert resp.status_code == 200
        # 5 * 200 * 0.018 = 18 kg
        assert abs(resp.json()["co2e_kg"] - 18.0) < 1e-4

    def test_energie_ok(self, client: TestClient):
        body = {
            "positions_id": "P-E1",
            "typ": "ENERGIE",
            "kategorie": "ENERGIE_WAERME",
            "menge": 500.0,
        }
        resp = client.post("/process/sustainability/co2-berechnen", json=body)
        assert resp.status_code == 200
        # 500 * 0.210 = 105 kg
        assert abs(resp.json()["co2e_kg"] - 105.0) < 1e-4

    def test_missing_fields_returns_422(self, client: TestClient):
        # Missing positions_id, typ, kategorie
        resp = client.post("/process/sustainability/co2-berechnen", json={})
        assert resp.status_code == 422

    def test_bad_kategorie_returns_422(self, client: TestClient):
        body = {
            "positions_id": "P-BAD",
            "typ": "TRANSPORT",
            "kategorie": "UNGUELTIGE_KATEGORIE",
            "menge": 10.0,
            "distanz_km": 100.0,
        }
        resp = client.post("/process/sustainability/co2-berechnen", json=body)
        assert resp.status_code == 422


# ===========================================================================
# TestBenchmarkEndpoints  (4 tests)
# ===========================================================================

class TestBenchmarkEndpoints:

    def test_get_benchmark_report_returns_six_kennzahlen(self, client: TestClient):
        resp = client.get("/process/benchmark/report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["kennzahlen_anzahl"] == 6

    def test_get_benchmark_report_filter_by_kategorie(self, client: TestClient):
        resp = client.get("/process/benchmark/report?kategorie=LOGISTIK")
        assert resp.status_code == 200
        data = resp.json()
        # Only LOGISTIK kennzahlen remain (BK-001 is LOGISTIK)
        for kz in data["kennzahlen"]:
            assert kz["kategorie"] == "LOGISTIK"

    def test_get_benchmark_report_bad_kategorie_returns_422(self, client: TestClient):
        resp = client.get("/process/benchmark/report?kategorie=UNGUELTIG")
        assert resp.status_code == 422

    def test_post_perzentile_with_eigenwert_returns_einordnung(self, client: TestClient):
        body = {
            "werte": [10.0, 20.0, 30.0, 40.0, 50.0],
            "eigenwert": 45.0,
            "kennzahl_id": "TEST-KZ",
        }
        resp = client.post("/process/benchmark/perzentile", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert "p25" in data
        assert "p90" in data
        assert "einordnung" in data
        assert data["eigenwert"] == 45.0
