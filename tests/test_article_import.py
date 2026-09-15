"""FSX-ARTIKEL-IMPORT — das kanonische Zwischenformat.

Die Vorlage ist das Angebot **GENO-Saaten / WWH Hycard**. Es wird hier
vollstaendig durchgespielt, weil daran die Trennung der fuenf Ebenen haengt:
„25 kg" ist keine Eigenschaft der Sorte, und „franko" keine Eigenschaft des
Artikels.

Der zweite Schwerpunkt sind die Stellen, an denen der Parser **widersprechen**
soll: ein Preis ohne Bezug, ein Zuschlag ohne Bezugsgroesse, eine Palette, die
nicht aufgeht — und „BKH", das keine erfundene Bedeutung bekommt.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.article_import import (
    FreightConditionType,
    ImportError_,
    parse_article_import,
)

pytestmark = pytest.mark.unit


ANGEBOT = """<?xml version="1.0" encoding="UTF-8"?>
<articleImport version="1.0">
  <article>
    <articleType>SAATGUT</articleType>
    <description>
      <name>WWH Hycard</name>
      <category>Winterweizen</category>
      <productGroup>Saatgut</productGroup>
    </description>
    <treatment>
      <treated>true</treated>
      <treatmentDescription>Beize lt. Etikett</treatmentDescription>
    </treatment>
    <baseUnit>KG</baseUnit>
    <supplierRelations>
      <supplierRelation>
        <supplier>
          <name>GENO-Saaten</name>
          <role>HAUPTLIEFERANT</role>
        </supplier>
        <purchaseUnit>
          <unit>KG</unit>
          <packageSize unit="KG">1</packageSize>
        </purchaseUnit>
        <supplierPrices>
          <supplierPrice>
            <price>64.00</price>
            <currency>EUR</currency>
            <priceUnit>1</priceUnit>
            <priceUnitMeasure>KG</priceUnitMeasure>
            <freightCondition>
              <type>NICHT_EINDEUTIG_ERKANNT</type>
              <sourceValue>BKH</sourceValue>
            </freightCondition>
          </supplierPrice>
          <supplierPrice>
            <price>66.50</price>
            <currency>EUR</currency>
            <priceUnit>1</priceUnit>
            <priceUnitMeasure>KG</priceUnitMeasure>
            <freightCondition>
              <type>FRANKO</type>
              <sourceValue>franko</sourceValue>
            </freightCondition>
          </supplierPrice>
        </supplierPrices>
        <deliveryConditions>
          <deliveryCondition>
            <code>FRANKO_COMPLETE_LOAD</code>
            <description>Frankopreise beziehen sich immer auf eine komplette Ladung.</description>
          </deliveryCondition>
          <deliveryCondition>
            <code>THIRD_PARTY_PURCHASE_SURCHARGE</code>
            <description>Bei zugekauften Partien koennen Preisaufschlaege und Vorfrachten entstehen.</description>
          </deliveryCondition>
        </deliveryConditions>
        <paymentTerms>
          <days>10</days>
          <discountPercent>0</discountPercent>
          <description>Zahlbar innerhalb von 10 Tagen nach Rechnungsdatum rein netto Kasse.</description>
        </paymentTerms>
        <tax>
          <priceIncludesVAT>false</priceIncludesVAT>
        </tax>
      </supplierRelation>
    </supplierRelations>
  </article>

  <supplierPackagingRules>
    <supplier>GENO-Saaten</supplier>
    <packagingRule>
      <packageType>BIG_BAG</packageType>
      <content unit="KG">1000</content>
      <pricingAdjustment>
        <type>DISCOUNT</type>
        <value>-1.00</value>
        <currency>EUR</currency>
        <perUnit>DT</perUnit>
      </pricingAdjustment>
    </packagingRule>
    <packagingRule>
      <packageType>BIG_BAG</packageType>
      <content unit="KG">500</content>
      <pricingAdjustment>
        <type>STANDARD</type>
        <value>0.00</value>
        <currency>EUR</currency>
      </pricingAdjustment>
    </packagingRule>
    <packagingRule>
      <packageType>BAG</packageType>
      <content unit="KG">25</content>
      <pricingAdjustment>
        <type>SURCHARGE</type>
        <value>1.00</value>
        <currency>EUR</currency>
        <perUnit>DT</perUnit>
      </pricingAdjustment>
      <exception>
        <condition>HYBRID=true</condition>
        <description>25-kg-Regel ausgenommen Hybriden</description>
      </exception>
    </packagingRule>
    <palletRule>
      <palletType>STANDARD_25KG</palletType>
      <totalNetWeight unit="KG">1225</totalNetWeight>
      <calculatedNumberOfBags>49</calculatedNumberOfBags>
    </palletRule>
    <palletRule>
      <palletType>ORGANIC_25KG</palletType>
      <totalNetWeight unit="KG">1000</totalNetWeight>
      <calculatedNumberOfBags>40</calculatedNumberOfBags>
    </palletRule>
    <palletCharge>
      <palletType>EURO_EXCHANGE_PALLET</palletType>
      <amount>20.00</amount>
      <currency>EUR</currency>
    </palletCharge>
    <palletCharge>
      <type>BROKEN_PALLET_SURCHARGE</type>
      <amount>20.00</amount>
      <currency>EUR</currency>
    </palletCharge>
  </supplierPackagingRules>

  <commercialTerms>
    <offerBinding>false</offerBinding>
    <terms>
      <term>Dieses Angebot ist freibleibend und vorbehaltlich Anerkennung und Eigenbelieferung.</term>
      <term>Es gelten die jeweils gueltigen Allgemeinen Einkaufs- und Verkaufsbedingungen.</term>
    </terms>
  </commercialTerms>
