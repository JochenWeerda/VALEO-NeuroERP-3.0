"""Einheiten, Gebinde und Packs des Agrarhandels.

Grundlage: ``docs/design/agrar-mengen-gebinde-modell.md`` (mit Quellen).

Der Kern ist eine Unterscheidung, die ein naives Einheitensystem nicht trifft:

* **Masse** (kg, dt, t) und **Volumen** (ml, l, hl) sind global und exakt
  umrechenbar.
* **Zaehleinheiten** (Sack, Kanister, Big Bag, Palette, Einheit, Pack, Stueck)
  sind es **nicht**. Ein Sack Duenger wiegt 25 kg, ein Sack Maissaatgut rund
  15 kg, und eine "Einheit" ist beim Saatgetreide eine Million keimfaehige
  Koerner, beim Mais fuenfzigtausend. Wer dafuer einen globalen Faktor
  hinterlegt, erzeugt eine Zahl, die meistens falsch ist — und unauffaellig.

Deshalb gilt hier durchgehend: **keine Umrechnung ohne belegten Faktor.** Fehlt
er, wird ``None`` geliefert und der Aufrufer sagt, dass es nicht geht. Das ist
dieselbe Disziplin wie in ``docflow_source_proposals.unit_factor`` — und
dieselbe wie im ganzen FSX-Programm: lieber eine fehlende Angabe als eine
erfundene.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class UnitKind(str, Enum):
    """Art einer Einheit — entscheidet, ob global umgerechnet werden darf."""

    MASSE = "masse"
    VOLUMEN = "volumen"
    ZAEHLEINHEIT = "zaehleinheit"


#: Masseeinheiten mit ihrem Faktor in Kilogramm.
#:
#: ``dt`` (Dezitonne, 100 kg) ist die uebliche Handelsgroesse des
#: Getreidehandels; sie hat den Doppelzentner abgeloest. Intern wird in kg
#: gerechnet, angezeigt und abgerechnet wird in dt, wo der Artikel es vorgibt —
#: Rundung gehoert an die Anzeige, nie an den gespeicherten Wert.
MASSE_IN_KG: dict[str, Decimal] = {
    "kg": Decimal(1),
    "dt": Decimal(100),
    "t": Decimal(1000),
}

#: Volumeneinheiten mit ihrem Faktor in Litern.
VOLUMEN_IN_L: dict[str, Decimal] = {
    "ml": Decimal("0.001"),
    "l": Decimal(1),
    "hl": Decimal(100),
}

#: Schreibweisen, die im Handel vorkommen und dasselbe meinen.
ALIASE: dict[str, str] = {
    "tonne": "t",
    "tonnen": "t",
    "to": "t",
    "dz": "dt",  # Doppelzentner — historisch, gleiche Groesse
    "doppelzentner": "dt",
    "dezitonne": "dt",
    "kilogramm": "kg",
    "liter": "l",
    "stk": "st",
    "stueck": "st",
    "stück": "st",
    "eh": "einheit",
    "e": "einheit",
}

#: Zaehleinheiten, die im Agrarhandel als Gebinde oder Verkaufseinheit auftreten.
#: Der Faktor steht **nicht** hier, sondern am Artikel — siehe Modul-Doku.
ZAEHLEINHEITEN: frozenset[str] = frozenset(
    {
        "st",  # Stueck
        "sack",
        "kanister",
        "flasche",
        "karton",
        "kiste",
        "big_bag",
        "palette",
        "einheit",  # Saatgut: Kornzahl, je Kultur verschieden
        "pack",  # Verbund verschiedener Artikel
        "container",
    }
)


def normalisiere(einheit: str) -> str:
    """Schreibweise vereinheitlichen, ohne zu raten."""
    schluessel = (einheit or "").strip().lower().replace(" ", "_").replace("-", "_")
    return ALIASE.get(schluessel, schluessel)


def art(einheit: str) -> UnitKind | None:
    """Art einer Einheit bestimmen; ``None`` bei unbekannter Einheit."""
    e = normalisiere(einheit)
    if e in MASSE_IN_KG:
        return UnitKind.MASSE
    if e in VOLUMEN_IN_L:
        return UnitKind.VOLUMEN
    if e in ZAEHLEINHEITEN:
        return UnitKind.ZAEHLEINHEIT
    return None


def globaler_faktor(quelle: str, ziel: str) -> Decimal | None:
    """Faktor fuer die Umrechnung ``quelle`` -> ``ziel``, oder ``None``.

    Global umgerechnet wird **nur** innerhalb von Masse und innerhalb von
    Volumen. Alles andere — Zaehleinheiten, gemischte Arten, Unbekanntes —
    liefert ``None``. Stueck in Kilogramm ist keine Umrechnung, sondern eine
    Annahme ueber das Gewicht.
    """
    q, z = normalisiere(quelle), normalisiere(ziel)
    if q == z and art(q) is not None:
        return Decimal(1)
    if q in MASSE_IN_KG and z in MASSE_IN_KG:
        return MASSE_IN_KG[q] / MASSE_IN_KG[z]
    if q in VOLUMEN_IN_L and z in VOLUMEN_IN_L:
        return VOLUMEN_IN_L[q] / VOLUMEN_IN_L[z]
    return None


@dataclass(frozen=True)
class Gebinde:
    """Eine Stufe der Verpackungsleiter eines Artikels.

    ``faktor`` ist die Menge in ``je_einheit`` — standardmaessig die
    Basiseinheit des Artikels, aber ausdruecklich auch eine **andere
    Gebindestufe**. Genau so wird im Handel gedacht und bei der Artikelanlage
    eingepflegt:

    * Duenger: ``Gebinde("sack", 25)`` → 25 kg (Basis).
    * Hybrid-/Maissaatgut: ``Gebinde("einheit", 50000, je_einheit="st")`` →
      eine Einheit sind 50.000 Koerner; ``Gebinde("sack", 1,
      je_einheit="einheit")`` → ein Sack **ist** eine Einheit; und
      ``Gebinde("big_bag", 11, je_einheit="einheit")`` → ein Big Bag enthaelt
      elf Einheiten.

    Die Alternative — alles auf die Basiseinheit umzurechnen — waere fachlich
    dasselbe, aber niemand pflegt "ein Big Bag = 550.000 Koerner" ein. Er pflegt
    elf Einheiten ein, und das Modell rechnet.
    """

    einheit: str
    faktor: Decimal
    #: Bezugsgroesse des Faktors. ``None`` = Basiseinheit des Artikels.
    je_einheit: str | None = None
    bezeichnung: str = ""

    def __post_init__(self) -> None:
        if self.faktor <= 0:
            raise ValueError("Gebindefaktor muss positiv sein")
        if art(self.einheit) is None:
            raise ValueError(f"Unbekannte Gebindeeinheit: {self.einheit!r}")
        if self.je_einheit is not None and art(self.je_einheit) is None:
            raise ValueError(f"Unbekannte Bezugseinheit: {self.je_einheit!r}")
        if self.je_einheit is not None and normalisiere(self.je_einheit) == normalisiere(self.einheit):
            raise ValueError(
                f"Gebinde {self.einheit!r} kann sich nicht auf sich selbst beziehen"
            )


@dataclass(frozen=True)
class ArtikelEinheiten:
    """Einheitenprofil eines Artikels.

    ``teilbar=False`` bedeutet: nur ganze Gebinde. Das ist bei
    Pflanzenschutzmitteln **keine Einstellung, sondern Fachrecht** — sie duerfen
    nur in der Originalverpackung abgegeben werden, ein Umfuellen in kleinere
    Einheiten ist unzulaessig. "Halber Kanister" ist deshalb keine zulaessige
    Teilmenge.
    """

    basis_einheit: str
    #: Bevorzugte Anzeige- und Abrechnungsgroesse, z. B. ``dt`` bei Getreide.
    handels_einheit: str | None = None
    gebinde: tuple[Gebinde, ...] = ()
    teilbar: bool = True

    def faktor(self, quelle: str, ziel: str) -> Decimal | None:
        """Umrechnung im Kontext **dieses** Artikels.

        Zuerst global (Masse/Volumen), dann ueber die Gebindeleiter. Eine
        Zaehleinheit ohne hinterlegtes Gebinde bleibt unumrechenbar — auch wenn
        sie im System bekannt ist.
        """
        q, z = normalisiere(quelle), normalisiere(ziel)
        direkt = globaler_faktor(q, z)
        if direkt is not None:
            return direkt

        basis = normalisiere(self.basis_einheit)
        nach_basis = self._in_basis(q, basis)
        von_basis = self._in_basis(z, basis)
        if nach_basis is None or von_basis is None:
            return None
        return nach_basis / von_basis

    def _in_basis(self, einheit: str, basis: str, gesehen: frozenset[str] = frozenset()) -> Decimal | None:
        """Wie viele Basiseinheiten sind eine Einheit ``einheit``?

        Folgt der Verpackungsleiter so weit noetig: Big Bag -> Einheit -> Korn.
        Ein Ring in der Pflege (A bezieht sich auf B, B auf A) wuerde sonst
        endlos laufen; ``gesehen`` bricht ihn ab und liefert ``None``, statt zu
        haengen oder eine Zahl zu erfinden.
        """
        if einheit == basis:
            return Decimal(1)
        if einheit in gesehen:
            return None

        for gebinde in self.gebinde:
            if normalisiere(gebinde.einheit) != einheit:
                continue
            bezug = normalisiere(gebinde.je_einheit) if gebinde.je_einheit else basis
            if bezug == basis:
                return gebinde.faktor
            weiter = self._in_basis(bezug, basis, gesehen | {einheit})
            return None if weiter is None else gebinde.faktor * weiter

        # Masse/Volumen relativ zur Basis, falls beide derselben Art sind.
        return globaler_faktor(einheit, basis)


class PackAufloesung(str, Enum):
    """Wie ein Pack behandelt werden darf."""

    #: Darf in seine Artikel zerlegt und einzeln gebucht werden — Rollenrecht.
    AUFLOESBAR = "aufloesbar"
    #: Artikel duerfen nur miteinander verkauft und zurueckgenommen werden.
    GESPERRT = "gesperrt"


@dataclass(frozen=True)
class PackPosition:
    artikel_id: str
    menge: Decimal
    einheit: str


@dataclass(frozen=True)
class Pack:
    """Verbund **verschiedener** Artikel als eine Verkaufseinheit.

    Im Pflanzenschutz ueblich (Mittel plus Additiv). Fachlich dem verknuepften
    Artikel aehnlich, aber mit eigener Regel: Ein gesperrter Pack darf nur als
    Ganzes verkauft **und nur als Ganzes zurueckgenommen** werden. Eine
    Teilrueckgabe ist dort keine Mengenfrage, sondern unzulaessig.
    """

    pack_id: str
    positionen: tuple[PackPosition, ...]
    aufloesung: PackAufloesung = PackAufloesung.GESPERRT
    #: Recht, das die Aufloesung erlaubt. ``None`` = niemand darf.
    aufloesung_permission: str | None = None
    bezeichnung: str = ""

    def darf_aufloesen(self, permissions: frozenset[str] | set[str] | None) -> bool:
        """Darf dieser Aufrufer den Pack zerlegen?

        Zwei Bedingungen, beide notwendig: der Pack muss aufloesbar **sein**, und
        der Aufrufer muss das Recht **haben**. Ein gesperrter Pack bleibt
        gesperrt, egal welche Rechte jemand mitbringt — die Sperre ist eine
        fachliche Eigenschaft des Verbunds, kein Berechtigungsthema.
        """
        if self.aufloesung is not PackAufloesung.AUFLOESBAR:
            return False
        if not self.aufloesung_permission:
            return False
        return self.aufloesung_permission in (permissions or frozenset())

    def aufloesen(self, permissions: frozenset[str] | set[str] | None) -> tuple[PackPosition, ...]:
        """Pack in seine Artikel zerlegen.

        Wirft, wenn es nicht erlaubt ist — und zwar mit dem Grund, damit die
        Maske ihn anzeigen kann statt nur "nicht moeglich".
        """
        if self.aufloesung is not PackAufloesung.AUFLOESBAR:
            raise PackGesperrtError(
                f"Pack {self.pack_id} ist gesperrt: Die Artikel duerfen nur "
                "miteinander verkauft und zurueckgenommen werden."
            )
        if not self.darf_aufloesen(permissions):
            raise PackRechtFehltError(
                f"Pack {self.pack_id} darf aufgeloest werden, aber dieses Recht "
                f"fehlt ({self.aufloesung_permission})."
            )
        return self.positionen


class PackGesperrtError(RuntimeError):
    """Der Pack ist fachlich gesperrt — kein Rollenrecht hilft."""


class PackRechtFehltError(PermissionError):
    """Der Pack waere aufloesbar, aber dem Aufrufer fehlt das Recht."""


def ist_zulaessige_menge(profil: ArtikelEinheiten, menge: Decimal, einheit: str) -> bool:
    """Ist diese Menge fuer diesen Artikel ueberhaupt buchbar?

    Bei nicht teilbaren Artikeln — Pflanzenschutz in Originalgebinde, gesperrter
    Pack — sind nur **ganze** Gebinde zulaessig. Das ist keine Strenge des
    Modells, sondern die Abgabevorschrift.
    """
    if menge <= 0:
        return False
    if profil.teilbar:
        return True
    return menge == menge.to_integral_value()
