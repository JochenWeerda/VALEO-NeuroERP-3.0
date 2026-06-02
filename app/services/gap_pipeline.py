"""GAP (Gemeinsame Agrarpolitik) ETL-Engine.

Reine, frameworkfreie Pipeline-Schritte, die die jährliche EU-Agrarfonds-
Begünstigtenliste (agrarzahlungen.de) in Potenzial-/Leaddaten überführen.
Aufgerufen von :mod:`app.services.gap_pipeline_service` (Background-Worker).

Schritte (vgl. ``docs/gap-annual-playbook.md``):
    1. import   – CSV → Tabelle ``gap_payments``
    2. aggregate – View ``gap_payments_direct_agg`` sicherstellen (Direktzahlungen)
    3. match    – Kunden ↔ Begünstigte abgleichen → ``gap_customer_match``
    4. snapshot – Potenzial/Segment je Kunde → ``customer_potential_snapshot``
    5. hydrate  – ``customers.analytics_*``-Spalten aktualisieren

Business-Formeln (Playbook §10/§11):
    geschätzte Fläche [ha] = Direktzahlung_EUR / GAP_EUR_PER_HA  (Default 270)
    Potenzial = Fläche * (Saatgut 50 + Dünger 150 + PSM 80) EUR/ha
    Share of Wallet [%] = Umsatz_Vorjahr / Potenzial_gesamt * 100
    Segment: A ≥ 80 %, B ≥ 40 %, C < 40 %

Schema-Quellen: ``database/analytics-gap.sql`` (gap_*-Tabellen + View),
``database/analytics-customer-fields.sql`` (customers.analytics_*),
``database/analytics-hydrate-customers.sql`` (Hydrate-UPDATE).
"""

from __future__ import annotations

import csv
import logging
import os
import re
from datetime import date
from pathlib import Path
from typing import Any, Callable, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

logger = logging.getLogger("gap.pipeline.engine")

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "gap"
SQL_DIR = BASE_DIR / "database"

# €/ha-Faktor zur Flächenschätzung aus Direktzahlungen (Playbook §11, env-überschreibbar).
EUR_PER_HA = float(os.getenv("GAP_EUR_PER_HA", "270") or "270")
# Potenzial-Komponenten je ha (Playbook §11).
POTENTIAL_SEED_PER_HA = float(os.getenv("GAP_POTENTIAL_SEED_PER_HA", "50") or "50")
POTENTIAL_FERT_PER_HA = float(os.getenv("GAP_POTENTIAL_FERT_PER_HA", "150") or "150")
POTENTIAL_PSM_PER_HA = float(os.getenv("GAP_POTENTIAL_PSM_PER_HA", "80") or "80")

# CSV-Spaltenindizes (agrarzahlungen.de „Gesamtliste der Begünstigten", semikolon-getrennt).
COL_YEAR = 0
COL_BENEFICIARY = 1
COL_PLZ = 4
COL_CITY = 5
COL_STATE = 6
COL_MEASURE = 7
COL_EGFL_ITEM = 11           # Betrag je Vorhaben EGFL
COL_ELER_ITEM = 13           # Betrag je Vorhaben ELER (EU-Mittel)
COL_NATIONAL_ITEM = 15       # Betrag je Vorhaben nationale Kofinanzierung

_INSERT_BATCH = 2000

ProgressCb = Optional[Callable[[str, int, str], None]]


# ── Helpers ───────────────────────────────────────────────────────────────────


def _emit(cb: ProgressCb, step: str, step_num: int, message: str) -> None:
    if cb is not None:
        try:
            cb(step, step_num, message)
        except Exception:  # noqa: BLE001 — Fortschritts-Reporting darf die Pipeline nie abbrechen
            logger.exception("[GAP] progress callback failed")


