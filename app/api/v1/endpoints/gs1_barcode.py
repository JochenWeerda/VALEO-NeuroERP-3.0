"""
GS1 Barcode Parse Service
Analog externe Agrar-ERP-Plattform POST /service/gs1/api/v1/gs1/action/parse
"""

from __future__ import annotations

import re
from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class GS1ParseInput(BaseModel):
    barcode_string: str
    format: str = "AUTO"  # EAN13 / EAN128 / DATAMATRIX / QR / AUTO


class GS1ParseResult(BaseModel):
    raw: str
    format_erkannt: str
    ai_felder: dict[str, Any]
    sscc: Optional[str] = None
    gtin: Optional[str] = None
    charge_nr: Optional[str] = None
    verfallsdatum: Optional[str] = None
    menge: Optional[float] = None
    seriennummer: Optional[str] = None
    gewicht_kg: Optional[float] = None
    lieferdatum: Optional[str] = None
    fehler: Optional[str] = None


# ---------------------------------------------------------------------------
# GS1 Parse helpers
# ---------------------------------------------------------------------------

_YYMMDD_RE = re.compile(r"^(\d{2})(\d{2})(\d{2})$")


def _convert_yymmdd(raw: str) -> str:
    """Convert YYMMDD → YYYY-MM-DD (assume 20xx)."""
    m = _YYMMDD_RE.match(raw)
    if not m:
        return raw
    yy, mm, dd = m.group(1), m.group(2), m.group(3)
    return f"20{yy}-{mm}-{dd}"


def _parse_ai_string(s: str) -> dict[str, str]:
    """Parse a GS1-128 string with AIs in parentheses: (01)...(10)..."""
    result: dict[str, str] = {}
    pattern = re.compile(r"\((\d{2,4})\)([^(]*)")
    for m in pattern.finditer(s):
        result[m.group(1)] = m.group(2).strip()
    return result


def _parse_gs1(barcode: str, fmt: str) -> GS1ParseResult:
    raw = barcode.strip()
    ai_felder: dict[str, Any] = {}
    format_erkannt = fmt
    sscc = gtin = charge_nr = verfallsdatum = seriennummer = lieferdatum = None
    menge: Optional[float] = None
    gewicht_kg: Optional[float] = None
    fehler: Optional[str] = None

    try:
        # Auto-detect
        if fmt == "AUTO":
            if raw.startswith("]d2") or raw.startswith("]C1"):
                format_erkannt = "DATAMATRIX"
            elif raw.startswith("("):
                format_erkannt = "EAN128"
            elif re.fullmatch(r"\d{13}", raw):
                format_erkannt = "EAN13"
            else:
                format_erkannt = "EAN128"

        if format_erkannt == "EAN13":
            gtin = raw[:13]
            ai_felder["01"] = gtin

        elif format_erkannt in ("EAN128", "DATAMATRIX", "QR"):
            # Strip DataMatrix prefix
            stripped = raw
            if stripped.startswith("]d2") or stripped.startswith("]C1"):
                stripped = stripped[3:]

            if "(" in stripped:
                ai_felder = _parse_ai_string(stripped)
            else:
                # raw concatenated AIs without parentheses — best-effort
                ai_felder = {}

            # Extract known AIs
            if "00" in ai_felder:
                sscc = ai_felder["00"]
            if "01" in ai_felder:
                gtin = ai_felder["01"]
            if "10" in ai_felder:
                charge_nr = ai_felder["10"]
            if "17" in ai_felder:
                verfallsdatum = _convert_yymmdd(ai_felder["17"])
                ai_felder["17"] = verfallsdatum
            if "21" in ai_felder:
                seriennummer = ai_felder["21"]
            if "30" in ai_felder:
                try:
                    menge = float(ai_felder["30"])
                except ValueError:
                    pass
            if menge is None and "37" in ai_felder:
                try:
                    menge = float(ai_felder["37"])
                except ValueError:
                    pass
            if "13" in ai_felder:
                lieferdatum = _convert_yymmdd(ai_felder["13"])
                ai_felder["13"] = lieferdatum
            # Weight AIs 3100-3109
            for ai_key in ai_felder:
                if re.fullmatch(r"310\d", ai_key):
                    dec_pos = int(ai_key[3])
                    try:
                        raw_val = float(ai_felder[ai_key]) / (10 ** dec_pos)
                        gewicht_kg = raw_val
                    except ValueError:
                        pass
                    break

    except Exception as exc:  # noqa: BLE001
        fehler = str(exc)

    return GS1ParseResult(
        raw=raw,
        format_erkannt=format_erkannt,
        ai_felder=ai_felder,
        sscc=sscc,
        gtin=gtin,
        charge_nr=charge_nr,
        verfallsdatum=verfallsdatum,
        menge=menge,
        seriennummer=seriennummer,
        gewicht_kg=gewicht_kg,
        lieferdatum=lieferdatum,
        fehler=fehler,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/parse", response_model=GS1ParseResult, tags=["gs1", "barcode"])
def parse_gs1(payload: GS1ParseInput) -> GS1ParseResult:
    """Parse a single GS1 barcode string and return structured AI fields."""
    return _parse_gs1(payload.barcode_string, payload.format)


@router.post("/batch-parse", response_model=list[GS1ParseResult], tags=["gs1", "barcode"])
def batch_parse_gs1(payloads: list[GS1ParseInput]) -> list[GS1ParseResult]:
    """Parse up to 100 GS1 barcodes in one call."""
    if len(payloads) > 100:
        payloads = payloads[:100]
    return [_parse_gs1(p.barcode_string, p.format) for p in payloads]
