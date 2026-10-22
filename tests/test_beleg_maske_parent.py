"""Vertragstests fuer BelegMaskeParent (BELEG-020 Vererbung).

Prueft, dass alle 9 kanonischen Belegvarianten (+ Kandidaten) den Parent-Vertrag
befolgen:
  - Parent-Vererbung aller Pflichtsektionen und Register-Tabs.
  - ProcessBand vs ProcessRibbon Invariante (keine Vermischung).
  - Varianten-Overrides (bucht, mit_preisen, folgebelege, Partnerrolle).
  - ``made by studio``-Metadaten-Bereitschaft (Gates A–C).

Keine Datenbank, keine Mock-DB: Reine Struktur-/Vertragsvalidierung.
"""
from __future__ import annotations

import pytest

from app.core import beleg_maske_parent as bmp
from app.core.belegvertrag import BELEGARTEN


# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────


def _build_parent(belegart: str, **extra: dict) -> dict:
    """Baut einen Parent fuer eine Belegart mit Default-Metadaten."""
    defaults = {
        "business_purpose": f"Verwalte {belegart}",
        "example_prompts": [f"Zeige mich die {belegart}"],
        "test_id": f"screen-{belegart}",
    }
    defaults.update(extra)
    return bmp.build_beleg_maske_parent(belegart, **defaults)


def _check_tabs(definition: dict, expected_keys: tuple[str, ...] = bmp.REITER) -> None:
    """Prueft, dass alle erwarteten Tabs (in Reihenfolge) vorhanden sind."""
    tabs = definition["tabs"]
    assert len(tabs) >= len(expected_keys), f"Erwartet min. {len(expected_keys)} Tabs, habe {len(tabs)}"
    for i, expected_key in enumerate(expected_keys):
        assert tabs[i]["key"] == expected_key, f"Tab {i}: erwarte '{expected_key}', habe '{tabs[i]['key']}'"


def _check_data_sources(definition: dict, expected_keys: tuple[str, ...]) -> None:
    """Prueft, dass die erforderlichen DataSources vorhanden sind."""
    sources = {ds["key"]: ds for ds in definition["dataSources"]}
    for key in expected_keys:
        assert key in sources, f"DataSource '{key}' fehlt"


def _check_kopf_felder(definition: dict, belegart: str, mit_preisen: bool, bucht: bool) -> None:
    """Prueft, dass die Kopf-Felder der Variante entsprechen."""
    kopf_tab = next((t for t in definition["tabs"] if t["key"] == "kopf"), None)
    assert kopf_tab is not None, "Kopf-Tab nicht gefunden"
    felder = kopf_tab["fields"]
    field_keys = [f["key"] for f in felder]

    # Basis-Felder, immer vorhanden.
    assert "beleg_nr" in field_keys
    assert "status" in field_keys
    assert "belegdatum" in field_keys
    assert "partner_nummer" in field_keys
    assert "partner_name" in field_keys

    # Summen nur wenn mit_preisen.
    if mit_preisen:
        assert "waehrung" in field_keys
        assert "netto" in field_keys
        assert "steuer" in field_keys
        assert "brutto" in field_keys
    else:
        # Keine Summen-Felder ohne Preise.
        assert "netto" not in field_keys
        assert "steuer" not in field_keys
        assert "brutto" not in field_keys

    # Buchungsstand nur wenn bucht.
    if bucht:
        assert "buchungsstand" in field_keys
        assert "buchungsgrund" in field_keys
    else:
        assert "buchungsstand" not in field_keys
        assert "buchungsgrund" not in field_keys

    # Aktionshinweise immer.
    assert "aktionshinweis" in field_keys


