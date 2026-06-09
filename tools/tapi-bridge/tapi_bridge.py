#!/usr/bin/env python3
"""VALEO NeuroERP — TAPI-/Telefonie-Bridge.

Lokaler Dienst auf dem Büro-PC: lauscht an der Telefonanlage auf eingehende
Anrufe und meldet sie an das ERP (POST /api/v1/crm/tapi/incoming). Das Frontend
pollt /crm/tapi/pending und zeigt das Anruf-Popup mit dem erkannten Kunden.

Bewusst **abhängigkeitsfrei** (nur Python-Standardbibliothek), damit der Dienst
ohne pip-Install auf jedem Windows-/Linux-Büro-PC mit Python 3.8+ läuft.

Quellen (Modus --source):
  fritzbox   FRITZ!Box-Callmonitor (TCP, Standard-Port 1012). Vorher am Telefon
             einmalig `#96*5*` wählen, um den Callmonitor zu aktivieren. Liefert
             Zeilen wie `…;RING;0;<Anrufer>;<Angerufene>;…` — der De-facto-Standard
             für Telefonie-Kopplung im deutschen Mittelstand.
  tcp-lines  Generischer Zeilen-Listener: verbindet TCP host:port und behandelt
             jede empfangene Zeile als Rufnummer (für eigene TSP-/CTI-Adapter).
  simulate   Sendet einen einzelnen Test-Anruf (zum Prüfen von Popup/Auflösung,
             ohne echte Telefonanlage).

Konfiguration über Umgebungsvariablen (oder CLI-Argumente, die Vorrang haben):
  VALEO_API_BASE   Basis-URL des ERP, z.B. http://erp-server:8000  (Default: http://localhost:8000)
  VALEO_API_TOKEN  Bearer-Token (Dev: dev-token; Prod: gültiges OIDC-Token)
  VALEO_TENANT_ID  X-Tenant-ID                                       (Default: 00000000-0000-0000-0000-000000000001)
  FRITZBOX_HOST    Hostname/IP der FRITZ!Box                         (Default: fritz.box)
  CALLMONITOR_PORT TCP-Port des Callmonitors                         (Default: 1012)

Beispiele:
  # FRITZ!Box-Callmonitor dauerhaft weiterleiten (typischer Produktivbetrieb):
  python tapi_bridge.py --source fritzbox --api-base http://erp:8000 --token dev-token

  # Einen Test-Anruf senden:
  python tapi_bridge.py --source simulate --caller 049417360 --api-base http://localhost:8000 --token dev-token
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

log = logging.getLogger("tapi-bridge")

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
RECONNECT_BACKOFF_S = (2, 5, 10, 20, 30)  # ansteigende Wartezeit bei Verbindungsabbruch


# ── ERP-Meldung ───────────────────────────────────────────────────────────────
class ErpClient:
    def __init__(self, api_base: str, token: str, tenant_id: str, timeout: float = 10.0) -> None:
        base = api_base.rstrip("/")
        self.url = base + "/api/v1/crm/tapi/incoming"
        self.transcript_url = base + "/api/v1/crm/kim/call-transcript"
        self.token = token
        self.tenant_id = tenant_id
        self.timeout = timeout

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "X-Tenant-ID": self.tenant_id,
        }

    def report_transcript(
        self,
        *,
        call_id: Optional[str],
        caller: Optional[str] = None,
        called: Optional[str] = None,
        direction: str = "incoming",
        transcript: Optional[str] = None,
        audio_url: Optional[str] = None,
        retries: int = 2,
    ) -> bool:
        """Meldet ein Anruf-Transkript nach Gesprächsende an die KIM-Auto-Capture.

        Entweder `transcript` (fertiger Text) ODER `audio_url` (Aufnahme; das ERP
        transkribiert per STT, falls STT_BASE_URL gesetzt ist) übergeben."""
        payload = {
            "callId": call_id,
            "caller": caller,
            "called": called,
            "direction": direction,
            "transcript": transcript,
            "audioUrl": audio_url,
        }
        data = json.dumps(payload).encode("utf-8")
        for attempt in range(retries + 1):
            req = urllib.request.Request(self.transcript_url, data=data, headers=self._headers(), method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    log.info("Transkript gemeldet (call_id=%s): status=%s", call_id, body.get("status"))
                    return True
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:200]
                log.error("ERP HTTP %s bei Transkript (%s): %s", exc.code, call_id, detail)
                if exc.code in (401, 403):
                    return False
            except (urllib.error.URLError, socket.timeout, ConnectionError) as exc:
                log.warning("ERP nicht erreichbar bei Transkript (%d/%d): %s", attempt + 1, retries + 1, exc)
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
        return False

    def report_call(self, caller: str, called: Optional[str] = None, retries: int = 2) -> bool:
        """Meldet einen eingehenden Anruf. Returns True bei Erfolg."""
        payload = json.dumps({"caller": caller, "called": called}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "X-Tenant-ID": self.tenant_id,
        }
        for attempt in range(retries + 1):
            req = urllib.request.Request(self.url, data=payload, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    kunde = body.get("kunde_name") or "unbekannter Anrufer"
                    log.info("Anruf gemeldet: %s → %s (call_id=%s)", caller, kunde, body.get("id"))
                    return True
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:200]
                log.error("ERP HTTP %s bei Anrufmeldung (%s): %s", exc.code, caller, detail)
                if exc.code in (401, 403):
                    log.error("Authentifizierung fehlgeschlagen — Token/Tenant prüfen. Kein Retry.")
                    return False
            except (urllib.error.URLError, socket.timeout, ConnectionError) as exc:
                log.warning("ERP nicht erreichbar (Versuch %d/%d): %s", attempt + 1, retries + 1, exc)
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
        return False


# ── Quellen ──────────────────────────────────────────────────────────────────
def parse_fritzbox_line(line: str) -> Optional[dict]:
    """Parst eine FRITZ!Box-Callmonitor-Zeile. Liefert {caller, called} nur für
    eingehende, klingelnde Anrufe (RING); andere Events werden ignoriert.

    Format (semikolongetrennt):
      Datum;RING;ConnID;Anrufer;Angerufene;SIP;        ← eingehend (das wollen wir)
      Datum;CALL;ConnID;Nst;EigeneNr;Zielrufnummer;SIP; ← ausgehend
      Datum;CONNECT/DISCONNECT;…                         ← Verbindung auf/ab
    """
    parts = line.strip().split(";")
    if len(parts) < 5 or parts[1] != "RING":
        return None
    caller = parts[3].strip()
    called = parts[4].strip()
    if not caller:
        caller = "anonym"
    return {"caller": caller, "called": called or None, "conn_id": parts[2].strip()}


def run_fritzbox(client: ErpClient, host: str, port: int) -> None:
    """Verbindet den FRITZ!Box-Callmonitor und meldet jeden eingehenden Anruf.

    Robust: automatischer Reconnect mit Backoff; je Verbindungs-ID wird ein RING
    nur einmal gemeldet (die Box wiederholt RING bis zum Abheben)."""
    log.info("FRITZ!Box-Callmonitor: verbinde %s:%d (zuvor am Telefon #96*5* aktivieren)", host, port)
    backoff_i = 0
    while True:
        seen_conn: set[str] = set()
        try:
            with socket.create_connection((host, port), timeout=30) as sock:
                log.info("Callmonitor verbunden — warte auf Anrufe …")
                backoff_i = 0
                buf = ""
                sock.settimeout(None)
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        raise ConnectionError("Callmonitor-Verbindung geschlossen")
                    buf += chunk.decode("latin-1", "replace")
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        evt = parse_fritzbox_line(line)
                        if not evt:
                            continue
                        if evt["conn_id"] and evt["conn_id"] in seen_conn:
                            continue  # selber Anruf, schon gemeldet
                        seen_conn.add(evt["conn_id"])
                        log.info("Eingehender Anruf: %s → %s", evt["caller"], evt["called"] or "?")
                        client.report_call(evt["caller"], evt["called"])
        except (OSError, ConnectionError) as exc:
            wait = RECONNECT_BACKOFF_S[min(backoff_i, len(RECONNECT_BACKOFF_S) - 1)]
            log.warning("Callmonitor-Verbindung verloren (%s) — neuer Versuch in %ds", exc, wait)
            time.sleep(wait)
            backoff_i += 1


def run_tcp_lines(client: ErpClient, host: str, port: int) -> None:
    """Generischer Listener: jede empfangene TCP-Zeile = eine Anrufer-Rufnummer."""
    log.info("TCP-Zeilen-Listener: verbinde %s:%d", host, port)
    backoff_i = 0
    while True:
        try:
            with socket.create_connection((host, port), timeout=30) as sock:
                log.info("Verbunden — warte auf Rufnummern-Zeilen …")
                backoff_i = 0
                buf = ""
                sock.settimeout(None)
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        raise ConnectionError("Verbindung geschlossen")
                    buf += chunk.decode("latin-1", "replace")
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        caller = line.strip()
                        if caller:
                            log.info("Eingehender Anruf: %s", caller)
                            client.report_call(caller)
        except (OSError, ConnectionError) as exc:
            wait = RECONNECT_BACKOFF_S[min(backoff_i, len(RECONNECT_BACKOFF_S) - 1)]
            log.warning("Verbindung verloren (%s) — neuer Versuch in %ds", exc, wait)
            time.sleep(wait)
            backoff_i += 1


def run_transcript(client: ErpClient, args) -> int:
    """Meldet ein Anruf-Transkript nach Gesprächsende (Einmal-Aktion).

    Aufruf typischerweise aus dem Recording-/CTI-Hook der Telefonanlage, sobald
    die Aufnahme/das Transkript vorliegt."""
    transcript = args.transcript
    if not transcript and args.transcript_file:
        try:
            with open(args.transcript_file, "r", encoding="utf-8") as fh:
                transcript = fh.read()
        except OSError as exc:
            log.error("Transkript-Datei nicht lesbar (%s): %s", args.transcript_file, exc)
            return 1
    if not transcript and not args.audio_url:
        log.error("--transcript, --transcript-file oder --audio-url erforderlich.")
        return 2
    ok = client.report_transcript(
        call_id=args.call_id,
        caller=args.caller,
        called=args.called,
        direction=args.direction,
        transcript=transcript,
        audio_url=args.audio_url,
    )
    if ok:
        log.info("OK — der Kontakt sollte jetzt in der KIM-Kontakthistorie erscheinen.")
        return 0
    log.error("Fehlgeschlagen — API-Base/Token/Tenant prüfen.")
    return 1


def run_simulate(client: ErpClient, caller: str, called: Optional[str]) -> int:
    log.info("Sende Test-Anruf %s …", caller)
    ok = client.report_call(caller, called)
    if ok:
        log.info("OK — das Anruf-Popup sollte jetzt im ERP erscheinen.")
        return 0
    log.error("Fehlgeschlagen — API-Base/Token/Tenant prüfen.")
    return 1


# ── CLI ────────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="VALEO NeuroERP TAPI-/Telefonie-Bridge")
    p.add_argument("--source", choices=("fritzbox", "tcp-lines", "simulate", "transcript"), default="fritzbox",
                   help="Anrufquelle bzw. 'transcript' zum Melden eines Gesprächs-Transkripts (Default: fritzbox)")
    p.add_argument("--api-base", default=os.getenv("VALEO_API_BASE", "http://localhost:8000"))
    p.add_argument("--token", default=os.getenv("VALEO_API_TOKEN", "dev-token"))
    p.add_argument("--tenant", default=os.getenv("VALEO_TENANT_ID", DEFAULT_TENANT))
    p.add_argument("--host", default=os.getenv("FRITZBOX_HOST", "fritz.box"),
                   help="Host der Telefonanlage/FRITZ!Box (Default: fritz.box)")
    p.add_argument("--port", type=int, default=int(os.getenv("CALLMONITOR_PORT", "1012")))
    p.add_argument("--caller", default="049417360", help="Rufnummer für --source simulate/transcript")
    p.add_argument("--called", default=None, help="Angerufene Nummer (optional)")
    # --source transcript:
    p.add_argument("--call-id", default=None, help="Call-ID (Idempotenz) für --source transcript")
    p.add_argument("--direction", default="incoming", choices=("incoming", "outgoing"),
                   help="Anruf-Richtung für --source transcript")
    p.add_argument("--transcript", default=None, help="Transkript-Text für --source transcript")
    p.add_argument("--transcript-file", default=None, help="Datei mit Transkript-Text")
    p.add_argument("--audio-url", default=None, help="URL der Aufnahme (ERP transkribiert per STT)")
    p.add_argument("--verbose", action="store_true")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    client = ErpClient(args.api_base, args.token, args.tenant)
    log.info("ERP-Ziel: %s (Tenant %s)", client.url, args.tenant)
    try:
        if args.source == "transcript":
            return run_transcript(client, args)
        if args.source == "simulate":
            return run_simulate(client, args.caller, args.called)
        if args.source == "tcp-lines":
            run_tcp_lines(client, args.host, args.port)
        else:
            run_fritzbox(client, args.host, args.port)
    except KeyboardInterrupt:
        log.info("Beendet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
