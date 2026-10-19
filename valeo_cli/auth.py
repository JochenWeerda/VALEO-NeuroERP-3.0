"""Anmeldung der CLI: OAuth 2.0 Device Authorization Grant (RFC 8628) gegen den Identity Provider.

Der Mensch meldet sich im Browser an — mit SSO, MFA oder Passkey, wie in der Maske. Die CLI sieht nie ein
Passwort und erhaelt ein Token **dieser** Person; es gibt keinen Dienstschluessel der CLI. Fuer Automatisierung
kann ein anderweitig ausgestelltes Token ueber ``VALEO_ACCESS_TOKEN`` uebergeben werden (z. B. eine
Agentenidentitaet) — dann gelten die Agentensperren der Maskenaktionen.

Die Sitzung (Access- und Refresh-Token) liegt nur im Benutzerprofil, Datei nur fuer den Eigentuemer lesbar.
Der Realm rotiert Refresh-Tokens (``revokeRefreshToken``); jede Erneuerung schreibt deshalb sofort zurueck.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import httpx

DEFAULT_ISSUER = "http://localhost:8080/realms/valeo-neuro-erp"
DEFAULT_CLIENT_ID = "valeo-neuro-erp-cli"
DEVICE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"


class AuthError(RuntimeError):
    """Anmeldung fehlgeschlagen oder abgelaufen — Text ist fuer Menschen, ohne Token-Inhalte."""


@dataclass(frozen=True)
class Settings:
    issuer: str
    client_id: str
    session_file: Path

    @classmethod
    def from_env(cls) -> "Settings":
        default = Path(os.environ.get("APPDATA") or Path.home() / ".config") / "valeo" / "cli-sitzung.json"
        return cls(issuer=os.environ.get("VALEO_OIDC_ISSUER", DEFAULT_ISSUER).rstrip("/"),
                   client_id=os.environ.get("VALEO_CLI_CLIENT_ID", DEFAULT_CLIENT_ID),
                   session_file=Path(os.environ.get("VALEO_CLI_SESSION", default)))


def claims(token: str) -> dict:
    """Nur zur Anzeige und fuer die Agentenpruefung der CLI. Gueltig macht ein Token allein der Server."""
    try:
        payload = token.split(".")[1]
        return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except (IndexError, ValueError):
        return {}


def _discovery(http: httpx.Client, settings: Settings) -> dict:
    response = http.get(f"{settings.issuer}/.well-known/openid-configuration")
    if response.status_code != 200:
        raise AuthError(f"Identity Provider nicht erreichbar ({response.status_code}).")
    return response.json()


def _save(settings: Settings, session: dict) -> None:
    settings.session_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = settings.session_file.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(session, handle)
    os.replace(tmp, settings.session_file)


def _load(settings: Settings) -> dict | None:
    try:
        session = json.loads(settings.session_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if session.get("issuer") != settings.issuer or session.get("client_id") != settings.client_id:
        return None  # Sitzung eines anderen Providers oder Clients nie wiederverwenden.
    return session


def _session_from(settings: Settings, tokens: dict, now: float) -> dict:
    if not tokens.get("access_token"):
        raise AuthError("Identity Provider lieferte kein Access-Token.")
    return {"issuer": settings.issuer, "client_id": settings.client_id,
            "access_token": tokens["access_token"], "refresh_token": tokens.get("refresh_token"),
            "expires_at": now + int(tokens.get("expires_in", 60))}


def login(http: httpx.Client, settings: Settings, *, announce: Callable[[str], None] = print,
          open_browser: bool = True, sleep: Callable[[float], None] = time.sleep,
          clock: Callable[[], float] = time.time) -> dict:
    """Device-Flow: Code anzeigen, Browser oeffnen, auf die Anmeldung warten, Sitzung speichern."""
    meta = _discovery(http, settings)
    device_endpoint = meta.get("device_authorization_endpoint")
    if not device_endpoint:
        raise AuthError("Der Identity Provider bietet keinen Device-Flow an.")
    # PKCE auch im Device-Flow: Der Realm verlangt S256 fuer jeden oeffentlichen Client. Nur wer den
    # Verifier haelt, kann den bestaetigten Code gegen ein Token tauschen.
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    start = http.post(device_endpoint, data={"client_id": settings.client_id, "scope": "openid",
                                             "code_challenge": challenge, "code_challenge_method": "S256"})
    if start.status_code != 200:
        error = start.json().get("error", "") if start.headers.get("content-type", "").startswith("application/json") else ""
        raise AuthError(f"Device-Anmeldung abgelehnt ({start.status_code} {error}). Ist der Client "
                        f"{settings.client_id} im Identity Provider eingerichtet?")
    grant = start.json()
    url = grant.get("verification_uri_complete") or grant["verification_uri"]
    announce(f"Anmelden unter {grant['verification_uri']} mit Code {grant['user_code']}")
    if open_browser:
        webbrowser.open(url)
    interval = int(grant.get("interval", 5))
    deadline = clock() + int(grant.get("expires_in", 600))
    while clock() < deadline:
        sleep(interval)
        response = http.post(meta["token_endpoint"], data={
            "grant_type": DEVICE_GRANT, "device_code": grant["device_code"], "client_id": settings.client_id,
            "code_verifier": verifier})
        if response.status_code == 200:
            session = _session_from(settings, response.json(), clock())
            _save(settings, session)
            return session
        error = response.json().get("error") if response.content else None
        if error == "authorization_pending":
            continue
        if error == "slow_down":
            interval += 5
            continue
        if error == "access_denied":
            raise AuthError("Anmeldung im Browser abgelehnt.")
        if error == "expired_token":
            break
        raise AuthError(f"Anmeldung fehlgeschlagen ({response.status_code} {error or ''}).".strip())
    raise AuthError("Der Anmeldecode ist abgelaufen. Bitte erneut anmelden.")


def access_token(http: httpx.Client, settings: Settings, *, clock: Callable[[], float] = time.time) -> str:
    """Gueltiges Token: aus ``VALEO_ACCESS_TOKEN`` oder aus der Sitzung, bei Bedarf erneuert."""
    supplied = os.environ.get("VALEO_ACCESS_TOKEN")
    if supplied:
        return supplied.strip()
    session = _load(settings)
    if session is None:
        raise AuthError("Nicht angemeldet. Bitte zuerst: python -m valeo_cli anmelden")
    if session["expires_at"] - 30 > clock():
        return session["access_token"]
    if not session.get("refresh_token"):
        raise AuthError("Sitzung abgelaufen. Bitte erneut anmelden.")
    meta = _discovery(http, settings)
    response = http.post(meta["token_endpoint"], data={
        "grant_type": "refresh_token", "refresh_token": session["refresh_token"], "client_id": settings.client_id})
    if response.status_code != 200:
        settings.session_file.unlink(missing_ok=True)
        raise AuthError("Sitzung abgelaufen oder widerrufen. Bitte erneut anmelden.")
    renewed = _session_from(settings, response.json(), clock())
    _save(settings, renewed)
    return renewed["access_token"]


def logout(http: httpx.Client, settings: Settings) -> bool:
    """Sitzung beim Provider beenden und lokal loeschen. ``False``: es gab keine."""
    session = _load(settings)
    if session is None:
        settings.session_file.unlink(missing_ok=True)
        return False
    if session.get("refresh_token"):
        meta = _discovery(http, settings)
        endpoint = meta.get("end_session_endpoint")
        if endpoint:
            response = http.post(endpoint, data={"client_id": settings.client_id,
                                                 "refresh_token": session["refresh_token"]})
            if response.status_code not in (200, 204):
                raise AuthError(f"Abmelden beim Provider fehlgeschlagen ({response.status_code}); "
                                "lokale Sitzung bleibt bestehen.")
    settings.session_file.unlink(missing_ok=True)
    return True
