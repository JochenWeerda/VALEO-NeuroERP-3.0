"""Both independent deliveries remain reachable through one migration head."""
from pathlib import Path
import unittest
from alembic.script import ScriptDirectory

class MigrationMergeContract(unittest.TestCase):
    def test_hr_and_tax_reachable_without_rewriting_applied_revisions(self):
        scripts=ScriptDirectory(str(Path(__file__).resolve().parents[1]/"alembic"))
        self.assertEqual(scripts.get_heads(),["merge_hr_tax_20261019"])
        merge=scripts.get_revision("merge_hr_tax_20261019")
        self.assertEqual(set(merge.down_revision),{"hr_employee_files_20261019","tax_account_category_20261019"})
        for branch in merge.down_revision:
            self.assertEqual(scripts.get_revision(branch).down_revision,"harvest_rule_store_20261015")
        for branch in merge.down_revision:
            self.assertIn(branch,{step.revision for step in scripts.walk_revisions()})
