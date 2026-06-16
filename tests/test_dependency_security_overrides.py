import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
STUDIO = json.loads(
    (
        ROOT
        / "packages"
        / "agrar-silo-materialfluss-studio"
        / "package.json"
    ).read_text(encoding="utf-8")
)


def test_security_overrides_pin_patched_high_advisory_ranges():
    overrides = PACKAGE["pnpm"]["overrides"]

    assert overrides["esbuild"] == "^0.28.1"
    assert overrides["ws"] == "^8.21.0"
    assert overrides["form-data"] == "^4.0.6"


def test_agrar_studio_uses_patched_esbuild_line():
    assert STUDIO["devDependencies"]["esbuild"] == "^0.28.1"
