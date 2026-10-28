"""Urheber aus der Anmeldung, nie aus dem Rumpf.

Bis 28.10.2026 nahmen Geschaeftspartner (``payload.audit.created_by``), Vertragsnachtrag (``createdBy``, Mandant
``tenantId``), Lohnexport (``createdBy``), Buchungsuebergabe-Export (GoBD-Artefakt ``created_by=body.bediener`` — das
ist der Filter) und Mahnstufe (``operator``, sonst ``"Maske"``) den Urheber aus dem Anfragekoerper. Der Vertragstest
uebersah das, weil sein Docstring-Filter ``text(\"\"\"`` mitten in der Zeile falsch zaehlte.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import business_partners, finance_actions, open_items, personal
from app.routers import contracts_router

pytestmark = pytest.mark.unit


def _anfrage(sub: str = "pruefer-1"):
    return SimpleNamespace(state=SimpleNamespace(token_claims={"sub": sub}))


OHNE = SimpleNamespace(state=SimpleNamespace())


class _Db:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass


def test_vertragsnachtrag_urheber_und_mandant_aus_dem_token(monkeypatch):
    gefragt = []

    async def vertrag(contract_id, db, tenant_id):
        gefragt.append((contract_id, tenant_id))
        return {}

    monkeypatch.setattr(contracts_router, "get_contract", vertrag)
    monkeypatch.setattr(contracts_router, "_amendment_to_item", lambda a: {"created_by": a.created_by, "tenant_id": a.tenant_id})
    body = contracts_router.AmendmentCreate(reason="Menge angepasst nach Ernte", tenantId="fremd", createdBy="jemand")
    ergebnis = asyncio.run(contracts_router.create_amendment("K-1", body, _anfrage(), db=_Db(), tenant_id="mandant-a"))
    assert ergebnis == {"created_by": "pruefer-1", "tenant_id": "mandant-a"}
    assert gefragt == [("K-1", "mandant-a")]
    assert "createdBy" not in contracts_router.AmendmentCreate.model_fields
    assert "tenantId" not in contracts_router.AmendmentCreate.model_fields


def test_vertragsnachtrag_fuer_fremden_vertrag_404(monkeypatch):
    async def fehlt(contract_id, db, tenant_id):
        raise HTTPException(404, "Contract not found")

    monkeypatch.setattr(contracts_router, "get_contract", fehlt)
    db = _Db()
    with pytest.raises(HTTPException) as info:
        asyncio.run(contracts_router.create_amendment(
            "K-fremd", contracts_router.AmendmentCreate(reason="Menge angepasst nach Ernte"), _anfrage(), db=db, tenant_id="a"))
    assert info.value.status_code == 404 and db.added == []


def test_ohne_gepruefte_identitaet_kein_nachtrag(monkeypatch):
    async def vertrag(contract_id, db, tenant_id):
        return {}

    monkeypatch.setattr(contracts_router, "get_contract", vertrag)
    with pytest.raises(HTTPException) as info:
        asyncio.run(contracts_router.create_amendment(
            "K-1", contracts_router.AmendmentCreate(reason="Menge angepasst nach Ernte"), OHNE, db=_Db(), tenant_id="a"))
    assert info.value.status_code == 403


class _PartnerDienst:
    def __init__(self, row=None):
        self.row = row
        self.gespeichert = None

    def check_partner_number_unique(self, *a, **k):
        pass

    def assign_account_numbers(self, row):
        pass

    def persist_new_partner(self, row):
        self.gespeichert = row
        return row

    def get_partner(self, partner_id):
        return self.row

    def persist_updated_partner(self, row):
        self.gespeichert = row
        return row


def _partner(created_by="jemand", updated_by="jemand"):
    return business_partners.BusinessPartnerEnvelope.model_validate({"business_partner": {
        "core_identity": {"partner_number": "K-1000", "name_1": "Hof Meyer"},
        "audit": {"created_by": created_by, "updated_by": updated_by},
    }})


def test_geschaeftspartner_urheber_aus_dem_token(monkeypatch):
    dienst = _PartnerDienst()
    monkeypatch.setattr(business_partners, "_svc", lambda db, tid: dienst)
    monkeypatch.setattr(business_partners, "_to_out", lambda row: row)
    row = asyncio.run(business_partners.create_business_partner(_partner(), _anfrage("anleger"), tenant_id="a", db=None))
    assert (row.created_by, row.updated_by) == ("anleger", "anleger")

    dienst.row = row
    row = asyncio.run(business_partners.update_business_partner(row.partner_id, _partner("x", "y"), _anfrage("aenderer"),
                                                                tenant_id="a", db=None))
    assert (row.created_by, row.updated_by) == ("anleger", "aenderer")


def test_lohnexport_urheber_aus_dem_token(monkeypatch):
    erfasst = {}

    class Dienst:
        def __init__(self, db, tenant_id):
            pass

        def get_payroll_time_rows(self, von, bis):
            return []

        def create_payroll_export(self, daten):
            erfasst.update(daten)
            return daten

    monkeypatch.setattr(personal, "PersonalService", Dienst)
    monkeypatch.setattr(personal, "_payroll_export_from_row", lambda row: row)
    asyncio.run(personal.create_payroll_export(
        personal.PayrollExportCreateIn(periodFrom="2026-10-01", periodTo="2026-10-31", createdBy="jemand"),
        _anfrage("lohnbuero"), tenant_id="a", db=None))
    assert erfasst["created_by"] == "lohnbuero"
    assert "createdBy" not in personal.PayrollExportCreateIn.model_fields


def test_mahnstufe_bearbeiter_aus_dem_token(monkeypatch):
    erfasst = {}

    async def posten(eid, tenant_id, db):
        return {"rechnungsnr": "RE-1"}

    def eskaliere(db, nummer, tid, akteur):
        erfasst["akteur"] = akteur
        return {"stufe": 1}

    async def ausfuehren(db, **kw):
        await kw["delegate_fn"](db, kw["body"], kw["entity_id"], kw["tenant_id"])
        return SimpleNamespace(model_dump=lambda: {"ok": True})

    import app.services.finance_mahnstufe_service as mahnstufe
    import app.services.mask_action_runtime_service as laufzeit
    monkeypatch.setattr(open_items, "get_open_item", posten)
    monkeypatch.setattr(mahnstufe, "eskaliere_mahnstufe", eskaliere)
    monkeypatch.setattr(laufzeit, "run_delegated_mask_action", ausfuehren)
    asyncio.run(open_items.action_mahnen("OP-1", _anfrage("mahnerin"), body={"operator": "jemand"}, db=None, tenant_id="a"))
    assert erfasst["akteur"] == "mahnerin"


def test_buchungsuebergabe_artefakt_traegt_den_exportierenden(monkeypatch):
    erfasst = {}

    class Ergebnis:
        def fetchall(self):
            return []

    class Db:
        def execute(self, *a, **k):
            return Ergebnis()

        def commit(self):
            pass

    monkeypatch.setattr(finance_actions, "register_artifact", lambda db, tid, *a, **k: erfasst.update(k))
    body = finance_actions.BuchungsuebergabeExportRequest(von="2026-10-01", bis="2026-10-31", bediener="KASSE1")
    try:
        asyncio.run(finance_actions.buchungsuebergabe_export(body, _anfrage("fibu"), tenant_id="a", db=Db()))
    except HTTPException as exc:
        pytest.fail(f"Export scheiterte: {exc.detail}")
    assert erfasst["created_by"] == "fibu"
