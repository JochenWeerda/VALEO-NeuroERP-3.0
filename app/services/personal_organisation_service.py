"""Organigramm und Arbeitszeitkonto — eine Wahrheit uber Baum und Saldo.

Zwei Faecher, die beide nachweispflichtig sind, lasen Tabellen, die es nicht gibt:
`domain_hr.org_units`, `domain_hr.time_account_adjustments` und
`domain_hr.schichten` — letzteres eine deutsche Dublette des vorhandenen
`domain_hr.shifts`.

Grundlage: § 16 Abs. 2 ArbZG (Aufzeichnung der ueber die werktaegliche Arbeitszeit
hinausgehenden Stunden), GoBD Rz. 30 ff. (Nachvollziehbarkeit). Siehe
``docs/quality-assurance/personal-organisation-zeitkonto-20261006.md``.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.business_time import business_today

logger = logging.getLogger(__name__)

EINHEITEN = "domain_hr.org_units"
KORREKTUREN = "domain_hr.time_account_adjustments"
ZEITEINTRAEGE = "domain_hr.time_entries"
#: Die kanonische Schichttabelle. `domain_hr.schichten` existiert nicht und hat
#: nie existiert; der Weg las zusaetzlich Spalten, die es dort nicht gibt.
SCHICHTEN = "domain_hr.shifts"
KOSTENSTELLEN = "domain_finance.kostenstellen"

#: Deckungsgleich mit ``shifts_status_ck`` der vorhandenen Schichttabelle.
SCHICHTSTAENDE = ("planned", "warning", "blocked", "cancelled")

#: Eine abgesagte Schicht plant keine Stunden.
SCHICHT_ABGESAGT = "cancelled"

#: Deckungsgleich mit ``ck_orgeinheit_art``.
EINHEITSARTEN = ("ABTEILUNG", "TEAM", "STANDORT", "KOSTENSTELLE", "GESCHAEFTSBEREICH")

#: Tiefengrenze der Baumrekursion. Ein Zyklus laeuft sonst endlos; wird die Grenze
#: erreicht, ist das ein Datenfehler und kein gekuerzter Baum.
MAX_TIEFE = 50

FELDER = (
    "id, tenant_id, unit_code, name, unit_type, parent_id, cost_center_id, "
    "manager_ref, aktiv, created_at, updated_at"
)

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (personal_organisation_zeitkonto_20261006)"
}


def nicht_lesbar(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Ein Lesefehler ist kein leeres Organigramm und kein Saldo von null.

    Ein Zeitkonto, das bei einer Stoerung null meldet, sagt dem Haus, es habe
    keine Ueberstunden zu bezahlen.
    """
    db.rollback()
    logger.exception("%s nicht lesbar (Mandant %s)", was, tenant_id)
    return HTTPException(
        status_code=503,
        detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
        headers=MIGRATIONS_HINWEIS,
    )


# ── Organigramm ─────────────────────────────────────────────────────────────


def baum_zeilen(db: Session, tenant_id: str, wurzel: Optional[str] = None) -> list[dict]:
    """Die Einheiten als flache Liste mit Tiefe — ab der Wurzel oder ab einer Einheit.

    Die Rekursion ist auf :data:`MAX_TIEFE` begrenzt. Wird die Grenze erreicht,
    liegt ein Zyklus vor; das meldet :func:`zyklus_pruefen`, statt einen
    gekuerzten Baum zu liefern. Ein Organigramm, das Teile stillschweigend
    weglaesst, ist schlimmer als eines, das sich beschwert.
    """
    bedingung = (
        "u.parent_id IS NULL" if wurzel is None else "u.id = :wurzel"
    )
    zeilen = db.execute(
        text(
            "WITH RECURSIVE baum AS ("
            f"    SELECT {FELDER}, 0 AS depth "  # nosec B608  # reviewed-safe: FELDER und Bedingung sind Code-Literale
            f"    FROM {EINHEITEN} u WHERE u.tenant_id = :tid AND {bedingung} "
            "    UNION ALL "
            "    SELECT u.id, u.tenant_id, u.unit_code, u.name, u.unit_type, u.parent_id, "
            "           u.cost_center_id, u.manager_ref, u.aktiv, u.created_at, u.updated_at, "
            "           b.depth + 1 "
            f"    FROM {EINHEITEN} u JOIN baum b ON u.parent_id = b.id "
            "    WHERE u.tenant_id = :tid AND b.depth < :max_tiefe"
            ") SELECT * FROM baum ORDER BY depth, name"
        ),
        {"tid": tenant_id, "wurzel": wurzel, "max_tiefe": MAX_TIEFE},
    ).mappings().fetchmany(5000)
    return [_als_dict(z) for z in zeilen]


