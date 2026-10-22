"""Batch 13 Stamm-ObjectPage ScreenDefinitions (MASK-STUDIO-ROLLOUT)."""
from __future__ import annotations

from typing import Any

from app.core.stamm_object_page_parent import (
    build_stamm_object_page,
    stamm_entity_source,
    stamm_kopf_tab,
)


def _batch13_stamm(
    screen_id: str,
    *,
    domain: str,
    title: str,
    entity_endpoint: str,
    identity_field: str,
    edit_permission: str,
    bearbeiten_endpoint: str | None = None,
) -> dict[str, Any]:
    kopf = [
        {"key": identity_field, "label": "Kennung", "type": "text"},
        {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"},
        {"key": "status", "label": "Status", "type": "text", "readOnly": True},
    ]
    overrides: dict[str, Any] | None = None
    if bearbeiten_endpoint:
        overrides = {
            "commandEndpoint": bearbeiten_endpoint,
            "method": "POST",
            "inputFields": [
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"},
            ],
        }
    return build_stamm_object_page(
        screen_id=screen_id,
        domain=domain,
        title=title,
        subtitle=screen_id,
        identity_field=identity_field,
        data_sources=[stamm_entity_source(entity_endpoint)],
        tabs=[stamm_kopf_tab(kopf)],
        edit_permission=edit_permission,
        edit_action_key="bearbeiten",
        edit_action_overrides=overrides,
        no_workflow_reason="Verwaltungsobjekt ohne separaten Prozess-Lebenszyklus in der Maske.",
        business_purpose=f"Stamm- und Fachmaske fuer {title} ({screen_id}).",
        example_prompts=[f"Zeige Stammdaten fuer {title} {{entity_id}}."],
        test_id=screen_id.replace("/", "-"),
        density="compact",
        context_rail="combined",
        table_profile="standard",
    )


def build_admin_agenten_integration() -> dict[str, Any]:
    return _batch13_stamm("admin/agenten-integration", domain="admin", title="Agenten integration",
        entity_endpoint="/api/v1/agent/integrations/providers/superglue/tenants/{entity_id}/admin-state", identity_field="bezeichnung",
        edit_permission="admin.agenten-integration.update", bearbeiten_endpoint=None)

def build_admin_ai_approvals() -> dict[str, Any]:
    return _batch13_stamm("admin/ai-approvals", domain="admin", title="Ai approvals",
        entity_endpoint="/api/v1/finance/ap/approval-workflow/status/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.ai-approvals.update", bearbeiten_endpoint=None)

def build_admin_api_keys() -> dict[str, Any]:
    return _batch13_stamm("admin/api-keys", domain="admin", title="Api keys",
        entity_endpoint="/api/v1/admin/benutzer/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.api-keys.update", bearbeiten_endpoint=None)

def build_admin_backup_restore() -> dict[str, Any]:
    return _batch13_stamm("admin/backup-restore", domain="admin", title="Backup restore",
        entity_endpoint="/api/v1/admin/benutzer/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.backup-restore.update", bearbeiten_endpoint=None)

def build_admin_berechtigungen_matrix() -> dict[str, Any]:
    return _batch13_stamm("admin/berechtigungen-matrix", domain="admin", title="Berechtigungen matrix",
        entity_endpoint="/api/v1/admin/report-permissions/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.berechtigungen-matrix.update", bearbeiten_endpoint=None)

def build_admin_branches() -> dict[str, Any]:
    return _batch13_stamm("admin/branches", domain="admin", title="Branches",
        entity_endpoint="/api/v1/admin/branches/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.branches.update", bearbeiten_endpoint=None)

def build_admin_command_monitor() -> dict[str, Any]:
    return _batch13_stamm("admin/command-monitor", domain="admin", title="Command monitor",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.command-monitor.update", bearbeiten_endpoint=None)

def build_admin_system_einstellungen() -> dict[str, Any]:
    return _batch13_stamm("admin/system-einstellungen", domain="admin", title="System einstellungen",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.system-einstellungen.update", bearbeiten_endpoint=None)

def build_admin_tankstelle_evb() -> dict[str, Any]:
    return _batch13_stamm("admin/tankstelle-evb", domain="admin", title="Tankstelle evb",
        entity_endpoint="/api/v1/tankstelle/zapfungen/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.tankstelle-evb.update", bearbeiten_endpoint=None)

def build_admin_tenants() -> dict[str, Any]:
    return _batch13_stamm("admin/tenants", domain="admin", title="Tenants",
        entity_endpoint="/api/v1/tenants/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.tenants.update", bearbeiten_endpoint=None)

def build_admin_users() -> dict[str, Any]:
    return _batch13_stamm("admin/users", domain="admin", title="Users",
        entity_endpoint="/api/v1/admin/benutzer/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.users.update", bearbeiten_endpoint=None)

def build_admin_workflow_editor() -> dict[str, Any]:
    return _batch13_stamm("admin/workflow-editor", domain="admin", title="Workflow editor",
        entity_endpoint="/api/v1/workflow/runtime/instances/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.workflow-editor.update", bearbeiten_endpoint=None)

def build_admin_zeitachsen_editor() -> dict[str, Any]:
    return _batch13_stamm("admin/zeitachsen-editor", domain="admin", title="Zeitachsen editor",
        entity_endpoint="/api/v1/workflow/cockpit/processes/{entity_id}", identity_field="bezeichnung",
        edit_permission="admin.zeitachsen-editor.update", bearbeiten_endpoint=None)

def build_agrar_annahme_abrechnung() -> dict[str, Any]:
    return _batch13_stamm("agrar/annahme-abrechnung", domain="agrar", title="Annahme abrechnung",
        entity_endpoint="/api/v1/agrar/self-billing/harvest-acceptance/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.annahme-abrechnung.update", bearbeiten_endpoint=None)

def build_agrar_ernte_annahme_abrechnung() -> dict[str, Any]:
    return _batch13_stamm("agrar/ernte-annahme-abrechnung", domain="agrar", title="Ernte annahme abrechnung",
        entity_endpoint="/api/v1/agrar/harvest-acceptance/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.ernte-annahme-abrechnung.update", bearbeiten_endpoint=None)

def build_agrar_kontrakte_formular() -> dict[str, Any]:
    return _batch13_stamm("agrar/kontrakte/formular", domain="agrar", title="Formular",
        entity_endpoint="/api/v1/kontrakte/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.kontrakte.formular.update", bearbeiten_endpoint='/api/v1/kontrakte/{entity_id}/actions/bearbeiten')

def build_agrar_lieferschein_erstellen() -> dict[str, Any]:
    return _batch13_stamm("agrar/lieferschein-erstellen", domain="agrar", title="Lieferschein erstellen",
        entity_endpoint="/api/v1/einkauf/lieferscheine/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.lieferschein-erstellen.update", bearbeiten_endpoint=None)

def build_agrar_maschinen_formular() -> dict[str, Any]:
    return _batch13_stamm("agrar/maschinen/formular", domain="agrar", title="Formular",
        entity_endpoint="/api/v1/agrar/maschinen/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.maschinen.formular.update", bearbeiten_endpoint=None)

def build_agrar_partie_historie() -> dict[str, Any]:
    return _batch13_stamm("agrar/partie-historie", domain="agrar", title="Partie historie",
        entity_endpoint="/api/v1/saatzucht/partien/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.partie-historie.update", bearbeiten_endpoint=None)

def build_agrar_pflanzenschutz_rechner() -> dict[str, Any]:
    return _batch13_stamm("agrar/pflanzenschutz-rechner", domain="agrar", title="Pflanzenschutz rechner",
        entity_endpoint="/api/v1/agrar/schlaege/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.pflanzenschutz-rechner.update", bearbeiten_endpoint=None)

def build_agrar_probenehmer_stamm() -> dict[str, Any]:
    return _batch13_stamm("agrar/probenehmer-stamm", domain="agrar", title="Probenehmer stamm",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.probenehmer-stamm.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_agrar_rechnungen_erstellen() -> dict[str, Any]:
    return _batch13_stamm("agrar/rechnungen-erstellen", domain="agrar", title="Rechnungen erstellen",
        entity_endpoint="/api/v1/agrar/self-billing/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.rechnungen-erstellen.update", bearbeiten_endpoint=None)

def build_agrar_saatgut_abrechnung() -> dict[str, Any]:
    return _batch13_stamm("agrar/saatgut/abrechnung", domain="agrar", title="Abrechnung",
        entity_endpoint="/api/v1/agrar/saatgut/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.saatgut.abrechnung.update", bearbeiten_endpoint=None)

def build_agrar_saatgut_formular() -> dict[str, Any]:
    return _batch13_stamm("agrar/saatgut/formular", domain="agrar", title="Formular",
        entity_endpoint="/api/v1/agrar/saatgut/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.saatgut.formular.update", bearbeiten_endpoint=None)

def build_agrar_saatgut_royalties() -> dict[str, Any]:
    return _batch13_stamm("agrar/saatgut/royalties", domain="agrar", title="Royalties",
        entity_endpoint="/api/v1/agrar/saatgut/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.saatgut.royalties.update", bearbeiten_endpoint=None)

def build_agrar_schlaege_bodenprobe() -> dict[str, Any]:
    return _batch13_stamm("agrar/schlaege/bodenprobe", domain="agrar", title="Bodenprobe",
        entity_endpoint="/api/v1/agrar/schlaege/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.schlaege.bodenprobe.update", bearbeiten_endpoint=None)

def build_agrar_schlaege_duengung() -> dict[str, Any]:
    return _batch13_stamm("agrar/schlaege/duengung", domain="agrar", title="Duengung",
        entity_endpoint="/api/v1/agrar/schlaege/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.schlaege.duengung.update", bearbeiten_endpoint=None)

def build_agrar_schlaege_ernte() -> dict[str, Any]:
    return _batch13_stamm("agrar/schlaege/ernte", domain="agrar", title="Ernte",
        entity_endpoint="/api/v1/agrar/ernte/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.schlaege.ernte.update", bearbeiten_endpoint=None)

def build_agrar_schlaege_formular() -> dict[str, Any]:
    return _batch13_stamm("agrar/schlaege/formular", domain="agrar", title="Formular",
        entity_endpoint="/api/v1/agrar/schlaege/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.schlaege.formular.update", bearbeiten_endpoint=None)

def build_agrar_schlaege_pflanzenschutz() -> dict[str, Any]:
    return _batch13_stamm("agrar/schlaege/pflanzenschutz", domain="agrar", title="Pflanzenschutz",
        entity_endpoint="/api/v1/agrar/schlaege/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.schlaege.pflanzenschutz.update", bearbeiten_endpoint=None)

def build_agrar_schlaege_saat() -> dict[str, Any]:
    return _batch13_stamm("agrar/schlaege/saat", domain="agrar", title="Saat",
        entity_endpoint="/api/v1/agrar/saatgut/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.schlaege.saat.update", bearbeiten_endpoint=None)

def build_agrar_self_billing() -> dict[str, Any]:
    return _batch13_stamm("agrar/self-billing", domain="agrar", title="Self billing",
        entity_endpoint="/api/v1/agrar/self-billing/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.self-billing.update", bearbeiten_endpoint=None)

def build_agrar_sorten_vermehrung() -> dict[str, Any]:
    return _batch13_stamm("agrar/sorten-vermehrung", domain="agrar", title="Sorten vermehrung",
        entity_endpoint="/api/v1/saatzucht/vermehrungsvertraege/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.sorten-vermehrung.update", bearbeiten_endpoint=None)

def build_agrar_vertraege_formular() -> dict[str, Any]:
    return _batch13_stamm("agrar/vertraege/formular", domain="agrar", title="Formular",
        entity_endpoint="/api/v1/kontrakte/{entity_id}", identity_field="bezeichnung",
        edit_permission="agrar.vertraege.formular.update", bearbeiten_endpoint='/api/v1/kontrakte/{entity_id}/actions/bearbeiten')

def build_agrar_wiegeschein_detail() -> dict[str, Any]:
    return _batch13_stamm("agrar/wiegeschein-detail", domain="agrar", title="Wiegeschein detail",
        entity_endpoint="/api/v1/waage/wiegungen/{entity_id}/extended", identity_field="bezeichnung",
        edit_permission="agrar.wiegeschein-detail.update", bearbeiten_endpoint=None)

def build_aktien_dividenden() -> dict[str, Any]:
    return _batch13_stamm("aktien/dividenden", domain="genossenschaft", title="Dividenden",
        entity_endpoint="/api/v1/genossenschaft/mitglieder/{entity_id}", identity_field="bezeichnung",
        edit_permission="aktien.dividenden.update", bearbeiten_endpoint=None)

def build_aktien_hauptversammlung() -> dict[str, Any]:
    return _batch13_stamm("aktien/hauptversammlung", domain="genossenschaft", title="Hauptversammlung",
        entity_endpoint="/api/v1/genossenschaft/mitglieder/{entity_id}", identity_field="bezeichnung",
        edit_permission="aktien.hauptversammlung.update", bearbeiten_endpoint=None)

def build_aktien_mitglieder() -> dict[str, Any]:
    return _batch13_stamm("aktien/mitglieder", domain="genossenschaft", title="Mitglieder",
        entity_endpoint="/api/v1/genossenschaft/mitglieder/{entity_id}", identity_field="bezeichnung",
        edit_permission="aktien.mitglieder.update", bearbeiten_endpoint=None)

def build_aktien_stimmrechte() -> dict[str, Any]:
    return _batch13_stamm("aktien/stimmrechte", domain="genossenschaft", title="Stimmrechte",
        entity_endpoint="/api/v1/genossenschaft/mitglieder/{entity_id}", identity_field="bezeichnung",
        edit_permission="aktien.stimmrechte.update", bearbeiten_endpoint=None)

def build_aktien_zeichnungen() -> dict[str, Any]:
    return _batch13_stamm("aktien/zeichnungen", domain="genossenschaft", title="Zeichnungen",
        entity_endpoint="/api/v1/genossenschaft/mitglieder/{entity_id}", identity_field="bezeichnung",
        edit_permission="aktien.zeichnungen.update", bearbeiten_endpoint=None)

def build_analysis_what_if_simulator() -> dict[str, Any]:
    return _batch13_stamm("analysis/what-if-simulator", domain="reporting", title="What if simulator",
        entity_endpoint="/api/v1/agrar/rations-optimization/feeding/reports/{entity_id}", identity_field="bezeichnung",
        edit_permission="analysis.what-if-simulator.update", bearbeiten_endpoint=None)

def build_annahme_erfassung() -> dict[str, Any]:
    return _batch13_stamm("annahme/erfassung", domain="agrar", title="Erfassung",
        entity_endpoint="/api/v1/annahme/warteschlange/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.erfassung.update", bearbeiten_endpoint=None)

def build_annahme_labor() -> dict[str, Any]:
    return _batch13_stamm("annahme/labor", domain="agrar", title="Labor",
        entity_endpoint="/api/v1/labor/labor-auftraege/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.labor.update", bearbeiten_endpoint=None)

def build_annahme_lkw_registrierung() -> dict[str, Any]:
    return _batch13_stamm("annahme/lkw-registrierung", domain="agrar", title="Lkw registrierung",
        entity_endpoint="/api/v1/annahme/warteschlange/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.lkw-registrierung.update", bearbeiten_endpoint=None)

def build_annahme_muster() -> dict[str, Any]:
    return _batch13_stamm("annahme/muster", domain="agrar", title="Muster",
        entity_endpoint="/api/v1/annahme/warteschlange/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.muster.update", bearbeiten_endpoint=None)

def build_annahme_qualitaets_check() -> dict[str, Any]:
    return _batch13_stamm("annahme/qualitaets-check", domain="agrar", title="Qualitaets check",
        entity_endpoint="/api/v1/annahme/warteschlange/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.qualitaets-check.update", bearbeiten_endpoint=None)

def build_annahme_rohwaren_annahme() -> dict[str, Any]:
    return _batch13_stamm("annahme/rohwaren-annahme", domain="agrar", title="Rohwaren annahme",
        entity_endpoint="/api/v1/annahme/warteschlange/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.rohwaren-annahme.update", bearbeiten_endpoint=None)

def build_annahme_silo_zuweisung() -> dict[str, Any]:
    return _batch13_stamm("annahme/silo-zuweisung", domain="agrar", title="Silo zuweisung",
        entity_endpoint="/api/v1/silo/zielzellen-vorschlag/lot/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.silo-zuweisung.update", bearbeiten_endpoint=None)

def build_annahme_trocknung() -> dict[str, Any]:
    return _batch13_stamm("annahme/trocknung", domain="agrar", title="Trocknung",
        entity_endpoint="/api/v1/process/trocknungs-abrechnung/preview/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.trocknung.update", bearbeiten_endpoint=None)

def build_annahme_voranmeldung() -> dict[str, Any]:
    return _batch13_stamm("annahme/voranmeldung", domain="agrar", title="Voranmeldung",
        entity_endpoint="/api/v1/annahme/warteschlange/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.voranmeldung.update", bearbeiten_endpoint=None)

def build_annahme_waage_1() -> dict[str, Any]:
    return _batch13_stamm("annahme/waage-1", domain="agrar", title="Waage 1",
        entity_endpoint="/api/v1/waage/waagen/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.waage-1.update", bearbeiten_endpoint=None)

def build_annahme_waage_2() -> dict[str, Any]:
    return _batch13_stamm("annahme/waage-2", domain="agrar", title="Waage 2",
        entity_endpoint="/api/v1/waage/waagen/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.waage-2.update", bearbeiten_endpoint=None)

def build_annahme_wartezeit() -> dict[str, Any]:
    return _batch13_stamm("annahme/wartezeit", domain="agrar", title="Wartezeit",
        entity_endpoint="/api/v1/annahme/warteschlange/{entity_id}", identity_field="bezeichnung",
        edit_permission="annahme.wartezeit.update", bearbeiten_endpoint=None)

def build_annahme_wiegeschein() -> dict[str, Any]:
    return _batch13_stamm("annahme/wiegeschein", domain="agrar", title="Wiegeschein",
        entity_endpoint="/api/v1/waage/wiegungen/{entity_id}/extended", identity_field="bezeichnung",
        edit_permission="annahme.wiegeschein.update", bearbeiten_endpoint=None)

def build_artikel_bestandsuebersicht() -> dict[str, Any]:
    return _batch13_stamm("artikel/bestandsuebersicht", domain="lager", title="Bestandsuebersicht",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.bestandsuebersicht.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_ersatzteile() -> dict[str, Any]:
    return _batch13_stamm("artikel/ersatzteile", domain="lager", title="Ersatzteile",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.ersatzteile.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_gebinde() -> dict[str, Any]:
    return _batch13_stamm("artikel/gebinde", domain="lager", title="Gebinde",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.gebinde.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_chargen_pflicht() -> dict[str, Any]:
    return _batch13_stamm("artikel/chargen-pflicht", domain="lager", title="Chargen pflicht",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.chargen-pflicht.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_gefahrgut() -> dict[str, Any]:
    return _batch13_stamm("artikel/gefahrgut", domain="lager", title="Gefahrgut",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.gefahrgut.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_herkunft() -> dict[str, Any]:
    return _batch13_stamm("artikel/herkunft", domain="lager", title="Herkunft",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.herkunft.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_kategorien() -> dict[str, Any]:
    return _batch13_stamm("artikel/kategorien", domain="lager", title="Kategorien",
        entity_endpoint="/api/v1/stammdaten/warengruppen/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.kategorien.update", bearbeiten_endpoint='/api/v1/stammdaten/warengruppen/{entity_id}/actions/bearbeiten')

def build_artikel_konditionen() -> dict[str, Any]:
    return _batch13_stamm("artikel/konditionen", domain="lager", title="Konditionen",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.konditionen.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_lieferanten_artikel() -> dict[str, Any]:
    return _batch13_stamm("artikel/lieferanten-artikel", domain="lager", title="Lieferanten artikel",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.lieferanten-artikel.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_preisstaffeln() -> dict[str, Any]:
    return _batch13_stamm("artikel/preisstaffeln", domain="lager", title="Preisstaffeln",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.preisstaffeln.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_qualitaetsmerkmale() -> dict[str, Any]:
    return _batch13_stamm("artikel/qualitaetsmerkmale", domain="lager", title="Qualitaetsmerkmale",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.qualitaetsmerkmale.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_rabattgruppen() -> dict[str, Any]:
    return _batch13_stamm("artikel/rabattgruppen", domain="lager", title="Rabattgruppen",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.rabattgruppen.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_stuecklisten() -> dict[str, Any]:
    return _batch13_stamm("artikel/stuecklisten", domain="lager", title="Stuecklisten",
        entity_endpoint="/api/v1/produktion/stuecklisten/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.stuecklisten.update", bearbeiten_endpoint=None)

def build_artikel_texte_medien() -> dict[str, Any]:
    return _batch13_stamm("artikel/texte-medien", domain="lager", title="Texte medien",
        entity_endpoint="/api/v1/articles/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.texte-medien.update", bearbeiten_endpoint='/api/v1/articles/{entity_id}/actions/bearbeiten')

def build_artikel_umrechnungen() -> dict[str, Any]:
    return _batch13_stamm("artikel/umrechnungen", domain="lager", title="Umrechnungen",
        entity_endpoint="/api/v1/artikel/mengeneinheiten/gruppen/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.umrechnungen.update", bearbeiten_endpoint=None)

def build_artikel_verpackungen() -> dict[str, Any]:
    return _batch13_stamm("artikel/verpackungen", domain="lager", title="Verpackungen",
        entity_endpoint="/api/v1/artikel/verpackungen/{entity_id}", identity_field="bezeichnung",
        edit_permission="artikel.verpackungen.update", bearbeiten_endpoint=None)

def build_artikel_zoll_intrastat() -> dict[str, Any]:
    return _batch13_stamm("artikel/zoll-intrastat", domain="lager", title="Zoll intrastat",
        entity_endpoint="/api/v1/compliance/intrastat/meldungen/{entity_id}/validate", identity_field="bezeichnung",
        edit_permission="artikel.zoll-intrastat.update", bearbeiten_endpoint=None)

def build_auswertungen_abfrage_generator() -> dict[str, Any]:
    return _batch13_stamm("auswertungen/abfrage-generator", domain="reporting", title="Abfrage generator",
        entity_endpoint="/api/v1/l3-report-catalog/{entity_id}/run", identity_field="bezeichnung",
        edit_permission="auswertungen.abfrage-generator.update", bearbeiten_endpoint=None)

def build_auswertungen_agrarmarkt_bericht() -> dict[str, Any]:
    return _batch13_stamm("auswertungen/agrarmarkt-bericht", domain="reporting", title="Agrarmarkt bericht",
        entity_endpoint="/api/v1/massebilanz/{entity_id}/bericht", identity_field="bezeichnung",
        edit_permission="auswertungen.agrarmarkt-bericht.update", bearbeiten_endpoint=None)

def build_auswertungen_deckungsbeitraege() -> dict[str, Any]:
    return _batch13_stamm("auswertungen/deckungsbeitraege", domain="reporting", title="Deckungsbeitraege",
        entity_endpoint="/api/v1/crm/bedarfsdeckung/{entity_id}", identity_field="bezeichnung",
        edit_permission="auswertungen.deckungsbeitraege.update", bearbeiten_endpoint=None)

def build_auswertungen_erntebilanz() -> dict[str, Any]:
    return _batch13_stamm("auswertungen/erntebilanz", domain="reporting", title="Erntebilanz",
        entity_endpoint="/api/v1/l3-report-catalog/{entity_id}/run", identity_field="bezeichnung",
        edit_permission="auswertungen.erntebilanz.update", bearbeiten_endpoint=None)

def build_auswertungen_kundenumsatz() -> dict[str, Any]:
    return _batch13_stamm("auswertungen/kundenumsatz", domain="reporting", title="Kundenumsatz",
        entity_endpoint="/api/v1/l3-report-catalog/{entity_id}/drilldown", identity_field="bezeichnung",
        edit_permission="auswertungen.kundenumsatz.update", bearbeiten_endpoint=None)

def build_auswertungen_lagerumschlag() -> dict[str, Any]:
    return _batch13_stamm("auswertungen/lagerumschlag", domain="reporting", title="Lagerumschlag",
        entity_endpoint="/api/v1/l3-report-catalog/{entity_id}/run", identity_field="bezeichnung",
        edit_permission="auswertungen.lagerumschlag.update", bearbeiten_endpoint=None)

def build_auswertungen_lieferantenbewertung() -> dict[str, Any]:
    return _batch13_stamm("auswertungen/lieferantenbewertung", domain="reporting", title="Lieferantenbewertung",
        entity_endpoint="/api/v1/l3-report-catalog/{entity_id}/run", identity_field="bezeichnung",
        edit_permission="auswertungen.lieferantenbewertung.update", bearbeiten_endpoint=None)

def build_auswertungen_rohertrag() -> dict[str, Any]:
    return _batch13_stamm("auswertungen/rohertrag", domain="reporting", title="Rohertrag",
        entity_endpoint="/api/v1/l3-report-catalog/{entity_id}/run", identity_field="bezeichnung",
        edit_permission="auswertungen.rohertrag.update", bearbeiten_endpoint=None)

BATCH13_SCREEN_BUILDERS: dict[str, Any] = {
    "admin/agenten-integration": build_admin_agenten_integration,
    "admin/ai-approvals": build_admin_ai_approvals,
    "admin/api-keys": build_admin_api_keys,
    "admin/backup-restore": build_admin_backup_restore,
    "admin/berechtigungen-matrix": build_admin_berechtigungen_matrix,
    "admin/branches": build_admin_branches,
    "admin/command-monitor": build_admin_command_monitor,
    "admin/system-einstellungen": build_admin_system_einstellungen,
    "admin/tankstelle-evb": build_admin_tankstelle_evb,
    "admin/tenants": build_admin_tenants,
    "admin/users": build_admin_users,
    "admin/workflow-editor": build_admin_workflow_editor,
    "admin/zeitachsen-editor": build_admin_zeitachsen_editor,
    "agrar/annahme-abrechnung": build_agrar_annahme_abrechnung,
    "agrar/ernte-annahme-abrechnung": build_agrar_ernte_annahme_abrechnung,
    "agrar/kontrakte/formular": build_agrar_kontrakte_formular,
    "agrar/lieferschein-erstellen": build_agrar_lieferschein_erstellen,
    "agrar/maschinen/formular": build_agrar_maschinen_formular,
    "agrar/partie-historie": build_agrar_partie_historie,
    "agrar/pflanzenschutz-rechner": build_agrar_pflanzenschutz_rechner,
    "agrar/probenehmer-stamm": build_agrar_probenehmer_stamm,
    "agrar/rechnungen-erstellen": build_agrar_rechnungen_erstellen,
    "agrar/saatgut/abrechnung": build_agrar_saatgut_abrechnung,
    "agrar/saatgut/formular": build_agrar_saatgut_formular,
    "agrar/saatgut/royalties": build_agrar_saatgut_royalties,
    "agrar/schlaege/bodenprobe": build_agrar_schlaege_bodenprobe,
    "agrar/schlaege/duengung": build_agrar_schlaege_duengung,
    "agrar/schlaege/ernte": build_agrar_schlaege_ernte,
    "agrar/schlaege/formular": build_agrar_schlaege_formular,
    "agrar/schlaege/pflanzenschutz": build_agrar_schlaege_pflanzenschutz,
    "agrar/schlaege/saat": build_agrar_schlaege_saat,
    "agrar/self-billing": build_agrar_self_billing,
    "agrar/sorten-vermehrung": build_agrar_sorten_vermehrung,
    "agrar/vertraege/formular": build_agrar_vertraege_formular,
    "agrar/wiegeschein-detail": build_agrar_wiegeschein_detail,
    "aktien/dividenden": build_aktien_dividenden,
    "aktien/hauptversammlung": build_aktien_hauptversammlung,
    "aktien/mitglieder": build_aktien_mitglieder,
    "aktien/stimmrechte": build_aktien_stimmrechte,
    "aktien/zeichnungen": build_aktien_zeichnungen,
    "analysis/what-if-simulator": build_analysis_what_if_simulator,
    "annahme/erfassung": build_annahme_erfassung,
    "annahme/labor": build_annahme_labor,
    "annahme/lkw-registrierung": build_annahme_lkw_registrierung,
    "annahme/muster": build_annahme_muster,
    "annahme/qualitaets-check": build_annahme_qualitaets_check,
    "annahme/rohwaren-annahme": build_annahme_rohwaren_annahme,
    "annahme/silo-zuweisung": build_annahme_silo_zuweisung,
    "annahme/trocknung": build_annahme_trocknung,
    "annahme/voranmeldung": build_annahme_voranmeldung,
    "annahme/waage-1": build_annahme_waage_1,
    "annahme/waage-2": build_annahme_waage_2,
    "annahme/wartezeit": build_annahme_wartezeit,
    "annahme/wiegeschein": build_annahme_wiegeschein,
    "artikel/bestandsuebersicht": build_artikel_bestandsuebersicht,
    "artikel/ersatzteile": build_artikel_ersatzteile,
    "artikel/gebinde": build_artikel_gebinde,
    "artikel/chargen-pflicht": build_artikel_chargen_pflicht,
    "artikel/gefahrgut": build_artikel_gefahrgut,
    "artikel/herkunft": build_artikel_herkunft,
    "artikel/kategorien": build_artikel_kategorien,
    "artikel/konditionen": build_artikel_konditionen,
    "artikel/lieferanten-artikel": build_artikel_lieferanten_artikel,
    "artikel/preisstaffeln": build_artikel_preisstaffeln,
    "artikel/qualitaetsmerkmale": build_artikel_qualitaetsmerkmale,
    "artikel/rabattgruppen": build_artikel_rabattgruppen,
    "artikel/stuecklisten": build_artikel_stuecklisten,
    "artikel/texte-medien": build_artikel_texte_medien,
    "artikel/umrechnungen": build_artikel_umrechnungen,
    "artikel/verpackungen": build_artikel_verpackungen,
    "artikel/zoll-intrastat": build_artikel_zoll_intrastat,
    "auswertungen/abfrage-generator": build_auswertungen_abfrage_generator,
    "auswertungen/agrarmarkt-bericht": build_auswertungen_agrarmarkt_bericht,
    "auswertungen/deckungsbeitraege": build_auswertungen_deckungsbeitraege,
    "auswertungen/erntebilanz": build_auswertungen_erntebilanz,
    "auswertungen/kundenumsatz": build_auswertungen_kundenumsatz,
    "auswertungen/lagerumschlag": build_auswertungen_lagerumschlag,
    "auswertungen/lieferantenbewertung": build_auswertungen_lieferantenbewertung,
    "auswertungen/rohertrag": build_auswertungen_rohertrag,
}

BATCH13_ROUTEN: dict[str, str] = {
    "admin/agenten-integration": "/admin/agenten-integration",
    "admin/ai-approvals": "/admin/ai-approvals",
    "admin/api-keys": "/admin/api-keys",
    "admin/backup-restore": "/admin/backup-restore",
    "admin/berechtigungen-matrix": "/admin/berechtigungen-matrix",
    "admin/branches": "/admin/branches",
    "admin/command-monitor": "/admin/command-monitor",
    "admin/system-einstellungen": "/admin/system-einstellungen",
    "admin/tankstelle-evb": "/admin/tankstelle-evb",
    "admin/tenants": "/admin/tenants",
    "admin/users": "/admin/users",
    "admin/workflow-editor": "/admin/workflow-editor",
    "admin/zeitachsen-editor": "/admin/zeitachsen-editor",
    "agrar/annahme-abrechnung": "/agrar/annahme-abrechnung",
    "agrar/ernte-annahme-abrechnung": "/agrar/ernte-annahme-abrechnung",
    "agrar/kontrakte/formular": "/agrar/kontrakte/formular",
    "agrar/lieferschein-erstellen": "/agrar/lieferschein-erstellen",
    "agrar/maschinen/formular": "/agrar/maschinen/formular",
    "agrar/partie-historie": "/agrar/partie-historie",
    "agrar/pflanzenschutz-rechner": "/agrar/pflanzenschutz-rechner",
    "agrar/probenehmer-stamm": "/agrar/probenehmer-stamm",
    "agrar/rechnungen-erstellen": "/agrar/rechnungen-erstellen",
    "agrar/saatgut/abrechnung": "/agrar/saatgut/abrechnung",
    "agrar/saatgut/formular": "/agrar/saatgut/formular",
    "agrar/saatgut/royalties": "/agrar/saatgut/royalties",
    "agrar/schlaege/bodenprobe": "/agrar/schlaege/bodenprobe",
    "agrar/schlaege/duengung": "/agrar/schlaege/duengung",
    "agrar/schlaege/ernte": "/agrar/schlaege/ernte",
    "agrar/schlaege/formular": "/agrar/schlaege/formular",
    "agrar/schlaege/pflanzenschutz": "/agrar/schlaege/pflanzenschutz",
    "agrar/schlaege/saat": "/agrar/schlaege/saat",
    "agrar/self-billing": "/agrar/self-billing",
    "agrar/sorten-vermehrung": "/agrar/sorten-vermehrung",
    "agrar/vertraege/formular": "/agrar/vertraege/formular",
    "agrar/wiegeschein-detail": "/agrar/wiegeschein-detail",
    "aktien/dividenden": "/aktien/dividenden",
    "aktien/hauptversammlung": "/aktien/hauptversammlung",
    "aktien/mitglieder": "/aktien/mitglieder",
    "aktien/stimmrechte": "/aktien/stimmrechte",
    "aktien/zeichnungen": "/aktien/zeichnungen",
    "analysis/what-if-simulator": "/analysis/what-if-simulator",
    "annahme/erfassung": "/annahme/erfassung",
    "annahme/labor": "/annahme/labor",
    "annahme/lkw-registrierung": "/annahme/lkw-registrierung",
    "annahme/muster": "/annahme/muster",
    "annahme/qualitaets-check": "/annahme/qualitaets-check",
    "annahme/rohwaren-annahme": "/annahme/rohwaren-annahme",
    "annahme/silo-zuweisung": "/annahme/silo-zuweisung",
    "annahme/trocknung": "/annahme/trocknung",
    "annahme/voranmeldung": "/annahme/voranmeldung",
    "annahme/waage-1": "/annahme/waage-1",
    "annahme/waage-2": "/annahme/waage-2",
    "annahme/wartezeit": "/annahme/wartezeit",
    "annahme/wiegeschein": "/annahme/wiegeschein",
    "artikel/bestandsuebersicht": "/artikel/bestandsuebersicht",
    "artikel/ersatzteile": "/artikel/ersatzteile",
    "artikel/gebinde": "/artikel/gebinde",
    "artikel/chargen-pflicht": "/artikel/chargen-pflicht",
    "artikel/gefahrgut": "/artikel/gefahrgut",
    "artikel/herkunft": "/artikel/herkunft",
    "artikel/kategorien": "/artikel/kategorien",
    "artikel/konditionen": "/artikel/konditionen",
    "artikel/lieferanten-artikel": "/artikel/lieferanten-artikel",
    "artikel/preisstaffeln": "/artikel/preisstaffeln",
    "artikel/qualitaetsmerkmale": "/artikel/qualitaetsmerkmale",
    "artikel/rabattgruppen": "/artikel/rabattgruppen",
    "artikel/stuecklisten": "/artikel/stuecklisten",
    "artikel/texte-medien": "/artikel/texte-medien",
    "artikel/umrechnungen": "/artikel/umrechnungen",
    "artikel/verpackungen": "/artikel/verpackungen",
    "artikel/zoll-intrastat": "/artikel/zoll-intrastat",
    "auswertungen/abfrage-generator": "/auswertungen/abfrage-generator",
    "auswertungen/agrarmarkt-bericht": "/auswertungen/agrarmarkt-bericht",
    "auswertungen/deckungsbeitraege": "/auswertungen/deckungsbeitraege",
    "auswertungen/erntebilanz": "/auswertungen/erntebilanz",
    "auswertungen/kundenumsatz": "/auswertungen/kundenumsatz",
    "auswertungen/lagerumschlag": "/auswertungen/lagerumschlag",
    "auswertungen/lieferantenbewertung": "/auswertungen/lieferantenbewertung",
    "auswertungen/rohertrag": "/auswertungen/rohertrag",
}

BATCH13_SYNONYME: dict[str, list[str]] = {}

