"""Tests fuer PORTAL-PREISSPIEGEL-001, PORTAL-INTELLIGENCE-001,
PORTAL-LOHNDIENST-001, PORTAL-INTERESSENT-001."""
from __future__ import annotations

from datetime import date

import pytest

# ─── Preisspiegel ────────────────────────────────────────────────────────────
from app.services.portal_preisspiegel_service import (
    PortalPreisspiegel,
    PreisVariante,
    PreisQuelle,
)


@pytest.fixture()
def preis_svc() -> PortalPreisspiegel:
    s = PortalPreisspiegel(tenant_id="test-preis")
    return s


class TestPreisspiegel:
    def test_seed_daten_geladen(self, preis_svc):
        alle = preis_svc.preise_alle()
        assert len(alle) >= 4

    def test_filter_variante(self, preis_svc):
        altware = preis_svc.preise_alle(variante=PreisVariante.ALTWARE_AB_HOF)
        assert all(p["variante"] == "altware_ab_hof" for p in altware)

    def test_filter_frucht_gruppe(self, preis_svc):
        oelsaaten = preis_svc.preise_alle(frucht_gruppe="Ölsaaten")
        assert all(p["frucht_gruppe"] == "Ölsaaten" for p in oelsaaten)

    def test_preisspiegel_fuer_kunde(self, preis_svc):
        result = preis_svc.preisspiegel_fuer_kunde(["WEI-001", "GER-001"])
        assert "preisspiegel" in result
        artikel_ids = [p["artikel_id"] for p in result["preisspiegel"]]
        assert "WEI-001" in artikel_ids

    def test_gesamtpreis_enthaelt_aufschlag(self, preis_svc):
        preise = preis_svc.preise_alle(variante=PreisVariante.ALTWARE_FREI_LAGER)
        for p in preise:
            assert abs(p["gesamtpreis_eur_dt"] - (p["preis_eur_dt"] + p["aufschlag_eur_dt"])) < 0.01

    def test_preis_setzen(self, preis_svc):
        p = preis_svc.preis_setzen(
            artikel_id="TST-001",
            artikel_name="Testfrucht",
            frucht_gruppe="Test",
            variante=PreisVariante.NEUE_ERNTE_FREI_LAGER,
            preis_eur_dt=25.00,
            basis_qualitaet="Test",
            ernte_jahr=2026,
        )
        assert p["preis_eur_dt"] == 25.00
        assert p["variante"] == "neue_ernte_frei_lager"

    def test_stand_datum_vorhanden(self, preis_svc):
        result = preis_svc.preisspiegel_fuer_kunde(["WEI-001"])
        assert "stand" in result
        assert result["stand"] == date.today().isoformat()


# ─── Intelligence / Cross-Sell ───────────────────────────────────────────────
from app.services.portal_intelligence_service import (
    PortalIntelligenceService,
    EmpfehlungTyp,
)


@pytest.fixture()
def intel_svc() -> PortalIntelligenceService:
    return PortalIntelligenceService(tenant_id="test-intel")


