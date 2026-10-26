"""RLS-Plan P4: das Bereinigungsskript trifft nur eindeutige Testmandanten."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from rls_cleanup_test_tenants import REGISTRY_REMOVABLE, TEST_TENANT  # noqa: E402

pytestmark = pytest.mark.unit

KEEP = [
    "00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000051",
    "00000000-0000-0000-0000-000000000002", "system", "SYSTEM", "default", "legacy-unassigned",
    "valeo", "sd-ee9250d7", "meridian-abnahme", "test-tenantx", "xtest-12345678", "test-1234567",
]
DROP = [
    "test-tenant", "test-44a44b76", "tenant-a", "TENANT-TEST", "t1", "tenant-api-test",
    "test-tenant-pos-001", "tenant-a-persist", "tenant-agent-persist", "test-tenant-finance-001",
]


@pytest.mark.parametrize("value", KEEP)
def test_bleibt(value):
    assert not TEST_TENANT.match(value)


@pytest.mark.parametrize("value", DROP)
def test_wird_entfernt(value):
    assert TEST_TENANT.match(value)


def test_register_nur_zufaellige_testmandanten():
    assert REGISTRY_REMOVABLE.match("test-44a44b76")
    assert not REGISTRY_REMOVABLE.match("test-tenant")
    assert not REGISTRY_REMOVABLE.match("00000000-0000-0000-0000-000000000002")
