"""Schadenmeldungen und Versicherungsvertraege — eine Meldung, die es gibt.

Bis zum 06.10.2026 antwortete `POST /schaeden/meldungen` mit `201`, einer
Meldungsnummer und `status: "gemeldet"` — und schrieb **nichts**. Die Liste
lieferte eine erfundene Hagelschadenmeldung ueber 12.500 EUR, die
Versicherungsliste vier erfundene Vertraege.

Das ist nicht derselbe Fehler wie eine fehlende Tabelle: Dort antwortet der Weg
503 und jemand merkt es. Hier hat ein Haus eine Meldungsnummer in der Hand und
meldet deshalb nicht noch einmal, waehrend die Frist nach § 30 Abs. 1 VVG laeuft.

Zwei Dinge sagt dieser Dienst deshalb ausdruecklich:

* **Das Anlegen erzeugt einen Entwurf**, keine Meldung. Es gibt keinen Versandweg
  zum Versicherer; das System kann nicht behaupten, er sei unterrichtet.
* **Das Melden ist ein eigener Schritt**, der festhaelt, *wann*, *durch wen* und
  *auf welchem Weg* unterrichtet wurde.

Siehe ``docs/quality-assurance/quittung-ohne-vorgang-20261006.md``.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.business_time import business_today

logger = logging.getLogger(__name__)

VERSICHERUNGEN = "domain_erp.versicherungen"
MELDUNGEN = "domain_erp.schaden_meldungen"

#: Deckungsgleich mit ``ck_versicherung_typ``.
VERSICHERUNGSARTEN = (
    "hagel", "haftpflicht", "feuer", "kasko", "inhalt", "transport", "sonstige",
)

#: Deckungsgleich mit ``ck_schaden_status``. `ENTWURF` ist der Eingangszustand.
STAENDE = ("ENTWURF", "GEMELDET", "IN_BEARBEITUNG", "REGULIERT", "ABGELEHNT")

#: Erlaubte Zustandswechsel. Aus `REGULIERT` und `ABGELEHNT` fuehrt kein Weg
#: heraus: Eine abgeschlossene Schadenakte wird nicht nachtraeglich geoeffnet.
UEBERGAENGE = {
    "ENTWURF": ("GEMELDET",),
    "GEMELDET": ("IN_BEARBEITUNG", "REGULIERT", "ABGELEHNT"),
    "IN_BEARBEITUNG": ("REGULIERT", "ABGELEHNT"),
    "REGULIERT": (),
    "ABGELEHNT": (),
}

#: Wege, auf denen ein Versicherer unterrichtet worden sein kann. Das System
#: uebermittelt nicht selbst — es haelt fest, was geschehen ist.
MELDEWEGE = ("TELEFON", "EMAIL", "POST", "FAX", "PORTAL", "PERSOENLICH")

FELDER_VERSICHERUNG = (
    "id, tenant_id, bezeichnung, vertragsnummer, typ, versicherer, gueltig_von, "
    "gueltig_bis, meldefrist_tage, ansprechpartner, kontakt, aktiv, created_at"
)

FELDER_MELDUNG = (
    "id, tenant_id, meldungsnummer, art, schadendatum, ort, beschreibung, "
    "schadenhoehe, versicherung_id, zeuge, status, gemeldet_am, gemeldet_durch, "
    "meldeweg, regulierungsbetrag, abgelehnt_grund, erfasst_durch, created_at, updated_at"
)

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (quittung_ohne_vorgang_20261006)"
}


def nicht_lesbar(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Ein Lesefehler ist keine leere Liste — und erst recht keine erfundene.

    Vorher stand hier eine Literalliste. Wer nicht lesen kann, antwortet 503.
    """
    db.rollback()
    logger.exception("%s nicht lesbar (Mandant %s)", was, tenant_id)
    return HTTPException(
        status_code=503,
        detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
        headers=MIGRATIONS_HINWEIS,
    )