</articleImport>
"""


@pytest.fixture()
def ergebnis():
    return parse_article_import(ANGEBOT)


# -- Die fuenf Ebenen bleiben getrennt -----------------------------------------


def test_artikel_traegt_weder_gebinde_noch_fracht(ergebnis) -> None:
    """Der wichtigste Test der Datei.

    „25 kg" ist keine Eigenschaft der Sorte — dieselbe Sorte kann morgen als
    500-kg-BigBag kommen. Und „franko" ist keine Eigenschaft des Artikels,
    sondern eine Beschaffungskondition. Beides gehoert eine Ebene tiefer.
    """
    artikel = ergebnis.articles[0]
    assert artikel.name == "WWH Hycard"
    assert artikel.article_type == "SAATGUT"
    assert artikel.base_unit == "kg"

    felder = set(vars(artikel))
    assert "package" not in felder
    assert "freight" not in felder
    assert "price" not in felder


def test_beizung_haengt_am_artikel_nicht_am_lieferanten(ergebnis) -> None:
    """Die Beize ist eine Eigenschaft der Ware, nicht der Bezugsquelle."""
    artikel = ergebnis.articles[0]
    assert artikel.treated is True
    assert artikel.treatment_description == "Beize lt. Etikett"


def test_gebinde_und_preise_haengen_am_lieferantenartikel(ergebnis) -> None:
    beziehung = ergebnis.articles[0].supplier_relations[0]
    assert beziehung.supplier_name == "GENO-Saaten"
    assert beziehung.role == "HAUPTLIEFERANT"
    assert beziehung.purchase_package is not None
    assert beziehung.purchase_package.net_content == Decimal(1)
    assert beziehung.purchase_package.unit == "kg"
    assert len(beziehung.prices) == 2


# -- Preisbasis ----------------------------------------------------------------


def test_jeder_preis_traegt_menge_und_einheit(ergebnis) -> None:
    """64,00 EUR allein ist keine Angabe, sondern eine Zahl.

    Saatgut wird in €/kg, €/dt, €/EH und €/Gebinde angeboten — ohne Menge und
    Einheit entstehen genau die Umrechnungsfehler, die das Mengenmodell
    vermeidet.
    """
    preise = ergebnis.articles[0].supplier_relations[0].prices
    assert [p.basis.amount for p in preise] == [Decimal("64.00"), Decimal("66.50")]
    for preis in preise:
        assert preis.basis.currency == "EUR"
        assert preis.basis.quantity == Decimal(1)
        assert preis.basis.unit == "kg"


def test_preis_ohne_bezug_wird_abgewiesen() -> None:
    xml = ANGEBOT.replace("<priceUnitMeasure>KG</priceUnitMeasure>", "", 1)
    with pytest.raises(ImportError_) as fehler:
        parse_article_import(xml)
    assert "priceUnitMeasure" in str(fehler.value)


def test_ausfuehrliche_preisbasis_wird_ebenso_gelesen() -> None:
    """Die empfohlene Schreibweise mit <priceBasis> ist gleichwertig."""
    xml = ANGEBOT.replace(
        """<price>64.00</price>
            <currency>EUR</currency>
            <priceUnit>1</priceUnit>
            <priceUnitMeasure>KG</priceUnitMeasure>""",
        """<priceBasis>
              <amount>64.00</amount>
              <currency>EUR</currency>
              <quantity>1</quantity>
              <unit>KG</unit>
            </priceBasis>""",
        1,
    )
    preis = parse_article_import(xml).articles[0].supplier_relations[0].prices[0]
    assert preis.basis.amount == Decimal("64.00")
    assert preis.basis.unit == "kg"


def test_deutsche_dezimalschreibweise_wird_verstanden() -> None:
    xml = ANGEBOT.replace("<price>64.00</price>", "<price>64,00</price>", 1)
    preis = parse_article_import(xml).articles[0].supplier_relations[0].prices[0]
    assert preis.basis.amount == Decimal("64.00")


# -- Unklares bleibt unklar ----------------------------------------------------


def test_bkh_bekommt_keine_erfundene_bedeutung(ergebnis) -> None:
    """Die Stelle, an der ein bequemer Import Schaden anrichten wuerde.

    „BKH" ist im Angebot nicht aufgeloest. Es als „ab Werk" oder „frei Haus" zu
    deuten waere eine Behauptung — und sie stuende danach im Stammsatz, ohne
    dass jemand sie je geprueft haette.
    """
    preis = ergebnis.articles[0].supplier_relations[0].prices[0]
    assert preis.freight is not None
    assert preis.freight.type is FreightConditionType.NICHT_EINDEUTIG_ERKANNT
    assert preis.freight.source_value == "BKH"
    assert preis.freight.verstanden is False


def test_unverstandene_fracht_wird_gemeldet_aber_nicht_abgewiesen(ergebnis) -> None:
    """Der Unterschied zwischen Abbruch und Hinweis.

    Ein fehlender Preisbezug ist ein Abbruch — damit kann man nicht rechnen.
    Eine unverstandene Frachtangabe ist es nicht: der Rest des Angebots bleibt
    brauchbar, jemand muss nur hinsehen.
    """
    assert any("BKH" in w for w in ergebnis.warnings)
    assert ergebnis.articles  # uebernommen wurde trotzdem


def test_erkannte_fracht_behaelt_den_quellwert(ergebnis) -> None:
    preis = ergebnis.articles[0].supplier_relations[0].prices[1]
    assert preis.freight.type is FreightConditionType.FRANKO
    # Auch wenn es verstanden wurde: was dastand, bleibt erhalten.
    assert preis.freight.source_value == "franko"


# -- Gebinderegeln -------------------------------------------------------------


def test_gebinderegeln_mit_bezugsgroesse(ergebnis) -> None:
    regeln = ergebnis.packaging_rules[0]
    assert regeln.supplier_name == "GENO-Saaten"

    bigbag_1000 = next(r for r in regeln.packaging_rules if r.package.net_content == Decimal(1000))
    assert bigbag_1000.adjustment.value == Decimal("-1.00")
    # -1,00 je dt ist etwas anderes als -1,00 je Gebinde.
    assert bigbag_1000.adjustment.per_unit == "dt"


def test_zuschlag_ohne_bezugsgroesse_wird_abgewiesen() -> None:
    xml = ANGEBOT.replace("<perUnit>DT</perUnit>", "", 1)
    with pytest.raises(ImportError_) as fehler:
        parse_article_import(xml)
    assert "perUnit" in str(fehler.value)


def test_standard_ohne_bezugsgroesse_ist_zulaessig(ergebnis) -> None:
    """Null braucht keine Bezugsgroesse — sie aendert nichts."""
    bigbag_500 = next(
        r for r in ergebnis.packaging_rules[0].packaging_rules
        if r.package.net_content == Decimal(500)
    )
    assert bigbag_500.adjustment.value == Decimal(0)
    assert bigbag_500.adjustment.per_unit is None


def test_ausnahme_bleibt_als_bedingung_erhalten(ergebnis) -> None:
    """„25-kg-Regel ausgenommen Hybriden" ist eine Regel, kein Kommentar."""
    sack = next(
        r for r in ergebnis.packaging_rules[0].packaging_rules
        if r.package.net_content == Decimal(25)
    )
    assert sack.exceptions == ("HYBRID=true",)


