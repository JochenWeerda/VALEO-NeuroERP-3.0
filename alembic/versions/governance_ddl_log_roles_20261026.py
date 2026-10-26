"""Prepare governance.ddl_events for separated database roles.

With scripts/provision_db_roles.py only valeo_owner/valeo_migrator may INSERT into the log.
Application and agent roles cannot run DDL, but their temporary tables still fire the event
triggers; the functions now return before touching the log when no persistent object is
involved, so those sessions neither need log privileges nor raise warnings. The log stays
closed to PUBLIC.
"""
from alembic import op

revision = "governance_ddl_log_roles_20261026"
down_revision = "governance_ddl_log_20261026"
branch_labels = None
depends_on = None

_SOURCE = """
    CASE
        WHEN current_setting('application_name') ILIKE 'alembic%' THEN 'alembic'
        WHEN current_setting('application_name') ILIKE 'drizzle-kit%' THEN 'drizzle-kit'
        WHEN current_setting('application_name') ILIKE 'orm-create-all%' THEN 'orm-create-all'
        WHEN current_setting('application_name') ILIKE 'agent:%' THEN 'agent'
        ELSE 'unbekannt'
    END
"""
_DDL_FILTER = "c.schema_name IS NULL OR c.schema_name NOT LIKE 'pg\\_temp%'"
_DROP_FILTER = "NOT d.is_temporary AND d.original"


def _functions(early_return: bool) -> None:
    guard_ddl = (
        f"IF NOT EXISTS (SELECT 1 FROM pg_event_trigger_ddl_commands() c WHERE {_DDL_FILTER}) THEN RETURN; END IF;"
        if early_return else ""
    )
    guard_drop = (
        f"IF NOT EXISTS (SELECT 1 FROM pg_event_trigger_dropped_objects() d WHERE {_DROP_FILTER}) THEN RETURN; END IF;"
        if early_return else ""
    )
    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION governance.log_ddl_command_end() RETURNS event_trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            {guard_ddl}
            INSERT INTO governance.ddl_events (event, command_tag, object_type, schema_name, object_identity,
                session_role, current_role_name, application_name, source, transaction_id, client_addr)
            SELECT 'ddl_command_end', c.command_tag, c.object_type, c.schema_name, c.object_identity,
                   session_user, current_user, current_setting('application_name'), {_SOURCE},
                   txid_current(), inet_client_addr()
              FROM pg_event_trigger_ddl_commands() c
             WHERE {_DDL_FILTER};
        EXCEPTION WHEN OTHERS THEN
            RAISE WARNING 'governance.ddl_events not written: %', SQLERRM;
        END;
        $$
        """
    )
    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION governance.log_sql_drop() RETURNS event_trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            {guard_drop}
            INSERT INTO governance.ddl_events (event, command_tag, object_type, schema_name, object_identity,
                session_role, current_role_name, application_name, source, transaction_id, client_addr)
            SELECT 'sql_drop', tg_tag, d.object_type, d.schema_name, d.object_identity,
                   session_user, current_user, current_setting('application_name'), {_SOURCE},
                   txid_current(), inet_client_addr()
              FROM pg_event_trigger_dropped_objects() d
             WHERE {_DROP_FILTER};
        EXCEPTION WHEN OTHERS THEN
            RAISE WARNING 'governance.ddl_events not written: %', SQLERRM;
        END;
        $$
        """
    )


def upgrade() -> None:
    _functions(early_return=True)
    op.execute("REVOKE ALL ON SCHEMA governance FROM PUBLIC")
    op.execute("REVOKE ALL ON ALL TABLES IN SCHEMA governance FROM PUBLIC")
    op.execute("REVOKE ALL ON ALL SEQUENCES IN SCHEMA governance FROM PUBLIC")


def downgrade() -> None:
    _functions(early_return=False)
