"""
Futtermittel-Stammdaten & Rezepte API

Liefert Einzelfuttermittel-, Mischfuttermittel- und Rezept-Stammdaten.
Demo-Seed-Daten werden inline bereitgestellt, bis persistente Modelle existieren.
"""

from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["futter", "stammdaten"])


# ── Schemas ─────────────────────────────────────────────────────

class EinzelfuttermittelDetail(BaseModel):
    id: str
    artikel: str
    art: str
    herkunft: str
    lieferant: str
    protein: float
    energie: float
    gvo_status: str
    qs_milch: bool
    verfuegbar: float


class MischfutterKomponente(BaseModel):
    komponente: str
    anteil: float


class MischfuttermittelDetail(BaseModel):
    id: str
    typ: str
    tierart: str
    leistungsstufe: str
    rezeptur: list[MischfutterKomponente]
    protein: float
    energie: float


class RezeptKomponente(BaseModel):
    id: str
    name: str
    anteil: float


class RezeptDetail(BaseModel):
    id: str
    name: str
    tierart: str
    komponenten: list[RezeptKomponente]
    protein: float
    energie: float


# ── Demo-Seed-Daten ─────────────────────────────────────────────

_EINZELFUTTER_SEED: dict[str, EinzelfuttermittelDetail] = {
    "EF-001": EinzelfuttermittelDetail(
        id="EF-001",
        artikel="Sojaschrot 44% Protein",
        art="Eiweißfutter",
        herkunft="Brasilien",
        lieferant="Agrar Import GmbH",
        protein=44.0,
        energie=13.2,
        gvo_status="gvo-frei-zertifiziert",
        qs_milch=True,
        verfuegbar=150,
    ),
    "EF-002": EinzelfuttermittelDetail(
        id="EF-002",
        artikel="Rapsschrot",
        art="Eiweißfutter",
        herkunft="Deutschland",
        lieferant="Raiffeisen Waren GmbH",
        protein=35.0,
        energie=11.5,
        gvo_status="gvo-frei",
        qs_milch=True,
        verfuegbar=280,
    ),
}

_MISCHFUTTER_SEED: dict[str, MischfuttermittelDetail] = {
    "MF-001": MischfuttermittelDetail(
        id="MF-001",
        typ="Milchviehfutter Hochleistung",
        tierart="Rind (Milch)",
        leistungsstufe="Hochleistung (>30 l/Tag)",
        rezeptur=[
            MischfutterKomponente(komponente="Sojaschrot 44%", anteil=25),
            MischfutterKomponente(komponente="Weizen", anteil=30),
            MischfutterKomponente(komponente="Mais", anteil=20),
            MischfutterKomponente(komponente="Mineralfutter", anteil=5),
        ],
        protein=18.5,
        energie=11.8,
    ),
    "MF-002": MischfuttermittelDetail(
        id="MF-002",
        typ="Schweinemastfutter Phase 2",
        tierart="Schwein (Mast)",
        leistungsstufe="Mittelmast (60-90 kg)",
        rezeptur=[
            MischfutterKomponente(komponente="Gerste", anteil=40),
            MischfutterKomponente(komponente="Weizen", anteil=25),
            MischfutterKomponente(komponente="Sojaschrot 44%", anteil=18),
            MischfutterKomponente(komponente="Mineralfutter", anteil=3),
        ],
        protein=16.0,
        energie=13.0,
    ),
}

_REZEPT_SEED: dict[str, RezeptDetail] = {
    "REZ-001": RezeptDetail(
        id="REZ-001",
        name="Milchviehfutter Hochleistung",
        tierart="Rind (Milch)",
        komponenten=[
            RezeptKomponente(id="1", name="Sojaschrot 44%", anteil=25),
            RezeptKomponente(id="2", name="Weizen", anteil=30),
            RezeptKomponente(id="3", name="Mais", anteil=20),
            RezeptKomponente(id="4", name="Mineralfutter", anteil=5),
        ],
        protein=18.5,
        energie=11.8,
    ),
    "REZ-002": RezeptDetail(
        id="REZ-002",
        name="Legehennenfutter Standard",
        tierart="Geflügel (Legehenne)",
        komponenten=[
            RezeptKomponente(id="1", name="Weizen", anteil=35),
            RezeptKomponente(id="2", name="Mais", anteil=25),
            RezeptKomponente(id="3", name="Sojaschrot 44%", anteil=20),
            RezeptKomponente(id="4", name="Kalk", anteil=8),
            RezeptKomponente(id="5", name="Mineralfutter", anteil=4),
        ],
        protein=17.0,
        energie=11.2,
    ),
}


# ── Endpoints ───────────────────────────────────────────────────

@router.get(
    "/einzelfuttermittel/{futter_id}",
    response_model=EinzelfuttermittelDetail,
    summary="Einzelfuttermittel-Stammdaten abrufen",
)
async def get_einzelfuttermittel(
    futter_id: str,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
):
    item = _EINZELFUTTER_SEED.get(futter_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Einzelfuttermittel '{futter_id}' nicht gefunden")
    return item


@router.get(
    "/mischfuttermittel/{misch_id}",
    response_model=MischfuttermittelDetail,
    summary="Mischfuttermittel-Stammdaten abrufen",
)
async def get_mischfuttermittel(
    misch_id: str,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
):
    item = _MISCHFUTTER_SEED.get(misch_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Mischfuttermittel '{misch_id}' nicht gefunden")
    return item


@router.get(
    "/rezepte/{rezept_id}",
    response_model=RezeptDetail,
    summary="Rezept-Stammdaten abrufen",
)
async def get_rezept(
    rezept_id: str,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
):
    item = _REZEPT_SEED.get(rezept_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Rezept '{rezept_id}' nicht gefunden")
    return item
