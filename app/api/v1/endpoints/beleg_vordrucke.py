"""Belegformular-Vordruck-Editor (Admin) — Druckvorlagen für Papier/PDF-Ausdrucke.

Vorlagen (Wiegeschein, Stundenzettel, Fahrtenbuch, Belege, Gutscheine,
Rabatt-Coupons, Info-Schreiben, Handouts, Sackanhänger, ...) werden als
Elementliste mit mm-Koordinaten gespeichert und über reportlab als PDF
gerendert. Datenfelder ({{key}}) werden beim Rendern aus den übergebenen
Daten bzw. den Beispieldaten der Vorlage aufgelöst.
"""

from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/admin/vordrucke", tags=["admin", "vordrucke", "druck"])


VordruckKategorie = Literal[
    "wiegeschein", "stundenzettel", "fahrtenbuch", "beleg", "gutschein",
    "rabatt_coupon", "info_schreiben", "handout", "sackanhaenger", "sonstig",
]

Papierformat = Literal["A4", "A5", "A6", "label_100x50", "label_60x30"]

# Seitengrößen in mm (Breite, Höhe) im Hochformat
_FORMATE_MM: dict[str, tuple[float, float]] = {
    "A4": (210, 297),
    "A5": (148, 210),
    "A6": (105, 148),
    "label_100x50": (100, 50),
    "label_60x30": (60, 30),
}


class VordruckElement(BaseModel):
    """Ein Layout-Element auf dem Vordruck (Koordinaten in mm, Ursprung oben links)."""
    typ: Literal["text", "feld", "linie", "rechteck", "qrcode"]
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    breite: float = Field(default=50, gt=0)
    hoehe: float = Field(default=8, gt=0)
    # text: statischer Text; feld: Platzhalter-Key ({{key}} in text erlaubt)
    text: Optional[str] = None
    feld_key: Optional[str] = None
    font_size: float = Field(default=10, gt=0, le=72)
    bold: bool = False
    align: Literal["left", "center", "right"] = "left"


class VordruckBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    kategorie: VordruckKategorie = "sonstig"
    beschreibung: Optional[str] = None
    papierformat: Papierformat = "A4"
    ausrichtung: Literal["hoch", "quer"] = "hoch"
    layout: list[VordruckElement] = []
    beispieldaten: dict[str, Any] = {}
    aktiv: bool = True


class VordruckCreate(VordruckBase):
    pass


