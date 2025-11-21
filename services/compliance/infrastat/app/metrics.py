"""Prometheus-Metriken für den InfraStat-Service."""

from prometheus_client import Counter, Gauge

VALIDATION_SUCCESS_TOTAL = Counter(
    "infrastat_validation_success_total",
    "Anzahl erfolgreich validierter InfraStat-Batches",
)

VALIDATION_FAILURE_TOTAL = Counter(
    "infrastat_validation_failure_total",
    "Anzahl fehlgeschlagener InfraStat-Validierungen",
)

SUBMISSION_ATTEMPTS_TOTAL = Counter(
    "infrastat_submission_attempts_total",
    "Anzahl gestarteter Übermittlungsversuche",
)

SUBMISSION_SUCCESS_TOTAL = Counter(
    "infrastat_submission_success_total",
    "Anzahl erfolgreicher InfraStat-Übermittlungen",
)

SUBMISSION_FAILURE_TOTAL = Counter(
    "infrastat_submission_failure_total",
    "Anzahl fehlgeschlagener InfraStat-Übermittlungen",
)

SUBMISSION_FAILURE_RATIO = Gauge(
    "infrastat_submission_failure_ratio",
    "Quote fehlgeschlagener Übermittlungen",
)
