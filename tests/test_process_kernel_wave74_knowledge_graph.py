"""
Wave 74 - Traversable knowledge graph for knowledge, roles, processes and entities.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import channel_work_surfaces
from app.core.database import get_db
from app.core.knowledge_core_contracts import get_default_knowledge_objects
from app.core.knowledge_graph import build_runtime_knowledge_graph


class _DummyDb:
    pass


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    app = FastAPI()
    app.include_router(channel_work_surfaces.router)
    app.dependency_overrides[get_db] = lambda: _DummyDb()
    monkeypatch.setattr(
        "app.core.knowledge_graph.load_runtime_knowledge_objects",
        lambda db: get_default_knowledge_objects(),
    )
    return TestClient(app)


def test_knowledge_graph_contains_core_node_types(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.core.knowledge_graph.load_runtime_knowledge_objects",
        lambda db: get_default_knowledge_objects(),
    )
    graph = build_runtime_knowledge_graph(_DummyDb())
    node_types = {node.node_type for node in graph.nodes}
    assert {"knowledge_object", "role", "process_definition", "entity"} <= node_types


def test_knowledge_graph_contains_support_knowledge_access_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.core.knowledge_graph.load_runtime_knowledge_objects",
        lambda db: get_default_knowledge_objects(),
    )
    graph = build_runtime_knowledge_graph(_DummyDb())
    path = graph.find_path("role:support", "knowledge:KNW-SUP-001")
    assert path == ["role:support", "knowledge:KNW-SUP-001"]


def test_knowledge_graph_connects_process_to_entity_sequence(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.core.knowledge_graph.load_runtime_knowledge_objects",
        lambda db: get_default_knowledge_objects(),
    )
    graph = build_runtime_knowledge_graph(_DummyDb())
    path = graph.find_path("process:settlement_to_finance", "entity:ap_invoice")
    assert path
    assert path[0] == "process:settlement_to_finance"
    assert path[-1] == "entity:ap_invoice"


def test_knowledge_graph_neighbors_return_connected_nodes(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.core.knowledge_graph.load_runtime_knowledge_objects",
        lambda db: get_default_knowledge_objects(),
    )
    graph = build_runtime_knowledge_graph(_DummyDb())
    neighbors = {node.node_id for node in graph.neighbors("knowledge:KNW-SUP-001")}
    assert "role:support" in neighbors
    assert "tag:oidc" in neighbors


def test_knowledge_graph_path_returns_empty_for_unknown_target(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.core.knowledge_graph.load_runtime_knowledge_objects",
        lambda db: get_default_knowledge_objects(),
    )
    graph = build_runtime_knowledge_graph(_DummyDb())
    assert graph.find_path("role:support", "entity:not_there") == []


def test_knowledge_graph_api_returns_graph(client: TestClient):
    response = client.get("/channels/knowledge-graph")
    assert response.status_code == 200
    body = response.json()
    assert body["node_count"] >= 1
    assert body["edge_count"] >= 1


def test_knowledge_graph_api_returns_node_neighbors(client: TestClient):
    response = client.get("/channels/knowledge-graph/nodes/knowledge:KNW-SUP-001")
    assert response.status_code == 200
    body = response.json()
    assert body["node"]["node_id"] == "knowledge:KNW-SUP-001"
    assert any(neighbor["node_id"] == "role:support" for neighbor in body["neighbors"])


def test_knowledge_graph_api_returns_path(client: TestClient):
    response = client.post(
        "/channels/knowledge-graph/path",
        json={
            "source_id": "role:support",
            "target_id": "knowledge:KNW-SUP-001",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["path"] == ["role:support", "knowledge:KNW-SUP-001"]


def test_knowledge_graph_api_returns_404_for_missing_node(client: TestClient):
    response = client.get("/channels/knowledge-graph/nodes/not-found")
    assert response.status_code == 404
