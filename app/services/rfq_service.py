"""RFQ-Service (Anfrage → Angebot → Zuschlag → Bestellung)."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def _f(v: Any) -> float:
    return float(v) if v is not None else 0.0


class RfqVersandFehler(DomainError):
    """Anfrage nicht versendet; der Status bleibt, wie er war."""

    error_code = "RFQ_NICHT_VERSENDET"

    def __init__(self, http_status: int, detail: str) -> None:
        super().__init__(detail)
        self.http_status = http_status


class RfqService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def list_requests(self) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, article_id, quantity, needed_by_date, notes, status, created_at "
                "FROM domain_einkauf.rfq_requests WHERE tenant_id = :tid "
                "ORDER BY created_at DESC"
            ),
            {"tid": self.tenant_id},
        ).fetchall()
        return [self._row_to_rfq(r) for r in rows]

    def create_request(
        self,
        *,
        article_id: str,
        quantity: float,
        needed_by_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> dict:
        row = self.db.execute(
            text(
                "INSERT INTO domain_einkauf.rfq_requests "
                "(article_id, quantity, needed_by_date, notes, tenant_id) "
                "VALUES (:aid, :qty, :nbd, :notes, :tid) "
                "RETURNING id, article_id, quantity, needed_by_date, notes, status, created_at"
            ),
            {
                "aid": article_id,
                "qty": quantity,
                "nbd": needed_by_date,
                "notes": notes,
                "tid": self.tenant_id,
            },
        ).fetchone()
        self.db.commit()
        return self._row_to_rfq(row)

    def get_request(self, rfq_id: int) -> Optional[dict]:
        rfq = self._fetch_rfq(rfq_id)
        if not rfq:
            return None
        quotes = self.db.execute(
            text(
                "SELECT id, supplier_id, unit_price, delivery_days, notes, status, received_at "
                "FROM domain_einkauf.rfq_quotes WHERE rfq_id = :rid AND tenant_id = :tid "
                "ORDER BY unit_price"
            ),
            {"rid": rfq_id, "tid": self.tenant_id},
        ).fetchall()
        out = self._row_to_rfq(rfq)
        out["quotes"] = [self._row_to_quote(q) for q in quotes]
        return out

    def send_request(self, rfq_id: int, supplier_ids: Optional[list[str]] = None, *,
                     nutzer: Optional[dict] = None) -> dict:
        """Schickt die Anfrage per E-Mail an jeden gewaehlten Lieferanten (Postfach ``einkauf``).

        ``VERSENDET`` erst, wenn mindestens eine Nachricht angenommen wurde. Bis 08.10.2026
        setzte dieser Weg den Status und meldete ``suppliers_notified`` ohne eine einzige Mail.
        """
        rfq = self._fetch_rfq(rfq_id)
        if not rfq:
            raise ValueError("Anfrage nicht gefunden")
        zeilen = ["Sehr geehrte Damen und Herren,", "",
                  "wir bitten um Ihr Angebot fuer:", f"  Artikel: {rfq[1]}", f"  Menge: {_f(rfq[2]):g}"]
        if rfq[3]:
            zeilen.append(f"  Benoetigt bis: {rfq[3]:%d.%m.%Y}")
        if rfq[4]:
            zeilen += ["", str(rfq[4])]
        zeilen += ["", f"Bitte geben Sie bei Ihrer Antwort die Anfragenummer {rfq_id} an."]
        versand = anfrage_an_lieferanten(self.db, self.tenant_id, supplier_ids,
                                         f"Preisanfrage Nr. {rfq_id}: {rfq[1]}", zeilen, nutzer)
        erreicht = [v["supplier_id"] for v in versand if v["status"] == "gesendet"]
        self.db.execute(
            text(
                "UPDATE domain_einkauf.rfq_requests SET status = 'VERSENDET' "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": rfq_id, "tid": self.tenant_id},
        )
        self.db.commit()
        return {"rfq_id": rfq_id, "status": "VERSENDET", "suppliers_notified": erreicht, "versand": versand}

    def add_quote(
        self,
        rfq_id: int,
        *,
        supplier_id: str,
        unit_price: float,
        delivery_days: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> dict:
        if not self._fetch_rfq(rfq_id):
            raise ValueError("Anfrage nicht gefunden")
        row = self.db.execute(
            text(
                "INSERT INTO domain_einkauf.rfq_quotes "
                "(rfq_id, supplier_id, unit_price, delivery_days, notes, tenant_id) "
                "VALUES (:rid, :sid, :price, :days, :notes, :tid) "
                "RETURNING id, rfq_id, supplier_id, unit_price, delivery_days, notes, status, received_at"
            ),
            {
                "rid": rfq_id,
                "sid": supplier_id,
                "price": unit_price,
                "days": delivery_days,
                "notes": notes,
                "tid": self.tenant_id,
            },
        ).fetchone()
        self.db.execute(
            text(
                "UPDATE domain_einkauf.rfq_requests SET status = 'BEWERTET' "
                "WHERE id = :id AND tenant_id = :tid AND status IN ('VERSENDET', 'OFFEN')"
            ),
            {"id": rfq_id, "tid": self.tenant_id},
        )
        self.db.commit()
        return self._row_to_quote(row, include_rfq_id=True)

    def compare_quotes(self, rfq_id: int) -> dict:
        rfq = self._fetch_rfq(rfq_id)
        if not rfq:
            raise ValueError("Anfrage nicht gefunden")
        rows = self.db.execute(
            text(
                "SELECT id, supplier_id, unit_price, delivery_days, notes, status, "
                "RANK() OVER (ORDER BY unit_price ASC) AS price_rank "
                "FROM domain_einkauf.rfq_quotes "
                "WHERE rfq_id = :rid AND tenant_id = :tid ORDER BY unit_price ASC"
            ),
            {"rid": rfq_id, "tid": self.tenant_id},
        ).fetchall()
        quotes = [
            {
                "id": r[0],
                "supplier_id": r[1],
                "unit_price": _f(r[2]),
                "delivery_days": r[3],
                "notes": r[4],
                "status": r[5],
                "price_rank": int(r[6]),
            }
            for r in rows
        ]
        return {
            "rfq_id": rfq_id,
            "article_id": rfq[1],
            "quantity": _f(rfq[2]),
            "quotes_count": len(quotes),
            "best_price": quotes[0]["unit_price"] if quotes else None,
            "quotes": quotes,
        }

    def accept_quote(self, rfq_id: int, quote_id: int) -> dict:
        rfq = self._fetch_rfq(rfq_id)
        if not rfq:
            raise ValueError("Anfrage nicht gefunden")

        quote = self.db.execute(
            text(
                "SELECT id, supplier_id, unit_price, delivery_days "
                "FROM domain_einkauf.rfq_quotes "
                "WHERE id = :qid AND rfq_id = :rid AND tenant_id = :tid"
            ),
            {"qid": quote_id, "rid": rfq_id, "tid": self.tenant_id},
        ).fetchone()
        if not quote:
            raise ValueError("Angebot nicht gefunden")

        self.db.execute(
            text(
                "UPDATE domain_einkauf.rfq_quotes SET status = 'AKZEPTIERT' "
                "WHERE id = :qid AND tenant_id = :tid"
            ),
            {"qid": quote_id, "tid": self.tenant_id},
        )
        self.db.execute(
            text(
                "UPDATE domain_einkauf.rfq_quotes SET status = 'ABGELEHNT' "
                "WHERE rfq_id = :rid AND id != :qid AND tenant_id = :tid"
            ),
            {"rid": rfq_id, "qid": quote_id, "tid": self.tenant_id},
        )
        self.db.execute(
            text(
                "UPDATE domain_einkauf.rfq_requests SET status = 'ABGESCHLOSSEN' "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": rfq_id, "tid": self.tenant_id},
        )

        quantity = _f(rfq[2])
        unit_price = _f(quote[2])
        netto = round(quantity * unit_price, 2)
        mwst = round(netto * 0.19, 2)
        po_id = self._create_purchase_order(
            lieferant_id=quote[1],
            article_id=rfq[1],
            quantity=quantity,
            unit_price=unit_price,
            netto=netto,
            mwst=mwst,
            delivery_days=quote[3],
            rfq_id=rfq_id,
        )
        self.db.commit()

        return {
            "rfq_id": rfq_id,
            "accepted_quote_id": quote_id,
            "supplier_id": quote[1],
            "unit_price": unit_price,
            "quantity": quantity,
            "total_amount": netto,
            "purchase_order_id": po_id,
            "status": "ABGESCHLOSSEN",
        }

    def _create_purchase_order(
        self,
        *,
        lieferant_id: str,
        article_id: str,
        quantity: float,
        unit_price: float,
        netto: float,
        mwst: float,
        delivery_days: Optional[int],
        rfq_id: int,
    ) -> str:
        po_id = str(uuid.uuid4())
        po_nr = f"RFQ-{rfq_id}-{po_id[:8].upper()}"
        lieferdatum = date.today() + timedelta(days=int(delivery_days or 14))
        self.db.execute(
            text(
                "INSERT INTO domain_einkauf.bestellungen "
                "(id, tenant_id, bestellnummer, lieferant_id, bestelldatum, lieferdatum_wunsch, "
                "status, netto_summe, mwst_betrag, brutto_summe, waehrung, notiz) "
                "VALUES (:id, :tid, :nr, :lf, :bd, :ld, 'bestellt', :netto, :mwst, :brutto, 'EUR', :notiz)"
            ),
            {
                "id": po_id,
                "tid": self.tenant_id,
                "nr": po_nr,
                "lf": lieferant_id,
                "bd": date.today(),
                "ld": lieferdatum,
                "netto": netto,
                "mwst": mwst,
                "brutto": round(netto + mwst, 2),
                "notiz": f"Zuschlag aus RFQ #{rfq_id}",
            },
        )
        pos_id = str(uuid.uuid4())
        self.db.execute(
            text(
                "INSERT INTO domain_einkauf.bestellung_positionen "
                "(id, bestellung_id, pos_nr, artikel_nr, artikel_bezeichnung, menge, einheit, "
                "einzelpreis, netto_betrag, mwst_satz, status) "
                "VALUES (:id, :bid, 1, :anr, :abez, :menge, 't', :preis, :netto, 19, 'offen')"
            ),
            {
                "id": pos_id,
                "bid": po_id,
                "anr": article_id,
                "abez": article_id,
                "menge": quantity,
                "preis": unit_price,
                "netto": netto,
            },
        )
        return po_id

    def _fetch_rfq(self, rfq_id: int) -> Any:
        return self.db.execute(
            text(
                "SELECT id, article_id, quantity, needed_by_date, notes, status, created_at "
                "FROM domain_einkauf.rfq_requests WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": rfq_id, "tid": self.tenant_id},
        ).fetchone()

    @staticmethod
    def _row_to_rfq(row: Any) -> dict:
        return {
            "id": row[0],
            "article_id": row[1],
            "quantity": _f(row[2]),
            "needed_by_date": row[3].isoformat() if row[3] else None,
            "notes": row[4],
            "status": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
        }

    @staticmethod
    def _row_to_quote(row: Any, *, include_rfq_id: bool = False) -> dict:
        out = {
            "id": row[0],
            "supplier_id": row[2] if include_rfq_id else row[1],
            "unit_price": _f(row[3] if include_rfq_id else row[2]),
            "delivery_days": row[4] if include_rfq_id else row[3],
            "notes": row[5] if include_rfq_id else row[4],
            "status": row[6] if include_rfq_id else row[5],
            "received_at": (
                (row[7] if include_rfq_id else row[6]).isoformat()
                if (row[7] if include_rfq_id else row[6])
                else None
            ),
        }
        if include_rfq_id:
            out["rfq_id"] = row[1]
        return out


def _lieferanten_adressen(db: Session, tenant_id: str, ids: list[str]) -> dict[str, tuple[str, Optional[str]]]:
    """Kennung -> (Name, E-Mail). Kennung ist die Lieferanten-ID, deren Partner-ID oder die
    ID des CRM-Geschaeftspartners (der Anfragedialog waehlt aus den CRM-Lieferanten)."""
    gefunden: dict[str, tuple[str, Optional[str]]] = {}
    for kennung, name, adresse in db.execute(
        text(
            "SELECT k.kennung, l.firmenname, COALESCE(NULLIF(l.email_bestellung, ''), NULLIF(l.email, '')) "
            "FROM domain_einkauf.lieferanten l "
            "JOIN unnest(CAST(:ids AS text[])) AS k(kennung) ON k.kennung IN (l.id::text, l.partner_id) "
            "WHERE l.tenant_id = :tid"
        ),
        {"tid": tenant_id, "ids": ids},
    ).fetchall():
        if kennung not in gefunden or (adresse and not gefunden[kennung][1]):
            gefunden[kennung] = (name, adresse)
    rest = [k for k in ids if k not in gefunden]
    if rest:
        for kennung, name, adresse in db.execute(
            text(
                "SELECT partner_id::text, COALESCE(NULLIF(name_1, ''), partner_number), NULLIF(email, '') "
                "FROM domain_crm.business_partners "
                "WHERE tenant_id::text = :tid AND partner_id::text = ANY(CAST(:ids AS text[]))"
            ),
            {"tid": tenant_id, "ids": rest},
        ).fetchall():
            gefunden[kennung] = (name, adresse)
    return gefunden


def anfrage_an_lieferanten(db: Session, tenant_id: str, supplier_ids: Optional[list[str]], betreff: str,
                           zeilen: list[str], nutzer: Optional[dict]) -> list[dict]:
    """Mailt eine Anfrage an jeden Lieferanten (Postfach ``einkauf``) und liefert das Ergebnis je
    Lieferant. Wirft ``RfqVersandFehler``, wenn keiner erreicht wurde — dann ist nichts versendet."""
    from app.services.mail_versand import (
        MailVersandFehler, MailVersandNichtEingerichtet, MailVersandVerweigert, sende_mail,
    )

    ids = list(dict.fromkeys(str(s).strip() for s in (supplier_ids or []) if str(s).strip()))
    if not ids:
        raise RfqVersandFehler(422, "Keine Lieferanten gewaehlt — an wen soll die Anfrage gehen?")
    adressen = _lieferanten_adressen(db, tenant_id, ids)
    unbekannt = [k for k in ids if k not in adressen]
    if unbekannt:
        raise RfqVersandFehler(422, f"Lieferanten nicht gefunden: {', '.join(unbekannt)}")

    versand: list[dict] = []
    for kennung in ids:
        name, adresse = adressen[kennung]
        eintrag = {"supplier_id": kennung, "name": name, "empfaenger": adresse}
        if not adresse:
            versand.append({**eintrag, "status": "fehler", "fehler": "Keine E-Mail-Adresse hinterlegt"})
            continue
        try:
            sende_mail(adresse, betreff, "\n".join(zeilen), db=db, tenant_id=tenant_id,
                       verwendung="einkauf", nutzer=nutzer)
        except MailVersandNichtEingerichtet as fehler:
            raise RfqVersandFehler(503, str(fehler)) from fehler
        except MailVersandVerweigert as fehler:
            raise RfqVersandFehler(403, str(fehler)) from fehler
        except MailVersandFehler as fehler:
            versand.append({**eintrag, "status": "fehler", "fehler": str(fehler)})
            continue
        versand.append({**eintrag, "status": "gesendet", "fehler": None})

    if not any(v["status"] == "gesendet" for v in versand):
        raise RfqVersandFehler(502, "Kein Lieferant erreicht: " + "; ".join(
            f"{v['name']}: {v['fehler']}" for v in versand))
    return versand


def versende_einkauf_anfrage(db: Session, tenant_id: str, anfrage_id: str, supplier_ids: Optional[list[str]],
                             methode: Optional[str], nutzer: Optional[dict]) -> dict:
    """Anfrage (BANF) an Lieferanten: Mail an jeden, danach Status ``ANGEBOTSPHASE``.

    Bis 08.10.2026 antwortete die Maskenbruecke ``sent: true``, ohne zu senden oder zu speichern."""
    from datetime import datetime, timezone

    if (methode or "email") != "email":
        raise RfqVersandFehler(422, f"Versandweg '{methode}' gibt es fuer Anfragen nicht; nur E-Mail.")
    anfrage = db.execute(
        text(
            "SELECT id, anfrage_nummer, artikel, menge, einheit, datum, notizen FROM einkauf_anfragen "
            "WHERE (id = :fid OR anfrage_nummer = :fid) AND tenant_id = :tid LIMIT 1"
        ),
        {"fid": anfrage_id, "tid": tenant_id},
    ).mappings().first()
    if anfrage is None:
        raise RfqVersandFehler(404, "Anfrage nicht gefunden")
    positionen = db.execute(
        text("SELECT artikel, quantity, unit, due_date FROM einkauf_anfragen_positionen "
             "WHERE anfrage_id = :id ORDER BY created_at"),
        {"id": anfrage["id"]},
    ).mappings().all()
    nummer = anfrage["anfrage_nummer"]
    zeilen = ["Sehr geehrte Damen und Herren,", "", "wir bitten um Ihr Angebot fuer:"]
    for pos in positionen or [{"artikel": anfrage["artikel"], "quantity": anfrage["menge"],
                               "unit": anfrage["einheit"], "due_date": anfrage["datum"]}]:
        zeile = f"  {pos['artikel'] or 'Position'}: {_f(pos['quantity']):g} {pos['unit'] or ''}".rstrip()
        if pos["due_date"]:
            zeile += f" (bis {pos['due_date']:%d.%m.%Y})"
        zeilen.append(zeile)
    if anfrage["notizen"]:
        zeilen += ["", str(anfrage["notizen"])]
    zeilen += ["", f"Bitte geben Sie bei Ihrer Antwort die Anfragenummer {nummer} an."]
    versand = anfrage_an_lieferanten(db, tenant_id, supplier_ids, f"Anfrage {nummer}", zeilen, nutzer)
    db.execute(
        text("UPDATE einkauf_anfragen SET status = 'ANGEBOTSPHASE', updated_at = now() "
             "WHERE id = :id AND tenant_id = :tid"),
        {"id": anfrage["id"], "tid": tenant_id},
    )
    db.commit()
    erreicht = [v["supplier_id"] for v in versand if v["status"] == "gesendet"]
    return {"id": str(anfrage["id"]), "status": "ANGEBOTSPHASE", "sent": True, "supplierIds": erreicht,
            "method": "email", "sent_at": datetime.now(timezone.utc).isoformat(), "count": len(erreicht),
            "versand": versand}
