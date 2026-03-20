"""
Wave 85 — E2E Prozesskette ohne Medienbruch (Gap 001)

Tests für ProzessGlied, E2EProzesskette, validate_e2e_kette(),
MedienbruchBefund und evaluate_e2e_kpi().

Gap 001: ≥95% Vorgänge ohne manuelle Nebenliste
"""
from __future__ import annotations

import pytest

from app.core.e2e_process_chain_contracts import (
    E2EKettenKpiReport,
    E2EProzesskette,
    GliedStatus,
    KettenStatus,
    KettenValidierungsResult,
    MedienbruchTyp,
    ProzessGlied,
    ProzessGliedTyp,
    evaluate_e2e_kpi,
    validate_e2e_kette,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _glied(
    typ: ProzessGliedTyp,
    referenz: str = "REF-001",
    parent: str = "PARENT-001",
    status: GliedStatus = GliedStatus.ABGESCHLOSSEN,
) -> ProzessGlied:
    return ProzessGlied(
        glied_id=f"G-{typ.value}",
        typ=typ,
        tenant_id="T-001",
        referenz_id=referenz,
        parent_referenz_id=parent,
        status=status,
        zeitstempel="2026-03-20T08:00:00Z",
    )


def _vollstaendige_kette(tenant_id: str = "T-001") -> E2EProzesskette:
    """Kette mit allen 4 Gliedern, kein Medienbruch."""
    kette = E2EProzesskette(ketten_id="K-001", tenant_id=tenant_id)
    kette.glieder = [
        _glied(ProzessGliedTyp.KONTRAKT, "KNR-001", ""),      # Anfang, kein Parent
        _glied(ProzessGliedTyp.ANNAHME,  "ANR-001", "KNR-001"),
        _glied(ProzessGliedTyp.QUALITAET, "QNR-001", "ANR-001"),
        _glied(ProzessGliedTyp.SETTLEMENT, "SNR-001", "QNR-001"),
    ]
    return kette


# ---------------------------------------------------------------------------
# TestProzessGlied
# ---------------------------------------------------------------------------

class TestProzessGlied:
    def test_hat_eltern_referenz_true(self):
        g = _glied(ProzessGliedTyp.ANNAHME, parent="KNR-001")
        assert g.hat_eltern_referenz is True

    def test_hat_eltern_referenz_false(self):
        g = _glied(ProzessGliedTyp.KONTRAKT, parent="")
        assert g.hat_eltern_referenz is False

    def test_ist_abgeschlossen(self):
        g = _glied(ProzessGliedTyp.ANNAHME, status=GliedStatus.ABGESCHLOSSEN)
        assert g.ist_abgeschlossen is True

    def test_nicht_abgeschlossen(self):
        g = _glied(ProzessGliedTyp.ANNAHME, status=GliedStatus.AKTIV)
        assert g.ist_abgeschlossen is False

    def test_as_dict_vollstaendig(self):
        g = _glied(ProzessGliedTyp.QUALITAET)
        d = g.as_dict()
        assert d["typ"] == "QUALITAET"
        assert "hat_eltern_referenz" in d
        assert "ist_abgeschlossen" in d


# ---------------------------------------------------------------------------
# TestE2EProzesskette
# ---------------------------------------------------------------------------

class TestE2EProzesskette:
    def test_vollstaendige_kette(self):
        kette = _vollstaendige_kette()
        assert kette.ist_vollstaendig is True

    def test_unvollstaendige_kette(self):
        kette = E2EProzesskette(ketten_id="K-002", tenant_id="T-001")
        kette.glieder = [
            _glied(ProzessGliedTyp.KONTRAKT, parent=""),
            _glied(ProzessGliedTyp.ANNAHME, parent="KNR-001"),
        ]
        assert kette.ist_vollstaendig is False

    def test_fortschritt_pct_vollstaendig(self):
        kette = _vollstaendige_kette()
        assert kette.fortschritt_pct == 100.0

    def test_fortschritt_pct_zwei_glieder(self):
        kette = E2EProzesskette(ketten_id="K-003", tenant_id="T-001")
        kette.glieder = [
            _glied(ProzessGliedTyp.KONTRAKT, parent=""),
            _glied(ProzessGliedTyp.ANNAHME, parent="KNR-001"),
        ]
        assert kette.fortschritt_pct == 50.0

    def test_get_glied_vorhanden(self):
        kette = _vollstaendige_kette()
        g = kette.get_glied(ProzessGliedTyp.SETTLEMENT)
        assert g is not None
        assert g.typ == ProzessGliedTyp.SETTLEMENT

    def test_get_glied_nicht_vorhanden(self):
        kette = E2EProzesskette(ketten_id="K-004", tenant_id="T-001")
        assert kette.get_glied(ProzessGliedTyp.QUALITAET) is None

    def test_abgeschlossene_glieder(self):
        kette = _vollstaendige_kette()
        assert kette.abgeschlossene_glieder == 4

    def test_as_dict_vollstaendig(self):
        kette = _vollstaendige_kette()
        d = kette.as_dict()
        assert d["ist_vollstaendig"] is True
        assert d["fortschritt_pct"] == 100.0
        assert "glieder" in d


# ---------------------------------------------------------------------------
# TestValidateE2EKette
# ---------------------------------------------------------------------------

class TestValidateE2EKette:
    def test_vollstaendige_kette_kein_bruch(self):
        kette = _vollstaendige_kette()
        result = validate_e2e_kette(kette)
        assert result.status == KettenStatus.VOLLSTAENDIG
        assert result.hat_medienbruch is False
        assert result.kpi_erfuellt is True

    def test_kette_ohne_elternreferenz_annahme(self):
        """ANNAHME ohne Referenz auf KONTRAKT → Medienbruch."""
        kette = E2EProzesskette(ketten_id="K-BRUCH", tenant_id="T-001")
        kette.glieder = [
            _glied(ProzessGliedTyp.KONTRAKT, parent=""),
            _glied(ProzessGliedTyp.ANNAHME, parent=""),  # fehlt!
            _glied(ProzessGliedTyp.QUALITAET, parent="ANR-001"),
            _glied(ProzessGliedTyp.SETTLEMENT, parent="QNR-001"),
        ]
        result = validate_e2e_kette(kette)
        assert result.hat_medienbruch is True
        assert any(b.bruch_typ == MedienbruchTyp.FEHLENDE_UEBERGABE
                   for b in result.medienbrueche)

    def test_uebersprungenes_glied_ist_medienbruch(self):
        """QUALITAET als UEBERSPRUNGEN → Medienbruch MANUELLE_NEBENLISTE."""
        kette = E2EProzesskette(ketten_id="K-SKIP", tenant_id="T-001")
        kette.glieder = [
            _glied(ProzessGliedTyp.KONTRAKT, parent=""),
            _glied(ProzessGliedTyp.ANNAHME, parent="KNR-001"),
            _glied(ProzessGliedTyp.QUALITAET, parent="ANR-001",
                   status=GliedStatus.UEBERSPRUNGEN),
            _glied(ProzessGliedTyp.SETTLEMENT, parent="QNR-001"),
        ]
        result = validate_e2e_kette(kette)
        assert result.hat_medienbruch is True
        assert any(b.bruch_typ == MedienbruchTyp.MANUELLE_NEBENLISTE
                   for b in result.medienbrueche)

    def test_teilweise_kette_kein_bruch(self):
        """Kette mit KONTRAKT + ANNAHME → TEILWEISE, kein Medienbruch."""
        kette = E2EProzesskette(ketten_id="K-TEIL", tenant_id="T-001")
        kette.glieder = [
            _glied(ProzessGliedTyp.KONTRAKT, parent=""),
            _glied(ProzessGliedTyp.ANNAHME, parent="KNR-001"),
        ]
        result = validate_e2e_kette(kette)
        assert result.status == KettenStatus.TEILWEISE
        assert result.hat_medienbruch is False

    def test_mehrere_medienbrueche(self):
        kette = E2EProzesskette(ketten_id="K-MULTI", tenant_id="T-001")
        kette.glieder = [
            _glied(ProzessGliedTyp.KONTRAKT, parent=""),
            _glied(ProzessGliedTyp.ANNAHME, parent=""),          # Bruch 1
            _glied(ProzessGliedTyp.QUALITAET, parent="",
                   status=GliedStatus.UEBERSPRUNGEN),            # Bruch 2
            _glied(ProzessGliedTyp.SETTLEMENT, parent="QNR-001"),
        ]
        result = validate_e2e_kette(kette)
        assert len(result.medienbrueche) >= 2

    def test_status_unterbrochen_bei_bruch(self):
        kette = E2EProzesskette(ketten_id="K-UNT", tenant_id="T-001")
        kette.glieder = [
            _glied(ProzessGliedTyp.KONTRAKT, parent=""),
            _glied(ProzessGliedTyp.ANNAHME, parent=""),  # Bruch
            _glied(ProzessGliedTyp.QUALITAET, parent="ANR-001"),
            _glied(ProzessGliedTyp.SETTLEMENT, parent="QNR-001"),
        ]
        result = validate_e2e_kette(kette)
        assert result.status == KettenStatus.UNTERBROCHEN

    def test_as_dict_vollstaendig(self):
        result = validate_e2e_kette(_vollstaendige_kette())
        d = result.as_dict()
        assert "status" in d
        assert "hat_medienbruch" in d
        assert "kpi_erfuellt" in d
        assert "medienbrueche" in d

    def test_empfehlung_bei_fehlender_uebergabe(self):
        kette = E2EProzesskette(ketten_id="K-EMP", tenant_id="T-001")
        kette.glieder = [
            _glied(ProzessGliedTyp.KONTRAKT, parent=""),
            _glied(ProzessGliedTyp.ANNAHME, parent=""),
        ]
        result = validate_e2e_kette(kette)
        bruch = result.medienbrueche[0]
        assert bruch.empfehlung != ""


# ---------------------------------------------------------------------------
# TestEvaluateE2EKpi
# ---------------------------------------------------------------------------

class TestEvaluateE2EKpi:
    def test_kpi_erfuellt_bei_100_pct(self):
        ketten = [_vollstaendige_kette(f"T-{i}") for i in range(10)]
        validierungen = [validate_e2e_kette(k) for k in ketten]
        # Alle gleichen Tenant überschreiben — simuliere mehrere Vorgänge
        for v in validierungen:
            v.ketten_id = f"K-{id(v)}"
        report = evaluate_e2e_kpi("T-001", validierungen)
        assert report.kpi_erfuellt is True
        assert report.kpi_pct == 100.0

    def test_kpi_nicht_erfuellt_unter_95(self):
        ohne_bruch = [
            KettenValidierungsResult(f"K-{i}", KettenStatus.VOLLSTAENDIG)
            for i in range(94)
        ]
        mit_bruch = [
            KettenValidierungsResult(
                f"K-B-{i}", KettenStatus.UNTERBROCHEN,
                medienbrueche=[
                    type("B", (), {"as_dict": lambda s: {}})()  # dummy
                ],
            )
            for i in range(6)
        ]
        # Manuell setzen statt Konstruktor (kein __post_init__ nötig)
        for v in mit_bruch:
            from app.core.e2e_process_chain_contracts import MedienbruchBefund
            v.medienbrueche = [MedienbruchBefund(
                bruch_typ=MedienbruchTyp.MANUELLE_NEBENLISTE,
                betroffenes_glied=ProzessGliedTyp.ANNAHME,
                beschreibung="Test",
            )]
        alle = ohne_bruch + mit_bruch
        report = evaluate_e2e_kpi("T-001", alle)
        assert report.kpi_erfuellt is False
        assert report.kpi_pct < 95.0

    def test_leere_validierungen_ergeben_100(self):
        report = evaluate_e2e_kpi("T-001", [])
        assert report.kpi_pct == 100.0
        assert report.kpi_erfuellt is False  # keine Stichproben → nicht erfüllt

    def test_as_dict_vollstaendig(self):
        report = evaluate_e2e_kpi("T-001", [validate_e2e_kette(_vollstaendige_kette())])
        d = report.as_dict()
        assert "kpi_pct" in d
        assert "kpi_erfuellt" in d
        assert "gesamt_ketten" in d


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    def test_typischer_erntevorgang_ohne_bruch(self):
        """
        Simuliert: Kontrakt → Annahme (Wiegeschein) → Qualitätslabor → Settlement.
        Alle Übergaben systemseitig → kein Medienbruch.
        """
        kette = E2EProzesskette(ketten_id="ERN-2026-0042", tenant_id="T-GENOSSENSCHAFT")
        kette.glieder = [
            ProzessGlied("G-K", ProzessGliedTyp.KONTRAKT, "T-GENOSSENSCHAFT",
                         "KNR-2026-042", "", GliedStatus.ABGESCHLOSSEN, "2026-08-01T06:00:00Z"),
            ProzessGlied("G-A", ProzessGliedTyp.ANNAHME, "T-GENOSSENSCHAFT",
                         "ANR-2026-0101", "KNR-2026-042", GliedStatus.ABGESCHLOSSEN, "2026-08-01T10:30:00Z"),
            ProzessGlied("G-Q", ProzessGliedTyp.QUALITAET, "T-GENOSSENSCHAFT",
                         "QNR-2026-0101", "ANR-2026-0101", GliedStatus.ABGESCHLOSSEN, "2026-08-01T11:00:00Z"),
            ProzessGlied("G-S", ProzessGliedTyp.SETTLEMENT, "T-GENOSSENSCHAFT",
                         "SET-2026-0101", "QNR-2026-0101", GliedStatus.ABGESCHLOSSEN, "2026-08-02T08:00:00Z"),
        ]
        result = validate_e2e_kette(kette)
        assert result.kpi_erfuellt is True
        assert result.status == KettenStatus.VOLLSTAENDIG
        assert kette.fortschritt_pct == 100.0

    def test_kpi_95_pct_schwelle(self):
        """95 von 100 Ketten ohne Bruch → KPI knapp erfüllt."""
        valide = [
            KettenValidierungsResult(f"K-OK-{i}", KettenStatus.VOLLSTAENDIG)
            for i in range(95)
        ]
        from app.core.e2e_process_chain_contracts import MedienbruchBefund
        bruch_ketten = []
        for i in range(5):
            v = KettenValidierungsResult(f"K-FAIL-{i}", KettenStatus.UNTERBROCHEN)
            v.medienbrueche = [MedienbruchBefund(
                bruch_typ=MedienbruchTyp.MANUELLE_NEBENLISTE,
                betroffenes_glied=ProzessGliedTyp.QUALITAET,
                beschreibung="Excel-Nebenliste",
            )]
            bruch_ketten.append(v)
        report = evaluate_e2e_kpi("T-001", valide + bruch_ketten)
        assert report.kpi_pct == 95.0
        assert report.kpi_erfuellt is True

    def test_tenant_isolation(self):
        """Ketten verschiedener Tenants werden unabhängig bewertet."""
        k1 = _vollstaendige_kette("T-A")
        k1.ketten_id = "K-A-001"
        k2 = _vollstaendige_kette("T-B")
        k2.ketten_id = "K-B-001"
        r1 = validate_e2e_kette(k1)
        r2 = validate_e2e_kette(k2)
        assert r1.ketten_id != r2.ketten_id
        assert r1.kpi_erfuellt is True
        assert r2.kpi_erfuellt is True
