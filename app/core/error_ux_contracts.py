"""
error_ux_contracts.py — Leitsystem für Ausnahmefälle / Error UX (Wave 80, Gap 028)

Strukturierte Fehlerklassifizierung mit deutschen Benutzerhinweisen und
Wiederherstellungsaktionen für alle ERP-Masken.

Gap 028: Leitsystem für Ausnahmefälle — KPI: 50% weniger Abbruchquote bei Fehlern
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ErrorCategory(str, Enum):
    """Kategorie eines Anwendungsfehlers."""
    NETWORK        = "NETWORK"        # Verbindungsproblem, Timeout
    VALIDATION     = "VALIDATION"     # Ungültige Eingabe
    AUTHORIZATION  = "AUTHORIZATION"  # Keine Berechtigung
    NOT_FOUND      = "NOT_FOUND"      # Datensatz nicht gefunden
    SERVER         = "SERVER"         # Interner Serverfehler
    CONFLICT       = "CONFLICT"       # Optimistic-Lock / Konkurrenzzugriff
    TIMEOUT        = "TIMEOUT"        # Anfrage zu langsam
    BUSINESS_RULE  = "BUSINESS_RULE"  # Fachliche Regelabweichung
    UNKNOWN        = "UNKNOWN"        # Unbekannter Fehler


class ErrorSeverity(str, Enum):
    """Auswirkung des Fehlers auf den Benutzerfluss."""
    BLOCKING    = "BLOCKING"    # Aktion nicht möglich, Weiterarbeit blockiert
    RECOVERABLE = "RECOVERABLE" # Mit Maßnahme lösbar, Daten nicht verloren
    WARNING     = "WARNING"     # Hinweis, Aktion möglich aber riskant


# ---------------------------------------------------------------------------
# Recovery Actions
# ---------------------------------------------------------------------------

@dataclass
class RecoveryAction:
    """
    Empfohlene Maßnahme zur Fehlerbeseitigung.

    action_key wird vom Frontend interpretiert (z.B. "retry", "login", "reload").
    """
    label: str           # Deutsch, z.B. "Erneut versuchen"
    action_key: str      # "retry" | "login" | "reload" | "back" | "contact_support" | "save_draft"
    primary: bool = True # Primäre vs. sekundäre Aktion (Styling)
    icon: str = ""       # Optional: Icon-Name (z.B. "RefreshCw", "LogIn")

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "action_key": self.action_key,
            "primary": self.primary,
            "icon": self.icon,
        }


# ---------------------------------------------------------------------------
# UserFacingError
# ---------------------------------------------------------------------------

@dataclass
class UserFacingError:
    """
    Benutzerfreundliche Fehlerbeschreibung mit Handlungsempfehlungen.

    Jeder technische Fehler wird auf einen UserFacingError gemappt,
    der dem Benutzer zeigt:
    - was schiefgelaufen ist (title, detail)
    - was er tun kann (recovery_actions, tip)
    - ob er Daten verloren hat (data_loss_risk)
    """
    category: ErrorCategory
    severity: ErrorSeverity
    title: str
    detail: str
    recovery_actions: list[RecoveryAction] = field(default_factory=list)
    tip: str = ""                  # Kontextueller Tipp (z.B. "Ihre Eingaben sind noch vorhanden")
    support_code: str = ""         # Fehlercode für Support (z.B. "ERR-AUTH-403")
    data_loss_risk: bool = False   # True wenn ungespeicherte Daten verloren sein könnten

    @property
    def primary_action(self) -> RecoveryAction | None:
        return next((a for a in self.recovery_actions if a.primary), None)

    @property
    def secondary_actions(self) -> list[RecoveryAction]:
        return [a for a in self.recovery_actions if not a.primary]

    def as_dict(self) -> dict:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "detail": self.detail,
            "recovery_actions": [a.as_dict() for a in self.recovery_actions],
            "tip": self.tip,
            "support_code": self.support_code,
            "data_loss_risk": self.data_loss_risk,
            "primary_action": self.primary_action.as_dict() if self.primary_action else None,
        }


# ---------------------------------------------------------------------------
# Standard-Recovery-Actions
# ---------------------------------------------------------------------------

def _action_retry() -> RecoveryAction:
    return RecoveryAction("Erneut versuchen", "retry", primary=True, icon="RefreshCw")

def _action_reload() -> RecoveryAction:
    return RecoveryAction("Seite neu laden", "reload", primary=False, icon="RefreshCw")

def _action_back() -> RecoveryAction:
    return RecoveryAction("Zurück", "back", primary=False, icon="ArrowLeft")

def _action_login() -> RecoveryAction:
    return RecoveryAction("Erneut anmelden", "login", primary=True, icon="LogIn")

def _action_support() -> RecoveryAction:
    return RecoveryAction("Support kontaktieren", "contact_support", primary=False, icon="LifeBuoy")

def _action_save_draft() -> RecoveryAction:
    return RecoveryAction("Entwurf speichern", "save_draft", primary=True, icon="Save")

def _action_refresh_and_merge() -> RecoveryAction:
    return RecoveryAction("Daten aktualisieren und zusammenführen", "refresh_merge", primary=True, icon="GitMerge")


# ---------------------------------------------------------------------------
# Klassifizierung nach HTTP-Statuscode
# ---------------------------------------------------------------------------

def classify_http_error(
    status_code: int,
    detail: str = "",
    context: str = "",
) -> UserFacingError:
    """
    Wandelt einen HTTP-Statuscode in einen UserFacingError um.

    Args:
        status_code: HTTP-Statuscode (400, 401, 403, 404, 409, 422, 500, 502, 503, 504)
        detail:      Optionale technische Detail-Meldung vom Server
        context:     Optionaler Kontext (z.B. "Speichern", "Laden")

    Returns:
        UserFacingError mit deutschen Texten und Handlungsempfehlungen.
    """
    aktion = f" beim {context}" if context else ""

    if status_code == 400:
        return UserFacingError(
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.RECOVERABLE,
            title=f"Ungültige Eingabe{aktion}",
            detail="Die übermittelten Daten konnten nicht verarbeitet werden. "
                   "Bitte prüfen Sie Ihre Eingaben.",
            recovery_actions=[_action_back()],
            tip="Prüfen Sie die rot markierten Felder und korrigieren Sie die Eingaben.",
            support_code=f"ERR-VALIDATION-400",
        )

    if status_code in (401, 403):
        code_label = "401" if status_code == 401 else "403"
        return UserFacingError(
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.BLOCKING,
            title="Keine Berechtigung",
            detail="Sie haben keine ausreichende Berechtigung für diese Aktion. "
                   "Wenden Sie sich an Ihren Administrator.",
            recovery_actions=[_action_login(), _action_support()],
            tip="Falls Sie gerade angemeldet sind, ist Ihre Sitzung möglicherweise abgelaufen.",
            support_code=f"ERR-AUTH-{code_label}",
            data_loss_risk=status_code == 401,
        )

    if status_code == 404:
        return UserFacingError(
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.RECOVERABLE,
            title=f"Datensatz nicht gefunden",
            detail="Der gesuchte Datensatz existiert nicht oder wurde bereits gelöscht.",
            recovery_actions=[_action_back(), _action_reload()],
            tip="Möglicherweise wurde der Datensatz von einem anderen Benutzer gelöscht.",
            support_code="ERR-NOTFOUND-404",
        )

    if status_code == 409:
        return UserFacingError(
            category=ErrorCategory.CONFLICT,
            severity=ErrorSeverity.RECOVERABLE,
            title="Bearbeitungskonflikt",
            detail="Ein anderer Benutzer hat den Datensatz gleichzeitig geändert. "
                   "Ihre Änderungen konnten nicht gespeichert werden.",
            recovery_actions=[_action_refresh_and_merge(), _action_save_draft()],
            tip="Ihre Eingaben sind noch vorhanden. "
                "Laden Sie die aktuellen Daten und prüfen Sie die Unterschiede.",
            support_code="ERR-CONFLICT-409",
            data_loss_risk=True,
        )

    if status_code == 422:
        return UserFacingError(
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.RECOVERABLE,
            title=f"Fachliche Validierung fehlgeschlagen{aktion}",
            detail="Die Daten entsprechen nicht den fachlichen Anforderungen. "
                   + (f"Details: {detail}" if detail else ""),
            recovery_actions=[_action_back()],
            tip="Prüfen Sie die Eingaben auf fachliche Vollständigkeit.",
            support_code="ERR-VALIDATION-422",
        )

    if status_code in (500, 502):
        code = str(status_code)
        return UserFacingError(
            category=ErrorCategory.SERVER,
            severity=ErrorSeverity.BLOCKING,
            title="Serverfehler",
            detail="Im System ist ein unerwarteter Fehler aufgetreten. "
                   "Wir wurden benachrichtigt und arbeiten an einer Lösung.",
            recovery_actions=[_action_retry(), _action_support()],
            tip="Versuchen Sie es in wenigen Minuten erneut. "
                "Falls das Problem anhält, wenden Sie sich an den Support.",
            support_code=f"ERR-SERVER-{code}",
            data_loss_risk=True,
        )

    if status_code == 503:
        return UserFacingError(
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.BLOCKING,
            title="Dienst vorübergehend nicht erreichbar",
            detail="Das System befindet sich möglicherweise in Wartung oder ist überlastet.",
            recovery_actions=[_action_retry(), _action_reload()],
            tip="Versuchen Sie es in einigen Minuten erneut.",
            support_code="ERR-UNAVAIL-503",
        )

    if status_code == 504:
        return UserFacingError(
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.RECOVERABLE,
            title="Zeitüberschreitung",
            detail="Die Anfrage hat zu lange gedauert und wurde abgebrochen. "
                   "Ihre Daten wurden möglicherweise nicht gespeichert.",
            recovery_actions=[_action_retry(), _action_reload()],
            tip="Prüfen Sie Ihre Internetverbindung und versuchen Sie es erneut.",
            support_code="ERR-TIMEOUT-504",
            data_loss_risk=True,
        )

    # Fallback für unbekannte Statuscodes
    return UserFacingError(
        category=ErrorCategory.UNKNOWN,
        severity=ErrorSeverity.BLOCKING,
        title="Unbekannter Fehler",
        detail=f"Ein unerwarteter Fehler ist aufgetreten (Code: {status_code}).",
        recovery_actions=[_action_reload(), _action_support()],
        support_code=f"ERR-UNKNOWN-{status_code}",
    )


def classify_network_error(error_type: str = "") -> UserFacingError:
    """
    Klassifiziert Netzwerkfehler (fetch failed, DNS, offline).
    """
    return UserFacingError(
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.BLOCKING,
        title="Keine Verbindung",
        detail="Das System kann den Server nicht erreichen. "
               "Prüfen Sie Ihre Netzwerkverbindung.",
        recovery_actions=[_action_retry(), _action_reload()],
        tip="Stellen Sie sicher, dass Sie mit dem Firmennetzwerk oder VPN verbunden sind.",
        support_code="ERR-NETWORK-OFFLINE",
    )


def classify_business_rule_error(
    regel: str,
    detail: str = "",
) -> UserFacingError:
    """
    Fachlicher Fehler (Workflow-Regel verletzt, z.B. Menge über Kontraktlimit).
    """
    return UserFacingError(
        category=ErrorCategory.BUSINESS_RULE,
        severity=ErrorSeverity.RECOVERABLE,
        title=f"Fachliche Regel verletzt: {regel}",
        detail=detail or f"Die Aktion verstößt gegen die Regel '{regel}'.",
        recovery_actions=[_action_back(), _action_support()],
        tip="Prüfen Sie die Regelkonfiguration oder sprechen Sie mit Ihrem Prozessverantwortlichen.",
        support_code=f"ERR-RULE-{regel.upper().replace(' ', '_')[:20]}",
    )


# ---------------------------------------------------------------------------
# ErrorUxRegistry — Vordefinierte Fehlermeldungen für bekannte Szenarien
# ---------------------------------------------------------------------------

@dataclass
class ErrorUxRegistry:
    """
    Registry bekannter Fehlerszenarien für schnellen Zugriff im Frontend.

    Jeder Eintrag ist ein benanntes Szenario mit fertigem UserFacingError.
    """
    eintraege: dict[str, UserFacingError] = field(default_factory=dict)

    def register(self, key: str, error: UserFacingError) -> None:
        self.eintraege[key] = error

    def get(self, key: str) -> UserFacingError | None:
        return self.eintraege.get(key)

    def keys(self) -> list[str]:
        return list(self.eintraege.keys())


def get_default_error_registry() -> ErrorUxRegistry:
    """Standardregistry mit bekannten ERP-Fehlerszenarien."""
    registry = ErrorUxRegistry()

    registry.register("session_expired", UserFacingError(
        category=ErrorCategory.AUTHORIZATION,
        severity=ErrorSeverity.BLOCKING,
        title="Sitzung abgelaufen",
        detail="Ihre Anmeldesitzung ist abgelaufen. Bitte melden Sie sich erneut an.",
        recovery_actions=[_action_login()],
        tip="Ihre ungespeicherten Eingaben können Sie nach der Anmeldung erneut eingeben.",
        support_code="ERR-SESSION-EXPIRED",
        data_loss_risk=True,
    ))

    registry.register("save_conflict", classify_http_error(409))

    registry.register("loading_failed", UserFacingError(
        category=ErrorCategory.SERVER,
        severity=ErrorSeverity.RECOVERABLE,
        title="Daten konnten nicht geladen werden",
        detail="Die angeforderten Daten sind vorübergehend nicht verfügbar.",
        recovery_actions=[_action_reload(), _action_retry()],
        tip="Versuchen Sie die Seite neu zu laden.",
        support_code="ERR-LOAD-FAILED",
    ))

    registry.register("no_permission_for_action", classify_http_error(403))

    registry.register("record_deleted_by_other_user", classify_http_error(404))

    registry.register("workflow_blocked", UserFacingError(
        category=ErrorCategory.BUSINESS_RULE,
        severity=ErrorSeverity.BLOCKING,
        title="Workflow gesperrt",
        detail="Dieser Vorgang befindet sich in einem Zustand, der keine weiteren Aktionen erlaubt.",
        recovery_actions=[_action_back(), _action_support()],
        tip="Möglicherweise wartet der Vorgang auf eine Freigabe durch eine andere Person.",
        support_code="ERR-WORKFLOW-BLOCKED",
    ))

    return registry
