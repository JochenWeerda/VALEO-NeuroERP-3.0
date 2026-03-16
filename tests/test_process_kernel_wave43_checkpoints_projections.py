"""
Wave 43 — Workflow Checkpoint Contracts & Cross-Domain Projection Contracts
60 deterministic pytest tests; no server/database required.
"""
import datetime

import pytest

from app.core.workflow_checkpoint_contracts import (
    CheckpointIntervall,
    CheckpointRegel,
    CheckpointStatus,
    CheckpointWiederherstellung,
    WiederherstellungsErgebnis,
    WorkflowCheckpoint,
    erstelle_checkpoint,
    get_default_checkpoint_regeln,
    stelle_checkpoint_wieder_her,
)
from app.core.cross_domain_projection_contracts import (
    CrossDomainJoin,
    DomainProjection,
    KonsistenzLevel,
    ProjectionGesundheit,
    ProjectionLagStufe,
    ProjectionStatus,
    berechne_lag_stufe,
    erstelle_projektions_gesundheit,
    get_default_projektionen,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
OLD_DT = datetime.datetime(2026, 1, 1, 0, 0, 0)   # reliably old
NOW_DT = datetime.datetime.utcnow()


def _fresh_checkpoint(
    checkpoint_id="CP-001",
    workflow_instanz_id="WF-001",
    schritt_id="S-01",
    tenant_id="T-001",
    status=CheckpointStatus.GUELTIG,
    zustand=None,
    schritte_ausgefuehrt=0,
    erstellt_am=None,
):
    return WorkflowCheckpoint(
        checkpoint_id=checkpoint_id,
        workflow_instanz_id=workflow_instanz_id,
        schritt_id=schritt_id,
        status=status,
        erstellt_am=erstellt_am if erstellt_am is not None else NOW_DT,
        tenant_id=tenant_id,
        zustand=zustand or {},
        schritte_ausgefuehrt=schritte_ausgefuehrt,
    )


def _fresh_projection(
    projection_id="PR-X",
    projection_name="test_proj",
    quell_domain="agrar",
    ziel_domain="finance",
    status=ProjectionStatus.AKTUELL,
    konsistenz_level=KonsistenzLevel.STARK,
    lag_sekunden=0.0,
    tenant_id="T-001",
):
    return DomainProjection(
        projection_id=projection_id,
        projection_name=projection_name,
        quell_domain=quell_domain,
        ziel_domain=ziel_domain,
        status=status,
        letztes_event_id="EVT-X",
        letztes_update=NOW_DT,
        konsistenz_level=konsistenz_level,
        lag_sekunden=lag_sekunden,
        tenant_id=tenant_id,
    )


# ===========================================================================
# MODULE 1 — WorkflowCheckpointContracts (30 tests)
# ===========================================================================

# --- Enums ------------------------------------------------------------------

def test_checkpoint_status_values():
    values = {s.value for s in CheckpointStatus}
    assert values == {"ERSTELLT", "GUELTIG", "VERALTET", "WIEDERHERGESTELLT", "FEHLGESCHLAGEN"}


def test_checkpoint_intervall_values():
    values = {i.value for i in CheckpointIntervall}
    assert values == {"NACH_JEDEM_SCHRITT", "ALLE_5_SCHRITTE", "ALLE_10_SCHRITTE", "MANUELL"}


def test_wiederherstellungs_ergebnis_values():
    values = {e.value for e in WiederherstellungsErgebnis}
    assert values == {"ERFOLGREICH", "CHECKPOINT_VERALTET", "CHECKPOINT_FEHLERHAFT", "KEIN_CHECKPOINT"}


# --- WorkflowCheckpoint -----------------------------------------------------

def test_checkpoint_ist_gueltig_true():
    cp = _fresh_checkpoint(status=CheckpointStatus.GUELTIG)
    assert cp.ist_gueltig is True


def test_checkpoint_ist_gueltig_false_when_fehlgeschlagen():
    cp = _fresh_checkpoint(status=CheckpointStatus.FEHLGESCHLAGEN)
    assert cp.ist_gueltig is False


def test_checkpoint_ist_gueltig_false_when_veraltet_status():
    cp = _fresh_checkpoint(status=CheckpointStatus.VERALTET)
    assert cp.ist_gueltig is False


def test_checkpoint_alter_minuten_fresh():
    cp = _fresh_checkpoint(erstellt_am=datetime.datetime.utcnow())
    assert cp.alter_minuten >= 0.0
    assert cp.alter_minuten < 1.0


def test_checkpoint_alter_minuten_old():
    cp = _fresh_checkpoint(erstellt_am=OLD_DT)
    assert cp.alter_minuten > 1000


def test_checkpoint_ist_veraltet_old():
    cp = _fresh_checkpoint(erstellt_am=OLD_DT)
    assert cp.ist_veraltet(60.0) is True


def test_checkpoint_ist_veraltet_fresh():
    cp = _fresh_checkpoint(erstellt_am=datetime.datetime.utcnow())
    assert cp.ist_veraltet(60.0) is False


def test_checkpoint_ist_veraltet_custom_max():
    two_min_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=2)
    cp = _fresh_checkpoint(erstellt_am=two_min_ago)
    assert cp.ist_veraltet(1.0) is True
    assert cp.ist_veraltet(10.0) is False


