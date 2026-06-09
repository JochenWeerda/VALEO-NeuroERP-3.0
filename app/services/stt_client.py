"""Speech-to-Text-Client (anbieterunabhängig, OpenAI-kompatibel).

Spricht jeden Server an, der die OpenAI-Audio-API implementiert
(`POST {base_url}/audio/transcriptions`) — z. B. die freien, selbst-hostbaren
faster-whisper-Server:
  • SYSTRAN/faster-whisper  + faster-whisper-server (kesjam)
  • hwdsl2/docker-whisper   (OpenAI-kompatibel, GPU/CPU)
  • OpenAI-Cloud (whisper-1) falls gewünscht.

Konfiguration über Umgebungsvariablen (kein Pflicht-Setup — ohne Config liefert
`transcribe()` None, sodass die Telefonie-Integration ohne STT weiterläuft und
nur reinen Transkript-Text akzeptiert):
  STT_BASE_URL   z. B. http://whisper:8000/v1   (Default: leer = deaktiviert)
  STT_MODEL      z. B. Systran/faster-whisper-small  (Default: whisper-1)
  STT_API_KEY    optional (lokale Server brauchen meist keinen)
  STT_LANGUAGE   z. B. de                       (Default: de)
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class SttClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        language: Optional[str] = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("STT_BASE_URL", "")).rstrip("/")
        self.model = model or os.getenv("STT_MODEL", "whisper-1")
        self.api_key = api_key or os.getenv("STT_API_KEY", "")
        self.language = language or os.getenv("STT_LANGUAGE", "de")
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.base_url)

    def transcribe(
        self, audio: bytes, filename: str = "call.wav", content_type: str = "audio/wav"
    ) -> Optional[str]:
        """Transkribiert Audio-Bytes. Liefert den Text oder None (nicht
        konfiguriert / Fehler) — der Aufrufer behandelt None als 'kein Transkript'."""
        if not self.configured or not audio:
            return None
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        data = {"model": self.model, "response_format": "text"}
        if self.language:
            data["language"] = self.language
        try:
            resp = httpx.post(
                f"{self.base_url}/audio/transcriptions",
                headers=headers,
                data=data,
                files={"file": (filename, audio, content_type)},
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001 — STT ist best-effort, Fehler => None
            logger.warning("STT transcription failed: %s", exc)
            return None
        text = resp.text.strip()
        # Manche Server liefern JSON {"text": "..."} trotz response_format=text.
        if text.startswith("{"):
            try:
                import json

                text = (json.loads(text).get("text") or "").strip()
            except Exception:
                pass
        return text or None

    @staticmethod
    def fetch_audio(url: str, timeout: float = 60.0) -> Optional[bytes]:
        """Lädt eine Aufnahme von einer URL (z. B. Recording-Store der Telefonanlage)."""
        try:
            resp = httpx.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.content
        except Exception as exc:  # noqa: BLE001
            logger.warning("STT fetch_audio failed (%s): %s", url, exc)
            return None
