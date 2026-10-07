"""Interessenten — und zwar die, die es gibt.

Drei Tabellen fuehrten denselben Begriff, und der benutzte war der leere:

* `public.crm_leads` — 97 Zeilen in der Entwicklungsdatenbank, gespeist aus der
  Durchdringungs-Akquise (`source`: `lkv`, `gap`); gelesen von
  `crm_lead_gen_service`, `crm_partner_suche`, `crm_reports`. **Das Register.**
* `domain_crm.leads` — haengt an einem `customer_id`: eine Verkaufschance an
  einem bestehenden Kunden, kein Interessent. Bleibt bestehen.
* `domain_crm.interessenten` — existiert in keiner Datenbank; `customers.py`
  schrieb sie. Wird **nicht angelegt**: Ein vierter Begriff fuer dieselbe Sache
  waere das Gegenteil einer Ordnung.

Siehe ``docs/quality-assurance/interessent-ist-lead-20261006.md``.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

#: Das Register der Interessenten. Liegt im `public`-Schema — das widerspricht der
#: Mehrschema-Ordnung, aber dort stehen die Daten. Der Umzug nach `domain_crm` ist
#: ein eigener Slice **mit Daten**.
LEADS = "public.crm_leads"

#: Die Verkaufschance an einem bestehenden Kunden. Nicht dasselbe wie ein Lead.
CHANCEN = "domain_crm.leads"

#: Die Staende des Bestands. Englisch, weil 97 Zeilen darauf stehen.
STAENDE = ("NEW", "CONTACTED", "QUALIFIED", "CONVERTED", "LOST")

#: Der Stand eines neuen Interessenten und der nach der Konvertierung.
NEU = "NEW"
KONVERTIERT = "CONVERTED"

#: Herkunft -> `source`. Die Akquise schreibt `lkv` und `gap`; der Weg aus der
#: Maske schreibt die eigene Herkunft. Eine Abbildung an einer Stelle.
HERKUNFT_ZU_QUELLE = {
    "WEBSITE": "website",
    "MESSE": "messe",
    "EMPFEHLUNG": "empfehlung",
    "KALTAKQUISE": "kaltakquise",
    "SONSTIGES": "sonstiges",
}

FELDER = (
    "id, tenant_id, company, contact_person, email, phone, source, potential, "
    "priority, status, assigned_to, expected_close_date, notes, created_at, updated_at"
)

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "public.crm_leads fehlt - Run: alembic upgrade head"
}


def nicht_lesbar(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Ein Lesefehler ist keine leere Interessentenliste.

    Vorher antwortete der Weg `[]`. Ein Haus, das keine Interessenten sieht,
    akquiriert nicht — und merkt nicht, dass die Liste nur nicht lesbar war.
    """
    db.rollback()
    logger.exception("%s nicht lesbar (Mandant %s)", was, tenant_id)
    return HTTPException(
        status_code=503,
        detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
        headers=MIGRATIONS_HINWEIS,
    )


def als_dict(row: Any) -> dict:
    """Eine Zeile in der Form, die der Interessentenweg nennt.

    Die Spalten des Registers heissen englisch (`company`, `contact_person`); der
    Weg nennt sie deutsch. Die Abbildung steht hier **einmal**, damit nicht beide
    Benennungen durch den Code wandern.
    """
    d = dict(row)
    return {
        "id": str(d["id"]),
        "tenant_id": d.get("tenant_id"),
        "interessenten_nr": d.get("interessenten_nr") or _nummer_aus_notiz(d.get("notes")),
        "name": d.get("company"),
        "ansprechpartner": d.get("contact_person"),
        "email": d.get("email"),
        "telefon": d.get("phone"),
        "herkunft": d.get("source"),
        "branche": d.get("potential"),
        "prioritaet": d.get("priority"),
        "status": d.get("status"),
        "betreut_von": d.get("assigned_to"),
        "notizen": d.get("notes"),
        "erstellt_am": (
            d["created_at"].isoformat() if d.get("created_at") is not None
            and hasattr(d["created_at"], "isoformat") else d.get("created_at")
        ),
    }


def _nummer_aus_notiz(notizen: Optional[str]) -> Optional[str]:
    """Die Interessentennummer, soweit sie vermerkt ist.

    Das Register fuehrt keine eigene Nummernspalte — die uebernommenen Leads aus
    der Akquise haben keine. Der Weg aus der Maske vermerkt sie in den Notizen
    (`[INT-JJJJ-NNNNN]`), damit sie nicht verloren geht; erfunden wird keine.
    """
    if not notizen or "[INT-" not in notizen:
        return None
    anfang = notizen.index("[INT-") + 1
    ende = notizen.find("]", anfang)
    return notizen[anfang:ende] if ende > anfang else None


