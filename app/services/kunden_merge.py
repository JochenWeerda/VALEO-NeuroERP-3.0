"""Kunden/Business-Partner-Merge — Dry-Run / Reconciliation (Phase 2A).

Risikoarmes Werkzeug zur Identitäts-Konsolidierung: analysiert und matcht die
bestehenden Silos (``public.kunden``, ``domain_crm.business_partners`` und die
CRM-Kundentabellen) **ohne** produktive Änderung und erzeugt einen
Reconciliation-Report + Backfill-Vorschläge für ``public.kunden.business_partner_id``.

Grundsätze:
- **Dry-Run ist Standard.** Schreiben nur mit ``--apply`` und nur für sichere
  Klassen (``exact_match``/``strong_match``); ``probable_match``/``conflict``
  bleiben manuell.
- **``kunden_nr`` ist fachlicher Schlüssel** und wird NIE überschrieben.
  Technische Identität ist ``business_partner_id`` (UUID).
- Vorhandene ``business_partner_id`` wird nicht überschrieben.

Die Matching-Logik ist als **reine Funktionen** über Dicts gebaut (DB-frei,
unit-testbar); der DB-Layer lädt nur Records und schreibt im Apply-Pfad.

CLI:
    python -m app.services.kunden_merge                 # Dry-Run, Markdown nach stdout
    python -m app.services.kunden_merge --format json --output recon.json
    python -m app.services.kunden_merge --apply         # backfillt nur exact/strong
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

# ── Klassifizierung ───────────────────────────────────────────────────────────

EXACT = "exact_match"
STRONG = "strong_match"
PROBABLE = "probable_match"
CONFLICT = "conflict"
DUPLICATE = "duplicate_candidate"
ORPHAN_KUNDE = "orphan_public_kunden"
ORPHAN_CRM = "orphan_crm_customer"
ORPHAN_BP = "orphan_business_partner"

# Match-Regeln in Prioritätsreihenfolge: (regel, klasse, confidence)
# Schlüssel werden je Record über _candidate_keys() berechnet.
RULE_PRIORITY = [
    ("business_partner_id", EXACT, 1.0),
    ("vat_tax", STRONG, 0.95),
    ("eu_farm_id", STRONG, 0.95),
    ("betriebsnummer", STRONG, 0.92),
    ("webshop_number", STRONG, 0.90),
    ("partner_kunden_number", STRONG, 0.85),
    ("name_plz", PROBABLE, 0.60),
    ("name_ort_strasse", PROBABLE, 0.50),
]


# ── Normalisierung (rein) ─────────────────────────────────────────────────────


def norm_id(value: Any) -> Optional[str]:
    """Normalisiert eine Geschäfts-ID (USt/Steuer/Betriebs-/Webshop-Nummer)."""
    if value is None:
        return None
    s = re.sub(r"[^a-z0-9]", "", str(value).lower())
    return s or None


def _tokenset(name: Any) -> str:
    """Reihenfolge-unabhängiger Namensschlüssel (lokal, DB-frei)."""
    if not name:
        return ""
    s = str(name).lower()
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    legal = {"gbr", "gmbh", "mbh", "kg", "ohg", "ag", "ug", "ek", "eg", "co", "cokg", "ev", "se", "und", "u"}
    toks = [t for t in s.split() if t and t not in legal]
    return " ".join(sorted(toks))


def _plz(value: Any) -> str:
    return str(value).strip() if value else ""


# ── Kandidatenschlüssel je Record (rein) ──────────────────────────────────────


def bp_keys(bp: dict) -> dict[str, set]:
    """Match-Schlüssel eines Business-Partner-Records."""
    name_plz = (_tokenset(bp.get("name_1")), _plz(bp.get("postal_code")))
    keys: dict[str, set] = {
        "business_partner_id": {str(bp.get("partner_id"))} if bp.get("partner_id") else set(),
        "vat_tax": {k for k in (norm_id(bp.get("vat_id")), norm_id(bp.get("tax_number"))) if k},
        "eu_farm_id": {norm_id(bp.get("eu_farm_id"))} if norm_id(bp.get("eu_farm_id")) else set(),
        "betriebsnummer": {k for k in (norm_id(bp.get("farm_number")), norm_id(bp.get("operation_number"))) if k},
        "webshop_number": {norm_id(bp.get("webshop_customer_number"))} if norm_id(bp.get("webshop_customer_number")) else set(),
        "partner_kunden_number": {norm_id(bp.get("partner_number"))} if norm_id(bp.get("partner_number")) else set(),
        "name_plz": {name_plz} if name_plz[0] and name_plz[1] else set(),
        "name_ort_strasse": {(_tokenset(bp.get("name_1")), _tokenset(bp.get("city")), _tokenset(bp.get("street")))}
        if bp.get("name_1") and bp.get("street") else set(),
    }
    return keys


def kunde_keys(k: dict) -> dict[str, set]:
    """Match-Schlüssel eines public.kunden-Records (USt fehlt im Stamm)."""
    name_plz = (_tokenset(k.get("name1")), _plz(k.get("plz")))
    return {
        "business_partner_id": {str(k.get("business_partner_id"))} if k.get("business_partner_id") else set(),
        "vat_tax": set(),  # public.kunden hat keine USt-Spalte
        "eu_farm_id": set(),
        "betriebsnummer": {norm_id(k.get("landwirtschaftsamt_betriebsnummer"))} if norm_id(k.get("landwirtschaftsamt_betriebsnummer")) else set(),
        "webshop_number": {norm_id(k.get("webshop_kunden_nr"))} if norm_id(k.get("webshop_kunden_nr")) else set(),
        "partner_kunden_number": {x for x in (norm_id(k.get("legacy_kunden_nr")), norm_id(k.get("kunden_nr"))) if x},
        "name_plz": {name_plz} if name_plz[0] and name_plz[1] else set(),
        "name_ort_strasse": {(_tokenset(k.get("name1")), _tokenset(k.get("ort")), _tokenset(k.get("strasse")))}
        if k.get("name1") and k.get("strasse") else set(),
    }


def crm_keys(rec: dict) -> dict[str, set]:
    """Match-Schlüssel eines CRM-Silo-Records (USt/Steuer vorhanden)."""
    name_plz = (_tokenset(rec.get("name")), _plz(rec.get("plz")))
    return {
        "business_partner_id": {rec["business_partner_id"]} if rec.get("business_partner_id") else set(),
        "vat_tax": {norm_id(rec.get("tax"))} if norm_id(rec.get("tax")) else set(),
        "eu_farm_id": set(),
        "betriebsnummer": set(),
        "webshop_number": set(),
        "partner_kunden_number": {norm_id(rec.get("customer_number"))} if norm_id(rec.get("customer_number")) else set(),
        "name_plz": {name_plz} if name_plz[0] and name_plz[1] else set(),
        "name_ort_strasse": set(),
    }


# ── Reine Matching-/Klassifizierungslogik ─────────────────────────────────────


@dataclass
class MergeCandidate:
    source: str
    source_key: str           # kunden_nr
    name: str
    plz: str
    existing_business_partner_id: Optional[str]
    proposed_business_partner_id: Optional[str]
    match_reason: Optional[str]
    match_class: str
    confidence_score: float
    conflict_fields: list[str] = field(default_factory=list)
    recommended_action: str = "manual_review"


def build_bp_index(bps: list[dict]) -> dict[str, dict[Any, list[dict]]]:
    """Baut je Regel einen Wert→[BP]-Index (rein)."""
    index: dict[str, dict[Any, list[dict]]] = {rule: {} for rule, _, _ in RULE_PRIORITY}
    for bp in bps:
        keys = bp_keys(bp)
        for rule in index:
            for val in keys.get(rule, set()):
                index[rule].setdefault(val, []).append(bp)
    return index


def _recommend(match_class: str, already_linked: bool) -> str:
    if already_linked:
        return "linked"
    if match_class in (EXACT, STRONG):
        return "backfill_business_partner_id"
    if match_class == ORPHAN_KUNDE:
        return "create_business_partner"
    return "manual_review"


def _match_against_bp(keys: dict[str, set], bp_index: dict, name: Any, plz: str) -> tuple:
    """Geteilte Regel-Iteration. Returns (rule, match_class, confidence, bp_id, conflict_fields);
    ``rule is None`` → kein Treffer."""
    for rule, match_class, conf in RULE_PRIORITY:
        hits: list[dict] = []
        seen: set = set()
        for val in keys.get(rule, set()):
            for bp in bp_index.get(rule, {}).get(val, []):
                pid = str(bp.get("partner_id"))
                if pid not in seen:
                    seen.add(pid)
                    hits.append(bp)
        if not hits:
            continue
        if len(hits) > 1:
            return rule, CONFLICT, 0.3, None, [rule, "multiple_bp"]
        bp = hits[0]
        pid = str(bp.get("partner_id"))
        conflict_fields: list[str] = []
        if rule not in ("business_partner_id", "name_plz", "name_ort_strasse"):
            tn, bn = _tokenset(name), _tokenset(bp.get("name_1"))
            if tn and bn and tn != bn and plz and _plz(bp.get("postal_code")) and plz != _plz(bp.get("postal_code")):
                conflict_fields.append("name")
        cls = CONFLICT if conflict_fields else match_class
        return rule, cls, (0.3 if conflict_fields else conf), pid, conflict_fields
    return None, None, 0.0, None, []


def classify_kunde(kunde: dict, bp_index: dict[str, dict[Any, list[dict]]]) -> MergeCandidate:
    """Klassifiziert einen public.kunden-Record gegen den BP-Index (rein)."""
    existing = str(kunde["business_partner_id"]) if kunde.get("business_partner_id") else None
    name, plz = kunde.get("name1"), _plz(kunde.get("plz"))
    base = dict(source="public.kunden", source_key=str(kunde.get("kunden_nr")), name=str(name or ""), plz=plz, existing_business_partner_id=existing)
    rule, cls, conf, pid, cf = _match_against_bp(kunde_keys(kunde), bp_index, name, plz)
    if rule is None:
        return MergeCandidate(**base, proposed_business_partner_id=None, match_reason=None, match_class=ORPHAN_KUNDE, confidence_score=0.0, recommended_action="create_business_partner")
    already = existing is not None and existing == pid
    return MergeCandidate(**base, proposed_business_partner_id=pid, match_reason=rule, match_class=cls, confidence_score=conf, conflict_fields=cf, recommended_action=_recommend(cls, already))


def classify_crm(rec: dict, bp_index: dict[str, dict[Any, list[dict]]]) -> MergeCandidate:
    """Klassifiziert einen CRM-Silo-Record gegen den BP-Index (rein).

    CRM-Records werden zu Projektionen (FK business_partner_id), nicht in den Stamm
    gemergt → keine Backfill-Aktion, sondern ``project_to_business_partner`` / Review.
    """
    existing = rec.get("business_partner_id")
    name, plz = rec.get("name") or "", _plz(rec.get("plz"))
    base = dict(source=rec["source"], source_key=str(rec.get("crm_id")), name=str(name), plz=plz, existing_business_partner_id=existing)
    rule, cls, conf, pid, cf = _match_against_bp(crm_keys(rec), bp_index, name, plz)
    if rule is None:
        return MergeCandidate(**base, proposed_business_partner_id=None, match_reason=None, match_class=ORPHAN_CRM, confidence_score=0.0, recommended_action="review_create_bp")
    already = existing is not None and existing == pid
    action = "linked" if already else ("manual_review" if cls == CONFLICT else "project_to_business_partner")
    return MergeCandidate(**base, proposed_business_partner_id=pid, match_reason=rule, match_class=cls, confidence_score=conf, conflict_fields=cf, recommended_action=action)


def reconcile_records(kunden: list[dict], bps: list[dict], crm: Optional[list[dict]] = None) -> dict:
    """Reine Reconciliation über geladene Records. Returns Report-Dict."""
    bp_index = build_bp_index(bps)
    candidates = [classify_kunde(k, bp_index) for k in kunden]

    # Dubletten: mehrere kunden schlagen denselben BP vor (exact/strong)
    by_bp: dict[str, list[MergeCandidate]] = {}
    for c in candidates:
        if c.proposed_business_partner_id and c.match_class in (EXACT, STRONG):
            by_bp.setdefault(c.proposed_business_partner_id, []).append(c)
    for pid, group in by_bp.items():
        if len(group) > 1:
            for c in group:
                c.match_class = DUPLICATE
                c.recommended_action = "manual_review"
                if "shared_bp" not in c.conflict_fields:
                    c.conflict_fields.append("shared_bp")

    # Kunden-seitige Dubletten: derselbe reale Kunde (Name+PLZ) mehrfach in public.kunden
    by_name_plz: dict[tuple, list[MergeCandidate]] = {}
    for c in candidates:
        by_name_plz.setdefault((_tokenset(c.name), c.plz), []).append(c)
    for (tname, tplz), group in by_name_plz.items():
        if tname and tplz and len(group) > 1:
            for c in group:
                c.match_class = DUPLICATE
                c.recommended_action = "manual_review"
                if "same_name_plz" not in c.conflict_fields:
                    c.conflict_fields.append("same_name_plz")

    # CRM-Silos klassifizieren (Projektionskandidaten, kein Backfill in den Stamm)
    crm_candidates = [classify_crm(r, bp_index) for r in (crm or [])]

    # Orphan-BP: BP, auf den weder kunde noch CRM zeigt (proposed oder bereits verlinkt)
    referenced = {
        ref
        for c in candidates + crm_candidates
        for ref in (c.proposed_business_partner_id, c.existing_business_partner_id)
        if ref
    }
    orphan_bps = [str(bp.get("partner_id")) for bp in bps if str(bp.get("partner_id")) not in referenced]

    counts: dict[str, int] = {}
    for c in candidates + crm_candidates:
        counts[c.match_class] = counts.get(c.match_class, 0) + 1
    counts[ORPHAN_BP] = len(orphan_bps)

    return {
        "summary": {
            "total_kunden": len(kunden),
            "total_business_partners": len(bps),
            "total_crm_silo": len(crm or []),
            "counts": counts,
            "backfillable": sum(1 for c in candidates if c.recommended_action == "backfill_business_partner_id"),
            "crm_projectable": sum(1 for c in crm_candidates if c.recommended_action == "project_to_business_partner"),
        },
        "candidates": [asdict(c) for c in candidates],
        "crm_candidates": [asdict(c) for c in crm_candidates],
        "orphan_business_partner_ids": orphan_bps,
    }


# ── DB-Layer ──────────────────────────────────────────────────────────────────


def _plz_clause(plz_prefixes: Optional[list[str]], params: dict, col: str = "plz") -> str:
    """Baut eine optionale ``AND (col LIKE :p0 OR ...)``-Bedingung für PLZ-Präfixe.

    Ermöglicht das Scopen eines Laufs auf Regionen/Landkreise (z. B. Aurich/Emden/
    Leer ≈ PLZ 265/266/267/268). Leere/None-Liste → kein Filter (ganzer Stamm).
    """
    if not plz_prefixes:
        return ""
    terms = []
    for i, p in enumerate(plz_prefixes):
        key = f"plzpfx{i}"
        params[key] = f"{p.strip()}%"
        terms.append(f"{col} LIKE :{key}")
    return " AND (" + " OR ".join(terms) + ")"


def load_kunden(db, plz_prefixes: Optional[list[str]] = None) -> list[dict]:
    from sqlalchemy import text

    params: dict = {}
    clause = _plz_clause(plz_prefixes, params)
    rows = db.execute(
        text(
            """
            SELECT kunden_nr, name1, plz, ort, strasse,
                   landwirtschaftsamt_betriebsnummer, webshop_kunden_nr,
                   business_partner_id, legacy_kunden_nr
            FROM public.kunden
            WHERE COALESCE(geloescht, FALSE) = FALSE
            """
            + clause
        ),
        params,
    ).mappings().all()
    return [dict(r) for r in rows]


def load_business_partners(db) -> list[dict]:
    from sqlalchemy import text

    rows = db.execute(
        text(
            """
            SELECT partner_id, partner_number, name_1, postal_code, city, street,
                   tax_number, vat_id, eu_farm_id, farm_number, operation_number,
                   webshop_customer_number
            FROM domain_crm.business_partners
            """
        )
    ).mappings().all()
    return [dict(r) for r in rows]


def load_crm_silos(db) -> list[dict]:
    """CRM-Silo-Records in normalisierter Shape (für Klassifizierung als Projektionen).

    Shape: ``{source, crm_id, name, plz, tax, business_partner_id, customer_number}``.
    """
    from sqlalchemy import text

    # (SQL, source, Spaltenabbildung name/plz/tax/bp_id/cust_no)
    sources = [
        ("SELECT id, customer_number, company_name, postal_code, tax_id, business_partner_id FROM domain_crm.customers",
         "domain_crm.customers", ("company_name", "postal_code", "tax_id", "business_partner_id", "customer_number")),
        ("SELECT id, customer_number, company_name, postal_code, tax_number FROM domain_crm.crm_customers",
         "domain_crm.crm_customers", ("company_name", "postal_code", "tax_number", None, "customer_number")),
        ("SELECT id, display_name FROM public.crm_core_customers",
         "public.crm_core_customers", ("display_name", None, None, None, None)),
    ]
    out: list[dict] = []
    for sql, src, (name_c, plz_c, tax_c, bp_c, num_c) in sources:
        try:
            rows = db.execute(text(sql)).mappings().all()
        except Exception:  # noqa: BLE001 — Silo evtl. nicht vorhanden
            db.rollback()
            continue
        for r in rows:
            out.append({
                "source": src,
                "crm_id": str(r.get("id")),
                "name": r.get(name_c) if name_c else None,
                "plz": r.get(plz_c) if plz_c else None,
                "tax": r.get(tax_c) if tax_c else None,
                "business_partner_id": str(r.get(bp_c)) if (bp_c and r.get(bp_c)) else None,
                "customer_number": r.get(num_c) if num_c else None,
            })
    return out


def reconcile(db, plz_prefixes: Optional[list[str]] = None) -> dict:
    """Lädt Records und führt die Reconciliation aus (Dry-Run, keine Mutation).

    ``plz_prefixes`` scopt die public.kunden-Seite auf Regionen/Landkreise; die
    Business-Partner-Seite bleibt vollständig (gegen alle BP gematcht).
    """
    return reconcile_records(load_kunden(db, plz_prefixes), load_business_partners(db), load_crm_silos(db))


def apply_backfill(db, report: dict) -> dict:
    """Schreibt ``business_partner_id`` NUR für sichere Fälle (exact/strong, action=backfill).

    Überschreibt niemals ``kunden_nr`` oder eine bereits gesetzte ``business_partner_id``.
    """
    from sqlalchemy import text

    written = 0
    skipped = 0
    for c in report["candidates"]:
        if c["recommended_action"] != "backfill_business_partner_id":
            continue
        if c["existing_business_partner_id"] or not c["proposed_business_partner_id"]:
            skipped += 1
            continue
        res = db.execute(
            text(
                """
                UPDATE public.kunden
                SET business_partner_id = CAST(:bp AS uuid)
                WHERE kunden_nr = :kn AND business_partner_id IS NULL
                """
            ),
            {"bp": c["proposed_business_partner_id"], "kn": c["source_key"]},
        )
        written += res.rowcount or 0
    db.commit()
    return {"written": written, "skipped": skipped}


def bridge_status(db, plz_prefixes: Optional[list[str]] = None) -> dict:
    """Readiness-Report für die Identitätsbrücke business_partner_id ↔ kunden_nr.

    Misst die Abdeckung von ``public.kunden.business_partner_id``, wie viele der
    noch unverbrückten Kunden per Matching auflösbar wären, und ob die spätere
    FK-Aktivierung (``public.kunden.business_partner_id`` →
    ``business_partners.partner_id``) frei von Orphans ist. Reine Lese-Operation.
    ``plz_prefixes`` scopt die Kennzahlen auf Regionen/Landkreise.
    """
    from sqlalchemy import text

    p_total: dict = {}
    c_total = _plz_clause(plz_prefixes, p_total)
    total = db.execute(
        text("SELECT count(*) FROM public.kunden WHERE coalesce(geloescht, FALSE) = FALSE" + c_total),
        p_total,
    ).scalar() or 0
    p_linked: dict = {}
    c_linked = _plz_clause(plz_prefixes, p_linked)
    linked = db.execute(
        text(
            "SELECT count(*) FROM public.kunden "
            "WHERE coalesce(geloescht, FALSE) = FALSE AND business_partner_id IS NOT NULL"
            + c_linked
        ),
        p_linked,
    ).scalar() or 0
    try:
        p_fk: dict = {}
        c_fk = _plz_clause(plz_prefixes, p_fk, col="k.plz")
        fk_orphans = db.execute(
            text(
                "SELECT count(*) FROM public.kunden k "
                "WHERE k.business_partner_id IS NOT NULL "
                "AND NOT EXISTS (SELECT 1 FROM domain_crm.business_partners b "
                "                WHERE b.partner_id = k.business_partner_id)"
                + c_fk
            ),
            p_fk,
        ).scalar() or 0
    except Exception:  # noqa: BLE001 — BP-Tabelle evtl. nicht vorhanden (Teilumgebung)
        db.rollback()
        fk_orphans = None

    report = reconcile(db, plz_prefixes)
    resolvable = sum(
        1
        for c in report["candidates"]
        if c["recommended_action"] == "backfill_business_partner_id"
        and not c["existing_business_partner_id"]
        and c["proposed_business_partner_id"]
    )
    unresolved = max(total - linked - resolvable, 0)
    return {
        "total_active": total,
        "linked": linked,
        "coverage_pct": round(linked / total * 100, 1) if total else 0.0,
        "resolvable_by_match": resolvable,
        "unresolved": unresolved,
        "fk_orphans": fk_orphans,
        "fk_ready": fk_orphans == 0 and linked == total and total > 0,
    }


def render_bridge_status(status: dict) -> str:
    # ASCII-sicher (Windows-cp1252-Konsole): keine Sonderzeichen in der Ausgabe.
    lines = [
        "# Identitaetsbruecke business_partner_id <-> kunden_nr - Readiness",
        "",
        f"- Aktive Kunden:              {status['total_active']:>6}",
        f"- Verbrueckt (bp_id gesetzt): {status['linked']:>6}  ({status['coverage_pct']}%)",
        f"- Per Match aufloesbar:       {status['resolvable_by_match']:>6}  (kunden_merge --apply)",
        f"- Unaufloesbar (Orphan):      {status['unresolved']:>6}",
        f"- FK-Orphans (bp_id ohne BP): {status['fk_orphans']}",
        f"- FK-aktivierbar:             {status['fk_ready']}",
    ]
    return "\n".join(lines)


# ── Report-Rendering ──────────────────────────────────────────────────────────


def render_markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# Kunden ↔ Business-Partner Reconciliation (Dry-Run)",
        "",
        f"- public.kunden: **{s['total_kunden']}**  ·  business_partners: **{s['total_business_partners']}**  ·  CRM-Silo-Records: **{s['total_crm_silo']}**",
        f"- Sicher backfillbar (exact/strong): **{s['backfillable']}**",
        "",
        "## Klassen",
        "| Klasse | Anzahl |",
        "|---|---|",
    ]
    for cls, n in sorted(s["counts"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {cls} | {n} |")
    lines += ["", "## Backfill-Vorschläge", "| kunden_nr | Name | PLZ | → business_partner_id | Regel | Klasse | Conf | Aktion | Konflikte |", "|---|---|---|---|---|---|---|---|---|"]
    for c in report["candidates"]:
        if c["match_class"] == ORPHAN_KUNDE:
            continue
        lines.append(
            f"| {c['source_key']} | {c['name'][:24]} | {c['plz']} | {c['proposed_business_partner_id'] or '—'} | "
            f"{c['match_reason'] or '—'} | {c['match_class']} | {c['confidence_score']:.2f} | {c['recommended_action']} | {','.join(c['conflict_fields']) or '—'} |"
        )
    orphans = [c for c in report["candidates"] if c["match_class"] == ORPHAN_KUNDE]
    if orphans:
        lines += ["", f"## Orphans public.kunden ({len(orphans)}) — kein BP, Vorschlag: BP anlegen", "| kunden_nr | Name | PLZ |", "|---|---|---|"]
        for c in orphans:
            lines.append(f"| {c['source_key']} | {c['name'][:30]} | {c['plz']} |")
    crm = report.get("crm_candidates", [])
    if crm:
        lines += [
            "", f"## CRM-Silo-Klassifizierung ({len(crm)}) — werden Projektionen, nicht in den Stamm",
            f"Projektierbar (eindeutig auf BP): **{report['summary'].get('crm_projectable', 0)}**", "",
            "| Quelle | id | Name | → business_partner_id | Regel | Klasse | Aktion | Konflikte |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for c in crm:
            lines.append(
                f"| {c['source']} | {c['source_key'][:10]} | {c['name'][:22]} | {c['proposed_business_partner_id'] or '—'} | "
                f"{c['match_reason'] or '—'} | {c['match_class']} | {c['recommended_action']} | {','.join(c['conflict_fields']) or '—'} |"
            )
    if report["orphan_business_partner_ids"]:
        lines += ["", f"## Orphan Business Partner ({len(report['orphan_business_partner_ids'])}) — kein passender Kunde/CRM"]
    return "\n".join(lines)


def render_json(report: dict) -> str:
    import json

    return json.dumps(report, indent=2, ensure_ascii=False, default=str)


def render_csv(report: dict) -> str:
    import csv
    import io

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["source", "source_key", "name", "plz", "existing_bp_id", "proposed_bp_id", "match_reason", "match_class", "confidence", "recommended_action", "conflict_fields"])
    for c in report["candidates"] + report.get("crm_candidates", []):
        w.writerow([c["source"], c["source_key"], c["name"], c["plz"], c["existing_business_partner_id"] or "", c["proposed_business_partner_id"] or "",
                    c["match_reason"] or "", c["match_class"], f"{c['confidence_score']:.2f}", c["recommended_action"], "|".join(c["conflict_fields"])])
    return buf.getvalue()


def _resolve_report_output_path(output: str) -> Path:
    """Restrict CLI report writes to the current workspace tree."""
    path = Path(output).expanduser().resolve()
    cwd = Path.cwd().resolve()
    if path != cwd and cwd not in path.parents:
        raise SystemExit(f"Output path must be inside the current working directory: {output}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":
    import argparse

    from app.core.database import SessionLocal

    parser = argparse.ArgumentParser(description="Kunden↔BusinessPartner Reconciliation (Dry-Run Standard).")
    parser.add_argument("--apply", action="store_true", help="Sichere Fälle (exact/strong) backfillen — sonst nur Report")
    parser.add_argument("--format", choices=["md", "json", "csv"], default="md")
    parser.add_argument("--output", type=str, default=None, help="Datei statt stdout")
    parser.add_argument("--bridge-status", action="store_true", help="Nur Readiness der Identitätsbrücke ausgeben")
    parser.add_argument(
        "--plz-prefix",
        type=str,
        default=None,
        help="Lauf auf PLZ-Präfixe scopen (kommagetrennt), z. B. Aurich/Emden/Leer: 265,266,267,268",
    )
    args = parser.parse_args()

    plz_prefixes = [p for p in (args.plz_prefix or "").split(",") if p.strip()] or None

    db = SessionLocal()
    try:
        if plz_prefixes:
            print(f"[SCOPE] PLZ-Präfixe: {', '.join(plz_prefixes)}")
        if args.bridge_status:
            print(render_bridge_status(bridge_status(db, plz_prefixes)))
            raise SystemExit(0)
        report = reconcile(db, plz_prefixes)
        rendered = {"md": render_markdown, "json": render_json, "csv": render_csv}[args.format](report)
        if args.output:
            output_path = _resolve_report_output_path(args.output)
            args.output = str(output_path)
            with output_path.open("w", encoding="utf-8") as fh:
                fh.write(rendered)
            print(f"Report → {args.output}")
        else:
            print(rendered)
        if args.apply:
            result = apply_backfill(db, report)
            print(f"\n[APPLY] business_partner_id geschrieben: {result['written']}, übersprungen: {result['skipped']}")
    finally:
        db.close()

