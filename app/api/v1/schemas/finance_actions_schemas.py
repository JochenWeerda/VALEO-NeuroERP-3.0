"""Pydantic schemas for the finance actions domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ActionResponse(BaseModel):
    """Standard response for finance actions"""
    success: bool = True
    message: str = ""


class JournalEntryPostRequest(BaseModel):
    """Request to post a journal entry by ID"""
    journal_entry_id: Optional[str] = Field(None, description="ID der zu buchenden Buchung")
    belegnummer: Optional[str] = Field(None, description="Alternative Belegnummer zur Ermittlung der Buchungs-ID")


class BankReconciliationRunRequest(BaseModel):
    """Request to run bank reconciliation"""
    bank_account_id: str = Field(..., description="Bankkonto-ID")
    statement_id: Optional[str] = Field(None, description="Optional: Kontoauszug-ID")


class ClosingActionRequest(BaseModel):
    period: str = Field(..., min_length=1)
    closing_type: str = Field(..., min_length=1)
    actor: str = Field(..., min_length=1)


class ClosingRunRequest(BaseModel):
    period: str = Field(..., description="Periode im Format YYYY-MM")
    closing_type: str = Field("month", description="month | quarter | year")


class BuchungsuebergabeExportRequest(BaseModel):
    """Request für ASC-Buchungsübergabe an die Finanzbuchhaltung."""
    von: date = Field(..., description="Startdatum (inkl.)")
    bis: date = Field(..., description="Enddatum (inkl.)")
    bediener: Optional[str] = Field(None, description="Beediener-Kürzel (leer = alle)")
    sortierung: str = Field(
        "datum",
        description="Sortierung: 'datum' = Buch.-Datum+Rechnung-Nr., 'rechnungsnr' = Rechnung-Nr.+Datum",
    )
    buchungsarten: Optional[List[str]] = Field(
        None, description="Filter auf bestimmte Buchungsarten (leer = alle)"
    )
    download: bool = Field(
        True, description="True = Dateidownload, False = JSON-Zusammenfassung"
    )

