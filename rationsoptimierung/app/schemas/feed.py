from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum

class FeedGroup(str, Enum):
    FORAGE = "forage"
    CONCENTRATE = "concentrate"
    PROTEIN = "protein"
    MINERAL = "mineral"
    OTHER = "other"

class FeedIngredient(BaseModel):
    id: str = Field(..., description="Unique identifier for the feed ingredient")
    name: str = Field(..., min_length=1, description="Name of the feed ingredient")
    group: FeedGroup = Field(..., description="Feed group classification")
    dm_frac: float = Field(..., gt=0, le=1, description="Dry matter fraction (0-1)")
    price_eur_kgdm: float = Field(..., ge=0, description="Price per kg dry matter in EUR")
    me_mj_kgdm: float = Field(..., ge=0, description="Metabolizable energy per kg DM in MJ")
    sidp_g_kgdm: float = Field(..., ge=0, description="Small intestine digestible protein per kg DM in g")
    andfom_g_kgdm: float = Field(..., ge=0, description="Ash-neutral detergent fiber organic matter per kg DM in g")
    starch_g_kgdm: float = Field(..., ge=0, description="Starch per kg DM in g")
    sugar_g_kgdm: float = Field(..., ge=0, description="Sugar per kg DM in g")
    fat_g_kgdm: float = Field(..., ge=0, description="Fat per kg DM in g")
    ca_g_kgdm: float = Field(..., ge=0, description="Calcium per kg DM in g")
    p_g_kgdm: float = Field(..., ge=0, description="Phosphorus per kg DM in g")
    na_g_kgdm: float = Field(..., ge=0, description="Sodium per kg DM in g")
    min_kgdm: float = Field(..., ge=0, description="Minimum usage in kg DM per cow per day")
    max_kgdm: float = Field(..., ge=0, description="Maximum usage in kg DM per cow per day")
    active: bool = Field(default=True, description="Whether the feed ingredient is active")
    
    @validator('max_kgdm')
    def max_must_be_greater_than_min(cls, v, values):
        if 'min_kgdm' in values and v < values['min_kgdm']:
            raise ValueError('max_kgdm must be greater than or equal to min_kgdm')
        return v
    
    class Config:
        schema_extra = {
            "example": {
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
        }