def test_checkpoint_as_dict_keys():
    cp = _fresh_checkpoint(zustand={"a": 1, "b": 2}, schritte_ausgefuehrt=3)
    d = cp.as_dict()
    assert "checkpoint_id" in d
    assert "schritte_ausgefuehrt" in d
    assert "zustand_groesse" in d
    assert "ist_gueltig" in d


def test_checkpoint_as_dict_zustand_groesse():
    cp = _fresh_checkpoint(zustand={"x": 1, "y": 2, "z": 3})
    d = cp.as_dict()
    assert d["zustand_groesse"] == 3


def test_checkpoint_as_dict_schritte():
    cp = _fresh_checkpoint(schritte_ausgefuehrt=7)
    d = cp.as_dict()
    assert d["schritte_ausgefuehrt"] == 7


def test_checkpoint_as_dict_ist_gueltig_true():
    cp = _fresh_checkpoint(status=CheckpointStatus.GUELTIG)
    assert cp.as_dict()["ist_gueltig"] is True


def test_checkpoint_default_zustand_empty():
    cp = _fresh_checkpoint()
    assert cp.zustand == {}


# --- erstelle_checkpoint ----------------------------------------------------

def test_erstelle_checkpoint_status_gueltig():
    cp = erstelle_checkpoint("CP-NEW", "WF-X", "S-1", "T-1")
    assert cp.status == CheckpointStatus.GUELTIG


def test_erstelle_checkpoint_defaults_zustand():
    cp = erstelle_checkpoint("CP-NEW", "WF-X", "S-1", "T-1")
    assert cp.zustand == {}


def test_erstelle_checkpoint_with_zustand():
    cp = erstelle_checkpoint("CP-NEW", "WF-X", "S-1", "T-1", zustand={"key": "val"})
    assert cp.zustand == {"key": "val"}


def test_erstelle_checkpoint_custom_erstellt_am():
    cp = erstelle_checkpoint("CP-NEW", "WF-X", "S-1", "T-1", erstellt_am=OLD_DT)
    assert cp.erstellt_am == OLD_DT


def test_erstelle_checkpoint_schritte_ausgefuehrt():
    cp = erstelle_checkpoint("CP-NEW", "WF-X", "S-1", "T-1", schritte_ausgefuehrt=5)
    assert cp.schritte_ausgefuehrt == 5


# --- CheckpointRegel --------------------------------------------------------

def test_regel_nach_jedem_schritt_zero():
    r = CheckpointRegel("R-1", "typ", CheckpointIntervall.NACH_JEDEM_SCHRITT)
    assert r.pruefe_intervall(0) is False


def test_regel_nach_jedem_schritt_nonzero():
    r = CheckpointRegel("R-1", "typ", CheckpointIntervall.NACH_JEDEM_SCHRITT)
    assert r.pruefe_intervall(1) is True
    assert r.pruefe_intervall(7) is True


def test_regel_alle_5_schritte():
    r = CheckpointRegel("R-2", "typ", CheckpointIntervall.ALLE_5_SCHRITTE)
    assert r.pruefe_intervall(5) is True
    assert r.pruefe_intervall(10) is True
    assert r.pruefe_intervall(4) is False
    assert r.pruefe_intervall(0) is False


def test_regel_alle_10_schritte():
    r = CheckpointRegel("R-3", "typ", CheckpointIntervall.ALLE_10_SCHRITTE)
    assert r.pruefe_intervall(10) is True
    assert r.pruefe_intervall(20) is True
    assert r.pruefe_intervall(5) is False
    assert r.pruefe_intervall(0) is False


