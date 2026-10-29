"""Record every schema change (DDL) independent of the tool that issues it.

Event triggers on ddl_command_end and sql_drop write one row per changed object to
governance.ddl_events: command, object, session/current role, application_name and the
source derived from it (alembic, drizzle-kit, orm-create-all, agent, unbekannt). The statement text is not
stored, it may carry secrets. Temporary objects are skipped.

application_name is declared by the client; the role columns are what the server knows.
Event triggers need a superuser login role; without it the log table and functions are created,
the triggers are not, and scripts/check_ddl_provenance.py reports the missing triggers.
"""
from alembic import op
import sqlalchemy as sa

revision = "governance_ddl_log_20261026"
down_revision = "loading_stop_fk_20261023"
branch_labels = None
depends_on = None

_TRIGGERS = ("governance_ddl_command_end", "governance_sql_drop")

_SOURCE = """
    CASE
        WHEN current_setting('application_name') ILIKE 'alembic%' THEN 'alembic'
        WHEN current_setting('application_name') ILIKE 'drizzle-kit%' THEN 'drizzle-kit'
        WHEN current_setting('application_name') ILIKE 'orm-create-all%' THEN 'orm-create-all'
        WHEN current_setting('application_name') ILIKE 'agent:%' THEN 'agent'
        ELSE 'unbekannt'
    END
"""


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS governance")
    op.execute(
        """
        CREATE TABLE governance.ddl_events (
            id bigserial PRIMARY KEY,
            occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            event text NOT NULL,
            command_tag text NOT NULL,
            object_type text,
            schema_name text,
            object_identity text,
            session_role text NOT NULL,
            current_role_name text NOT NULL,
            application_name text NOT NULL,
            source text NOT NULL,
            transaction_id bigint NOT NULL,
            client_addr inet
        )
        """
    )
    op.execute("CREATE INDEX ix_governance_ddl_events_occurred_at ON governance.ddl_events (occurred_at)")
    op.execute("CREATE INDEX ix_governance_ddl_events_source ON governance.ddl_events (source)")
    op.execute("COMMENT ON TABLE governance.ddl_events IS 'Schema changes from any tool; see governance_ddl_log_20261026'")
    # A failing log write must not block the schema change itself (fail open): the trigger
    # raises a WARNING instead, and check_ddl_provenance.py compares the log with the catalog.
    op.execute(
        f"""
        CREATE FUNCTION governance.log_ddl_command_end() RETURNS event_trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO governance.ddl_events (event, command_tag, object_type, schema_name, object_identity,
                session_role, current_role_name, application_name, source, transaction_id, client_addr)
            SELECT 'ddl_command_end', c.command_tag, c.object_type, c.schema_name, c.object_identity,
                   session_user, current_user, current_setting('application_name'), {_SOURCE},
                   txid_current(), inet_client_addr()
              FROM pg_event_trigger_ddl_commands() c
             WHERE c.schema_name IS NULL OR c.schema_name NOT LIKE 'pg\\_temp%';
        EXCEPTION WHEN OTHERS THEN
            RAISE WARNING 'governance.ddl_events not written: %', SQLERRM;
        END;
        $$
        """
    )
    op.execute(
        f"""
        CREATE FUNCTION governance.log_sql_drop() RETURNS event_trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO governance.ddl_events (event, command_tag, object_type, schema_name, object_identity,
                session_role, current_role_name, application_name, source, transaction_id, client_addr)
            SELECT 'sql_drop', tg_tag, d.object_type, d.schema_name, d.object_identity,
                   session_user, current_user, current_setting('application_name'), {_SOURCE},
                   txid_current(), inet_client_addr()
              FROM pg_event_trigger_dropped_objects() d
             WHERE NOT d.is_temporary AND d.original;
        EXCEPTION WHEN OTHERS THEN
            RAISE WARNING 'governance.ddl_events not written: %', SQLERRM;
        END;
        $$
        """
    )
    conn = op.get_bind()
    # The login role decides: migrations may run under SET ROLE valeo_owner (app.core.migration_session).
    is_superuser = conn.execute(sa.text("SELECT rolsuper FROM pg_roles WHERE rolname = session_user")).scalar()
    if not is_superuser:
        op.execute("DO $$ BEGIN RAISE WARNING 'governance: event triggers need superuser rights and were not created'; END $$")
        return
    acting_role = conn.execute(sa.text("SELECT current_user")).scalar()
    op.execute("RESET ROLE")
    op.execute(
        "CREATE EVENT TRIGGER governance_ddl_command_end ON ddl_command_end "
        "EXECUTE FUNCTION governance.log_ddl_command_end()"
    )
    op.execute(
        "CREATE EVENT TRIGGER governance_sql_drop ON sql_drop "
        "EXECUTE FUNCTION governance.log_sql_drop()"
    )
    if acting_role != conn.execute(sa.text("SELECT session_user")).scalar():
        op.execute(sa.text(f"SET ROLE {acting_role}"))


def downgrade() -> None:
    for trigger in _TRIGGERS:
        op.execute(f"DROP EVENT TRIGGER IF EXISTS {trigger}")
    op.execute("DROP SCHEMA IF EXISTS governance CASCADE")
