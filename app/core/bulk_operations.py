"""
bulk_operations.py — API-Bulk-Operationen-Contracts (Wave 33, Gap 034)

Typisierte Batch-Anfragen mit Domain-spezifischen Limits, Validierung
und strukturierten Ergebnissen — 3x Throughput bei Batch-Import.

Gap 034: API-Bulk-Operationen fuer Massenvorgaenge.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BulkOperationTyp(str, Enum):
    """Art der Bulk-Operation."""
    CREATE   = "CREATE"
    UPDATE   = "UPDATE"
    DELETE   = "DELETE"
    VALIDATE = "VALIDATE"    # Nur validieren, nicht ausfuehren
    UPSERT   = "UPSERT"      # Create-or-update


class BulkItemStatus(str, Enum):
    """Status eines einzelnen Items in der Batch-Antwort."""
    PENDING  = "PENDING"
    SUCCESS  = "SUCCESS"
    FEHLER   = "FEHLER"
    SKIP     = "SKIP"        # Uebersprungen (z.B. unveraendert)


class BulkFehlerCode(str, Enum):
    """Klassifikation von Bulk-Item-Fehlern."""
    VALIDIERUNG     = "VALIDIERUNG"     # Datenvalidierungsfehler
    LIMIT_ERREICHT  = "LIMIT_ERREICHT"  # Batch-Limit ueberschritten
    DUPLIKAT        = "DUPLIKAT"        # Duplikaterkennung
    REFERENZ_FEHLT  = "REFERENZ_FEHLT"  # Fremdschluessel nicht gefunden
    NICHT_GEFUNDEN  = "NICHT_GEFUNDEN"  # Item nicht gefunden (UPDATE/DELETE)
    UNBEKANNT       = "UNBEKANNT"


# ---------------------------------------------------------------------------
# Bulk-Limits (Domain-spezifisch)
# ---------------------------------------------------------------------------

@dataclass
class BulkLimit:
    """
    Konfigurierbare Limits fuer Bulk-Operationen einer Domain.
    """
    domain: str
    max_items_pro_request: int       # Maximale Items pro Batch-Request
    max_requests_pro_minute: int     # Rate-Limit fuer Batch-Requests
    max_payload_bytes: int           # Maximale Payload-Groesse in Bytes
    erlaubte_operationen: list[BulkOperationTyp]
    beschreibung: str

    def as_dict(self) -> dict:
        return {
            "domain": self.domain,
            "max_items_pro_request": self.max_items_pro_request,
            "max_requests_pro_minute": self.max_requests_pro_minute,
            "max_payload_bytes": self.max_payload_bytes,
            "erlaubte_operationen": [op.value for op in self.erlaubte_operationen],
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Bulk-Item
# ---------------------------------------------------------------------------

@dataclass
class BulkItem:
    """Ein einzelnes Item innerhalb einer Bulk-Anfrage."""
    item_id: str                     # Lokale Referenz-ID (aus Request)
    payload: dict[str, Any]
    status: BulkItemStatus = BulkItemStatus.PENDING
    fehler_code: BulkFehlerCode | None = None
    fehler_meldung: str = ""
    ergebnis_id: str | None = None   # Server-seitige ID nach CREATE/UPSERT

    def as_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "status": self.status.value,
            "fehler_code": self.fehler_code.value if self.fehler_code else None,
            "fehler_meldung": self.fehler_meldung,
            "ergebnis_id": self.ergebnis_id,
        }


# ---------------------------------------------------------------------------
# Bulk-Request
# ---------------------------------------------------------------------------

@dataclass
class BulkRequest:
    """
    Typisierte Bulk-Anfrage.

    Kapselt Operationstyp, Domain, Items und optionale Optionen.
    """
    operation_typ: BulkOperationTyp
    domain: str
    ressource: str                   # z.B. "kontrakte", "wiegescheine"
    items: list[BulkItem]
    trocken_lauf: bool = False       # Nur validieren, nicht persistieren
    stop_bei_erstem_fehler: bool = False
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "operation_typ": self.operation_typ.value,
            "domain": self.domain,
            "ressource": self.ressource,
            "item_count": len(self.items),
            "trocken_lauf": self.trocken_lauf,
            "stop_bei_erstem_fehler": self.stop_bei_erstem_fehler,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Bulk-Validation-Result
# ---------------------------------------------------------------------------

@dataclass
class BulkValidationResult:
    """Ergebnis der strukturellen Validierung einer BulkRequest."""
    gueltig: bool
    fehler: list[str]
    warnungen: list[str]
    item_count: int
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "gueltig": self.gueltig,
            "fehler": self.fehler,
            "warnungen": self.warnungen,
            "item_count": self.item_count,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Bulk-Result
# ---------------------------------------------------------------------------

@dataclass
class BulkResult:
    """
    Strukturiertes Ergebnis einer ausgefuehrten Bulk-Operation.
    """
    operation_typ: BulkOperationTyp
    domain: str
    ressource: str
    total: int
    success_count: int
    fehler_count: int
    skip_count: int
    items: list[BulkItem] = field(default_factory=list)
    trocken_lauf: bool = False
    abgebrochen: bool = False       # True wenn stop_bei_erstem_fehler griff
    schema_version: int = 1

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.success_count / self.total

    def as_dict(self) -> dict:
        return {
            "operation_typ": self.operation_typ.value,
            "domain": self.domain,
            "ressource": self.ressource,
            "total": self.total,
            "success_count": self.success_count,
            "fehler_count": self.fehler_count,
            "skip_count": self.skip_count,
            "success_rate": round(self.success_rate, 4),
            "trocken_lauf": self.trocken_lauf,
            "abgebrochen": self.abgebrochen,
            "items": [i.as_dict() for i in self.items],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# validate_bulk_request
# ---------------------------------------------------------------------------

def validate_bulk_request(
    request: BulkRequest,
    limit: BulkLimit | None = None,
) -> BulkValidationResult:
    """
    Validiert eine BulkRequest strukturell gegen optionale Domain-Limits.

    Prueft:
    - Items vorhanden
    - Operation in Domain erlaubt (falls limit angegeben)
    - item_count <= max_items_pro_request
    - Jedes Item hat item_id und payload

    Args:
        request: Die zu pruefende BulkRequest.
        limit: Optionale Domain-Limit-Konfiguration.

    Returns:
        BulkValidationResult.
    """
    fehler: list[str] = []
    warnungen: list[str] = []

    if not request.items:
        fehler.append("Keine Items in der Bulk-Anfrage.")

    if limit is not None:
        # Operation erlaubt?
        if request.operation_typ not in limit.erlaubte_operationen:
            fehler.append(
                f"Operation '{request.operation_typ.value}' ist fuer Domain "
                f"'{request.domain}' nicht erlaubt. "
                f"Erlaubt: {[op.value for op in limit.erlaubte_operationen]}"
            )
        # Batch-Groesse?
        if len(request.items) > limit.max_items_pro_request:
            fehler.append(
                f"Zu viele Items: {len(request.items)} > "
                f"Limit {limit.max_items_pro_request} fuer Domain '{request.domain}'."
            )
        # Warnung wenn nah am Limit
        elif len(request.items) > limit.max_items_pro_request * 0.9:
            warnungen.append(
                f"Item-Count {len(request.items)} naehert sich dem Limit "
                f"{limit.max_items_pro_request} (>90%)."
            )

    # Item-Qualitaet
    fehlende_ids = [
        str(i) for i, item in enumerate(request.items)
        if not item.item_id or not item.item_id.strip()
    ]
    if fehlende_ids:
        fehler.append(f"Items ohne item_id an Position(en): {fehlende_ids[:5]}")

    leere_payloads = [
        item.item_id for item in request.items
        if not item.payload
    ]
    if leere_payloads:
        fehler.append(f"Items mit leerem Payload: {leere_payloads[:5]}")

    return BulkValidationResult(
        gueltig=len(fehler) == 0,
        fehler=fehler,
        warnungen=warnungen,
        item_count=len(request.items),
    )


# ---------------------------------------------------------------------------
# Default-Bulk-Limits
# ---------------------------------------------------------------------------

def get_default_bulk_limits() -> list[BulkLimit]:
    """
    Liefert Default-Bulk-Limits fuer Finance, Agrar, Compliance, Workflow.

    Balanciert Throughput-Ziel (3x Batch-Import) mit Stabilitaetsschutz.
    """
    alle_ops = [
        BulkOperationTyp.CREATE,
        BulkOperationTyp.UPDATE,
        BulkOperationTyp.DELETE,
        BulkOperationTyp.VALIDATE,
        BulkOperationTyp.UPSERT,
    ]
    return [
        BulkLimit(
            domain="agrar",
            max_items_pro_request=500,
            max_requests_pro_minute=60,
            max_payload_bytes=5 * 1024 * 1024,   # 5 MB
            erlaubte_operationen=alle_ops,
            beschreibung="Agrar: Wiegescheine, Kontrakte, Qualitaets-Chargen im Batch",
        ),
        BulkLimit(
            domain="finance",
            max_items_pro_request=200,
            max_requests_pro_minute=30,
            max_payload_bytes=2 * 1024 * 1024,   # 2 MB
            erlaubte_operationen=[
                BulkOperationTyp.CREATE,
                BulkOperationTyp.VALIDATE,
                BulkOperationTyp.UPSERT,
            ],
            beschreibung="Finance: Rechnungen, Buchungssaetze — kein Massen-DELETE",
        ),
        BulkLimit(
            domain="compliance",
            max_items_pro_request=100,
            max_requests_pro_minute=20,
            max_payload_bytes=1 * 1024 * 1024,   # 1 MB
            erlaubte_operationen=[
                BulkOperationTyp.CREATE,
                BulkOperationTyp.UPDATE,
                BulkOperationTyp.VALIDATE,
            ],
            beschreibung="Compliance: Meldungen, Zertifikate — kein Massen-DELETE",
        ),
        BulkLimit(
            domain="workflow",
            max_items_pro_request=50,
            max_requests_pro_minute=10,
            max_payload_bytes=512 * 1024,         # 512 KB
            erlaubte_operationen=[
                BulkOperationTyp.CREATE,
                BulkOperationTyp.VALIDATE,
            ],
            beschreibung="Workflow: Instanz-Massenerstellung beschraenkt (Stabilitaet)",
        ),
        BulkLimit(
            domain="stammdaten",
            max_items_pro_request=1000,
            max_requests_pro_minute=20,
            max_payload_bytes=10 * 1024 * 1024,  # 10 MB
            erlaubte_operationen=alle_ops,
            beschreibung="Stammdaten: Artikel, Lieferanten, Kunden-Import gross",
        ),
    ]


def get_bulk_limit_by_domain(
    domain: str,
    limits: list[BulkLimit] | None = None,
) -> BulkLimit | None:
    """Gibt das BulkLimit fuer eine Domain zurueck (None wenn nicht konfiguriert)."""
    if limits is None:
        limits = get_default_bulk_limits()
    for lim in limits:
        if lim.domain == domain:
            return lim
    return None
