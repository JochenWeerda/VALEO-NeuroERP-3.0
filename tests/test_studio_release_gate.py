"""Trusted evidence cannot be reused for a different Studio candidate."""
from uuid import uuid4
import pytest
from app.services import studio_draft_store as store
from app.core import studio_release as release
from app.services import studio_process_simulation as simulation

@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield

@pytest.fixture(autouse=True)
def memory_store():
    store.reset_studio_drafts()
    yield
    store.use_sql_studio_drafts()

def candidate():
    from app.services.studio_propose import propose_studio_draft
    definition = propose_studio_draft("Artikel")
    definition["actions"]=[];definition["agentContract"]["availableActions"]=[];definition["agentContract"]["editableFields"]=[]
    definition.update(id="tenant/simulated", domain="agrar", adapter={"type":"native", "sourceId":"tenant/simulated", "temporary":True})
    draft=store.save_draft("own","editor",definition)
    return store.set_status("own",draft["id"],"editor","review",expected_snapshot=draft)

def proof(item):
    return {"tenant_id":item["tenant_id"],"draft_id":item["id"],"candidate_revision":item["revision"],
            "definition_hash":release.definition_hash(item["definition"]),"artifact_hash":simulation.simulation_artifact_hash(),
            "passed":True,"profile":"grain.v1","checks":{name:True for name in simulation._REQUIRED}}

def test_low_level_publish_cannot_bypass_missing_simulation():
    item=candidate()
    with pytest.raises(ValueError,match="simulation_fuer_diese_revision_fehlt"):
        store.set_status("own",item["id"],"human-reviewer","published_temp",expected_snapshot=item)
    assert store.get_draft("own",item["id"])["status"]=="review"

def test_exact_trusted_evidence_replays_once_and_allows_four_eyes(monkeypatch):
    item=candidate()
    execute=lambda value:proof(value)
    monkeypatch.setattr(release,"simulate_candidate",execute)
    key=str(uuid4())
    first=store.simulate_draft("own",item["id"],"editor",item["revision"],key)
    assert store.simulate_draft("own",item["id"],"editor",item["revision"],key)==first
    assert store.count_history("own",item["id"])==3
    assert store.set_status("own",item["id"],"human-reviewer","published_temp",expected_snapshot=item)["status"]=="published_temp"

@pytest.mark.parametrize("broken",["checks","artifact_hash","definition_hash","tenant_id","passed"])
def test_incomplete_or_wrong_evidence_blocks_publish(monkeypatch,broken):
    item=candidate()
    def execute(value):
        result=proof(value)
        result[broken]={} if broken=="checks" else False if broken=="passed" else "wrong"
        return result
    monkeypatch.setattr(release,"simulate_candidate",execute)
    store.simulate_draft("own",item["id"],"editor",item["revision"],str(uuid4()))
    with pytest.raises(ValueError,match="simulation_unvollstaendig"):
        store.set_status("own",item["id"],"human-reviewer","published_temp",expected_snapshot=item)

def test_evidence_does_not_follow_an_edit(monkeypatch):
    item=candidate()
    monkeypatch.setattr(release,"simulate_candidate",proof)
    store.simulate_draft("own",item["id"],"editor",item["revision"],str(uuid4()))
    changed=store.save_draft("own","editor",{**item["definition"],"title":"changed"},draft_id=item["id"],expected_revision=item["revision"])
    changed=store.set_status("own",item["id"],"editor","review",expected_snapshot=changed)
    with pytest.raises(ValueError,match="simulation_fuer_diese_revision_fehlt"):
        store.set_status("own",item["id"],"human-reviewer","published_temp",expected_snapshot=changed)


def test_active_runtime_requires_current_evidence(monkeypatch):
    item=candidate();monkeypatch.setattr(release,"simulate_candidate",proof)
    store.simulate_draft("own",item["id"],"editor",item["revision"],str(uuid4()))
    store.set_status("own",item["id"],"reviewer","published_temp",expected_snapshot=item)
    active=store.get_published_definition("own",item["screen_id"])
    assert active["studioRelease"]["candidateRevision"]==item["revision"]
    monkeypatch.setattr(simulation,"simulation_artifact_hash",lambda:"changed-release")
    assert store.get_published_definition("own",item["screen_id"]) is None
    assert store.list_published_definitions("own")==[]

def test_legacy_publication_has_no_invented_evidence():
    item=candidate();store._DRAFTS[item["id"]]["status"]="published_temp"
    assert store.get_published_definition("own",item["screen_id"]) is None

def test_uncovered_commands_and_rule_variants_are_not_certified():
    from app.services.studio_propose import propose_studio_draft
    value=propose_studio_draft("Artikel");value["domain"]="agrar"
    assert "screen_commands_not_covered" in release.profile_errors(value)
    value["actions"]=[];value["agentContract"]["availableActions"]=[];value["agentContract"]["editableFields"]=[]
    value["qualityRules"]={"discount":1}
    assert "rules_not_covered" in release.profile_errors(value)
