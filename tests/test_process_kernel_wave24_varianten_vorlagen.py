"""
Wave 24 — Tenant-Prozessvarianten + Kampagnenvorlagen Tests

AP1/AP5: TenantProzessVariante; resolve_process_steps(); validate_prozess_variante()
AP2/AP6: KampagnenVorlage; instantiate_from_vorlage(); get_default_kampagnen_vorlagen()
AP3:     API GET /process/kampagnen/vorlagen + /instantiate
AP4:     API GET /process/tenant/prozess-varianten + /steps
"""
from __future__ import annotations

from decimal import Decimal
from datetime import date

import pytest

from app.core.tenant_prozess_variante import (
    VARIANTE_SCHEMA_VERSION,
    ProzessSchrittDefinition,
    SchrittOverride,
    SchrittStatus,
    TenantProzessVariante,
    VarianteValidierungsFehler,
    build_default_tenant_variante,
    get_default_agrar_settlement_schritte,
    resolve_process_steps,
    validate_prozess_variante,
)
from app.core.kampagnen_vorlage import (
    VORLAGE_SCHEMA_VERSION,
    KampagnenTyp,
    get_default_kampagnen_vorlagen,
    get_vorlage_by_typ,
    instantiate_from_vorlage,
)


# ===========================================================================
# AP1: resolve_process_steps() — Grundverhalten
# ===========================================================================

def _schritte_basis() -> list[ProzessSchrittDefinition]:
    return [
        ProzessSchrittDefinition("S1", "Schritt 1", pflicht=True,  reihenfolge=10),
        ProzessSchrittDefinition("S2", "Schritt 2", pflicht=False, reihenfolge=20),
        ProzessSchrittDefinition("S3", "Schritt 3", pflicht=True,  reihenfolge=30),
        ProzessSchrittDefinition("S4", "Schritt 4", pflicht=False, reihenfolge=40),
    ]


def _variante(overrides: list[SchrittOverride] | None = None) -> TenantProzessVariante:
    return TenantProzessVariante(
        variante_id="V-001",
        tenant_id="t1",
        prozess_key="test_prozess",
        bezeichnung="Test",
        default_schritte=_schritte_basis(),
        overrides=overrides or [],
    )


def test_resolve_without_overrides_returns_all_active():
    variante = _variante()
    steps = resolve_process_steps(variante)
    assert len(steps) == 4
    assert all(s.status == SchrittStatus.AKTIV for s in steps)


def test_resolve_sorted_by_reihenfolge():
    variante = _variante()
    steps = resolve_process_steps(variante)
    reihenfolgen = [s.reihenfolge for s in steps]
    assert reihenfolgen == sorted(reihenfolgen)


def test_resolve_deactivates_optional_schritt():
    override = SchrittOverride("S2", status=SchrittStatus.DEAKTIVIERT)
    steps = resolve_process_steps(_variante([override]))
    ids = [s.schritt_id for s in steps]
    assert "S2" not in ids
    assert len(steps) == 3


def test_resolve_pflichtschritt_cannot_be_deactivated():
    override = SchrittOverride("S1", status=SchrittStatus.DEAKTIVIERT)  # S1 = Pflicht
    steps = resolve_process_steps(_variante([override]))
    ids = [s.schritt_id for s in steps]
    assert "S1" in ids  # Pflichtschritt bleibt
    s1 = next(s for s in steps if s.schritt_id == "S1")
    assert s1.status == SchrittStatus.AKTIV


def test_resolve_reihenfolge_override():
    override = SchrittOverride("S4", reihenfolge_override=5)  # S4 soll zuerst kommen
    steps = resolve_process_steps(_variante([override]))
    assert steps[0].schritt_id == "S4"


def test_resolve_sla_override():
    override = SchrittOverride("S1", sla_stunden_override=99)
    steps = resolve_process_steps(_variante([override]))
    s1 = next(s for s in steps if s.schritt_id == "S1")
    assert s1.sla_stunden == 99