def _als_dict(row: Any) -> dict:
    d = dict(row)
    for schluessel, wert in list(d.items()):
        if wert is not None and not isinstance(wert, (str, int, float, bool)):
            d[schluessel] = str(wert)
    return d


def zyklus_pruefen(zeilen: list[dict]) -> None:
    """Die Tiefengrenze erreicht heisst Zyklus — und das muss laut werden."""
    if any(int(z.get("depth") or 0) >= MAX_TIEFE for z in zeilen):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Das Organigramm ist mindestens {MAX_TIEFE} Ebenen tief. Das ist "
                "in aller Regel ein Zyklus in den Elternverweisen. Es wird kein "
                "gekuerzter Baum geliefert — die Zuordnung ist zu berichtigen."
            ),
        )


def baum_bauen(zeilen: list[dict], eltern: Optional[str]) -> list[dict]:
    """Aus der flachen Liste den verschachtelten Baum."""
    kinder = [dict(z) for z in zeilen if z.get("parent_id") == eltern]
    for kind in kinder:
        kind["children"] = baum_bauen(zeilen, kind["id"])
    return kinder


def kostenstelle_pruefen(db: Session, tenant_id: str, kostenstelle_id: Optional[str]) -> None:
    """Die Kostenstelle muss dem eigenen Mandanten gehoeren.

    Der Fremdschluessel allein kann das nicht sagen. Eine fremde Kostenstelle im
    Organigramm waere ein Auswertungsfehler, der wie eine Zuordnung aussieht.
    """
    if not kostenstelle_id:
        return
    vorhanden = db.execute(
        text(
            f"SELECT 1 FROM {KOSTENSTELLEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": kostenstelle_id, "tid": tenant_id},
    ).scalar()
    if not vorhanden:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Kostenstelle {kostenstelle_id!r} gehoert nicht zu diesem Mandanten "
                "oder existiert nicht."
            ),
        )


def eltern_pruefen(db: Session, tenant_id: str, eltern_id: Optional[str], eigene_id: str) -> None:
    """Die Elterneinheit muss dem Mandanten gehoeren und darf nicht man selbst sein."""
    if not eltern_id:
        return
    if eltern_id == eigene_id:
        raise HTTPException(
            status_code=422, detail="Eine Einheit ist nicht ihre eigene uebergeordnete Einheit."
        )
    vorhanden = db.execute(
        text(
            f"SELECT 1 FROM {EINHEITEN} WHERE id = :id AND tenant_id = :tid"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ),
        {"id": eltern_id, "tid": tenant_id},
    ).scalar()
    if not vorhanden:
        raise HTTPException(
            status_code=422,
            detail=f"Uebergeordnete Einheit {eltern_id!r} gehoert nicht zu diesem Mandanten.",
        )


def wuerde_zyklus(db: Session, tenant_id: str, einheit_id: str, neuer_eltern: str) -> bool:
    """Liegt die Einheit im Aufwaertspfad des neuen Elternteils?

    Beim Umhaengen entsteht der Zyklus **vor** dem Lesen — abweisen statt ihn
    spaeter als Tiefenfehler zu bemerken.
    """
    zeilen = db.execute(
        text(
            "WITH RECURSIVE aufwaerts AS ("
            f"    SELECT id, parent_id, 0 AS depth FROM {EINHEITEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "    WHERE id = :start AND tenant_id = :tid "
            "    UNION ALL "
            f"    SELECT u.id, u.parent_id, a.depth + 1 FROM {EINHEITEN} u "
            "    JOIN aufwaerts a ON u.id = a.parent_id "
            "    WHERE u.tenant_id = :tid AND a.depth < :max_tiefe"
            ") SELECT id FROM aufwaerts"
        ),
        {"start": neuer_eltern, "tid": tenant_id, "max_tiefe": MAX_TIEFE},
    ).scalars().fetchmany(MAX_TIEFE + 1)
    return einheit_id in {str(z) for z in zeilen}


