"""Mischfutter-Etikettenauswertung: OCR/PDF -> Struktur + Optimizer-Feed.

Extrahiert 2026-04-23 aus ``rations_optimization.py`` (Refactor
Schritt 1e). Die Logik ist verhaltensidentisch; einziger Unterschied
ist, dass ``parse_compound_feed_text`` jetzt einen
``feeds_provider``-Callable erwartet, um die DLG-Referenzdatenbank
ohne Zirkelimport verfuegbar zu machen.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi import HTTPException

from .models import (
    CompoundFeedComponent,
    CompoundFeedDeclaredAnalysis,
    CompoundFeedGfeEstimate,
    CompoundFeedParsed,
)

# ---------------------------------------------------------------------------
# Matcher-Regeln: normalisierter Token-Satz -> DLG-Feed-ID
# ---------------------------------------------------------------------------
COMPOUND_FEED_MATCHERS: List[Tuple[Tuple[str, ...], str]] = [
    (("mais", "korn"), "dlg_30880030"),
    (("mais",), "dlg_30880030"),
    (("gerste",), "dlg_30820030"),
    (("weizenkleie",), "dlg_31210030"),
    (("weizengriesskleie",), "dlg_31230030"),
    (("weizen",), "dlg_31190030"),
    (("melasseschnitzel",), "dlg_30940030"),
    (("ruebenmelasse",), "dlg_41290030"),
    (("melasse",), "dlg_41290030"),
    (("rapsextraktionsschrot", "thermisch"), "dlg_30980130"),
    (("rapsextraktionsschrot",), "dlg_30970130"),
    (("sojaextraktionsschrot", "geschaelter saat"), "dlg_31060030"),
    (("sojaextraktionsschrot", "geschalter saat"), "dlg_31060030"),
    (("sojaextraktionsschrot",), "dlg_31050130"),
    (("haferschaelkleie",), "dlg_30850030"),
    (("haferschalkleie",), "dlg_30850030"),
    (("hafer",), "dlg_30840030"),
]


# ---------------------------------------------------------------------------
# String-Helpers
# ---------------------------------------------------------------------------
def ascii_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "custom-feed"


def normalize_feed_label(value: str) -> str:
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "é": "e",
        "è": "e",
    }
    normalized = value.lower()
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    normalized = normalized.replace("&", " und ")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


def parse_localized_float(raw: str) -> Optional[float]:
    candidate = (
        raw.strip().replace(" ", "").replace("%", "").replace("mj", "").replace("kg", "")
    )
    candidate = candidate.replace(",", ".")
    try:
        return float(candidate)
    except (TypeError, ValueError):
        return None


def extract_value(text: str, pattern: str) -> Optional[float]:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return parse_localized_float(match.group(1))


def extract_labelled_value(text: str, label: str, suffix_pattern: str) -> Optional[float]:
    """Liest einen beschrifteten Deklarationswert aus einem Etikett.

    Wichtig: das "Label zuerst"-Muster muss vor dem "Wert zuerst"-Muster
    stehen. In Fliesstexten wie
        "Rohprotein 16,50 % Rohfett 2,80 % Rohasche 4,00 %"
    wuerde das inverse Muster (Zahl vor Label) sonst fuer "Rohfett" die
    16,5 aus "Rohprotein" zurueckgeben (Off-by-one-Verschub ueber die
    Inhaltsstoff-Liste). Das hat zuvor zu stark verfaelschten Werten
    gefuehrt (Ca = 7,2% statt 0,28%, XL = 165 g/kg statt 31 g/kg).
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if label.lower() not in line.lower():
            continue
        patterns = [
            rf"{label}\s*[:=]?\s*([0-9]+[.,][0-9]+)\s*{suffix_pattern}",
            rf"([0-9]+[.,][0-9]+)\s*{suffix_pattern}\s*{label}",
        ]
        for pattern in patterns:
            value = extract_value(line, pattern)
            if value is not None:
                return value
    compact_patterns = [
        rf"{label}\s*[:=]?\s*([0-9]+[.,][0-9]+)\s*{suffix_pattern}",
        rf"([0-9]+[.,][0-9]+)\s*{suffix_pattern}\s*{label}",
    ]
    for pattern in compact_patterns:
        value = extract_value(text, pattern)
        if value is not None:
            return value
    return None