def test_regel_manuell_always_false():
    r = CheckpointRegel("R-4", "typ", CheckpointIntervall.MANUELL)
    for n in [0, 1, 5, 10, 100]:
        assert r.pruefe_intervall(n) is False


# --- get_default_checkpoint_regeln ------------------------------------------

def test_default_regeln_count():
    regeln = get_default_checkpoint_regeln()
    assert len(regeln) == 4


def test_default_regeln_ids():
    regeln = get_default_checkpoint_regeln()
    ids = [r.regel_id for r in regeln]
    assert ids == ["CR-001", "CR-002", "CR-003", "CR-004"]


def test_default_regeln_cr001():
    regeln = get_default_checkpoint_regeln()
    cr001 = next(r for r in regeln if r.regel_id == "CR-001")
    assert cr001.workflow_typ == "kontrakt_annahme"
    assert cr001.intervall == CheckpointIntervall.NACH_JEDEM_SCHRITT
    assert cr001.max_checkpoints == 5
    assert cr001.max_alter_minuten == 120.0


def test_default_regeln_cr002():
    regeln = get_default_checkpoint_regeln()
    cr002 = next(r for r in regeln if r.regel_id == "CR-002")
    assert cr002.intervall == CheckpointIntervall.ALLE_5_SCHRITTE
    assert cr002.max_checkpoints == 10


def test_default_regeln_cr004_manuell():
    regeln = get_default_checkpoint_regeln()
    cr004 = next(r for r in regeln if r.regel_id == "CR-004")
    assert cr004.intervall == CheckpointIntervall.MANUELL
    assert cr004.max_alter_minuten == 1440.0


# --- stelle_checkpoint_wieder_her -------------------------------------------

def test_wiederherstellung_fehlgeschlagen_checkpoint():
    cp = _fresh_checkpoint(status=CheckpointStatus.FEHLGESCHLAGEN)
    result = stelle_checkpoint_wieder_her("WH-1", "WF-1", cp)
    assert result.ergebnis == WiederherstellungsErgebnis.CHECKPOINT_FEHLERHAFT
    assert result.kann_fortgesetzt_werden is False


def test_wiederherstellung_veraltet_checkpoint():
    cp = _fresh_checkpoint(erstellt_am=OLD_DT)
    result = stelle_checkpoint_wieder_her("WH-2", "WF-1", cp, max_alter_minuten=60.0)
    assert result.ergebnis == WiederherstellungsErgebnis.CHECKPOINT_VERALTET
    assert result.kann_fortgesetzt_werden is False


def test_wiederherstellung_erfolgreich():
    cp = _fresh_checkpoint(erstellt_am=datetime.datetime.utcnow(), status=CheckpointStatus.GUELTIG)
    result = stelle_checkpoint_wieder_her("WH-3", "WF-1", cp, max_alter_minuten=60.0)
    assert result.ergebnis == WiederherstellungsErgebnis.ERFOLGREICH
    assert result.kann_fortgesetzt_werden is True


def test_wiederherstellung_naechster_schritt_from_zustand():
    cp = _fresh_checkpoint(
        erstellt_am=datetime.datetime.utcnow(),
        zustand={"naechster_schritt": "S-NEXT"},
    )
    result = stelle_checkpoint_wieder_her("WH-4", "WF-1", cp, max_alter_minuten=60.0)
    assert result.naechster_schritt == "S-NEXT"


def test_wiederherstellung_naechster_schritt_fallback_to_schritt_id():
    cp = _fresh_checkpoint(
        erstellt_am=datetime.datetime.utcnow(),
        schritt_id="S-FALLBACK",
        zustand={},
    )
    result = stelle_checkpoint_wieder_her("WH-5", "WF-1", cp, max_alter_minuten=60.0)
    assert result.naechster_schritt == "S-FALLBACK"


def test_wiederherstellung_kann_fortgesetzt_false_veraltet():
    cp = _fresh_checkpoint(erstellt_am=OLD_DT)
    result = stelle_checkpoint_wieder_her("WH-6", "WF-1", cp)
    assert result.kann_fortgesetzt_werden is False


# ===========================================================================
# MODULE 2 — CrossDomainProjectionContracts (30 tests)
# ===========================================================================

# --- Enums ------------------------------------------------------------------

def test_projection_status_values():
    values = {s.value for s in ProjectionStatus}
    assert values == {"AKTUELL", "VERZOEGERT", "VERALTET", "FEHLERHAFT", "AUFBAUEND"}


