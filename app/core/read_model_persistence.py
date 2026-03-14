from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session


class SnapshotCursor(BaseModel):
    """Cursor fuer seitenweise Abfrage von Read-Model-Snapshots."""

    last_snapshot_id: Optional[str] = None
    limit: int = 20
    schema_version: int = 1


class ReadModelSnapshot(BaseModel):
    """Persistenter Snapshot eines Read-Models (Wave-2-Projektionen)."""

    snapshot_id: str
    model_name: str
    tenant_id: str
    payload_json: str
    payload_hash: str
    cursor: str
    created_at: datetime
    schema_version: int = 1

    @classmethod
    def build(cls, model_name: str, tenant_id: str, payload: dict[str, Any]) -> "ReadModelSnapshot":
        payload_json = json.dumps(payload, default=str, sort_keys=True)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        snapshot_id = str(uuid.uuid4())
        cursor = hashlib.sha256(snapshot_id.encode()).hexdigest()[:16]
        return cls(
            snapshot_id=snapshot_id,
            model_name=model_name,
            tenant_id=tenant_id,
            payload_json=payload_json,
            payload_hash=payload_hash,
            cursor=cursor,
            created_at=datetime.utcnow(),
        )

    def verify_integrity(self) -> bool:
        expected = hashlib.sha256(self.payload_json.encode()).hexdigest()
        return expected == self.payload_hash

    def get_payload(self) -> dict[str, Any]:
        return json.loads(self.payload_json)


class ReadModelSnapshotStore:
    """Snapshot-Store mit DB-Persistenz und In-Memory-Fallback."""

    def __init__(
        self,
        db_session: Session | None = None,
        snapshots: dict[str, ReadModelSnapshot] | None = None,
    ) -> None:
        self.db_session = db_session
        self.snapshots = snapshots or {}
        self.schema_version = 1

    def save(self, snapshot: ReadModelSnapshot) -> ReadModelSnapshot:
        if self.db_session is None:
            self.snapshots[snapshot.snapshot_id] = snapshot
            return snapshot

        from app.infrastructure.models.read_model_snapshots import ReadModelSnapshotRecord

        existing = self.db_session.get(ReadModelSnapshotRecord, snapshot.snapshot_id)
        if existing is None:
            existing = ReadModelSnapshotRecord(snapshot_id=snapshot.snapshot_id)
            self.db_session.add(existing)

        existing.model_name = snapshot.model_name
        existing.tenant_id = snapshot.tenant_id
        existing.payload_json = snapshot.payload_json
        existing.payload_hash = snapshot.payload_hash
        existing.cursor = snapshot.cursor
        existing.created_at = snapshot.created_at
        existing.schema_version = snapshot.schema_version
        self.db_session.commit()
        return self._from_record(existing)

    def get(self, snapshot_id: str) -> Optional[ReadModelSnapshot]:
        if self.db_session is None:
            return self.snapshots.get(snapshot_id)

        from app.infrastructure.models.read_model_snapshots import ReadModelSnapshotRecord

        record = self.db_session.get(ReadModelSnapshotRecord, snapshot_id)
        return self._from_record(record) if record is not None else None

    def get_latest(self, model_name: str, tenant_id: str) -> Optional[ReadModelSnapshot]:
        if self.db_session is None:
            matching = [
                snapshot
                for snapshot in self.snapshots.values()
                if snapshot.model_name == model_name and snapshot.tenant_id == tenant_id
            ]
            if not matching:
                return None
            return max(matching, key=lambda snapshot: snapshot.created_at)

        from app.infrastructure.models.read_model_snapshots import ReadModelSnapshotRecord

        record = (
            self.db_session.query(ReadModelSnapshotRecord)
            .filter(
                ReadModelSnapshotRecord.model_name == model_name,
                ReadModelSnapshotRecord.tenant_id == tenant_id,
            )
            .order_by(
                ReadModelSnapshotRecord.created_at.desc(),
                ReadModelSnapshotRecord.snapshot_id.desc(),
            )
            .first()
        )
        return self._from_record(record) if record is not None else None

    def get_page(
        self,
        model_name: str,
        tenant_id: str,
        cursor: SnapshotCursor,
    ) -> list[ReadModelSnapshot]:
        if self.db_session is None:
            matching = sorted(
                [
                    snapshot
                    for snapshot in self.snapshots.values()
                    if snapshot.model_name == model_name and snapshot.tenant_id == tenant_id
                ],
                key=lambda snapshot: (snapshot.created_at, snapshot.snapshot_id),
            )
            if cursor.last_snapshot_id:
                ids = [snapshot.snapshot_id for snapshot in matching]
                if cursor.last_snapshot_id in ids:
                    start = ids.index(cursor.last_snapshot_id) + 1
                    matching = matching[start:]
            return matching[: cursor.limit]

        from app.infrastructure.models.read_model_snapshots import ReadModelSnapshotRecord

        query = (
            self.db_session.query(ReadModelSnapshotRecord)
            .filter(
                ReadModelSnapshotRecord.model_name == model_name,
                ReadModelSnapshotRecord.tenant_id == tenant_id,
            )
            .order_by(
                ReadModelSnapshotRecord.created_at.asc(),
                ReadModelSnapshotRecord.snapshot_id.asc(),
            )
        )
        records = list(query.all())
        if cursor.last_snapshot_id:
            snapshot_ids = [record.snapshot_id for record in records]
            if cursor.last_snapshot_id in snapshot_ids:
                start = snapshot_ids.index(cursor.last_snapshot_id) + 1
                records = records[start:]
        return [self._from_record(record) for record in records[: cursor.limit]]

    def count(self, model_name: str, tenant_id: str) -> int:
        if self.db_session is None:
            return sum(
                1
                for snapshot in self.snapshots.values()
                if snapshot.model_name == model_name and snapshot.tenant_id == tenant_id
            )

        from app.infrastructure.models.read_model_snapshots import ReadModelSnapshotRecord

        return (
            self.db_session.query(ReadModelSnapshotRecord)
            .filter(
                ReadModelSnapshotRecord.model_name == model_name,
                ReadModelSnapshotRecord.tenant_id == tenant_id,
            )
            .count()
        )

    def all_model_names(self) -> list[str]:
        if self.db_session is None:
            return list({snapshot.model_name for snapshot in self.snapshots.values()})

        from app.infrastructure.models.read_model_snapshots import ReadModelSnapshotRecord

        rows = self.db_session.query(ReadModelSnapshotRecord.model_name).distinct().all()
        return [row[0] for row in rows]

    @staticmethod
    def _from_record(record: Any) -> ReadModelSnapshot:
        return ReadModelSnapshot(
            snapshot_id=record.snapshot_id,
            model_name=record.model_name,
            tenant_id=record.tenant_id,
            payload_json=record.payload_json,
            payload_hash=record.payload_hash,
            cursor=record.cursor,
            created_at=record.created_at,
            schema_version=record.schema_version,
        )
