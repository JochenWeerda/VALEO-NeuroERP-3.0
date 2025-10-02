import { SupplierId } from '../../core/entities/supplier';
import { RiskAssessmentEngine, RiskAssessment, RiskLevel } from './risk-assessment-engine';
export interface TPRMAssessmentRequest {
    supplierId: SupplierId;
    assessmentReason: 'onboarding' | 'periodic' | 'incident' | 'manual';
    businessUnit: string | undefined;
    criticalityLevel: 'low' | 'medium' | 'high' | 'critical';
    includeESG?: boolean;
    customFactors?: Record<string, any>;
}
export interface TPRMAssessmentResponse {
    assessment: RiskAssessment;
    alertsTriggered: RiskAlert[];
    complianceStatus: ComplianceStatus;
    nextAssessmentDate: Date;
}
export interface RiskAlert {
    alertId: string;
    type: 'threshold_exceeded' | 'compliance_violation' | 'escalation_required';
    severity: 'low' | 'medium' | 'high' | 'critical';
    title: string;
    description: string;
    recommendedActions: string[];
    deadline?: Date;
    assignedTo?: string;
}
export interface ComplianceStatus {
    overall: 'compliant' | 'non_compliant' | 'under_review';
    categories: {
        sanctions: boolean;
        certifications: boolean;
        dataPrivacy: boolean;
        environmental: boolean;
        labor: boolean;
    };
    lastVerified: Date;
    nextVerification: Date;
}
export interface ESGAssessmentRequest {
    supplierId: SupplierId;
    scope3Emissions?: number;
    renewableEnergyPercentage?: number;
    diversityRatio?: number;
    certifications: string[];
    controversies: Array<{
        date: string;
        type: 'environmental' | 'social' | 'governance';
        description: string;
        severity: 'low' | 'medium' | 'high';
    }>;
    disclosures: Array<{
        standard: string;
        year: number;
        verified: boolean;
    }>;
}
export declare class TPRMRiskService {
    private readonly riskEngine;
    constructor(riskEngine: RiskAssessmentEngine);
    /**
     * Perform comprehensive TPRM risk assessment
     */
    assessSupplierRisk(request: TPRMAssessmentRequest): Promise<TPRMAssessmentResponse>;
    /**
     * Get current risk score for a supplier
     */
    getSupplierRiskScore(supplierId: SupplierId): Promise<{
        currentScore: number;
        riskLevel: RiskLevel;
        lastAssessed: Date;
        validUntil: Date;
        categories: Record<string, number>;
    }>;
    /**
     * Perform ESG-specific assessment
     */
    assessSupplierESG(request: ESGAssessmentRequest): Promise<{
        esgScore: number;
        categories: {
            environmental: number;
            social: number;
            governance: number;
        };
        recommendations: string[];
        controversies: any[];
    }>;
    /**
     * Monitor supplier risk changes and trigger alerts
     */
    monitorSupplierRisk(supplierId: SupplierId): Promise<{
        riskChanged: boolean;
        previousScore?: number;
        currentScore: number;
        alerts: RiskAlert[];
    }>;
    /**
     * Get compliance status for a supplier
     */
    getComplianceStatus(supplierId: SupplierId): Promise<ComplianceStatus>;
    /**
     * Generate risk mitigation plan
     */
    generateMitigationPlan(supplierId: SupplierId): Promise<{
        planId: string;
        riskAreas: string[];
        actions: Array<{
            actionId: string;
            description: string;
            priority: 'low' | 'medium' | 'high' | 'critical';
            owner: string;
            deadline: Date;
            status: 'pending' | 'in_progress' | 'completed';
        }>;
        timeline: {
            shortTerm: Date;
            mediumTerm: Date;
            longTerm: Date;
        };
    }>;
    private gatherSupplierData;
    private checkRiskAlerts;
    private determineComplianceStatus;
    private calculateNextAssessmentDate;
    private triggerAlert;
    private generateESGRecommendations;
    private generateActionsForRiskArea;
}
export default TPRMRiskService;
//# sourceMappingURL=tprm-risk-service.d.ts.map