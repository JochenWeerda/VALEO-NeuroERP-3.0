"""
query_fallback_contracts.py — Query-Fallback-Contracts (Wave 32, Gap 032)

Legt fest, wie das System bei Query-Fehlern reagiert:
CACHE / SAFE_DEFAULT / ERROR_RESPONSE — deterministisch, ohne 500er zu propagieren.

Gap 032: 500er bei controlling/kpis/timeseries eliminieren — Error Rate <0.5%
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class QueryFallbackTyp(str, Enum):
    """Wie wird bei einem Query-Fehler reagiert?"""
    CACHE           = "CACHE"           # Letzten bekannten Cache-Wert zurueckgeben
    SAFE_DEFAULT    = "SAFE_DEFAULT"    # Definierten Default-Wert zurueckgeben
    ERROR_RESPONSE  = "ERROR_RESPONSE"  # Strukturierten Fehler zurueckgeben (kein 500)
    PARTIAL         = "PARTIAL"         # Teilweise Daten mit Warnung zurueckgeben


class QueryFehlerKlasse(str, Enum):
    """Klassifikation des Query-Fehlers."""
    TIMEOUT         = "TIMEOUT"
    DB_UNAVAILABLE  = "DB_UNAVAILABLE"
    SCHEMA_FEHLER   = "SCHEMA_FEHLER"
    BERECHNUNG      = "BERECHNUNG"
    UNBEKANNT       = "UNBEKANNT"


class FallbackPrioritaet(str, Enum):
    """Reihenfolge wenn mehrere Regeln matchen."""
    KRITISCH = "KRITISCH"   # Immer anwenden (z.B. Finance-Pflichtfelder)
    HOCH     = "HOCH"
    MITTEL   = "MITTEL"
    NIEDRIG  = "NIEDRIG"


# ---------------------------------------------------------------------------
# Fallback-Regel
# ---------------------------------------------------------------------------

@dataclass
class QueryFallbackRegel:
    """
    Regel: Bei Fehlerklasse X in Domain Y -> Fallback-Typ Z anwenden.
    """
    regel_id: str
    domain: str                          # "finance", "agrar", "compliance", "workflow"
    query_name: str                      # Spezifischer Query oder "*" fuer alle
    fehler_klasse: QueryFehlerKlasse
    fallback_typ: QueryFallbackTyp
    beschreibung: str
    prioritaet: FallbackPrioritaet = FallbackPrioritaet.MITTEL
    # Safe-Default-Wert (wenn fallback_typ == SAFE_DEFAULT)
    safe_default: Any = None
    # Cache-TTL in Sekunden (wenn fallback_typ == CACHE)
    cache_ttl_sekunden: int = 300
    aktiv: bool = True

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "domain": self.domain,
            "query_name": self.query_name,
            "fehler_klasse": self.fehler_klasse.value,
            "fallback_typ": self.fallback_typ.value,
            "beschreibung": self.beschreibung,
            "prioritaet": self.prioritaet.value,
            "cache_ttl_sekunden": self.cache_ttl_sekunden,
            "aktiv": self.aktiv,
        }


# ---------------------------------------------------------------------------
# Fallback-Ergebnis
# ---------------------------------------------------------------------------

@dataclass
class QueryFallbackResult:
    """
    Ergebnis der Fallback-Auswertung.
    Beschreibt was das System bei einem Query-Fehler tun soll.
    """
    fallback_typ: QueryFallbackTyp
    angewendete_regel_id: str | None
    domain: str
    query_name: str
    fehler_klasse: QueryFehlerKlasse
    empfohlener_http_status: int
    meldung: str
    safe_default_wert: Any = None
    cache_ttl_sekunden: int = 0
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "fallback_typ": self.fallback_typ.value,
            "angewendete_regel_id": self.angewendete_regel_id,
            "domain": self.domain,
            "query_name": self.query_name,
            "fehler_klasse": self.fehler_klasse.value,
            "empfohlener_http_status": self.empfohlener_http_status,
            "meldung": self.meldung,
            "safe_default_wert": self.safe_default_wert,
            "cache_ttl_sekunden": self.cache_ttl_sekunden,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Prioritaets-Rang
# ---------------------------------------------------------------------------

_PRIO_RANG: dict[FallbackPrioritaet, int] = {
    FallbackPrioritaet.KRITISCH: 4,
    FallbackPrioritaet.HOCH:     3,
    FallbackPrioritaet.MITTEL:   2,
    FallbackPrioritaet.NIEDRIG:  1,
}

_HTTP_STATUS: dict[QueryFallbackTyp, int] = {
    QueryFallbackTyp.CACHE:          200,
    QueryFallbackTyp.SAFE_DEFAULT:   200,
    QueryFallbackTyp.PARTIAL:        206,
    QueryFallbackTyp.ERROR_RESPONSE: 503,
}


# ---------------------------------------------------------------------------
# evaluate_fallback
# ---------------------------------------------------------------------------

def evaluate_fallback(
    fehler_klasse: QueryFehlerKlasse,
    domain: str,
    query_name: str,
    regeln: list[QueryFallbackRegel],
) -> QueryFallbackResult:
    """
    Bestimmt den anzuwendenden Fallback fuer einen fehlgeschlagenen Query.

    Matching-Logik:
    1. Aktive Regeln fuer die Fehlerklasse filtern
    2. Regeln die zur Domain passen (exakt oder "*")
    3. Regeln die zum query_name passen (exakt oder "*")
    4. Hoechste Prioritaet gewinnt

    Kein Match -> ERROR_RESPONSE mit HTTP 503 (keine 500er).

    Args:
        fehler_klasse: Klassifikation des aufgetretenen Fehlers.
        domain: Query-Domain (z.B. "finance", "agrar").
        query_name: Name des fehlgeschlagenen Queries.
        regeln: Liste der Fallback-Regeln.

    Returns:
        QueryFallbackResult mit empfohlenem Fallback.
    """
    kandidaten = [
        r for r in regeln
        if r.aktiv
        and r.fehler_klasse == fehler_klasse
        and (r.domain == domain or r.domain == "*")
        and (r.query_name == query_name or r.query_name == "*")
    ]

    if not kandidaten:
        return QueryFallbackResult(
            fallback_typ=QueryFallbackTyp.ERROR_RESPONSE,
            angewendete_regel_id=None,
            domain=domain,
            query_name=query_name,
            fehler_klasse=fehler_klasse,
            empfohlener_http_status=503,
            meldung=(
                f"Kein Fallback fuer '{domain}.{query_name}' "
                f"({fehler_klasse.value}) konfiguriert. Service degraded."
            ),
        )

    # Hoechste Prioritaet gewinnt; bei Gleichstand: erste in der Liste
    gewinner = max(kandidaten, key=lambda r: _PRIO_RANG[r.prioritaet])

    return QueryFallbackResult(
        fallback_typ=gewinner.fallback_typ,
        angewendete_regel_id=gewinner.regel_id,
        domain=domain,
        query_name=query_name,
        fehler_klasse=fehler_klasse,
        empfohlener_http_status=_HTTP_STATUS[gewinner.fallback_typ],
        meldung=gewinner.beschreibung,
        safe_default_wert=gewinner.safe_default,
        cache_ttl_sekunden=gewinner.cache_ttl_sekunden,
    )


# ---------------------------------------------------------------------------
# Default-Fallback-Regeln
# ---------------------------------------------------------------------------

def get_default_fallback_rules() -> list[QueryFallbackRegel]:
    """
    Liefert Default-Fallback-Regeln fuer Finance, Agrar, Compliance, Workflow.

    Deckt die haeufigsten Fehlermuster ab, die zu HTTP-500-Antworten
    fuehren koennen (Timeouts, DB-Unavailability, Berechnungsfehler).
    """
    return [
        # --- Finance ---
        QueryFallbackRegel(
            regel_id="FB-FIN-001",
            domain="finance",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.TIMEOUT,
            fallback_typ=QueryFallbackTyp.CACHE,
            beschreibung="Finance-Queries: Bei Timeout letzten Cache zurueckgeben",
            prioritaet=FallbackPrioritaet.HOCH,
            cache_ttl_sekunden=300,
        ),
        QueryFallbackRegel(
            regel_id="FB-FIN-002",
            domain="finance",
            query_name="kpis",
            fehler_klasse=QueryFehlerKlasse.DB_UNAVAILABLE,
            fallback_typ=QueryFallbackTyp.SAFE_DEFAULT,
            beschreibung="Finance-KPIs: Bei DB-Ausfall leeres KPI-Objekt zurueckgeben",
            prioritaet=FallbackPrioritaet.KRITISCH,
            safe_default={"status": "unavailable", "kpis": {}},
        ),
        QueryFallbackRegel(
            regel_id="FB-FIN-003",
            domain="finance",
            query_name="timeseries",
            fehler_klasse=QueryFehlerKlasse.DB_UNAVAILABLE,
            fallback_typ=QueryFallbackTyp.SAFE_DEFAULT,
            beschreibung="Finance-Timeseries: Bei DB-Ausfall leere Zeitreihe zurueckgeben",
            prioritaet=FallbackPrioritaet.KRITISCH,
            safe_default={"status": "unavailable", "data": []},
        ),
        QueryFallbackRegel(
            regel_id="FB-FIN-004",
            domain="finance",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.BERECHNUNG,
            fallback_typ=QueryFallbackTyp.PARTIAL,
            beschreibung="Finance: Berechnungsfehler -> Teilantwort mit Warnung",
            prioritaet=FallbackPrioritaet.MITTEL,
        ),
        # --- Agrar ---
        QueryFallbackRegel(
            regel_id="FB-AGR-001",
            domain="agrar",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.TIMEOUT,
            fallback_typ=QueryFallbackTyp.CACHE,
            beschreibung="Agrar-Queries: Bei Timeout letzten Cache zurueckgeben",
            prioritaet=FallbackPrioritaet.HOCH,
            cache_ttl_sekunden=120,
        ),
        QueryFallbackRegel(
            regel_id="FB-AGR-002",
            domain="agrar",
            query_name="settlement",
            fehler_klasse=QueryFehlerKlasse.DB_UNAVAILABLE,
            fallback_typ=QueryFallbackTyp.ERROR_RESPONSE,
            beschreibung="Agrar-Settlement: Bei DB-Ausfall strukturierten Fehler zurueckgeben",
            prioritaet=FallbackPrioritaet.KRITISCH,
        ),
        QueryFallbackRegel(
            regel_id="FB-AGR-003",
            domain="agrar",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.SCHEMA_FEHLER,
            fallback_typ=QueryFallbackTyp.ERROR_RESPONSE,
            beschreibung="Agrar: Schema-Fehler -> Klarer Fehler statt 500",
            prioritaet=FallbackPrioritaet.HOCH,
        ),
        # --- Compliance ---
        QueryFallbackRegel(
            regel_id="FB-COM-001",
            domain="compliance",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.TIMEOUT,
            fallback_typ=QueryFallbackTyp.CACHE,
            beschreibung="Compliance: Bei Timeout Cache bevorzugen (Daten aendern sich selten)",
            prioritaet=FallbackPrioritaet.HOCH,
            cache_ttl_sekunden=3600,
        ),
        QueryFallbackRegel(
            regel_id="FB-COM-002",
            domain="compliance",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.DB_UNAVAILABLE,
            fallback_typ=QueryFallbackTyp.CACHE,
            beschreibung="Compliance: Bei DB-Ausfall auch Cache akzeptieren",
            prioritaet=FallbackPrioritaet.MITTEL,
            cache_ttl_sekunden=3600,
        ),
        # --- Workflow ---
        QueryFallbackRegel(
            regel_id="FB-WF-001",
            domain="workflow",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.TIMEOUT,
            fallback_typ=QueryFallbackTyp.SAFE_DEFAULT,
            beschreibung="Workflow: Bei Timeout sicheren Standardzustand zurueckgeben",
            prioritaet=FallbackPrioritaet.HOCH,
            safe_default={"status": "unknown", "instanzen": []},
        ),
        QueryFallbackRegel(
            regel_id="FB-WF-002",
            domain="workflow",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.UNBEKANNT,
            fallback_typ=QueryFallbackTyp.ERROR_RESPONSE,
            beschreibung="Workflow: Unbekannte Fehler -> strukturierter 503 statt 500",
            prioritaet=FallbackPrioritaet.NIEDRIG,
        ),
        # --- Global-Catch-all ---
        QueryFallbackRegel(
            regel_id="FB-GLOBAL-001",
            domain="*",
            query_name="*",
            fehler_klasse=QueryFehlerKlasse.UNBEKANNT,
            fallback_typ=QueryFallbackTyp.ERROR_RESPONSE,
            beschreibung="Global: Alle unbekannten Fehler werden als strukturierter 503 zurueckgegeben",
            prioritaet=FallbackPrioritaet.NIEDRIG,
        ),
    ]
