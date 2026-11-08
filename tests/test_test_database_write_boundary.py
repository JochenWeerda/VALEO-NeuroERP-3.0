"""Test fixture authorization before any connection or tenant seed."""
import pytest
import conftest

TEST = 'postgresql://fixture:fixture@127.0.0.1:5432/valeo_probe'
DEV = 'postgresql://fixture:fixture@127.0.0.1:5432/valeo_neuro_erp'

@pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.delenv('TEST_DATABASE_URL', raising=False)
    monkeypatch.delenv('DATABASE_URL', raising=False)
    monkeypatch.delenv('CI', raising=False)
    monkeypatch.setenv('DEVELOPMENT_DATABASE_URL', DEV)


def test_missing_test_declaration_denies_local_database(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', DEV)
    assert not conftest._test_database_authorized(DEV)


def test_existing_explicit_probe_is_allowed(monkeypatch):
    monkeypatch.setenv('TEST_DATABASE_URL', TEST)
    assert conftest._test_database_authorized(TEST)


def test_effective_database_mismatch_is_rejected(monkeypatch):
    monkeypatch.setenv('TEST_DATABASE_URL', TEST)
    assert not conftest._test_database_authorized(DEV)


def test_malformed_test_configuration_is_rejected(monkeypatch):
    monkeypatch.setenv('TEST_DATABASE_URL', 'invalid-url')
    assert not conftest._test_database_authorized(TEST)


def test_relabeling_development_as_test_is_rejected(monkeypatch):
    monkeypatch.setenv('TEST_DATABASE_URL', DEV)
    assert not conftest._test_database_authorized(DEV)


def test_ci_reuses_only_its_job_database(monkeypatch):
    monkeypatch.setenv('CI', 'true')
    monkeypatch.setenv('DATABASE_URL', DEV)
    assert conftest._test_database_authorized(DEV)
    assert not conftest._test_database_authorized(TEST)


def test_ci_cannot_implicitly_use_config_defaults(monkeypatch):
    monkeypatch.setenv('CI', 'true')
    assert not conftest._test_database_authorized(DEV)


def test_ci_explicit_test_url_takes_precedence(monkeypatch):
    monkeypatch.setenv('CI', 'true')
    monkeypatch.setenv('DATABASE_URL', DEV)
    monkeypatch.setenv('TEST_DATABASE_URL', TEST)
    assert not conftest._test_database_authorized(DEV)
    assert conftest._test_database_authorized(TEST)


def test_seed_never_connects_without_authorization(monkeypatch):
    monkeypatch.setattr(conftest, '_database_fixtures_authorized', lambda: False)
    def forbidden_connection():
        pytest.fail('Seed attempted a database connection without permission')
    monkeypatch.setattr(conftest, '_is_db_reachable', forbidden_connection)
    fixture = conftest._seed_contract_test_tenants.__wrapped__()
    next(fixture)
    with pytest.raises(StopIteration):
        next(fixture)


def test_strict_business_fixture_fails_before_connection(monkeypatch):
    monkeypatch.setenv('PYTEST_REQUIRE_DB_STRICT', '1')
    monkeypatch.setattr(conftest, '_database_fixtures_authorized', lambda: False)
    def forbidden_connection():
        pytest.fail('Business fixture attempted an unauthorized connection')
    monkeypatch.setattr(conftest, '_is_db_reachable', forbidden_connection)
    with pytest.raises(pytest.fail.Exception, match='Explicit TEST_DATABASE_URL'):
        conftest.require_db.__wrapped__()
