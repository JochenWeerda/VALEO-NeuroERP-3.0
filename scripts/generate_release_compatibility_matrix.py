"""Generate the release compatibility matrix for a commit SHA.

The matrix binds application version, database revision, API contract,
runtime toolchains and optional immutable image digests to a single
release evidence record.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _git_short_sha(full_sha: str) -> str:
    return full_sha[:12]


def _alembic_head() -> str:
    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    if len(heads) != 1:
        raise SystemExit(f"Expected exactly 1 Alembic head, got {len(heads)}: {heads}")
    return heads[0]


def _app_version() -> str:
    package_json = PROJECT_ROOT / "packages/frontend-web/package.json"
    data = _read_json(package_json)
    return str(data.get("version", "0.0.0"))


def build_matrix(
    *,
    backend_image_digest: str | None = None,
    frontend_image_digest: str | None = None,
    git_sha: str | None = None,
) -> dict:
    pins = _read_json(PROJECT_ROOT / "config/release-toolchain-pins.json")
    full_sha = git_sha or _git_sha()

    matrix = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "git_sha": full_sha,
        "git_sha_short": _git_short_sha(full_sha),
        "app_version": _app_version(),
        "database_revision": _alembic_head(),
        "api_contract": pins["api_contract"],
        "runtime": {
            "python": pins["python"],
            "node": pins["node"],
            "pnpm": pins["pnpm"],
        },
        "toolchain_pins": pins["python_packages"],
        "images": {
            "backend_digest": backend_image_digest or "not-built",
            "frontend_digest": frontend_image_digest or "not-built",
        },
        "policy": "docs/operations/dependency-and-compatibility-maintenance.md",
    }
    return matrix


def render_markdown(matrix: dict) -> str:
    images = matrix["images"]
    toolchain = matrix["toolchain_pins"]
    runtime = matrix["runtime"]
    lines = [
        "# Release Compatibility Matrix",
        "",
        f"Generated: `{matrix['generated_at']}`",
        "",
        "| Dimension | Value |",
        "|---|---|",
        f"| Git SHA | `{matrix['git_sha_short']}` (`{matrix['git_sha']}`) |",
        f"| App version | `{matrix['app_version']}` |",
        f"| Database revision (Alembic head) | `{matrix['database_revision']}` |",
        f"| API contract | `{matrix['api_contract']}` |",
        f"| Python | `{runtime['python']}` |",
        f"| Node.js | `{runtime['node']}` |",
        f"| pnpm | `{runtime['pnpm']}` |",
        f"| Backend image digest | `{images['backend_digest']}` |",
        f"| Frontend image digest | `{images['frontend_digest']}` |",
        "",
        "## Python test toolchain",
        "",
        "| Package | Pin |",
        "|---|---|",
    ]
    for package, pin in sorted(toolchain.items()):
        lines.append(f"| `{package}` | `{pin}` |")
    lines.extend(
        [
            "",
            f"Policy: `{matrix['policy']}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=PROJECT_ROOT / "artifacts/release-compatibility-matrix.json",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=PROJECT_ROOT / "artifacts/release-compatibility-matrix.md",
    )
    parser.add_argument("--git-sha", default=None)
    parser.add_argument("--backend-image-digest", default=None)
    parser.add_argument("--frontend-image-digest", default=None)
    args = parser.parse_args()

    matrix = build_matrix(
        git_sha=args.git_sha,
        backend_image_digest=args.backend_image_digest,
        frontend_image_digest=args.frontend_image_digest,
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    args.output_markdown.write_text(render_markdown(matrix), encoding="utf-8")
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_markdown}")


if __name__ == "__main__":
    main()
