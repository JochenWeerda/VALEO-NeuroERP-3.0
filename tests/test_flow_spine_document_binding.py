"""FSX-010/011 — Belegzentrierter Einstieg: Fallsuche und kollisionsfeste Anlage.

Geprueft wird die Logik, nicht die Datenbank: der partielle Unique-Index kann
ohne PostgreSQL nicht laufen. Was hier gehalten wird, ist deshalb
(a) die Uebereinstimmung von Index-Bedingung und Anwendungslogik,
(b) die Aufloesung einer Kollision, und
(c) die Abgrenzung offen/abgeschlossen.

Die Index-Bedingung selbst steht in
alembic/versions/flow_spine_document_link_unique_20260915.py und wird gegen die
Konstante im Endpunkt gehalten — weicht eines ab, greift der Index an anderer
Stelle als der Code.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.api.v1.endpoints.flow_spines import CLOSED_LIFECYCLE_STATUSES

pytestmark = pytest.mark.unit

MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "flow_spine_document_link_unique_20260915.py"
)


def test_migration_existiert() -> None:
    assert MIGRATION.is_file(), "FSX-011-Migration fehlt"


def test_index_bedingung_deckt_sich_mit_der_anwendungslogik() -> None:
    """Der Index darf nicht andere Faelle ausnehmen als der Endpunkt."""
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


def test_index_ist_partiell_und_mandantengetrennt() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert 'INDEX_NAME = "uq_flow_spine_open_document_link"' in text
    assert "CREATE UNIQUE INDEX IF NOT EXISTS {INDEX_NAME}" in text
    # Mandant und Prozess gehoeren in den Schluessel: sonst blockieren sich
    # Mandanten gegenseitig, bzw. derselbe Beleg kann in zwei Prozessen keinen
    # eigenen Vorgang mehr haben.
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

    # Faelle ohne Belegreferenz bleiben ausgenommen — sie sind manuell
    # angelegte Vorgaenge und unterliegen der Idempotenz nicht.
    assert "linked_document_id IS NOT NULL" in text
    assert "linked_document_type IS NOT NULL" in text


def test_bereinigung_loescht_keine_vorgaenge() -> None:
    """Dubletten verlieren den Belegbezug, aber kein Vorgang wird geloescht."""
    text = MIGRATION.read_text(encoding="utf-8")
    assert "UPDATE domain_ops.ops_flow_spine_instances" in text
    assert "DELETE FROM domain_ops.ops_flow_spine_instances" not in text, (
        "Die Vorabbereinigung darf keine Vorgaenge loeschen — ein entzogener "
        "Belegbezug ist umkehrbar, ein geloeschter Vorgang nicht."
    )


def test_lookup_index_deckt_auch_abgeschlossene_vorgaenge() -> None:
    """FSX-010 fragt auch ueber abgeschlossene Faelle; der partielle Index reicht nicht."""
    text = MIGRATION.read_text(encoding="utf-8")
    assert "ix_flow_spine_document_lookup" in text


def test_abgeschlossene_zustaende_sind_vollstaendig() -> None:
    """completed, cancelled, failed — und 'on_hold' gehoert ausdruecklich nicht dazu."""
    assert set(CLOSED_LIFECYCLE_STATUSES) == {"completed", "cancelled", "failed"}
    assert "on_hold" not in CLOSED_LIFECYCLE_STATUSES, (
        "Ein pausierter Vorgang ist offen. Zaehlte er als abgeschlossen, "
        "koennte parallel ein zweiter Fall zum selben Beleg entstehen."
    )


def test_endpunkt_faengt_integrityerror_und_gibt_bestehenden_fall_zurueck() -> None:
    """Der Wettlauf wird aufgeloest, nicht durchgereicht."""
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
    # Ohne Belegreferenz gibt es nichts aufzuloesen — dann muss der Fehler
    # sichtbar bleiben statt als Erfolg durchzugehen.
    assert "if not has_document_ref:" in source


def test_patch_meldet_konflikt_statt_stillschweigender_umbindung() -> None:
    """V14: Beim Aktualisieren ist die Kollision ein Konflikt, kein Idempotenzfall."""
    source = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "api"
        / "v1"
        / "endpoints"
        / "flow_spines.py"
    ).read_text(encoding="utf-8")

    assert "status_code=409" in source, (
        "Ein PATCH, der einen Beleg an einen fremden offenen Vorgang haengt, "
        "muss einen Konflikt melden — nicht stillschweigend den anderen Fall "
        "zurueckgeben."
    )


def test_halbe_belegangabe_wird_abgewiesen() -> None:
    """Nur die Art oder nur die Nummer wuerde lautlos die ganze Liste liefern."""
    source = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "api"
        / "v1"
        / "endpoints"
        / "flow_spines.py"
    ).read_text(encoding="utf-8")

    assert "bool(linked_document_id) != bool(linked_document_type)" in source
    assert "status_code=422" in source
