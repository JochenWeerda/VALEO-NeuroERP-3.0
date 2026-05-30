"""
Kundenportal Shop API Endpunkte

Stellt Produkte mit Kontrakt- und Vorkauf-Informationen
für das Kundenportal bereit.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from app.core.uuid7 import uuid7_short_suffix

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import get_user_id_from_request
from sqlalchemy import and_, or_, desc

from app.core.database import get_db
from app.services.customer_sales_eligibility import assert_customer_allowed_for_sales_order
from app.core.config import settings
from app.infrastructure.models import Article as ArticleModel, Customer as CustomerModel
from app.infrastructure.models.portal_models import (
    CustomerContract, CustomerPrePurchase, 
    CustomerOrder, CustomerOrderItem, CustomerOrderHistory,
    ContractStatus as DBContractStatus, OrderStatus as DBOrderStatus,
    ORDER_STATUS_TRANSITIONS, validate_order_transition,
)
from app.api.v1.schemas.portal import (
    PortalProduct, PortalProductList, LastOrderInfo,
    ContractStatus, OrderStatus, PriceSource,
    OrderCreate, OrderResponse, OrderItemResponse,
    OrderList, OrderListItem
)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.portal_shop_schemas import PortalShopOut


router = APIRouter()


def get_customer_id_from_token(request: Request, tenant_id: str) -> str:
    """
    Extrahiert Kunden-ID aus JWT (token_claims.sub) oder X-User-ID.
    Im Portal-Kontext ist sub bzw. X-User-ID oft die Kunden-/Partner-ID.
    """
    uid = get_user_id_from_request(request)
    if uid and uid not in ("system", "dev-user"):
        return uid
    return "customer-demo-001"


@router.get("/products", response_model=PortalProductList, summary="Portal products abrufen")
async def get_portal_products(
    request: Request,
    tenant_id: str = Query(..., description="Mandanten-ID"),
    customer_id: Optional[str] = Query(None, description="Kunden-ID (falls nicht aus Token)"),
    kategorie: Optional[str] = Query(None, description="Filter nach Kategorie"),
    search: Optional[str] = Query(None, description="Suchbegriff"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Liefert Produkte für das Kundenportal mit Kontrakt- und Vorkauf-Informationen.
    
    Produkte werden angereichert mit:
    - Kontrakt-Status und -Preise falls Rahmenvertrag existiert
    - Vorkauf-Guthaben falls vorhanden
    - Letzte Bestellung für "Erneut bestellen" Funktion
    """
    effective_customer = customer_id or get_customer_id_from_token(request, tenant_id)
    
    # Basis-Query für Artikel
    query = db.query(ArticleModel).filter(
        and_(
            ArticleModel.tenant_id == tenant_id,
            ArticleModel.is_active == True
        )
    )
    
    # Filter nach Kategorie
    if kategorie and kategorie != "alle":
        query = query.filter(ArticleModel.category == kategorie)
    
    # Suche
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                ArticleModel.name.ilike(like),
                ArticleModel.article_number.ilike(like),
                ArticleModel.barcode.ilike(like)
            )
        )
    
    total = query.count()
    articles = query.offset(skip).limit(limit).all()
    
    # Lade Kontrakte für diesen Kunden
    contracts = db.query(CustomerContract).filter(
        and_(
            CustomerContract.tenant_id == tenant_id,
            CustomerContract.customer_id == effective_customer,
            CustomerContract.status != DBContractStatus.EXHAUSTED,
            CustomerContract.valid_until >= datetime.utcnow()
        )
    ).all()
    contract_by_article = {c.article_id: c for c in contracts}
    
    # Lade Vorkäufe für diesen Kunden
    pre_purchases = db.query(CustomerPrePurchase).filter(
        and_(
            CustomerPrePurchase.tenant_id == tenant_id,
            CustomerPrePurchase.customer_id == effective_customer,
            CustomerPrePurchase.is_active == True,
            CustomerPrePurchase.remaining_quantity > 0
        )
    ).all()
    pre_purchase_by_article = {pp.article_id: pp for pp in pre_purchases}
    
    # Lade Bestellhistorie (letzte 42 Tage)
    cutoff_date = datetime.utcnow() - timedelta(days=42)
    order_history = db.query(CustomerOrderHistory).filter(
        and_(
            CustomerOrderHistory.tenant_id == tenant_id,
            CustomerOrderHistory.customer_id == effective_customer,
            CustomerOrderHistory.last_order_date >= cutoff_date
        )
    ).all()
    history_by_article = {h.article_id: h for h in order_history}
    
    # Baue Portal-Produkte
    products = []
    has_contracts = 0
    has_pre_purchases = 0
    
    for article in articles:
        contract = contract_by_article.get(article.id)
        pre_purchase = pre_purchase_by_article.get(article.id)
        history = history_by_article.get(article.id)
        
        # Letzte Bestellung
        last_order = None
        if history:
            last_order = LastOrderInfo(
                datum=history.last_order_date,
                menge=history.last_order_quantity,
                unit=article.unit
            )
        
        # Kontrakt-Status ermitteln
        contract_status = ContractStatus.NONE
        contract_price = None
        contract_total = None
        contract_remaining = None
        
        if contract:
            has_contracts += 1
            contract_status = ContractStatus(contract.status.value)
            contract_price = contract.contract_price
            contract_total = contract.total_quantity
            contract_remaining = contract.remaining_quantity
        
        # Vorkauf-Daten
        is_pre_purchase = False
        pp_price = None
        pp_total = None
        pp_remaining = None
        
        if pre_purchase:
            has_pre_purchases += 1
            is_pre_purchase = True
            pp_price = pre_purchase.pre_purchase_price
            pp_total = pre_purchase.total_quantity
            pp_remaining = pre_purchase.remaining_quantity
        
        product = PortalProduct(
            id=article.id,
            artikelnummer=article.article_number,
            name=article.name,
            kategorie=article.category or "sonstiges",
            beschreibung=article.description,
            einheit=article.unit,
            preis=article.sales_price,
            rabattPreis=round(
                float(article.sales_price) * (1 - float(article.rabatt_auftrag_rechnung) / 100), 2
            ) if getattr(article, "rabatt_auftrag_rechnung", None) and article.sales_price else None,
            verfuegbar=article.available_stock > 0,
            bestand=article.available_stock,
            zertifikate=[c for c in [
                "Bio" if getattr(article, "bio_kennzeichnung", False) else None,
                "GMP+" if getattr(article, "gmp_plus_relevanz", False) else None,
                "Vegan" if getattr(article, "kennzeichnung_vegan", None) == "Ja" else None,
                "Vegetarisch" if getattr(article, "kennzeichnung_vegetarisch", None) == "Ja" else None,
            ] if c],
            letzteBestellung=last_order,
            contractStatus=contract_status,
            contractPrice=contract_price,
            contractTotalQty=contract_total,
            contractRemainingQty=contract_remaining,
            isPrePurchase=is_pre_purchase,
            prePurchasePrice=pp_price,
            prePurchaseTotalQty=pp_total,
            prePurchaseRemainingQty=pp_remaining
        )
        products.append(product)
    
    # Sortierung: Vorkäufe zuerst, dann Kontrakte, dann kürzlich bestellt
    def sort_key(p: PortalProduct):
        score = 0
        if p.is_pre_purchase:
            score += 1000
        if p.contract_status != ContractStatus.NONE:
            score += 500
        if p.letzte_bestellung:
            days_ago = (datetime.utcnow() - p.letzte_bestellung.datum).days
            score += max(0, 100 - days_ago)
        return -score
    
    products.sort(key=sort_key)
    
    return PortalProductList(
        items=products,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        has_contracts=has_contracts,
        has_pre_purchases=has_pre_purchases
    )


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Order anlegen")
async def create_order(
    request: Request,
    order_data: OrderCreate,
    tenant_id: str = Query(..., description="Mandanten-ID"),
    customer_id: Optional[str] = Query(None, description="Kunden-ID"),
    db: Session = Depends(get_db)
):
    """
    Erstellt eine neue Bestellung aus dem Kundenportal.
    
    Berücksichtigt automatisch:
    - Vorkauf-Guthaben (wird zuerst verwendet)
    - Kontrakt-Preise (falls verfügbar)
    - Listenpreise (als Fallback)
    
    Idempotency: Header X-Idempotency-Key verhindert doppelte Bestellungen.
    """
    effective_customer = customer_id or get_customer_id_from_token(request, tenant_id)

    # C3: Idempotency — gleicher Key liefert die vorhandene Bestellung zurück
    idempotency_key = request.headers.get("X-Idempotency-Key")
    if idempotency_key:
        existing_order = db.query(CustomerOrder).filter(
            and_(
                CustomerOrder.tenant_id == tenant_id,
                CustomerOrder.customer_id == effective_customer,
                CustomerOrder.idempotency_key == idempotency_key,
            )
        ).first()
        if existing_order:
            items = db.query(CustomerOrderItem).filter(
                CustomerOrderItem.order_id == existing_order.id
            ).all()
            return OrderResponse(
                id=existing_order.id,
                order_number=existing_order.order_number,
                order_date=existing_order.order_date,
                status=OrderStatus(existing_order.status.value),
                customer_id=existing_order.customer_id,
                customer_name=existing_order.customer_name,
                items=[
                    OrderItemResponse(
                        id=item.id,
                        article_id=item.article_id,
                        artikel_nummer=item.article_number,
                        name=item.article_name,
                        quantity=item.quantity,
                        einheit=item.unit,
                        unit_price=item.unit_price,
                        total_price=item.total_price,
                        price_source=PriceSource(item.price_source),
                        quantity_from_credit=item.quantity_from_credit,
                        quantity_at_list_price=item.quantity_at_list_price
                    )
                    for item in items
                ],
                total_net=existing_order.total_net,
                total_gross=existing_order.total_gross,
                delivery_address=existing_order.delivery_address,
                delivery_date_requested=existing_order.delivery_date_requested,
                customer_notes=existing_order.customer_notes,
                created_at=existing_order.created_at
            )

    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bestellung enthält keine Positionen"
        )

    if not effective_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kundenkontext fehlt (Anmeldung / customer_id)",
        )
    assert_customer_allowed_for_sales_order(db, tenant_id, effective_customer)

    # Lade Kundendaten aus CRM
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == effective_customer,
        CustomerModel.tenant_id == tenant_id,
    ).first()
    customer_name = customer.company_name if customer else "Unbekannter Kunde"
    customer_number = customer.customer_number if customer else f"K-{effective_customer[:8].upper()}"
    
    # Generiere Bestellnummer
    order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{uuid7_short_suffix()}"
    
    # Erstelle Bestellung
    order = CustomerOrder(
        tenant_id=tenant_id,
        customer_id=effective_customer,
        customer_number=customer_number,
        customer_name=customer_name,
        order_number=order_number,
        status=DBOrderStatus.SUBMITTED,
        delivery_address=order_data.delivery_address,
        delivery_date_requested=order_data.delivery_date_requested,
        customer_notes=order_data.customer_notes,
        idempotency_key=idempotency_key,
    )
    
    db.add(order)
    db.flush()  # ID generieren
    
    total_net = Decimal("0")
    order_items = []
    
    for item_data in order_data.items:
        # Lade Artikel
        article = db.query(ArticleModel).filter(
            and_(
                ArticleModel.id == item_data.article_id,
                ArticleModel.tenant_id == tenant_id
            )
        ).first()
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artikel {item_data.article_id} nicht gefunden"
            )
        
        # Prüfe Vorkauf
        pre_purchase = db.query(CustomerPrePurchase).filter(
            and_(
                CustomerPrePurchase.article_id == item_data.article_id,
                CustomerPrePurchase.customer_id == effective_customer,
                CustomerPrePurchase.is_active == True,
                CustomerPrePurchase.remaining_quantity > 0
            )
        ).first()
        
        # Prüfe Kontrakt
        contract = db.query(CustomerContract).filter(
            and_(
                CustomerContract.article_id == item_data.article_id,
                CustomerContract.customer_id == effective_customer,
                CustomerContract.status != DBContractStatus.EXHAUSTED,
                CustomerContract.valid_until >= datetime.utcnow()
            )
        ).first()
        
        # Berechne Preise und Mengen
        quantity = item_data.quantity
        quantity_from_credit = Decimal("0")
        quantity_at_list = Decimal("0")
        unit_price = article.sales_price
        price_source = PriceSource.LIST
        
        if pre_purchase and pre_purchase.remaining_quantity > 0:
            # Vorkauf hat Priorität
            credit_qty = min(quantity, pre_purchase.remaining_quantity)
            quantity_from_credit = credit_qty
            quantity_at_list = quantity - credit_qty
            
            # Vorkauf-Guthaben reduzieren
            pre_purchase.remaining_quantity -= credit_qty
            
            unit_price = Decimal("0") if quantity_at_list == 0 else article.sales_price
            price_source = PriceSource.PRE_PURCHASE
            
        elif contract and contract.remaining_quantity > 0:
            # Kontrakt verwenden
            contract_qty = min(quantity, contract.remaining_quantity)
            
            # Kontrakt-Menge reduzieren
            contract.remaining_quantity -= contract_qty
            contract.status = contract.calculate_status()
            
            unit_price = contract.contract_price
            price_source = PriceSource.CONTRACT
        
        # Gesamtpreis berechnen
        # Bei Vorkauf: Nur der Teil über das Guthaben hinaus kostet
        if price_source == PriceSource.PRE_PURCHASE:
            total_price = quantity_at_list * article.sales_price
        else:
            total_price = quantity * unit_price
        
        total_net += total_price
        
        # Bestellposition erstellen
        order_item = CustomerOrderItem(
            order_id=order.id,
            article_id=article.id,
            article_number=article.article_number,
            article_name=article.name,
            quantity=quantity,
            unit=article.unit,
            unit_price=unit_price,
            total_price=total_price,
            price_source=price_source.value,
            contract_id=contract.id if contract and price_source == PriceSource.CONTRACT else None,
            pre_purchase_id=pre_purchase.id if pre_purchase and price_source == PriceSource.PRE_PURCHASE else None,
            quantity_from_credit=quantity_from_credit,
            quantity_at_list_price=quantity_at_list
        )
        
        db.add(order_item)
        order_items.append(order_item)
        
        # Bestellhistorie aktualisieren
        history = db.query(CustomerOrderHistory).filter(
            and_(
                CustomerOrderHistory.article_id == article.id,
                CustomerOrderHistory.customer_id == effective_customer
            )
        ).first()
        
        if history:
            history.last_order_date = datetime.utcnow()
            history.last_order_quantity = quantity
            history.last_order_id = order.id
            history.total_orders += 1
            history.total_quantity += quantity
            history.average_quantity = history.total_quantity / history.total_orders
        else:
            history = CustomerOrderHistory(
                tenant_id=tenant_id,
                customer_id=effective_customer,
                article_id=article.id,
                last_order_date=datetime.utcnow(),
                last_order_quantity=quantity,
                last_order_id=order.id,
                total_orders=1,
                total_quantity=quantity,
                average_quantity=quantity
            )
            db.add(history)
    
    # Bestellung finalisieren
    order.total_net = total_net
    order.total_gross = total_net * Decimal(str(1 + settings.DEFAULT_VAT_RATE))

    # C1: Expliziter Rollback bei Fehler — kein Success-Response ohne erfolgreichen Commit
    try:
        db.commit()
        db.refresh(order)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bestellung konnte nicht gespeichert werden: {exc}",
        ) from exc
    
    # Response bauen
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        order_date=order.order_date,
        status=OrderStatus(order.status.value),
        customer_id=order.customer_id,
        customer_name=order.customer_name,
        items=[
            OrderItemResponse(
                id=item.id,
                article_id=item.article_id,
                artikel_nummer=item.article_number,
                name=item.article_name,
                quantity=item.quantity,
                einheit=item.unit,
                unit_price=item.unit_price,
                total_price=item.total_price,
                price_source=PriceSource(item.price_source),
                quantity_from_credit=item.quantity_from_credit,
                quantity_at_list_price=item.quantity_at_list_price
            )
            for item in order_items
        ],
        total_net=order.total_net,
        total_gross=order.total_gross,
        delivery_address=order.delivery_address,
        delivery_date_requested=order.delivery_date_requested,
        customer_notes=order.customer_notes,
        created_at=order.created_at
    )


