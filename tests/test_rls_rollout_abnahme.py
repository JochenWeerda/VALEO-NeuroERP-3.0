"""Explizite Domain-Abnahme bleibt von zufaelligen Heuristiktreffern unabhaengig."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import rls_rollout as rollout
import rls_domain_matrix as matrix


def test_nur_explizite_rueckstellung_haelt_kandidaten_zurueck(monkeypatch):
    held, other = "domain_agrar.seed_orders", "domain_x.neu"
    inventory = {"tables": [
        {"table": held, "class": "A", "rls": False},
        {"table": other, "class": "A", "rls": False},
    ]}
    monkeypatch.setattr(rollout, "_code_files", lambda: iter([]))
    result = rollout.analyse(inventory)
    assert result["pending"] == {held: ["abnahme_ausstehend"]}
    assert result["ready"] == [other]  # Neue unsichere Tabellen bleiben fuer das Gate sichtbar.
    assert matrix.policy("abnahme_ausstehend", {}, None).startswith("keine Aktivierung")


def test_abgesicherte_tabellen_duerfen_keinen_veralteten_abnahmevermerk_haben():
    inventory = json.loads(rollout.INVENTORY.read_text(encoding="utf-8"))
    unprotected = {row["table"] for row in inventory["tables"] if row["class"] == "A" and not row["rls"]}
    assert set(rollout.rollout_holds()) <= unprotected


def test_manuelle_rueckstellung_hat_vorrang_vor_gemeinsamer_lesbarkeit():
    table = "domain_x.audit"
    inventory = {"tables": [{"table": table, "class": "A", "rls": False}]}
    projected = {"pending": {table: ["abnahme_ausstehend"]}}
    files = [("app/audit.py", "SELECT * FROM domain_x.audit WHERE tenant_id IS NULL OR tenant_id = 'system'")]
    row = matrix.analyse(inventory, projected, {"tables": {}}, files)["tables"][0]
    assert "referenzdaten" in row["gruende"]
    assert "abnahme_ausstehend" in row["gruende"]
    assert row["policy"].startswith("keine Aktivierung")


@pytest.mark.parametrize("holds", [
    {"domain_x.nicht_bisher_zurueckgestellt": "beliebiger Grund"},
    {"domain_agrar.seed_orders": " "},
    {"domain_agrar.seed_orders": None},
    [],
])
def test_rueckstellung_darf_weder_neue_ausnahme_noch_leere_begruendung_sein(tmp_path, monkeypatch, holds):
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps({"zurueckgestellt": {"domain_agrar.seed_orders": "abnahme_ausstehend"},
                                "rollout_abnahme": holds}), encoding="utf-8")
    monkeypatch.setattr(rollout, "EXCEPTIONS", path)
    with pytest.raises(ValueError):
        rollout.rollout_holds()
