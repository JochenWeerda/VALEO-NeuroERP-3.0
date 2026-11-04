"""Vertrag: kein Mandanten-Rueckfall auf "system", eingefrorene Rueckfaelle auf "default".

Seit 27.10.2026 (SYSTEM-TENANT-FALLBACK) nimmt Code ohne ausdruecklichen Mandanten den des
Kontexts (``get_current_tenant_id``, fail-closed) oder - an HTTP-Eingaengen - den aus dem Token
(``get_tenant_id``). ``"system"`` ist der Mandant gemeinsamer Referenzdaten
(``SHARED_TENANT_ID``) und nie ein Rueckfall. Rueckfaelle auf ``"default"`` (Standardmandant)
sind ein eigener, aelterer Befund: ihre Zahl je Datei ist eingefroren und darf nur sinken.

Gesucht wird im Syntaxbaum, nicht im Text:
    def f(tenant_id: str = "system")             Vorgabe eines Parameters
    tenant_id: str = "system" / Field(default=)   Vorgabe eines Modellfelds
    payload.get("tenant_id", "system")             Rueckfall beim Lesen
    tenant_id or "system"                          Rueckfall im Ausdruck
"""

from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
CODE_ROOTS = ("app", "modules")
NAMES = {"tenant_id", "x_tenant_id", "x_tenant", "mandant_id", "mandanten_id", "tenant"}
LITERALS = ("system", "default")

# Stand 27.10.2026: alle 43 eingefrorenen Rueckfaelle abgebaut (TENANT-FALLBACK-ABBAU-20261027). Die Liste bleibt
# leer; ein neuer Eintrag ist ein Rueckfall, kein Ausnahmefall.
DEFAULT_BASELINE: dict[str, int] = {}


def _literal(node) -> str | None:
    if isinstance(node, ast.Constant) and node.value in LITERALS:
        return node.value
    if isinstance(node, ast.Call):
        for keyword in node.keywords:
            if keyword.arg == "default" and isinstance(keyword.value, ast.Constant) and keyword.value.value in LITERALS:
                return keyword.value.value
        for arg in node.args[:1]:  # Query("default") / Header("default")
            if isinstance(arg, ast.Constant) and arg.value in LITERALS:
                return arg.value
    return None


def fallbacks(source: str) -> list[tuple[int, str]]:
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            pairs = list(zip(args.args[len(args.args) - len(args.defaults):], args.defaults))
            pairs += [(a, d) for a, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None]
            found += [(d.lineno, lit) for a, d in pairs if a.arg in NAMES and (lit := _literal(d))]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in NAMES:
            if node.value is not None and (lit := _literal(node.value)):
                found.append((node.lineno, lit))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            if (len(node.args) == 2 and isinstance(node.args[0], ast.Constant) and node.args[0].value in NAMES
                    and isinstance(node.args[1], ast.Constant) and node.args[1].value in LITERALS):
                found.append((node.lineno, node.args[1].value))
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            names = [v for v in node.values if isinstance(v, ast.Name) and v.id in NAMES]
            lits = [v.value for v in node.values if isinstance(v, ast.Constant) and v.value in LITERALS]
            if names and lits:
                found.append((node.lineno, lits[0]))
    return found


def _scan() -> dict[str, list[tuple[int, str]]]:
    result = {}
    for root in CODE_ROOTS:
        for path in sorted((ROOT / root).rglob("*.py")):
            rel = path.relative_to(ROOT).as_posix()
            if "/tests/" in rel or "__pycache__" in rel:
                continue
            hits = fallbacks(path.read_text(encoding="utf-8-sig", errors="replace"))
            if hits:
                result[rel] = hits
    return result


SCAN = _scan()


def test_muster_selbsttest():
    source = '''
def a(tenant_id: str = "system"): pass
def b(x, *, tenant_id="default"): pass
def ok(tenant_id: str = Depends(get_tenant_id), template_key: str = "default"): pass
class M:
    tenant_id: str = "system"
    tenant: str = Field(default="default")
    other: str = "system"
v = payload.get("tenant_id", "system")
w = tenant_id or "default"
z = payload.get("role", "system")
'''
    assert sorted(lit for _, lit in fallbacks(source)) == ["default", "default", "default", "system", "system", "system"]


