"""Kunden-Ownership (DOM-CRM-004.3) — Zuordnung & Übergabe.

Owner je Kunde: Außendienst (`sales_rep_vb`) und Innendienst (`dispatcher_disp`)
im Satelliten public.kunden_crm360. Änderungen werden append-only in
public.crm_ownership_log protokolliert (Übergabe-Nachweis). Zusätzlich:
„ohne Zuordnung"-Worklist und Workload je Owner.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


class CrmOwnershipService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def get(self, kunden_nr: str) -> dict:
        r = self.db.execute(
            text("SELECT sales_rep_vb, dispatcher_disp FROM public.kunden_crm360 WHERE kunden_nr = :k"),
            {"k": kunden_nr},
        ).mappings().first()
        return {
            "kunden_nr": kunden_nr,
            "sales_rep": (r["sales_rep_vb"] if r else None),
            "dispatcher": (r["dispatcher_disp"] if r else None),
        }

    def _log(self, kunden_nr: str, feld: str, alt: Optional[str], neu: Optional[str],
             grund: Optional[str], bediener: str) -> None:
        self.db.execute(
            text("INSERT INTO public.crm_ownership_log (id, tenant_id, kunden_nr, feld, alt, neu, grund, bediener) "
                 "VALUES (:id, :t, :k, :f, :a, :n, :g, :by)"),
            {"id": str(uuid.uuid4()), "t": self.tenant_id, "k": kunden_nr, "f": feld,
             "a": alt, "n": neu, "g": grund, "by": bediener},
        )

    def set(self, kunden_nr: str, *, sales_rep: Optional[str] = None,
            dispatcher: Optional[str] = None, grund: Optional[str] = None,
            bediener: str = "KIM") -> dict:
        """Setzt Owner-Felder (nur übergebene) und protokolliert Änderungen.
        Legt bei Bedarf den kunden_crm360-Satelliten an (Upsert)."""
        current = self.get(kunden_nr)
        self.db.execute(
            text("INSERT INTO public.kunden_crm360 (kunden_nr) VALUES (:k) ON CONFLICT (kunden_nr) DO NOTHING"),
            {"k": kunden_nr},
        )
        changed = {}
        if sales_rep is not None and (sales_rep or None) != current["sales_rep"]:
            self.db.execute(
                text("UPDATE public.kunden_crm360 SET sales_rep_vb = :v, updated_at = now() WHERE kunden_nr = :k"),
                {"v": sales_rep or None, "k": kunden_nr},
            )
            self._log(kunden_nr, "sales_rep", current["sales_rep"], sales_rep or None, grund, bediener)
            changed["sales_rep"] = sales_rep or None
        if dispatcher is not None and (dispatcher or None) != current["dispatcher"]:
            self.db.execute(
                text("UPDATE public.kunden_crm360 SET dispatcher_disp = :v, updated_at = now() WHERE kunden_nr = :k"),
                {"v": dispatcher or None, "k": kunden_nr},
            )
            self._log(kunden_nr, "dispatcher", current["dispatcher"], dispatcher or None, grund, bediener)
            changed["dispatcher"] = dispatcher or None
        self.db.commit()
        return {"ok": True, "kunden_nr": kunden_nr, "geaendert": changed, **self.get(kunden_nr)}

    def history(self, kunden_nr: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT feld, alt, neu, grund, bediener, created_at FROM public.crm_ownership_log "
                 "WHERE kunden_nr = :k ORDER BY created_at DESC"),
            {"k": kunden_nr},
        ).mappings().all()
        return [{"feld": r["feld"], "alt": r["alt"], "neu": r["neu"], "grund": r["grund"],
                 "bediener": r["bediener"],
                 "created_at": r["created_at"].isoformat() if r["created_at"] else None} for r in rows]

    def unassigned(self, limit: int = 200) -> dict:
        """Aktive Kunden ohne Außendienst-Zuordnung (Worklist)."""
        rows = self.db.execute(
            text(
                "SELECT k.kunden_nr, k.name1, k.plz, k.ort "
                "FROM public.kunden k "
                "LEFT JOIN public.kunden_crm360 c ON c.kunden_nr = k.kunden_nr "
                "WHERE COALESCE(k.geloescht,false) = false "
                "AND (c.sales_rep_vb IS NULL OR c.sales_rep_vb = '') "
                "ORDER BY k.name1 LIMIT :lim"
            ),
            {"lim": max(1, min(limit, 1000))},
        ).mappings().all()
        total = self.db.execute(
            text("SELECT count(*) FROM public.kunden k LEFT JOIN public.kunden_crm360 c ON c.kunden_nr = k.kunden_nr "
                 "WHERE COALESCE(k.geloescht,false) = false AND (c.sales_rep_vb IS NULL OR c.sales_rep_vb = '')")
        ).scalar()
        return {"items": [dict(r) for r in rows], "total": int(total or 0)}

    def by_owner(self, sales_rep: str) -> dict:
        rows = self.db.execute(
            text(
                "SELECT k.kunden_nr, k.name1, k.plz, k.ort, c.dispatcher_disp "
                "FROM public.kunden_crm360 c JOIN public.kunden k ON k.kunden_nr = c.kunden_nr "
                "WHERE c.sales_rep_vb = :sr AND COALESCE(k.geloescht,false) = false ORDER BY k.name1"
            ),
            {"sr": sales_rep},
        ).mappings().all()
        return {"sales_rep": sales_rep, "items": [dict(r) for r in rows], "total": len(rows)}
