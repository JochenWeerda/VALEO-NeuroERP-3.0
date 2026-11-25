"""The branch launcher reads the tenant-scoped branch collection through Studio."""

from app.api.v1.endpoints.branches import Branch, router
from app.core.screen_definitions_stamm_batch13 import build_admin_branches, build_admin_branch_detail


def test_branch_launcher_uses_collection_schema():
    screen = build_admin_branches()
    table, = screen["tables"]
    source, = screen["dataSources"]
    route = next(route for route in router.routes if route.path == "/admin/branches" and "GET" in route.methods)
    assert route.response_model == list[Branch]
    assert screen["mode"] == "list"
    assert source["endpoint"] == f"/api/v1{route.path}"
    assert table["dataSourceKey"] == source["key"]
    assert table["serverPagination"] is False
    assert {column["key"] for column in table["columns"]} == {"branch_number", "name", "is_active"}
    assert all(column["key"] in Branch.model_fields for column in table["columns"])


def test_branch_list_opens_the_typed_branch_detail():
    screen = build_admin_branch_detail()
    action, = build_admin_branches()["tables"][0]["rowActions"]
    assert action["navigationRoute"] == "/admin/branches/{entity_id}"
    route = next(route for route in router.routes if route.path == "/admin/branches/{branch_id}" and "GET" in route.methods)
    assert route.response_model is Branch
    assert screen["mode"] == "detail"
    assert screen["dataSources"][0]["endpoint"] == f"/api/v1{route.path}".replace("{branch_id}", "{entity_id}")
    fields = screen["tabs"][0]["fields"]
    assert {field["key"] for field in fields} == {"branch_number", "name", "is_active", "created_at", "updated_at"}
    assert all(field["readOnly"] and field["key"] in Branch.model_fields for field in fields)


def test_branch_rename_definition_requires_version_and_audit():
    from app.api.v1.endpoints.branches import BranchRenameCommand, rename_branch

    action, = build_admin_branch_detail()["actions"]
    route = next(route for route in router.routes if route.endpoint is rename_branch)
    assert action["commandEndpoint"] == f"/api/v1{route.path}".replace("{branch_id}", "{entity_id}")
    assert route.methods == {action["method"]}
    assert action["requiresExpectedVersion"] and action["requiresIdempotencyKey"] and action["auditReasonRequired"]
    assert action["forbiddenForAgents"]
    assert set(BranchRenameCommand.model_json_schema()["required"]) == {"name", "expected_version"}
