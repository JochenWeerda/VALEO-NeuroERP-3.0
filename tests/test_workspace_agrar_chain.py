"""Pure Unit-Tests: Agrar-Ketten-Read-Model (kein DB, kein MagicMock)."""

from __future__ import annotations

import pytest

from app.workspace.agrar_chain import (
    AgrarChainInput,
    ChainHint,
    KonChainInput,
    NextStep,
    resolve_agrar_next_step,
    resolve_kon_next_step,
    resolve_next_step,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "inp, expected_step, reason_part",
    [
        (
            KonChainInput("K-1", "OFFEN"),
            NextStep.DISPOSITION,
            "abruf_fehlt_oder_offen",
        ),
        (
            KonChainInput("K-2", "OFFEN", disposition_status="OFFEN"),
            NextStep.DISPOSITION,
            "abruf_fehlt_oder_offen",
        ),
        (
            KonChainInput("K-3", "OFFEN", disposition_status="FREIGEGEBEN"),
            NextStep.WAAGE,
            "abruf_freigegeben",
        ),
        (
            KonChainInput("K-4", "OFFEN", disposition_status="GELIEFERT"),
            NextStep.QUALITAET,
            "geliefert",
        ),
        (
            KonChainInput("K-5", "OFFEN", weighing_present=True),
            NextStep.QUALITAET,
            "wiegeschein",
        ),
        (
            KonChainInput("K-6", "OFFEN", quality_is_final=True),
            NextStep.ABRECHNUNG,
            "qualitaet_final",
        ),
        (
            KonChainInput("K-7", "OFFEN", quality_is_final=True, settlement_status="draft"),
            NextStep.ABRECHNUNG,
            "qualitaet_final",
        ),
        (
            KonChainInput("K-8", "ERLEDIGT"),
            NextStep.DONE,
            "erledigt",
        ),
        (
            KonChainInput("K-9", "OFFEN", settlement_status="posted"),
            NextStep.DONE,
            "settlement_posted",
        ),
        (
            KonChainInput("K-10", "STORNIERT"),
            NextStep.BLOCKED,
            "storniert",
        ),
        (
            KonChainInput("K-11", "OFFEN", disposition_status="STORNIERT"),
            NextStep.BLOCKED,
            "storniert",
        ),
    ],
)
def test_kon_next_step_rules(
    inp: KonChainInput, expected_step: NextStep, reason_part: str
) -> None:
    hint = resolve_kon_next_step(inp)
    assert hint.contract_ref == inp.contract_ref
    assert hint.source_model == "kon"
    assert hint.next_step == expected_step
    assert reason_part in hint.reason


@pytest.mark.unit
@pytest.mark.parametrize(
    "inp, expected_step, reason_part",
    [
        (
            AgrarChainInput("A-1", "open"),
            NextStep.WAAGE,
            "einstieg_waage",
        ),
        (
            AgrarChainInput("A-2", "partially_allocated"),
            NextStep.WAAGE,
            "allokation_oder_wiegung",
        ),
        (
            AgrarChainInput("A-3", "open", weighing_status="open", allocation_status="unallocated"),
            NextStep.WAAGE,
            "allokation_oder_wiegung",
        ),
        (
            AgrarChainInput("A-4", "open", allocation_status="allocated"),
            NextStep.QUALITAET,
            "wiegeschein_allokiert",
        ),
        (
            AgrarChainInput("A-5", "fulfilled"),
            NextStep.QUALITAET,
            "fulfilled_ohne_qs",
        ),
        (
            AgrarChainInput("A-6", "open", harvest_release_status="draft"),
            NextStep.QUALITAET,
            "annahme_offen",
        ),
        (
            AgrarChainInput("A-7", "open", quality_is_final=True),
            NextStep.ABRECHNUNG,
            "qs_fertig",
        ),
        (
            AgrarChainInput("A-8", "open", harvest_release_status="final", settlement_status="draft"),
            NextStep.ABRECHNUNG,
            "settlement_offen",
        ),
        (
            AgrarChainInput("A-9", "closed"),
            NextStep.DONE,
            "closed",
        ),
        (
            AgrarChainInput("A-10", "open", settlement_status="posted"),
            NextStep.DONE,
            "settlement_posted",
        ),
        (
            AgrarChainInput("A-11", "cancelled"),
            NextStep.BLOCKED,
            "cancelled",
        ),
        (
            AgrarChainInput("A-12", "open", quality_status="rejected"),
            NextStep.BLOCKED,
            "rejected",
        ),
    ],
)
def test_agrar_next_step_rules(
    inp: AgrarChainInput, expected_step: NextStep, reason_part: str
) -> None:
    hint = resolve_agrar_next_step(inp)
    assert hint.contract_ref == inp.contract_ref
    assert hint.source_model == "agrar"
    assert hint.next_step == expected_step
    assert reason_part in hint.reason