@router.get("/orders", response_model=OrderList, summary="Orders auflisten")
async def list_orders(
    request: Request,
    tenant_id: str = Query(..., description="Mandanten-ID"),
    customer_id: Optional[str] = Query(None, description="Kunden-ID"),
    status_filter: Optional[OrderStatus] = Query(None, description="Filter nach Status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Listet Bestellungen des Kunden"""
    effective_customer = customer_id or get_customer_id_from_token(request, tenant_id)
    
    query = db.query(CustomerOrder).filter(
        and_(
            CustomerOrder.tenant_id == tenant_id,
            CustomerOrder.customer_id == effective_customer
        )
    )
    
    if status_filter:
        query = query.filter(CustomerOrder.status == DBOrderStatus(status_filter.value))
    
    query = query.order_by(desc(CustomerOrder.order_date))
    
    total = query.count()
    orders = query.offset(skip).limit(limit).all()
    
    items = []
    for order in orders:
        # Lade erste Position für Haupt-Artikel
        first_item = db.query(CustomerOrderItem).filter(
            CustomerOrderItem.order_id == order.id
        ).first()
        
        item_count = db.query(CustomerOrderItem).filter(
            CustomerOrderItem.order_id == order.id
        ).count()
        
        items.append(OrderListItem(
            id=order.id,
            order_number=order.order_number,
            order_date=order.order_date,
            status=OrderStatus(order.status.value),
            item_count=item_count,
            total_net=order.total_net,
            main_article=first_item.article_name if first_item else "Keine Artikel"
        ))
    
    return OrderList(
        items=items,
        total=total,
        page=(skip // limit) + 1,
        size=limit
    )


@router.get("/orders/{order_id}", response_model=OrderResponse, summary="Order abrufen")
async def get_order(
    request: Request,
    order_id: str,
    tenant_id: str = Query(..., description="Mandanten-ID"),
    customer_id: Optional[str] = Query(None, description="Kunden-ID"),
    db: Session = Depends(get_db)
):
    """Liefert Details einer Bestellung"""
    effective_customer = customer_id or get_customer_id_from_token(request, tenant_id)
    
    order = db.query(CustomerOrder).filter(
        and_(
            CustomerOrder.id == order_id,
            CustomerOrder.tenant_id == tenant_id,
            CustomerOrder.customer_id == effective_customer
        )
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestellung nicht gefunden"
        )
    
    items = db.query(CustomerOrderItem).filter(
        CustomerOrderItem.order_id == order.id
    ).all()
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        order_date=order.order_date,
        status=OrderStatus(order.status.value),
        customer_id=order.customer_id,
        customer_name=order.customer_name,
        items=[
            OrderItemResponse(
                id=item.id,
                article_id=item.article_id,
                artikel_nummer=item.article_number,
                name=item.article_name,
                quantity=item.quantity,
                einheit=item.unit,
                unit_price=item.unit_price,
                total_price=item.total_price,
                price_source=PriceSource(item.price_source),
                quantity_from_credit=item.quantity_from_credit,
                quantity_at_list_price=item.quantity_at_list_price
            )
            for item in items
        ],
        total_net=order.total_net,
        total_gross=order.total_gross,
        delivery_address=order.delivery_address,
        delivery_date_requested=order.delivery_date_requested,
        customer_notes=order.customer_notes,
        created_at=order.created_at
    )


@router.get("/contracts", response_model=list[PortalShopOut], summary="Contracts auflisten")
async def list_contracts(
    request: Request,
    tenant_id: str = Query(..., description="Mandanten-ID"),
    customer_id: Optional[str] = Query(None, description="Kunden-ID"),
    db: Session = Depends(get_db)
):
    """Listet alle aktiven Kontrakte des Kunden"""
    effective_customer = customer_id or get_customer_id_from_token(request, tenant_id)
    
    contracts = db.query(CustomerContract).filter(
        and_(
            CustomerContract.tenant_id == tenant_id,
            CustomerContract.customer_id == effective_customer,
            CustomerContract.valid_until >= datetime.utcnow()
        )
    ).order_by(CustomerContract.valid_until).all()
    
    return [
        {
            "id": c.id,
            "contract_number": c.contract_number,
            "article_name": c.article_name,
            "article_number": c.article_number,
            "contract_price": float(c.contract_price),
            "list_price": float(c.list_price),
            "unit": c.unit,
            "total_quantity": float(c.total_quantity),
            "remaining_quantity": float(c.remaining_quantity),
            "status": c.status.value,
            "valid_until": c.valid_until.isoformat()
        }
        for c in contracts
    ]


@router.get("/pre-purchases", response_model=list[PortalShopOut], summary="Pre purchases auflisten")
async def list_pre_purchases(
    request: Request,
    tenant_id: str = Query(..., description="Mandanten-ID"),
    customer_id: Optional[str] = Query(None, description="Kunden-ID"),
    db: Session = Depends(get_db)
):
    """Listet alle aktiven Vorkäufe/Guthaben des Kunden"""
    effective_customer = customer_id or get_customer_id_from_token(request, tenant_id)
    
    pre_purchases = db.query(CustomerPrePurchase).filter(
        and_(
            CustomerPrePurchase.tenant_id == tenant_id,
            CustomerPrePurchase.customer_id == effective_customer,
            CustomerPrePurchase.is_active == True,
            CustomerPrePurchase.remaining_quantity > 0
        )
    ).all()
    
    return [
        {
            "id": pp.id,
            "pre_purchase_number": pp.pre_purchase_number,
            "article_name": pp.article_name,
            "article_number": pp.article_number,
            "pre_purchase_price": float(pp.pre_purchase_price),
            "current_list_price": float(pp.current_list_price),
            "unit": pp.unit,
            "total_quantity": float(pp.total_quantity),
            "remaining_quantity": float(pp.remaining_quantity),
            "payment_date": pp.payment_date.isoformat(),
            "valid_until": pp.valid_until.isoformat() if pp.valid_until else None
        }
        for pp in pre_purchases
    ]


@router.patch("/orders/{order_id}/status", summary="Order status aktualisieren",
    response_model=PortalShopOut
)
async def update_order_status(
    request: Request,
    order_id: str,
    new_status: str = Query(..., description="Neuer Status"),
    tenant_id: str = Query(..., description="Mandanten-ID"),
    internal_notes: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    C2: Ändert den Bestellstatus mit validiertem Zustandsübergang.
    Erlaubte Übergänge: DRAFT→SUBMITTED→CONFIRMED→IN_PROGRESS→SHIPPED→DELIVERED.
    CANCELLED ist von jedem aktiven Status aus erreichbar (außer DELIVERED/CANCELLED).
    """
    order = db.query(CustomerOrder).filter(
        and_(
            CustomerOrder.id == order_id,
            CustomerOrder.tenant_id == tenant_id,
        )
    ).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bestellung nicht gefunden")

    try:
        target = DBOrderStatus(new_status)
    except ValueError:
        valid = [s.value for s in DBOrderStatus]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ungültiger Status '{new_status}'. Erlaubt: {valid}",
        )

    if not validate_order_transition(order.status, target):
        allowed = [s.value for s in ORDER_STATUS_TRANSITIONS.get(order.status, [])]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Übergang {order.status.value} → {target.value} nicht erlaubt. Erlaubt: {allowed}",
        )

    old_status = order.status.value
    order.status = target
    if internal_notes:
        order.internal_notes = (order.internal_notes or "") + f"\n[{old_status}→{target.value}] {internal_notes}"

    db.commit()
    db.refresh(order)

    return {
        "id": order.id,
        "order_number": order.order_number,
        "old_status": old_status,
        "new_status": order.status.value,
        "allowed_next": [s.value for s in ORDER_STATUS_TRANSITIONS.get(order.status, [])],
    }


@router.get("/orders/reconciliation", summary="Orders reconcile",
    response_model=PortalShopOut
)
async def reconcile_orders(
    tenant_id: str = Query(..., description="Mandanten-ID"),
    stale_hours: int = Query(48, ge=1, le=720, description="Stunden ohne Statusänderung"),
    db: Session = Depends(get_db),
):
    """
    C4: Reconciliation — findet Bestellungen in inkonsistentem Zustand.
    - SUBMITTED seit > stale_hours ohne Bestätigung
    - CONFIRMED seit > stale_hours ohne Bearbeitung
    - Orders ohne Positionen
    """

    cutoff = datetime.utcnow() - timedelta(hours=stale_hours)

    stale_submitted = db.query(CustomerOrder).filter(
        and_(
            CustomerOrder.tenant_id == tenant_id,
            CustomerOrder.status == DBOrderStatus.SUBMITTED,
            CustomerOrder.created_at < cutoff,
        )
    ).count()

    stale_confirmed = db.query(CustomerOrder).filter(
        and_(
            CustomerOrder.tenant_id == tenant_id,
            CustomerOrder.status == DBOrderStatus.CONFIRMED,
            CustomerOrder.created_at < cutoff,
        )
    ).count()

    empty_orders = (
        db.query(CustomerOrder)
        .outerjoin(CustomerOrderItem)
        .filter(
            CustomerOrder.tenant_id == tenant_id,
            CustomerOrderItem.id.is_(None),
        )
        .count()
    )

    issues = []
    if stale_submitted > 0:
        issues.append({"type": "stale_submitted", "count": stale_submitted, "severity": "warning"})
    if stale_confirmed > 0:
        issues.append({"type": "stale_confirmed", "count": stale_confirmed, "severity": "warning"})
    if empty_orders > 0:
        issues.append({"type": "empty_orders", "count": empty_orders, "severity": "error"})

    return {
        "tenant_id": tenant_id,
        "stale_threshold_hours": stale_hours,
        "issues": issues,
        "total_issues": sum(i["count"] for i in issues),
        "healthy": len(issues) == 0,
        "checked_at": datetime.utcnow().isoformat(),
    }


@router.get("/orders/observability", summary="Orders observability abrufen",
    response_model=PortalShopOut
)
async def get_orders_observability(
    tenant_id: str = Query(..., description="Mandanten-ID"),
    db: Session = Depends(get_db),
):
    """
    C5: Observability — KPI-Übersicht für Portal-Bestellungen.
    """
    from sqlalchemy import func

    status_counts = (
        db.query(CustomerOrder.status, func.count(CustomerOrder.id))
        .filter(CustomerOrder.tenant_id == tenant_id)
        .group_by(CustomerOrder.status)
        .all()
    )

    by_status = {s.value: c for s, c in status_counts}
    total = sum(by_status.values())

    today = datetime.utcnow().date()
    today_count = db.query(CustomerOrder).filter(
        and_(
            CustomerOrder.tenant_id == tenant_id,
            func.date(CustomerOrder.created_at) == today,
        )
    ).count()

    week_ago = datetime.utcnow() - timedelta(days=7)
    week_count = db.query(CustomerOrder).filter(
        and_(
            CustomerOrder.tenant_id == tenant_id,
            CustomerOrder.created_at >= week_ago,
        )
    ).count()

    avg_items = db.query(func.avg(
        db.query(func.count(CustomerOrderItem.id))
        .filter(CustomerOrderItem.order_id == CustomerOrder.id)
        .correlate(CustomerOrder)
        .scalar_subquery()
    )).filter(CustomerOrder.tenant_id == tenant_id).scalar()

    return {
        "tenant_id": tenant_id,
        "total_orders": total,
        "by_status": by_status,
        "today": today_count,
        "last_7_days": week_count,
        "avg_items_per_order": round(float(avg_items or 0), 1),
        "funnel": {
            "submitted": by_status.get("SUBMITTED", 0),
            "confirmed": by_status.get("CONFIRMED", 0),
            "in_progress": by_status.get("IN_PROGRESS", 0),
            "shipped": by_status.get("SHIPPED", 0),
            "delivered": by_status.get("DELIVERED", 0),
            "cancelled": by_status.get("CANCELLED", 0),
        },
    }

