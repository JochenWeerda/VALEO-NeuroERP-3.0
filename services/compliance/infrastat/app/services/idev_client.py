"""Client zum Destatis IDEV-Portal (Session + Zertifikate)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)


class IdevClient:
    """Stellt einen einfachen Session-basierten Zugriff auf das IDEV-Portal bereit."""

    def __init__(
        self,
        base_url: str,
        username: str | None,
        password: str | None,
        *,
        client_cert: Tuple[str, str] | None = None,
        verify_ssl: bool = True,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._timeout = timeout
        self._cert = client_cert
        self._verify_ssl = verify_ssl
        self._client: httpx.AsyncClient | None = None
        self._session_initialized = False

    @classmethod
    def from_settings(cls, settings) -> "IdevClient":
        cert_tuple = None
        if settings.SUBMISSION_CLIENT_CERT and settings.SUBMISSION_CLIENT_KEY:
            cert_tuple = (settings.SUBMISSION_CLIENT_CERT, settings.SUBMISSION_CLIENT_KEY)
        return cls(
            base_url=settings.SUBMISSION_BASE_URL,
            username=settings.SUBMISSION_USERNAME,
            password=settings.SUBMISSION_PASSWORD,
            client_cert=cert_tuple,
            verify_ssl=settings.SUBMISSION_VERIFY_SSL,
        )

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                cert=self._cert,
                verify=self._verify_ssl,
            )
        return self._client

    async def ensure_session(self) -> None:
        if self._session_initialized:
            return
        if not self._username or not self._password:
            logger.debug("IDEV-Client ohne Credentials initialisiert (nur Dry-Run möglich).")
            return

        client = await self._ensure_client()
        try:
            # 1) Login-Seite laden (Session-Cookie)
            await client.get("/#/login")

            # 2) Authentifizierung durchführen (API Endpoint laut IDEV-Doku)
            response = await client.post(
                "/api/login",
                json={"username": self._username, "password": self._password},
            )
            response.raise_for_status()
            self._session_initialized = True
            logger.info("IDEV-Login erfolgreich.")
        except httpx.HTTPError as exc:
            logger.error("IDEV-Login fehlgeschlagen: %s", exc, exc_info=True)
            raise

    async def upload(self, payload: str, submission_id: str) -> Dict[str, Any]:
        client = await self._ensure_client()

        if self._username and self._password:
            await self.ensure_session()

        files = {"file": ("instat.xml", payload, "application/xml")}
        data = {"submission_id": submission_id}

        response = await client.post("/api/upload", files=files, data=data)
        response.raise_for_status()
        logger.info("IDEV Upload erfolgreich (submission_id=%s)", submission_id)
        json_payload = response.json()
        json_payload.setdefault("status", "delivered")
        json_payload.setdefault("success", True)
        return json_payload

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
            self._session_initialized = False

