"""Pydantic-Modelle fuer Mischfutter-Etikettenanalyse (Compound-Feed).

Extrahiert 2026-04-23 aus
``app.api.v1.endpoints.rations_optimization`` (Refactor Schritt 1e).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CompoundFeedComponent(BaseModel):
    """Eine einzelne Rezepturkomponente (Rueckenetiketten-Position)."""
    name: str
    inclusion_pct: float
    matched_feed_id: Optional[str] = None
    matched_feed_name: Optional[str] = None


class CompoundFeedDeclaredAnalysis(BaseModel):
    """Deklarierte Inhaltsstoffe auf dem Etikett (Prozent FM)."""
    crude_protein_pct: Optional[float] = None
    crude_fat_pct: Optional[float] = None
    crude_fiber_pct: Optional[float] = None
    crude_ash_pct: Optional[float] = None
    calcium_pct: Optional[float] = None
    phosphorus_pct: Optional[float] = None
    sodium_pct: Optional[float] = None
    magnesium_pct: Optional[float] = None
    nel_mj_kg: Optional[float] = None


class CompoundFeedGfeEstimate(BaseModel):
    """Abgeleitete GfE-2023-Schaetzung aus Deklaration + Rezeptur-Match."""
    basis: str
    match_coverage_pct: float
    me_fan1_mj_kgdm: Optional[float] = None
    me_fani_mj_kgdm: Optional[float] = None
    nel_mj_kgdm: Optional[float] = None
    sidp_g_kgdm: Optional[float] = None
    nxp_g_kgdm: Optional[float] = None
    cp_g_kgdm: Optional[float] = None
    andfom_g_kgdm: Optional[float] = None
    starch_g_kgdm: Optional[float] = None
    sugar_g_kgdm: Optional[float] = None
    fat_g_kgdm: Optional[float] = None
    omd_method: Optional[str] = None


class CompoundFeedParsed(BaseModel):
    """Gesamtresultat einer Etikettenauswertung."""
    source_filename: str
    source_type: str
    product_name: str
    supplier_name: Optional[str] = None
    declared_analysis: CompoundFeedDeclaredAnalysis
    composition: List[CompoundFeedComponent]
    gfe2023_estimate: CompoundFeedGfeEstimate
    optimizer_feed: Dict[str, Any]
    warnings: List[str]
    raw_text_preview: str
