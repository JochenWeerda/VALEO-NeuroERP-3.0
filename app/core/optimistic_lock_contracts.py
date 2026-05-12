"""
Optimistic Concurrency Control (OCC) Contracts — Wave 20 AP2

Leichte, persistenzunabhaengige Versionskontrollen fuer konkurrierende
Bearbeitungssituationen (Gap 035: 0 stille Ueberschreibungen).

Einsatz:
- Settlement-Approval (Abrechnung wird parallel bearbeitet)
- Kontrakt-Preisaenderung (Mehrere Sachbearbeiter gleichzeitig)
- Beliebige Aggregat-Updates im Process Kernel

Integration: version_guard() wird in Command-Handler-Funktionen aufgerufen
BEVOR die eigentliche Zustandsaenderung stattfindet.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


LOCK_SCHEMA_VERSION = 1


class OptimisticLockError(Exception):
    """
    Wird geworfen, wenn ein Schreibvorgang mit einer veralteten Version kollidiert.

    HTTP-Semantik: 409 Conflict
    """

    def __init__(
        self,
        aggregate_type: str,
        aggregate_id: str,
        expected_version: int,
        actual_version: int,
        actor_id: str = "unknown",
    ) -> None:
        self.aggregate_type = aggregate_type
        self.aggregate_id = aggregate_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        self.actor_id = actor_id
        super().__init__(
            f"Optimistic-Lock-Konflikt: {aggregate_type}/{aggregate_id} "
            f"erwartet Version {expected_version}, aktuell Version {actual_version}. "
            f"Bitte Seite neu laden und Aenderung wiederholen."
        )

    def as_dict(self) -> dict:
        return {
            "error_code": "OPTIMISTIC_LOCK_CONFLICT",
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "expected_version": self.expected_version,
            "actual_version": self.actual_version,
            "actor_id": self.actor_id,
            "schema_version": LOCK_SCHEMA_VERSION,
        }


@dataclass
class VersionedAggregate:
    """
    Leichtes Wrapper-Objekt fuer versionierte Aggregates.

    Das version-Feld ist eine monoton steigende Ganzzahl.
    Jede erfolgreiche Zustandsaenderung erhoht die Version um 1.
    """

    aggregate_type: str
    aggregate_id: str
    version: int = 0
    last_modified_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    last_modified_by: str = "system"
    schema_version: int = LOCK_SCHEMA_VERSION

    def increment(self, actor_id: str = "system") -> "VersionedAggregate":
        """Erhoeht die Version um 1 und setzt Metadaten. Gibt self zurueck."""
        self.version += 1
        self.last_modified_at = datetime.now(timezone.utc).isoformat()
        self.last_modified_by = actor_id
        return self

    def as_dict(self) -> dict:
        return {
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "version": self.version,
            "last_modified_at": self.last_modified_at,
            "last_modified_by": self.last_modified_by,
            "schema_version": self.schema_version,
        }


def version_guard(
    current_version: int,
    expected_version: int,
    *,
    aggregate_type: str,
    aggregate_id: str,
    actor_id: str = "unknown",
) -> None:
    """
    Prüft ob expected_version der aktuellen Version entspricht.

    Wirft OptimisticLockError wenn nicht — muss VOR der Zustandsaenderung aufgerufen werden.

    Verwendung in Command-Handlern:
        version_guard(
            current_version=settlement.version,
            expected_version=request.expected_version,
            aggregate_type="Settlement",
            aggregate_id=settlement.id,
            actor_id=request.actor_id,
        )
    """
    if current_version != expected_version:
        raise OptimisticLockError(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            expected_version=expected_version,
            actual_version=current_version,
            actor_id=actor_id,
        )


@dataclass
class LockConflictRecord:
    """Audit-Eintrag fuer einen aufgetretenen Lock-Konflikt."""

    aggregate_type: str
    aggregate_id: str
    tenant_id: str
    actor_id: str
    expected_version: int
    actual_version: int
    detected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    schema_version: int = LOCK_SCHEMA_VERSION

    @classmethod
    def from_error(
        cls, error: OptimisticLockError, tenant_id: str
    ) -> "LockConflictRecord":
        return cls(
            aggregate_type=error.aggregate_type,
            aggregate_id=error.aggregate_id,
            tenant_id=tenant_id,
            actor_id=error.actor_id,
            expected_version=error.expected_version,
            actual_version=error.actual_version,
        )

    def as_dict(self) -> dict:
        return {
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "tenant_id": self.tenant_id,
            "actor_id": self.actor_id,
            "expected_version": self.expected_version,
            "actual_version": self.actual_version,
            "detected_at": self.detected_at,
            "schema_version": self.schema_version,
        }
