"""
VALEO Suite Anlagen (Asset Ledger) – Parser für Abschreibungs-/Anlagenbuchungen.
"""

from __future__ import annotations

import csv
import io
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List

from .base import ConnectorParser, NormalizedItem, NormalizedLine
from app.core.data_quality_enforcement import (
    DQValidationException,
    evaluate_asset_ledger_connector_datensatz,
)


class AssetLedgerParser(ConnectorParser):
    """Parser für Anlagenbuchhaltung-Exporte (Anlagen, Abschreibungen, Abgänge)."""

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
        asset_no_col = mapping.get("asset_no_column") or "anlagennr"
        posting_type_col = mapping.get("posting_type_column") or "buchungsart"

        content = raw.decode(encoding)
        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            return []

        items: List[NormalizedItem] = []
        for row_number, row in enumerate(rows, start=2):
            row = {k.strip().strip("\ufeff"): (v.strip() if v else "") for k, v in row.items()}
            date_str = row.get(date_fmt) or row.get("buchungsdatum") or row.get("entry_date", "")
            doc_no_val = row.get(doc_no) or row.get("belegnummer") or ""
            text_val = row.get(text_col) or row.get("buchungstext") or "Anlagenbuchhaltung"
            account = row.get(account_col) or row.get("konto", "")
            amt_str = row.get(amount_col) or row.get("betrag") or "0"
            asset_no = row.get(asset_no_col) or row.get("anlagennr")
            posting_type = row.get(posting_type_col) or row.get("buchungsart")

            dc_col = mapping.get("dc_column") or "soll_haben"
            dc_val = (row.get(dc_col) or row.get("soll_haben") or "S").strip().upper()[:1]
            dq_result = evaluate_asset_ledger_connector_datensatz(
                {
                    "booking_date": date_str,
                    "account": account,
                    "amount": str(amt_str).replace(",", "."),
                    "dc": dc_val,
                }
            )
            if not dq_result.bestanden:
                raise DQValidationException(
                    "AssetLedgerConnectorImport",
                    dq_result,
                ) from ValueError(f"Invalid asset-ledger connector row {row_number}")

            try:
                amount = Decimal(str(amt_str).replace(",", "."))
            except (InvalidOperation, ValueError):
                raise ValueError(f"Invalid asset-ledger amount in row {row_number}: {amt_str}")

            dc = "D" if dc_val in ("S", "D", "1") else "C"
            line = NormalizedLine(account=account, dc=dc, amount=amount)
            line.cost_center = row.get("kostenstelle") or row.get("cost_center")

            contra = row.get("gegenkonto") or row.get("contra_account")
            doc_prefix = doc_no_val or f"ANL-{date_str}"
            if contra:
                contra_dc = "C" if dc == "D" else "D"
                items.append(
                    NormalizedItem(
                        booking_date=_normalize_date(date_str),
                        document_no=doc_prefix,
                        text=text_val,
                        lines=[line, NormalizedLine(account=contra, dc=contra_dc, amount=amount)],
                        asset_no=asset_no,
                        posting_type=posting_type,
                    )
                )
            else:
                items.append(
                    NormalizedItem(
                        booking_date=_normalize_date(date_str),
                        document_no=doc_prefix,
                        text=text_val,
                        lines=[line],
                        asset_no=asset_no,
                        posting_type=posting_type,
                    )
                )

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
