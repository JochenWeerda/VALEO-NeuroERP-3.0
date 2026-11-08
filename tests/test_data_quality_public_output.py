"""The public endpoint must never publish internal regex or uniqueness configuration."""
import pytest
from app.api.v1.endpoints.process_kernel_api import get_dq_rulesets
from app.core.data_quality_rules import get_default_dq_rulesets


@pytest.mark.parametrize("entity", sorted(get_default_dq_rulesets()))
def test_public_rules_preserve_business_fields_and_hide_implementation(entity):
    source = get_default_dq_rulesets()[entity].as_dict()
    public = get_dq_rulesets()["rulesets"][entity]
    assert public["entity_typ"] == source["entity_typ"]
    assert len(public["regeln"]) == len(source["regeln"])
    assert all("format_regex" not in rule and "unique_felder" not in rule for rule in public["regeln"])
    assert get_default_dq_rulesets()[entity].as_dict() == source