def extract_document_text(
    filename: str, content: bytes
) -> Tuple[str, str, List[str]]:
    suffix = Path(filename).suffix.lower()
    warnings: List[str] = []
    if suffix == ".pdf":
        try:
            import io as _io

            import pdfplumber

            with pdfplumber.open(_io.BytesIO(content)) as pdf:
                text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        except ImportError as exc:
            raise HTTPException(503, f"PDF-Parsing nicht verfuegbar: {exc}")
        except Exception as exc:
            raise HTTPException(422, f"PDF konnte nicht gelesen werden: {exc}")
        if not text.strip():
            raise HTTPException(
                422,
                "Das PDF enthaelt keinen Textlayer. Bitte Lieferschein als Foto/JPG/PNG hochladen.",
            )
        return text, "pdf_text", warnings
    if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
        raise HTTPException(400, "Nur PDF- oder Bilddateien (PNG/JPG/WebP/TIFF) erlaubt")
    try:
        from io import BytesIO

        from PIL import Image
        import pytesseract

        image = Image.open(BytesIO(content))
        text = pytesseract.image_to_string(image, lang="deu+eng")
    except ImportError as exc:
        raise HTTPException(503, f"OCR nicht verfuegbar: {exc}")
    except Exception as exc:
        raise HTTPException(422, f"Bild konnte nicht via OCR gelesen werden: {exc}")
    if not text.strip():
        raise HTTPException(422, "Im Bild wurde kein lesbarer Text erkannt")
    warnings.append("OCR-Erkennung aktiv - Werte vor der Verwendung fachlich pruefen.")
    return text, "image_ocr", warnings


# ---------------------------------------------------------------------------
# Matching + Aggregation
# ---------------------------------------------------------------------------
def match_compound_component(
    name: str, feeds_by_id: Dict[str, Dict[str, Any]]
) -> Tuple[Optional[str], Optional[str]]:
    normalized = normalize_feed_label(name)
    for tokens, feed_id in COMPOUND_FEED_MATCHERS:
        if all(token in normalized for token in tokens):
            feed = feeds_by_id.get(feed_id)
            if feed:
                return feed_id, feed["name"]
    return None, None


def aggregate_compound_components(
    components: List[CompoundFeedComponent],
    feeds_by_id: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, float], float]:
    matched = [c for c in components if c.matched_feed_id and c.inclusion_pct > 0]
    matched_share = sum(c.inclusion_pct for c in matched)
    if matched_share <= 0:
        return {}, 0.0
    numeric_fields = [
        "dm_frac", "price", "me", "sidp", "cp", "ndf", "adf", "st", "bst", "zu",
        "nfc", "xl", "ca", "p", "na", "mg", "k", "rmd", "omdfan1",
    ]
    aggregate = {field: 0.0 for field in numeric_fields}
    for component in matched:
        feed = feeds_by_id[component.matched_feed_id]
        weight = component.inclusion_pct / matched_share
        for field in numeric_fields:
            aggregate[field] += float(feed.get(field) or 0.0) * weight
    return aggregate, matched_share


