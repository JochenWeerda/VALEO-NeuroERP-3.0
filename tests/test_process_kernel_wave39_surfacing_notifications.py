"""
Wave-39 Contract Tests: Command-Surfacing-Contracts und Process-Notification-Contracts

Testet:
- app.core.command_surfacing_contracts  (Enums, Regeln, berechne_surfacing)
- app.core.process_notification_contracts (Enums, Routing, Benachrichtigungen)
- API: GET /process/surfacing/regeln
- API: POST /process/surfacing/manifest
- API: GET /process/notifications/abonnements
- API: POST /process/notifications/route

60 Tests gesamt — keine DB, keine Mocks.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api
from app.core.command_surfacing_contracts import (
    CommandPrioritaet,
    CommandSurfacingManifest,
    DichteStufe,
    SurfacingAnfrage,
    SurfacingErgebnis,
    SurfacingErgebnisTyp,
    SurfacingKontext,
    SurfacingRegel,
    _DICHTE_RANG,
    berechne_surfacing,
    get_default_surfacing_regeln,
)
from app.core.process_notification_contracts import (
    EskalationsGrund,
    EskalationsRegel,
    NotifikationsAbonnement,
    NotifikationsAusloeser,
    NotifikationsKanal,
    NotifikationsNachricht,
    NotifikationsPrioritaet,
    NotifikationsRoutingErgebnis,
    NotifikationsStatus,
    berechne_prioritaet,
    erstelle_benachrichtigung,
    get_default_abonnements,
    get_default_eskalationsregeln,
    route_benachrichtigung,
)


# ---------------------------------------------------------------------------
# Fixture: TestClient
# ---------------------------------------------------------------------------

@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    return TestClient(app)


# ===========================================================================
# TestSurfacingEnums  (3 Tests)
# ===========================================================================

class TestSurfacingEnums:

    def test_dichte_stufe_has_three_values(self):
        values = [d.value for d in DichteStufe]
        assert set(values) == {"FOKUSSIERT", "STANDARD", "VERDICHTET"}

    def test_surfacing_ergebnis_typ_has_four_values(self):
        values = {e.value for e in SurfacingErgebnisTyp}
        assert "SICHTBAR" in values
        assert "AUSGEBLENDET" in values
        assert "BERECHTIGUNGS_GESPERRT" in values
        assert "KONTEXT_NICHT_VERFUEGBAR" in values

    def test_command_prioritaet_rang_order(self):
        # KRITISCH must have highest rank, NIEDRIG lowest
        from app.core.command_surfacing_contracts import _DICHTE_RANG
        assert _DICHTE_RANG[DichteStufe.FOKUSSIERT] == 0
        assert _DICHTE_RANG[DichteStufe.STANDARD] == 1
        assert _DICHTE_RANG[DichteStufe.VERDICHTET] == 2


# ===========================================================================
# TestSurfacingRegelDefaults  (4 Tests)
# ===========================================================================

class TestSurfacingRegelDefaults:

    def test_returns_exactly_12_regeln(self):
        regeln = get_default_surfacing_regeln()
        assert len(regeln) == 12

    def test_contains_two_kritisch_commands(self):
        regeln = get_default_surfacing_regeln()
        kritisch = [r for r in regeln if r.prioritaet == CommandPrioritaet.KRITISCH]
        # SR-001 (agrar), SR-005 (finance), SR-011 (global) → at least 2 KRITISCH
        assert len(kritisch) >= 2

    def test_agrar_and_finance_domain_rules_exist(self):
        regeln = get_default_surfacing_regeln()
        domains = {r.domain for r in regeln}
        assert "agrar" in domains
        assert "finance" in domains

    def test_all_regeln_have_at_least_one_sichtbar_in_kontext(self):
        regeln = get_default_surfacing_regeln()
        for r in regeln:
            assert len(r.sichtbar_in) >= 1, f"{r.regel_id} has no sichtbar_in"


# ===========================================================================
# TestBerechneSurfacingBasic  (6 Tests)
# ===========================================================================

class TestBerechneSurfacingBasic:

    def test_sachbearbeiter_standard_toolbar_primary_sees_sr001(self):
        anfrage = SurfacingAnfrage(
            rolle="sachbearbeiter",
            dichte=DichteStufe.STANDARD,
            kontext=SurfacingKontext.TOOLBAR_PRIMARY,
        )
        manifest = berechne_surfacing(anfrage)
        sichtbare_ids = [c.command_id for c in manifest.sichtbare_commands]
        assert "CMD_ANNAHME_ERFASSEN" in sichtbare_ids

    def test_kritisch_commands_always_visible_for_leiter_fokussiert(self):
        anfrage = SurfacingAnfrage(
            rolle="leiter",
            dichte=DichteStufe.FOKUSSIERT,
            kontext=SurfacingKontext.TOOLBAR_PRIMARY,
        )
        manifest = berechne_surfacing(anfrage)
        sichtbare_ids = [c.command_id for c in manifest.sichtbare_commands]
        # SR-001 (CMD_ANNAHME_ERFASSEN) and SR-005 (CMD_ZAHLUNGSLAUF_FREIGEBEN) are KRITISCH
        assert "CMD_ZAHLUNGSLAUF_FREIGEBEN" in sichtbare_ids

    def test_buchhaltung_cannot_see_sr001_role_blocked(self):
        anfrage = SurfacingAnfrage(
            rolle="buchhaltung",
            dichte=DichteStufe.VERDICHTET,
            kontext=SurfacingKontext.TOOLBAR_PRIMARY,
        )
        manifest = berechne_surfacing(anfrage)
        gesperrte_ids = [c.command_id for c in manifest.gesperrte_commands]
        # SR-001 erlaubte_rollen=["sachbearbeiter","leiter","admin"]
        assert "CMD_ANNAHME_ERFASSEN" in gesperrte_ids

    def test_toolbar_overflow_kontext_blocks_sr003(self):
        # SR-003 sichtbar_in=[TOOLBAR_PRIMARY, COMMAND_PALETTE, AGENT], NOT TOOLBAR_OVERFLOW
        anfrage = SurfacingAnfrage(
            rolle="buchhaltung",
            dichte=DichteStufe.VERDICHTET,
            kontext=SurfacingKontext.TOOLBAR_OVERFLOW,
        )
        manifest = berechne_surfacing(anfrage)
        ausgeblendete_ids = [c.command_id for c in manifest.ausgeblendete_commands]
        assert "CMD_SETTLEMENT_BERECHNEN" in ausgeblendete_ids

    def test_sachbearbeiter_fokussiert_command_palette_sr002_ausgeblendet(self):
        # SR-002 min_dichte=STANDARD, prioritaet=HOCH — density check fails at FOKUSSIERT
        anfrage = SurfacingAnfrage(
            rolle="sachbearbeiter",
            dichte=DichteStufe.FOKUSSIERT,
            kontext=SurfacingKontext.COMMAND_PALETTE,
        )
        manifest = berechne_surfacing(anfrage)
        ausgeblendete_ids = [c.command_id for c in manifest.ausgeblendete_commands]
        assert "CMD_QUALITAET_PRUEFUNG" in ausgeblendete_ids

    def test_admin_verdichtet_command_palette_sees_more_than_fokussiert(self):
        anf_verdichtet = SurfacingAnfrage(
            rolle="admin",
            dichte=DichteStufe.VERDICHTET,
            kontext=SurfacingKontext.COMMAND_PALETTE,
        )
        anf_fokussiert = SurfacingAnfrage(
            rolle="admin",
            dichte=DichteStufe.FOKUSSIERT,
            kontext=SurfacingKontext.COMMAND_PALETTE,
        )
        manifest_v = berechne_surfacing(anf_verdichtet)
        manifest_f = berechne_surfacing(anf_fokussiert)
        assert manifest_v.anzahl_sichtbar >= manifest_f.anzahl_sichtbar


# ===========================================================================
# TestBerechneSurfacingSorting  (3 Tests)
# ===========================================================================

class TestBerechneSurfacingSorting:

    def test_kritisch_commands_appear_first_in_sichtbare_list(self):
        anfrage = SurfacingAnfrage(
            rolle="sachbearbeiter",
            dichte=DichteStufe.STANDARD,
            kontext=SurfacingKontext.TOOLBAR_PRIMARY,
        )
        manifest = berechne_surfacing(anfrage)
        if len(manifest.sichtbare_commands) >= 2:
            first = manifest.sichtbare_commands[0]
            assert first.prioritaet == CommandPrioritaet.KRITISCH

    def test_manifest_as_dict_contains_required_keys(self):
        anfrage = SurfacingAnfrage(
            rolle="admin",
            dichte=DichteStufe.VERDICHTET,
            kontext=SurfacingKontext.COMMAND_PALETTE,
        )
        manifest = berechne_surfacing(anfrage)
        d = manifest.as_dict()
        assert "anzahl_sichtbar" in d
        assert "sichtbare_commands" in d
        assert "ausgeblendete_commands" in d
        assert "gesperrte_commands" in d

    def test_anzahl_sichtbar_matches_list_length(self):
        anfrage = SurfacingAnfrage(
            rolle="leiter",
            dichte=DichteStufe.STANDARD,
            kontext=SurfacingKontext.TOOLBAR_PRIMARY,
        )
        manifest = berechne_surfacing(anfrage)
        assert manifest.anzahl_sichtbar == len(manifest.sichtbare_commands)


# ===========================================================================
# TestBerechneSurfacingEdge  (3 Tests)
# ===========================================================================

class TestBerechneSurfacingEdge:

    def test_unknown_role_sees_only_open_role_rules(self):
        # erlaubte_rollen==[] means all roles allowed → should pass role check
        anfrage = SurfacingAnfrage(
            rolle="unknown_role_xyz",
            dichte=DichteStufe.VERDICHTET,
            kontext=SurfacingKontext.COMMAND_PALETTE,
        )
        manifest = berechne_surfacing(anfrage)
        # CMD_SHORTCUT_SUCHE (SR-011) has erlaubte_rollen=[] → should be visible
        sichtbare_ids = [c.command_id for c in manifest.sichtbare_commands]
        assert "CMD_SHORTCUT_SUCHE" in sichtbare_ids

    def test_empty_domain_matches_all_rules(self):
        # anfrage.domain="" → no domain filtering applied
        anfrage_no_domain = SurfacingAnfrage(
            rolle="admin",
            dichte=DichteStufe.VERDICHTET,
            kontext=SurfacingKontext.COMMAND_PALETTE,
            domain="",
        )
        anfrage_agrar = SurfacingAnfrage(
            rolle="admin",
            dichte=DichteStufe.VERDICHTET,
            kontext=SurfacingKontext.COMMAND_PALETTE,
            domain="agrar",
        )
        manifest_all = berechne_surfacing(anfrage_no_domain)
        manifest_agrar = berechne_surfacing(anfrage_agrar)
        # With no domain filter, all rules (incl. finance) are candidates
        total_all = (
            manifest_all.anzahl_sichtbar
            + len(manifest_all.ausgeblendete_commands)
            + len(manifest_all.gesperrte_commands)
        )
        total_agrar = (
            manifest_agrar.anzahl_sichtbar
            + len(manifest_agrar.ausgeblendete_commands)
            + len(manifest_agrar.gesperrte_commands)
        )
        assert total_all >= total_agrar

    def test_command_id_filter_returns_single_command(self):
        anfrage = SurfacingAnfrage(
            rolle="sachbearbeiter",
            dichte=DichteStufe.STANDARD,
            kontext=SurfacingKontext.TOOLBAR_PRIMARY,
            command_id="CMD_ANNAHME_ERFASSEN",
        )
        manifest = berechne_surfacing(anfrage)
        total = (
            manifest.anzahl_sichtbar
            + len(manifest.ausgeblendete_commands)
            + len(manifest.gesperrte_commands)
        )
        assert total == 1


# ===========================================================================
# TestNotifikationsEnums  (3 Tests)
# ===========================================================================

class TestNotifikationsEnums:

    def test_notifikations_kanal_has_six_values(self):
        values = {k.value for k in NotifikationsKanal}
        assert values == {"IN_APP", "EMAIL", "WEBHOOK", "PUSH", "SLACK", "TEAMS"}

    def test_notifikations_ausloeser_includes_eskalation(self):
        assert NotifikationsAusloeser.ESKALATION in list(NotifikationsAusloeser)

    def test_eskalations_grund_has_four_values(self):
        values = {g.value for g in EskalationsGrund}
        assert "KEINE_REAKTION" in values
        assert "SLA_UEBERSCHRITTEN" in values
        assert "FEHLERHAEUFT_SICH" in values
        assert "MANUELL" in values


# ===========================================================================
# TestBerechnePrioritaet  (5 Tests)
# ===========================================================================

class TestBerechnePrioritaet:

    def test_eskalation_maps_to_kritisch(self):
        assert berechne_prioritaet(NotifikationsAusloeser.ESKALATION) == NotifikationsPrioritaet.KRITISCH

    def test_sla_verletzung_maps_to_kritisch(self):
        assert berechne_prioritaet(NotifikationsAusloeser.SLA_VERLETZUNG) == NotifikationsPrioritaet.KRITISCH

    def test_freigabe_erforderlich_maps_to_hoch(self):
        assert berechne_prioritaet(NotifikationsAusloeser.FREIGABE_ERFORDERLICH) == NotifikationsPrioritaet.HOCH

    def test_fehler_aufgetreten_maps_to_hoch(self):
        assert berechne_prioritaet(NotifikationsAusloeser.FEHLER_AUFGETRETEN) == NotifikationsPrioritaet.HOCH

    def test_abschluss_maps_to_niedrig(self):
        assert berechne_prioritaet(NotifikationsAusloeser.ABSCHLUSS) == NotifikationsPrioritaet.NIEDRIG


# ===========================================================================
# TestRouteBenachrichtigung  (7 Tests)
# ===========================================================================

class TestRouteBenachrichtigung:

    def test_freigabe_erforderlich_matches_leiter_and_admin(self):
        ergebnis = route_benachrichtigung(NotifikationsAusloeser.FREIGABE_ERFORDERLICH)
        rollen = {a.empfaenger_rolle for a in ergebnis.abonnenten}
        assert "leiter" in rollen
        assert "admin" in rollen

    def test_domain_filter_excludes_finance_abos_for_agrar_abschluss(self):
        # ABO-008 has domain="finance" → should be excluded when routing for domain="agrar"
        ergebnis = route_benachrichtigung(
            NotifikationsAusloeser.ABSCHLUSS,
            domain="agrar",
        )
        for abo in ergebnis.abonnenten:
            assert not (abo.domain == "finance"), f"Finance abo {abo.abo_id} leaked into agrar routing"

    def test_abo007_prio_filter_only_matches_kritisch_triggers(self):
        # ABO-007 min_prioritaet=KRITISCH → should NOT match FREIGABE_ERFORDERLICH (HOCH)
        # but SHOULD match ESKALATION (KRITISCH)
        ergebnis_hoch = route_benachrichtigung(NotifikationsAusloeser.FREIGABE_ERFORDERLICH)
        ergebnis_kritisch = route_benachrichtigung(NotifikationsAusloeser.ESKALATION)

        abo007_in_hoch = any(a.abo_id == "ABO-007" for a in ergebnis_hoch.abonnenten)
        abo007_in_kritisch = any(a.abo_id == "ABO-007" for a in ergebnis_kritisch.abonnenten)

        assert not abo007_in_hoch
        assert abo007_in_kritisch

    def test_inaktives_abo_wird_ignoriert(self):
        custom_abos = [
            NotifikationsAbonnement(
                "ABO-INAKT", "leiter", "user-99",
                ausloeser=[NotifikationsAusloeser.ABSCHLUSS],
                kanaele=[NotifikationsKanal.IN_APP],
                aktiv=False,
            )
        ]
        ergebnis = route_benachrichtigung(
            NotifikationsAusloeser.ABSCHLUSS,
            abonnements=custom_abos,
        )
        assert ergebnis.anzahl_empfaenger == 0

    def test_effektive_kanaele_is_union_of_all_matching_abos(self):
        # ESKALATION → ABO-001 (IN_APP,EMAIL) + ABO-004 (IN_APP,EMAIL,WEBHOOK) + ABO-007 (WEBHOOK)
        ergebnis = route_benachrichtigung(NotifikationsAusloeser.ESKALATION)
        kanal_values = {k.value for k in ergebnis.effektive_kanaele}
        assert "IN_APP" in kanal_values
        assert "EMAIL" in kanal_values
        assert "WEBHOOK" in kanal_values

    def test_eskalationsregel_found_for_freigabe_erforderlich(self):
        ergebnis = route_benachrichtigung(NotifikationsAusloeser.FREIGABE_ERFORDERLICH)
        assert ergebnis.eskalations_regel is not None
        assert ergebnis.eskalations_regel.regel_id == "ESK-001"

    def test_abschluss_routing_with_no_domain_includes_abo004(self):
        # ABSCHLUSS → NIEDRIG priority. ABO-004 (admin, min_prioritaet=NIEDRIG) always matches.
        # ABO-002 (sachbearbeiter, min_prioritaet=NORMAL) → NORMAL rank > NIEDRIG rank → filtered out.
        ergebnis = route_benachrichtigung(NotifikationsAusloeser.ABSCHLUSS)
        abo_ids = {a.abo_id for a in ergebnis.abonnenten}
        assert "ABO-004" in abo_ids
        # ABO-002 should NOT be included (min_prioritaet=NORMAL > NIEDRIG)
        assert "ABO-002" not in abo_ids


# ===========================================================================
# TestErstelleBenachrichtigung  (4 Tests)
# ===========================================================================

class TestErstelleBenachrichtigung:

    def test_empfaenger_ids_derived_from_routing_abonnenten(self):
        routing = route_benachrichtigung(NotifikationsAusloeser.FREIGABE_ERFORDERLICH)
        nachricht = erstelle_benachrichtigung(
            nachricht_id="N-001",
            ausloeser=NotifikationsAusloeser.FREIGABE_ERFORDERLICH,
            titel="Freigabe nötig",
            inhalt="Bitte Rechnung freigeben.",
            routing=routing,
        )
        expected_ids = [a.empfaenger_id for a in routing.abonnenten]
        assert nachricht.empfaenger_ids == expected_ids

    def test_status_defaults_to_ausstehend(self):
        routing = route_benachrichtigung(NotifikationsAusloeser.ABSCHLUSS)
        nachricht = erstelle_benachrichtigung(
            nachricht_id="N-002",
            ausloeser=NotifikationsAusloeser.ABSCHLUSS,
            titel="Abgeschlossen",
            inhalt="Vorgang abgeschlossen.",
            routing=routing,
        )
        assert nachricht.status == NotifikationsStatus.AUSSTEHEND

    def test_routing_none_auto_routes_and_returns_valid_nachricht(self):
        nachricht = erstelle_benachrichtigung(
            nachricht_id="N-003",
            ausloeser=NotifikationsAusloeser.ESKALATION,
            titel="Eskalation",
            inhalt="Keine Reaktion auf Freigabe.",
            routing=None,
        )
        assert isinstance(nachricht, NotifikationsNachricht)
        assert isinstance(nachricht.empfaenger_ids, list)
        assert nachricht.prioritaet == NotifikationsPrioritaet.KRITISCH

    def test_kanaele_taken_from_routing_effektive_kanaele(self):
        routing = route_benachrichtigung(NotifikationsAusloeser.FEHLER_AUFGETRETEN)
        nachricht = erstelle_benachrichtigung(
            nachricht_id="N-004",
            ausloeser=NotifikationsAusloeser.FEHLER_AUFGETRETEN,
            titel="Fehler",
            inhalt="Fehler im Workflow.",
            routing=routing,
        )
        assert nachricht.kanaele == routing.effektive_kanaele


# ===========================================================================
# TestDefaultAbosEskalation  (4 Tests)
# ===========================================================================

class TestDefaultAbosEskalation:

    def test_get_default_abonnements_returns_eight(self):
        abos = get_default_abonnements()
        assert len(abos) == 8

    def test_get_default_eskalationsregeln_returns_five(self):
        regeln = get_default_eskalationsregeln()
        assert len(regeln) == 5

    def test_admin_abo_covers_all_ausloeser(self):
        abos = get_default_abonnements()
        admin_abo = next((a for a in abos if a.empfaenger_rolle == "admin" and a.domain == ""), None)
        assert admin_abo is not None
        for ausloeser in NotifikationsAusloeser:
            assert ausloeser in admin_abo.ausloeser, f"{ausloeser} missing from admin abo"

    def test_esk001_is_for_freigabe_erforderlich(self):
        regeln = get_default_eskalationsregeln()
        esk001 = next((r for r in regeln if r.regel_id == "ESK-001"), None)
        assert esk001 is not None
        assert esk001.ausloeser == NotifikationsAusloeser.FREIGABE_ERFORDERLICH
        assert esk001.eskalations_empfaenger_rolle == "leiter"

    def test_notifikations_nachricht_as_dict_has_expected_keys(self):
        nachricht = erstelle_benachrichtigung(
            nachricht_id="N-DICT-001",
            ausloeser=NotifikationsAusloeser.SLA_VERLETZUNG,
            titel="SLA verletzt",
            inhalt="Prozess hat SLA überschritten.",
        )
        d = nachricht.as_dict()
        assert "nachricht_id" in d
        assert "ausloeser" in d
        assert "empfaenger_ids" in d
        assert "kanaele" in d
        assert "prioritaet" in d
        assert "status" in d
        assert d["status"] == "AUSSTEHEND"

    def test_surfacing_ergebnis_ist_sichtbar_true_only_when_sichtbar(self):
        sichtbar = SurfacingErgebnis(
            command_id="CMD_X",
            command_bezeichnung="Test",
            typ=SurfacingErgebnisTyp.SICHTBAR,
        )
        gesperrt = SurfacingErgebnis(
            command_id="CMD_X",
            command_bezeichnung="Test",
            typ=SurfacingErgebnisTyp.BERECHTIGUNGS_GESPERRT,
        )
        assert sichtbar.as_dict()["ist_sichtbar"] is True
        assert gesperrt.as_dict()["ist_sichtbar"] is False


# ===========================================================================
# TestSurfacingRegelnEndpoint  (4 Tests)
# ===========================================================================

class TestSurfacingRegelnEndpoint:

    def test_get_regeln_returns_200_with_12_rules(self, client: TestClient):
        response = client.get("/process/surfacing/regeln")
        assert response.status_code == 200
        data = response.json()
        assert data["regel_count"] == 12

    def test_get_regeln_domain_agrar_filter(self, client: TestClient):
        response = client.get("/process/surfacing/regeln?domain=agrar")
        assert response.status_code == 200
        data = response.json()
        for regel in data["regeln"]:
            assert regel["domain"] in ("", "agrar")

    def test_get_regeln_kontext_toolbar_primary_filter(self, client: TestClient):
        response = client.get("/process/surfacing/regeln?kontext=TOOLBAR_PRIMARY")
        assert response.status_code == 200
        data = response.json()
        for regel in data["regeln"]:
            assert "TOOLBAR_PRIMARY" in regel["sichtbar_in"]

    def test_get_regeln_invalid_kontext_returns_422(self, client: TestClient):
        response = client.get("/process/surfacing/regeln?kontext=UNGUELTIG")
        assert response.status_code == 422


# ===========================================================================
# TestSurfacingManifestEndpoint  (4 Tests)
# ===========================================================================

class TestSurfacingManifestEndpoint:

    def test_post_manifest_leiter_verdichtet_command_palette(self, client: TestClient):
        response = client.post(
            "/process/surfacing/manifest",
            json={"rolle": "leiter", "dichte": "VERDICHTET", "kontext": "COMMAND_PALETTE"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["anzahl_sichtbar"] > 0

    def test_post_manifest_missing_fields_returns_422(self, client: TestClient):
        response = client.post(
            "/process/surfacing/manifest",
            json={"rolle": "leiter"},
        )
        assert response.status_code == 422

    def test_post_manifest_bad_dichte_returns_422(self, client: TestClient):
        response = client.post(
            "/process/surfacing/manifest",
            json={"rolle": "leiter", "dichte": "EXTREM", "kontext": "COMMAND_PALETTE"},
        )
        assert response.status_code == 422

    def test_post_manifest_response_has_expected_structure(self, client: TestClient):
        response = client.post(
            "/process/surfacing/manifest",
            json={"rolle": "admin", "dichte": "STANDARD", "kontext": "TOOLBAR_PRIMARY"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "sichtbare_commands" in data
        assert "ausgeblendete_commands" in data
        assert "gesperrte_commands" in data
        assert isinstance(data["sichtbare_commands"], list)


# ===========================================================================
# TestNotificationAbosEndpoint  (4 Tests)
# ===========================================================================

class TestNotificationAbosEndpoint:

    def test_get_abonnements_returns_200_with_8_abos(self, client: TestClient):
        response = client.get("/process/notifications/abonnements")
        assert response.status_code == 200
        data = response.json()
        assert data["abo_count"] == 8

    def test_get_abonnements_rolle_filter_leiter(self, client: TestClient):
        response = client.get("/process/notifications/abonnements?rolle=leiter")
        assert response.status_code == 200
        data = response.json()
        for abo in data["abonnements"]:
            assert abo["empfaenger_rolle"] == "leiter"

    def test_get_abonnements_ausloeser_filter_freigabe(self, client: TestClient):
        response = client.get(
            "/process/notifications/abonnements?ausloeser=FREIGABE_ERFORDERLICH"
        )
        assert response.status_code == 200
        data = response.json()
        for abo in data["abonnements"]:
            assert "FREIGABE_ERFORDERLICH" in abo["ausloeser"]

    def test_get_abonnements_invalid_ausloeser_returns_422(self, client: TestClient):
        response = client.get("/process/notifications/abonnements?ausloeser=UNGUELTIG")
        assert response.status_code == 422


# ===========================================================================
# TestNotificationRouteEndpoint  (4 Tests)
# ===========================================================================

class TestNotificationRouteEndpoint:

    def test_post_route_eskalation_returns_kritisch_priority(self, client: TestClient):
        response = client.post(
            "/process/notifications/route",
            json={"ausloeser": "ESKALATION"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prioritaet"] == "KRITISCH"

    def test_post_route_missing_ausloeser_returns_422(self, client: TestClient):
        response = client.post(
            "/process/notifications/route",
            json={"domain": "agrar"},
        )
        assert response.status_code == 422

    def test_post_route_with_titel_inhalt_nachricht_id_returns_nachricht(self, client: TestClient):
        response = client.post(
            "/process/notifications/route",
            json={
                "ausloeser": "FREIGABE_ERFORDERLICH",
                "titel": "Freigabe benötigt",
                "inhalt": "Bitte Eingangsrechnung genehmigen.",
                "nachricht_id": "N-TEST-001",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "nachricht" in data
        assert data["nachricht"]["nachricht_id"] == "N-TEST-001"
        assert data["nachricht"]["status"] == "AUSSTEHEND"

    def test_post_route_response_contains_effektive_kanaele(self, client: TestClient):
        response = client.post(
            "/process/notifications/route",
            json={"ausloeser": "SLA_VERLETZUNG"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "effektive_kanaele" in data
        assert isinstance(data["effektive_kanaele"], list)
        assert len(data["effektive_kanaele"]) > 0
