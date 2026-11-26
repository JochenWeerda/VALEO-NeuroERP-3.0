"""Spiegelbetrieb L3 -> VALEO: Abgleich der offenen Posten (M6, 25.11.2026) - liest nur, bucht nie.

Quelle: L3 ``FIBU_OP1`` (offene Posten je Konto), als Objektart ``offener_posten`` ueber die Adapterstrecke angenommen
und freigegeben (Profil ``l3_spiegel``). Kanonische Felder: ``konto`` (L3-Debitoren-/Kreditorennummer),
``rechnungsnr``, ``offener_betrag``. Die Bedeutung der L3-Spalten (u. a. ob ``OFFEN`` Betrag oder Kennzeichen ist)
wird am echten Abzug bestaetigt und im Profil-Mapping festgelegt, nicht hier.

Zuordnung: Seit dem Nutzerentscheid vom 25.11.2026 ist die L3-Kontonummer das Konto des Geschaeftspartners
(``business_partners.debtor_account``/``creditor_account``). VALEO-Posten kommen aus ``domain_erp.offene_posten``
(fuehrend fuer den offenen Betrag ist ``offen``; offen = ``op_status`` offen/teilweise und ``offen`` > 0, wie
``app/finance/op_saldo.py``).

Ergebnis je L3-Posten im Spiegelprotokoll: ``unveraendert`` (Betrag gleich), ``geaendert`` (Betrag weicht ab,
Felddifferenz ``offen``), ``fehler`` (Konto unbekannt oder Posten fehlt in VALEO). Dazu im Bericht die VALEO-Posten
auf zugeordneten Konten, die L3 nicht mehr offen fuehrt (``fehlt_in_l3``), und Summen je Konto. Warum keine
Uebernahme: Anfangs-OPs gehoeren zum Saldenvortrag unter der Buchungsautoritaet von Finance.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.spiegel_abgleich_basis import abschliessen, freigegebene_zeilen, neuer_zaehler, protokolliere

OBJEKTART = "offener_posten"
KONTOARTEN = {"debtor_account": "debitoren", "creditor_account": "kreditoren"}


def _betrag(roh: Any) -> Decimal:
    wert = str(roh or "").strip()
    if "," in wert and "." not in wert:
        wert = wert.replace(",", ".")
    try:
        return Decimal(wert).quantize(Decimal("0.01"))
    except InvalidOperation as fehler:
        raise ValueError(f"Betrag {roh!r} ist keine Zahl") from fehler


def _partner_fuer_konto(db: Session, tenant_id: str, konto: str) -> tuple[str, str] | None:
    """(partner_id, konto_typ) des Partners mit diesem Debitoren- oder Kreditorenkonto."""
    for spalte, konto_typ in KONTOARTEN.items():
        partner = db.execute(text(
            f"SELECT partner_id FROM domain_crm.business_partners WHERE tenant_id = :t AND {spalte} = :k"),  # nosec B608 - Spalte aus KONTOARTEN
            {"t": tenant_id, "k": konto}).scalar()
        if partner:
            return str(partner), konto_typ
    return None


def _valeo_posten(db: Session, tenant_id: str, partner_id: str, konto_typ: str) -> dict[str, Decimal]:
    zeilen = db.execute(text(
        "SELECT COALESCE(rechnungsnr, document_number) AS nr, SUM(offen) AS offen FROM domain_erp.offene_posten "
        "WHERE tenant_id = :t AND partner_id = :p AND konto_typ = :k AND op_status IN ('offen', 'teilweise') "
        "AND offen > 0 GROUP BY 1"), {"t": tenant_id, "p": partner_id, "k": konto_typ}).mappings().all()
    return {str(z["nr"]): Decimal(str(z["offen"])).quantize(Decimal("0.01")) for z in zeilen}


def abgleichen(db: Session, tenant_id: str, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
    """Gleicht die offenen L3-Posten eines freigegebenen Batches mit VALEO ab. Schreibt nur das Spiegelprotokoll."""
    profil, zeilen = freigegebene_zeilen(db, tenant_id, batch_id, OBJEKTART)
    zaehler = neuer_zaehler()
    konten: dict[str, dict[str, Any]] = {}
    gesehen: dict[tuple[str, str], set[str]] = {}
    for z in zeilen:
        p = dict(z["canonical_payload"] or {})
        konto = str(p.get("konto") or "").strip()
        nr = str(p.get("rechnungsnr") or "").strip()
        ergebnis, differenzen, fehler = "unveraendert", {}, None
        try:
            l3 = _betrag(p.get("offener_betrag"))
            zuordnung = _partner_fuer_konto(db, tenant_id, konto) if konto else None
            if zuordnung is None:
                raise ValueError(f"Konto {konto or '-'} ist keinem Geschaeftspartner zugeordnet")
            partner, konto_typ = zuordnung
            if (partner, konto_typ) not in gesehen:
                gesehen[(partner, konto_typ)] = set()
                konten[konto] = {"konto_typ": konto_typ, "l3": Decimal("0"),
                                 "valeo": sum(_valeo_posten(db, tenant_id, partner, konto_typ).values(), Decimal("0")),
                                 "partner": partner}
            konten[konto]["l3"] += l3
            gesehen[(partner, konto_typ)].add(nr)
            valeo = _valeo_posten(db, tenant_id, partner, konto_typ).get(nr)
            if valeo is None:
                raise ValueError(f"Posten {nr} auf Konto {konto} fehlt in VALEO (L3 offen {l3})")
            if valeo != l3:
                ergebnis, differenzen = "geaendert", {"offen": {"valeo": str(valeo), "l3": str(l3)}}
        except ValueError as exc:
            ergebnis, fehler = "fehler", str(exc)
        zaehler[ergebnis] += 1
        protokolliere(db, tenant_id, batch_id, z, OBJEKTART, ergebnis, differenzen, fehler)

    fehlt_in_l3 = []
    for (partner, konto_typ), nummern in gesehen.items():
        konto = next(k for k, v in konten.items() if v["partner"] == partner and v["konto_typ"] == konto_typ)
        for nr, offen in sorted(_valeo_posten(db, tenant_id, partner, konto_typ).items()):
            if nr not in nummern:
                fehlt_in_l3.append({"konto": konto, "rechnungsnr": nr, "valeo_offen": str(offen)})
    salden = {k: {"konto_typ": v["konto_typ"], "l3": str(v["l3"]), "valeo": str(v["valeo"]),
                  "differenz": str(v["valeo"] - v["l3"])} for k, v in sorted(konten.items())}
    abschliessen(db, tenant_id, batch_id, profil, "mirror_op_reconciled", actor, reason,
                 {**zaehler, "fehlt_in_l3": len(fehlt_in_l3)})
    return {"batch_id": batch_id, **zaehler, "fehlt_in_l3": fehlt_in_l3, "salden": salden,
            "abweichungsfrei": zaehler["geaendert"] == 0 and zaehler["fehler"] == 0 and not fehlt_in_l3}
