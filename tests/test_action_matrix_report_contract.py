from __future__ import annotations

import sys

import pytest
import yaml

from scripts import generate_action_matrix_report as report


def matrix(action_id='o2c-001', status='green'):
    return {'chain_id': 'o2c', 'chain_name': 'Auftrag', 'actions': [
        {'action_id': action_id, 'label': 'Anlegen', 'route_prefix': 'verkauf/auftrag', 'status': status, 'e2e_tag': '@critical'},
    ]}


def write_matrix(path, data):
    path.write_text(yaml.safe_dump(data), encoding='utf-8')


def test_deklaration_und_tag_sind_kein_laufnachweis(monkeypatch):
    monkeypatch.setattr(report, 'load_top50_prefixes', lambda: [])
    result = report.build_report([matrix()], set())
    md = report.build_markdown(result)
    assert result['green'] == 1
    assert 'Deklariert green (kein Laufnachweis)' in md
    assert 'Fuer keine Aktion ist hier ein konkreter' in md
    assert 'Testlauf mit Commit-SHA verknuepft' in md
    assert 'E2E @critical/@smoke grün' not in md


@pytest.mark.parametrize('invalid', ['passed', 'GREEN', '', None])
def test_unbekannter_status_faellt_hart(tmp_path, monkeypatch, invalid):
    monkeypatch.setattr(report, 'MATRIX_DIR', tmp_path)
    write_matrix(tmp_path / 'a.yaml', matrix(status=invalid))
    with pytest.raises(ValueError, match='ungueltiger Status'):
        report.load_matrices()


def test_doppelte_id_ueber_dateigrenzen_faellt_hart(tmp_path, monkeypatch):
    monkeypatch.setattr(report, 'MATRIX_DIR', tmp_path)
    write_matrix(tmp_path / 'a.yaml', matrix())
    write_matrix(tmp_path / 'b.yaml', matrix())
    with pytest.raises(ValueError, match='doppelte action_id o2c-001'):
        report.load_matrices()


@pytest.mark.parametrize('contents', ['chain_id: [', 'null', 'chain_id: o2c\nchain_name: X\nactions: []'])
def test_parse_und_strukturfehler_werden_nicht_uebersprungen(tmp_path, monkeypatch, contents):
    monkeypatch.setattr(report, 'MATRIX_DIR', tmp_path)
    (tmp_path / 'a.yaml').write_text(contents, encoding='utf-8')
    with pytest.raises(ValueError):
        report.load_matrices()


def test_check_scheitert_bei_fehlerhafter_datei(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(report, 'MATRIX_DIR', tmp_path)
    monkeypatch.setattr(sys, 'argv', ['report', '--check'])
    (tmp_path / 'broken.yaml').write_text('chain_id: [', encoding='utf-8')
    assert report.main() == 1
    assert 'FEHLER:' in capsys.readouterr().err


def test_check_erkennt_report_drift(tmp_path, monkeypatch):
    monkeypatch.setattr(report, 'MATRIX_DIR', tmp_path)
    monkeypatch.setattr(report, 'OUTPUT_MD', tmp_path / 'report.md')
    monkeypatch.setattr(report, 'load_top50_prefixes', lambda: [])
    monkeypatch.setattr(report, 'load_route_prefixes', lambda: set())
    monkeypatch.setattr(sys, 'argv', ['report', '--check'])
    write_matrix(tmp_path / 'a.yaml', matrix())
    report.OUTPUT_MD.write_text('veralteter Bericht', encoding='utf-8')
    assert report.main() == 1
