"""
Wave 40 — Workflow-Versionierung & Canonical Audit Trail
60 deterministische Pytest-Tests (keine Mocks, kein Server, keine DB).

Module:
  - app.core.workflow_versioning_contracts
  - app.core.canonical_process_audit_trail
"""
from __future__ import annotations

from datetime import datetime

import pytest

# ---------------------------------------------------------------------------
# Imports unter Test
# ---------------------------------------------------------------------------
from app.core.workflow_versioning_contracts import (
    MigrationsErgebnis,
    MigrationsRegel,
    MigrationsStatus,
    MigrationsTyp,
    SandboxModus,
    SandboxVersionsRegel,
    WorkflowDefinition,
    WorkflowDefinitionsStatus,
    WorkflowInstanzReferenz,
    WorkflowInstanzStatus,
    ermittle_aktive_definition,
    get_default_migrationsregeln,
    get_default_sandbox_regeln,
    get_default_workflow_definitionen,
    pruefe_migration,
)
from app.core.canonical_process_audit_trail import (
    AuditEintrag,
    AuditEreignisTyp,
    AuditIntegritaetsStatus,
    AuditKategorie,
    AuditKette,
    GoBDRelevanz,
    baue_beispiel_audit_kette,
    erstelle_audit_eintrag,
)


# ===========================================================================
# Hilfsdaten
# ===========================================================================

_BASIS = datetime(2026, 1, 1, 12, 0, 0)


def _make_definition(
    definition_id: str = "WD-TEST",
    workflow_typ: str = "test_workflow",
    version: str = "1.0.0",
    status: WorkflowDefinitionsStatus = WorkflowDefinitionsStatus.AKTIV,
    tenant_id: str = "",
    schritte: list[str] | None = None,
) -> WorkflowDefinition:
    return WorkflowDefinition(
        definition_id=definition_id,
        workflow_typ=workflow_typ,
        version=version,
        status=status,
        erstellt_am=_BASIS,
        tenant_id=tenant_id,
        beschreibung="Test-Definition",
        schritte=schritte or ["S1", "S2", "S3"],
    )


def _make_instanz(
    instanz_id: str = "INST-001",
    definition_id: str = "WD-TEST",
    versions_snapshot: str = "abc123",
    instanz_status: WorkflowInstanzStatus = WorkflowInstanzStatus.LAUFEND,
    tenant_id: str = "",
    migrationspfad: list[str] | None = None,
) -> WorkflowInstanzReferenz:
    return WorkflowInstanzReferenz(
        instanz_id=instanz_id,
        definition_id=definition_id,
        versions_snapshot=versions_snapshot,
        gestartet_am=_BASIS,
        instanz_status=instanz_status,
        tenant_id=tenant_id,
        migrationspfad=migrationspfad or [],
    )


def _make_audit_eintrag(
    eintrag_id: str = "AE-001",
    ereignis_typ: AuditEreignisTyp = AuditEreignisTyp.COMMAND_AUSGEFUEHRT,
    kategorie: AuditKategorie = AuditKategorie.PROZESS,
    vorgaenger_hash: str = "",
    gobd_relevanz: GoBDRelevanz = GoBDRelevanz.NICHT_RELEVANT,
) -> AuditEintrag:
    return AuditEintrag(
        eintrag_id=eintrag_id,
        ereignis_typ=ereignis_typ,
        kategorie=kategorie,
        zeitstempel=_BASIS,
        aktor_id="user-test",
        tenant_id="TENANT-001",
        objekt_typ="Kontrakt",
        objekt_id="KT-001",
        beschreibung="Test-Eintrag",
        gobd_relevanz=gobd_relevanz,
        vorgaenger_hash=vorgaenger_hash,
    )


# ===========================================================================
# Teil 1: WorkflowDefinition (14 Tests)
# ===========================================================================

def test_wf01_workflow_definition_erstellt():
    """WorkflowDefinition lässt sich instanziieren."""
    d = _make_definition()
    assert d.definition_id == "WD-TEST"
    assert d.workflow_typ == "test_workflow"
    assert d.version == "1.0.0"


def test_wf02_ist_aktiv_true_wenn_aktiv():
    d = _make_definition(status=WorkflowDefinitionsStatus.AKTIV)
    assert d.ist_aktiv is True


