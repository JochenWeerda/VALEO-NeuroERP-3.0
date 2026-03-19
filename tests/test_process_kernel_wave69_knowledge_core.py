"""
Wave 69 - Central Knowledge Core Contracts + API Surfacing.
Focus: versioned knowledge objects, unified retrieval, onboarding bundles.
"""
from __future__ import annotations

import ast
import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api
from app.core.knowledge_core_contracts import (
    KnowledgeFormat,
    KnowledgeObjectTyp,
    KnowledgeRetrievalRequest,
    KnowledgeStatus,
    build_onboarding_bundle,
    get_default_knowledge_objects,
    get_knowledge_object,
    retrieve_knowledge_objects,
)


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    return TestClient(app)


class TestKnowledgeObjectContracts:

    def test_default_objects_exist(self):
        objects = get_default_knowledge_objects()
        assert len(objects) >= 5

    def test_active_version_is_latest(self):
        obj = get_knowledge_object("KNW-SOP-001")
        assert obj.aktive_version().version == 2

    def test_explicit_version_can_be_loaded(self):
        obj = get_knowledge_object("KNW-SOP-001")
        assert obj.hole_version(1).format == KnowledgeFormat.PDF

    def test_agentenfaehig_true_for_released_markdown(self):
        obj = get_knowledge_object("KNW-COM-001")
        assert obj.ist_agentenfaehig() is True

    def test_agentenfaehig_false_for_draft_word(self):
        obj = get_knowledge_object("KNW-MKT-001")
        assert obj.ist_agentenfaehig() is False

    def test_as_dict_contains_core_fields(self):
        obj = get_knowledge_object("KNW-PROD-001")
        data = obj.as_dict()
        assert data["knowledge_id"] == "KNW-PROD-001"
        assert data["typ"] == KnowledgeObjectTyp.PRODUKTWISSEN.value
        assert "aktive_version" in data
        assert "agentenfaehig" in data

    def test_missing_object_raises(self):
        with pytest.raises(ValueError):
            get_knowledge_object("KNW-UNKNOWN")


class TestKnowledgeRetrieval:

    def test_query_prefers_relevant_object(self):
        request = KnowledgeRetrievalRequest(query="umsatz quartal")
        ergebnisse = retrieve_knowledge_objects(request)
        assert ergebnisse[0]["knowledge_id"] == "KNW-KPI-001"

    def test_filter_by_type(self):
        request = KnowledgeRetrievalRequest(
            query="",
            typen=[KnowledgeObjectTyp.SUPPORTWISSEN],
        )
        ergebnisse = retrieve_knowledge_objects(request)
        assert {eintrag["typ"] for eintrag in ergebnisse} == {KnowledgeObjectTyp.SUPPORTWISSEN.value}

    def test_filter_by_tags(self):
        request = KnowledgeRetrievalRequest(
            query="",
            tags=["oidc"],
        )
        ergebnisse = retrieve_knowledge_objects(request)
        assert [eintrag["knowledge_id"] for eintrag in ergebnisse] == ["KNW-SUP-001"]

    def test_agent_only_filters_out_non_agent_ready(self):
        request = KnowledgeRetrievalRequest(
            query="",
            nur_agentenfaehig=True,
            status=None,
        )
        ergebnisse = retrieve_knowledge_objects(request)
        ids = {eintrag["knowledge_id"] for eintrag in ergebnisse}
        assert "KNW-MKT-001" not in ids

    def test_role_filter_for_support(self):
        request = KnowledgeRetrievalRequest(
            query="",
            rolle="support",
            nur_agentenfaehig=True,
        )
        ergebnisse = retrieve_knowledge_objects(request)
        ids = {eintrag["knowledge_id"] for eintrag in ergebnisse}
        assert "KNW-SUP-001" in ids
        assert "KNW-KPI-001" not in ids

    def test_status_defaults_to_freigegeben(self):
        request = KnowledgeRetrievalRequest(query="")
        ergebnisse = retrieve_knowledge_objects(request)
        ids = {eintrag["knowledge_id"] for eintrag in ergebnisse}
        assert "KNW-MKT-001" not in ids

    def test_status_none_can_include_draft(self):
        request = KnowledgeRetrievalRequest(query="", status=None)
        ergebnisse = retrieve_knowledge_objects(request)
        ids = {eintrag["knowledge_id"] for eintrag in ergebnisse}
        assert "KNW-MKT-001" in ids

    def test_limit_is_applied(self):
        request = KnowledgeRetrievalRequest(query="", limit=2)
        ergebnisse = retrieve_knowledge_objects(request)
        assert len(ergebnisse) == 2

    def test_query_without_match_returns_empty(self):
        request = KnowledgeRetrievalRequest(query="nicht vorhandener fachbegriff")
        ergebnisse = retrieve_knowledge_objects(request)
        assert ergebnisse == []


