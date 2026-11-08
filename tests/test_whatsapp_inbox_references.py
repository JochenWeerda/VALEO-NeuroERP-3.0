"""Real shared PostgreSQL references and HTTP writes; no additional DB/container."""
import os
import uuid
from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.api.v1.endpoints import whatsapp_intake as endpoint
from app.auth.deps_oidc import oidc
from app.core.database import get_db
from app.services.whatsapp_intake_service import WhatsAppIntakeService, WhatsAppReferenceError

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]
PREFIX = uuid.uuid4().hex[:12]
A, B = "wai-a-" + PREFIX, "wai-b-" + PREFIX
K1, K2, KB, KU = (prefix + PREFIX for prefix in ("WA1", "WA2", "WAB", "WAU"))
P1, P2, PB = (str(uuid.uuid4()) for _ in range(3))
ART1, ART2, ARTB = (prefix + PREFIX for prefix in ("WA-A1-", "WA-A2-", "WA-B-"))
NAME = "IntakeCustomer" + PREFIX
PRODUCT = "IntakeProduct" + PREFIX


@pytest.fixture(scope="module")
def engine():
    url = os.environ.get("TEST_DATABASE_URL") or (os.environ.get("DATABASE_URL") if os.environ.get("GITHUB_ACTIONS") == "true" else None)
    if not url:
        pytest.skip("Explicit shared TEST_DATABASE_URL required; no development DB fallback")
    engine = create_engine(url, connect_args={"connect_timeout": 5})
    with engine.begin() as db:
        for tenant in (A, B):
            db.execute(text("INSERT INTO domain_shared.tenants (id,name,domain) VALUES (:id,'Owned inbox probe',:domain)"), {"id": tenant, "domain": tenant + ".invalid"})
        for partner, customer, tenant, name in [(P1, K1, A, NAME), (P2, K2, A, "Other" + PREFIX), (PB, KB, B, NAME)]:
            db.execute(text("INSERT INTO domain_crm.business_partners (partner_id,tenant_id,partner_number,name_1,is_customer,status) VALUES (:id,:tenant,:number,:name,true,'active')"), {"id": partner, "tenant": tenant, "number": customer, "name": name})
            db.execute(text("INSERT INTO public.kunden (kunden_nr,name1,business_partner_id) VALUES (:number,:name,:partner)"), {"number": customer, "name": name, "partner": partner})
        db.execute(text("INSERT INTO public.kunden (kunden_nr,name1) VALUES (:number,:name)"), {"number": KU, "name": "Unmapped" + PREFIX})
        for article, tenant, name in [(ART1, A, PRODUCT), (ART2, A, "OtherProduct" + PREFIX), (ARTB, B, PRODUCT)]:
            db.execute(text("INSERT INTO domain_inventory.articles (id,tenant_id,article_number,name,is_active) VALUES (:id,:tenant,:number,:name,true)"), {"id": str(uuid.uuid4()), "tenant": tenant, "number": article, "name": name})
    try:
        yield engine
    finally:
        with engine.begin() as db:
            db.execute(text("DELETE FROM public.whatsapp_bestellungen WHERE tenant_id IN (:a,:b)"), {"a": A, "b": B})
            db.execute(text("DELETE FROM public.kunden_kontakte WHERE tenant_id IN (:a,:b)"), {"a": A, "b": B})
            db.execute(text("DELETE FROM public.kunden WHERE kunden_nr IN (:k1,:k2,:kb,:ku)"), {"k1": K1, "k2": K2, "kb": KB, "ku": KU})
            db.execute(text("DELETE FROM domain_inventory.articles WHERE tenant_id IN (:a,:b)"), {"a": A, "b": B})
            db.execute(text("DELETE FROM domain_crm.business_partners WHERE tenant_id IN (:a,:b)"), {"a": A, "b": B})
            db.execute(text("DELETE FROM domain_shared.tenants WHERE id IN (:a,:b)"), {"a": A, "b": B})
        engine.dispose()


@pytest.fixture
def db(engine):
    with Session(engine) as db:
        yield db
        db.rollback()
    with engine.begin() as db:
        db.execute(text("DELETE FROM public.whatsapp_bestellungen WHERE tenant_id IN (:a,:b)"), {"a": A, "b": B})
        db.execute(text("DELETE FROM public.kunden_kontakte WHERE tenant_id IN (:a,:b)"), {"a": A, "b": B})


