"""Lesemodell des Pruefkorbs (FIN-CONTROL-002): Arbeitsliste und Lagebild fuer den Controller.

Die Befunde schreibt die Kontroll-Engine (``freigabe_engine``). Hier werden sie so aufbereitet, dass der Controller
sie ohne interne Schluessel lesen kann — Art, Vorgang, Beleg, Betrag — und dass ihm das System sagt, worauf er
zuerst sehen sollte (``lagebild``).
"""
from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.belegvertrag import BELEGARTEN

ARTEN: dict[str, str] = {
    "betrag": "Betrag über der Schwelle",
    "stueckelung": "Stückelung",
    "abweichung_ueblich": "Abweichung vom üblichen Betrag",
    "agrar_korrektur": "Abrechnungskorrektur",
    "storno_haeufung": "Gehäufte Stornos",
    "massenimport": "Massenimport",
    "dublette": "Mögliche Dublette",
    "abweichung_vorgaenger": "Abweichung vom Vorgänger",
    "geschuetztes_konto": "Geschütztes Konto",
    "gutschrift_ohne_bezug": "Gutschrift ohne Bezug",
}
VORGAENGE: dict[str, str] = {
    "docflow_document": "Beleg",
    "finance_ap_invoice": "Finanzrechnung",
    "sales_credit_note": "Verkaufsgutschrift",
    "finance_sales_invoice": "Ausgangsrechnung",
    "journal_entry": "Hauptbuchbuchung",
    "payment_run": "Zahlungslauf",
    "journal_import": "Massenimport",
    "einkauf_credit_memo": "Lieferantengutschrift",
    "einkauf_debit_memo": "Lieferantenbelastung",
}
AKTIONEN: dict[str, str] = {"post": "Buchen", "reverse": "Stornieren"}
SCHWEREN: dict[str, str] = {"kritisch": "Kritisch", "warnung": "Warnung"}
STAENDE: dict[str, str] = {"offen": "Offen", "geprueft": "Geprüft"}

_SORTIERUNG = {"erfasst": "f.created_at", "schwere": "f.severity", "betrag": "f.amount", "status": "f.status",
               "art": "f.code", "ausgeloest_von": "f.actor"}
_AB = (
    " FROM domain_docflow.control_findings f "
    "LEFT JOIN domain_docflow.document_headers h ON f.subject_type = 'docflow_document' "
    "AND CAST(h.id AS text) = f.subject_id AND h.tenant_id = f.tenant_id "
    "LEFT JOIN domain_erp.journal_entries j ON f.subject_type = 'journal_entry' "
    "AND CAST(j.id AS text) = f.subject_id AND j.tenant_id = f.tenant_id "
)
WARTEFRIST_TAGE = 7
HAEUFUNG_AB = 3
HAEUFUNG_TAGE = 30


def _schluessel(woerter: dict[str, str], gesucht: Any) -> list[str]:
    """Die internen Schluessel, deren Bezeichnung (oder Schluessel) den Suchtext enthaelt."""
    nadel = str(gesucht or "").casefold()
    return [k for k, v in woerter.items() if nadel in v.casefold() or nadel == k]


def _zeile(z: dict[str, Any]) -> dict[str, Any]:
    belegart = z.get("doc_type")
    variante = BELEGARTEN.get(belegart) if belegart else None
    vorgang = variante.bezeichnung if variante else VORGAENGE.get(z["subject_type"], "Vorgang")
    return {
        "id": str(z["id"]),
        "erfasst": z["created_at"],
        "schwere": z["severity"],
        "schwere_text": SCHWEREN.get(z["severity"], z["severity"]),
        "art": ARTEN.get(z["code"], z["code"]),
        "vorgang": vorgang,
        "aktion": AKTIONEN.get(z["action"], z["action"]),
        "beleg": z.get("doc_number") or z.get("entry_number"),
        "betrag": z["amount"],
        "hinweis": z["text"],
        "ausgeloest_von": z["actor"],
        "freigegeben": z["approval_id"] is not None,
        "status": z["status"],
        "status_text": STAENDE.get(z["status"], z["status"]),
        "geprueft_von": z["reviewed_by"],
        "geprueft_am": z["reviewed_at"],
        "bewertung": z["review_note"],
        "alter_tage": int(z["alter_tage"] or 0),
        # Zum Vorgang springen kann die Maske nur, wo es eine Maske des Vorgangs gibt: beim Beleg.
        "source_route": f"/belege/{belegart}/{z['subject_id']}" if variante else None,
    }


