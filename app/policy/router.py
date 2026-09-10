"""
Policy API Router
FastAPI-Router mit CRUD, Test, Backup/Restore und WebSocket
"""

import os
from pathlib import Path
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    Body,
    BackgroundTasks,
    Request,
    status,
)
import logging

from app.middleware.rate_limit import limiter
from .store import PolicyStore, DEFAULT_DB
from .ws import hub
from app.auth.deps import get_current_user, require_roles, User
from app.auth.jwt import decode_token
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_store() -> PolicyStore:
    """Dependency: Policy-Store Instance"""
    return PolicyStore(DEFAULT_DB)


router = APIRouter(prefix="/api/mcp/policy", tags=["policy"])


# --- CRUD ---
#
# Die Routen /list, /create, /update, /delete, /test und /export lagen hier
# doppelt. Sie wurden von app/api/v1/endpoints/policies.py ueberlagert, das in
# main.py frueher registriert wird — wodurch die hier deklarierten
# require_roles-Pruefungen wirkungslos waren. Entfernt in
# POLICY-ROUTE-DEDUP-20260910; die Rollenpruefungen sind auf die wirksame
# Implementierung gewandert. Hier verbleibt nur, was es dort nicht gibt:
# Backup, Backup-Liste, Restore aus Datei und der WebSocket.


# --- Backup / Restore (DB-Datei) ---

BACKUP_DIR = os.environ.get("POLICY_BACKUP_DIR", "data/backups")
Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)


BACKUP_SUFFIX = ".json"


def _resolve_backup_file(file_name: str) -> Path:
    backup_root = Path(BACKUP_DIR).resolve()
    submitted = Path(file_name)
    if submitted.name != file_name or submitted.is_absolute():
        raise HTTPException(status_code=400, detail="Backup path is invalid")
    if submitted.suffix != BACKUP_SUFFIX:
        raise HTTPException(status_code=400, detail="Backup path is invalid")
    candidate = (backup_root / submitted.name).resolve()
    if candidate.parent != backup_root:
        raise HTTPException(status_code=400, detail="Backup path is invalid")
    return candidate


@router.get("/backup", dependencies=[Depends(require_roles("admin"))])
async def backup_db(
    user: User = Depends(get_current_user),
    store: PolicyStore = Depends(get_store),
) -> dict:
    """Sichert alle Policies als JSON-Datei.

    Der Policy-Store liegt seit der Umstellung auf ``PolicyService`` in
    PostgreSQL; die frueheren Sicherungen kopierten eine SQLite-Datei, die es
    nicht mehr gibt (``DEFAULT_DB`` ist None). Gesichert wird deshalb der
    fachliche Inhalt ueber den JSON-Export, den ``/restore`` wieder einspielt.
    """
    try:
        import datetime

        ts = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
        dest = Path(BACKUP_DIR) / f"policies-{ts}{BACKUP_SUFFIX}"
        rules = store.export_json()
        dest.write_text(rules, encoding="utf-8")
        logger.info(f"Created backup: {dest} by {user['sub']}")
        return {"ok": True, "file": str(dest)}
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backups", dependencies=[Depends(require_roles("admin"))])
async def list_backups(user: User = Depends(get_current_user)) -> dict:
    """Listet alle verfügbaren Backups auf"""
    try:
        files = [
            str(Path(BACKUP_DIR) / f)
            for f in os.listdir(BACKUP_DIR)
            if f.endswith(BACKUP_SUFFIX)
        ]
        files.sort(reverse=True)
        return {"ok": True, "files": files}
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backups/restore", dependencies=[Depends(require_roles("admin"))])
@limiter.limit("5/minute")
async def restore_from_backup(
    request: Request,
    file: str = Body(..., embed=True),
    bg: BackgroundTasks = BackgroundTasks(),
    user: User = Depends(get_current_user),
    store: PolicyStore = Depends(get_store),
) -> dict:
    """Spielt eine zuvor geschriebene Backup-Datei wieder ein.

    ACHTUNG: ersetzt alle vorhandenen Regeln. Vor dem Einspielen wird der
    aktuelle Stand als ``pre-restore-<ts>.json`` gesichert.

    Der Pfad lautet ``/backups/restore`` und nicht ``/restore``: unter
    ``/restore`` liegt die JSON-Variante in
    ``app/api/v1/endpoints/policies.py``. Beide lagen frueher auf demselben
    Pfad, wodurch diese Fassung samt ihrer Rollenpruefung unerreichbar war
    (POLICY-ROUTE-DEDUP-20260910).

    Args:
        file: Dateiname eines Backups aus ``GET /backups``, ohne Pfadanteile.

    Returns:
        Status mit Angabe der Quelle und der Sicherungskopie.
    """
    try:
        import datetime

        src = _resolve_backup_file(file)
        if not src.exists():
            raise HTTPException(status_code=400, detail="Backup not found")

        # Safety-Backup vor Restore: aktueller Stand als JSON-Export
        ts = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
        safety = Path(BACKUP_DIR) / f"pre-restore-{ts}{BACKUP_SUFFIX}"
        safety.write_text(store.export_json(), encoding="utf-8")

        # Restore: ersetzt alle vorhandenen Regeln
        store.restore_json(src.read_text(encoding="utf-8"))
        logger.warning(
            f"Restored policies from {src} by {user['sub']} (safety backup: {safety})"
        )

        # Broadcast
        bg.add_task(
            hub.broadcast,
            {"service": "policy", "type": "restored", "from": str(src)},
        )

        return {
            "ok": True,
            "restoredFrom": str(src),
            "safetyBackup": str(safety),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restore backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- WebSocket ---


def _extract_websocket_token(websocket: WebSocket, query_token: str | None) -> str:
    if query_token:
        return query_token.strip()

    auth_header = (websocket.headers.get("authorization") or "").strip()
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return auth_header


def _resolve_policy_ws_auth(websocket: WebSocket, query_token: str | None) -> dict:
    token = _extract_websocket_token(websocket, query_token)
    if not token:
        raise ValueError("Missing bearer token")

    if settings.API_DEV_TOKEN and token == settings.API_DEV_TOKEN:
        return {"user_id": "dev", "roles": ["admin"]}

    claims = decode_token(token)
    user_id = (claims.get("sub") or "").strip()
    roles = claims.get("roles") or []
    if not isinstance(roles, list):
        roles = []
    if not user_id:
        raise ValueError("Invalid or expired token")
    if not {"admin", "manager"}.intersection(set(roles)):
        raise ValueError("Insufficient role")
    return {"user_id": user_id, "roles": roles}


@router.websocket("/ws")
async def ws_policy(websocket: WebSocket, token: str | None = Query(None)):
    """
    WebSocket-Endpoint für Realtime Policy-Updates

    Client erhält Broadcasts bei:
    - created
    - updated
    - deleted
    - bulk-created
    - restored
    """
    try:
        auth_context = _resolve_policy_ws_auth(websocket, token)
    except Exception as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(exc))
        return

    await hub.connect(websocket)
    logger.info("Policy WebSocket connected by %s", auth_context["user_id"])
    try:
        while True:
            # Simple ping/pong - ignoriere Content
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)

