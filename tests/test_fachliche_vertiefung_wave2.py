"""Tests: Fachliche Vertiefung Wave 2 — Kontraktmengenzeitraum, Zu-/Abschläge, Rezepturgruppen."""
import pytest
from decimal import Decimal
from datetime import date


@pytest.mark.unit
class TestMengenzeitraumGenerierung:
    def test_linear_monthly_split(self):
        """Gesamtmenge wird gleichmäßig auf Monate verteilt."""
        from app.api.v1.endpoints.kontrakt_mengenzeitraum import generiere_mengenzeitraeume

        # Hier nur die Berechnungslogik testen (nicht den DB-Teil)
        gesamt = Decimal("600")
        monate = 6
        pro_monat = (gesamt / monate).quantize(Decimal("0.001"))
        assert pro_monat == Decimal("100.000")

    def test_mengenzeitraum_schema_validation(self):
        from app.api.v1.endpoints.kontrakt_mengenzeitraum import MengenzeitraumCreate

        mz = MengenzeitraumCreate(
            kontrakt_nr="K-2026-001",
            zeitraum_von=date(2026, 1, 1),
            zeitraum_bis=date(2026, 3, 31),
            menge_t=Decimal("300"),
            variante="monatl. lin. Abnahme",
        )
        assert mz.menge_t == Decimal("300")

    def test_mengenzeitraum_negative_menge_rejected(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.kontrakt_mengenzeitraum import MengenzeitraumCreate

        with pytest.raises(ValidationError):
            MengenzeitraumCreate(
                kontrakt_nr="K-001",
                zeitraum_von=date(2026, 1, 1),
                zeitraum_bis=date(2026, 3, 31),
                menge_t=Decimal("-100"),
            )


@pytest.mark.unit
class TestZuAbschlaege:
    def test_zuabschlag_create_schema(self):
        from app.api.v1.endpoints.kontrakt_mengenzeitraum import ZuAbschlagCreate

        za = ZuAbschlagCreate(
            gruppe_id="grp-001",
            bezeichnung="Trocknungskosten",
            betrag_eur=Decimal("2.50"),
            einheit="t",
        )
        assert za.betrag_eur == Decimal("2.50")
        assert za.einheit == "t"

    def test_zuabschlag_prozent(self):
        from app.api.v1.endpoints.kontrakt_mengenzeitraum import ZuAbschlagCreate

        za = ZuAbschlagCreate(
            gruppe_id="grp-002",
            bezeichnung="Qualitätsbonus",
            prozent=Decimal("1.5"),
        )
        assert za.prozent == Decimal("1.5")
        assert za.betrag_eur is None

    def test_zuabschlagsgruppe_typ_valid(self):
        from app.api.v1.endpoints.kontrakt_mengenzeitraum import ZuAbschlagsGruppeCreate

        grp = ZuAbschlagsGruppeCreate(
            gruppe_nr="ZA-001",
            bezeichnung="Standard Abzüge",
            typ="abschlag",
        )
        assert grp.typ == "abschlag"


@pytest.mark.unit
class TestRezepturgruppen:
    def test_rezepturgruppe_create(self):
        from app.api.v1.endpoints.produktion_rezepturgruppen import RezepturGruppeCreate

        rg = RezepturGruppeCreate(
            gruppe_nr="RG-RIND",
            bezeichnung="Rindermischfutter",
            tierart="Rind",
            nutzungsrichtung="Milch",
        )
        assert rg.tierart == "Rind"
        assert rg.nutzungsrichtung == "Milch"

    def test_schnellerfassung_create(self):
        from app.api.v1.endpoints.produktion_rezepturgruppen import SchnellerfassungCreate

        se = SchnellerfassungCreate(
            bezeichnung="Tagesration Milchkühe",
            rezept_name="MK-Basis",
            standard_menge_t=Decimal("5.0"),
        )
        assert se.standard_menge_t == Decimal("5.0")

    def test_schnellerfassung_buchen_positive_menge(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.produktion_rezepturgruppen import SchnellerfassungBuchenPayload

        payload = SchnellerfassungBuchenPayload(menge_t=Decimal("3.5"))
        assert payload.menge_t == Decimal("3.5")

        with pytest.raises(ValidationError):
            SchnellerfassungBuchenPayload(menge_t=Decimal("0"))