def test_wf03_ist_aktiv_false_fuer_nicht_aktive_status():
    for s in (
        WorkflowDefinitionsStatus.ENTWURF,
        WorkflowDefinitionsStatus.VERALTET,
        WorkflowDefinitionsStatus.ARCHIVIERT,
    ):
        assert _make_definition(status=s).ist_aktiv is False


def test_wf04_versions_hash_ist_16_zeichen():
    d = _make_definition()
    assert len(d.versions_hash) == 16


def test_wf05_versions_hash_deterministisch():
    d1 = _make_definition()
    d2 = _make_definition()
    assert d1.versions_hash == d2.versions_hash


def test_wf06_versions_hash_aendert_sich_bei_anderen_schritten():
    d1 = _make_definition(schritte=["S1", "S2"])
    d2 = _make_definition(schritte=["S1", "S2", "S3"])
    assert d1.versions_hash != d2.versions_hash


def test_wf07_versions_hash_schritt_reihenfolge_egal():
    """Schritte werden vor Hashing sortiert."""
    d1 = _make_definition(schritte=["S1", "S2", "S3"])
    d2 = _make_definition(schritte=["S3", "S1", "S2"])
    assert d1.versions_hash == d2.versions_hash


def test_wf08_versions_hash_aendert_sich_bei_anderer_version():
    d1 = _make_definition(version="1.0.0")
    d2 = _make_definition(version="2.0.0")
    assert d1.versions_hash != d2.versions_hash


def test_wf09_as_dict_enthaelt_schritte_anzahl():
    d = _make_definition(schritte=["S1", "S2", "S3"])
    result = d.as_dict()
    assert result["schritte_anzahl"] == 3


def test_wf10_as_dict_enthaelt_versions_hash():
    d = _make_definition()
    result = d.as_dict()
    assert "versions_hash" in result
    assert result["versions_hash"] == d.versions_hash


def test_wf11_as_dict_status_als_string():
    d = _make_definition(status=WorkflowDefinitionsStatus.AKTIV)
    assert d.as_dict()["status"] == "AKTIV"


def test_wf12_as_dict_erstellt_am_isoformat():
    d = _make_definition()
    assert d.as_dict()["erstellt_am"] == _BASIS.isoformat()


def test_wf13_instanz_wurde_migriert_false_wenn_kein_pfad():
    i = _make_instanz(migrationspfad=[])
    assert i.wurde_migriert is False


def test_wf14_instanz_wurde_migriert_true_wenn_pfad_nicht_leer():
    i = _make_instanz(migrationspfad=["WD-OLD"])
    assert i.wurde_migriert is True


# ===========================================================================
# Teil 2: MigrationsRegel & MigrationsErgebnis (6 Tests)
# ===========================================================================

def test_wf15_migrations_regel_ist_zulaessig_kompatibel():
    r = MigrationsRegel("R1", "1.0.0", "2.0.0", "typ", MigrationsTyp.KOMPATIBEL)
    assert r.ist_zulaessig is True


def test_wf16_migrations_regel_nicht_zulaessig_breaking():
    r = MigrationsRegel("R1", "1.0.0", "2.0.0", "typ", MigrationsTyp.BREAKING)
    assert r.ist_zulaessig is False


def test_wf17_migrations_regel_inkompatibel_ist_zulaessig():
    r = MigrationsRegel("R1", "1.0.0", "2.0.0", "typ", MigrationsTyp.INKOMPATIBEL)
    assert r.ist_zulaessig is True


def test_wf18_migrations_ergebnis_as_dict_erfolgreich():
    e = MigrationsErgebnis(
        "I1", "WD-A", "WD-B", MigrationsStatus.ABGESCHLOSSEN, MigrationsTyp.KOMPATIBEL
    )
    assert e.as_dict()["erfolgreich"] is True


def test_wf19_migrations_ergebnis_as_dict_nicht_erfolgreich():
    e = MigrationsErgebnis(
        "I1", "WD-A", "WD-B", MigrationsStatus.FEHLGESCHLAGEN, MigrationsTyp.BREAKING
    )
    assert e.as_dict()["erfolgreich"] is False


def test_wf20_migrations_regel_as_dict_enthaelt_ist_zulaessig():
    r = MigrationsRegel("R1", "1.0.0", "2.0.0", "typ", MigrationsTyp.KOMPATIBEL)
    assert "ist_zulaessig" in r.as_dict()


