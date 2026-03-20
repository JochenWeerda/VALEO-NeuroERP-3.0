"""
Wave 87 — Lasttest-Contracts Erntepeak (Gap 037)

Tests für LasttestKonfiguration, LasttestErgebnis, ErntepeakSLAContract,
evaluate_erntepeak_sla() und Standard-Konfigurationen.

Gap 037: 500 gleichzeitige User stabil — Error Rate < 1%, p95 < 2s
"""
from __future__ import annotations

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
# Fixtures
# ---------------------------------------------------------------------------

def _ep(
    endpoint: str = "/api/v1/dashboard",
    kategorie: EndpointKategorie = EndpointKategorie.DASHBOARD,
    anfragen: int = 10000,
    fehler: int = 0,
    p50: float = 80.0,
    p95: float = 180.0,
    p99: float = 250.0,
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
    user: int = 500,
    szenario: LasttestSzenario = LasttestSzenario.ERNTEPEAK,
    eps: list[EndpointLasttestErgebnis] | None = None,
    status: LasttestStatus = LasttestStatus.ABGESCHLOSSEN,
) -> LasttestErgebnis:
    return LasttestErgebnis(
        test_id="T-ERNTE-001",
        szenario=szenario,
        gleichzeitige_user=user,
        status=status,
        dauer_sekunden=1800.0,
        endpoint_ergebnisse=eps or [],
    )


def _stabiles_erntepeak_ergebnis() -> LasttestErgebnis:
    """Ergebnis das alle SLA-Kriterien erfüllt."""
    return _ergebnis(user=500, eps=[
        _ep("/api/v1/dashboard",     EndpointKategorie.DASHBOARD,   10000, 0,   80,  180,  250,  55.0),
        _ep("/api/v1/annahme",       EndpointKategorie.ANNAHME,     8000,  10,  120, 500,  800,  44.0),
        _ep("/api/v1/controlling",   EndpointKategorie.CONTROLLING, 6000,  5,   90,  200,  350,  33.0),
        _ep("/api/v1/settlement",    EndpointKategorie.SETTLEMENT,  4000,  2,   200, 600,  900,  22.0),
    ])


# ---------------------------------------------------------------------------
# TestLasttestKonfiguration
# ---------------------------------------------------------------------------

class TestLasttestKonfiguration:
    def test_gueltiger_erntepeak(self):
        k = LasttestKonfiguration(
            szenario=LasttestSzenario.ERNTEPEAK,
            gleichzeitige_user=500,
            dauer_sekunden=1800,
        )
        assert k.gleichzeitige_user == 500

    def test_ungueltige_userzahl_raises(self):
        with pytest.raises(ValueError, match="gleichzeitige_user"):
            LasttestKonfiguration(LasttestSzenario.ERNTEPEAK, 0, 1800)

    def test_ungueltige_dauer_raises(self):
        with pytest.raises(ValueError, match="dauer_sekunden"):
            LasttestKonfiguration(LasttestSzenario.ERNTEPEAK, 100, 0)

    def test_requests_pro_sekunde(self):
        k = LasttestKonfiguration(
            szenario=LasttestSzenario.ERNTEPEAK,
            gleichzeitige_user=500,
            dauer_sekunden=1800,
            think_time_ms=500,
        )
        # 500 User / (500ms / 1000) = 1000 RPS theoretisch
        assert k.requests_pro_sekunde_theoretisch == 1000.0

    def test_as_dict(self):
        k = get_erntepeak_konfiguration()
        d = k.as_dict()
        assert d["szenario"] == "ERNTEPEAK"
        assert d["gleichzeitige_user"] == 500
        assert "requests_pro_sekunde_theoretisch" in d


# ---------------------------------------------------------------------------
# TestEndpointLasttestErgebnis
# ---------------------------------------------------------------------------

class TestEndpointLasttestErgebnis:
    def test_fehler_rate_berechnung(self):
        ep = _ep(anfragen=1000, fehler=5)
        assert ep.fehler_rate_pct == 0.5

    def test_fehler_rate_null(self):
        ep = _ep(anfragen=1000, fehler=0)
        assert ep.fehler_rate_pct == 0.0

    def test_fehler_rate_keine_anfragen(self):
        ep = _ep(anfragen=0, fehler=0)
        assert ep.fehler_rate_pct == 0.0

    def test_as_dict(self):
        ep = _ep()
        d = ep.as_dict()
        assert "fehler_rate_pct" in d
        assert "p95_ms" in d
        assert "throughput_rps" in d


