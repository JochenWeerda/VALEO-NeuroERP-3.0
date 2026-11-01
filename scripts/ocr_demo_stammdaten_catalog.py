"""Pseudonym-Katalog + Seed-Plan aus OCR-Übungsfixtures (ADAPTIVE Demo).

Namen sind absichtlich modifiziert (Investor-/Stakeholder-Demo, keine 1:1-Realnamen).
Artikelnummern tragen Praefix DEMO-.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.documents.position_extraction import extract_table_line_items

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "evidence" / "ocr-training" / "fixtures"

# Quell-Hinweis → Demo-Lieferant (firmenname, lieferantennummer, ort)
SUPPLIER_PSEUDONYMS: dict[str, dict[str, str]] = {
    "broering": {
        "source_hint": "Bröring / Broering",
        "firmenname": "Nordwestdeutsche Futtermittel GmbH & Co. KG",
        "lieferantennummer": "DEMO-LF-NWF",
        "ort": "Dinklage",
        "fixture": "re_broering_vr1466078.ocr.txt",
    },
    "birkhoff": {
        "source_hint": "Kurt Birkhoff KG",
        "firmenname": "Wesel Agrarhandel KG",
        "lieferantennummer": "DEMO-LF-WAH",
        "ort": "Wesel",
        "fixture": "re_birkhoff_227627.ocr.txt",
    },
    "hofmeister": {
        "source_hint": "Hofmeister & Meincke / Granit",
        "firmenname": "Nordsee Ersatzteilvertrieb SE",
        "lieferantennummer": "DEMO-LF-NEV",
        "ort": "Bremen",
        "fixture": "re_hofmeister_3420010919.ocr.txt",
    },
    "telekom": {
        "source_hint": "Telekom Deutschland",
        "firmenname": "Magenta Netzservice GmbH",
        "lieferantennummer": "DEMO-LF-MNS",
        "ort": "Bonn",
        "fixture": "re_telekom_11769046012511.ocr.txt",
    },
    "deuka": {
        "source_hint": "deuka Tiernahrung Cremer",
        "firmenname": "Rheinische Mischfutter AG",
        "lieferantennummer": "DEMO-LF-RMF",
        "ort": "Duesseldorf",
        "fixture": "re_deuka_korrektur_600350.ocr.txt",
    },
    "zill": {
        "source_hint": "Zill GmbH & Co. KG",
        "firmenname": "Donau Silo Technik GmbH & Co. KG",
        "lieferantennummer": "DEMO-LF-DST",
        "ort": "Lauingen",
        "fixture": "re_zill_r2609060.ocr.txt",
    },
    "webfleet": {
        "source_hint": "Webfleet Solutions",
        "firmenname": "FleetLink Telematik GmbH",
        "lieferantennummer": "DEMO-LF-FLT",
        "ort": "Leipzig",
        "fixture": "re_webfleet_11857345.ocr.txt",
    },
    "dgo": {
        "source_hint": "DGO Agrar",
        "firmenname": "Oldenburger Pflanzenschutzgroßhandel GmbH",
        "lieferantennummer": "DEMO-LF-OPG",
        "ort": "Cloppenburg",
        "fixture": "re_dgo_10043771.ocr.txt",
    },
    "sica": {
        "source_hint": "Sica GmbH & Co. KG",
        "firmenname": "Ammerland Fachgroßhandel GmbH & Co. KG",
        "lieferantennummer": "DEMO-LF-AFG",
        "ort": "Westerstede",
        "fixture": "re_sica_26648052.ocr.txt",
    },
    "bat": {
        "source_hint": "BAT Agrar",
        "firmenname": "Holstein Saatgut GmbH & Co. KG",
        "lieferantennummer": "DEMO-LF-HSG",
        "ort": "Ratzeburg",
        "fixture": "re_bat_3569308.ocr.txt",
    },
    "folkerts_ls": {
        "source_hint": "Folkerts Landhandel (Ausgangs-LS Absender)",
        "firmenname": "Kuestenlandhandel Demo GmbH & Co. KG",
        "lieferantennummer": "DEMO-LF-KLD",
        "ort": "Krummhoern",
        "fixture": "ls_folkerts_2607001.ocr.txt",
        "role": "issuer_ls",
    },
    "holtrop": {
        "source_hint": "Holtrop-Meyer GbR (LS-Empfaenger)",
        "firmenname": "Marschenhof GbR",
        "lieferantennummer": "DEMO-KD-MH",
        "ort": "Krummhoern-Coldewehr",
        "fixture": "ls_folkerts_2607001.ocr.txt",
        "role": "customer",
    },
}

# Extra Hofmeister-3715 nutzt denselben Lieferanten-Schluessel
FIXTURE_SUPPLIER_KEY: dict[str, str] = {
    "re_broering_vr1466078.ocr.txt": "broering",
    "re_birkhoff_227627.ocr.txt": "birkhoff",
    "re_hofmeister_3420010919.ocr.txt": "hofmeister",
    "re_hofmeister_3715298017.ocr.txt": "hofmeister",
    "re_telekom_11769046012511.ocr.txt": "telekom",
    "re_deuka_korrektur_600350.ocr.txt": "deuka",
    "re_zill_r2609060.ocr.txt": "zill",
    "re_webfleet_11857345.ocr.txt": "webfleet",
    "re_dgo_10043771.ocr.txt": "dgo",
    "re_sica_26648052.ocr.txt": "sica",
    "re_bat_3569308.ocr.txt": "bat",
    "ls_folkerts_2607001.ocr.txt": "folkerts_ls",
}

_DEFAULT_UNIT = "t"
_DEFAULT_CATEGORY = "Sonstige"
_DEFAULT_SALES_PRICE = 0.0

_UNIT_MAP = {
    "kg": "kg",
    "t": "t",
    "stk": "Stk",
    "st": "Stk",
    "l": "l",
    "m": "M",
    "eh": "Eh",
    "x": "Stk",  # Dienstleistungseinheit → Stueck fuer Stamm
}

_CATEGORY_HINTS: list[tuple[tuple[str, ...], str]] = [
    (("mais", "weizen", "gerste", "raps", "rapsschrot", "futter", "pellet"), "Futtermittel"),
    (("ballet", "belkar", "carax", "durano", "architect"), "Pflanzenschutz"),
    (("saat", "colyseeo", "avantasia"), "Saatgut"),
    (("schlauch", "kupplung", "schelle", "stutzen", "blinddeckel"), "Technik"),
    (("fett", "spray", "multispray"), "Betriebsstoffe"),
    (("garten", "hacke", "gabel", "schere", "koeder", "maut", "anlieferung"), "Fachhandel"),
    (("nutzung", "navigation", "webfleet", "fleet"), "Telematik"),
    (("versand", "fracht"), "Dienstleistung"),
    (("hobel", "span"), "Einstreu"),
]


def _norm_unit(raw: str | None) -> str:
    if not raw:
        return _DEFAULT_UNIT
    key = raw.strip().casefold()
    return _UNIT_MAP.get(key, raw[:10] if len(raw) <= 10 else "Stk")


def _category_for(name: str) -> str:
    blob = name.casefold()
    for needles, cat in _CATEGORY_HINTS:
        if any(n in blob for n in needles):
            return cat
    return _DEFAULT_CATEGORY


def _demo_article_number(source_nr: str | None, name: str, seq: int) -> str:
    base = (source_nr or "").strip().upper().replace(" ", "")
    if base and len(base) <= 24:
        return f"DEMO-{base}"[:50]
    slug = "".join(ch if ch.isalnum() else "-" for ch in name.upper())[:20].strip("-")
    return f"DEMO-A{seq:03d}-{slug}"[:50]


def _truncate_name(name: str, limit: int = 100) -> str:
    text = " ".join(name.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def build_demo_seed_plan(
    fixtures_dir: Path | None = None,
) -> dict[str, Any]:
    """Liest Fixtures, baut idempotenten Plan (Lieferanten + Artikel)."""
    root = fixtures_dir or FIXTURES
    suppliers: dict[str, dict[str, Any]] = {}
    articles: dict[str, dict[str, Any]] = {}
    inbox_samples: list[dict[str, Any]] = []
    seq = 1

    for key, meta in SUPPLIER_PSEUDONYMS.items():
        if meta.get("role") == "customer":
            # Kunden als Lieferanten-Stamm nur wenn als Partner-Demo gewuenscht —
            # hier als eigener Lieferanteneintrag mit DEMO-KD- Praefix (Partner-Stamm-Proxy).
            pass
        suppliers[meta["lieferantennummer"]] = {
            "key": key,
            "source_hint": meta["source_hint"],
            "firmenname": meta["firmenname"],
            "lieferantennummer": meta["lieferantennummer"],
            "ort": meta.get("ort") or "",
            "land": "Deutschland",
            "notiz": f"OCR-Demo Pseudonym fuer {meta['source_hint']}",
        }

    for fixture_name, supplier_key in FIXTURE_SUPPLIER_KEY.items():
        path = root / fixture_name
        if not path.exists():
            continue
        ocr = path.read_text(encoding="utf-8")
        meta = SUPPLIER_PSEUDONYMS[supplier_key]
        rows = extract_table_line_items(ocr)
        positionen: list[dict[str, Any]] = []
        for row in rows:
            name = _truncate_name(str(row.get("artikel_name") or row.get("artikel_nr") or "Position"))
            src_nr = row.get("artikel_nr")
            art_nr = _demo_article_number(str(src_nr) if src_nr else None, name, seq)
            seq += 1
            unit = _norm_unit(str(row.get("einheit") or ""))
            price_raw = row.get("einzelpreis")
            try:
                sales_price = float(price_raw) if price_raw is not None else _DEFAULT_SALES_PRICE
                if sales_price < 0:
                    sales_price = abs(sales_price)
            except (TypeError, ValueError):
                sales_price = _DEFAULT_SALES_PRICE
            article = {
                "article_number": art_nr,
                "name": name,
                "unit": unit or _DEFAULT_UNIT,
                "category": _category_for(name),
                "sales_price": sales_price,
                "supplier_number": meta["lieferantennummer"],
                "source_fixture": fixture_name,
                "source_artikel_nr": src_nr,
            }
            # Dedup per article_number (gleiche DEMO-Nr aus mehreren Fixtures)
            if art_nr not in articles:
                articles[art_nr] = article
            positionen.append({
                "artikel_name": name,
                "artikel_nr": art_nr,
                "menge": row.get("menge"),
                "einheit": unit,
                "einzelpreis": price_raw,
            })

        # Inbox-Sample nur fuer Belege mit Positionen (Match-Demo)
        if positionen and supplier_key not in ("telekom",):
            inbox_samples.append({
                "fixture": fixture_name,
                "supplier_key": supplier_key,
                "supplier_name": meta["firmenname"],
                "supplier_nr": meta["lieferantennummer"],
                "invoice_number": f"DEMO-{path.stem.upper()[:24]}",
                "positionen": positionen[:8],
                "ocr_excerpt": (
                    f"{meta['firmenname']}\nLieferantennr.: {meta['lieferantennummer']}\n"
                    f"Rechnung DEMO\n"
                    + "\n".join(
                        f"{i+1} {p.get('artikel_nr')} {p['artikel_name']} "
                        f"{p.get('menge') or ''} {p.get('einheit') or ''}"
                        for i, p in enumerate(positionen[:5])
                    )
                ),
            })

    return {
        "suppliers": list(suppliers.values()),
        "articles": list(articles.values()),
        "inbox_samples": inbox_samples,
        "pseudonym_map": {
            m["source_hint"]: {
                "firmenname": m["firmenname"],
                "lieferantennummer": m["lieferantennummer"],
            }
            for m in SUPPLIER_PSEUDONYMS.values()
        },
    }
