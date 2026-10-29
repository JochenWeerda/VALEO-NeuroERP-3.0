"""Backend und inventory-Dienst legen public.inventory_* in derselben Form an.

Der Dienst fuehrt die Tabellen (INVENTORY-OWNERSHIP-20261026); die Backend-Migration
inventory_service_shape_20261026 traegt Kopien seiner _create_*-Funktionen fuer die vier
Tabellen, die das Backend fuer den Wareneingangsabgleich liest. Weichen die Kopien ab, legt
eine frische Datenbank je nach Startreihenfolge zwei verschiedene Formen an.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "alembic" / "versions" / "inventory_service_shape_20261026.py"
SERVICE = ROOT / "services" / "inventory" / "alembic" / "versions" / "inventory_0001_baseline.py"

SHARED_TABLES = (
    "inventory_warehouses",
    "inventory_locations",
    "inventory_goods_receipts",
    "inventory_goods_receipt_lines",
)


def create_functions(source: str) -> dict[str, str]:
    """``_create_<tabelle>``-Funktionen als normalisierter AST-Dump je Tabellenname."""
    return {
        node.name.removeprefix("_create_"): ast.dump(ast.Module(body=node.body, type_ignores=[]))
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_create_")
    }


def test_muster_erkennt_abweichende_spalte():
    a = "def _create_t() -> None:\n    op.create_table('t', sa.Column('id', sa.UUID()))\n"
    b = a.replace("sa.UUID()", "sa.Text()")
    assert create_functions(a) == create_functions(a.replace("    op", "    op", 1))
    assert create_functions(a)["t"] != create_functions(b)["t"]


def test_backend_kopien_entsprechen_der_dienstbasis():
    backend = create_functions(BACKEND.read_text(encoding="utf-8"))
    service = create_functions(SERVICE.read_text(encoding="utf-8"))
    assert set(backend) == set(SHARED_TABLES)
    for table in SHARED_TABLES:
        assert backend[table] == service[table], f"{table}: Backend-Kopie weicht von der Dienstbasis ab"