@pytest.mark.unit
def test_resolve_next_step_dispatch_keeps_models_separate() -> None:
    kon = resolve_next_step(
        contract_ref="KON-100",
        source_model="kon",
        fields={"contract_status": "OFFEN", "disposition_status": "FREIGEGEBEN"},
    )
    agrar = resolve_next_step(
        contract_ref="AGR-100",
        source_model="agrar",
        fields={"contract_status": "open"},
    )
    assert kon == ChainHint("KON-100", "kon", NextStep.WAAGE, kon.reason)
    assert agrar.next_step == NextStep.WAAGE
    assert kon.source_model != agrar.source_model
    assert kon.as_dict()["next_step"] == "waage"
    assert set(kon.as_dict()) == {"contract_ref", "source_model", "next_step", "reason"}


@pytest.mark.unit
def test_resolve_next_step_rejects_unknown_source() -> None:
    with pytest.raises(ValueError, match="unknown source_model"):
        resolve_next_step(contract_ref="X", source_model="mixed", fields={})  # type: ignore[arg-type]


@pytest.mark.unit
def test_kon_and_agrar_do_not_share_disposition_semantics() -> None:
    """Agrar-open geht zur Waage; Kon-open ohne Abruf zur Disposition — nicht vereinheitlicht."""
    kon = resolve_kon_next_step(KonChainInput("K", "OFFEN"))
    agrar = resolve_agrar_next_step(AgrarChainInput("A", "open"))
    assert kon.next_step == NextStep.DISPOSITION
    assert agrar.next_step == NextStep.WAAGE


@pytest.mark.unit
@pytest.mark.parametrize(
    "status, expected_step",
    [
        ("open", NextStep.WAAGE),
        ("partially_allocated", NextStep.WAAGE),
        ("fulfilled", NextStep.QUALITAET),
        ("cancelled", NextStep.BLOCKED),
    ],
)
def test_home_agrar_contracts_status_only_mapping(
    status: str, expected_step: NextStep
) -> None:
    """Home sendet nur id+status aus GET /agrar/contracts — kein Fake von quality_is_final."""
    hint = resolve_agrar_next_step(AgrarChainInput(f"AC-{status}", status))
    assert hint.source_model == "agrar"
    assert hint.next_step == expected_step
    assert hint.next_step != NextStep.ABRECHNUNG


@pytest.mark.unit
def test_agrar_fulfilled_without_qs_is_qualitaet_not_abrechnung_or_done() -> None:
    """fulfilled = Menge allokiert (wie ticket_ready), nicht closed und nicht QS-final."""
    hint = resolve_agrar_next_step(AgrarChainInput("A-fulfilled", "fulfilled"))
    assert hint.next_step == NextStep.QUALITAET
    assert hint.next_step not in {NextStep.ABRECHNUNG, NextStep.DONE}
    assert "fulfilled_ohne_qs" in hint.reason


@pytest.mark.unit
def test_agrar_unknown_status_is_blocked_not_silent_done() -> None:
    hint = resolve_agrar_next_step(AgrarChainInput("A-x", "weird_status"))
    assert hint.next_step == NextStep.BLOCKED
    assert "unbekannt" in hint.reason


