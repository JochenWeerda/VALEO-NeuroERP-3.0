"""
Wave 26 — Trocknungsabrechnung Audit-Contract + Workflow-Migrations-Guard Tests

AP1/AP5/AP6: compute_trocknungs_abrechnung(); validate_trocknungs_ergebnis();
             get_default_trocknungsregeln(); SHA-256 Determinismus
AP2:         validate_workflow_migration(); MigrationCompatibilityResult;
             SAFE/WARNUNG/BREAKING-Klassifizierung
AP3:         API /trocknungs-abrechnung/preview + /regelsets
AP4:         API POST /workflow-migration/check
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.trocknungs_abrechnung import (
    TROCKNUNGS_SCHEMA_VERSION,
    AbzugsArt,
    PlausibilitaetsCode,
    TrocknungsInput,
    TrocknungsMethode,
    TrocknungsRegelParametrierung,
    compute_trocknungs_abrechnung,
    get_default_trocknungsregeln,
    validate_trocknungs_ergebnis,
)
from app.core.workflow_migrations_guard import (
    MIGRATIONS_GUARD_SCHEMA_VERSION,
    MigrationRisikoKlasse,
    MigrationViolationCode,
    WorkflowDefinitionSnapshot,
    WorkflowSchrittSnapshot,
    validate_workflow_migration,
)


# ===========================================================================
# Hilfsfunktionen
# ===========================================================================

def _inp(
    feuchte: str = "17.2",
    ziel: str = "14.5",
    brutto_kg: str = "50000",
    crop: str = "WW",
) -> TrocknungsInput:
    return TrocknungsInput(
        settlement_id="S-001",
        tenant_id="t1",
        crop_code=crop,
        rule_set_id="RS-WW-2024",
        rule_set_version=1,
        brutto_gewicht_kg=Decimal(brutto_kg),
        eingangs_feuchte_pct=Decimal(feuchte),
        ziel_feuchte_pct=Decimal(ziel),
        methode=TrocknungsMethode.FAKTOR_STUFUNG,
    )


def _params(**kwargs) -> TrocknungsRegelParametrierung:
    defaults = dict(
        start_threshold_pct=Decimal("14.5"),
        trocknungskosten_eur_per_pct_per_t=Decimal("2.50"),
        schwund_faktor=Decimal("1.00"),
        max_abzug_pct=None,
    )
    defaults.update(kwargs)
    return TrocknungsRegelParametrierung(**defaults)


# ===========================================================================
# AP1: compute_trocknungs_abrechnung()
# ===========================================================================

def test_compute_ergibt_schwund_und_kosten():
    ergebnis = compute_trocknungs_abrechnung(_inp(), _params())
    arts = {p.art for p in ergebnis.positionen}
    assert AbzugsArt.TROCKNUNGSSCHWUND in arts
    assert AbzugsArt.TROCKNUNGSKOSTEN in arts


def test_compute_keine_abzuege_unter_schwelle():
    """Feuchte <= Zielfeuchte → kein Abzug."""
    ergebnis = compute_trocknungs_abrechnung(_inp(feuchte="14.0", ziel="14.5"), _params())
    assert len(ergebnis.positionen) == 0
    assert ergebnis.gesamt_abzug_kg == Decimal("0")


def test_compute_keine_abzuege_exakt_am_threshold():
    """Feuchte == Zielfeuchte → kein Abzug."""
    ergebnis = compute_trocknungs_abrechnung(_inp(feuchte="14.5", ziel="14.5"), _params())
    assert ergebnis.gesamt_abzug_kg == Decimal("0")


def test_compute_schwund_deterministisch():
    """Gleicher Input → gleicher Audit-Hash."""
    e1 = compute_trocknungs_abrechnung(_inp(), _params())
    e2 = compute_trocknungs_abrechnung(_inp(), _params())
    assert e1.audit_hash == e2.audit_hash
    assert len(e1.audit_hash) == 64  # SHA-256 hex


def test_compute_audit_hash_aendert_sich_bei_anderem_input():
    e1 = compute_trocknungs_abrechnung(_inp(feuchte="17.2"), _params())
    e2 = compute_trocknungs_abrechnung(_inp(feuchte="18.0"), _params())
    assert e1.audit_hash != e2.audit_hash


def test_compute_schema_version():
    ergebnis = compute_trocknungs_abrechnung(_inp(), _params())
    assert ergebnis.schema_version == TROCKNUNGS_SCHEMA_VERSION


def test_compute_netto_gewicht():
    ergebnis = compute_trocknungs_abrechnung(_inp(brutto_kg="50000"), _params())
    assert ergebnis.netto_gewicht_kg == ergebnis.input_contract.brutto_gewicht_kg - ergebnis.gesamt_abzug_kg


def test_compute_netto_gewicht_positiv():
    ergebnis = compute_trocknungs_abrechnung(_inp(), _params())
    assert ergebnis.netto_gewicht_kg > Decimal("0")


def test_compute_max_abzug_clamp():
    """Max-Clamp begrenzt Schwund auf max_abzug_pct."""
    params = _params(max_abzug_pct=Decimal("1.0"))  # max 1%
    ergebnis = compute_trocknungs_abrechnung(_inp(feuchte="25.0", ziel="14.5"), params)
    max_kg = Decimal("50000") * Decimal("1.0") / Decimal("100")
    schwund = next((p for p in ergebnis.positionen if p.art == AbzugsArt.TROCKNUNGSSCHWUND), None)
    if schwund:
        assert schwund.abzug_kg <= max_kg + Decimal("0.001")


def test_compute_keine_kosten_wenn_rate_null():
    params = _params(trocknungskosten_eur_per_pct_per_t=Decimal("0"))
    ergebnis = compute_trocknungs_abrechnung(_inp(), params)
    arts = {p.art for p in ergebnis.positionen}
    assert AbzugsArt.TROCKNUNGSKOSTEN not in arts


def test_compute_as_dict():
    ergebnis = compute_trocknungs_abrechnung(_inp(), _params())
    d = ergebnis.as_dict()
    assert d["settlement_id"] == "S-001"
    assert d["schema_version"] == TROCKNUNGS_SCHEMA_VERSION
    assert "audit_hash" in d
    assert "gesamt_abzug_kg" in d
    assert "netto_gewicht_kg" in d
    assert isinstance(d["positionen"], list)


def test_compute_position_as_dict():
    ergebnis = compute_trocknungs_abrechnung(_inp(), _params())
    assert len(ergebnis.positionen) > 0
    d = ergebnis.positionen[0].as_dict()
    assert "art" in d
    assert "abzug_kg" in d
    assert "rule_ref" in d


# ===========================================================================
# AP5: validate_trocknungs_ergebnis()
# ===========================================================================

def test_valid_ergebnis_passes():
    ergebnis = compute_trocknungs_abrechnung(_inp(), _params())
    result = validate_trocknungs_ergebnis(ergebnis)
    assert result.valid is True
    assert len(result.violations) == 0


def test_validate_schema_version():
    ergebnis = compute_trocknungs_abrechnung(_inp(), _params())
    result = validate_trocknungs_ergebnis(ergebnis)
    assert result.schema_version == TROCKNUNGS_SCHEMA_VERSION


def test_validate_feuchte_unter_zielfeuchte_mit_abzug():
    """Feuchte < Ziel aber Abzug vorhanden → Violation."""
    from app.core.trocknungs_abrechnung import TrocknungsErgebnis, TrocknungsPosition
    ergebnis = compute_trocknungs_abrechnung(_inp(feuchte="13.0", ziel="14.5"), _params())
    # Manuell einen falschen Abzug einfuegen
    ergebnis.positionen.append(TrocknungsPosition(
        art=AbzugsArt.TROCKNUNGSSCHWUND,
        bezeichnung="Fehler-Abzug",
        basis_kg=Decimal("50000"),
        abzug_kg=Decimal("500"),
    ))
    result = validate_trocknungs_ergebnis(ergebnis)
    assert result.valid is False
    codes = [v.code for v in result.violations]
    assert PlausibilitaetsCode.FEUCHTE_UNTER_ZIELFEUCHTE in codes


def test_validate_extrem_feuchte():
    ergebnis = compute_trocknungs_abrechnung(
        _inp(feuchte="31.0", ziel="14.5"), _params()
    )
    result = validate_trocknungs_ergebnis(ergebnis)
    codes = [v.code for v in result.violations]
    assert PlausibilitaetsCode.FEUCHTE_AUSSERHALB_TOLERANZ in codes


def test_validate_as_dict():
    ergebnis = compute_trocknungs_abrechnung(_inp(), _params())
    result = validate_trocknungs_ergebnis(ergebnis)
    d = result.as_dict()
    assert d["valid"] is True
    assert "violation_count" in d
    assert isinstance(d["violations"], list)


# ===========================================================================
# AP6: get_default_trocknungsregeln()
# ===========================================================================

def test_default_regelsets_count():
    regeln = get_default_trocknungsregeln()
    assert len(regeln) == 5


def test_default_regelsets_fruchtarten():
    regeln = get_default_trocknungsregeln()
    assert "WW" in regeln
    assert "SG" in regeln
    assert "RA" in regeln
    assert "KM" in regeln
    assert "ZR" in regeln


def test_default_regelsets_raps_threshold():
    regeln = get_default_trocknungsregeln()
    assert regeln["RA"].start_threshold_pct == Decimal("9.0")


def test_default_regelsets_mais_faktor():
    regeln = get_default_trocknungsregeln()
    assert regeln["KM"].schwund_faktor > Decimal("1.0")  # Mais hat hoehere Schwundrate


def test_default_regelsets_alle_positiv():
    for code, p in get_default_trocknungsregeln().items():
        assert p.start_threshold_pct > Decimal("0"), f"{code}: threshold <= 0"
        assert p.trocknungskosten_eur_per_pct_per_t > Decimal("0"), f"{code}: kosten <= 0"


# ===========================================================================
# AP2: validate_workflow_migration() — SAFE
# ===========================================================================

def _snap(version: str, schritte: list[WorkflowSchrittSnapshot]) -> WorkflowDefinitionSnapshot:
    return WorkflowDefinitionSnapshot(
        prozess_key="agrar_settlement",
        version=version,
        schema_version=1,
        schritte=schritte,
    )


def _schritt(sid: str, pflicht: bool = True, reihenfolge: int = 10, terminal: bool = False, rolle: str = "sachbearbeiter") -> WorkflowSchrittSnapshot:
    return WorkflowSchrittSnapshot(sid, pflicht=pflicht, reihenfolge=reihenfolge, terminal=terminal, rolle=rolle)


def test_migration_safe_identisch():
    schritte = [_schritt("S1", reihenfolge=10), _schritt("S2", reihenfolge=20)]
    result = validate_workflow_migration(_snap("1.0", schritte), _snap("1.1", schritte))
    assert result.risiko_klasse == MigrationRisikoKlasse.SAFE
    assert result.migration_erlaubt is True
    assert result.violation_count == 0


def test_migration_safe_neuer_optionaler_schritt():
    alt = [_schritt("S1", reihenfolge=10)]
    neu = [_schritt("S1", reihenfolge=10), _schritt("S2", pflicht=False, reihenfolge=20)]
    result = validate_workflow_migration(_snap("1.0", alt), _snap("1.1", neu))
    assert result.risiko_klasse == MigrationRisikoKlasse.SAFE


def test_migration_breaking_pflichtschritt_entfernt():
    alt = [_schritt("S1", reihenfolge=10), _schritt("S2", reihenfolge=20)]
    neu = [_schritt("S2", reihenfolge=20)]
    result = validate_workflow_migration(_snap("1.0", alt), _snap("2.0", neu))
    assert result.risiko_klasse == MigrationRisikoKlasse.BREAKING
    assert result.migration_erlaubt is False
    codes = [v.code for v in result.violations]
    assert MigrationViolationCode.PFLICHTSCHRITT_ENTFERNT in codes


def test_migration_breaking_neuer_pflichtschritt():
    alt = [_schritt("S1", reihenfolge=10)]
    neu = [_schritt("S1", reihenfolge=10), _schritt("S_NEU", pflicht=True, reihenfolge=20)]
    result = validate_workflow_migration(_snap("1.0", alt), _snap("2.0", neu))
    assert result.risiko_klasse == MigrationRisikoKlasse.BREAKING
    codes = [v.code for v in result.violations]
    assert MigrationViolationCode.NEUER_PFLICHTSCHRITT_OHNE_MIGRATION in codes


def test_migration_breaking_terminal_entfernt():
    alt = [_schritt("S1", reihenfolge=10, terminal=True)]
    neu = [_schritt("S1", reihenfolge=10, terminal=False)]
    result = validate_workflow_migration(_snap("1.0", alt), _snap("2.0", neu))
    assert result.risiko_klasse == MigrationRisikoKlasse.BREAKING
    codes = [v.code for v in result.violations]
    assert MigrationViolationCode.TERMINALZUSTAND_GEAENDERT in codes


def test_migration_breaking_schema_downgrade():
    schritte = [_schritt("S1")]
    alt = WorkflowDefinitionSnapshot("p", "2.0", schema_version=2, schritte=schritte)
    neu = WorkflowDefinitionSnapshot("p", "1.9", schema_version=1, schritte=schritte)
    result = validate_workflow_migration(alt, neu)
    assert result.risiko_klasse == MigrationRisikoKlasse.BREAKING
    codes = [v.code for v in result.violations]
    assert MigrationViolationCode.SCHEMA_VERSION_DOWNGRADE in codes


def test_migration_warnung_reihenfolge_umgekehrt():
    alt = [_schritt("S1", reihenfolge=10), _schritt("S2", reihenfolge=20)]
    neu = [_schritt("S2", reihenfolge=10), _schritt("S1", reihenfolge=20)]
    result = validate_workflow_migration(_snap("1.0", alt), _snap("1.1", neu))
    assert result.risiko_klasse == MigrationRisikoKlasse.WARNUNG
    assert result.migration_erlaubt is True


def test_migration_result_as_dict():
    schritte = [_schritt("S1")]
    result = validate_workflow_migration(_snap("1.0", schritte), _snap("1.1", schritte))
    d = result.as_dict()
    assert d["risiko_klasse"] == "SAFE"
    assert d["migration_erlaubt"] is True
    assert d["schema_version"] == MIGRATIONS_GUARD_SCHEMA_VERSION
    assert "violations" in d


def test_migration_von_zu_version_in_result():
    schritte = [_schritt("S1")]
    result = validate_workflow_migration(_snap("1.0", schritte), _snap("2.0", schritte))
    assert result.von_version == "1.0"
    assert result.zu_version == "2.0"


def test_migration_snapshot_as_dict():
    snap = _snap("1.0", [_schritt("S1", terminal=True)])
    d = snap.as_dict()
    assert d["version"] == "1.0"
    assert "terminal_schritte" in d
    assert "S1" in d["terminal_schritte"]


# ===========================================================================
# AP3 + AP4: API-Endpoints via TestClient
# ===========================================================================

@pytest.fixture(scope="module")
def client():
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app, raise_server_exceptions=True)


def test_trocknungs_preview_endpoint(client):
    resp = client.get(
        "/api/v1/process/trocknungs-abrechnung/preview/S-W26-001",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["settlement_id"] == "S-W26-001"
    assert data["schema_version"] == 1
    assert "trocknungs_ergebnis" in data
    erg = data["trocknungs_ergebnis"]
    assert "audit_hash" in erg
    assert len(erg["audit_hash"]) == 64
    assert "netto_gewicht_kg" in erg


def test_trocknungs_preview_deterministisch(client):
    r1 = client.get(
        "/api/v1/process/trocknungs-abrechnung/preview/S-SAME",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    r2 = client.get(
        "/api/v1/process/trocknungs-abrechnung/preview/S-SAME",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert r1.json()["trocknungs_ergebnis"]["audit_hash"] == r2.json()["trocknungs_ergebnis"]["audit_hash"]


def test_trocknungs_regelsets_endpoint(client):
    resp = client.get(
        "/api/v1/process/trocknungs-abrechnung/regelsets",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 5
    assert "WW" in data["regelsets"]
    assert "RA" in data["regelsets"]


def test_workflow_migration_check_safe(client):
    resp = client.post(
        "/api/v1/process/workflow-migration/check",
        json={},  # leerer Body → Demo-Snapshot SAFE
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["risiko_klasse"] == "SAFE"
    assert data["migration_erlaubt"] is True
    assert data["schema_version"] == MIGRATIONS_GUARD_SCHEMA_VERSION


def test_workflow_migration_check_breaking(client):
    resp = client.post(
        "/api/v1/process/workflow-migration/check",
        json={
            "prozess_key": "agrar_settlement",
            "von_version": "1.0",
            "zu_version": "2.0",
            "alt_schritte": [
                {"schritt_id": "S1", "pflicht": True, "reihenfolge": 10, "terminal": False, "rolle": "sachbearbeiter"},
                {"schritt_id": "S2", "pflicht": True, "reihenfolge": 20, "terminal": True, "rolle": "buchhalter"},
            ],
            "neu_schritte": [
                {"schritt_id": "S2", "pflicht": True, "reihenfolge": 20, "terminal": True, "rolle": "buchhalter"},
            ],
        },
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["risiko_klasse"] == "BREAKING"
    assert data["migration_erlaubt"] is False
    assert data["violation_count"] >= 1
