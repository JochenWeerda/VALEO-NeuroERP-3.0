"""
Vergleich: alte Vilomix-Ration (12.03.2024, NEL-basierte Futtermittel-/Auswertelogik in der PDF)
vs. unsere Bedarfsrechnung GfE 2023 (ME) + lineare Optimierung.

Wichtig: **NEL und ME sind verschiedene Größen und dürfen nicht gleichgesetzt oder 1:1
substituiert werden.** Die PDF nennt u. a. NEL MJ/kg TM; unser Bedarf und LP nutzen **ME**
nach GfE-2023-Kernlogik. Vergleiche erfolgen nur über **separat angenommene oder deklarierte
ME-Werte** der Futtermittel (Testmatrix), niemals durch Übernahme von NEL-Zahlen als ME.

Die GfE-2023-Formeln in app.nutrition.gfe2023 werden hier nicht verändert.
"""
from __future__ import annotations

import pytest

from app.domain.models import CowProfile, Breed
from app.schemas.feed import FeedIngredient, FeedGroup
from app.schemas.optimization import OptimizationOptions
from app.optimization.solver import OptimizationService
from app.services.requirement_service import RequirementService
from app.nutrition import gfe2023


# --- Aus PDF „Rationsberechnung … 12.03.2024“ (kg Produkt × TM-% → kg TM) ---
# TM-% Spalten: AWS 38,4 %, Mais 36 %, MLF 87 %, ZRPS 21,8 %, Kartoffelpülpe 18 %,
# Soja 88,6 %, Triticale 88 %, Megalac 98 %; Wasser vernachlässigt.
PDF_KG_DM: dict[str, float] = {
    "aws_schnitt": 22.00 * 0.384,
    "maissilage_2023": 21.00 * 0.36,
    "mlf_standard_20_4": 1.50 * 0.87,
    "zr_pressschnitzel_22tm": 8.00 * 0.218,
    "kartoffelpulpe": 3.25 * 0.18,
    "sojaschrot_extr": 3.00 * 0.886,
    "triticale": 1.50 * 0.88,
    "megalac": 0.07 * 0.98,
}


def _sum_pdf_tm() -> float:
    return round(sum(PDF_KG_DM.values()), 3)


