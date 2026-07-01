"""Tests fuer scripts/maybe_regenerate_agent_handbuch.py."""

from __future__ import annotations

import pytest

from scripts.maybe_regenerate_agent_handbuch import should_regenerate


@pytest.mark.unit
def test_should_regenerate_on_screen_definitions() -> None:
    assert should_regenerate(["app/core/screen_definitions.py"])


@pytest.mark.unit
def test_should_regenerate_on_workflow_spec() -> None:
    assert should_regenerate(["docs/workflows/otc-sales-order.md"])


@pytest.mark.unit
def test_should_not_regenerate_on_unrelated() -> None:
    assert not should_regenerate(["app/api/v1/endpoints/health.py", "README.md"])