def _check_positions_spalten(definition: dict, mit_preisen: bool, richtung: str, folgebelege: tuple) -> None:
    """Prueft, dass Positionsspalten der Variante entsprechen."""
    pos_tab = next((t for t in definition["tabs"] if t["key"] == "positionen"), None)
    assert pos_tab is not None, "Positionen-Tab nicht gefunden"
    assert "tables" in pos_tab
    table = pos_tab["tables"][0]
    spalten = {s["key"]: s for s in table["columns"]}

    # Mengen-Spalten immer.
    assert "pos_nr" in spalten
    assert "artikel_nr" in spalten
    assert "bezeichnung" in spalten
    assert "menge" in spalten
    assert "einheit" in spalten
    assert "charge" in spalten

    # Offen-Spalte nur wenn Folgebelege.
    if folgebelege:
        assert "menge_offen" in spalten
    else:
        assert "menge_offen" not in spalten

    # Preisspalten nur wenn mit_preisen.
    if mit_preisen:
        assert "einzelpreis" in spalten
        assert "rabatt_prozent" in spalten
        assert "steuerschluessel" in spalten
        assert "netto" in spalten
        # Aufwandskonto nur in Einkauf.
        if richtung == "einkauf":
            assert "aufwandskonto" in spalten
        else:
            assert "aufwandskonto" not in spalten
    else:
        # Keine Preisspalten ohne mit_preisen.
        assert "einzelpreis" not in spalten
        assert "rabatt_prozent" not in spalten
        assert "steuerschluessel" not in spalten
        assert "netto" not in spalten
        assert "aufwandskonto" not in spalten


def _check_aktionen(definition: dict, bucht: bool, folgebelege: tuple) -> None:
    """Prueft, dass die Aktionen der Variante entsprechen."""
    aktionen = {a["key"]: a for a in definition["actions"]}

    # Basis-Aktionen immer.
    assert "bearbeiten" in aktionen
    assert "freigeben" in aktionen
    assert "stornieren" in aktionen

    # Buchen nur wenn bucht.
    if bucht:
        assert "buchen" in aktionen
    else:
        assert "buchen" not in aktionen

    # Umwandeln fuer jedes Folgebeleg.
    for folgeart in folgebelege:
        assert f"umwandeln:{folgeart}" in aktionen, f"Fehlt Aktion 'umwandeln:{folgeart}'"

    # Freigabe-Anfrage/Entscheidung nur wenn bucht.
    if bucht:
        assert any("freigabe_anfordern:post" in k for k in aktionen)
        assert any("freigabe_erteilen:post" in k for k in aktionen)
        assert any("freigabe_ablehnen:post" in k for k in aktionen)


def _check_no_process_band_ribbon_mix(definition: dict) -> None:
    """Prueft, dass weder ProcessBand noch ProcessRibbon interne Schluessel im Label zeigen.

    ProcessBand: zeigt Phasen, naechste Aktion, Blocker — Labels sind verstaendlich.
    ProcessRibbon: navigiert Belegkette — ist eine Renderer-Sache, nicht SD-Label.
    Invariante: Keine internen Prozessschluessel in Action-Labels.
    """
    for action in definition["actions"]:
        label = action.get("label", "")
        # Kein Kommandoname im Label.
        assert not any(f"docflow.{x}" in label.lower() for x in ["update", "post", "convert", "reverse"])
        # Keine interne Schluessel wie aktion_post, aktion_reverse in Labels.
        assert "aktion_" not in label.lower()


def _check_made_by_studio_gates(definition: dict, belegart: str) -> None:
    """Prueft ``made by studio`` Bereitschaft (Gates A–C aus Taxonomie §5).

    Gate A: SD im Register mit Versionshistorie (Builder gebunden).
    Gate B: Studio-Ausgangsimport mit eigener Revision.
    Gate C: Runtime verdrahtet (Route → Screen-ID, Commands gebunden).

    Diese Pruefung prueft nur, dass SD-Struktur und Adapter konsistent sind.
    """
    # Gate A: ID und Adapter konsistent.
    screen_id = f"beleg/{belegart.replace('_', '-')}"
    assert definition["id"] == screen_id, f"Screen-ID falsch: {definition['id']}"
    assert definition["adapter"]["type"] == "native"
    assert definition["adapter"]["sourceId"] == screen_id

    # Basis: schemaVersion, domain, mode sind gesetzt.
    assert definition["schemaVersion"] == 1
    assert definition["domain"] in ("einkauf", "sales")
    assert definition["mode"] == "detail"

    # variant: Metadaten fuer Variantenzuordnung.
    variant = definition.get("variant", {})
    assert variant.get("of") == "beleg"
    assert variant.get("belegart") == belegart
    assert "partnerrolle" in variant
    assert "mitPreisen" in variant
    assert "bucht" in variant
    assert "folgebelege" in variant


# ──────────────────────────────────────────────────────────────────────────────
# Test-Suite
# ──────────────────────────────────────────────────────────────────────────────


