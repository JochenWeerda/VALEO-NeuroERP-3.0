from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import Generator

import pytest

COMPOSE_FILE = Path(__file__).resolve().parents[3] / "docker-compose.integration.yml"


@pytest.fixture(scope="session")
def integration_environment() -> Generator[None, None, None]:
    if not COMPOSE_FILE.exists():
        pytest.skip("docker-compose.integration.yml nicht vorhanden")

    up_cmd = ["docker-compose", "-f", str(COMPOSE_FILE), "up", "-d", "--build"]
    down_cmd = ["docker-compose", "-f", str(COMPOSE_FILE), "down", "--remove-orphans"]

    subprocess.check_call(up_cmd)

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(asyncio.sleep(5))
        loop.close()
        yield
    finally:
        subprocess.check_call(down_cmd)
