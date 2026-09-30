import pytest
import json

from scripts.check_baseline_integrity import compare, exemptions, flatten


def test_gleichzeitiges_anheben_von_code_und_baseline_bleibt_rot():
    assert compare({"a": 1001}, {"a": 1002}, "down")
    assert not compare({"a": 1002}, {"a": 1001}, "down")


def test_neue_und_verschobene_schuld_bleibt_rot():
    assert compare({"a": 1}, {"b": 1}, "down")
    assert not compare({"a": 1}, {}, "down")


def test_coverage_darf_nicht_sinken_oder_verschwinden():
    assert compare({"a": .8}, {"a": .7}, "up")
    assert compare({"a": .8}, {}, "up")
    assert not compare({"a": .8}, {"a": .9, "b": .7}, "up")


def test_business_time_zaehler_werden_pro_muster_geschuetzt():
    assert compare({"a": {"date.today": 1}}, {"a": {"datetime.now.date": 1}}, "down")


@pytest.mark.parametrize("value", [True, -1, float("nan"), float("inf"), "1", None, []])
def test_ungueltige_zaehler_sind_keine_baseline(value):
    with pytest.raises(ValueError):
        flatten({"a": value})


def test_ausnahmen_sind_explizit_und_lesbar():
    assert exemptions("EXEMPT_FILES: set[str] = {'a.py'}") == {"a.py"}
    with pytest.raises(ValueError):
        exemptions("EXEMPT_FILES = get_exemptions()")


@pytest.mark.parametrize("thresholds", [None, {}, {"services/foo.py": .7}])
def test_coverage_gate_verlangt_vollstaendige_aktuelle_baseline(tmp_path, monkeypatch, thresholds):
    from scripts import check_critical_backend_coverage as coverage
    xml = tmp_path / "coverage.xml"
    xml.write_text('<coverage><class filename="services/foo.py" line-rate="1"/></coverage>', encoding="utf-8")
    monkeypatch.setattr(coverage, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(coverage, "COVERAGE_XML", xml)
    monkeypatch.setattr(coverage, "CRITICAL_THRESHOLDS", {"services/foo.py": .8})
    if thresholds is not None:
        folder = tmp_path / "config"
        folder.mkdir()
        (folder / "coverage_ratchet_baseline.json").write_text(json.dumps({"thresholds": thresholds}), encoding="utf-8")
    with pytest.raises(SystemExit):
        coverage.main()
