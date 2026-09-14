"""Regression tests for coverage and fail-closed service audit behavior."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from audit_service_dependencies import audit, discover, matrix


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="valeo-audit-test-")
        self.root = Path(self.temp.name)
        self.manifest = self.root / "services/finance/core/requirements.txt"
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_text("example==1.0\n")
        self.out = self.root / "out"

    def tearDown(self):
        self.temp.cleanup()

    def test_nested_and_new_manifests_are_discovered(self):
        added = self.root / "services/new/requirements.txt"
        added.parent.mkdir()
        added.write_text("example==1.0\n")
        self.assertEqual(len(discover(self.root)), 2)
        self.assertIn({"manifest": "services/finance/core/requirements.txt", "service": "finance--core"}, matrix(self.root)["include"])

    def test_empty_discovery_fails(self):
        with self.assertRaises(ValueError):
            discover(self.root / "absent")

    def run_fake(self, code=0, data=None):
        def fake(command, **kwargs):
            self.assertEqual(kwargs["cwd"], self.manifest.parent)
            self.assertIn("--strict", command)
            self.assertNotIn("--no-deps", command)
            self.assertNotIn("--ignore-vuln", command)
            if data is not None:
                Path(command[-1]).write_text(json.dumps(data))
            return subprocess.CompletedProcess(command, code)
        with patch("audit_service_dependencies.subprocess.run", side_effect=fake):
            return audit(self.manifest, self.out)

    def test_complete_clean_report_passes(self):
        self.assertEqual(self.run_fake(data={"dependencies": [{"name": "example", "version": "1.0", "vulns": []}]}), 0)

    def test_vulnerabilities_fail_and_keep_report(self):
        self.assertNotEqual(self.run_fake(1, {"dependencies": [{"vulns": [{"id": "TEST"}]}]}), 0)
        self.assertTrue((self.out / "pip-audit.json").is_file())

    def test_success_without_report_fails_and_removes_stale_result(self):
        self.out.mkdir()
        (self.out / "pip-audit.json").write_text('{"dependencies": [{"vulns": []}]}')
        self.assertNotEqual(self.run_fake(), 0)
        self.assertFalse((self.out / "pip-audit.json").exists())

    def test_skipped_or_empty_collection_fails(self):
        for dependencies in ([], [{"skip_reason": "unknown package"}], [{"vulns": [{"id": "TEST"}]}]):
            with self.subTest(dependencies=dependencies):
                self.assertNotEqual(self.run_fake(data={"dependencies": dependencies}), 0)

    def test_timeout_and_launch_error_fail(self):
        for error in (subprocess.TimeoutExpired("audit", 1), OSError("not found")):
            with self.subTest(error=type(error).__name__):
                with patch("audit_service_dependencies.subprocess.run", side_effect=error):
                    self.assertNotEqual(audit(self.manifest, self.out), 0)
                self.assertNotEqual(json.loads((self.out / "status.json").read_text())["exit_code"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
