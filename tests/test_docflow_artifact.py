"""Reine Logik-Tests der Artefakt-Versionierung/Freigabe (DOM-DOC-004.2)."""

from __future__ import annotations

import pytest

from app.services.docflow_artifact_service import next_version, sha256_hex, valid_transition

pytestmark = pytest.mark.unit


def test_next_version():
    assert next_version([]) == 1
    assert next_version([1]) == 2
    assert next_version([1, 2, 3]) == 4
    assert next_version([2, 5, 3]) == 6


def test_valid_transition_vorwaerts():
    assert valid_transition("entwurf", "freigegeben") is True
    assert valid_transition("freigegeben", "archiviert") is True


def test_valid_transition_rueckwaerts_verboten():
    assert valid_transition("archiviert", "freigegeben") is False
    assert valid_transition("freigegeben", "entwurf") is False
    assert valid_transition("entwurf", "archiviert") is False  # nur über freigegeben


def test_sha256_deterministisch():
    assert sha256_hex("PDF-Inhalt v1") == sha256_hex("PDF-Inhalt v1")
    assert sha256_hex("a") != sha256_hex("b")
    assert len(sha256_hex("x")) == 64
