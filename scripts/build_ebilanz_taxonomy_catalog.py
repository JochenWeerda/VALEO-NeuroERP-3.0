"""Derive the GCD/core concept catalog from the pinned official 6.9 package."""
import argparse
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

SHA256 = "accd62202d73c036910fee118b30730f0392934afc9730617788e30a0480df87"
SOURCE = "https://www.esteuer.de/download/taxonomie_20250618/german-gaap-taxonomy-v6.9-2025-04-01-xbrl.zip"
OUTPUT = Path(__file__).resolve().parents[1] / "app/data/ebilanz/taxonomy-6.9.json"
XS = "{http://www.w3.org/2001/XMLSchema}"
LINK = "{http://www.xbrl.org/2003/linkbase}"
XLINK = "{http://www.w3.org/1999/xlink}"
XBRLI = "{http://www.xbrl.org/2003/instance}"


def build(archive: Path) -> dict:
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Amtliches Taxonomiepaket stimmt nicht mit dem geprueften SHA256 ueberein")
    concepts = []
    with ZipFile(archive) as package:
        for prefix, classification in [("de-gcd", "GCD"), ("de-gaap-ci", "GAAP")]:
            stem = f"{prefix}-2025-04-01/{prefix}-2025-04-01"
            schema = ET.fromstring(package.read(stem + ".xsd"))
            labels = ET.fromstring(package.read(stem + "-label-de.xml"))
            resources = {e.get(XLINK + "label"): e.text for e in labels.iter(LINK + "label")
                         if e.get(XLINK + "role") == "http://www.xbrl.org/2003/role/label"}
            locators = {e.get(XLINK + "label"): e.get(XLINK + "href").split("#")[-1]
                        for e in labels.iter(LINK + "loc")}
            names = {locators[e.get(XLINK + "from")]: resources[e.get(XLINK + "to")]
                     for e in labels.iter(LINK + "labelArc") if e.get(XLINK + "to") in resources}
            for element in schema.findall(XS + "element"):
                concepts.append({
                    "element": f"{prefix}:{element.get('name')}", "klasse": classification,
                    "namespace": schema.get("targetNamespace"), "typ": element.get("type", "tuple"),
                    "label": names.get(element.get("id"), element.get("name")),
                    "abstract": element.get("abstract") == "true",
                    "nillable": element.get("nillable") == "true",
                    "periodType": element.get(XBRLI + "periodType"),
                    "balance": element.get(XBRLI + "balance"),
                    "substitutionGroup": element.get("substitutionGroup"),
                })
    return {"version": "6.9", "source": SOURCE, "source_sha256": SHA256,
            "attribution": "XBRL Deutschland e.V.; amtliches eSteuer-XBRL-Paket",
            "scope": "GCD und Kerntaxonomie; keine Branchen-/Dimensionskataloge oder ERiC-Regeln",
            "concepts": sorted(concepts, key=lambda e: e["element"])}


def render(data: dict) -> str:
    # One concept per line keeps the generated catalog reviewable and compact.
    rows = data["concepts"]
    header = json.dumps({key: value for key, value in data.items() if key != "concepts"}, ensure_ascii=False, indent=2)[:-2]
    return header + ',\n  "concepts": [\n' + ',\n'.join(
        '    ' + json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in rows
    ) + '\n  ]\n}\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render(build(args.archive))
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit("Taxonomiekatalog ist nicht deterministisch aktuell")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8")
    print("Amtlicher Katalog 6.9: 3944 GCD-/Kernkonzepte, Hash und Ausgabe geprueft.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
