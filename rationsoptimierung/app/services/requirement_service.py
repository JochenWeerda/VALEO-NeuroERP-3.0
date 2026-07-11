"""
Requirement service – Nährstoffbedarfe nach GfE-2023-Näherungsformeln (siehe app.nutrition.gfe2023).
"""
import logging

from ..schemas.requirement import NutrientRequirements
from ..domain.models import CowProfile
from ..nutrition import gfe2023

logger = logging.getLogger(__name__)


class RequirementService:
    """Bedarfskalkulation aus Kuhprofil (GfE 2023, öffentlich dokumentierte Kernelemente)."""

    def calculate_requirements(self, cow_profile: CowProfile) -> NutrientRequirements:
        """
        Nährstoffbedarf laktierende Milchkuh.

        Energie: ME_Erhalt = 0,64 × LM^0,75; ME_Milch = ECM × (3,15/0,66) mit
        ECM ≈ Milch × (0,337 + 0,116×Fett% + 0,06×Eiweiß%).

        sidP, Minerale, FAN-vollständige Aufnahme: Näherungen – Handbuch GfE 2023 für Tabellen.
        """
        logger.info(
            "Bedarfskalkulation GfE-2023-Näherung: %s, %.1f kg Milch/Tag",
            cow_profile.breed,
            cow_profile.milk_kg_day,
        )

        if cow_profile.target_dmi_kg is not None:
            dmi_kg = cow_profile.target_dmi_kg
        else:
            dmi_kg = gfe2023.estimate_dmi_lactating_kg(
                cow_profile.body_weight_kg,
                cow_profile.milk_kg_day,
                cow_profile.lactation_stage_days,
            )

        me_total, _me_m, _me_l = gfe2023.total_me_requirement_mj(
            cow_profile.body_weight_kg,
            cow_profile.milk_kg_day,
            cow_profile.milk_fat_pct,
            cow_profile.milk_protein_pct,
            getattr(cow_profile, "milk_lactose_pct", gfe2023.ECM_REFERENCE_LACTOSE_PCT),
        )
        sidp_total, _, _ = gfe2023.sidp_requirement_g(
            cow_profile.body_weight_kg,
            cow_profile.milk_kg_day,
            cow_profile.milk_protein_pct,
        )
        bounds = gfe2023.fiber_and_concentrate_bounds_g(dmi_kg)
        ca_min_g, p_min_g, na_min_g = gfe2023.minerals_ca_p_na_g(
            cow_profile.body_weight_kg,
            cow_profile.milk_kg_day,
        )

        return NutrientRequirements(
            dmi_kg=round(dmi_kg, 1),
            me_min_mj=round(me_total, 1),
            sidp_min_g=round(sidp_total),
            andfom_min_g=round(bounds["andfom_min_g"]),
            andfom_max_g=round(bounds["andfom_max_g"]),
            starch_max_g=round(bounds["starch_max_g"]),
            sugar_max_g=round(bounds["sugar_max_g"]),
            fat_max_g=round(bounds["fat_max_g"]),
            ca_min_g=round(ca_min_g, 1),
            p_min_g=round(p_min_g, 1),
            na_min_g=round(na_min_g, 2),
            forage_share_min=gfe2023.FORAGE_SHARE_MIN_LACTATING,
        )

    def get_maintenance_requirements(self, body_weight_kg: float) -> NutrientRequirements:
        """Erhaltungsbedarf Trockensteher (keine Milchleistung)."""
        dmi_kg = body_weight_kg * 0.019
        me_min_mj = gfe2023.energy_maintenance_me_mj(body_weight_kg)
        sidp_total, _, _ = gfe2023.sidp_requirement_g(body_weight_kg, 0.0, 0.0)
        bounds = gfe2023.fiber_bounds_dry_cow_g(dmi_kg)
        ca_min_g, p_min_g, na_min_g = gfe2023.minerals_ca_p_na_g(body_weight_kg, 0.0)

        return NutrientRequirements(
            dmi_kg=round(dmi_kg, 1),
            me_min_mj=round(me_min_mj, 1),
            sidp_min_g=round(sidp_total),
            andfom_min_g=round(bounds["andfom_min_g"]),
            andfom_max_g=round(bounds["andfom_max_g"]),
            starch_max_g=round(bounds["starch_max_g"]),
            sugar_max_g=round(bounds["sugar_max_g"]),
            fat_max_g=round(bounds["fat_max_g"]),
            ca_min_g=round(ca_min_g, 1),
            p_min_g=round(p_min_g, 1),
            na_min_g=round(na_min_g, 2),
            forage_share_min=gfe2023.FORAGE_SHARE_MIN_DRY,
        )
