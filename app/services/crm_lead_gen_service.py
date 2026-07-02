"""CRM Lead-Generierung — region-universale Lead-Kandidaten aus offenen Quellen.

Erzeugt Lead-Kandidaten für den Außendienst aus:
- **GAP** (``gap_payments``): EU-Agrarförderempfänger, je Betrieb aggregiert,
  Top-Prozent nach Fördersumme.
- **LKV** (``dairy_herd_performance``): Milchviehbetriebe, Top-Prozent nach
  Milchleistung.

**Region-universal (DACH):** Filterung über einen freien PLZ-Bereich
(``plz_min``–``plz_max``), nicht auf eine Region hartcodiert. Damit für jede
Vertriebsregion (DE/AT/CH, sofern entsprechende Quelldaten geladen sind)
einsetzbar. Reine Lese-/Vorschau-Schicht (keine Mutation).
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# Offensichtliche Nicht-Betriebe (Behörden/Verbände/Kommunen/Flur-/Jagdkörper).
_GAP_NAME_EXCLUDE = (
    "beneficiary_name_raw NOT ILIKE ALL (ARRAY["
    "'%NLWKN%', '%verband%', '%Gemeinde%', '%Samtgemeinde%', '%Landkreis%', "
    "'%Stadt %', '% Stadt%', '%e. V.%', '%e.V.%', '%Deich%', '%Wasser%', '%Amt %', "
    "'%Sielacht%', 'TG %', '%Realverband%', '%Realgemeinde%', '%Jagdgenossensch%', "
    "'%Teichgenoss%', '%Kirchengem%', '%Kloster%', '%Teilnehmergemeinschaft%', "
    "'%Nationalpark%', '%Wegegenoss%', '%Beregnung%', '%verwaltung%'])"
)


def _plz_clause(col: str, plz_min: Optional[str], plz_max: Optional[str], params: dict) -> str:
    if plz_min and plz_max:
        params["plz_min"], params["plz_max"] = plz_min, plz_max
        return f" AND {col} BETWEEN :plz_min AND :plz_max"
    if plz_min:
        params["plz_min"] = plz_min
        return f" AND {col} >= :plz_min"
    if plz_max:
        params["plz_max"] = plz_max
        return f" AND {col} <= :plz_max"
    return ""


def gap_candidates(db: Session, plz_min: Optional[str], plz_max: Optional[str],
                   top_pct: float, max_leads: int) -> list[dict]:
    params: dict = {"pct": top_pct, "lim": max_leads}
    clause = _plz_clause("postal_code", plz_min, plz_max, params)
    try:
        rows = db.execute(
            text(
                f"""
                WITH scoped AS (
                    SELECT beneficiary_name_norm AS name_norm,
                           max(beneficiary_name_raw)            AS name,
                           postal_code                          AS plz,
                           replace(max(city), ', Stadt', '')    AS ort,
                           max(street_raw)                      AS strasse,
                           sum(amount_total)                    AS score
                    FROM gap_payments
                    WHERE beneficiary_name_norm IS NOT NULL AND {_GAP_NAME_EXCLUDE}{clause}
                    GROUP BY beneficiary_name_norm, postal_code
                ), ranked AS (
                    SELECT *, percent_rank() OVER (ORDER BY score DESC) AS pr FROM scoped
                )
                SELECT name, plz, ort, strasse, round(score) AS score
                FROM ranked WHERE pr < :pct ORDER BY score DESC LIMIT :lim
                """
            ),
            params,
        ).mappings().all()
    except Exception:  # noqa: BLE001 — Tabelle fehlt im Dev/Test-System
        db.rollback()
        return []
    return [{**dict(r), "quelle": "gap", "score_label": "Fördersumme €"} for r in rows]


def lkv_candidates(db: Session, plz_min: Optional[str], plz_max: Optional[str],
                   top_pct: float, max_leads: int) -> list[dict]:
    params: dict = {"pct": top_pct, "lim": max_leads}
    clause = _plz_clause("postal_code", plz_min, plz_max, params)
    try:
        rows = db.execute(
            text(
                f"""
                WITH scoped AS (
                    SELECT name_norm, max(besitzer_raw) AS name, postal_code AS plz,
                           max(ort) AS ort, max(milch_kg) AS score
                    FROM dairy_herd_performance
                    WHERE besitzer_raw IS NOT NULL{clause}
                    GROUP BY name_norm, postal_code
                ), ranked AS (
                    SELECT *, percent_rank() OVER (ORDER BY score DESC NULLS LAST) AS pr FROM scoped
                )
                SELECT name, plz, ort, NULL AS strasse, round(score) AS score
                FROM ranked WHERE pr < :pct ORDER BY score DESC NULLS LAST LIMIT :lim
                """
            ),
            params,
        ).mappings().all()
    except Exception:  # noqa: BLE001 — Tabelle fehlt im Dev/Test-System
        db.rollback()
        return []
    return [{**dict(r), "quelle": "lkv", "score_label": "Milch kg/Kuh"} for r in rows]


_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


class CrmLeadGenService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def preview(self, *, quelle: str = "gap", plz_min: Optional[str] = None,
                plz_max: Optional[str] = None, top_pct: float = 0.10,
                max_leads: int = 200) -> dict:
        """Lead-Kandidaten-Vorschau. quelle: 'gap' | 'lkv' | 'beide'."""
        top_pct = max(0.01, min(1.0, top_pct))
        max_leads = max(1, min(2000, max_leads))
        cands: list[dict] = []
        if quelle in ("gap", "beide"):
            cands += gap_candidates(self.db, plz_min, plz_max, top_pct, max_leads)
        if quelle in ("lkv", "beide"):
            cands += lkv_candidates(self.db, plz_min, plz_max, top_pct, max_leads)
        return {
            "quelle": quelle,
            "plz_min": plz_min,
            "plz_max": plz_max,
            "top_pct": top_pct,
            "anzahl": len(cands),
            "kandidaten": cands[:max_leads],
        }

    def list_leads(self, search: Optional[str] = None) -> dict:
        """Übernommene CRM-Leads (public.crm_leads) in der Frontend-Lead-Shape."""
        params: dict = {"t": self.tenant_id}
        clause = ""
        if search and search.strip():
            clause = " AND company ILIKE :q"
            params["q"] = f"%{search.strip()}%"
        try:
            rows = self.db.execute(
                text(
                    "SELECT id, company, contact_person, email, phone, source, potential, "
                    "lower(priority::text) AS priority, lower(status::text) AS status "
                    "FROM public.crm_leads WHERE tenant_id = :t" + clause +
                    " ORDER BY potential DESC NULLS LAST LIMIT 1000"
                ),
                params,
            ).mappings().all()
        except Exception:  # noqa: BLE001
            self.db.rollback()
            return {"data": [], "total": 0}
        _status = {"new": "new", "qualified": "qualified", "converted": "qualified", "lost": "lost"}
        data = [
            {
                "id": r["id"], "company": r["company"] or "",
                "contact_person": r["contact_person"] or "",
                "email": r["email"] or "", "phone": r["phone"] or "",
                "source": r["source"] or "", "potential": float(r["potential"] or 0),
                "priority": r["priority"] or "medium",
                "status": _status.get(r["status"] or "new", "new"),
            }
            for r in rows
        ]
        return {"data": data, "total": len(data)}

    def get_lead(self, lead_id: str) -> Optional[dict]:
        """Einzelnen übernommenen CRM-Lead (public.crm_leads) in Frontend-Lead-Shape."""
        try:
            r = self.db.execute(
                text(
                    "SELECT id, company, contact_person, email, phone, source, potential, "
                    "lower(priority::text) AS priority, lower(status::text) AS status, "
                    "notes, address, expected_close_date, assigned_to "
                    "FROM public.crm_leads WHERE id = :id AND tenant_id = :t"
                ),
                {"id": lead_id, "t": self.tenant_id},
            ).mappings().first()
        except Exception:  # noqa: BLE001 — tolerant: fehlende Spalten/Tabelle
            self.db.rollback()
            r = self.db.execute(
                text(
                    "SELECT id, company, contact_person, email, phone, source, potential, "
                    "lower(priority::text) AS priority, lower(status::text) AS status "
                    "FROM public.crm_leads WHERE id = :id AND tenant_id = :t"
                ),
                {"id": lead_id, "t": self.tenant_id},
            ).mappings().first()
        if not r:
            return None
        _status = {"new": "new", "qualified": "qualified", "converted": "qualified", "lost": "lost"}
        d = dict(r)
        return {
            "id": d["id"], "company": d.get("company") or "",
            "contactPerson": d.get("contact_person") or "",
            "email": d.get("email") or "", "phone": d.get("phone") or "",
            "source": d.get("source") or "", "potential": float(d.get("potential") or 0),
            "priority": d.get("priority") or "medium",
            "status": _status.get(d.get("status") or "new", "new"),
            "notes": d.get("notes") or "", "address": d.get("address") or "",
            "expectedCloseDate": str(d["expected_close_date"]) if d.get("expected_close_date") else "",
            "assignedTo": d.get("assigned_to") or "",
        }

    def convert_lead(self, lead_id: str) -> dict:
        """Konvertiert einen Lead in einen Kunden (public.kunden) und setzt den
        Lead auf CONVERTED. Idempotent: erneutes Konvertieren liefert dieselbe
        kunden_nr und legt keinen Doppel-Kunden an."""
        from app.core.exceptions import EntityNotFoundError

        row = self.db.execute(
            text("SELECT id, company, notes FROM public.crm_leads WHERE id = :id AND tenant_id = :t"),
            {"id": lead_id, "t": self.tenant_id},
        ).mappings().first()
        if not row:
            raise EntityNotFoundError("Lead", lead_id)

        # Geo aus den Notizen rekonstruieren (Format "PLZ ORT — Label: Score").
        plz = ort = None
        geo = (row["notes"] or "").split(" — ")[0].strip()
        if geo:
            parts = geo.split(" ", 1)
            if parts[0].isdigit():
                plz = parts[0]
                ort = parts[1].strip() if len(parts) > 1 else None
        kn = ("L" + lead_id.replace("-", ""))[:20].upper()

        self.db.execute(
            text(
                "INSERT INTO public.kunden (kunden_nr, name1, plz, ort, land, geloescht, erstellt_am) "
                "VALUES (:kn, :name, :plz, :ort, 'DE', FALSE, now()) "
                "ON CONFLICT (kunden_nr) DO NOTHING"
            ),
            {"kn": kn, "name": (row["company"] or kn)[:200], "plz": plz, "ort": ort},
        )
        self.db.execute(
            text(
                "UPDATE public.crm_leads SET status = 'CONVERTED', updated_at = now(), "
                "notes = coalesce(notes, '') || :tag "
                "WHERE id = :id AND tenant_id = :t AND status <> 'CONVERTED'"
            ),
            {"tag": f" [→ Kunde {kn}]", "id": lead_id, "t": self.tenant_id},
        )
        self.db.commit()
        return {"lead_id": lead_id, "kunden_nr": kn, "status": "CONVERTED"}

    def leads_count(self) -> int:
        try:
            return int(self.db.execute(
                text("SELECT count(*) FROM public.crm_leads WHERE tenant_id = :t"),
                {"t": self.tenant_id},
            ).scalar() or 0)
        except Exception:  # noqa: BLE001 — Tabelle evtl. nicht vorhanden
            self.db.rollback()
            return 0

    def create_leads(self, kandidaten: list[dict]) -> dict:
        """Übernimmt Kandidaten als CRM-Leads (public.crm_leads). Idempotent je
        Firma+Mandant (Mehrfach-Übernahme erzeugt keine Dubletten)."""
        import uuid

        check = text(
            "SELECT 1 FROM public.crm_leads WHERE company = :company AND tenant_id = :tid LIMIT 1"
        )
        ins = text(
            "INSERT INTO public.crm_leads "
            "(id, company, source, potential, priority, status, notes, tenant_id) "
            "VALUES (:id, :company, :source, :potential, 'MEDIUM', 'NEW', :notes, :tid)"
        )
        created = skipped = 0
        try:
            for c in kandidaten:
                name = (c.get("name") or "").strip()
                if not name:
                    skipped += 1
                    continue
                exists = self.db.execute(check, {"company": name, "tid": self.tenant_id}).first()
                if exists:
                    skipped += 1
                    continue
                notes = f"{c.get('plz') or ''} {c.get('ort') or ''} — {c.get('score_label') or ''}: {c.get('score') or ''}".strip()
                self.db.execute(ins, {
                    "id": str(uuid.uuid4()), "company": name, "source": c.get("quelle"),
                    "potential": c.get("score"), "notes": notes, "tid": self.tenant_id,
                })
                created += 1
            self.db.commit()
        except Exception:  # noqa: BLE001
            self.db.rollback()
            raise
        return {"uebernommen": created, "uebersprungen": skipped, "leads_gesamt": self.leads_count()}
