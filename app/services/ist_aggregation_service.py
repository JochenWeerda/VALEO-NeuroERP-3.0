"""Echte Ist-Belegaggregation für das Bedarfsdeckungs-Cockpit.

Füllt public.kunden_produktgruppen_bezug (die Ist-Seite) aus den realen
Verkaufsbelegen statt aus modellierten Seeds. Zwei Beleg-Quellen werden
unioniert (jede wird übersprungen, wenn die Tabelle fehlt):

- ``domain_crm.sales_orders`` + ``sales_order_items`` (Auftrag/Angebot-Folge)
- ``domain_portal.customer_orders`` + ``customer_order_items`` (Webshop/Portal)

Zwei Brücken lösen die in der Architektur bekannten Medienbrüche auf:

1. **Kunde**: Beleg-``customer_id`` ist eine UUID (konsolidierter Business
   Partner), nicht die ``kunden_nr``. ``_kunden_resolver`` mappt jede bekannte
   Identitätsspalte (kunden_nr, business_partner_id, webshop_kunden_nr,
   legacy_kunden_nr) → kunden_nr. Portal-Belege tragen zusätzlich eine
   ``customer_number`` (i.d.R. direkt die kunden_nr) und werden zuerst darüber
   aufgelöst.
2. **Produkt**: Beleg-Position trägt eine ``article_number``. ``klassifiziere_artikel``
   ordnet sie über Warengruppe/Kategorie/Flags des Artikels (bzw. ersatzweise den
   Positionstext) einer der 9 Bedarfs-Produktgruppen zu (Milchvieh 6 + Ackerbau 3).

Aggregiert wird rollierend über 12 Monate je (kunden_nr, produktgruppe):
Umsatz, Menge, Deckungsbeitrag (sofern EK vorhanden), letzter Bezug. Geschrieben
mit ``quelle='verkauf'`` — Käufergruppen-Spalten der Zielzeile bleiben unberührt.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger("crm.ist_aggregation")

TENANT_DEFAULT = "00000000-0000-0000-0000-000000000001"

# ── Produkt-Klassifikator (rein, testbar) ─────────────────────────────────────
# Gültige Zielschlüssel = die Produktgruppen aus dem Bedarfsdeckungs-Cockpit.
PRODUKTGRUPPEN_KEYS = {
    "kraftfutter", "mineral_spezial", "kaelber", "grundfutterbau",
    "stallbedarf_hygiene", "beratung_analyse",
    "duenger_marktfrucht", "pflanzenschutz", "saatgut_marktfrucht",
}

# Namens-Schlüsselwörter, die Grundfutterbau (Milchvieh) von Marktfrucht trennen.
_GRUNDFUTTER_KW = ("mais", "gras", "weidel", "klee", "luzerne", "grünland",
                   "gruenland", "grunland", "wiese", "silo", "feldgras", "ackergras")


def _norm(*parts: Optional[str]) -> str:
    return " ".join(p for p in parts if p).lower()


def klassifiziere_artikel(
    name: Optional[str] = None,
    warengruppe: Optional[str] = None,
    category: Optional[str] = None,
    pflanzenschutzmittel: bool = False,
    duengemittel_bez: Optional[str] = None,
) -> Optional[str]:
    """Ordnet einen Artikel einer Bedarfs-Produktgruppe zu (oder None).

    Reihenfolge ist bewusst: spezifische Flags/Schlüsselwörter vor Warengruppe.
    Getreide-Ankauf vom Landwirt ist kein Betriebsmittel-Verkauf → None.
    """
    txt = _norm(name)
    wg = _norm(warengruppe, category)

    # 1) Pflanzenschutz (Flag oder Warengruppe oder Wirkstoff im Namen)
    if pflanzenschutzmittel or "pflanzenschutz" in wg or any(
        k in txt for k in ("herbizid", "fungizid", "insektizid", "glyphosat", "beize")
    ):
        return "pflanzenschutz"

    # 2) Saatgut → Grundfutter vs. Marktfrucht
    if "saatgut" in wg or "saatgut" in txt or "saat" in txt:
        return "grundfutterbau" if any(k in txt for k in _GRUNDFUTTER_KW) else "saatgut_marktfrucht"

    # 3) Dünger / organische Dünger / Düngemittel-Inhalt
    if ("duenger" in wg or "dünger" in wg or "organisch" in wg or duengemittel_bez
            or any(k in txt for k in ("dünger", "duenger", "npk", "kalk", "gülle", "guelle",
                                       "mist", "kompost", "harnstoff", "kas"))):
        return "grundfutterbau" if any(k in txt for k in _GRUNDFUTTER_KW) else "duenger_marktfrucht"

    # 4) Biostimulanzien → Betriebsmittel Pflanzenbau (Marktfrucht-nah)
    if "biostimul" in wg:
        return "duenger_marktfrucht"

    # 5) Futtermittel & Stall: feinere Trennung über Namens-Schlüsselwörter
    if any(k in txt for k in ("mineral", "puffer", "hefe", "toxinbinder", "lecksteine", "viehsalz")):
        return "mineral_spezial"
    if any(k in txt for k in ("kälber", "kaelber", "kalb", "milchaustauscher", "starter", "mat ")):
        return "kaelber"
    if any(k in txt for k in ("einstreu", "hygiene", "klauen", "dipp", "stallbedarf", "euter", "strohmehl")):
        return "stallbedarf_hygiene"
    if any(k in txt for k in ("beratung", "analyse", "rationsservice", "rationscheck", "probe")):
        return "beratung_analyse"
    if "futtermittel" in wg or any(k in txt for k in (
        "kraftfutter", "eiweiß", "eiweiss", "ausgleichsfutter", "mischfutter",
        "schrot", "tierfutter", "milchleistungsfutter", "mlf",
    )):
        return "kraftfutter"

    # 6) Getreide-Ankauf u. ä. = kein Betriebsmittel-Verkauf
    return None


# ── Beleg-Quellen-Konfiguration ───────────────────────────────────────────────
@dataclass
class OrderSource:
    """Eine Beleg-Quelle (Header + Positionen). Wird übersprungen, wenn fehlt."""
    name: str
    header_table: str
    item_table: str
    join_key: str            # item.<join_key> = header.id
    customer_ref_col: str    # Header-Spalte mit der Kundenreferenz (UUID o. Nr.)
    date_expr: str           # Header-Datumsausdruck (rollierende 12 M)
    qty_col: str
    amount_col: str          # Positions-Nettobetrag
    article_col: str         # item.article_number
    item_text_col: str       # Positionstext-Fallback für die Klassifikation
    customer_number_col: Optional[str] = None  # falls Header direkt die kunden_nr trägt
    ek_expr: Optional[str] = None              # EK je Position (für DB), optional
    extra_where: str = ""    # zusätzliche Header-Filter (Status etc.)


DEFAULT_SOURCES: list[OrderSource] = [
    OrderSource(
        name="crm_sales_orders",
        header_table="domain_crm.sales_orders",
        item_table="domain_crm.sales_order_items",
        join_key="order_id",
        customer_ref_col="customer_id",
        date_expr="COALESCE(h.delivery_date, h.created_at)",
        qty_col="i.quantity",
        amount_col="i.line_total",
        article_col="i.article_number",
        item_text_col="i.description",
        ek_expr="i.ek_price",
        extra_where="h.deleted_at IS NULL AND COALESCE(h.status,'') NOT ILIKE 'storn%' "
                    "AND COALESCE(h.status,'') NOT ILIKE 'cancel%'",
    ),
    OrderSource(
        name="portal_customer_orders",
        header_table="domain_portal.customer_orders",
        item_table="domain_portal.customer_order_items",
        join_key="order_id",
        customer_ref_col="customer_id",
        customer_number_col="customer_number",
        date_expr="h.order_date",
        qty_col="i.quantity",
        amount_col="i.total_price",
        article_col="i.article_number",
        item_text_col="i.article_name",
        extra_where="COALESCE(h.status::text,'') NOT ILIKE 'storn%' "
                    "AND COALESCE(h.status::text,'') NOT ILIKE 'cancel%'",
    ),
]


@dataclass
class _Acc:
    umsatz: float = 0.0
    menge: float = 0.0
    db: float = 0.0
    db_bekannt: bool = False
    letzter: Optional[object] = None
    quellen: set = field(default_factory=set)


class IstAggregationService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None,
                 sources: Optional[list[OrderSource]] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or TENANT_DEFAULT
        self.sources = sources if sources is not None else DEFAULT_SOURCES

    # ── Brücke 1: Kundenreferenz → kunden_nr ──────────────────────────────────
    def _kunden_resolver(self) -> dict[str, str]:
        rows = self.db.execute(
            text(
                "SELECT kunden_nr, business_partner_id, webshop_kunden_nr, legacy_kunden_nr "
                "FROM public.kunden WHERE coalesce(geloescht, FALSE) = FALSE"
            )
        ).all()
        idx: dict[str, str] = {}
        for kn, bp, web, legacy in rows:
            for ref in (kn, bp, web, legacy):
                if ref:
                    idx.setdefault(str(ref), kn)
        return idx

    # ── Brücke 2: article_number → produktgruppe ──────────────────────────────
    def _artikel_index(self) -> dict[str, Optional[str]]:
        if self.db.execute(text("SELECT to_regclass('domain_inventory.articles')")).scalar() is None:
            return {}
        rows = self.db.execute(
            text(
                "SELECT article_number, name, warengruppe, category, "
                "pflanzenschutzmittel, duengemittel_inhalte_bezeichnung "
                "FROM domain_inventory.articles WHERE article_number IS NOT NULL"
            )
        ).mappings().all()
        idx: dict[str, Optional[str]] = {}
        for a in rows:
            idx[a["article_number"]] = klassifiziere_artikel(
                a["name"], a["warengruppe"], a["category"],
                bool(a["pflanzenschutzmittel"]), a["duengemittel_inhalte_bezeichnung"],
            )
        return idx

    def _table_exists(self, qualified: str) -> bool:
        return self.db.execute(text("SELECT to_regclass(:n)"), {"n": qualified}).scalar() is not None

    def _read_source(self, src: OrderSource) -> list[dict]:
        if not (self._table_exists(src.header_table) and self._table_exists(src.item_table)):
            logger.info("[IST] Quelle %s übersprungen (Tabelle fehlt)", src.name)
            return []
        where = f"{src.date_expr} >= now() - interval '12 months'"
        if src.extra_where:
            where += f" AND ({src.extra_where})"
        cust_num = f"h.{src.customer_number_col}" if src.customer_number_col else "NULL"
        ek = src.ek_expr or "NULL"
        sql = text(
            f"""
            SELECT h.{src.customer_ref_col} AS customer_ref,
                   {cust_num}              AS customer_number,
                   {src.article_col}       AS article_number,
                   {src.item_text_col}     AS item_text,
                   {src.qty_col}           AS qty,
                   {src.amount_col}        AS amount,
                   {ek}                    AS ek_price,
                   {src.date_expr}         AS beleg_datum
            FROM {src.header_table} h
            JOIN {src.item_table} i ON i.{src.join_key} = h.id
            WHERE {where}
            """  # noqa: S608 — alle Identifier stammen aus code-kontrollierter Config
        )
        return [dict(r) for r in self.db.execute(sql).mappings().all()]

    # ── Aggregation + Upsert ──────────────────────────────────────────────────
    def aggregate(self, dry_run: bool = False) -> dict:
        resolver = self._kunden_resolver()
        artikel = self._artikel_index()
        acc: dict[tuple[str, str], _Acc] = {}
        gelesen = 0
        unmatched_kunde = 0
        unclassified = 0

        for src in self.sources:
            for row in self._read_source(src):
                gelesen += 1
                # Kunde auflösen: bevorzugt customer_number, sonst Referenz-UUID
                kn = None
                if row.get("customer_number"):
                    kn = resolver.get(str(row["customer_number"]))
                if not kn and row.get("customer_ref"):
                    kn = resolver.get(str(row["customer_ref"]))
                if not kn:
                    unmatched_kunde += 1
                    continue
                # Produktgruppe: Artikel-Stamm, sonst Positionstext
                key = artikel.get(row.get("article_number"))
                if key is None:
                    key = klassifiziere_artikel(name=row.get("item_text"))
                if key is None:
                    unclassified += 1
                    continue

                a = acc.setdefault((kn, key), _Acc())
                amount = float(row["amount"] or 0)
                qty = float(row["qty"] or 0)
                a.umsatz += amount
                a.menge += qty
                if row.get("ek_price") is not None:
                    a.db += amount - float(row["ek_price"]) * qty
                    a.db_bekannt = True
                d = row.get("beleg_datum")
                if d and (a.letzter is None or d > a.letzter):
                    a.letzter = d
                a.quellen.add(src.name)

        if not dry_run:
            for (kn, key), a in acc.items():
                self._upsert(kn, key, a)
            self.db.commit()

        return {
            "positionen_gelesen": gelesen,
            "kunde_nicht_aufloesbar": unmatched_kunde,
            "ohne_produktgruppe": unclassified,
            "aggregierte_zeilen": len(acc),
            "betroffene_kunden": len({kn for kn, _ in acc}),
            "dry_run": dry_run,
        }

    def _upsert(self, kunden_nr: str, produktgruppe: str, a: _Acc) -> None:
        self.db.execute(
            text(
                """
                INSERT INTO public.kunden_produktgruppen_bezug
                  (kunden_nr, produktgruppe, menge_12m, umsatz_12m_eur, db_12m_eur,
                   letzter_bezug, quelle, tenant_id)
                VALUES (:k, :g, :menge, :umsatz, :db, :last, 'verkauf', :t)
                ON CONFLICT (kunden_nr, produktgruppe, tenant_id) DO UPDATE SET
                  menge_12m = EXCLUDED.menge_12m,
                  umsatz_12m_eur = EXCLUDED.umsatz_12m_eur,
                  db_12m_eur = EXCLUDED.db_12m_eur,
                  letzter_bezug = EXCLUDED.letzter_bezug,
                  quelle = 'verkauf',
                  updated_at = now()
                """
            ),
            {
                "k": kunden_nr, "g": produktgruppe,
                "menge": round(a.menge, 2),
                "umsatz": round(a.umsatz, 2),
                "db": round(a.db, 2) if a.db_bekannt else None,
                "last": a.letzter, "t": self.tenant_id,
            },
        )
