"""
test_process_kernel_wave86_workflow_version_engine.py — Versionierte Workflow Engine (Gap 011)

Wave 86: Semantic Versioning für Workflows mit Migrationssicherheit
KPI: MAJOR-Änderungen immer mit genehmigungs_pflicht=True abgesichert
"""
import pytest
from app.core.workflow_version_engine_contracts import (
    AenderungsTyp,
    MigrationsStrategie,
    MigrationsSicherheitsResult,
    RisikoStufe,
    WorkflowMigrationsplan,
    WorkflowStatus,
    WorkflowVersion,
    WorkflowVersionDefinition,
    WorkflowVersionsHistorie,
    validate_migrations_sicherheit,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _version(major: int, minor: int, patch: int) -> WorkflowVersion:
    return WorkflowVersion(major=major, minor=minor, patch=patch)


def _plan(
    von: WorkflowVersion,
    zu: WorkflowVersion,
    strategie: MigrationsStrategie = MigrationsStrategie.SOFT_UPGRADE,
    risiko: RisikoStufe = RisikoStufe.NIEDRIG,
    reversibel: bool = True,
    genehmigungs_pflicht: bool = True,
    plan_id: str = "PLAN-001",
) -> WorkflowMigrationsplan:
    return WorkflowMigrationsplan(
        plan_id=plan_id,
        workflow_id="WF-ANNAHME",
        von_version=von,
        zu_version=zu,
        strategie=strategie,
        risiko=risiko,
        reversibel=reversibel,
        genehmigungs_pflicht=genehmigungs_pflicht,
        beschreibung="Testplan",
    )


def _version_def(
    major: int, minor: int, patch: int,
    status: WorkflowStatus = WorkflowStatus.FREIGEGEBEN,
    genehmigungs_pflicht: bool = False,
    workflow_id: str = "WF-001",
) -> WorkflowVersionDefinition:
    return WorkflowVersionDefinition(
        workflow_id=workflow_id,
        name="Test-Workflow",
        version=WorkflowVersion(major, minor, patch),
        status=status,
        beschreibung="Test",
        aenderungsprotokoll="Keine Änderungen",
        genehmigungs_pflicht=genehmigungs_pflicht,
        erstellt_von="admin",
        erstellt_am="2026-03-20T00:00:00Z",
    )


# ---------------------------------------------------------------------------
# TestWorkflowVersion
# ---------------------------------------------------------------------------

class TestWorkflowVersion:
    def test_als_string(self):
        v = _version(1, 2, 3)
        assert v.als_string() == "1.2.3"

    def test_negativ_major_fehler(self):
        with pytest.raises(ValueError):
            WorkflowVersion(major=-1, minor=0, patch=0)

    def test_negativ_minor_fehler(self):
        with pytest.raises(ValueError):
            WorkflowVersion(major=1, minor=-1, patch=0)

    def test_negativ_patch_fehler(self):
        with pytest.raises(ValueError):
            WorkflowVersion(major=1, minor=0, patch=-1)

    def test_aenderungstyp_major(self):
        v1 = _version(1, 0, 0)
        v2 = _version(2, 0, 0)
        assert v1.aenderungs_typ(v2) == AenderungsTyp.MAJOR

    def test_aenderungstyp_minor(self):
        v1 = _version(1, 0, 0)
        v2 = _version(1, 1, 0)
        assert v1.aenderungs_typ(v2) == AenderungsTyp.MINOR

    def test_aenderungstyp_patch(self):
        v1 = _version(1, 2, 0)
        v2 = _version(1, 2, 1)
        assert v1.aenderungs_typ(v2) == AenderungsTyp.PATCH

    def test_ist_neuer_als_true(self):
        v1 = _version(2, 0, 0)
        v2 = _version(1, 9, 9)
        assert v1.ist_neuer_als(v2) is True

    def test_ist_neuer_als_false(self):
        v1 = _version(1, 0, 0)
        v2 = _version(1, 0, 0)
        assert v1.ist_neuer_als(v2) is False

    def test_as_dict(self):
        v = _version(3, 1, 4)
        d = v.as_dict()
        assert d["major"] == 3
        assert d["als_string"] == "3.1.4"


# ---------------------------------------------------------------------------
# TestValidateMigrationsSicherheit — erlaubt
# ---------------------------------------------------------------------------

class TestValidateMigrationsSicherheitErlaubt:
    def test_patch_ohne_genehmigung_erlaubt(self):
        plan = _plan(
            _version(1, 0, 0), _version(1, 0, 1),
            genehmigungs_pflicht=False,
        )
        result = validate_migrations_sicherheit(plan)
        assert result.erlaubt is True
        assert result.blockierende_regeln == []

    def test_minor_ohne_genehmigung_erlaubt(self):
        plan = _plan(
            _version(1, 0, 0), _version(1, 1, 0),
            genehmigungs_pflicht=False,
        )
        result = validate_migrations_sicherheit(plan)
        assert result.erlaubt is True

    def test_major_mit_genehmigung_erlaubt(self):
        plan = _plan(
            _version(1, 0, 0), _version(2, 0, 0),
            genehmigungs_pflicht=True,
        )
        result = validate_migrations_sicherheit(plan)
        assert result.erlaubt is True
        assert result.blockierende_regeln == []

    def test_hard_cutover_ohne_aktive_instanzen_erlaubt(self):
        plan = _plan(
            _version(1, 0, 0), _version(1, 1, 0),
            strategie=MigrationsStrategie.HARD_CUTOVER,
        )
        result = validate_migrations_sicherheit(plan, aktive_instanzen=0)
        assert result.erlaubt is True

    def test_soft_upgrade_mit_aktiven_instanzen_erlaubt(self):
        plan = _plan(
            _version(1, 0, 0), _version(1, 1, 0),
            strategie=MigrationsStrategie.SOFT_UPGRADE,
        )
        result = validate_migrations_sicherheit(plan, aktive_instanzen=500)
        assert result.erlaubt is True


# ---------------------------------------------------------------------------
# TestValidateMigrationsSicherheit — blockiert
# ---------------------------------------------------------------------------

class TestValidateMigrationsSicherheitBlockiert:
    def test_major_ohne_genehmigung_blockiert(self):
        plan = _plan(
            _version(1, 0, 0), _version(2, 0, 0),
            genehmigungs_pflicht=False,
        )
        result = validate_migrations_sicherheit(plan)
        assert result.erlaubt is False
        assert len(result.blockierende_regeln) >= 1
        assert any("MAJOR" in r for r in result.blockierende_regeln)

    def test_hard_cutover_mit_aktiven_instanzen_blockiert(self):
        plan = _plan(
            _version(1, 0, 0), _version(1, 1, 0),
            strategie=MigrationsStrategie.HARD_CUTOVER,
        )
        result = validate_migrations_sicherheit(plan, aktive_instanzen=42)
        assert result.erlaubt is False
        assert any("HARD_CUTOVER" in r for r in result.blockierende_regeln)

    def test_major_ohne_genehmigung_und_hard_cutover_zwei_blocker(self):
        plan = _plan(
            _version(1, 0, 0), _version(2, 0, 0),
            strategie=MigrationsStrategie.HARD_CUTOVER,
            genehmigungs_pflicht=False,
        )
        result = validate_migrations_sicherheit(plan, aktive_instanzen=10)
        assert result.erlaubt is False
        assert len(result.blockierende_regeln) == 2


# ---------------------------------------------------------------------------
# TestValidateMigrationsSicherheit — Warnungen und Hinweise
# ---------------------------------------------------------------------------

class TestValidateMigrationsSicherheitHinweise:
    def test_irreversibel_hoch_risiko_hinweis(self):
        plan = _plan(
            _version(1, 0, 0), _version(1, 1, 0),
            reversibel=False,
            risiko=RisikoStufe.HOCH,
        )
        result = validate_migrations_sicherheit(plan)
        assert result.erlaubt is True
        assert len(result.hinweise) >= 1

    def test_irreversibel_kritisch_hinweis(self):
        plan = _plan(
            _version(1, 0, 0), _version(2, 0, 0),
            reversibel=False,
            risiko=RisikoStufe.KRITISCH,
            genehmigungs_pflicht=True,
        )
        result = validate_migrations_sicherheit(plan)
        assert len(result.hinweise) >= 1

    def test_reversibel_niedrig_kein_hinweis(self):
        plan = _plan(
            _version(1, 0, 0), _version(1, 0, 1),
            reversibel=True,
            risiko=RisikoStufe.NIEDRIG,
        )
        result = validate_migrations_sicherheit(plan)
        assert result.hinweise == []

    def test_parallel_run_kritisch_warnung(self):
        plan = _plan(
            _version(1, 0, 0), _version(1, 1, 0),
            strategie=MigrationsStrategie.PARALLEL_RUN,
            risiko=RisikoStufe.KRITISCH,
        )
        result = validate_migrations_sicherheit(plan)
        assert result.erlaubt is True
        assert len(result.warnungen) >= 1

    def test_result_as_dict(self):
        plan = _plan(_version(1, 0, 0), _version(1, 0, 1))
        result = validate_migrations_sicherheit(plan)
        d = result.as_dict()
        assert "erlaubt" in d
        assert "blockierende_regeln" in d
        assert "warnungen" in d


# ---------------------------------------------------------------------------
# TestWorkflowVersionsHistorie
# ---------------------------------------------------------------------------

class TestWorkflowVersionsHistorie:
    def _make_historie(self) -> WorkflowVersionsHistorie:
        return WorkflowVersionsHistorie(
            workflow_id="WF-ANNAHME",
            versionen=[
                _version_def(1, 0, 0),
                _version_def(1, 1, 0),
                _version_def(2, 0, 0),
                _version_def(2, 1, 0, status=WorkflowStatus.ENTWURF),
            ],
        )

    def test_aktuelle_version_neueste_freigegebene(self):
        h = self._make_historie()
        aktuell = h.aktuelle_version
        assert aktuell is not None
        assert aktuell.version.als_string() == "2.0.0"

    def test_aktuelle_version_none_wenn_keine_freigabe(self):
        h = WorkflowVersionsHistorie(
            workflow_id="WF-X",
            versionen=[_version_def(1, 0, 0, status=WorkflowStatus.ENTWURF)],
        )
        assert h.aktuelle_version is None

    def test_anzahl_major_releases(self):
        h = self._make_historie()
        assert h.anzahl_major_releases == 2  # 1.x.x und 2.x.x

    def test_get_version_gefunden(self):
        h = self._make_historie()
        v = h.get_version(1, 1, 0)
        assert v is not None
        assert v.version.minor == 1

    def test_get_version_nicht_gefunden(self):
        h = self._make_historie()
        assert h.get_version(9, 9, 9) is None

    def test_as_dict(self):
        h = self._make_historie()
        d = h.as_dict()
        assert d["anzahl_versionen"] == 4
        assert d["aktuelle_version"] == "2.0.0"


# ---------------------------------------------------------------------------
# TestWorkflowMigrationsplan
# ---------------------------------------------------------------------------

class TestWorkflowMigrationsplan:
    def test_aenderungstyp_aus_versionen(self):
        plan = _plan(_version(1, 0, 0), _version(2, 0, 0))
        assert plan.aenderungs_typ == AenderungsTyp.MAJOR

    def test_as_dict(self):
        plan = _plan(_version(1, 0, 0), _version(1, 1, 0))
        d = plan.as_dict()
        assert d["von_version"] == "1.0.0"
        assert d["zu_version"] == "1.1.0"
        assert d["aenderungs_typ"] == "MINOR"
