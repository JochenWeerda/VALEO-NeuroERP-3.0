"""Ein- und Ausgabe des Kontraktabrufs.

Bis zum 05.10.2026 hingen alle fuenf Dispositionswege an `KontraktOut` mit
``extra="allow"`` — einem Modell, das alles erlaubt und deshalb nichts
beschreibt. Das Anlegen gab die ganze Zeile zurueck, die Freigabe
`{id, status}`, die Lieferung `{id, status, wiegeschein_nr}`, und alles galt als
dasselbe.

`DispositionCreate` in ``kontrakte_schemas.py`` nahm ausserdem Felder an, die der
Abruf nicht selbst bestimmt: `lieferdatum` (das entsteht bei der Lieferung),
`freigabe` (das ist der Zustand) und `wiegeschein_nr` (der kommt mit der
Lieferung). Sie fehlen hier mit Absicht.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DispositionAnlegen(BaseModel):
    """Ein Abruf einer kontrahierten Menge."""

    model_config = ConfigDict(extra="forbid")

    kontrakt_pos_nr: int = Field(default=1, ge=1)
    menge: float = Field(gt=0, description="Abgerufene Menge in der Kontrakteinheit")
    geplantes_lieferdatum: Optional[date] = None
    bemerkung: Optional[str] = None
    erfasst_durch: Optional[str] = None


class DispositionGeliefert(BaseModel):
    """Die Lieferung eines Abrufs.

    Die Wiegescheinnummer wird gegen das Wiegeregister aufgeloest. Eine Nummer
    ohne Schein ist kein Beleg und damit keine Lieferung.
    """

    model_config = ConfigDict(extra="forbid")

    wiegeschein_nr: Optional[str] = None
    lieferdatum: Optional[date] = None


class DispositionOut(BaseModel):
    id: str
    tenant_id: str
    kontrakt_id: str
    kontrakt_nr: str
    kontrakt_pos_nr: int
    disposition_nr: int
    geplantes_lieferdatum: Optional[str] = None
    lieferdatum: Optional[str] = None
    menge: float
    status: str
    #: Abgeleitet aus dem Zustand, nicht gespeichert.
    freigabe: bool
    wiegeschein_id: Optional[str] = None
    bemerkung: Optional[str] = None
    erfasst_durch: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AbrufstandOut(BaseModel):
    """Was von einer Kontraktposition noch abrufbar ist."""

    kontrakt_id: str
    kontrakt_nr: str
    kontrakt_pos_nr: int
    menge_kontrahiert: float
    menge_abgerufen: float
    menge_offen: float
    ueberlieferung_erlaubt: bool
