"""
Command-Surfacing-Contracts — Wave 39
Rollen- und dichtebewusste Sichtbarkeitsregeln für Business-Commands
in Toolbar, Command-Palette, Kontextmenü, Voice und Agent-Kanälen.

Verbindet den Command-Katalog (Wave 14) mit dem Role-Density-System (Wave 27)
und dem Action-Dispatch-Contract (Wave 25).

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from app.core.business_commands import CommandDefinition, build_core_command_catalog

# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class SurfacingKontext(str, Enum):
    TOOLBAR_PRIMARY = "TOOLBAR_PRIMARY"
    TOOLBAR_OVERFLOW = "TOOLBAR_OVERFLOW"
    COMMAND_PALETTE = "COMMAND_PALETTE"
    KONTEXTMENUE = "KONTEXTMENUE"
    VOICE = "VOICE"
    SHORTCUT = "SHORTCUT"
    AGENT = "AGENT"


class DichteStufe(str, Enum):
    FOKUSSIERT = "FOKUSSIERT"       # Minimale Informationsdichte (neue/ungeübte User)
    STANDARD = "STANDARD"           # Standarddichte
    VERDICHTET = "VERDICHTET"       # Maximale Dichte (Power User, Leiter)


class SurfacingErgebnisTyp(str, Enum):
    SICHTBAR = "SICHTBAR"
    AUSGEBLENDET = "AUSGEBLENDET"
    BERECHTIGUNGS_GESPERRT = "BERECHTIGUNGS_GESPERRT"
    KONTEXT_NICHT_VERFUEGBAR = "KONTEXT_NICHT_VERFUEGBAR"


class CommandPrioritaet(str, Enum):
    KRITISCH = "KRITISCH"   # Immer sichtbar (unabhängig von Dichte)
    HOCH = "HOCH"           # Sichtbar ab STANDARD
    MITTEL = "MITTEL"       # Sichtbar ab VERDICHTET
    NIEDRIG = "NIEDRIG"     # Nur in Command-Palette / Agent


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SurfacingRegel:
    """Definiert wo und für wen ein Command sichtbar ist."""
    regel_id: str
    command_id: str
    command_bezeichnung: str
    erlaubte_rollen: list[str]          # [] = alle Rollen
    min_dichte: DichteStufe
    sichtbar_in: list[SurfacingKontext]
    prioritaet: CommandPrioritaet
    domain: str = ""                     # "agrar", "finance", "" = global
    erklaerung: str = ""                 # Warum sichtbar/nicht-sichtbar
    explainability_hint: Optional[str] = None        # Hinweis für Explainability-System
    authorization_hint: Optional[str] = None         # Hinweis für Autorisierungssystem

    def as_dict(self) -> dict[str, Any]:
        result = {
            "regel_id": self.regel_id,
            "command_id": self.command_id,
            "command_bezeichnung": self.command_bezeichnung,
            "erlaubte_rollen": self.erlaubte_rollen,
            "min_dichte": self.min_dichte.value,
            "sichtbar_in": [k.value for k in self.sichtbar_in],
            "prioritaet": self.prioritaet.value,
            "domain": self.domain,
            "erklaerung": self.erklaerung,
        }
        if self.explainability_hint is not None:
            result["explainability_hint"] = self.explainability_hint
        if self.authorization_hint is not None:
            result["authorization_hint"] = self.authorization_hint
        return result


@dataclass
class SurfacingAnfrage:
    """Anfrage: Welche Commands soll ich für diesen User/Kontext zeigen?"""
    rolle: str
    dichte: DichteStufe
    kontext: SurfacingKontext
    domain: str = ""          # "" = alle Domains
    command_id: str = ""      # "" = alle Commands


@dataclass
class SurfacingErgebnis:
    """Ergebnis für einen einzelnen Command + Kontext."""
    command_id: str
    command_bezeichnung: str
    typ: SurfacingErgebnisTyp
    grund: str = ""
    prioritaet: CommandPrioritaet = CommandPrioritaet.MITTEL
    explainability_hint: Optional[str] = None
    authorization_hint: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        result = {
            "command_id": self.command_id,
            "command_bezeichnung": self.command_bezeichnung,
            "typ": self.typ.value,
            "grund": self.grund,
            "prioritaet": self.prioritaet.value,
            "ist_sichtbar": self.typ == SurfacingErgebnisTyp.SICHTBAR,
        }
        if self.explainability_hint is not None:
            result["explainability_hint"] = self.explainability_hint
        if self.authorization_hint is not None:
            result["authorization_hint"] = self.authorization_hint
        return result


@dataclass
class CommandSurfacingManifest:
    """Vollständiges Manifest: alle sichtbaren Commands für eine Anfrage."""
    anfrage: SurfacingAnfrage
    sichtbare_commands: list[SurfacingErgebnis]
    ausgeblendete_commands: list[SurfacingErgebnis]
    gesperrte_commands: list[SurfacingErgebnis]

    @property
    def anzahl_sichtbar(self) -> int:
        return len(self.sichtbare_commands)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rolle": self.anfrage.rolle,
            "dichte": self.anfrage.dichte.value,
            "kontext": self.anfrage.kontext.value,
            "domain": self.anfrage.domain,
            "anzahl_sichtbar": self.anzahl_sichtbar,
            "sichtbare_commands": [c.as_dict() for c in self.sichtbare_commands],
            "ausgeblendete_commands": [c.as_dict() for c in self.ausgeblendete_commands],
            "gesperrte_commands": [c.as_dict() for c in self.gesperrte_commands],
        }


# ---------------------------------------------------------------------------
# Surfacing-Logik
# ---------------------------------------------------------------------------

# Dichte-Rangordnung: FOKUSSIERT < STANDARD < VERDICHTET
_DICHTE_RANG: dict[DichteStufe, int] = {
    DichteStufe.FOKUSSIERT: 0,
    DichteStufe.STANDARD: 1,
    DichteStufe.VERDICHTET: 2,
}


def berechne_surfacing(
    anfrage: SurfacingAnfrage,
    regeln: list[SurfacingRegel] | None = None,
) -> CommandSurfacingManifest:
    """
    Berechnet das Command-Surfacing-Manifest für eine Anfrage.

    Regeln:
    1. Domain-Filter: Regel gilt wenn domain=="" oder domain==anfrage.domain
    2. Rollen-Check: Regel gilt wenn erlaubte_rollen==[] oder rolle in erlaubte_rollen
    3. Dichte-Check: user_dichte >= regel.min_dichte (nach _DICHTE_RANG)
    4. Kontext-Check: kontext in regel.sichtbar_in
    5. KRITISCH-Commands sind immer sichtbar (übersteuern Dichte)
    """
    if regeln is None:
        regeln = get_default_surfacing_regeln()

    sichtbar: list[SurfacingErgebnis] = []
    ausgeblendet: list[SurfacingErgebnis] = []
    gesperrt: list[SurfacingErgebnis] = []

    user_dichte_rang = _DICHTE_RANG[anfrage.dichte]

    for regel in regeln:
        # Optionaler Command-Filter
        if anfrage.command_id and regel.command_id != anfrage.command_id:
            continue

        # Domain-Filter
        if regel.domain and anfrage.domain and regel.domain != anfrage.domain:
            continue

        # Rollen-Check
        rolle_ok = (not regel.erlaubte_rollen) or (anfrage.rolle in regel.erlaubte_rollen)
        if not rolle_ok:
            gesperrt.append(SurfacingErgebnis(
                command_id=regel.command_id,
                command_bezeichnung=regel.command_bezeichnung,
                typ=SurfacingErgebnisTyp.BERECHTIGUNGS_GESPERRT,
                grund=f"Rolle '{anfrage.rolle}' nicht in {regel.erlaubte_rollen}",
                prioritaet=regel.prioritaet,
            ))
            continue

        # Kontext-Check
        if anfrage.kontext not in regel.sichtbar_in:
            ausgeblendet.append(SurfacingErgebnis(
                command_id=regel.command_id,
                command_bezeichnung=regel.command_bezeichnung,
                typ=SurfacingErgebnisTyp.KONTEXT_NICHT_VERFUEGBAR,
                grund=f"Kontext '{anfrage.kontext.value}' nicht in {[k.value for k in regel.sichtbar_in]}",
                prioritaet=regel.prioritaet,
            ))
            continue

        # Dichte-Check (KRITISCH übersteuert)
        dichte_ok = (
            regel.prioritaet == CommandPrioritaet.KRITISCH
            or user_dichte_rang >= _DICHTE_RANG[regel.min_dichte]
        )
        if not dichte_ok:
            ausgeblendet.append(SurfacingErgebnis(
                command_id=regel.command_id,
                command_bezeichnung=regel.command_bezeichnung,
                typ=SurfacingErgebnisTyp.AUSGEBLENDET,
                grund=f"Dichte '{anfrage.dichte.value}' unter Minimum '{regel.min_dichte.value}'",
                prioritaet=regel.prioritaet,
            ))
            continue

        sichtbar.append(SurfacingErgebnis(
            command_id=regel.command_id,
            command_bezeichnung=regel.command_bezeichnung,
            typ=SurfacingErgebnisTyp.SICHTBAR,
            grund=regel.erklaerung,
            prioritaet=regel.prioritaet,
            explainability_hint=regel.explainability_hint,
            authorization_hint=regel.authorization_hint,
        ))

    # Sichtbare Commands nach Priorität sortieren (KRITISCH zuerst)
    _PRIO_RANG = {
        CommandPrioritaet.KRITISCH: 3,
        CommandPrioritaet.HOCH: 2,
        CommandPrioritaet.MITTEL: 1,
        CommandPrioritaet.NIEDRIG: 0,
    }
    sichtbar.sort(key=lambda c: _PRIO_RANG[c.prioritaet], reverse=True)

    return CommandSurfacingManifest(
        anfrage=anfrage,
        sichtbare_commands=sichtbar,
        ausgeblendete_commands=ausgeblendet,
        gesperrte_commands=gesperrt,
    )


# ---------------------------------------------------------------------------
# Produktive Backend-Manifeste für Surfacing-Regeln
# ---------------------------------------------------------------------------

def _build_surfacing_rules_from_command_definition(definition: CommandDefinition) -> list[SurfacingRegel]:
    """Build surfacing rules from a single command definition."""
    rules = []
    
    # Map command properties to surfacing rule properties
    # Determine appropriate surfaces based on command properties
    surfaces = [SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.COMMAND_PALETTE]
    # Add AGENT surface for commands that can be executed by agents
    if definition.allowed_agent_types and len(definition.allowed_agent_types) > 0:
        surfaces.append(SurfacingKontext.AGENT)
    # Add VOICE surface for commands with voice intent (simplified heuristic)
    if definition.command_name and any(keyword in definition.command_name.lower() for keyword in ['approve', 'reject', 'create', 'send']):
        surfaces.append(SurfacingKontext.VOICE)
    
    # Determine density based on command properties
    min_dichte = DichteStufe.FOKUSSIERT
    # Commands requiring human confirmation or explainability need at least standard density
    if definition.requires_human_confirmation:
        min_dichte = DichteStufe.STANDARD
    # Commands with many allowed roles or agent types need higher density
    if len(definition.allowed_roles) > 3 or len(definition.allowed_agent_types) > 1:
        min_dichte = DichteStufe.VERDICHTET
    # Commands with preconditions are more complex
    if len(definition.preconditions) > 2:
        min_dichte = DichteStufe.VERDICHTET
    
    # Determine priority based on command properties
    prioritaet = CommandPrioritaet.MITTEL
    # Critical: financial approvals, rejections, system commands
    if any(keyword in definition.command_name.lower() for keyword in ['approve', 'reject', 'execute', 'process']):
        prioritaet = CommandPrioritaet.KRITISCH
    # High: creation, sending, important business operations
    elif any(keyword in definition.command_name.lower() for keyword in ['create', 'send', 'generate', 'calculate']):
        prioritaet = CommandPrioritaet.HOCH
    # Low: queries, reports, informational commands
    elif any(keyword in definition.command_name.lower() for keyword in ['get', 'list', 'query', 'report', 'view']):
        prioritaet = CommandPrioritaet.NIEDRIG
    
    # Build explainability and authorization hints
    explainability_hint = None
    authorization_hint = None
    
    if definition.requires_human_confirmation:
        authorization_hint = "Dieser Befehl erfordert menschliche Bestätigung"
        explainability_hint = "Ausführungsgrund muss dokumentiert werden für Audit-Zwecke"
    
    # Build the rule
    rule = SurfacingRegel(
        regel_id=f"SR_CMD_{definition.command_name}",
        command_id=definition.command_name,
        command_bezeichnung=definition.command_name,  # Using command_name as label for now
        erlaubte_rollen=definition.allowed_roles,
        min_dichte=min_dichte,
        sichtbar_in=surfaces,
        prioritaet=prioritaet,
        domain=definition.aggregate_type,  # Using aggregate_type as domain
        erklaerung=f"Automatisch generiert aus Command-Definition: {definition.command_name}",
        explainability_hint=explainability_hint,
        authorization_hint=authorization_hint
    )
    rules.append(rule)
    
    return rules


def _build_surfacing_rules_from_policy_entries() -> list[SurfacingRegel]:
    """Build surfacing rules from policy contract entries."""
    # Placeholder for policy-based surfacing rules
    # In a full implementation, this would analyze policy contracts
    # to generate appropriate surfacing rules
    return []


def _build_surfacing_rules_from_approval_entries() -> list[SurfacingRegel]:
    """Build surfacing rules from approval contract entries."""
    # Placeholder for approval-based surfacing rules
    # In a full implementation, this would analyze approval contracts
    # to generate appropriate surfacing rules
    return []


def build_surfacing_rules(
    catalog: list[CommandDefinition] | None = None,
) -> list[SurfacingRegel]:
    """
    Build command surfacing rules from productive backend manifests.
    
    Similar to build_ui_density_manifest, this function creates surfacing rules
    from command definitions, policy contracts, and approval contracts.
    """
    definitions = catalog or build_core_command_catalog()
    
    rules: list[SurfacingRegel] = []
    
    # Build rules from command definitions
    for definition in definitions:
        rules.extend(_build_surfacing_rules_from_command_definition(definition))
    
    # Build rules from policy entries
    rules.extend(_build_surfacing_rules_from_policy_entries())
    
    # Build rules from approval entries
    rules.extend(_build_surfacing_rules_from_approval_entries())
    
    return rules


_DEFAULT_SURFACING_REGELN: list[SurfacingRegel] = [
    # SR-001 — Annahme erfassen (Agrar, KRITISCH)
    SurfacingRegel(
        regel_id="SR-001",
        command_id="CMD_ANNAHME_ERFASSEN",
        command_bezeichnung="Annahme erfassen",
        erlaubte_rollen=["sachbearbeiter", "leiter", "admin"],
        min_dichte=DichteStufe.FOKUSSIERT,
        sichtbar_in=[SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.AGENT],
        prioritaet=CommandPrioritaet.KRITISCH,
        domain="agrar",
    ),
    # SR-002 — Qualitätsprüfung (Agrar, HOCH, ab STANDARD)
    SurfacingRegel(
        regel_id="SR-002",
        command_id="CMD_QUALITAET_PRUEFUNG",
        command_bezeichnung="Qualitätsprüfung durchführen",
        erlaubte_rollen=["sachbearbeiter", "leiter", "admin"],
        min_dichte=DichteStufe.STANDARD,
        sichtbar_in=[SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.COMMAND_PALETTE],
        prioritaet=CommandPrioritaet.HOCH,
        domain="agrar",
    ),
    # SR-003 — Settlement berechnen (Agrar, MITTEL, kein TOOLBAR_OVERFLOW)
    SurfacingRegel(
        regel_id="SR-003",
        command_id="CMD_SETTLEMENT_BERECHNEN",
        command_bezeichnung="Settlement berechnen",
        erlaubte_rollen=[],
        min_dichte=DichteStufe.FOKUSSIERT,
        sichtbar_in=[SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.AGENT],
        prioritaet=CommandPrioritaet.MITTEL,
        domain="agrar",
    ),
    # SR-004 — Vertrag anlegen (Agrar, HOCH)
    SurfacingRegel(
        regel_id="SR-004",
        command_id="CMD_VERTRAG_ANLEGEN",
        command_bezeichnung="Vertrag anlegen",
        erlaubte_rollen=["sachbearbeiter", "leiter", "admin"],
        min_dichte=DichteStufe.STANDARD,
        sichtbar_in=[SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.COMMAND_PALETTE],
        prioritaet=CommandPrioritaet.HOCH,
        domain="agrar",
    ),
    # SR-005 — Zahlungslauf freigeben (Finance, KRITISCH)
    SurfacingRegel(
        regel_id="SR-005",
        command_id="CMD_ZAHLUNGSLAUF_FREIGEBEN",
        command_bezeichnung="Zahlungslauf freigeben",
        erlaubte_rollen=["leiter", "admin", "buchhaltung"],
        min_dichte=DichteStufe.FOKUSSIERT,
        sichtbar_in=[SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.COMMAND_PALETTE],
        prioritaet=CommandPrioritaet.KRITISCH,
        domain="finance",
    ),
    # SR-006 — Rechnung prüfen (Finance, HOCH)
    SurfacingRegel(
        regel_id="SR-006",
        command_id="CMD_RECHNUNG_PRUEFEN",
        command_bezeichnung="Rechnung prüfen",
        erlaubte_rollen=["buchhaltung", "leiter", "admin"],
        min_dichte=DichteStufe.STANDARD,
        sichtbar_in=[SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.COMMAND_PALETTE],
        prioritaet=CommandPrioritaet.HOCH,
        domain="finance",
    ),
    # SR-007 — Mahnlauf starten (Finance, MITTEL, ab VERDICHTET)
    SurfacingRegel(
        regel_id="SR-007",
        command_id="CMD_MAHNLAUF_STARTEN",
        command_bezeichnung="Mahnlauf starten",
        erlaubte_rollen=["buchhaltung", "leiter", "admin"],
        min_dichte=DichteStufe.VERDICHTET,
        sichtbar_in=[SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.KONTEXTMENUE],
        prioritaet=CommandPrioritaet.MITTEL,
        domain="finance",
    ),
    # SR-008 — Skonto optimieren (Finance, HOCH)
    SurfacingRegel(
        regel_id="SR-008",
        command_id="CMD_SKONTO_OPTIMIEREN",
        command_bezeichnung="Skonto optimieren",
        erlaubte_rollen=["buchhaltung", "leiter", "admin"],
        min_dichte=DichteStufe.STANDARD,
        sichtbar_in=[SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.AGENT],
        prioritaet=CommandPrioritaet.HOCH,
        domain="finance",
    ),
    # SR-009 — Compliance prüfen (Agrar, HOCH)
    SurfacingRegel(
        regel_id="SR-009",
        command_id="CMD_COMPLIANCE_PRUEFEN",
        command_bezeichnung="Compliance prüfen",
        erlaubte_rollen=["leiter", "admin"],
        min_dichte=DichteStufe.STANDARD,
        sichtbar_in=[SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.AGENT],
        prioritaet=CommandPrioritaet.HOCH,
        domain="agrar",
    ),
    # SR-010 — Bericht erstellen (Agrar, NIEDRIG, ab VERDICHTET)
    SurfacingRegel(
        regel_id="SR-010",
        command_id="CMD_BERICHT_ERSTELLEN",
        command_bezeichnung="Bericht erstellen",
        erlaubte_rollen=["sachbearbeiter", "leiter", "admin", "buchhaltung"],
        min_dichte=DichteStufe.VERDICHTET,
        sichtbar_in=[SurfacingKontext.COMMAND_PALETTE],
        prioritaet=CommandPrioritaet.NIEDRIG,
        domain="agrar",
    ),
    # SR-011 — Shortcut-Suche (global, alle Rollen, KRITISCH)
    SurfacingRegel(
        regel_id="SR-011",
        command_id="CMD_SHORTCUT_SUCHE",
        command_bezeichnung="Shortcut-Suche öffnen",
        erlaubte_rollen=[],
        min_dichte=DichteStufe.FOKUSSIERT,
        sichtbar_in=[SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.SHORTCUT],
        prioritaet=CommandPrioritaet.KRITISCH,
        domain="",
    ),
    # SR-012 — Hilfe anzeigen (global, alle Rollen, NIEDRIG)
    SurfacingRegel(
        regel_id="SR-012",
        command_id="CMD_HILFE_ANZEIGEN",
        command_bezeichnung="Hilfe anzeigen",
        erlaubte_rollen=[],
        min_dichte=DichteStufe.FOKUSSIERT,
        sichtbar_in=[SurfacingKontext.TOOLBAR_OVERFLOW, SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.VOICE],
        prioritaet=CommandPrioritaet.NIEDRIG,
        domain="",
    ),
]


def get_default_surfacing_regeln() -> list[SurfacingRegel]:
    """Gibt die 12 Standard-Surfacing-Regeln zurück (Process-Kernel-Kontrakt Wave 39)."""
    return list(_DEFAULT_SURFACING_REGELN)
