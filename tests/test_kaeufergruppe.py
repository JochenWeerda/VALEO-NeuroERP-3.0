"""Unit-Tests für Käufergruppen-Logik + realistisch gewinnbare Bedarfslücke."""

import pytest

from app.services.kaeufergruppe import (
    BuyingGroup,
    Verhaltenssignale,
    bewerte_luecke,
    grenzaufwand_faktor,
    klassifiziere,
    profil,
    ziel_anteil,
    SAETTIGUNG_SCHWELLE,
)

pytestmark = pytest.mark.unit


# ── Zielanteil ────────────────────────────────────────────────────────────────
def test_ziel_anteil_alleinlieferant_ist_nicht_standard():
    # Selbst der loyalste Typ zielt nicht auf 100 %.
    assert ziel_anteil(BuyingGroup.STRATEGISCHER_STAMMKUNDE) < 1.0
    assert ziel_anteil(BuyingGroup.STRATEGISCHER_STAMMKUNDE) <= 0.97


def test_ziel_anteil_risiko_streuer_unter_stammkunde():
    assert ziel_anteil(BuyingGroup.RISIKO_STREUER) < ziel_anteil(BuyingGroup.STRATEGISCHER_STAMMKUNDE)


def test_produktgruppen_modifikator_senkt_standardware():
    # Dünger (Standardware, stark verglichen) < Mineralfutter (beratungsintensiv) für denselben Typ.
    g = BuyingGroup.BEZIEHUNGSKAEUFER
    assert ziel_anteil(g, "duenger_marktfrucht") < ziel_anteil(g, "mineral_spezial")


def test_ziel_anteil_clamping():
    for g in BuyingGroup:
        for pg in ("kraftfutter", "mineral_spezial", "duenger_marktfrucht", None):
            za = ziel_anteil(g, pg)
            assert 0.30 <= za <= 0.97


# ── Grenzaufwand (abnehmender Grenzertrag) ────────────────────────────────────
def test_grenzaufwand_steigt_ueber_saettigung():
    g = BuyingGroup.PREISVERHANDLER
    low = grenzaufwand_faktor(g, 40)
    at = grenzaufwand_faktor(g, SAETTIGUNG_SCHWELLE * 100)
    high = grenzaufwand_faktor(g, 95)
    assert low == at  # bis zur Schwelle konstant
    assert high > at  # darüber überproportional teurer


# ── Lückenbewertung ───────────────────────────────────────────────────────────
def test_realistische_luecke_kleiner_als_theoretische():
    b = bewerte_luecke(100000, 30000, BuyingGroup.RISIKO_STREUER, "kraftfutter")
    assert b.theoretische_luecke_eur == 70000
    # Zielanteil < 100 % → realistische Lücke deutlich kleiner als theoretische.
    assert b.realistische_luecke_eur < b.theoretische_luecke_eur
    # geschützte + Ziel ergeben den Bedarf.
    assert b.geschuetzte_luecke_eur + b.ziel_umsatz_eur == pytest.approx(b.bedarf_eur, abs=2)


def test_realistische_luecke_null_wenn_ist_ueber_ziel():
    # Ist über dem realistischen Zielumsatz → keine echte Chance mehr.
    b = bewerte_luecke(100000, 90000, BuyingGroup.PREISVERHANDLER, "kraftfutter")
    assert b.realistische_luecke_eur == 0
    assert b.theoretische_luecke_eur == 10000  # rechnerisch bleibt eine Lücke


def test_geschuetzte_luecke_bei_streuer_groesser():
    streuer = bewerte_luecke(100000, 0, BuyingGroup.RISIKO_STREUER, "kraftfutter")
    stamm = bewerte_luecke(100000, 0, BuyingGroup.STRATEGISCHER_STAMMKUNDE, "kraftfutter")
    assert streuer.geschuetzte_luecke_eur > stamm.geschuetzte_luecke_eur


def test_prioritaet_sinkt_nahe_saettigung():
    # Gleicher Typ/Gruppe, gleiche absolute Lücke-Basis, aber hohe Ist-Deckung →
    # höherer Grenzaufwand + kleinere realistische Lücke → geringere Priorität.
    niedrig_gedeckt = bewerte_luecke(100000, 10000, BuyingGroup.BEZIEHUNGSKAEUFER, "mineral_spezial")
    hoch_gedeckt = bewerte_luecke(100000, 80000, BuyingGroup.BEZIEHUNGSKAEUFER, "mineral_spezial")
    assert niedrig_gedeckt.prioritaet > hoch_gedeckt.prioritaet


def test_marge_erhoeht_prioritaet():
    low = bewerte_luecke(100000, 0, BuyingGroup.PREISVERHANDLER, "kraftfutter", marge_faktor=0.9)
    high = bewerte_luecke(100000, 0, BuyingGroup.PREISVERHANDLER, "kraftfutter", marge_faktor=1.6)
    assert high.prioritaet > low.prioritaet


