from pathlib import Path

import pytest

from scripts.check_pagination import collect, ratchet_errors, scan_source


@pytest.mark.parametrize("source, expected", [
    ("def f(limit=10):\n return q.all()", 1),
    ("def f():\n return q.offset(10).all()", 1),
    ("def f():\n return q.limit(10).all()", 0),
    ("def f():\n return q.limit(None).all()", 1),
    ("def f():\n return q.limit(10).limit(None).all()", 1),
    ("def f():\n q2 = q.limit(10)\n return q2.all()", 0),
    ("def f():\n q2 = q.limit(10)\n q2 = q\n return q2.all()", 1),
    ("def f():\n stmt = q.limit(10)\n return db.execute(stmt).scalars().all()", 0),
    ("def f():\n q.limit(10)\n return q.all()", 1),
    ("def f():\n return q.limit(10).all()\ndef g():\n return q.all()", 1),
    ("def f():\n a=q.limit(10)\n return q.all(), a.all()", 1),
    ("def f():\n a=q\n if flag:\n  a=a.limit(10)\n return a.all()", 1),
    ("def f():\n if flag:\n  a=q.limit(10)\n else:\n  a=q.limit(20)\n return a.all()", 0),
    ("def f():\n a=q\n for x in xs:\n  a=q.limit(10)\n return a.all()", 1),
    ("def f():\n a=q.limit(10)\n for x in xs:\n  a=q\n return a.all()", 1),
    ("def f():\n a=q\n try:\n  a=q.limit(10)\n except Exception:\n  pass\n return a.all()", 1),
    ("# q.all()\ns='q.all()'", 0),
    ("\ufeffdef f():\n return q.all()", 1),
    ("def f():\n a=q.limit(10)\n a,b=get_queries()\n return a.all()", 1),
    ("def f():\n a=q.limit(10)\n (a:=q)\n return a.all()", 1),
    ("def f():\n a=q.limit(10)\n callback=lambda:a.all()\n a=q", 1),
    ("def f():\n a=q\n match flag:\n  case 1:\n   a=q.limit(10)\n return a.all()", 1),
])
def test_abfragegrenze_statt_dateiweiter_parameter(source, expected):
    assert len(scan_source(source)) == expected


def test_funktionsverschiebung_und_abbau():
    assert ratchet_errors({"b::f": 1}, {"a::f": 1}) == [
        "BASELINE SENKEN: a::f: 1 -> 0", "NEU/GEWACHSEN: b::f: 0 -> 1"
    ]


def test_unlesbarer_code_wird_nicht_als_sauber_gemeldet(tmp_path: Path):
    folder = tmp_path / "app/api/v1/endpoints"
    folder.mkdir(parents=True)
    (folder / "broken.py").write_text("def broken(", encoding="utf-8")
    with pytest.raises(SyntaxError):
        collect(tmp_path)
