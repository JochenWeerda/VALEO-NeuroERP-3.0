"""Typisierte ``Feed``-Ansicht für den Solver (Refactor Schritt 5, 2026-04-23).

Die bisherige Datenstruktur des Optimizer-Eingangs ist ein
``Dict[str, Any]`` mit ~30 numerischen und ~6 textuellen Feldern. Das ist
flexibel, aber teuer (``feed.get("me") or 0`` -> ``float(...)`` mehrfach)
und nicht typsicher.

Dieses Modul stellt eine schlanke, **rein read-only** Hülle um diese
Dict-Struktur bereit: ``Feed.from_dict(feed_dict)`` liefert eine
slotted Dataclass mit allen numerischen Feldern bereits ``float``
normalisiert und Fehlwerten durch 0.0 ersetzt.

**Einsatz**:
- Interne Solver-Hilfsfunktionen (``aggregate_ration``, zukünftige
  Constraint-Builder) können ``Feed`` statt Dict entgegennehmen.
- Die öffentlichen API-Antworten bleiben vorerst Dict-basiert, damit der
  Refactor ohne Breaking Changes bleibt.
- Ein vollständiger Feed-Dataclass-Switch im gesamten Solver ist ein
  zukünftiger, separat zu planender Schritt.

Grund: Der User hat "für den Solverbereich echte Modelle" gewünscht und
explizit ``@dataclass(slots=True)`` für interne Solver-Typen.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Mapping, Optional


def _f(value: Any) -> float:
    """``float``-Konvertierung mit 0.0 als Fallback."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _opt_f(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass(slots=True)
class Feed:
    """Schlanke, typisierte Ansicht eines Optimizer-Feeds.

    Wird via ``Feed.from_dict`` erzeugt. Die ursprüngliche Dict-Struktur
    bleibt daneben erhalten; ``Feed`` ist eine zusätzliche Sicht.
    """

    id: str
    name: str
    group: str
    futterart: str
    forage: bool
    structural_coproduct: bool
    dm_frac: float
    price: float
    min_kg: float
    max_kg: float

    me: float
    sidp: float
    cp: float
    ndf: float
    adf: float
    st: float
    bst: float
    zu: float
    nfc: float
    xl: float

    ca: float
    p: float
    na: float
    mg: float
    k: float

    # Optionale Felder (können None sein, wenn nicht gesetzt).
    rmd: Optional[float] = None
    omdfan1: Optional[float] = None
    sidlys: Optional[float] = None
    sidmet: Optional[float] = None
    ndfd: Optional[float] = None
    ge: Optional[float] = None
    dcab: Optional[float] = None
    edg: Optional[float] = None

    fan_slope_source: str = "fallback"
    special: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Feed":
        """Erzeugt einen ``Feed`` aus der bisherigen Dict-Repräsentation.

        Unbekannte Keys werden ignoriert; fehlende numerische Keys
        erhalten 0.0.
        """
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            group=str(data.get("group", "") or ""),
            futterart=str(data.get("futterart", "") or ""),
            forage=bool(data.get("forage", False)),
            structural_coproduct=bool(data.get("structural_coproduct", False)),
            dm_frac=_f(data.get("dm_frac")),
            price=_f(data.get("price")),
            min_kg=_f(data.get("min_kg")),
            max_kg=_f(data.get("max_kg")),
            me=_f(data.get("me")),
            sidp=_f(data.get("sidp")),
            cp=_f(data.get("cp")),
            ndf=_f(data.get("ndf")),
            adf=_f(data.get("adf")),
            st=_f(data.get("st")),
            bst=_f(data.get("bst")),
            zu=_f(data.get("zu")),
            nfc=_f(data.get("nfc")),
            xl=_f(data.get("xl")),
            ca=_f(data.get("ca")),
            p=_f(data.get("p")),
            na=_f(data.get("na")),
            mg=_f(data.get("mg")),
            k=_f(data.get("k")),
            rmd=_opt_f(data.get("rmd")),
            omdfan1=_opt_f(data.get("omdfan1")),
            sidlys=_opt_f(data.get("sidlys")),
            sidmet=_opt_f(data.get("sidmet")),
            ndfd=_opt_f(data.get("ndfd")),
            ge=_opt_f(data.get("ge")),
            dcab=_opt_f(data.get("dcab")),
            edg=_opt_f(data.get("edg")),
            fan_slope_source=str(data.get("_fan_slope_source", "fallback") or "fallback"),
            special=data.get("_special"),
        )


__all__ = ["Feed"]
