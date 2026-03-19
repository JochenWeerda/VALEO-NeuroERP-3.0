"""
Wave 68 — Workflow Dependency Visualization Contracts.
Pure domain layer: NO imports from app/api/.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set


class KnotenTyp(Enum):
    START = "START"
    AUFGABE = "AUFGABE"
    ENTSCHEIDUNG = "ENTSCHEIDUNG"
    PARALLELISIERUNG = "PARALLELISIERUNG"
    ZUSAMMENFUEHRUNG = "ZUSAMMENFUEHRUNG"
    ENDE = "ENDE"
    SUBPROZESS = "SUBPROZESS"


class KantenStil(Enum):
    NORMAL = "NORMAL"
    BEDINGT = "BEDINGT"              # conditional edge
    FEHLER = "FEHLER"                # error/exception path
    KOMPENSATION = "KOMPENSATION"    # compensation/rollback
    OPTIONAL = "OPTIONAL"


class LayoutRichtung(Enum):
    LINKS_RECHTS = "LR"
    OBEN_UNTEN = "TB"
    RECHTS_LINKS = "RL"
    UNTEN_OBEN = "BT"


@dataclass
class VisualisierungsKnoten:
    knoten_id: str
    bezeichnung: str
    typ: KnotenTyp
    ebene: int = 0                          # hierarchy level for layout
    gruppe: Optional[str] = None            # swimlane/group
    metadaten: Dict = field(default_factory=dict)


@dataclass
class VisualisierungsKante:
    von: str    # source knoten_id
    nach: str   # target knoten_id
    stil: KantenStil = KantenStil.NORMAL
    beschriftung: Optional[str] = None
    gewicht: int = 1  # for layout algorithms


@dataclass
class VisualisierungsGraph:
    graph_id: str
    workflow_id: str
    knoten: List[VisualisierungsKnoten] = field(default_factory=list)
    kanten: List[VisualisierungsKante] = field(default_factory=list)
    richtung: LayoutRichtung = LayoutRichtung.LINKS_RECHTS

    def knoten_nach_typ(self, typ: KnotenTyp) -> List[VisualisierungsKnoten]:
        return [k for k in self.knoten if k.typ == typ]

    def nachfolger(self, knoten_id: str) -> List[str]:
        return [k.nach for k in self.kanten if k.von == knoten_id]

    def vorgaenger(self, knoten_id: str) -> List[str]:
        return [k.von for k in self.kanten if k.nach == knoten_id]

    def kritischer_pfad(self) -> List[str]:
        """Returns longest path from START to END nodes using DFS with memoization."""
        start_knoten = [k.knoten_id for k in self.knoten if k.typ == KnotenTyp.START]
        ende_knoten = {k.knoten_id for k in self.knoten if k.typ == KnotenTyp.ENDE}

        if not start_knoten or not ende_knoten:
            return []

        # Build adjacency list
        adj: Dict[str, List[str]] = {k.knoten_id: [] for k in self.knoten}
        for kante in self.kanten:
            if kante.von in adj:
                adj[kante.von].append(kante.nach)

        memo: Dict[str, List[str]] = {}

        def dfs(node: str) -> List[str]:
            if node in memo:
                return memo[node]
            if node in ende_knoten:
                memo[node] = [node]
                return [node]
            beste: List[str] = []
            for nachf in adj.get(node, []):
                pfad = dfs(nachf)
                if len(pfad) + 1 > len(beste) + 1:
                    beste = pfad
            ergebnis = [node] + beste
            memo[node] = ergebnis
            return ergebnis

        bester_pfad: List[str] = []
        for start in start_knoten:
            pfad = dfs(start)
            if len(pfad) > len(bester_pfad):
                bester_pfad = pfad
        return bester_pfad

    def hat_zyklen(self) -> bool:
        """DFS cycle detection."""
        visited: Set[str] = set()
        in_stack: Set[str] = set()

        adj: Dict[str, List[str]] = {k.knoten_id: [] for k in self.knoten}
        for kante in self.kanten:
            if kante.von in adj:
                adj[kante.von].append(kante.nach)

        def dfs(node: str) -> bool:
            visited.add(node)
            in_stack.add(node)
            for nachf in adj.get(node, []):
                if nachf not in visited:
                    if dfs(nachf):
                        return True
                elif nachf in in_stack:
                    return True
            in_stack.discard(node)
            return False

        for knoten in self.knoten:
            if knoten.knoten_id not in visited:
                if dfs(knoten.knoten_id):
                    return True
        return False

    def ebenen_layout(self) -> Dict[str, int]:
        """Assign levels using topological BFS (longest path from roots)."""
        in_grad: Dict[str, int] = {k.knoten_id: 0 for k in self.knoten}
        adj: Dict[str, List[str]] = {k.knoten_id: [] for k in self.knoten}
        for kante in self.kanten:
            if kante.nach in in_grad:
                in_grad[kante.nach] += 1
            if kante.von in adj:
                adj[kante.von].append(kante.nach)

        ebene: Dict[str, int] = {}
        queue = [k for k, v in in_grad.items() if v == 0]
        for k in queue:
            ebene[k] = 0

        while queue:
            naechste = []
            for node in queue:
                for nachf in adj.get(node, []):
                    in_grad[nachf] -= 1
                    ebene[nachf] = max(ebene.get(nachf, 0), ebene[node] + 1)
                    if in_grad[nachf] == 0:
                        naechste.append(nachf)
            queue = naechste
        return ebene


@dataclass
class GraphExport:
    graph_id: str
    format: str   # "mermaid", "dot", "json"
    inhalt: str
    erstellt_am: str  # ISO datetime string

    def zeilen_anzahl(self) -> int:
        return len(self.inhalt.splitlines())
