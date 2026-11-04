"""Zeilenformen der Portal-Listenwege (``portal_kundenwege.py``, Masken-Cluster Batch 7, 03.11.2026).

Bis hier antworteten die Wege mit ``CompatBridgeOut`` (``extra="allow"`` ohne Felder): Das Feldvertrags-Gate konnte
nicht pruefen, ob die Portalmasken nach den gelieferten Schluesseln fragen. Die Felder entsprechen genau dem, was
``PortalCompatService.list_portal_*`` liefert; ein Feld, das hier fehlt, wuerde die Antwort stillschweigend kuerzen.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict


def _als_text(wert: Any) -> str | None:
    """Belege liegen als JSON vor: Nummern koennen Zahlen sein, Kennungen UUIDs, Daten ``date``-Werte."""
    if wert is None:
        return None
    if isinstance(wert, (date, datetime)):
        return wert.isoformat()
    return str(wert)


Text = Annotated[str | None, BeforeValidator(_als_text)]


class _Zeile(BaseModel):
    model_config = ConfigDict(extra="ignore")


class PortalAnfrageZeile(_Zeile):
    id: Text = None
    nummer: Text = None
    betreff: Text = None
    datum: Text = None
    status: Text = None


class PortalBestellungZeile(_Zeile):
    id: Text = None
    nummer: Text = None
    datum: Text = None
    artikel: Text = None
    menge: float | None = None
    betrag: float | None = None
    status: Text = None


class PortalDokumentZeile(_Zeile):
    id: Text = None
    name: Text = None
    kategorie: Text = None
    datum: Text = None
    groesse: int | None = None
    typ: Text = None


class PortalFeldbuchZeile(_Zeile):
    id: Text = None
    schlag: Text = None
    kultur: Text = None
    flaeche: float | None = None
    letzteMassnahme: Text = None  # noqa: N815 - Schluessel der bestehenden Antwort
    naechsteMassnahme: Text = None  # noqa: N815


class PortalNaehrstoffZeile(_Zeile):
    id: Text = None
    schlag: Text = None
    kultur: Text = None
    n_saldo: float | None = None
    p_saldo: float | None = None
    k_saldo: float | None = None
    bewertung: Text = None


class PortalRechnungZeile(_Zeile):
    id: Text = None
    nummer: Text = None
    datum: Text = None
    betrag: float | None = None
    status: Text = None


class PortalShopZeile(_Zeile):
    id: Text = None
    name: Text = None
    kategorie: Text = None
    preis: float | None = None
    einheit: Text = None
    verfuegbar: bool | None = None


class PortalVertragZeile(_Zeile):
    id: Text = None
    nummer: Text = None
    typ: Text = None
    partner: Text = None
    laufzeitBis: Text = None  # noqa: N815
    status: Text = None


class PortalZertifikatZeile(_Zeile):
    id: Text = None
    art: Text = None
    nummer: Text = None
    gueltigBis: Text = None  # noqa: N815
    status: Text = None
