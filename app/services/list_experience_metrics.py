"""Read-only list metrics shared across registered human/MCP/CLI projections."""
from decimal import Decimal, InvalidOperation
import re
from fastapi import HTTPException


def _matches(row, condition):
    raw = row.get(condition["field"])
    text = "" if raw is None else str(raw).lower() if isinstance(raw, bool) else str(raw)
    equal = text == condition["value"]
    return equal if condition["op"] == "eq" else not equal


def metric_currencies(experience: dict, rows: list[dict]) -> dict[str, str]:
    # Called only after successful metric validation; expose the actual unit to CLI/MCP.
    return {aggregate["key"]: next((str(row[aggregate["currencyField"]]) for row in rows
            if all(_matches(row, condition) for condition in aggregate["conditions"])), "EUR")
            for aggregate in experience.get("aggregates", []) if aggregate.get("currencyField")}


def list_metrics(experience: dict, rows: list[dict]) -> dict[str, int | float]:
    values = {}
    for aggregate in experience.get("aggregates", []):
        selected = []
        for row in rows:
            if all(_matches(row, condition) for condition in aggregate["conditions"]):
                selected.append(row)
        if aggregate.get("kind", "count") != "sum":
            values[aggregate["key"]] = len(selected)
            continue
        try:
            if aggregate.get("currencyField"):
                currencies = {row.get(aggregate["currencyField"]) for row in selected}
                if len(currencies) > 1 or any(not isinstance(code, str) or not re.fullmatch(r"[A-Z]{3}", code) for code in currencies):
                    raise ValueError("mixed currency")
            total = Decimal("0")
            for row in selected:
                raw = row.get(aggregate["field"])
                if isinstance(raw, bool) or not isinstance(raw, (str, int, float, Decimal)) or not re.fullmatch(r"-?[0-9]+(?:\.[0-9]{1,2})?", str(raw)):
                    raise ValueError("invalid money")
                amount = Decimal(str(raw))
                if not amount.is_finite():
                    raise ValueError("nonfinite money")
                total += amount
            if abs(total) > Decimal("900719925474.00"):
                raise ValueError("money bound")
            values[aggregate["key"]] = float(total)
        except (InvalidOperation, TypeError, ValueError, KeyError) as error:
            raise HTTPException(409, "Listenkennzahlen besitzen keinen sicheren Summenvertrag") from error
    return values
