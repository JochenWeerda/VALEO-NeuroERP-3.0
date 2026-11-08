"""Positionszeilen fuer DMS-Inbox / Lieferschein aus vorhandenen Extraktoren.

Reihenfolge:
1. Deterministische Tabellen-/Zeilen-Regex auf OCR-Text (ohne API-Key)
2. Optional Claude hinter ``EINKAUF_OCR_ENGINE=claude``
   (PDF → ``extract_invoice_pdf`` Vision; Text → ``LLMGateway``)

- nie ``engine=stub`` (Musterartikel), nie erfundene Heuristik-Zeilen
- ohne lesbare Zeilen → leere ``positionen`` + Gap-Code
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Mapping, Sequence

from app.core.dms_ocr_contracts import DokumentTyp, klassifiziere_dokument

logger = logging.getLogger(__name__)

OCR_ENGINE_ENV = "EINKAUF_OCR_ENGINE"

GAP_ENGINE_NOT_CLAUDE = "positionsextraktion_engine_nicht_claude"
GAP_LLM_UNAVAILABLE = "positionsextraktion_ohne_llm_key"
GAP_KIND_UNSUPPORTED = "positionsextraktion_belegart_ohne_zeilenpfad"
GAP_NO_LINES = "positionsextraktion_keine_zeilen"
GAP_PARSE_FAILED = "positionsextraktion_parse_fehlgeschlagen"
GAP_REGEX_NO_LINES = "positionsextraktion_regex_keine_zeilen"

# Einheiten aus echten Übungsbelegen + Live-OCR-Varianten (Stiick/Stick/Stilck).
# Längere Tokens zuerst; x nicht vor Ziffer (verhindert 24x20cm); t/m/l als ganze Tokens.
_UNITS = (
    r"Stiick|Stilck|Stick|Stück|Stueck|Stk|ST|St\.?|to|kg|"
    r"Pal|Palette|Sack|Big-?Bag|Eh|EH|TNE|C62|"
    r"t|l|L|M|m|x(?!\d)"
)
# DE-Mengen: 12,50 | 1.980,00 | 50.000 | -8.722,00 | 8
# Live-OCR Birkhoff: Leerzeichen nach Komma („25.200, 00“).
_QTY = r"-?\d{1,3}(?:\.\d{3})*(?:,\s*\d{1,3})?|-?\d+(?:[.,]\s*\d{1,3})?"
# Art-Nr mit mind. einer Ziffer; Punkt erlaubt (OCR „29.34611“ statt „29-34611“).
_SKU = r"(?=[A-Z0-9\-/.\*]*\d)[A-Z0-9][A-Z0-9\-/.\*]{1,24}"
# Pos: optional „+“ / Punkt / Gedankenstrich (Live: „1+ 768…“, „2. Monatliche“, „2 — 29-…“).
_POS = r"(\d{1,4})[+]?"
_SEP = r"(?:\.?(?:\s+[—\-–]\s+|\s+))"
# Einheit darf an Menge kleben; OCR-Müll („30,00M_“); keine Teilworte („Tage“, „ml“).
_UNIT_TOKEN = rf"({_UNITS})(?:[_.,\"”'\u201c\u201d]+)?(?![A-Za-zÄÖÜäöüß])"
_STOP_LINE = re.compile(
    r"^\s*(?:summe|gesamt|endbetrag|nettobetrag|bruttobetrag|mwst|ust|"
    r"unterschrift|empfangsbestaetigung|seite\s+\d|übertrag|uebertrag|"
    r"zahlungsziel|iban|bic|steuer|netto\s*gewicht|brutto\s*gewicht)\b",
    re.I,
)
_HEADER_HINT = re.compile(
    r"(?:^|\n)\s*(?:pos(?:ition)?\.?|p\.\s*|nr\.?|art(?:ikel)?\.?\-?nr\.?|"
    r"artikel(?:nummer|bez\.?)?|bezeichnung|beschreibung|menge|einheit|"
    r"ep|einzelpreis|vk-?preis|preis|beleg)\b",
    re.I,
)
_ROW_WITH_SKU = re.compile(
    rf"^\s*{_POS}{_SEP}"
    rf"({_SKU})\s+"
    rf"(.+?)\s+"
    rf"({_QTY})\s*"
    rf"{_UNIT_TOKEN}"
    rf"(?:\s*/\s*[Tt]\b)?"
    rf"(?:\s+({_QTY}))?",
    re.I,
)
_ROW_NO_SKU = re.compile(
    rf"^\s*{_POS}{_SEP}"
    rf"([A-Za-zÄÖÜäöüß][\wÄÖÜäöüß/\- .]{{2,60}}?)\s+"
    rf"({_QTY})\s*"
    rf"{_UNIT_TOKEN}"
    rf"(?:\s+({_QTY}))?",
    re.I,
)
# DGO-PSM: Pos | Art-Nr | Name | Anzahl | Menge | PE(=l/St, OCR oft „1“ für l).
# Name greedy + Backtracking, damit „201 64 1.280,00 1“ korrekt menge=1280 greift.
# PE „1“ nur alleinstehend (nicht Teil von 31,80).
_ROW_ANZAHL_MENGE = re.compile(
    rf"^\s*{_POS}{_SEP}"
    rf"({_SKU})\s+"
    rf"(.+)\s+"
    rf"({_QTY})\s+"
    rf"({_QTY})\s*"
    rf"(?:([lL]|St\.?|ST|kg|t)|(?<![,\d])(1)(?![\d,]))\b",
    re.I,
)
# DGO Live: Menge+Liter ohne Leerzeichen („20,001“ = 20,00 l)
_ROW_DGO_GLUED_LITER = re.compile(
    rf"^\s*{_POS}{_SEP}"
    rf"({_SKU})\s+"
    rf"(.+)\s+"
    rf"({_QTY})\s+"
    rf"(\d{{1,3}},\d{{2}})1\b",
    re.I,
)
# Lieferdatum OCR oft ohne Trenner („081026“ statt „08.10.26“) — sonst greift Preis auf „081“.
_ROW_BELEG_SKU = re.compile(
    rf"^\s*([A-Z]{{1,3}}\d{{4,}})\s+"
    rf"([A-Za-zÄÖÜäöüß][\wÄÖÜäöüß/\- .]{{2,50}}?)\s+"
    rf"({_QTY})\s*"
    rf"{_UNIT_TOKEN}"
    rf"(?:\s+(?:\d{{1,2}}[./]\d{{1,2}}(?:[./]\d{{2,4}})?|\d{{6}}|\d{{8}})\s+)?"
    rf"(?:\s+({_QTY}))?",
    re.I,
)
# Geldbeträge hinter ME (Preis/Netto/Brutto); OCR „11.55000“ ohne Komma.
_MONEY_AFTER_UNIT = re.compile(
    r"(?<![\d.])(\d{1,3}(?:\.\d{3})+,\d{2}|\d{1,3}(?:\.\d{3})+\d{2}|\d+,\d{2})(?!\d)"
)
_ROW_SKU_FIRST = re.compile(
    rf"^\s*(\d{{5,12}})\s+"
    rf"([A-Za-zÄÖÜäöüß_][\wÄÖÜäöüß/\- .]{{2,60}}?)\s+"
    rf"({_QTY})\s*"
    rf"{_UNIT_TOKEN}"
    rf"(?:\s+({_QTY}))?",
    re.I,
)
# Hofmeister Live: Pos an Art-Nr geklebt („376885487“≈3+76885487, „44850060521“≈4+4850060521)
# plus OCR „4,008T“≈4,00 ST
_ROW_GLUED_POS_SKU = re.compile(
    rf"^\s*(\d)(\d{{7,11}})\s+(?:[—\-–_]+\s*)?"
    rf"([A-Za-zÄÖÜäöüß_][\wÄÖÜäöüß/\- .]{{2,60}}?)\s+"
    rf"({_QTY})\s*"
    rf"{_UNIT_TOKEN}"
    rf"(?:\s+({_QTY}))?",
    re.I,
)
_ROW_GLUED_POS_SKU_ST = re.compile(
    rf"^\s*(\d)(\d{{7,11}})\s+"
    rf"([A-Za-zÄÖÜäöüß_'‘’\"“”][\wÄÖÜäöüß/\- .]{{2,60}}?)\s+"
    rf"(\d{{1,3}},\d{{2}})\d?s?T\b",
    re.I,
)
# Art-Nr Menge ME Bezeichnung — Folkerts-Ausgangs-LS (Name muss mit Buchstabe starten)
_ROW_SKU_QTY_NAME = re.compile(
    rf"^\s*(\d{{5,12}})\s+"
    rf"({_QTY})\s*"
    rf"{_UNIT_TOKEN}\s+"
    rf"([A-Za-zÄÖÜäöüß].+?)\s*$",
    re.I,
)
# Nur Art-Nr + Name (Deuka-Korrektur: Menge folgt auf nächster Zeile)
_ROW_SKU_NAME_ONLY = re.compile(
    rf"^\s*(\d{{6,12}})\s+"
    rf"([A-Za-zÄÖÜäöüß][\wÄÖÜäöüß/\- .]{{3,70}})\s*$",
    re.I,
)
# Fortsetzungszeile: optional Ref-Nr, dann Menge+Einheit (ggf. angeklebt).
# _QTY/_UNITS in (?:…) — sonst zerlegt das „|“ in _QTY die Alternative.
_ROW_QTY_UNIT_CONT = re.compile(
    rf"^(?:\d{{4,12}}\s+)?((?:{_QTY}))\s*{_UNIT_TOKEN}",
    re.I,
)
_HAS_QTY_UNIT = re.compile(
    rf"(?:{_QTY})\s+(?:{_UNITS})(?:[_.,\"”'\u201c\u201d]+)?(?![A-Za-zÄÖÜäöüß])",
    re.I,
)
_ROW_ERZEUGNIS = re.compile(
    rf"Erzeugnis:\s*(.+?)\s+"
    rf"(?:Spezifikation:\s*\S+\s+)?"
    rf"Menge:\s*({_QTY})\s*"
    rf"({_UNITS})?\b",
    re.I,
)
_ROW_FREE = re.compile(
    rf"^([A-Za-zÄÖÜäöüß][\wÄÖÜäöüß/\- .]{{2,45}}?)\s+"
    rf"({_QTY})\s*"
    rf"{_UNIT_TOKEN}"
    rf"(?:\s+({_QTY}))?",
    re.I,
)
_NAME_STOP = frozenset({
    "bezeichnung", "artikel", "position", "pos", "menge", "einheit", "summe",
    "beschreibung", "netto", "brutto", "gesamt", "skonto", "mwst", "ust",
    "rabatt", "fracht", "steuer", "seite",
})

_POSITION_KINDS = frozenset({
    DokumentTyp.LIEFERSCHEIN,
    DokumentTyp.EINGANGSRECHNUNG,
    DokumentTyp.GUTSCHRIFT,
})

_BELEG_POSITION_SCHEMA = (
    "Extrahiere Positionszeilen dieses Eingangsbelegs (Lieferschein oder "
    "Eingangsrechnung) als JSON (NUR JSON, keine Markdown-Bloecke).\n"
    "Schema:\n"
    '{"positionen":[{"artikel_name":"Bezeichnung","artikel_nr":"Nr oder null",'
    '"menge":Zahl_oder_null,"einheit":"t|kg|Stk|Pal|Sack|null",'
    '"einzelpreis":Zahl_oder_null}]}\n'
    "Nur Zeilen, die im Text stehen. Keine Musterartikel, keine Fantasiezeilen. "
    "Wenn keine Positionen erkennbar: {\"positionen\":[]}."
)


def resolve_ocr_engine() -> str:
    return (os.getenv(OCR_ENGINE_ENV) or "stub").strip().lower()


def document_kind_for_positions(ocr_text: str | None, item_id: str = "inbox") -> DokumentTyp | None:
    text = (ocr_text or "").strip()
    if not text:
        return None
    result = klassifiziere_dokument(item_id or "inbox", text)
    if result.manuell_pruefen or not result.gematchte_schlagwoerter:
        return None
    if result.erkannter_typ not in _POSITION_KINDS:
        return None
    return result.erkannter_typ


def _normalize_position_rows(raw: Sequence[Any] | None) -> list[dict[str, Any]]:
    """Nur echte Zeilen mit Name oder Nummer — keine Platzhalter."""
    rows: list[dict[str, Any]] = []
    if not isinstance(raw, list):
        return rows
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        name = _clean(
            item.get("artikel_name")
            or item.get("artikel")
            or item.get("name")
            or item.get("bezeichnung")
            or item.get("description")
            or item.get("article_name")
        )
        number = _clean(
            item.get("artikel_nr")
            or item.get("artikelnummer")
            or item.get("article_number")
            or item.get("sku")
        )
        if not name and not number:
            continue
        if name in ("—", "-", "Musterartikel A", "Musterartikel B"):
            continue
        row: dict[str, Any] = {}
        if name:
            row["artikel_name"] = name
        if number:
            row["artikel_nr"] = number
        menge = item.get("menge")
        if menge is None:
            menge = item.get("quantity") or item.get("qty")
        if menge is not None and str(menge).strip() != "":
            row["menge"] = menge
        einheit = _clean(item.get("einheit") or item.get("unit") or item.get("uom"))
        if einheit:
            row["einheit"] = einheit
        preis = item.get("einzelpreis")
        if preis is None:
            preis = item.get("unit_price") or item.get("price")
        if preis is not None and str(preis).strip() != "":
            row["einzelpreis"] = preis
        ean = _clean(item.get("ean") or item.get("ean_code") or item.get("barcode"))
        if ean:
            row["ean"] = ean
        rows.append(row)
    return rows


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_de_number(raw: Any) -> str | None:
    """DE-Mengen/Preise → ASCII-Dezimal (1.980,00 → 1980.00; 50.000 → 50000)."""
    text = _clean(raw)
    if text is None:
        return None
    s = text.replace(" ", "").replace("€", "").replace("EUR", "")
    neg = s.startswith("-")
    if neg:
        s = s[1:]
    # OCR Netto ohne Dezimal-Komma: „11.55000“ → 11550.00
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+\d{2}", s):
        s = f"{s[:-2]},{s[-2:]}"
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
        stripped = s.replace(".", "")
        # „0.000“ ist Nullmenge (Live Broering), kein Tausender-Gruppierung
        s = "0" if set(stripped) <= {"0"} else stripped
    if neg:
        s = f"-{s}"
    return s


def _qty_is_zero(menge_n: str | None) -> bool:
    if menge_n is None or menge_n == "":
        return True
    try:
        return abs(float(menge_n)) < 1e-9
    except ValueError:
        return not menge_n.replace("0", "").replace(".", "").replace("-", "")


def _preis_looks_plausible(preis_n: str | None) -> bool:
    """Verwirft Datumsfragmente (OCR „081“ aus „081026“) als Einzelpreis."""
    if not preis_n:
        return False
    try:
        value = float(preis_n)
    except ValueError:
        return False
    if value < 0.01 or value > 50_000:
        return False
    # reine 1–3-stellige Ganzzahlen ohne Nachkomma sind oft Datum/Steuersatz
    if re.fullmatch(r"0?\d{1,3}", preis_n):
        return False
    return True


def _recover_menge_from_price_netto(
    line: str,
    *,
    unit: str | None,
    preis_n: str | None,
) -> tuple[str | None, str | None]:
    """Wenn OCR-Menge 0: Menge aus Preis+Netto (Agrar €/dt oder €/t).

    Broering Live: „0.000 KG … 23,10 … 11.55000“ → 50000 kg (23,10 €/dt).
    Birkhoff mit ``/t``: netto/preis*1000.
    """
    unit_l = (unit or "").casefold()
    if unit_l not in ("kg", "t"):
        return None, preis_n

    unit_match = re.search(rf"\b(?:{_UNITS})\b", line, re.I)
    rest = line[unit_match.end() :] if unit_match else line
    rest = re.sub(
        r"^\s*(?:\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?|\d{6}|\d{8})\s*",
        " ",
        rest,
    )
    amounts: list[tuple[str, float]] = []
    for raw in _MONEY_AFTER_UNIT.findall(rest):
        normalized = _normalize_de_number(raw)
        if not normalized:
            continue
        try:
            value = float(normalized)
        except ValueError:
            continue
        if value <= 0:
            continue
        amounts.append((normalized, value))
    if not amounts:
        return None, preis_n

    # Nach ME (+ optional Datum): 1. Betrag = Preis, 2. = Netto (Brutto danach ignorieren).
    if _preis_looks_plausible(preis_n):
        price_str = preis_n
        price_v = float(preis_n)  # type: ignore[arg-type]
        following = [(s, v) for s, v in amounts if abs(v - price_v) > 0.005]
    else:
        price_str, price_v = amounts[0]
        following = amounts[1:]
    if not following:
        return None, price_str if _preis_looks_plausible(price_str) else preis_n
    _netto_str, netto_v = following[0]

    per_t = bool(re.search(r"/\s*[tT]\b", line))
    if unit_l == "t":
        qty = netto_v / price_v
    elif per_t:
        qty = netto_v / price_v * 1000.0
    else:
        # Getreide oft €/dt (100 kg): Broering 11.550/23,10*100 = 50.000
        qty_dt = netto_v / price_v * 100.0
        qty_t = netto_v / price_v * 1000.0
        if 100.0 <= qty_dt <= 100_000.0:
            qty = qty_dt
        elif 100.0 <= qty_t <= 100_000.0:
            qty = qty_t
        else:
            qty = netto_v / price_v

    if qty <= 0:
        return None, price_str if _preis_looks_plausible(price_str) else preis_n
    if abs(qty - round(qty)) < 0.05:
        menge_out = str(int(round(qty)))
    else:
        menge_out = f"{qty:.2f}"
    preis_out = price_str if _preis_looks_plausible(price_str) else preis_n
    return menge_out, preis_out


def _normalize_unit(einheit: str | None) -> str | None:
    unit = _clean(einheit)
    if not unit:
        return None
    unit = unit.rstrip("._\"'”““")
    low = unit.casefold()
    if low in ("to",):
        return "t"
    if low in ("st", "stk", "stück", "stueck", "stiick", "stilck", "stick"):
        return "Stk"
    if low == "m":
        return "M"
    if low == "kg":
        return "kg"
    if low == "x":
        return "x"
    if low == "eh":
        return "Eh"
    # DGO Live-OCR: Preiseinheit „l“ wird oft als „1“ gelesen
    if unit == "1":
        return "l"
    if low == "l":
        return "l"
    return unit


def _clean_article_name(name: str | None) -> str | None:
    """OCR-Müll am Namenanfang (Anführungszeichen, Unterstrich) entfernen."""
    text = _clean(name)
    if not text:
        return None
    text = text.lstrip("_'\"‘’“”\\ ").rstrip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def extract_table_line_items(ocr_text: str | None) -> list[dict[str, Any]]:
    """Deterministische Positionszeilen aus OCR-Fliesstext (Tabellen-/Mengenmuster).

    Keine Fantasiezeilen: nur Treffer mit Artikelname/-nr und Menge.
    Orientiert an typischen DE-Lieferschein-/Rechnungs-OCR (Pos|Art-Nr|Menge|Einheit)
    inkl. Live-OCR Folkerts/DGO/Sica/Deuka/Hofmeister/Zill.
    """
    text = (ocr_text or "").replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        return []

    rows: list[dict[str, Any]] = []

    def _add(
        *,
        name: str | None,
        number: str | None = None,
        menge: Any = None,
        einheit: str | None = None,
        preis: Any = None,
        line: str | None = None,
    ) -> None:
        # Kein Soft-Dedup: Webfleet-Gleichzeilen und DGO-Doppelpositionen behalten.
        name_c = _clean_article_name(name)
        number_c = _clean(number)
        if number_c:
            number_c = number_c.replace("*", "").strip() or None
        if not name_c and not number_c:
            return
        if name_c and name_c.casefold() in _NAME_STOP:
            return
        if name_c and name_c.casefold().split()[0] in _NAME_STOP:
            return
        # Preis-/MwSt-Müll nie als Artikelname (Deuka-OCR-Fortsetzung).
        if name_c and re.match(r"^[\d,.\-\s]+", name_c) and "eur" in name_c.casefold():
            return
        # Footer-/Adresszeilen (Hofmeister-OCR) ohne echte Warenposition
        if name_c and re.search(r"steuer|hotmetster|geschatsadrese|iban|amtsgericht", name_c, re.I):
            return
        menge_n = _normalize_de_number(menge)
        preis_n = _normalize_de_number(preis)
        unit = _normalize_unit(einheit)
        # Live-OCR Hofmeister: „30,00 ST“ → „3000sT“ (Komma verloren, Einheit angeklebt)
        raw_menge = str(menge).strip() if menge is not None else ""
        if (
            unit in ("Stk", "M")
            and menge_n
            and re.fullmatch(r"\d{3,6}", raw_menge)
            and raw_menge.endswith("00")
        ):
            menge_n = f"{int(raw_menge[:-2])}.{raw_menge[-2:]}"
        # Broering Live: Menge „0.000“ bei lesbarem Preis/Netto → aus €/dt rekonstruieren
        if _qty_is_zero(menge_n) and line:
            recovered, preis_fix = _recover_menge_from_price_netto(
                line, unit=unit, preis_n=preis_n
            )
            if recovered:
                menge_n = recovered
            if preis_fix:
                preis_n = preis_fix
            elif not _preis_looks_plausible(preis_n):
                preis_n = None
        elif not _preis_looks_plausible(preis_n):
            preis_n = None
        row: dict[str, Any] = {}
        if name_c:
            row["artikel_name"] = name_c
        if number_c:
            row["artikel_nr"] = number_c
        if menge_n is not None:
            row["menge"] = menge_n
        if unit:
            row["einheit"] = unit
        elif einheit is None and name_c and name_c.casefold() == "maut":
            row["einheit"] = "Stk"
        if preis_n is not None:
            row["einzelpreis"] = preis_n
        rows.append(row)

    for match in _ROW_ERZEUGNIS.finditer(text):
        _add(
            name=match.group(1),
            menge=match.group(2),
            einheit=match.group(3) or "t",
        )

    in_table = bool(_HEADER_HINT.search(text))
    pending_sku: tuple[str, str] | None = None
    lines = text.splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if not line or len(line) < 5:
            continue
        if line.casefold().startswith("lager:"):
            pending_sku = None
            continue
        if _STOP_LINE.match(line):
            in_table = False
            pending_sku = None
            continue
        if (
            _HEADER_HINT.match(line)
            and not _ROW_WITH_SKU.match(line)
            and not _ROW_NO_SKU.match(line)
            and not _ROW_BELEG_SKU.match(line)
            and not _ROW_SKU_QTY_NAME.match(line)
            and not _ROW_SKU_FIRST.match(line)
            and not _ROW_ANZAHL_MENGE.match(line)
            and not _ROW_SKU_NAME_ONLY.match(line)
        ):
            in_table = True
            pending_sku = None
            continue

        # Deuka-Korrektur u.ä.: Art-Nr+Name, Menge auf Folgeszeile
        if pending_sku is not None:
            m_cont = _ROW_QTY_UNIT_CONT.match(line)
            if m_cont:
                _add(
                    number=pending_sku[0],
                    name=pending_sku[1],
                    menge=m_cont.group(1),
                    einheit=m_cont.group(2),
                )
                pending_sku = None
                continue
            pending_sku = None

        m_anzahl = _ROW_ANZAHL_MENGE.match(line)
        if m_anzahl:
            pe = m_anzahl.group(6) or m_anzahl.group(7)
            _add(
                number=m_anzahl.group(2),
                name=m_anzahl.group(3),
                menge=m_anzahl.group(5),
                einheit=pe,
            )
            continue
        m_glued_l = _ROW_DGO_GLUED_LITER.match(line)
        if m_glued_l:
            _add(
                number=m_glued_l.group(2),
                name=m_glued_l.group(3),
                menge=m_glued_l.group(5),
                einheit="l",
            )
            continue
        m_sku = _ROW_WITH_SKU.match(line)
        if m_sku:
            _add(
                number=m_sku.group(2),
                name=m_sku.group(3),
                menge=m_sku.group(4),
                einheit=m_sku.group(5),
                preis=m_sku.group(6),
                line=line,
            )
            continue
        m_beleg = _ROW_BELEG_SKU.match(line)
        if m_beleg:
            _add(
                number=m_beleg.group(1),
                name=m_beleg.group(2),
                menge=m_beleg.group(3),
                einheit=m_beleg.group(4),
                preis=m_beleg.group(5),
                line=line,
            )
            continue
        m_sku_qty = _ROW_SKU_QTY_NAME.match(line)
        if m_sku_qty:
            _add(
                number=m_sku_qty.group(1),
                menge=m_sku_qty.group(2),
                einheit=m_sku_qty.group(3),
                name=m_sku_qty.group(4),
                line=line,
            )
            continue
        m_sku_first = _ROW_SKU_FIRST.match(line)
        if m_sku_first:
            _add(
                number=m_sku_first.group(1),
                name=m_sku_first.group(2),
                menge=m_sku_first.group(3),
                einheit=m_sku_first.group(4),
                preis=m_sku_first.group(5),
                line=line,
            )
            continue
        m_glued_st = _ROW_GLUED_POS_SKU_ST.match(line)
        if m_glued_st:
            _add(
                number=m_glued_st.group(2),
                name=m_glued_st.group(3),
                menge=m_glued_st.group(4),
                einheit="Stk",
                line=line,
            )
            continue
        m_glued = _ROW_GLUED_POS_SKU.match(line)
        if m_glued:
            _add(
                number=m_glued.group(2),
                name=m_glued.group(3),
                menge=m_glued.group(4),
                einheit=m_glued.group(5),
                preis=m_glued.group(6),
                line=line,
            )
            continue
        m_pos = _ROW_NO_SKU.match(line)
        if m_pos:
            _add(
                name=m_pos.group(2),
                menge=m_pos.group(3),
                einheit=m_pos.group(4),
                preis=m_pos.group(5),
                line=line,
            )
            continue
        m_name_only = _ROW_SKU_NAME_ONLY.match(line)
        if m_name_only and not _HAS_QTY_UNIT.search(line):
            pending_sku = (m_name_only.group(1), m_name_only.group(2))
            continue
        if in_table:
            m_free = _ROW_FREE.match(line)
            if m_free:
                unit = m_free.group(3)
                _add(
                    name=m_free.group(1),
                    menge=m_free.group(2),
                    einheit=unit if unit else "Stk",
                    preis=m_free.group(4),
                )

    return _normalize_position_rows(rows)


def _extract_via_pdf_claude(pdf_bytes: bytes, file_id: str = "dms-inbox.pdf") -> tuple[list[dict[str, Any]], list[str]]:
    """Nutzt denselben Claude-Pfad wie Einkauf OCR (Vision/Document)."""
    from app.einkauf.ocr_invoice import extract_invoice_pdf

    result = extract_invoice_pdf(file_id=file_id, engine="claude", pdf_bytes=pdf_bytes)
    extracted = result.get("extracted_data") or {}
    rows = _normalize_position_rows(extracted.get("positionen"))
    gaps: list[str] = []
    warnings = result.get("extraction_warnings") or []
    if not rows:
        if any("anthropic" in str(w).lower() or "claude" in str(w).lower() for w in warnings):
            gaps.append(GAP_LLM_UNAVAILABLE)
        else:
            gaps.append(GAP_NO_LINES)
    return rows, gaps


def _extract_via_llm_text(
    ocr_text: str,
    *,
    db: Any = None,
    tenant_id: str | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Text-Claude ueber LLMGateway — ohne Heuristik-Fallback."""
    from app.services.llm_gateway import LLMGateway, parse_json_object

    gateway = LLMGateway(db, tenant_id)
    if not gateway.available():
        return [], [GAP_LLM_UNAVAILABLE]

    prompt = f"{_BELEG_POSITION_SCHEMA}\n\nOCR-Text:\n{ocr_text[:8000]}"
    out = gateway.complete_or_none(prompt, max_tokens=1500)
    if not out:
        return [], [GAP_LLM_UNAVAILABLE]
    try:
        parsed = parse_json_object(out)
    except Exception:  # noqa: BLE001 — LLM-Antwort unbrauchbar
        logger.warning("dms_position_llm_json_ungültig")
        return [], [GAP_PARSE_FAILED]
    rows = _normalize_position_rows(parsed.get("positionen"))
    if not rows:
        return [], [GAP_NO_LINES]
    return rows, []


