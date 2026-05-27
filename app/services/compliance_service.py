"""Helpers and PDF builder for the Compliance domain."""

from __future__ import annotations

import io
from collections import defaultdict
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.documents.router_helpers import get_repository, list_from_store
from app.domains.operations.models import (
    ComplianceEintrag,
    ENNIMeldung,
    QSCheckEintrag,
    ZulassungRegister,
    SachkundeEintrag,
    SaatgutNachbauEintrag,
    VVVOEintrag,
    Charge,
)


def dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def list_sales_deliveries(db: Session) -> list[dict]:
    repo = get_repository(db)
    payload = list_from_store("sales_delivery", skip=0, limit=10_000, repo=repo)
    return payload.get("data", []) if isinstance(payload, dict) else []


def extract_hazard_export_rows(deliveries: list[dict], year: Optional[int] = None) -> list[dict]:
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


def compute_nutrient_stream(deliveries: list[dict], year: int) -> dict:
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
            k: {"deliveries": int(v["deliveries"]), "n_kg": round(v["n_kg"], 3), "p2o5_kg": round(v["p2o5_kg"], 3)}
            for k, v in sorted(by_month.items())
        },
    }


def build_lot_trace_report(lot: Charge, deliveries: list[dict]) -> dict:
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


def seed_compliance_data(db: Session) -> None:
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
        db.add(SachkundeEintrag(
            kunde="Landwirtschaft Mueller",
            kundennr="K-10023",
            nachweis_nr="SK-NDS-2022-4567",
            ausstellungsdatum=datetime(2022, 3, 15),
            gueltig_bis=datetime(2025, 3, 15),
            ausstellende_stelle="LWK Niedersachsen",
            status="ablaufend",
        ))
    if db.query(SaatgutNachbauEintrag).count() == 0:
        db.add(SaatgutNachbauEintrag(
            betrieb="Landwirtschaft Mueller",
            sorte="Weichweizen Eltan",
            kultur="Weichweizen",
            flaeche=45.5,
            erntejahr=2024,
            gebuehr=682.50,
            status="bezahlt",
        ))
    if db.query(VVVOEintrag).count() == 0:
        db.add(VVVOEintrag(
            betriebsname="Landwirtschaft Mueller",
            vvvo="03-276-123456",
            bundesland="Niedersachsen",
            tierart="Rind (Milch)",
            status="aktiv",
            letzte_aktualisierung=datetime(2026, 1, 15),
        ))
    db.commit()


def _pdf_escape(s: str) -> str:
    r"""Escape ( ) \ for PDF literal strings."""
    if s is None:
        return ""
    return str(s).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _pdf_text_line(x: float, y: float, text: str, font: str = "/F1", size: int = 10) -> bytes:
    t = _pdf_escape(text)
    return f"BT {font} {size} Tf {x:.1f} {y:.1f} Td ({t}) Tj ET\n".encode("latin-1", errors="replace")


def build_compliance_pdf_bytes(stats: dict, cross_items: list[dict]) -> bytes:
    """Baut ein mehrseitiges PDF mit automatischen Längen, Seitenumbrüchen und Zwischensummen."""
    margin = 72
    line_height = 14
    font_size = 10
    font_title = 14
    page_width = 612
    page_height = 792
    lines_per_page = int((page_height - 2 * margin - 80) / line_height)
    max_data_lines = max(10, lines_per_page - 12)

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
            stream_parts.append(_pdf_text_line(margin, y, f"Fortsetzung Cross-Compliance (Seite {len(pages_data) + 1})", size=font_size))
            y -= line_height * 1.5

        stream_parts.append(_pdf_text_line(margin, y, "Bereich", size=font_size))
        stream_parts.append(_pdf_text_line(margin + 120, y, "Anforderung", size=font_size))
        stream_parts.append(_pdf_text_line(margin + 320, y, "Status", size=font_size))
        stream_parts.append(_pdf_text_line(margin + 400, y, "Frist", size=font_size))
        y -= line_height
        stream_parts.append(f"0.5 w {margin} {y:.1f} m {page_width - margin} {y:.1f} l S\n".encode("latin-1"))
        y -= 4

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
        if row_end < len(cross_items):
            stream_parts.append(_pdf_text_line(margin, y, f"Zwischensumme Seite {len(pages_data) + 1}: Erfuellt {cumulative_erfuellt}, Offen {cumulative_offen}"))
        else:
            stream_parts.append(_pdf_text_line(margin, y, f"Summe gesamt: Erfuellt {total_erfuellt}, Offen {total_offen}"))
        body = b"".join(stream_parts)
        pages_data.append((body, cumulative_erfuellt, cumulative_offen))
        row_start = row_end
        if row_start >= len(cross_items):
            break

    if not pages_data:
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
    obj_ids_pages = list(range(3, 3 + npages))
    obj_ids_contents = list(range(3 + npages, 3 + npages * 2))
    objects: list[tuple[int, str | bytes]] = []
    objects.append((1, "<</Type/Catalog/Pages 2 0 R>>"))
    kids = " ".join(f"{i} 0 R" for i in obj_ids_pages)
    objects.append((2, f"<< /Type /Pages /Kids [{kids}] /Count {npages} >>"))
    for p in range(npages):
        contents_ref = obj_ids_contents[p]
        objects.append((
            3 + p,
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            f"/Contents {contents_ref} 0 R >>",
        ))
    for p in range(npages):
        body = pages_data[p][0]
        length = len(body)
        objects.append((obj_ids_contents[p], f"<< /Length {length} >>\nstream\n".encode() + body + b"\nendstream"))

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
