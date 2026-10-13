"""DocFlow-Belege in der Form des Belegvertrags (BELEG-011).

Der Adapter liest nur. Er entscheidet nichts selbst, was ein Kommando entscheidet: Ob gebucht werden kann, sagt
die Pruefung von Finance, die auch ``post`` benutzt; ob ein Folgebeleg moeglich ist, sagen Restmenge und
Rechnungsweg, die auch ``convert`` benutzt.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Callable, Optional

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.core.belegkommandos import BELEGKOMMANDOS
from app.core.belegvertrag import (
    BELEGARTEN, Beleg, Belegaktion, Belegdokument, Belegposition, Freigabestand, Belegvariante, Buchung, Historieneintrag, Kettenglied, Partner,
    Steuergruppe, Summen, ohne_preise,
)
from app.core.exceptions import ConflictError
from app.services.docflow_freigabe import DocflowFreigabe
from app.services.docflow_service import TRANSITIONS, DocflowService

_ENDE = {"reversed", "cancelled"}


def _d(wert: Any) -> Decimal:
    return Decimal(str(wert or 0))


def _datum(wert: Any) -> Optional[date]:
    return wert.date() if isinstance(wert, datetime) else wert


Darf = Callable[[str, str], bool]


def lies_beleg(svc: DocflowService, doc_id: str, darf: Optional[Darf] = None,
               leser: Optional[str] = None) -> Optional[Beleg]:
    """Der Beleg in Vertragsform — oder ``None``, wenn es ihn nicht gibt oder seine Belegart keine Variante hat.

    ``darf(recht, belegart)`` ist das Recht des Lesers. Ohne Preisrecht kommen weder Preisfelder noch Summen,
    und eine Aktion ohne Recht ist gesperrt. Ohne Angabe (Skripte, Tests des Adapters) gilt alles als erlaubt.
    ``leser`` ist die Kennung der Anmeldung — fuer die Funktionstrennung bei Freigaben.
    """
    header = svc.fetch_header(doc_id)
    if not header:
        return None
    variante = BELEGARTEN.get(str(header["doc_type"]))
    # Ein Kopf, der nur ein Archivstueck des alten Rechnungswegs traegt, ist kein DocFlow-Beleg.
    if variante is None or str(header.get("source_system") or "") == "gobd_artifact":
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
        partner=_partner(svc, variante, partner_nr),
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
        dokumente=_dokumente(svc, doc_id),
        historie=[
            Historieneintrag(
                zeitpunkt=h["changed_at"], von_status=h.get("from_status"), nach_status=h["to_status"],
                kommando=h.get("command"), akteur=h.get("actor"), grund=h.get("reason"),
            )
            for h in svc.fetch_status_history(doc_id)
        ],
        aktionen=_aktionen(svc, header, variante, status, buchung, offen, darf, leser),
        freigaben=_freigaben(DocflowFreigabe(svc.db, svc.tenant_id), doc_id) if variante.bucht else [],
    )
    if not variante.mit_preisen or (darf is not None and not darf("preise", variante.belegart)):
        return ohne_preise(beleg)
    return beleg


def _partner(svc: DocflowService, variante: Belegvariante, wert: Any) -> Optional[Partner]:
    """Nummer und Name des Partners aus den Stammdaten des Bereichs.

    DocFlow fuehrt am Beleg nur eine Kennung. Gefunden wird der Kunde ueber seine Kennung oder Kundennummer, der
    Lieferant ueber Kennung oder Lieferantennummer. Ohne Treffer bleibt die Kennung des Belegs stehen, ohne Namen.
    """
    if not wert:
        return None
    kennung = str(wert)
    if variante.partnerrolle == "lieferant":
        sql = ("SELECT lieferantennummer, firmenname FROM domain_einkauf.lieferanten "
               "WHERE tenant_id = :t AND (id::text = :p OR lieferantennummer = :p) LIMIT 1")
    else:
        sql = ("SELECT c.customer_number, COALESCE(NULLIF(bp.name_1, ''), c.company_name) "
               "FROM domain_crm.customers c LEFT JOIN domain_crm.business_partners bp "
               "ON bp.partner_id = c.business_partner_id AND bp.tenant_id = c.tenant_id "
               "WHERE c.tenant_id = :t AND (c.id = :p OR c.customer_number = :p) LIMIT 1")
    try:
        # Eigener Sicherungspunkt: Fehlen die Stammdatentabellen, bleibt die Transaktion des Lesens gesund.
        with svc.db.begin_nested():
            zeile = svc.db.execute(text(sql), {"t": svc.tenant_id, "p": kennung}).first()
    except (OperationalError, ProgrammingError):
        zeile = None
    if not zeile:
        return Partner(rolle=variante.partnerrolle, nummer=kennung)
    return Partner(rolle=variante.partnerrolle, nummer=str(zeile[0] or kennung), name=(zeile[1] or None))


def _dokumente(svc: DocflowService, doc_id: str) -> list[Belegdokument]:
    """Die Anhaenge des Belegs aus dem revisionssicheren Artefaktspeicher — jede Version, die juengste als aktuell."""
    zeilen = svc.db.execute(
        text(
            "SELECT id, artifact_type, file_name, COALESCE(version, 1) AS version, "
            "COALESCE(freigabe_status, 'entwurf') AS stand, created_at "
            "FROM domain_docflow.document_artifacts WHERE tenant_id = :t AND header_id = :id "
            "ORDER BY artifact_type, version"
        ),
        {"t": svc.tenant_id, "id": doc_id},
    ).mappings().all()
    juengste: dict[str, int] = {}
    for z in zeilen:
        juengste[z["artifact_type"]] = max(juengste.get(z["artifact_type"], 0), int(z["version"]))
    return [
        Belegdokument(
            dokument_id=str(z["id"]), bezeichnung=str(z["file_name"] or z["artifact_type"]), art=str(z["artifact_type"]),
            datum=z["created_at"], version=int(z["version"]), stand=str(z["stand"]),
            aktuell=int(z["version"]) == juengste[z["artifact_type"]],
        )
        for z in zeilen
    ]


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


_FREIGABESTAND = {"requested": "angefragt", "granted": "erteilt", "denied": "abgelehnt", "consumed": "verbraucht",
                  "expired": "abgelaufen", "invalidated": "ungueltig"}


def _freigaben(engine: DocflowFreigabe, doc_id: str) -> list[Freigabestand]:
    jetzt = datetime.now(timezone.utc)
    return [
        Freigabestand(
            freigabe_id=str(f["id"]), aktion=f["action"], risiko=f["risk"],
            stand="abgelaufen" if f["status"] in ("requested", "granted") and f["expires_at"] <= jetzt
            else _FREIGABESTAND[f["status"]],
            betrag=f["amount"], grund=f["reason"], angefragt_von=str(f["requested_by"]), angefragt_am=f["requested_at"],
            entschieden_von=f["decided_by"], entschieden_am=f["decided_at"], gueltig_bis=f["expires_at"],
        )
        for f in engine.liste(doc_id)
    ]


def _freigabe_einrechnen(engine: DocflowFreigabe, header: dict[str, Any], aktionen: list[Belegaktion],
                         leser: Optional[str]) -> dict[str, str]:
    """Buchen und Stornieren nach der Freigabematrix: gesperrt, solange die zweite Person fehlt.

    Gibt je zusaetzlicher Aktion das Recht zurueck, das sie braucht.
    """
    rechte: dict[str, str] = {}
    for key, aktion_name in (("buchen", "post"), ("stornieren", "reverse")):
        aktion = next((a for a in aktionen if a.key == key), None)
        if aktion is None:
            continue
        bedarf = engine.anforderung_fuer(header, aktion_name)
        aktion.freigabe_noetig = bedarf.zweitfreigabe
        # Ein sachlicher Sperrgrund bleibt stehen; dann stellt sich die Frage der Freigabe noch nicht.
        if not bedarf.zweitfreigabe or not aktion.erlaubt or engine.gueltige(header, aktion_name):
            continue
        aktion.erlaubt = False
        aktion.grund = f"Freigabe erforderlich ({bedarf.risiko}): {bedarf.grund}"
        offene = engine.offene(header, aktion_name)
        if offene is None:
            aktionen.append(Belegaktion(key=f"freigabe_anfordern:{aktion_name}", bezeichnung="Freigabe anfragen",
                                        kommando="docflow.approval_request"))
            rechte[f"freigabe_anfordern:{aktion_name}"] = "buchen" if aktion_name == "post" else "stornieren"
            continue
        selbst = leser is not None and leser in {str(offene["requested_by"]), str(header.get("created_by") or "")}
        aktionen.append(Belegaktion(
            key=f"freigabe_erteilen:{aktion_name}", bezeichnung="Freigabe erteilen", kommando="docflow.approval_decide",
            erlaubt=not selbst,
            grund="Funktionstrennung: Wer den Beleg angelegt oder die Freigabe angefragt hat, entscheidet nicht."
            if selbst else None,
        ))
        rechte[f"freigabe_erteilen:{aktion_name}"] = "freigeben_erhoeht" if bedarf.erhoeht else "freigeben"
    return rechte


def _aktion(key: str, bezeichnung: str, kommando: str, *, grund: Optional[str] = None,
            folgebelegart: Optional[str] = None) -> Belegaktion:
    """Eine Aktion des Belegs. Ob sie eine zweite Person braucht, rechnet ``_freigabe_einrechnen`` je Beleg ein."""
    return Belegaktion(
        key=key, bezeichnung=bezeichnung, kommando=kommando, folgebelegart=folgebelegart,
        erlaubt=grund is None, grund=grund,
    )


def _aktionen(svc: DocflowService, header: dict[str, Any], variante: Belegvariante, status: str, buchung: Buchung,
              offen: dict[str, Decimal], darf: Optional[Darf] = None, leser: Optional[str] = None) -> list[Belegaktion]:
    """Was mit dem Beleg in seinem Zustand geht — und was davon der Leser darf."""
    aktionen = _aktionen_im_zustand(svc, str(header["id"]), variante, status, buchung, offen)
    eigene_rechte = _freigabe_einrechnen(DocflowFreigabe(svc.db, svc.tenant_id), header, aktionen, leser)
    if darf is None:
        return aktionen
    for aktion in aktionen:
        recht = eigene_rechte.get(aktion.key) or BELEGKOMMANDOS[aktion.kommando].recht
        # Ein Folgebeleg braucht das Recht an der Belegart, die entsteht.
        if aktion.erlaubt and not darf(recht, aktion.folgebelegart or variante.belegart):
            aktion.erlaubt = False
            aktion.grund = "Keine Berechtigung."
    return aktionen


def _aktionen_im_zustand(svc: DocflowService, doc_id: str, variante: Belegvariante, status: str, buchung: Buchung,
                         offen: dict[str, Decimal]) -> list[Belegaktion]:
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