def try_fetch_mayan_pdf(
    client: Any,
    document_id: int,
    version_id: int | None = None,
    *,
    download_url: str | None = None,
) -> bytes | None:
    """Fetch only an advertised same-origin PDF link; otherwise preserve OCR text.

    The connector is an httpx.Client, with get/Response.content. No file-list
    or download endpoint is inferred from a document/version identifier.
    """
    if not isinstance(download_url, str) or not download_url.strip():
        return None
    try:
        import httpx

        base = httpx.URL(client.base_url)
        target = base.join(download_url)
        if (target.scheme, target.host, target.port) != (base.scheme, base.host, base.port):
            return None
        response = client.get(target, follow_redirects=False)
        response.raise_for_status()
        content = response.content
        return content if content.startswith(b"%PDF-") else None
    except Exception:  # noqa: BLE001 — optional PDF; OCR-text remains available
        logger.debug("mayan_advertised_pdf_unavailable")
        return None


def enrich_parsed_fields_with_positions(
    parsed_fields: Mapping[str, Any] | None,
    ocr_text: str | None,
    *,
    pdf_bytes: bytes | None = None,
    item_id: str = "inbox",
    db: Any = None,
    tenant_id: str | None = None,
    force_kind: DokumentTyp | str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Schreibt ``positionen`` in eine Kopie von parsed_fields, wenn Extraktion gelingt."""
    fields = dict(parsed_fields or {})
    gaps: list[str] = []

    existing = _normalize_position_rows(fields.get("positionen"))
    if existing:
        fields["positionen"] = existing
        return fields, gaps

    kind: DokumentTyp | None
    if force_kind is not None:
        if isinstance(force_kind, DokumentTyp):
            kind = force_kind if force_kind in _POSITION_KINDS else None
        else:
            try:
                kind = DokumentTyp(str(force_kind))
            except ValueError:
                kind = None
            if kind not in _POSITION_KINDS:
                kind = None
    else:
        kind = document_kind_for_positions(ocr_text, item_id)

    if kind is None:
        gaps.append(GAP_KIND_UNSUPPORTED)
        fields.setdefault("positionen", [])
        fields["position_extraction_gaps"] = gaps
        return fields, gaps

    fields["document_kind_hint"] = kind.value

    rows = extract_table_line_items(ocr_text)
    engine_used = "table_regex" if rows else None

    extract_gaps: list[str] = []
    engine = resolve_ocr_engine()
    if not rows and engine == "claude":
        if pdf_bytes:
            rows, extract_gaps = _extract_via_pdf_claude(pdf_bytes, file_id=f"{item_id}.pdf")
            if rows:
                engine_used = "claude_pdf"
        if not rows and (ocr_text or "").strip():
            text_rows, text_gaps = _extract_via_llm_text(
                ocr_text or "", db=db, tenant_id=tenant_id
            )
            if text_rows:
                rows = text_rows
                extract_gaps = []
                engine_used = "claude_text"
            else:
                extract_gaps = extract_gaps or text_gaps
    elif not rows and engine != "claude":
        extract_gaps = [GAP_REGEX_NO_LINES, GAP_ENGINE_NOT_CLAUDE]

    if not rows and not extract_gaps:
        extract_gaps = [GAP_NO_LINES]

    gaps.extend(extract_gaps)
    fields["positionen"] = rows
    fields["position_extraction_gaps"] = gaps
    fields["position_extraction_engine"] = engine_used or engine
    if rows:
        fields["position_extraction_gaps"] = [
            g for g in gaps if g not in {GAP_NO_LINES, GAP_REGEX_NO_LINES, GAP_ENGINE_NOT_CLAUDE}
        ]
        gaps = fields["position_extraction_gaps"]
    return fields, gaps


def looks_like_lieferschein_or_invoice(ocr_text: str | None) -> bool:
    """Schnelle Textprobe ohne Klassifikator — fuer Tests/Guards."""
    blob = (ocr_text or "").lower()
    return bool(
        re.search(r"lieferschein|delivery\s*note|\bls[\s\-]?nr", blob)
        or re.search(r"rechnung|invoice|eingangsrechnung", blob)
    )
