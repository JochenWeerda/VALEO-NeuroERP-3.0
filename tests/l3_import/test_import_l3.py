from __future__ import annotations

import json

import pytest

from scripts.import_l3 import (
    ImportContractError,
    load_table_file,
    normalize_table_identifier,
    parse_since_value,
    select_rows_since,
    validate_source_contract,
)


def test_validate_source_contract_rejects_missing_export_file(tmp_path):
    mapping = {
        "ABSCHLUSS": {
            "JAHR": {"target": "domain_finance.period_closure.fiscal_year"},
        }
    }

    with pytest.raises(ImportContractError) as exc:
        validate_source_contract(mapping, tmp_path)

    assert "Missing export file for mapped table" in str(exc.value)


def test_validate_source_contract_rejects_empty_csv(tmp_path):
    mapping = {
        "ABSCHLUSS": {
            "JAHR": {"target": "domain_finance.period_closure.fiscal_year"},
        }
    }
    (tmp_path / "ABSCHLUSS.csv").write_text("JAHR\n", encoding="utf-8")

    with pytest.raises(ImportContractError) as exc:
        validate_source_contract(mapping, tmp_path)

    assert "contains no rows" in str(exc.value)


def test_validate_source_contract_rejects_missing_required_column_but_ignores_skipped(tmp_path):
    mapping = {
        "ABSCHLUSS": {
            "JAHR": {"target": "domain_finance.period_closure.fiscal_year"},
            "ALTSPALTE": {"skip": True},
        }
    }
    (tmp_path / "ABSCHLUSS.csv").write_text("MONAT\n3\n", encoding="utf-8")

    with pytest.raises(ImportContractError) as exc:
        validate_source_contract(mapping, tmp_path)

    message = str(exc.value)
    assert "Column JAHR not present" in message
    assert "ALTSPALTE" not in message


def test_load_table_file_rejects_non_tabular_json(tmp_path):
    file_path = tmp_path / "ABSCHLUSS.json"
    file_path.write_text(json.dumps({"unexpected": "shape"}), encoding="utf-8")

    with pytest.raises(ImportContractError) as exc:
        load_table_file(file_path)

    assert "must contain a list of row objects" in str(exc.value)


def test_validate_source_contract_accepts_valid_json_rows(tmp_path):
    mapping = {
        "ABSCHLUSS": {
            "JAHR": {"target": "domain_finance.period_closure.fiscal_year"},
        }
    }
    (tmp_path / "ABSCHLUSS.json").write_text(json.dumps([{"JAHR": 2026}]), encoding="utf-8")

    validate_source_contract(mapping, tmp_path)


def test_select_rows_since_filters_rows_on_preferred_column():
    rows = [
        {"UPDATED_AT": "2024-01-01T00:00:00", "ID": 1},
        {"UPDATED_AT": "2024-03-01T12:00:00", "ID": 2},
    ]

    selected, used_column = select_rows_since(
        rows,
        since=parse_since_value("2024-02-01"),
        preferred_column="UPDATED_AT",
    )

    assert used_column == "UPDATED_AT"
    assert [row["ID"] for row in selected] == [2]


def test_select_rows_since_keeps_rows_when_no_incremental_column_exists():
    rows = [{"ID": 1}, {"ID": 2}]

    selected, used_column = select_rows_since(
        rows,
        since=parse_since_value("2024-02-01"),
    )

    assert used_column is None
    assert selected == rows


def test_normalize_table_identifier_converts_legacy_names():
    assert normalize_table_identifier("WWS_ARECHNUNG3") == "wws_arechnung3"
    assert normalize_table_identifier("  Abschluss Liste ") == "abschluss_liste"
