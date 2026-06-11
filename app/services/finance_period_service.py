"""Periodenabschluss & Storno-Konsistenz (DOM-FIN-004.4).

Steuerung der Buchungsperioden (public.finance_accounting_periods): Perioden listen,
Abschlussreife prüfen (keine offenen oder Storno-inkonsistenten Posten in der Periode)
und Periode schließen/wieder öffnen. Ist die Periodentabelle leer, werden die Perioden
aus den vorhandenen OP-Daten (Rechnungsmonat) abgeleitet — self-contained, ohne Seed.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def period_bounds(period: str) -> tuple[date, date]:
    """('YYYY-MM') → (erster, letzter Tag des Monats)."""
    y, m = int(period[:4]), int(period[5:7])
    start = date(y, m, 1)
    end = date(y + (m // 12), (m % 12) + 1, 1)
    from datetime import timedelta
    return start, end - timedelta(days=1)


def close_readiness(offen_count: int, storno_inkonsistent_count: int) -> dict:
    """Reine Abschlussreife-Prüfung. Liefert ready + Blocker-Liste."""
    blocker = []
    if offen_count > 0:
        blocker.append(f"{offen_count} offene Posten in der Periode")
    if storno_inkonsistent_count > 0:
        blocker.append(f"{storno_inkonsistent_count} Storno-inkonsistente Posten (storniert, aber offen > 0)")
    return {"ready": not blocker, "blocker": blocker}


class PeriodError(Exception):
    """Fachlicher Fehler bei der Periodensteuerung (→ HTTP 422)."""


class FinancePeriodService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _stored(self) -> dict[str, dict]:
        rows = self.db.execute(
            text("SELECT period, status, closed_at, closed_by FROM public.finance_accounting_periods "
                 "WHERE tenant_id = :t"),
            {"t": self.tenant_id},
        ).mappings().all()
        return {r["period"]: dict(r) for r in rows}

    def _derived_periods(self) -> list[str]:
        rows = self.db.execute(
            text("SELECT DISTINCT to_char(COALESCE(rechnungsdatum, faelligkeit, due_date), 'YYYY-MM') AS p "
                 "FROM domain_erp.offene_posten WHERE tenant_id = :t "
                 "AND COALESCE(rechnungsdatum, faelligkeit, due_date) IS NOT NULL"),
            {"t": self.tenant_id},
        ).mappings().all()
        return sorted({r["p"] for r in rows if r["p"]})

    def _period_metrics(self, period: str) -> dict:
        start, end = period_bounds(period)
        offen = self.db.execute(
            text("SELECT count(*) FROM domain_erp.offene_posten WHERE tenant_id = :t "
                 "AND COALESCE(rechnungsdatum, faelligkeit, due_date) BETWEEN :s AND :e "
                 "AND COALESCE(op_status,'') <> 'storniert' "
                 "AND COALESCE(offen, open_amount, betrag, 0) > 0"),
            {"t": self.tenant_id, "s": start, "e": end},
        ).scalar() or 0
        inkons = self.db.execute(
            text("SELECT count(*) FROM domain_erp.offene_posten WHERE tenant_id = :t "
                 "AND COALESCE(rechnungsdatum, faelligkeit, due_date) BETWEEN :s AND :e "
                 "AND COALESCE(op_status,'') = 'storniert' "
                 "AND COALESCE(offen, open_amount, betrag, 0) > 0"),
            {"t": self.tenant_id, "s": start, "e": end},
        ).scalar() or 0
        return {"offen_count": int(offen), "storno_inkonsistent": int(inkons)}

    def list_periods(self) -> list[dict]:
        stored = self._stored()
        periods = sorted(set(self._derived_periods()) | set(stored.keys()), reverse=True)
        out = []
        for p in periods:
            metrics = self._period_metrics(p)
            r = close_readiness(metrics["offen_count"], metrics["storno_inkonsistent"])
            st = stored.get(p)
            start, end = period_bounds(p)
            out.append({
                "period": p, "start": start.isoformat(), "end": end.isoformat(),
                "status": (st["status"] if st else "offen"),
                "closed_at": (st["closed_at"].isoformat() if st and st.get("closed_at") else None),
                "closed_by": st["closed_by"] if st else None,
                **metrics, "abschlussreif": r["ready"],
            })
        return out

    def readiness(self, period: str) -> dict[str, Any]:
        metrics = self._period_metrics(period)
        r = close_readiness(metrics["offen_count"], metrics["storno_inkonsistent"])
        return {"period": period, **metrics, **r}

    def close_period(self, period: str, bediener: str = "KIM", force: bool = False) -> dict[str, Any]:
        stored = self._stored().get(period)
        if stored and stored["status"] == "closed":
            raise PeriodError(f"Periode {period} ist bereits abgeschlossen.")
        metrics = self._period_metrics(period)
        r = close_readiness(metrics["offen_count"], metrics["storno_inkonsistent"])
        if not r["ready"] and not force:
            raise PeriodError("Periode nicht abschlussreif: " + "; ".join(r["blocker"]))
        start, end = period_bounds(period)
        if stored:
            self.db.execute(
                text("UPDATE public.finance_accounting_periods SET status='closed', closed_at=now(), "
                     "closed_by=:by WHERE period=:p AND tenant_id=:t"),
                {"by": bediener, "p": period, "t": self.tenant_id},
            )
        else:
            self.db.execute(
                text("INSERT INTO public.finance_accounting_periods "
                     "(id, tenant_id, period, status, start_date, end_date, closed_at, closed_by) "
                     "VALUES (:id, :t, :p, 'closed', :s, :e, now(), :by)"),
                {"id": str(uuid.uuid4()), "t": self.tenant_id, "p": period, "s": start, "e": end, "by": bediener},
            )
        self.db.commit()
        return {"ok": True, "period": period, "status": "closed", "erzwungen": force and not r["ready"]}

    def reopen_period(self, period: str, grund: str, bediener: str = "KIM") -> dict[str, Any]:
        if not (grund or "").strip():
            raise PeriodError("Grund für die Wiedereröffnung ist erforderlich.")
        stored = self._stored().get(period)
        if not stored or stored["status"] != "closed":
            raise PeriodError(f"Periode {period} ist nicht abgeschlossen.")
        self.db.execute(
            text("UPDATE public.finance_accounting_periods SET status='offen', closed_at=NULL, closed_by=NULL, "
                 "metadata = COALESCE(metadata,'{}'::jsonb) || jsonb_build_object('reopen_grund', :g, 'reopen_by', :by) "
                 "WHERE period=:p AND tenant_id=:t"),
            {"g": grund, "by": bediener, "p": period, "t": self.tenant_id},
        )
        self.db.commit()
        return {"ok": True, "period": period, "status": "offen"}
