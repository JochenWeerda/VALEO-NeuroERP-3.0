import copy
from datetime import date
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
from unittest.mock import patch

import audit_service_dependencies

from security_dependency_gate import evaluate, fingerprint


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="valeo-policy-")
        self.root = Path(self.tmp.name)
        self.source = self.root / "services/ai/app/services/vector_store.py"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("client = chromadb.PersistentClient(path='data')\n")
        self.manifest = "services/ai/requirements.txt"
        self.report = {"dependencies": [{"name": "chromadb", "version": "0.5.23", "vulns": [
            {"id": "PYSEC-test", "aliases": ["CVE-2026-45833"], "fix_versions": []}]}]}
        self.policy = {"schema_version": 1, "decisions": [{"manifest": self.manifest,
            "package": "chromadb", "version": "0.5.23", "advisory": "CVE-2026-45833",
            "decision": "not_affected", "exploitability": "unreachable", "owner": "reviewer",
            "reason": "Server not deployed", "sources": ["https://example.test/advisory"],
            "reviewed_on": "2026-09-15", "review_by": "2026-10-15",
            "control": "chroma_embedded_only", "evidence_sha256": fingerprint(self.root)}]}

    def tearDown(self):
        self.tmp.cleanup()

    def evaluate(self):
        return evaluate(self.report, self.manifest, self.policy, self.root, date(2026, 9, 15))

    def test_reviewed_unreachable_finding_passes_and_remains_visible(self):
        before = copy.deepcopy(self.report)
        result = self.evaluate()
        self.assertTrue(result["release_allowed"])
        self.assertEqual(result["not_affected"], 1)
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(before, self.report)

    def test_unknown_finding_blocks(self):
        self.report["dependencies"][0]["vulns"].append({"id": "NEW-CRITICAL"})
        self.assertFalse(self.evaluate()["release_allowed"])

    def test_expiry_and_reachable_cannot_be_accepted(self):
        for key, value in (("review_by", "2026-09-15"), ("exploitability", "reachable"),
                           ("decision", "accepted_risk"), ("owner", ""), ("sources", []),
                           ("reviewed_on", "2026-09-16")):
            with self.subTest(key=key):
                old = self.policy["decisions"][0][key]
                self.policy["decisions"][0][key] = value
                self.assertFalse(self.evaluate()["release_allowed"])
                self.policy["decisions"][0][key] = old

    def test_changed_and_added_source_invalidates_review(self):
        self.source.write_text(self.source.read_text() + "# changed\n")
        self.assertFalse(self.evaluate()["release_allowed"])
        self.policy["decisions"][0]["evidence_sha256"] = fingerprint(self.root)
        (self.source.parent / "new_module.py").write_text("pass\n")
        self.assertFalse(self.evaluate()["release_allowed"])

    def test_server_control_blocks_even_with_refreshed_hash(self):
        self.source.write_text("client = chromadb.PersistentClient(); chromadb.HttpClient()\n")
        self.policy["decisions"][0]["evidence_sha256"] = fingerprint(self.root)
        self.assertFalse(self.evaluate()["release_allowed"])

    def test_exact_version_and_service_binding(self):
        self.report["dependencies"][0]["version"] = "0.5.24"
        self.assertFalse(self.evaluate()["release_allowed"])
        self.report["dependencies"][0]["version"] = "0.5.23"
        self.manifest = "services/another/requirements.txt"
        self.assertFalse(self.evaluate()["release_allowed"])

    def test_missing_inventory_and_skipped_packages_fail(self):
        for data in ({}, {"dependencies": []}, {"dependencies": [{"name": "x", "skip_reason": "unknown"}]}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                evaluate(data, self.manifest, self.policy, self.root)

    def test_runner_preserves_raw_failure_and_applies_review(self):
        manifest = self.root / self.manifest
        manifest.write_text("chromadb==0.5.23\n")
        self.policy["decisions"][0]["evidence_sha256"] = fingerprint(self.root)
        policy_path = self.root / "config/security/dependency-decisions.json"
        policy_path.parent.mkdir(parents=True)
        policy_path.write_text(json.dumps(self.policy))
        def scanner(command, **kwargs):
            Path(command[-1]).write_text(json.dumps(self.report))
            return subprocess.CompletedProcess(command, 1)
        output = self.root / "output"
        with patch("audit_service_dependencies.ROOT", self.root), patch("audit_service_dependencies.subprocess.run", side_effect=scanner), patch("security_dependency_gate.date") as clock:
            clock.today.return_value = date(2026, 9, 15)
            clock.fromisoformat.side_effect = date.fromisoformat
            self.assertEqual(audit_service_dependencies.audit(manifest, output), 0)
        self.assertEqual(json.loads((output / "status.json").read_text())["scanner_exit_code"], 1)
        self.assertEqual(json.loads((output / "pip-audit.json").read_text()), self.report)

    def test_duplicate_decisions_fail(self):
        self.policy["decisions"].append(copy.deepcopy(self.policy["decisions"][0]))
        self.assertFalse(self.evaluate()["release_allowed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
