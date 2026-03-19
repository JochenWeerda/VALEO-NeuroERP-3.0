"""
Traversable knowledge graph for knowledge objects, roles, processes and entities.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.core.canonical_process_definitions import get_canonical_process_definitions
from app.core.knowledge_runtime import load_runtime_knowledge_objects


@dataclass
class KnowledgeGraphNode:
    node_id: str
    node_type: str
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "attributes": self.attributes,
        }


@dataclass
class KnowledgeGraphEdge:
    edge_id: str
    source_id: str
    target_id: str
    relation: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation,
            "attributes": self.attributes,
        }


@dataclass
class KnowledgeGraph:
    graph_id: str
    tenant_id: str | None
    nodes: list[KnowledgeGraphNode] = field(default_factory=list)
    edges: list[KnowledgeGraphEdge] = field(default_factory=list)

    def _adjacency(self) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = {node.node_id: [] for node in self.nodes}
        for edge in self.edges:
            adjacency.setdefault(edge.source_id, []).append(edge.target_id)
            adjacency.setdefault(edge.target_id, []).append(edge.source_id)
        return adjacency

    def get_node(self, node_id: str) -> KnowledgeGraphNode | None:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def neighbors(self, node_id: str) -> list[KnowledgeGraphNode]:
        adjacency = self._adjacency()
        return [
            self.get_node(neighbor_id)
            for neighbor_id in adjacency.get(node_id, [])
            if self.get_node(neighbor_id) is not None
        ]

    def find_path(self, source_id: str, target_id: str) -> list[str]:
        if source_id == target_id:
            return [source_id]
        adjacency = self._adjacency()
        visited = {source_id}
        queue: deque[list[str]] = deque([[source_id]])

        while queue:
            path = queue.popleft()
            current = path[-1]
            for neighbor in adjacency.get(current, []):
                if neighbor == target_id:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return []

    def as_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "tenant_id": self.tenant_id,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": [node.as_dict() for node in self.nodes],
            "edges": [edge.as_dict() for edge in self.edges],
        }


def _slug(value: str) -> str:
    return (
        value.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def build_runtime_knowledge_graph(db: Session, tenant_id: str | None = None) -> KnowledgeGraph:
    objects = load_runtime_knowledge_objects(db)
    definitions = get_canonical_process_definitions()

    nodes: dict[str, KnowledgeGraphNode] = {}
    edges: list[KnowledgeGraphEdge] = []

    def ensure_node(node_id: str, node_type: str, label: str, **attributes: Any) -> None:
        if node_id not in nodes:
            nodes[node_id] = KnowledgeGraphNode(
                node_id=node_id,
                node_type=node_type,
                label=label,
                attributes=attributes,
            )

    def add_edge(source_id: str, target_id: str, relation: str, **attributes: Any) -> None:
        edge_id = f"{relation}:{source_id}:{target_id}"
        edges.append(
            KnowledgeGraphEdge(
                edge_id=edge_id,
                source_id=source_id,
                target_id=target_id,
                relation=relation,
                attributes=attributes,
            )
        )

    for obj in objects:
        if tenant_id and obj.tenant_id not in {tenant_id, "system", "global"}:
            continue
        knowledge_node_id = f"knowledge:{obj.knowledge_id}"
        ensure_node(
            knowledge_node_id,
            "knowledge_object",
            obj.titel,
            knowledge_id=obj.knowledge_id,
            typ=obj.typ.value,
            status=obj.status.value,
            tags=obj.tags,
            zielrollen=obj.zielrollen,
        )
        for role in obj.zielrollen:
            role_node_id = f"role:{_slug(role)}"
            ensure_node(role_node_id, "role", role, role=role)
            add_edge(role_node_id, knowledge_node_id, "can_access")

        for tag in obj.tags:
            tag_node_id = f"tag:{_slug(tag)}"
            ensure_node(tag_node_id, "tag", tag, tag=tag)
            add_edge(knowledge_node_id, tag_node_id, "tagged_with")

    for definition in definitions:
        process_node_id = f"process:{definition.process_definition_key}"
        ensure_node(
            process_node_id,
            "process_definition",
            definition.label,
            process_definition_key=definition.process_definition_key,
            business_domain=definition.business_domain,
        )
        previous_aggregate_node_id: str | None = None
        for aggregate_type in definition.aggregate_sequence:
            aggregate_node_id = f"entity:{aggregate_type}"
            ensure_node(
                aggregate_node_id,
                "entity",
                aggregate_type,
                aggregate_type=aggregate_type,
            )
            add_edge(process_node_id, aggregate_node_id, "contains_aggregate")
            if previous_aggregate_node_id is not None:
                add_edge(previous_aggregate_node_id, aggregate_node_id, "precedes")
            previous_aggregate_node_id = aggregate_node_id

        for command_name in definition.action_command_names:
            command_node_id = f"command:{command_name}"
            ensure_node(
                command_node_id,
                "command",
                command_name,
                command_name=command_name,
            )
            add_edge(process_node_id, command_node_id, "uses_command")

    keyword_mappings = {
        "support": ["support", "login", "oidc"],
        "finance": ["kpi", "umsatz", "controlling"],
        "vertrieb": ["vertrieb", "angebot", "markenstil"],
        "settlement": ["settlement", "abrechnung"],
    }
    for node in list(nodes.values()):
        if node.node_type != "knowledge_object":
            continue
        tag_values = {str(tag).lower() for tag in node.attributes.get("tags", [])}
        for definition in definitions:
            process_node_id = f"process:{definition.process_definition_key}"
            process_tokens = set()
            for key, values in keyword_mappings.items():
                if key in definition.process_definition_key:
                    process_tokens.update(values)
            if not process_tokens:
                process_tokens = {
                    token
                    for token in definition.process_definition_key.replace("-", "_").split("_")
                    if token
                }
            if tag_values.intersection(process_tokens):
                add_edge(node.node_id, process_node_id, "supports_process")

    return KnowledgeGraph(
        graph_id="knowledge-core-graph",
        tenant_id=tenant_id,
        nodes=list(nodes.values()),
        edges=edges,
    )