# ── Arbeitszeitkonto ────────────────────────────────────────────────────────


def ist_stunden(db: Session, tenant_id: str, employee_ref: str) -> list[dict]:
    """Die Ist-Stunden je Monat aus den Zeiteintraegen."""
    zeilen = db.execute(
        text(
            "SELECT TO_CHAR(entry_date, 'YYYY-MM') AS monat, "
            "       COALESCE(SUM(hours), 0) AS stunden, COUNT(*) AS eintraege "
            f"FROM {ZEITEINTRAEGE} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE employee_ref = :ref AND tenant_id = :tid "
            "GROUP BY TO_CHAR(entry_date, 'YYYY-MM') ORDER BY monat"
        ),
        {"ref": employee_ref, "tid": tenant_id},
    ).mappings().fetchmany(600)
    return [
        {
            "monat": z["monat"],
            "actual_hours": float(z["stunden"] or 0),
            "eintraege": int(z["eintraege"] or 0),
        }
        for z in zeilen
    ]


def plan_stunden(db: Session, tenant_id: str, employee_ref: str) -> list[dict]:
    """Die Planstunden je Monat aus den **Schichten**.

    Vorher las dieser Weg ``SELECT SUM(planned_hours) FROM domain_hr.schichten``.
    Die Tabelle heisst `shifts` und hat keine dieser Spalten: Sie fuehrt
    `shift_date`, `starts_at`, `ends_at` als Uhrzeiten und
    `assigned_employee_refs` als JSONB-Liste. Der Verweis war also zweifach
    falsch — Name und Spalten.

    Gerechnet wird die Dauer aus den Uhrzeiten, und nur fuer Schichten, in deren
    Zuordnungsliste der Mitarbeiter steht. Eine ueber Mitternacht laufende
    Schicht zaehlt als Dauer bis zum naechsten Tag.
    """
    zeilen = db.execute(
        text(
            "SELECT TO_CHAR(shift_date, 'YYYY-MM') AS monat, "
            "       COALESCE(SUM("
            # Die Differenz zweier `time`-Werte ist ein Intervall; **auf** das
            # Intervall werden die 24 Stunden addiert. Eine Addition auf den
            # `time`-Wert selbst rechnet modulo 24 Stunden und ergaebe fuer eine
            # Nachtschicht ein negatives Ergebnis.
            "           EXTRACT(EPOCH FROM ("
            "               CASE WHEN ends_at >= starts_at THEN ends_at - starts_at "
            "                    ELSE (ends_at - starts_at) + INTERVAL '24 hours' END"
            "           )) / 3600.0"
            "       ), 0) AS stunden "
            f"FROM {SCHICHTEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE tenant_id = :tid AND starts_at IS NOT NULL AND ends_at IS NOT NULL "
            # Das Statuswoerterbuch der vorhandenen Tabelle ist englisch
            # (`shifts_status_ck`): planned, warning, blocked, cancelled.
            "  AND COALESCE(status, 'planned') <> 'cancelled' "
            "  AND assigned_employee_refs @> to_jsonb(ARRAY[:ref]::text[]) "
            "GROUP BY TO_CHAR(shift_date, 'YYYY-MM') ORDER BY monat"
        ),
        {"tid": tenant_id, "ref": employee_ref},
    ).mappings().fetchmany(600)
    return [
        {"monat": z["monat"], "planned_hours": round(float(z["stunden"] or 0), 2)}
        for z in zeilen
    ]


def korrekturen(db: Session, tenant_id: str, employee_ref: str) -> list[dict]:
    """Die Saldokorrekturen je Monat."""
    zeilen = db.execute(
        text(
            "SELECT TO_CHAR(adjustment_date, 'YYYY-MM') AS monat, "
            "       COALESCE(SUM(delta_hours), 0) AS stunden "
            f"FROM {KORREKTUREN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE employee_ref = :ref AND tenant_id = :tid "
            "GROUP BY TO_CHAR(adjustment_date, 'YYYY-MM') ORDER BY monat"
        ),
        {"ref": employee_ref, "tid": tenant_id},
    ).mappings().fetchmany(600)
    return [
        {"monat": z["monat"], "adjustment_hours": float(z["stunden"] or 0)} for z in zeilen
    ]