def als_dict(row: Any, zeitfelder: tuple[str, ...], zahlfelder: tuple[str, ...]) -> dict:
    d = dict(row)
    for schluessel in zeitfelder:
        wert = d.get(schluessel)
        if wert is not None and hasattr(wert, "isoformat"):
            d[schluessel] = wert.isoformat()
    for schluessel in zahlfelder:
        if d.get(schluessel) is not None:
            d[schluessel] = float(d[schluessel])
    return d


# ── Versicherungsvertraege ──────────────────────────────────────────────────


def versicherungen(db: Session, tenant_id: str, limit: int = 200) -> list[dict]:
    zeilen = db.execute(
        text(
            f"SELECT {FELDER_VERSICHERUNG} FROM {VERSICHERUNGEN} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE tenant_id = :tid AND aktiv ORDER BY bezeichnung LIMIT :limit"
        ),
        {"tid": tenant_id, "limit": limit},
    ).mappings().fetchmany(limit)
    return [
        als_dict(z, ("gueltig_von", "gueltig_bis", "created_at"), ())
        for z in zeilen
    ]


def versicherung_holen(db: Session, tenant_id: str, versicherung_id: str) -> dict:
    zeile = db.execute(
        text(
            f"SELECT {FELDER_VERSICHERUNG} FROM {VERSICHERUNGEN} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": versicherung_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Versicherungsvertrag {versicherung_id!r} gehoert nicht zu diesem "
                "Mandanten oder existiert nicht."
            ),
        )
    return dict(zeile)


def versicherung_anlegen(
    db: Session, tenant_id: str, neue_id: str, payload: Any
) -> dict:
    zeile = db.execute(
        text(
            f"INSERT INTO {VERSICHERUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, bezeichnung, vertragsnummer, typ, versicherer, "
            " gueltig_von, gueltig_bis, meldefrist_tage, ansprechpartner, kontakt) "
            "VALUES (:id, :tid, :bez, :nr, :typ, :vers, :von, :bis, :frist, :ap, :kontakt) "
            f"RETURNING {FELDER_VERSICHERUNG}"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "bez": payload.bezeichnung,
            "nr": payload.vertragsnummer,
            "typ": payload.typ,
            "vers": payload.versicherer,
            "von": payload.gueltig_von,
            "bis": payload.gueltig_bis,
            "frist": payload.meldefrist_tage,
            "ap": payload.ansprechpartner,
            "kontakt": payload.kontakt,
        },
    ).mappings().first()
    return als_dict(zeile, ("gueltig_von", "gueltig_bis", "created_at"), ())


# ── Schadenmeldungen ────────────────────────────────────────────────────────


def naechste_meldungsnummer(db: Session, tenant_id: str) -> str:
    """Fortlaufend je Mandant und Jahr.

    Gezaehlt wird die hoechste vergebene Nummer, nicht die Anzahl der Zeilen: Eine
    Schadenakte verschwindet nicht, und ihre Nummer wird nicht wiederverwendet.
    """
    jahr = db.execute(text("SELECT EXTRACT(YEAR FROM NOW())::int")).scalar()
    hoechste = db.execute(
        text(
            "SELECT MAX(SUBSTRING(meldungsnummer FROM '[0-9]+$')::int) "
            f"FROM {MELDUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE tenant_id = :tid AND meldungsnummer ~ :muster"
        ),
        {"tid": tenant_id, "muster": f"^SM-{jahr}-[0-9]+$"},
    ).scalar()
    return f"SM-{jahr}-{(hoechste or 0) + 1:05d}"


def melden_bis(schadendatum: Any, meldefrist_tage: Optional[int]) -> Optional[str]:
    """Die Frist am Schaden — abgeleitet aus der Frist des Vertrags.

    Eine Frist im Code wuerde fuer alle Policen gleich gelten, und das tut sie
    nicht. Ohne Frist am Vertrag gibt es keine abgeleitete Frist — und keine
    erfundene.
    """
    if not meldefrist_tage or schadendatum is None:
        return None
    tag = schadendatum
    if isinstance(tag, str):
        tag = date.fromisoformat(tag[:10])
    if isinstance(tag, datetime):
        tag = tag.date()
    return (tag + timedelta(days=int(meldefrist_tage))).isoformat()


