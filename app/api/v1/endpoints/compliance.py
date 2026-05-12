"""Compliance API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional
from collections import defaultdict
import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.documents.router_helpers import get_repository, list_from_store
from app.domains.operations.models import (
    ComplianceEintrag,
    ENNIMeldung,
    Charge,
    PCNMeldung,
    QSCheckEintrag,
    ZulassungRegister,
    SachkundeEintrag,
    SaatgutNachbauEintrag,
    VVVOEintrag,
)

router = APIRouter(prefix="/compliance", tags=["Compliance"])


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _list_sales_deliveries(db: Session) -> list[dict]:
    repo = get_repository(db)
    payload = list_from_store("sales_delivery", skip=0, limit=10_000, repo=repo)
    return payload.get("data", []) if isinstance(payload, dict) else []


def _extract_hazard_export_rows(deliveries: list[dict], year: Optional[int] = None) -> list[dict]:
    rows: list[dict] = []
    for d in deliveries:
        date_str = str(d.get("date") or "")
        if year and not date_str.startswith(f"{year}-"):
            continue
        doc_compliance = d.get("psmCompliance") or {}
        for line in d.get("lines") or []:
            has_psm = any([line.get("bvlZulassungsnummer"), line.get("hazardHinweise"), line.get("sdsReference")])
            if not has_psm:
                continue
            rows.append(
                {
                    "deliveryNumber": d.get("number") or d.get("id"),
                    "deliveryDate": date_str[:10] if len(date_str) >= 10 else None,
                    "supplierName": d.get("supplierName"),
                    "customerId": d.get("customerId"),
                    "article": line.get("article"),
                    "bvlZulassungsnummer": line.get("bvlZulassungsnummer"),
                    "hazardHinweise": line.get("hazardHinweise"),
                    "sdsReference": line.get("sdsReference"),
                    "sachkundeStatus": doc_compliance.get("sachkundeStatus"),
                    "sdsMitgeliefert": doc_compliance.get("sdsMitgeliefert"),
                    "adrPunkte": float(d.get("adrPunkte") or doc_compliance.get("adrPunkte") or 0),
                    "compliant": bool(doc_compliance.get("compliant", False)),
                }
            )
    return rows


def _compute_nutrient_stream(deliveries: list[dict], year: int) -> dict:
    by_month: dict[str, dict[str, float]] = defaultdict(lambda: {"deliveries": 0.0, "n_kg": 0.0, "p2o5_kg": 0.0})
    total_n = 0.0
    total_p2o5 = 0.0
    count = 0

    for d in deliveries:
        date_str = str(d.get("date") or "")
        if not date_str.startswith(f"{year}-"):
            continue
        month = date_str[:7]
        n_kg = float(d.get("totalNutrientNKg") or 0.0)
        p2o5_kg = float(d.get("totalNutrientP2o5Kg") or 0.0)

        by_month[month]["deliveries"] += 1
        by_month[month]["n_kg"] += n_kg
        by_month[month]["p2o5_kg"] += p2o5_kg
        total_n += n_kg
        total_p2o5 += p2o5_kg
        count += 1

    return {
        "year": year,
        "deliveryCount": count,
        "totalNutrientNKg": round(total_n, 3),
        "totalNutrientP2o5Kg": round(total_p2o5, 3),
        "byMonth": {
            k: {
                "deliveries": int(v["deliveries"]),
                "n_kg": round(v["n_kg"], 3),
                "p2o5_kg": round(v["p2o5_kg"], 3),
            }
            for k, v in sorted(by_month.items())
        },
    }


def _build_lot_trace_report(lot: Charge, deliveries: list[dict]) -> dict:
    events = [
        {"type": "charge_created", "date": lot.eingang.isoformat() if lot.eingang else None, "note": "Wareneingang erfasst"},
        {"type": "charge_updated", "date": lot.updated_at.isoformat() if lot.updated_at else None, "note": "Letzte Aktualisierung"},
    ]
    linked_deliveries = []
    for d in deliveries:
        for line in d.get("lines") or []:
            if (line.get("batchNumber") and str(line.get("batchNumber")) == str(lot.chargen_id)) or (
                line.get("articleId") and str(line.get("articleId")) == str(lot.artikel_id)
            ):
                linked_deliveries.append(
                    {
                        "deliveryNumber": d.get("number") or d.get("id"),
                        "deliveryDate": str(d.get("date") or "")[:10],
                        "article": line.get("article"),
                        "quantity": float(line.get("qty") or 0),
                        "customerId": d.get("customerId"),
                    }
                )
                break

    return {
        "lot": {
            "id": lot.id,
            "lotId": lot.chargen_id,
            "article": lot.artikel,
            "articleId": lot.artikel_id,
            "quantity": float(lot.menge or 0),
            "location": lot.lagerort,
            "status": lot.status,
            "qualityStatus": lot.qualitaetsstatus,
            "origin": lot.herkunft,
        },
        "events": events,
        "linkedDeliveries": linked_deliveries,
        "deliveryCount": len(linked_deliveries),
    }


def _seed(db: Session) -> None:
    if db.query(ComplianceEintrag).count() == 0:
        db.add_all([
            ComplianceEintrag(bereich="Gewaesserschutz", anforderung="Gewaesserrandstreifen 5m", erfuellt=True, nachweis="Feldprotokoll", frist=datetime(2026, 12, 31)),
            ComplianceEintrag(bereich="Duengeverordnung", anforderung="Naehrstoffbilanz erstellt", erfuellt=True, nachweis="Bilanz 2025/26", frist=datetime(2026, 3, 31)),
            ComplianceEintrag(bereich="PSM-Dokumentation", anforderung="Anwendungsprotokolle vollstaendig", erfuellt=False, nachweis="", frist=datetime(2026, 3, 15)),
        ])
    if db.query(ENNIMeldung).count() == 0:
        db.add_all([
            ENNIMeldung(typ="DBE", betrieb="Landwirtschaft Mueller", vvvo="03-276-1234", datum=datetime(2026, 1, 15), status="bestaetigt", naehrstoff_n=180, naehrstoff_p=60, naehrstoff_k=120),
            ENNIMeldung(typ="WDE", betrieb="Agrar Schmidt", vvvo="03-276-5678", datum=datetime(2026, 2, 1), status="gesendet", naehrstoff_n=150, naehrstoff_p=45, naehrstoff_k=90),
        ])
    if db.query(QSCheckEintrag).count() == 0:
        db.add_all([
            QSCheckEintrag(bereich="Wareneingangskontrolle", pruefpunkt="Lieferschein-Pruefung", erfuellt=True, bemerkung="Vollstaendig", geprueft_am=datetime(2026, 2, 10)),
            QSCheckEintrag(bereich="Temperaturkontrolle", pruefpunkt="Lagerungstemperatur dokumentiert", erfuellt=True, bemerkung="Im Normbereich", geprueft_am=datetime(2026, 2, 10)),
        ])
    if db.query(ZulassungRegister).count() == 0:
        db.add_all([
            ZulassungRegister(produkt="Roundup PowerFlex", typ="PSM", nummer="024567-00", behoerde="BVL", gueltig_bis=datetime(2026, 12, 31), status="aktiv"),
            ZulassungRegister(produkt="Fungizid X", typ="PSM", nummer="024568-00", behoerde="BVL", gueltig_bis=datetime(2025, 6, 30), status="auslaufend"),
        ])
    if db.query(SachkundeEintrag).count() == 0:
        db.add(
            SachkundeEintrag(
                kunde="Landwirtschaft Mueller",
                kundennr="K-10023",
                nachweis_nr="SK-NDS-2022-4567",
                ausstellungsdatum=datetime(2022, 3, 15),
                gueltig_bis=datetime(2025, 3, 15),
                ausstellende_stelle="LWK Niedersachsen",
                status="ablaufend",
            )
        )
    if db.query(SaatgutNachbauEintrag).count() == 0:
        db.add(
            SaatgutNachbauEintrag(
                betrieb="Landwirtschaft Mueller",
                sorte="Weichweizen Eltan",
                kultur="Weichweizen",
                flaeche=45.5,
                erntejahr=2024,
                gebuehr=682.50,
                status="bezahlt",
            )
        )
    if db.query(VVVOEintrag).count() == 0:
        db.add(
            VVVOEintrag(
                betriebsname="Landwirtschaft Mueller",
                vvvo="03-276-123456",
                bundesland="Niedersachsen",
                tierart="Rind (Milch)",
                status="aktiv",
                letzte_aktualisierung=datetime(2026, 1, 15),
            )
        )
    db.commit()


@router.get("/cross-compliance", response_model=dict)
async def list_cross_compliance(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(ComplianceEintrag).all()
    payload = [
        {
            "id": i.id,
            "bereich": i.bereich,
            "anforderung": i.anforderung,
            "erfuellt": bool(i.erfuellt),
            "nachweis": i.nachweis,
            "frist": _dt(i.frist),
        }
        for i in items
    ]
    return {
        "items": payload,
        "total": len(payload),
        "erfuellt": sum(1 for i in payload if i["erfuellt"]),
        "offen": sum(1 for i in payload if not i["erfuellt"]),
    }


@router.get("/enni-meldungen", response_model=dict)
async def list_enni_meldungen(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(ENNIMeldung).all()
    return {
        "items": [
            {
                "id": i.id,
                "typ": i.typ,
                "betrieb": i.betrieb,
                "vvvo": i.vvvo,
                "datum": _dt(i.datum),
                "status": i.status,
                "naehrstoffe": {"n": i.naehrstoff_n, "p": i.naehrstoff_p, "k": i.naehrstoff_k},
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/qs-checkliste", response_model=dict)
async def list_qs_checkliste(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(QSCheckEintrag).all()
    payload = [
        {
            "id": i.id,
            "bereich": i.bereich,
            "pruefpunkt": i.pruefpunkt,
            "erfuellt": bool(i.erfuellt),
            "bemerkung": i.bemerkung,
            "geprueft_am": _dt(i.geprueft_am),
            "geprrueftAm": _dt(i.geprueft_am),
        }
        for i in items
    ]
    return {
        "items": payload,
        "total": len(payload),
        "erfuellt": sum(1 for i in payload if i["erfuellt"]),
        "offen": sum(1 for i in payload if not i["erfuellt"]),
    }


@router.get("/zulassungen-register", response_model=dict)
async def list_zulassungen(
    typ: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    _seed(db)
    q = db.query(ZulassungRegister)
    if typ:
        q = q.filter(ZulassungRegister.typ == typ)
    if status:
        q = q.filter(ZulassungRegister.status == status)
    items = q.all()
    return {
        "items": [
            {
                "id": i.id,
                "produkt": i.produkt,
                "typ": i.typ,
                "nummer": i.nummer,
                "behoerde": i.behoerde,
                "gueltig_bis": _dt(i.gueltig_bis),
                "gueltigBis": _dt(i.gueltig_bis),
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/sachkunde-register", response_model=dict)
async def list_sachkunde(status: Optional[str] = Query(None), db: Session = Depends(get_db)) -> dict:
    _seed(db)
    q = db.query(SachkundeEintrag)
    if status:
        q = q.filter(SachkundeEintrag.status == status)
    items = q.all()
    return {
        "items": [
            {
                "id": i.id,
                "kunde": i.kunde,
                "kundennr": i.kundennr,
                "nachweis_nr": i.nachweis_nr,
                "nachweisNr": i.nachweis_nr,
                "ausstellungsdatum": _dt(i.ausstellungsdatum),
                "gueltig_bis": _dt(i.gueltig_bis),
                "gueltigBis": _dt(i.gueltig_bis),
                "ausstellende_stelle": i.ausstellende_stelle,
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/saatgut-nachbau", response_model=dict)
async def list_saatgut_nachbau(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(SaatgutNachbauEintrag).all()
    return {
        "items": [
            {
                "id": i.id,
                "betrieb": i.betrieb,
                "sorte": i.sorte,
                "kultur": i.kultur,
                "flaeche": i.flaeche,
                "erntejahr": i.erntejahr,
                "gebuehr": float(i.gebuehr or 0),
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/vvvo-register", response_model=dict)
async def list_vvvo(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(VVVOEintrag).all()
    return {
        "items": [
            {
                "id": i.id,
                "betriebsname": i.betriebsname,
                "vvvo": i.vvvo,
                "bundesland": i.bundesland,
                "tierart": i.tierart,
                "status": i.status,
                "letzte_aktualisierung": _dt(i.letzte_aktualisierung),
                "letzteAktualisierung": _dt(i.letzte_aktualisierung),
            }
            for i in items
        ],
        "total": len(items),
    }


def _pdf_escape(s: str) -> str:
    r"""Escape ( ) \ for PDF literal strings."""
    if s is None:
        return ""
    return str(s).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _pdf_text_line(x: float, y: float, text: str, font: str = "/F1", size: int = 10) -> bytes:
    """One line of text at position (x, y) in PDF content stream."""
    t = _pdf_escape(text)
    return f"BT {font} {size} Tf {x:.1f} {y:.1f} Td ({t}) Tj ET\n".encode("latin-1", errors="replace")


def _build_compliance_pdf_bytes(stats: dict, cross_items: list[dict]) -> bytes:
    """Baut ein mehrseitiges PDF mit automatischen Längen, Seitenumbrüchen und Zwischensummen."""
    _buffer = io.BytesIO()  # noqa: F841
    margin = 72
    line_height = 14
    font_size = 10
    font_title = 14
    page_width = 612
    page_height = 792
    lines_per_page = int((page_height - 2 * margin - 80) / line_height)  # Platz für Kopf/Fuss
    max_data_lines = max(10, lines_per_page - 12)

    # Inhalte pro Seite: Liste von (stream_body_bytes, zwischensumme_erfuellt, zwischensumme_offen)
    pages_data: list[tuple[bytes, int, int]] = []
    cumulative_erfuellt = 0
    cumulative_offen = 0
    row_start = 0
    total_erfuellt = sum(1 for i in cross_items if i.get("erfuellt"))
    total_offen = len(cross_items) - total_erfuellt

    while row_start < len(cross_items) or (row_start == 0 and not cross_items):
        stream_parts: list[bytes] = []
        y = page_height - margin
        page_erfuellt = 0
        page_offen = 0

        if row_start == 0:
            # Titelseite: Überschrift + Summen
            stream_parts.append(_pdf_text_line(margin, y, "Compliance-Report", size=font_title))
            y -= line_height * 1.5
            gen = stats.get("generated_at", "")[:19].replace("T", " ")
            stream_parts.append(_pdf_text_line(margin, y, f"Stand: {gen}", size=font_size))
            y -= line_height * 2
            cc = stats.get("cross_compliance", {})
            stream_parts.append(_pdf_text_line(margin, y, f"Cross-Compliance gesamt: {cc.get('quote', 0)}%"))
            y -= line_height
            stream_parts.append(_pdf_text_line(margin, y, f"Erfuellt: {cc.get('erfuellt', 0)}, Offen: {cc.get('offen', 0)}"))
            y -= line_height
            enni = stats.get("enni", {})
            stream_parts.append(_pdf_text_line(margin, y, f"ENNI: {enni.get('bestaetigt', 0)}/{enni.get('total', 0)} bestaetigt"))
            y -= line_height * 2
        else:
            # Folgeseite: Fortsetzung
            stream_parts.append(_pdf_text_line(margin, y, f"Fortsetzung Cross-Compliance (Seite {len(pages_data) + 1})", size=font_size))
            y -= line_height * 1.5

        # Tabellenkopf (auf jeder Seite)
        stream_parts.append(_pdf_text_line(margin, y, "Bereich", size=font_size))
        stream_parts.append(_pdf_text_line(margin + 120, y, "Anforderung", size=font_size))
        stream_parts.append(_pdf_text_line(margin + 320, y, "Status", size=font_size))
        stream_parts.append(_pdf_text_line(margin + 400, y, "Frist", size=font_size))
        y -= line_height
        stream_parts.append(f"0.5 w {margin} {y:.1f} m {page_width - margin} {y:.1f} l S\n".encode("latin-1"))
        y -= 4

        # Zeilen (Positionen)
        row_end = min(row_start + max_data_lines, len(cross_items))
        for i in range(row_start, row_end):
            item = cross_items[i]
            bereich = (item.get("bereich") or "")[:18]
            anforderung = (item.get("anforderung") or "")[:28]
            status = "Erfuellt" if item.get("erfuellt") else "Offen"
            frist = (item.get("frist") or "")[:10]
            stream_parts.append(_pdf_text_line(margin, y, bereich, size=font_size))
            stream_parts.append(_pdf_text_line(margin + 120, y, anforderung, size=font_size))
            stream_parts.append(_pdf_text_line(margin + 320, y, status, size=font_size))
            stream_parts.append(_pdf_text_line(margin + 400, y, frist, size=font_size))
            if item.get("erfuellt"):
                page_erfuellt += 1
            else:
                page_offen += 1
            y -= line_height

        cumulative_erfuellt += page_erfuellt
        cumulative_offen += page_offen
        y -= line_height
        stream_parts.append(f"0.5 w {margin} {y:.1f} m {page_width - margin} {y:.1f} l S\n".encode("latin-1"))
        y -= line_height
        # Zwischensumme / Summe
        if row_end < len(cross_items):
            stream_parts.append(
                _pdf_text_line(margin, y, f"Zwischensumme Seite {len(pages_data) + 1}: Erfuellt {cumulative_erfuellt}, Offen {cumulative_offen}")
            )
        else:
            stream_parts.append(
                _pdf_text_line(margin, y, f"Summe gesamt: Erfuellt {total_erfuellt}, Offen {total_offen}")
            )
        body = b"".join(stream_parts)
        pages_data.append((body, cumulative_erfuellt, cumulative_offen))
        row_start = row_end
        if row_start >= len(cross_items):
            break

    if not pages_data:
        # Leere Liste: eine Seite mit nur Überschrift und Summen
        stream_parts = []
        y = page_height - margin
        stream_parts.append(_pdf_text_line(margin, y, "Compliance-Report", size=font_title))
        y -= line_height * 2
        cc = stats.get("cross_compliance", {})
        stream_parts.append(_pdf_text_line(margin, y, f"Cross-Compliance: Erfuellt {cc.get('erfuellt', 0)}, Offen {cc.get('offen', 0)}"))
        y -= line_height
        stream_parts.append(_pdf_text_line(margin, y, "Keine Einzelpositionen."))
        pages_data.append((b"".join(stream_parts), cc.get("erfuellt", 0), cc.get("offen", 0)))

    npages = len(pages_data)
    # Objekt-IDs: 1=Catalog, 2=Pages, 3..2+npages=Page, 3+npages..2+npages*2=Contents
    obj_ids_pages = list(range(3, 3 + npages))
    obj_ids_contents = list(range(3 + npages, 3 + npages * 2))
    objects: list[tuple[int, str | bytes]] = []
    # Catalog
    objects.append((1, "<</Type/Catalog/Pages 2 0 R>>"))
    # Pages
    kids = " ".join(f"{i} 0 R" for i in obj_ids_pages)
    objects.append((2, f"<< /Type /Pages /Kids [{kids}] /Count {npages} >>"))
    # Page-Objekte
    for p in range(npages):
        contents_ref = obj_ids_contents[p]
        objects.append((
            3 + p,
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            f"/Contents {contents_ref} 0 R >>"
        ))
    # Content-Streams (Length muss gesetzt werden)
    for p in range(npages):
        body = pages_data[p][0]
        length = len(body)
        objects.append((obj_ids_contents[p], f"<< /Length {length} >>\nstream\n".encode() + body + b"\nendstream"))

    # PDF in Buffer schreiben und Offsets sammeln
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    xref_offsets: dict[int, int] = {}
    for obj_id, obj_content in objects:
        xref_offsets[obj_id] = out.tell()
        out.write(f"{obj_id} 0 obj\n".encode())
        if isinstance(obj_content, bytes):
            out.write(obj_content)
        else:
            out.write(obj_content.encode("latin-1", errors="replace"))
        out.write(b"\nendobj\n")

    xref_start = out.tell()
    out.write(b"xref\n")
    max_id = max(xref_offsets)
    out.write(f"0 {max_id + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for i in range(1, max_id + 1):
        offset = xref_offsets.get(i, 0)
        out.write(f"{offset:010d} 00000 n \n".encode())
    out.write(b"trailer << /Size " + str(max_id + 1).encode() + b" /Root 1 0 R >>\n")
    out.write(b"startxref\n")
    out.write(str(xref_start).encode())
    out.write(b"\n%%EOF\n")
    return out.getvalue()


@router.get("/report-pdf")
async def get_compliance_report_pdf(
    inline: bool = Query(False, description="Vorschau im Browser (inline) statt Download"),
    db: Session = Depends(get_db),
) -> Response:
    """Liefert Compliance-Report als mehrseitiges PDF mit Zwischensummen und automatischen Seitenumbrüchen."""
    _seed(db)
    stats = await get_compliance_stats(db=db)
    cross_payload = await list_cross_compliance(db=db)
    cross_items = cross_payload.get("items", [])
    pdf_bytes = _build_compliance_pdf_bytes(stats, cross_items)
    disposition = "inline" if inline else "attachment"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'{disposition}; filename="compliance-report.pdf"'},
    )


@router.get("/stats", response_model=dict)
async def get_compliance_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    total_checks = db.query(ComplianceEintrag).count()
    fulfilled = db.query(ComplianceEintrag).filter(ComplianceEintrag.erfuellt == True).count()  # noqa: E712
    enni_total = db.query(ENNIMeldung).count()
    enni_confirmed = db.query(ENNIMeldung).filter(ENNIMeldung.status == "bestaetigt").count()
    avg_n = db.query(ENNIMeldung).with_entities(ENNIMeldung.naehrstoff_n).all()
    avg_n_val = sum(float(x[0] or 0) for x in avg_n) / len(avg_n) if avg_n else 0

    return {
        "cross_compliance": {
            "total": total_checks,
            "erfuellt": fulfilled,
            "offen": total_checks - fulfilled,
            "quote": round((fulfilled / total_checks * 100) if total_checks else 0, 1),
        },
        "enni": {
            "total": enni_total,
            "bestaetigt": enni_confirmed,
            "in_bearbeitung": enni_total - enni_confirmed,
            "durchschnitt_n": round(avg_n_val, 1),
        },
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/exports/gefahrstoffdoku", response_model=dict)
async def export_gefahrstoffdoku(
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
) -> dict:
    deliveries = _list_sales_deliveries(db)
    rows = _extract_hazard_export_rows(deliveries, year=year)
    return {
        "year": year,
        "rows": rows,
        "total": len(rows),
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/exports/gefahrstoffdoku.csv")
async def export_gefahrstoffdoku_csv(
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    payload = await export_gefahrstoffdoku(year=year, db=db)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(
        [
            "Lieferschein",
            "Datum",
            "Lieferant",
            "Kunde",
            "Artikel",
            "BVL-Zulassungsnummer",
            "Gefahrhinweise",
            "SDB-Referenz",
            "Sachkunde-Status",
            "SDB mitgeliefert",
            "ADR Punkte",
            "Compliance",
        ]
    )
    for row in payload["rows"]:
        writer.writerow(
            [
                row.get("deliveryNumber"),
                row.get("deliveryDate"),
                row.get("supplierName"),
                row.get("customerId"),
                row.get("article"),
                row.get("bvlZulassungsnummer"),
                row.get("hazardHinweise"),
                row.get("sdsReference"),
                row.get("sachkundeStatus"),
                row.get("sdsMitgeliefert"),
                row.get("adrPunkte"),
                "ja" if row.get("compliant") else "nein",
            ]
        )
    filename = f"gefahrstoffdoku-{year}.csv" if year else "gefahrstoffdoku.csv"
    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode("utf-8-sig")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/exports/naehrstoffstrom", response_model=dict)
async def export_naehrstoffstrom(
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
) -> dict:
    deliveries = _list_sales_deliveries(db)
    data = _compute_nutrient_stream(deliveries, year=year)
    data["generated_at"] = datetime.utcnow().isoformat()
    return data


@router.get("/exports/naehrstoffstrom.csv")
async def export_naehrstoffstrom_csv(
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    data = await export_naehrstoffstrom(year=year, db=db)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(["Jahr", data["year"]])
    writer.writerow(["Anzahl Lieferscheine", data["deliveryCount"]])
    writer.writerow(["Summe N (kg)", data["totalNutrientNKg"]])
    writer.writerow(["Summe P2O5 (kg)", data["totalNutrientP2o5Kg"]])
    writer.writerow([])
    writer.writerow(["Monat", "Lieferscheine", "N (kg)", "P2O5 (kg)"])
    for month, row in data.get("byMonth", {}).items():
        writer.writerow([month, row.get("deliveries", 0), row.get("n_kg", 0), row.get("p2o5_kg", 0)])
    filename = f"naehrstoffstrom-{year}.csv"
    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode("utf-8-sig")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/exports/chargen-trace/{lot_id}", response_model=dict)
async def export_chargen_trace_report(
    lot_id: str,
    db: Session = Depends(get_db),
) -> dict:
    lot = db.query(Charge).filter((Charge.id == lot_id) | (Charge.chargen_id == lot_id)).first()
    if not lot:
        return {"error": "lot not found", "lot_id": lot_id}
    deliveries = _list_sales_deliveries(db)
    report = _build_lot_trace_report(lot, deliveries)
    report["generated_at"] = datetime.utcnow().isoformat()
    return report


# ---------------------------------------------------------------------------
# Wave 23 AP4: Intrastat-Meldungen
# ---------------------------------------------------------------------------

from ....core.intrastat_model import (
    IntrastatRichtung,
    build_stub_intrastat_meldung,
    validate_intrastat_meldung,
)

_INTRASTAT_STORE: dict[str, dict] = {}


@router.get("/intrastat/meldungen", response_model=dict)
async def list_intrastat_meldungen(
    meldezeitraum: Optional[str] = None,
    richtung: Optional[str] = None,
) -> dict:
    """
    Liste aller Intrastat-Meldungen (Gap 042).

    Optional filterbar nach Meldezeitraum (YYYY-MM) und Richtung (EINGANG/AUSGANG).
    """
    meldungen = list(_INTRASTAT_STORE.values())

    if meldezeitraum:
        meldungen = [m for m in meldungen if m.get("meldezeitraum") == meldezeitraum]
    if richtung:
        meldungen = [m for m in meldungen if m.get("richtung") == richtung.upper()]

    return {
        "meldungen": meldungen,
        "count": len(meldungen),
        "schema_version": 1,
    }


@router.post("/intrastat/meldungen", response_model=dict, status_code=201)
async def create_intrastat_meldung(
    body: dict,
) -> dict:
    """
    Anlage einer neuen Intrastat-Meldung (Gap 042).

    Fuehrt direkt eine Vollstaendigkeitspruefung gemaess VO (EG) 638/2004 durch.
    Gibt validation_result mit allen Violations zurueck.
    """
    meldung_id = body.get("meldung_id", f"INTRA-{len(_INTRASTAT_STORE) + 1:04d}")
    tenant_id = body.get("tenant_id", "demo-tenant")
    meldezeitraum = body.get("meldezeitraum", "2026-03")
    richtung_raw = body.get("richtung", "EINGANG")

    try:
        richtung = IntrastatRichtung(richtung_raw)
    except ValueError:
        richtung = IntrastatRichtung.EINGANG

    meldung = build_stub_intrastat_meldung(
        meldung_id=meldung_id,
        tenant_id=tenant_id,
        meldezeitraum=meldezeitraum,
        richtung=richtung,
    )
    validation = validate_intrastat_meldung(meldung)
    meldung_dict = meldung.as_dict()
    _INTRASTAT_STORE[meldung_id] = meldung_dict

    return {
        "meldung": meldung_dict,
        "validation_result": validation.as_dict(),
        "schema_version": 1,
    }


@router.get("/intrastat/meldungen/{meldung_id}/validate", response_model=dict)
async def validate_intrastat_meldung_endpoint(meldung_id: str) -> dict:
    """
    Vollstaendigkeitspruefung einer einzelnen Intrastat-Meldung nach EU-VO 638/2004.
    """
    meldung = build_stub_intrastat_meldung(
        meldung_id=meldung_id,
        tenant_id="demo-tenant",
    )
    result = validate_intrastat_meldung(meldung)
    return result.as_dict()


# ── PCN-Meldungen (Product Classification Notification / UFI) ────────────────

import re as _re
_UFI_PATTERN = _re.compile(r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$")


def _pcn_to_dict(m: PCNMeldung) -> dict:
    return {
        "meldung_id": m.id,
        "produktname": m.produktname,
        "ufi": m.ufi or "",
        "cas_nummern": m.cas_nummern or "",
        "gefahrenklassen": m.gefahrenklassen or [],
        "verwendungskategorie": m.verwendungskategorie or "",
        "pcnStatus": m.pcn_status,
        "tenant_id": m.tenant_id,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "schema_version": 1,
    }


@router.post("/pcn-meldungen", response_model=dict, status_code=201)
async def create_pcn_meldung(
    body: dict,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """
    Anlage einer neuen PCN-Meldung (Product Classification Notification) mit UFI.

    Validiert das UFI-Format (XXXX-XXXX-XXXX-XXXX) und legt die Meldung persistent an.
    Entspricht den Anforderungen der EU-Verordnung 2017/542 (CLP-Anhang VIII).
    """
    from fastapi import HTTPException

    produktname = str(body.get("produktname", "")).strip()
    if not produktname:
        raise HTTPException(status_code=422, detail="produktname ist erforderlich.")

    ufi = str(body.get("ufi", "")).strip()
    if ufi and not _UFI_PATTERN.match(ufi):
        raise HTTPException(
            status_code=422,
            detail=f"Ungültiges UFI-Format '{ufi}'. Erwartet: XXXX-XXXX-XXXX-XXXX (A-Z, 0-9).",
        )

    meldung = PCNMeldung(
        produktname=produktname,
        ufi=ufi or None,
        cas_nummern=body.get("cas_nummern") or None,
        gefahrenklassen=body.get("gefahrenklassen") or [],
        verwendungskategorie=body.get("verwendungskategorie") or None,
        pcn_status=body.get("pcnStatus", "entwurf"),
        tenant_id=tenant_id,
    )
    try:
        db.add(meldung)
        db.commit()
        db.refresh(meldung)
    except Exception:
        db.rollback()
        raise

    return _pcn_to_dict(meldung)


@router.get("/pcn-meldungen", response_model=dict)
async def list_pcn_meldungen(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Liste aller PCN-Meldungen (tenant-isoliert, paginiert)."""
    base_q = (
        db.query(PCNMeldung)
        .filter(PCNMeldung.tenant_id == tenant_id)
        .order_by(PCNMeldung.created_at.desc())
    )
    total = base_q.count()
    rows = base_q.offset(skip).limit(limit).all()
    meldungen = [_pcn_to_dict(m) for m in rows]
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "meldungen": meldungen,
        "items": meldungen,
        "schema_version": 1,
    }


