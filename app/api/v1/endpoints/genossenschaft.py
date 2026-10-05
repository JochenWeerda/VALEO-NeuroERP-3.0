"""Genossenschaft API — Mitgliederregister und Anteilsbewegungen einer eG.

Bis zum 05.10.2026 lasen alle Wege dieses Moduls zwei Tabellen, die **keine
Migration anlegt** und die in keiner Datenbank existierten. Der Lesefehler lief
in ``except: return []`` beziehungsweise in ein Nulldictionary: Die
Mitgliederliste war leer, die Kapitaluebersicht meldete 0 Mitglieder und
**0,00 EUR Kapital**. Fuer eine eingetragene Genossenschaft ist beides nie wahr
— § 30 GenG verpflichtet zur Mitgliederliste, und das Geschaeftsguthaben der
Mitglieder ist eine Bilanzposition (§ 337 HGB). Ausserdem lief keine Abfrage
mandantengebunden, obwohl ``get_tenant_id`` als Abhaengigkeit haengt.

Jetzt gilt: Der Anteilsbestand wird aus den Bewegungen **abgeleitet**, jede
Abfrage traegt den Mandanten, ein Lesefehler ist ein 503, und die
Hauptbuchbuchung einer Anteilsbewegung ist verbindlich — faellt sie aus, ist die
Bewegung nicht gebucht.

Entscheidungen und Beweislage:
``docs/quality-assurance/genossenschaft-mitgliederregister-20261005.md``.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.schemas.genossenschaft_schemas import (
    AnteilsbewegungCreate,
    AnteilsbewegungGebucht,
    KapitaluebersichtOut,
    MitgliedAngelegt,
    MitgliedCreate,
    MitgliedDetailOut,
    MitgliedGeaendert,
    MitgliedOut,
    MitgliedPatch,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services import genossenschaft_service as dienst

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/genossenschaft", tags=["Genossenschaft"])

#: Kontenzuordnung nach dem Bestandscode. Fachlich beim Finanz-Owner; hier nur
#: verbindlich gemacht, nicht erweitert.
KONTO_BANK = "1200"
KONTO_GESCHAEFTSGUTHABEN = "0900"
KONTO_VERBINDLICHKEIT_MITGLIED = "1600"

#: Bewegungen, die das Geschaeftsguthaben im Hauptbuch veraendern. Eine
#: Uebertragung steht nicht dabei: Anteile wechseln das Mitglied, die
#: Bilanzposition bleibt gleich.
GL_PFLICHTIG = ("ZEICHNUNG", "ERHOEHUNG", "TEILRUECKZAHLUNG", "VOLLRUECKZAHLUNG")


# ── Mitglieder (§ 30 GenG) ──────────────────────────────────────────────────


@router.get("/mitglieder", response_model=list[MitgliedOut], summary="Mitgliederliste (§ 30 GenG)")
def list_mitglieder(
    status: Optional[str] = Query(None, description="AKTIV | RUHEND | AUSGETRETEN"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    """Die Mitgliederliste des Mandanten samt abgeleitetem Anteilsbestand.

    Ein Lesefehler ist ein 503 und keine leere Liste: "Keine Mitglieder" ist bei
    einer eG keine moegliche Antwort, sondern ein Befund.
    """
    if status is not None and status not in dienst.STAENDE:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter Stand {status!r}. Erlaubt: {', '.join(dienst.STAENDE)}.",
        )
    try:
        zeilen = db.execute(
            text(
                f"SELECT * FROM ({dienst.MITGLIEDER_MIT_BESTAND}) q "  # nosec B608  # reviewed-safe: der Ausdruck ist aus Code-Literalen erzeugt, Werte sind gebunden
                "WHERE (:status IS NULL OR q.status = :status) "
                "ORDER BY q.mitglieds_nr LIMIT :limit OFFSET :offset"
            ),
            {"tid": tenant_id, "status": status, "limit": limit, "offset": offset},
        ).mappings().all()
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Mitgliederliste", tenant_id) from fehler
    return [dienst.als_dict(z) for z in zeilen]


@router.post("/mitglieder", status_code=201, response_model=MitgliedAngelegt,
             summary="Mitglied aufnehmen (§ 15 GenG)")
def create_mitglied(
    payload: MitgliedCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Nimmt ein Mitglied in die Liste auf.

    Eine Erstzeichnung wird als Bewegung ``ZEICHNUNG`` gebucht, nicht als Zahl
    gespeichert — damit auch der erste Anteil einen Beleg hat. Scheitert diese
    Bewegung oder ihre Hauptbuchbuchung, entsteht kein Mitglied: Ein Mitglied
    mit unbelegten Anteilen waere schlimmer als keines.
    """
    if payload.status == "AUSGETRETEN":
        raise HTTPException(
            status_code=422,
            detail="Ein Mitglied tritt nicht als AUSGETRETEN ein. Erst aufnehmen, dann austreten.",
        )
    mitglied_id = str(uuid7())
    try:
        mitglieds_nr = payload.mitglieds_nr or dienst.naechste_mitglieds_nr(db, tenant_id)
        db.execute(
            text(
                f"INSERT INTO {dienst.MITGLIEDER} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "(id, tenant_id, mitglieds_nr, name, adresse, eintrittsdatum, "
                " anteilswert_eur, status, iban, bank_name) "
                "VALUES (:id, :tid, :nr, :name, :adresse, :eintritt, "
                "        :anteilswert, :status, :iban, :bank)"
            ),
            {
                "id": mitglied_id,
                "tid": tenant_id,
                "nr": mitglieds_nr,
                "name": payload.name,
                "adresse": payload.adresse,
                "eintritt": payload.eintrittsdatum,
                "anteilswert": payload.anteilswert_eur,
                "status": payload.status,
                "iban": payload.iban,
                "bank": payload.bank_name,
            },
        )
        if payload.genossenschaftsanteile > 0:
            wert = payload.genossenschaftsanteile * payload.anteilswert_eur
            bewegung_id = str(uuid7())
            journal_id = _hauptbuch_buchen(
                db, tenant_id, "ZEICHNUNG", wert, payload.eintrittsdatum,
                bewegung_id, mitglieds_nr,
            )
            dienst.bewegung_schreiben(
                db, tenant_id, bewegung_id, mitglied_id, "ZEICHNUNG",
                payload.genossenschaftsanteile, wert, payload.eintrittsdatum,
                bemerkung="Erstzeichnung beim Beitritt",
                journal_entry_id=journal_id,
                erfasst_durch=payload.erfasst_durch,
            )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Mitglied nicht anlegbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Mitglied nicht angelegt",
                "grund": str(fehler),
                "migration_hint": dienst.MIGRATIONS_HINWEIS["X-Migration-Hint"],
            },
        ) from fehler
    return {
        "id": mitglied_id,
        "mitglieds_nr": mitglieds_nr,
        "genossenschaftsanteile": payload.genossenschaftsanteile,
    }


