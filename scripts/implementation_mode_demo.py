#!/usr/bin/env python3
"""
Small, self-contained demo for the APM implementation mode.

The previous version embedded large generated code snippets directly into
triple-quoted strings and had become syntactically invalid. This replacement
keeps the file executable and useful as a lightweight demonstration artifact.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ImplementationArtifact:
    name: str
    category: str
    status: str
    summary: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def build_demo_artifacts() -> list[ImplementationArtifact]:
    """Return a stable, serialisable example result for implementation mode."""
    return [
        ImplementationArtifact(
            name="db_connector.py",
            category="database",
            status="planned",
            summary="Connection handling and health checks for transactional workflows.",
        ),
        ImplementationArtifact(
            name="transaction_repository.py",
            category="repository",
            status="planned",
            summary="Persistence layer with optimistic locking and batch save support.",
        ),
        ImplementationArtifact(
            name="test_transaction.py",
            category="tests",
            status="planned",
            summary="Contract tests for transaction lifecycle and chunk processing.",
        ),
    ]


async def run_demo(output_path: Path | None = None) -> dict[str, object]:
    """Assemble and optionally persist a minimal implementation-mode snapshot."""
    artifacts = build_demo_artifacts()
    result = {
        "mode": "implementation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_count": len(artifacts),
        "artifacts": [asdict(artifact) for artifact in artifacts],
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        logger.info("Implementation demo written to %s", output_path)
    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    output_path = Path("data/demo/implementation_mode_demo.json")
    result = asyncio.run(run_demo(output_path))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
