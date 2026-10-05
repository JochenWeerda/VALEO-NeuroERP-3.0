"""GHSA-42vr-xj54-vc7v: malformed pre-verification payload is a token error."""
import base64

import jwt
import pytest


def test_deep_unverified_payload_cannot_escape_as_recursion_error():
    def encoded(value):
        return base64.urlsafe_b64encode(value).rstrip(b"=")

    token = b".".join((
        encoded(b'{"alg":"HS256","typ":"JWT"}'),
        encoded(b"[" * 20_000 + b"]" * 20_000),
        encoded(b"invalid-signature"),
    )).decode("ascii")
    # Pre-verification parsing is also used by PyJWKClient before key lookup.
    with pytest.raises(jwt.DecodeError):
        jwt.decode(token, options={"verify_signature": False})
