"""Bewerbungspipeline — ein Woerterbuch mit Uebergaengen und ein ehrlicher Fehler.

Was dieser Dienst in Ordnung bringt, hat der Zerlegungsslice benannt und
absichtlich liegen lassen:

* ``except Exception: raise HTTPException(503, "applications table not available")``
  verwischte jeden Fehler zu einer Tabellenaussage — auch einen Rechtefehler, eine
  verletzte Pruefbedingung oder eine Mandantenverletzung. Wer das liest, migriert
  und sucht an der falschen Stelle.
* ``APPLICATION_STAGES`` war ein ``set`` ohne Uebergaenge: Eine **abgelehnte**
  Bewerbung liess sich auf ``EINGESTELLT`` setzen.
* Die Liste war unbegrenzt, die Antwortmodelle offen, die Kennung ``uuid4``.

Grundlage: § 22 AGG (im Streitfall traegt der Arbeitgeber die Beweislast — eine
Ablehnung ohne Grund ist nicht verteidigbar), Art. 5 Abs. 1 lit. e DSGVO
(Speicherbegrenzung, siehe die benannte Luecke in der QA-Doku).

Siehe ``docs/quality-assurance/bewerbermanagement-ordnung-20261006.md``.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException
from psycopg2.errors import UndefinedColumn, UndefinedTable
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

BEWERBUNGEN = "domain_hr.applications"

#: Die Stufen der Pipeline. Deckungsgleich mit ``ck_bewerbung_status``.
STUFEN = (
    "EINGANG",
    "VORAUSWAHL",
    "ERSTGESPRAECH",
    "ENDGESPRAECH",
    "ANGEBOT",
    "EINGESTELLT",
    "ABGELEHNT",
)

#: Der Eingangsstand.
EINGANG = "EINGANG"

#: Endgueltige Staende. Aus ihnen fuehrt kein Weg heraus — eine Ablehnung ist eine
#: Mitteilung an einen Menschen, und eine Einstellung ist ein Vertrag.
ENDGUELTIG = ("EINGESTELLT", "ABGELEHNT")

#: Die laufenden Stufen in ihrer Reihenfolge. Innerhalb der laufenden Pipeline ist
#: ein Rueckschritt erlaubt: Eine Vorauswahl kann sich als zu frueh erweisen.
LAUFEND = ("EINGANG", "VORAUSWAHL", "ERSTGESPRAECH", "ENDGESPRAECH", "ANGEBOT")

#: Erlaubte Uebergaenge, aus den beiden Mengen erzeugt statt zweimal geschrieben.
UEBERGAENGE: dict[str, tuple[str, ...]] = {
    stand: tuple(z for z in LAUFEND if z != stand) + ENDGUELTIG for stand in LAUFEND
}
UEBERGAENGE.update({stand: () for stand in ENDGUELTIG})

FELDER = (
    "id, tenant_id, applicant_name, applicant_email, position_id, position_title, "
    "source, documents_ref, status, notes, ablehnungsgrund, entschieden_am, "
    "entschieden_durch, applied_at, last_updated"
)

ZEITFELDER = ("entschieden_am", "applied_at", "last_updated")

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (bewerbung_statuswoerterbuch_20261006)"
}


def fehler_deuten(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Einen Datenbankfehler so melden, dass die Ursache nennbar bleibt.

    Vorher wurde **jeder** Fehler zu ``503 "applications table not available"``.
    Das ist nur dann wahr, wenn die Tabelle tatsaechlich fehlt; in allen anderen
    Faellen schickt es den Leser in die Migration, waehrend das Problem ein
    Rechtefehler, eine verletzte Pruefbedingung oder ein Verbindungsabbruch ist.
    """
    db.rollback()
    logger.exception("%s fehlgeschlagen (Mandant %s)", was, tenant_id)
    urgrund = getattr(fehler, "orig", None)
    if isinstance(fehler, ProgrammingError) and isinstance(urgrund, (UndefinedTable, UndefinedColumn)):
        return HTTPException(
            status_code=503,
            detail={
                "error": f"{was}: Die Bewerbungstabelle ist nicht auf dem Migrationsstand.",
                "grund": str(fehler),
                "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"],
            },
            headers=MIGRATIONS_HINWEIS,
        )
    return HTTPException(
        status_code=409,
        detail={"error": f"{was} abgewiesen", "grund": str(fehler)},
    )


def als_dict(row: Any) -> dict:
    d = dict(row)
    for schluessel in ZEITFELDER:
        wert = d.get(schluessel)
        if wert is not None and hasattr(wert, "isoformat"):
            d[schluessel] = wert.isoformat()
    d["endgueltig"] = d.get("status") in ENDGUELTIG
    return d


def auflisten(
    db: Session,
    tenant_id: str,
    status: Optional[str],
    position_id: Optional[str],
    limit: int,
    offset: int,
) -> list[dict]:
    if status is not None and status not in STUFEN:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannte Stufe {status!r}. Erlaubt: {', '.join(STUFEN)}.",
        )
    zeilen = db.execute(
        text(
            f"SELECT {FELDER} FROM {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE tenant_id = :tid "
            "  AND (:status IS NULL OR status = :status) "
            "  AND (:position IS NULL OR position_id = :position) "
            "ORDER BY applied_at DESC LIMIT :limit OFFSET :offset"
        ),
        {
            "tid": tenant_id,
            "status": status,
            "position": position_id,
            "limit": limit,
            "offset": offset,
        },
    ).mappings().fetchmany(limit)
    return [als_dict(z) for z in zeilen]


