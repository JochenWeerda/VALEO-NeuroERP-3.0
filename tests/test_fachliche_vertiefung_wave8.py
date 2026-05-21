"""Unit-Tests für Fachliche Vertiefung Wave 8.

Rohwarengruppen, Rohware-Qualitäten, Zu-/Abschlag-Staffeln.
"""
import pytest
from decimal import Decimal


class TestRohwarengruppen:
    def test_create_schema(self):
        from app.api.v1.endpoints.rohwarengruppen import RohwarengruppeCreate
        g = RohwarengruppeCreate(
            gruppe_nr="G-GETREIDE",
            bezeichnung="Getreide EK",
            ek_aktiv=True,
            vk_aktiv=False,
            waehrung="EUR",
            mengeneinheit="t",
        )
        assert g.ek_aktiv is True
        assert g.vk_aktiv is False

    def test_abrechnungsschema_schema(self):
        from app.api.v1.endpoints.rohwarengruppen import AbrechnungsschemaCreate
        s = AbrechnungsschemaCreate(
            schema_nr="GERSTE-NORMAL",
            bezeichnung="Gerste normal",
            gruppe_id="dummy-id",
        )
        assert s.schema_nr == "GERSTE-NORMAL"

    def test_qualitaet_schema(self):
        from app.api.v1.endpoints.rohwarengruppen import RohwareQualitaetCreate
        q = RohwareQualitaetCreate(
            qualitaet_nr="FEUCHT-15",
            bezeichnung="Feuchtigkeit Basis 15%",
            gruppe_id="g1",
            basis_wert=Decimal("15.0"),
            basis_wert_bis=Decimal("15.5"),
            einheit="%",
            position_typ="qualitaet",
        )
        assert q.basis_wert == Decimal("15.0")
        assert q.position_typ == "qualitaet"

    def test_staffel_create_valid(self):
        from app.api.v1.endpoints.rohwarengruppen import ZaStaffelCreate, StaffelZeileCreate
        s = ZaStaffelCreate(
            staffel_nr="ST-FEUCHT",
            bezeichnung="Feuchtigkeitsstaffel",
            gruppe_id="g1",
            ergebnis_typ="preisabschlag",
            abrechnung_typ="gestaffelte_abrechnung",
            basiserweiterung=Decimal("0.5"),
            zeilen=[
                StaffelZeileCreate(zeile_nr=1, bis_wert=Decimal("4.4"), umrechnungsfaktor=Decimal("1.2")),
                StaffelZeileCreate(zeile_nr=2, bis_wert=Decimal("8.4"), umrechnungsfaktor=Decimal("1.3")),
                StaffelZeileCreate(zeile_nr=3, bis_wert=Decimal("20.0"), umrechnungsfaktor=Decimal("1.4")),
            ],
        )
        assert len(s.zeilen) == 3
        assert s.basiserweiterung == Decimal("0.5")

    def test_staffel_ungueltige_typen(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.rohwarengruppen import ZaStaffelCreate
        with pytest.raises((ValueError, ValidationError)):
            ZaStaffelCreate(
                staffel_nr="ST-BAD",
                bezeichnung="Test",
                gruppe_id="g1",
                ergebnis_typ="ungueltig",
                abrechnung_typ="einfacher_umrechnungsfaktor",
            )

    def test_berechnung_einfacher_faktor(self):
        from app.api.v1.endpoints.rohwarengruppen import _berechne_staffel
        zeilen = [
            {"bis_wert": Decimal("5.0"), "umrechnungsfaktor": Decimal("1.2")},
            {"bis_wert": Decimal("10.0"), "umrechnungsfaktor": Decimal("1.4")},
        ]
        # delta = 3.0, passt in erstes Intervall (bis 5.0)
        ergebnis = _berechne_staffel(zeilen, Decimal("3.0"), "einfacher_umrechnungsfaktor")
        assert ergebnis == Decimal("3.6000")

    def test_berechnung_gestaffelt_referenzbeispiel(self):
        from app.api.v1.endpoints.rohwarengruppen import _berechne_staffel
        # Referenz: delta = 9.8 (analysewert 18.3 - basis 9.0 + ext 0.5)
        # Intervalle: bis 4.4 → 1.2, bis 8.4 → 1.3, bis 20 → 1.4
        # Ergebnis: 4.4*1.2 + 4.0*1.3 + 1.4*1.4 = 5.28 + 5.20 + 1.96 = 12.44
        zeilen = [
            {"bis_wert": Decimal("4.4"), "umrechnungsfaktor": Decimal("1.2")},
            {"bis_wert": Decimal("8.4"), "umrechnungsfaktor": Decimal("1.3")},
            {"bis_wert": Decimal("20.0"), "umrechnungsfaktor": Decimal("1.4")},
        ]
        ergebnis = _berechne_staffel(zeilen, Decimal("9.8"), "gestaffelte_abrechnung")
        assert ergebnis == Decimal("12.4400")

    def test_delta_berechnung(self):
        # Referenz-Beispiel aus Domain 01:
        # Analysewert 18.3, Basiswert 9.0, Basiserweiterung 0.5
        # delta = (18.3 - 9.0) + 0.5 = 9.8
        analysewert = Decimal("18.3")
        basiswert = Decimal("9.0")
        basiserweiterung = Decimal("0.5")
        delta = analysewert - basiswert + basiserweiterung
        assert delta == Decimal("9.8")
