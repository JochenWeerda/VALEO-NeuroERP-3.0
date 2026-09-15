"""FSX-ARTIKEL-IMPORT — Bruecke vom Importformat in das Mengenmodell.

Aus den Gebinderegeln eines Angebots werden **Artikelvarianten**: je
Gebindegroesse ein eigener Stammsatz. So wird es in der Praxis gefuehrt — „WWH
Hycard Sack 25 kg" und „WWH Hycard BigBag 500 kg" sind zwei Artikel mit eigener
Nummer, eigenem Bestand und eigenem Preis. Die Sorteneigenschaften werden dabei
**vererbt**; die Chargen laufen innerhalb einer Variante.

Die Rechnung, die am Ende stimmen muss, ist die aus dem Angebot:
**49 x 25 kg = 1225 kg je Palette** — und zwar nur im Sack-Artikel.

Der zweite Schwerpunkt ist die Trennung: Was eine **Kondition** ist —
Zuschlaege, Ausnahmen, Palettengebuehren — darf nicht in den Einheiten landen.
Die Verpackungsleiter beantwortet „wie viele Kilogramm sind ein BigBag", nicht
„was kostet er".
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from app.core.agrar_units import ArtikelEinheiten, Gebinde, grundeinheit, normalisiere
from app.services.article_import import parse_article_import
from app.services.article_units_bridge import build_article_variants

#: Dieselbe Vorlage wie die Importtests — als Datei, nicht als Import.
#: Ein ``from tests.test_article_import import ...`` waere von einem
#: gleichnamigen Paket in site-packages verdeckt worden.
ANGEBOT = (Path(__file__).parent / "data" / "geno-saaten-angebot.xml").read_text(
    encoding="utf-8"
)

pytestmark = pytest.mark.unit


def _bruecke(xml: str = ANGEBOT):
    ergebnis = parse_article_import(xml)
    return build_article_variants(ergebnis.articles[0], ergebnis.packaging_rules[0])


def _variante(bruecke, einheit: str):
    return next(v for v in bruecke.variants if v.package_unit == einheit)


@pytest.fixture()
def bruecke():
    return _bruecke()


# -- Je Gebindegroesse ein Artikel ---------------------------------------------


def test_jede_gebindegroesse_wird_ein_eigener_stammsatz(bruecke) -> None:
    """Drei Gebinderegeln im Angebot, drei Artikel im Stamm.

    Nicht ein Artikel mit drei Gebinden: Lager, Disposition und Inventur
    unterscheiden Sack und BigBag, auch wenn dieselbe Sorte darin ist.
    """
    assert [v.package_unit for v in bruecke.variants] == [
        "big_bag:1000",
        "big_bag:500",
        "sack:25",
    ]


def test_die_variante_traegt_nur_ihr_eigenes_gebinde(bruecke) -> None:
    sack = _variante(bruecke, "sack:25")
    assert sack.units.faktor("sack:25", "kg") == Decimal(25)
    # Der BigBag ist ein anderer Artikel — in diesem Stammsatz kennt ihn niemand.
    assert not any(g.einheit.startswith("big_bag") for g in sack.units.gebinde)


def test_zwei_bigbags_bleiben_unterscheidbar(bruecke) -> None:
    """Der Fall, der die Bruecke ueberhaupt erst noetig gemacht hat.

    Der Lieferant fuehrt BigBag zu 500 **und** zu 1000 kg. Beide unter
    ``big_bag`` waeren mehrdeutig, und die Umrechnung haette stillschweigend eine
    davon genommen — ohne dass jemand saehe, welche. Als getrennte Stammsaetze
    stellt sich die Frage gar nicht erst.
    """
    assert _variante(bruecke, "big_bag:500").units.faktor("big_bag:500", "kg") == Decimal(500)
    assert _variante(bruecke, "big_bag:1000").units.faktor("big_bag:1000", "kg") == Decimal(1000)
    # Und beide in der Handelsgroesse des Getreidehandels:
    assert _variante(bruecke, "big_bag:500").units.faktor("big_bag:500", "dt") == Decimal(5)
    assert _variante(bruecke, "big_bag:1000").units.faktor("big_bag:1000", "dt") == Decimal(10)


def test_mehrdeutige_gebinde_werden_vom_modell_abgewiesen() -> None:
    """Die Absicherung eine Ebene tiefer — falls die Bruecke es je vergisst."""
    with pytest.raises(ValueError) as fehler:
        ArtikelEinheiten(
            basis_einheit="kg",
            gebinde=(Gebinde("big_bag", Decimal(1000)), Gebinde("big_bag", Decimal(500))),
        )
    assert "Mehrdeutige Gebinde" in str(fehler.value)


def test_der_variantenname_nennt_die_gebindegroesse(bruecke) -> None:
    namen = [v.name for v in bruecke.variants]
    assert all(n.startswith("WWH Hycard") for n in namen)
    assert any("25" in n for n in namen)
    assert len(set(namen)) == 3


# -- Vererbung -----------------------------------------------------------------


def test_sorteneigenschaften_werden_an_jede_variante_vererbt(bruecke) -> None:
    """Die Beize beschreibt die Ware, nicht die Verpackung — also gilt sie ueberall."""
    for variante in bruecke.variants:
        assert variante.article_type == "SAATGUT"
        assert variante.inherited["category"] == "Winterweizen"
        assert variante.inherited["treated"] is True
        assert variante.inherited["treatment_description"] == "Beize lt. Etikett"
        assert variante.inherited["base_unit"] == "kg"


def test_handelseinheit_kommt_aus_den_preisen(bruecke) -> None:
    """Der Lieferant rechnet in kg — beide Preise stehen je Kilogramm."""
    assert all(v.units.handels_einheit == "kg" for v in bruecke.variants)


# -- Die Palette ---------------------------------------------------------------


def test_palette_haengt_nur_an_dem_gebinde_das_sie_stapelt(bruecke) -> None:
    """49 Saecke, nicht 1225 kg — genau so steht es im Angebot.

    Die Palette wird als Vielfaches des **Gebindes** eingetragen, nicht als
    Gewicht. So bleibt sie richtig, wenn sich das Sackgewicht aendert. Und sie
    gehoert in den Sack-Artikel: eine 25-kg-Palette hat im BigBag nichts zu
    suchen.
    """
    sack = _variante(bruecke, "sack:25")
    palette = next(g for g in sack.units.gebinde if g.einheit == "palette:standard_25kg")
    assert palette.faktor == Decimal(49)
    assert palette.je_einheit == "sack:25"

    for einheit in ("big_bag:500", "big_bag:1000"):
        assert not any(
            g.einheit.startswith("palette") for g in _variante(bruecke, einheit).units.gebinde
        )


def test_die_rechnung_aus_dem_angebot_geht_auf(bruecke) -> None:
    """49 x 25 kg = 1225 kg — ueber die Leiter gerechnet, nicht eingetragen."""
    sack = _variante(bruecke, "sack:25")
    assert sack.units.faktor("palette:standard_25kg", "kg") == Decimal(1225)
    assert sack.units.faktor("palette:organic_25kg", "kg") == Decimal(1000)
    # Und quer: eine Standardpalette sind 49 Saecke.
    assert sack.units.faktor("palette:standard_25kg", "sack:25") == Decimal(49)


# -- Konditionen bleiben draussen ----------------------------------------------


def test_zuschlaege_landen_nicht_in_den_einheiten(bruecke) -> None:
    """„BigBag 1000 kg: -1,00 EUR/dt" ist eine Kondition, keine Umrechnung.

    Wer beides vermischt, kann den Preis nicht aendern, ohne die Mengenrechnung
    anzufassen. Sie steht deshalb an der Variante, zu der sie gehoert — und nicht
    an den anderen.
    """
    for variante in bruecke.variants:
        for gebinde in variante.units.gebinde:
            assert not hasattr(gebinde, "adjustment")

    assert any("-1.00 EUR je dt" in k for k in _variante(bruecke, "big_bag:1000").conditions)
    assert any("1.00 EUR je dt" in k for k in _variante(bruecke, "sack:25").conditions)
    # Der 500er ist der Standard: 0,00 ist keine Kondition, sondern die Abwesenheit einer.
    assert _variante(bruecke, "big_bag:500").conditions == []


def test_ausnahme_geht_nicht_verloren(bruecke) -> None:
    """„25-kg-Regel ausgenommen Hybriden" gehoert zur Kondition — und bleibt."""
    assert any("HYBRID=true" in k for k in _variante(bruecke, "sack:25").conditions)


