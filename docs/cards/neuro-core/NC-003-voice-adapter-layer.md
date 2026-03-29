# NC-003 — Voice Adapter Layer

**Lane:** Neuro-Core
**Prioritaet:** P1 (Architektur-kritisch)
**Status:** umgesetzt

## Kontext
Voice-Kanaele haben andere Anforderungen als textbasierte Kanaele — Echtzeit-Latenz unter 500ms, Sprecherwechsel-Erkennung und Audio-Streaming. Ein generischer Chat-Adapter reicht dafuer nicht aus.

## Loesung
Eine spezialisierte Adapter-Schicht mit STT/TTS-Adaptern, Turn Manager und Latency Controller verbindet Voice-Kanaele mit dem Neuro-Core Gateway und garantiert Echtzeit-Faehigkeit.

## Dateien
- `app/services/voice_adapter.py` — Kern-Service
- `app/api/v1/endpoints/neuro_voice.py` — REST-API
- `docs/workflows/nc-003-voice-adapter-layer.md` — Workflow-Doku
