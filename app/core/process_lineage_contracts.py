from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class LineageKnotenTyp(str, Enum):
    QUELLE = "QUELLE"                       # Data source
    TRANSFORMATION = "TRANSFORMATION"        # Processing step
    ZIEL = "ZIEL"                           # Output/target
    ZWISCHENSPEICHER = "ZWISCHENSPEICHER"   # Intermediate storage


class LineageOperationTyp(str, Enum):
    LESEN = "LESEN"
    SCHREIBEN = "SCHREIBEN"
    TRANSFORMIEREN = "TRANSFORMIEREN"
    KOPIEREN = "KOPIEREN"
    LOESCHEN = "LOESCHEN"


@dataclass
class LineageKnoten:
    knoten_id: str
    name: str
    knoten_typ: LineageKnotenTyp
    system: str       # e.g. "PostgreSQL", "NATS", "SAP"
    datensatz: str    # table/topic/entity name
    tenant_id: str = ""


@dataclass
class LineageKante:
    kante_id: str
    von_knoten_id: str
    zu_knoten_id: str
    operation: LineageOperationTyp
    workflow_instanz_id: str
    ausgefuehrt_am: datetime = field(default_factory=datetime.utcnow)
    datenmenge_bytes: int = 0


@dataclass
class LineageGraph:
    graph_id: str
    knoten: list = field(default_factory=list)   # list[LineageKnoten]
    kanten: list = field(default_factory=list)   # list[LineageKante]

    def quell_knoten(self) -> list:
        """Returns nodes of type QUELLE."""
        return [k for k in self.knoten if k.knoten_typ == LineageKnotenTyp.QUELLE]

    def ziel_knoten(self) -> list:
        """Returns nodes of type ZIEL."""
        return [k for k in self.knoten if k.knoten_typ == LineageKnotenTyp.ZIEL]

    def upstream_knoten(self, knoten_id: str) -> list:
        """
        Returns all LineageKnoten that directly feed into knoten_id
        (i.e. von_knoten where kante.zu_knoten_id == knoten_id).
        """
        von_ids = {k.von_knoten_id for k in self.kanten if k.zu_knoten_id == knoten_id}
        return [k for k in self.knoten if k.knoten_id in von_ids]

    def downstream_knoten(self, knoten_id: str) -> list:
        """
        Returns all LineageKnoten that knoten_id directly feeds into.
        """
        zu_ids = {k.zu_knoten_id for k in self.kanten if k.von_knoten_id == knoten_id}
        return [k for k in self.knoten if k.knoten_id in zu_ids]

    def gesamt_datenmenge_bytes(self) -> int:
        return sum(k.datenmenge_bytes for k in self.kanten)


def get_default_lineage_graph() -> LineageGraph:
    now = datetime(2026, 3, 16, 10, 0, 0)
    from datetime import timedelta
    g = LineageGraph("LG-001")
    g.knoten = [
        LineageKnoten("LK-001", "Waage-Eingang", LineageKnotenTyp.QUELLE, "IoT-Gateway", "waage_messung", "TENANT-A"),
        LineageKnoten("LK-002", "Kontrakt-DB", LineageKnotenTyp.QUELLE, "PostgreSQL", "kontrakte", "TENANT-A"),
        LineageKnoten("LK-003", "Settlement-Berechnung", LineageKnotenTyp.TRANSFORMATION, "Python-Service", "settlement_calc", "TENANT-A"),
        LineageKnoten("LK-004", "Journal-DB", LineageKnotenTyp.ZIEL, "PostgreSQL", "journal_eintraege", "TENANT-A"),
        LineageKnoten("LK-005", "Archiv-Speicher", LineageKnotenTyp.ZIEL, "S3", "archiv_bucket", "TENANT-A"),
        LineageKnoten("LK-006", "Zwischenpuffer", LineageKnotenTyp.ZWISCHENSPEICHER, "Redis", "settlement_cache", "TENANT-A"),
    ]
    g.kanten = [
        LineageKante("LE-001", "LK-001", "LK-003", LineageOperationTyp.LESEN, "WI-S-001", now, 1024),
        LineageKante("LE-002", "LK-002", "LK-003", LineageOperationTyp.LESEN, "WI-S-001", now, 2048),
        LineageKante("LE-003", "LK-003", "LK-006", LineageOperationTyp.SCHREIBEN, "WI-S-001", now + timedelta(minutes=1), 512),
        LineageKante("LE-004", "LK-006", "LK-004", LineageOperationTyp.TRANSFORMIEREN, "WI-S-001", now + timedelta(minutes=2), 512),
        LineageKante("LE-005", "LK-004", "LK-005", LineageOperationTyp.KOPIEREN, "WI-S-001", now + timedelta(minutes=3), 2048),
    ]
    return g
