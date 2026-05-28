"""
GS1 barcode parser endpoint (l3c-gs1)
Parses GS1-128 / GS1 DataMatrix barcodes into structured AI data.
"""


from fastapi import APIRouter
from pydantic import BaseModel

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter()

# GS1 Application Identifier definitions (subset)
AI_DEFS: dict[str, tuple[str, int | None]] = {
    "01": ("GTIN", 14),
    "02": ("CONTENT", 14),
    "10": ("BATCH", None),
    "11": ("PROD_DATE", 6),
    "13": ("PACK_DATE", 6),
    "15": ("BEST_BEFORE", 6),
    "17": ("EXPIRY", 6),
    "20": ("VARIANT", 2),
    "21": ("SERIAL", None),
    "30": ("VAR_COUNT", None),
    "37": ("COUNT", None),
    "310": ("NET_WEIGHT_KG", 6),
    "3100": ("NET_WEIGHT_KG_0", 6),
    "3101": ("NET_WEIGHT_KG_1", 6),
    "3102": ("NET_WEIGHT_KG_2", 6),
    "3103": ("NET_WEIGHT_KG_3", 6),
    "3900": ("AMOUNT", None),
    "400": ("ORDER_NUMBER", None),
    "410": ("SHIP_TO_LOC", 13),
    "420": ("SHIP_TO_POST", None),
    "00": ("SSCC", 18),
}


class GS1ParseRequest(BaseModel):
    barcode: str


class GS1ParseResponse(BaseModel):
    raw: str
    elements: dict[str, str]
    errors: list[str]


def _parse_gs1(raw: str) -> tuple[dict[str, str], list[str]]:
    """Parse a GS1-128 / DataMatrix barcode string."""
    elements: dict[str, str] = {}
    errors: list[str] = []
    # Replace FNC1 / GS characters
    data = raw.replace("\x1d", "|").replace("(", "").replace(")", "")
    pos = 0
    while pos < len(data):
        if data[pos] == "|":
            pos += 1
            continue
        matched = False
        # Try longest AI first (4, 3, 2 chars)
        for ai_len in (4, 3, 2):
            ai = data[pos:pos + ai_len]
            if ai in AI_DEFS:
                name, fixed_len = AI_DEFS[ai]
                pos += ai_len
                if fixed_len:
                    val = data[pos:pos + fixed_len]
                    pos += fixed_len
                else:
                    end = data.find("|", pos)
                    if end == -1:
                        end = len(data)
                    val = data[pos:end]
                    pos = end
                elements[name] = val
                matched = True
                break
        if not matched:
            errors.append(f"Unknown AI at position {pos}: {data[pos:pos+4]}")
            pos += 1
    return elements, errors


@router.post("/parse", response_model=GS1ParseResponse, summary="Gs1 barcode parse")
async def parse_gs1_barcode(payload: GS1ParseRequest):
    """POST GS1 Parse – parses GS1-128/DataMatrix barcodes."""
    elements, errors = _parse_gs1(payload.barcode)
    return GS1ParseResponse(raw=payload.barcode, elements=elements, errors=errors)
