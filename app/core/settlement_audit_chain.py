"""
Settlement Audit-Hash-Kette — Wave 20 AP1/AP6

GoBD-konforme SHA-256-Verkettung jedes Settlement-Freigabeschritts.
Jeder Ketten-Link enthaelt den Hash seines Vorgaengers, sodass nachträgliche
Manipulation einzelner Eintraege die gesamte Kette invalidiert.

Rechtsgrundlage: §§ 146, 147 AO (Unveraenderbarkeit digitaler Buchungsbelege),
GoBD Rz. 108-112 (Sicherung des Buchungsjournals).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


CHAIN_SCHEMA_VERSION = 1


@dataclass
class AuditChainLink:
    """Ein Glied in der Settlement-Audit-Hash-Kette."""

    link_id: str
    settlement_id: str
    tenant_id: str
    event_type: str           # z.B. "settlement.approval.zur_freigabe"
    actor_id: str
    actor_type: str           # "SACHBEARBEITER" | "ABTEILUNGSLEITER" | "AGENT" | ...
    previous_status: str
    new_status: str
    gross_amount: float
    currency: str
    previous_hash: str        # SHA-256 des unmittelbaren Vorgaengers ("0" * 64 fuer Kettenanker)
    own_hash: str = ""        # wird nach Aufbau gefuellt; leer == noch nicht berechnet
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    process_definition_key: str = "agrar_settlement"
    workflow_version: str = "1.0"
    schema_version: int = CHAIN_SCHEMA_VERSION

    # --- Hash-Berechnung ---

    def _canonical_payload(self) -> str:
        """Kanonisches JSON fuer den Hash — deterministisch sortiert."""
        return json.dumps(
            {
                "link_id": self.link_id,
                "settlement_id": self.settlement_id,
                "tenant_id": self.tenant_id,
                "event_type": self.event_type,
                "actor_id": self.actor_id,
                "actor_type": self.actor_type,
                "previous_status": self.previous_status,
                "new_status": self.new_status,
                "gross_amount": self.gross_amount,
                "currency": self.currency,
                "previous_hash": self.previous_hash,
                "recorded_at": self.recorded_at,
                "process_definition_key": self.process_definition_key,
                "workflow_version": self.workflow_version,
            },
            sort_keys=True,
        )

    def compute_hash(self) -> str:
        """Berechnet den SHA-256 des kanonischen Payloads."""
        return hashlib.sha256(self._canonical_payload().encode("utf-8")).hexdigest()

    def seal(self) -> "AuditChainLink":
        """Setzt own_hash und gibt self zurueck (Fluent Interface)."""
        self.own_hash = self.compute_hash()
        return self

    def verify(self) -> bool:
        """Prueft ob own_hash noch mit dem kanonischen Payload uebereinstimmt."""
        return self.own_hash == self.compute_hash()

    def as_dict(self) -> dict:
        return {
            "link_id": self.link_id,
            "settlement_id": self.settlement_id,
            "tenant_id": self.tenant_id,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "gross_amount": self.gross_amount,
            "currency": self.currency,
            "previous_hash": self.previous_hash,
            "own_hash": self.own_hash,
            "recorded_at": self.recorded_at,
            "process_definition_key": self.process_definition_key,
            "workflow_version": self.workflow_version,
            "schema_version": self.schema_version,
        }


# Sentinel-Hash fuer den Kettenanker (erstes Glied)
CHAIN_GENESIS_HASH = "0" * 64


@dataclass
class SettlementAuditChain:
    """Vollstaendige Audit-Hash-Kette eines Settlements."""

    settlement_id: str
    tenant_id: str
    links: list[AuditChainLink] = field(default_factory=list)
    schema_version: int = CHAIN_SCHEMA_VERSION

    @property
    def head_hash(self) -> str:
        """SHA-256 des letzten Kettenglieds ('neuester Stand')."""
        return self.links[-1].own_hash if self.links else CHAIN_GENESIS_HASH

    def append(
        self,
        *,
        link_id: str,
        event_type: str,
        actor_id: str,
        actor_type: str,
        previous_status: str,
        new_status: str,
        gross_amount: float,
        currency: str = "EUR",
        recorded_at: Optional[str] = None,
    ) -> AuditChainLink:
        """Haengt ein neues Glied an und versiegelt es sofort."""
        link = AuditChainLink(
            link_id=link_id,
            settlement_id=self.settlement_id,
            tenant_id=self.tenant_id,
            event_type=event_type,
            actor_id=actor_id,
            actor_type=actor_type,
            previous_status=previous_status,
            new_status=new_status,
            gross_amount=gross_amount,
            currency=currency,
            previous_hash=self.head_hash,
        )
        if recorded_at:
            link.recorded_at = recorded_at
        link.seal()
        self.links.append(link)
        return link

    def verify_integrity(self) -> "ChainIntegrityResult":
        """
        Prueft die vollstaendige Kette auf Konsistenz.

        Jedes Glied muss:
        1. seinen eigenen Hash korrekt reproduzieren (kein Tampering)
        2. den previous_hash des Nachfolgers auf own_hash setzen
        """
        if not self.links:
            return ChainIntegrityResult(
                settlement_id=self.settlement_id,
                intact=True,
                link_count=0,
                first_broken_link_id=None,
                error=None,
            )

        for i, link in enumerate(self.links):
            # Eigene Hash-Integritaet
            if not link.verify():
                return ChainIntegrityResult(
                    settlement_id=self.settlement_id,
                    intact=False,
                    link_count=len(self.links),
                    first_broken_link_id=link.link_id,
                    error=f"Link {link.link_id}: own_hash stimmt nicht mit Payload ueberein (Tampering).",
                )
            # Kettenglied: previous_hash des Nachfolgers muss own_hash dieses Glieds sein
            if i + 1 < len(self.links):
                expected = link.own_hash
                actual = self.links[i + 1].previous_hash
                if expected != actual:
                    return ChainIntegrityResult(
                        settlement_id=self.settlement_id,
                        intact=False,
                        link_count=len(self.links),
                        first_broken_link_id=self.links[i + 1].link_id,
                        error=(
                            f"Link {self.links[i + 1].link_id}: previous_hash passt nicht "
                            f"zu own_hash von Link {link.link_id} (Kettenbruch)."
                        ),
                    )

        return ChainIntegrityResult(
            settlement_id=self.settlement_id,
            intact=True,
            link_count=len(self.links),
            first_broken_link_id=None,
            error=None,
        )

    def as_dict(self) -> dict:
        integrity = self.verify_integrity()
        return {
            "settlement_id": self.settlement_id,
            "tenant_id": self.tenant_id,
            "schema_version": self.schema_version,
            "link_count": len(self.links),
            "head_hash": self.head_hash,
            "intact": integrity.intact,
            "integrity_error": integrity.error,
            "links": [link.as_dict() for link in self.links],
        }


@dataclass
class ChainIntegrityResult:
    settlement_id: str
    intact: bool
    link_count: int
    first_broken_link_id: Optional[str]
    error: Optional[str]

    def as_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "intact": self.intact,
            "link_count": self.link_count,
            "first_broken_link_id": self.first_broken_link_id,
            "error": self.error,
        }


def build_genesis_chain(
    settlement_id: str,
    tenant_id: str,
    gross_amount: float,
    currency: str = "EUR",
    actor_id: str = "system",
) -> SettlementAuditChain:
    """Baut eine neue Kette mit einem Anker-Link (ENTWURF-Erstanlage)."""
    chain = SettlementAuditChain(settlement_id=settlement_id, tenant_id=tenant_id)
    chain.append(
        link_id=f"{settlement_id}-L000",
        event_type="settlement.created",
        actor_id=actor_id,
        actor_type="SYSTEM",
        previous_status="",
        new_status="ENTWURF",
        gross_amount=gross_amount,
        currency=currency,
    )
    return chain
