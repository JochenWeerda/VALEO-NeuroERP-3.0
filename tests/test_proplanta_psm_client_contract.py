from __future__ import annotations

import pytest

from app.integrations import proplanta_psm_client


def test_proplanta_client_requires_real_tool_caller(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(proplanta_psm_client, "PROPLANTA_PSM_URL", "https://example.invalid")
    monkeypatch.setattr(proplanta_psm_client, "PROPLANTA_MCP_SERVER_NAME", "proplanta-server")
    client = proplanta_psm_client.ProplantaPSMClient()

    with pytest.raises(proplanta_psm_client.ProplantaPSMContractError):
        client.sync_psm_data()


def test_proplanta_client_parses_psm_list_without_mock(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(proplanta_psm_client, "PROPLANTA_PSM_URL", "https://example.invalid")
    monkeypatch.setattr(proplanta_psm_client, "PROPLANTA_MCP_SERVER_NAME", "proplanta-server")

    def tool_caller(tool_name: str, args: dict[str, object]) -> dict[str, object]:
        assert tool_name == "scrape_psm_list"
        assert args["url"] == "https://example.invalid"
        return {
            "content": [
                {"type": "text", "text": "Successfully scraped 1 PSM items"},
                {
                    "type": "text",
                    "text": '[{"id":"PSM001","name":"Roundup","activeIngredient":"Glyphosate","manufacturer":"Bayer"}]',
                },
            ]
        }

    client = proplanta_psm_client.ProplantaPSMClient(tool_caller=tool_caller)

    items = client.sync_psm_data()

    assert [item.id for item in items] == ["PSM001"]
    assert client.get_all_psm()[0].manufacturer == "Bayer"
