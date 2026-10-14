"""Explicit lifecycle doubles; actual domain/SQL evidence is tested separately."""
from copy import deepcopy
from uuid import uuid4
from unittest.mock import patch


def simulation_ready_definition(definition):
    """Lifecycle fixture: a UI-only Agrar overlay without untested commands/rules."""
    result=deepcopy(definition)
    result["domain"]="agrar"
    result["actions"]=[]
    result["processSimulation"]={"profile":"grain.v1"}
    if "agentContract" in result:
        result["agentContract"]["domain"]="agrar"
        result["agentContract"]["availableActions"]=[]
        result["agentContract"]["editableFields"]=[]
        result["agentContract"]["businessRules"]=[]
    return result


def isolated_lifecycle_proof(item):
    from app.core.studio_release import definition_hash, profile_errors
    from app.services.studio_process_simulation import simulation_artifact_hash, _REQUIRED
    assert not profile_errors(item["definition"])
    return {"passed":True,"profile":"grain.v1","checks":{name:True for name in _REQUIRED},
            "tenant_id":item["tenant_id"],"draft_id":item["id"],"candidate_revision":item["revision"],
            "definition_hash":definition_hash(item["definition"]),"artifact_hash":simulation_artifact_hash()}


def simulate_reviewed(client,path,revision,**kwargs):
    with patch("app.core.studio_release.simulate_candidate",side_effect=isolated_lifecycle_proof):
        result=client.post(path+"/simulate",json={"expected_revision":revision,"idempotency_key":str(uuid4())},**kwargs)
    assert result.status_code==200,result.text
    return result


def record_lifecycle_proof(item,actor="editor"):
    from app.services.studio_draft_store import simulate_draft
    with patch("app.core.studio_release.simulate_candidate",side_effect=isolated_lifecycle_proof):
        return simulate_draft(item["tenant_id"],item["id"],actor,item["revision"],str(uuid4()))


def publish_reviewed(client,path,**kwargs):
    draft_path=path.removesuffix("/publish")
    read=client.get(draft_path,headers=kwargs.get("headers"))
    assert read.status_code==200,read.text
    if read.json()["status"]=="draft":
        read=client.post(draft_path+"/submit-review",json={"expected_revision":read.json()["revision"],"idempotency_key":str(uuid4())},**kwargs)
        assert read.status_code==200,read.text
    simulate_reviewed(client,draft_path,read.json()["revision"],**kwargs)
    return client.post(path,json={"expected_revision":read.json()["revision"],"idempotency_key":str(uuid4())},**kwargs)
