"""
Wave 86 — Versionierte Workflow Engine mit Migrationen (Gap 011)

Tests für WorkflowVersion, WorkflowDefinition, WorkflowVersionRegistry,
MigrationsPlan, MigrationsSchritt und validate_migrations_sicherheit().

Gap 011: 0 ungeplante Workflow-Brüche bei Releases
"""
from __future__ import annotations

import pytest

from app.core.workflow_version_engine_contracts import (
    AenderungsTyp,
    BreakingChangeRisiko,
    MigrationStatus,
    MigrationStrategie,
    MigrationsSchritt,
    MigrationsPlan,
    MigrationsSicherheitsResult,
    WorkflowDefinition,
    WorkflowVersion,
    WorkflowVersionRegistry,
    validate_migrations_sicherheit,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _v(major: int, minor: int = 0, patch: int = 0) -> WorkflowVersion:
    return WorkflowVersion(major=major, minor=minor, patch=patch)


def _def(name: str = "ernte_annahme", major: int = 1, minor: int = 0, patch: int = 0,
         schritte: list[str] | None = None) -> WorkflowDefinition:
    return WorkflowDefinition(
        name=name,
        version=_v(major, minor, patch),
        schritte=schritte or ["KONTRAKT", "ANNAHME", "QUALITAET", "SETTLEMENT"],
        schema_hash=f"sha256:{major}{minor}{patch}abc",
    )


def _schritt(
    von: WorkflowVersion,
    bis: WorkflowVersion,
    strategie: MigrationStrategie = MigrationStrategie.DUAL_RUN,
    risiko: BreakingChangeRisiko = BreakingChangeRisiko.KEIN,
    umkehrbar: bool = True,
) -> MigrationsSchritt:
    return MigrationsSchritt(
        schritt_id=f"S-{von}->{bis}",
        von_version=von,
        bis_version=bis,
        strategie=strategie,
        transformation_beschreibung="Test-Transformation",
        ist_umkehrbar=umkehrbar,
        risiko=risiko,
    )


def _plan(
    von: WorkflowVersion,
    bis: WorkflowVersion,
    schritte: list[MigrationsSchritt] | None = None,
    genehmigt: bool = False,
) -> MigrationsPlan:
    return MigrationsPlan(
        plan_id=f"PLAN-{von}->{bis}",
        workflow_name="ernte_annahme",
        von_version=von,
        bis_version=bis,
        schritte=schritte or [],
        genehmigungs_pflicht=genehmigt,
    )


# ---------------------------------------------------------------------------
# TestWorkflowVersion
# ---------------------------------------------------------------------------

class TestWorkflowVersion:
    def test_str_darstellung(self):
        v = _v(1, 2, 3)
        assert str(v) == "1.2.3"

    def test_vergleich_kleiner(self):
        assert _v(1, 0, 0) < _v(2, 0, 0)
        assert _v(1, 0, 0) < _v(1, 1, 0)
        assert _v(1, 0, 0) < _v(1, 0, 1)

    def test_vergleich_gleich(self):
        assert _v(1, 2, 3) == _v(1, 2, 3)

    def test_kompatibel_gleiche_major(self):
        assert _v(1, 0, 0).ist_kompatibel_mit(_v(1, 5, 3)) is True

    def test_nicht_kompatibel_verschiedene_major(self):
        assert _v(1, 0, 0).ist_kompatibel_mit(_v(2, 0, 0)) is False

    def test_aenderungs_typ_patch(self):
        assert _v(1, 0, 0).aenderungs_typ(_v(1, 0, 1)) == AenderungsTyp.PATCH

    def test_aenderungs_typ_minor(self):
        assert _v(1, 0, 0).aenderungs_typ(_v(1, 1, 0)) == AenderungsTyp.MINOR

    def test_aenderungs_typ_major(self):
        assert _v(1, 0, 0).aenderungs_typ(_v(2, 0, 0)) == AenderungsTyp.MAJOR

    def test_as_dict(self):
        d = _v(2, 3, 4).as_dict()
        assert d["major"] == 2
        assert d["minor"] == 3
        assert d["patch"] == 4
        assert d["version_str"] == "2.3.4"


# ---------------------------------------------------------------------------
# TestWorkflowDefinition
# ---------------------------------------------------------------------------

class TestWorkflowDefinition:
    def test_version_key(self):
        d = _def("ernte", 1, 2, 3)
        assert d.version_key == "ernte@1.2.3"

    def test_as_dict(self):
        d = _def("ernte", 1, 0, 0)
        result = d.as_dict()
        assert result["name"] == "ernte"
        assert "version" in result
        assert "schritte" in result
        assert "schema_hash" in result


# ---------------------------------------------------------------------------
# TestWorkflowVersionRegistry
# ---------------------------------------------------------------------------

class TestWorkflowVersionRegistry:
    def test_register_und_get_latest(self):
        registry = WorkflowVersionRegistry()
        registry.register(_def("wf", 1, 0, 0))
        registry.register(_def("wf", 1, 1, 0))
        latest = registry.get_latest("wf")
        assert latest.version == _v(1, 1, 0)

    def test_get_spezifische_version(self):
        registry = WorkflowVersionRegistry()
        registry.register(_def("wf", 1, 0, 0))
        registry.register(_def("wf", 2, 0, 0))
        v = registry.get_version("wf", _v(1, 0, 0))
        assert v is not None
        assert v.version == _v(1, 0, 0)

    def test_get_unbekannte_version_gibt_none(self):
        registry = WorkflowVersionRegistry()
        registry.register(_def("wf", 1, 0, 0))
        assert registry.get_version("wf", _v(9, 9, 9)) is None

    def test_get_unbekannter_workflow_gibt_none(self):
        registry = WorkflowVersionRegistry()
        assert registry.get_latest("unbekannt") is None

    def test_duplikat_raises(self):
        registry = WorkflowVersionRegistry()
        registry.register(_def("wf", 1, 0, 0))
        with pytest.raises(ValueError, match="bereits registriert"):
            registry.register(_def("wf", 1, 0, 0))

    def test_alle_versionen_sortiert(self):
        registry = WorkflowVersionRegistry()
        registry.register(_def("wf", 1, 2, 0))
        registry.register(_def("wf", 1, 0, 0))
        registry.register(_def("wf", 2, 0, 0))
        versionen = registry.alle_versionen("wf")
        assert versionen == sorted(versionen)

    def test_anzahl_workflows(self):
        registry = WorkflowVersionRegistry()
        registry.register(_def("wf1", 1, 0, 0))
        registry.register(_def("wf2", 1, 0, 0))
        assert registry.anzahl_workflows == 2

    def test_anzahl_definitionen_gesamt(self):
        registry = WorkflowVersionRegistry()
        registry.register(_def("wf", 1, 0, 0))
        registry.register(_def("wf", 1, 1, 0))
        registry.register(_def("wf2", 1, 0, 0))
        assert registry.anzahl_definitionen_gesamt == 3

    def test_registrierte_workflows(self):
        registry = WorkflowVersionRegistry()
        registry.register(_def("ernte", 1, 0, 0))
        registry.register(_def("settlement", 1, 0, 0))
        namen = registry.registrierte_workflows()
        assert "ernte" in namen
        assert "settlement" in namen


# ---------------------------------------------------------------------------
# TestMigrationsSchritt
# ---------------------------------------------------------------------------

class TestMigrationsSchritt:
    def test_as_dict(self):
        s = _schritt(_v(1, 0, 0), _v(1, 1, 0))
        d = s.as_dict()
        assert d["von_version"] == "1.0.0"
        assert d["bis_version"] == "1.1.0"
        assert d["strategie"] == MigrationStrategie.DUAL_RUN.value

    def test_risiko_werte(self):
        for risiko in BreakingChangeRisiko:
            s = _schritt(_v(1), _v(2), risiko=risiko)
            assert s.risiko == risiko


# ---------------------------------------------------------------------------
# TestMigrationsPlan
# ---------------------------------------------------------------------------

class TestMigrationsPlan:
    def test_ist_breaking_major(self):
        plan = _plan(_v(1, 0, 0), _v(2, 0, 0))
        assert plan.ist_breaking is True

    def test_nicht_breaking_minor(self):
        plan = _plan(_v(1, 0, 0), _v(1, 1, 0))
        assert plan.ist_breaking is False

    def test_anzahl_schritte(self):
        plan = _plan(_v(1), _v(2), schritte=[
            _schritt(_v(1), _v(2)),
            _schritt(_v(1), _v(2)),
        ])
        assert plan.anzahl_schritte == 2

    def test_hoechstes_risiko_hoch(self):
        plan = _plan(_v(1), _v(2), schritte=[
            _schritt(_v(1), _v(2), risiko=BreakingChangeRisiko.NIEDRIG),
            _schritt(_v(1), _v(2), risiko=BreakingChangeRisiko.HOCH),
        ])
        assert plan.hoechstes_risiko == BreakingChangeRisiko.HOCH

    def test_hoechstes_risiko_leer(self):
        plan = _plan(_v(1), _v(2))
        assert plan.hoechstes_risiko == BreakingChangeRisiko.KEIN

    def test_as_dict(self):
        plan = _plan(_v(1, 0, 0), _v(2, 0, 0))
        d = plan.as_dict()
        assert d["ist_breaking"] is True
        assert "status" in d
        assert "genehmigungs_pflicht" in d


# ---------------------------------------------------------------------------
# TestValidateMigrationsSicherheit
# ---------------------------------------------------------------------------

class TestValidateMigrationsSicherheit:
    def test_patch_migration_ist_sicher(self):
        plan = _plan(_v(1, 0, 0), _v(1, 0, 1), schritte=[
            _schritt(_v(1, 0, 0), _v(1, 0, 1), MigrationStrategie.IN_PLACE),
        ])
        result = validate_migrations_sicherheit(plan)
        assert result.ist_sicher is True
        assert result.kpi_erfuellt is True

    def test_major_ohne_genehmigung_nicht_sicher(self):
        plan = _plan(_v(1, 0, 0), _v(2, 0, 0), genehmigt=False, schritte=[
            _schritt(_v(1), _v(2), risiko=BreakingChangeRisiko.HOCH),
        ])
        result = validate_migrations_sicherheit(plan)
        assert result.ist_sicher is False
        assert result.kpi_erfuellt is False
        assert len(result.blockierende_fehler) > 0

    def test_major_mit_genehmigung_ist_sicher(self):
        plan = _plan(_v(1, 0, 0), _v(2, 0, 0), genehmigt=True, schritte=[
            _schritt(_v(1), _v(2), MigrationStrategie.DUAL_RUN,
                     BreakingChangeRisiko.HOCH),
        ])
        result = validate_migrations_sicherheit(plan)
        assert result.ist_sicher is True

    def test_hard_cutover_mit_aktiven_instanzen_blockiert(self):
        plan = _plan(_v(1), _v(2), genehmigt=True, schritte=[
            _schritt(_v(1), _v(2), MigrationStrategie.HARD_CUTOVER),
        ])
        result = validate_migrations_sicherheit(plan, aktive_instanzen=42)
        assert result.ist_sicher is False
        assert any("HARD_CUTOVER" in f for f in result.blockierende_fehler)

    def test_hard_cutover_ohne_instanzen_ok(self):
        plan = _plan(_v(1), _v(2), genehmigt=True, schritte=[
            _schritt(_v(1), _v(2), MigrationStrategie.HARD_CUTOVER),
        ])
        result = validate_migrations_sicherheit(plan, aktive_instanzen=0)
        assert result.ist_sicher is True

    def test_nicht_umkehrbarer_hoch_risiko_schritt_warnung(self):
        plan = _plan(_v(1), _v(2), genehmigt=True, schritte=[
            _schritt(_v(1), _v(2), risiko=BreakingChangeRisiko.HOCH, umkehrbar=False),
        ])
        result = validate_migrations_sicherheit(plan)
        assert result.ist_sicher is True
        assert len(result.hinweise) > 0

    def test_leerer_plan_hat_hinweis(self):
        plan = _plan(_v(1, 0, 0), _v(1, 0, 1))
        result = validate_migrations_sicherheit(plan)
        assert result.ist_sicher is True
        assert any("NOOP" in h for h in result.hinweise)

    def test_as_dict(self):
        plan = _plan(_v(1), _v(1, 1, 0))
        result = validate_migrations_sicherheit(plan)
        d = result.as_dict()
        assert "ist_sicher" in d
        assert "risiko" in d
        assert "kpi_erfuellt" in d


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    def test_release_ohne_bruch_patch_update(self):
        """
        Patch-Release: 1.0.0 → 1.0.1
        In-Place, kein Breaking Change, kein Bruch.
        """
        registry = WorkflowVersionRegistry()
        registry.register(_def("ernte_annahme", 1, 0, 0))
        registry.register(_def("ernte_annahme", 1, 0, 1))

        plan = _plan(_v(1, 0, 0), _v(1, 0, 1), schritte=[
            _schritt(_v(1, 0, 0), _v(1, 0, 1), MigrationStrategie.IN_PLACE),
        ])
        result = validate_migrations_sicherheit(plan)
        assert result.kpi_erfuellt is True
        assert result.ist_sicher is True

    def test_major_release_dual_run(self):
        """
        Major-Release: 1.x → 2.0.0
        DUAL_RUN bis alle Instanzen beendet → kein Bruch.
        """
        registry = WorkflowVersionRegistry()
        registry.register(_def("ernte_annahme", 1, 0, 0))
        registry.register(_def("ernte_annahme", 2, 0, 0))

        plan = _plan(_v(1, 0, 0), _v(2, 0, 0), genehmigt=True, schritte=[
            _schritt(_v(1, 0, 0), _v(2, 0, 0),
                     MigrationStrategie.DUAL_RUN,
                     BreakingChangeRisiko.HOCH),
        ])
        result = validate_migrations_sicherheit(plan, aktive_instanzen=150)
        assert result.ist_sicher is True
        assert result.kpi_erfuellt is True

    def test_registry_liefert_versionshistorie(self):
        """Registry zeigt vollständige Versionshistorie eines Workflows."""
        registry = WorkflowVersionRegistry()
        for major, minor, patch in [(1, 0, 0), (1, 1, 0), (1, 2, 0), (2, 0, 0)]:
            registry.register(_def("settlement", major, minor, patch))
        versionen = registry.alle_versionen("settlement")
        assert len(versionen) == 4
        assert versionen[0] == _v(1, 0, 0)
        assert versionen[-1] == _v(2, 0, 0)

    def test_kein_unerwarteter_bruch_bei_geplanter_migration(self):
        """
        Alle 3 Migrations-Szenarien (Patch/Minor/Major) geplant
        → alle erfüllen KPI wenn korrekt konfiguriert.
        """
        szenarien = [
            (_v(1, 0, 0), _v(1, 0, 1), False, MigrationStrategie.IN_PLACE, BreakingChangeRisiko.KEIN),
            (_v(1, 0, 0), _v(1, 1, 0), False, MigrationStrategie.DUAL_RUN, BreakingChangeRisiko.NIEDRIG),
            (_v(1, 0, 0), _v(2, 0, 0), True,  MigrationStrategie.DUAL_RUN, BreakingChangeRisiko.HOCH),
        ]
        for von, bis, genehmigt, strategie, risiko in szenarien:
            plan = _plan(von, bis, genehmigt=genehmigt, schritte=[
                _schritt(von, bis, strategie, risiko),
            ])
            result = validate_migrations_sicherheit(plan)
            assert result.kpi_erfuellt is True, f"Szenario {von}→{bis} fehlgeschlagen"
