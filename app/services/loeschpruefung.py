"""Loeschpruefung nach den Aufbewahrungsfristen (M7 Loeschkonzept, 26.11.2026) - Bericht, loescht nie.

Grundlage ist der Fristenkatalog ``app/core/gobd_retention.py`` (geltendes Recht, PR #211). Je Datenkategorie zeigt der
Bericht, wie viele Saetze noch aufzubewahren, gesperrt oder nach Fristablauf loeschbar sind - mit den IDs der
loeschbaren Saetze, ohne Inhalte. Das Loeschen selbst ist eine irreversible Handlung und nach der Agentenmatrix
(``docs/security/umgebungen-und-agentenrechte.md``) immer freigabepflichtig; es ist nicht Teil dieses Moduls.

Regeln:
- Fristende = 31.12. des Jahres (Belegdatum + Frist), § 147 Abs. 4 AO.
- Lieferscheine: Ist eine Rechnung verknuepft (``document_header_links``), endet die Frist mit deren Datum
  (§ 147 Abs. 3 Satz 3/4 AO); ohne Verknuepfung gilt der Lieferschein vorsichtig als Buchungsbeleg (8 Jahre).
- Aktive Loeschsperren (``gobd_loeschsperren``, Status ACTIVE, ohne oder mit kuenftigem Enddatum) sperren den Satz.
- Ablaufhemmung (§ 147 Abs. 3 Satz 5 AO): Ist ``festsetzungsfrist_offen_bis`` nicht angegeben, ist der Bericht
  ausdruecklich "vorbehaltlich offener Festsetzungsfrist"; mit Datum gilt bis dahin nichts als loeschbar.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.business_time import business_today
from app.core.gobd_retention import RetentionKlasse, fristende, regel_fuer

#: Docflow-Belegart -> Dokumenttyp des Fristenkatalogs
BELEGART_ZU_DOKUMENTTYP: dict[str, str] = {
    "sales_invoice": "ar_invoice",
    "sales_credit_memo": "ar_invoice",
    "purchase_invoice": "ap_invoice",
    "purchase_credit_memo": "ap_invoice",
    "sales_order": "handelsbrief",
    "sales_offer": "handelsbrief",
    "purchase_order": "handelsbrief",
    "sales_delivery": "lieferschein",
    "goods_receipt": "lieferschein",
}
RECHNUNGSARTEN = ("sales_invoice", "purchase_invoice", "sales_credit_memo", "purchase_credit_memo")


@dataclass
class Kategorie:
    dokumenttyp: str
    rechtsgrundlage: str
    gesamt: int = 0
    in_frist: int = 0
    gesperrt: int = 0
    loeschbar: int = 0
    ohne_zuordnung: int = 0

    def als_dict(self, ids: list[str]) -> dict[str, Any]:
        return {"dokumenttyp": self.dokumenttyp, "rechtsgrundlage": self.rechtsgrundlage, "gesamt": self.gesamt,
                "in_frist": self.in_frist, "gesperrt": self.gesperrt, "loeschbar": self.loeschbar,
                "loeschbar_ids": ids, "vorsichtig_als_beleg": self.ohne_zuordnung}


def _gesperrt(db: Session, tenant_id: str, heute: date) -> tuple[set[str], set[str]]:
    """IDs und Belegtypen unter aktiver Loeschsperre."""
    zeilen = db.execute(text(
        "SELECT dokument_id, dokument_typ FROM public.gobd_loeschsperren WHERE tenant_id = :t AND status = 'ACTIVE' "
        "AND (hold_end_date IS NULL OR hold_end_date >= :h)"), {"t": tenant_id, "h": heute}).fetchall()
    ids = {str(z[0]) for z in zeilen if z[0]}
    typen = {str(z[1]).lower() for z in zeilen if z[1] and not z[0]}  # Sperre auf ganze Belegart
    return ids, typen


def _rechnungsdatum_je_lieferschein(db: Session, tenant_id: str) -> dict[str, date]:
    zeilen = db.execute(text(
        "SELECT CASE WHEN l.from_header_id = d.id THEN l.from_header_id ELSE l.to_header_id END AS lieferschein, "
        "max(r.document_date)::date AS rechnung FROM domain_docflow.document_header_links l "
        "JOIN domain_docflow.document_headers d ON d.id IN (l.from_header_id, l.to_header_id) "
        "AND d.doc_type IN ('sales_delivery', 'goods_receipt') "
        "JOIN domain_docflow.document_headers r ON r.id IN (l.from_header_id, l.to_header_id) AND r.id <> d.id "
        "AND r.doc_type = ANY(:rechnung) WHERE l.tenant_id = :t GROUP BY 1"),
        {"t": tenant_id, "rechnung": list(RECHNUNGSARTEN)}).fetchall()
    return {str(z[0]): z[1] for z in zeilen if z[1]}


def pruefe(db: Session, tenant_id: str, *, heute: date | None = None,
           festsetzungsfrist_offen_bis: date | None = None, max_ids: int = 500) -> dict[str, Any]:
    """Bericht je Datenkategorie. Schreibt nichts."""
    heute = heute or business_today()
    gesperrte_ids, gesperrte_typen = _gesperrt(db, tenant_id, heute)
    gehemmt = festsetzungsfrist_offen_bis is not None and heute <= festsetzungsfrist_offen_bis
    rechnung_zu = _rechnungsdatum_je_lieferschein(db, tenant_id)
    kategorien: dict[str, Kategorie] = {}
    ids: dict[str, list[str]] = defaultdict(list)

    def zaehle(kat_schluessel: str, regel_typ: str, satz_id: str, klasse: RetentionKlasse, ereignis: date,
               belegtyp: str) -> None:
        regel = regel_fuer(regel_typ)
        kat = kategorien.setdefault(kat_schluessel, Kategorie(kat_schluessel, regel.rechtsgrundlage if regel else ""))
        kat.gesamt += 1
        if satz_id in gesperrte_ids or belegtyp.lower() in gesperrte_typen:
            kat.gesperrt += 1
        elif gehemmt or heute <= fristende(klasse, ereignis):
            kat.in_frist += 1
        else:
            kat.loeschbar += 1
            if len(ids[kat_schluessel]) < max_ids:
                ids[kat_schluessel].append(satz_id)

    belege = db.execute(text(
        "SELECT id, doc_type, document_date::date AS datum FROM domain_docflow.document_headers "
        "WHERE tenant_id = :t AND deleted_at IS NULL AND document_date IS NOT NULL"), {"t": tenant_id}).fetchall()
    for satz_id, belegart, datum in belege:
        typ = BELEGART_ZU_DOKUMENTTYP.get(str(belegart))
        if typ is None:
            continue  # Belegart ohne Fristzuordnung (z. B. Testbelege) - im Bericht nicht bewertet
        if typ == "lieferschein":
            rechnung = rechnung_zu.get(str(satz_id))
            if rechnung is not None:
                zaehle("lieferschein", "lieferschein", str(satz_id), RetentionKlasse.BIS_RECHNUNG, rechnung, belegart)
            else:
                zaehle("lieferschein", "lieferschein_beleg", str(satz_id), RetentionKlasse.BELEG_8J, datum, belegart)
                kategorien["lieferschein"].ohne_zuordnung += 1
            continue
        regel = regel_fuer(typ)
        zaehle(typ, typ, str(satz_id), regel.klasse, datum, belegart)

    journal = db.execute(text(
        "SELECT id, entry_date FROM domain_erp.journal_entries WHERE tenant_id = :t AND entry_date IS NOT NULL"),
        {"t": tenant_id}).fetchall()
    for satz_id, datum in journal:
        zaehle("journal_entry", "journal_entry", str(satz_id), RetentionKlasse.STANDARD_10J, datum, "journal_entry")

    return {
        "tenant_id": tenant_id,
        "stichtag": heute.isoformat(),
        "vorbehalt": None if festsetzungsfrist_offen_bis else
        "vorbehaltlich offener Festsetzungsfrist (§ 147 Abs. 3 Satz 5 AO) - vor dem Loeschen mit dem Steuerberater klaeren",
        "kategorien": [kategorien[k].als_dict(ids[k]) for k in sorted(kategorien)],
        "hinweis": "Bericht, keine Loeschung. Loeschen ist irreversibel und braucht die Freigabe einer Person.",
    }
