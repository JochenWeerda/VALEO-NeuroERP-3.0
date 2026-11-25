"""Spiegelbetrieb L3: Quellreferenz je uebernommenem Datensatz und Uebernahmeprotokoll (M6, 25.11.2026).

Revision ID: spiegel_quellreferenz_20261125
Revises: ops_fahrer_tenant_20261124

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
down_revision = "ops_fahrer_tenant_20261124"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE domain_integration.spiegel_quellreferenzen (
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
    op.execute("ALTER TABLE domain_integration.spiegel_quellreferenzen ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY tenant_isolation_select ON domain_integration.spiegel_quellreferenzen FOR SELECT USING ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_insert ON domain_integration.spiegel_quellreferenzen FOR INSERT WITH CHECK ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_update ON domain_integration.spiegel_quellreferenzen FOR UPDATE USING ((tenant_id)::text = public.rls_current_tenant()) WITH CHECK ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_delete ON domain_integration.spiegel_quellreferenzen FOR DELETE USING ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("""
        CREATE TABLE domain_integration.spiegel_protokoll (
            id text PRIMARY KEY,
            tenant_id text NOT NULL REFERENCES domain_shared.tenants (id),
            batch_id text NOT NULL REFERENCES domain_integration.legacy_adapter_batches (id),
            line_no integer NOT NULL,
            objektart text NOT NULL,
            quellschluessel text,
            ergebnis text NOT NULL CHECK (ergebnis IN ('neu', 'geaendert', 'unveraendert', 'fehler')),
            differenzen jsonb NOT NULL DEFAULT '{}'::jsonb,
            fehler text,
            erstellt_am timestamptz NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX ix_spiegel_protokoll_lauf ON domain_integration.spiegel_protokoll (tenant_id, batch_id, ergebnis)")
    op.execute("ALTER TABLE domain_integration.spiegel_protokoll ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY tenant_isolation_select ON domain_integration.spiegel_protokoll FOR SELECT USING ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_insert ON domain_integration.spiegel_protokoll FOR INSERT WITH CHECK ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_update ON domain_integration.spiegel_protokoll FOR UPDATE USING ((tenant_id)::text = public.rls_current_tenant()) WITH CHECK ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_delete ON domain_integration.spiegel_protokoll FOR DELETE USING ((tenant_id)::text = public.rls_current_tenant())")
    # Protokollzeilen sind unveraenderlich (Korrektur = neuer Lauf). Loeschen bleibt fuer die Mandantenaufloesung moeglich.
    op.execute("""
        CREATE OR REPLACE FUNCTION domain_integration.spiegel_protokoll_unveraenderlich() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'Spiegelprotokoll ist unveraenderlich (Zeile %)', OLD.id USING ERRCODE = 'check_violation';
        END;
        $$
    """)
    op.execute("CREATE TRIGGER trg_spiegel_protokoll_unveraenderlich BEFORE UPDATE ON domain_integration.spiegel_protokoll "
               "FOR EACH ROW EXECUTE FUNCTION domain_integration.spiegel_protokoll_unveraenderlich()")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_integration.spiegel_protokoll")
    op.execute("DROP FUNCTION IF EXISTS domain_integration.spiegel_protokoll_unveraenderlich()")
    op.execute("DROP TABLE IF EXISTS domain_integration.spiegel_quellreferenzen")
