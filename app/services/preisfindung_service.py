"""Die Preiskaskade — jede Stufe wird ausgewertet, jeder Fehlschlag gemeldet.

Bis zum 05.10.2026 hatte die Kaskade fuenf Stufen, von denen drei nie
funktionierten: Der Kontraktrabatt las zwei Spalten, die es nicht gibt, der
Mitarbeiterrabatt eine Tabelle, die es nicht gibt, und die gepflegten
Mengenstaffeln wurden gar nicht gelesen. Jeder Fehlschlag lief in
``except Exception: db.rollback()``, und heraus kam der volle Listenpreis mit
``source: "base"``.

Ein Preis ist keine Anzeige, sondern die Grundlage der Rechnung. Deshalb gilt
hier: Eine Stufe liefert ein Ergebnis oder einen Fehler — nie stillschweigend
nichts.

Reihenfolge und Begruendung:
``docs/quality-assurance/preisfindung-kaskade-20261005.md``.
"""

from __future__ import annotations

import json
import logging
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

ARTIKEL = "domain_inventory.articles"
PREISLISTEN = "domain_pricing.price_lists"
PREISLISTENPOSITIONEN = "domain_pricing.price_list_items"
STAFFELN = "domain_pricing.staffelrabatte"
STAFFEL_ARTIKEL = "domain_pricing.staffelrabatt_artikel"
RABATTREGELN = "domain_pricing.discount_rules"
KONTRAKTE = "domain_ops.kon_contract"
KONTRAKTZEILEN = "domain_ops.kon_contract_line"

#: Die Stufen der Kaskade in ihrer Reihenfolge. Es gilt **eine** — die erste, die
#: greift. Nicht additiv.
#:
#: Die Staffel steht ueber dem Kundenrabatt, weil sie an der tatsaechlich
#: bestellten Menge haengt und damit die spezifischere Aussage ist; der Kontrakt
#: steht darueber, weil er eine Zusage ist.
STUFEN = (
    "contract",
    "staffelrabatt",
    "customer_discount",
    "employee_discount",
)

#: Alle Werte, die ``source`` annehmen kann.
QUELLEN = ("base", "price_list", *STUFEN)

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (preisfindung_rabattregeln_20261005)"
}


def stufe_nicht_lesbar(db: Session, fehler: Exception, stufe: str, tenant_id: str) -> HTTPException:
    """Eine unlesbare Stufe ist kein fehlender Rabatt.

    Vorher wurde daraus der volle Listenpreis. Wer einen Preis nicht vollstaendig
    ermitteln kann, darf keinen nennen — sonst wird auf einer Stoerung
    abgerechnet.
    """
    db.rollback()
    logger.exception("Preisstufe %s nicht lesbar (Mandant %s)", stufe, tenant_id)
    return HTTPException(
        status_code=503,
        detail={
            "error": (
                f"Die Preisstufe {stufe!r} ist nicht auswertbar. Es wird kein Preis "
                "genannt, solange die Kaskade unvollstaendig ist."
            ),
            "stufe": stufe,
            "grund": str(fehler),
            "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"],
        },
        headers=MIGRATIONS_HINWEIS,
    )