def auflisten(
    db: Session, tenant_id: str, status: Optional[str], limit: int, offset: int
) -> list[dict]:
    if status is not None and status not in STAENDE:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter Stand {status!r}. Erlaubt: {', '.join(STAENDE)}.",
        )
    zeilen = db.execute(
        text(
            f"SELECT {FELDER} FROM {LEADS} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE tenant_id = :tid AND (:status IS NULL OR status = :status) "
            "ORDER BY created_at DESC NULLS LAST LIMIT :limit OFFSET :offset"
        ),
        {"tid": tenant_id, "status": status, "limit": limit, "offset": offset},
    ).mappings().fetchmany(limit)
    return [als_dict(z) for z in zeilen]


def holen(db: Session, tenant_id: str, lead_id: str, sperren: bool = False) -> dict:
    zeile = db.execute(
        text(
            f"SELECT {FELDER} FROM {LEADS} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE id::text = :id AND tenant_id = :tid" + (" FOR UPDATE" if sperren else "")
        ),
        {"id": lead_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Interessent nicht gefunden")
    return dict(zeile)


def naechste_nummer(db: Session, tenant_id: str) -> str:
    """Die naechste Interessentennummer des Mandanten.

    Gezaehlt wird die **hoechste vermerkte** Nummer, nicht `COUNT(*) + 1`: Die
    Zeilenzahl aendert sich mit jedem uebernommenen Akquise-Lead, der keine Nummer
    traegt, und eine geloeschte Zeile gibt ihre Nummer frei. Beides ergab
    Doppelnummern. Und ein Lesefehler wird nicht zu `1` verschwiegen.
    """
    jahr = db.execute(text("SELECT EXTRACT(YEAR FROM NOW())::int")).scalar()
    hoechste = db.execute(
        text(
            "SELECT MAX(SUBSTRING(notes FROM :muster)::int) "
            f"FROM {LEADS} WHERE tenant_id = :tid AND notes ~ :suche"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ),
        {
            "tid": tenant_id,
            "muster": f"\\[INT-{jahr}-([0-9]+)\\]",
            "suche": f"\\[INT-{jahr}-[0-9]+\\]",
        },
    ).scalar()
    return f"INT-{jahr}-{(hoechste or 0) + 1:05d}"


def anlegen(
    db: Session, tenant_id: str, neue_id: str, nummer: str, payload: Any
) -> dict:
    """Legt den Interessenten im Register an.

    Vorher schrieb dieser Weg `domain_crm.interessenten`, fing den Fehlschlag und
    antwortete trotzdem `201` mit einer Nummer. Jetzt gibt es die Zeile — oder
    einen Fehler.
    """
    quelle = HERKUNFT_ZU_QUELLE.get(
        (payload.herkunft or "SONSTIGES").upper(), "sonstiges"
    )
    notizen = f"[{nummer}]"
    if payload.notizen:
        notizen = f"{notizen} {payload.notizen}"
    zeile = db.execute(
        text(
            f"INSERT INTO {LEADS} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, company, contact_person, email, phone, source, "
            " potential, status, notes, created_at, updated_at) "
            "VALUES (CAST(:id AS uuid), :tid, :firma, :person, :email, :telefon, "
            "        :quelle, :branche, :stand, :notizen, NOW(), NOW()) "
            f"RETURNING {FELDER}"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "firma": payload.name,
            "person": getattr(payload, "ansprechpartner", None),
            "email": payload.email,
            "telefon": payload.telefon,
            "quelle": quelle,
            "branche": payload.branche,
            "stand": NEU,
            "notizen": notizen,
        },
    ).mappings().first()
    ergebnis = als_dict(zeile)
    ergebnis["interessenten_nr"] = nummer
    return ergebnis


def stand_setzen(db: Session, tenant_id: str, lead_id: str, stand: str) -> None:
    """Den Stand im Register setzen — ohne eigenes `commit`.

    Das Festschreiben gehoert dem Aufrufer: Die Konvertierung legt einen
    Kundensatz an **und** setzt den Stand; beides muss zusammen gelten oder
    zusammen scheitern.
    """
    ergebnis = db.execute(
        text(
            f"UPDATE {LEADS} SET status = :stand, updated_at = NOW() "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE id::text = :id AND tenant_id = :tid"
        ),
        {"stand": stand, "id": lead_id, "tid": tenant_id},
    )
    if ergebnis.rowcount == 0:
        raise HTTPException(status_code=404, detail="Interessent nicht gefunden")


def schon_konvertiert(zeile: dict) -> None:
    """Ein zweites Mal konvertieren erzeugt einen zweiten Kunden."""
    if zeile.get("status") == KONVERTIERT:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Interessent {zeile.get('company')!r} ist bereits konvertiert. Ein "
                "zweiter Durchlauf legte einen zweiten Kundensatz an."
            ),
        )
