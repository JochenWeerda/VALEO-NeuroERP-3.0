"""
Payroll (Lohn) Connector – Parser für Lohnbuchungen (CSV/ASC).
"""

from __future__ import annotations

import csv
import io
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List

from .base import ConnectorParser, NormalizedItem, NormalizedLine
from app.core.data_quality_enforcement import (
    DQValidationException,
    evaluate_payroll_connector_datensatz,
)


class PayrollParser(ConnectorParser):
    """Konfigurierbarer CSV/ASC-Parser für Lohn-Exporte."""

    def detect(self, raw: bytes, settings: Dict[str, Any]) -> bool:
        try:
            content = raw.decode(settings.get("encoding", "utf-8-sig"))
            delim = settings.get("delimiter", ";")
            reader = csv.reader(io.StringIO(content), delimiter=delim)
            first = next(reader, None)
            return first is not None and len(first) >= 3
        except Exception:
            return False

    def parse(self, raw: bytes, settings: Dict[str, Any], mapping: Dict[str, Any]) -> List[NormalizedItem]:
        encoding = settings.get("encoding", "utf-8-sig")
        delimiter = settings.get("delimiter", ";")
        date_fmt = mapping.get("date_column") or "buchungsdatum"
        doc_no = mapping.get("document_no_column") or "belegnummer"
        text_col = mapping.get("text_column") or "buchungstext"
        account_col = mapping.get("account_column") or "konto"
        amount_col = mapping.get("amount_column") or "betrag"
        dc_col = mapping.get("dc_column")  # Soll/Haben oder "soll"/"haben"

        content = raw.decode(encoding)
        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            return []

        # Header aus erster Zeile
        headers = [h.strip().strip("\ufeff") for h in rows[0].keys()] if rows else []
        items: List[NormalizedItem] = []
        current_doc: Dict[str, Any] = {}
        current_lines: List[NormalizedLine] = []

        for row_number, row in enumerate(rows, start=2):
            row = {k.strip().strip("\ufeff"): (v.strip() if v else "") for k, v in row.items()}
            date_str = row.get(date_fmt) or row.get("buchungsdatum") or row.get("entry_date", "")
            doc_no_val = row.get(doc_no) or row.get("belegnummer") or ""
            text_val = row.get(text_col) or row.get("buchungstext") or row.get("description", "")
            account = row.get(account_col) or row.get("konto") or row.get("account_number", "")
            amt_str = row.get(amount_col) or row.get("betrag") or row.get("debit_amount") or row.get("credit_amount") or "0"
            dc_val = (row.get(dc_col) or row.get("soll_haben") or "S").strip().upper()[:1]

            dq_result = evaluate_payroll_connector_datensatz(
                {
                    "booking_date": date_str,
                    "account": account,
                    "amount": str(amt_str).replace(",", "."),
                    "dc": dc_val,
                }
            )
            if not dq_result.bestanden:
                raise DQValidationException(
                    "PayrollConnectorImport",
                    dq_result,
                ) from ValueError(f"Invalid payroll connector row {row_number}")

            try:
                amount = Decimal(str(amt_str).replace(",", "."))
            except (InvalidOperation, ValueError):
                raise ValueError(f"Invalid payroll amount in row {row_number}: {amt_str}")

            dc = "D" if dc_val in ("S", "D", "1") else "C"
            line = NormalizedLine(account=account, dc=dc, amount=amount)
            line.tax_code = row.get("steuerschluessel") or row.get("tax_code")
            line.cost_center = row.get("kostenstelle") or row.get("cost_center")

            doc_key = f"{date_str}_{doc_no_val}"
            if current_doc.get("_key") != doc_key and current_doc and current_lines:
                item = _lines_to_item(current_doc, current_lines)
                if item:
                    items.append(item)
                current_doc = {}
                current_lines = []

            current_doc["_key"] = doc_key
            current_doc["date"] = _normalize_date(date_str)
            current_doc["doc_no"] = doc_no_val or f"LOHN-{date_str}"
            current_doc["text"] = text_val or "Lohnbuchung"
            current_lines.append(line)

        if current_doc and current_lines:
            item = _lines_to_item(current_doc, current_lines)
            if item:
                items.append(item)

        return items


def _normalize_date(s: str) -> str:
    if len(s) == 10 and s[4] == "-":
        return s
    if len(s) == 8:
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    if len(s) == 10 and s[2] in (".", "/"):
        parts = s.replace("/", ".").split(".")
        if len(parts) == 3:
            d, m, y = parts[0].zfill(2), parts[1].zfill(2), parts[2]
            if len(y) == 2:
                y = "20" + y
            return f"{y}-{m}-{d}"
    return s


def _lines_to_item(doc: Dict[str, Any], lines: List[NormalizedLine]) -> NormalizedItem | None:
    if not lines:
        return None
    return NormalizedItem(
        booking_date=doc["date"],
        document_no=doc["doc_no"],
        text=doc["text"],
        lines=lines,
    )
