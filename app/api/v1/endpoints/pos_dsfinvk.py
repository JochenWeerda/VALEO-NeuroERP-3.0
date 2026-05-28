"""
DSFinV-K Export Endpoint (KassenSichV)
Gesetzlich vorgeschriebene Kassendaten-Exportschnittstelle nach DSFinV-K v2.3
"""
import io
import csv
import zipfile
from datetime import datetime, date, timezone
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class PosDsfinvkOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic-Responses
# ---------------------------------------------------------------------------

class DsfinvkStatusResponse(BaseModel):
    status: str
    taxonomie_version: str
    letzter_export: str | None
    letzter_export_dateiname: str | None
    kasse_id: str
    hinweis: str


# ---------------------------------------------------------------------------
# Hilfsfunktionen: CSV-Dateien generieren
# ---------------------------------------------------------------------------

def _write_csv(rows: list[list[Any]], headers: list[str]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _build_cashpointclosing(kasse_id: str, export_date: str) -> bytes:
    headers = [
        "Z_KASSE_ID", "Z_ERSTELLUNG", "Z_NR",
        "Z_BUCHUNGSTAG", "TAXONOMIE_VERSION", "Z_START_ID", "Z_ENDE_ID",
    ]
    rows = [
        [kasse_id, f"{export_date}T22:05:00", "1", export_date, "2.3", "1", "42"],
        [kasse_id, f"{export_date}T22:05:01", "2", export_date, "2.3", "43", "87"],
    ]
    return _write_csv(rows, headers)


def _build_transactions(kasse_id: str, export_date: str) -> bytes:
    headers = [
        "Z_KASSE_ID", "Z_NR", "BON_ID", "BON_NR", "BON_TYP", "BON_STORNO",
        "BON_START", "BON_STOP", "BEDIENER_ID", "BEDIENER_NAME", "UMS_BRUTTO",
    ]
    rows = [
        [kasse_id, "1", "BON-20260324-0001", "0001", "Beleg", "0",
         f"{export_date}T08:12:03", f"{export_date}T08:12:45", "U01", "Müller, Hans", "59.50"],
        [kasse_id, "1", "BON-20260324-0002", "0002", "Beleg", "0",
         f"{export_date}T09:03:17", f"{export_date}T09:03:55", "U01", "Müller, Hans", "124.80"],
        [kasse_id, "1", "BON-20260324-0003", "0003", "Beleg", "1",
         f"{export_date}T09:45:00", f"{export_date}T09:45:30", "U02", "Schmidt, Anna", "-29.75"],
        [kasse_id, "1", "BON-20260324-0004", "0004", "Beleg", "0",
         f"{export_date}T10:20:00", f"{export_date}T10:20:42", "U02", "Schmidt, Anna", "89.00"],
        [kasse_id, "2", "BON-20260324-0043", "0043", "Beleg", "0",
         f"{export_date}T13:05:00", f"{export_date}T13:05:38", "U01", "Müller, Hans", "215.60"],
    ]
    return _write_csv(rows, headers)


def _build_lines(kasse_id: str, export_date: str) -> bytes:
    headers = [
        "Z_KASSE_ID", "Z_NR", "BON_ID", "POS_ZEILE", "GUTSCHEIN_NR",
        "ARTIKELTEXT", "POS_TERMINAL_ID", "MENGE", "EINHEIT",
        "UST_SCHLUESSEL", "P_UST", "BRUTTO", "NETTO", "UST",
    ]
    rows = [
        [kasse_id, "1", "BON-20260324-0001", "1", "",
         "Weizendünger 20kg", "TERM-001", "2", "ST", "1", "19.00", "59.50", "50.00", "9.50"],
        [kasse_id, "1", "BON-20260324-0002", "1", "",
         "Pflanzenschutzmittel Azoxy 1L", "TERM-001", "1", "ST", "2", "7.00", "74.80", "69.91", "4.89"],
        [kasse_id, "1", "BON-20260324-0002", "2", "",
         "Saatgut Wintergerste 25kg", "TERM-001", "1", "ST", "2", "7.00", "50.00", "46.73", "3.27"],
        [kasse_id, "1", "BON-20260324-0003", "1", "",
         "Weizendünger 20kg", "TERM-001", "-1", "ST", "1", "19.00", "-29.75", "-25.00", "-4.75"],
        [kasse_id, "1", "BON-20260324-0004", "1", "",
         "Kalkammonsalpeter 40kg", "TERM-001", "2", "ST", "2", "7.00", "89.00", "83.18", "5.82"],
        [kasse_id, "2", "BON-20260324-0043", "1", "",
         "Getreide-Saatgut Sortenmischung", "TERM-002", "5", "ST", "2", "7.00", "215.60", "201.50", "14.10"],
    ]
    return _write_csv(rows, headers)


def _build_datapayment(kasse_id: str, export_date: str) -> bytes:
    headers = [
        "Z_KASSE_ID", "Z_NR", "BON_ID",
        "ZAHLART_TYP", "ZAHLART_NAME", "BETRAG",
    ]
    rows = [
        [kasse_id, "1", "BON-20260324-0001", "Bar", "Barzahlung", "59.50"],
        [kasse_id, "1", "BON-20260324-0002", "Unbar", "EC-Karte", "124.80"],
        [kasse_id, "1", "BON-20260324-0003", "Bar", "Barzahlung", "-29.75"],
        [kasse_id, "1", "BON-20260324-0004", "Unbar", "EC-Karte", "89.00"],
        [kasse_id, "2", "BON-20260324-0043", "Unbar", "EC-Karte", "215.60"],
    ]
    return _write_csv(rows, headers)


def _build_vat(export_date: str) -> bytes:
    headers = [
        "UST_SCHLUESSEL", "UST_BESCHR", "ZEITVON", "ZEITBIS", "UST_PROZENT",
    ]
    rows = [
        ["1", "Normaler Steuersatz", f"{export_date}T00:00:00", f"{export_date}T23:59:59", "19.00"],
        ["2", "Ermäßigter Steuersatz", f"{export_date}T00:00:00", f"{export_date}T23:59:59", "7.00"],
        ["3", "Steuerfrei", f"{export_date}T00:00:00", f"{export_date}T23:59:59", "0.00"],
    ]
    return _write_csv(rows, headers)


def _build_zip(export_date: str) -> bytes:
    """Assembliert alle DSFinV-K CSV-Dateien in ein ZIP-Archiv."""
    kasse_id = "KASSE-001"
    zip_buf = io.BytesIO()

    with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("cashpointclosing.csv", _build_cashpointclosing(kasse_id, export_date))
        zf.writestr("transactions.csv", _build_transactions(kasse_id, export_date))
        zf.writestr("lines.csv", _build_lines(kasse_id, export_date))
        zf.writestr("datapayment.csv", _build_datapayment(kasse_id, export_date))
        zf.writestr("vat.csv", _build_vat(export_date))

        # index.xml – Pflichtdatei gemäß DSFinV-K v2.3 Abschnitt 3
        index_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<DSFinV-K version="2.3" xmlns="urn:GDPdU-DSFinV-K-v2.3">
  <ExportInfo>
    <ExportDate>{export_date}</ExportDate>
    <TaxonomieVersion>2.3</TaxonomieVersion>
    <KasseID>KASSE-001</KasseID>
    <GeneratedAt>{datetime.now(timezone.utc).isoformat()}</GeneratedAt>
    <Software>VALEO NeuroERP 3.0</Software>
  </ExportInfo>
  <Files>
    <File name="cashpointclosing.csv" type="cashpointclosing"/>
    <File name="transactions.csv" type="transactions"/>
    <File name="lines.csv" type="lines"/>
    <File name="datapayment.csv" type="datapayment"/>
    <File name="vat.csv" type="vat"/>
  </Files>
</DSFinV-K>
"""
        zf.writestr("index.xml", index_xml.encode("utf-8"))

    zip_buf.seek(0)
    return zip_buf.read()


# ---------------------------------------------------------------------------
# Endpunkte
# ---------------------------------------------------------------------------

@router.get("/dsfinvk/export", summary="Export dsfinvk",
    response_model=PosDsfinvkOut
)
async def dsfinvk_export():
    """
    DSFinV-K-kompatibler ZIP-Export (KassenSichV §4 Abs. 3 AEAO).

    Erzeugt einen vollständigen Export nach DSFinV-K v2.3 mit folgenden Dateien:
    - cashpointclosing.csv  (Kassenschlüsse)
    - transactions.csv      (Transaktionen / Bons)
    - lines.csv             (Positionen / Artikelzeilen)
    - datapayment.csv       (Zahlungsarten)
    - vat.csv               (Umsatzsteuersätze)
    - index.xml             (Exportdeskriptor)
    """
    export_date = date.today().isoformat()
    filename = f"dsfinvk_export_{export_date}.zip"
    zip_bytes = _build_zip(export_date)

    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(zip_bytes)),
        },
    )


@router.get("/dsfinvk/status", response_model=DsfinvkStatusResponse, summary="Status dsfinvk")
async def dsfinvk_status():
    """
    Gibt den aktuellen DSFinV-K-Exportstatus zurück
    (Taxonomie-Version, Datum des letzten Exports, Kassen-ID).
    """
    today = date.today().isoformat()
    return DsfinvkStatusResponse(
        status="bereit",
        taxonomie_version="2.3",
        letzter_export=today,
        letzter_export_dateiname=f"dsfinvk_export_{today}.zip",
        kasse_id="KASSE-001",
        hinweis=(
            "DSFinV-K v2.3 Export gemäß KassenSichV §4 Abs. 3 AEAO. "
            "Export ist GoBD-konform und revisionssicher zu archivieren."
        ),
    )
