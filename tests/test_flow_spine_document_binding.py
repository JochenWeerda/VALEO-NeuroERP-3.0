"""FSX-010/011 — Belegzentrierter Einstieg: Fallsuche und kollisionsfeste Anlage.

Geprueft wird die Logik, nicht die Datenbank: der partielle Unique-Index kann
ohne PostgreSQL nicht laufen. Was hier gehalten wird, ist deshalb
(a) die Uebereinstimmung von Index-Bedingung und Anwendungslogik,
(b) die Aufloesung einer Kollision,
(c) ein Index statt zwei,
(d) Leerstring-Normalisierung, sonst greift der Index am falschen Ende.

Die Index-Bedingung selbst steht in
alembic/versions/flow_spine_document_link_unique_20260915.py.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.flow_spines import (
    CLOSED_LIFECYCLE_STATUSES,
    _normalize_document_ref,
    _require_complete_document_ref,
)

pytestmark = pytest.mark.unit

MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "flow_spine_document_link_unique_20260915.py"
)


def test_migration_existiert() -> None:
    assert MIGRATION.is_file(), "FSX-011-Migration fehlt"


def test_migration_haengt_am_aktuellen_head() -> None:
    """Eine alte down_revision erzeugt einen zweiten Alembic-Head."""
    text = MIGRATION.read_text(encoding="utf-8")
    assert 'down_revision = "agrar_harvest_acceptances_sammel_20260911"' in text


def test_index_bedingung_deckt_sich_mit_der_anwendungslogik() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    match = re.search(r"_CLOSED\s*=\s*\"([^\"]+)\"", text)
    assert match, "Die Migration deklariert keine _CLOSED-Liste"

    in_migration = {part.strip().strip("'") for part in match.group(1).split(",")}
    assert in_migration == set(CLOSED_LIFECYCLE_STATUSES), (
        "Die abgeschlossenen Lebenszyklus-Zustaende in der Migration und im "
        "Endpunkt laufen auseinander. Dann blockiert der Index andere Faelle als "
        "die Anwendungslogik erwartet — und der Wettlauf wird an genau der "
        f"Stelle nicht abgefangen. Migration: {sorted(in_migration)}, "
        f"Endpunkt: {sorted(CLOSED_LIFECYCLE_STATUSES)}"
    )


def test_index_ist_partiell_mandantengetrennt_und_ohne_leerstring() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert 'INDEX_NAME = "uq_flow_spine_open_by_document"' in text
    assert "CREATE UNIQUE INDEX IF NOT EXISTS {INDEX_NAME}" in text
    key_match = re.search(
        r"CREATE UNIQUE INDEX IF NOT EXISTS \{INDEX_NAME\}[^(]*\(([^)]*)\)", text
    )
    assert key_match, "Schluesselspalten des Unique-Index nicht gefunden"
    key = [c.strip() for c in key_match.group(1).split(",")]
    assert key == [
        "tenant_id",
        "process_key",
        "linked_document_type",
        "linked_document_id",
    ], f"Unerwarteter Schluessel: {key}"

    assert "btrim(linked_document_id) <> ''" in text
    assert "btrim(linked_document_type) <> ''" in text


def test_kein_zweiter_index_ohne_process_key() -> None:
    """FSX-010 nutzt denselben Schluessel. Ein schwacherer Lookup-Index entsteht nicht."""
    text = MIGRATION.read_text(encoding="utf-8")
    assert "ix_flow_spine_document_lookup" not in text
    assert text.count("CREATE INDEX") == 0
    assert text.count("CREATE UNIQUE INDEX") == 1


def test_bereinigung_loescht_keine_vorgaenge() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    assert "UPDATE domain_ops.ops_flow_spine_instances" in text
    assert "DELETE FROM domain_ops.ops_flow_spine_instances" not in text, (
        "Die Vorabbereinigung darf keine Vorgaenge loeschen — ein entzogener "
        "Belegbezug ist umkehrbar, ein geloeschter Vorgang nicht."
    )


def test_abgeschlossene_zustaende_sind_vollstaendig() -> None:
    assert set(CLOSED_LIFECYCLE_STATUSES) == {"completed", "cancelled", "failed"}
    assert "on_hold" not in CLOSED_LIFECYCLE_STATUSES, (
        "Ein pausierter Vorgang ist offen. Zaehlte er als abgeschlossen, "
        "koennte parallel ein zweiter Fall zum selben Beleg entstehen."
    )


def test_endpunkt_faengt_integrityerror_und_gibt_bestehenden_fall_zurueck() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "api"
        / "v1"
        / "endpoints"
        / "flow_spines.py"
    ).read_text(encoding="utf-8")

    assert "except IntegrityError" in source
    assert "_find_open_instance_for_document" in source
    assert "if not has_document_ref:" in source


def test_patch_meldet_konflikt_statt_stillschweigender_umbindung() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "api"
        / "v1"
        / "endpoints"
        / "flow_spines.py"
    ).read_text(encoding="utf-8")

    assert "status_code=409" in source


def test_halbe_belegangabe_wird_abgewiesen() -> None:
    with pytest.raises(HTTPException) as caught:
        _require_complete_document_ref("PO-1", None)
    assert caught.value.status_code == 422
    _require_complete_document_ref(None, None)
    _require_complete_document_ref("PO-1", "purchase_order")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, None),
        ("", None),
        ("   ", None),
        ("PO-1", "PO-1"),
        ("  PO-1  ", "PO-1"),
    ],
)
def test_leerstring_wird_zu_null(raw: str | None, expected: str | None) -> None:
    assert _normalize_document_ref(raw) == expected
