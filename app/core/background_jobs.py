"""
background_jobs.py — Queue-basierte Hintergrundjobs (Wave 33, Gap 036)

Job-Queue-Contracts fuer schwere Prozesse.
Kein echter Job-Runner im Core-Layer — Contracts sind Worker-agnostisch
(Celery, ARQ, NATS JetStream, etc.).

Gap 036: Queue-basierte Hintergrundjobs fuer schwere Prozesse — p95 UI-Response <300ms.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class JobTyp(str, Enum):
    """Fachliche Job-Typen fuer VALEO-Prozesse."""
    SETTLEMENT_BATCH        = "SETTLEMENT_BATCH"         # Massen-Abrechnung
    DATENQUALITAET_SCAN     = "DATENQUALITAET_SCAN"      # DQ-Regelausfuehrung
    SNAPSHOT_REBUILD        = "SNAPSHOT_REBUILD"          # Dashboard-Snapshots neu bauen
    REPORT_GENERATION       = "REPORT_GENERATION"         # Bericht erzeugen (PDF, XLSX)
    EDI_EXPORT              = "EDI_EXPORT"                # EDI-Nachricht generieren + senden
    INTRASTAT_MELDUNG       = "INTRASTAT_MELDUNG"         # Intrastat-Meldung aufbereiten
    BULK_IMPORT             = "BULK_IMPORT"               # Grosser Datenimport
    AUDIT_EXPORT            = "AUDIT_EXPORT"              # GoBD-Exportpaket erzeugen
    EMAIL_KAMPAGNE          = "EMAIL_KAMPAGNE"            # Massen-E-Mail
    PREIS_AKTUALISIERUNG    = "PREIS_AKTUALISIERUNG"      # Marktpreise aktualisieren


class JobStatus(str, Enum):
    """Lebenszyklus-Status eines Jobs."""
    PENDING    = "PENDING"     # In Queue, noch nicht gestartet
    RUNNING    = "RUNNING"     # Wird ausgefuehrt
    COMPLETED  = "COMPLETED"   # Erfolgreich abgeschlossen
    FAILED     = "FAILED"      # Fehlgeschlagen
    CANCELLED  = "CANCELLED"   # Abgebrochen (manuell oder Timeout)
    RETRYING   = "RETRYING"    # Wird erneut versucht


class JobPrioritaet(str, Enum):
    """Ausfuehrungs-Prioritaet in der Queue."""
    KRITISCH = "KRITISCH"   # Sofort (z.B. Settlement-Freigabe-Deadline)
    HOCH     = "HOCH"       # Innerhalb von Minuten
    MITTEL   = "MITTEL"     # Innerhalb von Stunden
    NIEDRIG  = "NIEDRIG"    # Best-Effort / Nacht-Batch


class WorkerKlasse(str, Enum):
    """Welcher Worker-Pool soll den Job verarbeiten."""
    FINANCE    = "FINANCE"      # Finance-Worker (Buchungen, Settlement)
    AGRAR      = "AGRAR"        # Agrar-Worker (Qualitaet, Kampagne)
    REPORTING  = "REPORTING"    # Report-Worker (PDF, Export)
    GENERAL    = "GENERAL"      # Allgemeiner Worker


# ---------------------------------------------------------------------------
# Background-Job
# ---------------------------------------------------------------------------

@dataclass
class BackgroundJob:
    """
    Repr. eines Hintergrund-Jobs mit Typ, Status und Ergebnis.

    Kein Job-Runner-Coupling — nur Contract. Worker bindet gegen dieses Modell.
    """
    job_id: str
    typ: JobTyp
    status: JobStatus
    prioritaet: JobPrioritaet
    angefordert_von: str            # User-/System-ID
    erstellt_am: datetime
    parameter: dict[str, Any] = field(default_factory=dict)
    gestartet_am: datetime | None = None
    abgeschlossen_am: datetime | None = None
    fehler_meldung: str = ""
    ergebnis_summary: str = ""
    retry_count: int = 0
    max_retries: int = 3
    tenant_id: str = ""
    schema_version: int = 1

    @property
    def laufzeit_sekunden(self) -> float | None:
        """Laufzeit in Sekunden wenn abgeschlossen."""
        if self.gestartet_am is None or self.abgeschlossen_am is None:
            return None
        return (self.abgeschlossen_am - self.gestartet_am).total_seconds()

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.status in {
            JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED
        }

    def as_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "typ": self.typ.value,
            "status": self.status.value,
            "prioritaet": self.prioritaet.value,
            "angefordert_von": self.angefordert_von,
            "erstellt_am": self.erstellt_am.isoformat(),
            "gestartet_am": self.gestartet_am.isoformat() if self.gestartet_am else None,
            "abgeschlossen_am": self.abgeschlossen_am.isoformat() if self.abgeschlossen_am else None,
            "laufzeit_sekunden": self.laufzeit_sekunden,
            "fehler_meldung": self.fehler_meldung,
            "ergebnis_summary": self.ergebnis_summary,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "tenant_id": self.tenant_id,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Job-Queue-Entry
# ---------------------------------------------------------------------------

@dataclass
class JobQueueEntry:
    """Eintrag in der In-Memory-Queue (Prioritaets-sortiert)."""
    job: BackgroundJob
    eingestellt_am: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def prioritaet_rang(self) -> int:
        return _PRIO_RANG[self.job.prioritaet]


_PRIO_RANG: dict[JobPrioritaet, int] = {
    JobPrioritaet.KRITISCH: 4,
    JobPrioritaet.HOCH:     3,
    JobPrioritaet.MITTEL:   2,
    JobPrioritaet.NIEDRIG:  1,
}


# ---------------------------------------------------------------------------
# Job-Queue
# ---------------------------------------------------------------------------

@dataclass
class JobQueue:
    """
    Einfache In-Memory-Queue fuer BackgroundJobs.

    Prioritaet gewinnt; bei Gleichstand FIFO (eingestellt_am).
    Im Produktivbetrieb wird diese Logik durch echten Job-Runner (Celery/ARQ)
    abgeloest — der Contract bleibt identisch.
    """
    _eintraege: list[JobQueueEntry] = field(default_factory=list)
    schema_version: int = 1

    def enqueue(self, job: BackgroundJob) -> str:
        """Stellt einen Job in die Queue und gibt die job_id zurueck."""
        eintrag = JobQueueEntry(job=job)
        self._eintraege.append(eintrag)
        return job.job_id

    def dequeue(self) -> BackgroundJob | None:
        """
        Gibt den naechsten Job (hoechste Prioritaet, aeltester zuerst) zurueck
        und entfernt ihn aus der Queue. None wenn Queue leer.
        """
        if not self._eintraege:
            return None
        # Sortiere: hoechste Prio zuerst; bei Gleichstand frueheste Zeit
        self._eintraege.sort(
            key=lambda e: (-e.prioritaet_rang, e.eingestellt_am)
        )
        eintrag = self._eintraege.pop(0)
        eintrag.job.status = JobStatus.RUNNING
        eintrag.job.gestartet_am = datetime.now(timezone.utc)
        return eintrag.job

    def cancel(self, job_id: str) -> bool:
        """Bricht einen PENDING-Job ab. Gibt True zurueck wenn erfolgreich."""
        for eintrag in self._eintraege:
            if eintrag.job.job_id == job_id:
                eintrag.job.status = JobStatus.CANCELLED
                eintrag.job.abgeschlossen_am = datetime.now(timezone.utc)
                self._eintraege.remove(eintrag)
                return True
        return False

    def pending_count(self) -> int:
        return len(self._eintraege)

    def by_typ(self, typ: JobTyp) -> list[BackgroundJob]:
        return [e.job for e in self._eintraege if e.job.typ == typ]

    def as_dict(self) -> dict:
        return {
            "pending_count": self.pending_count(),
            "typen": list({e.job.typ.value for e in self._eintraege}),
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Job-Routing
# ---------------------------------------------------------------------------

@dataclass
class JobRoutingResult:
    """Ergebnis der Job-Routing-Evaluierung."""
    job_typ: JobTyp
    worker_klasse: WorkerKlasse
    prioritaet: JobPrioritaet
    timeout_sekunden: int
    meldung: str
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "job_typ": self.job_typ.value,
            "worker_klasse": self.worker_klasse.value,
            "prioritaet": self.prioritaet.value,
            "timeout_sekunden": self.timeout_sekunden,
            "meldung": self.meldung,
            "schema_version": self.schema_version,
        }


# Routing-Tabelle: JobTyp -> (WorkerKlasse, Prioritaet, Timeout)
_JOB_ROUTING: dict[JobTyp, tuple[WorkerKlasse, JobPrioritaet, int]] = {
    JobTyp.SETTLEMENT_BATCH:        (WorkerKlasse.FINANCE,   JobPrioritaet.HOCH,    1800),
    JobTyp.DATENQUALITAET_SCAN:     (WorkerKlasse.GENERAL,   JobPrioritaet.MITTEL,   600),
    JobTyp.SNAPSHOT_REBUILD:        (WorkerKlasse.GENERAL,   JobPrioritaet.MITTEL,   300),
    JobTyp.REPORT_GENERATION:       (WorkerKlasse.REPORTING, JobPrioritaet.MITTEL,   600),
    JobTyp.EDI_EXPORT:              (WorkerKlasse.GENERAL,   JobPrioritaet.HOCH,     300),
    JobTyp.INTRASTAT_MELDUNG:       (WorkerKlasse.FINANCE,   JobPrioritaet.HOCH,     900),
    JobTyp.BULK_IMPORT:             (WorkerKlasse.AGRAR,     JobPrioritaet.MITTEL,  3600),
    JobTyp.AUDIT_EXPORT:            (WorkerKlasse.FINANCE,   JobPrioritaet.NIEDRIG, 3600),
    JobTyp.EMAIL_KAMPAGNE:          (WorkerKlasse.GENERAL,   JobPrioritaet.NIEDRIG,  900),
    JobTyp.PREIS_AKTUALISIERUNG:    (WorkerKlasse.AGRAR,     JobPrioritaet.KRITISCH,  60),
}


def evaluate_job_routing(typ: JobTyp) -> JobRoutingResult:
    """
    Bestimmt deterministisch Worker-Klasse, Prioritaet und Timeout fuer einen Job-Typ.

    Args:
        typ: Der Job-Typ.

    Returns:
        JobRoutingResult mit Worker-Klasse, Prioritaet und Timeout.
    """
    if typ not in _JOB_ROUTING:
        return JobRoutingResult(
            job_typ=typ,
            worker_klasse=WorkerKlasse.GENERAL,
            prioritaet=JobPrioritaet.NIEDRIG,
            timeout_sekunden=600,
            meldung=f"Kein Routing fuer '{typ.value}' konfiguriert — GENERAL-Fallback.",
        )
    worker, prio, timeout = _JOB_ROUTING[typ]
    return JobRoutingResult(
        job_typ=typ,
        worker_klasse=worker,
        prioritaet=prio,
        timeout_sekunden=timeout,
        meldung=f"{typ.value} -> {worker.value} ({prio.value}, {timeout}s).",
    )


# ---------------------------------------------------------------------------
# Job-Definition (Katalog-Eintrag)
# ---------------------------------------------------------------------------

@dataclass
class JobDefinition:
    """Katalog-Eintrag fuer einen Job-Typ mit Routing-Informationen."""
    typ: JobTyp
    beschreibung: str
    worker_klasse: WorkerKlasse
    standard_prioritaet: JobPrioritaet
    timeout_sekunden: int
    idempotent: bool                 # Sicher retry-bar ohne Duplikate?
    beispiel_parameter: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "typ": self.typ.value,
            "beschreibung": self.beschreibung,
            "worker_klasse": self.worker_klasse.value,
            "standard_prioritaet": self.standard_prioritaet.value,
            "timeout_sekunden": self.timeout_sekunden,
            "idempotent": self.idempotent,
        }


def get_default_job_types() -> list[JobDefinition]:
    """Liefert den Default-Katalog aller unterstuetzten Job-Typen."""
    return [
        JobDefinition(
            typ=JobTyp.SETTLEMENT_BATCH,
            beschreibung="Massenabrechnung einer Agrar-Kampagne (Settlement-Batch)",
            worker_klasse=WorkerKlasse.FINANCE,
            standard_prioritaet=JobPrioritaet.HOCH,
            timeout_sekunden=1800,
            idempotent=True,
            beispiel_parameter={"kampagne_id": "ERNTE_2025", "limit": 500},
        ),
        JobDefinition(
            typ=JobTyp.DATENQUALITAET_SCAN,
            beschreibung="DQ-Regelausfuehrung fuer eine Domain (Dublettencheck, Pflichtfelder)",
            worker_klasse=WorkerKlasse.GENERAL,
            standard_prioritaet=JobPrioritaet.MITTEL,
            timeout_sekunden=600,
            idempotent=True,
            beispiel_parameter={"domain": "agrar", "ruleset_id": "RS-WIEGESCHEIN"},
        ),
        JobDefinition(
            typ=JobTyp.SNAPSHOT_REBUILD,
            beschreibung="Dashboard-Read-Model-Snapshots neu aufbauen",
            worker_klasse=WorkerKlasse.GENERAL,
            standard_prioritaet=JobPrioritaet.MITTEL,
            timeout_sekunden=300,
            idempotent=True,
            beispiel_parameter={"snapshot_typ": "FINANCE_KPIS"},
        ),
        JobDefinition(
            typ=JobTyp.REPORT_GENERATION,
            beschreibung="Bericht generieren (PDF, XLSX, CSV)",
            worker_klasse=WorkerKlasse.REPORTING,
            standard_prioritaet=JobPrioritaet.MITTEL,
            timeout_sekunden=600,
            idempotent=False,
            beispiel_parameter={"report_typ": "INTRASTAT", "periode": "2025-03"},
        ),
        JobDefinition(
            typ=JobTyp.EDI_EXPORT,
            beschreibung="EDI-Nachricht generieren und an Empfaenger senden",
            worker_klasse=WorkerKlasse.GENERAL,
            standard_prioritaet=JobPrioritaet.HOCH,
            timeout_sekunden=300,
            idempotent=False,
            beispiel_parameter={"dokument_typ": "ORDERS", "empfaenger_id": "LFS-001"},
        ),
        JobDefinition(
            typ=JobTyp.INTRASTAT_MELDUNG,
            beschreibung="Intrastat-Meldung fuer Berichtsperiode aufbereiten",
            worker_klasse=WorkerKlasse.FINANCE,
            standard_prioritaet=JobPrioritaet.HOCH,
            timeout_sekunden=900,
            idempotent=True,
            beispiel_parameter={"periode": "2025-03", "richtung": "VERSENDUNG"},
        ),
        JobDefinition(
            typ=JobTyp.BULK_IMPORT,
            beschreibung="Grosser Datenimport (Stammdaten, Wiegescheine, Vertraege)",
            worker_klasse=WorkerKlasse.AGRAR,
            standard_prioritaet=JobPrioritaet.MITTEL,
            timeout_sekunden=3600,
            idempotent=True,
            beispiel_parameter={"domain": "agrar", "datei": "wiegescheine_2025.csv"},
        ),
        JobDefinition(
            typ=JobTyp.AUDIT_EXPORT,
            beschreibung="GoBD-Exportpaket fuer Betriebspruefung erzeugen",
            worker_klasse=WorkerKlasse.FINANCE,
            standard_prioritaet=JobPrioritaet.NIEDRIG,
            timeout_sekunden=3600,
            idempotent=True,
            beispiel_parameter={"jahr": 2025, "format": "GOBD_XML"},
        ),
        JobDefinition(
            typ=JobTyp.EMAIL_KAMPAGNE,
            beschreibung="Massen-E-Mail (Rundschreiben, Abrechnungsversand)",
            worker_klasse=WorkerKlasse.GENERAL,
            standard_prioritaet=JobPrioritaet.NIEDRIG,
            timeout_sekunden=900,
            idempotent=False,
            beispiel_parameter={"vorlage_id": "ABRECHNUNG_SAISONAL", "empfaenger_count": 250},
        ),
        JobDefinition(
            typ=JobTyp.PREIS_AKTUALISIERUNG,
            beschreibung="Marktpreise von Datenanbieter aktualisieren (MATIF, LME)",
            worker_klasse=WorkerKlasse.AGRAR,
            standard_prioritaet=JobPrioritaet.KRITISCH,
            timeout_sekunden=60,
            idempotent=True,
            beispiel_parameter={"markt": "MATIF", "produkt": "RAPS"},
        ),
    ]


# ---------------------------------------------------------------------------
# Job-Enqueue-Request/-Result
# ---------------------------------------------------------------------------

@dataclass
class JobEnqueueRequest:
    """Request zum Einreihen eines Jobs."""
    typ: JobTyp
    angefordert_von: str
    parameter: dict[str, Any] = field(default_factory=dict)
    prioritaet_override: JobPrioritaet | None = None
    tenant_id: str = ""

    def as_dict(self) -> dict:
        return {
            "typ": self.typ.value,
            "angefordert_von": self.angefordert_von,
            "prioritaet_override": (
                self.prioritaet_override.value if self.prioritaet_override else None
            ),
            "tenant_id": self.tenant_id,
        }


@dataclass
class JobEnqueueResult:
    """Ergebnis des Job-Einreihens."""
    job_id: str
    typ: JobTyp
    prioritaet: JobPrioritaet
    worker_klasse: WorkerKlasse
    meldung: str
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "typ": self.typ.value,
            "prioritaet": self.prioritaet.value,
            "worker_klasse": self.worker_klasse.value,
            "meldung": self.meldung,
            "schema_version": self.schema_version,
        }


def create_job_from_request(req: JobEnqueueRequest) -> tuple[BackgroundJob, JobRoutingResult]:
    """
    Erzeugt einen BackgroundJob aus einem JobEnqueueRequest.

    Wendet Routing an, generiert UUID und setzt Status PENDING.

    Returns:
        (BackgroundJob, JobRoutingResult)
    """
    routing = evaluate_job_routing(req.typ)
    prioritaet = req.prioritaet_override or routing.prioritaet
    job = BackgroundJob(
        job_id=str(uuid.uuid4()),
        typ=req.typ,
        status=JobStatus.PENDING,
        prioritaet=prioritaet,
        angefordert_von=req.angefordert_von,
        erstellt_am=datetime.now(timezone.utc),
        parameter=req.parameter,
        tenant_id=req.tenant_id,
    )
    return job, routing
