"""
Shared outbound HTTP target validation for SSRF-sensitive integrations.
"""

from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit, urlunsplit

from app.core.config import settings
from app.services.security_observability import security_observer

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


def _reject_outbound_target(
    message: str,
    *,
    raw_url: str,
    hostname: str | None = None,
) -> None:
    security_observer.record_event(
        category="outbound_http",
        outcome="blocked",
        severity="warning",
        message=message,
        details={
            "raw_url": str(raw_url),
            "hostname": hostname,
        },
    )
    raise OutboundTargetPolicyError(message)


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
        _reject_outbound_target("Nur HTTP/HTTPS URLs erlaubt", raw_url=raw_url)

    hostname = (parsed.hostname or "").strip().lower()
    if not hostname:
        _reject_outbound_target("Hostname fehlt", raw_url=raw_url)

    if hostname in _DISALLOWED_HOSTS or hostname.endswith(_DISALLOWED_HOST_SUFFIXES):
        _reject_outbound_target(
            "Localhost/interne Hostnamen sind nicht erlaubt",
            raw_url=raw_url,
            hostname=hostname,
        )

    _validate_host_against_network_policy(hostname, raw_url)
    _validate_host_against_allowlist(hostname, raw_url)

    return urlunsplit(parsed)


def _validate_host_against_network_policy(hostname: str, raw_url: str) -> None:
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
        _reject_outbound_target(
            "Interne/Private IP-Adressen nicht erlaubt",
            raw_url=raw_url,
            hostname=hostname,
        )


def _validate_host_against_allowlist(hostname: str, raw_url: str) -> None:
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

    _reject_outbound_target(
        "Zielhost ist nicht in der Outbound-Allowlist freigegeben",
        raw_url=raw_url,
        hostname=hostname,
    )
