"""Rollenbeschreibungen sind pflichtige, erhaltene Pruefvertraege."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("role_contract_check", ROOT / "scripts/check_fachrollen.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class RoleDescriptionContracts(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(check.KATALOG.read_text(encoding="utf8"))
        self.realm = json.loads(check.REALM.read_text(encoding="utf8"))

    def test_every_catalog_and_realm_role_has_contract(self):
        self.assertEqual(check.vertragsfehler(self.catalog, self.realm), [])

    def test_all_domain_roles_exist_in_realm_without_assignments(self):
        names = {r["name"] for r in self.realm["roles"]["realm"]}
        self.assertTrue({r["name"] for r in self.catalog["rollen"]} <= names)

    def test_missing_or_blank_contract_field_denies(self):
        for field in check.VERTRAGSFELDER:
            for value in (None, "", "   ", []):
                with self.subTest(field=field, value=value):
                    changed = copy.deepcopy(self.catalog)
                    changed["rollen"][0]["vertrag"][field] = value
                    self.assertTrue(check.vertragsfehler(changed, self.realm))

    def test_new_realm_role_needs_explicit_contract(self):
        self.realm["roles"]["realm"].append({"name": "unreviewed_role"})
        self.assertTrue(check.vertragsfehler(self.catalog, self.realm))

    def test_duplicate_name_denies(self):
        self.catalog["grundrollen"].append(copy.deepcopy(self.catalog["rollen"][0]))
        self.assertTrue(check.vertragsfehler(self.catalog, self.realm))

    def test_generator_preserves_reviewed_contract(self):
        self.catalog["rollen"][0]["vertrag"]["erlaubt"] = "Individuell begrenzter Auftrag"
        generated = check.katalog_aus_code(self.catalog)
        self.assertEqual(generated["rollen"][0]["vertrag"], self.catalog["rollen"][0]["vertrag"])
        self.assertEqual(generated["grundrollen"], self.catalog["grundrollen"])

    def test_new_code_role_without_contract_is_not_auto_approved(self):
        original = check.rollen_im_code
        try:
            check.rollen_im_code = lambda: {"NEU_BEARBEITEN": ["synthetic.py"]}
            generated = check.katalog_aus_code(self.catalog)
            self.assertTrue(check.vertragsfehler(generated))
        finally:
            check.rollen_im_code = original

    def test_missing_contract_or_description_denies(self):
        for field in ("vertrag", "beschreibung"):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.catalog)
                changed["rollen"][0].pop(field)
                self.assertTrue(check.vertragsfehler(changed))