def test_palettengebuehren_gelten_lieferantenweit(bruecke) -> None:
    """Die Tauschpalette ist keine Eigenschaft des Sacks — sie gilt fuer alles."""
    assert any("EURO_EXCHANGE_PALLET" in k for k in bruecke.conditions)
    assert any("BROKEN_PALLET_SURCHARGE" in k for k in bruecke.conditions)


def test_die_vorlage_laeuft_ohne_hinweise_durch(bruecke) -> None:
    assert bruecke.warnings == []


# -- Lose Ware -----------------------------------------------------------------


def test_ohne_gebinderegeln_bleibt_ein_artikel() -> None:
    """Schuettgut ist kein Sonderfall, sondern der Normalfall im Getreidehandel."""
    ergebnis = parse_article_import(ANGEBOT)
    bruecke = build_article_variants(ergebnis.articles[0])

    assert len(bruecke.variants) == 1
    assert bruecke.variants[0].package_unit is None
    assert bruecke.variants[0].name == "WWH Hycard"
    assert bruecke.variants[0].units.faktor("dt", "kg") == Decimal(100)


# -- Was die Bruecke nicht raet ------------------------------------------------


def test_unbekannter_gebindetyp_wird_gemeldet_statt_gebogen() -> None:
    xml = ANGEBOT.replace("<packageType>BAG</packageType>", "<packageType>OKTABIN</packageType>", 1)
    bruecke = _bruecke(xml)

    assert any("OKTABIN" in w for w in bruecke.warnings)
    assert not any(str(v.package_unit).startswith("oktabin") for v in bruecke.variants)
    # Der Rest bleibt brauchbar: die beiden BigBags stehen weiter.
    assert [v.package_unit for v in bruecke.variants] == ["big_bag:1000", "big_bag:500"]


