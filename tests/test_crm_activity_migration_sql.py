"""Rollback-only PostgreSQL checks for legacy CRM activity migration."""
import hashlib
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.engine import make_url

from app.core.database import engine
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


@pytest.fixture
def data(request):
    raw = os.environ.get("TEST_DATABASE_URL")
    assert raw and make_url(raw) == engine.url and engine.url.database not in {"valeo_neuro_erp", "postgres"}, "Explicit shared test database required"
    result = request.getfixturevalue("subject_data")
    connection = result[1].connection()
    connection.info["activity_test_heads"] = tuple(connection.execute(sa.text("SELECT version_num FROM alembic_version ORDER BY version_num")).scalars())
    _legacy_shape(connection)
    return result


def _legacy_shape(connection):
    """Exercise upgrade from its predecessor inside the fixture's rollback-only transaction.

    CI has already migrated to head; the shared probe may still be at the predecessor.
    Never stamp/reset a database or persist these narrowly scoped test DDL changes.
    """
    columns = {column["name"] for column in sa.inspect(connection).get_columns("activities", schema="domain_crm")}
    if "origin" not in columns:
        return
    for name in ("ck_activity_version_positive", "ck_activity_status", "ck_activity_type"):
        connection.execute(sa.text('ALTER TABLE domain_crm.activities DROP CONSTRAINT IF EXISTS "' + name + '"'))
    connection.execute(sa.text("DROP INDEX IF EXISTS domain_crm.ix_activities_tenant_date_id"))
    for name in ("customer_id", "contact_id", "version", "main_topics", "orders_placed", "follow_up_actions", "origin", "created_by", "updated_by"):
        connection.execute(sa.text('ALTER TABLE domain_crm.activities DROP COLUMN "' + name + '"'))
    connection.execute(sa.text("ALTER TABLE domain_crm.activities ALTER COLUMN tenant_id DROP NOT NULL"))


def migrate(connection):
    path = Path(__file__).resolve().parents[1] / "alembic/versions/crm_activity_canonical_20261029.py"
    spec = importlib.util.spec_from_file_location("crm_activity_migration_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with Operations.context(MigrationContext.configure(connection)):
        module.upgrade()


def table(connection, schema, name):
    return sa.Table(name, sa.MetaData(), schema=schema, autoload_with=connection)


def enum_value(column, expected):
    values = getattr(column.type, "enums", ())
    return next((v for v in values if v.casefold() == expected), expected)


def test_import_preserves_values_provenance_and_unverified_creator(data):
    _, db, _, tenant, *_ = data
    connection = db.connection()
    source = table(connection, "public", "crm_activities")
    contacts = table(connection, "public", "crm_contacts")
    record_id, contact_id = str(uuid4()), str(uuid4())
    date = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)
    savepoint = connection.begin_nested()
    try:
        connection.execute(contacts.insert().values(id=contact_id, tenant_id=tenant, name="Synthetic Person", company="Synthetic Company", email=contact_id + "@example.invalid", type=enum_value(contacts.c.type, "customer")))
        connection.execute(source.insert().values(id=record_id, tenant_id=tenant, contact_id=contact_id, type=enum_value(source.c.type, "call"), status=enum_value(source.c.status, "planned"), subject="Synthetic legacy call", date=date, notes="Legacy note", created_by="unverified legacy actor"))
        raw = dict(connection.execute(sa.select(source).where(source.c.id == record_id)).mappings().one())
        migrate(connection)
        target = table(connection, "domain_crm", "activities")
        row = connection.execute(sa.select(target).where(target.c.id == record_id)).mappings().one()
        assert (row["id"], row["tenant_id"], row["date"], row["contact_id"]) == (record_id, tenant, date, contact_id)
        assert (row["type"], row["status"], row["contact_person"], row["customer"]) == ("call", "planned", "Synthetic Person", "Synthetic Company")
        assert row["created_by"] is None and row["assigned_to"] == ""
        assert row["origin"]["source"] == "public.crm_activities"
        assert row["origin"]["record"] == json.loads(json.dumps(raw, default=str))
        assert row["origin"]["sha256"] == hashlib.sha256(json.dumps(raw, sort_keys=True, default=str).encode()).hexdigest()
        assert connection.execute(sa.select(source.c.id).where(source.c.id == record_id)).scalar_one() == record_id
    finally:
        savepoint.rollback()
    assert "origin" not in {c["name"] for c in sa.inspect(connection).get_columns("activities", schema="domain_crm")}
    assert connection.execute(sa.select(source.c.id).where(source.c.id == record_id)).first() is None
    assert tuple(connection.execute(sa.text("SELECT version_num FROM alembic_version ORDER BY version_num")).scalars()) == connection.info["activity_test_heads"]