@router.get("/mitglieder/{mitglied_id}", response_model=MitgliedDetailOut,
            summary="Mitglied mit Anteilsbewegungen")
def get_mitglied(
    mitglied_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Ein Mitglied samt Bestand und Bewegungshistorie.

    Die Historie wird nicht stillschweigend geleert, wenn sie nicht lesbar ist:
    Sie ist der Nachweis des Geschaeftsguthabens.
    """
    try:
        zeile = db.execute(
            text(
                f"SELECT * FROM ({dienst.MITGLIEDER_MIT_BESTAND}) q WHERE q.id = :id"  # nosec B608  # reviewed-safe: der Ausdruck ist aus Code-Literalen erzeugt, Werte sind gebunden
            ),
            {"tid": tenant_id, "id": mitglied_id},
        ).mappings().first()
        if not zeile:
            raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")
        mitglied = dienst.als_dict(zeile)
        mitglied["anteilsbewegungen"] = dienst.bewegungen(db, tenant_id, mitglied_id)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Mitgliedsakte", tenant_id) from fehler
    return mitglied


@router.patch("/mitglieder/{mitglied_id}", response_model=MitgliedGeaendert,
              summary="Mitgliedsstammdaten aendern")
def patch_mitglied(
    mitglied_id: str,
    payload: MitgliedPatch,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Aendert Stammdaten — nicht den Anteilsbestand.

    Der Bestand aendert sich ausschliesslich durch eine Bewegung; das Schema
    kennt das Feld deshalb nicht mehr. Ein Austritt braucht ein Datum und einen
    abgewickelten Bestand: Das Auseinandersetzungsguthaben nach § 73 GenG ist
    zuerst zu buchen, sonst verschwaende der Austritt eine offene Forderung.
    """
    aenderungen = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not aenderungen:
        raise HTTPException(status_code=400, detail="Keine Aenderungen uebergeben")

    erlaubt = {
        "name": "name",
        "adresse": "adresse",
        "anteilswert_eur": "anteilswert_eur",
        "status": "status",
        "austrittsdatum": "austrittsdatum",
        "iban": "iban",
        "bank_name": "bank_name",
    }
    unbekannt = set(aenderungen) - set(erlaubt)
    if unbekannt:
        raise HTTPException(status_code=422, detail=f"Nicht aenderbar: {', '.join(sorted(unbekannt))}")

    try:
        mitglied = dienst.mitglied_sperren(db, tenant_id, mitglied_id)
        if aenderungen.get("status") == "AUSGETRETEN":
            if "austrittsdatum" not in aenderungen:
                raise HTTPException(
                    status_code=422,
                    detail="Ein Austritt braucht ein Austrittsdatum (§ 30 Abs. 2 GenG).",
                )
            offen = dienst.bestand(db, tenant_id, mitglied_id)
            if offen != 0:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Mitglied {mitglied['mitglieds_nr']} haelt noch {offen} Anteile. "
                        "Vor dem Austritt ist das Auseinandersetzungsguthaben zu buchen "
                        "(§ 73 GenG) — VOLLRUECKZAHLUNG oder UEBERTRAGUNG_AB."
                    ),
                )
        zuweisungen = ", ".join(f"{erlaubt[k]} = :{k}" for k in aenderungen)
        db.execute(
            text(
                f"UPDATE {dienst.MITGLIEDER} SET {zuweisungen} "  # nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {**aenderungen, "id": mitglied_id, "tid": tenant_id},
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Mitglied nicht aenderbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=409, detail={"error": "Aenderung abgewiesen", "grund": str(fehler)}
        ) from fehler
    return {"id": mitglied_id, "geaenderte_felder": sorted(aenderungen)}


# ── Anteilsbewegungen ───────────────────────────────────────────────────────


def _belegnummer(bewegung_id: str) -> str:
    """Die Belegnummer aus der Bewegungskennung.

    Nicht aus den **ersten** Zeichen: ``uuid7`` ist zeitgeordnet, und die
    vorderen Stellen sind der Zeitstempel. Zwei Bewegungen derselben Minute
    bekaemen dieselbe Nummer — und weil ``journal_entries.entry_number``
    systemweit eindeutig ist, scheitert die zweite Buchung. Die hinteren Stellen
    sind der Zufallsteil.
    """
    return f"GENO-{bewegung_id.replace('-', '')[-12:].upper()}"


def _hauptbuch_buchen(
    db: Session,
    tenant_id: str,
    typ: str,
    wert: float,
    datum,
    bewegung_id: str,
    mitglieds_nr: str,
) -> Optional[str]:
    """Bucht die Anteilsbewegung ins Hauptbuch — verbindlich.

    Vor dem 05.10.2026 stand dieser Aufruf in
    ``except Exception: pass  # GL-Buchung nicht kritisch``. Faellt sie aus,
    weicht das gezeichnete Kapital im Hauptbuch dauerhaft von der
    Mitgliederliste ab (§ 238 HGB, GoBD Rz. 30 ff.) — und niemand erfaehrt es.
    Jetzt laeuft sie in derselben Transaktion, und ihr Fehlschlag verhindert die
    Bewegung.

    Eine Uebertragung wird nicht gebucht: Die Anteile wechseln das Mitglied, das
    Geschaeftsguthaben der Genossenschaft bleibt gleich.
    """
    if typ not in GL_PFLICHTIG:
        return None
    from app.services.finance_transaction_service import FinanceTransactionService

    fin = FinanceTransactionService(db, tenant_id)
    try:
        if typ in ("ZEICHNUNG", "ERHOEHUNG"):
            lines = [
                {"account_id": fin.account_id_for_number(KONTO_BANK),
                 "debit_amount": wert, "credit_amount": 0.0,
                 "description": f"Anteilszeichnung Mitglied {mitglieds_nr}"},
                {"account_id": fin.account_id_for_number(KONTO_GESCHAEFTSGUTHABEN),
                 "debit_amount": 0.0, "credit_amount": wert,
                 "description": "Geschaeftsguthaben der Mitglieder"},
            ]
        else:
            lines = [
                {"account_id": fin.account_id_for_number(KONTO_GESCHAEFTSGUTHABEN),
                 "debit_amount": wert, "credit_amount": 0.0,
                 "description": f"Anteilsrueckzahlung Mitglied {mitglieds_nr}"},
                {"account_id": fin.account_id_for_number(KONTO_VERBINDLICHKEIT_MITGLIED),
                 "debit_amount": 0.0, "credit_amount": wert,
                 "description": "Auseinandersetzungsguthaben (§ 73 GenG)"},
            ]
        eintrag = fin.create(
            entry_number=_belegnummer(bewegung_id),
            description=f"Anteilsbewegung {typ} Mitglied {mitglieds_nr}",
            entry_date=datum,
            lines=lines,
            reference=bewegung_id,
            source="genossenschaft_anteile",
            document_type="anteilsbewegung",
            period=str(datum)[:7],
        )
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        # Der Grund gehoert in die Antwort: Fehlt das Konto im Kontenrahmen oder
        # ist die Periode geschlossen, ist das eine Entscheidung des Hauses und
        # keine Stoerung, die man wegloggt.
        logger.exception("Hauptbuchbuchung der Anteilsbewegung %s fehlgeschlagen", bewegung_id)
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Anteilsbewegung nicht gebucht: Die Hauptbuchbuchung ist gescheitert.",
                "grund": str(fehler),
                "hinweis": (
                    f"Benoetigt werden die bebuchbaren Konten {KONTO_BANK}, "
                    f"{KONTO_GESCHAEFTSGUTHABEN} und {KONTO_VERBINDLICHKEIT_MITGLIED} "
                    "im Kontenrahmen des Mandanten sowie eine offene Periode."
                ),
            },
        ) from fehler
    return str(getattr(eintrag, "id", "") or "") or None


