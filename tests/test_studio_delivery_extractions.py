"""PCN payload contract after moving its mapper out of the endpoint godfile."""
import ast
import __future__
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace


def mapper():
    source = Path(__file__).parents[1] / 'app/services/compliance_service.py'
    node = next(n for n in ast.parse(source.read_text(encoding='utf-8')).body if isinstance(n, ast.FunctionDef) and n.name == 'pcn_to_dict')
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(source), 'exec', flags=__future__.annotations.compiler_flag), scope)
    return scope['pcn_to_dict']


def test_pcn_payload_retains_identity_tenant_status_and_timestamp():
    value = SimpleNamespace(id='pcn-1', produktname='Produkt', ufi='ABCD', cas_nummern='1', gefahrenklassen=['G1'], verwendungskategorie='Duenger', pcn_status='draft', tenant_id='tenant-a', created_at=datetime(2026, 1, 2, 3, 4, 5))
    assert mapper()(value) == {'meldung_id': 'pcn-1', 'produktname': 'Produkt', 'ufi': 'ABCD', 'cas_nummern': '1', 'gefahrenklassen': ['G1'], 'verwendungskategorie': 'Duenger', 'pcnStatus': 'draft', 'tenant_id': 'tenant-a', 'created_at': '2026-01-02T03:04:05', 'schema_version': 1}


def test_pcn_payload_preserves_empty_optional_values():
    value = SimpleNamespace(id='pcn-2', produktname='Leer', ufi=None, cas_nummern=None, gefahrenklassen=None, verwendungskategorie=None, pcn_status='draft', tenant_id='tenant-b', created_at=None)
    result = mapper()(value)
    assert result['ufi'] == result['cas_nummern'] == result['verwendungskategorie'] == ''
    assert result['gefahrenklassen'] == []
    assert result['created_at'] is None
    assert result['tenant_id'] == 'tenant-b'
