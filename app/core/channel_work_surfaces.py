"""
Channel-native work surfaces for Slack/Teams based on the knowledge core.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.knowledge_core_contracts import KnowledgeChannel
from app.core.knowledge_runtime import build_runtime_context_pack, retrieve_runtime_knowledge
from app.core.knowledge_core_contracts import KnowledgeObjectTyp, KnowledgeRetrievalRequest, KnowledgeStatus


@dataclass
class ChannelKnowledgeResponse:
    kanal: str
    rolle: str
    tenant_id: str | None
    query: str
    answer: str
    knowledge_ids: list[str]
    standards: list[str]
    prompt_hinweise: list[str]
    citations: list[dict]

    def as_dict(self) -> dict:
        return {
            "kanal": self.kanal,
            "rolle": self.rolle,
            "tenant_id": self.tenant_id,
            "query": self.query,
            "answer": self.answer,
            "knowledge_ids": self.knowledge_ids,
            "standards": self.standards,
            "prompt_hinweise": self.prompt_hinweise,
            "citations": self.citations,
        }


def _build_answer(query: str, citations: list[dict]) -> str:
    if not citations:
        if query.strip():
            return (
                f"Zu '{query}' wurde im freigegebenen Wissensbestand kein passender Treffer gefunden. "
                "Bitte Query praezisieren oder fehlendes Wissen nachpflegen."
            )
        return "Es wurden keine freigegebenen Wissensobjekte fuer diese Anfrage gefunden."

    top = citations[0]
    answer = top.get("kurztext") or f"Relevantes Wissen wurde in {top['knowledge_id']} gefunden."
    if len(citations) > 1:
        answer += f" Zusaetzlicher Kontext kommt aus {', '.join(item['knowledge_id'] for item in citations[1:])}."
    return answer


def build_channel_knowledge_response(
    *,
    db: Session,
    kanal: KnowledgeChannel,
    rolle: str,
    tenant_id: str | None,
    query: str,
    capability_key: str | None = None,
    limit: int = 4,
) -> ChannelKnowledgeResponse:
    request = KnowledgeRetrievalRequest(
        query=query,
        typen=[],
        tags=[],
        tenant_id=tenant_id,
        status=KnowledgeStatus.FREIGEGEBEN,
        nur_agentenfaehig=True,
        rolle=rolle,
        limit=limit,
    )
    citations = retrieve_runtime_knowledge(db, request)
    pack = build_runtime_context_pack(
        db=db,
        rolle=rolle,
        kanal=kanal,
        tenant_id=tenant_id,
        capability_key=capability_key,
        query=query,
        limit=limit,
    )
    return ChannelKnowledgeResponse(
        kanal=kanal.value,
        rolle=rolle,
        tenant_id=tenant_id,
        query=query,
        answer=_build_answer(query, citations),
        knowledge_ids=pack.knowledge_ids,
        standards=pack.standards,
        prompt_hinweise=pack.prompt_hinweise,
        citations=citations,
    )
