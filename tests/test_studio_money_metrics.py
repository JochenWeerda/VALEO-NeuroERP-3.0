from decimal import Decimal
import pytest
from fastapi import HTTPException
from app.services.list_experience_metrics import list_metrics
from app.services.studio_list_contracts import validate_list_experience

META={"searchFields":["name"],"aggregates":[{"key":"balance","label":"Saldo","kind":"sum","field":"amount","format":"currency","conditions":[]}],"export":{"filenamePrefix":"money","delimiter":";","columns":[{"key":"amount","label":"Betrag"}]}}

def definition(meta):
    return {"mode":"list","listExperience":meta,"tables":[{"columns":[{"key":"name"},{"key":"amount"}]}]}

def test_exact_decimal_metrics_match_the_browser_contract():
    assert list_metrics(META,[{"amount":"0.10"},{"amount":Decimal("0.20")},{"amount":"-0.01"}])=={"balance":0.29}
    assert validate_list_experience(definition(META))==[]

@pytest.mark.parametrize("value",[None,True,"0.001","NaN","1e2","900719925474.01"])
def test_unsafe_financial_summaries_fail_closed(value):
    with pytest.raises(HTTPException) as error: list_metrics(META,[{"amount":value}])
    assert error.value.status_code==409

@pytest.mark.parametrize("change",[{"kind":"sum","field":None},{"kind":"sum","field":"secret"},{"kind":"count","field":"amount"},{"kind":"count","field":None,"format":"currency"},{"kind":"average"}])
def test_aggregate_shape_and_declared_fields_cannot_be_bypassed(change):
    from copy import deepcopy
    meta=deepcopy(META);meta["aggregates"][0].update(change)
    assert validate_list_experience(definition(meta))


def test_currency_receipt_and_mixed_currency_do_not_manufacture_a_total():
    from copy import deepcopy
    from app.services.list_experience_metrics import metric_currencies
    meta=deepcopy(META);meta["aggregates"][0]["currencyField"]="currency"
    rows=[{"name":"A","amount":"0.10","currency":"USD"},{"name":"A","amount":"0.20","currency":"USD"}]
    assert list_metrics(meta,rows)=={"balance":0.3}
    assert metric_currencies(meta,rows)=={"balance":"USD"}
    rows[1]["currency"]="EUR"
    with pytest.raises(HTTPException): list_metrics(meta,rows)


def test_projector_keeps_readable_rows_but_marks_invalid_metrics():
    from types import SimpleNamespace
    from copy import deepcopy
    from app.services.mask_table_query import project_rows
    meta=deepcopy(META);meta["aggregates"][0]["currencyField"]="currency"
    table={"columns":[{"key":"name"},{"key":"amount"},{"key":"currency"}],"listExperience":meta}
    query=SimpleNamespace(sort=None,filter_plan={},q=None,page=1,limit=10)
    rows=[{"amount":"1.00","currency":"USD"},{"amount":"1.00","currency":"EUR"}]
    result=project_rows(rows,table,query)
    assert result["items"]==rows and result["total"]==2
    assert "aggregate_error" in result and "aggregates" not in result
