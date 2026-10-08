"""Real simple-fact XBRL drafts; neither tax-rule validation nor ELSTER submission."""
from datetime import date
from decimal import Decimal, InvalidOperation
from functools import lru_cache
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

VERSION = "6.9"
CATALOG = Path(__file__).resolve().parents[1] / "data/ebilanz/taxonomy-6.9.json"
CORE_FIELDS = (
    "de-gcd:genInfo.company.id.name", "de-gcd:genInfo.company.id.location.country",
    "de-gcd:genInfo.report.period.fiscalYearBegin", "de-gcd:genInfo.report.period.fiscalYearEnd",
)
NS = {
    "xbrli": "http://www.xbrl.org/2003/instance", "link": "http://www.xbrl.org/2003/linkbase",
    "xlink": "http://www.w3.org/1999/xlink", "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "iso4217": "http://www.xbrl.org/2003/iso4217",
    "de-gcd": "http://www.xbrl.de/taxonomies/de-gcd-2025-04-01",
    "de-gaap-ci": "http://www.xbrl.de/taxonomies/de-gaap-ci-2025-04-01",
}
_NUMERIC = {"monetaryItemType", "decimalItemType", "integerItemType", "nonNegativeIntegerItemType",
            "positiveIntegerItemType", "sharesItemType", "pureItemType", "percentItemType"}


def _xml_text(value: str) -> bool:
    return all(char in "\t\n\r" or 32 <= ord(char) <= 0xD7FF or 0xE000 <= ord(char) <= 0xFFFD
               or 0x10000 <= ord(char) <= 0x10FFFF for char in value)


@lru_cache(maxsize=1)
def _catalog() -> dict:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    if data["version"] != VERSION or len(data["concepts"]) != 3944:
        raise RuntimeError("Taxonomiekatalog ist unvollstaendig oder falsch versioniert")
    return {row["element"]: row for row in data["concepts"]}


def catalog_page(limit: int, skip: int) -> list[dict]:
    return [dict(row) for row in list(_catalog().values())[skip:skip + limit]]


def fact_text(name: str, value: str | None) -> str | None:
    concept = _catalog().get(name)
    if not concept:
        raise ValueError(f"Unbekanntes Konzept der Taxonomie 6.9: {name}")
    if concept["abstract"] or concept["substitutionGroup"] != "xbrli:item":
        raise ValueError(f"Kein einfacher berichtbarer Fakt: {name}")
    if value is None:
        if not concept["nillable"]:
            raise ValueError(f"Konzept erlaubt keinen nil-Fakt: {name}")
        return None
    if not isinstance(value, str) or len(value) > 10000 or not _xml_text(value):
        raise ValueError(f"Ungueltiger XML-Fakt: {name}")
    kind = concept["typ"].split(":")[-1]
    if kind in _NUMERIC:
        if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", value):
            raise ValueError(f"Ungueltiger Dezimalwert: {name}")
        try:
            numeric = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(f"Ungueltiger Zahlenwert: {name}") from exc
        integer = "Integer" in kind or kind == "integerItemType"
        if not numeric.is_finite() or integer and numeric != numeric.to_integral_value():
            raise ValueError(f"Ungueltiger Zahlenwert: {name}")
        if kind == "nonNegativeIntegerItemType" and numeric < 0 or kind == "positiveIntegerItemType" and numeric <= 0:
            raise ValueError(f"Ungueltiges Zahlenvorzeichen: {name}")
        return str(int(numeric)) if integer else format(numeric, "f")
    if kind == "dateItemType":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError(f"Ungueltiges Datum: {name}")
        return date.fromisoformat(value).isoformat()
    if kind == "booleanItemType":
        if value not in {"true", "false", "1", "0"}:
            raise ValueError(f"Ungueltiger boolescher Wert: {name}")
        return "true" if value in {"true", "1"} else "false"
    if kind not in {"stringItemType", "normalizedStringItemType", "tokenItemType"}:
        raise ValueError(f"Typ braucht einen erweiterten XBRL-Vertrag: {name} ({kind})")
    return value


def build_draft(facts: dict[str, str | None], start: date, end: date, identifier: str, scheme: str) -> bytes:
    if start > end or start.year not in {2025, 2026}:
        raise ValueError("Taxonomie 6.9 nur fuer Periodenbeginn 2025/2026 abgenommen")
    if not identifier.strip() or len(identifier) > 100 or not _xml_text(identifier) or not _xml_text(scheme) or not re.fullmatch(r"https?://[^\s<>]+", scheme):
        raise ValueError("Expliziter Entity-Identifier und URI-Scheme erforderlich")
    for field in CORE_FIELDS:
        if not isinstance(facts.get(field), str) or not facts[field].strip():
            raise ValueError(f"Lokale Entwurfsvoraussetzung fehlt: {field}")
    if facts[CORE_FIELDS[2]] != start.isoformat() or facts[CORE_FIELDS[3]] != end.isoformat():
        raise ValueError("Berichtsperiode und persistierte Exportperiode widersprechen sich")
    if len(facts) > 2000:
        raise ValueError("Maximal 2000 explizite Fakten pro Entwurf")
    values = {name: fact_text(name, value) for name, value in facts.items()}
    root = ET.Element("xbrli:xbrl", {f"xmlns:{key}": uri for key, uri in NS.items()})
    for prefix, suffix in [("de-gcd", "shell"), ("de-gaap-ci", "shell-fiscal")]:
        stem = f"{prefix}-2025-04-01"
        ET.SubElement(root, "link:schemaRef", {"xlink:type": "simple", "xlink:href":
            f"http://www.xbrl.de/taxonomies/{stem}/{stem}-{suffix}.xsd"})
    for context_id, instant in [("duration", False), ("instant", True)]:
        context = ET.SubElement(root, "xbrli:context", {"id": context_id})
        entity = ET.SubElement(context, "xbrli:entity")
        ET.SubElement(entity, "xbrli:identifier", {"scheme": scheme}).text = identifier
        period = ET.SubElement(context, "xbrli:period")
        if instant:
            ET.SubElement(period, "xbrli:instant").text = end.isoformat()
        else:
            ET.SubElement(period, "xbrli:startDate").text = start.isoformat()
            ET.SubElement(period, "xbrli:endDate").text = end.isoformat()
    for unit_id, measure in [("EUR", "iso4217:EUR"), ("pure", "xbrli:pure"), ("shares", "xbrli:shares")]:
        unit = ET.SubElement(root, "xbrli:unit", {"id": unit_id})
        ET.SubElement(unit, "xbrli:measure").text = measure
    for name, value in sorted(values.items()):
        concept = _catalog()[name]
        attributes = {"contextRef": concept["periodType"]}
        if concept["periodType"] not in {"duration", "instant"}:
            raise ValueError(f"Unbekannter Periodentyp: {name}")
        kind = concept["typ"].split(":")[-1]
        if kind in _NUMERIC:
            attributes.update(unitRef="EUR" if kind == "monetaryItemType" else "shares" if kind == "sharesItemType" else "pure", decimals="INF")
        if value is None:
            attributes["xsi:nil"] = "true"
        ET.SubElement(root, name, attributes).text = value
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
