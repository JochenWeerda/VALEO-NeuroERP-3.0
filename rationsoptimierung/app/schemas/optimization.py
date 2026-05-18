from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional, Dict, Any
from .feed import FeedIngredient
from .requirement import NutrientRequirements
from ..domain.models import CowProfile

class OptimizationOptions(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "objective": "least_cost",
            "allow_infeasible_soft_constraints": False,
            "export_dual_values": False,
            "export_slacks": False,
            "max_solver_time_sec": 30,
            "solver_name": "CBC"
        }
    })

    objective: str = Field(default="least_cost", description="Optimization objective")
    allow_infeasible_soft_constraints: bool = Field(default=False, description="Allow soft constraints for infeasible problems")
    export_dual_values: bool = Field(default=False, description="Export dual values from solution")
    export_slacks: bool = Field(default=False, description="Export slack variables from solution")
    max_solver_time_sec: int = Field(default=30, gt=0, description="Maximum solver time in seconds")
    solver_name: str = Field(default="CBC", description="Solver to use (CBC, GLPK, etc.)")


class OptimizationRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "cow_profile": {
                "breed": "Holstein",
                "body_weight_kg": 650,
                "milk_kg_day": 35,
                "milk_fat_pct": 3.8,
                "milk_protein_pct": 3.2,
                "lactation_stage_days": 150,
                "parity": 2,
                "target_dmi_kg": 22.0
            },
            "requirements": {
                "dmi_kg": 22.0,
                "me_min_mj": 220.0,
                "sidp_min_g": 3200,
                "andfom_min_g": 5500,
                "andfom_max_g": 7500,
                "starch_max_g": 4000,
                "sugar_max_g": 1000,
                "fat_max_g": 1200,
                "ca_min_g": 100,
                "p_min_g": 60,
                "na_min_g": 8,
                "forage_share_min": 0.4
            },
            "feeds": [
                {
                    "id": "grassilage",
                    "name": "Grassilage",
                    "group": "forage",
                    "dm_frac": 0.35,
                    "price_eur_kgdm": 0.15,
                    "me_mj_kgdm": 10.5,
                    "sidp_g_kgdm": 180,
                    "andfom_g_kgdm": 450,
                    "starch_g_kgdm": 20,
                    "sugar_g_kgdm": 15,
                    "fat_g_kgdm": 30,
                    "ca_g_kgdm": 6,
                    "p_g_kgdm": 3,
                    "na_g_kgdm": 1,
                    "min_kgdm": 0.0,
                    "max_kgdm": 15.0,
                    "active": True
                }
            ],
            "options": {
                "objective": "least_cost",
                "allow_infeasible_soft_constraints": False,
                "export_dual_values": False,
                "export_slacks": False,
                "max_solver_time_sec": 30,
                "solver_name": "CBC"
            }
        }
    })

    cow_profile: CowProfile = Field(..., description="Profile of the cow to optimize ration for")
    requirements: NutrientRequirements = Field(..., description="Nutrient requirements for the cow")
    feeds: List[FeedIngredient] = Field(..., min_items=1, description="Available feed ingredients")
    options: OptimizationOptions = Field(default_factory=OptimizationOptions, description="Optimization options")


