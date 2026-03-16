"""
Wave 45 — Feature Flag Contracts & Process Cost Contracts
==========================================================
60 deterministic unit tests, no mocking, no running server/DB required.

Modules under test:
  - app.core.feature_flag_contracts
  - app.core.process_cost_contracts
"""
import pytest
from datetime import datetime, timezone

from app.core.feature_flag_contracts import (
    FeatureFlagStatus,
    RolloutStrategie,
    FlagVariante,
    FeatureFlag,
    FeatureFlagEvaluierung,
    evaluiere_flags,
    get_aktive_flag_ids,
    get_default_feature_flags,
)
from app.core.process_cost_contracts import (
    KostenTyp,
    AbrechnungsEinheit,
    BudgetStatus,
    KostenPosition,
    ProzessKostenErfassung,
    BudgetUeberwachung,
    erstelle_kosten_erfassung,
    pruefe_budget,
    get_default_budget_ueberwachungen,
)


# ===========================================================================
# Helper factories
# ===========================================================================

def _make_flag(
    flag_id="FF-TEST",
    flag_name="test-flag",
    status=FeatureFlagStatus.AKTIV,
    rollout_strategie=RolloutStrategie.ALLE,
    rollout_prozentsatz=100,
    erlaubte_tenants=None,
    erlaubte_rollen=None,
    variante=FlagVariante.STANDARD,
    beschreibung="",
) -> FeatureFlag:
    return FeatureFlag(
        flag_id=flag_id,
        flag_name=flag_name,
        status=status,
        rollout_strategie=rollout_strategie,
        rollout_prozentsatz=rollout_prozentsatz,
        erlaubte_tenants=erlaubte_tenants or [],
        erlaubte_rollen=erlaubte_rollen or [],
        variante=variante,
        beschreibung=beschreibung,
    )


def _make_position(
    position_id="POS-001",
    kosten_typ=KostenTyp.CPU,
    menge=1.0,
    einheit_preis_eur=0.01,
    abrechnungs_einheit=AbrechnungsEinheit.PRO_AUSFUEHRUNG,
    beschreibung="",
) -> KostenPosition:
    return KostenPosition(
        position_id=position_id,
        kosten_typ=kosten_typ,
        menge=menge,
        einheit_preis_eur=einheit_preis_eur,
        abrechnungs_einheit=abrechnungs_einheit,
        beschreibung=beschreibung,
    )


def _make_budget(
    budget_id="BU-TEST",
    tenant_id="TENANT-001",
    domain="agrar",
    budget_eur=1000.0,
    verbraucht_eur=500.0,
    periode="2026-Q1",
) -> BudgetUeberwachung:
    return BudgetUeberwachung(
        budget_id=budget_id,
        tenant_id=tenant_id,
        domain=domain,
        budget_eur=budget_eur,
        verbraucht_eur=verbraucht_eur,
        periode=periode,
    )


# ===========================================================================
# Feature Flag Contracts — 30 tests
# ===========================================================================

# --- Enum values ---

def test_ff_status_enum_values():
    assert FeatureFlagStatus.AKTIV.value == "AKTIV"
    assert FeatureFlagStatus.INAKTIV.value == "INAKTIV"
    assert FeatureFlagStatus.ROLLOUT.value == "ROLLOUT"
    assert FeatureFlagStatus.ABGEKUENDIGT.value == "ABGEKUENDIGT"


def test_ff_rollout_strategie_enum_values():
    assert RolloutStrategie.ALLE.value == "ALLE"
    assert RolloutStrategie.PROZENTSATZ.value == "PROZENTSATZ"
    assert RolloutStrategie.TENANT_LISTE.value == "TENANT_LISTE"
    assert RolloutStrategie.ROLLE.value == "ROLLE"
    assert RolloutStrategie.KILL_SWITCH.value == "KILL_SWITCH"


def test_ff_variante_enum_values():
    assert FlagVariante.STANDARD.value == "STANDARD"
    assert FlagVariante.A.value == "A"
    assert FlagVariante.B.value == "B"
    assert FlagVariante.C.value == "C"


# --- ist_aktiv ---

def test_ff_ist_aktiv_true_when_aktiv():
    flag = _make_flag(status=FeatureFlagStatus.AKTIV)
    assert flag.ist_aktiv is True


