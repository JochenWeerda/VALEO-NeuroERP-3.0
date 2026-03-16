"""
Workflow Batch Processing Contracts — Wave 48
Batch-Job-Definitionen, Chunk-Verarbeitung, Fortschrittserfassung
und Fehlerbehandlung für Massenoperationen.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class BatchTyp(str, Enum):
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    VERARBEITUNG = "VERARBEITUNG"
    ABRECHNUNG = "ABRECHNUNG"
    ARCHIVIERUNG = "ARCHIVIERUNG"


class BatchStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    PAUSIERT = "PAUSIERT"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    TEILWEISE_ERFOLGREICH = "TEILWEISE_ERFOLGREICH"


class ChunkStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    ERFOLGREICH = "ERFOLGREICH"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    UEBERSPRUNGEN = "UEBERSPRUNGEN"


# ---------------------------------------------------------------------------
# Chunk
# ---------------------------------------------------------------------------

@dataclass
class BatchChunk:
    """Ein einzelner Verarbeitungs-Chunk innerhalb eines Batch-Jobs."""
    chunk_id: str
    batch_id: str
    chunk_nummer: int          # 1-basiert
    anzahl_datensaetze: int
    status: ChunkStatus
    fehlermeldung: str = ""
    verarbeitet_am: datetime | None = None

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.status in (
            ChunkStatus.ERFOLGREICH,
            ChunkStatus.FEHLGESCHLAGEN,
            ChunkStatus.UEBERSPRUNGEN,
        )

    @property
    def ist_erfolgreich(self) -> bool:
        return self.status == ChunkStatus.ERFOLGREICH

    def as_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "batch_id": self.batch_id,
            "chunk_nummer": self.chunk_nummer,
            "anzahl_datensaetze": self.anzahl_datensaetze,
            "status": self.status.value,
            "ist_abgeschlossen": self.ist_abgeschlossen,
            "ist_erfolgreich": self.ist_erfolgreich,
            "fehlermeldung": self.fehlermeldung,
            "verarbeitet_am": self.verarbeitet_am.isoformat() if self.verarbeitet_am else None,
        }


# ---------------------------------------------------------------------------
# Batch-Job
# ---------------------------------------------------------------------------

@dataclass
class BatchJob:
    """Definition und Laufzeitstatus eines Batch-Jobs."""
    batch_id: str
    batch_name: str
    batch_typ: BatchTyp
    tenant_id: str
    status: BatchStatus
    gesamt_datensaetze: int
    chunk_groesse: int
    erstellt_am: datetime
    chunks: list[BatchChunk] = field(default_factory=list)
    beschreibung: str = ""

    @property
    def gesamt_chunks(self) -> int:
        return len(self.chunks)

    @property
    def abgeschlossene_chunks(self) -> int:
        return sum(1 for c in self.chunks if c.ist_abgeschlossen)

    @property
    def erfolgreiche_chunks(self) -> int:
        return sum(1 for c in self.chunks if c.ist_erfolgreich)

    @property
    def fehlgeschlagene_chunks(self) -> int:
        return sum(1 for c in self.chunks if c.status == ChunkStatus.FEHLGESCHLAGEN)

    @property
    def verarbeitete_datensaetze(self) -> int:
        return sum(c.anzahl_datensaetze for c in self.chunks if c.ist_erfolgreich)

    @property
    def fortschritt_pct(self) -> float:
        """Fortschritt in Prozent (0–100) basierend auf abgeschlossenen Chunks."""
        if self.gesamt_chunks == 0:
            return 0.0
        return round(self.abgeschlossene_chunks / self.gesamt_chunks * 100, 2)

    @property
    def fehlerrate_pct(self) -> float:
        """Fehlerrate in Prozent basierend auf fehlgeschlagenen Chunks."""
        if self.gesamt_chunks == 0:
            return 0.0
        return round(self.fehlgeschlagene_chunks / self.gesamt_chunks * 100, 2)

    def as_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "batch_name": self.batch_name,
            "batch_typ": self.batch_typ.value,
            "tenant_id": self.tenant_id,
            "status": self.status.value,
            "gesamt_datensaetze": self.gesamt_datensaetze,
            "chunk_groesse": self.chunk_groesse,
            "erstellt_am": self.erstellt_am.isoformat(),
            "gesamt_chunks": self.gesamt_chunks,
            "abgeschlossene_chunks": self.abgeschlossene_chunks,
            "erfolgreiche_chunks": self.erfolgreiche_chunks,
            "fehlgeschlagene_chunks": self.fehlgeschlagene_chunks,
            "verarbeitete_datensaetze": self.verarbeitete_datensaetze,
            "fortschritt_pct": self.fortschritt_pct,
            "fehlerrate_pct": self.fehlerrate_pct,
            "beschreibung": self.beschreibung,
            "chunks": [c.as_dict() for c in self.chunks],
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def berechne_batch_status(job: BatchJob) -> BatchStatus:
    """
    Leitet den Batch-Status aus dem Chunk-Zustand ab.

    Logik:
    - Keine Chunks → AUSSTEHEND
    - Alle abgeschlossen, kein Fehler → ABGESCHLOSSEN
    - Alle abgeschlossen, einige Fehler → TEILWEISE_ERFOLGREICH
    - Alle abgeschlossen, nur Fehler → FEHLGESCHLAGEN
    - Mindestens einer LAUFEND → LAUFEND
    - Sonst → AUSSTEHEND
    """
    if not job.chunks:
        return BatchStatus.AUSSTEHEND

    laufend = any(c.status == ChunkStatus.LAUFEND for c in job.chunks)
    if laufend:
        return BatchStatus.LAUFEND

    alle_abgeschlossen = all(c.ist_abgeschlossen for c in job.chunks)
    if alle_abgeschlossen:
        if job.fehlgeschlagene_chunks == 0:
            return BatchStatus.ABGESCHLOSSEN
        if job.erfolgreiche_chunks == 0:
            return BatchStatus.FEHLGESCHLAGEN
        return BatchStatus.TEILWEISE_ERFOLGREICH

    return BatchStatus.AUSSTEHEND


def erstelle_chunks(
    batch_id: str,
    gesamt_datensaetze: int,
    chunk_groesse: int,
) -> list[BatchChunk]:
    """
    Erzeugt die Chunk-Liste für einen Batch-Job.

    Chunks werden 1-basiert nummeriert. Der letzte Chunk enthält die
    verbleibenden Datensätze (kann kleiner als chunk_groesse sein).
    """
    if gesamt_datensaetze <= 0 or chunk_groesse <= 0:
        return []

    chunks: list[BatchChunk] = []
    chunk_nummer = 1
    verbleibend = gesamt_datensaetze

    while verbleibend > 0:
        datensaetze = min(chunk_groesse, verbleibend)
        chunks.append(BatchChunk(
            chunk_id=f"{batch_id}-CHK-{chunk_nummer:03d}",
            batch_id=batch_id,
            chunk_nummer=chunk_nummer,
            anzahl_datensaetze=datensaetze,
            status=ChunkStatus.AUSSTEHEND,
        ))
        verbleibend -= datensaetze
        chunk_nummer += 1

    return chunks


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_batch_jobs(
    tenant_id: str = "TENANT-001",
) -> list[BatchJob]:
    """Gibt 4 Standard-Batch-Jobs zurück."""
    basis = datetime(2026, 3, 15, 6, 0)

    job1 = BatchJob(
        batch_id="BJ-001",
        batch_name="Jahreskontrakt-Import 2026",
        batch_typ=BatchTyp.IMPORT,
        tenant_id=tenant_id,
        status=BatchStatus.ABGESCHLOSSEN,
        gesamt_datensaetze=1500,
        chunk_groesse=250,
        erstellt_am=basis,
        beschreibung="Import aller Jahreskontrakte aus Vorsystem",
    )
    job1.chunks = [
        BatchChunk(f"BJ-001-CHK-{i:03d}", "BJ-001", i, 250, ChunkStatus.ERFOLGREICH,
                   verarbeitet_am=basis.replace(minute=i * 5))
        for i in range(1, 7)
    ]

    job2 = BatchJob(
        batch_id="BJ-002",
        batch_name="Settlement-Abrechnung März",
        batch_typ=BatchTyp.ABRECHNUNG,
        tenant_id=tenant_id,
        status=BatchStatus.TEILWEISE_ERFOLGREICH,
        gesamt_datensaetze=800,
        chunk_groesse=200,
        erstellt_am=basis.replace(hour=8),
        beschreibung="Monatliche Settlement-Abrechnung",
    )
    job2.chunks = [
        BatchChunk("BJ-002-CHK-001", "BJ-002", 1, 200, ChunkStatus.ERFOLGREICH),
        BatchChunk("BJ-002-CHK-002", "BJ-002", 2, 200, ChunkStatus.ERFOLGREICH),
        BatchChunk("BJ-002-CHK-003", "BJ-002", 3, 200, ChunkStatus.FEHLGESCHLAGEN,
                   fehlermeldung="Datenbankfehler bei Chunk 3"),
        BatchChunk("BJ-002-CHK-004", "BJ-002", 4, 200, ChunkStatus.UEBERSPRUNGEN),
    ]

    job3 = BatchJob(
        batch_id="BJ-003",
        batch_name="GoBD-Archivierung Q4 2025",
        batch_typ=BatchTyp.ARCHIVIERUNG,
        tenant_id=tenant_id,
        status=BatchStatus.LAUFEND,
        gesamt_datensaetze=5000,
        chunk_groesse=500,
        erstellt_am=basis.replace(hour=10),
        beschreibung="GoBD-konforme Archivierung Q4",
    )
    job3.chunks = [
        BatchChunk("BJ-003-CHK-001", "BJ-003", 1, 500, ChunkStatus.ERFOLGREICH),
        BatchChunk("BJ-003-CHK-002", "BJ-003", 2, 500, ChunkStatus.LAUFEND),
        BatchChunk("BJ-003-CHK-003", "BJ-003", 3, 500, ChunkStatus.AUSSTEHEND),
        BatchChunk("BJ-003-CHK-004", "BJ-003", 4, 500, ChunkStatus.AUSSTEHEND),
        BatchChunk("BJ-003-CHK-005", "BJ-003", 5, 500, ChunkStatus.AUSSTEHEND),
        BatchChunk("BJ-003-CHK-006", "BJ-003", 6, 500, ChunkStatus.AUSSTEHEND),
        BatchChunk("BJ-003-CHK-007", "BJ-003", 7, 500, ChunkStatus.AUSSTEHEND),
        BatchChunk("BJ-003-CHK-008", "BJ-003", 8, 500, ChunkStatus.AUSSTEHEND),
        BatchChunk("BJ-003-CHK-009", "BJ-003", 9, 500, ChunkStatus.AUSSTEHEND),
        BatchChunk("BJ-003-CHK-010", "BJ-003", 10, 500, ChunkStatus.AUSSTEHEND),
    ]

    job4 = BatchJob(
        batch_id="BJ-004",
        batch_name="Preislisten-Export Lieferanten",
        batch_typ=BatchTyp.EXPORT,
        tenant_id=tenant_id,
        status=BatchStatus.AUSSTEHEND,
        gesamt_datensaetze=300,
        chunk_groesse=100,
        erstellt_am=basis.replace(hour=14),
        beschreibung="Export aktueller Preislisten an Lieferantenportal",
    )

    return [job1, job2, job3, job4]