# ── Klassifikation ────────────────────────────────────────────────────────────
def test_klassifiziere_preisabfrager():
    s = Verhaltenssignale(preisabfragen_12m=12, abschlussquote=0.1, angebote_12m=10)
    k = klassifiziere(s)
    assert k.gruppe == BuyingGroup.PREISABFRAGER
    assert "Preisabfrage" in k.begruendung or "Preisanker" in k.begruendung
    assert 0 < k.confidence <= 1


def test_klassifiziere_preisverhandler():
    s = Verhaltenssignale(angebote_12m=8, abschlussquote=0.62, rabatt_schnitt=0.05)
    assert klassifiziere(s).gruppe == BuyingGroup.PREISVERHANDLER


def test_klassifiziere_stammkunde():
    s = Verhaltenssignale(deckung_gesamt_pct=82, kauffrequenz_12m=14, rabatt_schnitt=0.02)
    assert klassifiziere(s).gruppe == BuyingGroup.STRATEGISCHER_STAMMKUNDE


def test_klassifiziere_schlafender_potenzialkunde():
    s = Verhaltenssignale(bedarf_gesamt_eur=50000, deckung_gesamt_pct=5, angebote_12m=1)
    assert klassifiziere(s).gruppe == BuyingGroup.SCHLAFENDER_POTENZIALKUNDE


def test_klassifiziere_risiko_streuer():
    s = Verhaltenssignale(multi_lieferant_wahrsch=0.75, deckung_gesamt_pct=45, kauffrequenz_12m=6, preisabfragen_12m=4)
    assert klassifiziere(s).gruppe == BuyingGroup.RISIKO_STREUER


def test_klassifiziere_unbekannt_bei_duenner_datenlage():
    k = klassifiziere(Verhaltenssignale())
    assert k.gruppe == BuyingGroup.UNBEKANNT
    assert k.confidence < 0.5


def test_jede_klassifikation_hat_begruendung():
    cases = [
        Verhaltenssignale(preisabfragen_12m=12, abschlussquote=0.1, angebote_12m=10),
        Verhaltenssignale(deckung_gesamt_pct=82, kauffrequenz_12m=14, rabatt_schnitt=0.02),
        Verhaltenssignale(),
    ]
    for s in cases:
        assert klassifiziere(s).begruendung.strip()


def test_profil_fallback_bei_unbekanntem_string():
    assert profil("gibt_es_nicht").label == profil(BuyingGroup.UNBEKANNT).label


# ── Austauschbarer Klassifikator (#1) ─────────────────────────────────────────
def test_rule_based_klassifikator_entspricht_pure_funktion():
    from app.services.kaeufer_klassifikator import RuleBasedKlassifikator
    s = Verhaltenssignale(preisabfragen_12m=12, abschlussquote=0.1, angebote_12m=10)
    assert RuleBasedKlassifikator().klassifiziere(s).gruppe == klassifiziere(s).gruppe


def test_llm_klassifikator_faellt_ohne_key_auf_regeln_zurueck(monkeypatch):
    from app.services.kaeufer_klassifikator import LLMKlassifikator
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    s = Verhaltenssignale(deckung_gesamt_pct=82, kauffrequenz_12m=14, rabatt_schnitt=0.02)
    kl = LLMKlassifikator().klassifiziere(s)
    assert kl.gruppe == BuyingGroup.STRATEGISCHER_STAMMKUNDE  # = Regelfall


def test_klassifiziere_mit_quelle_ohne_key_ist_rule_based(monkeypatch):
    from app.services.kaeufer_klassifikator import klassifiziere_mit
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    _kl, source = klassifiziere_mit(Verhaltenssignale(preisabfragen_12m=12, abschlussquote=0.1, angebote_12m=10), prefer_ai=True)
    assert source == "rule_based"


# ── Echte Signal-Abbildung (#3) ───────────────────────────────────────────────
def test_signale_aus_werten_abschlussquote_und_multi():
    from app.services.kaeufer_signal_service import signale_aus_werten
    s = signale_aus_werten(preisanfragen_12m=4, angebote_12m=6, bestellungen_12m=3,
                           gruppen_bezogen=5, deckung_pct=20, bedarf_eur=50000)
    assert s.abschlussquote == pytest.approx(3 / 9, abs=0.01)
    # niedrige Deckung → hohe Mehrlieferanten-Wahrscheinlichkeit
    assert s.multi_lieferant_wahrsch > 0.7
    assert s.kauffrequenz_12m == 5


def test_signale_aus_werten_hohe_deckung_senkt_multi():
    from app.services.kaeufer_signal_service import signale_aus_werten
    s = signale_aus_werten(preisanfragen_12m=0, angebote_12m=0, bestellungen_12m=0,
                           gruppen_bezogen=8, deckung_pct=90, bedarf_eur=100000)
    assert s.multi_lieferant_wahrsch < 0.4
    assert s.abschlussquote == 0.0  # keine Interaktionen