def holen(db: Session, tenant_id: str, bewerbung_id: str, sperren: bool = False) -> dict:
    zeile = db.execute(
        text(
            f"SELECT {FELDER} FROM {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE id = :id AND tenant_id = :tid" + (" FOR UPDATE" if sperren else "")
        ),
        {"id": bewerbung_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail=f"Bewerbung {bewerbung_id} nicht gefunden")
    return dict(zeile)


def anlegen(db: Session, tenant_id: str, neue_id: str, payload: Any) -> dict:
    zeile = db.execute(
        text(
            f"INSERT INTO {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, applicant_name, applicant_email, position_id, "
            " position_title, source, documents_ref, status, applied_at) "
            "VALUES (:id, :tid, :name, :email, :position, :titel, :quelle, :doku, "
            "        :stand, NOW()) "
            f"RETURNING {FELDER}"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "name": payload.applicant_name,
            "email": payload.applicant_email,
            "position": payload.position_id,
            "titel": payload.position_title,
            "quelle": payload.source,
            "doku": payload.documents_ref,
            "stand": EINGANG,
        },
    ).mappings().first()
    return als_dict(zeile)


def uebergang_pruefen(von: str, nach: str, bewerbung_id: str) -> None:
    """Ein verbotener Stufenwechsel ist ein 409 mit den erlaubten Zielen.

    Vorher gab es nur die Pruefung, ob die Stufe **existiert**. Dass eine
    abgelehnte Bewerbung auf `EINGESTELLT` gesetzt werden konnte, war damit kein
    Fehler, sondern eine Luecke: Niemand kann spaeter sagen, ob die Ablehnung je
    galt.
    """
    if nach not in STUFEN:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannte Stufe {nach!r}. Erlaubt: {', '.join(STUFEN)}.",
        )
    if von not in UEBERGAENGE:
        raise HTTPException(
            status_code=409, detail=f"Bewerbung {bewerbung_id} steht in einem unbekannten Stand {von!r}."
        )
    if nach == von:
        raise HTTPException(
            status_code=409, detail=f"Bewerbung {bewerbung_id} steht bereits auf {von}."
        )
    if nach in UEBERGAENGE[von]:
        return
    if von in ENDGUELTIG:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Bewerbung {bewerbung_id} ist {von} — das ist endgueltig. Eine "
                "Ablehnung ist eine Mitteilung an einen Menschen und eine "
                "Einstellung ein Vertrag; beides wird nicht zurueckgenommen. Fuer "
                "eine neue Bewerbung desselben Menschen ist ein neuer Vorgang "
                "anzulegen."
            ),
        )
    raise HTTPException(
        status_code=409,
        detail=(
            f"Bewerbung {bewerbung_id} ist {von}; ein Wechsel nach {nach} ist nicht "
            f"vorgesehen. Erlaubt: {', '.join(UEBERGAENGE[von])}."
        ),
    )


def stufe_setzen(
    db: Session,
    tenant_id: str,
    bewerbung_id: str,
    nach: str,
    note: Optional[str] = None,
    ablehnungsgrund: Optional[str] = None,
    entschieden_durch: Optional[str] = None,
) -> dict:
    """Die Stufe wechseln — mit Sperre, Uebergangspruefung und Begruendungspflicht."""
    vorher = holen(db, tenant_id, bewerbung_id, sperren=True)
    uebergang_pruefen(vorher["status"], nach, bewerbung_id)

    if nach == "ABGELEHNT" and not (ablehnungsgrund or "").strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "Eine Ablehnung braucht einen Grund. Im Streitfall traegt der "
                "Arbeitgeber die Beweislast (§ 22 AGG) — ohne Grund ist die "
                "Ablehnung nicht verteidigbar."
            ),
        )

    verlauf = ""
    if note:
        verlauf = f"\n[{datetime.now(timezone.utc).isoformat()}] {note}"

    zeile = db.execute(
        text(
            f"UPDATE {BEWERBUNGEN} SET status = :nach, "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "    notes = COALESCE(notes, '') || :verlauf, "
            "    ablehnungsgrund = CASE WHEN :nach = 'ABGELEHNT' "
            "                           THEN :grund ELSE ablehnungsgrund END, "
            "    entschieden_am = CASE WHEN :nach IN ('EINGESTELLT', 'ABGELEHNT') "
            "                          THEN NOW() ELSE entschieden_am END, "
            "    entschieden_durch = CASE WHEN :nach IN ('EINGESTELLT', 'ABGELEHNT') "
            "                             THEN :durch ELSE entschieden_durch END, "
            "    last_updated = NOW() "
            f"WHERE id = :id AND tenant_id = :tid RETURNING {FELDER}"
        ),
        {
            "nach": nach,
            "verlauf": verlauf,
            "grund": (ablehnungsgrund or "").strip() or None,
            "durch": entschieden_durch,
            "id": bewerbung_id,
            "tid": tenant_id,
        },
    ).mappings().first()
    return als_dict(zeile)


def loeschen(db: Session, tenant_id: str, bewerbung_id: str) -> None:
    """Loescht eine Bewerbung des eigenen Mandanten.

    Der Weg stammt von einem anderen Agenten und bleibt in der Sache, wie er war:
    Eine Bewerbung ist kein Buchungsbeleg, und Art. 5 Abs. 1 lit. e DSGVO
    verlangt, personenbezogene Daten nicht laenger zu halten als noetig.
    """
    anzahl = db.execute(
        text(
            f"DELETE FROM {BEWERBUNGEN} WHERE id = :id AND tenant_id = :tid"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ),
        {"id": bewerbung_id, "tid": tenant_id},
    ).rowcount
    if not anzahl:
        raise HTTPException(status_code=404, detail=f"Bewerbung {bewerbung_id} nicht gefunden")
