"""E-Rechnung (XRechnung 3.0, UBL 2.1) aus dem DocFlow-Beleg (BELEG-052 Phase 2, 10.11.2026).

Die XRechnung-Wege lasen nur den alten Rechnungsspeicher; Rechnungen entstehen seit der Belegmaske in DocFlow - fuer
sie gab es keine E-Rechnung (B2B-Pflicht, § 14 UStG). Hier: aus dem Belegvertrag (Partner, Positionen, Steuer je
Schluessel, Summen, Zahlungsbaustein) in den vorhandenen Generator (``einvoice_generator``), das XML als fuehrendes
Original ins GoBD-Archiv (``document_artifacts``) - vor jeder Auslieferung, eine Wiederholung legt kein zweites an.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.belegvertrag import Beleg
from app.core.exceptions import ValidationFailedError

E_RECHNUNG_ARTEN = {"sales_invoice": "380", "sales_credit_memo": "381"}

# Einheiten nach UN/ECE Recommendation 20 (Pflicht in der XRechnung). Unbekanntes wird nicht geraten.
_EINHEIT_CODE = {"dt": "DTN", "kg": "KGM", "t": "TNE", "g": "GRM", "l": "LTR", "m3": "MTQ", "m": "MTR",
                 "stk": "C62", "st": "C62", "stueck": "C62", "h": "HUR", "ha": "HAR", "pal": "PF", "sack": "SA"}


def einheit_code(einheit: Optional[str]) -> str:
    from app.core.agrar_units import normalisiere

    schluessel = normalisiere(einheit or "").lower() if einheit else ""
    code = _EINHEIT_CODE.get(schluessel)
    if not code:
        raise ValidationFailedError(f"Einheit {einheit!r} hat keinen UN/ECE-Code fuer die E-Rechnung.")
    return code


def _verkaeufer(db: Session, tenant_id: str) -> dict[str, Any]:
    zeile = db.execute(text("SELECT name, settings FROM domain_shared.tenants WHERE id = :t"), {"t": tenant_id}).first()
    einstellungen = (zeile[1] if zeile else None) or {}
    adresse = einstellungen.get("anschrift") or einstellungen.get("standort") or {}
    return {"name": (zeile[0] if zeile else None) or tenant_id, "street": adresse.get("strasse", ""),
            "postal_code": adresse.get("plz", ""), "city": adresse.get("ort", ""), "country_code": "DE",
            "vat_id": einstellungen.get("ust_id", ""), "email": einstellungen.get("email", "")}


def _steuerart(db: Session, tenant_id: str, schluessel: Optional[str], satz: Decimal) -> str:
    if schluessel:
        zeile = db.execute(text("SELECT reverse_charge, steuersatz FROM domain_erp.tax_keys "
                                "WHERE tenant_id = :t AND code = :c LIMIT 1"), {"t": tenant_id, "c": schluessel}).first()
        if zeile and zeile[0]:
            return "AE"  # Steuerschuldnerschaft des Leistungsempfaengers
    return "S" if satz > 0 else "E"


def xrechnung_eingabe(db: Session, tenant_id: str, beleg: Beleg) -> dict[str, Any]:
    if beleg.belegart not in E_RECHNUNG_ARTEN:
        raise ValidationFailedError(f"Fuer {beleg.belegart} gibt es keine E-Rechnung.")
    if beleg.status != "posted":
        raise ValidationFailedError("E-Rechnung nur fuer einen gebuchten Beleg.")
    from app.services.business_partner_service import BusinessPartnerService

    kennung = db.execute(text("SELECT customer_id FROM domain_docflow.document_headers WHERE id = :id AND tenant_id = :t"),
                         {"id": beleg.beleg_id, "t": tenant_id}).scalar()
    if not kennung:
        raise ValidationFailedError("E-Rechnung ohne Kunde nicht moeglich.")
    kunde = BusinessPartnerService(db, tenant_id).get_customer_party(str(kennung))
    zahlung = beleg.bausteine.get("zahlung") or {}
    zeilen = [{
        "line_id": str(p.pos_nr), "article": p.artikel_nr, "description": p.bezeichnung or p.artikel_nr,
        "quantity": float(p.menge), "unit_code": einheit_code(p.einheit),
        "unit_price_net": float(p.einzelpreis or 0), "line_net_amount": float(p.netto or 0),
        "vat_rate_percent": float(p.steuersatz or 0),
        "vat_category_code": _steuerart(db, tenant_id, p.steuerschluessel, Decimal(str(p.steuersatz or 0))),
    } for p in beleg.positionen]
    summen = beleg.summen
    return {
        "invoice_number": beleg.beleg_nr, "invoice_date": beleg.belegdatum.isoformat(),
        "invoice_type_code": E_RECHNUNG_ARTEN[beleg.belegart], "currency": beleg.waehrung,
        "buyer_reference": (beleg.bausteine.get("referenzen") or {}).get("fremde_referenz") or beleg.beleg_nr,
        "payment_due_date": zahlung.get("faellig_am", ""), "payment_terms_text": zahlung.get("zahlungsbedingung", ""),
        "supplier": _verkaeufer(db, tenant_id), "customer": kunde, "lines": zeilen,
        "total_net": float(summen.netto if summen else 0), "total_vat": float(summen.steuer if summen else 0),
        "total_gross": float(summen.brutto if summen else 0),
    }


def archivierte_xrechnung(db: Session, tenant_id: str, beleg_id: str) -> Optional[tuple[str, bytes]]:
    zeile = db.execute(text("""
        SELECT file_name, content_bytes FROM domain_docflow.document_artifacts
        WHERE tenant_id = :t AND header_id = :h AND artifact_type = 'xml' AND content_bytes IS NOT NULL
        ORDER BY version DESC LIMIT 1
    """), {"t": tenant_id, "h": beleg_id}).first()
    return (str(zeile[0]), bytes(zeile[1])) if zeile else None


def erzeuge_und_archiviere(db: Session, tenant_id: str, beleg: Beleg, akteur: Optional[str]) -> tuple[str, bool]:
    """XRechnung bauen und archivieren. Gibt (Dateiname, neu) zurueck; gleicher Inhalt wird nicht doppelt archiviert."""
    from app.core.gobd_artifact import register_artifact, sha256_hex
    from app.services.einvoice_generator import build_xrechnung_xml

    xml = build_xrechnung_xml(xrechnung_eingabe(db, tenant_id, beleg)).encode("utf-8")
    hash_ = sha256_hex(xml)
    dateiname = f"XRechnung_{beleg.beleg_nr}.xml".replace("/", "-")
    schon = db.execute(text(
        "SELECT 1 FROM domain_docflow.document_artifacts WHERE tenant_id = :t AND header_id = :h "
        "AND artifact_type = 'xml' AND content_hash_sha256 = :x"), {"t": tenant_id, "h": beleg.beleg_id, "x": hash_}).first()
    if schon:
        return dateiname, False
    register_artifact(db=db, tenant_id=tenant_id, doc_number=beleg.beleg_nr, artifact_type="xml",
                      content_hash_sha256=hash_, storage_key=f"einvoice/xrechnung/{beleg.beleg_nr}",
                      file_name=dateiname, created_by=akteur, doc_type=beleg.belegart, content=xml)
    return dateiname, True
