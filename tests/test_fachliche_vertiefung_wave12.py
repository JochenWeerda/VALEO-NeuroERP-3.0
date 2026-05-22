"""Unit-Tests für Fachliche Vertiefung Wave 12.

Zu-/Abschlaggruppen [ZAGR], Zu-/Abschlagklassen [ZAKL], Vertreterprovisionen.
"""
import pytest
from decimal import Decimal
from datetime import date


class TestZuAbschlaggruppen:
    def test_create_vk(self):
        from app.api.v1.endpoints.zu_abschlaggruppen import ZuAbschlaggruppeCreate
        g = ZuAbschlaggruppeCreate(gruppe_nr="ZAG-001", bezeichnung="Getreide VK", richtung="vk")
        assert g.richtung == "vk"

    def test_create_ek(self):
        from app.api.v1.endpoints.zu_abschlaggruppen import ZuAbschlaggruppeCreate
        g = ZuAbschlaggruppeCreate(gruppe_nr="ZAG-002", bezeichnung="Dünger EK", richtung="ek")
        assert g.richtung == "ek"

    def test_ungueltige_richtung(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.zu_abschlaggruppen import ZuAbschlaggruppeCreate
        with pytest.raises((ValueError, ValidationError)):
            ZuAbschlaggruppeCreate(gruppe_nr="X", bezeichnung="Test", richtung="export")


class TestZuAbschlagklassen:
    def test_create_klasse(self):
        from app.api.v1.endpoints.zu_abschlaggruppen import ZuAbschlagklasseCreate
        k = ZuAbschlagklasseCreate(klasse_nr="ZAK-A", bezeichnung="Premiumkunde VK", richtung="vk")
        assert k.klasse_nr == "ZAK-A"

    def test_richtung_default_vk(self):
        from app.api.v1.endpoints.zu_abschlaggruppen import ZuAbschlagklasseCreate
        k = ZuAbschlagklasseCreate(klasse_nr="ZAK-B", bezeichnung="Standard")
        assert k.richtung == "vk"


class TestZuAbschlagKonditionen:
    def test_kondition_prozent(self):
        from app.api.v1.endpoints.zu_abschlaggruppen import ZuAbschlagKonditionCreate
        k = ZuAbschlagKonditionCreate(
            gruppe_id="g-1",
            klasse_id="k-1",
            kondition_typ="prozent",
            wert=Decimal("2.5"),
            gueltig_ab=date(2024, 1, 1),
        )
        assert k.wert == Decimal("2.5")
        assert k.kondition_typ == "prozent"

    def test_kondition_betrag(self):
        from app.api.v1.endpoints.zu_abschlaggruppen import ZuAbschlagKonditionCreate
        k = ZuAbschlagKonditionCreate(
            gruppe_id="g-1",
            klasse_id="k-1",
            kondition_typ="betrag",
            wert=Decimal("-5.00"),
            gueltig_ab=date(2024, 1, 1),
        )
        assert k.wert < 0  # Abschlag

    def test_ungueltige_kondition_typ(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.zu_abschlaggruppen import ZuAbschlagKonditionCreate
        with pytest.raises((ValueError, ValidationError)):
            ZuAbschlagKonditionCreate(
                gruppe_id="g-1",
                klasse_id="k-1",
                kondition_typ="staffel",
                wert=Decimal("1.0"),
                gueltig_ab=date(2024, 1, 1),
            )

    def test_gueltig_bis_optional(self):
        from app.api.v1.endpoints.zu_abschlaggruppen import ZuAbschlagKonditionCreate
        k = ZuAbschlagKonditionCreate(
            gruppe_id="g-1",
            klasse_id="k-1",
            wert=Decimal("3.0"),
            gueltig_ab=date(2024, 1, 1),
        )
        assert k.gueltig_bis is None


class TestVertreterProvisionsgruppen:
    def test_create_fix(self):
        from app.api.v1.endpoints.vertreterprovisionen import ProvisionsGruppeCreate
        g = ProvisionsGruppeCreate(
            gruppe_nr="PG-VK-01",
            bezeichnung="Standard-Provision VK",
            richtung="vk",
            provisionstyp="fix",
            provisionssatz=Decimal("1.5"),
        )
        assert g.provisionssatz == Decimal("1.5")
        assert g.provisionstyp == "fix"

    def test_fix_ohne_satz_fehler(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.vertreterprovisionen import ProvisionsGruppeCreate
        with pytest.raises((ValueError, ValidationError)):
            ProvisionsGruppeCreate(
                gruppe_nr="X",
                bezeichnung="Test",
                provisionstyp="fix",
                # provisionssatz fehlt
            )

    def test_staffel_typ(self):
        from app.api.v1.endpoints.vertreterprovisionen import ProvisionsGruppeCreate
        g = ProvisionsGruppeCreate(
            gruppe_nr="PG-STAFFEL",
            bezeichnung="Staffel-Provision",
            provisionstyp="staffel_optpreis",
        )
        assert g.provisionstyp == "staffel_optpreis"
        assert g.provisionssatz is None

    def test_provisionstypen(self):
        from app.api.v1.endpoints.vertreterprovisionen import GUELTIGE_PROVISIONSTYPEN
        assert "fix" in GUELTIGE_PROVISIONSTYPEN
        assert "staffel_optpreis" in GUELTIGE_PROVISIONSTYPEN
        assert "staffel_preis_zuab" in GUELTIGE_PROVISIONSTYPEN

    def test_ungueltige_richtung(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.vertreterprovisionen import ProvisionsGruppeCreate
        with pytest.raises((ValueError, ValidationError)):
            ProvisionsGruppeCreate(
                gruppe_nr="X",
                bezeichnung="Test",
                richtung="ungueltig",
                provisionstyp="fix",
                provisionssatz=Decimal("1.0"),
            )


class TestVertreterProvisionsstaffeln:
    def test_create_staffel(self):
        from app.api.v1.endpoints.vertreterprovisionen import (
            ProvisionsStaffelCreate, ProvisionsStaffelZeileCreate
        )
        s = ProvisionsStaffelCreate(
            gruppe_id="pg-1",
            vertreterklasse="VKL-A",
            zeilen=[
                ProvisionsStaffelZeileCreate(zeile_nr=1, ab_wert=Decimal("0"), provisionssatz=Decimal("1.0")),
                ProvisionsStaffelZeileCreate(zeile_nr=2, ab_wert=Decimal("10000"), provisionssatz=Decimal("1.5")),
                ProvisionsStaffelZeileCreate(zeile_nr=3, ab_wert=Decimal("50000"), provisionssatz=Decimal("2.0")),
            ]
        )
        assert len(s.zeilen) == 3
        assert s.zeilen[2].provisionssatz == Decimal("2.0")

    def test_staffel_ohne_zeilen(self):
        from app.api.v1.endpoints.vertreterprovisionen import ProvisionsStaffelCreate
        s = ProvisionsStaffelCreate(gruppe_id="pg-1")
        assert s.zeilen == []
        assert s.vertreterklasse is None
