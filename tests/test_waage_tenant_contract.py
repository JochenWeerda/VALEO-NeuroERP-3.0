from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.dialects import postgresql

from app.api.v1.endpoints import waage
from app.domains.operations.repository import WaageRepository


def finish(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    finally:
        coroutine.close()
    raise AssertionError("Unexpected suspension")


def test_payload_forbids_identity_and_invalid_values():
    for payload in (
        {"standort": "A", "typ": "LKW", "max_kapazitaet": 1, "tenant_id": "other"},
        {"standort": "A", "typ": "LKW", "max_kapazitaet": float("nan")},
        {"standort": "", "typ": "LKW", "max_kapazitaet": 1},
    ):
        with pytest.raises(ValidationError):
            waage.WaageCreate.model_validate(payload)


def test_repository_queries_include_verified_tenant_and_bound_limit():
    db = MagicMock()
    repo = WaageRepository(db, 'tenant-a')
    repo.get_by_id('foreign')
    # Mandant im Konstruktor: erst der Mandantenfilter, dann der Schluessel.
    expressions = (db.query.return_value.filter.call_args.args
                   + db.query.return_value.filter.return_value.filter.call_args.args)
    compiled = [str(x.compile(dialect=postgresql.dialect(), compile_kwargs={'literal_binds': True})) for x in expressions]
    assert any("tenant_id = 'tenant-a'" in x for x in compiled)
    assert any("id = 'foreign'" in x for x in compiled)
    repo.get_by_status('aktiv', skip=2, limit=3)
    db.query.return_value.filter.return_value.filter.return_value.offset.assert_called_with(2)
    db.query.return_value.filter.return_value.filter.return_value.offset.return_value.limit.assert_called_with(3)


def test_foreign_scale_and_calibration_are_denied(monkeypatch):
    repo = MagicMock()
    repo.get_by_id.return_value = None
    repo.update.return_value = None
    repo.delete.return_value = False
    mandanten = []
    monkeypatch.setattr(waage, 'WaageRepository', lambda db, tenant_id: mandanten.append(tenant_id) or repo)
    monkeypatch.setattr(waage.scale_import, 'locked_scale', lambda *args: (_ for _ in ()).throw(HTTPException(404, 'Waage nicht gefunden')))
    for operation in (
        waage.get_waage('foreign', db=object(), tenant_id='tenant-a'),
        waage.get_kalibrierung('foreign', db=object(), tenant_id='tenant-a'),
        waage.update_kalibrierung('foreign', waage.WaageCalibrationUpdate(), db=object(), tenant_id='tenant-a'),
        waage.update_waage('foreign', waage.WaageUpdate(typ='neu'), db=object(), tenant_id='tenant-a'),
        waage.delete_waage('foreign', db=object(), tenant_id='tenant-a'),
    ):
        with pytest.raises(HTTPException) as exc:
            finish(operation)
        assert exc.value.status_code == 404
    assert mandanten and set(mandanten) == {'tenant-a'}
    repo.get_by_id.assert_any_call('foreign')
    repo.update.assert_called_once_with('foreign', {'typ': 'neu'})
    repo.delete.assert_called_once_with('foreign')


def test_calibration_reads_canonical_scale(monkeypatch):
    from types import SimpleNamespace
    scale = SimpleNamespace(id='own', letzte_eichung=None, naechste_eichung=None, eichamt=None, zertifikat_nr=None)
    repo = MagicMock()
    repo.get_by_id.return_value = scale
    monkeypatch.setattr(waage, 'WaageRepository', lambda db, tenant_id: repo)
    assert finish(waage.get_kalibrierung('own', db=object(), tenant_id='tenant-a'))['waage_id'] == 'own'


def test_missing_tenant_cannot_query_unassigned():
    for leer in ('', '  ', None):
        with pytest.raises(ValueError):
            WaageRepository(MagicMock(), leer)


def test_legacy_child_prevents_scale_deletion():
    db = MagicMock()
    db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = object()
    db.query.return_value.filter.return_value.first.return_value = object()
    with pytest.raises(ValueError):
        WaageRepository(db, 'tenant-a').delete('own')
    db.delete.assert_not_called()


def test_legacy_weighing_is_retired():
    with pytest.raises(HTTPException) as exc:
        finish(waage.create_wiegung({'waage_id': 'foreign'}))
    assert exc.value.status_code == 410


def test_targeted_role_plan_rejects_bypass_and_unprotected_objects():
    from types import SimpleNamespace
    from scripts.provision_db_roles import waage_only_grant_plan

    def result(*, row=None, scalar=None, rows=()):
        value = MagicMock()
        value.one_or_none.return_value = row
        value.scalar_one.return_value = scalar
        value.scalars.return_value.all.return_value = list(rows)
        return value

    role = SimpleNamespace(rolsuper=False, rolbypassrls=False)
    target = SimpleNamespace(relrowsecurity=True, relforcerowsecurity=False, owner_member=False)
    conn = MagicMock()
    conn.execute.side_effect = [result(row=role), result(scalar=False), result(row=target), result(row=target), result(rows=['ops_wiegungen'])]
    with pytest.raises(RuntimeError, match='ungeschuetzte'):
        waage_only_grant_plan(conn)
    conn.execute.side_effect = [result(row=role), result(scalar=True)]
    with pytest.raises(RuntimeError, match='Bypass'):
        waage_only_grant_plan(conn)
    conn.execute.side_effect = [result(row=role), result(scalar=False), result(row=target), result(row=target), result(), result(), result()]
    assert waage_only_grant_plan(conn) == [
        'GRANT USAGE ON SCHEMA domain_ops TO valeo_app',
        'GRANT SELECT, INSERT, UPDATE, DELETE ON domain_ops.ops_waagen TO valeo_app',
        'GRANT SELECT, INSERT, UPDATE ON domain_ops.waage_import_entries TO valeo_app',
        'GRANT EXECUTE ON FUNCTION public.waage_reference_allowed(text) TO valeo_app',
    ]


def test_verified_claim_boundary_rejects_blank_and_conflicting_header():
    from app.auth.tenant import get_verified_tenant_id
    with pytest.raises(HTTPException) as missing:
        get_verified_tenant_id({'sub': 'user', 'raw': {'tenant_id': ''}}, None)
    assert missing.value.status_code == 403
    with pytest.raises(HTTPException) as conflicting:
        get_verified_tenant_id({'sub': 'user', 'raw': {'tenant_id': 'tenant-a'}}, 'tenant-b')
    assert conflicting.value.status_code == 403
    assert get_verified_tenant_id({'sub': 'user', 'raw': {'tenant_id': 'tenant-a'}}, 'tenant-a') == 'tenant-a'


def test_legacy_ascii_rejects_foreign_scale_before_read(monkeypatch):
    repo = MagicMock()
    repo.get_by_id.return_value = None
    monkeypatch.setattr(waage, 'WaageRepository', lambda db, tenant_id: repo)
    upload = MagicMock()
    with pytest.raises(HTTPException) as exc:
        finish(waage.import_ascii(upload, waage_id='foreign', db=object(), tenant_id='tenant-a'))
    assert exc.value.status_code == 404
    upload.read.assert_not_called()
