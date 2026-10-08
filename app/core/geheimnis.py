"""Geheimnisse (Passwoerter, Tokens) verschluesselt ablegen — AES-256-GCM.

Bis zum 08.10.2026 lag das IMAP-Passwort des CRM-Connectors im Klartext in
``domain_shared.tenants.settings``; der vorhandene ``encryption_service`` erzeugt
ohne gesetzten Schluessel bei jedem Start einen neuen — ein damit gespeichertes
Geheimnis waere nach dem Neustart unlesbar.

Hier gilt:

* Schluessel aus ``VALEO_SECRET_KEY``: 32 Byte als Base64 (``openssl rand -base64 32``)
  oder eine Passphrase ab 32 Zeichen (SHA-256). **Ohne Schluessel wird nichts
  gespeichert** — kein Klartext-, kein Wegwerf-Rueckfall.
* Jedes Chiffrat ist an Mandant und Zweck gebunden (AAD): ein Passwort aus Haus A
  laesst sich nicht als Passwort von Haus B entschluesseln.
* Format ``v1:<base64(nonce || chiffrat+tag)>``.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.exceptions import DomainError

_PRAEFIX = "v1:"


class GeheimnisNichtEingerichtet(DomainError):
    """``VALEO_SECRET_KEY`` fehlt oder ist zu schwach; Geheimnisse werden nicht gespeichert (503)."""

    http_status = 503
    error_code = "SECRET_KEY_MISSING"


class GeheimnisUngueltig(RuntimeError):
    """Chiffrat beschaedigt, mit anderem Schluessel oder fuer anderen Mandanten/Zweck erstellt."""


def _schluessel() -> bytes:
    roh = (os.getenv("VALEO_SECRET_KEY") or "").strip()
    if not roh:
        raise GeheimnisNichtEingerichtet(
            "VALEO_SECRET_KEY ist nicht gesetzt; Zugangsdaten werden nicht gespeichert."
        )
    try:
        schluessel = base64.b64decode(roh, validate=True)
        if len(schluessel) == 32:
            return schluessel
    except (binascii.Error, ValueError):
        pass
    if len(roh) >= 32:
        return hashlib.sha256(roh.encode("utf-8")).digest()
    raise GeheimnisNichtEingerichtet("VALEO_SECRET_KEY ist zu kurz (32 Byte Base64 oder mind. 32 Zeichen).")


def _aad(tenant_id: str, zweck: str) -> bytes:
    return f"{tenant_id}|{zweck}".encode("utf-8")


def ist_chiffrat(wert: object) -> bool:
    return isinstance(wert, str) and wert.startswith(_PRAEFIX)


def verschluesseln(klartext: str, *, tenant_id: str, zweck: str) -> str:
    nonce = os.urandom(12)
    chiffrat = AESGCM(_schluessel()).encrypt(nonce, klartext.encode("utf-8"), _aad(tenant_id, zweck))
    return _PRAEFIX + base64.b64encode(nonce + chiffrat).decode("ascii")


def entschluesseln(chiffrat: str, *, tenant_id: str, zweck: str) -> str:
    if not ist_chiffrat(chiffrat):
        raise GeheimnisUngueltig("Kein verschluesseltes Geheimnis.")
    try:
        roh = base64.b64decode(chiffrat[len(_PRAEFIX):], validate=True)
        klar = AESGCM(_schluessel()).decrypt(roh[:12], roh[12:], _aad(tenant_id, zweck))
    except (InvalidTag, binascii.Error, ValueError) as fehler:
        raise GeheimnisUngueltig("Geheimnis nicht lesbar (anderer Schluessel, Mandant oder Zweck).") from fehler
    return klar.decode("utf-8")


def signieren(nachricht: str) -> str:
    """HMAC-SHA256 ueber den Schluessel (z. B. fuer OAuth-``state``)."""
    return hmac.new(_schluessel(), nachricht.encode("utf-8"), hashlib.sha256).hexdigest()


def signatur_gueltig(nachricht: str, signatur: str) -> bool:
    return hmac.compare_digest(signieren(nachricht), signatur or "")