# ===========================================================================
# Teil 3: pruefe_migration (6 Tests)
# ===========================================================================

def test_wf21_keine_regel_ergibt_kompatibel():
    instanz = _make_instanz()
    ziel = _make_definition(workflow_typ="unbekannt_workflow", version="9.9.9")
    ergebnis = pruefe_migration(instanz, ziel, regeln=[])
    assert ergebnis.status == MigrationsStatus.ABGESCHLOSSEN
    assert ergebnis.migrations_typ == MigrationsTyp.KOMPATIBEL
    assert ergebnis.automatisch is True


def test_wf22_breaking_regel_wird_herausgefiltert_kompatibel():
    """BREAKING-Regeln werden durch ist_zulaessig herausgefiltert.
    Gibt es keine passende erlaubte Regel, ist das Ergebnis optimistisch KOMPATIBEL."""
    instanz = _make_instanz(definition_id="WD-OLD")
    ziel = _make_definition(workflow_typ="ap_approval", version="2.0.0")
    # MR-003 in den Default-Regeln ist BREAKING — wird herausgefiltert → keine passende Regel
    ergebnis = pruefe_migration(instanz, ziel)
    assert ergebnis.status == MigrationsStatus.ABGESCHLOSSEN
    assert ergebnis.migrations_typ == MigrationsTyp.KOMPATIBEL


def test_wf23_inkompatibel_regel_ergibt_ausstehend():
    instanz = _make_instanz(definition_id="WD-001")
    ziel = _make_definition(workflow_typ="kontrakt_annahme", version="2.0.0")
    # MR-001 ist INKOMPATIBEL: 1.0.0 → 2.0.0 kontrakt_annahme
    ergebnis = pruefe_migration(instanz, ziel)
    assert ergebnis.status == MigrationsStatus.AUSSTEHEND
    assert ergebnis.automatisch is False


def test_wf24_kompatibel_regel_ergibt_abgeschlossen():
    instanz = _make_instanz(definition_id="WD-003")
    ziel = _make_definition(workflow_typ="ap_approval", version="1.1.0")
    # MR-002 ist KOMPATIBEL: 1.0.0 → 1.1.0 ap_approval
    ergebnis = pruefe_migration(instanz, ziel)
    assert ergebnis.status == MigrationsStatus.ABGESCHLOSSEN


def test_wf25_deprecation_regel_ergibt_abgeschlossen():
    instanz = _make_instanz()
    ziel = _make_definition(workflow_typ="zahlungslauf_freigabe", version="1.1.0")
    # MR-004 ist DEPRECATION
    ergebnis = pruefe_migration(instanz, ziel)
    assert ergebnis.status == MigrationsStatus.ABGESCHLOSSEN
    assert ergebnis.migrations_typ == MigrationsTyp.DEPRECATION


def test_wf26_pruefe_migration_instanz_id_erhalten():
    instanz = _make_instanz(instanz_id="INST-XYZ")
    ziel = _make_definition(workflow_typ="unbekannt", version="1.0.0")
    ergebnis = pruefe_migration(instanz, ziel, regeln=[])
    assert ergebnis.instanz_id == "INST-XYZ"


# ===========================================================================
# Teil 4: ermittle_aktive_definition (6 Tests)
# ===========================================================================

def test_wf27_ermittle_aktive_global():
    defs = get_default_workflow_definitionen()
    d = ermittle_aktive_definition("kontrakt_annahme", defs)
    assert d is not None
    assert d.workflow_typ == "kontrakt_annahme"
    assert d.ist_aktiv


def test_wf28_ermittle_aktive_bevorzugt_tenant():
    global_def = _make_definition("WD-G", "test_wf", "1.0.0", tenant_id="")
    tenant_def = _make_definition("WD-T", "test_wf", "1.0.0", tenant_id="T-001")
    d = ermittle_aktive_definition("test_wf", [global_def, tenant_def], tenant_id="T-001")
    assert d is not None
    assert d.definition_id == "WD-T"


def test_wf29_ermittle_aktive_faellt_auf_global_zurueck():
    global_def = _make_definition("WD-G", "test_wf", "1.0.0", tenant_id="")
    d = ermittle_aktive_definition("test_wf", [global_def], tenant_id="T-999")
    assert d is not None
    assert d.definition_id == "WD-G"