# -- Palette und Gebinde sind zweierlei ----------------------------------------


def test_palette_wird_nachgerechnet_statt_geglaubt(ergebnis) -> None:
    """49 x 25 kg = 1225 kg — und das wird geprueft.

    Geht es auf, gibt es keinen Hinweis. Das ist der Normalfall der Vorlage.
    """
    standard = next(
        p for p in ergebnis.packaging_rules[0].pallet_rules
        if p.pallet_type == "STANDARD_25KG"
    )
    assert standard.number_of_packages == 49
    assert standard.total_net_weight == Decimal(1225)
    assert not any("STANDARD_25KG" in w for w in ergebnis.warnings)


def test_oekopalette_geht_ebenfalls_auf(ergebnis) -> None:
    """40 x 25 kg = 1000 kg."""
    assert not any("ORGANIC_25KG" in w for w in ergebnis.warnings)


def test_palette_die_nicht_aufgeht_wird_gemeldet() -> None:
    """Ein Tippfehler im Angebot soll auffallen, bevor daraus Bestand wird."""
    xml = ANGEBOT.replace(
        "<totalNetWeight unit=\"KG\">1225</totalNetWeight>",
        "<totalNetWeight unit=\"KG\">1250</totalNetWeight>",
        1,
    )
    ergebnis = parse_article_import(xml)
    befunde = [w for w in ergebnis.warnings if "STANDARD_25KG" in w]
    assert befunde, "Die unstimmige Palette haette auffallen muessen"
    # Der Hinweis nennt die vorhandenen Gebinde, damit jemand vergleichen kann.
    assert "25 kg" in befunde[0]


