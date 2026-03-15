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
from typing import Any

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

    def as_dict(self) -> dict[str, Any]:
        return {
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

    def as_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command_bezeichnung": self.command_bezeichnung,
            "typ": self.typ.value,
            "grund": self.grund,
            "prioritaet": self.prioritaet.value,
            "ist_sichtbar": self.typ == SurfacingErgebnisTyp.SICHTBAR,
        }


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
# Standard-Surfacing-Regeln (12 Regeln)
# ---------------------------------------------------------------------------

def get_default_surfacing_regeln() -> list[SurfacingRegel]:
    """Gibt 12 Standard-Surfacing-Regeln zurück."""
    _ALLE_TOOLBAR = [
        SurfacingKontext.TOOLBAR_PRIMARY,
        SurfacingKontext.TOOLBAR_OVERFLOW,
        SurfacingKontext.COMMAND_PALETTE,
    ]
    _ALLE_KANAELE = list(SurfacingKontext)

    return [
        # ── Agrar ────────────────────────────────────────────────────────────
        SurfacingRegel(
            "SR-001", "CMD_ANNAHME_ERFASSEN", "Annahme erfassen",
            erlaubte_rollen=["sachbearbeiter", "leiter", "admin"],
            min_dichte=DichteStufe.FOKUSSIERT,
            sichtbar_in=_ALLE_TOOLBAR,
            prioritaet=CommandPrioritaet.KRITISCH,
            domain="agrar",
            erklaerung="Kernprozess-Einstiegspunkt, immer sichtbar",
        ),
        SurfacingRegel(
            "SR-002", "CMD_QUALITAET_PRUEFUNG", "Qualitätsprüfung starten",
            erlaubte_rollen=["sachbearbeiter", "leiter", "admin"],
            min_dichte=DichteStufe.STANDARD,
            sichtbar_in=_ALLE_TOOLBAR,
            prioritaet=CommandPrioritaet.HOCH,
            domain="agrar",
        ),
        SurfacingRegel(
            "SR-003", "CMD_SETTLEMENT_BERECHNEN", "Settlement berechnen",
            erlaubte_rollen=["buchhaltung", "leiter", "admin"],
            min_dichte=DichteStufe.STANDARD,
            sichtbar_in=[SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.AGENT],
            prioritaet=CommandPrioritaet.HOCH,
            domain="agrar",
        ),
        SurfacingRegel(
            "SR-004", "CMD_KONTRAKT_TEILMENGE", "Teilmengen-Kontrakt anlegen",
            erlaubte_rollen=["sachbearbeiter", "leiter", "admin"],
            min_dichte=DichteStufe.VERDICHTET,
            sichtbar_in=[SurfacingKontext.TOOLBAR_OVERFLOW, SurfacingKontext.COMMAND_PALETTE],
            prioritaet=CommandPrioritaet.MITTEL,
            domain="agrar",
        ),
        # ── Finance ──────────────────────────────────────────────────────────
        SurfacingRegel(
            "SR-005", "CMD_ZAHLUNGSLAUF_FREIGEBEN", "Zahlungslauf freigeben",
            erlaubte_rollen=["leiter", "admin"],
            min_dichte=DichteStufe.FOKUSSIERT,
            sichtbar_in=_ALLE_TOOLBAR,
            prioritaet=CommandPrioritaet.KRITISCH,
            domain="finance",
            erklaerung="4-Augen-Freigabe, immer sichtbar für Leiter",
        ),
        SurfacingRegel(
            "SR-006", "CMD_AP_INVOICE_FREIGEBEN", "Eingangsrechnung freigeben",
            erlaubte_rollen=["buchhaltung", "leiter", "admin"],
            min_dichte=DichteStufe.STANDARD,
            sichtbar_in=[SurfacingKontext.TOOLBAR_PRIMARY, SurfacingKontext.COMMAND_PALETTE],
            prioritaet=CommandPrioritaet.HOCH,
            domain="finance",
        ),
        SurfacingRegel(
            "SR-007", "CMD_BUCHUNG_STORNIEREN", "Buchung stornieren",
            erlaubte_rollen=["buchhaltung", "admin"],
            min_dichte=DichteStufe.VERDICHTET,
            sichtbar_in=[SurfacingKontext.TOOLBAR_OVERFLOW, SurfacingKontext.COMMAND_PALETTE],
            prioritaet=CommandPrioritaet.MITTEL,
            domain="finance",
        ),
        # ── Compliance ────────────────────────────────────────────────────────
        SurfacingRegel(
            "SR-008", "CMD_COMPLIANCE_PRUEFEN", "Compliance prüfen",
            erlaubte_rollen=[],  # alle Rollen
            min_dichte=DichteStufe.STANDARD,
            sichtbar_in=[SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.AGENT],
            prioritaet=CommandPrioritaet.MITTEL,
            domain="compliance",
        ),
        # ── Global ────────────────────────────────────────────────────────────
        SurfacingRegel(
            "SR-009", "CMD_BENACHRICHTIGUNG_SENDEN", "Benachrichtigung senden",
            erlaubte_rollen=["sachbearbeiter", "buchhaltung", "leiter", "admin"],
            min_dichte=DichteStufe.VERDICHTET,
            sichtbar_in=[SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.AGENT],
            prioritaet=CommandPrioritaet.NIEDRIG,
            domain="",
        ),
        SurfacingRegel(
            "SR-010", "CMD_REPORT_GENERIEREN", "Report generieren",
            erlaubte_rollen=["leiter", "admin"],
            min_dichte=DichteStufe.STANDARD,
            sichtbar_in=[SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.AGENT, SurfacingKontext.SHORTCUT],
            prioritaet=CommandPrioritaet.MITTEL,
            domain="",
        ),
        SurfacingRegel(
            "SR-011", "CMD_SHORTCUT_SUCHE", "Schnellsuche",
            erlaubte_rollen=[],  # alle
            min_dichte=DichteStufe.FOKUSSIERT,
            sichtbar_in=_ALLE_KANAELE,
            prioritaet=CommandPrioritaet.KRITISCH,
            domain="",
            erklaerung="Globale Suche, immer und überall verfügbar",
        ),
        SurfacingRegel(
            "SR-012", "CMD_AGENT_AUFTRAG", "Agent-Auftrag erteilen",
            erlaubte_rollen=["leiter", "admin"],
            min_dichte=DichteStufe.VERDICHTET,
            sichtbar_in=[SurfacingKontext.COMMAND_PALETTE, SurfacingKontext.AGENT],
            prioritaet=CommandPrioritaet.NIEDRIG,
            domain="",
        ),
    ]