@pytest.mark.unit
def test_agrar_chain_response_model_exact_shape() -> None:
    """Response-Builder ohne DB/MagicMock — exakt vier Felder."""
    from app.workspace.agrar_chain_router import AgrarChainOut, build_agrar_chain_response

    out = build_agrar_chain_response(
        contract_ref="K-42",
        source_model="kon",
        contract_status="OFFEN",
        disposition_status="FREIGEGEBEN",
    )
    assert isinstance(out, AgrarChainOut)
    payload = out.model_dump()
    assert list(payload.keys()) == ["contract_ref", "source_model", "next_step", "reason"]
    assert payload == {
        "contract_ref": "K-42",
        "source_model": "kon",
        "next_step": "waage",
        "reason": out.reason,
    }
    assert "abruf_freigegeben" in out.reason


@pytest.mark.unit
def test_agrar_chain_response_rejects_blank_ref() -> None:
    from app.workspace.agrar_chain_router import build_agrar_chain_response

    with pytest.raises(ValueError, match="contract_ref_required"):
        build_agrar_chain_response(contract_ref="  ", source_model="agrar")


@pytest.mark.unit
def test_hint_with_qs_unknown_keeps_next_step() -> None:
    from app.workspace.agrar_chain import hint_with_qs_unknown

    base = resolve_agrar_next_step(AgrarChainInput("A-1", "fulfilled"))
    marked = hint_with_qs_unknown(base)
    assert marked.next_step == base.next_step == NextStep.QUALITAET
    assert marked.reason == "qs_unbekannt"


def _isolated_agrar_chain_client():
    """TestClient nur auf dem Chain-Router — kein Full-App, kein MagicMock-DB."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from app.core.tenant import get_tenant_id
    from app.workspace.agrar_chain_router import router

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    def _no_db():
        yield None

    app.dependency_overrides[get_tenant_id] = lambda: "tenant-test"
    app.dependency_overrides[get_db] = _no_db
    return TestClient(app)


@pytest.mark.unit
def test_agrar_chain_http_get_isolated_router() -> None:
    client = _isolated_agrar_chain_client()
    response = client.get(
        "/api/v1/workspace/agrar-chain",
        params={
            "contract_ref": "K-1",
            "source_model": "kon",
            "contract_status": "OFFEN",
            "disposition_status": "FREIGEGEBEN",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"contract_ref", "source_model", "next_step", "reason"}
    assert body["next_step"] == "waage"
    assert body["source_model"] == "kon"


@pytest.mark.unit
def test_kon_http_progression_disposition_waage_qualitaet_abrechnung() -> None:
    """Kon-Pfad allein: disposition → waage → qualitaet → abrechnung am GET.

    quality_is_final kommt nur als Query-Projektion (kein Kon-QS-Join).
    """
    client = _isolated_agrar_chain_client()
    steps = [
        (
            {
                "contract_ref": "K-PROG",
                "source_model": "kon",
                "contract_status": "OFFEN",
            },
            "disposition",
        ),
        (
            {
                "contract_ref": "K-PROG",
                "source_model": "kon",
                "contract_status": "OFFEN",
                "disposition_status": "FREIGEGEBEN",
            },
            "waage",
        ),
        (
            {
                "contract_ref": "K-PROG",
                "source_model": "kon",
                "contract_status": "OFFEN",
                "disposition_status": "GELIEFERT",
            },
            "qualitaet",
        ),
        (
            {
                "contract_ref": "K-PROG",
                "source_model": "kon",
                "contract_status": "OFFEN",
                "disposition_status": "GELIEFERT",
                "quality_is_final": True,
            },
            "abrechnung",
        ),
    ]
    seen: list[str] = []
    for params, expected in steps:
        response = client.get("/api/v1/workspace/agrar-chain", params=params)
        assert response.status_code == 200
        body = response.json()
        assert set(body) == {"contract_ref", "source_model", "next_step", "reason"}
        assert body["contract_ref"] == "K-PROG"
        assert body["source_model"] == "kon"
        assert body["next_step"] == expected
        seen.append(body["next_step"])
    assert seen == ["disposition", "waage", "qualitaet", "abrechnung"]


@pytest.mark.unit
def test_agrar_http_progression_waage_qualitaet_abrechnung() -> None:
    """Agrar-Pfad allein (kein disposition): waage → qualitaet → abrechnung.

    abrechnung nur mit quality_is_final; fulfilled ohne QS bleibt qualitaet.
    """
    client = _isolated_agrar_chain_client()
    steps = [
        (
            {
                "contract_ref": "A-PROG",
                "source_model": "agrar",
                "contract_status": "open",
            },
            "waage",
        ),
        (
            {
                "contract_ref": "A-PROG",
                "source_model": "agrar",
                "contract_status": "fulfilled",
            },
            "qualitaet",
        ),
        (
            {
                "contract_ref": "A-PROG",
                "source_model": "agrar",
                "contract_status": "fulfilled",
                "quality_is_final": True,
            },
            "abrechnung",
        ),
    ]
    seen: list[str] = []
    for params, expected in steps:
        response = client.get("/api/v1/workspace/agrar-chain", params=params)
        assert response.status_code == 200
        body = response.json()
        assert body["source_model"] == "agrar"
        assert body["contract_ref"] == "A-PROG"
        assert body["next_step"] == expected
        seen.append(body["next_step"])
    assert seen == ["waage", "qualitaet", "abrechnung"]
    assert "disposition" not in seen


@pytest.mark.unit
def test_kon_http_skips_agrar_quality_db_lookup() -> None:
    """source_model=kon darf read_agrar_quality_is_final nicht anfassen."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from app.core.tenant import get_tenant_id
    from app.workspace import agrar_chain_router as chain_router
    from app.workspace.agrar_chain_router import router

    calls: list[str] = []

    def _spy(*_a, **_k):
        calls.append("read")
        return True

    original = chain_router.read_agrar_quality_is_final
    chain_router.read_agrar_quality_is_final = _spy  # type: ignore[assignment]
    try:
        app = FastAPI()
        app.include_router(router, prefix="/api/v1")

        def _no_db():
            yield object()

        app.dependency_overrides[get_tenant_id] = lambda: "tenant-test"
        app.dependency_overrides[get_db] = _no_db
        client = TestClient(app)
        response = client.get(
            "/api/v1/workspace/agrar-chain",
            params={
                "contract_ref": "K-NO-QS",
                "source_model": "kon",
                "contract_status": "OFFEN",
                "disposition_status": "GELIEFERT",
            },
        )
    finally:
        chain_router.read_agrar_quality_is_final = original  # type: ignore[assignment]

    assert response.status_code == 200
    assert response.json()["next_step"] == "qualitaet"
    assert calls == []


