"""FSX-DOC-LINKS — beteiligte Belege je Flow-Spine-Vorgang.

Der Zweck dieser Tabelle ist, einen Widerspruch aufzuloesen, **bevor** er
ausloest: das n:m-Belegmodell verlangt, dass eine Rechnung sich an denselben
Vorgang haengen kann wie der Lieferschein — waehrend FSX-012 das Umbiegen des
fuehrenden Belegs zu Recht mit 409 abweist. Beides geht nur, wenn der fuehrende
Beleg und die beteiligten Belege getrennte Dinge sind.

Geprueft wird die Modell- und Vertragsebene; die Endpunkte selbst brauchen eine
Datenbank und laufen in den API-Tests.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.domains.operations.models import FlowSpineInstanceDocument

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "alembic" / "versions" / "flow_spine_instance_documents_20260915.py"
ENDPOINTS = ROOT / "app" / "api" / "v1" / "endpoints" / "flow_spines.py"


def test_ein_beleg_darf_in_mehreren_vorgaengen_beteiligt_sein() -> None:
    """Die Sammelrechnung ist der Grund fuer diese Tabelle.

    Eine Rechnung ueber drei Lieferscheine gehoert zu drei Vorgaengen. Eine
    globale Eindeutigkeit auf (Mandant, Belegart, Beleg-ID) wuerde genau das
    verbieten — sie darf es also nicht geben.
    """
    unique_columns = [
        tuple(sorted(constraint.columns.keys()))
        for constraint in FlowSpineInstanceDocument.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    ]
    for columns in unique_columns:
        assert "instance_id" in columns, (
            f"Eindeutigkeit ohne instance_id gefunden: {columns}. Damit koennte "
            "ein Beleg nur in genau einem Vorgang beteiligt sein, und eine "
            "Sammelrechnung ueber mehrere Lieferscheine waere nicht abbildbar."
        )


def test_derselbe_beleg_nicht_zweimal_im_selben_vorgang() -> None:
    """Das ist es, was das Anhaengen idempotent macht."""
    unique_columns = {
        tuple(sorted(constraint.columns.keys()))
        for constraint in FlowSpineInstanceDocument.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }
    expected = tuple(sorted(("tenant_id", "instance_id", "document_type", "document_id")))
    assert expected in unique_columns, (
        f"Erwartete Eindeutigkeit {expected} fehlt; gefunden: {unique_columns}"
    )


def test_mandant_ist_teil_des_schluessels() -> None:
    columns = FlowSpineInstanceDocument.__table__.columns
    assert "tenant_id" in columns
    assert columns["tenant_id"].nullable is False


def test_tabelle_traegt_keine_mengen() -> None:
    """Mengen gehoeren in das positionsbezogene n:m-Modell, nicht an den Vorgang.

    Eine Mengenspalte hier waere der Anfang eines zweiten, schwaecheren
    Belegflusses neben dem eigentlichen — und die beiden liefen garantiert
    auseinander.
    """
    verbotene = {"menge", "quantity", "qty", "amount", "unit", "einheit"}
    vorhanden = {name.lower() for name in FlowSpineInstanceDocument.__table__.columns.keys()}
    ueberschneidung = verbotene & vorhanden
    assert not ueberschneidung, (
        f"Mengenspalten in der Verknuepfungstabelle: {sorted(ueberschneidung)}. "
        "Teilmengen gehoeren in den Belegfluss (Quellposition, Zielposition, "
        "Menge, Status), nicht an die Vorgangsverknuepfung."
    )


def test_migration_haengt_am_flow_spine_strang() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    assert 'down_revision = "flow_spine_document_link_unique_20260915"' in text


def test_migration_legt_keine_globale_eindeutigkeit_an() -> None:
    """Der Rueckwaerts-Index darf kein UNIQUE sein — sonst faellt die Sammelrechnung."""
    text = MIGRATION.read_text(encoding="utf-8")

    unique_blocks = re.findall(r"CREATE UNIQUE INDEX[^;]+;", text)
    assert len(unique_blocks) == 1, f"Erwartet genau ein UNIQUE, gefunden {len(unique_blocks)}"
    assert "instance_id" in unique_blocks[0], (
        "Der einzige UNIQUE-Index muss instance_id enthalten, sonst kann ein "
        "Beleg nur zu einem Vorgang gehoeren."
    )

    assert 'LOOKUP_NAME = "ix_flow_spine_instance_document_lookup"' in text
    lookup = re.search(r"CREATE INDEX IF NOT EXISTS \{LOOKUP_NAME\}[^;]+;", text)
    assert lookup, "Rueckwaerts-Index fuer die Belegsuche fehlt"
    assert "UNIQUE" not in lookup.group(0)


def test_fuehrender_beleg_bleibt_unangetastet() -> None:
    """Der Schutz aus FSX-011/FSX-012 darf durch diesen Slice nicht aufgeweicht sein."""
    source = ENDPOINTS.read_text(encoding="utf-8")

    assert "_reject_rebind_to_other_document" in source, (
        "Der Schutz gegen Umbiegen des fuehrenden Belegs ist verschwunden. "
        "Die Verknuepfungstabelle sollte ihn ueberfluessig machen, nicht ersetzen."
    )
    assert "status_code=409" in source


def test_anhaengen_ist_idempotent_und_faengt_den_wettlauf() -> None:
    source = ENDPOINTS.read_text(encoding="utf-8")
    block = source[source.index("def attach_instance_document") :]
    block = block[: block.index("def detach_instance_document")]

    # Vorab nachschlagen genuegt nicht — zwei gleichzeitige Aufrufe sehen beide
    # "nicht vorhanden". Der Unique-Index entscheidet, der Code loest auf.
    assert "except IntegrityError" in block
    assert "response.status_code = 200" in block
    assert "response.status_code = 201" in block


def test_rueckwaertssuche_unterscheidet_fuehrend_und_beteiligt() -> None:
    """"Hiermit eroeffnet" und "gehoert auch dazu" sind verschiedene Aussagen."""
    source = ENDPOINTS.read_text(encoding="utf-8")
    block = source[source.index("def find_instances_for_document") :]

    assert '"role": "leading"' in block
    assert '"role": "participant"' in block
    # Ein Vorgang, der den Beleg fuehrend traegt, darf nicht zusaetzlich als
    # Beteiligter erscheinen.
    assert "if inst.id in seen:" in block


def test_rueckwaertssuche_ist_prozessuebergreifend() -> None:
    """Die Sammelrechnung muss auffindbar sein, ohne den Prozess vorher zu kennen."""
    source = ENDPOINTS.read_text(encoding="utf-8")
    assert '"/documents/{document_type}/{document_id}/instances"' in source
    block = source[source.index("def find_instances_for_document") :]
    assert "process_key" not in block.split("def find_instances_for_document")[0]