# ---------------------------------------------------------------------------
# TestLasttestErgebnis
# ---------------------------------------------------------------------------

class TestLasttestErgebnis:
    def test_gesamt_anfragen(self):
        ergebnis = _ergebnis(eps=[_ep(anfragen=5000), _ep(anfragen=3000)])
        assert ergebnis.gesamt_anfragen == 8000

    def test_gesamt_fehler(self):
        ergebnis = _ergebnis(eps=[_ep(fehler=10), _ep(fehler=5)])
        assert ergebnis.gesamt_fehler == 15

    def test_gesamt_fehler_rate(self):
        ergebnis = _ergebnis(eps=[_ep(anfragen=1000, fehler=5)])
        assert ergebnis.gesamt_fehler_rate_pct == 0.5

    def test_p95_max(self):
        ergebnis = _ergebnis(eps=[_ep(p95=200.0), _ep(p95=500.0)])
        assert ergebnis.p95_max_ms == 500.0

    def test_p95_avg(self):
        ergebnis = _ergebnis(eps=[_ep(p95=200.0), _ep(p95=400.0)])
        assert ergebnis.p95_avg_ms == 300.0

    def test_p95_leer(self):
        ergebnis = _ergebnis()
        assert ergebnis.p95_max_ms == 0.0
        assert ergebnis.p95_avg_ms == 0.0

    def test_get_endpoint_vorhanden(self):
        ergebnis = _ergebnis(eps=[_ep("/api/v1/dashboard")])
        ep = ergebnis.get_endpoint("/api/v1/dashboard")
        assert ep is not None

    def test_get_endpoint_nicht_vorhanden(self):
        ergebnis = _ergebnis()
        assert ergebnis.get_endpoint("/gibt/nicht") is None

    def test_as_dict(self):
        ergebnis = _stabiles_erntepeak_ergebnis()
        d = ergebnis.as_dict()
        assert d["gleichzeitige_user"] == 500
        assert "gesamt_fehler_rate_pct" in d
        assert "p95_max_ms" in d


# ---------------------------------------------------------------------------
# TestErntepeakSLAContract
# ---------------------------------------------------------------------------

class TestErntepeakSLAContract:
    def test_standard_werte(self):
        sla = ErntepeakSLAContract()
        assert sla.min_gleichzeitige_user == 500
        assert sla.max_fehler_rate_pct == 1.0
        assert sla.max_p95_global_ms == 2000.0
        assert sla.max_p95_dashboard_ms == 250.0

    def test_as_dict(self):
        sla = ErntepeakSLAContract()
        d = sla.as_dict()
        assert "min_gleichzeitige_user" in d
        assert "max_fehler_rate_pct" in d


# ---------------------------------------------------------------------------
# TestEvaluateErntepeak
# ---------------------------------------------------------------------------

