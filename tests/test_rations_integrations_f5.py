import asyncio
import pytest
from app.agrar.rations.integrations.adapters import agrirouter_to_feeding_log, icar_ade_to_cow_profile, laboratory_to_feed_ingredient, payload_hash
from app.api.v1.endpoints.rations_integrations import ImportBody, import_rations_data

AGRIR = {"message_type": "iso:11783:-10:time_log:protobuf", "context_id": "ctx-1", "group_id": "g1", "feeding_date": "2026-07-12", "animal_count": 58, "dry_matter_pct": 40,
    "components": [{"ddi": "ddi-1", "label": "Maissilage", "target_kg": 600, "actual_kg": 612}]}

def test_agrirouter_targets_feeding_control():
    value = agrirouter_to_feeding_log(AGRIR)
    assert value["source_version"] == "2.0-http-sse"
    assert value["target_model"] == "FeedingControlIn"
    assert value["target"]["tierzahl"] == 58
    assert value["target"]["komponenten"][0]["ist_kg"] == 612

def test_agrirouter_rejects_unknown_transport_payload():
    with pytest.raises(ValueError, match="message_type"):
        agrirouter_to_feeding_log({**AGRIR, "message_type": "mqtt:legacy"})

def test_icar_ade_targets_existing_cow_profile():
    value = icar_ade_to_cow_profile({"ade_version": "1.5.0", "event_id": "mlp-1", "milkRecordingStatistics": {"milkYield": 36.2, "fatPercent": 4.1, "proteinPercent": 3.45, "lactosePercent": 4.82, "liveWeight": 680, "daysInMilk": 95, "parity": 3, "ureaMgDl": 21}})
    assert value["target_model"] == "CowProfile"
    assert value["target"]["milk_kg_day"] == 36.2
    assert value["target"]["milk_lactose_pct"] == 4.82
    assert value["control_context"]["milk_urea_mg_dl"] == 21

def test_laboratory_targets_existing_feed_ingredient():
    value = laboratory_to_feed_ingredient({"sampleId": "LKS-42", "feedName": "Grassilage Silo 2", "dryMatterPercent": 36.5, "metabolizableEnergyMjKgDm": 10.8, "sidProteinGKgDm": 152, "ndfGKgDm": 415, "starchGKgDm": 18, "crudeFatGKgDm": 34})
    target = value["target"]
    assert value["target_model"] == "FeedIngredient"
    assert target["dm_frac"] == 0.365
    assert target["me_mj_kgdm"] == 10.8
    assert target["andfom_g_kgdm"] == 415

def test_payload_hash_is_order_stable():
    assert payload_hash({"a": 1, "b": 2}) == payload_hash({"b": 2, "a": 1})

class _Mappings:
    def __init__(self, row): self.row = row
    def mappings(self): return self
    def first(self): return self.row

class _ExistingDb:
    def execute(self, _statement, params):
        return _Mappings({"id": "journal-1", "adapter": params["adapter"], "external_id": params["external_id"], "source_version": "1.5.0", "target_model": "CowProfile", "result": {}, "imported_at": "now"})

def test_import_endpoint_returns_idempotent_duplicate():
    body = ImportBody(payload={"event_id": "mlp-1", "milkYield": 30})
    result = asyncio.run(import_rations_data("icar-ade", body, tenant_id="tenant-a", db=_ExistingDb()))
    assert result["duplicate"] is True
    assert result["external_id"] == "mlp-1"