class TestBelegMaskeParentStruktur:
    """Grundstruktur des Parent."""

    def test_screen_id_funktion(self) -> None:
        """screen_id() bildet Belegart auf Familie ab."""
        assert bmp.screen_id("sales_invoice") == "beleg/sales-invoice"
        assert bmp.screen_id("purchase_order") == "beleg/purchase-order"
        assert bmp.screen_id("goods_receipt") == "beleg/goods-receipt"

    def test_zustandsfeld_funktion(self) -> None:
        """zustandsfeld() erzeugt enabledWhen-Feldnamen."""
        assert bmp.zustandsfeld("bearbeiten") == "aktion_bearbeiten"
        assert bmp.zustandsfeld("umwandeln:sales_invoice") == "aktion_umwandeln_sales_invoice"

    def test_reiter_konstante(self) -> None:
        """REITER enthaelt alle unveraendlichen Tabs."""
        assert bmp.REITER == ("kopf", "positionen", "kette", "dokumente", "historie")


class TestBelegMaskeParentKanonisch:
    """Alle 9 kanonischen Belegvarianten erfuellen den Parent-Vertrag."""

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_jede_variante_baut_sich(self, belegart: str) -> None:
        """Jede Belegart kann parent-gebaut werden."""
        definition = _build_parent(belegart)
        assert definition is not None
        assert definition["id"] == bmp.screen_id(belegart)

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_tabs_vollstaendig(self, belegart: str) -> None:
        """Alle Register-Tabs sind vorhanden und in richtiger Reihenfolge."""
        definition = _build_parent(belegart)
        _check_tabs(definition)

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_data_sources_vollstaendig(self, belegart: str) -> None:
        """Alle Datensquellen vorhanden."""
        definition = _build_parent(belegart)
        _check_data_sources(definition, ("entity", "positionen", "kette", "dokumente", "historie"))

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_kopffelder_nach_variante(self, belegart: str) -> None:
        """Kopf-Felder entsprechen der Variante (Preise, Buchung)."""
        variante = BELEGARTEN[belegart]
        definition = _build_parent(belegart)
        _check_kopf_felder(definition, belegart, variante.mit_preisen, variante.bucht)

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_positions_spalten_nach_variante(self, belegart: str) -> None:
        """Positionsspalten entsprechen der Variante."""
        variante = BELEGARTEN[belegart]
        definition = _build_parent(belegart)
        _check_positions_spalten(
            definition,
            variante.mit_preisen,
            variante.richtung,
            variante.folgebelege,
        )

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_aktionen_nach_variante(self, belegart: str) -> None:
        """Aktionen entsprechen der Variante (bucht, folgebelege)."""
        variante = BELEGARTEN[belegart]
        definition = _build_parent(belegart)
        _check_aktionen(definition, variante.bucht, variante.folgebelege)

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_no_processband_ribbon_mix(self, belegart: str) -> None:
        """ProcessBand und ProcessRibbon sind nicht vermischt."""
        definition = _build_parent(belegart)
        _check_no_process_band_ribbon_mix(definition)


class TestBelegMaskeParentVererbungInvarianten:
    """Parent-Vererbung-Invarianten: was nicht ueberschrieben werden darf."""

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_floorplan_vererbt(self, belegart: str) -> None:
        """Floorplan ist immer 'transaction'."""
        definition = _build_parent(belegart)
        assert definition["layout"]["floorplan"] == "transaction"

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_sticky_header_footer_vererbt(self, belegart: str) -> None:
        """Header/Footer sind sticky."""
        definition = _build_parent(belegart)
        assert definition["layout"]["stickyHeader"] is True
        assert definition["layout"]["stickyFooter"] is True

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_register_tabs_vererbt(self, belegart: str) -> None:
        """Tabs sind in unveraendlicher Reihenfolge vorhanden."""
        definition = _build_parent(belegart)
        assert definition["layout"].get("registerTabs") is True or "kopf" == definition["tabs"][0]["key"]

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_schema_version_vererbt(self, belegart: str) -> None:
        """schemaVersion ist 1."""
        definition = _build_parent(belegart)
        assert definition["schemaVersion"] == 1

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_mode_vererbt(self, belegart: str) -> None:
        """mode ist 'detail'."""
        definition = _build_parent(belegart)
        assert definition["mode"] == "detail"


