"""
Knowledge-backed onboarding workspaces for new employees and agents.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.knowledge_core_contracts import KnowledgeChannel
from app.core.knowledge_runtime import build_runtime_context_pack, build_runtime_onboarding_bundle


@dataclass
class OnboardingWorkspace:
    rolle: str
    kanal: str
    tenant_id: str | None
    employee_ref: str | None
    capability_key: str | None
    checklist: dict[str, Any] | None
    onboarding_run: dict[str, Any] | None
    knowledge_bundle: dict[str, Any]
    context_pack: dict[str, Any]
    empfohlene_naechste_schritte: list[str]
    channel_message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "rolle": self.rolle,
            "kanal": self.kanal,
            "tenant_id": self.tenant_id,
            "employee_ref": self.employee_ref,
            "capability_key": self.capability_key,
            "checklist": self.checklist,
            "onboarding_run": self.onboarding_run,
            "knowledge_bundle": self.knowledge_bundle,
            "context_pack": self.context_pack,
            "empfohlene_naechste_schritte": self.empfohlene_naechste_schritte,
            "channel_message": self.channel_message,
        }


def _normalize_channel(kanal: str | KnowledgeChannel | None) -> KnowledgeChannel:
    if isinstance(kanal, KnowledgeChannel):
        return kanal
    if not kanal:
        return KnowledgeChannel.TEAMS
    return KnowledgeChannel(kanal.strip().upper())


def _as_task_list(checklist: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not checklist:
        return []
    tasks = checklist.get("tasks") or []
    if isinstance(tasks, list):
        return [task for task in tasks if isinstance(task, dict)]
    return []


def _next_steps(
    checklist: dict[str, Any] | None,
    onboarding_run: dict[str, Any] | None,
    context_pack: dict[str, Any],
) -> list[str]:
    next_steps: list[str] = []
    run_state = onboarding_run.get("state") if onboarding_run else {}
    erledigte_codes = set()
    if isinstance(run_state, dict):
        raw = run_state.get("completed_task_codes") or []
        if isinstance(raw, list):
            erledigte_codes = {str(item) for item in raw}

    for task in _as_task_list(checklist):
        task_code = str(task.get("code") or "").strip()
        if task_code and task_code in erledigte_codes:
            continue
        title = str(task.get("title") or task.get("label") or "").strip()
        if title:
            next_steps.append(title)
        if len(next_steps) >= 3:
            break

    if len(next_steps) < 3:
        for standard in context_pack.get("standards", []):
            next_steps.append(f"Standard verinnerlichen: {standard}")
            if len(next_steps) >= 3:
                break

    if len(next_steps) < 3:
        for knowledge_id in context_pack.get("knowledge_ids", []):
            next_steps.append(f"Wissensobjekt pruefen: {knowledge_id}")
            if len(next_steps) >= 3:
                break

    return next_steps


def _build_channel_message(
    *,
    rolle: str,
    kanal: KnowledgeChannel,
    knowledge_bundle: dict[str, Any],
    next_steps: list[str],
) -> str:
    object_count = knowledge_bundle.get("anzahl", 0)
    if kanal == KnowledgeChannel.SLACK:
        return (
            f"Onboarding fuer Rolle '{rolle}': {object_count} freigegebene Wissensobjekte sind bereit. "
            f"Naechster Fokus: {'; '.join(next_steps) if next_steps else 'Wissenspaket lesen.'}"
        )
    if kanal == KnowledgeChannel.VOICE:
        return (
            f"Onboarding fuer {rolle}. {object_count} Wissensobjekte stehen bereit. "
            f"Starte mit: {next_steps[0] if next_steps else 'dem freigegebenen Wissenspaket'}."
        )
    return (
        f"Onboarding-Workspace fuer Rolle '{rolle}' erstellt. "
        f"{object_count} freigegebene Wissensobjekte und die naechsten Schritte sind verfuegbar."
    )


def build_onboarding_workspace(
    *,
    db: Session,
    rolle: str,
    kanal: str | KnowledgeChannel | None = None,
    tenant_id: str | None = None,
    employee_ref: str | None = None,
    capability_key: str | None = "onboarding_assistant",
    query: str = "",
    limit: int = 5,
    checklist: dict[str, Any] | None = None,
    onboarding_run: dict[str, Any] | None = None,
) -> OnboardingWorkspace:
    normalized_channel = _normalize_channel(kanal)
    effective_query = query.strip() or f"onboarding standards best practices {rolle}"
    knowledge_bundle = build_runtime_onboarding_bundle(
        db=db,
        rolle=rolle,
        tenant_id=tenant_id,
        limit=limit,
    )
    context_pack = build_runtime_context_pack(
        db=db,
        rolle=rolle,
        kanal=normalized_channel,
        tenant_id=tenant_id,
        capability_key=capability_key,
        query=effective_query,
        limit=limit,
    )
    context_pack_dict = context_pack.as_dict()
    next_steps = _next_steps(checklist, onboarding_run, context_pack_dict)
    return OnboardingWorkspace(
        rolle=rolle,
        kanal=normalized_channel.value,
        tenant_id=tenant_id,
        employee_ref=employee_ref,
        capability_key=capability_key,
        checklist=checklist,
        onboarding_run=onboarding_run,
        knowledge_bundle=knowledge_bundle,
        context_pack=context_pack_dict,
        empfohlene_naechste_schritte=next_steps,
        channel_message=_build_channel_message(
            rolle=rolle,
            kanal=normalized_channel,
            knowledge_bundle=knowledge_bundle,
            next_steps=next_steps,
        ),
    )
