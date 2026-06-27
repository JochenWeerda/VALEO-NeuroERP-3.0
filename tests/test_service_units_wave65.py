"""Wave 65 — Unit-Tests fuer kaeufergruppe (Käufergruppen-Klassifikation, reines Domain-Modell)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# kaeufergruppe  (pure domain logic — keine DB, kein HTTP)
# ---------------------------------------------------------------------------

def _sig(**kw):
    from app.services.kaeufergruppe import Verhaltenssignale
    return Verhaltenssignale(**kw)


@pytest.mark.unit
def test_klassifiziere_schlafender_potenzialkunde() -> None:
    from app.services.kaeufergruppe import klassifiziere, BuyingGroup
    s = _sig(bedarf_gesamt_eur=50000, deckung_gesamt_pct=5, angebote_12m=1)
    result = klassifiziere(s)
    assert result.gruppe == BuyingGroup.SCHLAFENDER_POTENZIALKUNDE
    assert result.confidence > 0.5
    assert len(result.begruendung) > 0


@pytest.mark.unit
def test_klassifiziere_preisabfrager() -> None:
    from app.services.kaeufergruppe import klassifiziere, BuyingGroup
    s = _sig(preisabfragen_12m=12, abschlussquote=0.15)
    result = klassifiziere(s)
    assert result.gruppe == BuyingGroup.PREISABFRAGER


@pytest.mark.unit
def test_klassifiziere_preisverhandler() -> None:
    from app.services.kaeufergruppe import klassifiziere, BuyingGroup
    s = _sig(angebote_12m=8, abschlussquote=0.55, rabatt_schnitt=0.06)
    result = klassifiziere(s)
    assert result.gruppe == BuyingGroup.PREISVERHANDLER


@pytest.mark.unit
def test_klassifiziere_strategischer_stammkunde() -> None:
    from app.services.kaeufergruppe import klassifiziere, BuyingGroup
    s = _sig(deckung_gesamt_pct=80, kauffrequenz_12m=15, rabatt_schnitt=0.01)
    result = klassifiziere(s)
    assert result.gruppe == BuyingGroup.STRATEGISCHER_STAMMKUNDE


@pytest.mark.unit
def test_klassifiziere_beziehungskaeufer() -> None:
    from app.services.kaeufergruppe import klassifiziere, BuyingGroup
    s = _sig(kauffrequenz_12m=10, preisabfragen_12m=2, deckung_gesamt_pct=60)
    result = klassifiziere(s)
    assert result.gruppe == BuyingGroup.BEZIEHUNGSKAEUFER


@pytest.mark.unit
def test_klassifiziere_saison_ergaenzer() -> None:
    from app.services.kaeufergruppe import klassifiziere, BuyingGroup
    s = _sig(saison_konzentration=0.8, kauffrequenz_12m=4)
    result = klassifiziere(s)
    assert result.gruppe == BuyingGroup.SAISON_ERGAENZER


@pytest.mark.unit
def test_klassifiziere_risiko_streuer() -> None:
    from app.services.kaeufergruppe import klassifiziere, BuyingGroup
    s = _sig(multi_lieferant_wahrsch=0.75, deckung_gesamt_pct=40)
    result = klassifiziere(s)
    assert result.gruppe == BuyingGroup.RISIKO_STREUER


@pytest.mark.unit
def test_klassifiziere_opportunist() -> None:
    from app.services.kaeufergruppe import klassifiziere, BuyingGroup
    s = _sig(abschlussquote=0.25, kauffrequenz_12m=3, multi_lieferant_wahrsch=0.6)
    result = klassifiziere(s)
    assert result.gruppe == BuyingGroup.OPPORTUNIST


@pytest.mark.unit
def test_klassifiziere_unbekannt_for_empty_signals() -> None:
    from app.services.kaeufergruppe import klassifiziere, BuyingGroup
    s = _sig()
    result = klassifiziere(s)
    assert result.gruppe == BuyingGroup.UNBEKANNT
    assert result.confidence < 0.5


@pytest.mark.unit
def test_buying_group_enum_values() -> None:
    from app.services.kaeufergruppe import BuyingGroup
    assert BuyingGroup.PREISABFRAGER.value == "preisabfrager_ohne_abschluss"
    assert BuyingGroup.STRATEGISCHER_STAMMKUNDE.value == "strategischer_stammkunde"


@pytest.mark.unit
def test_gruppen_contains_all_buying_groups() -> None:
    from app.services.kaeufergruppe import GRUPPEN, BuyingGroup
    for group in BuyingGroup:
        if group != BuyingGroup.UNBEKANNT:
            assert group in GRUPPEN, f"{group} fehlt in GRUPPEN"


@pytest.mark.unit
def test_profil_returns_gruppenprofile() -> None:
    from app.services.kaeufergruppe import profil, BuyingGroup, GruppenProfil
    p = profil(BuyingGroup.PREISVERHANDLER)
    assert isinstance(p, GruppenProfil)
    assert 0.0 < p.ziel_anteil_min < p.ziel_anteil_max <= 1.0


@pytest.mark.unit
def test_ziel_anteil_returns_midpoint() -> None:
    from app.services.kaeufergruppe import ziel_anteil, BuyingGroup, profil
    p = profil(BuyingGroup.BEZIEHUNGSKAEUFER)
    za = ziel_anteil(BuyingGroup.BEZIEHUNGSKAEUFER)
    midpoint = (p.ziel_anteil_min + p.ziel_anteil_max) / 2
    assert abs(za - midpoint) < 0.01


@pytest.mark.unit
def test_bewerte_luecke_realistic_gap() -> None:
    from app.services.kaeufergruppe import bewerte_luecke, BuyingGroup, LueckenBewertung
    lk = bewerte_luecke(
        bedarf_eur=100_000,
        ist_eur=30_000,
        group=BuyingGroup.BEZIEHUNGSKAEUFER,
        produktgruppe_key="getreide",
        marge_faktor=0.15,
    )
    assert isinstance(lk, LueckenBewertung)
    assert lk.realistische_luecke_eur >= 0
    assert lk.prioritaet >= 0
