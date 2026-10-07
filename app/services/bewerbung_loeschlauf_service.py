"""Der Loeschlauf fuer Bewerberdaten.

Art. 5 Abs. 1 lit. e DSGVO verlangt, personenbezogene Daten nicht laenger zu
halten als fuer den Zweck noetig. Fuer Bewerberdaten ist der Zweck mit dem
Verfahren erledigt; ueblich sind sechs Monate nach der Ablehnung — zwei Monate
Geltendmachung nach § 15 Abs. 4 AGG plus Zustellung und Klagefrist-Puffer.

Drei Dinge, die dieser Dienst nicht tut:

* **Er loescht nicht ohne Regel.** Gibt es fuer den Mandanten keine
  Aufbewahrungsregel, loescht er nichts und sagt das. Eine Frist, die niemand
  beschlossen hat, ist keine Grundlage, um Daten zu vernichten.
* **Er loescht nichts Offenes.** Nur entschiedene Bewerbungen
  (`EINGESTELLT`/`ABGELEHNT`) haben einen Fristanker (`entschieden_am`).
* **Er uebergeht keine Sperre.** Laeuft eine AGG-Klage, sind die Daten
  Beweismittel; eine aktive Loeschsperre schuetzt sie, und der Lauf sagt, wie
  viele er deshalb stehen gelassen hat.

Der Nachweis traegt **Zahlen, keine Namen**: Man muss beweisen koennen, *dass*
geloescht wurde, ohne zu behalten, *was* geloescht wurde.

Siehe ``docs/quality-assurance/bewerbung-loeschlauf-20261006.md``.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.business_time import business_today

logger = logging.getLogger(__name__)

BEWERBUNGEN = "domain_hr.applications"
REGELN = "domain_hr.bewerbung_aufbewahrung"
LAEUFE = "domain_hr.bewerbung_loeschlaeufe"
#: Die allgemeine Loeschsperre. Trotz ihres Namens keine GoBD-Sache, sondern der
#: Begriff: ein Datensatz, der nicht geloescht werden darf.
SPERREN = "public.gobd_loeschsperren"

#: Der Dokumenttyp, unter dem eine Sperre auf eine Bewerbung zeigt.
SPERRE_TYP = "BEWERBUNG"

#: Der Stand einer wirksamen Sperre. Das Woerterbuch der Sperrtabelle ist
#: **englisch** (`ACTIVE`/`RELEASED`/`EXPIRED`, siehe `app/finance/models.py`
#: `DocumentHold` und `app/finance/router.py`) — ein deutsches "AKTIV" haette hier
#: nie getroffen und jede Sperre uebergangen.
SPERRE_AKTIV = "ACTIVE"

#: Nur entschiedene Bewerbungen haben einen Fristanker.
ENTSCHIEDEN = ("EINGESTELLT", "ABGELEHNT")

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (bewerbung_loeschlauf_20261006)"
}


def regel(db: Session, tenant_id: str) -> Optional[dict]:
    """Die aktive Aufbewahrungsregel des Mandanten — oder nichts."""
    zeile = db.execute(
        text(
            "SELECT id, tenant_id, aufbewahrung_tage, gesetzliche_grundlage, "
            "       beschluss_am, beschluss_durch "
            f"FROM {REGELN} WHERE tenant_id = :tid AND aktiv"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ),
        {"tid": tenant_id},
    ).mappings().first()
    return dict(zeile) if zeile else None


def regel_setzen(db: Session, tenant_id: str, neue_id: str, payload: Any) -> dict:
    """Legt die Regel an oder aendert sie. Je Mandant gilt eine."""
    zeile = db.execute(
        text(
            f"INSERT INTO {REGELN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, aufbewahrung_tage, gesetzliche_grundlage, beschluss_am, "
            " beschluss_durch) "
            "VALUES (:id, :tid, :tage, :grundlage, :am, :durch) "
            "ON CONFLICT (tenant_id) WHERE aktiv DO UPDATE SET "
            "    aufbewahrung_tage = EXCLUDED.aufbewahrung_tage, "
            "    gesetzliche_grundlage = EXCLUDED.gesetzliche_grundlage, "
            "    beschluss_am = EXCLUDED.beschluss_am, "
            "    beschluss_durch = EXCLUDED.beschluss_durch, "
            "    updated_at = NOW() "
            "RETURNING id, tenant_id, aufbewahrung_tage, gesetzliche_grundlage, "
            "          beschluss_am, beschluss_durch, aktiv"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "tage": payload.aufbewahrung_tage,
            "grundlage": payload.gesetzliche_grundlage,
            "am": payload.beschluss_am,
            "durch": payload.beschluss_durch,
        },
    ).mappings().first()
    d = dict(zeile)
    if d.get("beschluss_am") is not None and hasattr(d["beschluss_am"], "isoformat"):
        d["beschluss_am"] = d["beschluss_am"].isoformat()
    return d


def ohne_regel(tenant_id: str) -> HTTPException:
    """Ohne beschlossene Frist wird nicht geloescht — und das wird gesagt.

    Dass der Lauf dann nichts tut, kann als Fehlfunktion missverstanden werden.
    Deshalb nennt die Antwort den Grund und den Weg dorthin.
    """
    return HTTPException(
        status_code=409,
        detail={
            "error": (
                "Fuer diesen Mandanten ist keine Aufbewahrungsfrist fuer "
                "Bewerberdaten beschlossen. Ohne Frist wird nicht geloescht: Eine "
                "Frist, die niemand beschlossen hat, ist keine Grundlage, um Daten "
                "zu vernichten."
            ),
            "weg": "PUT /api/v1/personal/applications/aufbewahrung",
            "hinweis": (
                "Ueblich sind 180 Tage nach der Entscheidung — zwei Monate "
                "Geltendmachung nach § 15 Abs. 4 AGG plus Zustellung und "
                "Klagefrist-Puffer. Die Festlegung gehoert dem Haus."
            ),
        },
    )


def stichtag(tage: int, heute: Optional[date] = None) -> date:
    """Der Tag, bis zu dem eine Entscheidung gefallen sein muss, damit sie faellig ist."""
    return (heute or business_today()) - timedelta(days=int(tage))


def faellige(
    db: Session, tenant_id: str, tage: int, limit: int = 1000,
    *, heute: Optional[date] = None,
) -> list[dict]:
    """Die faelligen Bewerbungen — mit Grund, warum sie stehen bleiben.

    Die Liste traegt den Namen noch, weil sie ein **Trockenlauf** ist: Wer
    personenbezogene Daten vernichtet, soll vorher sehen koennen, welche. Ins
    Protokoll kommt der Name nicht.
    """
    heute = heute if heute is not None else business_today()
    tag = stichtag(tage, heute)
    zeilen = db.execute(
        text(
            "SELECT b.id, b.applicant_name, b.applicant_email, b.status, "
            "       b.entschieden_am, b.aufbewahrung_einwilligung_bis, "
            "       (b.aufbewahrung_einwilligung_bis IS NOT NULL "
            "        AND b.aufbewahrung_einwilligung_bis >= CAST(:heute AS date)) AS einwilligung_laeuft, "
            "       EXISTS (SELECT 1 FROM " + SPERREN + " s "
            "               WHERE s.dokument_id = b.id AND s.tenant_id = b.tenant_id "
            "                 AND s.dokument_typ = :sperrtyp AND s.status = :sperraktiv "
            "                 AND (s.hold_end_date IS NULL "
            "                      OR s.hold_end_date >= CAST(:heute AS date))) AS gesperrt "
            f"FROM {BEWERBUNGEN} b "  # nosec B608  # reviewed-safe: Tabellennamen sind Code-Literale
            "WHERE b.tenant_id = :tid AND b.status = ANY(:entschieden) "
            "  AND b.entschieden_am IS NOT NULL "
            "  AND b.entschieden_am::date <= :stichtag "
            "ORDER BY b.entschieden_am LIMIT :limit"
        ),
        {
            "tid": tenant_id,
            "entschieden": list(ENTSCHIEDEN),
            "stichtag": tag,
            "heute": heute,
            "sperrtyp": SPERRE_TYP,
            "sperraktiv": SPERRE_AKTIV,
            "limit": limit,
        },
    ).mappings().fetchmany(limit)
    ergebnis = []
    for z in zeilen:
        grund = None
        if z["gesperrt"]:
            grund = "LOESCHSPERRE"
        elif z["einwilligung_laeuft"]:
            grund = "EINWILLIGUNG"
        ergebnis.append(
            {
                "id": str(z["id"]),
                "applicant_name": z["applicant_name"],
                "applicant_email": z["applicant_email"],
                "status": z["status"],
                "entschieden_am": (
                    z["entschieden_am"].isoformat() if z["entschieden_am"] else None
                ),
                "aufbewahrung_einwilligung_bis": (
                    z["aufbewahrung_einwilligung_bis"].isoformat()
                    if z["aufbewahrung_einwilligung_bis"] else None
                ),
                "wird_geloescht": grund is None,
                "bleibt_wegen": grund,
            }
        )
    return ergebnis


def lauf_ausfuehren(
    db: Session,
    tenant_id: str,
    lauf_id: str,
    regelsatz: dict,
    durchgefuehrt_durch: Optional[str],
    limit: int = 1000,
) -> dict:
    """Loescht die faelligen Bewerbungen und schreibt den Nachweis.

    Beides in **einer** Transaktion: Ein Protokoll ohne Loeschung waere eine
    falsche Zusage, eine Loeschung ohne Protokoll ein unbelegter Eingriff.
    """
    tage = int(regelsatz["aufbewahrung_tage"])
    heute = business_today()
    tag = stichtag(tage, heute)
    kandidaten = faellige(db, tenant_id, tage, limit, heute=heute)

    zu_loeschen = [k["id"] for k in kandidaten if k["wird_geloescht"]]
    gesperrt = sum(1 for k in kandidaten if k["bleibt_wegen"] == "LOESCHSPERRE")
    einwilligung = sum(1 for k in kandidaten if k["bleibt_wegen"] == "EINWILLIGUNG")

    geloescht = 0
    if zu_loeschen:
        geloescht = db.execute(
            text(
                f"DELETE FROM {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "WHERE tenant_id = :tid AND id = ANY(:ids)"
            ),
            {"tid": tenant_id, "ids": zu_loeschen},
        ).rowcount

    zeile = db.execute(
        text(
            f"INSERT INTO {LAEUFE} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, aufbewahrung_tage, stichtag, geprueft, geloescht, "
            " uebersprungen_sperre, uebersprungen_einwilligung, durchgefuehrt_durch, hinweis) "
            "VALUES (:id, :tid, :tage, :stichtag, :geprueft, :geloescht, :sperre, "
            "        :einwilligung, :durch, :hinweis) "
            "RETURNING id, gestartet_am, aufbewahrung_tage, stichtag, geprueft, "
            "          geloescht, uebersprungen_sperre, uebersprungen_einwilligung, "
            "          durchgefuehrt_durch, hinweis"
        ),
        {
            "id": lauf_id,
            "tid": tenant_id,
            "tage": tage,
            "stichtag": tag,
            "geprueft": len(kandidaten),
            "geloescht": geloescht,
            "sperre": gesperrt,
            "einwilligung": einwilligung,
            "durch": durchgefuehrt_durch,
            "hinweis": regelsatz["gesetzliche_grundlage"],
        },
    ).mappings().first()
    d = dict(zeile)
    for schluessel in ("gestartet_am", "stichtag"):
        if d.get(schluessel) is not None and hasattr(d[schluessel], "isoformat"):
            d[schluessel] = d[schluessel].isoformat()
    # Wurde die Grenze erreicht, ist der Lauf unvollstaendig — das muss sichtbar
    # sein, sonst sieht ein halber Lauf wie ein fertiger aus.
    d["weitere_faellig"] = len(kandidaten) >= limit
    return d


def laeufe(db: Session, tenant_id: str, limit: int = 100) -> list[dict]:
    """Die vergangenen Laeufe — der Nachweis, dass geloescht wurde."""
    zeilen = db.execute(
        text(
            "SELECT id, gestartet_am, aufbewahrung_tage, stichtag, geprueft, geloescht, "
            "       uebersprungen_sperre, uebersprungen_einwilligung, "
            "       durchgefuehrt_durch, hinweis "
            f"FROM {LAEUFE} WHERE tenant_id = :tid "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "ORDER BY gestartet_am DESC LIMIT :limit"
        ),
        {"tid": tenant_id, "limit": limit},
    ).mappings().fetchmany(limit)
    ergebnis = []
    for z in zeilen:
        d = dict(z)
        for schluessel in ("gestartet_am", "stichtag"):
            if d.get(schluessel) is not None and hasattr(d[schluessel], "isoformat"):
                d[schluessel] = d[schluessel].isoformat()
        d["weitere_faellig"] = False
        ergebnis.append(d)
    return ergebnis
