from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable


ApprovalStatusLoader = Callable[[str, str, Any], Awaitable[Any]]
ApprovalRequestHandler = Callable[[str, str, str, str | None, Any], Awaitable[Any]]
ApprovalDecisionHandler = Callable[[str, str, str, str, str | None, Any], Awaitable[Any]]

ClosingWorkspaceHandler = Callable[[Any, Any], Awaitable[Any]]
ProjectionStatusLoader = Callable[[str, Any], Any]
RuntimeReportLoader = Callable[[str, Any], Any]
StoreLoader = Callable[[], dict[str, Any] | None]


@dataclass
class ApprovalWorkflowGateway:
    get_status: ApprovalStatusLoader
    request_approval: ApprovalRequestHandler
    approve_invoice: ApprovalDecisionHandler


@dataclass
class ClosingWorkspaceGateway:
    calculate: ClosingWorkspaceHandler
    approve: ClosingWorkspaceHandler
    close: ClosingWorkspaceHandler
    lock: ClosingWorkspaceHandler


_approval_workflow_gateway: ApprovalWorkflowGateway | None = None
_closing_workspace_gateway: ClosingWorkspaceGateway | None = None
_projection_status_loader: ProjectionStatusLoader | None = None
_runtime_report_loader: RuntimeReportLoader | None = None
_telemetry_device_store: dict[str, dict[str, Any]] | None = None
_telemetry_reading_store: dict[str, dict[str, list[Any]]] | None = None
_ap_invoice_store_loader: StoreLoader | None = None
_payment_run_store_loader: StoreLoader | None = None


def register_approval_workflow_gateway(gateway: ApprovalWorkflowGateway) -> None:
    global _approval_workflow_gateway
    _approval_workflow_gateway = gateway


def get_approval_workflow_gateway() -> ApprovalWorkflowGateway | None:
    return _approval_workflow_gateway


def register_closing_workspace_gateway(gateway: ClosingWorkspaceGateway) -> None:
    global _closing_workspace_gateway
    _closing_workspace_gateway = gateway


def get_closing_workspace_gateway() -> ClosingWorkspaceGateway | None:
    return _closing_workspace_gateway


def register_projection_status_loader(loader: ProjectionStatusLoader) -> None:
    global _projection_status_loader
    _projection_status_loader = loader


def get_projection_status_loader() -> ProjectionStatusLoader | None:
    return _projection_status_loader


def register_runtime_report_loader(loader: RuntimeReportLoader) -> None:
    global _runtime_report_loader
    _runtime_report_loader = loader


def get_runtime_report_loader() -> RuntimeReportLoader | None:
    return _runtime_report_loader


def register_telemetry_stores(
    *,
    device_store: dict[str, dict[str, Any]],
    reading_store: dict[str, dict[str, list[Any]]],
) -> None:
    global _telemetry_device_store, _telemetry_reading_store
    _telemetry_device_store = device_store
    _telemetry_reading_store = reading_store


def get_telemetry_device_store() -> dict[str, dict[str, Any]]:
    return _telemetry_device_store or {}


def get_telemetry_reading_store() -> dict[str, dict[str, list[Any]]]:
    return _telemetry_reading_store or {}


def register_ap_invoice_store_loader(loader: StoreLoader) -> None:
    global _ap_invoice_store_loader
    _ap_invoice_store_loader = loader


def get_ap_invoice_store_loader() -> StoreLoader | None:
    return _ap_invoice_store_loader


def register_payment_run_store_loader(loader: StoreLoader) -> None:
    global _payment_run_store_loader
    _payment_run_store_loader = loader


def get_payment_run_store_loader() -> StoreLoader | None:
    return _payment_run_store_loader
