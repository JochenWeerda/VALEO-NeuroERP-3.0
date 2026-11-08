"""Missing or invalid evidence must never produce a compliance certificate."""
from unittest.mock import Mock
import pytest
from app.security.compliance_monitor import ISO27001ComplianceMonitor


def monitor_with(**results):
    monitor = ISO27001ComplianceMonitor(None)
    monitor.compliance_checks = {
        key: {"check_function": Mock(return_value=value), "severity": "HIGH", "iso_control": "A.10"}
        for key, value in results.items()
    }
    return monitor


def test_default_monitor_has_no_fabricated_positive_evidence():
    monitor = ISO27001ComplianceMonitor(None)
    result = monitor.run_compliance_checks("tenant-a")
    assert result["overall_status"] == "UNKNOWN"
    assert result["compliance_score"] is None
    assert len(result["unverified_checks"]) == 8
    assert {check["status"] for check in result["checks"].values()} == {"UNKNOWN"}
    report = monitor.generate_compliance_report("tenant-a")
    assert report["certification_readiness"]["readiness_level"] == "UNKNOWN"
    assert report["certification_readiness"]["estimated_time_to_readiness"] is None
    dashboard = monitor.get_compliance_dashboard("tenant-b")
    assert dashboard["tenant_id"] == "tenant-b"
    assert dashboard["trend_data"] == []
    assert dashboard["compliance_score"] is None


@pytest.mark.parametrize("bad", [None, {}, {"status": "yes"}, {"status": "ERROR"}, {"status": "UNKNOWN"}])
def test_partial_or_invalid_evidence_blocks_score_and_readiness(bad):
    monitor = monitor_with(positive={"status": "PASSED"}, unavailable=bad)
    result = monitor.run_compliance_checks("tenant-a")
    assert result["overall_status"] == "UNKNOWN"
    assert result["compliance_score"] is None
    assert result["unverified_checks"] == ["unavailable"]
    assert monitor._assess_certification_readiness(result)["readiness_level"] == "UNKNOWN"
    monitor.compliance_checks["positive"]["check_function"].assert_called_once_with("tenant-a")


def test_exception_is_not_success_and_does_not_disclose_input(caplog):
    monitor = monitor_with(broken={"status": "PASSED"})
    monitor.compliance_checks["broken"]["check_function"].side_effect = ValueError("private-customer-input")
    result = monitor.run_compliance_checks("tenant-a")
    assert result["checks"]["broken"]["status"] == "ERROR"
    assert result["overall_status"] == "UNKNOWN"
    assert "private-customer-input" not in str(result) + caplog.text


@pytest.mark.parametrize("severity", ["MEDIUM", "HIGH", "CRITICAL"])
def test_known_failure_is_noncompliant_even_with_missing_other_evidence(severity):
    monitor = monitor_with(failed={"status": "FAILED"}, missing={"status": "UNKNOWN"})
    monitor.compliance_checks["failed"]["severity"] = severity
    result = monitor.run_compliance_checks("tenant-a")
    assert result["overall_status"] == "NON_COMPLIANT"
    assert result["compliance_score"] is None


def test_verified_results_still_score_without_inventing_certification_deadline():
    monitor = monitor_with(first={"status": "PASSED"}, second={"status": "PASSED"})
    result = monitor.run_compliance_checks("tenant-a")
    assert result["overall_status"] == "COMPLIANT"
    assert result["compliance_score"] == 100
    readiness = monitor._assess_certification_readiness(result)
    assert readiness["estimated_time_to_readiness"] is None
    assert "independent audit" in readiness["notes"]


def test_warning_is_not_all_clear():
    result = monitor_with(warning={"status": "WARNING"}).run_compliance_checks("tenant-a")
    assert result["overall_status"] == "WARNING"
    assert result["compliance_score"] == 98


def test_empty_check_configuration_is_unverified():
    result = monitor_with().run_compliance_checks("tenant-a")
    assert result["overall_status"] == "UNKNOWN"
    assert result["compliance_score"] is None


def test_high_numeric_score_cannot_overrule_a_verified_failure():
    monitor = monitor_with(failure={"status": "FAILED"})
    result = monitor.run_compliance_checks("tenant-a")
    assert result["compliance_score"] == 95
    assert monitor._assess_certification_readiness(result)["readiness_level"] == "NOT_READY"


def test_high_numeric_score_with_warning_is_not_certification_ready():
    monitor = monitor_with(warning={"status": "WARNING"})
    result = monitor.run_compliance_checks("tenant-a")
    assert result["compliance_score"] == 98
    assert monitor._assess_certification_readiness(result)["readiness_level"] == "NEAR_READY"
