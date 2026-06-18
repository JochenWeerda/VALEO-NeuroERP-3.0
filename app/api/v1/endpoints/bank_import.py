"""INT-BANK-001: Bank-API / SEPA-Import (MT940 + CAMT.053).

Importiert Kontoauszüge und matcht automatisch offene Posten:
- POST /bank/import/mt940   → MT940-Datei hochladen + parsen
- POST /bank/import/camt053 → CAMT.053 XML hochladen + parsen
- GET  /bank/statements     → importierte Auszüge
- POST /bank/match/{statement_id} → OP-Matching ausführen
"""
from __future__ import annotations

import io
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4
from xml.etree import ElementTree as ET

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/bank", tags=["schnittstellen", "bank", "zahlungsverkehr"])

# CAMT.053 Namespace
_CAMT_NS = "urn:iso:std:iso:20022:tech:xsd:camt.053.001.08"


# ── MT940-Parser ─────────────────────────────────────────────────────────────

def _parse_mt940(content: str) -> list[dict]:
    """Minimaler MT940-Parser. Extrahiert :61: Buchungszeilen."""
    transactions: list[dict] = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        # :61: Buchungszeile: YYMMDD[MMDD]C/D[R]BetragNWährungRef
        if line.startswith(":61:"):
            m = re.match(
                r":61:(\d{6})(\d{4})?(C|D|CR|DR)(\d+,\d*)(N\w+)(.*)",
                line,
            )
            if m:
                dt_str = m.group(1)
                side = "credit" if m.group(3).startswith("C") else "debit"
                amount = Decimal(m.group(4).replace(",", "."))
                ref = m.group(6).strip()
                # :86: Verwendungszweck
                purpose = ""
                if i + 1 < len(lines) and lines[i + 1].startswith(":86:"):
                    purpose = lines[i + 1][4:]
                try:
                    tx_date = datetime.strptime(dt_str, "%y%m%d").date()
                except ValueError:
                    tx_date = date.today()
                transactions.append({
                    "booking_date": str(tx_date),
                    "amount": float(amount),
                    "side": side,
                    "reference": ref,
                    "purpose": purpose,
                    "source": "MT940",
                })
        i += 1
    return transactions


# ── CAMT.053-Parser ──────────────────────────────────────────────────────────

def _parse_camt053(content: str) -> list[dict]:
    """CAMT.053.001.08 XML-Parser. Extrahiert Ntry-Einträge."""
    transactions: list[dict] = []
    try:
        root = ET.fromstring(content)
        ns = {"camt": _CAMT_NS}
        for ntry in root.findall(f".//{{{_CAMT_NS}}}Ntry"):
            amt_el = ntry.find(f"{{{_CAMT_NS}}}Amt")
            cd_el = ntry.find(f".//{{{_CAMT_NS}}}CdtDbtInd")
            date_el = ntry.find(f"{{{_CAMT_NS}}}BookgDt/{{{_CAMT_NS}}}Dt")
            ref_el = ntry.find(f".//{{{_CAMT_NS}}}EndToEndId")
            purp_el = ntry.find(f".//{{{_CAMT_NS}}}AddtlNtryInf")
            if amt_el is None:
                continue
            amount = Decimal(amt_el.text or "0")
            side = "credit" if (cd_el is not None and cd_el.text == "CRDT") else "debit"
            booking_date = date_el.text[:10] if date_el is not None else str(date.today())
            transactions.append({
                "booking_date": booking_date,
                "amount": float(amount),
                "side": side,
                "reference": ref_el.text if ref_el is not None else "",
                "purpose": purp_el.text if purp_el is not None else "",
                "source": "CAMT053",
            })
    except ET.ParseError as exc:
        raise HTTPException(status_code=422, detail=f"Ungültiges CAMT.053 XML: {exc}") from exc
    return transactions


# ── OP-Matching ──────────────────────────────────────────────────────────────

