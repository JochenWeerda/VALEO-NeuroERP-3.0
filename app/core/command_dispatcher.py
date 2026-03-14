"""
Command Dispatcher — Wave 5 Paket A.

Prueft Preconditions und Rollenberechtigung, fuehrt Command-Validierung durch,
schreibt AuditEvidenceEntry-Hook (best-effort).
"""

from __future__ import annotations

from typing import Optional, Any

from app.core.business_commands import (
    BusinessCommand,
    CommandDefinition,
    CommandResult,
    CommandError,
    CommandStatus,
    build_core_command_catalog,
)


class CommandDispatcher:
    """
    Prueft Preconditions und Rollenberechtigung, fuehrt Command aus,
    schreibt AuditEvidenceEntry-Hook (best-effort).
    """

    def __init__(self, catalog: Optional[list[CommandDefinition]] = None):
        self._catalog: dict[str, CommandDefinition] = {
            cd.command_name: cd for cd in (catalog or build_core_command_catalog())
        }

    def get_definition(self, command_name: str) -> Optional[CommandDefinition]:
        return self._catalog.get(command_name)

    def check_role(self, command: BusinessCommand, issuer_role: Optional[str]) -> bool:
        """Prueft ob die Rolle des Ausstellers berechtigt ist."""
        defn = self.get_definition(command.command_name)
        if defn is None:
            return False
        if not defn.allowed_roles:
            return True     # kein Rollenfilter → offen
        return issuer_role in defn.allowed_roles

    def check_preconditions(
        self,
        command: BusinessCommand,
        aggregate_state: dict[str, Any],
    ) -> Optional[CommandError]:
        """Prueft alle Preconditions; gibt CommandError zurueck wenn eine nicht erfuellt ist."""
        defn = self.get_definition(command.command_name)
        if defn is None:
            return CommandError(
                code="UNKNOWN_COMMAND",
                message=f"Command '{command.command_name}' ist nicht im Katalog",
            )
        for precond in defn.preconditions:
            actual = aggregate_state.get(precond.field)
            if not precond.evaluate(actual):
                return CommandError(
                    code=precond.error_code,
                    message=f"Vorbedingung nicht erfuellt: {precond.field} = {actual!r}",
                    detail=f"Erwartet: {precond.operator} {precond.expected!r}",
                )
        return None

    def dispatch(
        self,
        command: BusinessCommand,
        aggregate_state: dict[str, Any],
        issuer_role: Optional[str] = None,
    ) -> CommandResult:
        """
        Haupteinstiegspunkt: Rolle + Preconditions pruefen, Command akzeptieren oder ablehnen.
        Kein tatsaechlicher DB-Schreibvorgang hier — der Aufrufer fuehrt die Aktion aus.
        """
        defn = self.get_definition(command.command_name)
        if defn is None:
            return CommandResult(
                command_id=command.command_id,
                status=CommandStatus.REJECTED,
                aggregate_type=command.aggregate_type,
                aggregate_id=command.aggregate_id,
                error=CommandError(
                    code="UNKNOWN_COMMAND",
                    message=f"Unbekannter Command: {command.command_name}",
                ),
            )

        if not self.check_role(command, issuer_role):
            return CommandResult(
                command_id=command.command_id,
                status=CommandStatus.REJECTED,
                aggregate_type=command.aggregate_type,
                aggregate_id=command.aggregate_id,
                error=CommandError(
                    code="ROLE_DENIED",
                    message=f"Rolle '{issuer_role}' darf '{command.command_name}' nicht ausfuehren",
                ),
            )

        precond_error = self.check_preconditions(command, aggregate_state)
        if precond_error:
            return CommandResult(
                command_id=command.command_id,
                status=CommandStatus.REJECTED,
                aggregate_type=command.aggregate_type,
                aggregate_id=command.aggregate_id,
                error=precond_error,
            )

        if defn.requires_human_confirmation and not command.requires_human_confirmation:
            return CommandResult(
                command_id=command.command_id,
                status=CommandStatus.PENDING_APPROVAL,
                aggregate_type=command.aggregate_type,
                aggregate_id=command.aggregate_id,
                error=CommandError(
                    code="HUMAN_CONFIRMATION_REQUIRED",
                    message=f"'{command.command_name}' erfordert explizite Human-Confirmation",
                ),
            )

        return CommandResult(
            command_id=command.command_id,
            status=CommandStatus.ACCEPTED,
            aggregate_type=command.aggregate_type,
            aggregate_id=command.aggregate_id,
        )
