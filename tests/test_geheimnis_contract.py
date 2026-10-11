"""Real AEAD contracts without database setup or probabilistic substring checks."""
import base64
from types import SimpleNamespace

import pytest

from app.core import geheimnis


@pytest.fixture(autouse=True)
def key(monkeypatch):
    monkeypatch.setenv("VALEO_SECRET_KEY", base64.b64encode(b"k" * 32).decode())


def encrypt():
    return geheimnis.verschluesseln("pw", tenant_id="probe-a", zweck="mailkonto")


def decrypt(value, tenant_id="probe-a", zweck="mailkonto"):
    return geheimnis.entschluesseln(value, tenant_id=tenant_id, zweck=zweck)


def test_ciphertext_format_and_roundtrip():
    value = encrypt()
    assert value.startswith("v1:")
    binary = base64.b64decode(value[3:], validate=True)
    assert len(binary) == 12 + len(b"pw") + 16  # Nonce, encrypted bytes, GCM tag.
    assert decrypt(value) == "pw"


def test_short_plaintext_can_coincide_with_base64_nonce(monkeypatch):
    # A valid nonce starting with these bytes encodes to "pw". The previous
    # substring assertion rejected legitimate random ciphertext in real CI.
    nonce = bytes.fromhex("a70000000000000000000000")
    monkeypatch.setattr(geheimnis, "os", SimpleNamespace(
        urandom=lambda size: nonce, getenv=lambda name: base64.b64encode(b"k" * 32).decode()
    ))
    value = encrypt()
    assert "pw" in value
    assert decrypt(value) == "pw"


@pytest.mark.parametrize("tenant_id,zweck", [("probe-b", "mailkonto"), ("probe-a", "imap")])
def test_ciphertext_bound_to_tenant_and_purpose(tenant_id, zweck):
    with pytest.raises(geheimnis.GeheimnisUngueltig):
        decrypt(encrypt(), tenant_id=tenant_id, zweck=zweck)


def test_ciphertext_bound_to_key(monkeypatch):
    value = encrypt()
    monkeypatch.setenv("VALEO_SECRET_KEY", base64.b64encode(b"j" * 32).decode())
    with pytest.raises(geheimnis.GeheimnisUngueltig):
        decrypt(value)


@pytest.mark.parametrize("offset", [0, 12, -1])
def test_tampering_rejected(offset):
    value = encrypt()
    binary = bytearray(base64.b64decode(value[3:]))
    binary[offset] ^= 1
    with pytest.raises(geheimnis.GeheimnisUngueltig):
        decrypt("v1:" + base64.b64encode(binary).decode())


def test_same_plaintext_has_fresh_nonce():
    first, second = encrypt(), encrypt()
    assert first != second
    assert decrypt(first) == decrypt(second) == "pw"


def test_missing_key_rejects_encryption(monkeypatch):
    monkeypatch.delenv("VALEO_SECRET_KEY")
    with pytest.raises(geheimnis.GeheimnisNichtEingerichtet):
        encrypt()
