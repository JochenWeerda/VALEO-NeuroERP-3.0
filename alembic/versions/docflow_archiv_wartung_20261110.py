"""Archivierte Belegoriginale: Loeschen nur mit dem DocFlow-Wartungsschalter (BELEG-052 Phase 2).

Revision ID: docflow_archiv_wartung_20261110
Revises: docflow_position_kontrakt_20261110

Seit gebuchte Ausgangsrechnungen ihr Original ins Archiv schreiben, hat jede gebuchte Rechnung einen geschuetzten
Archiveintrag. ``guard_archived_content`` verbot das Loeschen ausnahmslos - auch beim Entfernen eines Mandanten
(DSGVO/Testpruefstand), wo Statushistorie, Kommandoprotokoll und Freigaben den Wartungsschalter
``valeo.docflow_wartung = 'loeschen'`` kennen. Gleiche Regel hier; Aendern bleibt ausnahmslos verboten.
"""
from __future__ import annotations

from alembic import op

revision = "docflow_archiv_wartung_20261110"
down_revision = "docflow_position_kontrakt_20261110"
branch_labels = None
depends_on = None

_KOERPER = """
        BEGIN
            IF OLD.content_bytes IS NOT NULL THEN
                IF TG_OP = 'DELETE' THEN
                    IF current_setting('valeo.docflow_wartung', true) = 'loeschen' THEN
                        RETURN OLD;
                    END IF;
                    RAISE EXCEPTION 'Archived content cannot be deleted';
                END IF;
                IF ROW(NEW.content_bytes, NEW.content_hash_sha256, NEW.tenant_id, NEW.header_id, NEW.storage_key)
                   IS DISTINCT FROM ROW(OLD.content_bytes, OLD.content_hash_sha256, OLD.tenant_id, OLD.header_id, OLD.storage_key) THEN
                    RAISE EXCEPTION 'Archived content and identity cannot be changed';
                END IF;
            END IF;
            IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
            RETURN NEW;
        END;
"""

_ALT = _KOERPER.replace("""                    IF current_setting('valeo.docflow_wartung', true) = 'loeschen' THEN
                        RETURN OLD;
                    END IF;
""", "")


def _setze(koerper: str) -> None:
    op.execute("CREATE OR REPLACE FUNCTION domain_docflow.guard_archived_content() RETURNS trigger "
               f"LANGUAGE plpgsql AS $${koerper}$$")


def upgrade() -> None:
    _setze(_KOERPER)


def downgrade() -> None:
    _setze(_ALT)
