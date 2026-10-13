"""Approval Engine fuer DocFlow-Belege (APPROVAL-001).

Die eine Stelle, die vor dem Buchen und Stornieren fragt, ob der Vorgang eine Freigabe durch eine zweite Person
braucht und ob eine gueltige vorliegt. ``DocflowService`` ruft sie im Kommando selbst auf — nicht der Endpunkt.
Damit gilt sie fuer jeden Zugang: Maske, REST, Skript, MCP.

* Die Regel steht in ``app/core/freigabe.py``.
* Eine Freigabe ist an Mandant, Beleg, Belegversion, Aktion, Betrag und Ablaufzeit gebunden. Ihr Abdruck umfasst
  Belegart, Partner, Summen und jede Position; aendert sich davon etwas, ist sie ungueltig.
* Funktionstrennung: Wer den Beleg angelegt oder die Freigabe angefragt hat, entscheidet nicht — auch nicht als
  Administrator. Ein technisches Konto entscheidet nie.
* Eine erteilte Freigabe wird beim Ausfuehren verbraucht, in derselben Transaktion wie die Buchung.
* Jede Anfrage, Entscheidung und Pruefung steht im unveraenderlichen Kommandoprotokoll des Belegs.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.beleg_roles import darf, rollen_von
from app.core.belegvertrag import BELEGARTEN
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.freigabe import AKTIONEN, GRUPPE, GUELTIGKEIT_STUNDEN, Anforderung, anforderung, wirksame_grenze

SUBJEKT = "docflow_document"
_ENDE = ("reversed", "cancelled")


def _d(wert: Any) -> Decimal:
    return Decimal(str(wert or 0))


class DocflowFreigabe:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Lesen ─────────────────────────────────────────────────────────────────

    def _header(self, doc_id: str) -> dict[str, Any]:
        zeile = self.db.execute(
            text("SELECT * FROM domain_docflow.document_headers WHERE tenant_id = :t AND id = :id AND deleted_at IS NULL"),
            {"t": self.tenant_id, "id": doc_id},
        ).mappings().first()
        if not zeile:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        return dict(zeile)

    def _items(self, doc_id: str) -> list[dict[str, Any]]:
        return [dict(z) for z in self.db.execute(
            text("SELECT * FROM domain_docflow.document_items WHERE tenant_id = :t AND header_id = :id ORDER BY line_number"),
            {"t": self.tenant_id, "id": doc_id},
        ).mappings().all()]

    def grenze(self, belegart: str) -> Optional[Decimal]:
        gruppe = GRUPPE.get(belegart)
        if gruppe is None:
            return None
        roh = self.db.execute(
            text("SELECT property_value FROM domain_shared.system_properties WHERE tenant_id = :t AND property_key = :k"),
            {"t": self.tenant_id, "k": f"freigabe.grenze.{gruppe}"},
        ).scalar()
        try:
            eigener = Decimal(str(roh)) if roh not in (None, "") else None
        except InvalidOperation:
            eigener = None  # Ein unlesbarer Wert lockert nichts: Es gilt die Systemvorgabe.
        return wirksame_grenze(gruppe, eigener)

    def abdruck(self, header: dict[str, Any], aktion: str) -> str:
        """Alles Freigaberelevante des Belegs. Druck- und Exportvermerke gehoeren nicht dazu."""
        inhalt = {
            "beleg": str(header["id"]), "art": header["doc_type"], "aktion": aktion,
            "kunde": header.get("customer_id"), "lieferant": header.get("supplier_id"),
            "waehrung": header.get("currency"),
            "summen": [str(_d(header.get(k))) for k in ("total_net", "total_tax", "total_gross")],
            "positionen": [
                [i.get("line_number"), i.get("article_number"), str(_d(i.get("quantity"))), str(_d(i.get("unit_price"))),
                 str(_d(i.get("discount_percent"))), i.get("tax_code"), str(_d(i.get("tax_rate"))), i.get("expense_account"),
                 str(_d(i.get("line_total_gross")))]
                for i in self._items(str(header["id"]))
            ],
        }
        return hashlib.sha256(json.dumps(inhalt, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    def _abgleich(self, doc_id: str) -> tuple[bool, str]:
        """Rechnungsabgleich der Eingangsrechnung gegen ihren Vorgaenger (Bestellung oder Wareneingang).

        In Ordnung ist: Jede Position stammt aus einer Position des Vorgaengers, mit dessen Preis und hoechstens
        dessen Menge. Eine frei erfasste Eingangsrechnung hat nichts, wogegen sie abgeglichen werden koennte.
        """
        zeilen = self.db.execute(
            text(
                """
                SELECT i.line_number, i.quantity, i.unit_price, q.quantity AS q_menge, q.unit_price AS q_preis
                FROM domain_docflow.document_items i
                LEFT JOIN domain_docflow.document_links l
                  ON l.tenant_id = i.tenant_id AND l.to_item_id = i.id AND l.to_header_id = i.header_id
                LEFT JOIN domain_docflow.document_items q ON q.tenant_id = i.tenant_id AND q.id = l.from_item_id
                WHERE i.tenant_id = :t AND i.header_id = :id ORDER BY i.line_number
                """
            ),
            {"t": self.tenant_id, "id": doc_id},
        ).fetchall()
        if not zeilen:
            return False, "keine Positionen"
        for nr, menge, preis, q_menge, q_preis in zeilen:
            if q_menge is None:
                return False, f"Position {nr} ohne Bestellung oder Wareneingang"
            if _d(preis) != _d(q_preis):
                return False, f"Position {nr}: Preis {_d(preis)} weicht von {_d(q_preis)} ab"
            if _d(menge) > _d(q_menge):
                return False, f"Position {nr}: Menge {_d(menge)} über {_d(q_menge)}"
        return True, ""

    def _brutto_des_vorgangs(self, header: dict[str, Any]) -> Decimal:
        """Summe der aktiven Belege derselben Art aus demselben Vorgaenger — sonst desselben Partners am selben Tag."""
        parameter = {"t": self.tenant_id, "id": header["id"], "art": header["doc_type"]}
        geschwister = self.db.execute(
            text(
                """
                SELECT COALESCE(SUM(b.total_gross), 0), COUNT(*) FROM domain_docflow.document_headers b
                WHERE b.tenant_id = :t AND b.doc_type = :art AND b.deleted_at IS NULL
                  AND b.status NOT IN ('reversed', 'cancelled')
                  AND b.id IN (
                    SELECT k2.to_header_id FROM domain_docflow.document_header_links k1
                    JOIN domain_docflow.document_header_links k2
                      ON k2.tenant_id = k1.tenant_id AND k2.from_header_id = k1.from_header_id
                    WHERE k1.tenant_id = :t AND k1.to_header_id = :id)
                """
            ),
            parameter,
        ).one()
        if geschwister[1]:
            return _d(geschwister[0])
        partner = header.get("supplier_id") or header.get("customer_id")
        if not partner:
            return _d(header.get("total_gross"))
        return _d(self.db.execute(
            text(
                """
                SELECT COALESCE(SUM(total_gross), 0) FROM domain_docflow.document_headers
                WHERE tenant_id = :t AND doc_type = :art AND deleted_at IS NULL AND status NOT IN ('reversed', 'cancelled')
                  AND COALESCE(supplier_id, customer_id) = :p AND document_date::date = CAST(:tag AS date)
                """
            ),
            {**parameter, "p": partner, "tag": header["document_date"]},
        ).scalar())

    def anforderung_fuer(self, header: dict[str, Any], aktion: str) -> Anforderung:
        belegart = str(header["doc_type"])
        if belegart not in BELEGARTEN or aktion not in AKTIONEN:
            return anforderung(belegart, aktion, brutto=Decimal("0"), gebucht=False)
        abgleich, hinweis = (True, "")
        if aktion == "post" and belegart == "purchase_invoice":
            abgleich, hinweis = self._abgleich(str(header["id"]))
        return anforderung(
            belegart, aktion,
            brutto=_d(header.get("total_gross")),
            gebucht=str(header.get("status")) == "posted",
            grenze=self.grenze(belegart),
            abgleich_in_ordnung=abgleich, abgleich_hinweis=hinweis,
            brutto_des_vorgangs=self._brutto_des_vorgangs(header) if aktion == "post" and belegart in GRUPPE else None,
        )

    def liste(self, doc_id: str) -> list[dict[str, Any]]:
        zeilen = self.db.execute(
            text(
                "SELECT id, action, risk, amount, status, reason, requested_by, requested_at, decided_by, decided_at, "
                "decision_note, expires_at, consumed_at, subject_version, fingerprint FROM domain_docflow.approvals "
                "WHERE tenant_id = :t AND subject_type = :s AND subject_id = :id ORDER BY requested_at, id"
            ),
            {"t": self.tenant_id, "s": SUBJEKT, "id": doc_id},
        ).mappings().all()
        return [dict(z) for z in zeilen]

    def gueltige(self, header: dict[str, Any], aktion: str) -> Optional[dict[str, Any]]:
        """Die erteilte, nicht abgelaufene Freigabe fuer genau diesen Inhalt — oder keine."""
        abdruck = self.abdruck(header, aktion)
        jetzt = datetime.now(timezone.utc)
        for f in reversed(self.liste(str(header["id"]))):
            if f["action"] == aktion and f["status"] == "granted" and f["fingerprint"] == abdruck and f["expires_at"] > jetzt:
                return f
        return None

    def offene(self, header: dict[str, Any], aktion: str) -> Optional[dict[str, Any]]:
        abdruck = self.abdruck(header, aktion)
        jetzt = datetime.now(timezone.utc)
        for f in reversed(self.liste(str(header["id"]))):
            if f["action"] == aktion and f["status"] == "requested" and f["fingerprint"] == abdruck and f["expires_at"] > jetzt:
                return f
        return None

    # ── Schreiben ─────────────────────────────────────────────────────────────

    def _protokoll(self, doc_id: str, kommando: str, akteur: Optional[str], daten: dict[str, Any]) -> None:
        self.db.execute(
            text(
                "INSERT INTO domain_docflow.document_command_log (tenant_id, header_id, command, actor, payload) "
                "VALUES (:t, :id, :c, :a, CAST(:p AS jsonb))"
            ),
            {"t": self.tenant_id, "id": doc_id, "c": kommando, "a": akteur, "p": json.dumps(daten, default=str)},
        )

    def beantrage(self, doc_id: str, aktion: str, antragsteller: str, grund: Optional[str] = None) -> dict[str, Any]:
        if aktion not in AKTIONEN:
            raise ValidationFailedError(f"Unbekannte Aktion: {aktion}")
        if not (antragsteller or "").strip():
            raise ValidationFailedError("Eine Freigabe braucht einen Antragsteller aus der Anmeldung.")
        header = self._header(doc_id)
        bedarf = self.anforderung_fuer(header, aktion)
        if not bedarf.zweitfreigabe:
            raise ValidationFailedError(f"Dieser Vorgang braucht keine Freigabe durch eine zweite Person. {bedarf.grund}")
        if str(header["status"]) in _ENDE:
            raise ValidationFailedError("Der Beleg ist storniert.")
        vorhanden = self.offene(header, aktion) or self.gueltige(header, aktion)
        if vorhanden:
            return {**vorhanden, "bereits_vorhanden": True}
        # Aeltere Anfragen und Freigaben zu einem anderen Inhalt gelten nicht mehr.
        self.db.execute(
            text(
                "UPDATE domain_docflow.approvals SET status = 'invalidated' WHERE tenant_id = :t AND subject_type = :s "
                "AND subject_id = :id AND action = :a AND status IN ('requested', 'granted')"
            ),
            {"t": self.tenant_id, "s": SUBJEKT, "id": doc_id, "a": aktion},
        )
        ablauf = datetime.now(timezone.utc) + timedelta(hours=GUELTIGKEIT_STUNDEN)
        neu = self.db.execute(
            text(
                "INSERT INTO domain_docflow.approvals (tenant_id, subject_type, subject_id, subject_version, action, amount, "
                "risk, fingerprint, reason, requested_by, expires_at) "
                "VALUES (:t, :s, :id, :v, :a, :betrag, :risk, :fp, :grund, :wer, :ablauf) RETURNING id"
            ),
            {"t": self.tenant_id, "s": SUBJEKT, "id": doc_id, "v": int(header.get("version") or 1), "a": aktion,
             "betrag": _d(header.get("total_gross")), "risk": bedarf.risiko, "fp": self.abdruck(header, aktion),
             "grund": grund, "wer": antragsteller, "ablauf": ablauf},
        ).scalar()
        self._protokoll(doc_id, "approval_request", antragsteller,
                        {"approval_id": neu, "action": aktion, "risk": bedarf.risiko, "why": bedarf.grund})
        self.db.commit()
        return next(f for f in self.liste(doc_id) if f["id"] == neu)

    def entscheide(self, doc_id: str, freigabe_id: str, entscheider: Any, erteilt: bool,
                   notiz: Optional[str] = None) -> dict[str, Any]:
        """Erteilen oder ablehnen. ``entscheider`` ist das Benutzerobjekt der geprueften Anmeldung."""
        wer = str((entscheider or {}).get("sub") or "").strip() if isinstance(entscheider, dict) else ""
        if not wer:
            raise ValidationFailedError("Eine Freigabe entscheidet nur eine angemeldete Person.")
        header = self._header(doc_id)
        freigabe = next((f for f in self.liste(doc_id) if f["id"] == freigabe_id), None)
        if freigabe is None:
            raise EntityNotFoundError("Approval", freigabe_id)

        def ablehnen(grund: str, fehler: type[Exception] = ConflictError) -> None:
            self._protokoll(doc_id, "approval_refused", wer, {"approval_id": freigabe_id, "why": grund})
            self.db.commit()
            raise fehler(grund)

        if freigabe["status"] != "requested":
            ablehnen(f"Die Anfrage ist nicht mehr offen ({freigabe['status']}).")
        if freigabe["expires_at"] <= datetime.now(timezone.utc):
            self.db.execute(text("UPDATE domain_docflow.approvals SET status = 'expired' WHERE id = :id"), {"id": freigabe_id})
            ablehnen("Die Anfrage ist abgelaufen.")
        if freigabe["fingerprint"] != self.abdruck(header, freigabe["action"]):
            self.db.execute(text("UPDATE domain_docflow.approvals SET status = 'invalidated' WHERE id = :id"), {"id": freigabe_id})
            ablehnen("Der Beleg wurde seit der Anfrage geändert; die Anfrage gilt nicht mehr.")
        # Funktionstrennung — vor dem Rollenrecht, damit sie auch fuer Administratoren gilt.
        if wer in {str(freigabe["requested_by"]), str(header.get("created_by") or "")}:
            ablehnen("Funktionstrennung: Wer den Beleg angelegt oder die Freigabe angefragt hat, entscheidet nicht.",
                     ValidationFailedError)
        if _technisches_konto(entscheider):
            ablehnen("Ein technisches Konto erteilt keine Freigabe.", ValidationFailedError)
        recht = "freigeben_erhoeht" if freigabe["risk"] == "R4" else "freigeben"
        if not darf(entscheider, recht, str(header["doc_type"])):
            ablehnen(f"Keine Berechtigung für diese Freigabe ({freigabe['risk']}).", ValidationFailedError)

        self.db.execute(
            text(
                "UPDATE domain_docflow.approvals SET status = :st, decided_by = :wer, decided_at = clock_timestamp(), "
                "decision_note = :notiz WHERE id = :id AND tenant_id = :t AND status = 'requested'"
            ),
            {"st": "granted" if erteilt else "denied", "wer": wer, "notiz": notiz, "id": freigabe_id, "t": self.tenant_id},
        )
        self._protokoll(doc_id, "approval_grant" if erteilt else "approval_deny", wer,
                        {"approval_id": freigabe_id, "action": freigabe["action"], "risk": freigabe["risk"],
                         "roles": sorted(rollen_von(entscheider))})
        self.db.commit()
        return next(f for f in self.liste(doc_id) if f["id"] == freigabe_id)

    def verlange(self, header: dict[str, Any], aktion: str, akteur: Optional[str]) -> Optional[str]:
        """Vor dem Ausfuehren: Braucht der Vorgang eine Zweitfreigabe, muss eine gueltige vorliegen.

        Verbraucht die Freigabe — ohne Commit, in der Transaktion des Kommandos. Scheitert das Kommando danach,
        bleibt die Freigabe erteilt.
        """
        bedarf = self.anforderung_fuer(header, aktion)
        if not bedarf.zweitfreigabe:
            return None
        doc_id = str(header["id"])
        freigabe = self.gueltige(header, aktion)
        if freigabe is None:
            raise ConflictError(f"Freigabe erforderlich ({bedarf.risiko}): {bedarf.grund}")
        self.db.execute(
            text("UPDATE domain_docflow.approvals SET status = 'consumed', consumed_at = clock_timestamp() WHERE id = :id"),
            {"id": freigabe["id"]},
        )
        self._protokoll(doc_id, "approval_consume", akteur,
                        {"approval_id": freigabe["id"], "action": aktion, "risk": bedarf.risiko,
                         "decided_by": freigabe["decided_by"]})
        return str(freigabe["id"])


def _technisches_konto(nutzer: Any) -> bool:
    """Dienstkonten des Anmeldeanbieters (Client-Credentials) sind keine zweite Person."""
    roh = nutzer.get("raw") if isinstance(nutzer, dict) else None
    name = str((roh or {}).get("preferred_username") or (nutzer.get("name") if isinstance(nutzer, dict) else "") or "")
    return name.startswith("service-account-") or bool((roh or {}).get("client_id") and not (roh or {}).get("preferred_username"))
