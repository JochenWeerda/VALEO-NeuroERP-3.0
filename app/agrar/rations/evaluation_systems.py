"""Registrierte Bedarfs-/Bewertungssysteme (FEED-CORE-020, FEED-REQ-002).

Die Formeln bleiben versionierter, golden-getesteter Code (Single Source of
Truth); diese Registry macht Auswahl und Version als Daten sichtbar und
referenziert das tragende Modul. Neue Normstaende werden als neue Version
angehaengt (append-only), nie durch Ueberschreiben.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationSystemSeed:
    system_id: str
    name: str
    description: str
    version_label: str
    module_ref: str


SEED_SYSTEMS: tuple[EvaluationSystemSeed, ...] = (
    EvaluationSystemSeed(
        system_id="gfe2023",
        name="GfE 2023 (ME/sidP)",
        description="Energie- und Proteinbedarf Milchkuh nach GfE 2023 (ME_FAN1, sidP).",
        version_label="2023",
        module_ref="app.agrar.rations.constants.gfe2023",
    ),
    EvaluationSystemSeed(
        system_id="dlg2025",
        name="DLG-Information 01/2025",
        description="Kontroll- und Bewertungskennzahlen (ECM, DCAB, peNDF, Effizienz) nach DLG 01/2025.",
        version_label="01-2025",
        module_ref="app.agrar.rations.constants.dlg2025",
    ),
)
