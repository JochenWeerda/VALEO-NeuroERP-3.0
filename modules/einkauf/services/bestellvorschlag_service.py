"""
Bestell-Vorschlag-Service — 3 Berechnungs-Engines

Engine 1: aus Lager (lager)
  → Artikel deren Bestand ≤ Meldebestand, Vorschlag bis zum Maximalbestand

Engine 2: aus Verkauf-Aufträgen (verkauf)
  → Offene VK-Auftrags-Positionen die noch nicht (vollständig) mit Bestand
    gedeckt sind → Fehlmenge als Bestellvorschlag

Engine 3: aus Rohstoff-Bedarf (rohware)
  → Artikel mit `rohware=True` oder Warengruppe 'Rohstoff', Bedarfs-Berechnung
    nach Stichtag aus den offenen Produktions-/Verarbeitungsaufträgen
    (Fallback: Tagesverbrauch × Wiederbeschaffungszeit)
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, func, or_, text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.infrastructure.models.einkauf_models import (
    ArtikelLagerParameter,
    EinkaufBestellvorschlag,
    EinkaufBestellvorschlagPosition,
    EinkaufKontrakt,
    EinkaufKontraktPosition,
    EinkaufLieferant,
)
from app.infrastructure.models.__init__ import (
    Article,
    ArticleSupplier,
    StockMovement,
)


# ─────────────────────────────────────────────────────────────────────────────
# Hilfsfunktionen
# ─────────────────────────────────────────────────────────────────────────────

def _current_stock(db: Session, article_id: str, tenant_id: str,
                   warehouse_id: str | None = None) -> Decimal:
    """
    Berechnet den aktuellen Lagerbestand aus den Bewegungsbuchungen
    (letzter new_stock-Wert je Artikel+Lager).
    Wenn kein warehouse_id → Summe über alle Lager.
    """
    q = (
        db.query(StockMovement.new_stock)
        .filter(
            StockMovement.article_id == article_id,
            StockMovement.tenant_id == tenant_id,
        )
    )
    if warehouse_id:
        q = q.filter(StockMovement.warehouse_id == warehouse_id)
    # neueste Bewegung
    last = q.order_by(StockMovement.created_at.desc()).first()
    return Decimal(str(last[0])) if last else Decimal("0")


def _open_sales_quantity(db: Session, article_id: str, tenant_id: str,
                         von_datum: date | None = None,
                         bis_datum: date | None = None,
                         niederlassung_id: str | None = None) -> Decimal:
    """
    Offene VK-Auftrags-Menge für einen Artikel.
    Liest aus `domain_sales.sales_order_items` (falls vorhanden),
    Fallback: 0 (kein Fehler wenn Tabelle noch nicht existiert).
    """
    try:
        params: dict[str, Any] = {
            "tenant_id": tenant_id,
            "article_id": article_id,
        }
        where_extra = ""
        if von_datum:
            where_extra += " AND so.order_date >= :von_datum"
            params["von_datum"] = von_datum
        if bis_datum:
            where_extra += " AND so.order_date <= :bis_datum"
            params["bis_datum"] = bis_datum
        if niederlassung_id:
            where_extra += " AND so.branch_id = :niederlassung_id"
            params["niederlassung_id"] = niederlassung_id

        sql = text(f"""
            SELECT COALESCE(SUM(soi.quantity - soi.delivered_quantity), 0)
            FROM domain_sales.sales_order_items soi
            JOIN domain_sales.sales_orders so ON so.id = soi.order_id
            WHERE soi.article_id = :article_id
              AND so.tenant_id   = :tenant_id
              AND so.status NOT IN ('cancelled', 'completed', 'delivered')
              AND soi.quantity   > soi.delivered_quantity
              {where_extra}
        """)
        result = db.execute(sql, params).scalar()
        return Decimal(str(result or 0))
    except Exception:
        return Decimal("0")


def _preferred_supplier(db: Session, article_id: str, tenant_id: str) -> tuple[str | None, str | None, Decimal | None]:
    """Gibt (lieferant_id, lieferant_name, letzter_preis) für Bevorzugten Lieferanten zurück."""
    art_sup = (
        db.query(ArticleSupplier)
        .filter(
            ArticleSupplier.article_id == article_id,
            ArticleSupplier.is_preferred == True,
        )
        .first()
    )
    if art_sup and art_sup.partner_id:
        # Lieferant aus domain_einkauf suchen (über partner_id)
        lf = (
            db.query(EinkaufLieferant)
            .filter(
                EinkaufLieferant.partner_id == art_sup.partner_id,
                EinkaufLieferant.tenant_id == tenant_id,
            )
            .first()
        )
        preis = Decimal(str(art_sup.purchase_price)) if art_sup.purchase_price else None
        if lf:
            return str(lf.id), lf.firmenname, preis
    return None, None, None


def _active_kontrakt_preis(db: Session, article_id: str, tenant_id: str,
                            lieferant_id: str | None) -> Decimal | None:
    """Sucht den aktuellen Kontrakt-Preis für Artikel + Lieferant."""
    if not lieferant_id:
        return None
    today = date.today()
    kp = (
        db.query(EinkaufKontraktPosition)
        .join(EinkaufKontraktPosition.kontrakt)
        .filter(
            EinkaufKontraktPosition.article_id == article_id,
            EinkaufKontraktPosition.kontrakt.has(
                and_(
                    EinkaufKontrakt.lieferant_id == lieferant_id,
                    EinkaufKontrakt.tenant_id == tenant_id,
                )
            ),
        )
        .filter(
            or_(
                EinkaufKontraktPosition.gueltig_von.is_(None),
                EinkaufKontraktPosition.gueltig_von <= today,
            ),
            or_(
                EinkaufKontraktPosition.gueltig_bis.is_(None),
                EinkaufKontraktPosition.gueltig_bis >= today,
            ),
        )
        .order_by(EinkaufKontraktPosition.gueltig_bis.desc())
        .first()
    )
    return Decimal(str(kp.preis)) if kp and kp.preis else None


# ─────────────────────────────────────────────────────────────────────────────
# Engine 1: aus Lager
# ─────────────────────────────────────────────────────────────────────────────

def engine_lager(
    db: Session,
    *,
    tenant_id: str,
    niederlassung_id: str | None = None,
    artikelgruppe: str | None = None,
    artikel_nr: str | None = None,
    warehouse_id: str | None = None,
    nur_unter_meldebestand: bool = True,
) -> list[dict[str, Any]]:
    """
    Berechnet Bestellvorschläge basierend auf Lagerbestand vs. Meldebestand.
    Gibt alle Artikel zurück, bei denen Bestand ≤ Meldebestand (oder alle mit Parametern).
    """
    # Artikel-Lager-Parameter laden
    q = (
        db.query(ArtikelLagerParameter, Article)
        .join(Article, Article.id == ArtikelLagerParameter.article_id)
        .filter(
            ArtikelLagerParameter.tenant_id == tenant_id,
            ArtikelLagerParameter.aktiv == True,
        )
    )
    if niederlassung_id:
        q = q.filter(ArtikelLagerParameter.niederlassung_id == niederlassung_id)
    if warehouse_id:
        q = q.filter(ArtikelLagerParameter.warehouse_id == warehouse_id)
    if artikelgruppe:
        q = q.filter(Article.warengruppe == artikelgruppe)
    if artikel_nr:
        q = q.filter(Article.article_number == artikel_nr)

    result = []
    for alp, art in q.all():
        ist = _current_stock(db, art.id, tenant_id, warehouse_id or alp.warehouse_id)
        melde = Decimal(str(alp.meldebestand or 0))
        maxi = Decimal(str(alp.maximalbestand or 0))
        soll = Decimal(str(alp.soll_bestand or 0)) or (maxi if maxi > 0 else melde * 2)

        if nur_unter_meldebestand and ist > melde:
            continue

        vorschlag = max(soll - ist, Decimal("0"))
        if alp.std_bestellmenge and vorschlag > 0:
            # Aufrunden auf Standardbestellmenge
            std = Decimal(str(alp.std_bestellmenge))
            vorschlag = (vorschlag // std + 1) * std if vorschlag % std != 0 else vorschlag

        lf_id, lf_name, letzter_preis = _preferred_supplier(db, art.id, tenant_id)

        # Letzter Einkauf
        last_purchase = (
            db.query(StockMovement.movement_date)
            .filter(
                StockMovement.article_id == art.id,
                StockMovement.tenant_id == tenant_id,
                StockMovement.movement_type == "in",
            )
            .order_by(StockMovement.movement_date.desc())
            .scalar()
        )

        result.append({
            "article_id":          art.id,
            "artikel_nr":          art.article_number,
            "artikel_bezeichnung": art.name,
            "artikel_gruppe":      art.warengruppe,
            "einheit":             alp.std_einheit or art.gebinde_einheit or "t",
            "ist_bestand":         float(ist),
            "mindestbestand":      float(alp.mindestbestand or 0),
            "maximalbestand":      float(maxi),
            "meldebestand":        float(melde),
            "vorschlag_menge":     float(vorschlag),
            "offene_auftraege":    0.0,
            "bedarf":              float(soll - ist),
            "lieferant_id":        lf_id,
            "lieferant_name":      lf_name,
            "letzter_preis":       float(letzter_preis) if letzter_preis else None,
            "preis_einheit":       "100kg",
            "letzter_kauf_datum":  str(last_purchase) if last_purchase else None,
            "wiederbeschaffungs_tage": alp.wiederbeschaffungs_tage,
            "reichweite_tage":     float(alp.reichweite_tage) if alp.reichweite_tage else None,
        })

    return sorted(result, key=lambda x: x["artikel_bezeichnung"])


# ─────────────────────────────────────────────────────────────────────────────
# Engine 2: aus Verkauf-Aufträgen
# ─────────────────────────────────────────────────────────────────────────────

def engine_verkauf(
    db: Session,
    *,
    tenant_id: str,
    niederlassung_id: str | None = None,
    artikelgruppe: str | None = None,
    von_datum: date | None = None,
    bis_datum: date | None = None,
) -> list[dict[str, Any]]:
    """
    Bestellvorschläge aus offenen VK-Auftrags-Positionen.
    Vergleicht offene Auftragsmengen mit verfügbarem Bestand.
    Fehlmenge = Bedarf für Bestellvorschlag.
    """
    # Alle offenen VK-Auftrags-Artikel ermitteln
    try:
        params: dict[str, Any] = {"tenant_id": tenant_id}
        where_extra = ""
        if von_datum:
            where_extra += " AND so.order_date >= :von_datum"
            params["von_datum"] = von_datum
        if bis_datum:
            where_extra += " AND so.order_date <= :bis_datum"
            params["bis_datum"] = bis_datum
        if niederlassung_id:
            where_extra += " AND so.branch_id = :niederlassung_id"
            params["niederlassung_id"] = niederlassung_id

        # Offene Mengen je Artikel summieren
        sql = text(f"""
            SELECT
                soi.article_id,
                a.article_number,
                a.name AS artikel_bezeichnung,
                a.warengruppe,
                SUM(soi.quantity - COALESCE(soi.delivered_quantity, 0)) AS offene_menge,
                a.gebinde_einheit AS einheit
            FROM domain_sales.sales_order_items soi
            JOIN domain_sales.sales_orders so ON so.id = soi.order_id
            JOIN domain_inventory.articles a ON a.id = soi.article_id
            WHERE so.tenant_id = :tenant_id
              AND so.status NOT IN ('cancelled', 'completed', 'delivered')
              AND soi.quantity > COALESCE(soi.delivered_quantity, 0)
              {where_extra}
            {'AND a.warengruppe = :artikelgruppe' if artikelgruppe else ''}
            GROUP BY soi.article_id, a.article_number, a.name, a.warengruppe, a.gebinde_einheit
            ORDER BY a.name
        """)
        if artikelgruppe:
            params["artikelgruppe"] = artikelgruppe

        rows = db.execute(sql, params).fetchall()
    except Exception:
        rows = []

    result = []
    for row in rows:
        article_id = row[0]
        offene_menge = Decimal(str(row[4] or 0))

        # Aktueller Bestand
        ist = _current_stock(db, article_id, tenant_id)

        # Fehlmenge = Bestellbedarf
        fehlmenge = max(offene_menge - ist, Decimal("0"))
        if fehlmenge <= 0:
            continue  # Bestand reicht

        # Puffer: +20% für Sicherheit
        vorschlag = fehlmenge * Decimal("1.2")

        # Auf Standardbestellmenge aufrunden
        alp = (
            db.query(ArtikelLagerParameter)
            .filter(
                ArtikelLagerParameter.article_id == article_id,
                ArtikelLagerParameter.tenant_id == tenant_id,
            )
            .first()
        )
        if alp and alp.std_bestellmenge:
            std = Decimal(str(alp.std_bestellmenge))
            vorschlag = (vorschlag // std + 1) * std if vorschlag % std != 0 else vorschlag

        lf_id, lf_name, letzter_preis = _preferred_supplier(db, article_id, tenant_id)

        result.append({
            "article_id":          article_id,
            "artikel_nr":          row[1],
            "artikel_bezeichnung": row[2],
            "artikel_gruppe":      row[3],
            "einheit":             row[5] or "t",
            "ist_bestand":         float(ist),
            "offene_auftraege":    float(offene_menge),
            "bedarf":              float(fehlmenge),
            "vorschlag_menge":     float(vorschlag),
            "mindestbestand":      0.0,
            "maximalbestand":      0.0,
            "meldebestand":        0.0,
            "lieferant_id":        lf_id,
            "lieferant_name":      lf_name,
            "letzter_preis":       float(letzter_preis) if letzter_preis else None,
            "preis_einheit":       "100kg",
            "letzter_kauf_datum":  None,
            "wiederbeschaffungs_tage": alp.wiederbeschaffungs_tage if alp else None,
            "reichweite_tage":     None,
        })

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Engine 3: aus Rohstoff-Bedarf
# ─────────────────────────────────────────────────────────────────────────────

def engine_rohware(
    db: Session,
    *,
    tenant_id: str,
    stichtag: date | None = None,
    niederlassung_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Bestellvorschläge für Rohwaren/Rohstoffe.
    Liest aus:
    1. Offene Produktions-/Verarbeitungsaufträge (domain_production, falls vorhanden)
    2. Fallback: ArtikelLagerParameter × Wiederbeschaffungszeit × Tagesverbrauch
       für Artikel mit warengruppe like '%rohstoff%' oder warengruppe like '%rohware%'

    Gibt benötigte Mengen für alle Rohwaren-Artikel zurück, bei denen
    der aktuelle Bestand den Bedarf nicht deckt.
    """
    if stichtag is None:
        stichtag = date.today()

    # Rohwaren-Artikel ermitteln
    rohwaren_q = (
        db.query(Article)
        .filter(
            Article.warengruppe.ilike("%rohstoff%")
            | Article.warengruppe.ilike("%rohware%")
            | Article.warengruppe.ilike("%grains%")
            | Article.warengruppe.ilike("%getreide%")
        )
    )
    rohwaren = rohwaren_q.all()
    if not rohwaren:
        # Fallback: alle Artikel mit ArtikelLagerParameter die als Rohware markiert
        rohwaren_ids_q = (
            db.query(ArtikelLagerParameter.article_id)
            .filter(
                ArtikelLagerParameter.tenant_id == tenant_id,
                ArtikelLagerParameter.aktiv == True,
                ArtikelLagerParameter.durchschnitt_verbrauch_tag > 0,
            )
        )
        if niederlassung_id:
            rohwaren_ids_q = rohwaren_ids_q.filter(
                ArtikelLagerParameter.niederlassung_id == niederlassung_id
            )
        rohwaren_ids = [r[0] for r in rohwaren_ids_q.all()]
        rohwaren = db.query(Article).filter(Article.id.in_(rohwaren_ids)).all() if rohwaren_ids else []

    result = []
    for art in rohwaren:
        alp = None
        ist = _current_stock(db, art.id, tenant_id)

        # Versuch: aus Produktionsaufträgen lesen
        produktions_bedarf = Decimal("0")
        try:
            sql = text("""
                SELECT COALESCE(SUM(pa.menge_bedarf), 0)
                FROM domain_production.produktionsauftrag_positionen pa
                JOIN domain_production.produktionsauftraege p ON p.id = pa.auftrag_id
                WHERE pa.article_id = :article_id
                  AND p.tenant_id   = :tenant_id
                  AND p.status NOT IN ('abgeschlossen', 'storniert')
                  AND p.start_datum <= :stichtag
            """)
            produktions_bedarf = Decimal(str(
                db.execute(sql, {"article_id": art.id, "tenant_id": tenant_id,
                                  "stichtag": stichtag}).scalar() or 0
            ))
        except Exception:
            db.rollback()
            pass

        # Fallback: Tagesverbrauch × Wiederbeschaffungszeit
        if produktions_bedarf == 0:
            alp = (
                db.query(ArtikelLagerParameter)
                .filter(
                    ArtikelLagerParameter.article_id == art.id,
                    ArtikelLagerParameter.tenant_id == tenant_id,
                )
                .first()
            )
            if alp and alp.durchschnitt_verbrauch_tag and alp.wiederbeschaffungs_tage:
                tage = alp.wiederbeschaffungs_tage + 2  # Sicherheitspuffer
                produktions_bedarf = (
                    Decimal(str(alp.durchschnitt_verbrauch_tag)) * tage
                )
            else:
                continue  # kein Bedarf ermittelbar

        fehlmenge = max(produktions_bedarf - ist, Decimal("0"))
        if fehlmenge <= 0:
            continue

        # Aufrunden auf Standardbestellmenge (alp ggf. aus Fallback-Block oben)
        if alp is None:
            alp = (
                db.query(ArtikelLagerParameter)
                .filter(
                    ArtikelLagerParameter.article_id == art.id,
                    ArtikelLagerParameter.tenant_id == tenant_id,
                )
                .first()
            )
        vorschlag = fehlmenge
        if alp and alp.std_bestellmenge:
            std = Decimal(str(alp.std_bestellmenge))
            vorschlag = (fehlmenge // std + 1) * std if fehlmenge % std != 0 else fehlmenge

        lf_id, lf_name, letzter_preis = _preferred_supplier(db, art.id, tenant_id)

        result.append({
            "article_id":          art.id,
            "artikel_nr":          art.article_number,
            "artikel_bezeichnung": art.name,
            "artikel_gruppe":      art.warengruppe,
            "einheit":             (alp.std_einheit if alp else None) or art.gebinde_einheit or "t",
            "ist_bestand":         float(ist),
            "offene_auftraege":    0.0,
            "bedarf":              float(produktions_bedarf),
            "vorschlag_menge":     float(vorschlag),
            "mindestbestand":      float(alp.mindestbestand) if alp else 0.0,
            "maximalbestand":      float(alp.maximalbestand) if alp else 0.0,
            "meldebestand":        float(alp.meldebestand) if alp else 0.0,
            "lieferant_id":        lf_id,
            "lieferant_name":      lf_name,
            "letzter_preis":       float(letzter_preis) if letzter_preis else None,
            "preis_einheit":       "100kg",
            "letzter_kauf_datum":  None,
            "wiederbeschaffungs_tage": alp.wiederbeschaffungs_tage if alp else None,
            "reichweite_tage":     None,
        })

    return sorted(result, key=lambda x: x["artikel_bezeichnung"])


# ─────────────────────────────────────────────────────────────────────────────
# Vorschlag speichern + in Bestellung umwandeln
# ─────────────────────────────────────────────────────────────────────────────

def save_vorschlag(
    db: Session,
    *,
    tenant_id: str,
    vorschlag_typ: str,
    positionen: list[dict[str, Any]],
    parameter: dict[str, Any] | None = None,
    niederlassung_id: str | None = None,
    erstellt_von: str = "system",
) -> EinkaufBestellvorschlag:
    """Speichert einen berechneten Vorschlag in die Datenbank."""
    vorschlag = EinkaufBestellvorschlag(
        id=uuid7(),
        tenant_id=tenant_id,
        vorschlag_typ=vorschlag_typ,
        datum=date.today(),
        niederlassung_id=niederlassung_id,
        parameter=parameter or {},
        status="entwurf",
        erstellt_von=erstellt_von,
    )
    db.add(vorschlag)
    db.flush()

    for i, pos in enumerate(positionen, start=1):
        bp = EinkaufBestellvorschlagPosition(
            id=uuid7(),
            vorschlag_id=vorschlag.id,
            pos_nr=i,
            article_id=pos["article_id"],
            artikel_nr=pos.get("artikel_nr"),
            artikel_bezeichnung=pos.get("artikel_bezeichnung"),
            artikel_gruppe=pos.get("artikel_gruppe"),
            einheit=pos.get("einheit"),
            ist_bestand=pos.get("ist_bestand", 0),
            offene_auftraege=pos.get("offene_auftraege", 0),
            bedarf=pos.get("bedarf", 0),
            vorschlag_menge=pos["vorschlag_menge"],
            bestell_menge=pos.get("bestell_menge") or pos["vorschlag_menge"],
            lieferant_id=pos.get("lieferant_id"),
            lieferant_name=pos.get("lieferant_name"),
            letzter_preis=pos.get("letzter_preis"),
            preis_einheit=pos.get("preis_einheit"),
            letzter_kauf_datum=pos.get("letzter_kauf_datum"),
        )
        db.add(bp)

    db.flush()
    return vorschlag


def vorschlag_zu_bestellungen(
    db: Session,
    *,
    vorschlag_id: str,
    tenant_id: str,
    freigegeben_von: str = "system",
) -> list[dict[str, Any]]:
    """
    Konvertiert einen freigegebenen Bestell-Vorschlag in Einkaufs-Bestellungen.
    Gruppiert Positionen nach Lieferant → je Lieferant eine Bestellung.
    Gibt eine Liste der erzeugten Bestellungen zurück.
    """
    from app.infrastructure.models.einkauf_models import EinkaufBestellung, EinkaufBestellungPosition

    vorschlag = (
        db.query(EinkaufBestellvorschlag)
        .filter(
            EinkaufBestellvorschlag.id == vorschlag_id,
            EinkaufBestellvorschlag.tenant_id == tenant_id,
        )
        .first()
    )
    if not vorschlag:
        raise ValueError(f"Vorschlag {vorschlag_id} nicht gefunden")

    # Positionen nach Lieferant gruppieren
    pos_by_lf: dict[str | None, list[EinkaufBestellvorschlagPosition]] = {}
    for pos in vorschlag.positionen:
        if pos.status == "ignoriert":
            continue
        lf_key = str(pos.lieferant_id) if pos.lieferant_id else "_kein_lieferant"
        pos_by_lf.setdefault(lf_key, []).append(pos)

    from datetime import date as dt
    import re

    created_orders = []
    for lf_key, positions in pos_by_lf.items():
        lf = None
        if lf_key != "_kein_lieferant":
            lf = db.query(EinkaufLieferant).filter(EinkaufLieferant.id == lf_key).first()

        lieferant_id = lf.id if lf else (positions[0].lieferant_id if positions else None)
        if lieferant_id is None:
            continue  # Bestellung ohne Lieferant nicht anlegen (NOT NULL)

        # Bestellnummer generieren
        ts = datetime.now().strftime("%y%m%d%H%M")
        bestell_nr = f"EK-{ts}-{lf_key[:4].upper() if lf_key != '_kein_lieferant' else 'XXXX'}"

        bestellung = EinkaufBestellung(
            id=uuid7(),
            tenant_id=tenant_id,
            bestellnummer=bestell_nr,
            lieferant_id=lieferant_id,
            vorschlag_id=vorschlag.id,
            niederlassung_id=vorschlag.niederlassung_id,
            bestelldatum=dt.today(),
            status="entwurf",
            erstellt_von=freigegeben_von,
        )
        db.add(bestellung)
        db.flush()

        netto = Decimal("0")
        for i, pos in enumerate(positions, start=1):
            menge = Decimal(str(pos.bestell_menge or pos.vorschlag_menge))
            preis = Decimal(str(pos.letzter_preis or 0))
            betrag = menge * preis / 100  # Preis je 100kg → je kg × menge

            bp = EinkaufBestellungPosition(
                id=uuid7(),
                bestellung_id=bestellung.id,
                pos_nr=i,
                article_id=pos.article_id,
                artikel_nr=pos.artikel_nr or "",
                artikel_bezeichnung=pos.artikel_bezeichnung or "",
                menge=menge,
                menge_geliefert=Decimal("0"),
                menge_offen=menge,
                einheit=pos.einheit or "t",
                einzelpreis=preis,
                preis_einheit=pos.preis_einheit or "100kg",
                netto_betrag=betrag,
                mwst_satz=Decimal("7"),   # Default Agrar 7%
                mwst_betrag=betrag * Decimal("0.07"),
                brutto_betrag=betrag * Decimal("1.07"),
                status="offen",
            )
            db.add(bp)
            netto += betrag
            # Vorschlag-Position als bestellt markieren
            pos.status = "bestellt"

        bestellung.netto_summe = netto
        bestellung.mwst_betrag = netto * Decimal("0.07")
        bestellung.brutto_summe = netto * Decimal("1.07")
        db.flush()

        created_orders.append({
            "bestellung_id":   str(bestellung.id),
            "bestellnummer":   bestellung.bestellnummer,
            "lieferant_name":  lf.firmenname if lf else "Kein Lieferant",
            "positionen_anz":  len(positions),
            "netto_summe":     float(netto),
        })

    # Vorschlag-Status aktualisieren
    vorschlag.status = "in_bestellung"
    vorschlag.freigegeben_von = freigegeben_von
    vorschlag.freigegeben_am = datetime.now()
    db.flush()

    return created_orders
