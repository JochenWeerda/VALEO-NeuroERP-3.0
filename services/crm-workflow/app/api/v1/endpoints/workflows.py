"""CRM Workflow API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....schemas.workflow import Workflow, WorkflowCreate, WorkflowUpdate, WorkflowExecution
from ....schemas.base import PaginatedResponse
from ....db.models import Workflow as WorkflowModel, WorkflowExecution as WorkflowExecutionModel

router = APIRouter()


@router.post("/", response_model=Workflow, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: AsyncSession = get_db
):
    """Create a new workflow."""
    workflow = WorkflowModel(**workflow_data.model_dump())
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return Workflow.model_validate(workflow)


@router.get("/", response_model=PaginatedResponse[Workflow])
async def list_workflows(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = get_db
):
    """List workflows with pagination and filtering."""
    query = db.query(WorkflowModel)

    if tenant_id:
        query = query.filter(WorkflowModel.tenant_id == tenant_id)
    if status:
        query = query.filter(WorkflowModel.status == status)

    total = await query.count()
    workflows = await query.offset(skip).limit(limit).all()

    return PaginatedResponse[Workflow](
        items=[Workflow.model_validate(workflow) for workflow in workflows],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = get_db
):
    """Get a specific workflow by ID."""
    workflow = await db.get(WorkflowModel, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return Workflow.model_validate(workflow)


@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    db: AsyncSession = get_db
):
    """Update a workflow."""
    workflow = await db.get(WorkflowModel, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    update_data = workflow_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)

    await db.commit()
    await db.refresh(workflow)
    return Workflow.model_validate(workflow)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    db: AsyncSession = get_db
):
    """Delete a workflow."""
    workflow = await db.get(WorkflowModel, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    await db.delete(workflow)
    await db.commit()


@router.post("/{workflow_id}/execute", response_model=WorkflowExecution)
async def execute_workflow(
    workflow_id: UUID,
    trigger_event: dict = {},
    db: AsyncSession = get_db
):
    """Manually execute a workflow."""
    workflow = await db.get(WorkflowModel, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Create execution record
    execution = WorkflowExecutionModel(
        workflow_id=workflow_id,
        trigger_event=trigger_event,
        execution_context={"manual": True},
        status="pending"
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    # TODO: Actually execute the workflow actions
    # For now, just mark as completed
    execution.status = "completed"
    await db.commit()
    await db.refresh(execution)

    return WorkflowExecution.model_validate(execution)


@router.get("/{workflow_id}/executions", response_model=list[WorkflowExecution])
async def get_workflow_executions(
    workflow_id: UUID,
    db: AsyncSession = get_db
):
    """Get execution history for a workflow."""
    workflow = await db.get(WorkflowModel, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    executions = await db.query(WorkflowExecutionModel).filter(
        WorkflowExecutionModel.workflow_id == workflow_id
    ).all()

    return [WorkflowExecution.model_validate(execution) for execution in executions]