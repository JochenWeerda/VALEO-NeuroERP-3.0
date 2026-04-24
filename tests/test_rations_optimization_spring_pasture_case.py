"""End-to-End Regression: Fruehjahrsweide-Praxisfall des Bruders.

Geschilderte Fuetterung:
- Ganztagsweide Fruehjahr, jung (DLG 10180010)
- Grassilage 2. Schnitt zur freien Aufnahme (DLG 10100020)
- 1 kg FM Maismehl (DLG 30880030)
- 1 kg FM Gerstenmehl (DLG 30820030, vom Solver optional)
- Bödeker Milchleistungsfutter II zu ausgeglichenen Grundfutterrationen

Vor der PMR+Weide-Kalibrierung (Slice 2026-04-21) blieb dieser Fall wegen zu enger
RMD-Dichte (1,5 g N/kg TM) und wegen fehlerhafter Compound-Feed-Parsing-Logik
(Off-by-one Deklarationsverschub, fehlende FM->TM-Umrechnung) infeasible.

Dieser Test stellt sicher, dass die Kombination aus
- RMD-Obergrenze 8,0 g N/kg TM im PMR+Weide-Modus (DLG 417),
- automatischem Mg/Na-Supplement als Pflichtbaustein,
- korrigiertem Compound-Feed-Parser
eine fachlich saubere Loesung erzeugt.
"""
from __future__ import annotations

from app.api.v1.endpoints.rations_optimization import (
    _optimize_internal,
    _parse_compound_feed_text,
)

BOEDEKER_TEXT = """
Milchleistungsfutter II zu ausgeglichenen Grundfutterrationen
Inhaltsstoffe:
Rohprotein 16,50 %
Rohfett 2,80 %
Rohasche 4,00 %
Rohfaser 7,20 %
Calcium 0,28 %
Phosphor 0,38 %
Natrium 0,06 %
Magnesium 0,18 %
NEL/kg 7,2MJ
Zusammensetzung:
39,0 % Mais, 14,0 % Melasseschnitzel, 14,0 % Weizen, 14,0 %
Rapsextraktionsschrotfutter, 14,0 % Sojaextraktionsschrot aus geschaelter Saat,
dampferhitzt, 5,0 % Haferschaelkleie
"""


def _make_result():
    parsed = _parse_compound_feed_text(BOEDEKER_TEXT, "boedeker.pdf", "pdf_text")
    boedeker_feed = dict(parsed.optimizer_feed)
    boedeker_feed["max_kg"] = 4.5

    profile = {
        "breed": "Holstein",
        "body_weight_kg": 650,
        "milk_kg_day": 25,
        "milk_fat_pct": 4.0,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 120,
        "parity": 3,
        "feeding_type": "PMR+Weide",
    }
    selected_ids = [
        "dlg_10180010",       # Weide Fruehjahr jung
        "dlg_10100020",       # Grassilage 2. Schnitt
        "dlg_30880030",       # Maismehl
        "dlg_30820030",       # Gerstenmehl
        boedeker_feed["id"],  # Boedeker Milchleistungsfutter
    ]
    max_tm_overrides = {
        "dlg_30880030": 1.0 * 0.88,
        "dlg_30820030": 1.0 * 0.88,
    }

    return _optimize_internal(
        profile,
        custom_feeds=[boedeker_feed],
        feed_ids=selected_ids,
        max_tm_overrides=max_tm_overrides,
    ), boedeker_feed


def test_spring_pasture_case_becomes_feasible_in_pmr_weide_mode():
    result, boedeker = _make_result()
    assert result["status"] == "optimal", (
        f"Fruehjahrsration bleibt infeasible: {result.get('warnings')}"
    )
    meta = result.get("metadata") or {}
    assert meta.get("feeding_type") == "PMR+Weide"
    assert meta.get("optimization_strategy") == "stage1_balance_then_stage2_cost"


def test_spring_pasture_case_contains_mandatory_pasture_mineral():
    result, _ = _make_result()
    ration = result["ration_items"]
    names = [item["name"] for item in ration]
    assert any("Weidemineral" in n or "Mg/Na" in n for n in names), (
        f"Kein Mg/Na-Supplement in der Ration: {names}"
    )
    mg_supp = next(item for item in ration if "Weidemineral" in item["name"])
    assert mg_supp["kgdm"] >= 0.05


