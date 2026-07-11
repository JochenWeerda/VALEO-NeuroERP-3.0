from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from enum import Enum

class Breed(str, Enum):
    HOLSTEIN = "Holstein"
    JERSEY = "Jersey"
    BROWN_SWISS = "Brown Swiss"
    OTHER = "Other"

class LactationStage(str, Enum):
    EARLY = "early"  # 0-100 days
    MID = "mid"      # 101-200 days
    LATE = "late"    # 201-305 days
    DRY = "dry"      # >305 days or dry period

class CowProfile(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "breed": "Holstein",
            "body_weight_kg": 650,
            "milk_kg_day": 35,
            "milk_fat_pct": 3.8,
            "milk_protein_pct": 3.2,
            "lactation_stage_days": 150,
            "parity": 2,
            "target_dmi_kg": 22.0
        }
    })

    breed: Breed = Field(default=Breed.HOLSTEIN, description="Breed of the cow")
    body_weight_kg: float = Field(..., gt=0, description="Body weight in kg")
    milk_kg_day: float = Field(..., ge=0, description="Milk production in kg per day")
    milk_fat_pct: float = Field(..., ge=0, le=10, description="Milk fat percentage")
    milk_protein_pct: float = Field(..., ge=0, le=10, description="Milk protein percentage")
    milk_lactose_pct: float = Field(
        default=4.8, ge=0, le=10,
        description="Milk lactose percentage (DLG 01|2025 ECM reference 4.8%)",
    )
    lactation_stage_days: int = Field(..., ge=0, description="Days in lactation")
    parity: int = Field(..., ge=1, description="Lactation number (1 = first lactation)")
    target_dmi_kg: Optional[float] = Field(None, gt=0, description="Target dry matter intake in kg per day (if known)")

    @validator('lactation_stage_days')
    def lactation_stage_must_be_reasonable(cls, v):
        if v > 500:  # More than ~16 months is unusual
            raise ValueError('lactation_stage_days seems unreasonably high')
        return v

class AnimalGroup(BaseModel):
    """Represents a group of animals with similar characteristics"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "high_yield_group",
            "name": "High Yield Holstein Group",
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
            "animal_count": 50
        }
    })

    id: str = Field(..., description="Unique identifier for the animal group")
    name: str = Field(..., min_length=1, description="Name of the animal group")
    cow_profile: CowProfile = Field(..., description="Profile of cows in this group")
    animal_count: int = Field(..., gt=0, description="Number of animals in the group")