def seed_inbox(db, tenant=A, customer=K1):
    item_id = str(uuid.uuid4())
    db.execute(text("INSERT INTO public.whatsapp_bestellungen (id,tenant_id,raw_text,absender,kunden_nr,status,parsed) VALUES (:id,:tenant,'Owned synthetic order','unverified sender',:customer,'geparst',CAST(:parsed AS JSONB))"), {"id": item_id, "tenant": tenant, "customer": customer, "parsed": '{"positionen":[]}'} )
    db.commit()
    return item_id


def own_contact_count(db):
    return db.execute(text("SELECT count(*) FROM public.kunden_kontakte WHERE tenant_id IN (:a,:b)"), {"a": A, "b": B}).scalar_one()


def test_same_customer_name_is_scoped_to_verified_partner_tenant(db):
    assert WhatsAppIntakeService(db, A).match_kunde(NAME, None)["kunden_nr"] == K1
    assert WhatsAppIntakeService(db, B).match_kunde(NAME, None)["kunden_nr"] == KB
    assert WhatsAppIntakeService(db, A).match_kunde("Unmapped" + PREFIX, None) is None


def test_two_customer_matches_stay_unresolved_even_with_ranking(db):
    db.execute(text("UPDATE public.kunden SET name1=:name WHERE kunden_nr=:number"), {"name": NAME + " longer", "number": K2})
    assert WhatsAppIntakeService(db, A).match_kunde(NAME, None) is None


def test_inactive_partner_cannot_be_matched_or_selected(db):
    db.execute(text("UPDATE domain_crm.business_partners SET status='inactive' WHERE partner_id=:id"), {"id": P1})
    service = WhatsAppIntakeService(db, A)
    assert service.match_kunde(NAME, None) is None
    with pytest.raises(WhatsAppReferenceError):
        service._customer_by_number(K1)


def test_article_matches_are_scoped_and_ambiguity_is_not_first_match(db):
    assert WhatsAppIntakeService(db, A).match_artikel(PRODUCT)["article_number"] == ART1
    assert WhatsAppIntakeService(db, B).match_artikel(PRODUCT)["article_number"] == ARTB
    db.execute(text("UPDATE domain_inventory.articles SET name=:name WHERE article_number=:number AND tenant_id=:tenant"), {"name": PRODUCT + " longer", "number": ART2, "tenant": A})
    assert WhatsAppIntakeService(db, A).match_artikel(PRODUCT) is None


@pytest.mark.parametrize("customer", [KB, KU, "missing", ""])
def test_foreign_unmapped_or_missing_customer_does_not_change_inbox_or_contact(db, customer):
    item_id = seed_inbox(db)
    service = WhatsAppIntakeService(db, A)
    before = service.get(item_id)
    with pytest.raises(WhatsAppReferenceError):
        service.bestaetigen(item_id, customer, "auftrag", None, actor="verified-actor")
    db.commit()
    assert service.get(item_id) == before
    assert own_contact_count(db) == 0


@pytest.mark.parametrize("position", [
    {"match_article_number": ARTB}, {"article_number": ARTB},
    {"match_article_number": ""}, {"match_article_number": ART1, "article_number": ART2},
    {"match_article_number": [ART1]},
])
def test_foreign_or_invalid_article_reference_does_not_change_any_data(db, position):
    item_id = seed_inbox(db)
    service = WhatsAppIntakeService(db, A)
    before = service.get(item_id)
    with pytest.raises(WhatsAppReferenceError):
        service.bestaetigen(item_id, None, "auftrag", {"positionen": [position]}, actor="verified-actor")
    db.commit()
    assert service.get(item_id) == before
    assert own_contact_count(db) == 0


def test_confirmation_restores_authoritative_names_and_records_verified_actor(db):
    item_id = seed_inbox(db)
    override = {"match_kunde": {"kunden_nr": KB, "name": "forged"}, "positionen": [{"artikel": PRODUCT, "match_article_number": ART1, "match_name": "forged", "menge": 0}]}
    original = deepcopy(override)
    result = WhatsAppIntakeService(db, A).bestaetigen(item_id, None, "auftrag", override, actor="verified-actor")
    assert result["parsed"]["match_kunde"]["kunden_nr"] == K1
    assert result["parsed"]["positionen"][0]["match_name"] == PRODUCT
    assert result["parsed"]["positionen"][0]["menge"] == 0
    assert override == original
    assert db.execute(text("SELECT bediener FROM public.kunden_kontakte WHERE tenant_id=:t"), {"t": A}).scalar_one() == "verified-actor"


