"""
Vergleich: gleicher Futtermittelkorb + gleiches Kuhprofil, zwei Bedarfssätze.

- „Legacy“: frühere Heuristik im Projekt (0,48 MJ Erhaltung, 5,3 MJ/kg Milch, sidP 2/65,
  Faser aus % LM, Mineralien wie früher im RequirementService).
- „GfE 2023“: aktueller RequirementService (app.nutrition.gfe2023).

Ausgabe: optimierte kg TM pro Futtermittel und Summenkennzahlen.
NEL wird nicht verwendet; beide Läufe nutzen ME im LP.

Aufruf (aus Ordner rationsoptimierung):
  python scripts/compare_legacy_vs_gfe_ration.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.domain.models import CowProfile, Breed  # noqa: E402
from app.schemas.requirement import NutrientRequirements  # noqa: E402
from app.schemas.optimization import OptimizationOptions  # noqa: E402
from app.services.feed_service import FeedService  # noqa: E402
from app.services.requirement_service import RequirementService  # noqa: E402
from app.optimization.solver import OptimizationService  # noqa: E402


def _legacy_requirements(cp: CowProfile) -> NutrientRequirements:
    """Entspricht der alten Heuristik vor Umstellung auf gfe2023 (nur für Vergleich)."""
    if cp.target_dmi_kg is not None:
        dmi_kg = cp.target_dmi_kg
    else:
        maintenance_dmi = cp.body_weight_kg * 0.038
        production_dmi = cp.milk_kg_day * 0.45
        dmi_kg = maintenance_dmi + production_dmi
        if cp.lactation_stage_days <= 0:
            lactation_factor = 0.8
        elif cp.lactation_stage_days <= 100:
            lactation_factor = 0.8 + (cp.lactation_stage_days / 100) * 0.2
        elif cp.lactation_stage_days <= 200:
            lactation_factor = 1.0
        elif cp.lactation_stage_days <= 305:
            lactation_factor = 1.0 - ((cp.lactation_stage_days - 200) / 105) * 0.1
        else:
            lactation_factor = 0.85
        dmi_kg *= lactation_factor

    maintenance_me = 0.48 * (cp.body_weight_kg**0.75)
    lactation_me = 5.3 * cp.milk_kg_day
    me_min_mj = maintenance_me + lactation_me

    milk_protein_kg = cp.milk_kg_day * (cp.milk_protein_pct / 100.0)
    maintenance_sidp = 2.0 * (cp.body_weight_kg**0.75)
    lactation_sidp = 65.0 * milk_protein_kg
    sidp_min_g = maintenance_sidp + lactation_sidp

    andfom_min_g = cp.body_weight_kg * 11.0
    andfom_max_g = cp.body_weight_kg * 18.0
    starch_max_g = dmi_kg * 150.0
    sugar_max_g = dmi_kg * 50.0
    fat_max_g = dmi_kg * 80.0
    ca_min_g = (cp.milk_kg_day * 2.5) + (cp.body_weight_kg * 0.05)
    p_min_g = (cp.milk_kg_day * 1.8) + (cp.body_weight_kg * 0.03)
    na_min_g = (cp.milk_kg_day * 0.18) + (cp.body_weight_kg * 0.005)

    return NutrientRequirements(
        dmi_kg=round(dmi_kg, 1),
        me_min_mj=round(me_min_mj, 1),
        sidp_min_g=round(sidp_min_g),
        andfom_min_g=round(andfom_min_g),
        andfom_max_g=round(andfom_max_g),
        starch_max_g=round(starch_max_g),
        sugar_max_g=round(sugar_max_g),
        fat_max_g=round(fat_max_g),
        ca_min_g=round(ca_min_g),
        p_min_g=round(p_min_g),
        na_min_g=round(na_min_g),
        forage_share_min=0.4,
    )


def _solution_kgdm(result) -> dict[str, float]:
    return {item.feed_id: item.kgdm for item in result.ration_items}


def _legacy_me_sidp_only_on_gfe_shell(cp: CowProfile, gfe_req: NutrientRequirements) -> NutrientRequirements:
    """Gleiche Nebenbedingungen wie GfE (Faser, Stärke, Mineralien, TM), nur ME/sidP aus Legacy-Heuristik."""
    maintenance_me = 0.48 * (cp.body_weight_kg**0.75)
    lactation_me = 5.3 * cp.milk_kg_day
    me_min_mj = round(maintenance_me + lactation_me, 1)
    milk_protein_kg = cp.milk_kg_day * (cp.milk_protein_pct / 100.0)
    sidp_min_g = round(2.0 * (cp.body_weight_kg**0.75) + 65.0 * milk_protein_kg)
    return gfe_req.model_copy(
        update={
            "me_min_mj": me_min_mj,
            "sidp_min_g": sidp_min_g,
        }
    )


def main() -> None:
    cp = CowProfile(
        breed=Breed.HOLSTEIN,
        body_weight_kg=650,
        milk_kg_day=35,
        milk_fat_pct=3.8,
        milk_protein_pct=3.2,
        lactation_stage_days=150,
        parity=2,
        target_dmi_kg=22.0,
    )
    feeds = FeedService().get_all_feeds(active_only=True, tenant_id="default")
    opt = OptimizationService()
    options = OptimizationOptions()

    leg_req = _legacy_requirements(cp)
    gfe_req = RequirementService().calculate_requirements(cp)
    leg_iso = _legacy_me_sidp_only_on_gfe_shell(cp, gfe_req)

    print("=== Bedarf (Legacy vs GfE 2023) ===")
    print(f"  DMI kg:     {leg_req.dmi_kg}  |  {gfe_req.dmi_kg}")
    print(f"  ME min MJ:  {leg_req.me_min_mj}  |  {gfe_req.me_min_mj}")
    print(f"  sidP min g: {leg_req.sidp_min_g}  |  {gfe_req.sidp_min_g}")
    print(f"  aNDFom g:   {leg_req.andfom_min_g:.0f}-{leg_req.andfom_max_g:.0f}  |  {gfe_req.andfom_min_g:.0f}-{gfe_req.andfom_max_g:.0f}")
    print(f"  Stärke max: {leg_req.starch_max_g:.0f}  |  {gfe_req.starch_max_g:.0f}")
    print(f"  Ca/P/Na:    {leg_req.ca_min_g:.0f}/{leg_req.p_min_g:.0f}/{leg_req.na_min_g:.1f}  |  {gfe_req.ca_min_g:.1f}/{gfe_req.p_min_g:.1f}/{gfe_req.na_min_g:.2f}")
    print()
    print("=== Iso-Shell (nur ME + sidP Legacy, übrige Bounds = GfE) ===")
    print(f"  ME min MJ:  {leg_iso.me_min_mj}  |  GfE {gfe_req.me_min_mj}")
    print(f"  sidP min g: {leg_iso.sidp_min_g}  |  GfE {gfe_req.sidp_min_g}")
    print()

    r_leg_full = opt.optimize_ration(feeds, leg_req, options)
    r_leg_iso = opt.optimize_ration(feeds, leg_iso, options)
    r_gfe = opt.optimize_ration(feeds, gfe_req, options)
    print(
        f"Status Legacy (voll): {r_leg_full.status}  |  Legacy (iso): {r_leg_iso.status}  |  GfE: {r_gfe.status}"
    )
    if r_leg_iso.status != "optimal" or r_gfe.status != "optimal":
        print("(Kein vollständiger Mengenvergleich bei nicht-optimalem Status.)")
        return

    k_leg = _solution_kgdm(r_leg_iso)
    k_gfe = _solution_kgdm(r_gfe)
    ids = sorted(set(k_leg) | set(k_gfe) | {f.id for f in feeds})

    print("\n=== kg TM pro Futtermittel: Legacy-ME/sidP (iso) -> GfE, Delta ===")
    print(f"{'Futtermittel':<22} {'L-iso':>8} {'GfE23':>8} {'Delta':>8}")
    for fid in ids:
        a = k_leg.get(fid, 0.0)
        b = k_gfe.get(fid, 0.0)
        if a < 0.001 and b < 0.001:
            continue
        name = next((f.name for f in feeds if f.id == fid), fid)
        print(f"{name[:21]:<22} {a:8.3f} {b:8.3f} {b - a:+8.3f}")

    forage_ids = {f.id for f in feeds if f.group.value == "forage"}

    def forage_share(d: dict[str, float]) -> float:
        fdm = sum(d.get(i, 0) for i in forage_ids)
        tot = sum(d.values())
        return 100.0 * fdm / tot if tot > 0 else 0.0

    print("\n=== Kennzahlen (iso vs GfE) ===")
    print(f"  Raufutteranteil % TM:  {forage_share(k_leg):5.1f}  ->  {forage_share(k_gfe):5.1f}")
    print(f"  Kosten EUR/Kuh/Tag:    {r_leg_iso.total_cost_eur_day or 0:.3f}  ->  {r_gfe.total_cost_eur_day or 0:.3f}")
    print(f"  ME angeboten MJ:       {r_leg_iso.nutrient_supply.me_mj:.2f}  ->  {r_gfe.nutrient_supply.me_mj:.2f}")
    print(f"  sidP angeboten g:      {r_leg_iso.nutrient_supply.sidp_g:.1f}  ->  {r_gfe.nutrient_supply.sidp_g:.1f}")


if __name__ == "__main__":
    main()
