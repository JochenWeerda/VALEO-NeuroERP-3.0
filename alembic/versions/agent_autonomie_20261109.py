"""Risikobasierte Agentenautonomie: Politikfreigabe, Delegation, Qualitaetsmodell, Autonomieentscheidung (ADR-086).

Revision ID: agent_autonomie_20261109
Revises: psm_register_entfernt_20261104

Vier Tabellen, alle je Mandant unter getrennten Policies je Befehl:

* ``agent_policy_approvals``: Die fachliche Freigabe einer Version der Autonomiepolitik (Inhaltsabdruck). Ohne sie
  gilt keine Autonomie; eine geaenderte Politik hat einen anderen Abdruck und ist nicht freigegeben.
* ``agent_delegations``: Ein Mensch delegiert einem Agenten eine Faehigkeit (z. B. ``sales.gutschrift.buchen``),
  begrenzt und widerrufbar. Widerruf setzt ``revoked_*``; geloescht wird nicht.
* ``agent_quality_events``: Messpunkte je Agent und Faehigkeit (ausgefuehrt, korrigiert, Befund, Testnachweis,
  Einwand eines Pruefagenten). Unveraenderlich.
* ``agent_autonomy_decisions``: Jede Autonomieentscheidung mit Politikversion, Abdruck und Gruenden. Unveraenderlich.
"""
from __future__ import annotations

from alembic import op

revision = "agent_autonomie_20261109"
down_revision = "psm_register_entfernt_20261104"
branch_labels = None
depends_on = None

OWN = "tenant_id = public.rls_current_tenant()"
TABELLEN = ("domain_shared.agent_policy_approvals", "domain_shared.agent_delegations",
            "domain_shared.agent_quality_events", "domain_shared.agent_autonomy_decisions")
UNVERAENDERLICH = ("domain_shared.agent_quality_events", "domain_shared.agent_autonomy_decisions")
MANDANT = ("tenant_id VARCHAR(120) NOT NULL DEFAULT public.rls_current_tenant() "
           "CHECK (tenant_id NOT IN ('', 'default', 'system'))")


def _policies(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def upgrade() -> None:
    op.execute(f"""
        CREATE TABLE domain_shared.agent_policy_approvals (
            id            VARCHAR(36)  PRIMARY KEY,
            {MANDANT},
            policy_id     VARCHAR(80)  NOT NULL,
            version       VARCHAR(20)  NOT NULL,
            content_hash  VARCHAR(64)  NOT NULL,
            approved_by   VARCHAR(100) NOT NULL,
            approved_at   TIMESTAMPTZ  NOT NULL DEFAULT clock_timestamp(),
            note          TEXT         NOT NULL CHECK (length(trim(note)) >= 10),
            revoked_at    TIMESTAMPTZ,
            revoked_by    VARCHAR(100),
            revoke_reason TEXT,
            CONSTRAINT ck_agent_policy_widerruf CHECK ((revoked_at IS NULL) = (revoked_by IS NULL))
        )""")
    op.execute("CREATE UNIQUE INDEX uq_agent_policy_aktiv ON domain_shared.agent_policy_approvals "
               "(tenant_id, policy_id, content_hash) WHERE revoked_at IS NULL")
    op.execute(f"""
        CREATE TABLE domain_shared.agent_delegations (
            id            VARCHAR(36)  PRIMARY KEY,
            {MANDANT},
            agent_id      VARCHAR(100) NOT NULL,
            capability    VARCHAR(120) NOT NULL,
            owner         VARCHAR(100) NOT NULL,
            max_brutto    NUMERIC(14, 2) CHECK (max_brutto IS NULL OR max_brutto > 0),
            valid_until   TIMESTAMPTZ,
            created_at    TIMESTAMPTZ  NOT NULL DEFAULT clock_timestamp(),
            revoked_at    TIMESTAMPTZ,
            revoked_by    VARCHAR(100),
            revoke_reason TEXT,
            CONSTRAINT ck_agent_delegation_selbst CHECK (owner <> agent_id),
            CONSTRAINT ck_agent_delegation_widerruf CHECK ((revoked_at IS NULL) = (revoked_by IS NULL))
        )""")
    op.execute("CREATE UNIQUE INDEX uq_agent_delegation_aktiv ON domain_shared.agent_delegations "
               "(tenant_id, agent_id, capability) WHERE revoked_at IS NULL")
    op.execute(f"""
        CREATE TABLE domain_shared.agent_quality_events (
            id           VARCHAR(36)  PRIMARY KEY,
            {MANDANT},
            agent_id     VARCHAR(100) NOT NULL,
            capability   VARCHAR(120) NOT NULL,
            kind         VARCHAR(30)  NOT NULL CHECK (kind IN ('ausgefuehrt', 'korrigiert', 'befund', 'test_bestanden',
                                                               'test_fehlgeschlagen', 'einwand', 'abgelehnt')),
            subject_id   VARCHAR(64),
            detail       JSONB        NOT NULL DEFAULT '{{}}'::jsonb,
            recorded_by  VARCHAR(100) NOT NULL,
            recorded_at  TIMESTAMPTZ  NOT NULL DEFAULT clock_timestamp()
        )""")
    op.execute("CREATE INDEX ix_agent_quality_agent ON domain_shared.agent_quality_events "
               "(tenant_id, agent_id, capability, recorded_at)")
    op.execute(f"""
        CREATE TABLE domain_shared.agent_autonomy_decisions (
            id             VARCHAR(36)  PRIMARY KEY,
            {MANDANT},
            agent_id       VARCHAR(100) NOT NULL,
            capability     VARCHAR(120) NOT NULL,
            subject_id     VARCHAR(64),
            policy_version VARCHAR(20),
            policy_hash    VARCHAR(64),
            outcome        VARCHAR(20)  NOT NULL CHECK (outcome IN ('autonom', 'freigabe', 'abgelehnt')),
            risk           VARCHAR(4),
            reasons        JSONB        NOT NULL DEFAULT '[]'::jsonb,
            decided_at     TIMESTAMPTZ  NOT NULL DEFAULT clock_timestamp()
        )""")
    op.execute("CREATE INDEX ix_agent_autonomy_subject ON domain_shared.agent_autonomy_decisions "
               "(tenant_id, capability, subject_id, decided_at)")
    for table in TABELLEN:
        _policies(table)
    op.execute("""
        CREATE FUNCTION domain_shared.agent_protokoll_unveraenderlich() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' AND current_setting('valeo.docflow_wartung', true) = 'loeschen' THEN
                RETURN OLD;
            END IF;
            RAISE EXCEPTION 'Das Protokoll der Agentenautonomie wird nicht geaendert oder geloescht.'
                USING ERRCODE = 'restrict_violation';
        END $$""")
    for table in UNVERAENDERLICH:
        name = table.split(".")[1]
        op.execute(f"CREATE TRIGGER {name}_unveraenderlich BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION domain_shared.agent_protokoll_unveraenderlich()")


def downgrade() -> None:
    for table in reversed(TABELLEN):
        op.execute(f"DROP TABLE IF EXISTS {table}")
    op.execute("DROP FUNCTION IF EXISTS domain_shared.agent_protokoll_unveraenderlich()")