def seite(
    db: Session,
    tenant_id: str,
    *,
    page: int = 1,
    limit: int = 50,
    q: Optional[str] = None,
    sort: Optional[str] = None,
    sort_dir: Optional[str] = None,
    filter_plan: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Eine Seite des Pruefkorbs. Ohne Angabe eines Standes: die offenen Befunde, kritische zuerst."""
    wo, werte = ["f.tenant_id = :t"], {"t": tenant_id}
    plan = {k: (v.get("value") if isinstance(v, dict) else v) for k, v in (filter_plan or {}).items()}
    stand = str(plan.get("status") or "offen").strip().lower()
    if stand in STAENDE:  # „alle" hebt die Vorgabe auf
        wo.append("f.status = :stand")
        werte["stand"] = stand
    if plan.get("schwere"):
        wo.append("f.severity = ANY(:schweren)")
        werte["schweren"] = _schluessel(SCHWEREN, plan["schwere"])
    if plan.get("art"):
        wo.append("f.code = ANY(:arten)")
        werte["arten"] = _schluessel(ARTEN, plan["art"])
    if plan.get("ausgeloest_von"):
        wo.append("f.actor ILIKE :wer")
        werte["wer"] = f"%{plan['ausgeloest_von']}%"
    if q and q.strip():
        wo.append("(f.text ILIKE :q OR f.actor ILIKE :q OR h.doc_number ILIKE :q OR j.entry_number ILIKE :q "
                  "OR f.code = ANY(:q_arten))")
        werte["q"] = f"%{q.strip()}%"
        werte["q_arten"] = _schluessel(ARTEN, q.strip())
    bedingung = " AND ".join(wo)
    spalte = _SORTIERUNG.get(sort or "")
    richtung = "DESC" if (sort_dir or "").lower() == "desc" else "ASC"
    # Vorgabe: kritisch vor Warnung („kritisch" < „warnung"), darin die aeltesten zuerst — sie warten am laengsten.
    ordnung = f"{spalte} {richtung} NULLS LAST, f.id" if spalte else "f.severity ASC, f.created_at ASC, f.id"
    gesamt = db.execute(text(f"SELECT COUNT(*) {_AB} WHERE {bedingung}"), werte).scalar_one()  # nosec B608  # feste Literale; Werte nur gebunden
    page, limit = max(1, page), max(1, min(limit, 200))
    zeilen = db.execute(
        text(
            "SELECT f.id, f.subject_type, f.subject_id, f.action, f.code, f.severity, f.text, f.amount, f.actor, "
            "f.approval_id, f.created_at, f.status, f.reviewed_by, f.reviewed_at, f.review_note, h.doc_number, "
            "h.doc_type, j.entry_number, EXTRACT(DAY FROM clock_timestamp() - f.created_at) AS alter_tage "
            f"{_AB} WHERE {bedingung} ORDER BY {ordnung} LIMIT :lim OFFSET :ab"  # nosec B608  # Spalten aus Allowlist; Werte nur gebunden
        ),
        {**werte, "lim": limit, "ab": (page - 1) * limit},
    ).mappings().all()
    return {"items": [_zeile(dict(z)) for z in zeilen], "total": int(gesamt), "page": page, "page_size": limit}


def lagebild(db: Session, tenant_id: str) -> dict[str, Any]:
    """Was der Controller zuerst wissen sollte: Zahlen, Wartezeiten, Haeufungen — in Saetzen, nicht in Schluesseln."""
    z = db.execute(
        text(
            "SELECT COUNT(*) FILTER (WHERE status = 'offen') AS offen, "
            "COUNT(*) FILTER (WHERE status = 'offen' AND severity = 'kritisch') AS kritisch_offen, "
            "COUNT(*) FILTER (WHERE status = 'offen' AND severity = 'warnung') AS warnung_offen, "
            "COUNT(*) FILTER (WHERE status = 'offen' AND created_at < clock_timestamp() - make_interval(days => :frist)) "
            "AS wartend, "
            "COALESCE(SUM(amount) FILTER (WHERE status = 'offen'), 0) AS betrag_offen, "
            "COUNT(*) FILTER (WHERE status = 'geprueft' AND reviewed_at >= clock_timestamp() - make_interval(days => 30)) "
            "AS geprueft_30_tage FROM domain_docflow.control_findings WHERE tenant_id = :t"
        ),
        {"t": tenant_id, "frist": WARTEFRIST_TAGE},
    ).mappings().one()
    arten = db.execute(
        text(
            "SELECT code, COUNT(*) AS anzahl FROM domain_docflow.control_findings WHERE tenant_id = :t AND status = 'offen' "
            "GROUP BY code ORDER BY anzahl DESC, code"
        ),
        {"t": tenant_id},
    ).all()
    haeufungen = db.execute(
        text(
            "SELECT actor, COUNT(*) AS anzahl FROM domain_docflow.control_findings WHERE tenant_id = :t "
            "AND actor IS NOT NULL AND created_at >= clock_timestamp() - make_interval(days => :tage) "
            "GROUP BY actor HAVING COUNT(*) >= :ab ORDER BY anzahl DESC, actor LIMIT 5"
        ),
        {"t": tenant_id, "tage": HAEUFUNG_TAGE, "ab": HAEUFUNG_AB},
    ).all()

    hinweise: list[str] = []
    if z["kritisch_offen"] == 1:
        hinweise.append("1 kritischer Befund wurde freigegeben und ist noch nicht bewertet.")
    elif z["kritisch_offen"]:
        hinweise.append(f"{z['kritisch_offen']} kritische Befunde wurden freigegeben und sind noch nicht bewertet.")
    if z["wartend"] == 1:
        hinweise.append(f"1 Befund wartet seit mehr als {WARTEFRIST_TAGE} Tagen.")
    elif z["wartend"]:
        hinweise.append(f"{z['wartend']} Befunde warten seit mehr als {WARTEFRIST_TAGE} Tagen.")
    for wer, anzahl in haeufungen:
        hinweise.append(f"{anzahl} Befunde in {HAEUFUNG_TAGE} Tagen bei {wer}.")
    if arten and z["offen"] > 1:
        hinweise.append(f"Häufigste Art: {ARTEN.get(arten[0][0], arten[0][0])} ({arten[0][1]}).")
    return {
        "offen": int(z["offen"]),
        "kritisch_offen": int(z["kritisch_offen"]),
        "warnung_offen": int(z["warnung_offen"]),
        "wartend": int(z["wartend"]),
        "betrag_offen": z["betrag_offen"],
        "geprueft_30_tage": int(z["geprueft_30_tage"]),
        "nach_art": [{"art": ARTEN.get(code, code), "anzahl": int(anzahl)} for code, anzahl in arten],
        "haeufungen": [{"ausgeloest_von": wer, "anzahl": int(anzahl)} for wer, anzahl in haeufungen],
        "hinweise": hinweise,
        "lage": " ".join(hinweise) if hinweise else "Keine offenen Auffälligkeiten.",
    }
