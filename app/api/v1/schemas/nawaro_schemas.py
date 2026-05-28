"""Pydantic schemas for the nawaro domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class NawaroNotificationIn(BaseModel):
    document_name: str = Field(..., min_length=3, max_length=255)
    harvest_year: int = Field(..., ge=2000, le=2100)
    article_number: str | None = Field(default=None, max_length=80)
    debtor_from: str | None = Field(default=None, max_length=80)
    debtor_to: str | None = Field(default=None, max_length=80)
    delivery_option: DeliveryOption = 'vollstaendige_ablieferung'
    form_code: str = Field(default='W12151', min_length=2, max_length=40)
    copies: int = Field(default=1, ge=1, le=999)
    printer_name: str | None = Field(default=None, max_length=255)


class NawaroNotificationOut(NawaroNotificationIn):
    id: str
    created_at: str | None = None
    updated_at: str | None = None


class NawaroContractRowIn(BaseModel):
    contract_number: str | None = None
    customer_name: str | None = None
    name_1: str | None = None
    total_area: str | None = None
    standard_quantity: str | None = None
    delivery_count: int | None = Field(default=None, ge=0)
    delivery_resource: str | None = None
    quantity_b: str | None = None
    harvest_declaration: str | None = None


class NawaroContractRowOut(NawaroContractRowIn):
    id: str


class NawaroContractSheetIn(BaseModel):
    harvest_year: int = Field(..., ge=2000, le=2100)
    article_number: str | None = Field(default=None, max_length=80)
    is_summer: bool = True
    is_winter: bool = False
    rows: list[NawaroContractRowIn] = Field(default_factory=list)


class NawaroContractSheetOut(NawaroContractSheetIn):
    id: str
    rows: list[NawaroContractRowOut]
    created_at: str | None = None
    updated_at: str | None = None


class NawaroAreaRowIn(BaseModel):
    customer_name: str | None = None
    name_1: str | None = None
    name_2: str | None = None
    postal_code: str | None = None
    city: str | None = None
    phone: str | None = None
    fax: str | None = None
    area_2022: str | None = None
    area_2023: str | None = None
    area_2024: str | None = None
    area_2025: str | None = None
    area_2026: str | None = None


class NawaroAreaRowOut(NawaroAreaRowIn):
    id: str


class NawaroAreaSheetIn(BaseModel):
    harvest_year_from: int = Field(..., ge=2000, le=2100)
    harvest_year_to: int = Field(..., ge=2000, le=2100)
    article_number: str | None = Field(default=None, max_length=80)
    is_summer: bool = True
    is_winter: bool = False
    form_code: str = Field(default='W12071', min_length=2, max_length=40)
    rows: list[NawaroAreaRowIn] = Field(default_factory=list)


class NawaroAreaSheetOut(NawaroAreaSheetIn):
    id: str
    rows: list[NawaroAreaRowOut]
    created_at: str | None = None
    updated_at: str | None = None