def test_ff_ist_aktiv_false_when_inaktiv():
    flag = _make_flag(status=FeatureFlagStatus.INAKTIV)
    assert flag.ist_aktiv is False


def test_ff_ist_aktiv_false_when_rollout():
    flag = _make_flag(status=FeatureFlagStatus.ROLLOUT)
    assert flag.ist_aktiv is False


# --- ist_kill_switch ---

def test_ff_ist_kill_switch_true():
    flag = _make_flag(rollout_strategie=RolloutStrategie.KILL_SWITCH)
    assert flag.ist_kill_switch is True


def test_ff_ist_kill_switch_false_for_alle():
    flag = _make_flag(rollout_strategie=RolloutStrategie.ALLE)
    assert flag.ist_kill_switch is False


# --- pruefe_zugang: KILL_SWITCH ---

def test_ff_zugang_kill_switch_always_false_regardless_of_status():
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.KILL_SWITCH,
    )
    assert flag.pruefe_zugang("TENANT-001") is False


def test_ff_zugang_inaktiv_always_false():
    flag = _make_flag(
        status=FeatureFlagStatus.INAKTIV,
        rollout_strategie=RolloutStrategie.ALLE,
    )
    assert flag.pruefe_zugang("TENANT-001") is False


# --- pruefe_zugang: ALLE ---

def test_ff_zugang_alle_grants_any_tenant():
    flag = _make_flag(status=FeatureFlagStatus.AKTIV, rollout_strategie=RolloutStrategie.ALLE)
    assert flag.pruefe_zugang("TENANT-XYZ") is True


def test_ff_zugang_alle_grants_without_rolle():
    flag = _make_flag(status=FeatureFlagStatus.AKTIV, rollout_strategie=RolloutStrategie.ALLE)
    assert flag.pruefe_zugang("TENANT-001", "") is True


# --- pruefe_zugang: TENANT_LISTE ---

def test_ff_zugang_tenant_liste_grants_listed_tenant():
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.TENANT_LISTE,
        erlaubte_tenants=["TENANT-001", "TENANT-002"],
    )
    assert flag.pruefe_zugang("TENANT-001") is True


def test_ff_zugang_tenant_liste_denies_unlisted_tenant():
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.TENANT_LISTE,
        erlaubte_tenants=["TENANT-001"],
    )
    assert flag.pruefe_zugang("TENANT-099") is False


def test_ff_zugang_tenant_liste_empty_list_denies_all():
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.TENANT_LISTE,
        erlaubte_tenants=[],
    )
    assert flag.pruefe_zugang("TENANT-001") is False


# --- pruefe_zugang: ROLLE ---

def test_ff_zugang_rolle_grants_listed_rolle():
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.ROLLE,
        erlaubte_rollen=["admin", "einkaufsleiter"],
    )
    assert flag.pruefe_zugang("TENANT-001", "einkaufsleiter") is True


def test_ff_zugang_rolle_denies_unlisted_rolle():
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.ROLLE,
        erlaubte_rollen=["admin"],
    )
    assert flag.pruefe_zugang("TENANT-001", "sachbearbeiter") is False


def test_ff_zugang_rolle_empty_list_grants_all():
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.ROLLE,
        erlaubte_rollen=[],
    )
    assert flag.pruefe_zugang("TENANT-001", "any_rolle") is True


# --- pruefe_zugang: PROZENTSATZ ---

def test_ff_zugang_prozentsatz_100_always_grants():
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.PROZENTSATZ,
        rollout_prozentsatz=100,
    )
    # bucket is always 0-99, which is always < 100
    for tenant in ["TENANT-001", "TENANT-002", "TENANT-999", "TENANT-ABC"]:
        assert flag.pruefe_zugang(tenant) is True, f"Expected access for {tenant}"


def test_ff_zugang_prozentsatz_0_never_grants():
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.PROZENTSATZ,
        rollout_prozentsatz=0,
    )
    # bucket is always >= 0, which is never < 0
    for tenant in ["TENANT-001", "TENANT-002", "TENANT-999", "TENANT-ABC"]:
        assert flag.pruefe_zugang(tenant) is False, f"Expected no access for {tenant}"


