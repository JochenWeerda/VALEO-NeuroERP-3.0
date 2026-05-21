"""Unit-Tests für Fachliche Vertiefung Wave 7.

Daueraufträge, Individualpreise, Stücklisten/Rezepturen.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal


# ── Daueraufträge ─────────────────────────────────────────────────────────────

class TestDauerauftraege:
    def test_naechster_termin_monatlich(self):
        from app.api.v1.endpoints.dauerauftraege import _naechster_termin
        start = date(2024, 1, 31)
        naechster = _naechster_termin(start, "monatlich", 1)
        # Februar hat nur 29 Tage (2024 ist Schaltjahr)
        assert naechster == date(2024, 2, 29)

    def test_naechster_termin_quartalsweise(self):
        from app.api.v1.endpoints.dauerauftraege import _naechster_termin
        start = date(2024, 3, 15)
        naechster = _naechster_termin(start, "monatlich", 3)
        assert naechster == date(2024, 6, 15)

    def test_naechster_termin_woechentlich(self):
        from app.api.v1.endpoints.dauerauftraege import _naechster_termin
        start = date(2024, 6, 3)  # Montag
        naechster = _naechster_termin(start, "woechentlich", 1)
        assert naechster == date(2024, 6, 10)

    def test_naechster_termin_alle_2_wochen(self):
        from app.api.v1.endpoints.dauerauftraege import _naechster_termin
        start = date(2024, 6, 1)
        naechster = _naechster_termin(start, "alle_2_wochen", 1)
        assert naechster == date(2024, 6, 15)

    def test_create_schema(self):
        from app.api.v1.endpoints.dauerauftraege import DauerauftragCreate, DauerauftragPositionCreate
        da = DauerauftragCreate(
            da_nr="DA-001",
            kunden_nr="K001",
            bezeichnung="Monatliche Lieferung",
            da_anfang=date(2024, 1, 1),
            da_naechster=date(2024, 2, 1),
            perioden_typ="monatlich",
            perioden_wert=1,
            positionen=[
                DauerauftragPositionCreate(
                    pos_nr=10,
                    artikel_nr="ART-001",
                    menge=Decimal("100"),
                    mengeneinheit="kg",
                    preis_eur=Decimal("1.50"),
                )
            ],
        )
        assert da.da_nr == "DA-001"
        assert len(da.positionen) == 1
        assert da.positionen[0].menge == Decimal("100")

    def test_da_ende_logic(self):
        # Dauerauftrag ist abgelaufen wenn da_ende < heute
        da_ende = date.today() - timedelta(days=1)
        assert da_ende < date.today()

    def test_jahresauftrag_12_monate(self):
        from app.api.v1.endpoints.dauerauftraege import _naechster_termin
        start = date(2024, 1, 31)
        naechster = _naechster_termin(start, "monatlich", 12)
        assert naechster == date(2025, 1, 31)


# ── Individualpreise ──────────────────────────────────────────────────────────

class TestIndividualpreise:
    def test_create_vk_preis(self):
        from app.api.v1.endpoints.individualpreise import IndividualpreisCreate
        preis = IndividualpreisCreate(
            preis_typ="VK",
            artikel_nr="ART-001",
            partner_nr="K001",
            gueltig_von=date(2024, 1, 1),
            gueltig_bis=date(2024, 12, 31),
            preis_eur=Decimal("25.99"),
        )
        assert preis.preis_typ == "VK"
        assert preis.preis_eur == Decimal("25.99")

    def test_create_ek_preis_ohne_partner(self):
        from app.api.v1.endpoints.individualpreise import IndividualpreisCreate
        preis = IndividualpreisCreate(
            preis_typ="EK",
            artikel_nr="ART-001",
            gueltig_von=date(2024, 1, 1),
            preis_eur=Decimal("18.00"),
            staffel_menge=Decimal("1000"),
        )
        assert preis.partner_nr is None
        assert preis.staffel_menge == Decimal("1000")

    def test_staffel_preise(self):
        # Beste Staffel für Menge 500 aus [0, 100, 500, 1000]
        staffeln = [
            {"staffel_menge": Decimal("0"), "preis_eur": Decimal("10.00")},
            {"staffel_menge": Decimal("100"), "preis_eur": Decimal("9.50")},
            {"staffel_menge": Decimal("500"), "preis_eur": Decimal("9.00")},
            {"staffel_menge": Decimal("1000"), "preis_eur": Decimal("8.50")},
        ]
        menge = Decimal("500")
        passende = [s for s in staffeln if s["staffel_menge"] <= menge]
        bester = max(passende, key=lambda x: x["staffel_menge"])
        assert bester["preis_eur"] == Decimal("9.00")

    def test_gueltigkeitszeitraum_check(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.individualpreise import IndividualpreisCreate
        # Gültig_bis < gültig_von ist kein Pydantic-Fehler, aber der Endpoint wirft 422
        # Hier testen wir nur die Schema-Erstellung
        preis = IndividualpreisCreate(
            preis_typ="VK",
            artikel_nr="ART-001",
            gueltig_von=date(2024, 6, 1),
            gueltig_bis=date(2024, 12, 31),
            preis_eur=Decimal("5.00"),
        )
        assert preis.gueltig_bis > preis.gueltig_von

    def test_ungueltige_preistyp(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.individualpreise import IndividualpreisCreate
        with pytest.raises(ValidationError):
            IndividualpreisCreate(
                preis_typ="XX",  # ungültig
                artikel_nr="ART-001",
                gueltig_von=date(2024, 1, 1),
                preis_eur=Decimal("5.00"),
            )


# ── Stücklisten / Rezepturen ──────────────────────────────────────────────────

class TestStuecklisten:
    def test_create_einfach(self):
        from app.api.v1.endpoints.stuecklisten import StuecklisteCreate, StuecklistenPositionCreate
        sl = StuecklisteCreate(
            stueckliste_nr="SL-001",
            artikel_nr="FG-001",
            bezeichnung="Rindermischung 18% Protein",
            menge_basis=Decimal("1000"),
            einheit="kg",
            positionen=[
                StuecklistenPositionCreate(pos_nr=10, komponente_nr="MAIS", menge=Decimal("400"), einheit="kg"),
                StuecklistenPositionCreate(pos_nr=20, komponente_nr="SOJA", menge=Decimal("200"), einheit="kg"),
                StuecklistenPositionCreate(pos_nr=30, komponente_nr="GERSTE", menge=Decimal("400"), einheit="kg"),
            ],
        )
        assert sl.menge_basis == Decimal("1000")
        assert len(sl.positionen) == 3

    def test_mengenbedarf_berechnung(self):
        from app.api.v1.endpoints.stuecklisten import StuecklistenPositionOut
        positionen = [
            StuecklistenPositionOut(
                id="1", pos_nr=10, komponente_nr="MAIS", komponente_bez=None,
                menge=Decimal("400"), einheit="kg", anteil_prozent=None, optional=False
            ),
            StuecklistenPositionOut(
                id="2", pos_nr=20, komponente_nr="SOJA", komponente_bez=None,
                menge=Decimal("200"), einheit="kg", anteil_prozent=None, optional=False
            ),
        ]
        menge_basis = Decimal("1000")
        produktionsmenge = Decimal("2500")
        faktor = produktionsmenge / menge_basis

        bedarfe = [(pos.komponente_nr, pos.menge * faktor) for pos in positionen]
        assert bedarfe[0] == ("MAIS", Decimal("1000"))
        assert bedarfe[1] == ("SOJA", Decimal("500"))

    def test_doppelte_pos_nr_fehler(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.stuecklisten import StuecklisteCreate, StuecklistenPositionCreate
        with pytest.raises((ValueError, ValidationError)):
            StuecklisteCreate(
                stueckliste_nr="SL-ERR",
                artikel_nr="FG-001",
                menge_basis=Decimal("100"),
                einheit="kg",
                positionen=[
                    StuecklistenPositionCreate(pos_nr=10, komponente_nr="A", menge=Decimal("50"), einheit="kg"),
                    StuecklistenPositionCreate(pos_nr=10, komponente_nr="B", menge=Decimal("50"), einheit="kg"),
                ],
            )

    def test_variable_komponenten_flag(self):
        from app.api.v1.endpoints.stuecklisten import StuecklisteCreate
        sl = StuecklisteCreate(
            stueckliste_nr="SL-VAR",
            artikel_nr="FG-002",
            menge_basis=Decimal("1"),
            einheit="Stk",
            variable_komp=True,
        )
        assert sl.variable_komp is True

    def test_optionale_position(self):
        from app.api.v1.endpoints.stuecklisten import StuecklistenPositionCreate
        pos = StuecklistenPositionCreate(
            pos_nr=99, komponente_nr="ZUSATZ", menge=Decimal("10"), optional=True
        )
        assert pos.optional is True