def test_kein_rueckfall_auf_system():
    hits = {f: [n for n, lit in h if lit == "system"] for f, h in SCAN.items()}
    hits = {f: n for f, n in hits.items() if n}
    assert not hits, f"Mandant 'system' als Rueckfall: {hits}"


def test_rueckfaelle_auf_default_nur_abnehmend():
    counts = {f: sum(lit == "default" for _, lit in h) for f, h in SCAN.items()}
    counts = {f: c for f, c in counts.items() if c}
    grown = {f: (c, DEFAULT_BASELINE.get(f, 0)) for f, c in counts.items() if c > DEFAULT_BASELINE.get(f, 0)}
    assert not grown, f"neue Rueckfaelle auf 'default' (gefunden, erlaubt): {grown}"
    shrunk = {f: (counts.get(f, 0), c) for f, c in DEFAULT_BASELINE.items() if counts.get(f, 0) < c}
    assert not shrunk, f"weniger Rueckfaelle - bitte DEFAULT_BASELINE senken: {shrunk}"


def test_gemeinsamer_mandant_ist_benannt():
    from app.core.knowledge_core_contracts import _default_knowledge_objects
    from app.core.tenant_context import SHARED_TENANT_ID

    assert SHARED_TENANT_ID == "system"
    assert {o.tenant_id for o in _default_knowledge_objects()} == {SHARED_TENANT_ID}


# --- Zweite und dritte Form: Standardmandant aus der Konfiguration oder als feste UUID ---------------------------
# Bis 28.10.2026 fielen ueber 60 Stellen nicht ueber das Literal "default", sondern ueber settings.DEFAULT_TENANT_ID
# (``tenant_id or DEFAULT_TENANT``, ``Query(DEFAULT_TENANT)``) oder eine fest eingetragene UUID
# (``tenant_id or _DEFAULT_TENANT``) auf den Standardmandanten zurueck — fuer das Muster oben unsichtbar.
STANDARD_UUID = "00000000-0000-0000-0000-000000000001"
STANDARD_ERLAUBT = {
    "app/core/config.py": "Definition der Einstellung",
    "app/core/fibu_audit.py": "Systemnutzer als Urheber von Hintergrundlaeufen, kein Mandant",
    "app/middleware/tenant_enforcement.py": "nur im Dev-Modus (API_DEV_TOKEN)",
    "app/core/inventory_permissions.py": "nur fuer das Dev-Token",
    "app/seeds/inventory_seed.py": "Seed fuer die Entwicklungsdatenbank",
    "app/api/v1/endpoints/reklamation_api.py": "Vergleich, kein Rueckfall (Codex-Claim Reklamation)",
    # Nicht eingebunden (kein Import in app/): toter Code, Aufraeumen ist ein eigener Slice.
    "app/security/audit_service.py": "nicht eingebunden",
    "app/security/compliance_monitor.py": "nicht eingebunden",
    "app/security/encryption_service.py": "nicht eingebunden",
    "app/security/incident_response.py": "nicht eingebunden",
    "app/quality/quality_assurance.py": "nicht eingebunden",
}


def _standard_stellen(source: str) -> list[int]:
    lines = []
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "DEFAULT_TENANT_ID":
            lines.append(node.lineno)
        elif isinstance(node, ast.Constant) and node.value == STANDARD_UUID:
            lines.append(node.lineno)
    return sorted(set(lines))


def test_kein_standardmandant_aus_konfiguration_oder_uuid():
    funde = {}
    for root in CODE_ROOTS:
        for path in sorted((ROOT / root).rglob("*.py")):
            rel = path.relative_to(ROOT).as_posix()
            if "/tests/" in rel or "__pycache__" in rel or rel in STANDARD_ERLAUBT:
                continue
            stellen = _standard_stellen(path.read_text(encoding="utf-8-sig", errors="replace"))
            if stellen:
                funde[rel] = stellen
    assert not funde, f"Standardmandant als Rueckfall: {funde}"


def test_standard_muster_selbsttest():
    quelle = 'x = tenant_id or settings.DEFAULT_TENANT_ID\n_D = "00000000-0000-0000-0000-000000000001"\n"""Doku: DEFAULT_TENANT_ID"""\n'
    assert _standard_stellen(quelle) == [1, 2]
