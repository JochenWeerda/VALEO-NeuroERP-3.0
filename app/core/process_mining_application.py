from __future__ import annotations

from datetime import date
import uuid
from typing import Any, Callable

from app.core.betriebskennzahlen import BetriebsKennzahl, BenchmarkReport, KennzahlEinheit
from app.core.iot_telemetry import DeviceManifest, TelemetryReading
from app.core.process_mining import ProcessMiningReport, build_process_mining_report


ProjectionStatusLoader = Callable[[str, Any], Any]
RuntimeReportLoader = Callable[[str, Any], Any]


def load_observability_context(
    tenant_id: str,
    device_store: dict[str, dict[str, Any]],
    reading_store: dict[str, dict[str, list[Any]]],
) -> tuple[list[DeviceManifest], list[TelemetryReading]]:
    device_rows = list(device_store.get(tenant_id, {}).values())
    devices = [row if isinstance(row, DeviceManifest) else DeviceManifest.model_validate(row) for row in device_rows]

    latest_readings: list[TelemetryReading] = []
    for rows in reading_store.get(tenant_id, {}).values():
        if not rows:
            continue
        latest = rows[-1]
        latest_readings.append(
            latest if isinstance(latest, TelemetryReading) else TelemetryReading.model_validate(latest)
        )
    return devices, latest_readings


def build_process_mining_report_for_tenant(
    tenant_id: str,
    db: Any,
    projection_status_loader: ProjectionStatusLoader,
    runtime_report_loader: RuntimeReportLoader,
    device_store: dict[str, dict[str, Any]],
    reading_store: dict[str, dict[str, list[Any]]],
) -> ProcessMiningReport:
    projection_status = projection_status_loader(tenant_id, db)
    runtime_report = runtime_report_loader(tenant_id, db)
    devices, latest_readings = load_observability_context(tenant_id, device_store, reading_store)
    return build_process_mining_report(
        projection_status=projection_status,
        runtime_report=runtime_report,
        device_manifests=devices,
        latest_readings=latest_readings,
    )


def build_process_mining_benchmark_report(
    verbund_id: str,
    periode: str,
    tenant_ids: list[str],
    projection_status_loader: ProjectionStatusLoader,
    runtime_report_loader: RuntimeReportLoader,
    device_store: dict[str, dict[str, Any]],
    reading_store: dict[str, dict[str, list[Any]]],
) -> BenchmarkReport:
    kennzahlen_je_tenant: dict[str, list[BetriebsKennzahl]] = {}
    for tenant_id in tenant_ids:
        mining_report = build_process_mining_report_for_tenant(
            tenant_id=tenant_id,
            db=None,
            projection_status_loader=projection_status_loader,
            runtime_report_loader=runtime_report_loader,
            device_store=device_store,
            reading_store=reading_store,
        )
        kennzahlen_je_tenant[tenant_id] = _build_process_mining_kennzahlen(
            tenant_id=tenant_id,
            periode=periode,
            mining_report=mining_report,
        )
    return BenchmarkReport.build(
        verbund_id=verbund_id,
        periode=periode,
        kennzahlen_je_tenant=kennzahlen_je_tenant,
    )


def _build_process_mining_kennzahlen(
    tenant_id: str,
    periode: str,
    mining_report: ProcessMiningReport,
) -> list[BetriebsKennzahl]:
    return [
        BetriebsKennzahl(
            kz_id=str(uuid.uuid4()),
            kz_name="process_ready_count",
            einheit=KennzahlEinheit.STUECK,
            wert=float(mining_report.ready_count),
            tenant_id=tenant_id,
            periode=periode,
            berechnet_am=date.today(),
        ),
        BetriebsKennzahl(
            kz_id=str(uuid.uuid4()),
            kz_name="process_lagging_count",
            einheit=KennzahlEinheit.STUECK,
            wert=float(mining_report.lagging_count),
            tenant_id=tenant_id,
            periode=periode,
            berechnet_am=date.today(),
        ),
        BetriebsKennzahl(
            kz_id=str(uuid.uuid4()),
            kz_name="process_critical_signal_count",
            einheit=KennzahlEinheit.STUECK,
            wert=float(mining_report.critical_signal_count),
            tenant_id=tenant_id,
            periode=periode,
            berechnet_am=date.today(),
        ),
    ]