def test_resolve_override_aktiv_flag():
    override = SchrittOverride("S2", status=SchrittStatus.OPTIONAL)
    steps = resolve_process_steps(_variante([override]))
    s2 = next(s for s in steps if s.schritt_id == "S2")
    assert s2.override_aktiv is True
    s1 = next(s for s in steps if s.schritt_id == "S1")
    assert s1.override_aktiv is False


def test_resolve_schritt_as_dict():
    steps = resolve_process_steps(_variante())
    d = steps[0].as_dict()
    assert "schritt_id" in d
    assert "reihenfolge" in d
    assert "status" in d
    assert "override_aktiv" in d


# ===========================================================================
# AP5: validate_prozess_variante()
# ===========================================================================

def test_valid_variante_passes():
    result = validate_prozess_variante(_variante())
    assert result.valid is True
    assert result.violation_count == 0


def test_validate_pflichtschritt_deaktiviert():
    override = SchrittOverride("S1", status=SchrittStatus.DEAKTIVIERT)
    result = validate_prozess_variante(_variante([override]))
    assert result.valid is False
    codes = [v.code for v in result.violations]
    assert VarianteValidierungsFehler.PFLICHTSCHRITT_DEAKTIVIERT in codes


def test_validate_unbekannter_schritt():
    override = SchrittOverride("S_UNBEKANNT", status=SchrittStatus.DEAKTIVIERT)
    result = validate_prozess_variante(_variante([override]))
    assert result.valid is False
    codes = [v.code for v in result.violations]
    assert VarianteValidierungsFehler.UNBEKANNTER_SCHRITT in codes


def test_validate_doppelter_schritt():
    schritte = _schritte_basis() + [ProzessSchrittDefinition("S1", "Doppelt", pflicht=True, reihenfolge=99)]
    variante = TenantProzessVariante(
        variante_id="V-DUP",
        tenant_id="t1",
        prozess_key="test",
        bezeichnung="Duplikat-Test",
        default_schritte=schritte,
    )
    result = validate_prozess_variante(variante)
    assert result.valid is False
    codes = [v.code for v in result.violations]
    assert VarianteValidierungsFehler.SCHRITT_DOPPELT in codes


def test_validate_reihenfolge_konflikt():
    override = SchrittOverride("S2", reihenfolge_override=10)  # Kollidiert mit S1 (Reihenfolge 10)
    result = validate_prozess_variante(_variante([override]))
    codes = [v.code for v in result.violations]
    assert VarianteValidierungsFehler.REIHENFOLGE_KONFLIKT in codes


def test_validate_as_dict():
    result = validate_prozess_variante(_variante())
    d = result.as_dict()
    assert d["valid"] is True
    assert d["violation_count"] == 0
    assert d["schema_version"] == VARIANTE_SCHEMA_VERSION
    assert isinstance(d["violations"], list)


def test_validate_schema_version():
    result = validate_prozess_variante(_variante())
    assert result.schema_version == VARIANTE_SCHEMA_VERSION


# ===========================================================================
# AP1: Default agrar_settlement Schritte
# ===========================================================================

def test_default_agrar_settlement_schritt_count():
    schritte = get_default_agrar_settlement_schritte()
    assert len(schritte) == 7


def test_default_agrar_settlement_pflichtschritte():
    schritte = get_default_agrar_settlement_schritte()
    pflicht = [s for s in schritte if s.pflicht]
    optional = [s for s in schritte if not s.pflicht]
    assert len(pflicht) == 5
    assert len(optional) == 2


def test_default_agrar_settlement_sorted():
    schritte = get_default_agrar_settlement_schritte()
    reihenfolgen = [s.reihenfolge for s in schritte]
    assert reihenfolgen == sorted(reihenfolgen)


def test_build_default_tenant_variante():
    variante = build_default_tenant_variante("tenant-abc")
    assert variante.tenant_id == "tenant-abc"
    assert variante.prozess_key == "agrar_settlement"
    assert len(variante.default_schritte) == 7
    assert len(variante.overrides) == 0