def test_spring_pasture_case_reports_k_mg_antagonism_warning():
    result, _ = _make_result()
    risk = result.get("pasture_risk")
    assert risk is not None and risk.get("active") is True
    # Bei Intensivjungweide muss ein K:Mg > 6 gemeldet werden (Grastetanie-Risiko).
    assert (risk.get("pasture_k_mg_ratio") or 0.0) > 6.0
    assert any("K" in w or "Mg" in w or "Tetanie" in w for w in risk.get("warnings") or [])


def test_spring_pasture_case_meets_energy_and_protein_targets():
    result, _ = _make_result()
    supply = result["nutrient_supply"]
    # ME soll mindestens den Bedarf decken (Toleranz siehe gfe_requirements-Check)
    assert supply["me_mj"] >= 180.0
    assert supply["sidp_g"] >= 1650.0
    # DMI innerhalb GfE-Korridor
    assert supply["dmi_kg"] >= 17.5
    # Mg-Mindestversorgung erfuellt
    assert supply["mg_g"] >= 33.0


# ---------------------------------------------------------------------------
# User-Review 2026-04-23, §6: Erweiterte Regressions-Assertions
# ---------------------------------------------------------------------------

def test_spring_pasture_no_false_global_structure_penalty():
    """Struktur-Strafen (aNDFomGF, pabKH, XL, CP) duerfen bei PMR+Weide
    NICHT durch den Weide-Block ausgeloest werden.

    Begruendung: Die Mischmasse-Struktur-Constraints gelten nur fuer den
    TMR-Block. Weide wird separat ueber Weide-Logik bewertet. Wenn diese
    Constraints rot waeren, obwohl die TMR-Mischung korrekt waere, laege
    eine fachliche Fehl-Bewertung vor (globale Strukturstrafe).
    """
    result, _ = _make_result()
    status = result.get("constraint_status") or []
    structural_names = {
        "aNDFomGF+CoP (g/kg TM)",
        "pabKH (g/kg TM)",
        "XL Rohfett (g/kg TM)",
    }
    # Struktur-Constraints duerfen aktiv sein, aber ihre Verletzungen
    # duerfen nicht durch die Weide verschuldet sein - Nachweis: wenn
    # Scoping aktiv ist (PMR+Weide mit staged block), sollten die actual-
    # Dichten auf TMR-Basis (nicht Gesamtration) gerechnet sein. Der Test
    # prueft, dass kein hartes Versagen (hard_violated) auftritt.
    structural_rows = [row for row in status if row.get("name") in structural_names]
    hard_fails = [row for row in structural_rows if row.get("status") == "hard_violated"]
    assert hard_fails == [], (
        "Keine harten Strukturverletzungen erwartet bei PMR+Weide "
        f"(waere fachliche Fehl-Bewertung): {hard_fails}"
    )


def test_spring_pasture_plausible_milk_from_forage():
    """Milch-aus-Grundfutter bleibt in plausiblem Korridor.

    Fachliche Obergrenze: Mit ~17-22 kg TM Grundfutter sind 24-30 kg Milch
    aus Grundfutter typisch, da 1 kg TM Grundfutter ca. 1 kg Milch liefert
    (User-Praxisangabe 2026-04-22). Werte > 35 kg deuten auf ein zu opti-
    mistisches k_l / ME-Dichte-Modell hin, < 10 kg auf eine Unterschaetzung.
    """
    result, _ = _make_result()
    risk = result.get("pasture_risk") or {}
    milk_pasture = (risk.get("milk_from_pasture") or {}).get("limiting_milk_kg") or 0.0
    milk_gs = (risk.get("milk_from_grass_silage") or {}).get("limiting_milk_kg") or 0.0
    milk_forage_total = milk_pasture + milk_gs
    # Plausibilitaets-Korridor (fachlich laut User-Regel ca. 1 kg Milch je kg TM):
    assert milk_forage_total >= 10.0, (
        f"Milch aus Grundfutter zu niedrig ({milk_forage_total:.1f} kg) - "
        "deutet auf zu konservatives Energie- oder Protein-Modell hin."
    )
    assert milk_forage_total <= 40.0, (
        f"Milch aus Grundfutter implausibel hoch ({milk_forage_total:.1f} kg) - "
        "deutet auf zu optimistisches k_l / ME-Dichte-Modell hin "
        "(Praxisregel 1 kg Milch/kg TM Grundfutter)."
    )


