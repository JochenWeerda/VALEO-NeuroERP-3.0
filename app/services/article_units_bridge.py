"""Bruecke vom Importformat in das Mengenmodell.

Aus den Gebinderegeln eines Lieferantenangebots werden **Artikelvarianten**:
je Gebindegroesse ein eigener Artikel. So wird es in der Praxis gefuehrt —
„WWH Hycard Sack 25 kg" und „WWH Hycard BigBag 500 kg" sind zwei Stammsaetze,
nicht einer mit zwei Gebinden.

Warum je Gebindegroesse ein Artikel
-----------------------------------

Weil daran haengt, was einen Artikel ausmacht: eigene Artikelnummer, eigener
Bestand, eigener Preis, eigene Etiketten. Ein Sack 25 kg und ein BigBag 500 kg
sind fuer Lager, Disposition und Inventur zwei Dinge — auch wenn dieselbe Sorte
darin ist.

Die **Sorteneigenschaften werden vererbt**: Artikelart, Kategorie, Beizung,
Basiseinheit, Handelsgroesse und Teilbarkeit kommen aus dem Angebot und gelten
fuer jede Variante. Innerhalb einer Variante laufen dann die **Chargen**, die
ihrerseits erben und partiebezogene Umrechnungen ergaenzen duerfen
(``agrar_units.ChargenEinheiten`` — dort liegt der Ort fuer das
Tausendkorngewicht einer konkreten Partie).

Was die Bruecke ausdruecklich **nicht** mitnimmt
------------------------------------------------

**Preisliche Zu- und Abschlaege.** „BigBag 1000 kg: −1,00 €/dt" ist eine
Kondition, keine Umrechnung. Die Verpackungsleiter beantwortet „wie viele
Kilogramm sind ein BigBag", nicht „was kostet er". Wer beides vermischt, kann
den Preis nicht aendern, ohne die Mengenrechnung anzufassen.

**Ausnahmen wie ``HYBRID=true``.** Sie gehoeren zur Kondition, aus demselben
Grund — gemeldet, damit sie nicht verloren gehen, aber nicht in den Einheiten.

**Die Teilbarkeit**, ausser sie ist rechtlich bestimmt: Pflanzenschutzmittel
duerfen nur in der Originalverpackung abgegeben werden. Fuer alles andere waere
eine Ableitung aus dem Angebot geraten.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.core.agrar_units import (
    VARIANTEN_TRENNER,
    ArtikelEinheiten,
    Gebinde,
    UnitKind,
    art,
    normalisiere,
)
from app.services.article_import import (
    ArticleImport,
    PackagingRule,
    SupplierPackagingRules,
)

#: Artikelarten, bei denen die Unteilbarkeit aus dem Fachrecht folgt.
NICHT_TEILBAR_ARTIKELARTEN = frozenset({"psm", "pflanzenschutz", "pflanzenschutzmittel"})


@dataclass
class ArticleVariant:
    """Ein Stammsatz: die Sorte in **einer** Gebindegroesse."""

    name: str
    article_type: str
    #: Einheitenname des Gebindes, z. B. ``sack:25``. ``None`` bei loser Ware.
    package_unit: str | None
    units: ArtikelEinheiten
    #: Was von der Sorte geerbt wurde — zur Nachvollziehbarkeit im Stammsatz.
    inherited: dict[str, object] = field(default_factory=dict)
    conditions: list[str] = field(default_factory=list)


@dataclass
class BridgeResult:
    variants: list[ArticleVariant] = field(default_factory=list)
    #: Konditionen, die fuer alle Varianten gelten (Palettengebuehren u. a.).
    conditions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _einheitenname(regel: PackagingRule) -> str | None:
    """Gebindename mit Auspraegung, damit zwei BigBags unterscheidbar bleiben.

    Der Lieferant fuehrt BigBag zu 500 **und** zu 1000 kg. Beide unter
    ``big_bag`` waeren mehrdeutig — das Mengenmodell weist das zu Recht ab. Der
    Name traegt deshalb die Groesse: ``big_bag:500``.

    Ist der Gebindetyp unbekannt, wird ``None`` geliefert. Ihn auf einen
    aehnlich klingenden zu biegen waere geraten.
    """
    typ = normalisiere(regel.package.package_type)
    if art(typ) is not UnitKind.ZAEHLEINHEIT:
        return None
    return f"{typ}{VARIANTEN_TRENNER}{_zahl(regel.package.net_content)}"


def _zahl(wert: Decimal) -> str:
    return str(wert.to_integral_value() if wert == wert.to_integral_value() else wert)


def _variantenname(basis: str, regel: PackagingRule) -> str:
    return (
        f"{basis} {regel.package.package_type} "
        f"{_zahl(regel.package.net_content)} {regel.package.unit}"
    )


def build_article_variants(
    article: ArticleImport,
    packaging: SupplierPackagingRules | None = None,
) -> BridgeResult:
    """Je Gebindegroesse eine Artikelvariante, mit geerbten Sorteneigenschaften."""
    basis = normalisiere(article.base_unit)
    handel = _handelseinheit(article)
    teilbar = normalisiere(article.article_type) not in NICHT_TEILBAR_ARTIKELARTEN

    geerbt: dict[str, object] = {
        "article_type": article.article_type,
        "category": article.category,
        "product_group": article.product_group,
        "base_unit": basis,
        "handels_einheit": handel,
        "treated": article.treated,
        "treatment_description": article.treatment_description,
        "teilbar": teilbar,
    }

    ergebnis = BridgeResult()
    if not teilbar:
        ergebnis.conditions.append(
            "Pflanzenschutz: nur ganze Gebinde — Abgabe ausschliesslich in der "
            "Originalverpackung."
        )

    if packaging is None or not packaging.packaging_rules:
        # Lose Ware: eine Variante ohne Gebinde. Kein Sonderfall, sondern der
        # Normalfall bei Schuettgut.
        ergebnis.variants.append(
            ArticleVariant(
                name=article.name,
                article_type=article.article_type,
                package_unit=None,
                units=ArtikelEinheiten(
                    basis_einheit=basis, handels_einheit=handel, teilbar=teilbar
                ),
                inherited=dict(geerbt),
            )
        )
        return ergebnis

    gebinde_je_regel: list[tuple[PackagingRule, Gebinde]] = []
    for regel in packaging.packaging_rules:
        einheit = normalisiere(regel.package.unit)
        if einheit != basis:
            ergebnis.warnings.append(
                f"Gebinde {regel.package.package_type} ist in {regel.package.unit} "
                f"angegeben, der Artikel rechnet in {basis} — nicht uebernommen, "
                "weil die Umrechnung nicht belegt ist."
            )
            continue
        name = _einheitenname(regel)
        if name is None:
            ergebnis.warnings.append(
                f"Gebindetyp {regel.package.package_type!r} ist nicht bekannt — "
                "nicht uebernommen. Ihn auf einen aehnlichen zu biegen waere "
                "geraten; die Entsprechung gehoert in die Alias-Liste."
            )
            continue
        gebinde_je_regel.append(
            (
                regel,
                Gebinde(
                    einheit=name,
                    faktor=regel.package.net_content,
                    bezeichnung=(
                        f"{regel.package.package_type} "
                        f"{_zahl(regel.package.net_content)} {einheit}"
                    ),
                ),
            )
        )

    paletten = _palettenstufen(packaging, gebinde_je_regel, ergebnis.warnings)

    for regel, gebinde in gebinde_je_regel:
        stufen: list[Gebinde] = [gebinde]
        # Nur die Paletten, die **dieses** Gebinde stapeln, gehoeren zu dieser
        # Variante. Eine 25-kg-Palette hat im BigBag-Artikel nichts zu suchen.
        stufen.extend(p for p, bezug in paletten if bezug == gebinde.einheit)

        bedingungen: list[str] = []
        if regel.adjustment is not None and regel.adjustment.value != 0:
            bedingungen.append(
                f"{regel.adjustment.value} {regel.adjustment.currency}"
                + (f" je {regel.adjustment.per_unit}" if regel.adjustment.per_unit else "")
            )
        bedingungen.extend(f"Ausnahme {a}" for a in regel.exceptions)

        ergebnis.variants.append(
            ArticleVariant(
                name=_variantenname(article.name, regel),
                article_type=article.article_type,
                package_unit=gebinde.einheit,
                units=ArtikelEinheiten(
                    basis_einheit=basis,
                    handels_einheit=handel,
                    gebinde=tuple(stufen),
                    teilbar=teilbar,
                ),
                inherited=dict(geerbt),
                conditions=bedingungen,
            )
        )

    ergebnis.conditions.extend(
        f"{gebuehr.type}: {gebuehr.amount} {gebuehr.currency}"
        for gebuehr in packaging.pallet_charges
    )
    return ergebnis


def _palettenstufen(
    packaging: SupplierPackagingRules,
    gebinde_je_regel: list[tuple[PackagingRule, Gebinde]],
    warnings: list[str],
) -> list[tuple[Gebinde, str]]:
    """Paletten als Stufe **ueber** dem Gebinde: 49 Saecke, nicht 1225 kg.

    So bleibt die Palette richtig, wenn sich das Sackgewicht aendert. Passt die
    Rechnung zu keinem oder zu mehreren Gebinden, wird sie nicht uebernommen —
    eine geratene Zuordnung waere schlimmer als keine.
    """
    stufen: list[tuple[Gebinde, str]] = []
    for palette in packaging.pallet_rules:
        if palette.number_of_packages is None:
            warnings.append(
                f"Palette {palette.pallet_type} nennt keine Gebindeanzahl — ohne "
                "sie ist sie keine Stufe der Verpackungsleiter, sondern nur ein "
                "Gewicht."
            )
            continue
        passend = [
            g
            for _, g in gebinde_je_regel
            if Decimal(palette.number_of_packages) * g.faktor == palette.total_net_weight
        ]
        if len(passend) != 1:
            warnings.append(
                f"Palette {palette.pallet_type}: {palette.number_of_packages} x "
                f"welches Gebinde ergibt {palette.total_net_weight} {palette.unit}? "
                + (
                    "Mehrere Gebinde passen — nicht eindeutig."
                    if len(passend) > 1
                    else "Kein angegebenes Gebinde passt."
                )
            )
            continue
        bezug = passend[0]
        stufen.append(
            (
                Gebinde(
                    einheit=f"palette{VARIANTEN_TRENNER}{normalisiere(palette.pallet_type)}",
                    faktor=Decimal(palette.number_of_packages),
                    je_einheit=bezug.einheit,
                    bezeichnung=(
                        f"{palette.pallet_type}: {palette.number_of_packages} x "
                        f"{bezug.bezeichnung}"
                    ),
                ),
                bezug.einheit,
            )
        )
    return stufen


def _handelseinheit(article: ArticleImport) -> str | None:
    """Abrechnungsgroesse aus den Preisen ableiten — wenn sie einheitlich ist.

    Steht in allen Preisen dieselbe Einheit, ist das die Groesse, in der dieser
    Lieferant rechnet. Stehen verschiedene, wird **keine** gewaehlt: Eine
    willkuerlich herausgegriffene waere schlimmer als gar keine, weil sie die
    Anzeige falsch beschriftet.
    """
    einheiten = {
        normalisiere(preis.basis.unit)
        for beziehung in article.supplier_relations
        for preis in beziehung.prices
    }
    return einheiten.pop() if len(einheiten) == 1 else None
