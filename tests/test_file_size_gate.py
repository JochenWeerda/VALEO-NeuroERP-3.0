from pathlib import Path

from scripts.check_file_size import collect_godfiles, load_baseline, ratchet_errors, write_baseline


def _write(root: Path, name: str, lines: int) -> None:
    path = root / "app/api/v1/endpoints" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x\n" * lines, encoding="utf-8")


def test_exakte_baseline_ist_gruen(tmp_path: Path) -> None:
    _write(tmp_path, "gross.py", 1001)
    current = collect_godfiles(tmp_path)
    assert ratchet_errors(current, current) == []


def test_neues_godfile_wird_blockiert(tmp_path: Path) -> None:
    _write(tmp_path, "neu.py", 1001)
    assert ratchet_errors(collect_godfiles(tmp_path), {}) == [
        "NEU: app/api/v1/endpoints/neu.py (1001 Zeilen)"
    ]


def test_verschieben_wird_als_neu_und_abgebaut_erkannt(tmp_path: Path) -> None:
    _write(tmp_path, "neu.py", 1001)
    errors = ratchet_errors(
        collect_godfiles(tmp_path),
        {"app/api/v1/endpoints/alt.py": 1001},
    )
    assert errors == [
        "NEU: app/api/v1/endpoints/neu.py (1001 Zeilen)",
        "BASELINE SENKEN: app/api/v1/endpoints/alt.py ist kein Godfile mehr",
    ]


def test_wachstum_und_abbau_verlangen_exakte_baseline() -> None:
    path = "app/api/v1/endpoints/gross.py"
    assert ratchet_errors({path: 1002}, {path: 1001}) == [
        f"GEWACHSEN: {path} 1001 -> 1002 Zeilen"
    ]
    assert ratchet_errors({path: 1001}, {path: 1002}) == [
        f"BASELINE SENKEN: {path} 1002 -> 1001 Zeilen"
    ]


def test_baseline_update_schreibt_sortierten_bestand(tmp_path: Path) -> None:
    baseline = tmp_path / "config/godfile_baseline.json"
    files = {"z.py": 1200, "a.py": 1001}
    write_baseline(baseline, files)
    assert load_baseline(baseline) == {"a.py": 1001, "z.py": 1200}