class TestBelegMaskeParentVariantenUeberschreibung:
    """Varianten-Overrides: was Child richtig ueberschreiben kann."""

    def test_extra_kopffelder_werden_angehaengt(self) -> None:
        """Child kann Kopf-Felder hinzufuegen."""
        definition = _build_parent(
            "sales_invoice",
            extra_kopffelder=[
                {"key": "custom_field", "label": "Kundenfeldä", "type": "text", "readOnly": True}
            ],
        )
        kopf_tab = next((t for t in definition["tabs"] if t["key"] == "kopf"), None)
        field_keys = [f["key"] for f in kopf_tab["fields"]]
        assert "custom_field" in field_keys

    def test_extra_aktionen_werden_angehaengt(self) -> None:
        """Child kann Aktionen hinzufuegen."""
        extra_action = {
            "key": "custom_action",
            "label": "Fachspezifisch",
            "kind": "secondary",
            "commandEndpoint": "/api/test",
            "method": "POST",
        }
        definition = _build_parent("sales_invoice", extra_aktionen=[extra_action])
        action_keys = [a["key"] for a in definition["actions"]]
        assert "custom_action" in action_keys

    def test_business_purpose_pro_belegart(self) -> None:
        """agentContract.businessPurpose ist pro Belegart."""
        definition = _build_parent("sales_invoice", business_purpose="Manage sales invoices")
        assert definition["agentContract"]["businessPurpose"] == "Manage sales invoices"

    def test_example_prompts_pro_belegart(self) -> None:
        """agentContract.examplePrompts ist pro Belegart."""
        prompts = ["Show me sales invoices", "Create a new invoice"]
        definition = _build_parent("sales_invoice", example_prompts=prompts)
        assert definition["agentContract"]["examplePrompts"] == prompts

    def test_sensitive_fields_dokumentiert(self) -> None:
        """agentContract.sensitiveFields wird dokumentiert."""
        sensitive = ["partner_name", "netto"]
        definition = _build_parent("sales_invoice", sensitive_fields=sensitive)
        assert set(definition["agentContract"]["sensitiveFields"]) == set(sensitive)


class TestBelegMaskeParentMadeByStudioGates:
    """'Made by studio'-Bereitschaft (Gates A–C)."""

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_made_by_studio_gate_a(self, belegart: str) -> None:
        """Gate A: SD im Register mit Versionsbindung."""
        definition = _build_parent(belegart)
        _check_made_by_studio_gates(definition, belegart)

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_variant_metadaten_vorhanden(self, belegart: str) -> None:
        """Variant-Metadaten fuer Variantenzuordnung."""
        variante = BELEGARTEN[belegart]
        definition = _build_parent(belegart)
        assert definition["variant"]["belegart"] == belegart
        assert definition["variant"]["partnerrolle"] == variante.partnerrolle
        assert definition["variant"]["mitPreisen"] == variante.mit_preisen
        assert definition["variant"]["bucht"] == variante.bucht
        assert definition["variant"]["folgebelege"] == list(variante.folgebelege)


class TestBelegMaskeParentDocFlowIntegration:
    """DocFlow-Integration: Creation und Adapter."""

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_creation_default_vorhanden(self, belegart: str) -> None:
        """Default creation (DocFlow) ist konfiguriert."""
        definition = _build_parent(belegart)
        assert "creation" in definition
        creation = definition["creation"]
        assert creation["adapter"] == "docflow.create.v1"
        assert creation["endpoint"] == "/api/v1/docflow/"
        assert creation["permission"] == "belege.bearbeiten"

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_creation_partner_datenquelle(self, belegart: str) -> None:
        """Creation hat Partner-Lookup-Datenquelle."""
        definition = _build_parent(belegart)
        creation = definition["creation"]
        partner_source = next(
            (s for s in creation.get("dataSources", []) if s["key"] == "partner"),
            None,
        )
        assert partner_source is not None

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_adapter_native_vererbt(self, belegart: str) -> None:
        """Adapter ist immer 'native'."""
        definition = _build_parent(belegart)
        assert definition["adapter"]["type"] == "native"
        assert definition["adapter"]["sourceId"] == bmp.screen_id(belegart)
        assert definition["adapter"]["temporary"] is False


