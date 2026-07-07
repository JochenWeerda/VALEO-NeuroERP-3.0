"""Collab Rail notes API (UIX-062)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_user_id_from_request
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services.compat_helpers import enqueue_event

router = APIRouter(prefix="/collab/notes", tags=["collab"])


class MentionIn(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    display: str | None = Field(default=None, max_length=200)

    @field_validator("user_id")
    @classmethod
    def user_id_plain(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Mention user_id is required")
        if any(ch.isspace() for ch in trimmed):
            raise ValueError("Mention user_id must not contain whitespace")
        return trimmed


class NoteCreate(BaseModel):
    entity_type: str = Field(min_length=1, max_length=64)
    entity_id: str = Field(min_length=1, max_length=64)
    body: str = Field(min_length=1, max_length=4000)
    mentions: list[MentionIn] = Field(default_factory=list)

    @field_validator("entity_type", "entity_id", "body")
    @classmethod
    def non_empty_trimmed(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Value must not be empty")
        return trimmed


class NotePatch(BaseModel):
    body: str | None = Field(default=None, min_length=1, max_length=4000)
    mentions: list[MentionIn] | None = None

    @field_validator("body")
    @classmethod
    def body_trimmed(cls, value: str | None) -> str | None:
        if value is None:
            return value
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("body must not be empty")
        return trimmed


class NoteOut(BaseModel):
    id: str
    tenant_id: str
    entity_type: str
    entity_id: str
    body: str
    mentions: list[MentionIn]
    created_by: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


def _normalize_mentions(mentions: list[MentionIn] | None) -> list[dict[str, str | None]]:
    return [mention.model_dump() for mention in mentions or []]


def _row_to_note(row: Any) -> NoteOut:
    data = dict(row)
    mentions = data.get("mentions") or []
    return NoteOut(
        id=str(data["id"]),
        tenant_id=str(data["tenant_id"]),
        entity_type=str(data["entity_type"]),
        entity_id=str(data["entity_id"]),
        body=str(data["body"]),
        mentions=[MentionIn.model_validate(mention) for mention in mentions],
        created_by=str(data["created_by"]),
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        deleted_at=data.get("deleted_at"),
    )


def _fetch_note(db: Session, *, tenant_id: str, note_id: str) -> Any | None:
    result = db.execute(
        text(
            """
            SELECT id, tenant_id, entity_type, entity_id, body, mentions, created_by,
                   created_at, updated_at, deleted_at
              FROM domain_shared.entity_notes
             WHERE tenant_id = :tenant_id
               AND id = :id
               AND deleted_at IS NULL
            """
        ),
        {"tenant_id": tenant_id, "id": note_id},
    )
    return result.mappings().first()


def _require_creator(db: Session, *, tenant_id: str, note_id: str, user_id: str) -> Any:
    row = _fetch_note(db, tenant_id=tenant_id, note_id=note_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    if str(row["created_by"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can modify this note")
    return row


def _validate_mentions(db: Session, *, tenant_id: str, mentions: list[MentionIn] | None) -> None:
    user_ids = sorted({mention.user_id for mention in mentions or []})
    if not user_ids:
        return
    result = db.execute(
        text(
            """
            SELECT id
              FROM domain_shared.users
             WHERE tenant_id = :tenant_id
               AND id = ANY(:user_ids)
            """
        ),
        {"tenant_id": tenant_id, "user_ids": user_ids},
    )
    existing = {str(row["id"]) for row in result.mappings().all()}
    missing = [user_id for user_id in user_ids if user_id not in existing]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Unknown mention user_id(s): {', '.join(missing)}",
        )


def _insert_message(db: Session, *, tenant_id: str, note_id: str, sender_id: str, recipient_id: str, body: str) -> None:
    db.execute(
        text(
            """
            INSERT INTO domain_shared.internal_messages
                (id, sender_id, recipient_id, subject, body, is_read, tenant_id, created_at)
            VALUES
                (:id, :sender_id, :recipient_id, :subject, :body, false, :tenant_id, now())
            """
        ),
        {
            "id": uuid7(),
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "subject": "Neue Erwaehnung in einer Notiz",
            "body": f"Notiz {note_id}: {body}",
            "tenant_id": tenant_id,
        },
    )


@router.get("", response_model=list[NoteOut], summary="Collab-Notizen fuer Datensatz")
async def list_notes(
    entity_type: str = Query(..., min_length=1, max_length=64),
    entity_id: str = Query(..., min_length=1, max_length=64),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[NoteOut]:
    result = db.execute(
        text(
            """
            SELECT id, tenant_id, entity_type, entity_id, body, mentions, created_by,
                   created_at, updated_at, deleted_at
              FROM domain_shared.entity_notes
             WHERE tenant_id = :tenant_id
               AND entity_type = :entity_type
               AND entity_id = :entity_id
               AND deleted_at IS NULL
             ORDER BY created_at ASC
             LIMIT :limit
            """
        ),
        {
            "tenant_id": tenant_id,
            "entity_type": entity_type.strip(),
            "entity_id": entity_id.strip(),
            "limit": limit,
        },
    )
    return [_row_to_note(row) for row in result.mappings().all()]


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED, summary="Collab-Notiz anlegen")
async def create_note(
    payload: NoteCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> NoteOut:
    creator = get_user_id_from_request(request)
    mentions = _normalize_mentions(payload.mentions)
    _validate_mentions(db, tenant_id=tenant_id, mentions=payload.mentions)
    note_id = uuid7()

    try:
        result = db.execute(
            text(
                """
                INSERT INTO domain_shared.entity_notes
                    (id, tenant_id, entity_type, entity_id, body, mentions, created_by, created_at, updated_at)
                VALUES
                    (:id, :tenant_id, :entity_type, :entity_id, :body, CAST(:mentions AS jsonb), :created_by, now(), now())
                RETURNING id, tenant_id, entity_type, entity_id, body, mentions, created_by,
                          created_at, updated_at, deleted_at
                """
            ),
            {
                "id": note_id,
                "tenant_id": tenant_id,
                "entity_type": payload.entity_type,
                "entity_id": payload.entity_id,
                "body": payload.body,
                "mentions": json.dumps(mentions),
                "created_by": creator,
            },
        )
        row = result.mappings().first()
        for mention in payload.mentions:
            _insert_message(
                db,
                tenant_id=tenant_id,
                note_id=note_id,
                sender_id=creator,
                recipient_id=mention.user_id,
                body=payload.body,
            )
        await enqueue_event(
            db,
            event_type="collab.note.created",
            aggregate_id=note_id,
            tenant_id=tenant_id,
            payload={
                "note_id": note_id,
                "entity_type": payload.entity_type,
                "entity_id": payload.entity_id,
                "created_by": creator,
                "mentions": mentions,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    if row is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Note insert failed")
    return _row_to_note(row)


@router.patch("/{note_id}", response_model=NoteOut, summary="Collab-Notiz aktualisieren")
async def update_note(
    note_id: str,
    payload: NotePatch,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> NoteOut:
    creator = get_user_id_from_request(request)
    _require_creator(db, tenant_id=tenant_id, note_id=note_id, user_id=creator)
    _validate_mentions(db, tenant_id=tenant_id, mentions=payload.mentions)

    body_update = payload.body is not None
    mentions_update = payload.mentions is not None
    if not body_update and not mentions_update:
        row = _fetch_note(db, tenant_id=tenant_id, note_id=note_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return _row_to_note(row)

    result = db.execute(
        text(
            """
            UPDATE domain_shared.entity_notes
               SET body = CASE WHEN :body_update THEN :body ELSE body END,
                   mentions = CASE WHEN :mentions_update THEN CAST(:mentions AS jsonb) ELSE mentions END,
                   updated_at = now()
             WHERE tenant_id = :tenant_id
               AND id = :id
               AND deleted_at IS NULL
            RETURNING id, tenant_id, entity_type, entity_id, body, mentions, created_by,
                      created_at, updated_at, deleted_at
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": note_id,
            "body_update": body_update,
            "body": payload.body,
            "mentions_update": mentions_update,
            "mentions": json.dumps(_normalize_mentions(payload.mentions)),
        },
    )
    db.commit()
    row = result.mappings().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return _row_to_note(row)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Collab-Notiz loeschen")
async def delete_note(
    note_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> None:
    creator = get_user_id_from_request(request)
    _require_creator(db, tenant_id=tenant_id, note_id=note_id, user_id=creator)
    db.execute(
        text(
            """
            UPDATE domain_shared.entity_notes
               SET deleted_at = now(), updated_at = now()
             WHERE tenant_id = :tenant_id
               AND id = :id
               AND deleted_at IS NULL
            """
        ),
        {"tenant_id": tenant_id, "id": note_id},
    )
    db.commit()
    return None