def test_ff_zugang_prozentsatz_matches_hash_directly():
    # Verify the formula: bucket = abs(hash(tenant_id)) % 100 < rollout_prozentsatz
    tenant = "TENANT-HASH-TEST"
    bucket = abs(hash(tenant)) % 100
    threshold = bucket + 1  # rollout_prozentsatz just above bucket → must grant
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.PROZENTSATZ,
        rollout_prozentsatz=threshold,
    )
    assert flag.pruefe_zugang(tenant) is True


def test_ff_zugang_prozentsatz_excluded_when_bucket_equals_threshold():
    # rollout_prozentsatz == bucket → bucket < threshold is False
    tenant = "TENANT-HASH-TEST"
    bucket = abs(hash(tenant)) % 100
    flag = _make_flag(
        status=FeatureFlagStatus.AKTIV,
        rollout_strategie=RolloutStrategie.PROZENTSATZ,
        rollout_prozentsatz=bucket,  # not < bucket, so excluded
    )
    assert flag.pruefe_zugang(tenant) is False


# --- as_dict ---

def test_ff_as_dict_contains_ist_aktiv():
    flag = _make_flag(status=FeatureFlagStatus.AKTIV)
    d = flag.as_dict()
    assert d["ist_aktiv"] is True


def test_ff_as_dict_contains_ist_kill_switch():
    flag = _make_flag(rollout_strategie=RolloutStrategie.KILL_SWITCH)
    d = flag.as_dict()
    assert d["ist_kill_switch"] is True


def test_ff_as_dict_variante_is_string():
    flag = _make_flag(variante=FlagVariante.A)
    d = flag.as_dict()
    assert d["variante"] == "A"
    assert isinstance(d["variante"], str)


def test_ff_as_dict_status_is_string():
    flag = _make_flag(status=FeatureFlagStatus.ROLLOUT)
    d = flag.as_dict()
    assert d["status"] == "ROLLOUT"
    assert isinstance(d["status"], str)


# --- evaluiere_flags ---

def test_evaluiere_flags_returns_one_per_flag():
    flags = get_default_feature_flags()
    result = evaluiere_flags("TENANT-001", "admin", flags)
    assert len(result) == 5


def test_evaluiere_flags_hat_zugang_property():
    flags = [_make_flag(status=FeatureFlagStatus.AKTIV, rollout_strategie=RolloutStrategie.ALLE)]
    result = evaluiere_flags("TENANT-001", "", flags)
    assert result[0].hat_zugang is True


def test_evaluiere_flags_uses_provided_timestamp():
    ts = datetime(2026, 3, 16, 12, 0, 0, tzinfo=timezone.utc)
    flags = [_make_flag()]
    result = evaluiere_flags("TENANT-001", "", flags, evaluiert_am=ts)
    assert result[0].evaluiert_am == ts


def test_evaluiere_flags_defaults_timestamp_when_none():
    flags = [_make_flag()]
    result = evaluiere_flags("TENANT-001", "", flags, evaluiert_am=None)
    assert isinstance(result[0].evaluiert_am, datetime)


# --- get_aktive_flag_ids ---

def test_get_aktive_flag_ids_ff001_always_included():
    flags = get_default_feature_flags()
    active = get_aktive_flag_ids("TENANT-001", "admin", flags)
    assert "FF-001" in active


def test_get_aktive_flag_ids_ff005_never_included():
    flags = get_default_feature_flags()
    active = get_aktive_flag_ids("TENANT-001", "admin", flags)
    assert "FF-005" not in active


# --- get_default_feature_flags ---

def test_get_default_feature_flags_returns_5():
    flags = get_default_feature_flags()
    assert len(flags) == 5


def test_get_default_feature_flags_ff003_variante_a():
    flags = get_default_feature_flags()
    ff003 = next(f for f in flags if f.flag_id == "FF-003")
    assert ff003.variante == FlagVariante.A


def test_get_default_feature_flags_ff004_variante_b():
    flags = get_default_feature_flags()
    ff004 = next(f for f in flags if f.flag_id == "FF-004")
    assert ff004.variante == FlagVariante.B


def test_get_default_feature_flags_ff001_grants_all_tenants():
    flags = get_default_feature_flags()
    ff001 = next(f for f in flags if f.flag_id == "FF-001")
    assert ff001.pruefe_zugang("ANY-TENANT") is True


def test_get_default_feature_flags_ff003_grants_listed_tenants_only():
    flags = get_default_feature_flags()
    ff003 = next(f for f in flags if f.flag_id == "FF-003")
    assert ff003.pruefe_zugang("TENANT-001") is True
    assert ff003.pruefe_zugang("TENANT-999") is False