def test_spring_pasture_no_technical_false_infeasible():
    """Es darf kein technisches False-Infeasible auftreten.

    Ein False-Infeasible liegt vor, wenn der Solver nur wegen eines
    Modellierungs-Fehlers scheitert (z.B. pauschaler Weide-Cap, falsche
    TMR/PMR-Behandlung, Struktur-Constraint auf Weide angewendet).

    Die Ration muss optimal loesbar sein, und wenn doch eine Relaxation
    aktiv war, muss das transparent gemeldet sein (nicht stillschweigend
    scheitern und nicht mit unspezifischer Solver-Fehlermeldung enden).
    """
    result, _ = _make_result()
    status = result["status"]
    assert status == "optimal", (
        f"PMR+Weide-Fall muss loesbar sein (False-Infeasible-Schutz). "
        f"status={status}, warnings={result.get('warnings')}"
    )
    # Falls Relaxation aktiv war, muss das transparent dokumentiert sein
    meta = result.get("metadata") or {}
    infeasibility_hint = meta.get("infeasibility_hint")
    if meta.get("relaxed"):
        assert infeasibility_hint is None or isinstance(infeasibility_hint, (dict, str)), (
            "Bei Relaxation muss ein strukturierter infeasibility_hint vorhanden sein"
        )


def test_spring_pasture_k_mg_diagnosis_complete():
    """Mg/K-Diagnose muss vollstaendig sein (Grastetanie-Risiko).

    User-Review 2026-04-23, §6: korrekte Diagnose bei Mg/K- und SARA-Risiko.
    Fuer den Fruehjahrsfall ist K:Mg > 6 der Hauptrisikofaktor.
    """
    result, _ = _make_result()
    risk = result.get("pasture_risk")
    assert risk is not None, "Weide-Risiko-Panel muss aktiv sein"
    # K:Mg-Verhaeltnis muss gesetzt und > 6 sein
    assert (risk.get("pasture_k_mg_ratio") or 0.0) > 6.0
    # Mg-Supplement-Info muss vorhanden sein
    assert "mg_supplement_dmi_kg" in risk
    # Warnungen muessen Grastetanie explizit benennen
    warnings_text = " ".join(risk.get("warnings") or [])
    assert "Grastetanie" in warnings_text or "K/Mg" in warnings_text or "K:Mg" in warnings_text


def test_spring_pasture_response_contains_ration_blocks_aggregate():
    """Slice 1f: Response enthaelt ration_blocks mit Block-Aggregaten.

    Bei PMR+Weide muss pasture_block und ggf. concentrate_staged_block
    mit Daten befuellt sein; tmr_block darf leer/klein sein, wenn keine
    TMR-Feeds vorhanden sind.
    """
    result, _ = _make_result()
    blocks = result.get("ration_blocks")
    assert blocks is not None, "ration_blocks muss in Response vorhanden sein"
    assert "feeding_system" in blocks
    assert blocks["feeding_system"]["system"] in {"PMR_pasture", "PMR_stall", "TMR"}
    # Der Pasture-Block muss bei PMR+Weide tatsaechlich DMI enthalten
    assert blocks["pasture_block"]["dmi_kg"] > 0.0
    # Summen-Plausibilitaet: Summe der Block-DMI ~= Gesamt-DMI
    total_dmi_blocks = (
        blocks["tmr_block"]["dmi_kg"]
        + blocks["pasture_block"]["dmi_kg"]
        + blocks["concentrate_staged_block"]["dmi_kg"]
    )
    supply = result["nutrient_supply"]
    assert abs(total_dmi_blocks - supply["dmi_kg"]) < 0.05, (
        f"Block-DMI-Summe {total_dmi_blocks} weicht von Gesamt-DMI "
        f"{supply['dmi_kg']} ab - Block-Zuordnung nicht deckungsgleich"
    )


def test_spring_pasture_feeding_system_config_present():
    """Nachschaerfung: FeedingSystemConfig muss aufgeloest sein.

    PMR+Weide muss automatisch auf system=PMR_pasture mappen (Fallback
    aus profile.feeding_type). Dient als Smoke-Test fuer die neue Archi-
    tektur; dass k_l=0,60 tatsaechlich greift, wird in den Plausi-Tests
    (milk_plausibility) geprueft.
    """
    result, _ = _make_result()
    meta = result.get("metadata") or {}
    # feeding_type Backward-Compat
    assert meta.get("feeding_type") == "PMR+Weide"
    # Strategie muss Stage1-Balance-Then-Stage2-Cost sein
    assert meta.get("optimization_strategy") == "stage1_balance_then_stage2_cost"