def build_compound_estimate(
    product_name: str,
    declared: CompoundFeedDeclaredAnalysis,
    aggregate: Dict[str, float],
    matched_share: float,
) -> Tuple[CompoundFeedGfeEstimate, Dict[str, Any]]:
    from modules.agrar.services.naehrwert_service import (
        AnalytikInput,
        FutterTyp,
        QuelleTyp,
        berechne_naehrwerte as _berechne_naehrwerte,
    )

    dm_frac = float(aggregate.get("dm_frac") or 0.88)
    if dm_frac <= 0.0:
        dm_frac = 0.88
    pct_to_g_per_kg_tm = 10.0 / dm_frac  # %-FM -> g/kg TM

    def _declared_to_tm(pct: Optional[float], fallback: float) -> float:
        if pct is None:
            return fallback
        return float(pct) * pct_to_g_per_kg_tm

    cp_g = _declared_to_tm(declared.crude_protein_pct, float(aggregate.get("cp") or 0.0))
    fat_g = _declared_to_tm(declared.crude_fat_pct, float(aggregate.get("xl") or 0.0))
    ash_g = (
        _declared_to_tm(declared.crude_ash_pct, 0.0)
        if declared.crude_ash_pct is not None
        else max(35.0, 1000.0 - float(aggregate.get("nfc") or 820.0))
    )
    fiber_pct = declared.crude_fiber_pct
    ndf_g = float(
        aggregate.get("ndf") or max((fiber_pct or 8.0) * 22.0 / dm_frac * 0.1 * 10.0, 130.0)
    )
    adf_g = float(
        aggregate.get("adf") or max((fiber_pct or 8.0) * 12.0 / dm_frac * 0.1 * 10.0, 75.0)
    )
    starch_g = float(aggregate.get("st") or 220.0)
    sugar_g = float(aggregate.get("zu") or 65.0)

    analytik = AnalytikInput(
        tm=max(float(aggregate.get("dm_frac") or 0.88) * 1000.0, 870.0),
        cp=round(cp_g, 2),
        cl=round(fat_g, 2),
        ca=round(ash_g, 2),
        zucker=round(sugar_g, 2),
        staerke=round(starch_g, 2),
        adfom=round(adf_g, 2),
        andFom=round(ndf_g, 2),
        fan=2.5,
        futtertyp=FutterTyp.MISCHFUTTER,
        quelle=QuelleTyp.USER,
    )
    result = _berechne_naehrwerte(analytik, modus="beratung")

    ca_g = _declared_to_tm(declared.calcium_pct, float(aggregate.get("ca") or 1.5))
    p_g = _declared_to_tm(declared.phosphorus_pct, float(aggregate.get("p") or 4.5))
    na_g = _declared_to_tm(declared.sodium_pct, float(aggregate.get("na") or 1.5))
    mg_g = _declared_to_tm(declared.magnesium_pct, float(aggregate.get("mg") or 2.5))
    nfc_g = max(1000.0 - cp_g - fat_g - ash_g - ndf_g, 0.0)
    product_slug = ascii_slug(product_name)

    estimate = CompoundFeedGfeEstimate(
        basis="composition_match" if matched_share >= 60.0 else "declared_analysis_fallback",
        match_coverage_pct=round(matched_share, 1),
        me_fan1_mj_kgdm=round(result.energie.me_fan1_mj_kg_tm, 3),
        me_fani_mj_kgdm=round(result.energie.me_fani_mj_kg_tm, 3),
        nel_mj_kgdm=round(result.nel_mj_kg_tm, 3),
        sidp_g_kgdm=round(result.protein.sidp_gesamt, 1),
        nxp_g_kgdm=round(result.nxp_g_kg_tm, 1),
        cp_g_kgdm=round(cp_g, 1),
        andfom_g_kgdm=round(ndf_g, 1),
        starch_g_kgdm=round(starch_g, 1),
        sugar_g_kgdm=round(sugar_g, 1),
        fat_g_kgdm=round(fat_g, 1),
        omd_method=result.energie.omd_methode,
    )
    optimizer_feed = {
        "id": f"compound_{product_slug}",
        "lid": None,
        "name": product_name,
        "konservierung": "",
        "group": "Kraftfutter/Betrieb",
        "futterart": "Kraftfutter, Mischfutter",
        "forage": False,
        "dm_frac": round(float(aggregate.get("dm_frac") or 0.88), 3),
        "price": round(float(aggregate.get("price") or 0.38), 3),
        "min_kg": 0.0,
        "max_kg": 8.0,
        "me": float(estimate.me_fan1_mj_kgdm or 0.0),
        "sidp": float(estimate.sidp_g_kgdm or 0.0),
        "cp": round(cp_g, 1),
        "ndf": round(ndf_g, 1),
        "adf": round(adf_g, 1),
        "st": round(starch_g, 1),
        "bst": round(starch_g * 0.60, 1),
        "zu": round(sugar_g, 1),
        "nfc": round(nfc_g, 1),
        "xl": round(fat_g, 1),
        "ca": round(ca_g, 2),
        "p": round(p_g, 2),
        "na": round(na_g, 2),
        "mg": round(mg_g, 2),
        "k": round(float(aggregate.get("k") or 8.0), 2),
        "dcab": None,
        "edg": None,
        "rmd": round(float(aggregate.get("rmd") or result.protein.rmd), 2),
        "omdfan1": round(float(aggregate.get("omdfan1") or result.energie.omd_fan1), 2),
        "ndfd": None,
        "ge": None,
        "sidlys": None,
        "sidmet": None,
        "_source": "compound_upload",
        "_match_coverage_pct": round(matched_share, 1),
        "_legacy_nel_mj_kg": declared.nel_mj_kg,
    }
    return estimate, optimizer_feed


FeedsProvider = Callable[[], List[Dict[str, Any]]]


