#!/usr/bin/env python3
"""Testfabrik: Eingang im E-Rechnungs-Postfach (public.finance_erechnungen) zu einer Bestellnummer.

Bis 17.11.2026 legte dieses Skript Demo-Bestellungen und -Wareneingaenge in den alten Belegspeichern an. Die gibt es
seit BELEG-052 S5 nicht mehr; Bestellung und Wareneingang entstehen per DocFlow-Kommando
(``tests/procurement_identity_fixture.py``). Geblieben ist der Postfach-Eingang, den der 3-Wege-Abgleich zaehlt,
wenn es keine DocFlow-Eingangsrechnung gibt. Der Steuerbetrag ist eine feste Testannahme, keine Steuerlogik.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import text

TENANT = "00000000-0000-0000-0000-000000000001"


def _invoice(db, po_number: str, rechnungsnummer: str, netto: float) -> None:
    exists = db.execute(
        text("SELECT 1 FROM public.finance_erechnungen WHERE rechnungsnummer = :nr AND tenant_id = :t"),
        {"nr": rechnungsnummer, "t": TENANT},
    ).first()
    if exists:
        return
    mwst = round(netto * 0.19, 2)
    db.execute(
        text(
            "INSERT INTO public.finance_erechnungen "
            "(id, tenant_id, rechnungsnummer, rechnungsdatum, faelligkeitsdatum, "
            "lieferant_name, rechnungssteller_name, gesamt_netto, gesamt_mwst, gesamt_brutto, "
            "zugeordneter_auftrag, status, created_at) "
            "VALUES (:id, :t, :nr, :rd, :fd, :ln, :rn, :netto, :mwst, :brutto, :po, 'ERSTELLT', NOW())"
        ),
        {
            "id": str(uuid.uuid4()),
            "t": TENANT,
            "nr": rechnungsnummer,
            "rd": date.today(),
            "fd": date.today(),
            "ln": "Demo Agrar-Lieferant GmbH",
            "rn": "VALEO Demo GmbH",
            "netto": netto,
            "mwst": mwst,
            "brutto": round(netto + mwst, 2),
            "po": po_number,
        },
    )
