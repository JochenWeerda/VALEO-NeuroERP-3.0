"""User-Upload Übungsbelege: Positionen + Header (ADAPTIVE OCR-Training)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.dms_ocr_contracts import DokumentTyp
from app.documents.inbox_contract import (
    build_article_create_proposals,
    classify_document,
    document_kind_from_existing,
    extract_line_items,
)
from app.documents.position_extraction import (
    GAP_REGEX_NO_LINES,
    enrich_parsed_fields_with_positions,
    extract_table_line_items,
)
from app.integrations.dms_parser import DMSParser

FIXTURES = Path(__file__).resolve().parents[1] / "evidence" / "ocr-training" / "fixtures"
LIVE = FIXTURES / "live-ocr"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_broering_mais_position_and_header():
    ocr = _load("re_broering_vr1466078.ocr.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 1
    assert rows[0]["artikel_name"].startswith("MAIS")
    assert rows[0]["menge"] == "50000"
    assert rows[0]["einheit"] == "kg"
    parsed = DMSParser().parse(ocr)["fields"]
    assert "Broering" in (parsed.get("supplier") or "") or "Bröring" in (parsed.get("supplier") or "")
    assert "VR1466078" in (parsed.get("invoice_number") or "")
    assert "folkerts" not in (parsed.get("supplier") or "").casefold()


def test_birkhoff_two_rapsschrot_lines():
    ocr = _load("re_birkhoff_227627.ocr.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 2
    assert all(r["artikel_nr"] == "291040" for r in rows)
    assert rows[0]["menge"] == "1980.00"
    assert rows[1]["menge"] == "25200.00"
    parsed = DMSParser().parse(ocr)["fields"]
    assert parsed.get("contract_id") == "13842"
    assert "227627" in (parsed.get("invoice_number") or "")


def test_broering_live_ocr_maklerkontrakt_number():
    """Live-OCR-Korpus: Maklerkontraktnr. → contract_id fuer Inbox-Abgleich."""
    live = FIXTURES / "live-ocr" / "broering_vr1466078.live.ocr.txt"
    if not live.exists():
        pytest.skip("live-ocr Broering fehlt")
    ocr = live.read_text(encoding="utf-8")
    parsed = DMSParser().parse(ocr)["fields"]
    assert parsed.get("contract_id") == "63044-25"


def test_broering_live_menge_recovered_from_price_netto():
    """Live-OCR liest Menge als 0.000 — Rekonstruktion 50.000 kg aus 23,10 €/dt × Netto."""
    path = LIVE / "broering_vr1466078.live.ocr.txt"
    if not path.exists():
        pytest.skip("live-ocr Broering fehlt")
    rows = extract_table_line_items(path.read_text(encoding="utf-8"))
    assert len(rows) == 1
    assert rows[0]["artikel_nr"] == "VL2439509"
    assert rows[0]["menge"] == "50000"
    assert rows[0]["einheit"] == "kg"
    assert rows[0].get("einzelpreis") == "23.10"
    # Roh-OCR darf nicht als Datumsfragment 081 im Preis landen
    assert rows[0].get("einzelpreis") != "081"


def test_birkhoff_live_spaced_decimal_menge():
    """Live-OCR „25.200, 00 kg“ (Leerzeichen nach Komma) → 25200.00, nicht Menge 00."""
    path = LIVE / "birkhoff_227627.live.ocr.txt"
    if not path.exists():
        pytest.skip("live-ocr Birkhoff fehlt")
    rows = extract_table_line_items(path.read_text(encoding="utf-8"))
    assert len(rows) == 2
    assert rows[0]["menge"] == "1980.00"
    assert rows[0]["einheit"] == "kg"
    assert rows[1]["artikel_nr"] == "291040"
    assert rows[1]["menge"] == "25200.00"
    assert rows[1]["einheit"] == "kg"
    assert "25.200" not in (rows[1].get("artikel_name") or "")


def test_hofmeister_st_positions():
    ocr = _load("re_hofmeister_3420010919.ocr.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 3
    assert rows[0]["einheit"] == "Stk"
    assert rows[0]["menge"] == "24"


def test_hofmeister_mixed_m_and_st_seven_lines():
    ocr = _load("re_hofmeister_3715298017.ocr.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 7
    assert rows[0]["einheit"] == "M"
    assert rows[1]["einheit"] == "Stk"


def test_telekom_header_empty_positions_ok(monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "stub")
    ocr = _load("re_telekom_11769046012511.ocr.txt")
    assert extract_table_line_items(ocr) == []
    parsed = DMSParser().parse(ocr)["fields"]
    assert "Telekom" in (parsed.get("supplier") or "")
    assert "11769046012511" in (parsed.get("invoice_number") or "").replace(" ", "")
    assert parsed.get("total") == "216.34"
    fields, gaps = enrich_parsed_fields_with_positions(
        parsed, ocr, force_kind=DokumentTyp.EINGANGSRECHNUNG
    )
    assert fields["positionen"] == []
    assert GAP_REGEX_NO_LINES in gaps
    assert classify_document(parsed, ocr)["direction"] == "incoming"


def test_deuka_korrektur_gutschrift_negative_line():
    ocr = _load("re_deuka_korrektur_600350.ocr.txt")
    assert document_kind_from_existing(ocr) == DokumentTyp.GUTSCHRIFT.value
    rows = extract_table_line_items(ocr)
    assert len(rows) == 1
    assert rows[0]["artikel_nr"] == "434452000"
    assert rows[0]["menge"] == "-8722.00"
    assert classify_document(DMSParser().parse(ocr)["fields"], ocr)["direction"] == "incoming"


def test_zill_stueck_and_maut_supplier_not_folkerts():
    ocr = _load("re_zill_r2609060.ocr.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 2
    assert rows[0]["artikel_nr"] == "951215"
    assert rows[1]["artikel_name"] == "Maut"
    parsed = DMSParser().parse(ocr)["fields"]
    assert "Zill" in (parsed.get("supplier") or "")
    assert "folkerts" not in (parsed.get("supplier") or "").casefold()


def test_webfleet_ten_service_lines_unit_x():
    ocr = _load("re_webfleet_11857345.ocr.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 10
    assert all(r.get("einheit") == "x" for r in rows)
    assert rows[0]["artikel_name"].startswith("Monatliche Nutzung")
    assert "Monatliche" not in (rows[0].get("artikel_nr") or "")
    parsed = DMSParser().parse(ocr)["fields"]
    assert "Webfleet" in (parsed.get("supplier") or "")
    assert "11857345" in (parsed.get("invoice_number") or "")


def test_folkerts_outgoing_lieferschein_two_st_lines():
    ocr = _load("ls_folkerts_2607001.ocr.txt")
    assert document_kind_from_existing(ocr) == DokumentTyp.LIEFERSCHEIN.value
    rows = extract_table_line_items(ocr)
    assert len(rows) == 2
    assert rows[0]["artikel_nr"] == "185030"
    assert rows[0]["menge"] == "15"
    assert rows[0]["einheit"] == "Stk"
    assert "HOBEL" in rows[0]["artikel_name"].upper()
    assert rows[1]["artikel_nr"] == "191075"
    parsed = DMSParser().parse(ocr)["fields"]
    assert "2607001" in (parsed.get("invoice_number") or "")


def test_dgo_seven_psm_lines_across_ls_groups():
    ocr = _load("re_dgo_10043771.ocr.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 7
    assert rows[0]["artikel_nr"] == "7720178"
    assert rows[0]["einheit"] == "l"
    assert rows[1]["einheit"] == "Stk"
    assert rows[-1]["artikel_name"].startswith("Durano")
    assert sum(1 for r in rows if r["artikel_nr"] == "7720178") == 2


def test_sica_five_stueck_lines():
    ocr = _load("re_sica_26648052.ocr.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 5
    assert rows[0]["artikel_nr"] == "17-697"
    assert rows[0]["menge"] == "4"
    assert rows[0]["einheit"] == "Stk"
    assert rows[-1]["artikel_name"].startswith("Anlieferung")
    parsed = DMSParser().parse(ocr)["fields"]
    assert "Sica" in (parsed.get("supplier") or "")
    assert "26648052" in (parsed.get("invoice_number") or "")
    assert parsed.get("total") == "209.02"


def test_bat_two_saatgut_lines_eh_and_kg():
    ocr = _load("re_bat_3569308.ocr.txt")
    rows = extract_table_line_items(ocr)
    assert len(rows) == 2
    assert rows[0]["artikel_nr"] == "506917-11"
    assert rows[0]["menge"] == "48.00"
    assert rows[0]["einheit"] == "Eh"
    assert rows[1]["artikel_nr"] == "502260-14"
    assert rows[1]["menge"] == "250.00"
    assert rows[1]["einheit"] == "kg"
    parsed = DMSParser().parse(ocr)["fields"]
    assert "BAT" in (parsed.get("supplier") or "")
    assert "3569308" in (parsed.get("invoice_number") or "")
    assert parsed.get("total") == "3769.48"
    proposals = build_article_create_proposals(
        extract_line_items({"positionen": rows}), {0: [], 1: []}
    )
    assert all(p["status"] == "propose" for p in proposals)


@pytest.mark.parametrize(
    ("fixture", "min_rows"),
    [
        ("re_broering_vr1466078.ocr.txt", 1),
        ("re_birkhoff_227627.ocr.txt", 2),
        ("re_hofmeister_3420010919.ocr.txt", 3),
        ("re_hofmeister_3715298017.ocr.txt", 7),
        ("re_zill_r2609060.ocr.txt", 2),
        ("re_deuka_korrektur_600350.ocr.txt", 1),
        ("re_webfleet_11857345.ocr.txt", 10),
        ("ls_folkerts_2607001.ocr.txt", 2),
        ("re_dgo_10043771.ocr.txt", 7),
        ("re_sica_26648052.ocr.txt", 5),
        ("re_bat_3569308.ocr.txt", 2),
    ],
)
def test_dms_parser_attaches_positionen(fixture, min_rows):
    ocr = _load(fixture)
    parsed = DMSParser().parse(ocr)
    pos = parsed["fields"].get("positionen") or []
    assert len(pos) >= min_rows


@pytest.mark.parametrize(
    ("live_name", "min_rows", "must_contain"),
    [
        ("sica_26648052.live.ocr.txt", 5, "17-697"),
        ("dgo_10043771.live.ocr.txt", 7, "7720178"),
        ("deuka_korrektur_600350.live.ocr.txt", 1, "434452000"),
        ("hofmeister_3715298017.live.ocr.txt", 7, "76883307"),
        ("zill_r2609060.live.ocr.txt", 2, "951215"),
        ("webfleet_11857345.live.ocr.txt", 10, None),
        ("folkerts_ls_2607001.live.ocr.txt", 2, "185030"),
        ("hofmeister_3420010919.live.ocr.txt", 3, "MB29500301"),
        ("broering_vr1466078.live.ocr.txt", 1, "VL2439509"),
        ("birkhoff_227627.live.ocr.txt", 2, "291040"),
    ],
)
def test_live_ocr_user_invoices_yield_positions(live_name, min_rows, must_contain):
    """Live-Tesseract der User-Uploads — zuvor oft 0/Müll-Zeilen."""
    path = LIVE / live_name
    if not path.exists():
        pytest.skip(f"live-ocr {live_name} fehlt")
    ocr = path.read_text(encoding="utf-8")
    rows = extract_table_line_items(ocr)
    assert len(rows) >= min_rows
    if must_contain:
        blob = " ".join(
            f"{r.get('artikel_nr') or ''} {r.get('artikel_name') or ''}" for r in rows
        )
        assert must_contain in blob
    parsed = DMSParser().parse(ocr)
    assert len(parsed["fields"].get("positionen") or []) >= min_rows


def test_live_deuka_not_garbage_price_as_name():
    path = LIVE / "deuka_korrektur_600350.live.ocr.txt"
    if not path.exists():
        pytest.skip("live-ocr deuka fehlt")
    rows = extract_table_line_items(path.read_text(encoding="utf-8"))
    assert len(rows) == 1
    assert rows[0]["artikel_nr"] == "434452000"
    assert "Nordkraft" in rows[0]["artikel_name"]
    assert rows[0]["menge"] == "-8722.00"
    assert "EUR" not in rows[0]["artikel_name"]


def test_live_dgo_durano_menge_is_1280_not_anzahl():
    path = LIVE / "dgo_10043771.live.ocr.txt"
    if not path.exists():
        pytest.skip("live-ocr dgo fehlt")
    rows = extract_table_line_items(path.read_text(encoding="utf-8"))
    durano = [r for r in rows if r.get("artikel_nr") == "7719142"]
    assert len(durano) == 1
    assert durano[0]["menge"] == "1280.00"
    assert durano[0]["einheit"] == "l"
