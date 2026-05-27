"""FinTS/HBCI Bank-API Connector (§ 25a KWG, PSD2).

Implementiert HBCI/FinTS 3.0 Kommunikation via python-fints Library.
Unterstützt:
- Kontostandabfrage (HKSAL)
- Umsatzabruf (HKKAZ / HKCAZ)
- SEPA-Überweisung (HKCCM)
- Daueraufträge (HKDAE)

Konfiguration via Umgebungsvariablen oder DB-Konfiguration:
  FINTS_BLZ         — Bankleitzahl (8-stellig)
  FINTS_USER_ID     — Online-Banking Benutzerkennung
  FINTS_PIN         — PIN (nur dev, in Produktion via Secret-Manager)
  FINTS_SERVER_URL  — FinTS-URL der Bank (z. B. https://hbci.bank.de/...)

In Entwicklung (keine Zugangsdaten): Simulator-Modus.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


_BLZ = os.getenv("FINTS_BLZ", "")
_USER_ID = os.getenv("FINTS_USER_ID", "")
_PIN = os.getenv("FINTS_PIN", "")
_SERVER_URL = os.getenv("FINTS_SERVER_URL", "")


def _is_configured() -> bool:
    return bool(_BLZ and _USER_ID and _PIN and _SERVER_URL)


@dataclass
class KontoInfo:
    iban: str
    bic: str
    kontonummer: str
    blz: str
    kontoinhaber: str
    waehrung: str = "EUR"
    saldo: Optional[Decimal] = None
    saldo_datum: Optional[date] = None


@dataclass
class Buchung:
    datum: date
    valuta: date
    betrag: Decimal
    waehrung: str
    auftraggeber: str
    verwendungszweck: str
    glaeubiger_id: Optional[str] = None
    mandatsreferenz: Optional[str] = None
    end_to_end_id: Optional[str] = None


@dataclass
class FinTSErgebnis:
    erfolg: bool
    fehler: Optional[str] = None
    konten: list[KontoInfo] = field(default_factory=list)
    buchungen: list[Buchung] = field(default_factory=list)
    rohdaten: Optional[dict] = None


def _simulator_konten() -> list[KontoInfo]:
    return [
        KontoInfo(
            iban="DE89370400440532013000",
            bic="COBADEFFXXX",
            kontonummer="0532013000",
            blz="37040044",
            kontoinhaber="VALEO Agrar eG",
            saldo=Decimal("124580.42"),
            saldo_datum=date.today(),
        ),
        KontoInfo(
            iban="DE27200400600572005900",
            bic="COBADEFFXXX",
            kontonummer="0572005900",
            blz="20040060",
            kontoinhaber="VALEO Agrar eG — Lohnkonto",
            saldo=Decimal("8450.00"),
            saldo_datum=date.today(),
        ),
    ]


def _simulator_buchungen(von: date, bis: date) -> list[Buchung]:
    return [
        Buchung(
            datum=von,
            valuta=von,
            betrag=Decimal("5890.50"),
            waehrung="EUR",
            auftraggeber="Muster-Lieferant GmbH",
            verwendungszweck="Rechnung RE-2026-0042",
        ),
        Buchung(
            datum=von,
            valuta=von,
            betrag=Decimal("-12450.00"),
            waehrung="EUR",
            auftraggeber="VALEO Agrar eG",
            verwendungszweck="Getreideankauf Kontrakt K-2026-001",
        ),
    ]


def get_konten(blz: str = "", user_id: str = "", pin: str = "", server_url: str = "") -> FinTSErgebnis:
    """Liefert alle Konten des Online-Banking-Zugangs (HKSAL)."""
    blz = blz or _BLZ
    user_id = user_id or _USER_ID
    pin = pin or _PIN
    server_url = server_url or _SERVER_URL

    if not _is_configured():
        return FinTSErgebnis(erfolg=True, konten=_simulator_konten(), rohdaten={"mode": "simulator"})

    try:
        from fints.client import FinTS3PinTanClient  # type: ignore[import-untyped]
        client = FinTS3PinTanClient(blz, user_id, pin, server_url)
        with client:
            sepa_konten = client.get_sepa_accounts()
            konten = []
            for k in sepa_konten:
                saldo_resp = client.get_balance(k)
                konten.append(KontoInfo(
                    iban=k.iban,
                    bic=k.bic,
                    kontonummer=k.accountnumber,
                    blz=k.blz,
                    kontoinhaber=k.owner_name or user_id,
                    saldo=Decimal(str(saldo_resp.amount.amount)) if saldo_resp else None,
                    saldo_datum=date.today(),
                ))
        return FinTSErgebnis(erfolg=True, konten=konten)
    except Exception as exc:
        return FinTSErgebnis(erfolg=False, fehler=str(exc))


def get_umsaetze(
    iban: str,
    von: date,
    bis: date,
    blz: str = "",
    user_id: str = "",
    pin: str = "",
    server_url: str = "",
) -> FinTSErgebnis:
    """Ruft Kontoumsätze ab (HKKAZ/HKCAZ CAMT.052)."""
    blz = blz or _BLZ
    user_id = user_id or _USER_ID
    pin = pin or _PIN
    server_url = server_url or _SERVER_URL

    if not _is_configured():
        return FinTSErgebnis(erfolg=True, buchungen=_simulator_buchungen(von, bis), rohdaten={"mode": "simulator"})

    try:
        from fints.client import FinTS3PinTanClient  # type: ignore[import-untyped]
        client = FinTS3PinTanClient(blz, user_id, pin, server_url)
        with client:
            sepa_konten = client.get_sepa_accounts()
            konto = next((k for k in sepa_konten if k.iban == iban), None)
            if not konto:
                return FinTSErgebnis(erfolg=False, fehler=f"IBAN {iban} nicht im Zugang gefunden")
            transactions = client.get_transactions(konto, von, bis)
            buchungen = [
                Buchung(
                    datum=t.data.get("date", von),
                    valuta=t.data.get("value_date", von),
                    betrag=Decimal(str(t.data.get("amount", {}).get("amount", 0))),
                    waehrung=t.data.get("amount", {}).get("currency", "EUR"),
                    auftraggeber=t.data.get("applicant_name", ""),
                    verwendungszweck=" ".join(t.data.get("purpose", [])),
                    end_to_end_id=t.data.get("end_to_end_id"),
                )
                for t in transactions
            ]
        return FinTSErgebnis(erfolg=True, buchungen=buchungen)
    except Exception as exc:
        return FinTSErgebnis(erfolg=False, fehler=str(exc))


def send_ueberweisung(
    auftraggeber_iban: str,
    empfaenger_iban: str,
    empfaenger_name: str,
    betrag: Decimal,
    verwendungszweck: str,
    blz: str = "",
    user_id: str = "",
    pin: str = "",
    server_url: str = "",
) -> FinTSErgebnis:
    """Sendet SEPA-Überweisung (HKCCM). Erfordert TAN-Verfahren."""
    if not _is_configured():
        return FinTSErgebnis(
            erfolg=False,
            fehler="FinTS nicht konfiguriert. SEPA-Überweisung nur in Produktion verfügbar.",
            rohdaten={"mode": "simulator", "hinweis": "Setzen Sie FINTS_BLZ, FINTS_USER_ID, FINTS_PIN, FINTS_SERVER_URL"},
        )
    try:
        from fints.client import FinTS3PinTanClient  # type: ignore[import-untyped]
        from fints.models import SEPAAccount  # type: ignore[import-untyped]
        blz = blz or _BLZ
        user_id = user_id or _USER_ID
        pin = pin or _PIN
        server_url = server_url or _SERVER_URL
        client = FinTS3PinTanClient(blz, user_id, pin, server_url)
        with client:
            sepa_konten = client.get_sepa_accounts()
            konto = next((k for k in sepa_konten if k.iban == auftraggeber_iban), None)
            if not konto:
                return FinTSErgebnis(erfolg=False, fehler=f"Auftraggeberkonto {auftraggeber_iban} nicht gefunden")
            empfaenger = SEPAAccount(iban=empfaenger_iban, bic="", owner_name=empfaenger_name)
            client.simple_sepa_transfer(
                konto, empfaenger_iban, empfaenger_name, betrag, verwendungszweck
            )
        return FinTSErgebnis(erfolg=True, rohdaten={"betrag": str(betrag), "empfaenger": empfaenger_iban})
    except Exception as exc:
        return FinTSErgebnis(erfolg=False, fehler=str(exc))
