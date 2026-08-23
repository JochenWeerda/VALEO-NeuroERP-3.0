"""Response-Schemas fuer die Dev-Mock-Harness (EXTERNAL-MOCK-HARNESS-001).

SPEC-P1-06 Welle 2: ersetzt ``response_model=dict[str, Any]`` in
``app/api/v1/endpoints/external_mock_harness.py``.

Die Rueckgaben von ``ExternalMockHarnessService`` sind vollstaendig im Code
konstruiert und deterministisch, die Feldlisten daher exakt ableitbar. Jede
Antwort traegt ``simulated: true`` — das Feld ist der Vertrag der Harness und
darf nie wegtypisiert werden.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class SimulatedResponse(BaseSchema):
    """Gemeinsamer Kopf aller Mock-Antworten."""

    simulated: bool = Field(
        default=True, description="Immer true — kennzeichnet die Antwort als simuliert"
    )
    system: Optional[str] = Field(
        default=None, description="datev | tse | dsfinvk | elster | dms | bank_camt"
    )
    action: Optional[str] = Field(default=None, description="Ausgefuehrte Mock-Operation")
    hinweis: Optional[str] = Field(
        default=None, description="Klartext-Hinweis, dass kein echtes Fremdsystem beteiligt war"
    )


class MockSystemOut(BaseSchema):
    """Eintrag der Systemuebersicht."""

    system: Optional[str] = None
    verfuegbar: Optional[bool] = None
    beschreibung: Optional[str] = None


class SystemsOverviewOut(SimulatedResponse):
    """``GET /dev/external-mocks/``"""

    systems: list[MockSystemOut] = Field(default_factory=list)


class DatevExportStartOut(SimulatedResponse):
    """``POST /dev/external-mocks/datev/export``"""

    job_id: Optional[str] = None
    mandant_nr: Optional[str] = None
    zeitraum_von: Optional[str] = None
    zeitraum_bis: Optional[str] = None
    status: Optional[str] = None
    estimated_completion: Optional[str] = Field(
        default=None, description="Voraussichtlicher Abschluss (ISO)"
    )


class DatevExportStatusOut(SimulatedResponse):
    """``GET /dev/external-mocks/datev/export/{job_id}``"""

    job_id: Optional[str] = None
    status: Optional[str] = None
    datei_name: Optional[str] = None
    datei_groesse_kb: Optional[int] = None
    uebertragen_am: Optional[str] = None


class TseSignOut(SimulatedResponse):
    """``POST /dev/external-mocks/tse/sign``"""

    kasse_id: Optional[str] = None
    bon_nr: Optional[str] = None
    signatur: Optional[str] = None
    transaktions_nr: Optional[int] = None
    zertifikat_id: Optional[str] = None
    signiert_am: Optional[str] = None


class DsfinvkExportOut(SimulatedResponse):
    """``POST /dev/external-mocks/dsfinvk/export``"""

    export_id: Optional[str] = None
    kasse_id: Optional[str] = None
    abschluss_datum: Optional[str] = None
    dateien: list[str] = Field(default_factory=list, description="Dateien des DSFinV-K-Pakets")
    status: Optional[str] = None


class ElsterSubmitOut(SimulatedResponse):
    """``POST /dev/external-mocks/elster/submit``"""

    ticket_id: Optional[str] = None
    steuer_nr: Optional[str] = None
    formular_typ: Optional[str] = None
    zeitraum: Optional[str] = None
    status: Optional[str] = None
    eingegangen_am: Optional[str] = None
    rueckgabe_code: Optional[str] = Field(default=None, description="ERiC-Rueckgabecode, '0' = ok")


class ElsterStatusOut(SimulatedResponse):
    """``GET /dev/external-mocks/elster/status/{ticket_id}``"""

    ticket_id: Optional[str] = None
    status: Optional[str] = None
    bearbeitet_am: Optional[str] = None


class DmsUploadOut(SimulatedResponse):
    """``POST /dev/external-mocks/dms/upload``"""

    dokument_id: Optional[str] = None
    titel: Optional[str] = None
    dokument_typ: Optional[str] = None
    status: Optional[str] = None
    archiviert_am: Optional[str] = None


class DmsSearchHitOut(BaseSchema):
    """Treffer der simulierten DMS-Suche."""

    dokument_id: Optional[str] = None
    titel: Optional[str] = None
    erstellt_am: Optional[str] = None


class DmsSearchOut(SimulatedResponse):
    """``GET /dev/external-mocks/dms/search``"""

    treffer: list[DmsSearchHitOut] = Field(default_factory=list)


class CamtBookingOut(BaseSchema):
    """Buchung aus dem simulierten CAMT.053-Import."""

    buchungs_id: Optional[str] = None
    betrag_eur: Optional[float] = None
    valuta: Optional[str] = None
    verwendungszweck: Optional[str] = None
    gegenkonto: Optional[str] = None


class BankCamtImportOut(SimulatedResponse):
    """``POST /dev/external-mocks/bank/camt-import``"""

    iban: Optional[str] = None
    kontoauszug_nr: Optional[int] = None
    buchungen: list[CamtBookingOut] = Field(default_factory=list)
