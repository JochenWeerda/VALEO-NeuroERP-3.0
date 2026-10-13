"""DocFlow-Belege in der Form des Belegvertrags (BELEG-011).

Der Adapter liest nur. Er entscheidet nichts selbst, was ein Kommando entscheidet: Ob gebucht werden kann, sagt
die Pruefung von Finance, die auch ``post`` benutzt; ob ein Folgebeleg moeglich ist, sagen Restmenge und
Rechnungsweg, die auch ``convert`` benutzt.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text

from app.core.belegkommandos import BELEGKOMMANDOS
from app.core.belegvertrag import (
    BELEGARTEN, Beleg, Belegaktion, Belegposition, Belegvariante, Buchung, Historieneintrag, Kettenglied, Partner,
    Steuergruppe, Summen, ohne_preise,
)
from app.core.exceptions import ConflictError
from app.services.docflow_service import TRANSITIONS, DocflowService

_ENDE = {"reversed", "cancelled"}


def _d(wert: Any) -> Decimal:
    return Decimal(str(wert or 0))


def _datum(wert: Any) -> Optional[date]:
    return wert.date() if isinstance(wert, datetime) else wert


def lies_beleg(svc: DocflowService, doc_id: str) -> Optional[Beleg]:
    """Der Beleg in Vertragsform — oder ``None``, wenn es ihn nicht gibt oder seine Belegart keine Variante hat."""
    header = svc.fetch_header(doc_id)
    if not header:
        return None
    variante = BELEGARTEN.get(str(header["doc_type"]))
    if variante is None:
        return None
    items = svc.fetch_items(doc_id)
    status = str(header["status"])
    offen = _offene_mengen(svc, doc_id, variante, items)
    buchung = _buchung(svc, header, variante)

    partner_nr = header.get("supplier_id") if variante.partnerrolle == "lieferant" else header.get("customer_id")
    gruppen: dict[tuple[str | None, Decimal], list[Decimal]] = {}
    for i in items:
        summe = gruppen.setdefault((i.get("tax_code") or None, _d(i.get("tax_rate"))), [Decimal("0"), Decimal("0")])
        summe[0] += _d(i.get("line_total_net"))
        summe[1] += _d(i.get("line_total_tax"))

    beleg = Beleg(
        beleg_id=str(header["id"]),
        belegart=variante.belegart,
        beleg_nr=str(header["doc_number"]),
        status=status,
        belegdatum=_datum(header["document_date"]),
        buchungsdatum=_datum(header.get("posting_date")),
        waehrung=str(header.get("currency") or "EUR"),
        version=int(header.get("version") or 1),
        partner=Partner(rolle=variante.partnerrolle, nummer=str(partner_nr)) if partner_nr else None,
        positionen=[
            Belegposition(
                pos_nr=int(i.get("line_number") or 0),
                artikel_nr=str(i.get("article_number") or ""),
                bezeichnung=i.get("description"),
                menge=_d(i.get("quantity")),
                einheit=i.get("unit"),
                charge=i.get("charge"),
                menge_uebernommen=(_d(i.get("quantity")) - offen[str(i["id"])]) if variante.folgebelege else None,
                menge_offen=offen[str(i["id"])] if variante.folgebelege else None,
                einzelpreis=_d(i.get("unit_price")),
                rabatt_prozent=_d(i.get("discount_percent")),
                steuerschluessel=i.get("tax_code") or None,
                steuersatz=_d(i.get("tax_rate")),
                netto=_d(i.get("line_total_net")),
                steuer=_d(i.get("line_total_tax")),
                brutto=_d(i.get("line_total_gross")),
                aufwandskonto=i.get("expense_account") or None,
            )
            for i in items
        ],
        summen=Summen(
            netto=_d(header.get("total_net")), steuer=_d(header.get("total_tax")), brutto=_d(header.get("total_gross")),
            steuergruppen=[
                Steuergruppe(steuerschluessel=schluessel, steuersatz=satz, netto=netto, steuer=steuer)
                for (schluessel, satz), (netto, steuer) in gruppen.items()
            ],
        ),
        buchung=buchung,
        kette=_kette(svc, doc_id),
        historie=[
            Historieneintrag(
                zeitpunkt=h["changed_at"], von_status=h.get("from_status"), nach_status=h["to_status"],
                kommando=h.get("command"), akteur=h.get("actor"), grund=h.get("reason"),
            )
            for h in svc.fetch_status_history(doc_id)
        ],
        aktionen=_aktionen(svc, doc_id, variante, status, buchung, offen),
    )
    return beleg if variante.mit_preisen else ohne_preise(beleg)


def _offene_mengen(svc: DocflowService, doc_id: str, variante: Belegvariante, items: list[dict[str, Any]]) -> dict[str, Decimal]:
    """Je Position die Menge, die noch in keinen Folgebeleg gegangen ist.

    Ein Auftrag wird ueber Lieferungen oder direkt berechnet, nie beides; uebernommen ist deshalb der groessere
    der beiden Wege.
    """
    uebernommen: dict[str, Decimal] = {}
    for folgeart in variante.folgebelege:
        for item_id, menge in svc.umgewandelte_mengen(doc_id, TRANSITIONS[variante.belegart][folgeart]).items():
            uebernommen[item_id] = max(uebernommen.get(item_id, Decimal("0")), menge)
    return {
        str(i["id"]): max(_d(i.get("quantity")) - uebernommen.get(str(i["id"]), Decimal("0")), Decimal("0"))
        for i in items
    }


def _buchung(svc: DocflowService, header: dict[str, Any], variante: Belegvariante) -> Buchung:
    if not variante.bucht:
        return Buchung()
    doc_id, status, nummer = str(header["id"]), str(header["status"]), str(header["doc_number"])
    journal = svc.db.execute(
        text(
            "SELECT journal_entry_id FROM domain_docflow.document_postings "
            "WHERE tenant_id = :t AND header_id = :id AND journal_entry_id IS NOT NULL ORDER BY posted_at, id LIMIT 1"
        ),
        {"t": svc.tenant_id, "id": doc_id},
    ).scalar()
    if status == "posted":
        if journal:
            return Buchung(stand="gebucht", journal_id=str(journal))
        return Buchung(stand="pruefen", grund="Der Beleg steht auf gebucht, hat aber keinen Buchungsnachweis.")
    if status == "reversed" and journal:
        return Buchung(stand="storniert", journal_id=str(journal))
    if status in _ENDE:
        return Buchung()
    # Dieselbe Pruefung, die ``post`` vor dem Buchen macht.
    partner = header.get("supplier_id") if variante.partnerrolle == "lieferant" else header.get("customer_id")
    if not partner:
        return Buchung(stand="pruefen", grund="Lieferant fehlt." if variante.partnerrolle == "lieferant" else "Kunde fehlt.")
    try:
        if variante.richtung == "einkauf":
            svc._vorsteuergruppen_des_belegs(doc_id, nummer)
        else:
            svc._steuergruppen_der_rechnung(doc_id, nummer)
    except ConflictError as klaerung:
        return Buchung(stand="pruefen", grund=str(klaerung.detail if hasattr(klaerung, "detail") else klaerung))
    return Buchung()


def _kette(svc: DocflowService, doc_id: str) -> list[Kettenglied]:
    zeilen = svc.db.execute(
        text(
            """
            SELECT 'nachfolger' AS richtung, b.doc_type, b.id, b.doc_number, b.status, b.created_at,
                   (SELECT SUM(l.quantity_linked) FROM domain_docflow.document_links l
                     WHERE l.tenant_id = k.tenant_id AND l.from_header_id = k.from_header_id
                       AND l.to_header_id = k.to_header_id) AS menge
            FROM domain_docflow.document_header_links k
            JOIN domain_docflow.document_headers b ON b.id = k.to_header_id AND b.tenant_id = k.tenant_id
            WHERE k.tenant_id = :t AND k.from_header_id = :id AND b.deleted_at IS NULL
            UNION ALL
            SELECT 'vorgaenger', b.doc_type, b.id, b.doc_number, b.status, b.created_at,
                   (SELECT SUM(l.quantity_linked) FROM domain_docflow.document_links l
                     WHERE l.tenant_id = k.tenant_id AND l.from_header_id = k.from_header_id
                       AND l.to_header_id = k.to_header_id)
            FROM domain_docflow.document_header_links k
            JOIN domain_docflow.document_headers b ON b.id = k.from_header_id AND b.tenant_id = k.tenant_id
            WHERE k.tenant_id = :t AND k.to_header_id = :id AND b.deleted_at IS NULL
            ORDER BY 1 DESC, 6, 4
            """
        ),
        {"t": svc.tenant_id, "id": doc_id},
    ).fetchall()
    return [
        Kettenglied(richtung=z[0], belegart=str(z[1]), beleg_id=str(z[2]), beleg_nr=str(z[3]), status=str(z[4]),
                    menge=_d(z[6]) if z[6] is not None else None)
        for z in zeilen
    ]


def _aktion(key: str, bezeichnung: str, kommando: str, *, grund: Optional[str] = None,
            folgebelegart: Optional[str] = None) -> Belegaktion:
    """Eine Aktion des Belegs; ob sie eine Freigabe braucht, sagt das Verzeichnis der Belegkommandos."""
    return Belegaktion(
        key=key, bezeichnung=bezeichnung, kommando=kommando, folgebelegart=folgebelegart,
        freigabe_noetig=BELEGKOMMANDOS[kommando].freigabe_noetig, erlaubt=grund is None, grund=grund,
    )


def _aktionen(svc: DocflowService, doc_id: str, variante: Belegvariante, status: str, buchung: Buchung,
              offen: dict[str, Decimal]) -> list[Belegaktion]:
    """Was mit dem Beleg in seinem Zustand geht. Das Recht des Lesers ist hier noch nicht eingerechnet (BELEG-012)."""
    aktionen: list[Belegaktion] = []
    if status == "draft":
        aktionen.append(_aktion("bearbeiten", "Bearbeiten", "docflow.update"))
        aktionen.append(_aktion("freigeben", "Freigeben", "docflow.release"))
    if variante.bucht and status not in _ENDE | {"posted"}:
        aktionen.append(_aktion(
            "buchen", "Buchen", "docflow.post", grund=buchung.grund if buchung.stand == "pruefen" else None))
    for folgeart in variante.folgebelege:
        grund = None
        if status in _ENDE:
            grund = "Der Beleg ist storniert."
        elif not any(menge > 0 for menge in offen.values()):
            grund = "Alle Mengen sind bereits übernommen."
        else:
            try:
                svc._pruefe_rechnungsweg(doc_id, variante.belegart, TRANSITIONS[variante.belegart][folgeart])
            except ConflictError as konflikt:
                grund = str(konflikt.detail if hasattr(konflikt, "detail") else konflikt)
        aktionen.append(_aktion(
            f"umwandeln:{folgeart}", f"{BELEGARTEN[folgeart].bezeichnung} erstellen", "docflow.convert",
            grund=grund, folgebelegart=folgeart))
    if status not in _ENDE:
        grund = None
        if variante.belegart.endswith("_credit_memo") and status == "posted":
            grund = "Eine gebuchte Gutschrift lässt sich noch nicht stornieren: Die Gegenbuchung fehlt."
        elif variante.belegart.endswith("_invoice") and status != "posted":
            grund = "Storniert wird nur ein gebuchter Beleg."
        aktionen.append(_aktion("stornieren", "Stornieren", "docflow.reverse", grund=grund))
    return aktionen
