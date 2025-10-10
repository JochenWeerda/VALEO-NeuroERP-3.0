"""
Policy API Router
FastAPI-Router mit CRUD, Test, Backup/Restore und WebSocket
"""

from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Body,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse
import logging

from .models import Rule, RulesEnvelope, Alert, Decision
from .store import PolicyStore, DEFAULT_DB
from .engine import decide
from .ws import hub
from app.auth.deps import get_current_user, require_roles, User

logger = logging.getLogger(__name__)


def get_store() -> PolicyStore:
    """Dependency: Policy-Store Instance"""
    return PolicyStore(DEFAULT_DB)


router = APIRouter(prefix="/api/mcp/policy", tags=["policy"])


# --- CRUD ---


@router.get("/list")
async def list_policies(store: PolicyStore = Depends(get_store)) -> dict:
    """Listet alle Policies auf"""
    try:
        rules = store.list()
        return {"ok": True, "data": [r.model_dump() for r in rules]}
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", dependencies=[Depends(require_roles("manager", "admin"))])
async def create_policy(
    payload: dict = Body(...),
    bg: BackgroundTasks = BackgroundTasks(),
    store: PolicyStore = Depends(get_store),
    user: User = Depends(get_current_user),
):
    """
    Erstellt Policy (einzeln oder bulk)

    Payload:
    - Einzeln: Rule-Objekt
    - Bulk: { "rules": [Rule, ...] }
    """
    try:
        # Bulk-Import?
        if "rules" in payload:
            env = RulesEnvelope.model_validate(payload)
            store.bulk_upsert(env.rules)
            logger.info(f"Created {len(env.rules)} policies (bulk) by {user['sub']}")
            bg.add_task(
                hub.broadcast,
                {"service": "policy", "type": "bulk-created", "count": len(env.rules)},
            )
            return {"ok": True, "count": len(env.rules)}

        # Einzelne Rule
        rule = Rule.model_validate(payload)
        store.upsert(rule)
        logger.info(f"Created policy: {rule.id} by {user['sub']}")
        bg.add_task(
            hub.broadcast, {"service": "policy", "type": "created", "id": rule.id}
        )
        return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to create policy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update", dependencies=[Depends(require_roles("manager", "admin"))])
async def update_policy(
    rule: Rule,
    bg: BackgroundTasks = BackgroundTasks(),
    store: PolicyStore = Depends(get_store),
    user: User = Depends(get_current_user),
):
    """Aktualisiert existierende Policy"""
    try:
        if not store.get(rule.id):
            raise HTTPException(status_code=404, detail="Policy not found")

        store.upsert(rule)
        logger.info(f"Updated policy: {rule.id} by {user['sub']}")
        bg.add_task(
            hub.broadcast, {"service": "policy", "type": "updated", "id": rule.id}
        )
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update policy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/delete", dependencies=[Depends(require_roles("manager", "admin"))])
async def delete_policy(
    id: str = Body(..., embed=True),
    bg: BackgroundTasks = BackgroundTasks(),
    store: PolicyStore = Depends(get_store),
    user: User = Depends(get_current_user),
):
    """Löscht Policy"""
    try:
        if not store.get(id):
            raise HTTPException(status_code=404, detail="Policy not found")

        store.delete(id)
        logger.info(f"Deleted policy: {id} by {user['sub']}")
        bg.add_task(hub.broadcast, {"service": "policy", "type": "deleted", "id": id})
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Test / Simulator ---


@router.post("/test")
async def test_decision(
    alert: Alert,
    roles: List[str] = Body(default=[]),
    store: PolicyStore = Depends(get_store),
) -> dict:
    """
    Test-Simulator - testet Policy-Entscheidung gegen Alert

    Args:
        alert: Alert-Objekt
        roles: User-Rollen (z.B. ["manager"])

    Returns:
        Decision-Objekt
    """
    try:
        decision: Decision = decide(roles, alert, store.list())
        logger.info(f"Policy test: {alert.kpiId} -> {decision.type}")
        return {"ok": True, "decision": decision.model_dump()}
    except Exception as e:
        logger.error(f"Failed to test policy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# --- Export JSON ---


@router.get("/export", dependencies=[Depends(require_roles("admin"))])
async def export_json(
    store: PolicyStore = Depends(get_store), user: User = Depends(get_current_user)
) -> JSONResponse:
    """Exportiert alle Policies als JSON-Download"""
    try:
        rules = store.list()
        logger.info(f"Exported {len(rules)} policies as JSON by {user['sub']}")
        return JSONResponse(
            content={"ok": True, "rules": [r.model_dump() for r in rules]},
            headers={
                "Content-Disposition": 'attachment; filename="policies-export.json"'
            },
        )
    except Exception as e:
        logger.error(f"Failed to export policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Backup / Restore (DB-Datei) ---

BACKUP_DIR = os.environ.get("POLICY_BACKUP_DIR", "data/backups")
Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)


@router.get("/backup", dependencies=[Depends(require_roles("admin"))])
async def backup_db(user: User = Depends(get_current_user)) -> dict:
    """Erstellt Backup der SQLite-Datenbank"""
    try:
        import datetime

        ts = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
        dest = Path(BACKUP_DIR) / f"policies-{ts}.db"
        shutil.copyfile(DEFAULT_DB, dest)
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
            if f.endswith(".db")
        ]
        files.sort(reverse=True)
        return {"ok": True, "files": files}
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore", dependencies=[Depends(require_roles("admin"))])
async def restore_db(
    file: str = Body(..., embed=True),
    bg: BackgroundTasks = BackgroundTasks(),
    user: User = Depends(get_current_user),
) -> dict:
    """
    Stellt Backup wieder her (ACHTUNG: Überschreibt aktuelle DB!)

    Args:
        file: Pfad zum Backup-File

    Returns:
        Status mit Safety-Backup-Info
    """
    try:
        import datetime

        src = Path(file)
        if not src.exists():
            raise HTTPException(status_code=400, detail="Backup not found")

        # Safety-Backup vor Restore
        ts = datetime.datetime.now().isoformat().replace(":", "-").replace(".", "-")
        safety = Path(BACKUP_DIR) / f"pre-restore-{ts}.db"
        if Path(DEFAULT_DB).exists():
            shutil.copyfile(DEFAULT_DB, safety)

        # Restore
        shutil.copyfile(src, DEFAULT_DB)
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


@router.websocket("/ws")
async def ws_policy(websocket: WebSocket):
    """
    WebSocket-Endpoint für Realtime Policy-Updates

    Client erhält Broadcasts bei:
    - created
    - updated
    - deleted
    - bulk-created
    - restored
    """
    await hub.connect(websocket)
    try:
        while True:
            # Simple ping/pong - ignoriere Content
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)

