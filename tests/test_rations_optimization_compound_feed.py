from app.api.v1.endpoints.rations_optimization import _parse_compound_feed_text


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


def test_parse_compound_feed_text_recovers_declared_and_matched_components():
    parsed = _parse_compound_feed_text(BOEDEKER_TEXT, "boedeker.pdf", "pdf_text")

    assert parsed.product_name.startswith("Milchleistungsfutter II")
    assert parsed.declared_analysis.crude_protein_pct == 16.5
    assert parsed.declared_analysis.nel_mj_kg == 7.2
    assert len(parsed.composition) >= 5

    matched_ids = {component.matched_feed_id for component in parsed.composition if component.matched_feed_id}
    assert "dlg_30880030" in matched_ids  # Mais, Korn
    assert "dlg_30940030" in matched_ids  # Melasseschnitzel
    assert "dlg_31190030" in matched_ids  # Weizen
    assert "dlg_30970130" in matched_ids  # Rapsextraktionsschrot
    assert "dlg_31060030" in matched_ids  # Sojaextraktionsschrot, geschaelte Saat
    assert "dlg_30850030" in matched_ids  # Haferschaelkleie

    assert parsed.gfe2023_estimate.me_fan1_mj_kgdm is not None
    assert parsed.gfe2023_estimate.sidp_g_kgdm is not None
    assert parsed.gfe2023_estimate.match_coverage_pct >= 95.0
    assert parsed.optimizer_feed["id"].startswith("compound_")
    assert parsed.optimizer_feed["_source"] == "compound_upload"


def test_parse_compound_feed_text_declared_values_do_not_shift():
    """Regression: Das Off-by-one-Matching im Fliesstext hatte zuvor die Werte
    um eine Zeile verschoben (z.B. Rohfett = 16,5 statt 2,8). Diese Absicherung
    stellt sicher, dass jede Deklaration genau dem richtigen Label zugeordnet wird.
    """
    parsed = _parse_compound_feed_text(BOEDEKER_TEXT, "boedeker.pdf", "pdf_text")
    da = parsed.declared_analysis
    assert da.crude_protein_pct == 16.5
    assert da.crude_fat_pct == 2.8
    assert da.crude_ash_pct == 4.0
    assert da.crude_fiber_pct == 7.2
    assert da.calcium_pct == 0.28
    assert da.phosphorus_pct == 0.38
    assert da.sodium_pct == 0.06
    assert da.magnesium_pct == 0.18


def test_parse_compound_feed_text_optimizer_feed_is_physically_plausible():
    """Regression: zuvor fuehrten Off-by-one + fehlende FM->TM-Umrechnung zu
    physikalisch unmoeglichen Werten (ME = 15,4 MJ/kg TM, XL = 165 g/kg TM,
    Ca = 72 g/kg TM). Die Grenzen hier bilden die biologische Plausibilitaet ab.
    """
    parsed = _parse_compound_feed_text(BOEDEKER_TEXT, "boedeker.pdf", "pdf_text")
    of = parsed.optimizer_feed
    # ME Milchleistungsfutter realistisch 11-13.5 MJ/kg TM
    assert 10.5 < of["me"] < 13.8, f"ME unplausibel: {of['me']}"
    # Rohfett ~ 28 g/kg FM / 0.887 ~= 31 g/kg TM
    assert 25.0 < of["xl"] < 45.0, f"XL unplausibel: {of['xl']}"
    # Rohprotein ~ 165 g/kg FM / 0.887 ~= 186 g/kg TM
    assert 170.0 < of["cp"] < 210.0, f"CP unplausibel: {of['cp']}"
    # Ca ~ 2.8 g/kg FM / 0.887 ~= 3.2 g/kg TM
    assert 2.0 < of["ca"] < 6.0, f"Ca unplausibel: {of['ca']}"
    # Mg ~ 1.8 g/kg FM / 0.887 ~= 2.0 g/kg TM
    assert 1.0 < of["mg"] < 3.5, f"Mg unplausibel: {of['mg']}"
    # Na ~ 0.6 g/kg FM / 0.887 ~= 0.68 g/kg TM
    assert 0.3 < of["na"] < 1.5, f"Na unplausibel: {of['na']}"
    # P ~ 3.8 g/kg FM / 0.887 ~= 4.3 g/kg TM
    assert 3.0 < of["p"] < 6.0, f"P unplausibel: {of['p']}"


def test_parse_compound_feed_text_fm_to_tm_conversion_applied():
    """Stellt sicher, dass Deklaration (% FM) konsistent durch dm_frac geteilt
    und damit auf g/kg TM umgerechnet wird."""
    parsed = _parse_compound_feed_text(BOEDEKER_TEXT, "boedeker.pdf", "pdf_text")
    of = parsed.optimizer_feed
    dm_frac = of["dm_frac"]
    assert 0.85 <= dm_frac <= 0.92
    # cp_g_kg_TM soll mindestens 10% groesser sein als cp_pct*10 (=g/kg FM)
    cp_fm = 16.5 * 10.0
    assert of["cp"] > cp_fm * 1.05, (
        f"CP ({of['cp']}) wurde nicht auf TM-Basis umgerechnet"
    )
