"""Deterministic inventory, analysis and price readiness rules."""
from __future__ import annotations
from datetime import date, datetime
from typing import Any

def _days_old(value: date | datetime | None, as_of: date) -> int | None:
    if value is None: return None
    return (as_of - (value.date() if isinstance(value, datetime) else value)).days

def evaluate_material(*, feed_id: str | None, name: str, daily_kg: float,
    stock_kg: float | None, forage: bool, analysis_id: str | None,
    analysis_date: date | None, selected_analysis_id: str | None,
    price_eur_t: float | None, price_valid_from: date | None,
    price_valid_to: date | None, price_updated_at: datetime | None,
    as_of: date) -> dict[str, Any]:
    """Return one explainable readiness row without persistence side effects."""
    issues: list[dict[str, str]] = []
    reach_days = None if stock_kg is None or daily_kg <= 0 else round(stock_kg / daily_kg, 1)
    if stock_kg is not None and daily_kg > 0:
        if stock_kg <= 0 or (reach_days is not None and reach_days < 3):
            issues.append({"code": "stock_critical", "severity": "blocker", "message": "Bestand reicht weniger als drei Tage."})
        elif reach_days is not None and reach_days < 14:
            issues.append({"code": "stock_low", "severity": "warning", "message": "Reichweite liegt unter 14 Tagen."})
    elif daily_kg > 0:
        issues.append({"code": "inventory_unmapped", "severity": "warning", "message": "Keine eindeutige Bestandszuordnung vorhanden."})
    analysis_age_days = _days_old(analysis_date, as_of)
    if forage and not analysis_id:
        issues.append({"code": "analysis_missing", "severity": "blocker", "message": "Grundfutter hat keine verifizierbare Laboranalyse."})
    elif forage and analysis_age_days is not None and analysis_age_days > 90:
        issues.append({"code": "analysis_stale", "severity": "warning", "message": "Laboranalyse ist aelter als 90 Tage."})
    if selected_analysis_id and analysis_id and selected_analysis_id != analysis_id:
        issues.append({"code": "analysis_changed", "severity": "warning", "message": "Seit dem Entwurf liegt eine neuere Analyse vor."})
    price_age_days = _days_old(price_updated_at, as_of)
    if price_eur_t is None:
        issues.append({"code": "price_missing", "severity": "blocker", "message": "Kein Preisstand vorhanden."})
    elif price_valid_from and price_valid_from > as_of:
        issues.append({"code": "price_not_yet_valid", "severity": "blocker", "message": "Preisstand ist noch nicht gueltig."})
    elif price_valid_to and price_valid_to < as_of:
        issues.append({"code": "price_expired", "severity": "blocker", "message": "Preisstand ist abgelaufen."})
    elif not price_valid_to and price_age_days is not None and price_age_days > 90:
        issues.append({"code": "price_stale", "severity": "warning", "message": "Preisstand ist aelter als 90 Tage."})
    status = "blocked" if any(i["severity"] == "blocker" for i in issues) else ("warning" if issues else "ready")
    return {"feed_id": feed_id, "name": name, "daily_kg": round(max(0.0, daily_kg), 3),
        "stock_kg": None if stock_kg is None else round(stock_kg, 3), "reach_days": reach_days,
        "analysis_id": analysis_id, "analysis_date": analysis_date,
        "analysis_age_days": analysis_age_days, "price_eur_t": price_eur_t,
        "price_valid_to": price_valid_to, "status": status, "issues": issues,
        "issue_summary": " | ".join(i["message"] for i in issues) or "Einsatzbereit"}

def summarize(rows: list[dict[str, Any]], as_of: date) -> dict[str, Any]:
    blockers = sum(1 for row in rows for issue in row["issues"] if issue["severity"] == "blocker")
    warnings = sum(1 for row in rows for issue in row["issues"] if issue["severity"] == "warning")
    return {"as_of": as_of, "status": "blocked" if blockers else ("warning" if warnings else "ready"),
        "blocker_count": blockers, "warning_count": warnings, "materials": rows}