def test_wf30_ermittle_aktive_none_wenn_nicht_vorhanden():
    defs = get_default_workflow_definitionen()
    d = ermittle_aktive_definition("nicht_existierend", defs)
    assert d is None


def test_wf31_ermittle_aktive_max_version():
    d1 = _make_definition("WD-1", "multi_wf", "1.0.0", tenant_id="")
    d2 = _make_definition("WD-2", "multi_wf", "2.0.0", tenant_id="")
    result = ermittle_aktive_definition("multi_wf", [d1, d2])
    assert result is not None
    assert result.version == "2.0.0"


def test_wf32_ermittle_aktive_ignoriert_nicht_aktive():
    veraltet = _make_definition("WD-V", "typ_x", "3.0.0",
                                status=WorkflowDefinitionsStatus.VERALTET, tenant_id="")
    aktiv = _make_definition("WD-A", "typ_x", "1.0.0",
                             status=WorkflowDefinitionsStatus.AKTIV, tenant_id="")
    result = ermittle_aktive_definition("typ_x", [veraltet, aktiv])
    assert result is not None
    assert result.definition_id == "WD-A"


# ===========================================================================
# Teil 5: Standarddaten (4 Tests)
# ===========================================================================

def test_wf33_get_default_workflow_definitionen_anzahl():
    defs = get_default_workflow_definitionen()
    assert len(defs) == 6


def test_wf34_get_default_migrationsregeln_anzahl():
    regeln = get_default_migrationsregeln()
    assert len(regeln) == 5


def test_wf35_get_default_sandbox_regeln_anzahl():
    regeln = get_default_sandbox_regeln()
    assert len(regeln) == 4


def test_wf36_sandbox_regel_as_dict_felder():
    r = SandboxVersionsRegel("kontrakt_annahme", SandboxModus.AKTUELLE_AKTIV)
    d = r.as_dict()
    assert d["sandbox_modus"] == "AKTUELLE_AKTIV"
    assert d["workflow_typ"] == "kontrakt_annahme"


# ===========================================================================
# Teil 6: AuditEintrag — 12 Tests (Tests 37–48)
# ===========================================================================

def test_at01_audit_eintrag_erstellt():
    e = _make_audit_eintrag()
    assert e.eintrag_id == "AE-001"


def test_at02_eintrag_hash_nach_init_berechnet():
    e = _make_audit_eintrag()
    assert len(e.eintrag_hash) == 64  # SHA256 hex-digest


def test_at03_pruefe_integritaet_unveraendert():
    e = _make_audit_eintrag()
    assert e.pruefe_integritaet() is True


def test_at04_ist_gobd_pflichtig_true():
    e = _make_audit_eintrag(gobd_relevanz=GoBDRelevanz.PFLICHT)
    assert e.ist_gobd_pflichtig is True


def test_at05_ist_gobd_pflichtig_false_fuer_nicht_pflicht():
    for r in (GoBDRelevanz.RELEVANT, GoBDRelevanz.NICHT_RELEVANT):
        assert _make_audit_eintrag(gobd_relevanz=r).ist_gobd_pflichtig is False


def test_at06_as_dict_enthaelt_ist_gobd_pflichtig():
    e = _make_audit_eintrag(gobd_relevanz=GoBDRelevanz.PFLICHT)
    d = e.as_dict()
    assert d["ist_gobd_pflichtig"] is True


def test_at07_as_dict_enthaelt_eintrag_hash():
    e = _make_audit_eintrag()
    d = e.as_dict()
    assert "eintrag_hash" in d
    assert d["eintrag_hash"] == e.eintrag_hash


def test_at08_hash_aendert_sich_bei_anderem_vorgaenger():
    e1 = _make_audit_eintrag(vorgaenger_hash="")
    e2 = _make_audit_eintrag(vorgaenger_hash="deadbeef")
    assert e1.eintrag_hash != e2.eintrag_hash


def test_at09_erstelle_audit_eintrag_helper_integritaet():
    e = erstelle_audit_eintrag(
        eintrag_id="AE-H01",
        ereignis_typ=AuditEreignisTyp.WORKFLOW_GESTARTET,
        kategorie=AuditKategorie.PROZESS,
        aktor_id="user-x",
        tenant_id="T-001",
        objekt_typ="Kontrakt",
        objekt_id="KT-001",
        beschreibung="Test",
    )
    assert e.eintrag_id == "AE-H01"
    assert e.pruefe_integritaet() is True