class OptimizeFromProfileRequest(BaseModel):
    """Body für POST /optimize/from-profile: Kuhprofil, optional Futtermittel-IDs und Solver-Optionen."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "cow_profile": {
                "breed": "Holstein",
                "body_weight_kg": 650,
                "milk_kg_day": 35,
                "milk_fat_pct": 3.8,
                "milk_protein_pct": 3.2,
                "lactation_stage_days": 150,
                "parity": 2,
            },
            "feeds": ["grassilage", "maissilage", "sojaschrot"],
        }
    })

    cow_profile: CowProfile = Field(..., description="Kuhprofil (Bedarfe werden per GfE-Näherung berechnet)")
    feeds: Optional[List[str]] = Field(
        None,
        description="Liste von Futtermittel-IDs; leer/weg lassen = alle aktiven Futtermittel des Mandanten",
    )
    options: Optional[OptimizationOptions] = Field(None, description="Solver- und Laufoptionen")


class RationItem(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "feed_id": "grassilage",
            "name": "Grassilage",
            "kgdm": 8.0,
            "kgfm": 22.9,
            "unit_cost": 0.15,
            "total_cost": 1.2
        }
    })

    feed_id: str = Field(..., description="Identifier of the feed ingredient")
    name: str = Field(..., description="Name of the feed ingredient")
    kgdm: float = Field(..., ge=0, description="Amount in kg dry matter per cow per day")
    kgfm: float = Field(..., ge=0, description="Amount in kg fresh matter per cow per day")
    unit_cost: float = Field(..., ge=0, description="Cost per kg dry matter in EUR")
    total_cost: float = Field(..., ge=0, description="Total cost per cow per day in EUR")

    @validator('kgfm')
    def kgfm_must_be_consistent_with_kgdm(cls, v, values):
        if 'kgdm' in values and 'feed_id' in values:
            if v < values['kgdm']:
                raise ValueError('kgfm must be greater than or equal to kgdm')
        return v


class NutrientSupply(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "dmi_kg": 22.0,
            "me_mj": 225.5,
            "sidp_g": 3350,
            "andfom_g": 6200,
            "starch_g": 3200,
            "sugar_g": 800,
            "fat_g": 950,
            "ca_g": 105,
            "p_g": 62,
            "na_g": 9,
            "forage_share_pct": 45.5
        }
    })

    dmi_kg: float = Field(..., ge=0, description="Total dry matter intake in kg per day")
    me_mj: float = Field(..., ge=0, description="Metabolizable energy supplied in MJ per day")
    sidp_g: float = Field(..., ge=0, description="Small intestine digestible protein supplied in g per day")
    andfom_g: float = Field(..., ge=0, description="Ash-neutral detergent fiber organic matter supplied in g per day")
    starch_g: float = Field(..., ge=0, description="Starch supplied in g per day")
    sugar_g: float = Field(..., ge=0, description="Sugar supplied in g per day")
    fat_g: float = Field(..., ge=0, description="Fat supplied in g per day")
    ca_g: float = Field(..., ge=0, description="Calcium supplied in g per day")
    p_g: float = Field(..., ge=0, description="Phosphorus supplied in g per day")
    na_g: float = Field(..., ge=0, description="Sodium supplied in g per day")
    forage_share_pct: float = Field(..., ge=0, le=100, description="Forage share of DMI as percentage")


class ConstraintReportItem(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Dry Matter Intake",
            "target": 22.0,
            "actual": 22.0,
            "difference": 0.0,
            "fulfilled": True,
            "status": "OK"
        }
    })

    name: str = Field(..., description="Name of the constraint")
    target: float = Field(..., description="Target value for the constraint")
    actual: float = Field(..., description="Actual value achieved")
    difference: float = Field(..., description="Difference between actual and target")
    fulfilled: bool = Field(..., description="Whether the constraint is fulfilled")
    status: str = Field(..., description="Status description (e.g., 'OK', 'MIN_NOT_MET', 'MAX_EXCEEDED')")


class OptimizationResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status": "optimal",
            "objective_value": 3.45,
            "total_cost_eur_day": 3.45,
            "ration_items": [
                {
                    "feed_id": "grassilage",
                    "name": "Grassilage",
                    "kgdm": 8.0,
                    "kgfm": 22.9,
                    "unit_cost": 0.15,
                    "total_cost": 1.2
                },
                {
                    "feed_id": "maissilage",
                    "name": "Maissilage",
                    "kgdm": 6.0,
                    "kgfm": 20.0,
                    "unit_cost": 0.12,
                    "total_cost": 0.72
                }
            ],
            "nutrient_supply": {
                "dmi_kg": 22.0,
                "me_mj": 225.5,
                "sidp_g": 3350,
                "andfom_g": 6200,
                "starch_g": 3200,
                "sugar_g": 800,
                "fat_g": 950,
                "ca_g": 105,
                "p_g": 62,
                "na_g": 9,
                "forage_share_pct": 45.5
            },
            "constraint_report": [
                {
                    "name": "Dry Matter Intake",
                    "target": 22.0,
                    "actual": 22.0,
                    "difference": 0.0,
                    "fulfilled": True,
                    "status": "OK"
                },
                {
                    "name": "Metabolizable Energy",
                    "target": 220.0,
                    "actual": 225.5,
                    "difference": 5.5,
                    "fulfilled": True,
                    "status": "OK"
                }
            ],
            "warnings": [],
            "metadata": {
                "solver": "CBC",
                "solve_time_sec": 0.8,
                "iterations": 42
            }
        }
    })

    status: str = Field(..., description="Optimization status (optimal, infeasible, unbounded, etc.)")
    objective_value: Optional[float] = Field(None, description="Objective function value (total cost)")
    total_cost_eur_day: Optional[float] = Field(None, ge=0, description="Total cost per cow per day in EUR")
    ration_items: List[RationItem] = Field(default_factory=list, description="Optimized ration items")
    nutrient_supply: NutrientSupply = Field(..., description="Nutrients supplied by the optimized ration")
    constraint_report: List[ConstraintReportItem] = Field(default_factory=list, description="Report on constraint fulfillment")
    warnings: List[str] = Field(default_factory=list, description="Warnings about the solution")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the optimization")