@router.post("/mitglieder/{mitglied_id}/anteilsbewegung", status_code=201,
             response_model=AnteilsbewegungGebucht, summary="Anteilsbewegung buchen")
def create_anteilsbewegung(
    mitglied_id: str,
    payload: AnteilsbewegungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Buchen einer Anteilsbewegung. Der Bestand folgt daraus.

    Geprueft wird gegen den **abgeleiteten** Bestand unter einer Zeilensperre:
    Zwei gleichzeitige Rueckzahlungen duerfen nicht denselben Bestand sehen. Eine
    Uebertragung schreibt beide Seiten oder keine.
    """
    bewegung_id = str(uuid7())
    gegenbewegung_id: Optional[str] = None
    try:
        mitglied = dienst.mitglied_sperren(db, tenant_id, mitglied_id)
        verfuegbar = dienst.bestand(db, tenant_id, mitglied_id)
        dienst.abgang_pruefen(
            payload.bewegungstyp, payload.anzahl_anteile, verfuegbar, mitglied["mitglieds_nr"]
        )

        gegenseite = None
        if payload.bewegungstyp in dienst.UEBERTRAGUNGEN:
            if not payload.gegen_mitglieds_id:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"{payload.bewegungstyp} braucht eine Gegenseite: Eine Uebertragung "
                        "hat zwei Seiten, sonst entstehen oder verschwinden Anteile."
                    ),
                )
            if payload.gegen_mitglieds_id == mitglied_id:
                raise HTTPException(
                    status_code=422, detail="Eine Uebertragung an sich selbst ist keine."
                )
            gegenseite = dienst.mitglied_sperren(db, tenant_id, payload.gegen_mitglieds_id)
            gegentyp = dienst.GEGENTYP[payload.bewegungstyp]
            if gegentyp in dienst.ABGANG:
                dienst.abgang_pruefen(
                    gegentyp,
                    payload.anzahl_anteile,
                    dienst.bestand(db, tenant_id, payload.gegen_mitglieds_id),
                    gegenseite["mitglieds_nr"],
                )
        elif payload.gegen_mitglieds_id:
            raise HTTPException(
                status_code=422,
                detail=f"{payload.bewegungstyp} kennt keine Gegenseite.",
            )

        journal_id = _hauptbuch_buchen(
            db, tenant_id, payload.bewegungstyp, payload.wert_eur, payload.datum,
            bewegung_id, mitglied["mitglieds_nr"],
        )
        dienst.bewegung_schreiben(
            db, tenant_id, bewegung_id, mitglied_id, payload.bewegungstyp,
            payload.anzahl_anteile, payload.wert_eur, payload.datum,
            bemerkung=payload.bemerkung,
            gegen_mitglieds_id=payload.gegen_mitglieds_id,
            journal_entry_id=journal_id,
            erfasst_durch=payload.erfasst_durch,
        )
        if gegenseite is not None:
            gegenbewegung_id = str(uuid7())
            dienst.bewegung_schreiben(
                db, tenant_id, gegenbewegung_id, payload.gegen_mitglieds_id,
                dienst.GEGENTYP[payload.bewegungstyp], payload.anzahl_anteile,
                payload.wert_eur, payload.datum,
                bemerkung=f"Gegenbuchung zu {bewegung_id}",
                gegen_mitglieds_id=mitglied_id,
                erfasst_durch=payload.erfasst_durch,
            )
        bestand_nachher = verfuegbar + dienst.VORZEICHEN[payload.bewegungstyp] * payload.anzahl_anteile
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Anteilsbewegung nicht buchbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Anteilsbewegung abgewiesen",
                "grund": str(fehler),
                "migration_hint": dienst.MIGRATIONS_HINWEIS["X-Migration-Hint"],
            },
        ) from fehler
    return {
        "id": bewegung_id,
        "mitglieds_id": mitglied_id,
        "bewegungstyp": payload.bewegungstyp,
        "bestand_anteile": bestand_nachher,
        "gegenbewegung_id": gegenbewegung_id,
        "journal_entry_id": journal_id,
    }


# ── Kapital (§ 337 HGB) ─────────────────────────────────────────────────────


@router.get("/kapitaluebersicht", response_model=KapitaluebersichtOut,
            summary="Geschaeftsguthaben der Mitglieder (§ 337 HGB)")
def kapitaluebersicht(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Die Aggregatsicht auf das Geschaeftsguthaben.

    Summiert wird ueber die abgeleiteten Bestaende, nicht ueber eine
    fortgeschriebene Spalte. Ein Lesefehler ist ein 503: Ein Kapital von
    0,00 EUR ist eine Bilanzaussage und darf nicht aus einem Fehler entstehen.
    """
    try:
        zeile = db.execute(
            text(
                "SELECT COUNT(*) AS total_mitglieder, "
                "       COALESCE(SUM(q.genossenschaftsanteile), 0) AS total_anteile, "
                "       COALESCE(SUM(q.geschaeftsguthaben_eur), 0.0) AS total_kapital_eur, "
                "       COUNT(*) FILTER (WHERE q.status = 'AKTIV') AS aktiv, "
                "       COUNT(*) FILTER (WHERE q.status = 'RUHEND') AS ruhend, "
                "       COUNT(*) FILTER (WHERE q.status = 'AUSGETRETEN') AS ausgetreten, "
                "       COALESCE(SUM(q.genossenschaftsanteile) "
                "                FILTER (WHERE q.status = 'AUSGETRETEN'), 0) "
                "         AS offene_auseinandersetzung_anteile "
                f"FROM ({dienst.MITGLIEDER_MIT_BESTAND}) q"  # nosec B608  # reviewed-safe: der Ausdruck ist aus Code-Literalen erzeugt, Werte sind gebunden
            ),
            {"tid": tenant_id},
        ).mappings().first()
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Kapitaluebersicht", tenant_id) from fehler
    if not zeile:
        raise dienst.nicht_lesbar(
            db, RuntimeError("Aggregat ohne Zeile"), "Kapitaluebersicht", tenant_id
        )
    return {
        "total_mitglieder": int(zeile["total_mitglieder"] or 0),
        "total_anteile": int(zeile["total_anteile"] or 0),
        "total_kapital_eur": float(zeile["total_kapital_eur"] or 0.0),
        "aktiv": int(zeile["aktiv"] or 0),
        "ruhend": int(zeile["ruhend"] or 0),
        "ausgetreten": int(zeile["ausgetreten"] or 0),
        "offene_auseinandersetzung_anteile": int(
            zeile["offene_auseinandersetzung_anteile"] or 0
        ),
    }
