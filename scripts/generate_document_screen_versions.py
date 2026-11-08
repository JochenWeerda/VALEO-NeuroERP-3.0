"""Append explicit document-mask releases or check the current builder projection."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.document_screen_versions import REGISTRY_PATH, check_registry, extend_registry, resolve_variant
from app.core.screen_definitions_beleg import BELEGARTEN, build_beleg_screen_definition


def current_matches(registry, definitions):
    check_registry(registry)
    if set(registry["current"]) != set(definitions):
        return False
    for key, expected in definitions.items():
        actual = resolve_variant(registry, key)
        actual.pop("documentVariant")
        if actual != expected:
            return False
    return True


def write_release(path, definitions, version):
    """Serialize writers and replace the complete file atomically, including on Windows."""
    lock = path.with_suffix(".lock")
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError("document_screen_release_busy") from error
    pending = None
    try:
        previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        result = extend_registry(definitions, version, previous)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent,
                                         prefix="document-screen-versions-", suffix=".tmp", delete=False) as target:
            pending = Path(target.name)
            json.dump(result, target, ensure_ascii=False, sort_keys=True, indent=2)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(pending, path)
        pending = None
        return result
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)
        os.close(handle)
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--release-version")
    args = parser.parse_args()
    if bool(args.check) == bool(args.release_version):
        parser.error("Choose --check or an explicit --release-version")
    definitions = {key: build_beleg_screen_definition(key) for key in BELEGARTEN}
    if args.check:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")) if REGISTRY_PATH.exists() else None
        if registry is None or not current_matches(registry, definitions):
            parser.exit(1, "Document mask versions differ from the canonical builder.\n")
        print(f"Document mask versions synchronized: {len(definitions)} variants")
        return 0
    write_release(REGISTRY_PATH, definitions, args.release_version)
    print(f"Appended document mask release {args.release_version}: {len(definitions)} variants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
