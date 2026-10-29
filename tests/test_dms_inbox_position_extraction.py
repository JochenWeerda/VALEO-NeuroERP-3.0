"""Positions-Extraktion DMS-Inbox: Tabellen-Regex + Claude hinter Flag."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.dms_ocr_contracts import DokumentTyp
from app.documents.inbox_contract import build_article_create_proposals, extract_line_items
from app.documents.position_extraction import (
    GAP_ENGINE_NOT_CLAUDE,
    GAP_LLM_UNAVAILABLE,
    GAP_NO_LINES,
    GAP_REGEX_NO_LINES,
    enrich_parsed_fields_with_positions,
    extract_table_line_items,
    resolve_ocr_engine,
)
from app.integrations.dms_parser import DMSParser

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "dms_inbox"

# OCR ohne tabellarische Positionszeilen — fuer Claude-Fallback-Tests.
LIEFERSCHEIN_OCR_HEADER_ONLY = (
    "Lieferschein Nr. LS-7788 Datum 12.03.2026\n"
    "Lieferant: Agrar Handel Nord GmbH\n"
    "Bitte Pruefung der Lieferung.\n"
)


def _load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_resolve_ocr_engine_defaults_to_stub(monkeypatch):
    monkeypatch.delenv("EINKAUF_OCR_ENGINE", raising=False)
    assert resolve_ocr_engine() == "stub"


def test_table_regex_from_agrar_lieferschein_fixture():
    ocr = _load_fixture("synthetic_delivery_table.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 3
    assert rows[0]["artikel_nr"] == "WW-100"
    assert rows[0]["artikel_name"] == "Winterweizen A"
    assert rows[0]["menge"] == "12.50"
    assert rows[0]["einheit"] == "t"
    assert rows[0]["einzelpreis"] == "215.00"
    assert rows[2]["artikel_nr"] == "RM-9"


def test_table_regex_naturland_erzeugnis_fixture():
    ocr = _load_fixture("synthetic_delivery_product_lines.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) >= 2
    names = {r["artikel_name"] for r in rows}
    assert any("Winterweizen" in n for n in names)
    assert any("Hafer" in n for n in names)


def test_table_regex_rechnung_duenger_fixture():
    ocr = _load_fixture("synthetic_invoice_table.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 3
    assert rows[0]["artikel_nr"] == "DU-NPK15"
    assert rows[1]["menge"] == "5.00"


def test_enrich_fixture_without_claude_fills_positionen(monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "stub")
    ocr = _load_fixture("synthetic_delivery_table.txt")
    fields, gaps = enrich_parsed_fields_with_positions(
        {},
        ocr,
        force_kind=DokumentTyp.LIEFERSCHEIN,
    )
    assert gaps == []
    assert fields["position_extraction_engine"] == "table_regex"
    assert len(fields["positionen"]) == 3
    lines = extract_line_items(fields)
    proposals = build_article_create_proposals(lines, {0: [], 1: [], 2: []})
    assert all(p["status"] == "propose" for p in proposals)
    assert proposals[0]["payload"]["article_number"] == "WW-100"


def test_dms_parser_adds_positionen_from_fixture_ocr():
    ocr = _load_fixture("synthetic_invoice_table.txt")
    parsed = DMSParser().parse(ocr)
    assert "supplier" in parsed["fields"] or "invoice_number" in parsed["fields"]
    pos = parsed["fields"].get("positionen") or []
    assert len(pos) == 3
    assert extract_line_items(parsed["fields"])[0]["name"] == "NPK 15-15-15"


def test_enrich_non_claude_header_only_gaps(monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "pdfplumber")
    fields, gaps = enrich_parsed_fields_with_positions(
        {"supplier": "Agrar Handel Nord GmbH", "invoice_number": "LS-7788"},
        LIEFERSCHEIN_OCR_HEADER_ONLY,
        force_kind=DokumentTyp.LIEFERSCHEIN,
    )
    assert fields["positionen"] == []
    assert GAP_ENGINE_NOT_CLAUDE in gaps
    assert GAP_REGEX_NO_LINES in gaps
    assert extract_line_items(fields) == []


def test_enrich_stub_engine_never_injects_musterartikel(monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "stub")
    fields, gaps = enrich_parsed_fields_with_positions(
        {},
        LIEFERSCHEIN_OCR_HEADER_ONLY,
        force_kind=DokumentTyp.LIEFERSCHEIN,
    )
    assert fields["positionen"] == []
    assert GAP_ENGINE_NOT_CLAUDE in gaps
    assert "Musterartikel" not in json.dumps(fields)


def test_enrich_claude_without_llm_returns_gap(monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "claude")

    class _UnavailableGateway:
        def available(self) -> bool:
            return False

        def complete_or_none(self, *args, **kwargs):  # noqa: ANN002, ANN003
            return None

    monkeypatch.setattr(
        "app.services.llm_gateway.LLMGateway",
        lambda *a, **k: _UnavailableGateway(),
    )
    fields, gaps = enrich_parsed_fields_with_positions(
        {"date": "2026-03-12"},
        LIEFERSCHEIN_OCR_HEADER_ONLY,
        force_kind=DokumentTyp.LIEFERSCHEIN,
    )
    assert fields["positionen"] == []
    assert GAP_LLM_UNAVAILABLE in gaps


def test_enrich_claude_text_path_when_regex_empty(monkeypatch):
    """Claude nur wenn Regex keine Zeilen findet — Fixture simuliert Parser-JSON."""
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "claude")

    fixture_payload = {
        "positionen": [
            {
                "artikel_name": "Winterweizen A",
                "artikel_nr": "WW-1",
                "menge": 10,
                "einheit": "t",
                "einzelpreis": 215.5,
            },
        ],
    }

    class _OkGateway:
        def available(self) -> bool:
            return True

        def complete_or_none(self, prompt: str, max_tokens: int = 1024):
            assert "OCR-Text" in prompt
            return json.dumps(fixture_payload)

    monkeypatch.setattr(
        "app.services.llm_gateway.LLMGateway",
        lambda *a, **k: _OkGateway(),
    )
    fields, gaps = enrich_parsed_fields_with_positions(
        {"supplier": "Agrar Handel Nord GmbH"},
        LIEFERSCHEIN_OCR_HEADER_ONLY,
        force_kind=DokumentTyp.LIEFERSCHEIN,
    )
    assert gaps == []
    assert fields["position_extraction_engine"] == "claude_text"
    assert fields["positionen"][0]["artikel_nr"] == "WW-1"
    proposals = build_article_create_proposals(extract_line_items(fields), {0: []})
    assert proposals[0]["status"] == "propose"


def test_enrich_claude_empty_array_is_gap_not_invented(monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "claude")

    class _EmptyGateway:
        def available(self) -> bool:
            return True

        def complete_or_none(self, *args, **kwargs):  # noqa: ANN002, ANN003
            return '{"positionen":[]}'

    monkeypatch.setattr(
        "app.services.llm_gateway.LLMGateway",
        lambda *a, **k: _EmptyGateway(),
    )
    fields, gaps = enrich_parsed_fields_with_positions(
        {},
        LIEFERSCHEIN_OCR_HEADER_ONLY,
        force_kind=DokumentTyp.LIEFERSCHEIN,
    )
    assert fields["positionen"] == []
    assert GAP_NO_LINES in gaps


def test_enrich_preserves_existing_real_positions(monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "stub")
    existing = {
        "positionen": [
            {"artikel_name": "Sojaschrot", "artikel_nr": "SOJA-1", "menge": 2, "einheit": "t"},
        ],
    }
    fields, gaps = enrich_parsed_fields_with_positions(
        existing,
        LIEFERSCHEIN_OCR_HEADER_ONLY,
        force_kind=DokumentTyp.LIEFERSCHEIN,
    )
    assert gaps == []
    assert fields["positionen"][0]["artikel_nr"] == "SOJA-1"


def test_enrich_filters_musterartikel_from_claude(monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "claude")

    class _StubLikeGateway:
        def available(self) -> bool:
            return True

        def complete_or_none(self, *args, **kwargs):  # noqa: ANN002, ANN003
            return json.dumps({
                "positionen": [
                    {"artikel_name": "Musterartikel A", "menge": 10},
                    {"artikel_name": "Rapsmehl", "artikel_nr": "RM-9", "menge": 3, "einheit": "t"},
                ],
            })

    monkeypatch.setattr(
        "app.services.llm_gateway.LLMGateway",
        lambda *a, **k: _StubLikeGateway(),
    )
    fields, gaps = enrich_parsed_fields_with_positions(
        {},
        LIEFERSCHEIN_OCR_HEADER_ONLY,
        force_kind=DokumentTyp.EINGANGSRECHNUNG,
    )
    assert gaps == []
    assert len(fields["positionen"]) == 1
    assert fields["positionen"][0]["artikel_name"] == "Rapsmehl"


def test_enrich_pdf_claude_path_uses_extract_invoice_pdf(monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "claude")

    def _fake_extract(*, file_id, engine, pdf_bytes):
        assert engine == "claude"
        assert pdf_bytes == b"%PDF-1.4 fixture"
        return {
            "extracted_data": {
                "positionen": [
                    {
                        "artikel_name": "Gerste",
                        "artikel_nr": "GE-2",
                        "menge": 5,
                        "einheit": "t",
                        "einzelpreis": 180.0,
                    },
                ],
            },
            "extraction_warnings": [],
            "confidence_score": 0.92,
            "ocr_model": "claude-opus-4-7",
        }

    monkeypatch.setattr(
        "app.einkauf.ocr_invoice.extract_invoice_pdf",
        _fake_extract,
    )
    fields, gaps = enrich_parsed_fields_with_positions(
        {},
        LIEFERSCHEIN_OCR_HEADER_ONLY,
        pdf_bytes=b"%PDF-1.4 fixture",
        force_kind=DokumentTyp.LIEFERSCHEIN,
    )
    assert gaps == []
    assert fields["positionen"][0]["artikel_nr"] == "GE-2"
    assert fields["position_extraction_engine"] == "claude_pdf"


@pytest.mark.parametrize(
    "kind",
    [DokumentTyp.LIEFERSCHEIN, DokumentTyp.EINGANGSRECHNUNG],
)
def test_supported_kinds_accept_force(kind, monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "pdfplumber")
    _fields, gaps = enrich_parsed_fields_with_positions(
        {},
        "irrelevant",
        force_kind=kind,
    )
    assert GAP_ENGINE_NOT_CLAUDE in gaps


def test_mayan_pdf_uses_real_httpx_response_and_advertised_link():
    import httpx
    from app.documents.position_extraction import try_fetch_mayan_pdf

    paths = []
    def serve(request):
        paths.append(request.url.path)
        return httpx.Response(200, content=b"%PDF-1.4 fixture")

    with httpx.Client(base_url="https://mayan.example", transport=httpx.MockTransport(serve)) as client:
        assert try_fetch_mayan_pdf(client, 42, 7) is None
        assert paths == []
        assert try_fetch_mayan_pdf(client, 42, 7, download_url="/advertised.pdf") == b"%PDF-1.4 fixture"
        assert paths == ["/advertised.pdf"]
        assert try_fetch_mayan_pdf(client, 42, 7, download_url="https://foreign.example/file") is None
        assert paths == ["/advertised.pdf"]


@pytest.mark.parametrize("status, content", [(302, b""), (403, b"denied"), (200, b"not a PDF")])
def test_mayan_pdf_failure_preserves_text_fallback(status, content, monkeypatch):
    import httpx
    from app.documents.position_extraction import try_fetch_mayan_pdf

    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "stub")
    with httpx.Client(base_url="https://mayan.example", transport=httpx.MockTransport(
        lambda request: httpx.Response(status, content=content, headers={"Location": "https://foreign.example"})
    )) as client:
        pdf = try_fetch_mayan_pdf(client, 42, download_url="/advertised.pdf")
    assert pdf is None
    fields, _ = enrich_parsed_fields_with_positions(
        {}, "Lieferschein\nPos Art-Nr Bezeichnung Menge ME Preis\n1 AB12 Korn 2 kg 3,00\n",
        pdf_bytes=pdf, force_kind=DokumentTyp.LIEFERSCHEIN,
    )
    assert fields["positionen"][0]["artikel_nr"] == "AB12"
    assert fields["position_extraction_engine"] == "table_regex"


def test_parser_has_no_placeholder_positions_without_document_lines():
    parsed = DMSParser().parse("Rechnung Nr RE-SYNTH-EMPTY\nLieferant: Synthetischer Testlieferant\n")
    assert not parsed["fields"].get("positionen")


def test_webhook_enrichment_preserves_parser_positions_without_reextracting(monkeypatch):
    parsed = DMSParser().parse(_load_fixture("synthetic_invoice_table.txt"))
    def unexpected(*args, **kwargs):
        raise AssertionError("Existing deterministic rows must not be extracted twice")
    monkeypatch.setattr("app.documents.position_extraction.extract_table_line_items", unexpected)
    monkeypatch.setattr("app.documents.position_extraction._extract_via_pdf_claude", unexpected)
    fields, gaps = enrich_parsed_fields_with_positions(parsed["fields"], parsed["raw_text"])
    assert fields["positionen"] == parsed["fields"]["positionen"]
    assert gaps == []
