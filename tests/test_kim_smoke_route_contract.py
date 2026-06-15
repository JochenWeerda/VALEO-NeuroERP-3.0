from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_kim_smoke_registers_fallback_before_specific_routes():
    text = (
        ROOT
        / "playwright-tests"
        / "specs"
        / "crm"
        / "kim-performance-smoke.spec.ts"
    ).read_text(encoding="utf-8")

    fallback = text.index("adminPage.route('**/api/v1/crm/kim/**'")
    customers = text.index("adminPage.route('**/api/v1/crm/kim/customers?**'")
    dashboard = text.index(
        "adminPage.route('**/api/v1/crm/kim/customers/*/dashboard'"
    )

    assert fallback < customers < dashboard
    assert "Playwright evaluates route handlers in reverse registration order" in text