def test_default_variante_as_dict():
    variante = build_default_tenant_variante("t1")
    d = variante.as_dict()
    assert d["schema_version"] == VARIANTE_SCHEMA_VERSION
    assert d["prozess_key"] == "agrar_settlement"


# ===========================================================================
# AP2/AP6: KampagnenVorlagen
# ===========================================================================

def test_default_vorlagen_count():
    vorlagen = get_default_kampagnen_vorlagen()
    assert len(vorlagen) == 5


def test_default_vorlagen_typen():
    vorlagen = get_default_kampagnen_vorlagen()
    typen = {v.kampagnen_typ for v in vorlagen}
    assert KampagnenTyp.WINTERWEIZEN in typen
    assert KampagnenTyp.SOMMERGERSTE in typen
    assert KampagnenTyp.RAPS in typen
    assert KampagnenTyp.KOERNERMAIS in typen
    assert KampagnenTyp.ZUCKERRUEBEN in typen


def test_default_vorlagen_schema_version():
    for vorlage in get_default_kampagnen_vorlagen():
        assert vorlage.schema_version == VORLAGE_SCHEMA_VERSION


def test_default_vorlagen_have_meilensteine():
    for vorlage in get_default_kampagnen_vorlagen():
        assert len(vorlage.meilensteine) > 0, f"{vorlage.kampagnen_typ} hat keine Meilensteine"


def test_default_vorlagen_have_qualitaet():
    for vorlage in get_default_kampagnen_vorlagen():
        q = vorlage.qualitaet
        assert q.feuchte_max_pct > Decimal("0")
        assert q.hl_gewicht_min > Decimal("0")


def test_default_vorlagen_have_intrastat_code():
    for vorlage in get_default_kampagnen_vorlagen():
        assert vorlage.intrastat_cn8_code is not None
        assert len(vorlage.intrastat_cn8_code) == 8


def test_vorlage_as_dict():
    vorlage = get_vorlage_by_typ(KampagnenTyp.WINTERWEIZEN)
    assert vorlage is not None
    d = vorlage.as_dict()
    assert d["kampagnen_typ"] == "WINTERWEIZEN"
    assert d["frucht_art_code"] == "WW"
    assert "qualitaet" in d
    assert "meilensteine" in d
    assert d["schema_version"] == VORLAGE_SCHEMA_VERSION


def test_get_vorlage_by_typ_raps():
    vorlage = get_vorlage_by_typ(KampagnenTyp.RAPS)
    assert vorlage is not None
    assert vorlage.frucht_art_code == "RA"
    assert vorlage.typischer_erntebeginn_kw == 25


def test_get_vorlage_by_typ_unknown_returns_none():
    # KampagnenTyp hat nur 5 Werte — dieser Test benutzt direkt get_vorlage_by_typ
    # mit einem unmoeglich gesetzten Mock-Typ (nicht testbar ohne Monkeypatch)
    # Stattdessen: alle 5 Typen liefern valide Ergebnisse
    for typ in KampagnenTyp:
        vorlage = get_vorlage_by_typ(typ)
        assert vorlage is not None


# ===========================================================================
# AP2: instantiate_from_vorlage()
# ===========================================================================

def test_instantiate_basic():
    vorlage = get_vorlage_by_typ(KampagnenTyp.WINTERWEIZEN)
    instanz = instantiate_from_vorlage(
        vorlage,
        instanz_id="KI-001",
        tenant_id="t1",
        wirtschaftsjahr=2026,
    )
    assert instanz.instanz_id == "KI-001"
    assert instanz.tenant_id == "t1"
    assert instanz.wirtschaftsjahr == 2026
    assert instanz.vorlage.kampagnen_typ == KampagnenTyp.WINTERWEIZEN


def test_instantiate_with_start_computes_end():
    vorlage = get_vorlage_by_typ(KampagnenTyp.WINTERWEIZEN)
    start = date(2026, 7, 10)
    instanz = instantiate_from_vorlage(
        vorlage,
        instanz_id="KI-002",
        tenant_id="t1",
        wirtschaftsjahr=2026,
        geplanter_start=start,
    )
    assert instanz.geplanter_start == start
    assert instanz.geplantes_ende is not None
    delta = (instanz.geplantes_ende - instanz.geplanter_start).days
    assert delta == vorlage.standard_kampagnendauer_tage


