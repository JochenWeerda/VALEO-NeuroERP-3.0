from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional

class NutrientRequirements(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
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
        }
    })

    dmi_kg: float = Field(..., gt=0, description="Dry matter intake in kg per cow per day")
    me_min_mj: float = Field(..., ge=0, description="Minimum metabolizable energy requirement in MJ per day")
    sidp_min_g: float = Field(..., ge=0, description="Minimum small intestine digestible protein requirement in g per day")
    andfom_min_g: float = Field(..., ge=0, description="Minimum ash-neutral detergent fiber organic matter requirement in g per day")
    andfom_max_g: float = Field(..., ge=0, description="Maximum ash-neutral detergent fiber organic matter allowance in g per day")
    starch_max_g: float = Field(..., ge=0, description="Maximum starch allowance in g per day")
    sugar_max_g: float = Field(..., ge=0, description="Maximum sugar allowance in g per day")
    fat_max_g: float = Field(..., ge=0, description="Maximum fat allowance in g per day")
    ca_min_g: float = Field(..., ge=0, description="Minimum calcium requirement in g per day")
    p_min_g: float = Field(..., ge=0, description="Minimum phosphorus requirement in g per day")
    na_min_g: float = Field(..., ge=0, description="Minimum sodium requirement in g per day")
    forage_share_min: float = Field(..., ge=0, le=1, description="Minimum forage share of DMI (0-1)")

    @validator('andfom_max_g')
    def andfom_max_must_be_greater_than_min(cls, v, values):
        if 'andfom_min_g' in values and v < values['andfom_min_g']:
            raise ValueError('andfom_max_g must be greater than or equal to andfom_min_g')
        return v
