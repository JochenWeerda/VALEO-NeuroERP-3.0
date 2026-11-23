"""The branch launcher reads the tenant-scoped branch collection through Studio."""

from app.api.v1.endpoints.branches import Branch, router
from app.core.screen_definitions_stamm_batch13 import build_admin_branches


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