def _vilofoss_like_feeds() -> list[FeedIngredient]:
    """
    Vilomix-ähnliche Futtermittel für das LP (ME/SIDP/Rohfaser-Konsistenz, keine Formeländerung).
    Nährwerte grob orientiert an typischen Silagen/Konzentraten; Preise nur für Zielfunktion.
    """
    return [
        FeedIngredient(
            id="aws_schnitt",
            name="AWS 2 Schnitt (wie PDF)",
            group=FeedGroup.FORAGE,
            dm_frac=0.384,
            price_eur_kgdm=0.16,
            me_mj_kgdm=10.6,
            sidp_g_kgdm=185,
            andfom_g_kgdm=440,
            starch_g_kgdm=25,
            sugar_g_kgdm=45,
            fat_g_kgdm=32,
            ca_g_kgdm=6.0,
            p_g_kgdm=3.0,
            na_g_kgdm=1.0,
            min_kgdm=0.0,
            max_kgdm=14.0,
            active=True,
        ),
        FeedIngredient(
            id="maissilage_2023",
            name="Maissilage 2023 (wie PDF)",
            group=FeedGroup.FORAGE,
            dm_frac=0.36,
            price_eur_kgdm=0.13,
            me_mj_kgdm=11.0,
            sidp_g_kgdm=85,
            andfom_g_kgdm=240,
            # Stärke: im LP als „wirksame“ Stärke niedriger als Rohstärke (Verdauung); sonst
            # Stärke-Deckel + hoher Maisanteil → schnell unlösbar trotz realer Ration.
            starch_g_kgdm=260,
            sugar_g_kgdm=22,
            fat_g_kgdm=26,
            ca_g_kgdm=2.2,
            p_g_kgdm=2.2,
            na_g_kgdm=1.0,
            min_kgdm=0.0,
            max_kgdm=12.0,
            active=True,
        ),
        FeedIngredient(
            id="rapsstroh",
            name="Rapsstroh (Zusatz Raufutter, niedrige Stärke)",
            group=FeedGroup.FORAGE,
            dm_frac=0.90,
            price_eur_kgdm=0.06,
            me_mj_kgdm=6.2,
            sidp_g_kgdm=40,
            andfom_g_kgdm=480,
            starch_g_kgdm=12,
            sugar_g_kgdm=10,
            fat_g_kgdm=14,
            ca_g_kgdm=4.0,
            p_g_kgdm=2.0,
            na_g_kgdm=1.0,
            min_kgdm=0.0,
            max_kgdm=3.5,
            active=True,
        ),
        FeedIngredient(
            id="mlf_standard_20_4",
            name="MLF-Standard 20/4 (wie PDF)",
            group=FeedGroup.CONCENTRATE,
            dm_frac=0.87,
            price_eur_kgdm=0.55,
            me_mj_kgdm=11.5,
            sidp_g_kgdm=200,
            andfom_g_kgdm=80,
            starch_g_kgdm=180,
            sugar_g_kgdm=220,
            fat_g_kgdm=65,
            ca_g_kgdm=9.0,
            p_g_kgdm=6.5,
            na_g_kgdm=3.5,
            min_kgdm=0.0,
            max_kgdm=3.0,
            active=True,
        ),
        FeedIngredient(
            id="zr_pressschnitzel_22tm",
            name="Zuckerrübenpressschnitzel (wie PDF)",
            group=FeedGroup.CONCENTRATE,
            dm_frac=0.218,
            price_eur_kgdm=0.10,
            me_mj_kgdm=12.2,
            sidp_g_kgdm=35,
            andfom_g_kgdm=120,
            starch_g_kgdm=50,
            sugar_g_kgdm=200,
            fat_g_kgdm=12,
            ca_g_kgdm=2.5,
            p_g_kgdm=0.25,
            na_g_kgdm=0.15,
            min_kgdm=0.0,
            max_kgdm=4.0,
            active=True,
        ),
        FeedIngredient(
            id="kartoffelpulpe",
            name="Kartoffelpülpe (wie PDF)",
            group=FeedGroup.CONCENTRATE,
            dm_frac=0.18,
            price_eur_kgdm=0.09,
            me_mj_kgdm=12.5,
            sidp_g_kgdm=60,
            andfom_g_kgdm=100,
            starch_g_kgdm=200,
            sugar_g_kgdm=280,
            fat_g_kgdm=12,
            ca_g_kgdm=1.0,
            p_g_kgdm=1.0,
            na_g_kgdm=1.0,
            min_kgdm=0.0,
            max_kgdm=2.0,
            active=True,
        ),
        FeedIngredient(
            id="sojaschrot_extr",
            name="Sojaschrot extr. (wie PDF)",
            group=FeedGroup.PROTEIN,
            dm_frac=0.886,
            price_eur_kgdm=0.48,
            me_mj_kgdm=12.2,
            sidp_g_kgdm=380,
            andfom_g_kgdm=120,
            starch_g_kgdm=35,
            sugar_g_kgdm=12,
            fat_g_kgdm=22,
            ca_g_kgdm=3.0,
            p_g_kgdm=6.5,
            na_g_kgdm=0.5,
            min_kgdm=0.0,
            max_kgdm=5.0,
            active=True,
        ),
        FeedIngredient(
            id="triticale",
            name="Triticale (wie PDF)",
            group=FeedGroup.CONCENTRATE,
            dm_frac=0.88,
            price_eur_kgdm=0.19,
            me_mj_kgdm=13.0,
            sidp_g_kgdm=115,
            andfom_g_kgdm=40,
            starch_g_kgdm=580,
            sugar_g_kgdm=22,
            fat_g_kgdm=18,
            ca_g_kgdm=0.6,
            p_g_kgdm=3.4,
            na_g_kgdm=0.5,
            min_kgdm=0.0,
            max_kgdm=3.5,
            active=True,
        ),
        FeedIngredient(
            id="megalac",
            name="Megalac (wie PDF)",
            group=FeedGroup.CONCENTRATE,
            dm_frac=0.98,
            price_eur_kgdm=1.15,
            me_mj_kgdm=35.0,
            sidp_g_kgdm=0.0,
            andfom_g_kgdm=0.0,
            starch_g_kgdm=0.0,
            sugar_g_kgdm=0.0,
            fat_g_kgdm=990.0,
            ca_g_kgdm=0.0,
            p_g_kgdm=0.0,
            na_g_kgdm=0.0,
            min_kgdm=0.0,
            max_kgdm=0.45,
            active=True,
        ),
        FeedIngredient(
            id="nacl_lick",
            name="Speisesalz (Na-Ergänzung)",
            group=FeedGroup.MINERAL,
            dm_frac=1.0,
            price_eur_kgdm=0.18,
            me_mj_kgdm=0.0,
            sidp_g_kgdm=0.0,
            andfom_g_kgdm=0.0,
            starch_g_kgdm=0.0,
            sugar_g_kgdm=0.0,
            fat_g_kgdm=0.0,
            ca_g_kgdm=0.0,
            p_g_kgdm=0.0,
            na_g_kgdm=393.0,
            min_kgdm=0.0,
            max_kgdm=0.12,
            active=True,
        ),
        FeedIngredient(
            id="mineralfutter_vilomix",
            name="Mineral (ergänzend, LP)",
            group=FeedGroup.MINERAL,
            dm_frac=0.90,
            price_eur_kgdm=0.52,
            me_mj_kgdm=0.0,
            sidp_g_kgdm=0.0,
            andfom_g_kgdm=0.0,
            starch_g_kgdm=0.0,
            sugar_g_kgdm=0.0,
            fat_g_kgdm=0.0,
            ca_g_kgdm=250.0,
            p_g_kgdm=120.0,
            na_g_kgdm=100.0,
            min_kgdm=0.05,
            max_kgdm=0.55,
            active=True,
        ),
    ]


