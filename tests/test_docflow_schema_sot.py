"""Adapters must refer to the exact canonical model objects, never stale copies."""
import ast
from pathlib import Path
import pytest
from app.api.v1.endpoints import docflow
from app.api.v1.schemas import docflow_schemas

MODELS = ['DocflowOut', 'DocflowItemOut', 'DocflowHeaderOut', 'DocflowConvertRequest', 'DocflowPostRequest', 'DocflowReleaseRequest', 'DocflowReverseRequest', 'DocflowRecordPrintRequest', 'DocflowRecordExportRequest', 'DocflowCommandResult', 'DocflowLineInput', 'PosComplianceInput', 'DocflowCreateRequest', 'DocflowUpdateRequest', 'DocflowApprovalRequest', 'DocflowApprovalDecision']

@pytest.mark.parametrize('name',MODELS)
def test_router_uses_canonical_model_object(name):
    assert getattr(docflow,name) is getattr(docflow_schemas,name)
    getattr(docflow_schemas,name).model_json_schema()


def test_router_cannot_reintroduce_local_contract_copies():
    tree=ast.parse(Path(docflow.__file__).read_text(encoding='utf-8'))
    assert not [node.name for node in tree.body if isinstance(node,ast.ClassDef)]


def test_update_requirements_are_not_the_old_optional_contract():
    schema=docflow_schemas.DocflowUpdateRequest.model_json_schema()
    assert {'expected_version','idempotency_key'} <= set(schema['required'])