class TestEvaluateErntepeak:
    def test_stabile_last_erfuellt_kpi(self):
        ergebnis = _stabiles_erntepeak_ergebnis()
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is True
        assert result.erfuellungsgrad == SLAErfuellungsGrad.ERFUELLT

    def test_zu_wenige_user_verletzt_kpi(self):
        ergebnis = _ergebnis(user=200, eps=[_ep()])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert result.erfuellungsgrad == SLAErfuellungsGrad.VERLETZT
        assert any("User" in v for v in result.verletzte_kriterien)

    def test_hohe_fehlerrate_verletzt_kpi(self):
        ergebnis = _ergebnis(user=500, eps=[
            _ep(anfragen=1000, fehler=20),  # 2% > 1%
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert any("Error Rate" in v for v in result.verletzte_kriterien)

    def test_langsamer_p95_verletzt_kpi(self):
        ergebnis = _ergebnis(user=500, eps=[
            _ep(p95=3000.0),  # > 2000ms
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert any("p95" in v for v in result.verletzte_kriterien)

    def test_dashboard_p95_verletzt_kpi(self):
        """Dashboard-Endpoint verletzt 250ms-SLA (Gap 033)."""
        ergebnis = _ergebnis(user=500, eps=[
            _ep("/api/v1/dashboard", EndpointKategorie.DASHBOARD,
                p95=400.0),  # > 250ms
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert any("Dashboard" in v for v in result.verletzte_kriterien)

    def test_niedriger_throughput_nur_warnung(self):
        """Throughput-Unterschreitung → Warnung, kein Fehler."""
        ergebnis = _ergebnis(user=500, eps=[
            _ep(throughput=5.0, p95=180.0),  # 5 RPS < 100 RPS Ziel
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert len(result.warnungen) > 0
        # Error Rate und p95 ok → kein KPI-Verstoß wegen Throughput allein
        assert len(result.verletzte_kriterien) == 0

    def test_leere_endpoints_nicht_messbar(self):
        ergebnis = _ergebnis(user=500, eps=[])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.erfuellungsgrad == SLAErfuellungsGrad.NICHT_MESSBAR
        assert result.kpi_erfuellt is False

    def test_as_dict(self):
        result = evaluate_erntepeak_sla(_stabiles_erntepeak_ergebnis())
        d = result.as_dict()
        assert "kpi_erfuellt" in d
        assert "erfuellungsgrad" in d
        assert "verletzte_kriterien" in d

    def test_custom_sla_vertrag(self):
        """Angepasster SLA (strengere Werte) kann separat übergeben werden."""
        sla = ErntepeakSLAContract(
            min_gleichzeitige_user=500,
            max_fehler_rate_pct=0.5,    # strenger: < 0.5%
            max_p95_global_ms=1000.0,   # strenger: < 1s
            max_p95_dashboard_ms=200.0,
        )
        # Non-dashboard endpoint — kein Dashboard-Limit
        ergebnis = _ergebnis(user=500, eps=[
            _ep("/api/v1/annahme", EndpointKategorie.ANNAHME,
                anfragen=1000, fehler=4, p95=800.0, throughput=110.0),  # 0.4%, p95=800ms < 1000ms
        ])
        result = evaluate_erntepeak_sla(ergebnis, sla)
        assert result.kpi_erfuellt is True


# ---------------------------------------------------------------------------
# TestStandardKonfigurationen
# ---------------------------------------------------------------------------

class TestStandardKonfigurationen:
    def test_erntepeak_konfiguration(self):
        k = get_erntepeak_konfiguration()
        assert k.szenario == LasttestSzenario.ERNTEPEAK
        assert k.gleichzeitige_user == 500
        assert k.dauer_sekunden >= 1800
        assert k.tenant_count >= 5

    def test_normalbetrieb_konfiguration(self):
        k = get_normalbetrieb_konfiguration()
        assert k.szenario == LasttestSzenario.NORMALBETRIEB
        assert k.gleichzeitige_user <= 100


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    def test_vollstaendiger_erntepeak_test(self):
        """
        Vollständiger Erntepeak-Test: 500 User, 30 Min,
        alle Endpoints innerhalb SLA → KPI erfüllt.
        """
        config = get_erntepeak_konfiguration()
        assert config.gleichzeitige_user == 500

        ergebnis = _stabiles_erntepeak_ergebnis()
        result = evaluate_erntepeak_sla(ergebnis)

        assert result.kpi_erfuellt is True
        assert result.erfuellungsgrad == SLAErfuellungsGrad.ERFUELLT
        assert len(result.verletzte_kriterien) == 0

    def test_degradierter_betrieb_bei_uebertemperierung(self):
        """
        Bei 500 Usern aber hoher p95 → SLA verletzt, KPI nicht erfüllt.
        Dashboard > 250ms + Globaler p95 > 2000ms.
        """
        ergebnis = _ergebnis(user=500, eps=[
            _ep("/api/v1/dashboard", EndpointKategorie.DASHBOARD,
                anfragen=5000, fehler=0, p95=300.0, throughput=50.0),   # Dashboard > 250ms
            _ep("/api/v1/annahme", EndpointKategorie.ANNAHME,
                anfragen=3000, fehler=0, p95=3800.0, throughput=30.0),  # p95 avg = (300+3800)/2=2050 > 2000ms
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        assert result.kpi_erfuellt is False
        assert len(result.verletzte_kriterien) >= 2

    def test_alle_szenarien_konfigurierbar(self):
        """Alle Lasttest-Szenarien können instanziiert werden."""
        for szenario in LasttestSzenario:
            k = LasttestKonfiguration(
                szenario=szenario,
                gleichzeitige_user=100,
                dauer_sekunden=300,
            )
            assert k.szenario == szenario

    def test_fehlerrate_grenzwert_genau_1_pct(self):
        """Genau 1% Fehlerrate liegt auf der Grenze — noch erfüllt."""
        ergebnis = _ergebnis(user=500, eps=[
            _ep(anfragen=1000, fehler=10, p95=180.0),  # exakt 1.0%
        ])
        result = evaluate_erntepeak_sla(ergebnis)
        # 1.0% == max_fehler_rate_pct → nicht verletzt
        assert "Error Rate" not in " ".join(result.verletzte_kriterien)
