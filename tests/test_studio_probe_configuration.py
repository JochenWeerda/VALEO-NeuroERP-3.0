"""Probe selection cannot turn a development/production database into a simulator."""
import pytest
from app.services import studio_process_simulation as simulation
from app.core.config import settings


@pytest.mark.parametrize('environment', ['development', 'production', 'staging'])
def test_same_application_database_rejected_outside_explicit_test(monkeypatch, environment):
    url = 'postgresql://synthetic@localhost/valeo_probe'
    monkeypatch.setenv('TEST_DATABASE_URL', url)
    monkeypatch.delenv('CI', raising=False)
    monkeypatch.setattr(settings, 'APP_ENV', environment)
    monkeypatch.setattr(settings, 'DATABASE_URL', url)
    with pytest.raises(RuntimeError, match='simulation_database_not_authorized'):
        simulation._configured_probe()


def test_explicit_shared_test_probe_uses_declared_engine(monkeypatch):
    url = 'postgresql://synthetic@localhost/valeo_probe'
    monkeypatch.setenv('TEST_DATABASE_URL', url)
    monkeypatch.delenv('CI', raising=False)
    monkeypatch.setattr(settings, 'APP_ENV', 'test')
    monkeypatch.setattr(settings, 'DATABASE_URL', url)
    sentinel = object()
    monkeypatch.setattr(simulation, '_probe_engine', lambda selected: sentinel if selected == url else None)
    assert simulation._configured_probe() is sentinel


@pytest.mark.parametrize('app_url,probe_url', [
    ('postgresql://synthetic@localhost/production', 'postgresql://synthetic@localhost/production'),
    ('postgresql://synthetic@localhost/valeo_probe', 'postgresql://synthetic@elsewhere/valeo_probe'),
    ('postgresql://synthetic@localhost/valeo_probe', 'postgresql://other@localhost/valeo_probe'),
])
def test_test_environment_does_not_waive_database_or_connection_identity(monkeypatch, app_url, probe_url):
    monkeypatch.setenv('TEST_DATABASE_URL', probe_url)
    monkeypatch.delenv('CI', raising=False)
    monkeypatch.setattr(settings, 'APP_ENV', 'test')
    monkeypatch.setattr(settings, 'DATABASE_URL', app_url)
    with pytest.raises(RuntimeError, match='simulation_database_not_authorized'):
        simulation._configured_probe()


def test_ci_still_requires_exact_job_database(monkeypatch):
    monkeypatch.setenv('CI', 'true')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://synthetic@localhost/job')
    monkeypatch.setenv('TEST_DATABASE_URL', 'postgresql://synthetic@localhost/valeo_probe')
    monkeypatch.setattr(settings, 'APP_ENV', 'test')
    with pytest.raises(RuntimeError, match='simulation_ci_database_not_authorized'):
        simulation._configured_probe()