@pytest.mark.unit
def test_agrar_qs_lookup_failure_sets_qs_unbekannt_reason() -> None:
    """DB-Fehler: next_step ohne QS, reason qs_unbekannt — kein Fake-True."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from app.core.tenant import get_tenant_id
    from app.workspace import agrar_chain_router as chain_router
    from app.workspace.agrar_chain_router import router

    class _BoomDb:
        pass

    def _boom_db():
        yield _BoomDb()

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-test"
    app.dependency_overrides[get_db] = _boom_db

    def _raise(*_a, **_k):
        raise RuntimeError("qs read failed")

    original = chain_router.read_agrar_quality_is_final
    chain_router.read_agrar_quality_is_final = _raise  # type: ignore[assignment]
    try:
        client = TestClient(app)
        response = client.get(
            "/api/v1/workspace/agrar-chain",
            params={
                "contract_ref": "A-boom",
                "source_model": "agrar",
                "contract_status": "fulfilled",
            },
        )
    finally:
        chain_router.read_agrar_quality_is_final = original  # type: ignore[assignment]

    assert response.status_code == 200
    body = response.json()
    assert body["next_step"] == "qualitaet"
    assert body["reason"] == "qs_unbekannt"


def _seed_agrar_qs_probe_rows(
    db,
    *,
    tenant_id: str,
    marker: str,
    is_final: bool,
) -> tuple[str, str, str, str]:
    """Minimale Zeilen fuer Agrar-QS-Join. IDs: customer, contract, acceptance, protocol."""
    from datetime import date
    from decimal import Decimal

    from app.infrastructure.models import (
        AgrarContract,
        Customer,
        HarvestAcceptance,
        QualityProtocol,
    )

    customer_id = f"{marker}-cust"
    contract_id = f"{marker}-ctr"
    acceptance_id = f"{marker}-ha"
    protocol_id = f"{marker}-qp"
    db.add(
        Customer(
            id=customer_id,
            tenant_id=tenant_id,
            customer_number=marker[:50],
            company_name="WS Agrar QS Probe",
        )
    )
    db.add(
        AgrarContract(
            id=contract_id,
            tenant_id=tenant_id,
            contract_number=f"CTR-{marker}"[:50],
            contract_type="buy",
            harvest_year=2026,
            partner_id=f"{marker}-partner",
            article_id=f"{marker}-article",
            pricing_model="fixed",
            total_quantity_kg=Decimal("1000.000"),
            remaining_quantity_kg=Decimal("1000.000"),
            status="fulfilled",
        )
    )
    db.flush()
    db.add(
        HarvestAcceptance(
            id=acceptance_id,
            tenant_id=tenant_id,
            acceptance_number=f"HA-{marker}"[:50],
            delivery_date=date(2026, 10, 22),
            operator_id=f"{marker}-op",
            customer_id=customer_id,
            contract_id=contract_id,
        )
    )
    db.flush()
    db.add(
        QualityProtocol(
            id=protocol_id,
            tenant_id=tenant_id,
            harvest_acceptance_id=acceptance_id,
            protocol_number=f"QP-{marker}"[:50],
            version=1,
            is_final=is_final,
            source_type="manual",
        )
    )
    db.commit()
    return customer_id, contract_id, acceptance_id, protocol_id


def _cleanup_agrar_qs_probe_rows(
    db,
    *,
    customer_id: str,
    contract_id: str,
    acceptance_id: str,
    protocol_id: str,
) -> None:
    from app.infrastructure.models import (
        AgrarContract,
        Customer,
        HarvestAcceptance,
        QualityProtocol,
    )

    # Flush pro Zeile: sonst kann UoW Customer vor HarvestAcceptance loeschen.
    try:
        db.rollback()
    except Exception:
        pass
    for model, pk in (
        (QualityProtocol, protocol_id),
        (HarvestAcceptance, acceptance_id),
        (AgrarContract, contract_id),
        (Customer, customer_id),
    ):
        row = db.get(model, pk)
        if row is not None:
            db.delete(row)
            db.flush()
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def _probe_agrar_chain_http_client(*, tenant_id: str):
    """TestClient auf Chain-Router mit echter SessionLocal — kein MagicMock-DB."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.core.database import SessionLocal, get_db
    from app.core.tenant import get_tenant_id
    from app.workspace.agrar_chain_router import router

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    def _db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_tenant_id] = lambda: tenant_id
    app.dependency_overrides[get_db] = _db
    return TestClient(app)