def test_get_default_feature_flags_ff004_grants_correct_roles():
    flags = get_default_feature_flags()
    ff004 = next(f for f in flags if f.flag_id == "FF-004")
    assert ff004.pruefe_zugang("TENANT-001", "einkaufsleiter") is True
    assert ff004.pruefe_zugang("TENANT-001", "disposition") is True
    assert ff004.pruefe_zugang("TENANT-001", "sachbearbeiter") is False


def test_get_default_feature_flags_ff005_never_grants():
    flags = get_default_feature_flags()
    ff005 = next(f for f in flags if f.flag_id == "FF-005")
    assert ff005.pruefe_zugang("TENANT-001") is False


# ===========================================================================
# Process Cost Contracts — 30 tests
# ===========================================================================

# --- Enum values ---

def test_kosten_typ_enum_values():
    assert KostenTyp.CPU.value == "CPU"
    assert KostenTyp.SPEICHER.value == "SPEICHER"
    assert KostenTyp.NETZWERK.value == "NETZWERK"
    assert KostenTyp.STORAGE.value == "STORAGE"
    assert KostenTyp.EXTERNE_API.value == "EXTERNE_API"
    assert KostenTyp.MANUELL.value == "MANUELL"


def test_abrechnungs_einheit_enum_values():
    assert AbrechnungsEinheit.PRO_AUSFUEHRUNG.value == "PRO_AUSFUEHRUNG"
    assert AbrechnungsEinheit.PRO_SEKUNDE.value == "PRO_SEKUNDE"
    assert AbrechnungsEinheit.PRO_MEGABYTE.value == "PRO_MEGABYTE"
    assert AbrechnungsEinheit.PRO_API_AUFRUF.value == "PRO_API_AUFRUF"
    assert AbrechnungsEinheit.PAUSCHAL.value == "PAUSCHAL"


def test_budget_status_enum_values():
    assert BudgetStatus.IM_RAHMEN.value == "IM_RAHMEN"
    assert BudgetStatus.WARNUNG.value == "WARNUNG"
    assert BudgetStatus.UEBERSCHRITTEN.value == "UEBERSCHRITTEN"
    assert BudgetStatus.GESPERRT.value == "GESPERRT"


# --- KostenPosition.gesamt_eur ---

def test_kosten_position_gesamt_eur_basic():
    pos = _make_position(menge=10.0, einheit_preis_eur=0.05)
    assert pos.gesamt_eur == 0.5


def test_kosten_position_gesamt_eur_rounded_to_4_decimals():
    pos = _make_position(menge=3.0, einheit_preis_eur=0.0001)
    assert pos.gesamt_eur == round(3.0 * 0.0001, 4)


def test_kosten_position_gesamt_eur_zero_menge():
    pos = _make_position(menge=0.0, einheit_preis_eur=100.0)
    assert pos.gesamt_eur == 0.0


# --- KostenPosition.as_dict ---

def test_kosten_position_as_dict_includes_gesamt_eur():
    pos = _make_position(menge=5.0, einheit_preis_eur=2.0)
    d = pos.as_dict()
    assert d["gesamt_eur"] == 10.0


def test_kosten_position_as_dict_kosten_typ_is_string():
    pos = _make_position(kosten_typ=KostenTyp.EXTERNE_API)
    d = pos.as_dict()
    assert d["kosten_typ"] == "EXTERNE_API"
    assert isinstance(d["kosten_typ"], str)


def test_kosten_position_as_dict_abrechnungs_einheit_is_string():
    pos = _make_position(abrechnungs_einheit=AbrechnungsEinheit.PRO_MEGABYTE)
    d = pos.as_dict()
    assert d["abrechnungs_einheit"] == "PRO_MEGABYTE"
    assert isinstance(d["abrechnungs_einheit"], str)


# --- ProzessKostenErfassung ---

def test_prozess_kosten_erfassung_gesamt_kosten_empty():
    erfassung = ProzessKostenErfassung(
        erfassung_id="E-001",
        workflow_instanz_id="WI-001",
        tenant_id="TENANT-001",
        erstellt_am=datetime(2026, 3, 16),
        positionen=[],
    )
    assert erfassung.gesamt_kosten_eur == 0.0


