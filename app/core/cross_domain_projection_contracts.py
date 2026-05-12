"""
Cross-Domain Projection Contracts
Wave 43 — Checkpoints & Cross-Domain Projections
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum


class ProjectionStatus(str, Enum):
    AKTUELL = "AKTUELL"
    VERZOEGERT = "VERZOEGERT"
    VERALTET = "VERALTET"
    FEHLERHAFT = "FEHLERHAFT"
    AUFBAUEND = "AUFBAUEND"


class KonsistenzLevel(str, Enum):
    STARK = "STARK"
    LESEKONSISTENT = "LESEKONSISTENT"
    EVENTUAL = "EVENTUAL"
    SNAPSHOT = "SNAPSHOT"


class ProjectionLagStufe(str, Enum):
    KEIN = "KEIN"
    GERING = "GERING"
    MODERAT = "MODERAT"
    KRITISCH = "KRITISCH"


def berechne_lag_stufe(lag_sekunden: float) -> ProjectionLagStufe:
    if lag_sekunden >= 60:
        return ProjectionLagStufe.KRITISCH
    if lag_sekunden >= 10:
        return ProjectionLagStufe.MODERAT
    if lag_sekunden >= 1:
        return ProjectionLagStufe.GERING
    return ProjectionLagStufe.KEIN


@dataclass
class DomainProjection:
    projection_id: str
    projection_name: str
    quell_domain: str
    ziel_domain: str
    status: ProjectionStatus
    letztes_event_id: str
    letztes_update: datetime.datetime
    konsistenz_level: KonsistenzLevel
    lag_sekunden: float
    tenant_id: str

    @property
    def lag_stufe(self) -> ProjectionLagStufe:
        return berechne_lag_stufe(self.lag_sekunden)

    @property
    def ist_aktuell(self) -> bool:
        return self.status == ProjectionStatus.AKTUELL

    def as_dict(self) -> dict:
        return {
            "projection_id": self.projection_id,
            "projection_name": self.projection_name,
            "quell_domain": self.quell_domain,
            "ziel_domain": self.ziel_domain,
            "status": self.status.value,
            "letztes_event_id": self.letztes_event_id,
            "letztes_update": self.letztes_update.isoformat(),
            "konsistenz_level": self.konsistenz_level.value,
            "lag_sekunden": self.lag_sekunden,
            "tenant_id": self.tenant_id,
            "lag_stufe": self.lag_stufe.value,
            "ist_aktuell": self.ist_aktuell,
        }


@dataclass
class CrossDomainJoin:
    join_id: str
    links_projection_id: str
    rechts_projection_id: str
    join_typ: str
    join_felder: list
    konsistenz_level: KonsistenzLevel

    @property
    def ist_stark_konsistent(self) -> bool:
        return self.konsistenz_level in {KonsistenzLevel.STARK, KonsistenzLevel.LESEKONSISTENT}

    def as_dict(self) -> dict:
        return {
            "join_id": self.join_id,
            "links_projection_id": self.links_projection_id,
            "rechts_projection_id": self.rechts_projection_id,
            "join_typ": self.join_typ,
            "join_felder": self.join_felder,
            "konsistenz_level": self.konsistenz_level.value,
            "ist_stark_konsistent": self.ist_stark_konsistent,
        }


@dataclass
class ProjectionGesundheit:
    gesundheits_id: str
    geprueft_am: datetime.datetime
    projektionen: list = field(default_factory=list)

    @property
    def kritische_projektionen(self) -> list:
        result = []
        for p in self.projektionen:
            if p.lag_stufe == ProjectionLagStufe.KRITISCH or p.status in {
                ProjectionStatus.FEHLERHAFT,
                ProjectionStatus.VERALTET,
            }:
                result.append(p)
        return result

    @property
    def gesamtstatus(self) -> ProjectionStatus:
        if any(p.status == ProjectionStatus.FEHLERHAFT for p in self.projektionen):
            return ProjectionStatus.FEHLERHAFT
        if any(p.status == ProjectionStatus.VERALTET for p in self.projektionen):
            return ProjectionStatus.VERALTET
        if any(p.lag_stufe == ProjectionLagStufe.KRITISCH for p in self.projektionen):
            return ProjectionStatus.VERZOEGERT
        if any(p.status == ProjectionStatus.VERZOEGERT for p in self.projektionen):
            return ProjectionStatus.VERZOEGERT
        return ProjectionStatus.AKTUELL

    def as_dict(self) -> dict:
        return {
            "gesundheits_id": self.gesundheits_id,
            "geprueft_am": self.geprueft_am.isoformat(),
            "projektionen_anzahl": len(self.projektionen),
            "kritische_anzahl": len(self.kritische_projektionen),
            "gesamtstatus": self.gesamtstatus.value,
        }


def erstelle_projektions_gesundheit(
    gesundheits_id: str,
    projektionen: list,
    geprueft_am=None,
) -> ProjectionGesundheit:
    return ProjectionGesundheit(
        gesundheits_id=gesundheits_id,
        geprueft_am=geprueft_am if geprueft_am is not None else datetime.datetime.utcnow(),
        projektionen=projektionen,
    )


def get_default_projektionen(tenant_id: str = "TENANT-001") -> list:
    now = datetime.datetime.utcnow()
    return [
        DomainProjection(
            projection_id="PR-001",
            projection_name="agrar_zu_finance",
            quell_domain="agrar",
            ziel_domain="finance",
            status=ProjectionStatus.AKTUELL,
            letztes_event_id="EVT-001",
            letztes_update=now,
            konsistenz_level=KonsistenzLevel.STARK,
            lag_sekunden=0.3,
            tenant_id=tenant_id,
        ),
        DomainProjection(
            projection_id="PR-002",
            projection_name="agrar_zu_lager",
            quell_domain="agrar",
            ziel_domain="lager",
            status=ProjectionStatus.AKTUELL,
            letztes_event_id="EVT-002",
            letztes_update=now,
            konsistenz_level=KonsistenzLevel.EVENTUAL,
            lag_sekunden=4.2,
            tenant_id=tenant_id,
        ),
        DomainProjection(
            projection_id="PR-003",
            projection_name="finance_zu_controlling",
            quell_domain="finance",
            ziel_domain="controlling",
            status=ProjectionStatus.VERZOEGERT,
            letztes_event_id="EVT-003",
            letztes_update=now,
            konsistenz_level=KonsistenzLevel.SNAPSHOT,
            lag_sekunden=75.0,
            tenant_id=tenant_id,
        ),
        DomainProjection(
            projection_id="PR-004",
            projection_name="compliance_zu_reporting",
            quell_domain="compliance",
            ziel_domain="reporting",
            status=ProjectionStatus.AKTUELL,
            letztes_event_id="EVT-004",
            letztes_update=now,
            konsistenz_level=KonsistenzLevel.LESEKONSISTENT,
            lag_sekunden=0.8,
            tenant_id=tenant_id,
        ),
        DomainProjection(
            projection_id="PR-005",
            projection_name="finance_zu_audit",
            quell_domain="finance",
            ziel_domain="audit",
            status=ProjectionStatus.FEHLERHAFT,
            letztes_event_id="EVT-005",
            letztes_update=now,
            konsistenz_level=KonsistenzLevel.STARK,
            lag_sekunden=120.0,
            tenant_id=tenant_id,
        ),
    ]
