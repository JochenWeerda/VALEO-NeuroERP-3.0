"""POS: Retoure und Abgleich offline kassierter Bons.

Beide Wege sind Geschaeftsvorfaelle an der Kasse und werden deshalb ueber den Fiskalisierungsdienst
signiert (§ 146a AO) — derselbe Dienst, ueber den das Terminal online kassiert
(``/pos/fiscalization/transactions/*``, ``domain_docflow.pos_fiscal_transactions``).

Bis zum 27.10.2026 antwortete ``/pos/checkout`` mit ``completed``, ohne irgendetwas zu speichern. Die
Offline-Warteschlange des Terminals loeschte den Bon daraufhin lokal: Jeder offline kassierte Bon ging
verloren. Die Retoure nahm den Mandanten aus dem Rumpf (Rueckfall Standardmandant), verschluckte
Buchungsfehler und meldete trotzdem ``erfolgreich gebucht``.

Jetzt gilt: Mandant aus dem Token; Erfolg nur, wenn signiert und gespeichert ist; sonst 422 (der Bon ist
fachlich nicht buchbar und bleibt in der Warteschlange sichtbar) oder 503 (spaeter erneut versuchen).
Beide Wege sind ueber eine Vorgangskennung idempotent — ein wiederholter Abgleich signiert nicht doppelt.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.fiscalization.contracts import FinishTransactionCommand, FiscalLine, PaymentLine
from app.services.fiscalization.providers import FiscalProviderError
from app.services.fiscalization.service import FiscalizationService

router = APIRouter()

CENT = Decimal("0.01")

#: Zahlarten der Kasse -> Zahlart der Fiskalisierung (wie ``payMap`` im Terminal).
ZAHLART = {"bar": "CASH", "ec": "NON_CASH", "paypal": "NON_CASH", "b2b": "INTERNAL", "gift_card": "INTERNAL"}

#: Steuersaetze, die die Kasse signieren kann (DSFinV-K ``amounts_per_vat_rate``).
KASSEN_STEUERSAETZE = frozenset({Decimal("19"), Decimal("7"), Decimal("10.7"), Decimal("5.5"), Decimal("0")})


class RetourPosition(BaseModel):
    artikelnr: str = Field(min_length=1)
    bezeichnung: str
    ean: Optional[str] = None
    einzelpreis: Decimal = Field(ge=0)
    menge: int = Field(gt=0)
    grund: Optional[str] = None


class RetourRequest(BaseModel):
    #: Vom Client je Retoure einmal erzeugt; eine Wiederholung mit derselben Kennung bucht nicht doppelt.
    vorgang_id: str = Field(min_length=8, max_length=100)
    original_bon_nr: Optional[str] = None
    kassierer: Optional[str] = None  # Anzeigename an der Kasse; zurechenbar ist der angemeldete Nutzer
    positionen: List[RetourPosition] = Field(min_length=1)
    zahlungsrueckerstattung: str = "bar"  # bar | ec | gift_card
    gesamt: Decimal = Field(gt=0)


class RetourResponse(BaseModel):
    retoure_id: str
    retoure_bon_nr: str
    gesamt: float
    status: str
    signatur_zaehler: Optional[int] = None
    simuliert: bool = False
    message: str


class KassenPosition(BaseModel):
    model_config = ConfigDict(extra="ignore")

    artikelnr: Optional[str] = None
    bezeichnung: str
    ean: Optional[str] = None
    preis: Decimal = Field(ge=0)
    menge: Decimal = Field(gt=0)
    rabatt_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    vat_rate: Optional[Decimal] = None


class KassenZahlung(BaseModel):
    model_config = ConfigDict(extra="ignore")

    art: str
    betrag: Decimal


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    #: Kennung der Offline-Transaktion — zugleich Transaktionskennung der Signatur (Idempotenz).
    offline_id: str = Field(min_length=8, max_length=120)
    cart: List[KassenPosition] = Field(min_length=1)
    zahlungen: List[KassenZahlung] = Field(min_length=1)
    gesamt: Decimal = Field(gt=0)
    kassierer: Optional[str] = None
    timestamp: Optional[str] = None


class CheckoutResponse(BaseModel):
    bon_nr: str
    status: str
    offline_id: str
    gesamt: float
    signatur_zaehler: Optional[int] = None
    simuliert: bool = False


def _steuersatz_aus_stamm(db: Session, tenant_id: str, artikelnr: Optional[str]) -> Decimal:
    """Steuersatz eines Artikels aus seinem Verkaufs-Steuerschluessel (``domain_erp.tax_keys``) — nie angenommen."""
    if not artikelnr:
        raise HTTPException(422, "Position ohne Artikelnummer und ohne Steuersatz: nicht signierbar.")
    row = db.execute(
        text(
            """
            SELECT a.steuerschluessel_verkauf, tk.steuersatz
            FROM domain_inventory.articles a
            LEFT JOIN domain_erp.tax_keys tk
              ON tk.tenant_id = a.tenant_id AND tk.code = a.steuerschluessel_verkauf AND tk.active
             AND tk.gueltig_von <= CURRENT_DATE AND (tk.gueltig_bis IS NULL OR tk.gueltig_bis >= CURRENT_DATE)
            WHERE a.tenant_id = :tid AND a.article_number = :nr
            LIMIT 1
            """
        ),
        {"tid": tenant_id, "nr": artikelnr},
    ).first()
    if row is None:
        raise HTTPException(422, f"Artikel {artikelnr} ist nicht bekannt.")
    if row[1] is None:
        raise HTTPException(422, f"Artikel {artikelnr} hat keinen gueltigen Verkaufs-Steuerschluessel.")
    return Decimal(str(row[1]))


def _kassensatz(satz: Decimal) -> Decimal:
    if satz not in KASSEN_STEUERSAETZE:
        raise HTTPException(422, f"Steuersatz {satz.normalize():f} % kann an der Kasse nicht signiert werden.")
    return satz


def _zahlart(art: str) -> str:
    methode = ZAHLART.get((art or "").strip().lower())
    if methode is None:
        raise HTTPException(422, f"Zahlart {art!r} ist unbekannt.")
    return methode


def _gleich(a: Decimal, b: Decimal) -> bool:
    return abs(a - b) < CENT


def _kasse(service: FiscalizationService) -> dict[str, Any]:
    config = service.get_config()
    if not config.get("configured") or not config.get("cash_register_id") or not config.get("client_id"):
        raise HTTPException(503, "Fiskalisierungsprovider ist fuer diesen Mandanten nicht konfiguriert.")
    return config


def _signiere(service: FiscalizationService, command: FinishTransactionCommand):
    """Start und Abschluss ueber den Fiskalisierungsdienst; beide sind ueber die Transaktionskennung idempotent.

    Eine Wiederholung muss denselben Vorgang meinen: Der Dienst gaebe sonst den frueher signierten Stand zurueck,
    waehrend der Aufrufer andere Positionen bucht.
    """
    brutto = sum((line.gross_amount for line in command.lines), Decimal("0"))
    frueher = service.db.execute(
        text(
            "SELECT gross_total FROM domain_docflow.pos_fiscal_transactions "
            "WHERE tenant_id = :tid AND transaction_id = :tx"
        ),
        {"tid": service.tenant_id, "tx": command.transaction_id},
    ).first()
    if frueher is not None and frueher[0] is not None and not _gleich(Decimal(str(frueher[0])), brutto):
        raise HTTPException(409, "Diese Vorgangskennung wurde bereits mit anderen Betraegen signiert.")
    try:
        service.start(command)
        ergebnis = service.finish(command)
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise HTTPException(503, f"Signatur nicht moeglich: {exc}") from exc
    if ergebnis.state != "FINISHED":
        raise HTTPException(503, f"Signatur nicht abgeschlossen (Status {ergebnis.state}).")
    return ergebnis


@router.post("/retoure", response_model=RetourResponse, summary="Retoure anlegen", dependencies=SCHREIBEN["VERKAUF"])
async def create_retoure(
    data: RetourRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Warenrueckgabe: signierter Kassenbeleg mit negativen Betraegen, danach Bestandszugang je Position."""
    erstattung = _zahlart(data.zahlungsrueckerstattung)
    zeilen: list[FiscalLine] = []
    summe = Decimal("0")
    for pos in data.positionen:
        satz = _kassensatz(_steuersatz_aus_stamm(db, tenant_id, pos.artikelnr))
        brutto = (pos.einzelpreis * pos.menge).quantize(CENT)
        summe += brutto
        zeilen.append(FiscalLine(text=pos.bezeichnung, quantity=Decimal(pos.menge), gross_amount=-brutto, vat_rate=satz))
    if not _gleich(summe, data.gesamt):
        raise HTTPException(422, f"Summe der Positionen {summe:.2f} weicht vom Gesamtbetrag {data.gesamt:.2f} ab.")

    lager = db.execute(
        text("SELECT id FROM domain_inventory.warehouses WHERE tenant_id = :tid ORDER BY warehouse_code LIMIT 1"),
        {"tid": tenant_id},
    ).scalar()
    if lager is None:
        raise HTTPException(422, "Fuer diesen Mandanten ist kein Lager angelegt; die Retoure kann nicht eingelagert werden.")

    service = FiscalizationService(db, tenant_id)
    kasse = _kasse(service)
    bon_nr = f"RET-{data.vorgang_id[-12:].upper()}"
    signiert = _signiere(service, FinishTransactionCommand(
        terminal_id=(kasse.get("settings") or {}).get("terminal_id") or kasse["client_id"],
        cash_register_id=kasse["cash_register_id"],
        client_id=kasse["client_id"],
        transaction_id=data.vorgang_id,
        transaction_type="RECEIPT",
        lines=zeilen,
        payments=[PaymentLine(method=erstattung, amount=-summe)],
        receipt_number=bon_nr,
    ))

    try:
        schon_gebucht = db.execute(
            text(
                "SELECT 1 FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :tid "
                "AND source_document_type = 'pos_retoure' AND source_document_id = :vorgang LIMIT 1"
            ),
            {"tid": tenant_id, "vorgang": data.vorgang_id},
        ).first()
        if schon_gebucht is None:
            for pos in data.positionen:
                eingefuegt = db.execute(
                    text("""
                        INSERT INTO domain_inventory.inventory_stock_movements
                            (id, tenant_id, article_id, warehouse_id, movement_type, quantity, unit,
                             reference_number, source_document_id, source_document_type, notes,
                             previous_stock, new_stock, auto_created, ownership_type, created_at)
                        SELECT
                            gen_random_uuid()::text, :tenant_id, a.id, :lager, 'RETOURE', :qty,
                            COALESCE(a.unit, 'ST'), :bon_nr, :vorgang, 'pos_retoure', :notes,
                            COALESCE(a.current_stock, 0), COALESCE(a.current_stock, 0) + :qty,
                            false, 'owned', NOW()
                        FROM domain_inventory.articles a
                        WHERE a.article_number = :artikelnr AND a.tenant_id = :tenant_id
                        LIMIT 1
                    """),
                    {
                        "tenant_id": tenant_id, "lager": lager, "qty": pos.menge, "vorgang": data.vorgang_id,
                        "bon_nr": bon_nr, "notes": f"POS Retoure {bon_nr}: {pos.grund or 'Rückgabe'}",
                        "artikelnr": pos.artikelnr,
                    },
                ).rowcount
                if eingefuegt != 1:
                    raise HTTPException(422, f"Artikel {pos.artikelnr} ist nicht bekannt.")
                # Bestandsfortschreibung: erster freier Lagerplatz des Lagers, sofern dort Bestand gefuehrt wird.
                db.execute(
                    text("""
                        UPDATE domain_inventory.bin_stock bs
                        SET quantity_kg = bs.quantity_kg + :qty, last_movement_at = NOW()
                        WHERE bs.article_id = (
                            SELECT a.id FROM domain_inventory.articles a
                            WHERE a.article_number = :artikelnr AND a.tenant_id = :tenant_id LIMIT 1
                        )
                        AND bs.tenant_id = :tenant_id
                        AND bs.bin_id = (
                            SELECT wb.id FROM domain_inventory.warehouse_bins wb
                            JOIN domain_inventory.warehouse_zones wz ON wz.id = wb.zone_id
                            WHERE wz.warehouse_id = :lager AND wb.is_blocked = false
                            ORDER BY wb.bin_code
                            LIMIT 1
                        )
                    """),
                    {"qty": pos.menge, "artikelnr": pos.artikelnr, "tenant_id": tenant_id, "lager": lager},
                )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(503, "Retoure ist signiert, der Bestand konnte nicht gebucht werden; bitte erneut senden.") from exc

    return RetourResponse(
        retoure_id=data.vorgang_id,
        retoure_bon_nr=bon_nr,
        gesamt=float(summe),
        status="completed",
        signatur_zaehler=signiert.signature_counter,
        simuliert=signiert.simulated,
        message=f"Retoure {bon_nr} signiert und eingelagert. Rückerstattung via {data.zahlungsrueckerstattung}.",
    )


