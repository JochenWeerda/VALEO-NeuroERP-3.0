"""Pricing calculation endpoints with hierarchical cascade logic."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services import preisfindung_service as preis

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/pricing", tags=["pricing"])

# Alias-Prefix für Frontend-Konvention /preise/* — wird in api.py parallel eingebunden.



class PriceCalculationRequest(BaseModel):
    article_id: str
    customer_id: Optional[str] = None
    quantity: Decimal = Field(default=Decimal("1"), ge=Decimal("0"))
    contract_id: Optional[str] = None
    user_role: Optional[str] = None


class PriceCalculationResponse(BaseModel):
    """Der gefundene Preis und die Stufe, die ihn bestimmt hat."""

    list_price: Decimal
    discount: Decimal
    net_price: Decimal
    #: Eine der Stufen aus ``preisfindung_service.QUELLEN``.
    source: str
    price_list_id: Optional[str] = None
    contract_id: Optional[str] = None
    #: Gesetzt, wenn eine Mengenstaffel den Preis bestimmt hat.
    staffelrabatt_id: Optional[str] = None
    staffel_ab_menge: Optional[Decimal] = None
    #: Gesetzt, wenn ein Rabatt ausgeschlossen ist — mit dem Grund. Ein
    #: stillschweigender Rabatt von null waere nicht unterscheidbar von
    #: "kein Rabatt gefunden".
    rabatt_gesperrt: bool = False
    rabatt_sperrgrund: Optional[str] = None


@router.get("/calculate", response_model=PriceCalculationResponse, summary="Preis finden")
async def calculate_price(
    article_id: str = Query(..., description="Artikelkennung"),
    customer_id: Optional[str] = Query(None, description="Kundenkennung"),
    quantity: Decimal = Query(Decimal("1"), ge=Decimal("0"), description="Menge"),
    contract_id: Optional[str] = Query(None, description="Kontraktkennung"),
    user_role: Optional[str] = Query(None, description="Rolle fuer Mitarbeiterrabatte"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> PriceCalculationResponse:
    """Preisfindung in einer Kaskade — es gilt **eine** Stufe, nicht die Summe.

    Reihenfolge: Preisliste (ersetzt den Basispreis), dann Kontrakt, Mengenstaffel,
    Kundenrabatt, Rollenrabatt; sonst der Basispreis des Artikels.

    Bis zum 05.10.2026 kam der Mandant aus einem **Query-Parameter** mit
    Vorgabewert — wer ihn setzte, fragte fremde Preislisten ab; wer ihn wegliess,
    bekam stillschweigend die des Vorgabemandanten. Und drei der fuenf Stufen
    funktionierten nie: Der Kontraktrabatt las zwei Spalten, die es nicht gibt,
    der Rollenrabatt eine Tabelle, die es nicht gibt, und die gepflegten
    Mengenstaffeln wurden nicht gelesen. Jeder Fehlschlag lief in
    ``except: db.rollback()``, und heraus kam der volle Listenpreis mit
    ``source: "base"``.

    Jetzt ist ein Fehlschlag ein 503 mit der Stufe im Text: Wer einen Preis nicht
    vollstaendig ermitteln kann, darf keinen nennen.
    """
    artikel = preis.artikel_holen(db, tenant_id, article_id)

    list_price = Decimal(str(artikel["sales_price"] or 0))
    discount = Decimal("0")
    source = "base"
    price_list_id: Optional[str] = None
    contract_id_result: Optional[str] = None
    staffelrabatt_id: Optional[str] = None
    staffel_ab_menge: Optional[Decimal] = None

    # 1. Preisliste — ersetzt den Basispreis.
    try:
        position = preis.preisliste(db, tenant_id, artikel, quantity)
    except Exception as fehler:  # noqa: BLE001
        raise preis.stufe_nicht_lesbar(db, fehler, "price_list", tenant_id) from fehler
    if position:
        if position["unit_price"] is not None:
            list_price = Decimal(str(position["unit_price"]))
        if position["discount_percent"] is not None:
            discount = preis.pruefe_rabatt(
                Decimal(str(position["discount_percent"])), "price_list"
            )
        source = "price_list"
        price_list_id = position["price_list_id"]

    # 2. Kontrakt — eine Zusage geht jeder allgemeinen Regel vor.
    if contract_id:
        try:
            zeile = preis.kontraktpreis(db, tenant_id, contract_id, article_id)
        except Exception as fehler:  # noqa: BLE001
            raise preis.stufe_nicht_lesbar(db, fehler, "contract", tenant_id) from fehler
        if zeile:
            if zeile["unit_price"] is not None:
                list_price = Decimal(str(zeile["unit_price"]))
            discount = preis.pruefe_rabatt(
                Decimal(str(zeile["discount_pct"] or 0)), "contract"
            )
            source = "contract"
            contract_id_result = contract_id

    # 3. Mengenstaffel — haengt an der tatsaechlich bestellten Menge.
    #    Ein vereinbarter Kundenpreis wird erst danach gelesen (Stufe 4), weil er
    #    die Staffel verdraengt und nicht umgekehrt: Eine Zusage schlaegt eine
    #    allgemeine Mengenregel.
    if source in ("base", "price_list"):
        try:
            stufe = preis.staffel_stufe(db, tenant_id, artikel, quantity, customer_id)
        except Exception as fehler:  # noqa: BLE001
            raise preis.stufe_nicht_lesbar(db, fehler, "staffelrabatt", tenant_id) from fehler
        if stufe:
            if stufe["festpreis"] is not None:
                list_price = Decimal(str(stufe["festpreis"]))
                discount = Decimal("0")
            else:
                discount = preis.pruefe_rabatt(
                    Decimal(str(stufe["rabatt_prozent"] or 0)), "staffelrabatt"
                )
            source = "staffelrabatt"
            staffelrabatt_id = stufe["staffel_id"]
            staffel_ab_menge = Decimal(str(stufe["ab_menge"]))

    # 4. Kundenpreis und Kundenrabatt — vom Besonderen zum Allgemeinen.
    zusage = None
    if customer_id:
        from app.services.business_partner_service import BusinessPartnerService

        partner = BusinessPartnerService(db, tenant_id)
        artikelnummer = artikel.get("article_number")
        try:
            zusage = partner.get_customer_price_agreement(customer_id, artikelnummer)
        except Exception as fehler:  # noqa: BLE001
            raise preis.stufe_nicht_lesbar(db, fehler, "customer_price", tenant_id) from fehler
        if zusage and zusage.get("price_net") is not None and source != "contract":
            list_price = Decimal(str(zusage["price_net"]))
            discount = Decimal("0")
            source = "customer_price"

        if source in ("base", "price_list", "customer_price"):
            try:
                artikelrabatt = partner.get_customer_article_discount(
                    customer_id, artikelnummer
                )
            except Exception as fehler:  # noqa: BLE001
                raise preis.stufe_nicht_lesbar(
                    db, fehler, "customer_article_discount", tenant_id
                ) from fehler
            if artikelrabatt is not None:
                discount = preis.pruefe_rabatt(artikelrabatt, "customer_article_discount")
                source = "customer_article_discount"

        if source in ("base", "price_list"):
            try:
                kundenrabatt = partner.get_customer_discount(customer_id)
            except Exception as fehler:  # noqa: BLE001
                raise preis.stufe_nicht_lesbar(
                    db, fehler, "customer_discount", tenant_id
                ) from fehler
            if kundenrabatt is not None:
                discount = preis.pruefe_rabatt(kundenrabatt, "customer_discount")
                source = "customer_discount"

    # 5. Rollenrabatt.
    if source in ("base", "price_list") and user_role:
        try:
            rollenrabatt = preis.rollenrabatt(db, tenant_id, user_role)
        except Exception as fehler:  # noqa: BLE001
            raise preis.stufe_nicht_lesbar(
                db, fehler, "employee_discount", tenant_id
            ) from fehler
        if rollenrabatt is not None:
            discount = preis.pruefe_rabatt(rollenrabatt, "employee_discount")
            source = "employee_discount"

    # Die Sperren des Bestands, die die Kaskade nie gelesen hat.
    erlaubt, sperrgrund = preis.rabatt_erlaubt(artikel, zusage)
    if not erlaubt and discount > 0:
        discount = Decimal("0")
        source = "customer_price" if source == "customer_price" else source

    net_price = (list_price * (Decimal("1") - discount / Decimal("100"))).quantize(
        Decimal("0.0001")
    )
    return PriceCalculationResponse(
        list_price=list_price,
        discount=discount,
        net_price=net_price,
        source=source,
        price_list_id=price_list_id,
        contract_id=contract_id_result,
        staffelrabatt_id=staffelrabatt_id,
        staffel_ab_menge=staffel_ab_menge,
        rabatt_gesperrt=not erlaubt,
        rabatt_sperrgrund=sperrgrund,
    )


@router.get(
    "/find",
    response_model=PriceCalculationResponse,
    summary="Preisfindung (Frontend-Alias fuer /calculate)",
)
async def find_price(
    article_id: str = Query(...),
    customer_id: Optional[str] = Query(None),
    quantity: Decimal = Query(Decimal("1"), ge=Decimal("0")),
    contract_id: Optional[str] = Query(None),
    user_role: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> PriceCalculationResponse:
    """Frontend-Alias fuer /pricing/calculate — dieselbe Kaskade."""
    return await calculate_price(
        article_id=article_id,
        customer_id=customer_id,
        quantity=quantity,
        contract_id=contract_id,
        user_role=user_role,
        tenant_id=tenant_id,
        db=db,
    )


# ---------------------------------------------------------------------------
# Staffelrabatte  GET/POST /pricing/staffelrabatte
# ---------------------------------------------------------------------------

class StaffelStufe(BaseModel):
    ab_menge: Decimal = Field(..., ge=Decimal("0"), description="Ab dieser Menge gilt der Rabatt")
    rabatt_prozent: Optional[Decimal] = Field(None, description="Rabatt in Prozent")
    festpreis: Optional[Decimal] = Field(None, description="Festpreis statt Rabatt")


class StaffelrabattIn(BaseModel):
    artikel_id: Optional[str] = Field(None)
    artikel_ids: Optional[list[str]] = Field(None, description="Mehrere Artikel gleichzeitig zuordnen (M2M)")
    artikelgruppe: Optional[str] = Field(None)
    kunden_id: Optional[str] = Field(None)
    kundengruppe: Optional[str] = Field(None)
    gueltig_von: Optional[str] = Field(None)
    gueltig_bis: Optional[str] = Field(None)
    stufen: list[StaffelStufe] = Field(..., min_length=1)
    bezeichnung: Optional[str] = Field(None)


class StaffelrabattOut(BaseModel):
    id: str
    artikel_id: Optional[str]
    artikel_ids: list[str] = Field(default_factory=list)
    artikelgruppe: Optional[str]
    kunden_id: Optional[str]
    kundengruppe: Optional[str]
    gueltig_von: Optional[str]
    gueltig_bis: Optional[str]
    stufen: list[StaffelStufe]
    bezeichnung: Optional[str]
    tenant_id: str
    status: str


@router.get(
    "/staffelrabatte",
    response_model=list[StaffelrabattOut],
    summary="Staffelrabatte auflisten",
)
async def list_staffelrabatte(
    artikel_id: Optional[str] = Query(None),
    kunden_id: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[StaffelrabattOut]:
    """Staffelrabatte abfragen — filterbar nach Artikel und Kunde."""
    import json as _json

    conditions = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id}
    if artikel_id:
        conditions.append("artikel_id = :artikel_id")
        params["artikel_id"] = artikel_id
    if kunden_id:
        conditions.append("kunden_id = :kunden_id")
        params["kunden_id"] = kunden_id

    where = " AND ".join(conditions)
    rows = db.execute(
        text(f"SELECT * FROM domain_pricing.staffelrabatte WHERE {where} ORDER BY created_at DESC"),  # nosec B608  # where besteht nur aus festen Literalen dieser Funktion, alle Werte via Bind-Params
        params,
    ).mappings().all()

    ids = [r["id"] for r in rows]
    artikel_ids_by_staffel: dict[str, list[str]] = {i: [] for i in ids}
    if ids:
        m2m_rows = db.execute(
            text("""
                SELECT staffelrabatt_id, artikel_id FROM domain_pricing.staffelrabatt_artikel
                WHERE tenant_id = :tenant_id AND staffelrabatt_id = ANY(:ids)
            """),
            {"tenant_id": tenant_id, "ids": ids},
        ).mappings().all()
        for m in m2m_rows:
            artikel_ids_by_staffel.setdefault(m["staffelrabatt_id"], []).append(m["artikel_id"])

    result = []
    for r in rows:
        stufen_raw = r["stufen"]
        if isinstance(stufen_raw, str):
            stufen_raw = _json.loads(stufen_raw)
        result.append(
            StaffelrabattOut(
                id=r["id"],
                artikel_id=r.get("artikel_id"),
                artikel_ids=artikel_ids_by_staffel.get(r["id"], []),
                artikelgruppe=r.get("artikelgruppe"),
                kunden_id=r.get("kunden_id"),
                kundengruppe=r.get("kundengruppe"),
                gueltig_von=str(r["gueltig_von"]) if r.get("gueltig_von") else None,
                gueltig_bis=str(r["gueltig_bis"]) if r.get("gueltig_bis") else None,
                stufen=[StaffelStufe(**s) for s in stufen_raw],
                bezeichnung=r.get("bezeichnung"),
                tenant_id=r["tenant_id"],
                status=r.get("status", "aktiv"),
            )
        )
    return result


@router.post(
    "/staffelrabatte",
    response_model=StaffelrabattOut,
    status_code=201,
    summary="Staffelrabatt anlegen",
)
async def create_staffelrabatt(
    payload: StaffelrabattIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> StaffelrabattOut:
    """Staffelrabatt anlegen (Mengen-/Preisstufen für Artikel oder Artikelgruppe)."""
    import json as _json
    from uuid import uuid4 as _uuid4

    if not payload.artikel_id and not payload.artikelgruppe:
        raise HTTPException(status_code=422, detail="artikel_id oder artikelgruppe erforderlich")

    new_id = str(_uuid4())
    stufen_json = _json.dumps([s.model_dump(mode="json") for s in payload.stufen])

    try:
        db.execute(
            text("""
                INSERT INTO domain_pricing.staffelrabatte
                    (id, tenant_id, artikel_id, artikelgruppe, kunden_id, kundengruppe,
                     gueltig_von, gueltig_bis, stufen, bezeichnung, status)
                VALUES
                    (:id, :tenant_id, :artikel_id, :artikelgruppe, :kunden_id, :kundengruppe,
                     :gueltig_von, :gueltig_bis, CAST(:stufen AS jsonb), :bezeichnung, 'aktiv')
            """),
            {
                "id": new_id,
                "tenant_id": tenant_id,
                "artikel_id": payload.artikel_id,
                "artikelgruppe": payload.artikelgruppe,
                "kunden_id": payload.kunden_id,
                "kundengruppe": payload.kundengruppe,
                "gueltig_von": payload.gueltig_von,
                "gueltig_bis": payload.gueltig_bis,
                "stufen": stufen_json,
                "bezeichnung": payload.bezeichnung,
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return StaffelrabattOut(
        id=new_id,
        artikel_id=payload.artikel_id,
        artikelgruppe=payload.artikelgruppe,
        kunden_id=payload.kunden_id,
        kundengruppe=payload.kundengruppe,
        gueltig_von=payload.gueltig_von,
        gueltig_bis=payload.gueltig_bis,
        stufen=payload.stufen,
        bezeichnung=payload.bezeichnung,
        tenant_id=tenant_id,
        status="aktiv",
    )

