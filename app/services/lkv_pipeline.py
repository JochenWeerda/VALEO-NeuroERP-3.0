"""LKV-Pipeline – Download der LKV-Weser-Ems-Jahresberichte (Milchleistungsprüfung).

Erste Stufe der Milchvieh-Datenquelle: lädt die jährlichen LKV-Jahresberichte
(PDF) von lkv-we.de herunter. Die Berichte enthalten Rangierungslisten mit
Betriebsname, PLZ, Ort und Herdenleistung (Milch kg, Fett+Eiweiß kg, Zellzahl,
Lebenstagsleistung) – Rohstoff für die spätere Tabellen-Extraktion und das
Matching gegen Kundenstammdaten (analog zur GAP-Pipeline, key = name_norm+PLZ).

Robustheit: Die konkreten PDF-URLs enthalten WordPress-spezifische Pfadteile
(interne ID, Upload-Monat), die sich jährlich ändern. Daher werden die Links
primär über die Downloadseite *entdeckt* (HTML-Scrape) und nur ersatzweise auf
ein bekanntes URL-Muster zurückgegriffen.

Quelle: https://lkv-we.de/downloads/
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from sqlalchemy import text

from app.core.database import SessionLocal

logger = logging.getLogger("lkv.pipeline")

BASE_DIR = Path(__file__).resolve().parents[2]
LKV_DATA_DIR = BASE_DIR / "data" / "lkv"
LKV_DOWNLOADS_URL = os.getenv("LKV_DOWNLOADS_URL", "https://lkv-we.de/downloads/")

# Dateinamen-Schlüsselwort (im PDF-Link) → kanonischer Regionsname.
LKV_REGION_KEYWORDS: dict[str, str] = {
    "hauptteil": "niedersachsen-gesamt",
    "elso": "emsland-suedoldenburg",
    "friesland": "friesland",
    "oldenburg": "oldenburg",
    "osnabrueck": "osnabrueck",
    "osnabrück": "osnabrueck",
}

# Für PLZ-26 relevante Regionen (Ostfriesland/Oldenburger Land).
DEFAULT_LKV_REGIONS = ["friesland", "oldenburg"]

# Bekanntes URL-Muster als Fallback, falls die Discovery (HTML-Scrape) nichts findet.
# Achtung: ID/Upload-Monat sind jahresspezifisch – nur Fallback, kein Primärpfad.
LKV_URL_FALLBACK_TEMPLATE = os.getenv(
    "LKV_URL_FALLBACK_TEMPLATE",
    "https://lkv-we.de/wp-content/uploads/sites/3/2026/01/4914_LKV_{region_file}{year}.pdf",
)
_FALLBACK_REGION_FILE = {
    "niedersachsen-gesamt": "Hauptteil",
    "emsland-suedoldenburg": "ELSO",
    "friesland": "Friesland",
    "oldenburg": "Oldenburg",
    "osnabrueck": "Osnabrueck",
}


def discover_lkv_report_urls(year: int) -> dict[str, str]:
    """Entdeckt die PDF-Links der Jahresberichte eines Jahres auf der Downloadseite.

    Returns ``{regionsname: url}``. Findet die Seite keine Links (z.B. geändertes
    Layout), bleibt das Dict leer und der Aufrufer nutzt den Fallback.
    """
    import httpx

    try:
        resp = httpx.get(
            LKV_DOWNLOADS_URL,
            follow_redirects=True,
            timeout=httpx.Timeout(30.0),
            headers={"User-Agent": "VALEO-NeuroERP-LKV-Sync/1.0"},
        )
        resp.raise_for_status()
    except Exception:  # noqa: BLE001 — Discovery best-effort; Fallback greift
        logger.exception("[LKV] Downloadseite nicht erreichbar: %s", LKV_DOWNLOADS_URL)
        return {}

    html = resp.text
    found: dict[str, str] = {}
    for raw in re.findall(r'href=["\']([^"\']+?\.pdf)["\']', html, flags=re.IGNORECASE):
        url = urljoin(LKV_DOWNLOADS_URL, raw)
        fname = url.rsplit("/", 1)[-1].lower()
        if str(year) not in fname:
            continue
        for keyword, region in LKV_REGION_KEYWORDS.items():
            if keyword in fname:
                found.setdefault(region, url)
                break
    if found:
        logger.info("[LKV] %d Berichte für %s entdeckt: %s", len(found), year, sorted(found))
    return found


def _resolve_url(year: int, region: str, discovered: dict[str, str]) -> Optional[str]:
    if region in discovered:
        return discovered[region]
    region_file = _FALLBACK_REGION_FILE.get(region)
    if region_file:
        return LKV_URL_FALLBACK_TEMPLATE.format(region_file=region_file, year=year)
    return None


def download_lkv_report(year: int, region: str, force: bool = False, discovered: Optional[dict[str, str]] = None) -> str:
    """Lädt den Jahresbericht einer Region herunter → ``data/lkv/lkv_{region}_{year}.pdf``."""
    import httpx

    region = region.lower()
    LKV_DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = LKV_DATA_DIR / f"lkv_{region}_{year}.pdf"
    if dest.exists() and not force:
        return str(dest)

    if discovered is None:
        discovered = discover_lkv_report_urls(year)
    url = _resolve_url(year, region, discovered)
    if not url:
        raise ValueError(f"Keine LKV-Region '{region}' bekannt. Verfügbar: {sorted(_FALLBACK_REGION_FILE)}")

    tmp = dest.with_suffix(".pdf.part")
    logger.info("[LKV] Lade %s (%s) → %s", url, region, dest)
    try:
        with httpx.stream(
            "GET", url, follow_redirects=True,
            timeout=httpx.Timeout(60.0, read=300.0),
            headers={"User-Agent": "VALEO-NeuroERP-LKV-Sync/1.0"},
        ) as resp:
            if resp.status_code == 404:
                raise RuntimeError(f"LKV-Bericht {region} {year} nicht gefunden (HTTP 404 auf {url}).")
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "")
            written = 0
            with open(tmp, "wb") as fh:
                for chunk in resp.iter_bytes(chunk_size=1 << 18):
                    fh.write(chunk)
                    written += len(chunk)
        # Plausibilität: PDF beginnt mit %PDF
        with open(tmp, "rb") as fh:
            head = fh.read(5)
        if not head.startswith(b"%PDF"):
            tmp.unlink(missing_ok=True)
            raise RuntimeError(
                f"Download von {url} ist kein PDF (Content-Type '{ctype}', Beginn {head!r}). "
                "Vermutlich Layout-/URL-Änderung – Downloadseite prüfen."
            )
        tmp.replace(dest)
        logger.info("[LKV] Fertig: %s (%.1f MB)", dest, written / 1_048_576)
        return str(dest)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def download_lkv_reports(
    year: int, regions: Optional[list[str]] = None, force: bool = False
) -> dict[str, str]:
    """Lädt mehrere Regionsberichte. Default = PLZ-26-relevante (Friesland, Oldenburg)."""
    regions = regions or DEFAULT_LKV_REGIONS
    discovered = discover_lkv_report_urls(year)
    results: dict[str, str] = {}
    for region in regions:
        try:
            results[region.lower()] = download_lkv_report(year, region, force=force, discovered=discovered)
        except Exception as exc:  # noqa: BLE001 — einzelne Region darf den Rest nicht stoppen
            logger.error("[LKV] Download %s %s fehlgeschlagen: %s", region, year, exc)
            results[region.lower()] = f"ERROR: {exc}"
    return results


# ── Extraktion: „Die höchsten Herdendurchschnittsleistungen" ──────────────────

# Titel der Herdenmittel-Ranking-Tabelle – variiert je Regionalbericht.
TARGET_SECTIONS = (
    "Die höchsten Herdendurchschnittsleistungen",  # Friesland u.a.
    "Die höchsten Herdenleistungen",               # Oldenburg
)
TARGET_SECTION = TARGET_SECTIONS[0]  # Rückwärtskompatibilität
# Eine Abschnittsüberschrift im Bericht beginnt mit „Die höchsten/besten/Leistungen …".
# Damit wird die Zielsektion sauber begrenzt (kein Bleed in 305-Tage-/Lebensleistungs-
# Tabellen, die einzelne Kühe statt Herdenmittel listen).
_SECTION_HDR_RE = re.compile(r"^Die\s+(h[öo]chsten|besten|Leistungen)\b", re.IGNORECASE)

# Eine vollständige Datenzeile, an den exakten Spaltenformaten verankert:
#   "12. Nachname, Vorname 26506 Ort-Teil 65,7 12.549 4,81 604 3,30 414 1.018"
#   rank  besitzer          PLZ   Ort      Alter Milch  Fett% Fkg Eiw% Ekg F+E
# finditer statt match, weil pdfplumber gelegentlich die linke und rechte
# Berichtsspalte (zwei Betriebe) in EINE Textzeile zusammenzieht.
_ROW_FULL = re.compile(
    r"(\d{1,3})\.\s+"                 # 1 Rang
    r"(.+?)\s+"                       # 2 Besitzer (non-greedy)
    r"(\d{5})\s+"                     # 3 PLZ
    r"(.+?)\s+"                       # 4 Ort (non-greedy, stoppt am Alter)
    r"(\d{1,3},\d)\s+"               # 5 Alter (xx,x)
    r"(\d{1,2}\.\d{3}|\d{4,5})\s+"   # 6 Milch kg
    r"(\d,\d{2})\s+"                 # 7 Fett %
    r"(\d{2,4})\s+"                  # 8 Fett kg
    r"(\d,\d{2})\s+"                 # 9 Eiw %
    r"(\d{2,4})\s+"                  # 10 Eiw kg
    r"(\d\.\d{3}|\d{3,4})"           # 11 Fett+Eiweiß kg (Friesland '1.021', Oldenburg '1021')
)
# Variante ohne PLZ (z.B. Oldenburg): "1. Besitzer, Wohnort 58,6 10.028 4,16 417 3,50 351 768"
# Besitzer und Wohnort sind komma-getrennt (letztes Komma trennt); keine PLZ-Spalte.
_ROW_NOPLZ = re.compile(
    r"(\d{1,3})\.\s+"                 # 1 Rang
    r"(.+?)\s+"                       # 2 Besitzer + Wohnort (letztes Komma trennt)
    r"(\d{1,3},\d)\s+"               # 3 Alter
    r"(\d{1,2}\.\d{3}|\d{4,5})\s+"   # 4 Milch kg
    r"(\d,\d{2})\s+"                 # 5 Fett %
    r"(\d{2,4})\s+"                  # 6 Fett kg
    r"(\d,\d{2})\s+"                 # 7 Eiw %
    r"(\d{2,4})\s+"                  # 8 Eiw kg
    r"(\d\.\d{3}|\d{3,4})"           # 9 Fett+Eiweiß kg (mit/ohne Tausenderpunkt)
)
_GROUP_RE = re.compile(r"^\s*Gruppe\s+([\d,\.\s-]+?)\s*Kühe", re.IGNORECASE)


def _de_num(s: str) -> Optional[float]:
    """Deutsches Zahlenformat: '12.549'→12549, '4,81'→4.81, '1.018'→1018, '65,7'→65.7."""
    s = (s or "").strip()
    if not s:
        return None
    try:
        return float(s.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def extract_herd_performance(
    pdf_path: str,
    region: str,
    year: int,
    section_titles: tuple[str, ...] = TARGET_SECTIONS,
) -> list[dict]:
    """Parst die Tabelle „Die höchsten Herdendurchschnittsleistungen" aus einem LKV-PDF.

    Returns je Betrieb ein Dict: besitzer_raw, name_norm, postal_code, ort,
    herd_size_group, alter, milch_kg, fett_pct, fett_kg, eiw_pct, eiw_kg,
    fett_eiweiss_kg (+ region, ref_year). Zeilenbasiert (PLZ als Anker, die
    letzten 7 Tokens = Zahlenspalten); ``extract_tables`` ist hier unbrauchbar.
    """
    import pdfplumber

    from app.services.gap_pipeline import normalize_name

    rows: list[dict] = []
    seen: set[tuple] = set()
    in_section = False
    current_group: Optional[str] = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for line in (page.extract_text() or "").splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                # Abschnittsüberschrift: aktiviert die Zielsektion nur, wenn sie einen
                # Zieltitel trägt – jede andere „Die …"-Überschrift beendet sie.
                if _SECTION_HDR_RE.match(stripped):
                    in_section = any(t in stripped for t in section_titles)
                    continue
                if not in_section:
                    continue
                if stripped.startswith("Nr. ") or stripped.startswith("Nr.\t"):
                    continue  # Spaltenkopf
                gm = _GROUP_RE.match(stripped)
                if gm:
                    current_group = gm.group(1).strip() + " Kühe"
                    continue
                # finditer: je Textzeile können (selten) zwei Betriebe stehen.
                # Layout A (mit PLZ, z.B. Friesland) hat Vorrang; sonst Layout B ohne PLZ.
                parsed: list[tuple] = []
                for m in _ROW_FULL.finditer(stripped):
                    besitzer, plz, ort = m.group(2, 3, 4)
                    parsed.append((besitzer, plz, ort, *m.group(5, 6, 7, 8, 9, 10, 11)))
                if not parsed:
                    for m in _ROW_NOPLZ.finditer(stripped):
                        combined = m.group(2)
                        if "," in combined:
                            besitzer, ort = (p.strip() for p in combined.rsplit(",", 1))
                        else:
                            besitzer, ort = combined.strip(), ""
                        parsed.append((besitzer, None, ort, *m.group(3, 4, 5, 6, 7, 8, 9)))

                for besitzer, plz, ort, alter, milch, fett_pct, fett_kg, eiw_pct, eiw_kg, fe_kg in parsed:
                    # Ortsnamen enthalten keine Ziffern – Ziffern im Ort signalisieren eine
                    # zeichenweise verschränkte Doppelspalte (pdfplumber-Artefakt) → verwerfen.
                    if re.search(r"\d", ort):
                        continue
                    # Dedup: identische Herdenmittel-Zeilen erscheinen layoutbedingt
                    # mehrfach (gleiche Tabelle auf Folgeseiten wiederholt).
                    dkey = (normalize_name(besitzer), plz, ort.strip(), _de_num(milch), _de_num(fe_kg))
                    if dkey in seen:
                        continue
                    seen.add(dkey)
                    rows.append(
                        {
                            "region": region,
                            "ref_year": year,
                            "besitzer_raw": besitzer.strip(),
                            "name_norm": normalize_name(besitzer),
                            "postal_code": plz,
                            "ort": ort.strip(),
                            "herd_size_group": current_group,
                            "alter": _de_num(alter),
                            "milch_kg": _de_num(milch),
                            "fett_pct": _de_num(fett_pct),
                            "fett_kg": _de_num(fett_kg),
                            "eiw_pct": _de_num(eiw_pct),
                            "eiw_kg": _de_num(eiw_kg),
                            "fett_eiweiss_kg": _de_num(fe_kg),
                        }
                    )
    logger.info("[LKV] %s %s: %d Herden extrahiert", region, year, len(rows))
    return rows


# ── Ort→PLZ-Auflösung (Variante a: via GAP-Gemeinde-Mapping) ──────────────────


def _gemeinde_key(value: Optional[str]) -> str:
    """Normalisiert einen Orts-/Gemeindenamen auf die Gemeinde (vor Ortsteil/Zusatz).

    „Wardenburg-Benthullen" → „wardenburg"; „Jever, Stadt" → „jever";
    „Bad Zwischenahn" → „bad zwischenahn".
    """
    if not value:
        return ""
    s = value.lower().strip()
    s = s.split(",")[0]      # „Jever, Stadt" → „jever"
    s = s.split("-")[0]      # „Wardenburg-Benthullen" → „wardenburg"
    return s.strip()


def build_city_plz_map(db) -> dict[str, str]:
    """Baut aus ``gap_payments`` ein ``{gemeinde_key: häufigste_PLZ}``-Mapping."""
    from collections import defaultdict

    rows = db.execute(
        text(
            """
            SELECT city, postal_code, COUNT(*) AS c
            FROM gap_payments
            WHERE city IS NOT NULL AND postal_code IS NOT NULL AND postal_code <> ''
            GROUP BY city, postal_code
            """
        )
    ).all()
    tally: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for city, plz, c in rows:
        tally[_gemeinde_key(city)][plz] += int(c)
    return {g: max(plzs, key=plzs.get) for g, plzs in tally.items() if g}


def resolve_postal_codes(rows: list[dict], city_plz_map: dict[str, str]) -> dict[str, int]:
    """Ergänzt fehlende PLZ (Oldenburg) über die Gemeinde. Mutiert ``rows`` in-place.

    Setzt ``postal_code_source`` = 'pdf' | 'resolved_gemeinde' | 'unresolved'.
    Returns Statistik-Dict.
    """
    stats = {"pdf": 0, "resolved_gemeinde": 0, "unresolved": 0}
    for r in rows:
        if r.get("postal_code"):
            r["postal_code_source"] = "pdf"
            stats["pdf"] += 1
            continue
        plz = city_plz_map.get(_gemeinde_key(r.get("ort")))
        if plz:
            r["postal_code"] = plz
            r["postal_code_source"] = "resolved_gemeinde"
            stats["resolved_gemeinde"] += 1
        else:
            r["postal_code_source"] = "unresolved"
            stats["unresolved"] += 1
    return stats


# ── Persistenz ────────────────────────────────────────────────────────────────


def ensure_lkv_schema(db) -> None:
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS dairy_herd_performance (
                id                BIGSERIAL PRIMARY KEY,
                ref_year          SMALLINT     NOT NULL,
                region            TEXT         NOT NULL,
                besitzer_raw      TEXT         NOT NULL,
                name_norm         TEXT         NOT NULL,
                postal_code       TEXT,
                postal_code_source TEXT,
                ort               TEXT,
                herd_size_group   TEXT,
                alter_monate      NUMERIC(5,1),
                milch_kg          NUMERIC(8,1),
                fett_pct          NUMERIC(4,2),
                fett_kg           NUMERIC(7,1),
                eiw_pct           NUMERIC(4,2),
                eiw_kg            NUMERIC(7,1),
                fett_eiweiss_kg   NUMERIC(7,1),
                loaded_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_dairy_year ON dairy_herd_performance (ref_year)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_dairy_name_plz ON dairy_herd_performance (name_norm, postal_code)"))
    db.commit()


def persist_herd_performance(db, rows: list[dict], region: str, year: int) -> int:
    """Schreibt extrahierte Herden (idempotent je region+year). Returns Anzahl."""
    ensure_lkv_schema(db)
    db.execute(
        text("DELETE FROM dairy_herd_performance WHERE ref_year = :y AND region = :r"),
        {"y": year, "r": region},
    )
    if rows:
        db.execute(
            text(
                """
                INSERT INTO dairy_herd_performance
                  (ref_year, region, besitzer_raw, name_norm, postal_code, postal_code_source,
                   ort, herd_size_group, alter_monate, milch_kg, fett_pct, fett_kg, eiw_pct, eiw_kg, fett_eiweiss_kg)
                VALUES
                  (:ref_year, :region, :besitzer_raw, :name_norm, :postal_code, :postal_code_source,
                   :ort, :herd_size_group, :alter, :milch_kg, :fett_pct, :fett_kg, :eiw_pct, :eiw_kg, :fett_eiweiss_kg)
                """
            ),
            [{**r, "postal_code_source": r.get("postal_code_source")} for r in rows],
        )
    db.commit()
    return len(rows)


def run_lkv_import(
    year: int, regions: Optional[list[str]] = None, force_download: bool = False
) -> dict:
    """Voll-Pipeline: Download (falls nötig) → Extraktion → Ort→PLZ → Persistenz."""
    regions = regions or DEFAULT_LKV_REGIONS
    db = SessionLocal()
    result: dict = {"year": year, "regions": {}}
    try:
        city_plz_map = build_city_plz_map(db)
        result["gemeinde_mapping_size"] = len(city_plz_map)
        for region in regions:
            region = region.lower()
            try:
                pdf_path = download_lkv_report(year, region, force=force_download)
                rows = extract_herd_performance(pdf_path, region, year)
                res_stats = resolve_postal_codes(rows, city_plz_map)
                count = persist_herd_performance(db, rows, region, year)
                result["regions"][region] = {"herds": count, "plz_resolution": res_stats}
            except Exception as exc:  # noqa: BLE001 — eine Region darf den Rest nicht stoppen
                logger.exception("[LKV] Import %s %s fehlgeschlagen", region, year)
                result["regions"][region] = {"error": str(exc)}
    finally:
        db.close()
    return result


# ── Match dairy → Kundenstamm ─────────────────────────────────────────────────
# Der Kundenmatch läuft ausschließlich über die kanonische Zugriffsschicht
# (build_customer_match_lookup), die BP-Identität + public.kunden + Adress-
# Satellit vereint. Kein Roh-SQL / keine env-konfigurierte Kundenstammquelle mehr.


def build_kunden_lookup(db) -> dict[tuple, str]:
    """{(tokenset(name), plz): kunden_handle} für den Kundenmatch.

    Delegiert an die kanonische Zugriffsschicht
    (:func:`app.services.business_partner_service.build_customer_match_lookup`),
    die Business-Partner-Identität (SoR) **und** ``public.kunden`` vereint. Der
    Handle bevorzugt die stabile ``business_partner_id`` (sonst partner_number /
    kunden_nr). Kein Roh-SQL auf Kundentabellen mehr hier (Stammdaten-Konsolidierung).
    """
    from app.services.business_partner_service import build_customer_match_lookup, resolve_customer_ref

    unified = build_customer_match_lookup(db)
    return {key: ref for key, entry in unified.items() if (ref := resolve_customer_ref(entry))}


def ensure_dairy_match_schema(db) -> None:
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS dairy_kunden_match (
                id              BIGSERIAL PRIMARY KEY,
                ref_year        SMALLINT     NOT NULL,
                kunden_nr       TEXT         NOT NULL,
                region          TEXT,
                dairy_besitzer  TEXT,
                name_norm       TEXT,
                postal_code     TEXT,
                milch_kg        NUMERIC(8,1),
                fett_eiweiss_kg NUMERIC(7,1),
                herd_size_group TEXT,
                match_method    TEXT,
                matched_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_dkm_kunde ON dairy_kunden_match (kunden_nr, ref_year)"))
    db.commit()


def match_dairy_to_kunden(db=None, year: int = 2025) -> dict:
    """Matcht ``dairy_herd_performance`` gegen den Kundenstamm (name+PLZ) → dairy_kunden_match.

    Token-Set-Match (Namensreihenfolge-unabhängig) + PLZ. Idempotent je Jahr.
    """
    from app.services.gap_pipeline import tokenset

    owns = db is None
    db = db or SessionLocal()
    try:
        ensure_dairy_match_schema(db)
        kunden = build_kunden_lookup(db)
        if not kunden:
            return {"year": year, "matched": 0, "scanned": 0, "kunden": 0, "skipped": "kein Kundenstamm"}

        herds = db.execute(
            text(
                """
                SELECT region, besitzer_raw, name_norm, postal_code, milch_kg, fett_eiweiss_kg, herd_size_group
                FROM dairy_herd_performance
                WHERE ref_year = :y AND postal_code IS NOT NULL
                """
            ),
            {"y": year},
        ).mappings().all()

        db.execute(text("DELETE FROM dairy_kunden_match WHERE ref_year = :y"), {"y": year})
        insert_sql = text(
            """
            INSERT INTO dairy_kunden_match
              (ref_year, kunden_nr, region, dairy_besitzer, name_norm, postal_code,
               milch_kg, fett_eiweiss_kg, herd_size_group, match_method)
            VALUES
              (:ref_year, :kunden_nr, :region, :dairy_besitzer, :name_norm, :postal_code,
               :milch_kg, :fett_eiweiss_kg, :herd_size_group, 'tokenset_plz')
            """
        )
        matched = 0
        for h in herds:
            kn = kunden.get((tokenset(h["name_norm"]), str(h["postal_code"]).strip()))
            if not kn:
                continue
            db.execute(
                insert_sql,
                {
                    "ref_year": year,
                    "kunden_nr": kn,
                    "region": h["region"],
                    "dairy_besitzer": h["besitzer_raw"],
                    "name_norm": h["name_norm"],
                    "postal_code": h["postal_code"],
                    "milch_kg": h["milch_kg"],
                    "fett_eiweiss_kg": h["fett_eiweiss_kg"],
                    "herd_size_group": h["herd_size_group"],
                },
            )
            matched += 1
        db.commit()
        logger.info("[KUNDEN] dairy→kunden %s: %s von %s Herden gematcht (%s Kunden)", year, matched, len(herds), len(kunden))
        return {"year": year, "matched": matched, "scanned": len(herds), "kunden": len(kunden)}
    finally:
        if owns:
            db.close()


if __name__ == "__main__":
    import argparse
    import json

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="LKV-Jahresberichte (PDF) herunterladen.")
    parser.add_argument("--year", type=int, default=2025, help="Berichtsjahr (Default 2025)")
    parser.add_argument("--regions", type=str, default=None, help="Komma-Liste, z.B. 'friesland,oldenburg' (Default)")
    parser.add_argument("--force", action="store_true", help="Erneut laden, auch wenn vorhanden")
    args = parser.parse_args()
    regs = [r.strip() for r in args.regions.split(",")] if args.regions else None
    out = download_lkv_reports(args.year, regions=regs, force=args.force)
    print(json.dumps(out, indent=2, ensure_ascii=False))