def test_foreign_inbox_cannot_be_read_confirmed_or_discarded(db):
    item_id = seed_inbox(db, B, KB)
    own = WhatsAppIntakeService(db, A)
    assert own.get(item_id) == {}
    assert own.list_inbox() == []
    assert own.bestaetigen(item_id, K1, "auftrag", None, actor="verified-actor") == {}
    assert own.verwerfen(item_id) == {}
    assert WhatsAppIntakeService(db, B).get(item_id)["status"] == "geparst"
    assert own_contact_count(db) == 0


def test_create_keeps_manual_text_and_does_not_trust_extractor_references(db, monkeypatch):
    extracted = {"kunde": NAME, "positionen": [{"artikel": PRODUCT, "match_article_number": ARTB, "match_name": "forged", "silo": "Silo 3", "menge": None}]}
    original = deepcopy(extracted)
    monkeypatch.setattr(WhatsAppIntakeService, "extract", lambda self, raw: (extracted, "heuristik", 0.45))
    result = WhatsAppIntakeService(db, A).create_inbox("Owned synthetic order", "sender")
    assert result["kunden_nr"] == K1
    assert result["parsed"]["positionen"][0]["match_article_number"] == ART1
    assert result["parsed"]["positionen"][0]["silo"] == "Silo 3"
    assert result["parsed"]["positionen"][0]["menge"] is None
    assert extracted == original


def test_unmatched_manual_position_can_be_confirmed_without_invented_reference(db):
    item_id = seed_inbox(db)
    result = WhatsAppIntakeService(db, A).bestaetigen(item_id, K1, "auftrag", {"positionen": [{"artikel": "Manuell zu pruefen", "silo": "Silo 2", "menge": None}]}, actor="verified-actor")
    assert result["status"] == "bestaetigt"
    assert result["parsed"]["positionen"][0].get("match_article_number") is None


@pytest.mark.parametrize("positions", [{"artikel": "x"}, ["invalid"], "invalid"])
def test_invalid_position_shape_cannot_mutate_inbox(db, positions):
    item_id = seed_inbox(db)
    service = WhatsAppIntakeService(db, A)
    before = service.get(item_id)
    with pytest.raises(WhatsAppReferenceError):
        service.bestaetigen(item_id, K1, "auftrag", {"positionen": positions}, actor="verified-actor")
    db.commit()
    assert service.get(item_id) == before
    assert own_contact_count(db) == 0


def test_revoked_article_is_not_selectable(db):
    item_id = seed_inbox(db)
    db.execute(text("UPDATE domain_inventory.articles SET is_active=false WHERE tenant_id=:tenant AND article_number=:number"), {"tenant": A, "number": ART1})
    with pytest.raises(WhatsAppReferenceError):
        WhatsAppIntakeService(db, A).bestaetigen(item_id, K1, "auftrag", {"positionen": [{"match_article_number": ART1}]}, actor="verified-actor")
    assert own_contact_count(db) == 0


def test_http_with_real_db_rejects_foreign_refs_and_uses_token_actor(db, monkeypatch):
    item_id = seed_inbox(db)
    foreign_id = seed_inbox(db, B, KB)

    async def verify(token):
        return {"sub": "token-actor", "tenant_id": A, "scope": "crm:read crm:write"}

    monkeypatch.setattr(oidc, "verify", verify)
    app = FastAPI()
    app.include_router(endpoint.router)
    app.dependency_overrides[get_db] = lambda: db
    path = "/crm/bestell-inbox/"
    headers = {"Authorization": "Bearer owned-test"}
    with TestClient(app) as client:
        for body in [{"kunden_nr": KB}, {"parsed": {"positionen": [{"article_number": ARTB}]}}]:
            response = client.post(path + item_id + "/bestaetigen", json=body, headers=headers)
            assert response.status_code == 422
            assert KB not in response.text and ARTB not in response.text
            assert WhatsAppIntakeService(db, A).get(item_id)["status"] == "geparst"
            assert own_contact_count(db) == 0
        for suffix, method in [("", "GET"), ("/verwerfen", "POST"), ("/bestaetigen", "POST")]:
            assert client.request(method, path + foreign_id + suffix, json={} if method == "POST" else None, headers=headers).status_code == 404
        assert client.post(path + item_id + "/bestaetigen", json={}, headers=headers).status_code == 200
    assert db.execute(text("SELECT bediener FROM public.kunden_kontakte WHERE tenant_id=:t"), {"t": A}).scalar_one() == "token-actor"