def test_palettengebuehren_werden_getrennt_gefuehrt(ergebnis) -> None:
    gebuehren = {g.type: g.amount for g in ergebnis.packaging_rules[0].pallet_charges}
    assert gebuehren["EURO_EXCHANGE_PALLET"] == Decimal("20.00")
    assert gebuehren["BROKEN_PALLET_SURCHARGE"] == Decimal("20.00")


# -- Konditionen und Rahmen ----------------------------------------------------


def test_zahlungsbedingung_und_steuer(ergebnis) -> None:
    beziehung = ergebnis.articles[0].supplier_relations[0]
    assert beziehung.payment_terms.days == 10
    assert beziehung.payment_terms.discount_percent == Decimal(0)
    assert beziehung.price_includes_vat is False


def test_lieferbedingungen_bleiben_im_klartext(ergebnis) -> None:
    """Frankopreis gilt fuer eine komplette Ladung — das ist rechnungsrelevant."""
    codes = dict(ergebnis.articles[0].supplier_relations[0].delivery_conditions)
    assert "FRANKO_COMPLETE_LOAD" in codes
    assert "komplette Ladung" in codes["FRANKO_COMPLETE_LOAD"]
    assert "THIRD_PARTY_PURCHASE_SURCHARGE" in codes


def test_freibleibendes_angebot_wird_als_solches_gefuehrt(ergebnis) -> None:
    assert ergebnis.offer_binding is False
    assert any("freibleibend" in t for t in ergebnis.terms)


# -- Abweisungen ---------------------------------------------------------------


def test_falsches_wurzelelement_wird_abgewiesen() -> None:
    with pytest.raises(ImportError_) as fehler:
        parse_article_import("<artikel><name>X</name></artikel>")
    assert "articleImport" in str(fehler.value)


def test_kaputtes_xml_wird_abgewiesen() -> None:
    with pytest.raises(ImportError_):
        parse_article_import("<articleImport><article>")


def test_leeres_dokument_wird_abgewiesen() -> None:
    with pytest.raises(ImportError_) as fehler:
        parse_article_import('<articleImport version="1.0"></articleImport>')
    assert "weder Artikel noch Gebinderegeln" in str(fehler.value)


def test_artikel_ohne_namen_wird_abgewiesen() -> None:
    xml = ANGEBOT.replace("<name>WWH Hycard</name>", "<name></name>", 1)
    with pytest.raises(ImportError_) as fehler:
        parse_article_import(xml)
    assert "description/name" in str(fehler.value)
