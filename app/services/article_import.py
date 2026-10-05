"""FSX-ARTIKEL-IMPORT — kanonisches Zwischenformat fuer den Artikelstamm.

Lieferantenangebote kommen als PDF, Tabelle oder E-Mail. Sie werden zuerst in
**dieses** XML ueberfuehrt und erst danach geprueft und uebernommen. Der Umweg
ist der Zweck: Zwischen „was im Angebot steht" und „was im Stammsatz landet"
gehoert eine Stufe, die man lesen, pruefen und zurueckweisen kann.

Fuenf Ebenen, strikt getrennt
-----------------------------

``Artikel → Variante → Lieferantenartikel → Gebinde → Kondition``

Der Grund ist nicht Ordnungsliebe. **„25 kg" ist keine Eigenschaft der Sorte** —
dieselbe Sorte kann morgen als 500-kg-BigBag kommen. Und **``franko`` ist keine
Eigenschaft des Artikels**, sondern eine Beschaffungskondition. Wer das in einen
Satz wirft, kann Gebinde und Fracht nicht mehr aendern, ohne den Artikel
anzufassen.

Drei Regeln, die dieselbe Haltung haben wie das Mengenmodell
------------------------------------------------------------

1. **Kein Preis ohne Preisbasis.** ``64,00 EUR`` allein ist keine Angabe —
   Saatgut wird in €/kg, €/dt, €/EH und €/Gebinde angeboten. Menge und Einheit
   gehoeren an den Preis, sonst entstehen genau die Umrechnungsfehler, die das
   Mengenmodell vermeidet.
2. **Unklares wird nicht gedeutet.** Die Frachtangabe „BKH" aus der Vorlage
   bekommt keine erratene Bedeutung, sondern bleibt als ``source_value``
   erhalten und wird als ``nicht_eindeutig_erkannt`` markiert. Dasselbe Prinzip
   wie „nicht ermittelt" im Leitstand.
3. **Gerechnet wird nachgerechnet.** Eine Palette mit 49 Saecken zu 25 kg muss
   1225 kg wiegen. Steht dort etwas anderes, ist das ein Befund und keine
   Rundung.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import Enum
from xml.etree import ElementTree

from app.core.agrar_units import normalisiere


class ImportError_(ValueError):
    """Das Dokument ist nicht uebernehmbar."""


class FreightConditionType(str, Enum):
    FRANKO = "franko"
    AB_WERK = "ab_werk"
    #: Ausdruecklich: verstanden haben wir es nicht.
    NICHT_EINDEUTIG_ERKANNT = "nicht_eindeutig_erkannt"


#: Nur was belegt ist, wird zugeordnet. Alles andere bleibt Quellwert.
FREIGHT_BEKANNT: dict[str, FreightConditionType] = {
    "franko": FreightConditionType.FRANKO,
    "frei haus": FreightConditionType.FRANKO,
    "ab werk": FreightConditionType.AB_WERK,
    "ex works": FreightConditionType.AB_WERK,
}


@dataclass(frozen=True)
class PriceBasis:
    """Betrag **je Menge und Einheit** — nie nur ein Betrag."""

    amount: Decimal
    currency: str
    quantity: Decimal
    unit: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ImportError_("Ein Preis darf nicht negativ sein.")
        if self.quantity <= 0:
            raise ImportError_("Die Preismenge muss groesser als null sein.")


@dataclass(frozen=True)
class FreightCondition:
    type: FreightConditionType
    #: Was im Angebot stand — immer erhalten, auch wenn es verstanden wurde.
    source_value: str

    @property
    def verstanden(self) -> bool:
        return self.type is not FreightConditionType.NICHT_EINDEUTIG_ERKANNT


@dataclass(frozen=True)
class SupplierPrice:
    basis: PriceBasis
    freight: FreightCondition | None = None


@dataclass(frozen=True)
class Package:
    """Das Gebinde selbst — Sack, BigBag, Kanister."""

    package_type: str
    net_content: Decimal
    unit: str


@dataclass(frozen=True)
class LogisticUnit:
    """Die Logistikeinheit — Palette mit einer Anzahl Gebinde.

    Strikt getrennt vom Gebinde: 49 Saecke zu 25 kg sind 1225 kg. Das Gebinde
    beschreibt den Sack, die Logistikeinheit die Palette.
    """

    type: str
    packages: int
    net_weight: Decimal
    unit: str

    def erwartetes_gewicht(self, gebinde: Package) -> Decimal:
        return Decimal(self.packages) * gebinde.net_content


@dataclass(frozen=True)
class PricingAdjustment:
    """Zu- oder Abschlag, immer mit Bezugsgroesse.

    ``-1,00 EUR je dt`` ist etwas anderes als ``-1,00 EUR je Gebinde``. Ohne
    ``per_unit`` waere der Wert nicht anwendbar.
    """

    type: str
    value: Decimal
    currency: str
    per_unit: str | None = None


@dataclass(frozen=True)
class PackagingRule:
    package: Package
    adjustment: PricingAdjustment | None = None
    #: Ausnahmen bleiben als Bedingung erhalten, z. B. ``HYBRID=true``.
    exceptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class PalletRule:
    pallet_type: str
    total_net_weight: Decimal
    unit: str
    number_of_packages: int | None = None


@dataclass(frozen=True)
class PalletCharge:
    type: str
    amount: Decimal
    currency: str


@dataclass(frozen=True)
class PaymentTerms:
    days: int
    discount_percent: Decimal
    description: str = ""


@dataclass(frozen=True)
class SupplierRelation:
    """Die Lieferantenebene — Bezugsquelle, Gebinde, Preise, Konditionen."""

    supplier_name: str
    role: str | None = None
    purchase_package: Package | None = None
    prices: tuple[SupplierPrice, ...] = ()
    delivery_conditions: tuple[tuple[str, str], ...] = ()
    payment_terms: PaymentTerms | None = None
    price_includes_vat: bool | None = None


@dataclass(frozen=True)
class ArticleImport:
    """Der Artikel — ohne Gebinde und ohne Kondition."""

    article_type: str
    name: str
    category: str | None = None
    product_group: str | None = None
    base_unit: str = "kg"
    treated: bool | None = None
    treatment_description: str | None = None
    supplier_relations: tuple[SupplierRelation, ...] = ()


@dataclass(frozen=True)
class SupplierPackagingRules:
    supplier_name: str
    packaging_rules: tuple[PackagingRule, ...] = ()
    pallet_rules: tuple[PalletRule, ...] = ()
    pallet_charges: tuple[PalletCharge, ...] = ()


@dataclass
class ImportResult:
    articles: list[ArticleImport] = field(default_factory=list)
    packaging_rules: list[SupplierPackagingRules] = field(default_factory=list)
    offer_binding: bool | None = None
    terms: list[str] = field(default_factory=list)
    #: Was uebernommen wurde, aber jemand ansehen sollte.
    warnings: list[str] = field(default_factory=list)


# -- Hilfen --------------------------------------------------------------------


def _text(element: ElementTree.Element | None, pfad: str, pflicht: bool = False) -> str | None:
    if element is None:
        if pflicht:
            raise ImportError_(f"Pflichtangabe fehlt: {pfad}")
        return None
    treffer = element.find(pfad)
    wert = (treffer.text or "").strip() if treffer is not None else ""
    if not wert:
        if pflicht:
            raise ImportError_(f"Pflichtangabe fehlt oder ist leer: {pfad}")
        return None
    return wert


def _dezimal(wert: str | None, pfad: str, pflicht: bool = False) -> Decimal | None:
    if wert is None:
        if pflicht:
            raise ImportError_(f"Pflichtangabe fehlt: {pfad}")
        return None
    # Angebote schreiben "64,00" ebenso wie "64.00".
    bereinigt = wert.replace(" ", "").replace(",", ".")
    try:
        return Decimal(bereinigt)
    except InvalidOperation as fehler:
        raise ImportError_(f"{pfad!r} ist keine Zahl: {wert!r}") from fehler


def _bool(wert: str | None) -> bool | None:
    if wert is None:
        return None
    return wert.strip().lower() in {"true", "ja", "1", "yes"}


def _freight(element: ElementTree.Element | None) -> FreightCondition | None:
    """Frachtkondition lesen — und Unverstandenes als solches kennzeichnen."""
    if element is None:
        return None
    quellwert = _text(element, "sourceValue") or _text(element, "type") or ""
    typ_text = (_text(element, "type") or "").strip().lower()

    if typ_text in {t.value for t in FreightConditionType}:
        typ = FreightConditionType(typ_text)
    else:
        typ = FREIGHT_BEKANNT.get(quellwert.strip().lower(), FreightConditionType.NICHT_EINDEUTIG_ERKANNT)

    return FreightCondition(type=typ, source_value=quellwert)


def _package(element: ElementTree.Element | None, pfad: str) -> Package | None:
    if element is None:
        return None
    inhalt = element.find("netContent")
    if inhalt is None:
        inhalt = element.find("content")
    if inhalt is None:
        inhalt = element.find("packageSize")
    if inhalt is None:
        return None
    menge = _dezimal(inhalt.text, f"{pfad}/netContent", pflicht=True)
    einheit = normalisiere(inhalt.attrib.get("unit") or "kg")
    typ = _text(element, "packageType") or _text(element, "unit") or "unbekannt"
    assert menge is not None
    return Package(package_type=typ, net_content=menge, unit=einheit)


# -- Parser --------------------------------------------------------------------


def parse_article_import(xml: str | bytes) -> ImportResult:
    """Kanonisches Import-XML in typisierte Strukturen ueberfuehren.

    Wirft ``ImportError_`` bei allem, was nicht uebernehmbar ist. Was
    uebernehmbar, aber zweifelhaft ist, landet in ``warnings`` — der
    Unterschied ist wichtig: Ein fehlender Preisbezug ist ein Abbruch, eine
    unverstandene Frachtangabe nicht.
    """
    try:
        wurzel = ElementTree.fromstring(xml)
    except ElementTree.ParseError as fehler:
        raise ImportError_(f"Kein gueltiges XML: {fehler}") from fehler

    if wurzel.tag != "articleImport":
        raise ImportError_(
            f"Wurzelelement ist {wurzel.tag!r}, erwartet wird 'articleImport'."
        )

    ergebnis = ImportResult()

    for artikel_el in wurzel.findall("article"):
        ergebnis.articles.append(_parse_article(artikel_el, ergebnis))

    for regeln_el in wurzel.findall("supplierPackagingRules"):
        ergebnis.packaging_rules.append(_parse_packaging_rules(regeln_el, ergebnis))

    terms_el = wurzel.find("commercialTerms")
    if terms_el is not None:
        ergebnis.offer_binding = _bool(_text(terms_el, "offerBinding"))
        for term in terms_el.findall("terms/term"):
            text = (term.text or "").strip()
            if text:
                ergebnis.terms.append(" ".join(text.split()))

    if not ergebnis.articles and not ergebnis.packaging_rules:
        raise ImportError_("Das Dokument enthaelt weder Artikel noch Gebinderegeln.")

    return ergebnis


def _parse_article(element: ElementTree.Element, ergebnis: ImportResult) -> ArticleImport:
    name = _text(element, "description/name", pflicht=True)
    assert name is not None

    behandlung = element.find("treatment")
    relationen = tuple(
        _parse_supplier_relation(rel, name, ergebnis)
        for rel in element.findall("supplierRelations/supplierRelation")
    )

    return ArticleImport(
        article_type=_text(element, "articleType") or "unbekannt",
        name=name,
        category=_text(element, "description/category"),
        product_group=_text(element, "description/productGroup"),
        base_unit=normalisiere(_text(element, "baseUnit") or "kg"),
        treated=_bool(_text(behandlung, "treated")) if behandlung is not None else None,
        treatment_description=_text(behandlung, "treatmentDescription") if behandlung is not None else None,
        supplier_relations=relationen,
    )


def _parse_supplier_relation(
    element: ElementTree.Element, artikel: str, ergebnis: ImportResult
) -> SupplierRelation:
    lieferant = _text(element, "supplier/name", pflicht=True)
    assert lieferant is not None

    preise: list[SupplierPrice] = []
    for preis_el in element.findall("supplierPrices/supplierPrice"):
        preise.append(_parse_price(preis_el, artikel, lieferant, ergebnis))

    konditionen = tuple(
        (
            _text(k, "code") or "",
            " ".join((_text(k, "description") or "").split()),
        )
        for k in element.findall("deliveryConditions/deliveryCondition")
    )

    zahlung = None
    zahlung_el = element.find("paymentTerms")
    if zahlung_el is not None:
        tage = _dezimal(_text(zahlung_el, "days"), "paymentTerms/days", pflicht=True)
        rabatt = _dezimal(_text(zahlung_el, "discountPercent"), "paymentTerms/discountPercent") or Decimal(0)
        assert tage is not None
        zahlung = PaymentTerms(
            days=int(tage),
            discount_percent=rabatt,
            description=" ".join((_text(zahlung_el, "description") or "").split()),
        )

    steuer_el = element.find("tax")
    inkl_ust = _bool(_text(steuer_el, "priceIncludesVAT")) if steuer_el is not None else None

    return SupplierRelation(
        supplier_name=lieferant,
        role=_text(element, "supplier/role"),
        purchase_package=_package(element.find("purchaseUnit"), "purchaseUnit"),
        prices=tuple(preise),
        delivery_conditions=konditionen,
        payment_terms=zahlung,
        price_includes_vat=inkl_ust,
    )


def _parse_price(
    element: ElementTree.Element, artikel: str, lieferant: str, ergebnis: ImportResult
) -> SupplierPrice:
    """Preis lesen — und ohne Preisbasis ablehnen.

    Beide Schreibweisen werden akzeptiert: das ausfuehrliche ``<priceBasis>`` und
    die flache Form mit ``price``/``priceUnit``/``priceUnitMeasure``. Was in
    **keiner** von beiden fehlen darf, sind Menge und Einheit — ``64,00 EUR``
    allein ist keine Angabe, sondern eine Zahl.
    """
    basis_el = element.find("priceBasis")
    if basis_el is not None:
        betrag = _dezimal(_text(basis_el, "amount"), "priceBasis/amount", pflicht=True)
        waehrung = _text(basis_el, "currency", pflicht=True)
        menge = _dezimal(_text(basis_el, "quantity"), "priceBasis/quantity", pflicht=True)
        einheit = _text(basis_el, "unit", pflicht=True)
    else:
        betrag = _dezimal(_text(element, "price"), "price", pflicht=True)
        waehrung = _text(element, "currency", pflicht=True)
        menge = _dezimal(_text(element, "priceUnit"), "priceUnit", pflicht=True)
        einheit = _text(element, "priceUnitMeasure", pflicht=True)

    assert betrag is not None and menge is not None and waehrung and einheit

    fracht = _freight(element.find("freightCondition"))
    if fracht is not None and not fracht.verstanden:
        ergebnis.warnings.append(
            f"{artikel} / {lieferant}: Frachtangabe {fracht.source_value!r} nicht "
            "eindeutig erkannt — als Quellwert uebernommen, ohne Bedeutung."
        )

    return SupplierPrice(
        basis=PriceBasis(
            amount=betrag,
            currency=waehrung.upper(),
            quantity=menge,
            unit=normalisiere(einheit),
        ),
        freight=fracht,
    )


def _parse_packaging_rules(
    element: ElementTree.Element, ergebnis: ImportResult
) -> SupplierPackagingRules:
    lieferant = _text(element, "supplier", pflicht=True)
    assert lieferant is not None

    regeln: list[PackagingRule] = []
    for regel_el in element.findall("packagingRule"):
        gebinde = _package(regel_el, "packagingRule")
        if gebinde is None:
            raise ImportError_("packagingRule ohne Inhaltsangabe.")
        anpassung = None
        anpassung_el = regel_el.find("pricingAdjustment")
        if anpassung_el is not None:
            wert = _dezimal(_text(anpassung_el, "value"), "pricingAdjustment/value", pflicht=True)
            assert wert is not None
            per_unit = _text(anpassung_el, "perUnit")
            typ = (_text(anpassung_el, "type") or "").lower()
            if wert != 0 and not per_unit:
                # Ein Zu-/Abschlag ohne Bezugsgroesse ist nicht anwendbar:
                # -1,00 je dt ist etwas anderes als -1,00 je Gebinde.
                raise ImportError_(
                    f"Preisanpassung {wert} ohne perUnit — ohne Bezugsgroesse "
                    "ist der Wert nicht anwendbar."
                )
            anpassung = PricingAdjustment(
                type=typ or "unbekannt",
                value=wert,
                currency=(_text(anpassung_el, "currency") or "EUR").upper(),
                per_unit=normalisiere(per_unit) if per_unit else None,
            )
        ausnahmen = tuple(
            (_text(a, "condition") or "").strip()
            for a in regel_el.findall("exception")
            if _text(a, "condition")
        )
        regeln.append(PackagingRule(package=gebinde, adjustment=anpassung, exceptions=ausnahmen))

    paletten: list[PalletRule] = []
    for palette_el in element.findall("palletRule"):
        gewicht_el = palette_el.find("totalNetWeight")
        if gewicht_el is None:
            raise ImportError_("palletRule ohne totalNetWeight.")
        gewicht = _dezimal(gewicht_el.text, "palletRule/totalNetWeight", pflicht=True)
        anzahl = _dezimal(_text(palette_el, "calculatedNumberOfBags"), "calculatedNumberOfBags")
        assert gewicht is not None
        paletten.append(
            PalletRule(
                pallet_type=_text(palette_el, "palletType") or "unbekannt",
                total_net_weight=gewicht,
                unit=normalisiere(gewicht_el.attrib.get("unit") or "kg"),
                number_of_packages=int(anzahl) if anzahl is not None else None,
            )
        )

    gebuehren = []
    for gebuehr_el in element.findall("palletCharge"):
        betrag = _dezimal(_text(gebuehr_el, "amount"), "palletCharge/amount", pflicht=True)
        assert betrag is not None
        gebuehren.append(
            PalletCharge(
                type=_text(gebuehr_el, "palletType") or _text(gebuehr_el, "type") or "unbekannt",
                amount=betrag,
                currency=(_text(gebuehr_el, "currency") or "EUR").upper(),
            )
        )

    regelwerk = SupplierPackagingRules(
        supplier_name=lieferant,
        packaging_rules=tuple(regeln),
        pallet_rules=tuple(paletten),
        pallet_charges=tuple(gebuehren),
    )
    ergebnis.warnings.extend(pruefe_palettengewichte(regelwerk))
    return regelwerk


def pruefe_palettengewichte(regelwerk: SupplierPackagingRules) -> list[str]:
    """Nachrechnen statt glauben: Anzahl x Gebindeinhalt muss das Gewicht ergeben.

    49 Saecke zu 25 kg sind 1225 kg. Steht dort etwas anderes, ist das ein
    Befund — entweder ein Tippfehler im Angebot oder ein anderes Gebinde als
    angenommen. Beides will jemand wissen, bevor daraus Lagerbestand wird.
    """
    befunde: list[str] = []
    for palette in regelwerk.pallet_rules:
        if palette.number_of_packages is None:
            continue
        passende = [
            regel.package
            for regel in regelwerk.packaging_rules
            if regel.package.unit == palette.unit
            and Decimal(palette.number_of_packages) * regel.package.net_content
            == palette.total_net_weight
        ]
        if passende:
            continue
        kandidaten = [
            f"{regel.package.net_content} {regel.package.unit}"
            for regel in regelwerk.packaging_rules
            if regel.package.unit == palette.unit
        ]
        befunde.append(
            f"{regelwerk.supplier_name}: Palette {palette.pallet_type} nennt "
            f"{palette.number_of_packages} Gebinde und "
            f"{palette.total_net_weight} {palette.unit}; das geht mit keinem der "
            f"angegebenen Gebinde auf ({', '.join(kandidaten) or 'keine Gebinde angegeben'})."
        )
    return befunde
