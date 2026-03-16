"""
Feature Flag Contracts — Wave 45
Tenant-spezifische Feature-Flags für den Process-Kernel:
Rollout-Strategien, A/B-Varianten, Kill-Switches und Zugangsevaluierung.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class FeatureFlagStatus(str, Enum):
    AKTIV = "AKTIV"
    INAKTIV = "INAKTIV"
    ROLLOUT = "ROLLOUT"           # Schrittweiser Rollout
    ABGEKUENDIGT = "ABGEKUENDIGT"  # Geplante Abschaltung


class RolloutStrategie(str, Enum):
    ALLE = "ALLE"                    # Für alle Tenants aktiv
    PROZENTSATZ = "PROZENTSATZ"      # Hash-basierter Rollout-Prozentsatz
    TENANT_LISTE = "TENANT_LISTE"    # Nur explizit gelistete Tenants
    ROLLE = "ROLLE"                  # Nur bestimmte Rollen
    KILL_SWITCH = "KILL_SWITCH"      # Sofortabschaltung — immer False


class FlagVariante(str, Enum):
    STANDARD = "STANDARD"
    A = "A"
    B = "B"
    C = "C"


# ---------------------------------------------------------------------------
# Feature-Flag
# ---------------------------------------------------------------------------

@dataclass
class FeatureFlag:
    """Definition eines Feature-Flags mit Rollout-Strategie."""
    flag_id: str
    flag_name: str
    status: FeatureFlagStatus
    rollout_strategie: RolloutStrategie
    rollout_prozentsatz: int = 100          # 0–100, nur relevant bei PROZENTSATZ
    erlaubte_tenants: list[str] = field(default_factory=list)
    erlaubte_rollen: list[str] = field(default_factory=list)
    variante: FlagVariante = FlagVariante.STANDARD
    beschreibung: str = ""

    @property
    def ist_aktiv(self) -> bool:
        return self.status == FeatureFlagStatus.AKTIV

    @property
    def ist_kill_switch(self) -> bool:
        return self.rollout_strategie == RolloutStrategie.KILL_SWITCH

    def pruefe_zugang(
        self,
        tenant_id: str,
        rolle: str = "",
    ) -> bool:
        """
        Prüft ob ein Tenant/eine Rolle Zugang zu diesem Feature hat.

        Logik:
        - KILL_SWITCH oder INAKTIV → immer False
        - ALLE → True
        - TENANT_LISTE → tenant_id muss in erlaubte_tenants sein
        - ROLLE → rolle muss in erlaubte_rollen sein (wenn Liste nicht leer)
        - PROZENTSATZ → hash(tenant_id) % 100 < rollout_prozentsatz
        """
        if self.ist_kill_switch or self.status == FeatureFlagStatus.INAKTIV:
            return False

        if self.rollout_strategie == RolloutStrategie.ALLE:
            return True

        if self.rollout_strategie == RolloutStrategie.TENANT_LISTE:
            return tenant_id in self.erlaubte_tenants

        if self.rollout_strategie == RolloutStrategie.ROLLE:
            if not self.erlaubte_rollen:
                return True
            return rolle in self.erlaubte_rollen

        if self.rollout_strategie == RolloutStrategie.PROZENTSATZ:
            bucket = abs(hash(tenant_id)) % 100
            return bucket < self.rollout_prozentsatz

        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "flag_id": self.flag_id,
            "flag_name": self.flag_name,
            "status": self.status.value,
            "rollout_strategie": self.rollout_strategie.value,
            "rollout_prozentsatz": self.rollout_prozentsatz,
            "erlaubte_tenants": self.erlaubte_tenants,
            "erlaubte_rollen": self.erlaubte_rollen,
            "variante": self.variante.value,
            "ist_aktiv": self.ist_aktiv,
            "ist_kill_switch": self.ist_kill_switch,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Feature-Flag-Evaluierung
# ---------------------------------------------------------------------------

@dataclass
class FeatureFlagEvaluierung:
    """Ergebnis der Zugangs-Evaluierung eines Flags für einen Tenant."""
    flag_id: str
    flag_name: str
    tenant_id: str
    rolle: str
    zugang_gewaehrt: bool
    variante: FlagVariante
    evaluiert_am: datetime

    @property
    def hat_zugang(self) -> bool:
        return self.zugang_gewaehrt

    def as_dict(self) -> dict[str, Any]:
        return {
            "flag_id": self.flag_id,
            "flag_name": self.flag_name,
            "tenant_id": self.tenant_id,
            "rolle": self.rolle,
            "zugang_gewaehrt": self.zugang_gewaehrt,
            "hat_zugang": self.hat_zugang,
            "variante": self.variante.value,
            "evaluiert_am": self.evaluiert_am.isoformat(),
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def evaluiere_flags(
    tenant_id: str,
    rolle: str,
    flags: list[FeatureFlag],
    evaluiert_am: datetime | None = None,
) -> list[FeatureFlagEvaluierung]:
    """Evaluiert alle Flags für einen Tenant und eine Rolle."""
    ts = evaluiert_am or datetime.utcnow()
    return [
        FeatureFlagEvaluierung(
            flag_id=f.flag_id,
            flag_name=f.flag_name,
            tenant_id=tenant_id,
            rolle=rolle,
            zugang_gewaehrt=f.pruefe_zugang(tenant_id, rolle),
            variante=f.variante,
            evaluiert_am=ts,
        )
        for f in flags
    ]


def get_aktive_flag_ids(
    tenant_id: str,
    rolle: str,
    flags: list[FeatureFlag],
) -> list[str]:
    """Gibt die flag_ids zurück, für die der Tenant/die Rolle Zugang hat."""
    return [
        f.flag_id for f in flags
        if f.pruefe_zugang(tenant_id, rolle)
    ]


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_feature_flags() -> list[FeatureFlag]:
    """Gibt 5 Standard-Feature-Flags zurück."""
    return [
        FeatureFlag(
            flag_id="FF-001",
            flag_name="process_kernel_v2_routing",
            status=FeatureFlagStatus.AKTIV,
            rollout_strategie=RolloutStrategie.ALLE,
            beschreibung="Neues priorisiertes Routing-System (Wave 44)",
        ),
        FeatureFlag(
            flag_id="FF-002",
            flag_name="event_replay_ui",
            status=FeatureFlagStatus.ROLLOUT,
            rollout_strategie=RolloutStrategie.PROZENTSATZ,
            rollout_prozentsatz=30,
            beschreibung="Event-Replay-UI für Sachbearbeiter (30% Rollout)",
        ),
        FeatureFlag(
            flag_id="FF-003",
            flag_name="gobd_audit_chain",
            status=FeatureFlagStatus.AKTIV,
            rollout_strategie=RolloutStrategie.TENANT_LISTE,
            erlaubte_tenants=["TENANT-001", "TENANT-002", "TENANT-003"],
            variante=FlagVariante.A,
            beschreibung="GoBD-Audit-Trail-Verkettung (Wave 40) — Pilot-Tenants",
        ),
        FeatureFlag(
            flag_id="FF-004",
            flag_name="ki_bestellvorschlag_v2",
            status=FeatureFlagStatus.ROLLOUT,
            rollout_strategie=RolloutStrategie.ROLLE,
            erlaubte_rollen=["einkaufsleiter", "disposition"],
            variante=FlagVariante.B,
            beschreibung="KI-Bestellvorschlag v2 nur für Einkaufsleiter und Disposition",
        ),
        FeatureFlag(
            flag_id="FF-005",
            flag_name="legacy_settlement_engine",
            status=FeatureFlagStatus.INAKTIV,
            rollout_strategie=RolloutStrategie.KILL_SWITCH,
            beschreibung="Legacy-Settlement-Engine — dauerhaft deaktiviert",
        ),
    ]