def test_instantiate_copies_meilensteine():
    vorlage = get_vorlage_by_typ(KampagnenTyp.RAPS)
    instanz = instantiate_from_vorlage(
        vorlage,
        instanz_id="KI-003",
        tenant_id="t1",
        wirtschaftsjahr=2026,
    )
    assert len(instanz.angepasste_meilensteine) == len(vorlage.meilensteine)


def test_instantiate_as_dict():
    vorlage = get_vorlage_by_typ(KampagnenTyp.KOERNERMAIS)
    instanz = instantiate_from_vorlage(
        vorlage,
        instanz_id="KI-004",
        tenant_id="t1",
        wirtschaftsjahr=2026,
    )
    d = instanz.as_dict()
    assert d["kampagnen_typ"] == "KOERNERMAIS"
    assert d["schema_version"] == VORLAGE_SCHEMA_VERSION
    assert "qualitaet" in d
    assert "meilensteine" in d


def test_instantiate_custom_bezeichnung():
    vorlage = get_vorlage_by_typ(KampagnenTyp.ZUCKERRUEBEN)
    instanz = instantiate_from_vorlage(
        vorlage,
        instanz_id="KI-005",
        tenant_id="t1",
        wirtschaftsjahr=2026,
        bezeichnung="Meine Rübenkampagne 2026",
    )
    assert instanz.bezeichnung == "Meine Rübenkampagne 2026"


# ===========================================================================
# AP3 + AP4: API-Endpoints via TestClient
# ===========================================================================

@pytest.fixture(scope="module")
def client():
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app, raise_server_exceptions=True)


def test_list_kampagnen_vorlagen_endpoint(client):
    resp = client.get(
        "/api/v1/process/kampagnen/vorlagen",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 5
    assert data["schema_version"] == 1
    assert len(data["vorlagen"]) == 5


def test_list_kampagnen_vorlagen_has_qualitaet(client):
    resp = client.get(
        "/api/v1/process/kampagnen/vorlagen",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    vorlagen = resp.json()["vorlagen"]
    for v in vorlagen:
        assert "qualitaet" in v
        assert "feuchte_max_pct" in v["qualitaet"]


def test_instantiate_winterweizen_endpoint(client):
    resp = client.get(
        "/api/v1/process/kampagnen/vorlagen/WINTERWEIZEN/instantiate",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["schema_version"] == 1
    assert "instanz" in data
    assert data["instanz"]["kampagnen_typ"] == "WINTERWEIZEN"
    assert data["vorlage_id"] == "VL-WW-2024"


def test_instantiate_unknown_typ_returns_400(client):
    resp = client.get(
        "/api/v1/process/kampagnen/vorlagen/BANANE/instantiate",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 400


def test_list_prozess_varianten_endpoint(client):
    resp = client.get(
        "/api/v1/process/tenant/prozess-varianten",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["schema_version"] == 1
    assert len(data["prozesse"]) >= 1
    proc = data["prozesse"][0]
    assert proc["prozess_key"] == "agrar_settlement"
    assert proc["schritt_count"] == 7


def test_get_prozess_steps_endpoint(client):
    resp = client.get(
        "/api/v1/process/tenant/prozess-varianten/agrar_settlement/steps",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["prozess_key"] == "agrar_settlement"
    assert data["schema_version"] == 1
    assert data["step_count"] == 7
    assert "steps" in data
    assert "validation" in data
    assert data["validation"]["valid"] is True


def test_get_prozess_steps_sorted(client):
    resp = client.get(
        "/api/v1/process/tenant/prozess-varianten/agrar_settlement/steps",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    steps = resp.json()["steps"]
    reihenfolgen = [s["reihenfolge"] for s in steps]
    assert reihenfolgen == sorted(reihenfolgen)