def _match_transactions(db: Session, tenant_id: str,
                        statement_id: str, transactions: list[dict]) -> dict:
    """Matcht Bankbuchungen gegen offene Posten.

    Strategie:
    1. Referenz-Match: purpose/reference enthält invoice_number oder settlement_number
    2. Betrag-Match: exakter Betrag ±0.01 EUR auf offene Debitoren-OP
    """
    matched = 0
    unmatched = 0
    for tx in transactions:
        if tx["side"] != "credit":
            unmatched += 1
            continue  # Einzahlungen matchen gegen AR-OPs

        amount = tx["amount"]
        purpose = (tx.get("purpose") or "") + " " + (tx.get("reference") or "")

        try:
            # 1. Referenz-Match
            op = db.execute(text("""
                SELECT id, betrag, offen, referenz_id, referenz_typ
                  FROM domain_erp.offene_posten
                 WHERE tenant_id = :tid
                   AND konto_typ = 'debitoren'
                   AND op_status = 'offen'
                   AND :purpose ILIKE '%' || referenz_id || '%'
                 LIMIT 1
            """), {"tid": tenant_id, "purpose": purpose}).fetchone()

            # 2. Betrag-Match (Fallback)
            if not op:
                op = db.execute(text("""
                    SELECT id, betrag, offen, referenz_id, referenz_typ
                      FROM domain_erp.offene_posten
                     WHERE tenant_id = :tid
                       AND konto_typ = 'debitoren'
                       AND op_status = 'offen'
                       AND ABS(offen - :amt) <= 0.01
                     ORDER BY faellig_am ASC
                     LIMIT 1
                """), {"tid": tenant_id, "amt": amount}).fetchone()
        except Exception:
            db.rollback()
            unmatched += 1
            continue

        if op:
            db.execute(text("""
                UPDATE domain_erp.offene_posten
                   SET offen = GREATEST(0, offen - :amt),
                       op_status = CASE WHEN offen - :amt <= 0.01 THEN 'ausgeziffert' ELSE op_status END,
                       updated_at = NOW()
                 WHERE id = :op_id AND tenant_id = :tid
            """), {"amt": amount, "op_id": str(op[0]), "tid": tenant_id})
            # Bank-Statement-Zeile als gebucht markieren
            db.execute(text("""
                WITH candidate AS (
                    SELECT id
                      FROM domain_finance.bank_statement_lines
                     WHERE statement_id = :sid AND booking_date = :bdate
                       AND ABS(amount - :amt) <= 0.01
                       AND match_status = 'offen'
                     LIMIT 1
                )
                UPDATE domain_finance.bank_statement_lines
                   SET match_status = 'gematcht', matched_op_id = :op_id
                 WHERE id IN (SELECT id FROM candidate)
            """), {"op_id": str(op[0]), "sid": statement_id,
                   "bdate": tx["booking_date"], "amt": amount})
            matched += 1
        else:
            unmatched += 1

    db.commit()
    return {"matched": matched, "unmatched": unmatched}


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/import/mt940", status_code=201, summary="MT940-Kontoauszug importieren (INT-BANK-001)")
async def import_mt940(
    file: UploadFile = File(..., description="MT940-Datei (.sta / .txt)"),
    iban: str = Query(..., description="IBAN des Kontos"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Importiert MT940 und persistiert als Bank-Statement mit Einzelbuchungen."""
    content = (await file.read()).decode("iso-8859-1", errors="replace")
    transactions = _parse_mt940(content)
    if not transactions:
        raise HTTPException(status_code=422, detail="Keine Buchungszeilen in MT940 gefunden")

    return _persist_statement(db, tenant_id, iban, transactions, "MT940", file.filename or "")


@router.post("/import/camt053", status_code=201, summary="CAMT.053 XML importieren (INT-BANK-001)")
async def import_camt053(
    file: UploadFile = File(..., description="CAMT.053 XML-Datei"),
    iban: str = Query(..., description="IBAN des Kontos"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Importiert CAMT.053 XML und persistiert als Bank-Statement."""
    content = (await file.read()).decode("utf-8", errors="replace")
    transactions = _parse_camt053(content)
    if not transactions:
        raise HTTPException(status_code=422, detail="Keine Ntry-Einträge in CAMT.053 gefunden")

    return _persist_statement(db, tenant_id, iban, transactions, "CAMT053", file.filename or "")


def _persist_statement(db: Session, tenant_id: str, iban: str,
                       transactions: list[dict], format_: str, filename: str) -> dict:
    statement_id = str(uuid7())
    try:
        db.execute(text("""
            INSERT INTO domain_finance.bank_statements
              (id, tenant_id, iban, format, filename, line_count, imported_at)
            VALUES
              (:id, :tid, :iban, :fmt, :fn, :cnt, NOW())
        """), {"id": statement_id, "tid": tenant_id, "iban": iban,
               "fmt": format_, "fn": filename, "cnt": len(transactions)})

        for tx in transactions:
            db.execute(text("""
                INSERT INTO domain_finance.bank_statement_lines
                  (id, statement_id, tenant_id, booking_date, amount, side,
                   reference, purpose, match_status, source)
                VALUES
                  (gen_random_uuid(), :sid, :tid, :bd, :amt, :side,
                   :ref, :purp, 'offen', :src)
            """), {"sid": statement_id, "tid": tenant_id,
                   "bd": tx["booking_date"], "amt": tx["amount"],
                   "side": tx["side"], "ref": tx.get("reference", ""),
                   "purp": tx.get("purpose", ""), "src": tx["source"]})

        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import fehlgeschlagen: {exc}") from exc

    return {"statement_id": statement_id, "lines": len(transactions),
            "iban": iban, "format": format_}


@router.post("/match/{statement_id}", summary="OP-Matching für importierten Auszug ausführen")
def run_matching(
    statement_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Matcht alle offenen Buchungen des Auszugs gegen Debitoren-OPs."""
    try:
        lines = db.execute(text("""
            SELECT booking_date, amount, side, reference, purpose
              FROM domain_finance.bank_statement_lines
             WHERE statement_id = :sid AND tenant_id = :tid AND match_status = 'offen'
        """), {"sid": statement_id, "tid": tenant_id}).fetchall()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not lines:
        return {"statement_id": statement_id, "matched": 0, "unmatched": 0,
                "info": "Keine offenen Buchungen"}

    txs = [{"booking_date": str(r[0]), "amount": float(r[1]),
             "side": str(r[2]), "reference": r[3], "purpose": r[4]}
           for r in lines]
    result = _match_transactions(db, tenant_id, statement_id, txs)
    return {"statement_id": statement_id, **result}


@router.get("/statements", summary="Importierte Kontoauszüge auflisten")
def list_statements(
    iban: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    where = "tenant_id = :tid"
    params: dict = {"tid": tenant_id, "lim": limit}
    if iban:
        where += " AND iban = :iban"
        params["iban"] = iban
    try:
        rows = db.execute(text(f"""
            SELECT id, iban, format, filename, line_count, imported_at
              FROM domain_finance.bank_statements
             WHERE {where}
             ORDER BY imported_at DESC
             LIMIT :lim
        """), params).fetchall()
        return {
            "items": [{"id": str(r[0]), "iban": r[1], "format": r[2],
                       "filename": r[3], "line_count": r[4],
                       "imported_at": r[5].isoformat() if r[5] else None}
                      for r in rows],
            "count": len(rows),
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
