"""
controlling_safe_read_contracts.py — Defensive Controlling-Read-Contracts (Wave 82, Gap 032)

Stellt sicher dass KPI/Timeseries-Endpoints nie 500 liefern:
- None/fehlende Werte werden sicher in typisierte Defaults umgewandelt
- Ampel-Status immer gesetzt ("UNBEKANNT" statt Exception)
- safe_kpi_response() und safe_timeseries_response() als Wrapper

Gap 032: 500er bei controlling/kpis/timeseries eliminieren — KPI: Error Rate <0.5%
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AmpelStatus(str, Enum):
    """Ampelstatus eines KPI-Werts."""
    GRUEN     = "GRUEN"      # Ziel erreicht oder übertroffen
    GELB      = "GELB"       # Im Toleranzbereich
    ROT       = "ROT"        # Ziel verfehlt
    UNBEKANNT = "UNBEKANNT"  # Kein Vergleichswert vorhanden


class KpiVerfuegbarkeit(str, Enum):
    """Verfügbarkeit eines KPI-Werts."""
    VERFUEGBAR  = "VERFUEGBAR"   # Wert vorhanden und plausibel
    LEER        = "LEER"         # Kein Wert in DB
    SCHEMA_FEHLT = "SCHEMA_FEHLT" # Tabelle/Schema nicht vorhanden
    PARSE_FEHLER = "PARSE_FEHLER" # Wert konnte nicht geparst werden


# ---------------------------------------------------------------------------
# Safe KPI Value
# ---------------------------------------------------------------------------

@dataclass
class KpiSafeValue:
    """
    Typisierter KPI-Wert mit sicheren Defaults — niemals None bei Pflichtfeldern.

    Erzeugt via KpiSafeValue.from_raw(rohdaten_dict) oder safe_kpi_response().
    """
    kpi_code: str
    name: str
    wert: float | None          # None = kein Messwert vorhanden
    zielwert: float | None
    einheit: str
    ampel: AmpelStatus
    verfuegbarkeit: KpiVerfuegbarkeit
    periode: str = ""           # ISO-Datum des letzten Messwerts
    fehler_meldung: str = ""    # Leer wenn kein Fehler

    @classmethod
    def from_raw(cls, raw: dict[str, Any], kpi_code: str = "") -> "KpiSafeValue":
        """
        Erzeugt KpiSafeValue aus rohen DB-Daten ohne Exception-Risiko.
        Ungültige oder fehlende Felder werden auf sichere Defaults gesetzt.
        """
        if not raw:
            return cls(
                kpi_code=kpi_code or "UNBEKANNT",
                name="",
                wert=None,
                zielwert=None,
                einheit="",
                ampel=AmpelStatus.UNBEKANNT,
                verfuegbarkeit=KpiVerfuegbarkeit.LEER,
                fehler_meldung="Kein Datensatz gefunden",
            )

        def _safe_float(v: Any) -> float | None:
            if v is None:
                return None
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        wert = _safe_float(raw.get("current_value") or raw.get("wert") or raw.get("value"))
        zielwert = _safe_float(raw.get("target_value") or raw.get("zielwert") or raw.get("target"))

        # Ampel berechnen wenn Wert und Ziel vorhanden
        ampel = AmpelStatus.UNBEKANNT
        if wert is not None and zielwert is not None and zielwert != 0:
            ratio = wert / zielwert
            if ratio >= 0.95:
                ampel = AmpelStatus.GRUEN
            elif ratio >= 0.80:
                ampel = AmpelStatus.GELB
            else:
                ampel = AmpelStatus.ROT
        elif wert is not None:
            ampel = AmpelStatus.GRUEN  # Wert vorhanden, kein Ziel → neutral grün

        # Ampel aus DB überschreibt Berechnung falls explizit gesetzt
        raw_ampel = raw.get("ampel") or raw.get("ampel_status") or ""
        if raw_ampel:
            try:
                ampel = AmpelStatus(str(raw_ampel).upper())
            except ValueError:
                pass  # ungültiger Wert aus DB → berechneter Wert bleibt

        verfuegbarkeit = (
            KpiVerfuegbarkeit.LEER if wert is None else KpiVerfuegbarkeit.VERFUEGBAR
        )

        return cls(
            kpi_code=str(raw.get("kpi_code") or kpi_code or "UNBEKANNT"),
            name=str(raw.get("name") or raw.get("kpi_name") or ""),
            wert=wert,
            zielwert=zielwert,
            einheit=str(raw.get("unit") or raw.get("einheit") or ""),
            ampel=ampel,
            verfuegbarkeit=verfuegbarkeit,
            periode=str(raw.get("period_start") or raw.get("periode") or ""),
        )

    @property
    def ist_verfuegbar(self) -> bool:
        return self.verfuegbarkeit == KpiVerfuegbarkeit.VERFUEGBAR

    @property
    def wert_oder_null(self) -> float:
        """Gibt 0.0 zurück wenn kein Wert vorhanden — nie None."""
        return self.wert if self.wert is not None else 0.0

    def as_dict(self) -> dict:
        return {
            "kpi_code": self.kpi_code,
            "name": self.name,
            "wert": self.wert,
            "zielwert": self.zielwert,
            "einheit": self.einheit,
            "ampel": self.ampel.value,
            "verfuegbarkeit": self.verfuegbarkeit.value,
            "ist_verfuegbar": self.ist_verfuegbar,
            "wert_oder_null": self.wert_oder_null,
            "periode": self.periode,
            "fehler_meldung": self.fehler_meldung,
        }


# ---------------------------------------------------------------------------
# Safe Timeseries Entry
# ---------------------------------------------------------------------------

@dataclass
class TimeseriesSafeEntry:
    """Ein einzelner Zeitreihenwert — immer typisiert und nie None."""
    periode: str
    wert: float
    einheit: str = ""
    kpi_code: str = ""

    def as_dict(self) -> dict:
        return {
            "periode": self.periode,
            "wert": self.wert,
            "einheit": self.einheit,
            "kpi_code": self.kpi_code,
        }


@dataclass
class TimeseriesSafeResult:
    """Ergebnis einer Timeseries-Abfrage — immer valide, nie 500."""
    eintraege: list[TimeseriesSafeEntry]
    kpi_code: str = ""
    ist_leer: bool = False
    fehler_meldung: str = ""

    @property
    def anzahl(self) -> int:
        return len(self.eintraege)

    def as_dict(self) -> dict:
        return {
            "kpi_code": self.kpi_code,
            "anzahl": self.anzahl,
            "ist_leer": self.ist_leer,
            "fehler_meldung": self.fehler_meldung,
            "eintraege": [e.as_dict() for e in self.eintraege],
        }


# ---------------------------------------------------------------------------
# Safety Evaluation
# ---------------------------------------------------------------------------

@dataclass
class ControllingReadSafetyResult:
    """Ergebnis der Sicherheitsprüfung für einen Controlling-Datensatz."""
    kpi_code: str
    is_safe: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "kpi_code": self.kpi_code,
            "is_safe": self.is_safe,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def evaluate_controlling_safety(raw: dict[str, Any]) -> ControllingReadSafetyResult:
    """
    Prüft ob ein roher KPI-Datensatz sicher verarbeitet werden kann.

    Gibt is_safe=True zurück wenn keine kritischen Fehler vorhanden.
    Kritische Fehler: kpi_code fehlt, Wert nicht parsebar wenn angegeben.
    """
    errors: list[str] = []
    warnings: list[str] = []
    kpi_code = str(raw.get("kpi_code") or "")

    if not kpi_code:
        errors.append("kpi_code fehlt")

    raw_wert = raw.get("current_value") or raw.get("wert") or raw.get("value")
    if raw_wert is not None:
        try:
            float(raw_wert)
        except (TypeError, ValueError):
            errors.append(f"Wert '{raw_wert}' ist nicht parsebar")

    raw_ziel = raw.get("target_value") or raw.get("zielwert")
    if raw_ziel is not None:
        try:
            float(raw_ziel)
        except (TypeError, ValueError):
            warnings.append(f"Zielwert '{raw_ziel}' ist nicht parsebar — wird ignoriert")

    if not raw.get("name"):
        warnings.append("KPI-Name fehlt")

    return ControllingReadSafetyResult(
        kpi_code=kpi_code,
        is_safe=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Safe Response Factories
# ---------------------------------------------------------------------------

def safe_kpi_response(
    raw: dict[str, Any] | None,
    kpi_code: str = "",
) -> KpiSafeValue:
    """
    Erstellt sicher einen KpiSafeValue — niemals Exception.

    Wird in FastAPI-Endpoints als Wrapper um DB-Abfragen genutzt:
        return safe_kpi_response(db.query(...).first(), "UMSATZ_MONAT")
    """
    try:
        return KpiSafeValue.from_raw(raw or {}, kpi_code)
    except Exception as exc:
        return KpiSafeValue(
            kpi_code=kpi_code or "UNBEKANNT",
            name="",
            wert=None,
            zielwert=None,
            einheit="",
            ampel=AmpelStatus.UNBEKANNT,
            verfuegbarkeit=KpiVerfuegbarkeit.PARSE_FEHLER,
            fehler_meldung=f"Parse-Fehler: {exc}",
        )


def safe_timeseries_response(
    raw_list: list[dict[str, Any]] | None,
    kpi_code: str = "",
) -> TimeseriesSafeResult:
    """
    Erstellt sicher einen TimeseriesSafeResult — niemals Exception.

    Leere Liste und None werden als ist_leer=True zurückgegeben.
    """
    if not raw_list:
        return TimeseriesSafeResult(
            eintraege=[],
            kpi_code=kpi_code,
            ist_leer=True,
        )

    eintraege: list[TimeseriesSafeEntry] = []
    for row in raw_list:
        try:
            wert_raw = row.get("wert") or row.get("value") or row.get("kpi_value") or 0
            wert = float(wert_raw)
            periode = str(row.get("periode") or row.get("period_start") or row.get("period") or "")
            eintraege.append(TimeseriesSafeEntry(
                periode=periode,
                wert=wert,
                einheit=str(row.get("unit") or row.get("einheit") or ""),
                kpi_code=str(row.get("kpi_code") or kpi_code),
            ))
        except (TypeError, ValueError):
            continue  # Einzelne fehlerhafte Zeile überspringen, nicht 500

    return TimeseriesSafeResult(
        eintraege=eintraege,
        kpi_code=kpi_code,
        ist_leer=len(eintraege) == 0,
    )


def safe_kpi_list_response(
    raw_list: list[dict[str, Any]] | None,
) -> list[KpiSafeValue]:
    """Erstellt sicher eine Liste von KpiSafeValues — niemals Exception."""
    if not raw_list:
        return []
    result = []
    for row in raw_list:
        try:
            result.append(KpiSafeValue.from_raw(row))
        except Exception:
            continue
    return result