def test_palette_ohne_passendes_gebinde_wird_gemeldet() -> None:
    """Ohne Gebinde ist die Palette nur ein Gewicht, keine Stufe."""
    xml = ANGEBOT.replace(
        "<calculatedNumberOfBags>49</calculatedNumberOfBags>",
        "<calculatedNumberOfBags>50</calculatedNumberOfBags>",
        1,
    )
    bruecke = _bruecke(xml)

    assert any("STANDARD_25KG" in w for w in bruecke.warnings)
    assert not any(
        g.einheit == "palette:standard_25kg" for g in _variante(bruecke, "sack:25").units.gebinde
    )


def test_gebinde_in_fremder_einheit_wird_nicht_uebernommen() -> None:
    """Ein Kanister in Litern passt nicht an einen Artikel, der in kg rechnet."""
    xml = ANGEBOT.replace('<content unit="KG">25</content>', '<content unit="L">25</content>', 1)
    bruecke = _bruecke(xml)

    assert any("nicht uebernommen" in w for w in bruecke.warnings)
    assert not any(v.package_unit == "sack:25" for v in bruecke.variants)


def test_uneinheitliche_preiseinheiten_ergeben_keine_handelsgroesse() -> None:
    """Eine willkuerlich herausgegriffene waere schlimmer als gar keine."""
    xml = ANGEBOT.replace(
        "<priceUnitMeasure>KG</priceUnitMeasure>",
        "<priceUnitMeasure>DT</priceUnitMeasure>",
        1,
    )
    bruecke = _bruecke(xml)
    assert all(v.units.handels_einheit is None for v in bruecke.variants)


# -- Teilbarkeit ---------------------------------------------------------------


def test_saatgut_bleibt_teilbar(bruecke) -> None:
    assert all(v.units.teilbar is True for v in bruecke.variants)


def test_pflanzenschutz_ist_nicht_teilbar() -> None:
    """Die einzige Ableitung, die die Bruecke sich erlaubt — sie folgt aus dem Recht."""
    xml = ANGEBOT.replace("<articleType>SAATGUT</articleType>", "<articleType>PSM</articleType>", 1)
    bruecke = _bruecke(xml)

    assert all(v.units.teilbar is False for v in bruecke.variants)
    assert any("Originalverpackung" in k for k in bruecke.conditions)


# -- Der Varianten-Trenner -----------------------------------------------------


def test_auspraegung_wird_ausdruecklich_getrennt_nicht_geraten() -> None:
    """Ein erster Entwurf deutete eine angehaengte Ziffernfolge als Groesse.

    Das trug Paletten wie ``palette:standard_25kg`` nicht und haette bei jedem
    Gebindenamen mit Zahl im Wort danebengelegen.
    """
    assert grundeinheit("big_bag:500") == "big_bag"
    assert grundeinheit("palette:standard_25kg") == "palette"
    # Ohne Trenner bleibt der Name, wie er ist — nichts wird abgeschnitten.
    assert grundeinheit("big_bag") == "big_bag"


def test_englische_gebindenamen_werden_nur_belegt_uebersetzt() -> None:
    assert normalisiere("BAG") == "sack"
    assert normalisiere("BigBag") == "big_bag"
    assert normalisiere("Pallet") == "palette"
    # Was nicht in der Liste steht, bleibt unbekannt statt gebogen zu werden.
    assert normalisiere("Oktabin") == "oktabin"
