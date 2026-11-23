import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/ci/zap_baseline.sh"


@pytest.mark.parametrize(
    ("status", "report", "success"),
    [
        (0, {"site": [{"alerts": []}]}, True),
        (2, {"site": [{"alerts": [{"riskcode": "1"}]}]}, True),
        (1, {"site": [{"alerts": [{"riskcode": "1"}]}]}, False),
        (3, {"site": [{"alerts": []}]}, False),
        (2, {"site": [{"alerts": [{"riskcode": "2"}]}]}, False),
        (0, {"site": [{"alerts": [{"riskcode": "3"}]}]}, False),
        (0, {"site": []}, False),
        (0, {"site": [None]}, False),
        (0, {"site": [{}]}, False),
        (0, {"site": [{"alerts": [{"riskcode": "invalid"}]}]}, False),
        (0, "{", False),
        (0, None, False),
    ],
)
def test_scanner_result_and_report(tmp_path, status, report, success):
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    bash = str(git_bash) if os.name == "nt" and git_bash.exists() else shutil.which("bash")
    assert bash, "bash is required"
    (tmp_path / ".zap").mkdir()
    (tmp_path / ".zap/rules.tsv").write_text("rule\n")
    mock_bin = tmp_path / "bin"
    mock_bin.mkdir()
    docker = mock_bin / "docker"
    docker.write_text(
        '#!/usr/bin/env bash\n'
        'while [ "$1" != "-v" ]; do shift; done\n'
        'mount=$2; dir=${mount%%:/zap/wrk:rw}\n'
        'test "$dir" != "$PWD" || exit 9\n'
        'cmp "$dir/rules.tsv" .zap/rules.tsv || exit 9\n'
        'printf "%s" "$dir" > "$PWD/mount-path"\n'
        'if [ "$MOCK_REPORT" != MISSING ]; then printf "%s" "$MOCK_REPORT" > "$dir/report_json.json"; fi\n'
        'exit "$MOCK_STATUS"\n', encoding="utf-8")
    docker.chmod(0o755)
    env = dict(os.environ, PATH=f"{mock_bin}{os.pathsep}{os.environ['PATH']}",
               MOCK_STATUS=str(status), MOCK_REPORT="MISSING" if report is None else
               report if isinstance(report, str) else json.dumps(report))
    result = subprocess.run([bash, str(SCRIPT)], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert (tmp_path / "mount-path").exists(), result.stdout + result.stderr
    cleanup = subprocess.run([bash, "-c", 'test ! -e "$(cat mount-path)"'], cwd=tmp_path, env=env, timeout=15)
    assert cleanup.returncode == 0
    assert (result.returncode == 0) is success, result.stdout + result.stderr
