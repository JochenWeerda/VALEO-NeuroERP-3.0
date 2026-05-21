"""Tests: Fachliche Vertiefung Wave 1 — Massebilanz, Zinsabrechnung, Hofliste, Artikel-Ext."""
import pytest
from decimal import Decimal
from datetime import date


# ── Massebilanz ───────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestMassebilanzSchema:
    def test_massebilanz_periode_format(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.massebilanz import MassebilanzCreate

        valid = MassebilanzCreate(periode="2026-05", anfangsbestand_kg=Decimal("1000"))
        assert valid.periode == "2026-05"

        with pytest.raises(ValidationError):
            MassebilanzCreate(periode="2026", anfangsbestand_kg=Decimal("0"))

    def test_massebilanz_vorzeichen_valid(self):
        from pydantic import ValidationError
        from app.api.v1.endpoints.massebilanz import BewegungCreate

        valid = BewegungCreate(
            massebilanz_id="test-id",
            buchungsdatum=date(2026, 5, 1),
            menge_kg=Decimal("500"),
            vorzeichen="+",
        )
        assert valid.vorzeichen == "+"

        with pytest.raises(ValidationError):
            BewegungCreate(
                massebilanz_id="test-id",
                buchungsdatum=date(2026, 5, 1),
                menge_kg=Decimal("500"),
                vorzeichen="x",
            )


# ── Zinsabrechnung ────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestZinsabrechnungBerechnung:
    def test_zins_berechnung_korrekt(self):
        from app.api.v1.endpoints.zinsabrechnung import _berechne_zins

        von = date(2026, 1, 1)
        bis = date(2026, 4, 1)  # 90 Tage
        tage, zinsbetrag, mwst = _berechne_zins(
            Decimal("100000"), Decimal("4.0"), von, bis
        )
        assert tage == 90
        # 100000 * 4% * 90/360 = 1000.00
        assert zinsbetrag == Decimal("1000.00")

    def test_zins_berechnung_negative_tage_raises(self):
        from app.api.v1.endpoints.zinsabrechnung import _berechne_zins

        with pytest.raises(ValueError, match="bis_datum"):
            _berechne_zins(
                Decimal("100000"), Decimal("4.0"),
                date(2026, 5, 1), date(2026, 1, 1)
            )

    def test_zins_volle_jahresrate(self):
        from app.api.v1.endpoints.zinsabrechnung import _berechne_zins

        # 360 Tage = genau ein Jahr
        von = date(2026, 1, 1)
        bis = date(2026, 12, 27)  # 360 Tage
        tage, zinsbetrag, _ = _berechne_zins(
            Decimal("100000"), Decimal("3.5"), von, bis
        )
        assert tage == 360
        # 100000 * 3.5% * 360/360 = 3500.00
        assert zinsbetrag == Decimal("3500.00")


# ── Hofliste ──────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestHoflisteSchema:
    def test_hofliste_create_valid(self):
        from app.api.v1.endpoints.hofliste import HoflisteCreate

        entry = HoflisteCreate(
            kfz_kennzeichen="OS-AB 1234",
            fahrer_name="Max Mustermann",
            kontrakt_nr="K-2026-001",
            geplante_menge_t=Decimal("25.5"),
        )
        assert entry.kfz_kennzeichen == "OS-AB 1234"
        assert entry.partievorerfassung is False

    def test_valid_status_list(self):
        from app.api.v1.endpoints.hofliste import VALID_STATUS

        assert "vorgemeldet" in VALID_STATUS
        assert "auf_hof" in VALID_STATUS
        assert "abgefahren" in VALID_STATUS
        assert len(VALID_STATUS) == 5


# ── Folgeartikel ──────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestFolgeArtikelSchema:
    def test_folgeartikel_create_valid(self):
        from app.api.v1.endpoints.artikel_stamm_ext import FolgeartikelCreate

        fa = FolgeartikelCreate(
            artikel_nr="W-001",
            folge_artikel_nr="W-002",
            grund="Auslauf",
            automatisch_ersetzen=True,
        )
        assert fa.artikel_nr == "W-001"
        assert fa.automatisch_ersetzen is True


# ── Inventurgruppe ────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestInventurgruppeSchema:
    def test_inventurgruppe_create(self):
        from app.api.v1.endpoints.artikel_stamm_ext import InventurgruppeCreate

        grp = InventurgruppeCreate(
            gruppe_nr="A",
            bezeichnung="Jahresinventur - Agrarartikel",
            inventur_zyklus="jaehrlich",
        )
        assert grp.gruppe_nr == "A"
        assert grp.inventur_zyklus == "jaehrlich"


# ── Wiegungsgruppen ───────────────────────────────────────────────────────────

@pytest.mark.unit
class TestWiegungsgruppeSchema:
    def test_wiegungsgruppe_typ_valid(self):
        from app.api.v1.endpoints.artikel_stamm_ext import WiegungsgruppeCreate

        wg = WiegungsgruppeCreate(
            typ="gerafft",
            wiegeschein_ids=["wg-001", "wg-002"],
            kontrakt_nr="K-2026-001",
        )
        assert wg.typ == "gerafft"
        assert len(wg.wiegeschein_ids) == 2

    def test_wiegungsgruppe_aufgeteilt(self):
        from app.api.v1.endpoints.artikel_stamm_ext import WiegungsgruppeCreate

        wg = WiegungsgruppeCreate(
            typ="aufgeteilt",
            wiegeschein_ids=["wg-010"],
        )
        assert wg.typ == "aufgeteilt"
