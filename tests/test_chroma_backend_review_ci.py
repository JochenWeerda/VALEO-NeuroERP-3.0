"""Include the standalone policy contracts in the ordinary backend CI suite."""
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.fixture(autouse=True)
def _enable_dev_token():
    """This isolated policy suite has no HTTP application."""
    yield


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """Policy fixtures use temporary files, never a database."""
    yield


def test_both_chroma_consumers_have_fail_closed_review_contracts():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "scripts",
         "-p", "test_chroma_backend_evidence.py", "-v"],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    # A missing/renamed suite must not silently pass unittest's zero-test run.
    assert "Ran 12 tests" in result.stderr, result.stdout + result.stderr
