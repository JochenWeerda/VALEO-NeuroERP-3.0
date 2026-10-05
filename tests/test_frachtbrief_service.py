"""Der Frachtbrief entsteht erst aus einer vollständigen Verladung."""

from decimal import Decimal
from types import SimpleNamespace

from app.domains.logistik.sendung import (
    Belegart,
    FuehrenderSatz,
    FUEHREND,
    Sendung,
    frachtbrief_sicht,
    lieferschein_sicht,
)
from app.services.frachtbrief_service import fehlende_angaben


def _verladung(**overrides):
    daten = dict(
        status="verladen",
        kennzeichen="HH-AB 123",
        artikel="Weizen",
        menge=24.5,
        ladeort="Lager Ost",
        kunde="Mühle Nord",
        zielort="",
    )
    daten.update(overrides)
    return SimpleNamespace(**daten)


def test_vollstaendige_verladung_ist_bereit():
    assert fehlende_angaben(_verladung()) == []


def test_geplante_verladung_erzeugt_keinen_beleg():
    assert "verladung" in fehlende_angaben(_verladung(status="geplant"))


def test_ohne_uebernahmeort_und_empfaenger_fehlt_der_beleg():
    fehlend = fehlende_angaben(_verladung(ladeort="", kunde="", zielort=""))
    assert "uebernahmeort" in fehlend
    assert "empfaenger" in fehlend


def test_zielort_traegt_den_empfaenger():
    assert "empfaenger" not in fehlende_angaben(_verladung(kunde="", zielort="Silo West"))


def test_lieferschein_und_frachtbrief_sind_zwei_sichten():
    """Folkerts übergibt KAS an die Spedition; der Lieferschein bleibt das Handelsgeschäft."""
    sendung = Sendung(
        absender="Folkerts",
        empfaenger="Janssen",
        frachtfuehrer="Spedition Meyer",
        kennzeichen="EL-AB 123",
        anhaenger_kennzeichen="EL-CD 456",
        ladeort="Lager Emden",
        ablieferstelle="Betrieb Janssen",
        artikel="KAS 27 % N + 4 % MgO",
        verpackung="lose",
        menge=Decimal("25.460"),
        einheit="kg",
        brutto=Decimal("40.820"),
        tara=Decimal("15.360"),
        netto=Decimal("25.460"),
        charge="ABC123",
        lieferschein_nr="LS-2026-005841",
        auftrag_nr="100472",
    )
    waren = lieferschein_sicht(sendung)
    transport = frachtbrief_sicht(sendung)

    assert waren.belegart is Belegart.LIEFERSCHEIN
    assert transport.belegart is Belegart.FRACHTBRIEF
    assert waren.kunde == "Janssen"
    assert waren.auftrag_nr == "100472"
    assert waren.menge == Decimal("25.460")
    assert transport.frachtfuehrer == "Spedition Meyer"
    assert transport.kennzeichen == "EL-AB 123"
    assert transport.anhaenger_kennzeichen == "EL-CD 456"
    assert transport.lieferschein_nr == "LS-2026-005841"
    assert transport.netto == Decimal("25.460")
    assert not hasattr(waren, "kennzeichen")
    assert not hasattr(transport, "auftrag_nr")


def test_gewicht_gehoert_der_waage_handel_dem_lieferschein():
    assert FUEHREND["netto"] is FuehrenderSatz.WIEGUNG
    assert FUEHREND["handelsmenge"] is FuehrenderSatz.LIEFERSCHEIN
    assert FUEHREND["produktrecht"] is FuehrenderSatz.BEGLEITDOKUMENT
    assert FUEHREND["fahrzeug"] is FuehrenderSatz.VERLADUNG
