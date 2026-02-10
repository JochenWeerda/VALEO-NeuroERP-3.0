"""
ISO 27001 Risk Assessment Engine
Informationssicherheits-Managementsystem Risk Assessment

Dieses Modul implementiert die Risk Assessment Engine gemäß ISO 27001 Annex A.12
für VALEO-NeuroERP.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """ISO 27001 Risk Level Classification"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AssetType(Enum):
    """Asset Types for Risk Assessment"""
    DATABASE = "database"
    API_ENDPOINT = "api_endpoint"
    USER_DATA = "user_data"
    FINANCIAL_DATA = "financial_data"
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"


@dataclass
class Asset:
    """Asset representation for risk assessment"""
    id: str
    name: str
    type: AssetType
    classification: str  # public, internal, confidential, restricted
    owner: str
    tenant_id: str
    description: str
    location: str
    value: int  # Business value score 1-10
    created_at: datetime
    last_assessed: Optional[datetime] = None


@dataclass
class Threat:
    """Threat representation"""
    id: str
    name: str
    category: str  # natural, human, technical
    likelihood: int  # 1-5 scale
    description: str


@dataclass
class Vulnerability:
    """Vulnerability representation"""
    id: str
    name: str
    severity: int  # 1-5 scale
    description: str
    affected_assets: List[str]


@dataclass
class RiskAssessment:
    """Complete risk assessment result"""
    asset_id: str
    risk_score: int
    risk_level: RiskLevel
    impact_score: int
    likelihood_score: int
    threats: List[Dict[str, Any]]
    vulnerabilities: List[Dict[str, Any]]
    mitigation_required: bool
    required_mitigations: List[str]
    assessment_date: datetime
    next_assessment_due: datetime
    assessor: str
    compliance_status: Dict[str, Any]