@pytest.mark.parametrize("failure", ["unknown_status", "id_collision"])
def test_invalid_legacy_data_aborts_without_overwriting(data, failure):
    _, db, _, tenant, *_ = data
    connection = db.connection()
    source = table(connection, "public", "crm_activities")
    target = table(connection, "domain_crm", "activities")
    record_id = str(uuid4())
    savepoint = connection.begin_nested()
    try:
        connection.execute(target.insert().values(id=record_id, tenant_id=tenant, type="call", title="Existing synthetic", customer="", contact_person="", date=datetime.now(timezone.utc), status="unknown-status" if failure == "unknown_status" else "planned", assigned_to=""))
        if failure == "id_collision":
            connection.execute(source.insert().values(id=record_id, tenant_id=tenant, type=enum_value(source.c.type, "call"), status=enum_value(source.c.status, "planned"), subject="Conflicting synthetic", date=datetime.now(timezone.utc)))
        with pytest.raises(RuntimeError, match="Unknown legacy CRM activity classification" if failure == "unknown_status" else "ID collision"):
            migrate(connection)
        assert connection.execute(sa.select(target.c.title).where(target.c.id == record_id)).scalar_one() == "Existing synthetic"
    finally:
        savepoint.rollback()
    assert "origin" not in {c["name"] for c in sa.inspect(connection).get_columns("activities", schema="domain_crm")}
    assert connection.execute(sa.select(target.c.id).where(target.c.id == record_id)).first() is None
    assert connection.execute(sa.select(source.c.id).where(source.c.id == record_id)).first() is None
    assert tuple(connection.execute(sa.text("SELECT version_num FROM alembic_version ORDER BY version_num")).scalars()) == connection.info["activity_test_heads"]


def test_effective_screen_actions_require_idempotency_and_block_agents():
    from app.core.screen_definitions import build_crm_customer_360_screen_definition, build_crm_opportunity_screen_definition
    for builder, expected_fields in ((build_crm_customer_360_screen_definition, {"betreff", "typ"}), (build_crm_opportunity_screen_definition, {"subject", "activity_type"})):
        action = next(a for a in builder()["actions"] if a["key"] == "create_activity")
        assert action["requiresIdempotencyKey"] is True
        assert action["forbiddenForAgents"] is True
        assert expected_fields <= {field["key"] for field in action["inputFields"]}


def test_erasure_deletes_only_matching_tenant_activities(data, monkeypatch):
    from app.api.v1.endpoints import compliance_dsgvo
    _, db, _, tenant, foreign, *_ = data
    connection = db.connection()
    target = table(connection, "domain_crm", "activities")
    ids = [str(uuid4()) for _ in range(3)]
    name = "Synthetic erasure " + str(uuid4())
    savepoint = connection.begin_nested()
    try:
        for record_id, tid in zip(ids, (tenant, foreign, None)):
            connection.execute(target.insert().values(id=record_id, tenant_id=tid, type="call", title="Synthetic", customer=name, contact_person="", date=datetime.now(timezone.utc), status="planned", assigned_to=""))
        monkeypatch.setattr(compliance_dsgvo, "_namen_des_betroffenen", lambda *args: [name])
        log = compliance_dsgvo._anonymize_subject(db, "CUSTOMER", str(uuid4()), tenant)
        entry = next(item for item in log if item["table"] == "domain_crm.activities")
        assert entry["rows_affected"] == 1 and "error" not in entry
        remaining = set(connection.execute(sa.select(target.c.id).where(target.c.id.in_(ids))).scalars())
        assert remaining == set(ids[1:])
    finally:
        savepoint.rollback()


def test_upgrade_rehearsal_also_works_when_ci_started_on_current_head(data):
    connection = data[1].connection()
    savepoint = connection.begin_nested()
    try:
        migrate(connection)
        assert "origin" in {column["name"] for column in sa.inspect(connection).get_columns("activities", schema="domain_crm")}
        _legacy_shape(connection)
        assert "origin" not in {column["name"] for column in sa.inspect(connection).get_columns("activities", schema="domain_crm")}
        migrate(connection)
        assert "origin" in {column["name"] for column in sa.inspect(connection).get_columns("activities", schema="domain_crm")}
    finally:
        savepoint.rollback()
    assert tuple(connection.execute(sa.text("SELECT version_num FROM alembic_version ORDER BY version_num")).scalars()) == connection.info["activity_test_heads"]