@router.post("/checkout", summary="Offline kassierten Bon nachtraeglich signieren",
             response_model=CheckoutResponse, dependencies=SCHREIBEN["VERKAUF"])
async def pos_checkout(
    data: CheckoutRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Abgleich der Offline-Warteschlange: derselbe signierte Kassenbeleg wie beim Online-Verkauf."""
    zeilen: list[FiscalLine] = []
    summe = Decimal("0")
    for pos in data.cart:
        satz = _kassensatz(pos.vat_rate if pos.vat_rate is not None
                           else _steuersatz_aus_stamm(db, tenant_id, pos.artikelnr))
        brutto = (pos.preis * (Decimal("1") - pos.rabatt_pct / Decimal("100")) * pos.menge).quantize(CENT)
        summe += brutto
        zeilen.append(FiscalLine(text=pos.bezeichnung, quantity=pos.menge, gross_amount=brutto, vat_rate=satz))
    if not _gleich(summe, data.gesamt):
        raise HTTPException(422, f"Summe der Positionen {summe:.2f} weicht vom Gesamtbetrag {data.gesamt:.2f} ab.")
    zahlungen = [PaymentLine(method=_zahlart(z.art), amount=z.betrag) for z in data.zahlungen]
    if not _gleich(sum((z.amount for z in zahlungen), Decimal("0")), summe):
        raise HTTPException(422, "Die Zahlungen decken den Gesamtbetrag nicht genau.")

    service = FiscalizationService(db, tenant_id)
    kasse = _kasse(service)
    signiert = _signiere(service, FinishTransactionCommand(
        terminal_id=(kasse.get("settings") or {}).get("terminal_id") or kasse["client_id"],
        cash_register_id=kasse["cash_register_id"],
        client_id=kasse["client_id"],
        transaction_id=data.offline_id,
        transaction_type="RECEIPT",
        lines=zeilen,
        payments=zahlungen,
    ))
    return CheckoutResponse(
        bon_nr=f"BON-{signiert.signature_counter}",
        status="completed",
        offline_id=data.offline_id,
        gesamt=float(summe),
        signatur_zaehler=signiert.signature_counter,
        simuliert=signiert.simulated,
    )
