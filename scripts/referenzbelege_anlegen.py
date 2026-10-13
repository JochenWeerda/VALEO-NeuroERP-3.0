#!/usr/bin/env python3
"""Legt Referenzbelege fuer Sicht- und Browserpruefungen an — wiederholbar, je Mandant.

    python scripts/referenzbelege_anlegen.py --tenant <id>           # zeigt, was angelegt wuerde
    python scripts/referenzbelege_anlegen.py --tenant <id> --apply   # legt an

Phase 0.7 der Belegmasken-Planung: Die Sichtabnahme braucht Belege mit unterschiedlichen Positionen,
Steuerarten und Staenden. Die Belege entstehen ueber DocFlow — denselben Weg, den die Masken benutzen —,
nicht per SQL: Statushistorie, Protokoll, Belegkette und Buchungen sind echt.

Wiederholbar: Jeder Schritt traegt einen festen Idempotenzschluessel. Ein zweiter Lauf legt nichts doppelt an
und bucht nichts doppelt.

Voraussetzung: Der Mandant bucht nach SKR03 mit den Steuerschluesseln 2, 3, 8, 9 und besitzt die Konten dazu
(``scripts/seed_steuerschluessel_skr03.py``) sowie 1400 (Forderungen). Fehlt etwas, bricht das Skript ab,
bevor es etwas anlegt.

Der Satz:

  Verkauf   Angebot -> Auftrag -> zwei Teillieferscheine -> Rechnung 1 (gebucht) mit Gutschrift (gebucht),
            Rechnung 2 (offen); eine Rechnung ohne Steuerschluessel (Entwurf, nicht buchbar);
            eine Rechnung gebucht und storniert.
  Einkauf   Bestellung -> zwei Wareneingaenge -> Eingangsrechnung 1 (gebucht) mit Einkaufsgutschrift (gebucht),
            Eingangsrechnung 2 (offen); eine Eingangsrechnung ohne Steuerschluessel (offen, nicht buchbar);
            eine Eingangsrechnung gebucht und storniert.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from app.api.v1.endpoints.docflow import (  # noqa: E402
    DocflowConvertRequest,
    DocflowCreateRequest,
    DocflowLineInput,
    DocflowPostRequest,
    DocflowReverseRequest,
)
from app.core.database import SessionLocal  # noqa: E402
from app.services.docflow_service import DocflowService  # noqa: E402

AKTEUR = "referenzbelege"
KUNDE = "REF-KUNDE"
LIEFERANT = "REF-LIEFERANT"
# (Artikel, Bezeichnung, Menge, Einheit, Preis, Steuerschluessel)
VERKAUF = [("KAS-27", "Kalkammonsalpeter 27 % N", 25, "t", 350, "3"), ("FW-01", "Futterweizen", 5, "t", 210, "2")]
EINKAUF = [("NPK-15", "NPK-Duenger 15-15-15", 40, "t", 300, "9"), ("SG-WW", "Saatgut Winterweizen", 10, "t", 500, "8")]
SCHLUESSEL = {"2": ("credit_account", "revenue_account"), "3": ("credit_account", "revenue_account"),
              "8": ("debit_account", "expense_account"), "9": ("debit_account", "expense_account")}

PLAN = [
    "Verkauf: Angebot REF-VK-AN-001 (25 t KAS zu 19 %, 5 t Futterweizen zu 7 %)",
    "Verkauf: Auftrag aus dem Angebot",
    "Verkauf: Teillieferschein 1 (15 t KAS, 5 t Futterweizen), Teillieferschein 2 (10 t KAS)",
    "Verkauf: Rechnung aus Lieferschein 1, gebucht; Gutschrift ueber 2 t KAS, gebucht",
    "Verkauf: Rechnung aus Lieferschein 2, offen",
    "Verkauf: Rechnung REF-VK-RE-OHNE ohne Steuerschluessel, Entwurf (nicht buchbar)",
    "Verkauf: Rechnung REF-VK-RE-STORNO, gebucht und storniert",
    "Einkauf: Bestellung REF-EK-BE-001 (40 t NPK zu 19 %, 10 t Saatgut zu 7 %)",
    "Einkauf: Wareneingang 1 (25 t NPK, 10 t Saatgut), Wareneingang 2 (15 t NPK)",
    "Einkauf: Eingangsrechnung aus Wareneingang 1, gebucht; Einkaufsgutschrift ueber 1 t NPK, gebucht",
    "Einkauf: Eingangsrechnung aus Wareneingang 2, offen",
    "Einkauf: Eingangsrechnung REF-EK-RE-OHNE ohne Steuerschluessel, offen (nicht buchbar)",
    "Einkauf: Eingangsrechnung REF-EK-RE-STORNO, gebucht und storniert",
]


def fehlende_voraussetzungen(db, tenant_id: str) -> list[str]:
    """Was dem Mandanten fehlt, um den Satz zu buchen. Leer = alles da."""
    fehlt: list[str] = []
    konten = {str(z[0]) for z in db.execute(text(
        "SELECT account_number FROM domain_erp.chart_of_accounts WHERE tenant_id = :t AND COALESCE(is_active, true) "
        "AND deleted_at IS NULL"), {"t": tenant_id}).fetchall()}
    zeilen = {str(z[0]): z for z in db.execute(text(
        "SELECT code, credit_account, revenue_account, debit_account, expense_account FROM domain_erp.tax_keys "
        "WHERE tenant_id = :t AND active"), {"t": tenant_id}).fetchall()}
    felder = {"credit_account": 1, "revenue_account": 2, "debit_account": 3, "expense_account": 4}
    for code, noetig in SCHLUESSEL.items():
        if code not in zeilen:
            fehlt.append(f"Steuerschluessel {code}")
            continue
        for feld in noetig:
            konto = zeilen[code][felder[feld]]
            if not konto:
                fehlt.append(f"Steuerschluessel {code}: {feld} ist leer")
            elif str(konto) not in konten:
                fehlt.append(f"Steuerschluessel {code}: Konto {konto} gehoert dem Mandanten nicht")
    for konto, wofuer in (("1400", "Forderungen"), ("1600", "Verbindlichkeiten")):
        if konto not in konten:
            fehlt.append(f"Konto {konto} ({wofuer})")
    return fehlt


def _positionen(zeilen, mit_schluessel: bool = True) -> list[DocflowLineInput]:
    return [
        DocflowLineInput(article_number=nr, description=name, quantity=menge, unit=einheit, unit_price=preis,
                         tax_code=code if mit_schluessel else None)
        for nr, name, menge, einheit, preis, code in zeilen
    ]


class Satz:
    """Die Schritte des Referenzsatzes; jeder mit festem Schluessel, damit ein zweiter Lauf nichts verdoppelt."""

    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        self.belege: list[dict[str, Any]] = []

    def _svc(self, db) -> DocflowService:
        return DocflowService(db, self.tenant_id, AKTEUR)

    def _merke(self, db, doc_id: str, rolle: str) -> str:
        kopf = self._svc(db).fetch_header(doc_id) or {}
        self.belege = [b for b in self.belege if b["id"] != doc_id]
        self.belege.append({"id": doc_id, "rolle": rolle, "doc_type": kopf.get("doc_type"),
                            "doc_number": kopf.get("doc_number"), "status": kopf.get("status")})
        return doc_id

    def anlegen(self, db, rolle: str, doc_type: str, nummer: str, zeilen, *, status: str = "open",
                mit_schluessel: bool = True) -> str:
        einkauf = doc_type.startswith("purchase") or doc_type == "goods_receipt"
        doc_id = self._svc(db).create_document(DocflowCreateRequest(
            doc_type=doc_type, doc_number=nummer, status=status,
            customer_id=None if einkauf else KUNDE, supplier_id=LIEFERANT if einkauf else None,
            items=_positionen(zeilen, mit_schluessel), idempotency_key=f"referenz-anlegen-{nummer}",
        ))
        return self._merke(db, doc_id, rolle)

    def wandeln(self, db, rolle: str, quelle: str, ziel: str, mengen: Optional[dict[int, float]] = None) -> str:
        """``mengen``: Positionsnummer der Quelle -> Menge; ohne Angabe der ganze Beleg."""
        svc = self._svc(db)
        je_position = None
        if mengen is not None:
            nach_nummer = {int(i["line_number"]): str(i["id"]) for i in svc.fetch_items(quelle)}
            je_position = {nach_nummer[nr]: menge for nr, menge in mengen.items()}
        antwort = svc.convert(quelle, DocflowConvertRequest(
            target_doc_type=ziel, idempotency_key=f"referenz-wandeln-{rolle}", quantities_by_source_item_id=je_position or {},
        ))
        return self._merke(db, str(antwort["target_doc_id"]), rolle)

    def buchen(self, db, doc_id: str, rolle: str) -> None:
        self._svc(db).post_document(doc_id, DocflowPostRequest(idempotency_key=f"referenz-buchen-{rolle}"))
        self._merke(db, doc_id, rolle)

    def stornieren(self, db, doc_id: str, rolle: str) -> None:
        self._svc(db).reverse_document(doc_id, DocflowReverseRequest(
            idempotency_key=f"referenz-storno-{rolle}", reason="Referenzbeleg: Storno zur Sichtpruefung"))
        self._merke(db, doc_id, rolle)


def lege_an(db, tenant_id: str) -> list[dict[str, Any]]:
    """Legt den Satz an (DocFlow schreibt je Schritt fest). Gibt die Belege mit Rolle, Art, Nummer und Stand zurueck."""
    fehlt = fehlende_voraussetzungen(db, tenant_id)
    if fehlt:
        raise RuntimeError("Voraussetzungen fehlen: " + "; ".join(fehlt))
    s = Satz(tenant_id)

    # --- Verkauf ---
    angebot = s.anlegen(db, "vk-angebot", "sales_offer", "REF-VK-AN-001", VERKAUF)
    auftrag = s.wandeln(db, "vk-auftrag", angebot, "sales_order")
    ls1 = s.wandeln(db, "vk-lieferschein-1", auftrag, "sales_delivery", {1: 15, 2: 5})
    ls2 = s.wandeln(db, "vk-lieferschein-2", auftrag, "sales_delivery", {1: 10})
    re1 = s.wandeln(db, "vk-rechnung-1", ls1, "sales_invoice")
    s.buchen(db, re1, "vk-rechnung-1")
    gutschrift = s.wandeln(db, "vk-gutschrift", re1, "sales_credit_memo", {1: 2})
    s.buchen(db, gutschrift, "vk-gutschrift")
    s.wandeln(db, "vk-rechnung-2", ls2, "sales_invoice")
    s.anlegen(db, "vk-rechnung-ohne-schluessel", "sales_invoice", "REF-VK-RE-OHNE", VERKAUF[:1],
              status="draft", mit_schluessel=False)
    storno = s.anlegen(db, "vk-rechnung-storno", "sales_invoice", "REF-VK-RE-STORNO", VERKAUF[1:])
    s.buchen(db, storno, "vk-rechnung-storno")
    s.stornieren(db, storno, "vk-rechnung-storno")

    # --- Einkauf ---
    bestellung = s.anlegen(db, "ek-bestellung", "purchase_order", "REF-EK-BE-001", EINKAUF)
    we1 = s.wandeln(db, "ek-wareneingang-1", bestellung, "goods_receipt", {1: 25, 2: 10})
    we2 = s.wandeln(db, "ek-wareneingang-2", bestellung, "goods_receipt", {1: 15})
    er1 = s.wandeln(db, "ek-rechnung-1", we1, "purchase_invoice")
    s.buchen(db, er1, "ek-rechnung-1")
    ek_gutschrift = s.wandeln(db, "ek-gutschrift", er1, "purchase_credit_memo", {1: 1})
    s.buchen(db, ek_gutschrift, "ek-gutschrift")
    s.wandeln(db, "ek-rechnung-2", we2, "purchase_invoice")
    s.anlegen(db, "ek-rechnung-ohne-schluessel", "purchase_invoice", "REF-EK-RE-OHNE", EINKAUF[:1], mit_schluessel=False)
    ek_storno = s.anlegen(db, "ek-rechnung-storno", "purchase_invoice", "REF-EK-RE-STORNO", EINKAUF[1:])
    s.buchen(db, ek_storno, "ek-rechnung-storno")
    s.stornieren(db, ek_storno, "ek-rechnung-storno")
    return s.belege


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--apply", action="store_true", help="anlegen (sonst nur zeigen)")
    args = parser.parse_args()
    with SessionLocal() as db:
        fehlt = fehlende_voraussetzungen(db, args.tenant)
        if fehlt:
            print("Voraussetzungen fehlen — nichts angelegt:")
            for zeile in fehlt:
                print("  -", zeile)
            return 1
        if not args.apply:
            print(f"Wuerde fuer {args.tenant} anlegen (--apply legt an):")
            for zeile in PLAN:
                print("  -", zeile)
            return 0
        belege = lege_an(db, args.tenant)
    print(f"Referenzbelege fuer {args.tenant}: {len(belege)}")
    for b in belege:
        print(f"  {b['rolle']:30} {b['doc_type']:22} {b['doc_number']:22} {b['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
