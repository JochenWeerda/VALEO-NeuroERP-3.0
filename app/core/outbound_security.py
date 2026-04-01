"""
Shared outbound HTTP target validation for SSRF-sensitive integrations.
"""

from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit, urlunsplit

from app.core.config import settings

_DISALLOWED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
}

_DISALLOWED_HOST_SUFFIXES = (
    ".localhost",
    ".local",
    ".internal",
)


class OutboundTargetPolicyError(ValueError):
    """Raised when an outbound URL violates the central egress policy."""


def validate_outbound_http_target(
    raw_url: str,
    *,
    allowed_schemes: tuple[str, ...] = ("http", "https"),
) -> str:
    """
    Validate an outbound HTTP target against the shared SSRF policy and
    return a normalized URL string.
    """

    parsed = urlsplit(str(raw_url).strip())
    scheme = parsed.scheme.lower()
    if scheme not in allowed_schemes:
        raise OutboundTargetPolicyError("Nur HTTP/HTTPS URLs erlaubt")

    hostname = (parsed.hostname or "").strip().lower()
    if not hostname:
        raise OutboundTargetPolicyError("Hostname fehlt")

    if hostname in _DISALLOWED_HOSTS or hostname.endswith(_DISALLOWED_HOST_SUFFIXES):
        raise OutboundTargetPolicyError("Localhost/interne Hostnamen sind nicht erlaubt")

    _validate_host_against_network_policy(hostname)
    _validate_host_against_allowlist(hostname)

    return urlunsplit(parsed)


def _validate_host_against_network_policy(hostname: str) -> None:
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return

    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    ):
        raise OutboundTargetPolicyError("Interne/Private IP-Adressen nicht erlaubt")


def _validate_host_against_allowlist(hostname: str) -> None:
    allowed_hosts = {host.strip().lower() for host in settings.OUTBOUND_HTTP_ALLOWED_HOSTS if host.strip()}
    allowed_domains = {
        domain.strip().lower().lstrip(".")
        for domain in settings.OUTBOUND_HTTP_ALLOWED_DOMAINS
        if domain.strip()
    }
    if not allowed_hosts and not allowed_domains:
        return

    if hostname in allowed_hosts:
        return

    for domain in allowed_domains:
        if hostname == domain or hostname.endswith(f".{domain}"):
            return

    raise OutboundTargetPolicyError("Zielhost ist nicht in der Outbound-Allowlist freigegeben")
