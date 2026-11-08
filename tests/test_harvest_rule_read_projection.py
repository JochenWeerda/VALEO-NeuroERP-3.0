"""Displayed columns are a readonly projection of the authoritative rule."""
from app.api.v1.endpoints.harvest_rules import RuleVersionOut
from app.core.screen_definitions_harvest_controls import build_harvest_controls
from modules.agrar.contracts.harvest_deductions_v1 import HarvestDeductionRuleV1


def rule():
    return HarvestDeductionRuleV1(rule_id='synthetic-read-projection', rule_version=2,
        tenant_id='synthetic-tenant', customer_id='synthetic-customer', article_id='synthetic-article',
        valid_from='2026-10-01', valid_until='2026-10-31', source_reference='Synthetic contract',
        measurement_method='synthetic-lab', measurement_method_version='1',
        impurities_free_pct='0', quality_limit_pct=None)


def test_every_display_column_exists_in_actual_serialized_response_and_schema():
    definition=rule()
    output=RuleVersionOut(id='synthetic-version',definition=definition,content_hash=definition.content_hash,
        created_by='verified-actor',status='draft')
    serialized=output.model_dump(mode='json')
    schema=RuleVersionOut.model_json_schema(mode='serialization')
    table=build_harvest_controls()['tabs'][0]['tables'][0]
    for column in table['columns']:
        assert column['key'] in serialized
        assert column['key'] in schema['properties']
    assert serialized['impurities_free_pct']=='0'
    assert serialized['quality_limit_pct'] is None
    assert serialized['definition']==definition.model_dump(mode='json')
    assert output.definition.content_hash==definition.content_hash


def test_supplied_flat_values_cannot_override_the_immutable_definition():
    definition=rule()
    output=RuleVersionOut.model_validate(dict(id='synthetic-version',definition=definition,
        content_hash=definition.content_hash,created_by='verified-actor',status='draft',
        rule_id='forged',rule_version=999,impurities_free_pct='100',source_reference='forged'))
    actual=output.model_dump(mode='json')
    for field in ['rule_id','rule_version','impurities_free_pct','source_reference']:
        assert actual[field]==actual['definition'][field]
        assert RuleVersionOut.model_json_schema(mode='serialization')['properties'][field]['readOnly'] is True
    assert 'rule_id' not in RuleVersionOut.model_json_schema(mode='validation')['properties']