def artikel_holen(db: Session, tenant_id: str, article_id: str) -> dict:
    zeile = db.execute(
        text(
            "SELECT id, article_number, sales_price, warengruppe, category "
            f"FROM {ARTIKEL} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE id = :id AND tenant_id = :tid AND is_active = TRUE"
        ),
        {"id": article_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    return dict(zeile)


def preisliste(
    db: Session, tenant_id: str, artikel: dict, menge: Decimal
) -> Optional[dict]:
    """Die guenstigste zutreffende Preislistenposition — oder nichts."""
    return db.execute(
        text(
            "SELECT pli.id, pli.price_list_id, pli.unit_price, pli.discount_percent, "
            "       pl.name AS listenname "
            f"FROM {PREISLISTENPOSITIONEN} pli "  # nosec B608  # reviewed-safe: Tabellennamen sind Code-Literale
            f"JOIN {PREISLISTEN} pl ON pl.id = pli.price_list_id "
            "WHERE pl.tenant_id = :tid AND pl.is_active = TRUE "
            "  AND (pl.valid_from IS NULL OR pl.valid_from <= CURRENT_DATE) "
            "  AND (pl.valid_until IS NULL OR pl.valid_until >= CURRENT_DATE) "
            "  AND (pli.article_id = :aid OR pli.article_number = :anr) "
            "  AND (pli.valid_from IS NULL OR pli.valid_from <= CURRENT_DATE) "
            "  AND (pli.valid_until IS NULL OR pli.valid_until >= CURRENT_DATE) "
            "  AND (pli.min_quantity IS NULL OR pli.min_quantity <= :menge) "
            "ORDER BY pli.min_quantity DESC NULLS LAST LIMIT 1"
        ),
        {
            "tid": tenant_id,
            "aid": artikel["id"],
            "anr": artikel.get("article_number") or "",
            "menge": float(menge),
        },
    ).mappings().first()


def kontraktpreis(
    db: Session, tenant_id: str, kontrakt_id: str, article_id: str
) -> Optional[dict]:
    """Preis und Rabatt aus der Kontraktposition des Artikels.

    Vorher las diese Stufe ``domain_contracts.contracts.discount_percent`` —
    zwei Spalten, die es nicht gibt. `domain_contracts.contracts` ist ein
    Vertragsregister (Titel, Gegenpartei, Kuendigungsfrist), kein
    Handelskontrakt. Das fuehrende Kontraktmodell traegt Preis und Rabatt **je
    Artikel** an der Position; das ist genauer als ein pauschaler Kopfrabatt.
    """
    return db.execute(
        text(
            "SELECT z.unit_price, z.discount_pct, z.surcharge, k.contract_no "
            f"FROM {KONTRAKTZEILEN} z "  # nosec B608  # reviewed-safe: Tabellennamen sind Code-Literale
            f"JOIN {KONTRAKTE} k "
            "     ON k.contract_id = z.contract_id AND k.tenant_id = z.tenant_id "
            "WHERE z.contract_id = :kid AND z.tenant_id = :tid AND z.article_id = :aid "
            "ORDER BY z.position_no LIMIT 1"
        ),
        {"kid": kontrakt_id, "tid": tenant_id, "aid": article_id},
    ).mappings().first()


def staffel_stufe(
    db: Session,
    tenant_id: str,
    artikel: dict,
    menge: Decimal,
    customer_id: Optional[str],
) -> Optional[dict]:
    """Die zutreffende Staffelstufe fuer diese Menge — oder nichts.

    Gepflegte Staffeln blieben wirkungslos: Es gab Wege zum Anlegen und
    Auflisten, aber die Kaskade las sie nicht. Eine Staffel haengt an der
    **tatsaechlich bestellten Menge** und ist damit spezifischer als ein
    pauschaler Kundenrabatt.

    Zutreffend ist eine Staffel, die den Artikel (direkt, ueber die
    Zuordnungstabelle oder ueber die Artikelgruppe) und — falls sie einen Kunden
    nennt — diesen Kunden betrifft, und deren Gueltigkeit heute laeuft.
    """
    zeilen = db.execute(
        text(
            "SELECT s.id, s.stufen, s.bezeichnung, s.artikel_id, s.artikelgruppe, "
            "       s.kunden_id "
            f"FROM {STAFFELN} s "  # nosec B608  # reviewed-safe: Tabellennamen sind Code-Literale
            "WHERE s.tenant_id = :tid AND COALESCE(s.status, 'aktiv') = 'aktiv' "
            "  AND (s.gueltig_von IS NULL OR s.gueltig_von <= CURRENT_DATE) "
            "  AND (s.gueltig_bis IS NULL OR s.gueltig_bis >= CURRENT_DATE) "
            "  AND (s.kunden_id IS NULL OR s.kunden_id = :kid) "
            "  AND ( s.artikel_id = :aid "
            "        OR (s.artikelgruppe IS NOT NULL AND s.artikelgruppe = :gruppe) "
            f"       OR EXISTS (SELECT 1 FROM {STAFFEL_ARTIKEL} sa "
            "                   WHERE sa.staffelrabatt_id = s.id "
            "                     AND sa.tenant_id = s.tenant_id "
            "                     AND sa.artikel_id = :aid) ) "
            # Die kundenbezogene Staffel geht der allgemeinen vor, die
            # artikelbezogene der gruppenbezogenen: vom Besonderen zum Allgemeinen.
            "ORDER BY (s.kunden_id IS NOT NULL) DESC, (s.artikel_id IS NOT NULL) DESC, "
            "         s.created_at DESC "
            "LIMIT 50"
        ),
        {
            "tid": tenant_id,
            "kid": customer_id,
            "aid": artikel["id"],
            "gruppe": artikel.get("warengruppe") or artikel.get("category"),
        },
    ).mappings().fetchmany(50)

    for zeile in zeilen:
        treffer = _beste_stufe(zeile["stufen"], menge)
        if treffer is not None:
            return {
                "staffel_id": zeile["id"],
                "bezeichnung": zeile["bezeichnung"],
                "ab_menge": treffer["ab_menge"],
                "rabatt_prozent": treffer.get("rabatt_prozent"),
                "festpreis": treffer.get("festpreis"),
            }
    return None


def _beste_stufe(stufen: Any, menge: Decimal) -> Optional[dict]:
    """Die hoechste Stufe, deren Mindestmenge erreicht ist.

    Eine Stufe ohne Wirkung (kein Rabatt, kein Festpreis) zaehlt nicht als
    Treffer — sonst wuerde eine Nullstufe ``ab_menge: 1, rabatt: 0`` die
    nachfolgenden Stufen und den Kundenrabatt verdraengen.
    """
    if isinstance(stufen, str):
        stufen = json.loads(stufen)
    if not isinstance(stufen, list):
        return None
    passend = []
    for eintrag in stufen:
        if not isinstance(eintrag, dict) or eintrag.get("ab_menge") is None:
            continue
        ab = Decimal(str(eintrag["ab_menge"]))
        if ab > menge:
            continue
        rabatt = eintrag.get("rabatt_prozent")
        festpreis = eintrag.get("festpreis")
        wirkt = (rabatt is not None and Decimal(str(rabatt)) > 0) or (
            festpreis is not None and Decimal(str(festpreis)) > 0
        )
        if wirkt:
            passend.append((ab, eintrag))
    if not passend:
        return None
    return max(passend, key=lambda p: p[0])[1]


def rollenrabatt(db: Session, tenant_id: str, rolle: str) -> Optional[Decimal]:
    """Der Rabatt einer Rolle. Je Mandant und Rolle gilt genau eine Regel."""
    wert = db.execute(
        text(
            "SELECT discount_percent "
            f"FROM {RABATTREGELN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE tenant_id = :tid AND role = :rolle AND is_active = TRUE "
            "  AND (valid_from IS NULL OR valid_from <= CURRENT_DATE) "
            "  AND (valid_until IS NULL OR valid_until >= CURRENT_DATE) "
            "ORDER BY discount_percent DESC LIMIT 1"
        ),
        {"tid": tenant_id, "rolle": rolle},
    ).scalar()
    return None if wert is None else Decimal(str(wert))


def pruefe_rabatt(rabatt: Decimal, stufe: str) -> Decimal:
    """Ein Rabatt bleibt zwischen null und hundert Prozent.

    Ueber hundert Prozent waere der Preis negativ — das Haus wuerde fuer die
    Lieferung zahlen. Die Datenbank haelt es bei den Rabattregeln nach; bei
    Preislisten, Kontraktzeilen und Staffeln sind die Spalten aelter, also wird
    hier geprueft statt gehofft.
    """
    if rabatt < 0 or rabatt > 100:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Die Stufe {stufe!r} nennt {rabatt} % Rabatt. Ein Rabatt ausserhalb "
                "von 0 bis 100 % ergibt keinen Preis — der Satz ist zu berichtigen."
            ),
        )
    return rabatt