def _num(raw: Any) -> Optional[float]:
    """Parst einen Geldbetrag aus dem CSV (englisches oder deutsches Zahlenformat)."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if "," in s and "." in s:
        # Deutsches Format: 1.234,56 → Tausenderpunkt entfernen, Komma → Punkt
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    s = s.replace(" ", "").replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return None


_LEGAL_FORMS = {
    "gbr", "gmbh", "mbh", "kg", "ohg", "ag", "ug", "ek", "eg", "co", "cokg",
    "gmbhcokg", "ev", "se", "kgaa", "und", "u",
}


def normalize_name(name: Optional[str]) -> str:
    """Normalisiert einen Betriebs-/Begünstigtennamen für den Abgleich.

    Lowercase, Umlaute/ß entfaltet, Rechtsformen & Satzzeichen entfernt,
    Whitespace kollabiert. Muss bei Import (Begünstigte) und Match (Kunden)
    identisch angewandt werden.
    """
    if not name:
        return ""
    s = name.lower().strip()
    s = (
        s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    )
    s = re.sub(r"[^a-z0-9]+", " ", s)
    tokens = [t for t in s.split() if t and t not in _LEGAL_FORMS]
    return " ".join(tokens)


def tokenset(name: Optional[str]) -> str:
    """Reihenfolge-unabhängiger Namensschlüssel (sortierte normalisierte Tokens).

    Überbrückt unterschiedliche Namensreihenfolgen über Quellen hinweg
    (GAP „Nachname Vorname" ↔ CSV/Kundenstamm „Vorname Nachname",
    LKV „Nachname, Vorname"). Genutzt für Cross-Source-Matching.
    """
    return " ".join(sorted(normalize_name(name).split()))


def _plz_matches(plz: Optional[str], filters: Optional[list[str]]) -> bool:
    """True, wenn die PLZ einem der Filter-Tokens entspricht.

    Filter-Tokens: Präfix (``"49"``) oder numerischer Bereich (``"26500-26999"``).
    Ohne Filter immer True.
    """
    if not filters:
        return True
    if not plz:
        return False
    plz = plz.strip()
    for tok in filters:
        tok = tok.strip()
        if not tok:
            continue
        if "-" in tok:
            lo, _, hi = tok.partition("-")
            lo, hi = lo.strip(), hi.strip()
            if lo.isdigit() and hi.isdigit() and plz.isdigit():
                if int(lo) <= int(plz) <= int(hi):
                    return True
        elif plz.startswith(tok):
            return True
    return False


def _verify_header(header: Optional[list[str]], filename: str) -> None:
    """Plausibilisiert die CSV-Kopfzeile gegen das erwartete Positionslayout.

    Das Parsing erfolgt nach fester Spaltenposition (EU-Anhang-IX-Standard).
    Weicht das Layout ab (z.B. geändertes Portal-Format), wird laut gewarnt,
    damit kein stilles Fehl-Mapping passiert.
    """
    if not header:
        logger.warning("[GAP] %s: leere Kopfzeile.", filename)
        return
    n = len(header)
    plz_ok = n > COL_PLZ and "plz" in (header[COL_PLZ] or "").lower()
    measure_ok = n > COL_MEASURE and ("maßnahme" in (header[COL_MEASURE] or "").lower() or "massnahme" in (header[COL_MEASURE] or "").lower() or "code" in (header[COL_MEASURE] or "").lower())
    if n < 19 or not plz_ok or not measure_ok:
        logger.warning(
            "[GAP] %s: unerwartetes CSV-Layout (Spalten=%s, PLZ@%d ok=%s, Maßnahme@%d ok=%s). "
            "Spalten-Mapping per Position könnte falsch sein – bitte Header prüfen.",
            filename, n, COL_PLZ, plz_ok, COL_MEASURE, measure_ok,
        )


def _open_session(db: Optional[Session]) -> tuple[Session, bool]:
    """Liefert (session, owns). ``owns=True`` → Aufrufer muss schließen."""
    if db is not None:
        return db, False
    return SessionLocal(), True


def _table_exists(db: Session, name: str) -> bool:
    return db.execute(text("SELECT to_regclass(:n)"), {"n": name}).scalar() is not None


def _exec_sql_file(db: Session, sql_file: str) -> None:
    path = SQL_DIR / sql_file
    if not path.exists():
        logger.warning("[GAP] Schema-Datei fehlt: %s", path)
        return
    raw = path.read_text(encoding="utf-8")
    # Volltext-Kommentarzeilen entfernen, damit ein führender Kommentar nicht
    # das nachfolgende Statement (z.B. CREATE TABLE) mit verschluckt.
    # Inline-Kommentare (Code … -- Text) bleiben erhalten und sind in PostgreSQL gültig.
    cleaned = "\n".join(line for line in raw.splitlines() if not line.strip().startswith("--"))
    for statement in cleaned.split(";"):
        stmt = statement.strip()
        if stmt:
            db.execute(text(stmt))


def ensure_schema(db: Session) -> None:
    """Legt GAP-Tabellen + View idempotent an; erweitert ``customers`` nur, wenn vorhanden.

    Die ``gap_*``-Tabellen und der View gehören der GAP-Domäne und werden immer
    sichergestellt. Die ``customers.analytics_*``-Spalten werden nur ergänzt,
    wenn die ``customers``-Tabelle (Eigentum der Haupt-App/Migrationen) existiert.
    """
    _exec_sql_file(db, "analytics-gap.sql")
    if _table_exists(db, "customers"):
        _exec_sql_file(db, "analytics-customer-fields.sql")
    else:
        logger.warning("[GAP] Tabelle 'customers' fehlt – überspringe analytics_*-Spalten (Match/Hydrate liefern 0).")
    db.commit()


# ── Step 1: import ────────────────────────────────────────────────────────────


def run_import(
    year: int,
    csv_path: Optional[str] = None,
    batch_id: Optional[str] = None,
    progress_callback: ProgressCb = None,
    plz_filter: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Importiert die GAP-CSV eines Jahres nach ``gap_payments`` (idempotent je Jahr)."""
    path = Path(csv_path) if csv_path else (DATA_DIR / f"impdata{year}.csv")
    if not path.exists():
        raise FileNotFoundError(f"GAP-CSV nicht gefunden: {path}")

    load_batch = batch_id or str(uuid4())
    db, owns = _open_session(None)
    inserted = 0
    skipped = 0
    try:
        ensure_schema(db)
        _emit(progress_callback, "import", 1, f"Import startet: {path.name}")
        db.execute(text("DELETE FROM gap_payments WHERE ref_year = :year"), {"year": year})
        db.commit()

        insert_sql = text(
            """
            INSERT INTO gap_payments
              (ref_year, data_source, member_state, region_code, region_name,
               beneficiary_name_raw, beneficiary_name_norm, postal_code, city, country_code,
               measure_code, amount_egfl, amount_eler, amount_national_cofin, amount_total,
               load_batch_id, loaded_at)
            VALUES
              (:ref_year, :data_source, :member_state, NULL, NULL,
               :beneficiary_name_raw, :beneficiary_name_norm, :postal_code, :city, 'DE',
               :measure_code, :amount_egfl, :amount_eler, :amount_national_cofin, :amount_total,
               :load_batch_id, NOW())
            """
        )

        batch: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.reader(fh, delimiter=";", quotechar='"')
            header = next(reader, None)  # Kopfzeile
            _verify_header(header, path.name)
            for row in reader:
                if len(row) <= COL_MEASURE:
                    skipped += 1
                    continue
                plz = (row[COL_PLZ] or "").strip()
                if not _plz_matches(plz, plz_filter):
                    skipped += 1
                    continue
                name_raw = (row[COL_BENEFICIARY] or "").strip()
                if not name_raw:
                    skipped += 1
                    continue
                egfl = _num(row[COL_EGFL_ITEM]) if len(row) > COL_EGFL_ITEM else None
                eler = _num(row[COL_ELER_ITEM]) if len(row) > COL_ELER_ITEM else None
                national = _num(row[COL_NATIONAL_ITEM]) if len(row) > COL_NATIONAL_ITEM else None
                total = (egfl or 0) + (eler or 0) + (national or 0)
                batch.append(
                    {
                        "ref_year": year,
                        "data_source": path.name,
                        "member_state": (row[COL_STATE] or "DE").strip()[:2] or "DE",
                        "beneficiary_name_raw": name_raw,
                        "beneficiary_name_norm": normalize_name(name_raw),
                        "postal_code": plz or None,
                        "city": (row[COL_CITY] or "").strip() or None,
                        "measure_code": (row[COL_MEASURE] or "").strip() or None,
                        "amount_egfl": egfl,
                        "amount_eler": eler,
                        "amount_national_cofin": national,
                        "amount_total": total or None,
                        "load_batch_id": load_batch,
                    }
                )
                if len(batch) >= _INSERT_BATCH:
                    db.execute(insert_sql, batch)
                    db.commit()
                    inserted += len(batch)
                    batch.clear()
                    if inserted % (_INSERT_BATCH * 25) == 0:
                        _emit(progress_callback, "import", 1, f"{inserted:,} Zeilen importiert...")
        if batch:
            db.execute(insert_sql, batch)
            db.commit()
            inserted += len(batch)

        logger.info("[GAP] Import Jahr %s: %s Zeilen, %s übersprungen", year, inserted, skipped)
        return {"step": "import", "year": year, "inserted": inserted, "skipped": skipped, "batch_id": load_batch}
    finally:
        if owns:
            db.close()


# ── Step 2: aggregate ─────────────────────────────────────────────────────────


def run_aggregate(year: int, progress_callback: ProgressCb = None) -> dict[str, Any]:
    """Stellt den Direktzahlungs-View sicher (auto-aggregiert) und zählt Begünstigte."""
    db, owns = _open_session(None)
    try:
        ensure_schema(db)
        _emit(progress_callback, "aggregate", 2, "Aggregat-View aktualisiert")
        count = db.execute(
            text("SELECT COUNT(*) FROM gap_payments_direct_agg WHERE ref_year = :year"),
            {"year": year},
        ).scalar() or 0
        return {"step": "aggregate", "year": year, "beneficiaries": int(count)}
    finally:
        if owns:
            db.close()


# ── Step 3: match ─────────────────────────────────────────────────────────────


def run_match(year: int, progress_callback: ProgressCb = None) -> dict[str, Any]:
    """Gleicht Kunden gegen Begünstigte ab (Name normalisiert + PLZ) → gap_customer_match."""
    db, owns = _open_session(None)
    try:
        ensure_schema(db)
        if not _table_exists(db, "customers"):
            logger.warning("[GAP] Match übersprungen – Tabelle 'customers' fehlt.")
            return {"step": "match", "year": year, "matched": 0, "customers_scanned": 0, "skipped": "no customers table"}
        _emit(progress_callback, "match", 3, "Lade Begünstigten-Aggregat...")

        # Aggregat je (name_norm, PLZ) aus dem View aufbauen (identische Normalisierung wie Import).
        agg: dict[tuple[str, str], dict[str, Any]] = {}
        rows = db.execute(
            text(
                """
                SELECT beneficiary_name_norm, postal_code, city, SUM(direct_total_eur) AS direct_total
                FROM gap_payments_direct_agg
                WHERE ref_year = :year
                GROUP BY beneficiary_name_norm, postal_code, city
                """
            ),
            {"year": year},
        )
        for name_norm, plz, city, direct_total in rows:
            if not name_norm or not plz:
                continue
            key = (name_norm, plz.strip())
            entry = agg.setdefault(key, {"direct_total": 0.0, "city": city})
            entry["direct_total"] += float(direct_total or 0)

        _emit(progress_callback, "match", 3, "Gleiche Kunden ab...")
        customers = db.execute(
            text("SELECT id, name, postal_code, city FROM customers WHERE name IS NOT NULL")
        ).mappings().all()

        db.execute(text("DELETE FROM gap_customer_match WHERE ref_year = :year"), {"year": year})

        insert_sql = text(
            """
            INSERT INTO gap_customer_match
              (ref_year, customer_id, customer_name_norm, beneficiary_name_norm, postal_code, city,
               match_score, match_method, is_confident, status, gap_direct_total_eur, gap_estimated_area_ha)
            VALUES
              (:ref_year, :customer_id, :customer_name_norm, :beneficiary_name_norm, :postal_code, :city,
               :match_score, :match_method, TRUE, 'auto-match', :gap_direct_total_eur, :gap_estimated_area_ha)
            """
        )

        matches: list[dict[str, Any]] = []
        matched = 0
        for c in customers:
            plz = (c["postal_code"] or "").strip()
            name_norm = normalize_name(c["name"])
            if not plz or not name_norm:
                continue
            hit = agg.get((name_norm, plz))
            if not hit:
                continue
            direct_total = round(hit["direct_total"], 2)
            matches.append(
                {
                    "ref_year": year,
                    "customer_id": str(c["id"]),
                    "customer_name_norm": name_norm,
                    "beneficiary_name_norm": name_norm,
                    "postal_code": plz,
                    "city": c["city"] or hit.get("city"),
                    "match_score": 100.0,
                    "match_method": "exact_name_plz",
                    "gap_direct_total_eur": direct_total,
                    "gap_estimated_area_ha": round(direct_total / EUR_PER_HA, 2) if EUR_PER_HA else None,
                }
            )
            matched += 1
            if len(matches) >= _INSERT_BATCH:
                db.execute(insert_sql, matches)
                matches.clear()
        if matches:
            db.execute(insert_sql, matches)
        db.commit()

        logger.info("[GAP] Match Jahr %s: %s Kunden zugeordnet (von %s)", year, matched, len(customers))
        return {"step": "match", "year": year, "matched": matched, "customers_scanned": len(customers)}
    finally:
        if owns:
            db.close()


# ── Step 4: snapshot ──────────────────────────────────────────────────────────


def _segment_for_sow(sow_pct: Optional[float]) -> str:
    if sow_pct is None:
        return "C"
    if sow_pct >= 80:
        return "A"
    if sow_pct >= 40:
        return "B"
    return "C"


def run_snapshot(year: int, progress_callback: ProgressCb = None) -> dict[str, Any]:
    """Berechnet Potenzial/Segment je gematchtem Kunden → customer_potential_snapshot."""
    db, owns = _open_session(None)
    try:
        ensure_schema(db)
        if not _table_exists(db, "customers"):
            logger.warning("[GAP] Snapshot übersprungen – Tabelle 'customers' fehlt.")
            return {"step": "snapshot", "year": year, "snapshots": 0, "skipped": "no customers table"}
        _emit(progress_callback, "snapshot", 4, "Berechne Potenzial-Snapshots...")

        # Bestehender Umsatz (manuell gepflegt) je Kunde – Quelle für Share of Wallet.
        matches = db.execute(
            text(
                """
                SELECT m.customer_id,
                       m.gap_direct_total_eur,
                       m.gap_estimated_area_ha,
                       c.analytics_turnover_total_last_year_eur AS turnover
                FROM gap_customer_match m
                JOIN customers c ON c.id = m.customer_id
                WHERE m.ref_year = :year
                """
            ),
            {"year": year},
        ).mappings().all()

        db.execute(text("DELETE FROM customer_potential_snapshot WHERE ref_year = :year"), {"year": year})

        insert_sql = text(
            """
            INSERT INTO customer_potential_snapshot
              (ref_year, customer_id, gap_direct_total_eur, gap_estimated_area_ha,
               potential_seed_eur, potential_fertilizer_eur, potential_psm_eur, potential_total_eur,
               turnover_total_last_year_eur, share_of_wallet_total_pct, segment, potential_notes)
            VALUES
              (:ref_year, :customer_id, :gap_direct_total_eur, :gap_estimated_area_ha,
               :potential_seed_eur, :potential_fertilizer_eur, :potential_psm_eur, :potential_total_eur,
               :turnover, :sow, :segment, :notes)
            """
        )

        rows: list[dict[str, Any]] = []
        for m in matches:
            area = float(m["gap_estimated_area_ha"] or 0)
            seed = round(area * POTENTIAL_SEED_PER_HA, 2)
            fert = round(area * POTENTIAL_FERT_PER_HA, 2)
            psm = round(area * POTENTIAL_PSM_PER_HA, 2)
            total = round(seed + fert + psm, 2)
            turnover = float(m["turnover"]) if m["turnover"] is not None else None
            sow = round(turnover / total * 100, 2) if (turnover and total) else None
            rows.append(
                {
                    "ref_year": year,
                    "customer_id": str(m["customer_id"]),
                    "gap_direct_total_eur": m["gap_direct_total_eur"],
                    "gap_estimated_area_ha": m["gap_estimated_area_ha"],
                    "potential_seed_eur": seed,
                    "potential_fertilizer_eur": fert,
                    "potential_psm_eur": psm,
                    "potential_total_eur": total,
                    "turnover": turnover,
                    "sow": sow,
                    "segment": _segment_for_sow(sow),
                    "notes": f"Auto-Snapshot GAP {year} (Fläche {area:.1f} ha @ {EUR_PER_HA:.0f} EUR/ha)",
                }
            )
            if len(rows) >= _INSERT_BATCH:
                db.execute(insert_sql, rows)
                rows.clear()
        if rows:
            db.execute(insert_sql, rows)
        db.commit()

        count = len(matches)
        logger.info("[GAP] Snapshot Jahr %s: %s Snapshots", year, count)
        return {"step": "snapshot", "year": year, "snapshots": count}
    finally:
        if owns:
            db.close()


# ── Step 5: hydrate ───────────────────────────────────────────────────────────


def run_hydrate_customers(year: int, progress_callback: ProgressCb = None) -> dict[str, Any]:
    """Schreibt Snapshot-Werte in ``customers.analytics_*`` (Schutz-Flag respektiert)."""
    db, owns = _open_session(None)
    try:
        ensure_schema(db)
        if not _table_exists(db, "customers"):
            logger.warning("[GAP] Hydrate übersprungen – Tabelle 'customers' fehlt.")
            return {"step": "hydrate-customers", "year": year, "updated": 0, "skipped": "no customers table"}
        _emit(progress_callback, "hydrate-customers", 5, "Aktualisiere Kunden-Analytics...")
        result = db.execute(
            text(
                """
                UPDATE customers AS c
                SET
                  analytics_gap_ref_year = s.ref_year,
                  analytics_gap_direct_total_eur = s.gap_direct_total_eur,
                  analytics_gap_estimated_area_ha = s.gap_estimated_area_ha,
                  analytics_potential_seed_eur = s.potential_seed_eur,
                  analytics_potential_fertilizer_eur = s.potential_fertilizer_eur,
                  analytics_potential_psm_eur = s.potential_psm_eur,
                  analytics_potential_total_eur = s.potential_total_eur,
                  analytics_turnover_total_last_year_eur = s.turnover_total_last_year_eur,
                  analytics_share_of_wallet_total_pct = s.share_of_wallet_total_pct,
                  analytics_segment = s.segment,
                  analytics_potential_notes = s.potential_notes,
                  analytics_gap_last_sync_at = NOW(),
                  analytics_gap_last_sync_status = 'ok'
                FROM customer_potential_snapshot AS s
                WHERE s.ref_year = :year
                  AND s.customer_id = c.id
                  AND COALESCE(c.analytics_block_auto_potential_update, FALSE) = FALSE
                """
            ),
            {"year": year},
        )
        db.commit()
        updated = result.rowcount or 0
        logger.info("[GAP] Hydrate Jahr %s: %s Kunden aktualisiert", year, updated)
        return {"step": "hydrate-customers", "year": year, "updated": updated}
    finally:
        if owns:
            db.close()


# ── Download ──────────────────────────────────────────────────────────────────


# Stabiler Direktlink-Muster der Bundesanstalt für Landwirtschaft und Ernährung
# (agrarzahlungen.de). Verifiziert für 2023/2024/2025. Über env überschreibbar.
GAP_CSV_URL_TEMPLATE = os.getenv(
    "GAP_CSV_URL_TEMPLATE",
    "https://www.agrarzahlungen.de/fileadmin/afig-csv/impdata{year}.csv",
)


def latest_published_year(today: Optional[date] = None) -> int:
    """Letztes öffentlich verfügbares GAP-Haushaltsjahr.

    Die EU-Transparenzregel (Art. 98 VO (EU) 2021/2116) verpflichtet die
    Mitgliedstaaten, die Begünstigtenliste jährlich **bis zum 31. Mai** für das
    vorangegangene Haushaltsjahr (16.10.–15.10.) zu veröffentlichen. Nach dem
    31.5. ist daher das Vorjahr verfügbar, davor das Vor-Vorjahr.
    """
    today = today or date.today()
    may_31 = date(today.year, 5, 31)
    return today.year - 1 if today >= may_31 else today.year - 2


def download_gap_csv(year: int, force: bool = False) -> str:
    """Lädt die GAP-CSV eines Jahres von agrarzahlungen.de herunter (Streaming).

    Quelle: Bundesanstalt für Landwirtschaft und Ernährung, stabiles Direktlink-
    Muster ``…/fileadmin/afig-csv/impdata{year}.csv``. Die Datei ist sehr groß
    (>1 Mio. Datensätze) und wird daher gestreamt in ``data/gap/impdataYYYY.csv``
    geschrieben (atomar via temporärer Datei). Kleinstempfänger bis 1.250 EUR
    sind nach EU-Transparenzregeln nicht namentlich enthalten.

    Existiert die Datei bereits und ``force`` ist ``False``, wird ihr Pfad
    zurückgegeben (kein erneuter Download).
    """
    import httpx

    path = DATA_DIR / f"impdata{year}.csv"
    if path.exists() and not force:
        return str(path)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    url = GAP_CSV_URL_TEMPLATE.format(year=year)
    tmp = path.with_suffix(f".csv.part-{uuid4().hex[:8]}")
    logger.info("[GAP DOWNLOAD] Lade %s → %s", url, path)
    try:
        with httpx.stream(
            "GET",
            url,
            follow_redirects=True,
            timeout=httpx.Timeout(60.0, read=900.0),
            headers={"User-Agent": "VALEO-NeuroERP-GAP-Sync/1.0"},
        ) as resp:
            if resp.status_code == 404:
                raise RuntimeError(
                    f"GAP-CSV für {year} noch nicht veröffentlicht (HTTP 404 auf {url}). "
                    "Die Liste erscheint jährlich bis zum 31. Mai für das Vorjahr."
                )
            resp.raise_for_status()
            bytes_written = 0
            with open(tmp, "wb") as fh:
                for chunk in resp.iter_bytes(chunk_size=1 << 20):
                    fh.write(chunk)
                    bytes_written += len(chunk)
        tmp.replace(path)
        logger.info("[GAP DOWNLOAD] Fertig: %s (%.1f MB)", path, bytes_written / 1_048_576)
        return str(path)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def download_latest_gap_csv(force: bool = False) -> tuple[int, str]:
    """Lädt die CSV des aktuell verfügbaren Jahres herunter. Returns ``(year, path)``."""
    year = latest_published_year()
    return year, download_gap_csv(year, force=force)


# ── Orchestrierung ────────────────────────────────────────────────────────────


def run_year_pipeline(
    year: int,
    csv_path: Optional[str] = None,
    batch_id: Optional[str] = None,
    progress_callback: ProgressCb = None,
    plz_filter: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Führt die komplette Pipeline (import → aggregate → match → snapshot → hydrate) aus."""
    results: dict[str, Any] = {}

    # Import nur, wenn CSV vorhanden/auffindbar; sonst auf bereits importierten Daten aufsetzen.
    resolved_csv = csv_path
    if not resolved_csv:
        default_path = DATA_DIR / f"impdata{year}.csv"
        resolved_csv = str(default_path) if default_path.exists() else None

    if resolved_csv:
        results["import"] = run_import(
            year, csv_path=resolved_csv, batch_id=batch_id, progress_callback=progress_callback, plz_filter=plz_filter
        )
    else:
        _emit(progress_callback, "import", 1, "Kein CSV – überspringe Import, nutze vorhandene Daten")

    results["aggregate"] = run_aggregate(year, progress_callback=progress_callback)
    results["match"] = run_match(year, progress_callback=progress_callback)
    results["snapshot"] = run_snapshot(year, progress_callback=progress_callback)
    results["hydrate"] = run_hydrate_customers(year, progress_callback=progress_callback)
    return results
