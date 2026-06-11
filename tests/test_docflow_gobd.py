"""Reine Logik-Tests des GoBD-Exportpakets (DOM-DOC-004.4)."""

from __future__ import annotations

import pytest

from app.services.docflow_gobd_service import build_gobd_manifest

pytestmark = pytest.mark.unit

_EVIDENCE = {
    "doc_number": "PYTEST-1", "doc_type": "sales_invoice", "status": "posted", "version": 1,
    "artefakte": [
        {"datei": "rechnung.pdf", "hash": "aaa", "typ": "pdf"},
        {"datei": "anhang.pdf", "hash": "bbb", "typ": "pdf"},
    ],
    "vorgangskette": [{"relation": "x"}],
    "buchungen": [{"typ": "journal"}],
    "luecken": [],
}


def test_manifest_revisionssicher_und_zaehlungen():
    m = build_gobd_manifest(_EVIDENCE, "2026-06-11T00:00:00Z", "KIM")
    assert m["revisionssicher"] is True
    assert m["anzahl_artefakte"] == 2 and m["buchungen"] == 1 and m["vorgangskette"] == 1
    assert m["vorgang"] == "PYTEST-1"


def test_manifest_pruefsumme_deterministisch():
    a = build_gobd_manifest(_EVIDENCE, "t", "u")["pruefsumme_sha256"]
    b = build_gobd_manifest(_EVIDENCE, "t2", "u2")["pruefsumme_sha256"]
    assert a == b and len(a) == 64  # Prüfsumme nur über Artefakt-Hashes


def test_manifest_nicht_revisionssicher_ohne_hash():
    ev = {**_EVIDENCE, "artefakte": [{"datei": "x.pdf", "hash": None, "typ": "pdf"}]}
    assert build_gobd_manifest(ev, "t", "u")["revisionssicher"] is False


def test_manifest_nicht_revisionssicher_ohne_artefakt():
    ev = {**_EVIDENCE, "artefakte": []}
    assert build_gobd_manifest(ev, "t", "u")["revisionssicher"] is False