def test_prozess_kosten_erfassung_gesamt_kosten_sum():
    pos1 = _make_position("P1", KostenTyp.CPU, menge=10.0, einheit_preis_eur=0.01)
    pos2 = _make_position("P2", KostenTyp.SPEICHER, menge=5.0, einheit_preis_eur=0.02)
    erfassung = ProzessKostenErfassung(
        erfassung_id="E-002",
        workflow_instanz_id="WI-002",
        tenant_id="TENANT-001",
        erstellt_am=datetime(2026, 3, 16),
        positionen=[pos1, pos2],
    )
    # CPU: 10*0.01=0.10, SPEICHER: 5*0.02=0.10 → total=0.20
    assert erfassung.gesamt_kosten_eur == pytest.approx(0.20, abs=1e-4)


def test_prozess_kosten_erfassung_positionen_nach_typ_groups_correctly():
    pos1 = _make_position("P1", KostenTyp.CPU, menge=2.0, einheit_preis_eur=1.0)
    pos2 = _make_position("P2", KostenTyp.CPU, menge=3.0, einheit_preis_eur=1.0)
    pos3 = _make_position("P3", KostenTyp.NETZWERK, menge=1.0, einheit_preis_eur=5.0)
    erfassung = ProzessKostenErfassung(
        erfassung_id="E-003",
        workflow_instanz_id="WI-003",
        tenant_id="TENANT-001",
        erstellt_am=datetime(2026, 3, 16),
        positionen=[pos1, pos2, pos3],
    )
    typ_map = erfassung.positionen_nach_typ
    assert typ_map["CPU"] == pytest.approx(5.0, abs=1e-4)
    assert typ_map["NETZWERK"] == pytest.approx(5.0, abs=1e-4)


def test_prozess_kosten_erfassung_as_dict_includes_positionen_anzahl():
    pos1 = _make_position("P1")
    pos2 = _make_position("P2")
    erfassung = ProzessKostenErfassung(
        erfassung_id="E-004",
        workflow_instanz_id="WI-004",
        tenant_id="TENANT-001",
        erstellt_am=datetime(2026, 3, 16),
        positionen=[pos1, pos2],
    )
    d = erfassung.as_dict()
    assert d["positionen_anzahl"] == 2


def test_prozess_kosten_erfassung_as_dict_includes_gesamt_kosten():
    pos = _make_position(menge=4.0, einheit_preis_eur=2.5)
    erfassung = ProzessKostenErfassung(
        erfassung_id="E-005",
        workflow_instanz_id="WI-005",
        tenant_id="TENANT-001",
        erstellt_am=datetime(2026, 3, 16),
        positionen=[pos],
    )
    d = erfassung.as_dict()
    assert d["gesamt_kosten_eur"] == pytest.approx(10.0, abs=1e-4)


def test_prozess_kosten_erfassung_as_dict_includes_positionen_nach_typ():
    pos = _make_position(kosten_typ=KostenTyp.STORAGE, menge=1.0, einheit_preis_eur=3.0)
    erfassung = ProzessKostenErfassung(
        erfassung_id="E-006",
        workflow_instanz_id="WI-006",
        tenant_id="TENANT-001",
        erstellt_am=datetime(2026, 3, 16),
        positionen=[pos],
    )
    d = erfassung.as_dict()
    assert "positionen_nach_typ" in d
    assert d["positionen_nach_typ"]["STORAGE"] == pytest.approx(3.0, abs=1e-4)


# --- BudgetUeberwachung ---

def test_budget_auslastung_pct_basic():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=500.0)
    assert b.auslastung_pct == 50.0


def test_budget_auslastung_pct_zero_when_budget_zero():
    b = _make_budget(budget_eur=0.0, verbraucht_eur=100.0)
    assert b.auslastung_pct == 0.0


def test_budget_verbleibend_eur_positive():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=300.0)
    assert b.verbleibend_eur == pytest.approx(700.0, abs=1e-4)


def test_budget_verbleibend_eur_negative_when_overspent():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=1200.0)
    assert b.verbleibend_eur == pytest.approx(-200.0, abs=1e-4)


def test_budget_status_im_rahmen():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=500.0)
    assert b.budget_status == BudgetStatus.IM_RAHMEN


def test_budget_status_warnung_at_80_pct():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=800.0)
    assert b.budget_status == BudgetStatus.WARNUNG


