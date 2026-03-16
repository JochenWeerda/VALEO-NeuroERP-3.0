"""
Data Lineage Contracts — Wave 44
Datenherkunfts-Tracking: Lineage-Knoten, Transformationskanten,
gerichteter Abhängigkeitsgraph mit Pfadfindung und Zyklus-Erkennung.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class LineageKnotenTyp(str, Enum):
    QUELLE = "QUELLE"                    # Datenquelle (z.B. Wiegeschein-Erfassung)
    TRANSFORMATION = "TRANSFORMATION"    # Einzelne Transformation
    AGGREGATION = "AGGREGATION"          # Aggregationsschritt
    SENKE = "SENKE"                      # Datenziel (z.B. GoBD-Archiv)
    ZWISCHENSPEICHER = "ZWISCHENSPEICHER"  # Temporärer Speicher / Cache


class TransformationsTyp(str, Enum):
    FILTER = "FILTER"
    PROJEKTION = "PROJEKTION"
    ANREICHERUNG = "ANREICHERUNG"
    BERECHNUNG = "BERECHNUNG"
    NORMALISIERUNG = "NORMALISIERUNG"
    ZUSAMMENFUEHRUNG = "ZUSAMMENFUEHRUNG"


class LineageStatus(str, Enum):
    AKTIV = "AKTIV"
    VERALTET = "VERALTET"
    ARCHIVIERT = "ARCHIVIERT"


# ---------------------------------------------------------------------------
# Lineage-Knoten
# ---------------------------------------------------------------------------

@dataclass
class LineageKnoten:
    """Ein Knoten im Datenherkunftsgraphen."""
    knoten_id: str
    knoten_name: str
    knoten_typ: LineageKnotenTyp
    tenant_id: str
    erstellt_am: datetime
    schema_id: str = ""     # Referenz auf EventSchemaEintrag (optional)
    status: LineageStatus = LineageStatus.AKTIV
    metadaten: dict[str, str] = field(default_factory=dict)

    @property
    def ist_quelle(self) -> bool:
        return self.knoten_typ == LineageKnotenTyp.QUELLE

    @property
    def ist_senke(self) -> bool:
        return self.knoten_typ == LineageKnotenTyp.SENKE

    def as_dict(self) -> dict[str, Any]:
        return {
            "knoten_id": self.knoten_id,
            "knoten_name": self.knoten_name,
            "knoten_typ": self.knoten_typ.value,
            "tenant_id": self.tenant_id,
            "erstellt_am": self.erstellt_am.isoformat(),
            "schema_id": self.schema_id,
            "status": self.status.value,
            "ist_quelle": self.ist_quelle,
            "ist_senke": self.ist_senke,
        }


# ---------------------------------------------------------------------------
# Lineage-Kante
# ---------------------------------------------------------------------------

@dataclass
class LineageKante:
    """Eine gerichtete Transformationskante zwischen zwei Knoten."""
    kante_id: str
    von_knoten_id: str
    zu_knoten_id: str
    transformations_typ: TransformationsTyp
    beschreibung: str = ""
    erstellt_am: datetime = field(default_factory=datetime.utcnow)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kante_id": self.kante_id,
            "von_knoten_id": self.von_knoten_id,
            "zu_knoten_id": self.zu_knoten_id,
            "transformations_typ": self.transformations_typ.value,
            "beschreibung": self.beschreibung,
            "erstellt_am": self.erstellt_am.isoformat(),
        }


# ---------------------------------------------------------------------------
# Lineage-Graph
# ---------------------------------------------------------------------------

@dataclass
class LineageGraph:
    """
    Gerichteter Datenherkunftsgraph mit Knoten und Kanten.
    Ermöglicht Pfadfindung (BFS) und Zyklus-Erkennung (DFS).
    """
    graph_id: str
    tenant_id: str
    knoten: list[LineageKnoten] = field(default_factory=list)
    kanten: list[LineageKante] = field(default_factory=list)

    @property
    def quellen(self) -> list[LineageKnoten]:
        return [k for k in self.knoten if k.ist_quelle]

    @property
    def senken(self) -> list[LineageKnoten]:
        return [k for k in self.knoten if k.ist_senke]

    def _adjazenz(self) -> dict[str, list[str]]:
        """Aufbau der Adjazenzliste aus den Kanten."""
        adj: dict[str, list[str]] = {k.knoten_id: [] for k in self.knoten}
        for kante in self.kanten:
            if kante.von_knoten_id in adj:
                adj[kante.von_knoten_id].append(kante.zu_knoten_id)
        return adj

    def finde_pfad(self, von_knoten_id: str, zu_knoten_id: str) -> list[str]:
        """
        BFS-Pfadfindung von von_knoten_id zu zu_knoten_id.
        Gibt die Liste der Knoten-IDs zurück oder [] wenn kein Pfad existiert.
        """
        if von_knoten_id == zu_knoten_id:
            return [von_knoten_id]

        adj = self._adjazenz()
        besucht: set[str] = {von_knoten_id}
        warteschlange: deque[list[str]] = deque([[von_knoten_id]])

        while warteschlange:
            pfad = warteschlange.popleft()
            aktuell = pfad[-1]
            for nachbar in adj.get(aktuell, []):
                if nachbar == zu_knoten_id:
                    return pfad + [nachbar]
                if nachbar not in besucht:
                    besucht.add(nachbar)
                    warteschlange.append(pfad + [nachbar])

        return []

    @property
    def hat_zyklus(self) -> bool:
        """DFS-basierte Zyklus-Erkennung im gerichteten Graphen."""
        adj = self._adjazenz()
        besucht: set[str] = set()
        im_stapel: set[str] = set()

        def dfs(knoten_id: str) -> bool:
            besucht.add(knoten_id)
            im_stapel.add(knoten_id)
            for nachbar in adj.get(knoten_id, []):
                if nachbar not in besucht:
                    if dfs(nachbar):
                        return True
                elif nachbar in im_stapel:
                    return True
            im_stapel.discard(knoten_id)
            return False

        for knoten_id in adj:
            if knoten_id not in besucht:
                if dfs(knoten_id):
                    return True
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "tenant_id": self.tenant_id,
            "knoten_anzahl": len(self.knoten),
            "kanten_anzahl": len(self.kanten),
            "quellen_anzahl": len(self.quellen),
            "senken_anzahl": len(self.senken),
            "hat_zyklus": self.hat_zyklus,
            "knoten": [k.as_dict() for k in self.knoten],
            "kanten": [k.as_dict() for k in self.kanten],
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def erstelle_lineage_graph(
    graph_id: str,
    tenant_id: str,
    knoten: list[LineageKnoten],
    kanten: list[LineageKante],
) -> LineageGraph:
    """Erstellt einen neuen Lineage-Graphen."""
    return LineageGraph(
        graph_id=graph_id,
        tenant_id=tenant_id,
        knoten=knoten,
        kanten=kanten,
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_lineage_graph(tenant_id: str = "TENANT-001") -> LineageGraph:
    """
    Gibt einen Beispiel-Lineage-Graphen für den Agrar-Annahme-Settlement-Prozess zurück.

    Topologie (azyklisch):
      Wiegeschein-Erfassung (QUELLE)
          → Qualitäts-Normalisierung (TRANSFORMATION)
              → Settlement-Berechnung (AGGREGATION)
                  → GoBD-Beleg (SENKE)
                  → Controlling-KPI (ZWISCHENSPEICHER)
    """
    basis = datetime(2026, 3, 1)
    knoten = [
        LineageKnoten("LK-001", "Wiegeschein-Erfassung",
                      LineageKnotenTyp.QUELLE, tenant_id, basis,
                      schema_id="ES-003"),
        LineageKnoten("LK-002", "Qualitäts-Normalisierung",
                      LineageKnotenTyp.TRANSFORMATION, tenant_id,
                      basis.replace(day=2)),
        LineageKnoten("LK-003", "Settlement-Berechnung",
                      LineageKnotenTyp.AGGREGATION, tenant_id,
                      basis.replace(day=3)),
        LineageKnoten("LK-004", "GoBD-Abrechnungsbeleg",
                      LineageKnotenTyp.SENKE, tenant_id,
                      basis.replace(day=4),
                      schema_id="ES-004"),
        LineageKnoten("LK-005", "Controlling-KPI-Cache",
                      LineageKnotenTyp.ZWISCHENSPEICHER, tenant_id,
                      basis.replace(day=4)),
    ]
    kanten = [
        LineageKante("LKT-001", "LK-001", "LK-002",
                     TransformationsTyp.NORMALISIERUNG,
                     "Feuchte- und Verunreinigungsabzüge normalisieren",
                     basis.replace(day=2)),
        LineageKante("LKT-002", "LK-002", "LK-003",
                     TransformationsTyp.BERECHNUNG,
                     "Nettomenge × Preis + Qualitätsabzüge",
                     basis.replace(day=3)),
        LineageKante("LKT-003", "LK-003", "LK-004",
                     TransformationsTyp.PROJEKTION,
                     "GoBD-konforme Belegfelder projizieren",
                     basis.replace(day=4)),
        LineageKante("LKT-004", "LK-003", "LK-005",
                     TransformationsTyp.ANREICHERUNG,
                     "KPI-Anreicherung für Controlling-Dashboard",
                     basis.replace(day=4)),
        LineageKante("LKT-005", "LK-001", "LK-003",
                     TransformationsTyp.FILTER,
                     "Direkt-Filter: Wiegescheine ohne Qualitätsmangel",
                     basis.replace(day=3)),
    ]
    return LineageGraph(
        graph_id="LG-AGRAR-SETTLEMENT",
        tenant_id=tenant_id,
        knoten=knoten,
        kanten=kanten,
    )
