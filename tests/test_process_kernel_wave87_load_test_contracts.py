"""
test_process_kernel_wave87_load_test_contracts.py — Lasttest-SLA-Contracts (Gap 037)

Wave 87: ErntepeakSLAContract, LasttestErgebnis, evaluate_erntepeak_sla()

HINWEIS: Diese Tests prüfen das Datenmodell und die SLA-Auswertungslogik.
         Sie führen KEINE echten Lasttests durch. Echte Lasttests erfolgen via:
         - load-tests/locustfile.py (Locust)
         - load-tests/erntepeak-load-test.js (k6)
"""
import pytest
from app.core.load_test_contracts import (
    EndpointKategorie,
    EndpointLasttestErgebnis,
    ErntepeakSLAContract,
    LasttestErgebnis,
    LasttestKonfiguration,
    LasttestSLAErgebnis,
    LasttestSzenario,
    LasttestStatus,
    SLAErfuellungsGrad,
    evaluate_erntepeak_sla,
    get_erntepeak_konfiguration,
    get_normalbetrieb_konfiguration,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ep(
    endpoint: str = "/controlling/dashboards",
    kategorie: EndpointKategorie = EndpointKategorie.DASHBOARD,
    anfragen: int = 1000,
    fehler: int = 0,
    p50: float = 80.0,
    p95: float = 150.0,
    p99: float = 220.0,
    throughput: float = 50.0,
) -> EndpointLasttestErgebnis:
    return EndpointLasttestErgebnis(
        endpoint=endpoint,
        kategorie=kategorie,
        anfragen_gesamt=anfragen,
        fehler_anzahl=fehler,
        p50_ms=p50,
        p95_ms=p95,
        p99_ms=p99,
        throughput_rps=throughput,
    )


def _ergebnis(
    gleichzeitige_user: int = 500,
    endpoints: list[EndpointLasttestErgebnis] | None = None,
) -> LasttestErgebnis:
    if endpoints is None:
        endpoints = [_ep()]
    return LasttestErgebnis(
        test_id="TEST-001",
        szenario=LasttestSzenario.ERNTEPEAK,
        gleichzeitige_user=gleichzeitige_user,
        status=LasttestStatus.ABGESCHLOSSEN,
        dauer_sekunden=1800.0,
        endpoint_ergebnisse=endpoints,
    )


# ---------------------------------------------------------------------------
# TestLasttestKonfiguration
# ---------------------------------------------------------------------------

class TestLasttestKonfiguration:
    def test_erntepeak_konfiguration(self):
        k = get_erntepeak_konfiguration()
        assert k.gleichzeitige_user == 500
        assert k.szenario == LasttestSzenario.ERNTEPEAK

    def test_normalbetrieb_konfiguration(self):
        k = get_normalbetrieb_konfiguration()
        assert k.gleichzeitige_user == 50
        assert k.szenario == LasttestSzenario.NORMALBETRIEB

    def test_negativ_user_fehler(self):
        with pytest.raises(ValueError):
            LasttestKonfiguration(
                szenario=LasttestSzenario.ERNTEPEAK,
                gleichzeitige_user=0,
                dauer_sekunden=300,
            )

    def test_requests_pro_sekunde_theoretisch(self):
        k = LasttestKonfiguration(
            szenario=LasttestSzenario.ERNTEPEAK,
            gleichzeitige_user=500,
            dauer_sekunden=1800,
            think_time_ms=500,
        )
        # 500 user / 0.5s = 1000 RPS theoretisch
        assert k.requests_pro_sekunde_theoretisch == 1000.0

    def test_as_dict(self):
        k = get_erntepeak_konfiguration()
        d = k.as_dict()
        assert "gleichzeitige_user" in d
        assert "szenario" in d


# ---------------------------------------------------------------------------
# TestEndpointLasttestErgebnis
# ---------------------------------------------------------------------------

class TestEndpointLasttestErgebnis:
    def test_fehlerrate_null(self):
        ep = _ep(anfragen=1000, fehler=0)
        assert ep.fehler_rate_pct == 0.0

    def test_fehlerrate_berechnung(self):
        ep = _ep(anfragen=1000, fehler=10)
        assert ep.fehler_rate_pct == 1.0

    def test_fehlerrate_null_anfragen(self):
        ep = _ep(anfragen=0, fehler=0)
        assert ep.fehler_rate_pct == 0.0

    def test_as_dict(self):
        ep = _ep()
        d = ep.as_dict()
        assert "endpoint" in d
        assert "kategorie" in d
        assert "fehler_rate_pct" in d


# ---------------------------------------------------------------------------
# TestLasttestErgebnis
# ---------------------------------------------------------------------------

class TestLasttestErgebnis:
    def test_gesamt_anfragen(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(anfragen=1000),
            _ep(anfragen=500, endpoint="/controlling/kpis"),
        ])
        assert ergebnis.gesamt_anfragen == 1500

    def test_gesamt_fehler(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(fehler=10),
            _ep(fehler=5, endpoint="/controlling/kpis"),
        ])
        assert ergebnis.gesamt_fehler == 15

    def test_gesamt_fehler_rate(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(anfragen=1000, fehler=5),
        ])
        assert ergebnis.gesamt_fehler_rate_pct == 0.5

    def test_p95_max(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(p95=100.0),
            _ep(p95=800.0, endpoint="/agrar/settlements"),
        ])
        assert ergebnis.p95_max_ms == 800.0

    def test_p95_avg(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(p95=100.0),
            _ep(p95=300.0, endpoint="/agrar/settlements"),
        ])
        assert ergebnis.p95_avg_ms == 200.0

    def test_get_endpoint_gefunden(self):
        ergebnis = _ergebnis(endpoints=[_ep(endpoint="/controlling/dashboards")])
        ep = ergebnis.get_endpoint("/controlling/dashboards")
        assert ep is not None

    def test_get_endpoint_nicht_gefunden(self):
        ergebnis = _ergebnis()
        assert ergebnis.get_endpoint("/not/existing") is None

    def test_as_dict(self):
        ergebnis = _ergebnis()
        d = ergebnis.as_dict()
        assert "gesamt_anfragen" in d
        assert "endpoint_ergebnisse" in d


