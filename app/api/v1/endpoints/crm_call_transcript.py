"""KIM Telefon-Transkript-Connector — Anrufe automatisch als Kontakt erfassen.

Nach Anrufende meldet die Telefonie-Schicht (TAPI-Bridge / Telefonanlage) das
Gespräch hierher. Drei Eingangsvarianten:
  • `transcript`  — fertiger Text (Telefonanlage liefert bereits Transkript)  → direkt
  • `audioUrl`    — URL der Aufnahme → wird geladen und per STT transkribiert
  • `audioBase64` — Aufnahme inline → per STT transkribiert

STT ist anbieterunabhängig (OpenAI-kompatibler faster-whisper-Server, siehe
SttClient). Ohne STT-Konfiguration funktioniert der reine `transcript`-Weg.
Daraus wird via Auto-Capture (channel='telefon') ein Kontakt — idempotent über
die Call-ID (`verweis`); nicht zuordenbare Anrufe gehen in die Klärfall-Inbox.
"""

from __future__ import annotations

import base64
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_auto_capture_service import CrmAutoCaptureService
from app.services.stt_client import SttClient

router = APIRouter(prefix="/crm/kim", tags=["crm", "kim", "360"])


class CallTranscriptIn(BaseModel):
    callId: Optional[str] = None           # → verweis (Idempotenz)
    direction: str = "incoming"            # incoming | outgoing
    caller: Optional[str] = None           # Anrufer-Nummer
    called: Optional[str] = None           # angerufene Nummer
    kundenNr: Optional[str] = None
    transcript: Optional[str] = None       # fertiger Text
    audioUrl: Optional[str] = None         # Aufnahme-URL → STT
    audioBase64: Optional[str] = None      # Aufnahme inline → STT
    audioContentType: str = "audio/wav"


@router.post("/call-transcript", response_model=dict, summary="Anruf-Transkript als Kontakt erfassen (Text oder Audio→STT)")
def call_transcript(
    body: CallTranscriptIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    transcript = (body.transcript or "").strip()

    # Audio → STT, falls kein fertiger Text vorliegt.
    if not transcript and (body.audioUrl or body.audioBase64):
        stt = SttClient.for_tenant(db, tenant_id)
        if not stt.configured:
            return {"status": "stt_unconfigured",
                    "detail": "Kein STT-Server konfiguriert (STT_BASE_URL). "
                              "Bitte fertigen Transkript-Text senden."}
        audio: Optional[bytes] = None
        if body.audioBase64:
            try:
                audio = base64.b64decode(body.audioBase64)
            except Exception:
                return {"status": "bad_audio", "detail": "audioBase64 nicht dekodierbar"}
        elif body.audioUrl:
            audio = SttClient.fetch_audio(body.audioUrl)
        transcript = (stt.transcribe(audio or b"", content_type=body.audioContentType) or "").strip()
        if not transcript:
            return {"status": "stt_failed", "detail": "Transkription leer/fehlgeschlagen"}

    if not transcript:
        return {"status": "empty", "detail": "Weder transcript noch audio übergeben"}

    # Gegenseite: Anrufer bei eingehend, angerufene Nummer bei ausgehend.
    is_incoming = (body.direction or "").lower().startswith(("in", "ein"))
    peer = body.caller if is_incoming else (body.called or body.caller)

    return CrmAutoCaptureService(db, tenant_id).capture(
        channel="telefon",
        direction=body.direction,
        peer=peer,
        content=transcript,
        kunden_nr=body.kundenNr,
        verweis=body.callId,
        bediener="AUTO",
    )