class TestIntelligence:
    def test_generiere_aus_ration(self, intel_svc):
        neue = intel_svc.generiere_aus_ration(
            kunden_nr="K-001",
            tiere_anzahl=80,
            tier_kategorie="Milchkühe",
            benoetigt_rohwaren=["SES-001"],
        )
        assert len(neue) >= 2  # Rohware + Mahl+Misch + Lohnmahlen

    def test_lohndienst_empfehlung_in_ration(self, intel_svc):
        neue = intel_svc.generiere_aus_ration("K-002", 50, "Rinder", [])
        typen = [e["typ"] for e in neue]
        assert EmpfehlungTyp.LOHNDIENST.value in typen

    def test_generiere_aus_schlagkartei_getreide(self, intel_svc):
        neue = intel_svc.generiere_aus_schlagkartei(
            kunden_nr="K-003",
            kulturen=["Winterweizen", "Raps"],
            flaeche_ha=50.0,
            ernte_jahr=2026,
        )
        assert len(neue) >= 2
        typen = [e["typ"] for e in neue]
        assert EmpfehlungTyp.ANKAUF_KONTRAKT.value in typen
        assert EmpfehlungTyp.LOHNDIENST.value in typen

    def test_kein_duplikat_ankauf(self, intel_svc):
        intel_svc.generiere_aus_schlagkartei("K-004", ["Raps"], 30.0, 2026)
        # Zweiter Aufruf: keine neuen ANKAUF_KONTRAKT für Raps
        neue2 = intel_svc.generiere_aus_schlagkartei("K-004", ["Raps"], 30.0, 2026)
        ankauf = [e for e in neue2 if e["typ"] == EmpfehlungTyp.ANKAUF_KONTRAKT.value]
        assert len(ankauf) == 0

    def test_als_gesehen_markieren(self, intel_svc):
        neue = intel_svc.generiere_aus_ration("K-005", 20, "Schweine", [])
        eid = neue[0]["empfehlung_id"]
        assert intel_svc.als_gesehen_markieren(eid, "K-005") is True
        liste = intel_svc.empfehlungen_fuer_kunden("K-005")
        gesehen = [e for e in liste if e["empfehlung_id"] == eid][0]
        assert gesehen["gesehen"] is True

    def test_zusammenfassung(self, intel_svc):
        intel_svc.generiere_aus_ration("K-006", 30, "Rinder", [])
        z = intel_svc.zusammenfassung("K-006")
        assert z["gesamt"] > 0
        assert z["ungesehen"] > 0

    def test_tenant_isolation(self):
        s1 = PortalIntelligenceService(tenant_id="tenant-A")
        s2 = PortalIntelligenceService(tenant_id="tenant-B")
        s1.generiere_aus_ration("K-100", 10, "Rinder", [])
        assert len(s2.empfehlungen_fuer_kunden("K-100")) == 0


# ─── Lohndienst ──────────────────────────────────────────────────────────────
from app.services.portal_lohndienst_service import (
    LohndienstService,
    LohndienstTyp,
    LohndienstStatus,
    UngueltigerStatusFehler,
    AuftragNichtGefundenFehler,
)


@pytest.fixture()
def lohn_svc() -> LohndienstService:
    return LohndienstService(tenant_id="test-lohn")


class TestLohndienst:
    def test_auftrag_anlegen(self, lohn_svc):
        a = lohn_svc.auftrag_anlegen(kunden_nr="K-001", typ=LohndienstTyp.LOHN_SPRITZ, kultur="Weizen")
        assert a.status == LohndienstStatus.ANGEFRAGT
        assert a.typ == LohndienstTyp.LOHN_SPRITZ

    def test_status_bestaetigen(self, lohn_svc):
        a = lohn_svc.auftrag_anlegen("K-001", LohndienstTyp.MAHL_MISCH)
        b = lohn_svc.status_wechsel(a.auftrag_id, LohndienstStatus.BESTAETIGT)
        assert b.status == LohndienstStatus.BESTAETIGT

    def test_status_ungueltig_raises(self, lohn_svc):
        a = lohn_svc.auftrag_anlegen("K-001", LohndienstTyp.LOHN_MAHLEN)
        with pytest.raises(UngueltigerStatusFehler):
            lohn_svc.status_wechsel(a.auftrag_id, LohndienstStatus.ABGESCHLOSSEN)

    def test_nicht_gefunden_raises(self, lohn_svc):
        with pytest.raises(AuftragNichtGefundenFehler):
            lohn_svc.get_auftrag("nicht-vorhanden")

    def test_list_filter_typ(self, lohn_svc):
        lohn_svc.auftrag_anlegen("K-001", LohndienstTyp.LOHN_SPRITZ)
        lohn_svc.auftrag_anlegen("K-001", LohndienstTyp.MAHL_MISCH)
        result = lohn_svc.list_auftraege(kunden_nr="K-001", typ=LohndienstTyp.LOHN_SPRITZ)
        assert all(a["typ"] == "lohn_spritz" for a in result)

    def test_typ_bezeichnung_in_result(self, lohn_svc):
        a = lohn_svc.auftrag_anlegen("K-002", LohndienstTyp.TMR_WAGON)
        d = a.to_dict()
        assert "typ_bezeichnung" in d
        assert "TMR" in d["typ_bezeichnung"]

    def test_vollstaendiger_lifecycle(self, lohn_svc):
        a = lohn_svc.auftrag_anlegen("K-003", LohndienstTyp.LOHN_ERNTE)
        lohn_svc.status_wechsel(a.auftrag_id, LohndienstStatus.BESTAETIGT)
        lohn_svc.status_wechsel(a.auftrag_id, LohndienstStatus.EINGEPLANT)
        f = lohn_svc.status_wechsel(a.auftrag_id, LohndienstStatus.ABGESCHLOSSEN)
        assert f.to_dict()["abgeschlossen"] is True