class TestOnboardingBundle:

    def test_onboarding_bundle_returns_role_specific_objects(self):
        bundle = build_onboarding_bundle("vertrieb")
        ids = {eintrag["knowledge_id"] for eintrag in bundle["wissensobjekte"]}
        assert "KNW-SOP-001" in ids
        assert "KNW-COM-001" in ids

    def test_onboarding_bundle_is_agent_only(self):
        bundle = build_onboarding_bundle("einkauf", limit=10)
        ids = {eintrag["knowledge_id"] for eintrag in bundle["wissensobjekte"]}
        assert "KNW-MKT-001" not in ids


class TestKnowledgeApi:

    def test_list_endpoint_returns_objects(self, client: TestClient):
        response = client.get("/process/knowledge/objekte")
        assert response.status_code == 200
        body = response.json()
        assert len(body) >= 5
        assert any(eintrag["knowledge_id"] == "KNW-SOP-001" for eintrag in body)

    def test_detail_endpoint_returns_active_version(self, client: TestClient):
        response = client.get("/process/knowledge/objekte/KNW-SOP-001")
        assert response.status_code == 200
        body = response.json()
        assert body["version"] == 2
        assert body["agentenfaehig"] is True

    def test_detail_endpoint_can_return_explicit_version(self, client: TestClient):
        response = client.get("/process/knowledge/objekte/KNW-SOP-001?version=1")
        assert response.status_code == 200
        body = response.json()
        assert body["version"] == 1
        assert body["format"] == KnowledgeFormat.PDF.value
        assert body["agentenfaehig"] is False

    def test_detail_endpoint_404_for_unknown_object(self, client: TestClient):
        response = client.get("/process/knowledge/objekte/KNW-UNKNOWN")
        assert response.status_code == 404

    def test_retrieve_endpoint_supports_filters(self, client: TestClient):
        response = client.post(
            "/process/knowledge/retrieve",
            json={
                "query": "oidc login",
                "typen": [KnowledgeObjectTyp.SUPPORTWISSEN.value],
                "nur_agentenfaehig": True,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["anzahl"] == 1
        assert body["ergebnisse"][0]["knowledge_id"] == "KNW-SUP-001"

    def test_retrieve_endpoint_can_include_drafts(self, client: TestClient):
        response = client.post(
            "/process/knowledge/retrieve",
            json={
                "query": "",
                "status": None,
                "tags": ["preise"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        ids = {eintrag["knowledge_id"] for eintrag in body["ergebnisse"]}
        assert "KNW-MKT-001" in ids

    def test_onboarding_endpoint_requires_role(self, client: TestClient):
        response = client.post("/process/knowledge/onboarding-bundle", json={})
        assert response.status_code == 400

    def test_onboarding_endpoint_returns_bundle(self, client: TestClient):
        response = client.post(
            "/process/knowledge/onboarding-bundle",
            json={"rolle": "support", "limit": 3},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["rolle"] == "support"
        assert body["anzahl"] >= 1
        assert any(eintrag["knowledge_id"] == "KNW-SUP-001" for eintrag in body["wissensobjekte"])


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
