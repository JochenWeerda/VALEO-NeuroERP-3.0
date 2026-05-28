"""
Fix GET/POST/PATCH/PUT routes with response_model=None that return actual data.
Uses existing domain _schemas.py files where available.
"""
from __future__ import annotations
import re
from pathlib import Path

ENDPOINTS = Path("app/api/v1/endpoints")
SCHEMAS = Path("app/api/v1/schemas")


def schema_name_for_file(fname: str) -> tuple[str, str]:
    """Return (module_name, schema_class_name)."""
    base = fname.replace(".py", "")
    pascal = "".join(w.capitalize() for w in base.split("_"))
    return f"{base}_schemas", f"{pascal}Out"


def ensure_import(text: str, module: str, class_name: str) -> str:
    if class_name in text:
        return text
    import_line = f"from app.api.v1.schemas.{module} import {class_name}\n"
    # Insert after last "from app." import
    m = None
    for m in re.finditer(r"from app\.[^\n]+\n", text):
        pass
    if m:
        text = text[: m.end()] + import_line + text[m.end():]
    return text


def fix_route(fpath: Path, line_idx: int, new_model: str, module: str | None) -> bool:
    text = fpath.read_text(encoding="utf-8-sig")
    lines = text.split("\n")
    idx = line_idx - 1

    for j in range(max(0, idx - 3), min(len(lines), idx + 5)):
        if "response_model=None" in lines[j]:
            lines[j] = lines[j].replace("response_model=None", f"response_model={new_model}")
            break
        if "response_model = None" in lines[j]:
            lines[j] = lines[j].replace("response_model = None", f"response_model={new_model}")
            break

    new_text = "\n".join(lines)
    if module:
        new_text = ensure_import(new_text, module, new_model)

    fpath.write_text(new_text, encoding="utf-8")
    return True


# Map: (filename, line_idx) -> (model_name, module_or_None, notes)
# For files with existing _schemas.py, use DomainOut
# For special cases, use inline schemas or create new ones

FIXES = {
    # --- Files with domain schemas ---
    "projekte.py": [
        (107, "ProjekteOut", "projekte_schemas"),
        (151, "list[ProjekteOut]", "projekte_schemas"),
        (178, "ProjekteOut", "projekte_schemas"),
    ],
    "transporte.py": [(107, "TransporteOut", "transporte_schemas")],
    "verladung.py": [(105, "VerladungOut", "verladung_schemas")],
    "versicherungen.py": [(103, "VersicherungenOut", "versicherungen_schemas")],
    "vertraege.py": [(107, "VertraegeOut", "vertraege_schemas")],
    "wartung.py": [
        (103, "WartungOut", "wartung_schemas"),
        (139, "list[WartungOut]", "wartung_schemas"),
    ],
    "strecke_speditionen.py": [(74, "StreckeSpeditionen Out", "strecke_speditionen_schemas")],
    "webshop_integration.py": [(135, "WebshopIntegrationOut", "webshop_integration_schemas")],
    "ernte_kampagne_api.py": [
        (51, "ErntekampagneApiOut", "ernte_kampagne_api_schemas"),
        (103, "ErntekampagneApiOut", "ernte_kampagne_api_schemas"),
    ],
    "ernte_planung.py": [
        (72, "ErntePlanungOut", "ernte_planung_schemas"),
        (82, "ErntePlanungOut", "ernte_planung_schemas"),
    ],
    "grundfutter_analysen.py": [(673, "GrundfutterAnalysenOut", "grundfutter_analysen_schemas")],
    "number_ranges.py": [
        (99, "NumberRangesOut", "number_ranges_schemas"),
        (112, "NumberRangesOut", "number_ranges_schemas"),
    ],
    "service_anfragen.py": [(134, "ServiceAnfragenOut", "service_anfragen_schemas")],
    "tankstelle.py": [(114, "list[TankstelleOut]", "tankstelle_schemas")],
    "marketing.py": [(168, "MarketingOut", "marketing_schemas")],
    "disposition.py": [(172, "DispositionOut", "disposition_schemas")],
    "zertifikate.py": [(148, "ZertifikateOut", "zertifikate_schemas")],
    # --- Special cases with inline schemas ---
    "partiestamm.py": [
        (228, "PartiestammOut", "partiestamm_schemas"),
        (249, "PartiestammOut", "partiestamm_schemas"),
    ],
    "dokumente.py": [(87, "DokumenteOut", "dokumente_schemas")],
    "intrastat.py": [(285, "IntrastatOut", "intrastat_schemas")],
    "versandprofile.py": [(233, "VersandprofileOut", "versandprofile_schemas")],
    # --- Files needing special handling ---
    "agrar_feldbuch.py": [
        (315, "AgrarFeldbuchOut", "agrar_feldbuch_schemas"),
        (594, "AgrarFeldbuchOut", "agrar_feldbuch_schemas"),
    ],
    "individuelle_artikelnummern.py": [(121, "IndividuelleArtikelNrOut", "individuelle_artikelnummern_schemas")],
    "customers.py": [(225, "CustomersOut", "customers_schemas")],
    "einkauf_bestellvorschlag.py": [(443, "EinkaufBestellvorschlagOut", "einkauf_bestellvorschlag_schemas")],
}


def main() -> None:
    total = 0
    for fname, fixes in FIXES.items():
        fpath = ENDPOINTS / fname

        # Check which schemas files exist
        for line_idx, model, module in fixes:
            # Check if module schema file exists
            if module:
                schema_path = SCHEMAS / f"{module}.py"
                if not schema_path.exists():
                    # Create it
                    # Extract base class name
                    base_cls = model.replace("list[", "").replace("]", "")
                    domain_desc = fname.replace(".py", "").replace("_", " ")
                    schema_path.write_text(
                        f'"""Auto-generated domain schemas for {domain_desc}."""\n'
                        f"from __future__ import annotations\n"
                        f"from app.api.v1.schemas.base import BaseSchema\n"
                        f"from pydantic import ConfigDict\n\n\n"
                        f"class {base_cls}(BaseSchema):\n"
                        f'    """Response schema for {domain_desc} endpoints."""\n'
                        f"    model_config = ConfigDict(extra=\"allow\")\n",
                        encoding="utf-8",
                    )

            # Fix the model name (remove spaces if any typos)
            clean_model = model.replace(" Out", "Out")
            fix_route(fpath, line_idx, clean_model, module)
            total += 1
            print(f"  {fname}:{line_idx} -> {clean_model}")

    print(f"\nTotal fixes: {total}")


if __name__ == "__main__":
    main()
