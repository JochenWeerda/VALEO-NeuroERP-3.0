"""Spiegelbetrieb L3: Quellreferenz je uebernommenem Datensatz und Uebernahmeprotokoll (M6, 25.11.2026).

Revision ID: spiegel_quellreferenz_20261125
Revises: folgeartikel_fremdschluessel_20261124

Die vorhandene Adapterstrecke (``domain_integration.legacy_adapter_*``: Annahme, Staging, Mengenabgleich, Freigabe)
endete vor den Fachtabellen. Die Uebernahme braucht:

- ``spiegel_quellreferenzen``: welcher L3-Datensatz (Quellsystem, Objektart, Quellschluessel) welches VALEO-Objekt
  erzeugt hat, mit Pruefsumme des zuletzt uebernommenen Inhalts. Wiederholte Laeufe erkennen daran "unveraendert";
  ein Zielobjekt hat hoechstens eine Quelle.
- ``spiegel_protokoll``: Ergebnis je Quellzeile und Lauf (neu, geaendert, unveraendert, fehler) mit den
  Felddifferenzen - Grundlage des Differenzberichts. Nur anfuegen; Korrekturen sind neue Laeufe.
"""
from __future__ import annotations

from alembic import op

revision = "spiegel_quellreferenz_20261125"
down_revision = "folgeartikel_fremdschluessel_20261124"
branch_labels = None
depends_on = None

REFERENZ = "domain_integration.spiegel_quellreferenzen"
PROTOKOLL = "domain_integration.spiegel_protokoll"
OWN = "(tenant_id)::text = public.rls_current_tenant()"


def _rls(tabelle: str) -> None:
    op.execute(f"ALTER TABLE {tabelle} ENABLE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {tabelle} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {tabelle} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {tabelle} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {tabelle} FOR DELETE USING ({OWN})")


def upgrade() -> None:
    op.execute(f"""
        CREATE TABLE {REFERENZ} (
            tenant_id text NOT NULL REFERENCES domain_shared.tenants (id),
            quellsystem text NOT NULL,
            objektart text NOT NULL,
            quellschluessel text NOT NULL,
            ziel_tabelle text NOT NULL,
            ziel_id text NOT NULL,
            payload_hash text NOT NULL,
            batch_id text NOT NULL REFERENCES domain_integration.legacy_adapter_batches (id),
            version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
            erstmals_am timestamptz NOT NULL DEFAULT now(),
            zuletzt_am timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT pk_spiegel_quellreferenzen PRIMARY KEY (tenant_id, quellsystem, objektart, quellschluessel),
            CONSTRAINT uq_spiegel_quellreferenz_ziel UNIQUE (tenant_id, ziel_tabelle, ziel_id)
        )
    """)
    _rls(REFERENZ)
    op.execute(f"""
        CREATE TABLE {PROTOKOLL} (
            id text PRIMARY KEY,
            tenant_id text NOT NULL REFERENCES domain_shared.tenants (id),
            batch_id text NOT NULL REFERENCES domain_integration.legacy_adapter_batches (id),
            line_no integer NOT NULL,
            objektart text NOT NULL,
            quellschluessel text,
            ergebnis text NOT NULL CHECK (ergebnis IN ('neu', 'geaendert', 'unveraendert', 'fehler')),
            differenzen jsonb NOT NULL DEFAULT '{{}}'::jsonb,
            fehler text,
            erstellt_am timestamptz NOT NULL DEFAULT now()
        )
    """)
    op.execute(f"CREATE INDEX ix_spiegel_protokoll_lauf ON {PROTOKOLL} (tenant_id, batch_id, ergebnis)")
    _rls(PROTOKOLL)
    # Protokollzeilen sind unveraenderlich (Korrektur = neuer Lauf). Loeschen bleibt fuer die Mandantenaufloesung moeglich.
    op.execute("""
        CREATE OR REPLACE FUNCTION domain_integration.spiegel_protokoll_unveraenderlich() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'Spiegelprotokoll ist unveraenderlich (Zeile %)', OLD.id USING ERRCODE = 'check_violation';
        END;
        $$
    """)
    op.execute(f"CREATE TRIGGER trg_spiegel_protokoll_unveraenderlich BEFORE UPDATE ON {PROTOKOLL} "
               "FOR EACH ROW EXECUTE FUNCTION domain_integration.spiegel_protokoll_unveraenderlich()")


def downgrade() -> None:
    op.execute(f"DROP TABLE IF EXISTS {PROTOKOLL}")
    op.execute("DROP FUNCTION IF EXISTS domain_integration.spiegel_protokoll_unveraenderlich()")
    op.execute(f"DROP TABLE IF EXISTS {REFERENZ}")
