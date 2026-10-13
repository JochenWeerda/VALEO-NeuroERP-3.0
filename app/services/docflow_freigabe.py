"""DocFlow-Belege an der zentralen Approval Engine (APPROVAL-001).

``DocflowService`` ruft die Pruefung im Kommando selbst auf — nicht der Endpunkt. Damit gilt sie fuer jeden Zugang:
Maske, REST, Skript, MCP. Die Engine und ihre Regeln stehen in ``app/services/freigabe_engine.py``; hier steht nur,
was ein DocFlow-Beleg fuer sie ist: Betrag, Stand, Ersteller, freigaberelevanter Inhalt — und was an ihm auffaellt
(Abweichung vom Vorgaenger, Dublette, Gutschrift ohne Bezug, gehaeufte Stornos, Stueckelung).
"""
from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text

from app.core.belegvertrag import BELEGARTEN
from app.core.exceptions import EntityNotFoundError
from app.core.freigabe import AKTIONEN, GRUPPE, Anforderung, Befund, anforderung
from app.services.freigabe_engine import FreigabeEngine, Vorgang

SUBJEKT = "docflow_document"
_ENDE = ("reversed", "cancelled")


def _d(wert: Any) -> Decimal:
    return Decimal(str(wert or 0))


class DocflowFreigabe(FreigabeEngine):
    SUBJEKT = SUBJEKT

    # ── Der Beleg als Vorgang ─────────────────────────────────────────────────

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

    def vorgang(self, subject_id: str, aktion: str) -> Vorgang:
        return self._vorgang_aus(self._header(subject_id), aktion)

    def _vorgang_aus(self, header: dict[str, Any], aktion: str) -> Vorgang:
        doc_id, belegart, stand = str(header["id"]), str(header["doc_type"]), str(header.get("status") or "")
        return Vorgang(
            subject_id=doc_id, belegart=belegart, brutto=_d(header.get("total_gross")), gebucht=stand == "posted",
            beendet=stand in _ENDE, version=int(header.get("version") or 1), ersteller=header.get("created_by"),
            # Alles Freigaberelevante des Belegs. Druck- und Exportvermerke gehoeren nicht dazu.
            inhalt={
                "kunde": header.get("customer_id"), "lieferant": header.get("supplier_id"), "waehrung": header.get("currency"),
                "summen": [str(_d(header.get(k))) for k in ("total_net", "total_tax", "total_gross")],
                "positionen": [
                    [i.get("line_number"), i.get("article_number"), str(_d(i.get("quantity"))), str(_d(i.get("unit_price"))),
                     str(_d(i.get("discount_percent"))), i.get("tax_code"), str(_d(i.get("tax_rate"))),
                     i.get("expense_account"), str(_d(i.get("line_total_gross")))]
                    for i in self._items(doc_id)
                ],
            },
            befunde=self._befunde(header, aktion),
            brutto_des_vorgangs=self._brutto_des_vorgangs(header) if aktion == "post" and belegart in GRUPPE else None,
        )

    def _befunde(self, header: dict[str, Any], aktion: str) -> list[Befund]:
        """Was an diesem Beleg auffaellt (FIN-CONTROL-001). Betragsschwellen kommen aus der Regel dazu."""
        doc_id, art, stand = str(header["id"]), str(header["doc_type"]), str(header.get("status") or "")
        befunde: list[Befund] = []
        if aktion == "post" and art == "purchase_invoice":
            befunde += [Befund("abweichung_vorgaenger", "kritisch", f"Eingangsrechnung weicht von Bestellung bzw. "
                               f"Wareneingang ab: {a}.") for a in self._abweichungen(doc_id)[:1]]
            doppelt = self._dublette(header)
            if doppelt:
                befunde.append(Befund("dublette", "kritisch", f"Mögliche Dublette der Eingangsrechnung {doppelt}."))
        if aktion == "post" and art.endswith("_credit_memo") and not self._hat_vorgaenger(doc_id):
            grenze = self.grenze(art)
            if grenze is not None and _d(header.get("total_gross")) > grenze:
                befunde.append(Befund(
                    "gutschrift_ohne_bezug", "kritisch",
                    f"Gutschrift über {grenze} EUR ohne Bezugsrechnung (Forderungsverzicht ohne Beleg)."))
        if aktion == "reverse" and stand == "posted":
            weitere = self._stornos_des_partners(header)
            if weitere >= 2:
                befunde.append(Befund(
                    "storno_haeufung", "warnung",
                    f"Storno: bereits {weitere} stornierte Belege dieses Partners in den letzten 90 Tagen."))
        return befunde

    def _abweichungen(self, doc_id: str) -> list[str]:
        """Abweichungen der Eingangsrechnung von ihrem Vorgaenger (Bestellung oder Wareneingang).

        Eine frei erfasste Eingangsrechnung hat keinen Vorgaenger und damit keine Abweichung — sie ist Routine der
        Buchhaltung. Stammt die Rechnung aus einem Vorgaenger, faellt auf: ein anderer Preis, eine hoehere Menge,
        eine Position, die der Vorgaenger nicht kennt.
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
        if not any(z[3] is not None for z in zeilen):
            return []
        abweichungen = []
        for nr, menge, preis, q_menge, q_preis in zeilen:
            if q_menge is None:
                abweichungen.append(f"Position {nr} ohne Bestellung oder Wareneingang")
            elif _d(preis) != _d(q_preis):
                abweichungen.append(f"Position {nr}: Preis {_d(preis)} statt {_d(q_preis)}")
            elif _d(menge) > _d(q_menge):
                abweichungen.append(f"Position {nr}: Menge {_d(menge)} über {_d(q_menge)}")
        return abweichungen

    def _dublette(self, header: dict[str, Any]) -> Optional[str]:
        """Eine andere aktive Eingangsrechnung desselben Lieferanten mit derselben Fremdnummer oder demselben Betrag
        am selben Tag — unabhaengig vom Betrag ein Grund zu sperren."""
        if not header.get("supplier_id"):
            return None
        return self.db.execute(
            text(
                """
                SELECT doc_number FROM domain_docflow.document_headers
                WHERE tenant_id = :t AND doc_type = 'purchase_invoice' AND id <> :id AND supplier_id = :s
                  AND deleted_at IS NULL AND status NOT IN ('reversed', 'cancelled')
                  AND ((CAST(:ref AS text) IS NOT NULL AND source_ref = :ref)
                       OR (total_gross = :brutto AND total_gross > 0 AND document_date::date = CAST(:tag AS date)))
                ORDER BY created_at LIMIT 1
                """
            ),
            {"t": self.tenant_id, "id": header["id"], "s": header["supplier_id"], "ref": header.get("source_ref") or None,
             "brutto": _d(header.get("total_gross")), "tag": header["document_date"]},
        ).scalar()

    def _hat_vorgaenger(self, doc_id: str) -> bool:
        return bool(self.db.execute(
            text("SELECT 1 FROM domain_docflow.document_header_links WHERE tenant_id = :t AND to_header_id = :id LIMIT 1"),
            {"t": self.tenant_id, "id": doc_id},
        ).first())

    def _stornos_des_partners(self, header: dict[str, Any]) -> int:
        partner = header.get("supplier_id") or header.get("customer_id")
        if not partner:
            return 0
        return int(self.db.execute(
            text(
                """
                SELECT count(*) FROM domain_docflow.document_headers
                WHERE tenant_id = :t AND id <> :id AND status = 'reversed' AND deleted_at IS NULL
                  AND COALESCE(supplier_id, customer_id) = :p AND updated_at > now() - interval '90 days'
                """
            ),
            {"t": self.tenant_id, "id": header["id"], "p": partner},
        ).scalar() or 0)

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

    def protokolliere_am_vorgang(self, subject_id: str, kommando: str, akteur: Optional[str], daten: dict[str, Any]) -> None:
        """Die Freigabe steht auch im Kommandoprotokoll des Belegs: Seine Historie ist damit vollstaendig."""
        self.db.execute(
            text(
                "INSERT INTO domain_docflow.document_command_log (tenant_id, header_id, command, actor, payload) "
                "VALUES (:t, :id, :c, :a, CAST(:p AS jsonb))"
            ),
            {"t": self.tenant_id, "id": subject_id, "c": kommando, "a": akteur, "p": json.dumps(daten, default=str)},
        )

    # ── Mit dem Belegkopf, wie DocFlow ihn in der Hand hat ────────────────────

    def anforderung_fuer(self, header: dict[str, Any], aktion: str) -> Anforderung:
        if str(header["doc_type"]) not in BELEGARTEN or aktion not in AKTIONEN:
            return anforderung(str(header["doc_type"]), aktion, brutto=Decimal("0"), gebucht=False)
        return self.anforderung(self._vorgang_aus(header, aktion), aktion)

    def gueltige(self, header: dict[str, Any], aktion: str) -> Optional[dict[str, Any]]:
        return self.gueltige_fuer(self._vorgang_aus(header, aktion), aktion)

    def offene(self, header: dict[str, Any], aktion: str) -> Optional[dict[str, Any]]:
        return self.offene_fuer(self._vorgang_aus(header, aktion), aktion)

    def verlange(self, header: dict[str, Any], aktion: str, akteur: Optional[str]) -> Optional[str]:
        if str(header["doc_type"]) not in BELEGARTEN:
            return None  # Kassenbelege: bis auf Weiteres nicht erfasst (Entscheidung vom 13.10.2026, vor MCP-Schreibfreigabe zu schliessen)
        return self.verlange_fuer(self._vorgang_aus(header, aktion), aktion, akteur)
