"""Retired mock RAG must never claim successful indexing/search/deletion."""
import importlib.util
from pathlib import Path
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

@pytest.mark.parametrize('method,path,kwargs', [
    ('post','/search',{'json': {'query': 'sensitive query'}}),
    ('post','/index/document',{'params': {'content': 'private content', 'source': 'own-doc'}}),
    ('delete','/index/own-doc',{}),
])
def test_unimplemented_rag_is_explicitly_unavailable(method,path,kwargs):
    file = Path(__file__).resolve().parents[1] / 'services/ai/app/api/v1/endpoints/rag.py'
    spec = importlib.util.spec_from_file_location('retired_rag',file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = FastAPI()
    app.include_router(module.router)
    with TestClient(app) as client:
        response = getattr(client,method)(path,**kwargs)
    assert response.status_code == 503
    assert response.json()['detail']['code'] == 'rag_backend_unavailable'
    assert 'private content' not in response.text and 'sensitive query' not in response.text
    assert 'indexed' not in response.text and 'removed' not in response.text
