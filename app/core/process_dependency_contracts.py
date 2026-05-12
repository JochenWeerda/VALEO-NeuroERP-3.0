from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime

class AbhaengigkeitsTyp(str, Enum):
    SEQUENZIELL = "SEQUENZIELL"    # B can only start after A finishes
    PARALLEL = "PARALLEL"          # B can start when A starts
    OPTIONAL = "OPTIONAL"          # B can start even if A fails
    BLOCKIEREND = "BLOCKIEREND"    # B cannot start if A fails

class SchrittStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    BEREIT = "BEREIT"          # All dependencies satisfied
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    UEBERSPRUNGEN = "UEBERSPRUNGEN"

@dataclass
class AbhaengigkeitsKante:
    von_schritt_id: str
    zu_schritt_id: str
    typ: AbhaengigkeitsTyp

@dataclass
class ProzessSchritt:
    schritt_id: str
    name: str
    status: SchrittStatus = SchrittStatus.AUSSTEHEND
    abhaengigkeiten: list = field(default_factory=list)  # list[str] of schritt_ids this depends on

@dataclass
class ProzessGraph:
    graph_id: str
    schritte: list = field(default_factory=list)   # list[ProzessSchritt]
    kanten: list = field(default_factory=list)     # list[AbhaengigkeitsKante]

    def _schritt_map(self) -> dict:
        return {s.schritt_id: s for s in self.schritte}

    def bereite_schritte(self) -> list:
        """
        Returns steps that are AUSSTEHEND and whose SEQUENZIELL/BLOCKIEREND
        dependencies are all ABGESCHLOSSEN (or UEBERSPRUNGEN for OPTIONAL).
        Steps with no incoming SEQUENZIELL/BLOCKIEREND edges are immediately ready.
        Logic:
        - For each AUSSTEHEND step, check all incoming kanten:
          - SEQUENZIELL: von_schritt must be ABGESCHLOSSEN
          - BLOCKIEREND: von_schritt must be ABGESCHLOSSEN (if FEHLGESCHLAGEN -> not ready)
          - PARALLEL: no blocking constraint (von_schritt can be any status)
          - OPTIONAL: no blocking constraint
        - If all blocking constraints satisfied -> step is BEREIT
        """
        schritt_map = self._schritt_map()
        # Build incoming edges per step
        eingehend = {s.schritt_id: [] for s in self.schritte}
        for k in self.kanten:
            eingehend[k.zu_schritt_id].append(k)

        bereit = []
        for schritt in self.schritte:
            if schritt.status != SchrittStatus.AUSSTEHEND:
                continue
            blockiert = False
            for kante in eingehend[schritt.schritt_id]:
                von = schritt_map.get(kante.von_schritt_id)
                if von is None:
                    continue
                if kante.typ in (AbhaengigkeitsTyp.SEQUENZIELL, AbhaengigkeitsTyp.BLOCKIEREND):
                    if von.status != SchrittStatus.ABGESCHLOSSEN:
                        blockiert = True
                        break
            if not blockiert:
                bereit.append(schritt)
        return bereit

    def topologische_reihenfolge(self) -> list:
        """
        Returns schritt_ids in topological order (Kahn's algorithm).
        Returns empty list if cycle detected.
        Uses only SEQUENZIELL and BLOCKIEREND edges for ordering.
        """
        from collections import deque
        eingehend_grad = {s.schritt_id: 0 for s in self.schritte}
        nachfolger = {s.schritt_id: [] for s in self.schritte}
        for k in self.kanten:
            if k.typ in (AbhaengigkeitsTyp.SEQUENZIELL, AbhaengigkeitsTyp.BLOCKIEREND):
                eingehend_grad[k.zu_schritt_id] += 1
                nachfolger[k.von_schritt_id].append(k.zu_schritt_id)
        queue = deque([sid for sid, grad in eingehend_grad.items() if grad == 0])
        reihenfolge = []
        while queue:
            sid = queue.popleft()
            reihenfolge.append(sid)
            for nachf in nachfolger[sid]:
                eingehend_grad[nachf] -= 1
                if eingehend_grad[nachf] == 0:
                    queue.append(nachf)
        if len(reihenfolge) != len(self.schritte):
            return []  # cycle detected
        return reihenfolge

def get_default_prozess_graphen() -> list:
    """Returns 2 default ProzessGraph instances."""
    _now = datetime(2026, 3, 16, 10, 0, 0)  # noqa: F841

    # Graph 1: Linear kontrakt process: S1->S2->S3->S4
    g1 = ProzessGraph("PG-001")
    g1.schritte = [
        ProzessSchritt("S1", "Erfassen", SchrittStatus.ABGESCHLOSSEN),
        ProzessSchritt("S2", "Pruefen", SchrittStatus.ABGESCHLOSSEN),
        ProzessSchritt("S3", "Freigeben", SchrittStatus.AUSSTEHEND),
        ProzessSchritt("S4", "Archivieren", SchrittStatus.AUSSTEHEND),
    ]
    g1.kanten = [
        AbhaengigkeitsKante("S1", "S2", AbhaengigkeitsTyp.SEQUENZIELL),
        AbhaengigkeitsKante("S2", "S3", AbhaengigkeitsTyp.SEQUENZIELL),
        AbhaengigkeitsKante("S3", "S4", AbhaengigkeitsTyp.SEQUENZIELL),
    ]

    # Graph 2: Fork-join: S1->S2a, S1->S2b (parallel), S2a+S2b->S3
    g2 = ProzessGraph("PG-002")
    g2.schritte = [
        ProzessSchritt("S1", "Start", SchrittStatus.ABGESCHLOSSEN),
        ProzessSchritt("S2a", "Qualitaetspruefung", SchrittStatus.AUSSTEHEND),
        ProzessSchritt("S2b", "Mengenpruefung", SchrittStatus.AUSSTEHEND),
        ProzessSchritt("S3", "Settlement", SchrittStatus.AUSSTEHEND),
    ]
    g2.kanten = [
        AbhaengigkeitsKante("S1", "S2a", AbhaengigkeitsTyp.SEQUENZIELL),
        AbhaengigkeitsKante("S1", "S2b", AbhaengigkeitsTyp.SEQUENZIELL),
        AbhaengigkeitsKante("S2a", "S3", AbhaengigkeitsTyp.SEQUENZIELL),
        AbhaengigkeitsKante("S2b", "S3", AbhaengigkeitsTyp.SEQUENZIELL),
    ]

    return [g1, g2]
