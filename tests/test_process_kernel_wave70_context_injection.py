"""
Wave 70 - Knowledge Context Injection for humans and agents.
"""
from __future__ import annotations

import ast
import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import agent_context_api, process_kernel_api
from app.core.knowledge_core_contracts import KnowledgeChannel, build_context_pack


@pytest.fixture
def client(require_db) -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    app.include_router(agent_context_api.router)
    return TestClient(app)


class TestContextPackContracts:

    def test_context_pack_for_support_includes_relevant_knowledge(self):
        pack = build_context_pack(
            rolle="support",
            kanal=KnowledgeChannel.CHAT,
            capability_key="support_assistant",
            query="oidc login",
        )
        assert "KNW-SUP-001" in pack.knowledge_ids
        assert any("Capability-Kontext aktiv" in hinweis for hinweis in pack.prompt_hinweise)

    def test_context_pack_for_voice_adds_voice_hint(self):
        pack = build_context_pack(
            rolle="vertrieb",
            kanal=KnowledgeChannel.VOICE,
            query="angebot freigabe",
        )
        assert any("sprechbar" in hinweis for hinweis in pack.prompt_hinweise)

    def test_context_pack_collects_standards(self):
        pack = build_context_pack(
            rolle="vertrieb",
            kanal=KnowledgeChannel.TEAMS,
            query="angebot markenstil",
            limit=5,
        )
        assert any("Kommunikationsstandard" in standard for standard in pack.standards)
        assert any("Prozessstandard" in standard for standard in pack.standards)


class TestContextPackApi:

    def test_process_kernel_context_pack_endpoint(self, client: TestClient):
        response = client.post(
            "/process/knowledge/context-pack",
            json={
                "rolle": "vertrieb",
                "kanal": "TEAMS",
                "capability_key": "sales_assistant",
                "query": "angebot freigabe",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["rolle"] == "vertrieb"
        assert body["kanal"] == "TEAMS"
        assert "KNW-SOP-001" in body["knowledge_ids"]

    def test_process_kernel_context_pack_requires_role(self, client: TestClient):
        response = client.post("/process/knowledge/context-pack", json={"query": "oidc"})
        assert response.status_code == 400

    def test_agent_context_knowledge_pack_endpoint(self, client: TestClient):
        context_response = client.post(
            "/agent-context",
            json={
                "agent_id": "agent-1",
                "tenant_id": "tenant-a",
                "delegated_roles": ["support"],
                "ttl_sekunden": 1200,
            },
        )
        assert context_response.status_code == 201
        context_id = context_response.json()["context_id"]

        response = client.post(
            f"/agent-context/{context_id}/knowledge-pack",
            json={
                "rolle": "support",
                "kanal": "SLACK",
                "capability_key": "support_assistant",
                "query": "oidc login",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["tenant_id"] == "tenant-a"
        assert body["knowledge_pack"]["kanal"] == "SLACK"
        assert "KNW-SUP-001" in body["knowledge_pack"]["knowledge_ids"]

    def test_agent_context_knowledge_pack_404_without_context(self, client: TestClient):
        response = client.post(
            "/agent-context/does-not-exist/knowledge-pack",
            json={"rolle": "support"},
        )
        assert response.status_code == 404


class TestArchitectureConstraints:

    def _get_imports(self, module_path: str) -> list[str]:
        with open(module_path, "r", encoding="utf-8") as handle:
            source = handle.read()
        tree = ast.parse(source)
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        return imports

    def test_no_api_imports_in_knowledge_core(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "app",
            "core",
            "knowledge_core_contracts.py",
        )
        imports = self._get_imports(os.path.normpath(path))
        api_imports = [eintrag for eintrag in imports if "app.api" in eintrag]
        assert api_imports == []