@pytest.mark.integration
def test_read_agrar_quality_is_final_on_probe(require_db) -> None:
    """Join gegen valeo_probe: Negativ + eigener True/False-Pfad (nur eigene Zeilen)."""
    from uuid import uuid4

    from sqlalchemy.exc import IntegrityError

    from app.core.database import SessionLocal
    from app.infrastructure.models import QualityProtocol
    from app.workspace.agrar_chain import read_agrar_quality_is_final

    tenant_id = "00000000-0000-0000-0000-000000000001"
    marker = f"ws-agrar-qs-{uuid4().hex[:12]}"
    customer_id = f"{marker}-cust"
    contract_id = f"{marker}-ctr"
    acceptance_id = f"{marker}-ha"
    protocol_id = f"{marker}-qp"
    seeded = False

    db = SessionLocal()
    try:
        assert (
            read_agrar_quality_is_final(
                db,
                tenant_id=tenant_id,
                agrar_contract_id="missing-agrar-chain-contract-xyz",
            )
            is None
        )

        try:
            customer_id, contract_id, acceptance_id, protocol_id = _seed_agrar_qs_probe_rows(
                db, tenant_id=tenant_id, marker=marker, is_final=True
            )
            seeded = True
        except IntegrityError as exc:
            db.rollback()
            _cleanup_agrar_qs_probe_rows(
                db,
                customer_id=customer_id,
                contract_id=contract_id,
                acceptance_id=acceptance_id,
                protocol_id=protocol_id,
            )
            pytest.skip(
                "Insert blockiert durch Pflicht-FK/Constraint ausserhalb des "
                f"Agrar-QS-Join-Slices: {exc.orig}"
            )

        assert (
            read_agrar_quality_is_final(
                db, tenant_id=tenant_id, agrar_contract_id=contract_id
            )
            is True
        )

        protocol = db.get(QualityProtocol, protocol_id)
        assert protocol is not None
        protocol.is_final = False
        db.commit()
        assert (
            read_agrar_quality_is_final(
                db, tenant_id=tenant_id, agrar_contract_id=contract_id
            )
            is False
        )
    finally:
        try:
            if seeded:
                _cleanup_agrar_qs_probe_rows(
                    db,
                    customer_id=customer_id,
                    contract_id=contract_id,
                    acceptance_id=acceptance_id,
                    protocol_id=protocol_id,
                )
        finally:
            db.close()


