"""Vertrag: ein Cast auf einem Bind-Parameter muss den Parameter binden.

Die Schreibweise ``:name::typ`` sieht richtig aus, bindet aber nicht — sie ist
die Ursache dafuer gewesen, dass Dokumente still in den In-Memory-Fallback
liefen und die E-Rechnungs-Endpunkte danach 404 lieferten.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "name",
    ["data", "ids", "config_json", "date_from", "src_ids", "cnt"],
)
def test_doppelpunkt_cast_verliert_den_parameternamen(name: str) -> None:
    """Dokumentiert die Falle: der gebundene Name ist nicht der geschriebene."""
    gebunden = list(text(f"SELECT :{name}::jsonb")._bindparams)
    assert gebunden != [name], (
        "Diese SQLAlchemy-Version bindet ':name::typ' inzwischen korrekt - "
        "dann darf das Gate scripts/check_sql_bind_casts.py gelockert werden."
    )


@pytest.mark.parametrize(
    "name",
    ["data", "ids", "config_json", "date_from", "src_ids", "cnt"],
)
def test_cast_schreibweise_bindet_den_vollen_namen(name: str) -> None:
    gebunden = list(text(f"SELECT CAST(:{name} AS jsonb)")._bindparams)
    assert gebunden == [name]


def test_spaltencast_bleibt_unberuehrt() -> None:
    """``data::jsonb`` ist ein Spaltencast und darf keinen Parameter erzeugen."""
    anweisung = text("SELECT 1 FROM t WHERE data::jsonb->>'status' = :status")
    assert list(anweisung._bindparams) == ["status"]


def test_repository_insert_bindet_alle_parameter() -> None:
    """Die reparierte Anweisung aus app/documents/repository.py."""
    anweisung = text(
        """
        INSERT INTO documents (id, doc_type, doc_number, data, created_at, updated_at)
        VALUES (:id, :doc_type, :doc_number, CAST(:data AS jsonb), :created_at, :updated_at)
        """
    )
    assert sorted(anweisung._bindparams) == [
        "created_at",
        "data",
        "doc_number",
        "doc_type",
        "id",
        "updated_at",
    ]


def test_gate_findet_die_fehlerhafte_schreibweise() -> None:
    """Der Waechter selbst muss die Falle erkennen."""
    from scripts.check_sql_bind_casts import PATTERN

    assert PATTERN.search("VALUES (:id, :data::jsonb)")
    assert PATTERN.search("SET config_json = :config_json::jsonb")
    assert not PATTERN.search("WHERE data::jsonb->>'status' = :status")
    assert not PATTERN.search("VALUES (:id, CAST(:data AS jsonb))")


def test_repository_enthaelt_keine_fehlerhafte_schreibweise_mehr() -> None:
    from scripts.check_sql_bind_casts import find_hits

    treffer = [h for h in find_hits(("app",)) if h[0].endswith("documents/repository.py")]
    assert treffer == []
