"""CI drift contract for the frontend projection of authoritative document rights."""
from scripts.generate_beleg_permission_projection import OUT, render


def test_generated_document_permissions_match_current_domain_policy():
    assert OUT.read_text(encoding="utf-8") == render(), "Regenerate with scripts/generate_beleg_permission_projection.py"
