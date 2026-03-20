"""
test_process_kernel_wave85_e2e_process_chain.py — E2E Prozesskette (Gap 001)

Wave 85: KONTRAKT → ANNAHME → QUALITAET → SETTLEMENT ohne Medienbruch
KPI: ≥ 95% aller Ketten ohne manuellen Eingriff
"""
import pytest
from app.core.e2e_process_chain_contracts import (
    E2EKettenKpiReport,
    E2EProzesskette,
    GliedStatus,
    KettenValidierungsResult,
    MedienbruchBefund,
    MedienbruchTyp,
    ProzessGlied,
    ProzessGliedTyp,
    evaluate_e2e_kpi,
    validate_e2e_kette,
    ERLAUBTE_REIHENFOLGE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _glied(
    glied_id: str,
    typ: ProzessGliedTyp,
    parent: str = "P001",
    status: GliedStatus = GliedStatus.ABGESCHLOSSEN,
    tenant: str = "T-001",
) -> ProzessGlied:
    return ProzessGlied(
        glied_id=glied_id,
        typ=typ,
        tenant_id=tenant,
        referenz_id=f"REF-{glied_id}",
        parent_referenz_id=parent,
        status=status,
        zeitstempel="2026-03-20T06:00:00Z",
    )


def _vollstaendige_kette(kette_id: str = "K-001", tenant: str = "T-001") -> E2EProzesskette:
    """Vollständige Kette ohne Medienbruch."""
    return E2EProzesskette(
        kette_id=kette_id,
        tenant_id=tenant,
        glieder=[
            _glied("G1", ProzessGliedTyp.KONTRAKT, parent=""),
            _glied("G2", ProzessGliedTyp.ANNAHME, parent="REF-G1"),
            _glied("G3", ProzessGliedTyp.QUALITAET, parent="REF-G2"),
            _glied("G4", ProzessGliedTyp.SETTLEMENT, parent="REF-G3"),
        ],
    )


# ---------------------------------------------------------------------------
# TestProzessGlied
# ---------------------------------------------------------------------------

class TestProzessGlied:
    def test_hat_eltern_referenz_true(self):
        g = _glied("G1", ProzessGliedTyp.ANNAHME, parent="KONTRAKT-001")
        assert g.hat_eltern_referenz is True

    def test_hat_eltern_referenz_false_leer(self):
        g = _glied("G1", ProzessGliedTyp.KONTRAKT, parent="")
        assert g.hat_eltern_referenz is False

    def test_ist_uebersprungen_true(self):
        g = _glied("G1", ProzessGliedTyp.ANNAHME, status=GliedStatus.UEBERSPRUNGEN)
        assert g.ist_uebersprungen is True

    def test_ist_uebersprungen_false(self):
        g = _glied("G1", ProzessGliedTyp.ANNAHME, status=GliedStatus.ABGESCHLOSSEN)
        assert g.ist_uebersprungen is False

    def test_as_dict_keys(self):
        g = _glied("G1", ProzessGliedTyp.ANNAHME)
        d = g.as_dict()
        assert "glied_id" in d
        assert "typ" in d
        assert "hat_eltern_referenz" in d
        assert d["typ"] == "ANNAHME"


# ---------------------------------------------------------------------------
# TestE2EProzesskette
# ---------------------------------------------------------------------------

class TestE2EProzesskette:
    def test_vollstaendige_kette(self):
        kette = _vollstaendige_kette()
        assert kette.ist_vollstaendig is True

    def test_unvollstaendige_kette_ohne_settlement(self):
        kette = E2EProzesskette(
            kette_id="K-001",
            tenant_id="T-001",
            glieder=[
                _glied("G1", ProzessGliedTyp.KONTRAKT, parent=""),
                _glied("G2", ProzessGliedTyp.ANNAHME, parent="REF-G1"),
            ],
        )
        assert kette.ist_vollstaendig is False

    def test_typen_in_kette(self):
        kette = _vollstaendige_kette()
        typen = kette.typen_in_kette
        assert ProzessGliedTyp.KONTRAKT in typen
        assert ProzessGliedTyp.SETTLEMENT in typen

    def test_get_glied_gefunden(self):
        kette = _vollstaendige_kette()
        g = kette.get_glied(ProzessGliedTyp.QUALITAET)
        assert g is not None
        assert g.glied_id == "G3"

    def test_get_glied_nicht_gefunden(self):
        kette = E2EProzesskette(kette_id="K-X", tenant_id="T-001", glieder=[
            _glied("G1", ProzessGliedTyp.KONTRAKT, parent=""),
        ])
        assert kette.get_glied(ProzessGliedTyp.SETTLEMENT) is None

    def test_as_dict_vollstaendig(self):
        kette = _vollstaendige_kette()
        d = kette.as_dict()
        assert d["ist_vollstaendig"] is True
        assert len(d["glieder"]) == 4


# ---------------------------------------------------------------------------
# TestValidateE2eKette — keine Medienbrüche
# ---------------------------------------------------------------------------

class TestValidateE2eKetteOhneBreuch:
    def test_vollstaendige_kette_kein_bruch(self):
        kette = _vollstaendige_kette()
        result = validate_e2e_kette(kette)
        assert result.hat_medienbruch is False
        assert result.anzahl_brueche == 0

    def test_kontrakt_ohne_parent_ok(self):
        """Kontrakt-Glied darf parent_referenz_id leer haben."""
        kette = E2EProzesskette(kette_id="K-001", tenant_id="T-001", glieder=[
            _glied("G1", ProzessGliedTyp.KONTRAKT, parent=""),
            _glied("G2", ProzessGliedTyp.ANNAHME, parent="REF-G1"),
        ])
        result = validate_e2e_kette(kette)
        # Kein FEHLENDE_UEBERGABE für den Kontrakt
        bruch_typen = [b.typ for b in result.befunde]
        assert MedienbruchTyp.FEHLENDE_UEBERGABE not in bruch_typen


# ---------------------------------------------------------------------------
# TestValidateE2eKette — Medienbrüche erkennen
# ---------------------------------------------------------------------------

class TestValidateE2eKetteMitBruch:
    def test_manuelle_nebenliste_durch_uebersprungen(self):
        kette = E2EProzesskette(kette_id="K-001", tenant_id="T-001", glieder=[
            _glied("G1", ProzessGliedTyp.KONTRAKT, parent=""),
            _glied("G2", ProzessGliedTyp.ANNAHME, parent="REF-G1",
                   status=GliedStatus.UEBERSPRUNGEN),
            _glied("G3", ProzessGliedTyp.QUALITAET, parent="REF-G2"),
        ])
        result = validate_e2e_kette(kette)
        assert result.hat_medienbruch is True
        typen = [b.typ for b in result.befunde]
        assert MedienbruchTyp.MANUELLE_NEBENLISTE in typen

    def test_fehlende_uebergabe_annahme_ohne_parent(self):
        kette = E2EProzesskette(kette_id="K-002", tenant_id="T-001", glieder=[
            _glied("G1", ProzessGliedTyp.KONTRAKT, parent=""),
            _glied("G2", ProzessGliedTyp.ANNAHME, parent=""),   # fehlende Übergabe
            _glied("G3", ProzessGliedTyp.QUALITAET, parent="REF-G2"),
        ])
        result = validate_e2e_kette(kette)
        assert result.hat_medienbruch is True
        typen = [b.typ for b in result.befunde]
        assert MedienbruchTyp.FEHLENDE_UEBERGABE in typen

    def test_settlement_ohne_parent_bruch(self):
        kette = E2EProzesskette(kette_id="K-003", tenant_id="T-001", glieder=[
            _glied("G1", ProzessGliedTyp.SETTLEMENT, parent=""),  # Settlement ohne Vorgänger
        ])
        result = validate_e2e_kette(kette)
        assert result.hat_medienbruch is True

    def test_mehrere_brueche_gezaehlt(self):
        kette = E2EProzesskette(kette_id="K-004", tenant_id="T-001", glieder=[
            _glied("G1", ProzessGliedTyp.KONTRAKT, parent=""),
            _glied("G2", ProzessGliedTyp.ANNAHME, parent="",
                   status=GliedStatus.UEBERSPRUNGEN),  # 2 Brüche: kein parent + übersprungen
            _glied("G3", ProzessGliedTyp.QUALITAET, parent=""),  # 1 Bruch: kein parent
        ])
        result = validate_e2e_kette(kette)
        assert result.anzahl_brueche >= 2

    def test_bruch_beschreibung_nicht_leer(self):
        kette = E2EProzesskette(kette_id="K-005", tenant_id="T-001", glieder=[
            _glied("G1", ProzessGliedTyp.ANNAHME, parent=""),
        ])
        result = validate_e2e_kette(kette)
        for befund in result.befunde:
            assert befund.beschreibung != ""
            assert befund.kette_id == "K-005"


# ---------------------------------------------------------------------------
# TestEvaluateE2eKpi
# ---------------------------------------------------------------------------

class TestEvaluateE2eKpi:
    def _make_result(self, hat_bruch: bool, kette_id: str = "K-001") -> KettenValidierungsResult:
        befunde = []
        if hat_bruch:
            befunde = [MedienbruchBefund(
                kette_id=kette_id,
                glied_id="G1",
                typ=MedienbruchTyp.MANUELLE_NEBENLISTE,
                beschreibung="Test-Bruch",
            )]
        return KettenValidierungsResult(
            kette_id=kette_id,
            hat_medienbruch=hat_bruch,
            befunde=befunde,
        )

    def test_kpi_erfuellt_bei_100_pct(self):
        validierungen = [self._make_result(False, f"K-{i:03d}") for i in range(100)]
        report = evaluate_e2e_kpi("T-001", validierungen)
        assert report.kpi_erfuellt is True
        assert report.kpi_pct == 100.0
        assert report.ketten_ohne_bruch == 100

    def test_kpi_erfuellt_bei_genau_95_pct(self):
        validierungen = (
            [self._make_result(False, f"K-{i:03d}") for i in range(95)]
            + [self._make_result(True, f"K-{i:03d}") for i in range(95, 100)]
        )
        report = evaluate_e2e_kpi("T-001", validierungen)
        assert report.kpi_erfuellt is True
        assert report.kpi_pct == 95.0

    def test_kpi_nicht_erfuellt_unter_95(self):
        # 94 ok + 6 mit Bruch = 94% < 95%
        validierungen = (
            [self._make_result(False, f"K-{i:03d}") for i in range(94)]
            + [self._make_result(True, f"K-{i:03d}") for i in range(94, 100)]
        )
        report = evaluate_e2e_kpi("T-001", validierungen)
        assert report.kpi_erfuellt is False
        assert report.kpi_pct < 95.0

    def test_kpi_leere_liste(self):
        report = evaluate_e2e_kpi("T-001", [])
        assert report.gesamt_ketten == 0
        assert report.kpi_pct == 0.0
        assert report.kpi_erfuellt is False

    def test_report_as_dict(self):
        validierungen = [self._make_result(False, f"K-{i:03d}") for i in range(10)]
        report = evaluate_e2e_kpi("T-001", validierungen)
        d = report.as_dict()
        assert "kpi_erfuellt" in d
        assert "kpi_pct" in d
        assert d["tenant_id"] == "T-001"

    def test_bruch_details_nur_mit_bruch(self):
        validierungen = [
            self._make_result(False, "K-001"),
            self._make_result(True, "K-002"),
        ]
        report = evaluate_e2e_kpi("T-001", validierungen)
        assert len(report.bruch_details) == 1
        assert report.bruch_details[0].kette_id == "K-002"

    def test_benutzerdefiniertes_kpi_ziel(self):
        validierungen = [self._make_result(False, f"K-{i:03d}") for i in range(90)] + \
                        [self._make_result(True, f"K-{i:03d}") for i in range(90, 100)]
        report_95 = evaluate_e2e_kpi("T-001", validierungen, kpi_ziel_pct=95.0)
        report_85 = evaluate_e2e_kpi("T-001", validierungen, kpi_ziel_pct=85.0)
        assert report_95.kpi_erfuellt is False
        assert report_85.kpi_erfuellt is True


# ---------------------------------------------------------------------------
# TestMedienbruchBefund
# ---------------------------------------------------------------------------

class TestMedienbruchBefund:
    def test_as_dict(self):
        b = MedienbruchBefund(
            kette_id="K-001",
            glied_id="G1",
            typ=MedienbruchTyp.FEHLENDE_UEBERGABE,
            beschreibung="Test",
            schweregrad="HOCH",
        )
        d = b.as_dict()
        assert d["typ"] == "FEHLENDE_UEBERGABE"
        assert d["schweregrad"] == "HOCH"


# ---------------------------------------------------------------------------
# TestErlaubteReihenfolge
# ---------------------------------------------------------------------------

class TestErlaubteReihenfolge:
    def test_vier_typen_definiert(self):
        assert len(ERLAUBTE_REIHENFOLGE) == 4

    def test_reihenfolge_korrekt(self):
        assert ERLAUBTE_REIHENFOLGE[0] == ProzessGliedTyp.KONTRAKT
        assert ERLAUBTE_REIHENFOLGE[-1] == ProzessGliedTyp.SETTLEMENT