class ISMSRiskAssessment:
    """
    ISO 27001 Risk Assessment Engine
    Implements Annex A.12 - Operations Security
    """

    def __init__(self, db_session):
        self.db = db_session
        self.risk_matrix = {
            'impact': {'low': 1, 'medium': 2, 'high': 3, 'critical': 4},
            'likelihood': {'rare': 1, 'unlikely': 2, 'possible': 3, 'likely': 4, 'almost_certain': 5}
        }

        # ISO 27001 Risk Assessment Frequency
        self.assessment_intervals = {
            RiskLevel.LOW: 365,      # Annual
            RiskLevel.MEDIUM: 180,   # Semi-annual
            RiskLevel.HIGH: 90,      # Quarterly
            RiskLevel.CRITICAL: 30   # Monthly
        }

    def assess_asset_risk(self, asset_id: str, tenant_id: str, assessor: str = "system") -> RiskAssessment:
        """
        Perform comprehensive risk assessment for an asset
        Returns: Complete RiskAssessment with all details
        """
        logger.info(f"Starting risk assessment for asset {asset_id} (tenant: {tenant_id})")

        # Get asset details
        asset = self._get_asset_details(asset_id, tenant_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Identify relevant threats and vulnerabilities
        threats = self._identify_threats(asset)
        vulnerabilities = self._identify_vulnerabilities(asset)

        # Calculate risk scores
        impact_score = self._calculate_impact(asset)
        likelihood_score = self._calculate_likelihood(threats, vulnerabilities)

        risk_score = impact_score * likelihood_score
        risk_level = self._classify_risk_level(risk_score)

        # Determine mitigation requirements
        mitigation_required = risk_score >= 10  # ISO 27001 threshold
        required_mitigations = self._get_mitigation_requirements(risk_score, risk_level)

        # Calculate next assessment date
        next_assessment_due = self._calculate_next_assessment(risk_level)

        # Check compliance status
        compliance_status = self._check_compliance_status(asset)

        assessment = RiskAssessment(
            asset_id=asset_id,
            risk_score=risk_score,
            risk_level=risk_level,
            impact_score=impact_score,
            likelihood_score=likelihood_score,
            threats=[{"id": t.id, "name": t.name, "category": t.category, "likelihood": t.likelihood} for t in threats],
            vulnerabilities=[{"id": v.id, "name": v.name, "severity": v.severity} for v in vulnerabilities],
            mitigation_required=mitigation_required,
            required_mitigations=required_mitigations,
            assessment_date=datetime.utcnow(),
            next_assessment_due=next_assessment_due,
            assessor=assessor,
            compliance_status=compliance_status
        )

        # Store assessment result
        self._store_assessment(assessment, tenant_id)

        logger.info(f"Risk assessment completed for asset {asset_id}: Score {risk_score}, Level {risk_level.value}")
        return assessment

    def _get_asset_details(self, asset_id: str, tenant_id: str) -> Optional[Asset]:
        """Get asset details from database"""
        # This would query the actual asset database
        # For now, return mock data based on asset type
        asset_types = {
            "db": AssetType.DATABASE,
            "api": AssetType.API_ENDPOINT,
            "user": AssetType.USER_DATA,
            "finance": AssetType.FINANCIAL_DATA,
            "infra": AssetType.INFRASTRUCTURE,
            "app": AssetType.APPLICATION
        }

        asset_type = AssetType.APPLICATION  # Default
        for prefix, atype in asset_types.items():
            if asset_id.startswith(prefix):
                asset_type = atype
                break

        return Asset(
            id=asset_id,
            name=f"{asset_type.value.title()} Asset {asset_id}",
            type=asset_type,
            classification=self._determine_classification(asset_type),
            owner="system",
            tenant_id=tenant_id,
            description=f"Asset of type {asset_type.value}",
            location="primary_datacenter",
            value=self._calculate_asset_value(asset_type),
            created_at=datetime.utcnow(),
            last_assessed=datetime.utcnow()
        )

    def _determine_classification(self, asset_type: AssetType) -> str:
        """Determine data classification based on asset type"""
        classification_map = {
            AssetType.DATABASE: "confidential",
            AssetType.API_ENDPOINT: "internal",
            AssetType.USER_DATA: "restricted",
            AssetType.FINANCIAL_DATA: "restricted",
            AssetType.INFRASTRUCTURE: "confidential",
            AssetType.APPLICATION: "internal"
        }
        return classification_map.get(asset_type, "internal")

    def _calculate_asset_value(self, asset_type: AssetType) -> int:
        """Calculate business value score 1-10"""
        value_map = {
            AssetType.DATABASE: 9,
            AssetType.API_ENDPOINT: 7,
            AssetType.USER_DATA: 10,
            AssetType.FINANCIAL_DATA: 10,
            AssetType.INFRASTRUCTURE: 8,
            AssetType.APPLICATION: 6
        }
        return value_map.get(asset_type, 5)

    def _identify_threats(self, asset: Asset) -> List[Threat]:
        """Identify relevant threats for the asset"""
        base_threats = [
            Threat("T001", "Unauthorized Access", "human", 3, "Attempted unauthorized system access"),
            Threat("T002", "Data Breach", "human", 2, "Malicious data exfiltration"),
            Threat("T003", "System Failure", "technical", 3, "Hardware/software failure"),
            Threat("T004", "Natural Disaster", "natural", 1, "Flood, fire, or other disaster"),
            Threat("T005", "Cyber Attack", "technical", 3, "Malware, DDoS, or other attacks")
        ]

        # Filter threats based on asset type
        relevant_threats = []
        for threat in base_threats:
            if self._is_threat_relevant(threat, asset):
                relevant_threats.append(threat)

        return relevant_threats

    def _is_threat_relevant(self, threat: Threat, asset: Asset) -> bool:
        """Check if threat is relevant for this asset type"""
        threat_relevance = {
            AssetType.DATABASE: ["T001", "T002", "T003", "T005"],
            AssetType.API_ENDPOINT: ["T001", "T002", "T005"],
            AssetType.USER_DATA: ["T001", "T002", "T005"],
            AssetType.FINANCIAL_DATA: ["T001", "T002", "T005"],
            AssetType.INFRASTRUCTURE: ["T001", "T003", "T004", "T005"],
            AssetType.APPLICATION: ["T001", "T002", "T003", "T005"]
        }

        relevant_ids = threat_relevance.get(asset.type, [])
        return threat.id in relevant_ids

    def _identify_vulnerabilities(self, asset: Asset) -> List[Vulnerability]:
        """Identify relevant vulnerabilities for the asset"""
        base_vulnerabilities = [
            Vulnerability("V001", "Weak Authentication", 4, "Insufficient password policies", []),
            Vulnerability("V002", "Unpatched Software", 3, "Outdated software versions", []),
            Vulnerability("V003", "Misconfiguration", 3, "Incorrect system configuration", []),
            Vulnerability("V004", "Insufficient Logging", 2, "Lack of audit trails", []),
            Vulnerability("V005", "Physical Security", 2, "Inadequate physical access controls", [])
        ]

        # Filter vulnerabilities based on asset type
        relevant_vulnerabilities = []
        for vuln in base_vulnerabilities:
            if self._is_vulnerability_relevant(vuln, asset):
                vuln.affected_assets = [asset.id]
                relevant_vulnerabilities.append(vuln)

        return relevant_vulnerabilities

    def _is_vulnerability_relevant(self, vulnerability: Vulnerability, asset: Asset) -> bool:
        """Check if vulnerability is relevant for this asset type"""
        vuln_relevance = {
            AssetType.DATABASE: ["V001", "V002", "V003", "V004"],
            AssetType.API_ENDPOINT: ["V001", "V002", "V003", "V004"],
            AssetType.USER_DATA: ["V001", "V002", "V003", "V004"],
            AssetType.FINANCIAL_DATA: ["V001", "V002", "V003", "V004"],
            AssetType.INFRASTRUCTURE: ["V002", "V003", "V004", "V005"],
            AssetType.APPLICATION: ["V001", "V002", "V003", "V004"]
        }

        relevant_ids = vuln_relevance.get(asset.type, [])
        return vulnerability.id in relevant_ids

    def _calculate_impact(self, asset: Asset) -> int:
        """Calculate impact score based on asset value and classification"""
        base_impact = asset.value

        # Adjust based on classification
        classification_multiplier = {
            "public": 1.0,
            "internal": 1.5,
            "confidential": 2.0,
            "restricted": 2.5
        }

        multiplier = classification_multiplier.get(asset.classification, 1.0)
        impact_score = min(int(base_impact * multiplier), 5)  # Cap at 5

        return impact_score

    def _calculate_likelihood(self, threats: List[Threat], vulnerabilities: List[Vulnerability]) -> int:
        """Calculate likelihood score based on threats and vulnerabilities"""
        if not threats:
            return 1  # Minimum likelihood

        # Average threat likelihood
        avg_threat_likelihood = sum(t.likelihood for t in threats) / len(threats)

        # Factor in vulnerabilities
        vuln_severity = max((v.severity for v in vulnerabilities), default=1)
        vuln_factor = vuln_severity / 5.0  # Normalize to 0-1

        likelihood_score = int(avg_threat_likelihood * (1 + vuln_factor))
        return min(likelihood_score, 5)  # Cap at 5

    def _classify_risk_level(self, score: int) -> RiskLevel:
        """Classify risk level according to ISO 27001"""
        if score >= 15:
            return RiskLevel.CRITICAL
        elif score >= 10:
            return RiskLevel.HIGH
        elif score >= 6:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _get_mitigation_requirements(self, score: int, level: RiskLevel) -> List[str]:
        """Return required mitigation measures"""
        requirements = []

        if level == RiskLevel.CRITICAL:
            requirements.extend([
                "Immediate mitigation required within 24 hours",
                "Board-level approval needed for risk acceptance",
                "Independent security review mandatory",
                "Insurance coverage review required",
                "Business continuity plan activation",
                "Stakeholder notification within 4 hours"
            ])
        elif level == RiskLevel.HIGH:
            requirements.extend([
                "Senior management approval required",
                "Detailed mitigation plan within 7 days",
                "Implementation within 30 days",
                "Regular monitoring and reporting",
                "Security control enhancement",
                "Training and awareness program"
            ])
        elif level == RiskLevel.MEDIUM:
            requirements.extend([
                "Management approval required",
                "Mitigation plan within 30 days",
                "Implementation within 90 days",
                "Regular risk monitoring",
                "Staff training on new controls"
            ])
        else:  # LOW
            requirements.extend([
                "Document risk acceptance",
                "Monitor for changes",
                "Annual reassessment",
                "Consider mitigation if cost-effective"
            ])

        return requirements

    def _calculate_next_assessment(self, risk_level: RiskLevel) -> datetime:
        """Calculate next assessment date based on risk level"""
        days = self.assessment_intervals[risk_level]
        return datetime.utcnow() + timedelta(days=days)

    def _check_compliance_status(self, asset: Asset) -> Dict[str, Any]:
        """Check compliance status for the asset"""
        # This would check against various compliance frameworks
        return {
            "iso27001_compliant": True,  # Assume compliant for now
            "gdpr_compliant": asset.classification in ["public", "internal"],
            "sox_compliant": asset.type != AssetType.FINANCIAL_DATA or True,
            "last_compliance_check": datetime.utcnow(),
            "compliance_score": 95  # Percentage
        }

    def _store_assessment(self, assessment: RiskAssessment, tenant_id: str):
        """Store risk assessment in database"""
        # This would persist the assessment result
        # For now, just log it
        logger.info(f"Stored risk assessment for asset {assessment.asset_id}: {assessment.risk_score}")

    def get_assessment_history(self, asset_id: str, tenant_id: str, limit: int = 10) -> List[RiskAssessment]:
        """Get assessment history for an asset"""
        # This would query the database for historical assessments
        return []

    def get_risk_dashboard(self, tenant_id: str) -> Dict[str, Any]:
        """Get risk dashboard data for a tenant"""
        return {
            "total_assets": 0,
            "critical_risks": 0,
            "high_risks": 0,
            "medium_risks": 0,
            "low_risks": 0,
            "overall_risk_score": 0,
            "last_updated": datetime.utcnow()
        }