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


@dataclass
class TanChallenge:
    tan_medium: str
    challenge_text: str
    challenge_hhduc: Optional[str] = None
    tan_verfahren: str = "pushTAN"
    session_token: Optional[str] = None


@dataclass
class TanMedium:
    name: str
    tan_verfahren: str
    aktiv: bool = True


def get_tan_medien(blz: str = "", user_id: str = "", pin: str = "", server_url: str = "") -> FinTSErgebnis:
    """Listet verfuegbare TAN-Medien bzw. TAN-Verfahren."""
    blz = blz or _BLZ
    user_id = user_id or _USER_ID
    pin = pin or _PIN
    server_url = server_url or _SERVER_URL

    if not _is_configured():
        return FinTSErgebnis(
            erfolg=True,
            rohdaten={
                "mode": "simulator",
                "tan_medien": [
                    {"name": "Meine SparkassenCard", "tan_verfahren": "chipTAN", "aktiv": True},
                    {"name": "pushTAN-App", "tan_verfahren": "pushTAN", "aktiv": True},
                ],
            },
        )

    try:
        from fints.client import FinTS3PinTanClient  # type: ignore[import-untyped]

        client = FinTS3PinTanClient(blz, user_id, pin, server_url)
        with client:
            mechanisms = client.get_tan_mechanisms()
            return FinTSErgebnis(
                erfolg=True,
                rohdaten={
                    "mode": "produktiv",
                    "tan_medien": [
                        {"id": key, "name": mechanism.name, "tan_verfahren": key, "aktiv": True}
                        for key, mechanism in mechanisms.items()
                    ],
                },
            )
    except Exception as exc:
        return FinTSErgebnis(erfolg=False, fehler=str(exc))


def initiiere_ueberweisung_mit_tan(
    auftraggeber_iban: str,
    empfaenger_iban: str,
    empfaenger_name: str,
    betrag: Decimal,
    verwendungszweck: str,
    blz: str = "",
    user_id: str = "",
    pin: str = "",
    server_url: str = "",
    tan_verfahren_id: str = "",
) -> tuple[FinTSErgebnis, Optional[TanChallenge]]:
    """Schritt 1 des TAN-Flows: Ueberweisung einleiten und Challenge liefern."""
    if not _is_configured():
        challenge = TanChallenge(
            tan_medium="pushTAN-App (Simulator)",
            challenge_text="Bitte bestaetigen Sie die Ueberweisung in Ihrer Banking-App.",
            tan_verfahren="pushTAN",
            session_token=f"SIM-{auftraggeber_iban[-4:]}-{empfaenger_iban[-4:]}-{abs(hash((betrag, verwendungszweck))) % 100000}",
        )
        return FinTSErgebnis(erfolg=True, rohdaten={"mode": "simulator", "schritt": "challenge"}), challenge

    try:
        from fints.client import FinTS3PinTanClient, NeedTANResponse  # type: ignore[import-untyped]

        blz = blz or _BLZ
        user_id = user_id or _USER_ID
        pin = pin or _PIN
        server_url = server_url or _SERVER_URL

        client = FinTS3PinTanClient(blz, user_id, pin, server_url)
        with client:
            if tan_verfahren_id:
                mechanisms = client.get_tan_mechanisms()
                if tan_verfahren_id in mechanisms:
                    client.set_tan_mechanism(mechanisms[tan_verfahren_id])

            sepa_konten = client.get_sepa_accounts()
            konto = next((k for k in sepa_konten if k.iban == auftraggeber_iban), None)
            if not konto:
                return FinTSErgebnis(erfolg=False, fehler=f"Konto {auftraggeber_iban} nicht gefunden"), None

            try:
                client.simple_sepa_transfer(konto, empfaenger_iban, empfaenger_name, betrag, verwendungszweck)
                return FinTSErgebnis(erfolg=True, rohdaten={"schritt": "abgeschlossen"}), None
            except NeedTANResponse as tan_request:
                challenge = TanChallenge(
                    tan_medium=getattr(tan_request, "tan_medium_name", "TAN-Medium"),
                    challenge_text=getattr(tan_request, "challenge", "Bitte TAN eingeben"),
                    challenge_hhduc=getattr(tan_request, "challenge_hhduc", None),
                    tan_verfahren=tan_verfahren_id or "unbekannt",
                    session_token=getattr(tan_request, "challenge_label", None),
                )
                return FinTSErgebnis(erfolg=True, rohdaten={"schritt": "challenge"}), challenge
    except Exception as exc:
        return FinTSErgebnis(erfolg=False, fehler=str(exc)), None


def bestaetige_tan(
    session_token: str,
    tan: str,
    blz: str = "",
    user_id: str = "",
    pin: str = "",
    server_url: str = "",
) -> FinTSErgebnis:
    """Schritt 2 des TAN-Flows: TAN bestaetigen und Auftrag abschliessen."""
    if not _is_configured():
        if tan == "000000":
            return FinTSErgebnis(
                erfolg=True,
                rohdaten={"mode": "simulator", "schritt": "abgeschlossen", "session_token": session_token},
            )
        return FinTSErgebnis(erfolg=False, fehler="TAN ungueltig (Simulator: '000000' verwenden)")

    try:
        from fints.client import FinTS3PinTanClient  # type: ignore[import-untyped]

        blz = blz or _BLZ
        user_id = user_id or _USER_ID
        pin = pin or _PIN
        server_url = server_url or _SERVER_URL

        client = FinTS3PinTanClient(blz, user_id, pin, server_url)
        with client:
            client.send_tan(tan, session_token)
        return FinTSErgebnis(erfolg=True, rohdaten={"schritt": "abgeschlossen"})
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
