"""
policy_explainability_contracts.py — Policy Explainability im UI (Wave 81, Gap 019)

Erklärt Policy-Entscheidungen in verständlichem Deutsch:
"Warum wurde diese Aktion freigegeben / blockiert / eskaliert?"

Baut auf PolicyEvaluationResult aus policy_code_engine.py auf.

Gap 019: Policy Explainability im UI — KPI: 50% weniger Support-Rückfragen
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.policy_code_engine import PolicyEvaluationResult

from app.core.policy_code_engine import PolicyAktion


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ExplanationVerbosity(str, Enum):
    """Detailgrad der Erklärung."""
    BRIEF    = "BRIEF"    # Einzeiler: "Freigegeben – keine Regel verletzt"
    STANDARD = "STANDARD" # Zusammenfassung + wichtigste Regel
    DETAILED = "DETAILED" # Alle ausgelösten Regeln mit Begründungen


class EntscheidungsErgebnis(str, Enum):
    """Vereinfachtes Ergebnis für die UI-Anzeige."""
    FREIGEGEBEN  = "FREIGEGEBEN"   # ERLAUBT
    ABGELEHNT    = "ABGELEHNT"     # ABGELEHNT
    WARNUNG      = "WARNUNG"       # WARNUNG
    ESKALATION   = "ESKALATION"    # ESKALATION erforderlich
    KEINE_REGEL  = "KEINE_REGEL"   # Keine Regel traf zu → implizit freigegeben


# ---------------------------------------------------------------------------
# Policy Reason Entry
# ---------------------------------------------------------------------------

@dataclass
class PolicyReasonEntry:
    """
    Ein Grund für die Entscheidung (eine ausgelöste Regel).

    ergebnis_text: Lesbare Beschreibung z.B.
        "Regel 'Vier-Augen-Prinzip': Betrag (5.000 €) überschreitet Limit → Eskalation erforderlich"
    """
    regel_id: str
    regel_name: str
    aktion: PolicyAktion
    ergebnis_text: str          # Deutsch, vollständige Erklärung
    ist_entscheidend: bool      # True = diese Regel hat die Endentscheidung bestimmt

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "regel_name": self.regel_name,
            "aktion": self.aktion.value,
            "ergebnis_text": self.ergebnis_text,
            "ist_entscheidend": self.ist_entscheidend,
        }


# ---------------------------------------------------------------------------
# PolicyExplanation
# ---------------------------------------------------------------------------

@dataclass
class PolicyExplanation:
    """
    Vollständige Erklärung einer Policy-Entscheidung für den Benutzer.

    zusammenfassung: Einzeiler für Tooltip/Badge
    gruende:         Detailliste der ausgelösten Regeln
    """
    entscheidung: EntscheidungsErgebnis
    zusammenfassung: str                    # z.B. "Freigegeben – alle 3 Regeln erfüllt"
    gruende: list[PolicyReasonEntry] = field(default_factory=list)
    anzahl_gepruefter_regeln: int = 0
    tenant_override_aktiv: bool = False
    prozess_key: str = ""
    policy_set_id: str = ""
    schema_version: int = 1

    @property
    def ist_freigegeben(self) -> bool:
        return self.entscheidung in {
            EntscheidungsErgebnis.FREIGEGEBEN,
            EntscheidungsErgebnis.KEINE_REGEL,
        }

    @property
    def entscheidende_gruende(self) -> list[PolicyReasonEntry]:
        """Nur die Gründe die die Endentscheidung bestimmt haben."""
        return [g for g in self.gruende if g.ist_entscheidend]

    @property
    def icon(self) -> str:
        """Passendes Icon für die UI."""
        match self.entscheidung:
            case EntscheidungsErgebnis.FREIGEGEBEN | EntscheidungsErgebnis.KEINE_REGEL:
                return "CheckCircle2"
            case EntscheidungsErgebnis.ABGELEHNT:
                return "XCircle"
            case EntscheidungsErgebnis.WARNUNG:
                return "AlertTriangle"
            case EntscheidungsErgebnis.ESKALATION:
                return "ArrowUpCircle"
            case _:
                return "HelpCircle"

    @property
    def badge_farbe(self) -> str:
        """CSS-Farbklasse für Badge."""
        match self.entscheidung:
            case EntscheidungsErgebnis.FREIGEGEBEN | EntscheidungsErgebnis.KEINE_REGEL:
                return "green"
            case EntscheidungsErgebnis.ABGELEHNT:
                return "red"
            case EntscheidungsErgebnis.WARNUNG:
                return "amber"
            case EntscheidungsErgebnis.ESKALATION:
                return "orange"
            case _:
                return "slate"

    def as_dict(self) -> dict:
        return {
            "entscheidung": self.entscheidung.value,
            "zusammenfassung": self.zusammenfassung,
            "gruende": [g.as_dict() for g in self.gruende],
            "anzahl_gepruefter_regeln": self.anzahl_gepruefter_regeln,
            "entscheidende_gruende_count": len(self.entscheidende_gruende),
            "ist_freigegeben": self.ist_freigegeben,
            "tenant_override_aktiv": self.tenant_override_aktiv,
            "prozess_key": self.prozess_key,
            "policy_set_id": self.policy_set_id,
            "icon": self.icon,
            "badge_farbe": self.badge_farbe,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Texttemplates
# ---------------------------------------------------------------------------

_ZUSAMMENFASSUNG_TEMPLATES: dict[EntscheidungsErgebnis, str] = {
    EntscheidungsErgebnis.FREIGEGEBEN:  "Freigegeben – alle Regeln erfüllt",
    EntscheidungsErgebnis.KEINE_REGEL:  "Freigegeben – keine einschränkende Regel vorhanden",
    EntscheidungsErgebnis.ABGELEHNT:    "Abgelehnt – Regel verletzt: {regel}",
    EntscheidungsErgebnis.WARNUNG:      "Warnung – Hinweis beachten: {regel}",
    EntscheidungsErgebnis.ESKALATION:   "Eskalation erforderlich – Freigabe durch Leitung: {regel}",
}

_AKTION_DEUTSCH: dict[PolicyAktion, str] = {
    PolicyAktion.ERLAUBT:    "erlaubt",
    PolicyAktion.ABGELEHNT:  "abgelehnt",
    PolicyAktion.WARNUNG:    "Warnung",
    PolicyAktion.ESKALATION: "Eskalation erforderlich",
}

_ERGEBNIS_MAP: dict[PolicyAktion, EntscheidungsErgebnis] = {
    PolicyAktion.ERLAUBT:    EntscheidungsErgebnis.FREIGEGEBEN,
    PolicyAktion.ABGELEHNT:  EntscheidungsErgebnis.ABGELEHNT,
    PolicyAktion.WARNUNG:    EntscheidungsErgebnis.WARNUNG,
    PolicyAktion.ESKALATION: EntscheidungsErgebnis.ESKALATION,
}


def _build_ergebnis_text(treffer_bezeichnung: str, aktion: PolicyAktion, begruendung: str) -> str:
    aktion_text = _AKTION_DEUTSCH.get(aktion, aktion.value)
    if begruendung:
        return f"Regel \"{treffer_bezeichnung}\": {begruendung} => {aktion_text}"
    return f"Regel \"{treffer_bezeichnung}\": {aktion_text}"


# ---------------------------------------------------------------------------
# explain_policy_result()
# ---------------------------------------------------------------------------

def explain_policy_result(
    result: "PolicyEvaluationResult",
    verbosity: ExplanationVerbosity = ExplanationVerbosity.STANDARD,
) -> PolicyExplanation:
    """
    Erzeugt eine benutzerfreundliche Erklärung für ein PolicyEvaluationResult.

    Args:
        result:     Auswertungsergebnis aus evaluate_policy_set()
        verbosity:  Detailgrad der Erklärung

    Returns:
        PolicyExplanation mit deutschen Texten und Struktur für das UI.
    """
    if result.kein_treffer:
        return PolicyExplanation(
            entscheidung=EntscheidungsErgebnis.KEINE_REGEL,
            zusammenfassung=_ZUSAMMENFASSUNG_TEMPLATES[EntscheidungsErgebnis.KEINE_REGEL],
            anzahl_gepruefter_regeln=0,
            prozess_key=result.prozess_key,
            policy_set_id=result.policy_set_id,
        )

    endentscheidung = _ERGEBNIS_MAP.get(result.wirksame_aktion, EntscheidungsErgebnis.FREIGEGEBEN)

    # Gründe aufbauen
    gruende: list[PolicyReasonEntry] = []
    for treffer in result.treffer:
        ist_entscheidend = (treffer.aktion == result.wirksame_aktion)
        ergebnis_text = _build_ergebnis_text(
            treffer.bezeichnung, treffer.aktion, treffer.begruendung
        )
        gruende.append(PolicyReasonEntry(
            regel_id=treffer.regel_id,
            regel_name=treffer.bezeichnung,
            aktion=treffer.aktion,
            ergebnis_text=ergebnis_text,
            ist_entscheidend=ist_entscheidend,
        ))

    # Zusammenfassung
    entscheidende = [g for g in gruende if g.ist_entscheidend]
    erste_entscheidende_regel = entscheidende[0].regel_name if entscheidende else ""
    template = _ZUSAMMENFASSUNG_TEMPLATES.get(endentscheidung, "{regel}")
    zusammenfassung = template.replace("{regel}", erste_entscheidende_regel)

    # Detailgrad
    if verbosity == ExplanationVerbosity.BRIEF:
        gruende_gefiltert = entscheidende[:1]
    elif verbosity == ExplanationVerbosity.STANDARD:
        gruende_gefiltert = entscheidende[:3]
    else:
        gruende_gefiltert = gruende

    return PolicyExplanation(
        entscheidung=endentscheidung,
        zusammenfassung=zusammenfassung,
        gruende=gruende_gefiltert,
        anzahl_gepruefter_regeln=len(result.treffer),
        prozess_key=result.prozess_key,
        policy_set_id=result.policy_set_id,
    )


# ---------------------------------------------------------------------------
# PolicyExplainabilityCache — wiederverwendbare Erklärungen je Prozess
# ---------------------------------------------------------------------------

@dataclass
class PolicyExplainabilityCache:
    """
    Einfacher In-Memory Cache für Policy-Erklärungen.

    Verhindert redundante Neuberechnungen bei mehrfach aufgerufenen
    Entscheidungen innerhalb einer UI-Session.
    """
    _cache: dict[str, PolicyExplanation] = field(default_factory=dict)

    def _key(self, policy_set_id: str, prozess_key: str, context_hash: str) -> str:
        return f"{policy_set_id}::{prozess_key}::{context_hash}"

    def get(
        self, policy_set_id: str, prozess_key: str, context_hash: str
    ) -> PolicyExplanation | None:
        return self._cache.get(self._key(policy_set_id, prozess_key, context_hash))

    def put(
        self,
        policy_set_id: str,
        prozess_key: str,
        context_hash: str,
        explanation: PolicyExplanation,
    ) -> None:
        self._cache[self._key(policy_set_id, prozess_key, context_hash)] = explanation

    def invalidate(self, policy_set_id: str) -> int:
        """Löscht alle Cache-Einträge für ein PolicySet. Gibt Anzahl gelöschter Einträge zurück."""
        keys_to_delete = [k for k in self._cache if k.startswith(f"{policy_set_id}::")]
        for k in keys_to_delete:
            del self._cache[k]
        return len(keys_to_delete)

    @property
    def size(self) -> int:
        return len(self._cache)