def zeitkonto(
    db: Session, tenant_id: str, employee_ref: str, jahr: Optional[int] = None
) -> dict:
    """Saldo, Uebertrag und Monatsaufstellung — jede Zahl genau einmal.

    Vorher ging die Korrektur **zweimal** ein: in ``saldo_hours`` und in
    ``transferred_from_prev_period``. Letzteres summierte ausserdem die
    Ist-Stunden aller Vorjahre; das ist kein Uebertrag, sondern eine Lebenssumme.

    Jetzt gilt:

    * **Uebertrag** = (Ist − Plan + Korrekturen) **aller Vorperioden**.
    * **laufende Periode** = (Ist − Plan + Korrekturen) des betrachteten Jahres.
    * **Saldo** = Uebertrag + laufende Periode.

    Damit ist der Saldo die Summe der beiden ausgewiesenen Zahlen — und jede
    Stunde steckt in genau einer von ihnen.
    """
    jahr = jahr or business_today().year
    monate: dict[str, dict] = {}
    for liste, feld in (
        (ist_stunden(db, tenant_id, employee_ref), "actual_hours"),
        (plan_stunden(db, tenant_id, employee_ref), "planned_hours"),
        (korrekturen(db, tenant_id, employee_ref), "adjustment_hours"),
    ):
        for eintrag in liste:
            ziel = monate.setdefault(
                eintrag["monat"],
                {
                    "monat": eintrag["monat"],
                    "actual_hours": 0.0,
                    "planned_hours": 0.0,
                    "adjustment_hours": 0.0,
                    "eintraege": 0,
                },
            )
            ziel[feld] = eintrag[feld]
            if "eintraege" in eintrag:
                ziel["eintraege"] = eintrag["eintraege"]

    aufstellung = []
    for monat in sorted(monate):
        zeile = monate[monat]
        zeile["saldo_hours"] = round(
            zeile["actual_hours"] - zeile["planned_hours"] + zeile["adjustment_hours"], 2
        )
        aufstellung.append(zeile)

    praefix = str(jahr)
    uebertrag = round(
        sum(z["saldo_hours"] for z in aufstellung if z["monat"] < f"{praefix}-01"), 2
    )
    laufend = round(
        sum(z["saldo_hours"] for z in aufstellung if z["monat"].startswith(praefix)), 2
    )
    spaeter = round(
        sum(z["saldo_hours"] for z in aufstellung if z["monat"] > f"{praefix}-12"), 2
    )
    return {
        "employee_ref": employee_ref,
        "jahr": jahr,
        "uebertrag_vorperioden": uebertrag,
        "saldo_laufende_periode": laufend,
        "saldo_folgeperioden": spaeter,
        "saldo_hours": round(uebertrag + laufend + spaeter, 2),
        "monate": aufstellung,
    }


def korrektur_schreiben(
    db: Session,
    tenant_id: str,
    korrektur_id: str,
    employee_ref: str,
    delta_hours: float,
    reason: str,
    adjustment_date: Any,
    erfasst_durch: Optional[str] = None,
) -> dict:
    """Eine Saldokorrektur festschreiben."""
    if not reason or not reason.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "Eine Korrektur am Zeitkonto braucht einen Grund. Ohne ihn ist die "
                "Aenderung nicht nachvollziehbar (§ 16 Abs. 2 ArbZG, GoBD Rz. 30 ff.)."
            ),
        )
    if not delta_hours:
        raise HTTPException(
            status_code=422, detail="Eine Korrektur um null Stunden ist keine Korrektur."
        )
    zeile = db.execute(
        text(
            f"INSERT INTO {KORREKTUREN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, employee_ref, delta_hours, reason, adjustment_date, erfasst_durch) "
            "VALUES (:id, :tid, :ref, :delta, :grund, :datum, :durch) "
            "RETURNING id, employee_ref, delta_hours, reason, adjustment_date"
        ),
        {
            "id": korrektur_id,
            "tid": tenant_id,
            "ref": employee_ref,
            "delta": Decimal(str(delta_hours)),
            "grund": reason.strip(),
            "datum": adjustment_date,
            "durch": erfasst_durch,
        },
    ).mappings().first()
    d = dict(zeile)
    d["delta_hours"] = float(d["delta_hours"])
    d["adjustment_date"] = (
        d["adjustment_date"].isoformat() if hasattr(d["adjustment_date"], "isoformat")
        else d["adjustment_date"]
    )
    return d
