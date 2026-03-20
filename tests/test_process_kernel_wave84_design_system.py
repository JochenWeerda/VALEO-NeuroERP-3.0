"""
Wave 84 — Einheitliches Designsystem (Gap 021)

Tests für DesignToken, KomponentenKontrakt, DesignSystemRegistry,
validate_page_uses_ds_components() und get_valeo_design_system().

Gap 021: 100% neue Seiten nutzen DS-Komponenten
"""
from __future__ import annotations

import pytest

from app.core.design_system_contracts import (
    DSComplianceResult,
    DesignSystemRegistry,
    DesignToken,
    KomponentenKategorie,
    KomponentenKontrakt,
    KomponentenStatus,
    TokenTyp,
    get_valeo_design_system,
    validate_page_uses_ds_components,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _registry_mit_komponenten() -> DesignSystemRegistry:
    registry = DesignSystemRegistry()
    for name, kat in [
        ("Button", KomponentenKategorie.EINGABE),
        ("Input", KomponentenKategorie.EINGABE),
        ("ObjectPage", KomponentenKategorie.MUSTER),
        ("ErrorPanel", KomponentenKategorie.FEEDBACK),
        ("PolicyExplanationBadge", KomponentenKategorie.POLICY),
    ]:
        registry.register_komponente(KomponentenKontrakt(
            name=name,
            kategorie=kat,
            status=KomponentenStatus.STABIL,
            dateipfad=f"components/{name.lower()}.tsx",
        ))
    return registry


def _token(name: str = "color.primary.500", typ: TokenTyp = TokenTyp.FARBE) -> DesignToken:
    return DesignToken(name=name, wert="#2563eb", typ=typ, tailwind_klasse="text-blue-600")


# ---------------------------------------------------------------------------
# TestDesignToken
# ---------------------------------------------------------------------------

class TestDesignToken:
    def test_as_dict_vollstaendig(self):
        token = _token()
        d = token.as_dict()
        assert d["name"] == "color.primary.500"
        assert d["typ"] == TokenTyp.FARBE.value
        assert d["tailwind_klasse"] == "text-blue-600"

    def test_alle_token_typen(self):
        for typ in TokenTyp:
            t = DesignToken(name=f"t.{typ.value}", wert="x", typ=typ)
            assert t.typ == typ


# ---------------------------------------------------------------------------
# TestKomponentenKontrakt
# ---------------------------------------------------------------------------

class TestKomponentenKontrakt:
    def test_as_dict_vollstaendig(self):
        k = KomponentenKontrakt(
            name="InlineValidationMessage",
            kategorie=KomponentenKategorie.FEEDBACK,
            status=KomponentenStatus.STABIL,
            dateipfad="components/validation/InlineValidationMessage.tsx",
            pflicht_props=["result"],
            optionale_props=["showSuccessIcon"],
            wcag_regeln=["role=alert"],
            welle=79,
        )
        d = k.as_dict()
        assert d["name"] == "InlineValidationMessage"
        assert d["kategorie"] == KomponentenKategorie.FEEDBACK.value
        assert d["status"] == KomponentenStatus.STABIL.value
        assert d["welle"] == 79
        assert "result" in d["pflicht_props"]

    def test_alle_kategorien(self):
        for kat in KomponentenKategorie:
            k = KomponentenKontrakt(
                name=f"K_{kat.value}", kategorie=kat,
                status=KomponentenStatus.STABIL, dateipfad="x.tsx",
            )
            assert k.kategorie == kat

    def test_alle_status_werte(self):
        for status in KomponentenStatus:
            k = KomponentenKontrakt(
                name="X", kategorie=KomponentenKategorie.EINGABE,
                status=status, dateipfad="x.tsx",
            )
            assert k.status == status


# ---------------------------------------------------------------------------
# TestDesignSystemRegistry
# ---------------------------------------------------------------------------

class TestDesignSystemRegistry:
    def test_register_und_get_komponente(self):
        registry = DesignSystemRegistry()
        k = KomponentenKontrakt(
            name="Button", kategorie=KomponentenKategorie.EINGABE,
            status=KomponentenStatus.STABIL, dateipfad="components/ui/button.tsx",
        )
        registry.register_komponente(k)
        assert registry.get_komponente("Button") is k

    def test_get_unbekannte_komponente_gibt_none(self):
        registry = DesignSystemRegistry()
        assert registry.get_komponente("Unbekannt") is None

    def test_register_und_get_token(self):
        registry = DesignSystemRegistry()
        token = _token()
        registry.register_token(token)
        assert registry.get_token("color.primary.500") is token

    def test_get_unbekannter_token_gibt_none(self):
        registry = DesignSystemRegistry()
        assert registry.get_token("nicht.vorhanden") is None

    def test_anzahl_komponenten(self):
        registry = _registry_mit_komponenten()
        assert registry.anzahl_komponenten == 5

    def test_anzahl_tokens(self):
        registry = DesignSystemRegistry()
        registry.register_token(_token("t1", TokenTyp.FARBE))
        registry.register_token(_token("t2", TokenTyp.ABSTAND))
        assert registry.anzahl_tokens == 2

    def test_komponenten_nach_kategorie(self):
        registry = _registry_mit_komponenten()
        eingabe = registry.komponenten_nach_kategorie(KomponentenKategorie.EINGABE)
        assert len(eingabe) == 2
        assert all(k.kategorie == KomponentenKategorie.EINGABE for k in eingabe)

    def test_stabile_komponenten(self):
        registry = DesignSystemRegistry()
        registry.register_komponente(KomponentenKontrakt(
            "Stabil", KomponentenKategorie.EINGABE, KomponentenStatus.STABIL, "x.tsx",
        ))
        registry.register_komponente(KomponentenKontrakt(
            "Beta", KomponentenKategorie.EINGABE, KomponentenStatus.BETA, "y.tsx",
        ))
        stabil = registry.stabile_komponenten()
        assert len(stabil) == 1
        assert stabil[0].name == "Stabil"

    def test_deprecated_komponenten(self):
        registry = DesignSystemRegistry()
        registry.register_komponente(KomponentenKontrakt(
            "Alt", KomponentenKategorie.EINGABE, KomponentenStatus.DEPRECATED, "alt.tsx",
        ))
        registry.register_komponente(KomponentenKontrakt(
            "Neu", KomponentenKategorie.EINGABE, KomponentenStatus.STABIL, "neu.tsx",
        ))
        deprecated = registry.deprecated_komponenten()
        assert len(deprecated) == 1
        assert deprecated[0].name == "Alt"

    def test_register_ueberschreibt_vorherigen(self):
        registry = DesignSystemRegistry()
        k1 = KomponentenKontrakt("Button", KomponentenKategorie.EINGABE, KomponentenStatus.BETA, "v1.tsx")
        k2 = KomponentenKontrakt("Button", KomponentenKategorie.EINGABE, KomponentenStatus.STABIL, "v2.tsx")
        registry.register_komponente(k1)
        registry.register_komponente(k2)
        assert registry.get_komponente("Button").status == KomponentenStatus.STABIL
        assert registry.anzahl_komponenten == 1


# ---------------------------------------------------------------------------
# TestValidatePageUsesDsComponents
# ---------------------------------------------------------------------------

class TestValidatePageUsesDsComponents:
    def test_100_pct_compliance(self):
        registry = _registry_mit_komponenten()
        result = validate_page_uses_ds_components(
            "TestSeite",
            ["Button", "ObjectPage"],
            registry,
        )
        assert result.compliance_pct == 100.0
        assert result.kpi_erfuellt is True
        assert len(result.fremde_komponenten) == 0

    def test_0_pct_compliance(self):
        registry = _registry_mit_komponenten()
        result = validate_page_uses_ds_components(
            "TestSeite",
            ["CustomCard", "FremdesWidget"],
            registry,
        )
        assert result.compliance_pct == 0.0
        assert result.kpi_erfuellt is False
        assert len(result.fremde_komponenten) == 2

    def test_partial_compliance(self):
        registry = _registry_mit_komponenten()
        result = validate_page_uses_ds_components(
            "MischSeite",
            ["Button", "FremdesWidget"],
            registry,
        )
        assert result.compliance_pct == 50.0
        assert result.kpi_erfuellt is False

    def test_leere_komponenten_liste_ergibt_100(self):
        registry = _registry_mit_komponenten()
        result = validate_page_uses_ds_components("Leer", [], registry)
        assert result.compliance_pct == 100.0
        assert result.kpi_erfuellt is True

    def test_empfehlungen_bei_fremden_komponenten(self):
        registry = _registry_mit_komponenten()
        result = validate_page_uses_ds_components(
            "TestSeite",
            ["CustomButton"],   # ähnlich wie "Button" im DS
            registry,
        )
        assert len(result.empfehlungen) > 0

    def test_empfehlung_fuer_unbekannte_komponente(self):
        registry = _registry_mit_komponenten()
        result = validate_page_uses_ds_components(
            "TestSeite",
            ["ZZZVölligUnbekannt"],
            registry,
        )
        assert any("nicht im DS" in e or "registrieren" in e for e in result.empfehlungen)

    def test_as_dict_vollstaendig(self):
        registry = _registry_mit_komponenten()
        result = validate_page_uses_ds_components("X", ["Button"], registry)
        d = result.as_dict()
        assert "seiten_name" in d
        assert "compliance_pct" in d
        assert "kpi_erfuellt" in d
        assert "ds_komponenten" in d
        assert "fremde_komponenten" in d

    def test_ds_komponenten_sind_sortiert(self):
        registry = _registry_mit_komponenten()
        result = validate_page_uses_ds_components(
            "X", ["ObjectPage", "Button", "Input"], registry,
        )
        assert result.ds_komponenten == sorted(result.ds_komponenten)


# ---------------------------------------------------------------------------
# TestDSComplianceResult
# ---------------------------------------------------------------------------

class TestDSComplianceResult:
    def test_kpi_erfuellt_wenn_keine_fremden(self):
        r = DSComplianceResult(
            seiten_name="X",
            verwendete_komponenten=["Button"],
            ds_komponenten=["Button"],
            fremde_komponenten=[],
            compliance_pct=100.0,
            kpi_erfuellt=True,
        )
        assert r.kpi_erfuellt is True

    def test_kpi_nicht_erfuellt_wenn_fremde_vorhanden(self):
        r = DSComplianceResult(
            seiten_name="X",
            verwendete_komponenten=["Button", "Fremd"],
            ds_komponenten=["Button"],
            fremde_komponenten=["Fremd"],
            compliance_pct=50.0,
            kpi_erfuellt=False,
        )
        assert r.kpi_erfuellt is False


# ---------------------------------------------------------------------------
# TestGetValeoDesignSystem
# ---------------------------------------------------------------------------

class TestGetValeoDesignSystem:
    def test_registry_nicht_leer(self):
        registry = get_valeo_design_system()
        assert registry.anzahl_komponenten > 0
        assert registry.anzahl_tokens > 0

    def test_muster_komponenten_vorhanden(self):
        registry = get_valeo_design_system()
        for name in ["ObjectPage", "ListReport", "Wizard", "Worklist", "OverviewPage"]:
            assert registry.get_komponente(name) is not None, f"{name} fehlt in DS"

    def test_feedback_komponenten_vorhanden(self):
        registry = get_valeo_design_system()
        assert registry.get_komponente("InlineValidationMessage") is not None
        assert registry.get_komponente("ErrorPanel") is not None

    def test_policy_komponente_vorhanden(self):
        registry = get_valeo_design_system()
        assert registry.get_komponente("PolicyExplanationBadge") is not None

    def test_touch_komponenten_vorhanden(self):
        registry = get_valeo_design_system()
        for name in ["TouchCard", "TouchNumericInput", "TouchSubmitButton", "TouchConfirmCard"]:
            assert registry.get_komponente(name) is not None, f"{name} fehlt in DS"

    def test_keyboard_komponente_vorhanden(self):
        registry = get_valeo_design_system()
        assert registry.get_komponente("KeyboardShortcutBar") is not None

    def test_ui_primitives_vorhanden(self):
        registry = get_valeo_design_system()
        for name in ["Button", "Input", "Label", "Card", "Tabs", "Dialog"]:
            assert registry.get_komponente(name) is not None, f"{name} fehlt in DS"

    def test_farb_tokens_vorhanden(self):
        registry = get_valeo_design_system()
        for name in ["color.primary.500", "color.success.500", "color.warning.500", "color.danger.500"]:
            assert registry.get_token(name) is not None, f"Token {name} fehlt"

    def test_spacing_tokens_vorhanden(self):
        registry = get_valeo_design_system()
        assert registry.get_token("spacing.touch.min") is not None
        assert registry.get_token("spacing.touch.large") is not None

    def test_alle_muster_sind_stabil(self):
        registry = get_valeo_design_system()
        muster = registry.komponenten_nach_kategorie(KomponentenKategorie.MUSTER)
        assert len(muster) > 0
        assert all(k.status == KomponentenStatus.STABIL for k in muster)

    def test_muster_haben_pflicht_props(self):
        registry = get_valeo_design_system()
        object_page = registry.get_komponente("ObjectPage")
        assert "config" in object_page.pflicht_props

    def test_wcag_regeln_gesetzt(self):
        registry = get_valeo_design_system()
        ivm = registry.get_komponente("InlineValidationMessage")
        assert len(ivm.wcag_regeln) > 0
        assert any("alert" in r.lower() for r in ivm.wcag_regeln)

    def test_touch_min_hoehe_token(self):
        registry = get_valeo_design_system()
        token = registry.get_token("spacing.touch.min")
        assert token.wert == "44px"
        assert "44px" in token.tailwind_klasse


# ---------------------------------------------------------------------------
# TestIntegrationSzenario
# ---------------------------------------------------------------------------

class TestIntegrationSzenario:
    def test_neue_seite_mit_ds_komponenten_ist_compliant(self):
        """Neue Seite die ausschließlich DS-Komponenten nutzt → KPI erfüllt."""
        registry = get_valeo_design_system()
        result = validate_page_uses_ds_components(
            "neue_seite_rechnungseingang",
            ["ObjectPage", "Button", "Input", "InlineValidationMessage", "ErrorPanel"],
            registry,
        )
        assert result.kpi_erfuellt is True
        assert result.compliance_pct == 100.0

    def test_seite_mit_fremden_komponenten_nicht_compliant(self):
        """Seite mit eigenen Nicht-DS-Komponenten verletzt das KPI."""
        registry = get_valeo_design_system()
        result = validate_page_uses_ds_components(
            "alte_seite_custom_table",
            ["ObjectPage", "CustomTable", "FremdesFilter"],
            registry,
        )
        assert result.kpi_erfuellt is False
        assert len(result.fremde_komponenten) == 2

    def test_compliance_check_mit_allen_waves(self):
        """Komponenten aus allen Waves (76-84) können zusammen geprüft werden."""
        registry = get_valeo_design_system()
        komponenten = [
            "TouchCard",             # Wave 76
            "KeyboardShortcutBar",   # Wave 77
            "ObjectPage",            # Wave 77
            "InlineValidationMessage",  # Wave 79
            "ErrorPanel",            # Wave 80
            "PolicyExplanationBadge",  # Wave 81
        ]
        result = validate_page_uses_ds_components("VollständigeSeite", komponenten, registry)
        assert result.kpi_erfuellt is True

    def test_registry_ist_deterministisch(self):
        """get_valeo_design_system() liefert immer denselben Stand."""
        r1 = get_valeo_design_system()
        r2 = get_valeo_design_system()
        assert r1.anzahl_komponenten == r2.anzahl_komponenten
        assert r1.anzahl_tokens == r2.anzahl_tokens

    def test_design_token_tailwind_abdeckung(self):
        """Alle Tokens haben eine Tailwind-Klasse für CSS-freies Theming."""
        registry = get_valeo_design_system()
        tokens_ohne_tw = [t for t in registry.tokens.values() if not t.tailwind_klasse]
        assert len(tokens_ohne_tw) == 0, f"Tokens ohne Tailwind-Klasse: {[t.name for t in tokens_ohne_tw]}"
