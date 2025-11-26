"""
ISO 27001 Risk Management and Assessment
Information Security Risk Management Framework

Dieses Modul implementiert das Risk Management and Assessment Framework
gemäß ISO 27001 Annex A.5 für VALEO-NeuroERP mit Risk Assessment, Treatment und Monitoring.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk impact and likelihood levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RiskCategory(Enum):
    """Risk categories based on ISO 27001"""
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    TECHNICAL = "technical"
    HUMAN = "human"
    PHYSICAL = "physical"
    ENVIRONMENTAL = "environmental"


class RiskStatus(Enum):
    """Risk assessment status"""
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    TREATED = "treated"
    ACCEPTED = "accepted"
    MITIGATED = "mitigated"
    TRANSFERRED = "transferred"
    AVOIDED = "avoided"
    MONITORING = "monitoring"
    CLOSED = "closed"


class RiskTreatment(Enum):
    """Risk treatment options"""
    MODIFY = "modify"  # Reduce likelihood or impact
    AVOID = "avoid"    # Eliminate the risk
    TRANSFER = "transfer"  # Transfer to third party
    ACCEPT = "accept"  # Accept the risk
    SHARE = "share"    # Share with other parties


class RiskSource(Enum):
    """Sources of risk identification"""
    AUDIT = "audit"
    INCIDENT = "incident"
    ASSESSMENT = "assessment"
    MONITORING = "monitoring"
    THREAT_INTELLIGENCE = "threat_intelligence"
    BUSINESS_IMPACT = "business_impact"
    COMPLIANCE_REVIEW = "compliance_review"


@dataclass
class RiskAssessment:
    """Risk assessment record"""
    id: str
    title: str
    description: str
    category: RiskCategory
    source: RiskSource
    likelihood: RiskLevel
    impact: RiskLevel
    risk_score: int  # Calculated from likelihood * impact
    risk_level: RiskLevel  # Overall risk level
    affected_assets: List[str]
    threat_agents: List[str]
    vulnerabilities: List[str]
    existing_controls: List[str]
    status: RiskStatus = RiskStatus.IDENTIFIED
    assessed_by: str = ""
    assessed_at: Optional[datetime] = None
    review_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskTreatmentPlan:
    """Risk treatment plan"""
    id: str
    risk_id: str
    treatment_option: RiskTreatment
    justification: str
    planned_actions: List[Dict[str, Any]]
    responsible_party: str
    target_completion_date: datetime
    estimated_cost: float
    resource_requirements: List[str]
    success_criteria: List[str]
    status: str = "planned"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskRegister:
    """Risk register entry"""
    id: str
    risk_assessment_id: str
    current_likelihood: RiskLevel
    current_impact: RiskLevel
    current_risk_score: int
    residual_likelihood: Optional[RiskLevel] = None
    residual_impact: Optional[RiskLevel] = None
    residual_risk_score: Optional[int] = None
    treatment_status: str = "pending"
    monitoring_frequency: str = "monthly"
    next_review_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    last_updated: datetime = field(default_factory=datetime.utcnow)
    updated_by: str = ""


@dataclass
class RiskMonitoring:
    """Risk monitoring record"""
    id: str
    risk_id: str
    monitoring_date: datetime
    status_change: bool
    new_likelihood: Optional[RiskLevel] = None
    new_impact: Optional[RiskLevel] = None
    new_risk_score: Optional[int] = None
    indicators: Dict[str, Any] = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)
    next_monitoring_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    monitored_by: str = ""


@dataclass
class RiskAppetite:
    """Organizational risk appetite"""
    id: str
    category: RiskCategory
    max_acceptable_risk: RiskLevel
    risk_tolerance_threshold: int  # Risk score threshold
    treatment_required_threshold: int
    senior_management_approval_threshold: int
    automatic_treatment_threshold: int
    is_active: bool = True
    defined_by: str = ""
    defined_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskHeatmap:
    """Risk heatmap data"""
    id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    risk_distribution: Dict[str, int] = field(default_factory=dict)  # Risk level -> count
    category_distribution: Dict[str, int] = field(default_factory=dict)  # Category -> count
    top_risks: List[Dict[str, Any]] = field(default_factory=list)
    emerging_trends: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ISO27001RiskManagement:
    """
    ISO 27001 Risk Management and Assessment
    Implements Annex A.5 - Information Security Risk Management
    """

    def __init__(self, db_session, asset_service=None, threat_service=None):
        self.db = db_session
        self.assets = asset_service
        self.threats = threat_service

        # Risk management components
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        self.risk_treatments: Dict[str, RiskTreatmentPlan] = {}
        self.risk_register: Dict[str, RiskRegister] = {}
        self.risk_monitoring: List[RiskMonitoring] = {}
        self.risk_appetite: Dict[str, RiskAppetite] = {}
        self.risk_heatmaps: List[RiskHeatmap] = {}

        # Risk assessment configuration
        self.risk_config = self._initialize_risk_config()

        # Risk scoring matrix
        self.risk_matrix = self._initialize_risk_matrix()

        # Default risk appetite
        self._initialize_default_risk_appetite()

    def _initialize_risk_config(self) -> Dict[str, Any]:
        """Initialize risk management configuration"""
        return {
            'assessment_frequency': {
                'critical_assets': 'monthly',
                'high_risk_assets': 'quarterly',
                'standard_assets': 'biannual'
            },
            'review_cycles': {
                'risk_register': 30,  # days
                'treatment_plans': 90,  # days
                'risk_appetite': 180   # days
            },
            'escalation_thresholds': {
                'immediate_attention': 15,  # risk score
                'management_review': 12,
                'board_notification': 20
            },
            'monitoring_intervals': {
                'high_risk': 30,   # days
                'medium_risk': 60,
                'low_risk': 90
            }
        }

    def _initialize_risk_matrix(self) -> Dict[Tuple[RiskLevel, RiskLevel], Dict[str, Any]]:
        """Initialize risk scoring matrix"""
        matrix = {}

        # Define risk scores (1-25 scale)
        scores = {
            (RiskLevel.VERY_LOW, RiskLevel.VERY_LOW): {'score': 1, 'level': RiskLevel.VERY_LOW},
            (RiskLevel.VERY_LOW, RiskLevel.LOW): {'score': 2, 'level': RiskLevel.VERY_LOW},
            (RiskLevel.VERY_LOW, RiskLevel.MEDIUM): {'score': 3, 'level': RiskLevel.LOW},
            (RiskLevel.VERY_LOW, RiskLevel.HIGH): {'score': 4, 'level': RiskLevel.LOW},
            (RiskLevel.VERY_LOW, RiskLevel.VERY_HIGH): {'score': 5, 'level': RiskLevel.MEDIUM},

            (RiskLevel.LOW, RiskLevel.VERY_LOW): {'score': 2, 'level': RiskLevel.VERY_LOW},
            (RiskLevel.LOW, RiskLevel.LOW): {'score': 4, 'level': RiskLevel.LOW},
            (RiskLevel.LOW, RiskLevel.MEDIUM): {'score': 6, 'level': RiskLevel.MEDIUM},
            (RiskLevel.LOW, RiskLevel.HIGH): {'score': 8, 'level': RiskLevel.MEDIUM},
            (RiskLevel.LOW, RiskLevel.VERY_HIGH): {'score': 10, 'level': RiskLevel.HIGH},

            (RiskLevel.MEDIUM, RiskLevel.VERY_LOW): {'score': 3, 'level': RiskLevel.LOW},
            (RiskLevel.MEDIUM, RiskLevel.LOW): {'score': 6, 'level': RiskLevel.MEDIUM},
            (RiskLevel.MEDIUM, RiskLevel.MEDIUM): {'score': 9, 'level': RiskLevel.MEDIUM},
            (RiskLevel.MEDIUM, RiskLevel.HIGH): {'score': 12, 'level': RiskLevel.HIGH},
            (RiskLevel.MEDIUM, RiskLevel.VERY_HIGH): {'score': 15, 'level': RiskLevel.HIGH},

            (RiskLevel.HIGH, RiskLevel.VERY_LOW): {'score': 4, 'level': RiskLevel.LOW},
            (RiskLevel.HIGH, RiskLevel.LOW): {'score': 8, 'level': RiskLevel.MEDIUM},
            (RiskLevel.HIGH, RiskLevel.MEDIUM): {'score': 12, 'level': RiskLevel.HIGH},
            (RiskLevel.HIGH, RiskLevel.HIGH): {'score': 16, 'level': RiskLevel.HIGH},
            (RiskLevel.HIGH, RiskLevel.VERY_HIGH): {'score': 20, 'level': RiskLevel.VERY_HIGH},

            (RiskLevel.VERY_HIGH, RiskLevel.VERY_LOW): {'score': 5, 'level': RiskLevel.MEDIUM},
            (RiskLevel.VERY_HIGH, RiskLevel.LOW): {'score': 10, 'level': RiskLevel.HIGH},
            (RiskLevel.VERY_HIGH, RiskLevel.MEDIUM): {'score': 15, 'level': RiskLevel.HIGH},
            (RiskLevel.VERY_HIGH, RiskLevel.HIGH): {'score': 20, 'level': RiskLevel.VERY_HIGH},
            (RiskLevel.VERY_HIGH, RiskLevel.VERY_HIGH): {'score': 25, 'level': RiskLevel.VERY_HIGH}
        }

        matrix.update(scores)
        return matrix

    def _initialize_default_risk_appetite(self):
        """Initialize default risk appetite settings"""
        default_appetite = {
            'strategic': {'max_acceptable': RiskLevel.HIGH, 'tolerance': 12, 'treatment': 8, 'approval': 16, 'auto': 4},
            'operational': {'max_acceptable': RiskLevel.MEDIUM, 'tolerance': 9, 'treatment': 6, 'approval': 12, 'auto': 3},
            'financial': {'max_acceptable': RiskLevel.MEDIUM, 'tolerance': 9, 'treatment': 6, 'approval': 12, 'auto': 3},
            'compliance': {'max_acceptable': RiskLevel.LOW, 'tolerance': 6, 'treatment': 4, 'approval': 8, 'auto': 2},
            'technical': {'max_acceptable': RiskLevel.MEDIUM, 'tolerance': 9, 'treatment': 6, 'approval': 12, 'auto': 3},
            'human': {'max_acceptable': RiskLevel.MEDIUM, 'tolerance': 9, 'treatment': 6, 'approval': 12, 'auto': 3},
            'physical': {'max_acceptable': RiskLevel.HIGH, 'tolerance': 12, 'treatment': 8, 'approval': 16, 'auto': 4},
            'environmental': {'max_acceptable': RiskLevel.MEDIUM, 'tolerance': 9, 'treatment': 6, 'approval': 12, 'auto': 3}
        }

        for category_name, settings in default_appetite.items():
            appetite = RiskAppetite(
                id=f"{category_name}_appetite",
                category=RiskCategory[category_name.upper()],
                max_acceptable_risk=settings['max_acceptable'],
                risk_tolerance_threshold=settings['tolerance'],
                treatment_required_threshold=settings['treatment'],
                senior_management_approval_threshold=settings['approval'],
                automatic_treatment_threshold=settings['auto']
            )
            self.risk_appetite[appetite.id] = appetite

    def assess_risk(self, risk_data: Dict[str, Any]) -> str:
        """
        Perform risk assessment
        Returns risk assessment ID
        """
        risk_id = str(uuid.uuid4())

        # Calculate risk score
        likelihood = RiskLevel[risk_data['likelihood'].upper()]
        impact = RiskLevel[risk_data['impact'].upper()]

        matrix_key = (likelihood, impact)
        risk_calculation = self.risk_matrix.get(matrix_key, {'score': 1, 'level': RiskLevel.VERY_LOW})

        risk = RiskAssessment(
            id=risk_id,
            title=risk_data['title'],
            description=risk_data['description'],
            category=RiskCategory[risk_data['category'].upper()],
            source=RiskSource[risk_data['source'].upper()],
            likelihood=likelihood,
            impact=impact,
            risk_score=risk_calculation['score'],
            risk_level=risk_calculation['level'],
            affected_assets=risk_data.get('affected_assets', []),
            threat_agents=risk_data.get('threat_agents', []),
            vulnerabilities=risk_data.get('vulnerabilities', []),
            existing_controls=risk_data.get('existing_controls', []),
            assessed_by=risk_data.get('assessed_by', 'system')
        )

        risk.assessed_at = datetime.utcnow()
        risk.status = RiskStatus.ASSESSED

        self.risk_assessments[risk_id] = risk

        # Create risk register entry
        self._create_risk_register_entry(risk)

        # Check if treatment is required
        self._evaluate_risk_treatment_requirement(risk)

        logger.info(f"Risk assessed: {risk.title} (Score: {risk.risk_score}, Level: {risk.risk_level.value})")
        return risk_id

    def _create_risk_register_entry(self, risk: RiskAssessment):
        """Create risk register entry"""
        register_entry = RiskRegister(
            id=str(uuid.uuid4()),
            risk_assessment_id=risk.id,
            current_likelihood=risk.likelihood,
            current_impact=risk.impact,
            current_risk_score=risk.risk_score,
            updated_by=risk.assessed_by
        )

        self.risk_register[register_entry.id] = register_entry

    def _evaluate_risk_treatment_requirement(self, risk: RiskAssessment):
        """Evaluate if risk treatment is required"""
        appetite = self.risk_appetite.get(f"{risk.category.value}_appetite")

        if appetite:
            if risk.risk_score >= appetite.treatment_required_threshold:
                # Auto-create treatment plan for high-risk items
                if risk.risk_score >= appetite.automatic_treatment_threshold:
                    self._create_automatic_treatment_plan(risk)
                else:
                    logger.warning(f"Risk treatment required for: {risk.title} (Score: {risk.risk_score})")

    def _create_automatic_treatment_plan(self, risk: RiskAssessment):
        """Create automatic treatment plan for high-risk items"""
        treatment_data = {
            'risk_id': risk.id,
            'treatment_option': 'MODIFY',
            'justification': f'Automatic treatment for high-risk item (Score: {risk.risk_score})',
            'planned_actions': [
                {
                    'action': 'Implement additional controls',
                    'description': 'Review and implement additional security controls',
                    'owner': 'Security Team',
                    'timeline': '30 days'
                },
                {
                    'action': 'Monitor effectiveness',
                    'description': 'Monitor control effectiveness and risk reduction',
                    'owner': 'Risk Manager',
                    'timeline': 'Ongoing'
                }
            ],
            'responsible_party': 'Security Team',
            'target_completion_date': datetime.utcnow() + timedelta(days=30),
            'estimated_cost': 5000.0,
            'resource_requirements': ['Security Team', 'IT Resources'],
            'success_criteria': [
                'Risk score reduced below treatment threshold',
                'Controls implemented and tested',
                'Monitoring established'
            ]
        }

        self.create_risk_treatment_plan(treatment_data)

    def create_risk_treatment_plan(self, treatment_data: Dict[str, Any]) -> str:
        """
        Create risk treatment plan
        Returns treatment plan ID
        """
        plan_id = str(uuid.uuid4())

        plan = RiskTreatmentPlan(
            id=plan_id,
            risk_id=treatment_data['risk_id'],
            treatment_option=RiskTreatment[treatment_data['treatment_option'].upper()],
            justification=treatment_data['justification'],
            planned_actions=treatment_data.get('planned_actions', []),
            responsible_party=treatment_data['responsible_party'],
            target_completion_date=treatment_data['target_completion_date'],
            estimated_cost=treatment_data.get('estimated_cost', 0.0),
            resource_requirements=treatment_data.get('resource_requirements', []),
            success_criteria=treatment_data.get('success_criteria', [])
        )

        self.risk_treatments[plan_id] = plan

        # Update risk status
        if plan.risk_id in self.risk_assessments:
            risk = self.risk_assessments[plan.risk_id]
            risk.status = RiskStatus.TREATED

        logger.info(f"Risk treatment plan created for risk: {plan.risk_id}")
        return plan_id

    def monitor_risk(self, risk_id: str, monitoring_data: Dict[str, Any]) -> str:
        """
        Monitor risk status
        Returns monitoring record ID
        """
        monitoring_id = str(uuid.uuid4())

        # Get current risk register entry
        register_entry = None
        for entry in self.risk_register.values():
            if entry.risk_assessment_id == risk_id:
                register_entry = entry
                break

        if not register_entry:
            raise ValueError(f"Risk register entry not found for risk: {risk_id}")

        # Check for status changes
        status_changed = False
        new_likelihood = monitoring_data.get('new_likelihood')
        new_impact = monitoring_data.get('new_impact')

        if new_likelihood or new_impact:
            status_changed = True
            if new_likelihood:
                register_entry.residual_likelihood = RiskLevel[new_likelihood.upper()]
            if new_impact:
                register_entry.residual_impact = RiskLevel[new_impact.upper()]

            # Recalculate residual risk score
            if register_entry.residual_likelihood and register_entry.residual_impact:
                matrix_key = (register_entry.residual_likelihood, register_entry.residual_impact)
                residual_calc = self.risk_matrix.get(matrix_key, {'score': register_entry.current_risk_score})
                register_entry.residual_risk_score = residual_calc['score']

        # Create monitoring record
        monitoring = RiskMonitoring(
            id=monitoring_id,
            risk_id=risk_id,
            monitoring_date=datetime.utcnow(),
            status_change=status_changed,
            new_likelihood=register_entry.residual_likelihood if status_changed else None,
            new_impact=register_entry.residual_impact if status_changed else None,
            new_risk_score=register_entry.residual_risk_score if status_changed else None,
            indicators=monitoring_data.get('indicators', {}),
            actions_taken=monitoring_data.get('actions_taken', []),
            monitored_by=monitoring_data.get('monitored_by', 'system')
        )

        self.risk_monitoring.append(monitoring)

        # Update register entry
        register_entry.last_updated = datetime.utcnow()
        register_entry.updated_by = monitoring.monitored_by

        logger.info(f"Risk monitoring completed for risk: {risk_id} (Status changed: {status_changed})")
        return monitoring_id

    def generate_risk_heatmap(self, period_days: int = 90) -> str:
        """
        Generate risk heatmap
        Returns heatmap ID
        """
        heatmap_id = str(uuid.uuid4())

        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)

        # Analyze risk distribution
        risk_distribution = {}
        category_distribution = {}
        top_risks = []

        for risk in self.risk_assessments.values():
            # Risk level distribution
            level_key = risk.risk_level.value
            risk_distribution[level_key] = risk_distribution.get(level_key, 0) + 1

            # Category distribution
            category_key = risk.category.value
            category_distribution[category_key] = category_distribution.get(category_key, 0) + 1

            # Top risks (by score)
            top_risks.append({
                'id': risk.id,
                'title': risk.title,
                'score': risk.risk_score,
                'level': risk.risk_level.value,
                'category': risk.category.value
            })

        # Sort top risks
        top_risks.sort(key=lambda x: x['score'], reverse=True)
        top_risks = top_risks[:10]  # Top 10

        # Generate recommendations
        recommendations = self._generate_heatmap_recommendations(risk_distribution, category_distribution)

        heatmap = RiskHeatmap(
            id=heatmap_id,
            generated_at=datetime.utcnow(),
            period_start=period_start,
            period_end=period_end,
            risk_distribution=risk_distribution,
            category_distribution=category_distribution,
            top_risks=top_risks,
            recommendations=recommendations
        )

        self.risk_heatmaps.append(heatmap)

        logger.info(f"Risk heatmap generated for period: {period_start.date()} to {period_end.date()}")
        return heatmap_id

    def _generate_heatmap_recommendations(self, risk_dist: Dict[str, int],
                                        category_dist: Dict[str, int]) -> List[str]:
        """Generate heatmap recommendations"""
        recommendations = []

        # Check for high concentration of high-risk items
        high_risk_count = risk_dist.get('high', 0) + risk_dist.get('very_high', 0)
        if high_risk_count > len(self.risk_assessments) * 0.2:  # More than 20%
            recommendations.append("High concentration of high-risk items detected - prioritize treatment plans")

        # Check for category concentrations
        max_category = max(category_dist.items(), key=lambda x: x[1])
        if max_category[1] > len(self.risk_assessments) * 0.3:  # More than 30% in one category
            recommendations.append(f"Risk concentration in {max_category[0]} category - review category-specific controls")

        # General recommendations
        recommendations.extend([
            "Regular risk assessments should be conducted quarterly",
            "Ensure risk treatment plans are implemented within defined timelines",
            "Monitor emerging risks and update risk register accordingly"
        ])

        return recommendations

    def get_risk_management_dashboard(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate comprehensive risk management dashboard"""
        # Get current risk statistics
        total_risks = len(self.risk_assessments)
        assessed_risks = len([r for r in self.risk_assessments.values() if r.status != RiskStatus.IDENTIFIED])
        treated_risks = len([r for r in self.risk_assessments.values() if r.status in [RiskStatus.TREATED, RiskStatus.MITIGATED]])

        # Risk distribution by level
        risk_by_level = {}
        for risk in self.risk_assessments.values():
            level = risk.risk_level.value
            risk_by_level[level] = risk_by_level.get(level, 0) + 1

        # Risk distribution by category
        risk_by_category = {}
        for risk in self.risk_assessments.values():
            category = risk.category.value
            risk_by_category[category] = risk_by_category.get(category, 0) + 1

        # Treatment plan status
        treatment_stats = {
            'total_plans': len(self.risk_treatments),
            'completed_plans': len([p for p in self.risk_treatments.values() if p.status == 'completed']),
            'overdue_plans': len([p for p in self.risk_treatments.values()
                                if p.target_completion_date < datetime.utcnow() and p.status != 'completed'])
        }

        # Recent monitoring activities
        recent_monitoring = [m for m in self.risk_monitoring[-20:]]  # Last 20 monitoring records

        # Active alerts (high-risk items requiring attention)
        active_alerts = []
        for risk in self.risk_assessments.values():
            appetite = self.risk_appetite.get(f"{risk.category.value}_appetite")
            if appetite and risk.risk_score >= appetite.senior_management_approval_threshold:
                active_alerts.append({
                    'risk_id': risk.id,
                    'title': risk.title,
                    'score': risk.risk_score,
                    'level': risk.risk_level.value,
                    'category': risk.category.value
                })

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'risk_statistics': {
                'total_risks': total_risks,
                'assessed_risks': assessed_risks,
                'treated_risks': treated_risks,
                'assessment_completion_rate': (assessed_risks / total_risks * 100) if total_risks > 0 else 0,
                'treatment_completion_rate': (treated_risks / assessed_risks * 100) if assessed_risks > 0 else 0
            },
            'risk_distribution': {
                'by_level': risk_by_level,
                'by_category': risk_by_category
            },
            'treatment_statistics': treatment_stats,
            'active_alerts': active_alerts[:10],  # Top 10 alerts
            'recent_monitoring': [
                {
                    'risk_id': m.risk_id,
                    'monitoring_date': m.monitoring_date.isoformat(),
                    'status_changed': m.status_change,
                    'monitored_by': m.monitored_by
                } for m in recent_monitoring
            ],
            'risk_appetite_status': self._get_risk_appetite_status(),
            'upcoming_reviews': self._get_upcoming_reviews()
        }

    def _get_risk_appetite_status(self) -> Dict[str, Any]:
        """Get risk appetite compliance status"""
        appetite_status = {}

        for appetite in self.risk_appetite.values():
            category_risks = [r for r in self.risk_assessments.values() if r.category == appetite.category]
            exceeding_risks = [r for r in category_risks if r.risk_score > appetite.risk_tolerance_threshold]

            appetite_status[appetite.category.value] = {
                'appetite_level': appetite.max_acceptable_risk.value,
                'tolerance_threshold': appetite.risk_tolerance_threshold,
                'total_risks': len(category_risks),
                'exceeding_risks': len(exceeding_risks),
                'compliance_rate': ((len(category_risks) - len(exceeding_risks)) / len(category_risks) * 100) if category_risks else 100
            }

        return appetite_status

    def _get_upcoming_reviews(self) -> List[Dict[str, Any]]:
        """Get upcoming risk reviews"""
        upcoming_reviews = []

        # Check risk register review dates
        for register in self.risk_register.values():
            if register.next_review_date > datetime.utcnow() and register.next_review_date < datetime.utcnow() + timedelta(days=30):
                upcoming_reviews.append({
                    'type': 'risk_register_review',
                    'item_id': register.id,
                    'due_date': register.next_review_date.isoformat(),
                    'days_until_due': (register.next_review_date - datetime.utcnow()).days
                })

        # Check treatment plan reviews
        for plan in self.risk_treatments.values():
            if plan.target_completion_date > datetime.utcnow() and plan.target_completion_date < datetime.utcnow() + timedelta(days=30):
                upcoming_reviews.append({
                    'type': 'treatment_plan_review',
                    'item_id': plan.id,
                    'due_date': plan.target_completion_date.isoformat(),
                    'days_until_due': (plan.target_completion_date - datetime.utcnow()).days
                })

        return sorted(upcoming_reviews, key=lambda x: x['days_until_due'])

    def check_risk_management_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 risk management compliance"""
        assessments = list(self.risk_assessments.values())
        treatments = list(self.risk_treatments.values())
        monitoring_records = self.risk_monitoring[-50:]  # Last 50 monitoring records

        compliance_status = self._assess_risk_management_compliance(assessments, treatments, monitoring_records)

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_status['compliance_score'],
            'total_issues': len(compliance_status['issues']),
            'issues': compliance_status['issues'],
            'recommendations': compliance_status['recommendations'],
            'iso_standard': 'ISO 27001:2022',
            'annex': 'A.5 Information Security Risk Management',
            'last_check': datetime.utcnow().isoformat()
        }

    def _assess_risk_management_compliance(self, assessments: List[RiskAssessment],
                                         treatments: List[RiskTreatmentPlan],
                                         monitoring: List[RiskMonitoring]) -> Dict[str, Any]:
        """Assess ISO 27001 risk management compliance"""
        issues = []

        # Check risk assessment coverage
        if len(assessments) < 10:  # Arbitrary minimum
            issues.append("Insufficient number of risk assessments conducted")

        # Check assessment completeness
        incomplete_assessments = len([a for a in assessments if not a.assessed_at])
        if incomplete_assessments > 0:
            issues.append(f"{incomplete_assessments} risk assessments are incomplete")

        # Check treatment plan coverage
        high_risk_assessments = [a for a in assessments if a.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]]
        treated_high_risks = len([t for t in treatments if any(a.id == t.risk_id for a in high_risk_assessments)])
        if treated_high_risks < len(high_risk_assessments) * 0.8:  # Less than 80% treated
            issues.append("Insufficient treatment plans for high-risk items")

        # Check monitoring frequency
        recent_monitoring = len([m for m in monitoring if (datetime.utcnow() - m.monitoring_date).days <= 90])
        if recent_monitoring < len(assessments) * 0.5:  # Less than 50% monitored in last 90 days
            issues.append("Risk monitoring frequency is insufficient")

        # Check risk appetite definition
        if len(self.risk_appetite) < len(RiskCategory):
            issues.append("Risk appetite not defined for all risk categories")

        compliance_score = max(0, 100 - (len(issues) * 10))

        return {
            'compliance_score': compliance_score,
            'issues': issues,
            'recommendations': self._generate_risk_compliance_recommendations(issues)
        }

    def _generate_risk_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Generate risk management compliance recommendations"""
        recommendations = []

        if any('assessment' in issue.lower() for issue in issues):
            recommendations.append("Conduct comprehensive risk assessments covering all information assets and processes")

        if any('treatment' in issue.lower() for issue in issues):
            recommendations.append("Develop and implement risk treatment plans for all high-risk items")

        if any('monitoring' in issue.lower() for issue in issues):
            recommendations.append("Establish regular risk monitoring and review processes")

        if any('appetite' in issue.lower() for issue in issues):
            recommendations.append("Define organizational risk appetite for all risk categories")

        recommendations.append("Maintain regular risk management reviews and updates to the risk register")

        return recommendations