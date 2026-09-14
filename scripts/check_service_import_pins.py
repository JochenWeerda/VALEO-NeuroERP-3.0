#!/usr/bin/env python
"""Prueft, ob jeder Service-Import in seiner requirements.txt gepinnt ist.

Hintergrund: Ein Docker-Image kann fehlerfrei bauen und die App trotzdem beim
Import sterben, wenn eine Laufzeit-Abhaengigkeit im Manifest fehlt. Genau so
sind ``services/ai`` (fehlendes ``python-multipart``) und
``services/crm-marketing`` (fehlendes ``PyJWT``) ausgefallen -- in beiden
Faellen war der Build gruen. Dieser Check findet die Luecke statisch, ohne
22 Images bauen zu muessen.

Der Check unterscheidet drei Kategorien:

* **Luecke** (Exit 1): Ein Pflicht-Import hat keinen Pin. Die App stirbt beim Start.
* **Optional** (nur Hinweis): Der Import steht in ``try/except ImportError``.
  Der Service laeuft, aber mit stillem Funktionsverlust.
* **Repo-Paket** (nur Hinweis): Der Import zeigt auf ein Paket unter ``packages/``,
  das das Manifest nicht per ``-e`` verdrahtet.

Aufruf:
    python scripts/check_service_import_pins.py                 # alle Services
    python scripts/check_service_import_pins.py services/ai     # einzeln
    python scripts/check_service_import_pins.py --include-tests # Testcode mitpruefen
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Importname -> Distributionsname. Nur Faelle, in denen beide auseinanderfallen;
# der Rest wird ueber Normalisierung (Unterstrich/Bindestrich) aufgeloest.
IMPORT_TO_DISTRIBUTION = {
    "attr": "attrs",
    "cv2": "opencv-python",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "fitz": "pymupdf",
    "jose": "python-jose",
    "jwt": "pyjwt",
    "multipart": "python-multipart",
    "nats": "nats-py",
    "OpenSSL": "pyopenssl",
    "PIL": "pillow",
    "pkg_resources": "setuptools",
    "psycopg2": "psycopg2-binary",
    "pythonjsonlogger": "python-json-logger",
    "sklearn": "scikit-learn",
    "yaml": "pyyaml",
}

# Distributionen, die weitere Importnamen mitbringen (Extras oder harte Abhaengigkeiten).
DISTRIBUTION_PROVIDES = {
    "uvicorn": {"uvicorn", "uvloop", "httptools", "watchfiles", "websockets"},
    "celery": {"celery", "kombu", "billiard", "vine"},
    "fastapi": {"fastapi", "starlette", "pydantic"},
    "sentence-transformers": {"sentence_transformers", "torch", "transformers", "numpy", "scipy", "sklearn"},
    "chromadb": {"chromadb", "numpy", "pydantic", "onnxruntime", "tokenizers"},
    "langchain-core": {"langchain_core", "langsmith", "tenacity", "jsonpatch"},
    "langgraph": {"langgraph", "langchain_core"},
    "opentelemetry-api": {"opentelemetry"},
    "opentelemetry-sdk": {"opentelemetry"},
    "pandas": {"pandas", "numpy"},
    "scikit-learn": {"sklearn", "numpy", "scipy", "joblib"},
    "beautifulsoup4": {"bs4"},
}

# Verzeichnisnamen, die als lokale Pakete gelten und nie gepinnt sein muessen.
LOCAL_PACKAGE_HINTS = {"app", "src", "tests", "test", "alembic", "main", "core", "shared", "services"}

REQUIREMENT_LINE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*(?:[<>=!~;].*)?$")


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


@dataclass
class Manifest:
    provided: set[str] = field(default_factory=set)
    editable_paths: list[str] = field(default_factory=list)


@dataclass
class ImportSite:
    sample: Path
    optional: bool
    lazy: bool = False


def parse_requirements(path: Path) -> Manifest:
    """Sammelt gepinnte Distributionen samt der Namen, die sie mitliefern."""
    manifest = Manifest()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith(("-e ", "--editable ")):
            manifest.editable_paths.append(line.split(maxsplit=1)[1].strip())
            continue
        if line.startswith("-"):
            continue
        match = REQUIREMENT_LINE.match(line)
        if not match:
            continue
        dist = normalize(match.group(1))
        manifest.provided.add(dist)
        for extra in DISTRIBUTION_PROVIDES.get(dist, set()):
            manifest.provided.add(normalize(extra))
    return manifest


def modules_from_editable(service_dir: Path, editable_paths: list[str]) -> set[str]:
    """Top-Level-Modulnamen, die ein per ``-e`` eingebundenes Paket bereitstellt."""
    modules: set[str] = set()
    for rel in editable_paths:
        target = (service_dir / rel).resolve()
        if not target.is_dir():
            continue
        modules.add(normalize(target.name))
        for child in target.iterdir():
            if child.is_dir() and (child / "__init__.py").exists():
                modules.add(normalize(child.name))
            elif child.suffix == ".py" and child.stem != "setup":
                modules.add(normalize(child.stem))
    return modules


def _catches_import_error(node: ast.Try) -> bool:
    for handler in node.handlers:
        exc = handler.type
        names: list[str] = []
        if isinstance(exc, ast.Name):
            names = [exc.id]
        elif isinstance(exc, ast.Tuple):
            names = [e.id for e in exc.elts if isinstance(e, ast.Name)]
        elif exc is None:
            names = ["ImportError"]
        if {"ImportError", "ModuleNotFoundError", "Exception"} & set(names):
            return True
    return False


def _collect_imports(
    body: list[ast.stmt],
    *,
    lazy: bool,
    guarded: bool,
    out: list[tuple[ast.stmt, bool, bool]],
) -> None:
    """Sammelt Imports und merkt sich, ob sie erst zur Laufzeit bzw. abgesichert laufen.

    ``lazy`` markiert Imports innerhalb von Funktionen oder Klassen: die koennen den
    App-Start nicht verhindern. ``guarded`` markiert Imports in einem
    ``try/except ImportError``.
    """
    for stmt in body:
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            out.append((stmt, lazy, guarded))
        elif isinstance(stmt, ast.Try):
            inner_guarded = guarded or _catches_import_error(stmt)
            _collect_imports(stmt.body, lazy=lazy, guarded=inner_guarded, out=out)
            for handler in stmt.handlers:
                _collect_imports(handler.body, lazy=lazy, guarded=True, out=out)
            _collect_imports(stmt.orelse, lazy=lazy, guarded=inner_guarded, out=out)
            _collect_imports(stmt.finalbody, lazy=lazy, guarded=guarded, out=out)
        elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            _collect_imports(stmt.body, lazy=True, guarded=guarded, out=out)
        elif isinstance(stmt, (ast.If, ast.With, ast.AsyncWith, ast.For, ast.AsyncFor, ast.While)):
            _collect_imports(stmt.body, lazy=lazy, guarded=guarded, out=out)
            _collect_imports(getattr(stmt, "orelse", []), lazy=lazy, guarded=guarded, out=out)


def _is_test_file(py_file: Path, service_dir: Path) -> bool:
    relative = py_file.relative_to(service_dir)
    if py_file.name.startswith("test_") or py_file.name == "conftest.py":
        return True
    return any(part in {"tests", "test"} for part in relative.parts)


def _service_python_files(service_dir: Path, include_tests: bool) -> list[Path]:
    """Python-Dateien des Service, ohne Unterservices mit eigenem Manifest."""
    nested = {
        manifest.parent
        for manifest in service_dir.rglob("requirements.txt")
        if manifest.parent != service_dir
    }
    files: list[Path] = []
    for py_file in sorted(service_dir.rglob("*.py")):
        if any(part in {".venv", "venv", "node_modules", "__pycache__"} for part in py_file.parts):
            continue
        if any(nested_dir in py_file.parents for nested_dir in nested):
            continue
        if not include_tests and _is_test_file(py_file, service_dir):
            continue
        files.append(py_file)
    return files


def top_level_imports(service_dir: Path, include_tests: bool) -> dict[str, ImportSite]:
    """Importnamen des Service-Codes mit Beispieldatei, Optionalitaet und Ladezeitpunkt."""
    found: dict[str, ImportSite] = {}
    for py_file in _service_python_files(service_dir, include_tests):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue
        collected: list[tuple[ast.stmt, bool, bool]] = []
        _collect_imports(tree.body, lazy=False, guarded=False, out=collected)
        for node, lazy, guarded in collected:
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            else:
                if node.level:  # relativer Import, immer lokal
                    continue
                names = [node.module.split(".")[0]] if node.module else []
            for name in names:
                site = ImportSite(sample=py_file, optional=guarded, lazy=lazy)
                previous = found.get(name)
                # Der strengste Fundort gewinnt: Import-Zeit und ungeschuetzt schlaegt alles.
                if previous is None or _severity(site) > _severity(previous):
                    found[name] = site
    return found


def _severity(site: ImportSite) -> int:
    """2 = bricht den Start, 1 = still abgesichert, 0 = erst zur Laufzeit."""
    if site.lazy:
        return 0
    return 1 if site.optional else 2


def local_module_names(service_dir: Path) -> set[str]:
    names = set(LOCAL_PACKAGE_HINTS)
    for child in service_dir.iterdir():
        if child.is_dir() and not child.name.startswith("."):
            names.add(child.name)
        elif child.suffix == ".py":
            names.add(child.stem)
    return names


def repo_package_modules() -> set[str]:
    """Normalisierte Namen der Repo-internen Pakete unter ``packages/``."""
    packages_dir = REPO_ROOT / "packages"
    if not packages_dir.is_dir():
        return set()
    return {normalize(child.name) for child in packages_dir.iterdir() if child.is_dir()}


@dataclass
class Result:
    missing: list[tuple[str, ImportSite]] = field(default_factory=list)
    optional: list[tuple[str, ImportSite]] = field(default_factory=list)
    lazy: list[tuple[str, ImportSite]] = field(default_factory=list)
    repo_packages: list[tuple[str, ImportSite]] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not (self.missing or self.optional or self.lazy or self.repo_packages)


def check_service(requirements: Path, include_tests: bool) -> Result:
    service_dir = requirements.parent
    manifest = parse_requirements(requirements)
    provided = manifest.provided | modules_from_editable(service_dir, manifest.editable_paths)
    local = local_module_names(service_dir)
    stdlib = set(sys.stdlib_module_names)
    repo_packages = repo_package_modules()

    result = Result()
    for import_name, site in sorted(top_level_imports(service_dir, include_tests).items()):
        if import_name in stdlib or import_name in local or import_name.startswith("_"):
            continue
        candidates = {normalize(import_name)}
        mapped = IMPORT_TO_DISTRIBUTION.get(import_name)
        if mapped:
            candidates.add(normalize(mapped))
        if candidates & provided:
            continue
        if candidates & repo_packages:
            result.repo_packages.append((import_name, site))
        elif site.lazy:
            result.lazy.append((import_name, site))
        elif site.optional:
            result.optional.append((import_name, site))
        else:
            result.missing.append((import_name, site))
    return result


def _relative(path: Path) -> Path:
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("services", nargs="*", help="Service-Verzeichnisse (Default: alle unter services/)")
    parser.add_argument("--include-tests", action="store_true", help="Testcode mitpruefen")
    args = parser.parse_args()

    if args.services:
        manifests = [Path(s) / "requirements.txt" if Path(s).is_dir() else Path(s) for s in args.services]
    else:
        manifests = sorted((REPO_ROOT / "services").rglob("requirements.txt"))

    hard_failures = 0
    for manifest in manifests:
        if not manifest.exists():
            print(f"FEHLT   {manifest}")
            hard_failures += 1
            continue
        result = check_service(manifest, args.include_tests)
        relative = _relative(manifest)
        if result.clean:
            print(f"OK      {relative}")
            continue
        label = "LUECKE " if result.missing else "HINWEIS"
        print(f"{label} {relative}")
        if result.missing:
            hard_failures += 1
        for import_name, site in result.missing:
            hint = IMPORT_TO_DISTRIBUTION.get(import_name, import_name)
            print(f"        Pflicht-Import {import_name!r} ohne Pin (erwartet: {hint}) -- {_relative(site.sample)}")
        for import_name, site in result.optional:
            print(f"        optional: {import_name!r} nur in try/except -- stiller Funktionsverlust ({_relative(site.sample)})")
        for import_name, site in result.lazy:
            print(f"        lazy: {import_name!r} wird erst in einer Funktion importiert ({_relative(site.sample)})")
        for import_name, site in result.repo_packages:
            print(f"        Repo-Paket: {import_name!r} liegt unter packages/, aber nicht per -e verdrahtet ({_relative(site.sample)})")

    if hard_failures:
        print(f"\n{hard_failures} Manifest(e) mit fehlenden Pflicht-Pins.")
        return 1
    print(f"\n{len(manifests)} Manifest(e) geprueft, keine fehlenden Pflicht-Pins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
