import json
from pathlib import Path

import pytest

from scripts import run_improvement_pipelines as pipeline
from scripts.verify_quality_evidence import verify, write


def test_runner_fuehrt_erfolg_und_fehler_getrennt_aus(tmp_path: Path):
    (tmp_path / "ok.py").write_text("print('ok')", encoding="utf-8")
    (tmp_path / "bad.py").write_text("raise SystemExit(7)", encoding="utf-8")
    ok = pipeline.run_check("ok", ["ok.py"], tmp_path, 5)
    bad = pipeline.run_check("bad", ["bad.py"], tmp_path, 5)
    assert ok["status"] == "passed"
    assert bad["status"] == "failed" and bad["exit_code"] == 7


def test_timeout_wird_nicht_als_erfolg_verbucht(tmp_path: Path):
    (tmp_path / "slow.py").write_text("import time; time.sleep(10)", encoding="utf-8")
    assert pipeline.run_check("slow", ["slow.py"], tmp_path, .1)["status"] == "timeout"


def test_rohausgaben_werden_nicht_in_berichte_kopiert(tmp_path: Path):
    (tmp_path / "output.py").write_text("print('sensitive-test-value')", encoding="utf-8")
    result = pipeline.run_check("output", ["output.py"], tmp_path, 5)
    assert "sensitive-test-value" not in json.dumps(result)
    assert len(result["output_sha256"]) == 64


def test_ein_roter_check_verdeckt_keine_anderen(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(pipeline, "CHECKS", {"a": [], "b": []})
    monkeypatch.setattr(pipeline, "snapshot", lambda root: {"sha": "a", "dirty": False})
    monkeypatch.setattr(pipeline, "run_check", lambda name, *_args: {
        "name": name, "status": "failed" if name == "a" else "passed"
    })
    report = pipeline.run(tmp_path, 2, 5)
    assert report["status"] == "failed"
    assert {c["name"] for c in report["checks"]} == {"a", "b"}


def test_wechselnder_arbeitsbaum_ist_keine_gueltige_messung(monkeypatch, tmp_path: Path):
    snapshots = iter([{"sha": "a"}, {"sha": "b"}])
    monkeypatch.setattr(pipeline, "snapshot", lambda root: next(snapshots))
    monkeypatch.setattr(pipeline, "CHECKS", {})
    report = pipeline.run(tmp_path, 1, 5)
    assert report["status"] == "failed" and not report["snapshot_stable"]


def test_nachweis_prueft_commit_und_inhalt(tmp_path: Path):
    path = tmp_path / "coverage.xml"
    path.write_text("<coverage/>", encoding="utf-8")
    write(path, "a" * 40)
    verify(path, "a" * 40)
    with pytest.raises(ValueError):
        verify(path, "b" * 40)
    path.write_text("<changed/>", encoding="utf-8")
    with pytest.raises(ValueError):
        verify(path, "a" * 40)


def test_fehlende_oder_leere_coverage_hat_keinen_nachweis(tmp_path: Path):
    with pytest.raises(ValueError):
        write(tmp_path / "missing", "a" * 40)
    empty = tmp_path / "empty"
    empty.touch()
    with pytest.raises(ValueError):
        write(empty, "a" * 40)
