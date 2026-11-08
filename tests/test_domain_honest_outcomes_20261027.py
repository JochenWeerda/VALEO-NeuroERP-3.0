import asyncio
import pytest
from fastapi import HTTPException
import ast
import __future__
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime


def endpoint_body(module_name, function_name):
    # Isolated unit test of the unchanged function body; not an HTTP/auth test.
    source = Path(__file__).parents[1] / 'app/api/v1/endpoints' / (module_name + '.py')
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == function_name)
    function.decorator_list = []
    function.args.defaults = [ast.Constant(None) for _ in function.args.defaults]
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    scope = {'HTTPException': HTTPException, 'datetime': datetime}
    exec(compile(module, str(source), 'exec', flags=__future__.annotations.compiler_flag), scope)
    return scope[function_name]


compliance = SimpleNamespace(get_ustva_status=endpoint_body('compliance', 'get_ustva_status'))
pos_retoure = SimpleNamespace(pos_checkout=endpoint_body('pos_retoure', 'pos_checkout'))

class Result:
    def __init__(self, row=None, scalar=None): self.row, self.value = row, scalar
    def fetchone(self): return self.row
    def scalar(self): return self.value

class Database:
    def __init__(self, fail=False): self.fail, self.calls = fail, []
    def execute(self, statement, params):
        self.calls.append(params)
        if self.fail: raise RuntimeError('database unavailable')
        return Result(row=(100, 19, 4)) if len(self.calls) == 1 else Result(scalar=0)

def test_checkout_never_claims_a_booking():
    db = Database()
    with pytest.raises(HTTPException) as error:
        asyncio.run(pos_retoure.pos_checkout({'offline_id': 'offline-1', 'gesamt': 42}, db))
    assert error.value.status_code == 501
    assert 'nicht angebunden' in error.value.detail
    assert not db.calls

class _Anmeldung:
    """Antwort der Anmeldungsabfrage: keine Anmeldung im Zeitraum."""
    def __init__(self, calls): self.calls = calls
    def execute(self, statement, params):
        self.calls.append(params)
        return SimpleNamespace(mappings=lambda: SimpleNamespace(first=lambda: None))
    def rollback(self): pass


def _stand(**werte):
    # Hauptbuchstand (app.finance.ustva.berechne): seit 03.11.2026 die einzige Rechenquelle des Status.
    vorgabe = dict(gebuchte_buchungen=3, offene_entwuerfe=0, klaerungen=[], umsatz_netto=100, umsatzsteuer=19,
                   vorsteuer=4, zahllast=15)
    return SimpleNamespace(**{**vorgabe, **werte})


def test_ustva_readiness_is_not_transmission(monkeypatch):
    import app.finance.ustva as ustva
    aufrufe = []
    monkeypatch.setattr(ustva, 'berechne', lambda db, tenant, periode: aufrufe.append(tenant) or _stand())
    db = _Anmeldung([])
    body = asyncio.run(compliance.get_ustva_status(periode='2026-04', db=db, tenant_id='tenant-a'))
    assert body['readiness_pct'] == 100
    assert body['status'] == 'BEREIT'  # bereit, aber nicht uebermittelt
    assert body['elster_uebermittlung'] == 'NICHT_UEBERMITTELT'
    assert body['elster_transferticket'] is None
    assert body['zahllast'] == 15
    assert aufrufe == ['tenant-a'] and all(call['tid'] == 'tenant-a' for call in db.calls)

def test_ustva_database_failure_is_not_zero_report(monkeypatch):
    import app.finance.ustva as ustva
    from sqlalchemy.exc import OperationalError

    def kaputt(db, tenant, periode):
        raise OperationalError('SELECT', {}, Exception('database unavailable'))
    monkeypatch.setattr(ustva, 'berechne', kaputt)
    with pytest.raises(HTTPException) as error:
        asyncio.run(compliance.get_ustva_status(periode='2026-04', db=_Anmeldung([]), tenant_id='tenant-a'))
    assert error.value.status_code == 503
    assert 'nicht verfügbar' in error.value.detail
