from app.api.v1.endpoints.kontrakte import build_kontrakt_screen_summary


def test_kontrakt_screen_summary_contract() -> None:
    payload = build_kontrakt_screen_summary(
        contract_id="contract-1",
        tenant_id="tenant-1",
        contract={
            "contract_no": "K-2026-001",
            "contract_type": "VERKAUF",
            "status": "OFFEN",
            "total_quantity": 500.0,
            "rest_quantity": 120.0,
            "valid_to": "2026-12-31",
        },
        line_count=2,
        party_name="Landwirt Schmidt",
    )

    assert payload["schema_version"] == 1
    assert payload["screen_id"] == "agrar/kontrakte"
    assert payload["summary"]["line_count"] == 2
    assert payload["tab_endpoints"]["positionen"].endswith("/kontrakte/contract-1/tabs/positionen")
    assert payload["tab_endpoints"]["umsaetze"].endswith("/kontrakte/contract-1/tabs/umsaetze")
    assert "kopf" in payload["available_tabs"]
    assert payload["performance"]["tabs_lazy"] is True


def test_kontrakt_screen_summary_includes_party_name() -> None:
    payload = build_kontrakt_screen_summary(
        contract_id="contract-1",
        tenant_id="tenant-1",
        contract={"contract_no": "K-100", "status": "OFFEN"},
        line_count=0,
        party_name="Muster Genossenschaft",
    )

    assert payload["party_name"] == "Muster Genossenschaft"
    assert payload["subtitle"] == "Muster Genossenschaft"
