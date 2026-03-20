"""
design_system_contracts.py — Einheitliches Designsystem (Wave 84, Gap 021)

Verbindlicher Komponentenkatalog und Design-Token-Registry für VALEO NeuroERP.
Alle neuen Seiten müssen DS-Komponenten verwenden.

Enthält die Komponenten aus Waves 76-83 als registrierte DS-Einträge:
- TouchFieldLayout (Wave 76)
- KeyboardShortcutBar (Wave 77)
- InlineValidationMessage (Wave 79)
- ErrorPanel (Wave 80)
- PolicyExplanationBadge (Wave 81)

Gap 021: Einheitliches Designsystem — KPI: 100% neue Seiten nutzen DS-Komponenten
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class KomponentenKategorie(str, Enum):
    """Kategorie einer DS-Komponente."""
    LAYOUT      = "LAYOUT"       # Strukturgebende Container
    EINGABE     = "EINGABE"      # Input, Select, Textarea
    FEEDBACK    = "FEEDBACK"     # Validierung, Fehler, Loading
    NAVIGATION  = "NAVIGATION"   # Tabs, Breadcrumb, Sidebar
    DATEN       = "DATEN"        # Tabellen, Listen, Cards
    AKTION      = "AKTION"       # Buttons, Toolbar, Quick Actions
    OVERLAY     = "OVERLAY"      # Dialog, Toast, Tooltip
    POLICY      = "POLICY"       # Policy-Entscheidungen, Badges
    MUSTER      = "MUSTER"       # Vollständige ERP-Masken (ObjectPage etc.)


class TokenTyp(str, Enum):
    """Typ eines Design-Tokens."""
    FARBE       = "FARBE"
    ABSTAND     = "ABSTAND"
    SCHRIFT     = "SCHRIFT"
    RADIUS      = "RADIUS"
    SCHATTEN    = "SCHATTEN"
    ANIMATION   = "ANIMATION"


class KomponentenStatus(str, Enum):
    """Reifegrad einer Komponente."""
    STABIL      = "STABIL"      # Produktiv, keine Breaking Changes
    BETA        = "BETA"        # Einsetzbar, kann sich noch ändern
    DEPRECATED  = "DEPRECATED"  # Veraltet, Migration nötig
    EXPERIMENTELL = "EXPERIMENTELL"


# ---------------------------------------------------------------------------
# Design Token
# ---------------------------------------------------------------------------

@dataclass
class DesignToken:
    """
    Atomarer Design-Wert (Farbe, Abstand, Schrift, ...).

    Tokens sind die Basis des DS — Komponenten referenzieren Tokens,
    nicht Rohwerte. Dadurch ist Theme-Switching ohne Code-Umbau möglich.
    """
    name: str               # z.B. "color.primary.500"
    wert: str               # z.B. "#2563eb"
    typ: TokenTyp
    beschreibung: str = ""
    tailwind_klasse: str = ""  # z.B. "bg-blue-600"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "wert": self.wert,
            "typ": self.typ.value,
            "beschreibung": self.beschreibung,
            "tailwind_klasse": self.tailwind_klasse,
        }


# ---------------------------------------------------------------------------
# Komponenten-Kontrakt
# ---------------------------------------------------------------------------

@dataclass
class KomponentenKontrakt:
    """
    Vertrag einer DS-Komponente: Wo liegt sie, welche Props erwartet sie,
    welche Tokens nutzt sie, welche WCAG-Regeln müssen erfüllt sein.
    """
    name: str                           # z.B. "InlineValidationMessage"
    kategorie: KomponentenKategorie
    status: KomponentenStatus
    dateipfad: str                      # Relativ zu packages/frontend-web/src/
    pflicht_props: list[str] = field(default_factory=list)
    optionale_props: list[str] = field(default_factory=list)
    genutzte_tokens: list[str] = field(default_factory=list)  # Token-Namen
    wcag_regeln: list[str] = field(default_factory=list)
    welle: int = 0                      # Wave in der die Komponente geliefert wurde
    beschreibung: str = ""

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "kategorie": self.kategorie.value,
            "status": self.status.value,
            "dateipfad": self.dateipfad,
            "pflicht_props": self.pflicht_props,
            "optionale_props": self.optionale_props,
            "wcag_regeln": self.wcag_regeln,
            "welle": self.welle,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Design System Registry
# ---------------------------------------------------------------------------

@dataclass
class DesignSystemRegistry:
    """
    Zentrales Register aller DS-Komponenten und Design-Tokens.

    Neue Seiten MÜSSEN hier registrierte Komponenten verwenden.
    Der Compliance-Check `validate_page_uses_ds_components()` prüft das.
    """
    komponenten: dict[str, KomponentenKontrakt] = field(default_factory=dict)
    tokens: dict[str, DesignToken] = field(default_factory=dict)

    def register_komponente(self, kontrakt: KomponentenKontrakt) -> None:
        self.komponenten[kontrakt.name] = kontrakt

    def register_token(self, token: DesignToken) -> None:
        self.tokens[token.name] = token

    def get_komponente(self, name: str) -> KomponentenKontrakt | None:
        return self.komponenten.get(name)

    def get_token(self, name: str) -> DesignToken | None:
        return self.tokens.get(name)

    def komponenten_nach_kategorie(self, kategorie: KomponentenKategorie) -> list[KomponentenKontrakt]:
        return [k for k in self.komponenten.values() if k.kategorie == kategorie]

    def stabile_komponenten(self) -> list[KomponentenKontrakt]:
        return [k for k in self.komponenten.values() if k.status == KomponentenStatus.STABIL]

    def deprecated_komponenten(self) -> list[KomponentenKontrakt]:
        return [k for k in self.komponenten.values() if k.status == KomponentenStatus.DEPRECATED]

    @property
    def anzahl_komponenten(self) -> int:
        return len(self.komponenten)

    @property
    def anzahl_tokens(self) -> int:
        return len(self.tokens)


# ---------------------------------------------------------------------------
# DS-Compliance Check
# ---------------------------------------------------------------------------

@dataclass
class DSComplianceResult:
    """Ergebnis des DS-Compliance-Checks für eine neue Seite."""
    seiten_name: str
    verwendete_komponenten: list[str]
    ds_komponenten: list[str]           # Schnittmenge mit Registry
    fremde_komponenten: list[str]       # Nicht im DS
    compliance_pct: float
    kpi_erfuellt: bool                  # >= 100% DS-Komponenten
    empfehlungen: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "seiten_name": self.seiten_name,
            "verwendete_komponenten": self.verwendete_komponenten,
            "ds_komponenten": self.ds_komponenten,
            "fremde_komponenten": self.fremde_komponenten,
            "compliance_pct": self.compliance_pct,
            "kpi_erfuellt": self.kpi_erfuellt,
            "empfehlungen": self.empfehlungen,
        }


def validate_page_uses_ds_components(
    seiten_name: str,
    verwendete_komponenten: list[str],
    registry: DesignSystemRegistry,
) -> DSComplianceResult:
    """
    Prüft ob eine Seite ausschließlich DS-Komponenten verwendet.

    KPI: 100% neue Seiten nutzen DS-Komponenten.
    """
    ds_names = set(registry.komponenten.keys())
    verwendet = set(verwendete_komponenten)

    ds_komponenten = sorted(verwendet & ds_names)
    fremde = sorted(verwendet - ds_names)

    gesamt = len(verwendet)
    compliance = (len(ds_komponenten) / gesamt * 100) if gesamt > 0 else 100.0

    empfehlungen = []
    for fremd in fremde[:3]:
        # Suche ähnliche DS-Komponente
        aehnlich = [k for k in ds_names if fremd.lower()[:4] in k.lower()]
        if aehnlich:
            empfehlungen.append(f"Ersetze '{fremd}' durch '{aehnlich[0]}' aus dem DS.")
        else:
            empfehlungen.append(f"'{fremd}' ist nicht im DS — bitte registrieren oder ersetzen.")

    return DSComplianceResult(
        seiten_name=seiten_name,
        verwendete_komponenten=sorted(verwendet),
        ds_komponenten=ds_komponenten,
        fremde_komponenten=fremde,
        compliance_pct=round(compliance, 1),
        kpi_erfuellt=(len(fremde) == 0),
        empfehlungen=empfehlungen,
    )


# ---------------------------------------------------------------------------
# VALEO DS — Standard-Registry (alle Komponenten aus Waves 76-84)
# ---------------------------------------------------------------------------

def get_valeo_design_system() -> DesignSystemRegistry:
    """
    Liefert die offizielle VALEO DS-Registry mit allen registrierten Komponenten.
    """
    registry = DesignSystemRegistry()

    # --- Tokens ---
    for name, wert, typ, tw in [
        ("color.primary.500",   "#2563eb", TokenTyp.FARBE,    "text-blue-600"),
        ("color.success.500",   "#16a34a", TokenTyp.FARBE,    "text-green-600"),
        ("color.warning.500",   "#d97706", TokenTyp.FARBE,    "text-amber-600"),
        ("color.danger.500",    "#dc2626", TokenTyp.FARBE,    "text-red-600"),
        ("color.neutral.100",   "#f1f5f9", TokenTyp.FARBE,    "bg-slate-100"),
        ("spacing.touch.min",   "44px",    TokenTyp.ABSTAND,  "min-h-[44px]"),
        ("spacing.touch.large", "64px",    TokenTyp.ABSTAND,  "min-h-[64px]"),
        ("radius.md",           "6px",     TokenTyp.RADIUS,   "rounded-md"),
        ("radius.full",         "9999px",  TokenTyp.RADIUS,   "rounded-full"),
        ("font.size.xs",        "12px",    TokenTyp.SCHRIFT,  "text-xs"),
        ("font.size.sm",        "14px",    TokenTyp.SCHRIFT,  "text-sm"),
    ]:
        registry.register_token(DesignToken(name=name, wert=wert, typ=typ, tailwind_klasse=tw))

    # --- Muster-Komponenten (ERP-Masken) ---
    for name, pfad, welle, props in [
        ("ObjectPage",   "components/mask-builder/ObjectPage.tsx",  77, ["config", "onSave", "onCancel"]),
        ("ListReport",   "components/mask-builder/ListReport.tsx",   1,  ["config"]),
        ("Wizard",       "components/mask-builder/Wizard.tsx",       1,  ["config", "onFinish"]),
        ("Worklist",     "components/mask-builder/Worklist.tsx",     1,  ["config"]),
        ("OverviewPage", "components/mask-builder/OverviewPage.tsx", 1,  ["config"]),
    ]:
        registry.register_komponente(KomponentenKontrakt(
            name=name, kategorie=KomponentenKategorie.MUSTER,
            status=KomponentenStatus.STABIL, dateipfad=pfad,
            pflicht_props=props, welle=welle,
            wcag_regeln=["WCAG 2.1 SC 1.3.1", "WCAG 2.1 SC 2.4.3"],
        ))

    # --- Feedback-Komponenten ---
    registry.register_komponente(KomponentenKontrakt(
        name="InlineValidationMessage",
        kategorie=KomponentenKategorie.FEEDBACK,
        status=KomponentenStatus.STABIL,
        dateipfad="components/validation/InlineValidationMessage.tsx",
        pflicht_props=["result"],
        optionale_props=["showSuccessIcon", "className"],
        wcag_regeln=["WCAG 2.1 SC 1.3.3", "role=alert", "aria-live=polite"],
        welle=79,
        beschreibung="Domain-spezifische Inline-Validierungshinweise (GLN, IBAN, Menge, Preis)",
    ))

    registry.register_komponente(KomponentenKontrakt(
        name="ErrorPanel",
        kategorie=KomponentenKategorie.FEEDBACK,
        status=KomponentenStatus.STABIL,
        dateipfad="components/error/ErrorPanel.tsx",
        pflicht_props=["error"],
        optionale_props=["onAction", "compact", "className"],
        wcag_regeln=["role=alert", "aria-live=assertive"],
        welle=80,
        beschreibung="Strukturierte Fehleranzeige mit RecoveryActions (alle HTTP-Fehlercodes)",
    ))

    # --- Policy-Komponenten ---
    registry.register_komponente(KomponentenKontrakt(
        name="PolicyExplanationBadge",
        kategorie=KomponentenKategorie.POLICY,
        status=KomponentenStatus.STABIL,
        dateipfad="components/policy/PolicyExplanationBadge.tsx",
        pflicht_props=["explanation"],
        optionale_props=["showDetails", "className"],
        wcag_regeln=["WCAG 2.1 SC 1.4.1"],
        welle=81,
        beschreibung="Kompakter Badge für Policy-Entscheidungen (Freigegeben/Abgelehnt/Warnung)",
    ))

    # --- Touch-Komponenten ---
    for name, pfad, props in [
        ("TouchCard",         "components/touch/TouchFieldLayout.tsx", ["label", "selected", "onSelect"]),
        ("TouchNumericInput", "components/touch/TouchFieldLayout.tsx", ["value", "onChange"]),
        ("TouchSubmitButton", "components/touch/TouchFieldLayout.tsx", ["label", "onPress"]),
        ("TouchConfirmCard",  "components/touch/TouchFieldLayout.tsx", ["title", "onConfirm"]),
    ]:
        registry.register_komponente(KomponentenKontrakt(
            name=name, kategorie=KomponentenKategorie.EINGABE,
            status=KomponentenStatus.STABIL, dateipfad=pfad,
            pflicht_props=props, welle=76,
            wcag_regeln=["WCAG 2.1 SC 2.5.5 (min 44px touch target)"],
        ))

    # --- Navigation / Keyboard ---
    registry.register_komponente(KomponentenKontrakt(
        name="KeyboardShortcutBar",
        kategorie=KomponentenKategorie.NAVIGATION,
        status=KomponentenStatus.STABIL,
        dateipfad="components/keyboard/KeyboardShortcutBar.tsx",
        pflicht_props=["shortcuts"],
        optionale_props=["maxVisible", "className"],
        wcag_regeln=["role=status", "WCAG 2.1 SC 2.1.1"],
        welle=77,
        beschreibung="Footer-Leiste mit aktiven Keyboard-Shortcuts (nur Desktop, nicht Touch)",
    ))

    # --- Primitives (Radix-based) ---
    for name in ["Button", "Input", "Label", "Card", "Tabs", "Dialog", "NativeSelect", "Textarea"]:
        registry.register_komponente(KomponentenKontrakt(
            name=name, kategorie=KomponentenKategorie.EINGABE,
            status=KomponentenStatus.STABIL,
            dateipfad=f"components/ui/{name.lower()}.tsx",
            welle=1,
        ))

    return registry