def test_at10_erstelle_audit_eintrag_default_zeitstempel_ist_datetime():
    e = erstelle_audit_eintrag(
        eintrag_id="AE-H02",
        ereignis_typ=AuditEreignisTyp.DATENMUTATION,
        kategorie=AuditKategorie.SYSTEM,
        aktor_id="system",
        tenant_id="T-001",
        objekt_typ="Tabelle",
        objekt_id="T1",
        beschreibung="Mutation",
    )
    assert isinstance(e.zeitstempel, datetime)


def test_at11_as_dict_ereignis_typ_als_string():
    e = _make_audit_eintrag(ereignis_typ=AuditEreignisTyp.FREIGABE_ERTEILT)
    assert e.as_dict()["ereignis_typ"] == "FREIGABE_ERTEILT"


def test_at12_as_dict_kategorie_als_string():
    e = _make_audit_eintrag(kategorie=AuditKategorie.FINANZ)
    assert e.as_dict()["kategorie"] == "FINANZ"


# ===========================================================================
# Teil 7: AuditKette — 12 Tests (Tests 49–60)
# ===========================================================================

def test_at13_leere_kette_letzter_hash_leer():
    kette = AuditKette("AK-001", "TENANT-001")
    assert kette.letzter_hash == ""


def test_at14_append_eintrag_erhoeht_laenge():
    kette = AuditKette("AK-001", "TENANT-001")
    kette.append(_make_audit_eintrag())
    assert len(kette.eintraege) == 1


def test_at15_letzter_hash_nach_append_korrekt():
    kette = AuditKette("AK-001", "TENANT-001")
    e = _make_audit_eintrag()
    kette.append(e)
    assert kette.letzter_hash == e.eintrag_hash


def test_at16_gobd_pflichtige_gefiltert():
    kette = AuditKette("AK-001", "TENANT-001")
    kette.append(_make_audit_eintrag("AE-1", gobd_relevanz=GoBDRelevanz.PFLICHT))
    kette.append(_make_audit_eintrag("AE-2", gobd_relevanz=GoBDRelevanz.NICHT_RELEVANT))
    assert len(kette.gobd_pflichtige_eintraege) == 1


def test_at17_leere_kette_ist_integer():
    kette = AuditKette("AK-001", "TENANT-001")
    assert kette.ist_integer is True


def test_at18_kette_integer_nach_korrektem_append():
    kette = AuditKette("AK-001", "TENANT-001")
    e1 = _make_audit_eintrag("AE-1", vorgaenger_hash="")
    kette.append(e1)
    e2 = _make_audit_eintrag("AE-2", vorgaenger_hash=e1.eintrag_hash)
    kette.append(e2)
    assert kette.ist_integer is True


def test_at19_beispiel_kette_hat_5_eintraege():
    kette = baue_beispiel_audit_kette()
    assert len(kette.eintraege) == 5


def test_at20_beispiel_kette_ist_integer():
    kette = baue_beispiel_audit_kette()
    assert kette.ist_integer is True


def test_at21_beispiel_kette_3_gobd_pflicht():
    kette = baue_beispiel_audit_kette()
    assert len(kette.gobd_pflichtige_eintraege) == 3


def test_at22_beispiel_kette_id():
    kette = baue_beispiel_audit_kette(kontrakt_id="KT-2026-0042")
    assert kette.kette_id == "AK-KT-2026-0042"


def test_at23_beispiel_kette_verkettung_korrekt():
    """Jeder Eintrag ab Index 1 referenziert den Hash seines Vorgängers."""
    kette = baue_beispiel_audit_kette()
    for i in range(1, len(kette.eintraege)):
        assert kette.eintraege[i].vorgaenger_hash == kette.eintraege[i - 1].eintrag_hash


def test_at24_hash_fehler_erkannt():
    """Manipulierter Eintrag wird als HASH_FEHLER erkannt."""
    kette = AuditKette("AK-M", "TENANT-001")
    e1 = _make_audit_eintrag("AE-1", vorgaenger_hash="")
    kette.append(e1)
    # Direkte Mutation des Eintrags — Hash stimmt dann nicht mehr
    e1.beschreibung = "manipuliert"
    stati = kette.pruefe_kettenintegritaet()
    assert stati[0] == AuditIntegritaetsStatus.HASH_FEHLER
