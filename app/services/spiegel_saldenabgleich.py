"""Spiegelbetrieb L3 -> VALEO: monatlicher Saldenabgleich je Personenkonto (M6, 26.11.2026) - liest nur.

Quelle: L3 ``DEBITOREN``/``KREDITOREN`` (je Konto und Jahr EBVORTRAG und Monatswerte SIST01-SIST12) als Objektart
``kontosaldo`` ueber die Adapterstrecke (Profil ``l3_spiegel``, freigegeben). Die Abzugsabfrage liefert je Konto den
**Saldo zum Monatsende** (``saldo``) samt ``jahr`` und ``monat``; ob SIST Monatsbewegung oder kumulierter Stand ist,
wird am Abzug bestaetigt und dort verrechnet, nicht hier.

VALEO-Seite: ``app/finance/personenkonto.saldenliste`` zum letzten Tag des Monats - der Saldo je Personenkonto aus
gebuchten Zeilen der Sammelkonten (Personenkonten im Hauptbuch, Nutzerentscheid 26.11.2026). Die L3-Kontonummer ist
seit dem Nutzerentscheid vom 25.11.2026 das Konto des Geschaeftspartners, deshalb ist der Abgleich Konto fuer Konto.

Ergebnis je L3-Konto: ``unveraendert`` (Saldo gleich), ``geaendert`` (Differenz ``saldo``), ``fehler`` (Konto fehlt
in VALEO bei L3-Saldo ungleich 0). Dazu ``fehlt_in_l3``: VALEO-Personenkonten mit Saldo, die der Abzug nicht
enthaelt, und Zeilen ohne Personenkonto - beides sind ungeklaerte Differenzen im Sinne der M6-Abnahme.
"""
from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy.orm import Session

from app.finance.personenkonto import saldenliste
from app.services.spiegel_abgleich_basis import abschliessen, freigegebene_zeilen, neuer_zaehler, protokolliere

OBJEKTART = "kontosaldo"


def _betrag(roh: Any) -> Decimal:
    wert = str(roh if roh is not None else "").strip()
    if "," in wert and "." not in wert:
        wert = wert.replace(",", ".")
    try:
        return Decimal(wert or "0").quantize(Decimal("0.01"))
    except InvalidOperation as fehler:
        raise ValueError(f"Saldo {roh!r} ist keine Zahl") from fehler


def _monatsende(zeilen: list[Any]) -> date:
    perioden = {(int(dict(z["canonical_payload"] or {}).get("jahr") or 0),
                 int(dict(z["canonical_payload"] or {}).get("monat") or 0)) for z in zeilen}
    if len(perioden) != 1:
        raise ValueError("Ein Abzug muss genau einen Monat enthalten (jahr, monat)")
    jahr, monat = perioden.pop()
    if not 1 <= monat <= 12 or jahr < 2000:
        raise ValueError(f"Periode {jahr}-{monat} ist ungueltig")
    return date(jahr, monat, calendar.monthrange(jahr, monat)[1])


def abgleichen(db: Session, tenant_id: str, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
    """Gleicht die L3-Monatssalden eines freigegebenen Batches mit der VALEO-Saldenliste ab."""
    profil, zeilen = freigegebene_zeilen(db, tenant_id, batch_id, OBJEKTART)
    stichtag = _monatsende(zeilen) if zeilen else None
    valeo = saldenliste(db, tenant_id, bis=stichtag) if stichtag else {"personenkonten": {}, "ohne_personenkonto": {}}
    konten = valeo["personenkonten"]
    zaehler = neuer_zaehler()
    gesehen: set[str] = set()
    for z in zeilen:
        p = dict(z["canonical_payload"] or {})
        konto = str(p.get("konto") or "").strip()
        differenzen: dict[str, Any] = {}
        fehler = None
        try:
            l3 = _betrag(p.get("saldo"))
            gesehen.add(konto)
            ist = Decimal(konten[konto]["saldo"]) if konto in konten else None
            if ist is None and l3 != 0:
                raise ValueError(f"Konto {konto or '-'} hat in L3 Saldo {l3}, in VALEO keine Buchung")
            ergebnis = "unveraendert" if (ist or Decimal("0")) == l3 else "geaendert"
            if ergebnis == "geaendert":
                differenzen = {"saldo": {"valeo": str(ist), "l3": str(l3)}}
        except ValueError as exc:
            ergebnis, fehler = "fehler", str(exc)
        zaehler[ergebnis] += 1
        protokolliere(db, tenant_id, batch_id, z, OBJEKTART, ergebnis, differenzen, fehler)
    fehlt = [{"konto": k, "valeo_saldo": v["saldo"]} for k, v in sorted(konten.items())
             if k not in gesehen and Decimal(v["saldo"]) != 0]
    ohne = valeo.get("ohne_personenkonto", {})
    abschliessen(db, tenant_id, batch_id, profil, "mirror_balances_reconciled", actor, reason,
                 {**zaehler, "fehlt_in_l3": len(fehlt), "ohne_personenkonto": len(ohne)})
    return {"batch_id": batch_id, "stichtag": stichtag.isoformat() if stichtag else None, **zaehler,
            "fehlt_in_l3": fehlt, "ohne_personenkonto": ohne,
            "abweichungsfrei": zaehler["geaendert"] == 0 and zaehler["fehler"] == 0 and not fehlt and not ohne}