def test_konsistenz_level_values():
    values = {k.value for k in KonsistenzLevel}
    assert values == {"STARK", "LESEKONSISTENT", "EVENTUAL", "SNAPSHOT"}


def test_projection_lag_stufe_values():
    values = {lv.value for lv in ProjectionLagStufe}
    assert values == {"KEIN", "GERING", "MODERAT", "KRITISCH"}


# --- berechne_lag_stufe -----------------------------------------------------

def test_lag_stufe_kein():
    assert berechne_lag_stufe(0.0) == ProjectionLagStufe.KEIN
    assert berechne_lag_stufe(0.5) == ProjectionLagStufe.KEIN


def test_lag_stufe_gering():
    assert berechne_lag_stufe(1.0) == ProjectionLagStufe.GERING
    assert berechne_lag_stufe(5.0) == ProjectionLagStufe.GERING
    assert berechne_lag_stufe(9.9) == ProjectionLagStufe.GERING


def test_lag_stufe_moderat():
    assert berechne_lag_stufe(10.0) == ProjectionLagStufe.MODERAT
    assert berechne_lag_stufe(30.0) == ProjectionLagStufe.MODERAT
    assert berechne_lag_stufe(59.9) == ProjectionLagStufe.MODERAT


def test_lag_stufe_kritisch():
    assert berechne_lag_stufe(60.0) == ProjectionLagStufe.KRITISCH
    assert berechne_lag_stufe(120.0) == ProjectionLagStufe.KRITISCH
    assert berechne_lag_stufe(1000.0) == ProjectionLagStufe.KRITISCH


# --- DomainProjection -------------------------------------------------------

def test_domain_projection_ist_aktuell_true():
    p = _fresh_projection(status=ProjectionStatus.AKTUELL)
    assert p.ist_aktuell is True


def test_domain_projection_ist_aktuell_false():
    p = _fresh_projection(status=ProjectionStatus.VERZOEGERT)
    assert p.ist_aktuell is False


def test_domain_projection_lag_stufe_kein():
    p = _fresh_projection(lag_sekunden=0.3)
    assert p.lag_stufe == ProjectionLagStufe.KEIN


def test_domain_projection_lag_stufe_gering():
    p = _fresh_projection(lag_sekunden=4.2)
    assert p.lag_stufe == ProjectionLagStufe.GERING


def test_domain_projection_lag_stufe_kritisch():
    p = _fresh_projection(lag_sekunden=75.0)
    assert p.lag_stufe == ProjectionLagStufe.KRITISCH


def test_domain_projection_as_dict_keys():
    p = _fresh_projection()
    d = p.as_dict()
    assert "lag_stufe" in d
    assert "ist_aktuell" in d
    assert "projection_id" in d


def test_domain_projection_as_dict_lag_stufe_string():
    p = _fresh_projection(lag_sekunden=75.0)
    d = p.as_dict()
    assert d["lag_stufe"] == "KRITISCH"


def test_domain_projection_as_dict_ist_aktuell_false():
    p = _fresh_projection(status=ProjectionStatus.FEHLERHAFT)
    d = p.as_dict()
    assert d["ist_aktuell"] is False


# --- CrossDomainJoin --------------------------------------------------------

def test_cross_domain_join_stark_konsistent_stark():
    j = CrossDomainJoin("J-1", "PR-1", "PR-2", "INNER", ["id"], KonsistenzLevel.STARK)
    assert j.ist_stark_konsistent is True


def test_cross_domain_join_stark_konsistent_lesekonsistent():
    j = CrossDomainJoin("J-2", "PR-1", "PR-2", "LEFT", ["id"], KonsistenzLevel.LESEKONSISTENT)
    assert j.ist_stark_konsistent is True


def test_cross_domain_join_not_stark_eventual():
    j = CrossDomainJoin("J-3", "PR-1", "PR-2", "INNER", ["id"], KonsistenzLevel.EVENTUAL)
    assert j.ist_stark_konsistent is False


def test_cross_domain_join_not_stark_snapshot():
    j = CrossDomainJoin("J-4", "PR-1", "PR-2", "INNER", ["id"], KonsistenzLevel.SNAPSHOT)
    assert j.ist_stark_konsistent is False


def test_cross_domain_join_as_dict():
    j = CrossDomainJoin("J-5", "PR-A", "PR-B", "INNER", ["tenant_id", "id"], KonsistenzLevel.STARK)
    d = j.as_dict()
    assert d["ist_stark_konsistent"] is True
    assert d["join_felder"] == ["tenant_id", "id"]
    assert d["konsistenz_level"] == "STARK"