def test_budget_status_ueberschritten_at_100_pct():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=1000.0)
    assert b.budget_status == BudgetStatus.UEBERSCHRITTEN


def test_budget_status_gesperrt_when_over_budget():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=1001.0)
    assert b.budget_status == BudgetStatus.GESPERRT


def test_budget_as_dict_includes_auslastung_pct():
    b = _make_budget(budget_eur=200.0, verbraucht_eur=100.0)
    d = b.as_dict()
    assert d["auslastung_pct"] == 50.0


def test_budget_as_dict_includes_verbleibend_eur():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=400.0)
    d = b.as_dict()
    assert d["verbleibend_eur"] == pytest.approx(600.0, abs=1e-4)


def test_budget_as_dict_budget_status_is_string():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=200.0)
    d = b.as_dict()
    assert d["budget_status"] == "IM_RAHMEN"
    assert isinstance(d["budget_status"], str)


# --- erstelle_kosten_erfassung ---

def test_erstelle_kosten_erfassung_sets_fields():
    pos = _make_position()
    ts = datetime(2026, 3, 16, 10, 0, 0)
    erfassung = erstelle_kosten_erfassung("E-100", "WI-100", "TENANT-001", [pos], erstellt_am=ts)
    assert erfassung.erfassung_id == "E-100"
    assert erfassung.workflow_instanz_id == "WI-100"
    assert erfassung.tenant_id == "TENANT-001"
    assert erfassung.erstellt_am == ts
    assert len(erfassung.positionen) == 1


def test_erstelle_kosten_erfassung_defaults_timestamp():
    erfassung = erstelle_kosten_erfassung("E-101", "WI-101", "TENANT-001", [], erstellt_am=None)
    assert isinstance(erfassung.erstellt_am, datetime)


# --- pruefe_budget ---

def test_pruefe_budget_does_not_modify_original():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=500.0)
    pruefe_budget(b, 600.0)
    assert b.verbraucht_eur == 500.0


def test_pruefe_budget_im_rahmen():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=100.0)
    status = pruefe_budget(b, 200.0)
    assert status == BudgetStatus.IM_RAHMEN


def test_pruefe_budget_warnung():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=600.0)
    status = pruefe_budget(b, 250.0)  # 850 / 1000 = 85% → WARNUNG
    assert status == BudgetStatus.WARNUNG


def test_pruefe_budget_ueberschritten():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=900.0)
    status = pruefe_budget(b, 100.0)  # 1000 / 1000 = 100% → UEBERSCHRITTEN
    assert status == BudgetStatus.UEBERSCHRITTEN


def test_pruefe_budget_gesperrt():
    b = _make_budget(budget_eur=1000.0, verbraucht_eur=950.0)
    status = pruefe_budget(b, 100.0)  # 1050 > 1000 → GESPERRT
    assert status == BudgetStatus.GESPERRT


# --- get_default_budget_ueberwachungen ---

def test_get_default_budget_returns_4():
    budgets = get_default_budget_ueberwachungen()
    assert len(budgets) == 4


def test_get_default_budget_bu001_im_rahmen():
    budgets = get_default_budget_ueberwachungen()
    bu001 = next(b for b in budgets if b.budget_id == "BU-001")
    assert bu001.budget_status == BudgetStatus.IM_RAHMEN


def test_get_default_budget_bu002_warnung():
    budgets = get_default_budget_ueberwachungen()
    bu002 = next(b for b in budgets if b.budget_id == "BU-002")
    assert bu002.budget_status == BudgetStatus.WARNUNG


def test_get_default_budget_bu003_gesperrt():
    budgets = get_default_budget_ueberwachungen()
    bu003 = next(b for b in budgets if b.budget_id == "BU-003")
    assert bu003.budget_status == BudgetStatus.GESPERRT


def test_get_default_budget_bu004_im_rahmen():
    budgets = get_default_budget_ueberwachungen()
    bu004 = next(b for b in budgets if b.budget_id == "BU-004")
    assert bu004.budget_status == BudgetStatus.IM_RAHMEN


def test_get_default_budget_custom_tenant_id():
    budgets = get_default_budget_ueberwachungen(tenant_id="TENANT-XYZ")
    for b in budgets:
        assert b.tenant_id == "TENANT-XYZ"