class TestBelegMaskeParentWorkflow:
    """Workflow und ProcessBand-Handling."""

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_workflow_oder_no_workflow_reason(self, belegart: str) -> None:
        """Entweder workflow oder noWorkflowReason gesetzt."""
        definition = _build_parent(belegart)
        has_workflow = "workflow" in definition
        has_reason = "noWorkflowReason" in definition
        assert has_workflow or has_reason, "Beleg braucht workflow oder noWorkflowReason"

    def test_custom_workflow_wird_respektiert(self) -> None:
        """Child kann custom workflow definieren."""
        custom_workflow = {
            "phases": [{"id": "draft", "label": "Entwurf"}],
        }
        definition = _build_parent(
            "sales_invoice",
            workflow=custom_workflow,
        )
        assert definition["workflow"] == custom_workflow

    @pytest.mark.parametrize("belegart", sorted(BELEGARTEN.keys()))
    def test_action_labels_keine_internen_schluessel(self, belegart: str) -> None:
        """Action-Labels zeigen keine internen Prozessschluessel."""
        definition = _build_parent(belegart)
        for action in definition["actions"]:
            label = action.get("label", "")
            # Keine interne Schl. wie "docflow.post" im Label.
            assert "docflow" not in label.lower()
            # Keine interne Feld-Schluessel wie "aktion_post".
            assert "aktion_" not in label.lower()


class TestBelegMaskeParentInvalidInputs:
    """Error-Handling: ungueltige Eingaben."""

    def test_unbekannte_belegart_schlaegt_fehl(self) -> None:
        """Unbekannte Belegart wirft ValueError."""
        with pytest.raises(ValueError, match="hat keine Variante"):
            _build_parent("unknown_type")

    def test_fehlende_business_purpose_nicht_kritisch(self) -> None:
        """Fehlende business_purpose ist kein Fehler (nur im agentContract)."""
        # Konstruktor erlaubt Default.
        definition = _build_parent("sales_invoice", business_purpose="")
        assert definition["agentContract"]["businessPurpose"] == ""


class TestBelegMaskeParentHelpers:
    """Hilfsfunktionen: Spalten, Felder, Aktionen."""

    def test_beleg_positionsspalten_varianten(self) -> None:
        """positionsspalten() passt sich an Variante an."""
        v_mit_preisen = BELEGARTEN["sales_invoice"]
        spalten_mit = bmp.beleg_positionsspalten(v_mit_preisen)
        spalten_keys = [s["key"] for s in spalten_mit]
        assert "einzelpreis" in spalten_keys

        v_ohne_preisen = BELEGARTEN["sales_delivery"]
        spalten_ohne = bmp.beleg_positionsspalten(v_ohne_preisen)
        spalten_keys_ohne = [s["key"] for s in spalten_ohne]
        assert "einzelpreis" not in spalten_keys_ohne

    def test_beleg_kopffelder_mit_preisen(self) -> None:
        """kopffelder() enthaelt Summen wenn mit_preisen."""
        variante = BELEGARTEN["sales_invoice"]
        felder = bmp.beleg_kopffelder(variante)
        field_keys = [f["key"] for f in felder]
        assert "netto" in field_keys
        assert "steuer" in field_keys
        assert "brutto" in field_keys

    def test_beleg_kopffelder_ohne_preisen(self) -> None:
        """kopffelder() hat keine Summen ohne mit_preisen."""
        variante = BELEGARTEN["sales_delivery"]
        felder = bmp.beleg_kopffelder(variante)
        field_keys = [f["key"] for f in felder]
        assert "netto" not in field_keys
        assert "steuer" not in field_keys
        assert "brutto" not in field_keys

    def test_beleg_aktionen_buchen(self) -> None:
        """aktionen() enthaelt 'buchen' wenn bucht."""
        variante = BELEGARTEN["sales_invoice"]
        aktionen = bmp.beleg_aktionen(variante)
        action_keys = [a["key"] for a in aktionen]
        assert "buchen" in action_keys

    def test_beleg_aktionen_keine_buchen(self) -> None:
        """aktionen() hat kein 'buchen' wenn nicht bucht."""
        variante = BELEGARTEN["sales_delivery"]
        aktionen = bmp.beleg_aktionen(variante)
        action_keys = [a["key"] for a in aktionen]
        assert "buchen" not in action_keys

    def test_beleg_meridian_layout_extras(self) -> None:
        """Meridian-Profil unterscheidet preisende und mengenonly Varianten."""
        mit = bmp.beleg_meridian_layout_extras(BELEGARTEN["sales_invoice"])
        ohne = bmp.beleg_meridian_layout_extras(BELEGARTEN["sales_delivery"])
        assert mit["tableProfile"] == "financial"
        assert ohne["tableProfile"] == "standard"
        assert mit["contextRail"] == "workflow"
        assert mit["density"] == "compact"
