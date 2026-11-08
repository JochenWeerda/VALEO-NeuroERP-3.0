"""Umsatzsteuer-Voranmeldung aus dem Hauptbuch: die eine Berechnung fuer Vorberechnung, Anmeldung und Statusanzeige.

Quelle der Steuerlogik ist ``domain_erp.tax_keys`` (siehe ``app/finance/steuerschluessel.py``). Ein Steuerschluessel
nennt die Konten, auf die gebucht wird — Erloeskonto (``revenue_account``), Umsatzsteuerkonto (``credit_account``),
Vorsteuerkonto (``debit_account``) — und die Kennzahl der Voranmeldung (``ustva_position``). Die Voranmeldung liest
deshalb die gebuchten Salden genau dieser Konten:

* Bemessungsgrundlage einer Kennzahl = Haben minus Soll auf den Erloeskonten ihrer Schluessel,
* Umsatzsteuer = Haben minus Soll auf den Umsatzsteuerkonten,
* Vorsteuer = Soll minus Haben auf den Vorsteuerkonten.

Bis 27.10.2026 erkannten zwei Berechnungen Erloes- und Aufwandskonten am ersten Zeichen der **Konto-UUID**, rechneten
pauschal mit 19 % und filterten auf ``journal_entry_lines.tax_code`` — eine Spalte, die keine Buchung schreibt. Sie
lieferten immer null und meldeten Fehler ebenfalls als null.

Nichts wird angenommen: Was sich nicht eindeutig einer Kennzahl zuordnen laesst, ist eine **Klaerung**. Eine Anmeldung
mit offenen Klaerungen wird nicht angelegt.
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

CENT = Decimal("0.01")
NULL = Decimal("0")

_MONAT = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")
_QUARTAL = re.compile(r"^(\d{4})-Q([1-4])$")

#: Bezeichnungen der gaengigen Kennzahlen (Formular UStVA); ein Schluessel kann eine eigene Bezeichnung tragen.
KENNZAHLEN = {
    "81": "Steuerpflichtige Umsätze 19 %",
    "86": "Steuerpflichtige Umsätze 7 %",
    "35": "Umsätze zu anderen Steuersätzen",
    "41": "Innergemeinschaftliche Lieferungen an Abnehmer mit USt-IdNr.",
    "43": "Weitere steuerfreie Umsätze mit Vorsteuerabzug",
    "48": "Steuerfreie Umsätze ohne Vorsteuerabzug",
    "66": "Vorsteuerbeträge aus Rechnungen von anderen Unternehmern",
}


class Kennzahl(BaseModel):
    kennzahl: str
    bezeichnung: str
    seite: str  # "umsatz" oder "vorsteuer"
    steuersatz: Optional[Decimal] = None
    bemessungsgrundlage: Optional[Decimal] = None
    steuer: Decimal = NULL
    steuerschluessel: list[str]


class UStVAStand(BaseModel):
    zeitraum: str
    perioden: list[str]
    kennzahlen: list[Kennzahl]
    umsatz_netto: Decimal
    umsatzsteuer: Decimal
    vorsteuer: Decimal
    zahllast: Decimal  # Kennzahl 83: positiv Zahlung, negativ Erstattung
    klaerungen: list[str]
    gebuchte_buchungen: int
    offene_entwuerfe: int


def perioden(zeitraum: str) -> list[str]:
    """``YYYY-MM`` oder ``YYYY-Q1``..``Q4`` -> Buchungsperioden. Alles andere ist ein Eingabefehler."""
    zeitraum = (zeitraum or "").strip()
    if _MONAT.match(zeitraum):
        return [zeitraum]
    if m := _QUARTAL.match(zeitraum):
        jahr, quartal = m.group(1), int(m.group(2))
        return [f"{jahr}-{monat:02d}" for monat in range(3 * quartal - 2, 3 * quartal + 1)]
    raise ValueError(f"Zeitraum {zeitraum!r}: erwartet YYYY-MM oder YYYY-Q1 bis YYYY-Q4.")


def abgabefrist(zeitraum: str) -> date:
    """10. Tag nach Ablauf des Zeitraums (§ 18 Abs. 1 UStG), am Wochenende der naechste Werktag (§ 108 Abs. 3 AO).

    Ohne Dauerfristverlaengerung und ohne Feiertage (die sind landesabhaengig).
    """
    letzte = perioden(zeitraum)[-1]
    jahr, monat = int(letzte[:4]), int(letzte[5:])
    frist = date(jahr + (monat == 12), monat % 12 + 1, 10)
    while frist.weekday() >= 5:
        frist += timedelta(days=1)
    return frist


def _konto(wert: Any) -> Optional[str]:
    return str(wert).strip() if wert is not None and str(wert).strip() else None


def berechne(db: Session, tenant_id: str, zeitraum: str) -> UStVAStand:
    """Voranmeldung des Zeitraums aus den gebuchten Salden der Steuerschluessel-Konten."""
    ps = perioden(zeitraum)
    schluessel = db.execute(
        text(
            """
            SELECT code, steuersatz, ustva_position, ustva_bezeichnung,
                   credit_account, debit_account, revenue_account, reverse_charge
            FROM domain_erp.tax_keys
            WHERE tenant_id = :tid AND active
            ORDER BY code
            """
        ),
        {"tid": tenant_id},
    ).mappings().all()
    salden: dict[str, tuple[Decimal, Decimal]] = {
        str(r["konto"]): (Decimal(str(r["soll"] or 0)), Decimal(str(r["haben"] or 0)))
        for r in db.execute(
            text(
                """
                SELECT coa.account_number AS konto, SUM(jel.debit) AS soll, SUM(jel.credit) AS haben
                FROM domain_erp.journal_entry_lines jel
                JOIN domain_erp.journal_entries je ON je.id = jel.journal_entry_id
                JOIN domain_erp.chart_of_accounts coa ON coa.id = jel.account_id
                WHERE je.tenant_id = :tid AND je.status = 'posted' AND je.period = ANY(:ps)
                GROUP BY coa.account_number
                """
            ),
            {"tid": tenant_id, "ps": ps},
        ).mappings()
    }
    stand = db.execute(
        text(
            """
            SELECT COUNT(*) FILTER (WHERE status = 'posted') AS gebucht,
                   COUNT(*) FILTER (WHERE status = 'draft')  AS entwurf
            FROM domain_erp.journal_entries
            WHERE tenant_id = :tid AND period = ANY(:ps)
            """
        ),
        {"tid": tenant_id, "ps": ps},
    ).mappings().one()

    def bewegt(konto: Optional[str]) -> bool:
        return konto is not None and salden.get(konto, (NULL, NULL)) != (NULL, NULL)

    def haben_saldo(konto: Optional[str]) -> Decimal:
        soll, haben = salden.get(konto or "", (NULL, NULL))
        return haben - soll

    klaerungen: list[str] = []
    #: Konto -> (Rolle, Kennzahl, Satz, Schluessel); ein Konto darf nur einer Kennzahl gehoeren.
    konten: dict[str, list[tuple[str, str, Decimal, str]]] = {}
    for s in schluessel:
        code = str(s["code"])
        satz = Decimal(str(s["steuersatz"]))
        kz = _konto(s["ustva_position"])
        ust, vst, erl = _konto(s["credit_account"]), _konto(s["debit_account"]), _konto(s["revenue_account"])
        konten_des_schluessels = [k for k in (ust, vst, erl) if k]
        if not any(bewegt(k) for k in konten_des_schluessels):
            continue  # im Zeitraum nicht bebucht: fuer diese Anmeldung ohne Bedeutung
        if s["reverse_charge"] or (vst and (ust or erl)):
            klaerungen.append(
                f"Steuerschlüssel {code} bucht Umsatzsteuer und Vorsteuer (z. B. § 13b UStG); "
                "diese Kennzahlen werden nicht automatisch angemeldet."
            )
            continue
        if kz is None:
            klaerungen.append(f"Steuerschlüssel {code} hat Buchungen im Zeitraum, aber keine UStVA-Kennzahl.")
            continue
        for konto, rolle in ((erl, "erloes"), (ust, "steuer"), (vst, "vorsteuer")):
            if konto:
                konten.setdefault(konto, []).append((rolle, kz, satz, code))

    kennzahlen: dict[str, Kennzahl] = {}
    for konto, nutzungen in sorted(konten.items()):
        if len({(rolle, kz, satz) for rolle, kz, satz, _ in nutzungen}) > 1:
            klaerungen.append(
                f"Konto {konto} gehört zu Steuerschlüsseln {', '.join(sorted({c for *_, c in nutzungen}))} "
                "mit verschiedenen Kennzahlen oder Sätzen; die Buchungen lassen sich nicht zuordnen."
            )
            continue
        rolle, kz, satz, _ = nutzungen[0]
        eintrag = kennzahlen.setdefault(kz, Kennzahl(
            kennzahl=kz, bezeichnung=KENNZAHLEN.get(kz, f"Kennzahl {kz}"),
            seite="vorsteuer" if rolle == "vorsteuer" else "umsatz",
            steuersatz=None if rolle == "vorsteuer" else satz,
            bemessungsgrundlage=None if rolle == "vorsteuer" else NULL,
            steuerschluessel=[],
        ))
        if (eintrag.seite == "vorsteuer") != (rolle == "vorsteuer") or (
            rolle != "vorsteuer" and eintrag.steuersatz != satz
        ):
            klaerungen.append(f"Kennzahl {kz} wird von Umsatz- und Vorsteuerkonten oder mit verschiedenen Sätzen bebucht.")
            continue
        eintrag.steuerschluessel = sorted(set(eintrag.steuerschluessel) | {c for *_, c in nutzungen})
        if rolle == "erloes":
            eintrag.bemessungsgrundlage = (eintrag.bemessungsgrundlage or NULL) + haben_saldo(konto)
        elif rolle == "steuer":
            eintrag.steuer += haben_saldo(konto)
        else:
            eintrag.steuer -= haben_saldo(konto)

    for k in kennzahlen.values():
        if k.seite == "umsatz" and k.steuersatz and k.bemessungsgrundlage is not None:
            erwartet = k.bemessungsgrundlage * k.steuersatz / Decimal("100")
            if abs(erwartet - k.steuer) > max(Decimal("1.00"), abs(erwartet) * Decimal("0.002")):
                klaerungen.append(
                    f"Kennzahl {k.kennzahl}: Umsatzsteuer {k.steuer:.2f} passt nicht zu "
                    f"{k.steuersatz.normalize():f} % von {k.bemessungsgrundlage:.2f}."
                )

    liste = sorted(kennzahlen.values(), key=lambda k: (k.seite != "umsatz", k.kennzahl))
    umsatz_netto = sum((k.bemessungsgrundlage or NULL for k in liste if k.seite == "umsatz"), NULL)
    umsatzsteuer = sum((k.steuer for k in liste if k.seite == "umsatz"), NULL)
    vorsteuer = sum((k.steuer for k in liste if k.seite == "vorsteuer"), NULL)
    return UStVAStand(
        zeitraum=zeitraum, perioden=ps, kennzahlen=liste,
        umsatz_netto=umsatz_netto.quantize(CENT), umsatzsteuer=umsatzsteuer.quantize(CENT),
        vorsteuer=vorsteuer.quantize(CENT), zahllast=(umsatzsteuer - vorsteuer).quantize(CENT),
        klaerungen=klaerungen, gebuchte_buchungen=int(stand["gebucht"] or 0), offene_entwuerfe=int(stand["entwurf"] or 0),
    )