def anreichern(zeile: dict, frist_tage: Optional[int]) -> dict:
    """Die Meldung mit abgeleiteter Frist und Fristlage."""
    d = als_dict(
        zeile,
        ("schadendatum", "gemeldet_am", "created_at", "updated_at"),
        ("schadenhoehe", "regulierungsbetrag"),
    )
    d["meldefrist_tage"] = frist_tage
    d["melden_bis"] = melden_bis(zeile.get("schadendatum"), frist_tage)
    if d["melden_bis"] and d["status"] == "ENTWURF":
        d["frist_ueberschritten"] = d["melden_bis"] < business_today().isoformat()
    else:
        d["frist_ueberschritten"] = False
    return d


def auflisten(
    db: Session, tenant_id: str, status: Optional[str], limit: int
) -> list[dict]:
    if status is not None and status not in STAENDE:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter Stand {status!r}. Erlaubt: {', '.join(STAENDE)}.",
        )
    zeilen = db.execute(
        text(
            f"SELECT m.*, v.meldefrist_tage AS frist_tage FROM {MELDUNGEN} m "  # nosec B608  # reviewed-safe: Tabellennamen sind Code-Literale
            f"LEFT JOIN {VERSICHERUNGEN} v "
            "       ON v.id = m.versicherung_id AND v.tenant_id = m.tenant_id "
            "WHERE m.tenant_id = :tid AND (:status IS NULL OR m.status = :status) "
            "ORDER BY m.schadendatum DESC, m.meldungsnummer DESC LIMIT :limit"
        ),
        {"tid": tenant_id, "status": status, "limit": limit},
    ).mappings().fetchmany(limit)
    return [anreichern(z, z.get("frist_tage")) for z in zeilen]


def holen(db: Session, tenant_id: str, meldung_id: str, sperren: bool = False) -> dict:
    zeile = db.execute(
        text(
            f"SELECT m.*, v.meldefrist_tage AS frist_tage FROM {MELDUNGEN} m "  # nosec B608  # reviewed-safe: Tabellennamen sind Code-Literale
            f"LEFT JOIN {VERSICHERUNGEN} v "
            "       ON v.id = m.versicherung_id AND v.tenant_id = m.tenant_id "
            "WHERE m.id = :id AND m.tenant_id = :tid"
            + (" FOR UPDATE OF m" if sperren else "")
        ),
        {"id": meldung_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail=f"Schadenmeldung {meldung_id} nicht gefunden")
    return dict(zeile)


def anlegen(db: Session, tenant_id: str, neue_id: str, nummer: str, payload: Any) -> dict:
    """Legt einen **Entwurf** an.

    Nicht `GEMELDET`: Es gibt keinen Versandweg zum Versicherer, und das System
    darf nicht behaupten, er sei unterrichtet. Vorher antwortete dieser Weg
    `status: "gemeldet"` und schrieb nicht einmal eine Zeile.
    """
    frist = None
    if payload.versicherung_id:
        frist = versicherung_holen(db, tenant_id, payload.versicherung_id).get(
            "meldefrist_tage"
        )
    zeile = db.execute(
        text(
            f"INSERT INTO {MELDUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, meldungsnummer, art, schadendatum, ort, beschreibung, "
            " schadenhoehe, versicherung_id, zeuge, status, erfasst_durch) "
            "VALUES (:id, :tid, :nr, :art, :datum, :ort, :text, :hoehe, :vers, :zeuge, "
            "        'ENTWURF', :durch) "
            "RETURNING *"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "nr": nummer,
            "art": payload.art,
            "datum": payload.schadendatum,
            "ort": payload.ort,
            "text": payload.beschreibung,
            "hoehe": Decimal(str(payload.schadenhoehe or 0)),
            "vers": payload.versicherung_id,
            "zeuge": payload.zeuge,
            "durch": payload.erfasst_durch,
        },
    ).mappings().first()
    return anreichern(dict(zeile), frist)


def uebergang_pruefen(von: str, nach: str, nummer: str) -> None:
    if von not in UEBERGAENGE:
        raise HTTPException(status_code=409, detail=f"Unbekannter Zustand {von!r} an {nummer}.")
    if nach in UEBERGAENGE[von]:
        return
    if not UEBERGAENGE[von]:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Schadenmeldung {nummer} ist {von} — die Akte ist abgeschlossen und "
                "wird nicht nachtraeglich geoeffnet."
            ),
        )
    raise HTTPException(
        status_code=409,
        detail=(
            f"Schadenmeldung {nummer} ist {von}; ein Wechsel nach {nach} ist nicht "
            f"vorgesehen. Erlaubt: {', '.join(UEBERGAENGE[von])}."
        ),
    )