@pytest.mark.integration
def test_agrar_http_qs_join_abrechnung_on_probe(require_db) -> None:
    """GET /workspace/agrar-chain: Agrar-QS-Join aus DB ohne Query-quality_is_final.

    Groesste Vertragsluecke Deliverable 7: Pure-Join und HTTP-Progression waren
    getrennt; hier der Draht Router → read_agrar_quality_is_final → Shape.
    Kein Kon-QS-Join. Waage-/Touren-Godfiles unberuehrt.
    """
    from uuid import uuid4

    from sqlalchemy.exc import IntegrityError

    from app.core.database import SessionLocal
    from app.infrastructure.models import QualityProtocol

    tenant_id = "00000000-0000-0000-0000-000000000001"
    marker = f"ws-agrar-http-{uuid4().hex[:12]}"
    customer_id = f"{marker}-cust"
    contract_id = f"{marker}-ctr"
    acceptance_id = f"{marker}-ha"
    protocol_id = f"{marker}-qp"
    seeded = False

    db = SessionLocal()
    try:
        try:
            customer_id, contract_id, acceptance_id, protocol_id = _seed_agrar_qs_probe_rows(
                db, tenant_id=tenant_id, marker=marker, is_final=True
            )
            seeded = True
        except IntegrityError as exc:
            db.rollback()
            _cleanup_agrar_qs_probe_rows(
                db,
                customer_id=customer_id,
                contract_id=contract_id,
                acceptance_id=acceptance_id,
                protocol_id=protocol_id,
            )
            pytest.skip(
                "Insert blockiert durch Pflicht-FK/Constraint ausserhalb des "
                f"Agrar-HTTP-QS-Slices: {exc.orig}"
            )

        client = _probe_agrar_chain_http_client(tenant_id=tenant_id)

        # Ohne quality_is_final-Query: Join liest is_final=True → abrechnung.
        response = client.get(
            "/api/v1/workspace/agrar-chain",
            params={
                "contract_ref": contract_id,
                "source_model": "agrar",
                "contract_status": "fulfilled",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert set(body) == {"contract_ref", "source_model", "next_step", "reason"}
        assert body["contract_ref"] == contract_id
        assert body["source_model"] == "agrar"
        assert body["next_step"] == "abrechnung"
        assert "qs" in body["reason"] or "settlement_offen" in body["reason"]

        protocol = db.get(QualityProtocol, protocol_id)
        assert protocol is not None
        protocol.is_final = False
        db.commit()

        # Join is_final=False: fulfilled bleibt qualitaet — kein Fake-abrechnung.
        response_open = client.get(
            "/api/v1/workspace/agrar-chain",
            params={
                "contract_ref": contract_id,
                "source_model": "agrar",
                "contract_status": "fulfilled",
            },
        )
        assert response_open.status_code == 200
        open_body = response_open.json()
        assert open_body["next_step"] == "qualitaet"
        assert open_body["reason"] != "qs_unbekannt"

        # Kon-Pfad mit derselben contract_ref: kein Agrar-Join → kein abrechnung.
        kon_response = client.get(
            "/api/v1/workspace/agrar-chain",
            params={
                "contract_ref": contract_id,
                "source_model": "kon",
                "contract_status": "OFFEN",
                "disposition_status": "GELIEFERT",
            },
        )
        assert kon_response.status_code == 200
        kon_body = kon_response.json()
        assert kon_body["source_model"] == "kon"
        assert kon_body["next_step"] == "qualitaet"
    finally:
        try:
            if seeded:
                _cleanup_agrar_qs_probe_rows(
                    db,
                    customer_id=customer_id,
                    contract_id=contract_id,
                    acceptance_id=acceptance_id,
                    protocol_id=protocol_id,
                )
        finally:
            db.close()


@pytest.mark.integration
def test_finalize_quality_protocol_writes_outbox_on_probe(require_db) -> None:
    """POST finalize: is_final + Outbox agrar.quality_protocol.completed (Workspace-Spiegel).

    Schliesst Deliverable-7-Luecke: Kernel-Event ohne Produktions-store_event.
    outbox.py unberuehrt — Aufruf aus quality_protocols.py wie weighing_tickets.
    """
    from uuid import uuid4

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from sqlalchemy.exc import IntegrityError

    from app.api.v1.endpoints import quality_protocols as qp_api
    from app.auth.deps import get_current_user
    from app.core.database import SessionLocal, get_db
    from app.core.tenant import get_tenant_id
    from app.infrastructure.eventbus.outbox import OutboxEvent
    from app.infrastructure.models import QualityProtocol

    tenant_id = "00000000-0000-0000-0000-000000000001"
    marker = f"ws-qs-outbox-{uuid4().hex[:12]}"
    customer_id = f"{marker}-cust"
    contract_id = f"{marker}-ctr"
    acceptance_id = f"{marker}-ha"
    protocol_id = f"{marker}-qp"
    seeded = False
    outbox_ids: list[str] = []

    db = SessionLocal()
    try:
        try:
            customer_id, contract_id, acceptance_id, protocol_id = _seed_agrar_qs_probe_rows(
                db, tenant_id=tenant_id, marker=marker, is_final=False
            )
            seeded = True
        except IntegrityError as exc:
            db.rollback()
            _cleanup_agrar_qs_probe_rows(
                db,
                customer_id=customer_id,
                contract_id=contract_id,
                acceptance_id=acceptance_id,
                protocol_id=protocol_id,
            )
            pytest.skip(
                "Insert blockiert durch Pflicht-FK/Constraint ausserhalb des "
                f"QS-Outbox-Slices: {exc.orig}"
            )

        app = FastAPI()
        app.include_router(qp_api.router, prefix="/api/v1/agrar/quality-protocols")

        def _db():
            session = SessionLocal()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_tenant_id] = lambda: tenant_id
        app.dependency_overrides[get_db] = _db
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "ws-qs-outbox-tester",
            "roles": ["admin", "AGRAR_BEARBEITEN"],
        }
        client = TestClient(app)

        response = client.post(
            f"/api/v1/agrar/quality-protocols/{protocol_id}/finalize",
            json={"approved_by": "ws-qs-outbox-tester"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == protocol_id
        assert body["is_final"] is True
        assert body["approved_by"] == "ws-qs-outbox-tester"

        db.expire_all()
        protocol = db.get(QualityProtocol, protocol_id)
        assert protocol is not None
        assert protocol.is_final is True

        events = (
            db.query(OutboxEvent)
            .filter(
                OutboxEvent.aggregate_id == protocol_id,
                OutboxEvent.event_type == "agrar.quality_protocol.completed",
                OutboxEvent.tenant_id == tenant_id,
            )
            .all()
        )
        assert len(events) == 1
        assert events[0].published is False
        outbox_ids = [events[0].id]

        conflict = client.post(
            f"/api/v1/agrar/quality-protocols/{protocol_id}/finalize",
            json={"approved_by": "ws-qs-outbox-tester"},
        )
        assert conflict.status_code == 409
    finally:
        try:
            for event_id in outbox_ids:
                row = db.get(OutboxEvent, event_id)
                if row is not None:
                    db.delete(row)
                    db.flush()
            if outbox_ids:
                db.commit()
            if seeded:
                _cleanup_agrar_qs_probe_rows(
                    db,
                    customer_id=customer_id,
                    contract_id=contract_id,
                    acceptance_id=acceptance_id,
                    protocol_id=protocol_id,
                )
        finally:
            db.close()
