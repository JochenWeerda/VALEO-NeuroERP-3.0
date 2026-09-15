"""FSX-MENGENMODELL — Einheiten, Gebinde und Packs des Agrarhandels.

Die Faelle stammen aus der Recherche in
``docs/design/agrar-mengen-gebinde-modell.md`` und sind dort belegt. Sie sind
bewusst mit echten Handelsgroessen besetzt: 750.000 Koerner je Saatgetreidesack,
50.000 je Maiseinheit, 600 kg Big Bag, 25 kg Duengersack.

Der rote Faden: **keine Umrechnung ohne belegten Faktor.** Was nicht hinterlegt
ist, wird nicht geraten.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.agrar_units import (
    ArtikelEinheiten,
    Gebinde,
    Pack,
    PackAufloesung,
    PackGesperrtError,
    PackPosition,
    PackRechtFehltError,
    UnitKind,
    art,
    globaler_faktor,
    ist_zulaessige_menge,
    normalisiere,
)

pytestmark = pytest.mark.unit


# -- dt als Standardgroesse ----------------------------------------------------


def test_dezitonne_ist_hundert_kilogramm() -> None:
    assert globaler_faktor("dt", "kg") == Decimal(100)
    assert globaler_faktor("kg", "dt") == Decimal("0.01")
    assert globaler_faktor("t", "dt") == Decimal(10)


def test_doppelzentner_ist_dieselbe_groesse_wie_dezitonne() -> None:
    """dz hat die Dezitonne historisch vorweggenommen — 100 kg ist 100 kg."""
    assert globaler_faktor("dz", "dt") == Decimal(1)
    assert globaler_faktor("Doppelzentner", "kg") == Decimal(100)


def test_schreibweisen_werden_vereinheitlicht_ohne_zu_raten() -> None:
    assert normalisiere("Tonnen") == "t"
    assert normalisiere(" DT ") == "dt"
    assert normalisiere("EH") == "einheit"
    # Was nicht hinterlegt ist, bleibt wie es ist — und faellt dann als
    # unbekannt auf, statt still auf etwas Aehnliches zu zeigen.
    assert normalisiere("Fuder") == "fuder"
    assert art("Fuder") is None


# -- Die zentrale Trennung -----------------------------------------------------


def test_zaehleinheiten_werden_nicht_global_umgerechnet() -> None:
    """Der wichtigste Test der Datei.

    Ein Sack Duenger wiegt 25 kg, ein Sack Maissaatgut rund 15 kg. Ein globaler
    Faktor waere in mindestens einem der beiden Faelle falsch — und zwar
    unauffaellig falsch.
    """
    for einheit in ("sack", "kanister", "big_bag", "palette", "einheit", "st", "pack"):
        assert art(einheit) is UnitKind.ZAEHLEINHEIT
        assert globaler_faktor(einheit, "kg") is None, einheit
        assert globaler_faktor("kg", einheit) is None, einheit


def test_masse_und_volumen_werden_nicht_vermischt() -> None:
    assert globaler_faktor("l", "kg") is None
    assert globaler_faktor("kg", "l") is None
    # Innerhalb der Arten dagegen exakt.
    assert globaler_faktor("hl", "l") == Decimal(100)
    assert globaler_faktor("ml", "l") == Decimal("0.001")


# -- Gebinde je Artikel --------------------------------------------------------


def duenger() -> ArtikelEinheiten:
    return ArtikelEinheiten(
        basis_einheit="kg",
        handels_einheit="dt",
        gebinde=(
            Gebinde("sack", Decimal(25), bezeichnung="Sack 25 kg"),
            Gebinde("big_bag", Decimal(600), bezeichnung="Big Bag 600 kg"),
        ),
    )


def test_gebinde_rechnet_im_kontext_des_artikels() -> None:
    profil = duenger()
    assert profil.faktor("big_bag", "kg") == Decimal(600)
    assert profil.faktor("sack", "kg") == Decimal(25)
    # Und quer durch die Leiter: ein Big Bag sind 24 Saecke.
    assert profil.faktor("big_bag", "sack") == Decimal(24)
    # Ueber die Handelsgroesse: ein Big Bag sind 6 dt.
    assert profil.faktor("big_bag", "dt") == Decimal(6)


def test_unbekanntes_gebinde_bleibt_unumrechenbar() -> None:
    """Auch eine dem System bekannte Zaehleinheit hilft nicht ohne Faktor."""
    profil = duenger()
    # 'palette' ist eine gueltige Einheit, aber bei diesem Artikel nicht belegt.
    assert art("palette") is UnitKind.ZAEHLEINHEIT
    assert profil.faktor("palette", "kg") is None


def test_gebinde_mit_unsinnigem_faktor_wird_abgewiesen() -> None:
    with pytest.raises(ValueError):
        Gebinde("sack", Decimal(0))
    with pytest.raises(ValueError):
        Gebinde("fuder", Decimal(25))


# -- Saatgut: die Einheit ist eine Kornzahl ------------------------------------


def saatgetreide() -> ArtikelEinheiten:
    """Saatgetreide: 1 Einheit = 1 Mio. keimfaehige Koerner, Sack = 750.000."""
    return ArtikelEinheiten(
        basis_einheit="st",  # Koerner
        handels_einheit="einheit",
        gebinde=(
            Gebinde("einheit", Decimal(1_000_000), bezeichnung="1 Mio. keimfaehige Koerner"),
            Gebinde("sack", Decimal(750_000), bezeichnung="Sack 750.000 Koerner"),
        ),
    )


def mais(koerner_je_einheit: int = 50_000, einheiten_je_bigbag: int = 11) -> ArtikelEinheiten:
    """Hybrid-/Maissaatgut, so wie es bei der Artikelanlage eingepflegt wird.

    Bezugsgroesse ist die **Einheit (EH)**. Ein Sack *ist* eine Einheit; ein Big
    Bag enthaelt mehrere Einheiten. Die Kornzahl je Einheit ist artikelabhaengig
    — 50.000 oder 90.000 sind beide ueblich.
    """
    return ArtikelEinheiten(
        basis_einheit="st",
        handels_einheit="einheit",
        gebinde=(
            Gebinde("einheit", Decimal(koerner_je_einheit), je_einheit="st"),
            Gebinde("sack", Decimal(1), je_einheit="einheit", bezeichnung="1 Sack = 1 EH"),
            Gebinde("big_bag", Decimal(einheiten_je_bigbag), je_einheit="einheit"),
        ),
    )


def test_hybridsaatgut_wird_in_einheiten_gepflegt() -> None:
    """Die Leiter, wie sie im Handel gedacht wird: BB -> EH -> Korn.

    Niemand pflegt "ein Big Bag = 550.000 Koerner" ein. Er pflegt elf Einheiten
    ein, und das Modell rechnet den Rest.
    """
    profil = mais(koerner_je_einheit=50_000, einheiten_je_bigbag=11)

    assert profil.faktor("einheit", "st") == Decimal(50_000)
    assert profil.faktor("sack", "einheit") == Decimal(1)
    assert profil.faktor("big_bag", "einheit") == Decimal(11)
    # Und ueber zwei Stufen hinweg, ohne dass es jemand eingepflegt hat:
    assert profil.faktor("big_bag", "st") == Decimal(550_000)
    assert profil.faktor("big_bag", "sack") == Decimal(11)


def test_kornzahl_je_einheit_ist_artikelsache() -> None:
    """50.000 und 90.000 sind beide uebliche Einheitsgroessen.

    Zwei Artikel, derselbe Einheitenname, verschiedene Groesse — der Grund,
    warum 'einheit' keinen globalen Faktor haben darf.
    """
    assert mais(50_000).faktor("einheit", "st") == Decimal(50_000)
    assert mais(90_000).faktor("einheit", "st") == Decimal(90_000)
    # Ein Big Bag mit elf Einheiten ist entsprechend verschieden gross.
    assert mais(90_000, 11).faktor("big_bag", "st") == Decimal(990_000)


def test_ringbezug_in_der_pflege_wird_abgefangen() -> None:
    """Ein Pflegefehler darf nicht endlos laufen.

    Sack bezieht sich auf Big Bag, Big Bag auf Sack — die Leiter erreicht die
    Basis nie. Statt zu haengen oder eine Zahl zu erfinden: nicht umrechenbar.
    """
    ring = ArtikelEinheiten(
        basis_einheit="st",
        gebinde=(
            Gebinde("sack", Decimal(1), je_einheit="big_bag"),
            Gebinde("big_bag", Decimal(11), je_einheit="sack"),
        ),
    )
    assert ring.faktor("sack", "st") is None


def test_gebinde_kann_sich_nicht_auf_sich_selbst_beziehen() -> None:
    with pytest.raises(ValueError):
        Gebinde("sack", Decimal(2), je_einheit="sack")


def test_saatgut_einheit_ist_je_kultur_verschieden() -> None:
    """Derselbe Einheitenname, zwei verschiedene Groessen.

    Genau deshalb darf 'einheit' keinen globalen Faktor haben: Saatgetreide
    rechnet mit einer Million Koernern, Mais mit fuenfzigtausend.
    """
    assert saatgetreide().faktor("einheit", "st") == Decimal(1_000_000)
    assert mais().faktor("einheit", "st") == Decimal(50_000)


def test_saatgetreidesack_ist_dreiviertel_einheit() -> None:
    assert saatgetreide().faktor("sack", "einheit") == Decimal("0.75")


def test_saatgut_einheit_laesst_sich_nicht_in_kilogramm_umrechnen() -> None:
    """Der Fall, an dem ein gewichtsbasiertes Modell zerbricht.

    Das Gewicht einer Saatgut-Einheit haengt an Tausendkorngewicht und
    Keimfaehigkeit und schwankt je Partie. Es steht auf dem Etikett — zum
    Einstellen der Drillmaschine —, ist aber keine Handelsgroesse.
    """
    assert saatgetreide().faktor("einheit", "kg") is None
    assert mais().faktor("einheit", "kg") is None


# -- Pack: Verbund mit Rollenschranke ------------------------------------------


def psm_pack(aufloesung: PackAufloesung, recht: str | None = "psm.pack.aufloesen") -> Pack:
    return Pack(
        pack_id="PACK-1",
        positionen=(
            PackPosition("ART-HERBIZID", Decimal(2), "kanister"),
            PackPosition("ART-ADDITIV", Decimal(1), "kanister"),
        ),
        aufloesung=aufloesung,
        aufloesung_permission=recht,
    )


def test_gesperrter_pack_bleibt_gesperrt_egal_welche_rechte() -> None:
    """Die Sperre ist eine fachliche Eigenschaft, kein Berechtigungsthema.

    Wer alle Rechte der Welt hat, darf einen gesperrten Verbund trotzdem nicht
    zerlegen — die Artikel duerfen nur miteinander verkauft und zurueckgenommen
    werden.
    """
    pack = psm_pack(PackAufloesung.GESPERRT)
    assert pack.darf_aufloesen({"psm.pack.aufloesen", "admin", "alles"}) is False
    with pytest.raises(PackGesperrtError) as fehler:
        pack.aufloesen({"psm.pack.aufloesen"})
    assert "nur miteinander" in str(fehler.value)


def test_aufloesbarer_pack_braucht_trotzdem_das_recht() -> None:
    pack = psm_pack(PackAufloesung.AUFLOESBAR)
    assert pack.darf_aufloesen({"verkauf.lesen"}) is False
    with pytest.raises(PackRechtFehltError) as fehler:
        pack.aufloesen({"verkauf.lesen"})
    # Der Grund gehoert in die Meldung, damit die Maske ihn zeigen kann.
    assert "psm.pack.aufloesen" in str(fehler.value)


def test_aufloesbarer_pack_mit_recht_liefert_die_artikel() -> None:
    pack = psm_pack(PackAufloesung.AUFLOESBAR)
    positionen = pack.aufloesen({"psm.pack.aufloesen", "verkauf.schreiben"})
    assert [p.artikel_id for p in positionen] == ["ART-HERBIZID", "ART-ADDITIV"]


def test_pack_ohne_hinterlegtes_recht_ist_nicht_aufloesbar() -> None:
    """Kein Recht hinterlegt heisst: niemand darf — nicht: jeder darf."""
    pack = psm_pack(PackAufloesung.AUFLOESBAR, recht=None)
    assert pack.darf_aufloesen({"admin"}) is False
    with pytest.raises(PackRechtFehltError):
        pack.aufloesen({"admin"})


def test_leere_rechte_sind_zulaessig_und_bedeuten_nein() -> None:
    pack = psm_pack(PackAufloesung.AUFLOESBAR)
    assert pack.darf_aufloesen(None) is False
    assert pack.darf_aufloesen(set()) is False


# -- Teilbarkeit ist Fachrecht, nicht Einstellung ------------------------------


def psm_artikel() -> ArtikelEinheiten:
    """Pflanzenschutz: nur Originalgebinde, kein Umfuellen."""
    return ArtikelEinheiten(
        basis_einheit="l",
        gebinde=(Gebinde("kanister", Decimal(10), bezeichnung="Kanister 10 l"),),
        teilbar=False,
    )


def test_nicht_teilbarer_artikel_laesst_nur_ganze_gebinde_zu() -> None:
    profil = psm_artikel()
    assert ist_zulaessige_menge(profil, Decimal(2), "kanister") is True
    # "Halber Kanister" ist keine Mengenfrage, sondern unzulaessig: PSM duerfen
    # nur in der Originalverpackung abgegeben werden.
    assert ist_zulaessige_menge(profil, Decimal("0.5"), "kanister") is False


def test_teilbarer_artikel_laesst_teilmengen_zu() -> None:
    assert ist_zulaessige_menge(duenger(), Decimal("12.5"), "kg") is True


def test_null_und_negative_mengen_sind_nie_zulaessig() -> None:
    for profil in (duenger(), psm_artikel()):
        assert ist_zulaessige_menge(profil, Decimal(0), "kg") is False
        assert ist_zulaessige_menge(profil, Decimal(-1), "kg") is False
