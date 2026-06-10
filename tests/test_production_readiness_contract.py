from pathlib import Path

from scripts.check_required_domain_schemas import REQUIRED_COLUMNS
from scripts.check_production_readiness import validate_compose, validate_helm
from scripts.simulate_external_assessors import PROFILES, evaluate


ROOT = Path(__file__).resolve().parents[1]


def test_production_compose_has_no_dev_runtime_or_inline_secrets():
    findings = validate_compose(ROOT / "docker-compose.production.yml", "production")
    assert findings == []


def test_production_helm_values_are_fail_closed():
    findings = validate_helm(ROOT / "k8s/helm/valeo-erp/values-production.yaml")
    assert findings == []


def test_simulated_assessors_require_repository_evidence_and_keep_external_gates():
    results = [evaluate(profile) for profile in PROFILES]

    assert all(result["status"] == "conditional" for result in results)
    assert all(
        not check["missing_evidence"]
        for result in results
        for check in result["checks"]
    )
    assert all(
        not check["failed_assertions"]
        for result in results
        for check in result["checks"]
    )
    external_gates = [
        check["external_gate"]
        for result in results
        for check in result["checks"]
        if check["external_gate"]
    ]
    assert len(external_gates) >= 5


def test_release_workflows_have_no_skip_or_tolerated_failure_contract():
    files = (
        ROOT / ".github/workflows/release-gates.yml",
        ROOT / ".github/workflows/deploy-staging.yml",
        ROOT / ".github/workflows/valeo-erp-deployment.yml",
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)

    assert "skip_tests" not in text
    assert "continue-on-error: true" not in text
    assert "|| true" not in (ROOT / ".github/workflows/release-gates.yml").read_text(encoding="utf-8")
    assert "--quiet" in (ROOT / ".github/workflows/release-gates.yml").read_text(encoding="utf-8")
    assert "--atomic --wait" in text
    assert "scripts/init_db.py" in text
    assert "/readyz" in text
    assert "Dockerfile.frontend" in text
    assert "frontend.image.tag" in text


def test_frontend_runtime_is_static_non_root_and_spa_capable():
    dockerfile = (ROOT / "Dockerfile.frontend").read_text(encoding="utf-8")
    nginx = (ROOT / "deploy/nginx/frontend.conf").read_text(encoding="utf-8")

    assert "pnpm-lock.yaml" in dockerfile
    assert "--frozen-lockfile" in dockerfile
    assert "pnpm run build:prod" in dockerfile
    assert "nginx-unprivileged" in dockerfile
    assert 'CMD ["vite"' not in dockerfile
    assert "try_files $uri $uri/ /index.html" in nginx
    assert "server_tokens off" in nginx


def test_schema_drift_contract_covers_repaired_production_objects():
    assert ("domain_inventory", "agrar_settlements") in REQUIRED_COLUMNS
    assert ("domain_erp", "chart_of_accounts") in REQUIRED_COLUMNS
    assert ("domain_hr", "time_entries") in REQUIRED_COLUMNS
    assert ("domain_hr", "shifts") in REQUIRED_COLUMNS
    assert ("domain_inventory", "drying_rule_sets") in REQUIRED_COLUMNS


def test_dependency_maintenance_policy_covers_forced_major_updates():
    policy = (
        ROOT / "docs/operations/dependency-and-compatibility-maintenance.md"
    ).read_text(encoding="utf-8")

    assert "SemVer" in policy
    assert "Expand/Migrate/Contract" in policy
    assert "Critical" in policy
    assert "High" in policy
    assert "Major-Update" in policy
    assert "Rollback" in policy
    assert "SBOM" in policy