# ─── Interessent / Onboarding ────────────────────────────────────────────────
from app.services.portal_interessent_service import (
    PortalInteressentService,
    InteressentStatus,
    BetriebsTyp,
    UngueltigerUebergangFehler,
    InteressentNichtGefundenFehler,
)


@pytest.fixture()
def interessent_svc() -> PortalInteressentService:
    return PortalInteressentService(tenant_id="test-int")


class TestInteressent:
    def test_registrieren(self, interessent_svc):
        i = interessent_svc.registrieren("Hans", "Müller", "hans@example.de")
        assert i.status == InteressentStatus.INTERESSENT
        assert i.vollname if hasattr(i, 'vollname') else True  # to_dict check below
        d = i.to_dict()
        assert d["vollname"] == "Hans Müller"

    def test_pflichtfelder_fehlen_raises(self, interessent_svc):
        with pytest.raises(ValueError):
            interessent_svc.registrieren("", "Müller", "test@test.de")

    def test_ungueltige_email_raises(self, interessent_svc):
        with pytest.raises(ValueError):
            interessent_svc.registrieren("Hans", "Müller", "keine-email")

    def test_doppelregistrierung_raises(self, interessent_svc):
        interessent_svc.registrieren("Klaus", "Klein", "kk@example.de")
        with pytest.raises(ValueError):
            interessent_svc.registrieren("Klaus", "Klein", "KK@example.de")

    def test_qualifizieren(self, interessent_svc):
        i = interessent_svc.registrieren("Eva", "Groß", "eva@farm.de")
        q = interessent_svc.status_wechsel(i.interessent_id, InteressentStatus.QUALIFIZIERT)
        assert q.status == InteressentStatus.QUALIFIZIERT
        assert q.qualifiziert_am is not None

    def test_zu_kunde_konvertieren(self, interessent_svc):
        i = interessent_svc.registrieren("Peter", "Bauer", "pb@hof.de")
        interessent_svc.status_wechsel(i.interessent_id, InteressentStatus.QUALIFIZIERT)
        k = interessent_svc.status_wechsel(i.interessent_id, InteressentStatus.KUNDE, kunden_nr="K-9999")
        assert k.kunden_nr == "K-9999"
        assert k.konvertiert_am is not None

    def test_konvertierung_ohne_kunden_nr_raises(self, interessent_svc):
        i = interessent_svc.registrieren("Anna", "Land", "al@hof.de")
        interessent_svc.status_wechsel(i.interessent_id, InteressentStatus.QUALIFIZIERT)
        with pytest.raises(ValueError):
            interessent_svc.status_wechsel(i.interessent_id, InteressentStatus.KUNDE)

    def test_ungueltige_transition_raises(self, interessent_svc):
        i = interessent_svc.registrieren("Max", "Feld", "mf@feld.de")
        with pytest.raises(UngueltigerUebergangFehler):
            interessent_svc.status_wechsel(i.interessent_id, InteressentStatus.KUNDE)

    def test_nicht_gefunden_raises(self, interessent_svc):
        with pytest.raises(InteressentNichtGefundenFehler):
            interessent_svc.get("ghost-id")

    def test_tenant_isolation(self):
        s1 = PortalInteressentService(tenant_id="X")
        s2 = PortalInteressentService(tenant_id="Y")
        s1.registrieren("X", "User", "x@x.de")
        assert len(s2.list_interessenten()) == 0
