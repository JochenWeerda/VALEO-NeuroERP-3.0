"""Image evidence must match the complete checkout, without stale host artifacts."""
import importlib.util
import os
from pathlib import Path
import shlex
import shutil

ROOT = Path(__file__).resolve().parents[1]


def load_report(root):
    spec = importlib.util.spec_from_file_location("image_drift_report", root / "scripts/doc_drift_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_report()


def test_image_stage_matches_full_checkout_report(tmp_path):
    if os.name == "nt":
        tmp_path = Path("\\\\?\\" + str(tmp_path.resolve()))
    checkout = tmp_path / "checkout"
    output = tmp_path / "image-inputs"
    fixtures = {
        "docs/deep/coverage.md": "covered_endpoint covered_service covered_migration",
        "app/api/v1/endpoints/covered_endpoint.py": "",
        "app/api/v1/endpoints/missing_endpoint.py": "",
        "app/services/covered_service.py": "",
        "alembic/versions/covered_migration.py": "",
        "packages/frontend-web/src/pages/entry.tsx": "import '@/components/bridge';",
        "packages/frontend-web/src/components/bridge.ts": "import '@/pages/embedded';",
        "packages/frontend-web/src/pages/embedded.tsx": "export default function Page() {}",
        "packages/frontend-web/src/app/navigation/domains/empty.tsx": "",
        "packages/frontend-web/src/app/routing/route-inventory.gen.json": '{"routes":[{"module":"@/pages/entry","path":"/entry"}]}',
        "config/doc_drift_page_altlast.json": '{"seiten":[]}',
        "scripts/doc_drift_report.py": (ROOT / "scripts/doc_drift_report.py").read_text(encoding="utf-8"),
    }
    for relative, text in fixtures.items():
        target = checkout / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    dockerfile = (ROOT / "Dockerfile.backend").read_text(encoding="utf-8")
    stage = dockerfile.split("AS quality-evidence\n", 1)[1].split("FROM ${PYTHON_IMAGE} AS builder", 1)[0]
    for line in stage.splitlines():
        if not line.startswith("COPY "):
            continue
        _, source, destination = shlex.split(line)
        source_path = checkout / source
        target = output / destination
        if source_path.is_dir():
            if source == "docs/":
                for item in source_path.rglob("*"):
                    if item.is_file() and (item.suffix == ".md" or item == checkout / "docs/admin/table-catalog.json"):
                        dest = target / item.relative_to(source_path)
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(item, dest)
            else:
                shutil.copytree(source_path, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target)
    actual = load_report(output)
    expected = load_report(checkout)
    assert actual["summary"] == expected["summary"]
    assert actual["summary"]["total_drift_items"] == 1
    assert actual["summary"]["endpoint_no_doc"] == 1
    assert actual["issues"] == expected["issues"]
    runtime = dockerfile.split("AS runtime", 1)[1]
    assert "COPY --from=quality-evidence --chown=appuser:appuser /evidence/artifacts/doc_drift_report.json /app/artifacts/doc_drift_report.json" in runtime
    assert "COPY docs/" not in runtime
    assert "COPY artifacts/" not in stage + runtime


def test_backend_context_preserves_secret_and_artifact_exclusions():
    base = (ROOT / ".dockerignore").read_text(encoding="utf-8")
    specific = (ROOT / "Dockerfile.backend.dockerignore").read_text(encoding="utf-8")
    assert specific.startswith(base)
    exceptions = [line for line in specific[len(base):].splitlines() if line and not line.startswith("#")]
    assert exceptions[:3] == ["!docs/", "!docs/**/", "!docs/**/*.md"]
    assert "**/.env*" in exceptions[3:]
    for tree in (".git", "node_modules", "artifacts", ".venv", "__pycache__"):
        assert f"**/{tree}" in exceptions[3:]
        assert f"**/{tree}/**" in exceptions[3:]
    assert ".env" in base.splitlines()
    assert "artifacts" in base.splitlines()