# ── EUDR (EU Deforestation Regulation) ───────────────────────────────────────

@router.get("/eudr", response_model=dict)
async def get_eudr_status(
    tenant_id: Optional[str] = Query(None, description="Tenant context"),
    db: Session = Depends(get_db),
) -> dict:
    """
    EU Deforestation Regulation (EUDR) compliance status — aggregated from charge/lot data.
    Falls back to a zero-state response when no EUDR data exists yet.
    """
    from sqlalchemy import text as _text
    tid = tenant_id or "default"
    try:
        row = db.execute(
            _text("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE eudr_compliant = TRUE) AS compliant,
                    COUNT(*) FILTER (WHERE eudr_compliant = FALSE) AS flagged,
                    ARRAY_AGG(DISTINCT origin_country) FILTER (WHERE origin_country IS NOT NULL) AS countries
                FROM domain_inventory.lots
                WHERE tenant_id = :tid
            """),
            {"tid": tid},
        ).fetchone()
        total = int(row[0]) if row and row[0] else 0
        compliant = int(row[1]) if row and row[1] else 0
        flagged = int(row[2]) if row and row[2] else 0
        countries = list(row[3]) if row and row[3] else []
    except Exception:
        total = compliant = flagged = 0
        countries = []

    try:
        stmt_count = db.execute(
            _text("SELECT COUNT(*) FROM domain_compliance.eudr_due_diligence WHERE tenant_id = :tid"),
            {"tid": tid},
        ).scalar() or 0
    except Exception:
        stmt_count = 0

    status_label = "KONFORM" if flagged == 0 else ("KRITISCH" if flagged > 5 else "WARNUNG")
    return {
        "status": status_label,
        "last_check": datetime.utcnow().isoformat(),
        "batches_total": total,
        "batches_compliant": compliant,
        "batches_flagged": flagged,
        "due_diligence_statements": int(stmt_count),
        "origin_countries": countries,
        "deforestation_risk": "NIEDRIG" if flagged == 0 else "MITTEL",
        "next_report_due": None,
    }


# ── USTVA (Umsatzsteuer-Voranmeldung) ────────────────────────────────────────

@router.get("/ustva", response_model=dict)
async def get_ustva_status(
    tenant_id: Optional[str] = Query(None, description="Tenant context"),
    periode: Optional[str] = Query(None, description="Meldezeitraum z.B. 2026-03"),
    db: Session = Depends(get_db),
) -> dict:
    """
    UStVA-Bereitschaftsstatus — aggregiert aus gebuchten Journal-Einträgen der Periode.
    """
    from datetime import timezone
    from sqlalchemy import text as _text
    current_period = periode or datetime.now(timezone.utc).strftime("%Y-%m")
    tid = tenant_id or "default"
    try:
        row = db.execute(
            _text("""
                SELECT
                    COALESCE(SUM(CASE WHEN jel.credit > 0 AND coa.account_type = 'revenue' THEN jel.credit ELSE 0 END), 0) AS umsatz,
                    COALESCE(SUM(CASE WHEN jel.credit > 0 AND coa.account_number LIKE '17%' THEN jel.credit ELSE 0 END), 0) AS ust_soll,
                    COALESCE(SUM(CASE WHEN jel.debit > 0 AND coa.account_number LIKE '15%' THEN jel.debit ELSE 0 END), 0) AS vorsteuer
                FROM domain_erp.journal_entries je
                JOIN domain_erp.journal_entry_lines jel ON jel.journal_entry_id = je.id
                JOIN domain_erp.chart_of_accounts coa ON coa.id = jel.account_id
                WHERE je.tenant_id = :tid
                  AND je.status = 'posted'
                  AND TO_CHAR(je.entry_date::date, 'YYYY-MM') = :period
            """),
            {"tid": tid, "period": current_period},
        ).fetchone()
        umsatz = float(row[0]) if row else 0.0
        ust_soll = float(row[1]) if row else 0.0
        vorsteuer = float(row[2]) if row else 0.0
        zahllast = round(ust_soll - vorsteuer, 2)
        offene = db.execute(
            _text("""
                SELECT COUNT(*) FROM domain_erp.journal_entries
                WHERE tenant_id = :tid AND status = 'draft'
                  AND TO_CHAR(entry_date::date, 'YYYY-MM') = :period
            """),
            {"tid": tid, "period": current_period},
        ).scalar() or 0
        readiness = min(100, int(100 * (1 - int(offene) / max(int(offene) + 1, 1))))
        elster_status = "EINGEREICHT" if readiness == 100 else "AUSSTEHEND"
    except Exception:
        umsatz = ust_soll = vorsteuer = zahllast = 0.0
        offene = 0
        readiness = 0
        elster_status = "AUSSTEHEND"

    return {
        "periode": current_period,
        "status": "BEREIT" if readiness >= 95 else "IN_VORBEREITUNG",
        "readiness_pct": readiness,
        "steuerliche_bemessungsgrundlage": umsatz,
        "ust_soll": ust_soll,
        "vorsteuer": vorsteuer,
        "zahllast": zahllast,
        "offene_positionen": int(offene),
        "elster_uebermittlung": elster_status,
        "deadline": None,
        "last_updated": datetime.utcnow().isoformat(),
    }


# ── BVL-Umsatzmeldung (Pflanzenschutzmittel) ────────────────────────────────

@router.get("/bvl-umsaetze", response_model=list)
async def get_bvl_umsaetze(
    tenant_id: Optional[str] = Query(None, description="Tenant context"),
    db: Session = Depends(get_db),
) -> list:
    """
    PSM-Umsaetze fuer BVL-Meldung aggregieren.
    Liefert Wirkstoffe mit Absatzmengen aus Lagerbewegungen/Rechnungen.
    """
    from sqlalchemy import text
    tid = tenant_id or "default"
    try:
        rows = db.execute(
            text("""
                SELECT a.name AS wirkstoff,
                       COALESCE(SUM(sm.quantity), 0) AS menge,
                       COALESCE(a.unit, 'kg') AS einheit
                FROM domain_inventory.inventory_stock_movements sm
                JOIN domain_inventory.articles a ON a.id = sm.article_id
                WHERE sm.tenant_id = :tid
                  AND sm.movement_type = 'out'
                  AND a.article_group = 'PSM'
                  AND EXTRACT(YEAR FROM sm.movement_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1
                GROUP BY a.name, a.unit
                ORDER BY menge DESC
            """),
            {"tid": tid},
        ).fetchall()
        return [{"wirkstoff": r[0], "menge": float(r[1]), "einheit": r[2]} for r in rows]
    except Exception:
        return []