def parse_compound_feed_text(
    text: str,
    filename: str,
    source_type: str,
    feeds_provider: Optional[FeedsProvider] = None,
) -> CompoundFeedParsed:
    """Parst ein Mischfutter-Etikett (Text) und erzeugt einen Optimizer-Feed.

    Wenn ``feeds_provider`` None ist, wird lazily die
    ``_get_feeds``-Funktion aus der Haupt-Endpoint-Datei importiert
    (um Zirkelimporte zu vermeiden). Tests koennen stattdessen einen
    beliebigen Feeds-Provider injizieren.
    """
    if feeds_provider is None:
        from app.api.v1.endpoints.rations_optimization import _get_feeds as _default
        feeds_provider = _default

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    flat_text = re.sub(r"\s+", " ", text.replace("-\n", "").replace("\n", " "))
    product_name = "Milchleistungsfutter"
    product_match = re.search(
        r"(Milchleistungsfutter[^\n]+)", text.replace("-\n", ""), flags=re.IGNORECASE
    )
    if product_match:
        product_name = " ".join(product_match.group(1).split())
    else:
        for idx, line in enumerate(lines):
            if "Inhaltsstoffe" in line:
                for back in range(max(0, idx - 2), idx):
                    candidate = lines[back]
                    if len(candidate) > 12 and not re.search(r"^[0-9./ -]+$", candidate):
                        product_name = candidate
                        break
                break
    analysis_match = re.search(
        r"Inhaltsstoffe:\s*(.+?)(?:\s+Zusatzstoffe:|\s+Zusammensetzung:)",
        flat_text,
        flags=re.IGNORECASE,
    )
    analysis_text = analysis_match.group(1) if analysis_match else flat_text
    declared = CompoundFeedDeclaredAnalysis(
        crude_protein_pct=extract_labelled_value(analysis_text, "Rohprotein", "%"),
        crude_fat_pct=extract_labelled_value(analysis_text, "Rohfett", "%"),
        crude_fiber_pct=extract_labelled_value(analysis_text, "Rohfaser", "%"),
        crude_ash_pct=extract_labelled_value(analysis_text, "Rohasche", "%"),
        calcium_pct=extract_labelled_value(analysis_text, "Calcium", "%"),
        phosphorus_pct=extract_labelled_value(analysis_text, "Phosphor", "%"),
        sodium_pct=extract_labelled_value(analysis_text, "Natrium", "%"),
        magnesium_pct=extract_labelled_value(analysis_text, "Magnesium", "%"),
        nel_mj_kg=(
            extract_value(analysis_text, r"NEL/?kg\s*([0-9]+[.,][0-9]+)\s*MJ")
            or extract_value(analysis_text, r"([0-9]+[.,][0-9]+)\s*MJ\s*NEL/?kg")
        ),
    )
    components: List[CompoundFeedComponent] = []
    composition_match = re.search(
        r"Zusammensetzung:\s*(.+?)(?:\s+(?:Tel\.|Fax|Email:|Ernährungsphysiologische Zusatzstoffe|Ernaehrungsphysiologische Zusatzstoffe|Fütterungshinweis|Fuetterungshinweis|GmbH\s*&|$))",
        flat_text,
        flags=re.IGNORECASE,
    )
    composition_text = composition_match.group(1) if composition_match else ""
    parts = re.findall(
        r"([0-9]+[.,][0-9]+)\s*%\s*([^%]+?)(?=(?:[0-9]+[.,][0-9]+\s*%|$))",
        composition_text,
        flags=re.IGNORECASE,
    )
    feeds_by_id = {feed["id"]: feed for feed in feeds_provider()}
    for pct_raw, name_raw in parts:
        pct = parse_localized_float(pct_raw)
        if pct is None:
            continue
        cleaned_name = name_raw.strip(" ,.;")
        matched_feed_id, matched_feed_name = match_compound_component(
            cleaned_name, feeds_by_id
        )
        components.append(
            CompoundFeedComponent(
                name=cleaned_name,
                inclusion_pct=round(pct, 2),
                matched_feed_id=matched_feed_id,
                matched_feed_name=matched_feed_name,
            )
        )
    aggregate, matched_share = aggregate_compound_components(components, feeds_by_id)
    estimate, optimizer_feed = build_compound_estimate(
        product_name, declared, aggregate, matched_share
    )
    warnings: List[str] = []
    if matched_share < 100.0:
        warnings.append(
            f"Rezeptur-Match deckt {matched_share:.1f}% der Zusammensetzung gegen DLG-Futtermittel ab."
        )
    if declared.nel_mj_kg is not None and estimate.nel_mj_kgdm is not None:
        dm_frac_for_nel = float(optimizer_feed.get("dm_frac") or 0.88)
        declared_nel_tm = (
            declared.nel_mj_kg / dm_frac_for_nel
            if dm_frac_for_nel > 0
            else declared.nel_mj_kg
        )
        delta = abs(declared_nel_tm - estimate.nel_mj_kgdm)
        if delta > 0.4:
            warnings.append(
                "Abweichung zwischen deklarierter NEL "
                f"({declared.nel_mj_kg:.1f} MJ/kg FM ≈ {declared_nel_tm:.2f} MJ/kg TM) und geschaetzter NEL "
                f"({estimate.nel_mj_kgdm:.2f} MJ/kg TM) beachten."
            )
    if not components:
        warnings.append(
            "Keine verwertbare Rezeptur-Zusammensetzung erkannt; GfE-Schaetzung basiert auf Deklarationsanalyse."
        )
    return CompoundFeedParsed(
        source_filename=filename,
        source_type=source_type,
        product_name=product_name,
        supplier_name=None,
        declared_analysis=declared,
        composition=components,
        gfe2023_estimate=estimate,
        optimizer_feed=optimizer_feed,
        warnings=warnings,
        raw_text_preview=text[:1200],
    )
