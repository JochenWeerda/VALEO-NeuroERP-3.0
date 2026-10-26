"""Dienst-Ketten unter services/*/alembic teilen sich die Datenbank mit dem Backend.

Ohne eigene ``version_table`` lesen sie ``public.alembic_version`` des Backends, finden
dessen Revision nicht und scheitern bei jedem Start still (SERVICES-VERSION-TABLE-20261026).
Drei weitere Fehler hielten dieselben Ketten unbemerkt am Boden: Revisions-IDs laenger als
``version_num varchar(32)`` und Enum-Typen, die per ``CREATE TYPE`` und noch einmal implizit
ueber ``ENUM(name=...)`` angelegt wurden.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ROOT / "services"

# Ratsche: Dienste ohne eigene Versionstabelle. Laufen derzeit nicht (crm-ai nur in Compose
# definiert, die uebrigen gar nicht); ihre Ketten sind ungeprueft. Liste darf nur schrumpfen.
OHNE_EIGENE_VERSIONSTABELLE = {"crm-ai", "crm-consent", "crm-gdpr", "crm-marketing"}

VERSION_NUM_MAX = 32  # alembic_version.version_num ist varchar(32)


def configure_calls_without_version_table(source: str) -> int:
    """Zaehlt ``context.configure(...)``-Aufrufe ohne ``version_table``-Argument."""
    missing = 0
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "configure"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "context"
            and not any(kw.arg == "version_table" for kw in node.keywords)
        ):
            missing += 1
    return missing


def version_table_names(source: str) -> set[str]:
    """Liefert die Literalwerte von ``version_table`` (direkt oder ueber VERSION_TABLE)."""
    tree = ast.parse(source)
    constants = {
        target.id: node.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "version_table":
            if isinstance(node.value, ast.Constant):
                names.add(node.value.value)
            elif isinstance(node.value, ast.Name) and node.value.id in constants:
                names.add(constants[node.value.id])
    return names


def revision_id(source: str) -> str | None:
    for node in ast.parse(source).body:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
        if any(isinstance(t, ast.Name) and t.id == "revision" for t in targets):
            return node.value.value if isinstance(node.value, ast.Constant) else None
    return None


def doubly_created_enums(source: str) -> set[str]:
    """Enum-Namen, die per CREATE TYPE und zusaetzlich ohne create_type=False angelegt werden."""
    explicit = set(re.findall(r"CREATE TYPE\s+(\w+)", source))
    implicit = set(re.findall(r"ENUM\([^()]*name\s*=\s*['\"](\w+)['\"]", source))
    with_flag = set(re.findall(r"ENUM\([^()]*name\s*=\s*['\"](\w+)['\"][^()]*create_type\s*=\s*False", source))
    with_flag |= set(re.findall(r"ENUM\([^()]*create_type\s*=\s*False[^()]*name\s*=\s*['\"](\w+)['\"]", source))
    return explicit & (implicit - with_flag)


def _service_envs() -> list[Path]:
    return sorted(SERVICES.glob("*/alembic/env.py"))


def _service_revisions() -> list[Path]:
    # Ketten der Ratschen-Dienste sind ungeprueft (crm-marketing legt Enums doppelt an) und
    # werden mit ihrer Versionstabelle zusammen behoben.
    return sorted(
        p
        for p in SERVICES.glob("*/alembic/versions/*.py")
        if p.parents[2].name not in OHNE_EIGENE_VERSIONSTABELLE
    )


# --- Selbsttest der Muster -------------------------------------------------------------


def test_muster_erkennen_fehlende_und_vorhandene_versionstabelle():
    without = "context.configure(connection=c, target_metadata=m)\n"
    direct = 'context.configure(connection=c, version_table="x_alembic_version")\n'
    via_name = 'VT = "y_alembic_version"\ncontext.configure(url=u, version_table=VT)\n'
    assert configure_calls_without_version_table(without) == 1
    assert configure_calls_without_version_table(direct) == 0
    assert version_table_names(direct) == {"x_alembic_version"}
    assert version_table_names(via_name) == {"y_alembic_version"}


def test_muster_erkennen_doppelte_enum_anlage():
    doubled = (
        "op.execute(\"CREATE TYPE s AS ENUM ('a')\")\n"
        "sa.Column('x', postgresql.ENUM('a', name='s'))\n"
    )
    guarded = doubled.replace("name='s')", "name='s', create_type=False)")
    assert doubly_created_enums(doubled) == {"s"}
    assert doubly_created_enums(guarded) == set()
    assert revision_id('revision = "abc"\ndown_revision = None\n') == "abc"


# --- Vertrag ---------------------------------------------------------------------------


def test_jede_dienstkette_hat_eine_eigene_versionstabelle():
    envs = _service_envs()
    assert len(envs) >= 8, "Dienst-Ketten nicht gefunden"
    missing = {
        env.parents[1].name
        for env in envs
        if configure_calls_without_version_table(env.read_text(encoding="utf-8"))
    }
    assert missing <= OHNE_EIGENE_VERSIONSTABELLE, f"ohne eigene Versionstabelle: {sorted(missing - OHNE_EIGENE_VERSIONSTABELLE)}"
    assert OHNE_EIGENE_VERSIONSTABELLE <= missing, (
        f"Ratsche nachziehen, inzwischen behoben: {sorted(OHNE_EIGENE_VERSIONSTABELLE - missing)}"
    )


def test_versionstabellen_sind_eindeutig_und_nicht_die_des_backends():
    owners: dict[str, str] = {}
    for env in _service_envs():
        for name in version_table_names(env.read_text(encoding="utf-8")):
            assert name != "alembic_version", env
            assert owners.setdefault(name, env.parents[1].name) == env.parents[1].name, (
                f"{name} doppelt: {owners[name]} und {env.parents[1].name}"
            )


@pytest.mark.parametrize("path", _service_revisions(), ids=lambda p: f"{p.parents[2].name}/{p.name}")
def test_revisionen_passen_in_version_num_und_legen_enums_einmal_an(path: Path):
    source = path.read_text(encoding="utf-8")
    rev = revision_id(source)
    assert rev, "revision fehlt"
    assert len(rev) <= VERSION_NUM_MAX, f"{rev!r} hat {len(rev)} Zeichen"
    assert not doubly_created_enums(source)
