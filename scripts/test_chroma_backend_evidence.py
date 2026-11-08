"""The second embedded consumer must not escape the dependency review."""
import copy

import test_security_dependency_gate as base
from security_dependency_gate import fingerprint


class BackendEvidenceTests(base.GateTests):
    def setUp(self):
        super().setUp()
        self.backend = self.root / "app/infrastructure/rag/vector_store.py"
        self.backend.parent.mkdir(parents=True)
        self.backend.write_text("client = chromadb.Client()\n")
        self.policy["decisions"][0]["evidence_sha256"] = fingerprint(self.root)

    def test_backend_changes_invalidate_review(self):
        self.assertTrue(self.evaluate()["release_allowed"])
        self.backend.write_text("client = chromadb.Client()  # changed\n")
        self.assertFalse(self.evaluate()["release_allowed"])

    def test_backend_server_modes_block_even_after_hash_refresh(self):
        original = copy.deepcopy(self.policy)
        for forbidden in ("HttpClient()", "AsyncHttpClient()", "trust_remote_code=True",
                          "SimpleRBACAuthorizationProvider", "chroma_server_host='remote'"):
            with self.subTest(forbidden=forbidden):
                self.policy = copy.deepcopy(original)
                self.backend.write_text("client = chromadb.Client(); " + forbidden + "\n")
                self.policy["decisions"][0]["evidence_sha256"] = fingerprint(self.root)
                self.assertFalse(self.evaluate()["release_allowed"])

    def test_backend_removal_invalidates_review(self):
        self.backend.unlink()
        self.assertFalse(self.evaluate()["release_allowed"])