# ---------------------------------------------------------------------------
# TestErntepeakSLAContract
# ---------------------------------------------------------------------------

class TestErntepeakSLAContract:
    def test_standardwerte(self):
        sla = ErntepeakSLAContract()
        assert sla.min_gleichzeitige_user == 500
        assert sla.max_fehler_rate_pct == 1.0
        assert sla.max_p95_global_ms == 2000.0
        assert sla.max_p95_dashboard_ms == 250.0
        assert sla.min_throughput_rps == 100.0

    def test_as_dict(self):
        sla = ErntepeakSLAContract()
        d = sla.as_dict()
        assert d["max_fehler_rate_pct"] == 1.0
        assert d["max_p95_dashboard_ms"] == 250.0


# ---------------------------------------------------------------------------
# TestEvaluateErntePeakSla — ERFUELLT
# ---------------------------------------------------------------------------

class TestEvaluateErntePeakSlaErfuellt:
    def test_perfektes_ergebnis_erfuellt(self):
        ergebnis = _ergebnis(
            gleichzeitige_user=500,
            endpoints=[_ep(fehler=0, p95=150.0, throughput=200.0)],
        )
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is True
        assert result.erfuellungsgrad == SLAErfuellungsGrad.ERFUELLT

    def test_genau_an_grenzwerten_erfuellt(self):
        ergebnis = _ergebnis(
            gleichzeitige_user=500,
            endpoints=[
                _ep(anfragen=1000, fehler=9, p95=249.0, throughput=101.0),  # 0.9% error, p95=249ms
            ],
        )
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is True


# ---------------------------------------------------------------------------
# TestEvaluateErntePeakSla — VERLETZT
# ---------------------------------------------------------------------------

class TestEvaluateErntePeakSlaVerletzt:
    def test_error_rate_verletzt(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(anfragen=1000, fehler=20),  # 2% > 1%
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert any("Error Rate" in v for v in result.verletzte_kriterien)

    def test_p95_global_verletzt(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(p95=2500.0, kategorie=EndpointKategorie.ANNAHME),  # > 2000ms avg
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert any("p95" in v for v in result.verletzte_kriterien)

    def test_dashboard_p95_verletzt(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(p95=300.0, kategorie=EndpointKategorie.DASHBOARD),  # > 250ms
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert any("Dashboard" in v for v in result.verletzte_kriterien)

    def test_zu_wenig_user_verletzt(self):
        ergebnis = _ergebnis(gleichzeitige_user=100)  # < 500
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert any("User" in v for v in result.verletzte_kriterien)

    def test_keine_endpoints_nicht_messbar(self):
        ergebnis = _ergebnis(endpoints=[])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert result.erfuellungsgrad == SLAErfuellungsGrad.NICHT_MESSBAR

    def test_mehrere_verletzungen(self):
        ergebnis = _ergebnis(
            gleichzeitige_user=100,  # Verletzung 1: zu wenig User
            endpoints=[
                _ep(anfragen=100, fehler=5, p95=300.0),  # V2: error rate, V3: dashboard p95
            ],
        )
        result = evaluate_erntepeak_sla(ergebnis)
        assert len(result.verletzte_kriterien) >= 2

    def test_custom_sla_vertrag(self):
        """Benutzerdefinierter SLA-Vertrag mit strengeren Grenzen."""
        sla = ErntepeakSLAContract(max_p95_dashboard_ms=200.0)
        ergebnis = _ergebnis(endpoints=[
            _ep(p95=220.0, kategorie=EndpointKategorie.ANNAHME),   # ANNAHME, kein Dashboard
        ])
        result = evaluate_erntepeak_sla(ergebnis, sla=sla)
        # p95 avg = 220ms < 2000ms global SLA, kein Dashboard-Endpoint → kein Verstoß
        assert result.kpi_erfuellt is True


# ---------------------------------------------------------------------------
# TestEvaluateErntePeakSla — Details und Warnungen
# ---------------------------------------------------------------------------

class TestEvaluateErntePeakSlaDetails:
    def test_details_enthalten_fehlerrate(self):
        ergebnis = _ergebnis()
        result = evaluate_erntepeak_sla(ergebnis)
        assert "gesamt_fehler_rate_pct" in result.details

    def test_details_enthalten_p95(self):
        ergebnis = _ergebnis()
        result = evaluate_erntepeak_sla(ergebnis)
        assert "p95_avg_ms" in result.details

    def test_throughput_warnung_niedrig(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(throughput=10.0),  # < 100 RPS min
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert any("Throughput" in w for w in result.warnungen)

    def test_grenzwertig_bei_throughput_warnung_ohne_verletzung(self):
        ergebnis = _ergebnis(endpoints=[
            _ep(fehler=0, p95=100.0, throughput=50.0),  # Throughput-Warnung, aber keine Verletzung
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is True
        assert result.erfuellungsgrad == SLAErfuellungsGrad.GRENZWERTIG

    def test_as_dict(self):
        ergebnis = _ergebnis()
        result = evaluate_erntepeak_sla(ergebnis)
        d = result.as_dict()
        assert "kpi_erfuellt" in d
        assert "erfuellungsgrad" in d
        assert "verletzte_kriterien" in d
