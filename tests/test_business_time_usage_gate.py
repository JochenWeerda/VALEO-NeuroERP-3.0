from pathlib import Path

from scripts.check_business_time_usage import (
    compare_counts,
    counts_for,
    scan_file,
)


def _scan(tmp_path: Path, source: str):
    app = tmp_path / "app"
    app.mkdir()
    path = app / "sample.py"
    path.write_text(source, encoding="utf-8")
    return scan_file(path, root=tmp_path)


def test_detects_direct_calendar_sources_with_aliases(tmp_path: Path) -> None:
    findings = _scan(
        tmp_path,
        """
import datetime as dt
from datetime import date as _date
from datetime import datetime as Clock

a = _date.today()
b = dt.date.today()
c = Clock.now().date()
d = dt.datetime.now(dt.timezone.utc).date()
e = Clock.utcnow().date()
f = dt.datetime.today().date()
""",
    )

    assert [item.kind for item in findings] == [
        "date.today",
        "date.today",
        "datetime.now.date",
        "datetime.now.date",
        "datetime.utcnow.date",
        "datetime.today.date",
    ]


def test_ignores_business_time_and_unrelated_date_calls(tmp_path: Path) -> None:
    findings = _scan(
        tmp_path,
        """
from app.core.business_time import business_date_at, business_today

today = business_today()
weighing_day = business_date_at(timestamp)
parsed = timestamp.date()
""",
    )

    assert findings == []


def test_counts_are_path_and_pattern_specific(tmp_path: Path) -> None:
    findings = _scan(
        tmp_path,
        """
from datetime import date, datetime

a = date.today()
b = date.today()
c = datetime.utcnow().date()
""",
    )

    assert counts_for(findings) == {
        "app/sample.py": {"date.today": 2, "datetime.utcnow.date": 1}
    }


def test_ratchet_rejects_new_and_moved_findings() -> None:
    baseline = {"app/a.py": {"date.today": 1}}
    current = {
        "app/a.py": {"date.today": 1},
        "app/b.py": {"date.today": 1},
    }

    increased, reduced = compare_counts(current, baseline)

    assert increased == {"app/b.py|date.today": 1}
    assert reduced == {}


def test_ratchet_requires_baseline_update_after_reduction() -> None:
    baseline = {"app/a.py": {"date.today": 2, "datetime.now.date": 1}}
    current = {"app/a.py": {"date.today": 1}}

    increased, reduced = compare_counts(current, baseline)

    assert increased == {}
    assert reduced == {
        "app/a.py|date.today": 1,
        "app/a.py|datetime.now.date": 1,
    }
