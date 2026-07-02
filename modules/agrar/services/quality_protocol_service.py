"""
Quality Protocol Service für Ernte-Annahme.

Verwaltet Qualitätsprotokolle für Laborwerte mit Versionierung und Import-Funktionalität.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Protocol, Literal
import json
import csv
from io import StringIO

from app.core.uuid7 import uuid7

from app.core.data_quality_enforcement import (
    DQValidationException,
    evaluate_quality_protocol_datensatz,
)

SourceType = Literal["manual", "import", "lims", "device"]


@dataclass
class QualityProtocol:
    """Qualitätsprotokoll-Datenstruktur."""
    id: str
    tenant_id: str
    harvest_acceptance_id: Optional[str]
    protocol_number: str
    version: int
    
    # Laborwerte
    moisture_pct: Optional[Decimal] = None
    impurities_pct: Optional[Decimal] = None
    hl_weight_kg_per_hl: Optional[Decimal] = None
    protein_pct: Optional[Decimal] = None
    mycotoxin_ppb: Optional[Decimal] = None
    other_values: Optional[dict] = None  # JSONB für weitere Werte
    
    # Quelle
    source_type: Optional[SourceType] = None
    source_device_id: Optional[str] = None
    source_file_name: Optional[str] = None
    source_file_content: Optional[str] = None
    
    # Status
    is_final: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Audit
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


@dataclass
class QualityProtocolCreate:
    """Input für Protokoll-Erstellung."""
    tenant_id: str
    harvest_acceptance_id: Optional[str] = None
    protocol_number: Optional[str] = None  # Auto-generiert wenn None
    
    # Laborwerte
    moisture_pct: Optional[Decimal] = None
    impurities_pct: Optional[Decimal] = None
    hl_weight_kg_per_hl: Optional[Decimal] = None
    protein_pct: Optional[Decimal] = None
    mycotoxin_ppb: Optional[Decimal] = None
    other_values: Optional[dict] = None
    
    # Quelle
    source_type: SourceType = "manual"
    source_device_id: Optional[str] = None
    source_file_name: Optional[str] = None
    source_file_content: Optional[str] = None
    
    # Audit
    created_by: Optional[str] = None


@dataclass
class QualityProtocolUpdate:
    """Input für Protokoll-Update."""
    # Laborwerte
    moisture_pct: Optional[Decimal] = None
    impurities_pct: Optional[Decimal] = None
    hl_weight_kg_per_hl: Optional[Decimal] = None
    protein_pct: Optional[Decimal] = None
    mycotoxin_ppb: Optional[Decimal] = None
    other_values: Optional[dict] = None
    
    # Audit
    updated_by: Optional[str] = None


class QualityProtocolRepository(Protocol):
    """Protocol für Quality Protocol Repository."""
    
    def create(self, protocol: QualityProtocol) -> QualityProtocol:
        """Erstellt ein neues Qualitätsprotokoll."""
        ...
    
    def get_by_id(self, protocol_id: str) -> Optional[QualityProtocol]:
        """Ruft ein Protokoll anhand der ID ab."""
        ...
    
    def get_by_harvest_acceptance(self, harvest_acceptance_id: str) -> list[QualityProtocol]:
        """Ruft alle Protokolle für eine Ernte-Annahme ab."""
        ...
    
    def get_latest(self, harvest_acceptance_id: str) -> Optional[QualityProtocol]:
        """Ruft das neueste Protokoll für eine Ernte-Annahme ab."""
        ...
    
    def update(self, protocol_id: str, update: QualityProtocolUpdate) -> QualityProtocol:
        """Aktualisiert ein Protokoll."""
        ...
    
    def finalize(self, protocol_id: str, approved_by: str) -> QualityProtocol:
        """Finalisiert ein Protokoll."""
        ...


def _generate_protocol_number(harvest_acceptance_id: Optional[str], version: int) -> str:
    """Generiert eine Protokoll-Nummer."""
    if harvest_acceptance_id:
        return f"QP-{harvest_acceptance_id[:8]}-V{version:02d}"
    return f"QP-{datetime.now().strftime('%Y%m%d')}-V{version:02d}"


def create_quality_protocol(
    repo: QualityProtocolRepository,
    create_input: QualityProtocolCreate,
) -> QualityProtocol:
    """
    Erstellt ein neues Qualitätsprotokoll.
    
    Wenn harvest_acceptance_id vorhanden ist, wird die Versionsnummer automatisch
    basierend auf bestehenden Protokollen erhöht.
    """
    dq_result = evaluate_quality_protocol_datensatz(
        {
            "ernteannahme_id": create_input.harvest_acceptance_id,
            "quelle": create_input.source_type,
            "feuchte_pct": create_input.moisture_pct,
            "protein_pct": create_input.protein_pct,
            "hl_gewicht": create_input.hl_weight_kg_per_hl,
        }
    )
    if not dq_result.bestanden:
        raise DQValidationException("Qualitaetsprotokoll", dq_result)

    # Prüfe bestehende Protokolle für Versionsnummer
    version = 1
    if create_input.harvest_acceptance_id:
        existing = repo.get_by_harvest_acceptance(create_input.harvest_acceptance_id)
        if existing:
            version = max(p.version for p in existing) + 1
    
    # Generiere Protokoll-Nummer
    protocol_number = create_input.protocol_number
    if not protocol_number:
        protocol_number = _generate_protocol_number(create_input.harvest_acceptance_id, version)
    
    protocol = QualityProtocol(
        # UUIDv7 statt Sekunden-Timestamp: der alte Schlüssel qp_<YYYYMMDDHHMMSS>_<version>
        # kollidierte, sobald zwei Protokolle (verschiedener Annahmen) in derselben
        # Sekunde entstanden — genau der Batch-Nachtrag-Fall aus dem Laborbuch.
        id=f"qp_{uuid7()}",
        tenant_id=create_input.tenant_id,
        harvest_acceptance_id=create_input.harvest_acceptance_id,
        protocol_number=protocol_number,
        version=version,
        moisture_pct=create_input.moisture_pct,
        impurities_pct=create_input.impurities_pct,
        hl_weight_kg_per_hl=create_input.hl_weight_kg_per_hl,
        protein_pct=create_input.protein_pct,
        mycotoxin_ppb=create_input.mycotoxin_ppb,
        other_values=create_input.other_values,
        source_type=create_input.source_type,
        source_device_id=create_input.source_device_id,
        source_file_name=create_input.source_file_name,
        source_file_content=create_input.source_file_content,
        is_final=False,
        created_at=datetime.now(),
        created_by=create_input.created_by,
    )
    
    return repo.create(protocol)


def update_quality_protocol(
    repo: QualityProtocolRepository,
    protocol_id: str,
    update_input: QualityProtocolUpdate,
) -> QualityProtocol:
    """
    Aktualisiert ein Qualitätsprotokoll.
    
    Nur möglich, wenn is_final = False.
    """
    protocol = repo.get_by_id(protocol_id)
    if not protocol:
        raise ValueError(f"Quality protocol {protocol_id} not found")
    
    if protocol.is_final:
        raise ValueError(f"Quality protocol {protocol_id} is finalized and cannot be updated")
    
    return repo.update(protocol_id, update_input)


def finalize_quality_protocol(
    repo: QualityProtocolRepository,
    protocol_id: str,
    approved_by: str,
) -> QualityProtocol:
    """
    Finalisiert ein Qualitätsprotokoll.
    
    Nach Finalisierung können keine Änderungen mehr vorgenommen werden.
    """
    protocol = repo.get_by_id(protocol_id)
    if not protocol:
        raise ValueError(f"Quality protocol {protocol_id} not found")
    
    if protocol.is_final:
        raise ValueError(f"Quality protocol {protocol_id} is already finalized")
    
    return repo.finalize(protocol_id, approved_by)


def import_from_csv(
    repo: QualityProtocolRepository,
    tenant_id: str,
    harvest_acceptance_id: Optional[str],
    csv_content: str,
    file_name: str,
    created_by: Optional[str] = None,
) -> QualityProtocol:
    """
    Importiert Laborwerte aus CSV.
    
    Erwartetes CSV-Format:
    - Header: moisture_pct,impurities_pct,hl_weight_kg_per_hl,protein_pct,mycotoxin_ppb
    - Werte: Dezimalzahlen (Komma oder Punkt als Dezimaltrenner)
    """
    reader = csv.DictReader(StringIO(csv_content))
    row = next(reader, None)
    
    if not row:
        raise ValueError("CSV file is empty")
    
    # Konvertiere Werte
    def _parse_decimal(value: Optional[str]) -> Optional[Decimal]:
        if not value or value.strip() == "":
            return None
        # Ersetze Komma durch Punkt
        value = value.replace(",", ".")
        return Decimal(value)

    moisture_pct = _parse_decimal(row.get("moisture_pct"))
    impurities_pct = _parse_decimal(row.get("impurities_pct"))
    hl_weight = _parse_decimal(row.get("hl_weight_kg_per_hl"))
    protein_pct = _parse_decimal(row.get("protein_pct"))
    mycotoxin_ppb = _parse_decimal(row.get("mycotoxin_ppb"))
    
    create_input = QualityProtocolCreate(
        tenant_id=tenant_id,
        harvest_acceptance_id=harvest_acceptance_id,
        moisture_pct=moisture_pct,
        impurities_pct=impurities_pct,
        hl_weight_kg_per_hl=hl_weight,
        protein_pct=protein_pct,
        mycotoxin_ppb=mycotoxin_ppb,
        source_type="import",
        source_file_name=file_name,
        source_file_content=csv_content,
        created_by=created_by,
    )
    
    return create_quality_protocol(repo, create_input)


def import_from_json(
    repo: QualityProtocolRepository,
    tenant_id: str,
    harvest_acceptance_id: Optional[str],
    json_content: str,
    file_name: str,
    created_by: Optional[str] = None,
) -> QualityProtocol:
    """
    Importiert Laborwerte aus JSON.
    
    Erwartetes JSON-Format:
    {
        "moisture_pct": 15.5,
        "impurities_pct": 2.1,
        "hl_weight_kg_per_hl": 75.2,
        "protein_pct": 12.3,
        "mycotoxin_ppb": 150.0,
        "other_values": {...}
    }
    """
    data = json.loads(json_content)
    
    def _parse_decimal(value) -> Optional[Decimal]:
        if value is None:
            return None
        return Decimal(str(value))

    moisture_pct = _parse_decimal(data.get("moisture_pct"))
    impurities_pct = _parse_decimal(data.get("impurities_pct"))
    hl_weight = _parse_decimal(data.get("hl_weight_kg_per_hl"))
    protein_pct = _parse_decimal(data.get("protein_pct"))
    mycotoxin_ppb = _parse_decimal(data.get("mycotoxin_ppb"))
    
    create_input = QualityProtocolCreate(
        tenant_id=tenant_id,
        harvest_acceptance_id=harvest_acceptance_id,
        moisture_pct=moisture_pct,
        impurities_pct=impurities_pct,
        hl_weight_kg_per_hl=hl_weight,
        protein_pct=protein_pct,
        mycotoxin_ppb=mycotoxin_ppb,
        other_values=data.get("other_values"),
        source_type="import",
        source_file_name=file_name,
        source_file_content=json_content,
        created_by=created_by,
    )
    
    return create_quality_protocol(repo, create_input)


def get_latest_protocol(
    repo: QualityProtocolRepository,
    harvest_acceptance_id: str,
) -> Optional[QualityProtocol]:
    """
    Ruft das neueste (höchste Version) Qualitätsprotokoll für eine Ernte-Annahme ab.
    """
    return repo.get_latest(harvest_acceptance_id)