@pytest.fixture
def cow_pdf_tiergruppe() -> CowProfile:
    """Zeile Tiergruppe aus der PDF: 650 kg, ~49 kg Milch, Fett/Eiweiß."""
    return CowProfile(
        breed=Breed.HOLSTEIN,
        body_weight_kg=650.0,
        milk_kg_day=49.28,
        milk_fat_pct=4.08,
        milk_protein_pct=3.25,
        lactation_stage_days=120,
        parity=2,
    )


def test_pdf_tm_splits_sum_matches_document():
    assert _sum_pdf_tm() == pytest.approx(23.691, abs=0.02)


def test_gfe2023_me_requirement_high_performance_cow(cow_pdf_tiergruppe):
    me_tot, me_m, me_l = gfe2023.total_me_requirement_mj(
        cow_pdf_tiergruppe.body_weight_kg,
        cow_pdf_tiergruppe.milk_kg_day,
        cow_pdf_tiergruppe.milk_fat_pct,
        cow_pdf_tiergruppe.milk_protein_pct,
    )
    assert me_m == pytest.approx(gfe2023.energy_maintenance_me_mj(650.0), rel=1e-4)
    assert me_tot > 300.0
    assert me_l > me_m


def test_pdf_static_mix_me_from_feed_declarations_vs_gfe2023_me_need(cow_pdf_tiergruppe):
    """
    Energiebilanz ohne NEL: Summe (kg TM_i × ME_i) aus **dieser Test-Futtermittelmatrix**
    (me_mj_kgdm = umsetzbare Energie pro kg TM, nicht aus der PDF-NEL abgeleitet).
    So lässt sich die PDF-Mischung gegen den **GfE-2023-ME-Bedarf** abgrenzen, ohne
    NEL fälschlich als ME zu verwenden.
    """
    req = RequirementService().calculate_requirements(
        cow_pdf_tiergruppe.model_copy(update={"target_dmi_kg": _sum_pdf_tm()})
    )
    feed_by_id = {f.id: f for f in _vilofoss_like_feeds()}
    me_supply_mj = sum(PDF_KG_DM[fid] * feed_by_id[fid].me_mj_kgdm for fid in PDF_KG_DM)
    assert me_supply_mj < req.me_min_mj - 5.0


def test_lp_vilofoss_like_basket_optimal_under_gfe2023(cow_pdf_tiergruppe):
    """
    Lineare Optimierung: gleicher Kuh-Typ wie PDF, geschätzte TM (kein Fix auf 23,7 kg),
    vilomix-ähnlicher Korb → erwartbar zulässig und kostenoptimal.
    Zusätzlich: hoher Raufutteranteil (wie in der PDF-Ration überwiegend Silagen).
    """
    rs = RequirementService()
    requirements = rs.calculate_requirements(cow_pdf_tiergruppe)
    feeds = _vilofoss_like_feeds()
    res = OptimizationService().optimize_ration(feeds, requirements, OptimizationOptions())

    assert res.status == "optimal"
    assert res.nutrient_supply.me_mj >= requirements.me_min_mj - 0.05
    assert res.nutrient_supply.sidp_g >= requirements.sidp_min_g - 1.0
    # PDF: überwiegend AWS + Mais (~16 kg TM von ~23,7) → > 60 % Raufutter
    assert res.nutrient_supply.forage_share_pct >= 55.0


def test_pdf_exact_tm_split_not_guaranteed_feasible_under_gfe2023_constraints(cow_pdf_tiergruppe):
    """
    Die historische Vilomix-Ration (NEL-Auswertung) mit exakt den PDF-TM-Mengen ist unter
    unserem vollen LP mit GfE-2023-Bedarfsrahmen (ME, sidP-Näherung, aNDFom-, Stärke-,
    Mineral-Grenzen) typischerweise **nicht** zulässig – das ist kein LP-Fehler, sondern
    zeigt den Methoden-/Rahmenwechsel (Bedarfsrahmen ME nach GfE 2023 vs. ältere NEL-Auswertung
    in der PDF, unterschiedliche Mineral-/Nebenbedingungen). Die lineare Optimierung mit
    angepasstem Futtermittelkorb bleibt
    dagegen lösbar (s. test_lp_vilofoss_like_basket_optimal_under_gfe2023).
    """
    feeds = []
    for f in _vilofoss_like_feeds():
        if f.id not in PDF_KG_DM:
            kg = 0.0
        else:
            kg = PDF_KG_DM[f.id]
        feeds.append(f.model_copy(update={"min_kgdm": kg, "max_kgdm": kg}))

    rs = RequirementService()
    requirements = rs.calculate_requirements(
        cow_pdf_tiergruppe.model_copy(update={"target_dmi_kg": _sum_pdf_tm()})
    )
    res = OptimizationService().optimize_ration(feeds, requirements, OptimizationOptions())
    assert res.status == "infeasible"