# --- get_default_projektionen -----------------------------------------------

def test_default_projektionen_count():
    projections = get_default_projektionen()
    assert len(projections) == 5


def test_default_projektionen_ids():
    projections = get_default_projektionen()
    ids = [p.projection_id for p in projections]
    assert "PR-001" in ids
    assert "PR-005" in ids


def test_default_projektion_pr001_lag_stufe():
    projections = get_default_projektionen()
    pr001 = next(p for p in projections if p.projection_id == "PR-001")
    assert pr001.lag_stufe == ProjectionLagStufe.KEIN


def test_default_projektion_pr002_lag_stufe():
    projections = get_default_projektionen()
    pr002 = next(p for p in projections if p.projection_id == "PR-002")
    assert pr002.lag_stufe == ProjectionLagStufe.GERING


def test_default_projektion_pr003_lag_stufe():
    projections = get_default_projektionen()
    pr003 = next(p for p in projections if p.projection_id == "PR-003")
    assert pr003.lag_stufe == ProjectionLagStufe.KRITISCH


def test_default_projektion_pr005_fehlerhaft():
    projections = get_default_projektionen()
    pr005 = next(p for p in projections if p.projection_id == "PR-005")
    assert pr005.status == ProjectionStatus.FEHLERHAFT


def test_default_projektionen_tenant_id():
    projections = get_default_projektionen("MY-TENANT")
    for p in projections:
        assert p.tenant_id == "MY-TENANT"


# --- ProjectionGesundheit ---------------------------------------------------

def test_projektions_gesundheit_gesamtstatus_fehlerhaft():
    projections = get_default_projektionen()
    gesundheit = erstelle_projektions_gesundheit("GH-1", projections)
    assert gesundheit.gesamtstatus == ProjectionStatus.FEHLERHAFT


def test_projektions_gesundheit_kritische_projektionen_count():
    projections = get_default_projektionen()
    gesundheit = erstelle_projektions_gesundheit("GH-2", projections)
    # PR-003 (KRITISCH lag), PR-005 (FEHLERHAFT status) = 2
    assert len(gesundheit.kritische_projektionen) == 2


def test_projektions_gesundheit_as_dict_keys():
    projections = get_default_projektionen()
    gesundheit = erstelle_projektions_gesundheit("GH-3", projections)
    d = gesundheit.as_dict()
    assert "projektionen_anzahl" in d
    assert "kritische_anzahl" in d
    assert "gesamtstatus" in d


def test_projektions_gesundheit_as_dict_projektionen_anzahl():
    projections = get_default_projektionen()
    gesundheit = erstelle_projektions_gesundheit("GH-4", projections)
    d = gesundheit.as_dict()
    assert d["projektionen_anzahl"] == 5


def test_projektions_gesundheit_as_dict_kritische_anzahl():
    projections = get_default_projektionen()
    gesundheit = erstelle_projektions_gesundheit("GH-5", projections)
    d = gesundheit.as_dict()
    assert d["kritische_anzahl"] == 2


def test_projektions_gesundheit_all_aktuell():
    projections = [
        _fresh_projection("P-A", lag_sekunden=0.1),
        _fresh_projection("P-B", lag_sekunden=0.2),
    ]
    gesundheit = erstelle_projektions_gesundheit("GH-6", projections)
    assert gesundheit.gesamtstatus == ProjectionStatus.AKTUELL
    assert len(gesundheit.kritische_projektionen) == 0


def test_projektions_gesundheit_verzoegert_from_lag():
    projections = [
        _fresh_projection("P-A", lag_sekunden=0.1),
        _fresh_projection("P-B", lag_sekunden=75.0),
    ]
    gesundheit = erstelle_projektions_gesundheit("GH-7", projections)
    assert gesundheit.gesamtstatus == ProjectionStatus.VERZOEGERT


def test_erstelle_projektions_gesundheit_geprueft_am_default():
    projections = get_default_projektionen()
    before = datetime.datetime.utcnow()
    gesundheit = erstelle_projektions_gesundheit("GH-8", projections)
    after = datetime.datetime.utcnow()
    assert before <= gesundheit.geprueft_am <= after


def test_erstelle_projektions_gesundheit_geprueft_am_custom():
    projections = get_default_projektionen()
    gesundheit = erstelle_projektions_gesundheit("GH-9", projections, geprueft_am=OLD_DT)
    assert gesundheit.geprueft_am == OLD_DT