class VordruckOut(VordruckBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class RenderRequest(BaseModel):
    daten: dict[str, Any] = {}


def _row_to_out(row: Any) -> VordruckOut:
    layout_raw = row["layout"]
    beispiel_raw = row["beispieldaten"]
    return VordruckOut(
        id=row["id"],
        name=row["name"],
        kategorie=row["kategorie"],
        beschreibung=row["beschreibung"],
        papierformat=row["papierformat"],
        ausrichtung=row["ausrichtung"],
        layout=[VordruckElement(**e) for e in (layout_raw if isinstance(layout_raw, list) else json.loads(layout_raw or "[]"))],
        beispieldaten=beispiel_raw if isinstance(beispiel_raw, dict) else json.loads(beispiel_raw or "{}"),
        aktiv=row["aktiv"],
        created_at=row["created_at"].isoformat() if row["created_at"] else None,
        updated_at=row["updated_at"].isoformat() if row["updated_at"] else None,
    )


def _get_or_404(db: Session, vordruck_id: str, tenant_id: str) -> Any:
    row = db.execute(
        text("SELECT * FROM domain_shared.beleg_vordrucke WHERE id = :id AND tenant_id = :tid"),
        {"id": vordruck_id, "tid": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Vordruck nicht gefunden")
    return row


@router.get("", response_model=list[VordruckOut], summary="Vordrucke auflisten")
def list_vordrucke(
    kategorie: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    where = "tenant_id = :tid" + (" AND kategorie = :kat" if kategorie else "")
    params: dict[str, Any] = {"tid": tenant_id}
    if kategorie:
        params["kat"] = kategorie
    rows = db.execute(
        text(f"SELECT * FROM domain_shared.beleg_vordrucke WHERE {where} ORDER BY kategorie, name"),  # nosec B608 — where aus Code-Konstanten
        params,
    ).mappings().all()
    return [_row_to_out(r) for r in rows]


@router.post("", response_model=VordruckOut, status_code=201, summary="Vordruck anlegen")
def create_vordruck(
    payload: VordruckCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = str(uuid7())
    db.execute(
        text(
            "INSERT INTO domain_shared.beleg_vordrucke "
            "(id, tenant_id, name, kategorie, beschreibung, papierformat, ausrichtung, "
            " layout, beispieldaten, aktiv) "
            "VALUES (:id, :tid, :name, :kat, :beschr, :format, :ausr, "
            " :layout::jsonb, :beispiel::jsonb, :aktiv)"
        ),
        {
            "id": new_id, "tid": tenant_id, "name": payload.name,
            "kat": payload.kategorie, "beschr": payload.beschreibung,
            "format": payload.papierformat, "ausr": payload.ausrichtung,
            "layout": json.dumps([e.model_dump() for e in payload.layout]),
            "beispiel": json.dumps(payload.beispieldaten),
            "aktiv": payload.aktiv,
        },
    )
    db.commit()
    return _row_to_out(_get_or_404(db, new_id, tenant_id))


@router.get("/{vordruck_id}", response_model=VordruckOut, summary="Vordruck abrufen")
def get_vordruck(
    vordruck_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    return _row_to_out(_get_or_404(db, vordruck_id, tenant_id))


@router.put("/{vordruck_id}", response_model=VordruckOut, summary="Vordruck aktualisieren")
def update_vordruck(
    vordruck_id: str,
    payload: VordruckCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    _get_or_404(db, vordruck_id, tenant_id)
    db.execute(
        text(
            "UPDATE domain_shared.beleg_vordrucke SET name=:name, kategorie=:kat, "
            "beschreibung=:beschr, papierformat=:format, ausrichtung=:ausr, "
            "layout=:layout::jsonb, beispieldaten=:beispiel::jsonb, aktiv=:aktiv, "
            "updated_at=NOW() WHERE id=:id AND tenant_id=:tid"
        ),
        {
            "id": vordruck_id, "tid": tenant_id, "name": payload.name,
            "kat": payload.kategorie, "beschr": payload.beschreibung,
            "format": payload.papierformat, "ausr": payload.ausrichtung,
            "layout": json.dumps([e.model_dump() for e in payload.layout]),
            "beispiel": json.dumps(payload.beispieldaten),
            "aktiv": payload.aktiv,
        },
    )
    db.commit()
    return _row_to_out(_get_or_404(db, vordruck_id, tenant_id))


@router.delete("/{vordruck_id}", status_code=204, response_class=Response, summary="Vordruck löschen")
def delete_vordruck(
    vordruck_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    _get_or_404(db, vordruck_id, tenant_id)
    db.execute(
        text("DELETE FROM domain_shared.beleg_vordrucke WHERE id=:id AND tenant_id=:tid"),
        {"id": vordruck_id, "tid": tenant_id},
    )
    db.commit()
    return Response(status_code=204)


@router.post("/{vordruck_id}/duplizieren", response_model=VordruckOut, status_code=201, summary="Vordruck duplizieren")
def duplicate_vordruck(
    vordruck_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = _get_or_404(db, vordruck_id, tenant_id)
    original = _row_to_out(row)
    kopie = VordruckCreate(
        **{**original.model_dump(exclude={"id", "created_at", "updated_at"}),
           "name": f"{original.name} (Kopie)"}
    )
    return create_vordruck(kopie, db, tenant_id)


# ── PDF-Rendering ────────────────────────────────────────────────────────────

def _resolve_text(element: VordruckElement, daten: dict[str, Any]) -> str:
    """Feld-Keys auflösen: feld nutzt feld_key, text ersetzt {{key}}-Platzhalter."""
    if element.typ == "feld":
        key = element.feld_key or ""
        value = daten.get(key, f"{{{{{key}}}}}")
        return str(value)
    raw = element.text or ""
    for key, value in daten.items():
        raw = raw.replace(f"{{{{{key}}}}}", str(value))
    return raw


def _render_pdf(vordruck: VordruckOut, daten: dict[str, Any]) -> bytes:
    try:
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas as pdf_canvas
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail="reportlab nicht verfügbar") from exc

    breite_mm, hoehe_mm = _FORMATE_MM.get(vordruck.papierformat, _FORMATE_MM["A4"])
    if vordruck.ausrichtung == "quer":
        breite_mm, hoehe_mm = hoehe_mm, breite_mm

    buf = BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=(breite_mm * mm, hoehe_mm * mm))

    merged = {**vordruck.beispieldaten, **daten}

    for el in vordruck.layout:
        # Vordruck-Koordinaten: Ursprung oben links → PDF: unten links
        x_pt = el.x * mm
        y_pt = (hoehe_mm - el.y - el.hoehe) * mm

        if el.typ in ("text", "feld"):
            inhalt = _resolve_text(el, merged)
            font = "Helvetica-Bold" if el.bold else "Helvetica"
            c.setFont(font, el.font_size)
            # Text an der Oberkante des Elements ausrichten
            text_y = (hoehe_mm - el.y) * mm - el.font_size
            if el.align == "center":
                c.drawCentredString(x_pt + (el.breite * mm) / 2, text_y, inhalt)
            elif el.align == "right":
                c.drawRightString(x_pt + el.breite * mm, text_y, inhalt)
            else:
                c.drawString(x_pt, text_y, inhalt)
        elif el.typ == "linie":
            line_y = (hoehe_mm - el.y) * mm
            c.setLineWidth(max(el.hoehe * mm / 4, 0.3))
            c.line(x_pt, line_y, x_pt + el.breite * mm, line_y)
        elif el.typ == "rechteck":
            c.setLineWidth(0.5)
            c.rect(x_pt, y_pt, el.breite * mm, el.hoehe * mm, stroke=1, fill=0)
        elif el.typ == "qrcode":
            try:
                from reportlab.graphics import renderPDF
                from reportlab.graphics.barcode.qr import QrCodeWidget
                from reportlab.graphics.shapes import Drawing

                inhalt = _resolve_text(el, merged) or "VALEO"
                widget = QrCodeWidget(inhalt)
                bounds = widget.getBounds()
                w = bounds[2] - bounds[0]
                h = bounds[3] - bounds[1]
                d = Drawing(
                    el.breite * mm, el.hoehe * mm,
                    transform=[el.breite * mm / w, 0, 0, el.hoehe * mm / h, 0, 0],
                )
                d.add(widget)
                renderPDF.draw(d, c, x_pt, y_pt)
            except Exception:  # noqa: BLE001 — QR optional: Platzhalter-Rechteck statt Crash
                c.rect(x_pt, y_pt, el.breite * mm, el.hoehe * mm, stroke=1, fill=0)
                c.setFont("Helvetica", 6)
                c.drawCentredString(x_pt + el.breite * mm / 2, y_pt + el.hoehe * mm / 2, "QR")

    c.showPage()
    c.save()
    return buf.getvalue()


@router.post("/{vordruck_id}/render", summary="Vordruck als PDF rendern")
def render_vordruck(
    vordruck_id: str,
    payload: RenderRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    vordruck = _row_to_out(_get_or_404(db, vordruck_id, tenant_id))
    pdf = _render_pdf(vordruck, payload.daten)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{vordruck.name}.pdf"'},
    )


# ── Standard-Vorlagen ────────────────────────────────────────────────────────

def _standard_vorlagen() -> list[VordruckCreate]:
    kopf = [
        VordruckElement(typ="text", x=10, y=8, breite=120, hoehe=8, text="{{firma}}", font_size=14, bold=True),
        VordruckElement(typ="linie", x=10, y=20, breite=190, hoehe=1),
    ]
    return [
        VordruckCreate(
            name="Wiegeschein Standard", kategorie="wiegeschein", papierformat="A5", ausrichtung="quer",
            beschreibung="Wiegeschein mit Erst-/Zweitwiegung, Netto und Charge",
            layout=[
                VordruckElement(typ="text", x=10, y=8, breite=100, hoehe=8, text="{{firma}}", font_size=13, bold=True),
                VordruckElement(typ="text", x=150, y=8, breite=50, hoehe=6, text="Wiegeschein {{wiegeschein_nr}}", font_size=10, bold=True, align="right"),
                VordruckElement(typ="linie", x=10, y=18, breite=190, hoehe=1),
                VordruckElement(typ="text", x=10, y=24, breite=40, hoehe=6, text="Datum:", font_size=9),
                VordruckElement(typ="feld", x=45, y=24, breite=50, hoehe=6, feld_key="datum", font_size=9),
                VordruckElement(typ="text", x=10, y=32, breite=40, hoehe=6, text="Lieferant/Kunde:", font_size=9),
                VordruckElement(typ="feld", x=45, y=32, breite=100, hoehe=6, feld_key="partner", font_size=9),
                VordruckElement(typ="text", x=10, y=40, breite=40, hoehe=6, text="Artikel:", font_size=9),
                VordruckElement(typ="feld", x=45, y=40, breite=100, hoehe=6, feld_key="artikel", font_size=9),
                VordruckElement(typ="text", x=10, y=48, breite=40, hoehe=6, text="Kennzeichen:", font_size=9),
                VordruckElement(typ="feld", x=45, y=48, breite=50, hoehe=6, feld_key="kennzeichen", font_size=9),
                VordruckElement(typ="text", x=10, y=60, breite=40, hoehe=6, text="Erstwiegung (kg):", font_size=9),
                VordruckElement(typ="feld", x=60, y=60, breite=30, hoehe=6, feld_key="erstwiegung_kg", font_size=9, align="right"),
                VordruckElement(typ="text", x=10, y=68, breite=40, hoehe=6, text="Zweitwiegung (kg):", font_size=9),
                VordruckElement(typ="feld", x=60, y=68, breite=30, hoehe=6, feld_key="zweitwiegung_kg", font_size=9, align="right"),
                VordruckElement(typ="text", x=10, y=76, breite=40, hoehe=6, text="Netto (kg):", font_size=10, bold=True),
                VordruckElement(typ="feld", x=60, y=76, breite=30, hoehe=6, feld_key="netto_kg", font_size=10, bold=True, align="right"),
                VordruckElement(typ="text", x=110, y=60, breite=30, hoehe=6, text="Charge:", font_size=9),
                VordruckElement(typ="feld", x=130, y=60, breite=40, hoehe=6, feld_key="charge", font_size=9),
                VordruckElement(typ="qrcode", x=165, y=95, breite=25, hoehe=25, text="{{wiegeschein_nr}}"),
                VordruckElement(typ="linie", x=10, y=125, breite=60, hoehe=1),
                VordruckElement(typ="text", x=10, y=128, breite=60, hoehe=5, text="Unterschrift Waage", font_size=7),
                VordruckElement(typ="linie", x=90, y=125, breite=60, hoehe=1),
                VordruckElement(typ="text", x=90, y=128, breite=60, hoehe=5, text="Unterschrift Fahrer", font_size=7),
            ],
            beispieldaten={
                "firma": "Hinrich Folkerts GmbH & Co. KG", "wiegeschein_nr": "WS-2026-04711",
                "datum": "02.07.2026", "partner": "Berkhout Dirk C.", "artikel": "Weizen B-Qualität",
                "kennzeichen": "LER-AB 123", "erstwiegung_kg": "24.480", "zweitwiegung_kg": "10.220",
                "netto_kg": "14.260", "charge": "CH-2026-0815",
            },
        ),
        VordruckCreate(
            name="Stundenzettel Standard", kategorie="stundenzettel", papierformat="A4",
            beschreibung="Wöchentlicher Stundenzettel mit Unterschriftsfeldern",
            layout=kopf + [
                VordruckElement(typ="text", x=10, y=26, breite=100, hoehe=8, text="Stundenzettel KW {{kw}}", font_size=12, bold=True),
                VordruckElement(typ="text", x=10, y=38, breite=30, hoehe=6, text="Mitarbeiter:", font_size=10),
                VordruckElement(typ="feld", x=45, y=38, breite=80, hoehe=6, feld_key="mitarbeiter", font_size=10),
                VordruckElement(typ="text", x=120, y=38, breite=30, hoehe=6, text="Personal-Nr.:", font_size=10),
                VordruckElement(typ="feld", x=150, y=38, breite=40, hoehe=6, feld_key="personal_nr", font_size=10),
                VordruckElement(typ="rechteck", x=10, y=50, breite=190, hoehe=120),
                VordruckElement(typ="text", x=12, y=52, breite=30, hoehe=6, text="Tag", font_size=9, bold=True),
                VordruckElement(typ="text", x=50, y=52, breite=30, hoehe=6, text="Beginn", font_size=9, bold=True),
                VordruckElement(typ="text", x=85, y=52, breite=30, hoehe=6, text="Ende", font_size=9, bold=True),
                VordruckElement(typ="text", x=120, y=52, breite=30, hoehe=6, text="Pause", font_size=9, bold=True),
                VordruckElement(typ="text", x=155, y=52, breite=30, hoehe=6, text="Stunden", font_size=9, bold=True),
                VordruckElement(typ="linie", x=10, y=60, breite=190, hoehe=1),
                VordruckElement(typ="linie", x=10, y=250, breite=70, hoehe=1),
                VordruckElement(typ="text", x=10, y=253, breite=70, hoehe=5, text="Unterschrift Mitarbeiter", font_size=8),
                VordruckElement(typ="linie", x=120, y=250, breite=70, hoehe=1),
                VordruckElement(typ="text", x=120, y=253, breite=70, hoehe=5, text="Unterschrift Vorgesetzter", font_size=8),
            ],
            beispieldaten={"firma": "Hinrich Folkerts GmbH & Co. KG", "kw": "27/2026", "mitarbeiter": "Anna Schulte", "personal_nr": "P-0042"},
        ),
        VordruckCreate(
            name="Fahrtenbuch Standard", kategorie="fahrtenbuch", papierformat="A4", ausrichtung="quer",
            beschreibung="Fahrtenbuch-Blatt mit Spalten für Datum, Strecke, km, Zweck",
            layout=[
                VordruckElement(typ="text", x=10, y=8, breite=120, hoehe=8, text="Fahrtenbuch — {{fahrzeug}} ({{kennzeichen}})", font_size=13, bold=True),
                VordruckElement(typ="text", x=230, y=8, breite=57, hoehe=6, text="Zeitraum: {{zeitraum}}", font_size=10, align="right"),
                VordruckElement(typ="linie", x=10, y=18, breite=277, hoehe=1),
                VordruckElement(typ="rechteck", x=10, y=24, breite=277, hoehe=150),
                VordruckElement(typ="text", x=12, y=26, breite=25, hoehe=6, text="Datum", font_size=9, bold=True),
                VordruckElement(typ="text", x=45, y=26, breite=60, hoehe=6, text="Start → Ziel", font_size=9, bold=True),
                VordruckElement(typ="text", x=130, y=26, breite=25, hoehe=6, text="km Beginn", font_size=9, bold=True),
                VordruckElement(typ="text", x=165, y=26, breite=25, hoehe=6, text="km Ende", font_size=9, bold=True),
                VordruckElement(typ="text", x=200, y=26, breite=25, hoehe=6, text="gefahren", font_size=9, bold=True),
                VordruckElement(typ="text", x=235, y=26, breite=50, hoehe=6, text="Zweck/Kunde", font_size=9, bold=True),
                VordruckElement(typ="linie", x=10, y=34, breite=277, hoehe=1),
            ],
            beispieldaten={"fahrzeug": "MB Sprinter", "kennzeichen": "AUR-XY 99", "zeitraum": "Juli 2026"},
        ),
        VordruckCreate(
            name="Geschenk-Gutschein", kategorie="gutschein", papierformat="A6", ausrichtung="quer",
            beschreibung="Geschenkgutschein mit Betrag, Code und QR",
            layout=[
                VordruckElement(typ="rechteck", x=4, y=4, breite=140, hoehe=97),
                VordruckElement(typ="text", x=10, y=12, breite=100, hoehe=8, text="{{firma}}", font_size=12, bold=True),
                VordruckElement(typ="text", x=10, y=30, breite=128, hoehe=12, text="GESCHENK-GUTSCHEIN", font_size=18, bold=True, align="center"),
                VordruckElement(typ="text", x=10, y=48, breite=128, hoehe=12, text="{{betrag}} EUR", font_size=22, bold=True, align="center"),
                VordruckElement(typ="text", x=10, y=68, breite=60, hoehe=6, text="Gutschein-Code: {{code}}", font_size=9),
                VordruckElement(typ="text", x=10, y=76, breite=60, hoehe=6, text="Gültig bis: {{gueltig_bis}}", font_size=9),
                VordruckElement(typ="qrcode", x=110, y=62, breite=28, hoehe=28, text="{{code}}"),
            ],
            beispieldaten={"firma": "Hinrich Folkerts GmbH & Co. KG", "betrag": "50,00", "code": "GS-2026-8F4K2", "gueltig_bis": "31.12.2027"},
        ),
        VordruckCreate(
            name="Rabatt-Coupon", kategorie="rabatt_coupon", papierformat="label_100x50", ausrichtung="hoch",
            beschreibung="Coupon mit Rabattsatz, Aktion und Code",
            layout=[
                VordruckElement(typ="rechteck", x=2, y=2, breite=96, hoehe=46),
                VordruckElement(typ="text", x=4, y=6, breite=64, hoehe=10, text="{{rabatt}} % RABATT", font_size=16, bold=True),
                VordruckElement(typ="text", x=4, y=20, breite=64, hoehe=6, text="{{aktion}}", font_size=8),
                VordruckElement(typ="text", x=4, y=28, breite=64, hoehe=6, text="Code: {{code}} — gültig bis {{gueltig_bis}}", font_size=7),
                VordruckElement(typ="qrcode", x=72, y=10, breite=24, hoehe=24, text="{{code}}"),
            ],
            beispieldaten={"rabatt": "10", "aktion": "Saatgut-Frühbezug 2027", "code": "RC-FRUEH27", "gueltig_bis": "28.02.2027"},
        ),
        VordruckCreate(
            name="Info-Schreiben", kategorie="info_schreiben", papierformat="A4",
            beschreibung="Briefkopf mit Adressfeld und Textbereich",
            layout=kopf + [
                VordruckElement(typ="text", x=10, y=40, breite=85, hoehe=6, text="{{empfaenger_name}}", font_size=10),
                VordruckElement(typ="text", x=10, y=46, breite=85, hoehe=6, text="{{empfaenger_strasse}}", font_size=10),
                VordruckElement(typ="text", x=10, y=52, breite=85, hoehe=6, text="{{empfaenger_ort}}", font_size=10),
                VordruckElement(typ="text", x=140, y=52, breite=60, hoehe=6, text="{{datum}}", font_size=10, align="right"),
                VordruckElement(typ="text", x=10, y=75, breite=150, hoehe=8, text="{{betreff}}", font_size=11, bold=True),
                VordruckElement(typ="text", x=10, y=88, breite=190, hoehe=100, text="{{text}}", font_size=10),
                VordruckElement(typ="text", x=10, y=200, breite=100, hoehe=6, text="Mit freundlichen Grüßen", font_size=10),
                VordruckElement(typ="text", x=10, y=215, breite=100, hoehe=6, text="{{unterzeichner}}", font_size=10),
            ],
            beispieldaten={
                "firma": "Hinrich Folkerts GmbH & Co. KG", "empfaenger_name": "Berkhout Dirk C.",
                "empfaenger_strasse": "Groothuser Grenzweg 2", "empfaenger_ort": "26736 Krummhörn",
                "datum": "02.07.2026", "betreff": "Information zur Ernteanlieferung 2026",
                "text": "Sehr geehrte Damen und Herren, ...", "unterzeichner": "Die Geschäftsleitung",
            },
        ),
        VordruckCreate(
            name="Sackanhänger", kategorie="sackanhaenger", papierformat="label_100x50",
            beschreibung="Anhänger mit Artikel, Partie, Gewicht und QR",
            layout=[
                VordruckElement(typ="rechteck", x=2, y=2, breite=96, hoehe=46),
                VordruckElement(typ="text", x=4, y=5, breite=64, hoehe=8, text="{{artikel}}", font_size=11, bold=True),
                VordruckElement(typ="text", x=4, y=15, breite=64, hoehe=5, text="Partie: {{partie_nr}}", font_size=8),
                VordruckElement(typ="text", x=4, y=22, breite=64, hoehe=5, text="Charge: {{charge}}", font_size=8),
                VordruckElement(typ="text", x=4, y=29, breite=64, hoehe=5, text="Gewicht: {{gewicht_kg}} kg", font_size=8),
                VordruckElement(typ="text", x=4, y=36, breite=64, hoehe=5, text="MHD: {{mhd}} — Z-Nr: {{zulassung}}", font_size=7),
                VordruckElement(typ="qrcode", x=72, y=12, breite=24, hoehe=24, text="{{partie_nr}}"),
            ],
            beispieldaten={
                "artikel": "Saatweizen ASORY E", "partie_nr": "PA-2026-0042", "charge": "CH-2026-0815",
                "gewicht_kg": "25", "mhd": "30.09.2027", "zulassung": "DE-026-12345",
            },
        ),
        VordruckCreate(
            name="Quittung / Beleg", kategorie="beleg", papierformat="A6",
            beschreibung="Einfacher Quittungsbeleg",
            layout=[
                VordruckElement(typ="text", x=8, y=8, breite=90, hoehe=8, text="{{firma}}", font_size=11, bold=True),
                VordruckElement(typ="text", x=8, y=20, breite=90, hoehe=8, text="QUITTUNG Nr. {{beleg_nr}}", font_size=12, bold=True),
                VordruckElement(typ="text", x=8, y=34, breite=40, hoehe=6, text="Datum:", font_size=9),
                VordruckElement(typ="feld", x=40, y=34, breite=40, hoehe=6, feld_key="datum", font_size=9),
                VordruckElement(typ="text", x=8, y=44, breite=40, hoehe=6, text="Von:", font_size=9),
                VordruckElement(typ="feld", x=40, y=44, breite=60, hoehe=6, feld_key="zahler", font_size=9),
                VordruckElement(typ="text", x=8, y=54, breite=40, hoehe=6, text="Betrag:", font_size=9),
                VordruckElement(typ="feld", x=40, y=54, breite=40, hoehe=6, feld_key="betrag", font_size=11, bold=True),
                VordruckElement(typ="text", x=8, y=64, breite=40, hoehe=6, text="Zweck:", font_size=9),
                VordruckElement(typ="feld", x=40, y=64, breite=60, hoehe=6, feld_key="zweck", font_size=9),
                VordruckElement(typ="linie", x=8, y=120, breite=60, hoehe=1),
                VordruckElement(typ="text", x=8, y=123, breite=60, hoehe=5, text="Unterschrift", font_size=7),
            ],
            beispieldaten={"firma": "Hinrich Folkerts GmbH & Co. KG", "beleg_nr": "Q-2026-0101", "datum": "02.07.2026", "zahler": "Barverkauf Hofladen", "betrag": "23,50 EUR", "zweck": "Saatgut Kleinmenge"},
        ),
        VordruckCreate(
            name="Handout / Aushang", kategorie="handout", papierformat="A4",
            beschreibung="Einseitiger Aushang mit Titel und Textbereich",
            layout=[
                VordruckElement(typ="text", x=10, y=20, breite=190, hoehe=16, text="{{titel}}", font_size=24, bold=True, align="center"),
                VordruckElement(typ="linie", x=40, y=42, breite=130, hoehe=1),
                VordruckElement(typ="text", x=20, y=60, breite=170, hoehe=150, text="{{text}}", font_size=12),
                VordruckElement(typ="text", x=10, y=270, breite=190, hoehe=6, text="{{firma}} — {{datum}}", font_size=9, align="center"),
            ],
            beispieldaten={"titel": "Annahmezeiten Ernte 2026", "text": "Mo–Fr 6:00–20:00 Uhr, Sa 7:00–14:00 Uhr", "firma": "Hinrich Folkerts GmbH & Co. KG", "datum": "02.07.2026"},
        ),
    ]


@router.post("/seed-standard", response_model=list[VordruckOut], status_code=201,
             summary="Standard-Vorlagen anlegen (idempotent je Name)")
def seed_standard_vorlagen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Legt die mitgelieferten Standard-Vorlagen an; vorhandene Namen werden übersprungen."""
    existing = {
        r["name"] for r in db.execute(
            text("SELECT name FROM domain_shared.beleg_vordrucke WHERE tenant_id = :tid"),
            {"tid": tenant_id},
        ).mappings().all()
    }
    created: list[VordruckOut] = []
    for vorlage in _standard_vorlagen():
        if vorlage.name in existing:
            continue
        created.append(create_vordruck(vorlage, db, tenant_id))
    return created
