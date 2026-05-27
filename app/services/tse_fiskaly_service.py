"""TSE/Fiskaly Cloud-TSE Service (KassenSichV § 146a AO).

Implementiert die Fiskaly Cloud-TSE REST API v2 für:
- TSE-Einrichtung (CreateTSE)
- Transaktionssignierung (StartTransaction/FinishTransaction)
- Exportabruf (ExportData)

Konfiguration via Umgebungsvariablen:
  FISKALY_API_KEY   — Fiskaly API Key
  FISKALY_API_SECRET — Fiskaly API Secret
  FISKALY_BASE_URL  — https://kassensichv-middleware.fiskaly.com/api/v2 (Default)

In Entwicklung (kein Key gesetzt): Simulator-Modus mit realistischen Dummy-Werten.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from base64 import b64encode
from datetime import datetime
from typing import Any, Optional


_BASE_URL = os.getenv("FISKALY_BASE_URL", "https://kassensichv-middleware.fiskaly.com/api/v2")
_API_KEY = os.getenv("FISKALY_API_KEY", "")
_API_SECRET = os.getenv("FISKALY_API_SECRET", "")


def _is_configured() -> bool:
    return bool(_API_KEY and _API_SECRET)


def _fiskaly_auth_header() -> str:
    """Einfaches HMAC-SHA256-Auth-Header für Fiskaly API v2."""
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    msg = f"{_API_KEY}\n{timestamp}"
    sig = hmac.new(_API_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    return f"FiskalyV2 key={_API_KEY},ts={timestamp},sig={sig}"


def _simulate_signature(amount_cents: int, tx_id: str, counter: int) -> dict:
    """Deterministischer Simulator für Dev-Umgebungen."""
    payload = f"{tx_id}:{amount_cents}:{counter}"
    sig = hashlib.sha256(payload.encode()).hexdigest()[:64]
    return {
        "tse_transaction_id": tx_id,
        "tse_signature": b64encode(sig.encode()).decode(),
        "tse_signature_counter": counter,
        "tse_time_format": "UnixTime",
        "tse_transaction_time_start": datetime.utcnow().isoformat() + "Z",
        "tse_transaction_time_end": datetime.utcnow().isoformat() + "Z",
        "tse_serial_number": "SIMULATOR-0000000000000000",
        "tse_signature_algorithm": "ecdsa-plain-SHA384",
        "qr_code_data": f"V0;SIMULATOR;{sig[:16]};{counter};{amount_cents}",
        "simulator": True,
    }


def create_tse(tss_id: Optional[str] = None) -> dict:
    """Legt neue TSS (Technical Security System) bei Fiskaly an oder gibt Simulator zurück."""
    tss_id = tss_id or str(uuid.uuid4())
    if not _is_configured():
        return {
            "tss_id": tss_id,
            "status": "INITIALIZED",
            "description": "VALEO-NeuroERP POS TSE (Simulator)",
            "time_creation": datetime.utcnow().isoformat() + "Z",
            "simulator": True,
            "hint": "Setzen Sie FISKALY_API_KEY + FISKALY_API_SECRET für produktiven Betrieb",
        }
    try:
        import httpx
        resp = httpx.put(
            f"{_BASE_URL}/tss/{tss_id}",
            json={"description": f"VALEO-NeuroERP-TSS-{tss_id[:8]}", "state": "INITIALIZED"},
            headers={"Authorization": _fiskaly_auth_header(), "Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        raise RuntimeError(f"Fiskaly TSS-Anlage fehlgeschlagen: {exc}") from exc


def start_transaction(
    tss_id: str,
    client_id: str,
    amount_cents: int,
    payment_type: str = "Unbar",
) -> dict:
    """Startet eine Kassentransaktion (StartTransaction) und gibt Signatur zurück."""
    tx_id = str(uuid.uuid4())
    if not _is_configured():
        return {**_simulate_signature(amount_cents, tx_id, 1), "client_id": client_id, "tss_id": tss_id}
    try:
        import httpx
        resp = httpx.put(
            f"{_BASE_URL}/tss/{tss_id}/tx/{tx_id}",
            json={
                "client_id": client_id,
                "type": "RECEIPT",
                "state": "ACTIVE",
                "data": {"payment_type": payment_type, "amount_per_vat_rate": [{"vat_rate": "NORMAL", "amount": str(amount_cents / 100)}]},
            },
            headers={"Authorization": _fiskaly_auth_header(), "Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        raise RuntimeError(f"Fiskaly StartTransaction fehlgeschlagen: {exc}") from exc


def finish_transaction(tss_id: str, tx_id: str, amount_cents: int, counter: int) -> dict:
    """Schließt Transaktion ab (FinishTransaction) — liefert finale Signatur."""
    if not _is_configured():
        return _simulate_signature(amount_cents, tx_id, counter)
    try:
        import httpx
        resp = httpx.patch(
            f"{_BASE_URL}/tss/{tss_id}/tx/{tx_id}",
            json={"state": "FINISHED"},
            headers={"Authorization": _fiskaly_auth_header(), "Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "tse_transaction_id": tx_id,
            "tse_signature": data.get("signature", {}).get("value", ""),
            "tse_signature_counter": data.get("signature", {}).get("counter", counter),
            "tse_serial_number": data.get("tss", {}).get("serial_number", ""),
            "qr_code_data": data.get("qr_code_data", ""),
        }
    except Exception as exc:
        raise RuntimeError(f"Fiskaly FinishTransaction fehlgeschlagen: {exc}") from exc


def export_data(tss_id: str, start_date: str, end_date: str) -> dict:
    """Initiiert DSFinV-K-konformen Export bei Fiskaly."""
    if not _is_configured():
        return {
            "export_id": str(uuid.uuid4()),
            "tss_id": tss_id,
            "status": "PENDING",
            "start_date": start_date,
            "end_date": end_date,
            "simulator": True,
            "hinweis": "Kein Fiskaly-Key konfiguriert — Export nur in Produktion verfügbar.",
        }
    try:
        import httpx
        export_id = str(uuid.uuid4())
        resp = httpx.put(
            f"{_BASE_URL}/tss/{tss_id}/export/{export_id}",
            json={"start_date": start_date, "end_date": end_date},
            headers={"Authorization": _fiskaly_auth_header(), "Content-Type": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        raise RuntimeError(f"Fiskaly Export fehlgeschlagen: {exc}") from exc


def get_status() -> dict:
    """Prüft Fiskaly-Konnektivität und TSE-Konfiguration."""
    configured = _is_configured()
    result: dict[str, Any] = {
        "fiskaly_configured": configured,
        "base_url": _BASE_URL,
        "mode": "produktiv" if configured else "simulator",
    }
    if configured:
        try:
            import httpx
            resp = httpx.get(
                f"{_BASE_URL}/tss",
                headers={"Authorization": _fiskaly_auth_header()},
                timeout=5,
            )
            result["api_reachable"] = resp.status_code < 500
            result["tss_count"] = len(resp.json().get("data", []))
        except Exception as exc:
            result["api_reachable"] = False
            result["error"] = str(exc)
    return result
