"""Unit-Tests: Einkauf OCR-Extraktions-Hilfen (ohne echte PDF-Pipeline)."""

from __future__ import annotations

from app.einkauf.ocr_invoice import extract_invoice_pdf, resolve_pdf_bytes


def test_stub_engine_has_sample_positions_and_model_tag():
    r = extract_invoice_pdf(file_id="file123stub", engine="stub", pdf_bytes=None)
    assert r["extracted_data"]["positionen"], "Stub soll Demo-Positionen liefern"
    assert r["confidence_score"] >= 0.9
    assert "stub" in r["ocr_model"].lower()


def test_pdfplumber_without_upload_dir_uses_fallback():
    r = extract_invoice_pdf(file_id="missing-upload", engine="pdfplumber", pdf_bytes=None)
    assert "fallback" in r["ocr_model"]
    texts = [w.lower() for w in r.get("extraction_warnings", [])]
    assert any("kein pdf" in t or "upload" in t for t in texts)


def test_resolve_pdf_bytes_none_without_env(tmp_path, monkeypatch):  # noqa: ARG001
    monkeypatch.delenv("EINKAUF_OCR_UPLOAD_DIR", raising=False)
    assert resolve_pdf_bytes("any.pdf") is None


def test_resolve_pdf_reads_from_upload_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("EINKAUF_OCR_UPLOAD_DIR", str(tmp_path))
    p = tmp_path / "inv1.pdf"
    p.write_bytes(b"%PDF-1.4 dummy")
    blob = resolve_pdf_bytes("inv1.pdf")
    assert blob is not None and blob.startswith(b"%PDF")
