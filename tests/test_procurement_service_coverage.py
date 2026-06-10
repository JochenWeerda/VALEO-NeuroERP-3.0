"""Tests für ProcurementService — Ziel: Coverage >50%.

Verwendet MagicMock für DB-Session.  Keine echte DB-Verbindung notwendig.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, PropertyMock
import pytest

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_db() -> MagicMock:
    """Erzeugt eine Mock-DB-Session."""
    db = MagicMock()
    db.query.return_value = db
    db.options.return_value = db
    db.filter.return_value = db
    db.order_by.return_value = db
    db.first.return_value = None
    db.all.return_value = []
    db.flush.return_value = None
    db.commit.return_value = None
    db.rollback.return_value = None
    db.add.return_value = None
    db.delete.return_value = None
    db.refresh.return_value = None
    return db


def _make_svc(db=None):
    from app.services.procurement_service import ProcurementService
    return ProcurementService(db=db or _make_db(), tenant_id="tenant-test")


def _make_lieferant(**kwargs):
    """Erstellt ein simuliertes EinkaufLieferant-Objekt."""
    defaults = {
        "id": "lf-001",
        "lieferantennummer": "LF-001",
        "firmenname": "Agrar Supplies GmbH",
        "ort": "Hannover",
        "plz": "30159",
        "email": "info@agrar.de",
        "telefon": "0511-123456",
        "partner_id": None,
        "zahlungsbedingungen": "14 Tage netto",
        "lieferzeit_tage": 3,
        "bewertung": 4,
        "aktiv": True,
    }
    defaults.update(kwargs)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    obj.__table__ = MagicMock()
    obj.__table__.columns = [
        SimpleNamespace(name=k) for k in defaults
    ]
    return obj


def _make_bestellung(**kwargs):
    defaults = {
        "id": "best-001",
        "bestellnummer": "EK-2600101",
        "tenant_id": "tenant-test",
        "lieferant_id": "lf-001",
        "bestelldatum": date(2026, 1, 1),
        "lieferdatum_wunsch": date(2026, 1, 10),
        "lieferdatum_zugesagt": None,
        "status": "entwurf",
        "versand_art": "email",
        "versandt_am": None,
        "netto_summe": Decimal("5000.00"),
        "mwst_betrag": Decimal("950.00"),
        "brutto_summe": Decimal("5950.00"),
        "unsere_referenz": None,
        "ihre_referenz": None,
        "freitext_kopf": None,
        "freitext_fuss": None,
        "notiz": None,
        "positionen": [],
        "lieferant": None,
    }
    defaults.update(kwargs)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_vorschlag(**kwargs):
    defaults = {
        "id": "vs-001",
        "vorschlag_typ": "lager",
        "bezeichnung": "Lager-Vorschlag Mai",
        "datum": date(2026, 5, 1),
        "status": "offen",
        "niederlassung_id": "nl-001",
        "erstellt_von": "system",
        "freigegeben_von": None,
        "freigegeben_am": None,
        "parameter": {},
        "positionen": [],
        "created_at": datetime(2026, 5, 1),
        "tenant_id": "tenant-test",
    }
    defaults.update(kwargs)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


# ── Tests: list_lieferanten ───────────────────────────────────────────────────

class TestListLieferanten:
    def test_returns_empty_list_when_none(self):
        svc = _make_svc()
        result = svc.list_lieferanten()
        assert result == []

    def test_returns_mapped_list(self):
        db = _make_db()
        lf = _make_lieferant()
        db.all.return_value = [lf]
        svc = _make_svc(db)
        result = svc.list_lieferanten()
        assert len(result) == 1
        assert result[0]["firmenname"] == "Agrar Supplies GmbH"
        assert result[0]["aktiv"] is True

    def test_filter_aktiv(self):
        svc = _make_svc()
        svc.list_lieferanten(aktiv=True)
        # filter wurde aufgerufen
        svc.db.filter.assert_called()

    def test_filter_suche(self):
        svc = _make_svc()
        svc.list_lieferanten(suche="Agrar")
        svc.db.filter.assert_called()


# ── Tests: get_lieferant ──────────────────────────────────────────────────────

class TestGetLieferant:
    def test_raises_not_found_when_missing(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError) as exc_info:
            svc.get_lieferant("missing-id")
        assert "EinkaufLieferant" in str(exc_info.value)

    def test_returns_dict_when_found(self):
        db = _make_db()
        lf = _make_lieferant()
        db.first.return_value = lf
        svc = _make_svc(db)
        result = svc.get_lieferant("lf-001")
        assert result["firmenname"] == "Agrar Supplies GmbH"


# ── Tests: create_lieferant ───────────────────────────────────────────────────

class TestCreateLieferant:
    def test_creates_lieferant(self):
        db = _make_db()
        new_lf = _make_lieferant(id="lf-new", lieferantennummer="LF-002", firmenname="Müller Agrar")
        db.refresh.side_effect = lambda obj: None
        # simulate post-commit state
        with patch("app.services.procurement_service.uuid7", return_value="lf-new"), \
             patch("app.services.procurement_service.EinkaufLieferant", return_value=new_lf):
            svc = _make_svc(db)
            result = svc.create_lieferant({"firmenname": "Müller Agrar", "lieferantennummer": "LF-002"})
        assert result["firmenname"] == "Müller Agrar"
        db.add.assert_called_once()
        db.commit.assert_called_once()


# ── Tests: update_lieferant ───────────────────────────────────────────────────

class TestUpdateLieferant:
    def test_raises_not_found(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError):
            svc.update_lieferant("missing-id", {"firmenname": "Test"})

    def test_updates_fields(self):
        db = _make_db()
        lf = _make_lieferant()
        db.first.return_value = lf
        svc = _make_svc(db)
        result = svc.update_lieferant("lf-001", {"firmenname": "Neuer Name"})
        assert lf.firmenname == "Neuer Name"
        db.commit.assert_called_once()


# ── Tests: list_bestellungen ──────────────────────────────────────────────────

class TestListBestellungen:
    def test_returns_empty(self):
        svc = _make_svc()
        result = svc.list_bestellungen()
        assert result == []

    def test_returns_mapped_bestellungen(self):
        db = _make_db()
        best = _make_bestellung()
        db.all.return_value = [best]
        svc = _make_svc(db)
        result = svc.list_bestellungen()
        assert len(result) == 1
        assert result[0]["bestellnummer"] == "EK-2600101"
        assert result[0]["netto_summe"] == 5000.0


# ── Tests: get_bestellung ─────────────────────────────────────────────────────

class TestGetBestellung:
    def test_raises_not_found(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError) as exc_info:
            svc.get_bestellung("missing")
        assert "EinkaufBestellung" in str(exc_info.value)

    def test_returns_bestellung(self):
        db = _make_db()
        best = _make_bestellung()
        db.first.return_value = best
        svc = _make_svc(db)
        result = svc.get_bestellung("best-001")
        assert result["bestellnummer"] == "EK-2600101"
        assert result["netto_summe"] == 5000.0


# ── Tests: freigebe_bestellung ────────────────────────────────────────────────

class TestFreegebeBestellung:
    def test_raises_not_found(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError):
            svc.freigebe_bestellung("missing")

    def test_raises_validation_for_wrong_status(self):
        db = _make_db()
        best = _make_bestellung(status="freigegeben")
        db.first.return_value = best
        svc = _make_svc(db)
        with pytest.raises(ValidationFailedError) as exc_info:
            svc.freigebe_bestellung("best-001")
        assert "freigegeben" in str(exc_info.value)

    def test_freigabe_sets_status(self):
        db = _make_db()
        best = _make_bestellung(status="entwurf", netto_summe=Decimal("0"))
        db.first.return_value = best
        svc = _make_svc(db)
        result = svc.freigebe_bestellung("best-001")
        assert best.status == "freigegeben"
        assert result["status"] == "freigegeben"
        db.commit.assert_called()


# ── Tests: storniere_bestellung ───────────────────────────────────────────────

class TestStorniereBestellung:
    def test_raises_not_found(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError):
            svc.storniere_bestellung("missing")

    def test_raises_for_abgeschlossen(self):
        db = _make_db()
        best = _make_bestellung(status="abgeschlossen")
        db.first.return_value = best
        svc = _make_svc(db)
        with pytest.raises(ValidationFailedError):
            svc.storniere_bestellung("best-001")

    def test_storniert_sets_status(self):
        db = _make_db()
        best = _make_bestellung(status="freigegeben")
        db.first.return_value = best
        svc = _make_svc(db)
        result = svc.storniere_bestellung("best-001")
        assert best.status == "storniert"
        assert result["status"] == "storniert"


# ── Tests: update_bestellung ──────────────────────────────────────────────────

class TestUpdateBestellung:
    def test_raises_not_found(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError):
            svc.update_bestellung("missing", {"status": "freigegeben"})

    def test_updates_allowed_fields(self):
        db = _make_db()
        best = _make_bestellung()
        db.first.return_value = best
        svc = _make_svc(db)
        result = svc.update_bestellung("best-001", {"status": "freigegeben", "notiz": "Dringend"})
        assert best.status == "freigegeben"
        assert best.notiz == "Dringend"
        db.commit.assert_called_once()


# ── Tests: list_vorschlaege ───────────────────────────────────────────────────

class TestListVorschlaege:
    def test_returns_empty(self):
        svc = _make_svc()
        result = svc.list_vorschlaege()
        assert result == []

    def test_mapped_result(self):
        db = _make_db()
        vs = _make_vorschlag()
        db.all.return_value = [vs]
        svc = _make_svc(db)
        result = svc.list_vorschlaege()
        assert len(result) == 1
        assert result[0]["vorschlag_typ"] == "lager"


# ── Tests: get_vorschlag ──────────────────────────────────────────────────────

class TestGetVorschlag:
    def test_raises_not_found(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError):
            svc.get_vorschlag("missing")

    def test_returns_full_vorschlag(self):
        db = _make_db()
        vs = _make_vorschlag()
        db.first.return_value = vs
        svc = _make_svc(db)
        result = svc.get_vorschlag("vs-001")
        assert result["vorschlag_typ"] == "lager"
        assert "positionen" in result


# ── Tests: delete_vorschlag ───────────────────────────────────────────────────

class TestDeleteVorschlag:
    def test_raises_not_found(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError):
            svc.delete_vorschlag("missing")

    def test_deletes_when_found(self):
        db = _make_db()
        vs = _make_vorschlag()
        db.first.return_value = vs
        svc = _make_svc(db)
        svc.delete_vorschlag("vs-001")
        db.delete.assert_called_once_with(vs)
        db.commit.assert_called_once()


# ── Tests: create_bestellung ──────────────────────────────────────────────────

class TestCreateBestellung:
    def test_creates_with_positionen(self):
        db = _make_db()
        new_best = _make_bestellung(id="best-new", bestellnummer="EK-260518120000")
        db.refresh.side_effect = lambda obj: None

        with patch("app.services.procurement_service.uuid7", return_value="best-new"), \
             patch("app.services.procurement_service.EinkaufBestellung", return_value=new_best), \
             patch("app.services.procurement_service.EinkaufBestellungPosition"):
            svc = _make_svc(db)
            result = svc.create_bestellung({
                "lieferant_id": "lf-001",
                "positionen": [
                    {"artikel_nr": "100", "artikel_bezeichnung": "Weizen", "menge": 10.0, "einheit": "t"},
                ],
            })
        assert result["bestellnummer"] == "EK-260518120000"
        db.flush.assert_called()
        db.commit.assert_called()


# ── Tests: list_kontrakte ─────────────────────────────────────────────────────

class TestListKontrakte:
    def test_returns_empty(self):
        svc = _make_svc()
        result = svc.list_kontrakte()
        assert result == []

    def test_filter_by_status(self):
        svc = _make_svc()
        svc.list_kontrakte(status="aktiv")
        svc.db.filter.assert_called()


# ── Tests: Artikel-Lager-Parameter ───────────────────────────────────────────

class TestArtikelLagerParameter:
    def test_list_returns_empty(self):
        svc = _make_svc()
        result = svc.list_artikel_lager_parameter()
        assert result == []

    def test_update_raises_not_found(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError):
            svc.update_artikel_lager_parameter("missing", {"mindestbestand": 10})

    def test_delete_raises_not_found(self):
        svc = _make_svc()
        svc.db.first.return_value = None
        with pytest.raises(EntityNotFoundError):
            svc.delete_artikel_lager_parameter("missing")


# ── Tests: Paletten-Konto ─────────────────────────────────────────────────────

class TestPalettenKonto:
    def test_saldo_no_buchungen(self):
        db = _make_db()
        db.all.return_value = []
        svc = _make_svc(db)
        result = svc.get_paletten_saldo("partner-001")
        assert result["saldo"] == 0
        assert result["buchungen_anz"] == 0

    def test_saldo_with_buchungen(self):
        db = _make_db()
        buchung = MagicMock()
        buchung.saldo_nachher = 42
        buchung.buchungsdatum = date(2026, 5, 1)
        db.all.return_value = [buchung]
        svc = _make_svc(db)
        result = svc.get_paletten_saldo("partner-001")
        assert result["saldo"] == 42
