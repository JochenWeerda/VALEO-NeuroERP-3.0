import { SupplierId } from '../../core/entities/supplier';
export interface RiskAssessment {
    assessmentId: string;
    supplierId: SupplierId;
    overallScore: number;
    riskLevel: RiskLevel;
    categories: RiskCategories;
    esgScore: EsgScore | undefined;
    assessedAt: Date;
    assessedBy: string;
    validUntil: Date;
    factors: RiskFactor[];
    recommendations: RiskRecommendation[];
}
export declare enum RiskLevel {
    LOW = "low",// 0-25
    MEDIUM = "medium",// 26-50
    HIGH = "high",// 51-75
    CRITICAL = "critical"
}
export interface RiskCategories {
    cyber: number;
    compliance: number;
    financial: number;
    geographic: number;
    operational: number;
    reputational: number;
}
export interface EsgScore {
    environmental: number;
    social: number;
    governance: number;
    overall: number;
    disclosures: EsgDisclosure[];
}
export interface EsgDisclosure {
    standard: string;
    year: number;
    scope3Emissions?: number;
    renewableEnergyPercentage?: number;
    diversityRatio?: number;
    verified: boolean;
    lastAudit?: Date;
}
export interface RiskFactor {
    category: keyof RiskCategories;
    factor: string;
    score: number;
    weight: number;
    evidence: string[];
    mitigation: string | undefined;
}
export interface RiskRecommendation {
    type: RecommendationType;
    priority: 'low' | 'medium' | 'high' | 'critical';
    description: string;
    actions: string[];
    deadline?: Date;
    responsibleParty?: string;
}
export declare enum RecommendationType {
    MONITORING = "monitoring",
    MITIGATION = "mitigation",
    CONTRACTUAL = "contractual",
    ESCALATION = "escalation",
    TERMINATION = "termination"
}
export interface RiskThresholds {
    cyber: {
        low: number;
        medium: number;
        high: number;
        critical: number;
    };
    compliance: {
        low: number;
        medium: number;
        high: number;
        critical: number;
    };
    financial: {
        low: number;
        medium: number;
        high: number;
        critical: number;
    };
    geographic: {
        low: number;
        medium: number;
        high: number;
        critical: number;
    };
    operational: {
        low: number;
        medium: number;
        high: number;
        critical: number;
    };
    reputational: {
        low: number;
        medium: number;
        high: number;
        critical: number;
    };
    overall: {
        low: number;
        medium: number;
        high: number;
        critical: number;
    };
}
export declare class RiskAssessmentEngine {
    private readonly defaultThresholds;
    /**
     * Perform comprehensive risk assessment for a supplier
     */
    assessSupplierRisk(supplierId: SupplierId, supplierData: SupplierAssessmentData, assessmentContext: AssessmentContext): Promise<RiskAssessment>;
    /**
     * Collect all relevant risk factors for assessment
     */
    private collectRiskFactors;
    /**
     * Assess cybersecurity risk factors
     */
    private assessCyberRisk;
    /**
     * Assess compliance risk factors
     */
    private assessComplianceRisk;
    /**
     * Assess financial risk factors
     */
    private assessFinancialRisk;
    /**
     * Assess geographic risk factors
     */
    private assessGeographicRisk;
    /**
     * Assess operational risk factors
     */
    private assessOperationalRisk;
    /**
     * Assess reputational risk factors
     */
    private assessReputationalRisk;
    /**
     * Assess ESG risk factors
     */
    private assessEsgRisk;
    /**
     * Calculate category scores from factors
     */
    private calculateCategoryScores;
    /**
     * Calculate overall risk score
     */
    private calculateOverallScore;
    /**
     * Determine risk level from score
     */
    private determineRiskLevel;
    /**
     * Generate recommendations based on assessment
     */
    private generateRecommendations;
    private generateAssessmentId;
    private calculateValidityDate;
    private getRegionFromCountry;
    private assessSizeRisk;
    private assessConcentrationRisk;
    private assessIndustryReputation;
    private calculateEnvironmentalScore;
    private calculateSocialScore;
    private calculateGovernanceScore;
    private mapFactorToRecommendationType;
    private calculateRecommendationDeadline;
}
export interface SupplierAssessmentData {
    supplierId: SupplierId;
    name: string;
    country: string;
    industry?: string;
    companySize?: string;
    certifications: string[];
    cyberIncidents?: Array<{
        date: string;
        description: string;
        severity: string;
    }>;
    sanctionsScreening?: {
        hits: Array<{
            list: string;
            reason: string;
            date: string;
        }>;
    };
    financialData?: {
        creditRating?: string;
        debtToEquityRatio?: number;
        revenue?: number;
        profitMargin?: number;
    };
    paymentHistory?: {
        totalPayments: number;
        latePayments: number;
        averageDaysLate?: number;
    };
    qualityIncidents?: Array<{
        date: string;
        description: string;
        severity: string;
    }>;
    mediaCoverage?: {
        positive: number;
        negative: number;
        neutral: number;
    };
    esgData?: {
        controversies: Array<{
            date: string;
            type: string;
            description: string;
            severity: string;
        }>;
        scope3Emissions?: number;
        renewableEnergyPercentage?: number;
        diversityRatio?: number;
        disclosures: EsgDisclosure[];
    };
}
export interface AssessmentContext {
    assessedBy: string;
    assessmentReason: 'onboarding' | 'periodic' | 'incident' | 'manual';
    businessUnit?: string;
    criticalityLevel: 'low' | 'medium' | 'high' | 'critical';
    relatedDocuments?: string[];
}
//# sourceMappingURL=risk-assessment-engine.d.ts.map