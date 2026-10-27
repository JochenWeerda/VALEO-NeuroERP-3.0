"""Public data-quality views keep implementation-only rule fields private."""
from __future__ import annotations

from app.core.data_quality_rules import DQRuleSet


def dq_ruleset_public(ruleset: "DQRuleSet") -> dict:
    """Serialisiert ein DQRuleSet ohne interne Implementierungsdetails."""
    d = ruleset.as_dict()
    for regel in d.get("regeln", []):
        # format_regex und unique_felder sind Implementierungsdetails,
        # nicht fuer externe Konsumenten bestimmt.
        regel.pop("format_regex", None)
        regel.pop("unique_felder", None)
    return d