def melden(
    db: Session,
    tenant_id: str,
    meldung_id: str,
    meldeweg: str,
    gemeldet_durch: Optional[str],
    gemeldet_am: Optional[Any] = None,
) -> dict:
    """Haelt fest, dass der Versicherer unterrichtet wurde.

    Das System **uebermittelt nicht**. Es verzeichnet, wann, durch wen und auf
    welchem Weg die Anzeige erfolgt ist — das ist der Nachweis, den § 30 Abs. 1
    VVG braucht, und es ist etwas anderes als die Behauptung, eine Software habe
    gemeldet.
    """
    if meldeweg not in MELDEWEGE:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter Meldeweg {meldeweg!r}. Erlaubt: {', '.join(MELDEWEGE)}.",
        )
    vorher = holen(db, tenant_id, meldung_id, sperren=True)
    uebergang_pruefen(vorher["status"], "GEMELDET", vorher["meldungsnummer"])
    if not vorher.get("versicherung_id"):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Schadenmeldung {vorher['meldungsnummer']} nennt keinen "
                "Versicherungsvertrag. Ohne ihn ist nicht festzustellen, wem "
                "gemeldet wurde und welche Frist galt."
            ),
        )
    zeile = db.execute(
        text(
            f"UPDATE {MELDUNGEN} SET status = 'GEMELDET', "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "    gemeldet_am = COALESCE(CAST(:wann AS timestamptz), NOW()), "
            "    gemeldet_durch = :durch, meldeweg = :weg, updated_at = NOW() "
            "WHERE id = :id AND tenant_id = :tid RETURNING *"
        ),
        {
            "wann": gemeldet_am,
            "durch": gemeldet_durch,
            "weg": meldeweg,
            "id": meldung_id,
            "tid": tenant_id,
        },
    ).mappings().first()
    return anreichern(dict(zeile), vorher.get("frist_tage"))


def stand_setzen(
    db: Session,
    tenant_id: str,
    meldung_id: str,
    nach: str,
    regulierungsbetrag: Optional[float] = None,
    abgelehnt_grund: Optional[str] = None,
) -> dict:
    """Weiterer Zustandswechsel — Bearbeitung, Regulierung, Ablehnung."""
    vorher = holen(db, tenant_id, meldung_id, sperren=True)
    uebergang_pruefen(vorher["status"], nach, vorher["meldungsnummer"])
    if nach == "REGULIERT" and regulierungsbetrag is None:
        raise HTTPException(
            status_code=422,
            detail="Eine Regulierung ohne Betrag ist keine — der regulierte Betrag fehlt.",
        )
    if nach == "ABGELEHNT" and not (abgelehnt_grund or "").strip():
        raise HTTPException(
            status_code=422,
            detail="Eine Ablehnung ohne Grund laesst sich nicht pruefen.",
        )
    zeile = db.execute(
        text(
            f"UPDATE {MELDUNGEN} SET status = :nach, "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "    regulierungsbetrag = COALESCE(CAST(:betrag AS numeric), regulierungsbetrag), "
            "    abgelehnt_grund = COALESCE(:grund, abgelehnt_grund), updated_at = NOW() "
            "WHERE id = :id AND tenant_id = :tid RETURNING *"
        ),
        {
            "nach": nach,
            "betrag": regulierungsbetrag,
            "grund": (abgelehnt_grund or "").strip() or None,
            "id": meldung_id,
            "tid": tenant_id,
        },
    ).mappings().first()
    return anreichern(dict(zeile), vorher.get("frist_tage"))
