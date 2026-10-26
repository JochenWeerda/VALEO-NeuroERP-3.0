"""Carry the tenant context into every database transaction (RLS plan P2).

Before a statement runs, the engine compares the tenant of the current context with what it
last set on this connection and, only if they differ, sets the transaction-local setting
``app.tenant_id`` (``set_config(..., true)``). Row-level security policies compare
``tenant_id`` with that setting. Without context the setting is empty and a policy sees no
tenant rows: fail-closed.

Comparing per statement instead of per transaction matters: a worker may read the tenant
registry and then switch ``tenant_scope`` inside one transaction. The cache lives in the
connection record and is dropped at commit, rollback, rollback to savepoint and pool checkout,
because the transaction-local value is gone then.
"""

from __future__ import annotations

import logging

from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.tenant_context import cross_tenant_reason, current_tenant_or_none

logger = logging.getLogger(__name__)

SETTING = "app.tenant_id"
_APPLIED = "rls_tenant_applied"
_SQL = {
    "pyformat": ("SELECT set_config(%(name)s, %(value)s, true)", lambda v: {"name": SETTING, "value": v}),
    "format": ("SELECT set_config(%s, %s, true)", lambda v: (SETTING, v)),
}


# Transaction control issued by SQLAlchemy itself. Setting the tenant right before SAVEPOINT or
# ROLLBACK TO SAVEPOINT would place it inside the subtransaction that is then undone.
_TX_CONTROL = ("SAVEPOINT", "RELEASE", "ROLLBACK", "COMMIT", "BEGIN")


def _is_tx_control(statement: str) -> bool:
    return statement.lstrip()[:9].upper().startswith(_TX_CONTROL)


def desired_tenant() -> str:
    return current_tenant_or_none() or ""


def _apply(conn, cursor, statement, parameters, context, executemany):
    if _is_tx_control(statement):
        return
    desired = desired_tenant()
    if conn.info.get(_APPLIED) == desired:
        return
    sql, params = _SQL[conn.dialect.paramstyle]
    cursor.execute(sql, params(desired))
    conn.info[_APPLIED] = desired
    if not desired:
        from app.core.metrics import db_transactions_without_tenant_total

        scope = "cross_tenant" if cross_tenant_reason() else "none"
        db_transactions_without_tenant_total.labels(scope=scope).inc()
        logger.debug("db transaction without tenant (scope=%s)", scope)


def _forget_on_connection(conn, *args):
    conn.info.pop(_APPLIED, None)


def _forget_after_savepoint_rollback(conn, cursor, statement, parameters, context, executemany):
    # The rollback_savepoint event fires before the statement; forget again once it has run.
    if statement.lstrip()[:21].upper().startswith("ROLLBACK TO SAVEPOINT"):
        conn.info.pop(_APPLIED, None)


def _forget_on_checkout(dbapi_connection, connection_record, connection_proxy):
    connection_record.info.pop(_APPLIED, None)


def install_tenant_setting(engine: Engine) -> Engine:
    if engine.dialect.paramstyle not in _SQL:
        raise RuntimeError(f"Unsupported paramstyle {engine.dialect.paramstyle!r} for RLS tenant setting")
    if event.contains(engine, "before_cursor_execute", _apply):
        return engine
    event.listen(engine, "before_cursor_execute", _apply)
    event.listen(engine, "after_cursor_execute", _forget_after_savepoint_rollback)
    for name in ("commit", "rollback", "rollback_savepoint"):
        event.listen(engine, name, _forget_on_connection)
    event.listen(engine, "checkout", _forget_on_checkout)
    return engine
