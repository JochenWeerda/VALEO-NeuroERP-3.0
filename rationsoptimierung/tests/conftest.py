"""Pytest configuration for rationsoptimierung tests."""
import os
import sys

# Ensure rationsoptimierung app is on path when running from project root
_rations_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _rations_dir not in sys.path:
    sys.path.insert(0, _rations_dir)

import pytest
from fastapi.testclient import TestClient

# Default API key must match app's dev default
API_KEY = os.getenv("RATIONS_OPTIMIZATION_API_KEY", "dev-api-key-change-in-production")


@pytest.fixture
def client():
    """Test client with API key header for authenticated endpoints."""
    from app.main import app
    return TestClient(app, headers={"X-API-Key": API_KEY})


@pytest.fixture
def client_no_auth():
    """Test client without API key (for health endpoint)."""
    from app.main import app
    return TestClient(app)
