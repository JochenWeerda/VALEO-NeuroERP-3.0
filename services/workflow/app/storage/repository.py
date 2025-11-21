"""
Persistenzschicht für Workflow-Definitionen und -Instanzen.
"""

from __future__ import annotations

import asyncio
from typing import Dict, Iterable, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Base, WorkflowDefinitionModel, WorkflowInstanceModel
from app.db.session import engine, SessionLocal
from app.schemas.workflow import WorkflowDefinition, WorkflowInstance


class WorkflowRepository:
    """Kapselt den Zugriff auf die relationale Datenbank."""

    def __init__(self) -> None:
        self._session_factory = SessionLocal

    async def create_schema(self) -> None:
        def _create() -> None:
            Base.metadata.create_all(bind=engine)

        await asyncio.to_thread(_create)

    async def load_definitions(self) -> Iterable[WorkflowDefinition]:
        def _load() -> Iterable[WorkflowDefinition]:
            with self._session_factory() as session:
                rows = session.query(WorkflowDefinitionModel).all()
                return [
                    WorkflowDefinition(**row.definition)  # type: ignore[arg-type]
                    for row in rows
                ]

        return await asyncio.to_thread(_load)

    async def save_definition(self, definition: WorkflowDefinition) -> None:
        def _persist() -> None:
            with self._session_factory() as session:
                key = f"{definition.tenant}:{definition.name}:{definition.version}"
                row = session.query(WorkflowDefinitionModel).filter_by(key=key).first()
                payload: Dict[str, object] = definition.model_dump()
                if not row:
                    row = WorkflowDefinitionModel(
                        key=key,
                        name=definition.name,
                        version=definition.version,
                        tenant=definition.tenant,
                        definition=payload,
                    )
                    session.add(row)
                else:
                    row.definition = payload
                session.commit()

        await asyncio.to_thread(_persist)

    async def save_instance(self, instance: WorkflowInstance) -> None:
        def _persist() -> None:
            with self._session_factory() as session:
                row = session.query(WorkflowInstanceModel).filter_by(id=instance.id).first()
                payload = instance.model_dump()
                if not row:
                    row = WorkflowInstanceModel(
                        id=instance.id,
                        workflow_name=instance.workflow_name,
                        workflow_version=instance.workflow_version,
                        tenant=instance.tenant,
                        state=instance.state,
                        context=payload["context"],
                        created_at=instance.created_at,
                        updated_at=instance.updated_at,
                    )
                    session.add(row)
                else:
                    row.state = instance.state
                    row.context = payload["context"]
                session.commit()

        await asyncio.to_thread(_persist)

    async def get_instance(self, instance_id: UUID) -> Optional[WorkflowInstance]:
        def _fetch() -> Optional[WorkflowInstance]:
            with self._session_factory() as session:
                row = session.query(WorkflowInstanceModel).filter_by(id=instance_id).first()
                if not row:
                    return None
                return WorkflowInstance(
                    id=row.id,
                    workflow_name=row.workflow_name,
                    workflow_version=row.workflow_version,
                    tenant=row.tenant,
                    state=row.state,
                    context=row.context,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )

        return await asyncio.to_thread(_fetch)


