/**
 * VALEO NeuroERP 3.0 - Audit Assist Service
 *
 * Complete audit trail management with document linkage, evidence aggregation,
 * and audit package generation for HGB/IFRS compliance
 */
import { Result } from '../core/entities/ar-invoice';
export interface AuditTrailEntry {
    readonly id: string;
    readonly tenantId: string;
    readonly tableName: string;
    readonly recordId: string;
    readonly operation: 'INSERT' | 'UPDATE' | 'DELETE';
    readonly oldValues?: Record<string, any>;
    readonly newValues?: Record<string, any>;
    readonly changedBy: string;
    readonly changedAt: Date;
    readonly ipAddress?: string;
    readonly userAgent?: string;
    readonly sessionId?: string;
    readonly transactionId?: string;
    readonly documentRefs: string[];
    readonly explanation?: string;
    readonly aiDecision?: AIDecisionMetadata;
}
export interface AIDecisionMetadata {
    readonly decisionId: string;
    readonly algorithm: string;
    readonly confidence: number;
    readonly features: Record<string, number>;
    readonly rules: string[];
    readonly explanation: string;
    readonly approvedBy?: string;
    readonly approvedAt?: Date;
    readonly feedback?: AIFeedback;
}
export interface AIFeedback {
    readonly correct: boolean;
    readonly userCorrection?: Record<string, any>;
    readonly notes?: string;
    readonly providedAt: Date;
    readonly providedBy: string;
}
export interface AuditPackage {
    readonly id: string;
    readonly tenantId: string;
    readonly period: string;
    readonly packageType: 'MONTHLY' | 'QUARTERLY' | 'ANNUAL' | 'SPECIAL';
    readonly status: 'DRAFT' | 'FINAL' | 'EXPORTED';
    readonly entries: AuditTrailEntry[];
    readonly documents: AuditDocument[];
    readonly summary: AuditSummary;
    readonly compliance: ComplianceCheck[];
    readonly hash: string;
    readonly generatedAt: Date;
    readonly exportedAt?: Date;
}
export interface AuditDocument {
    readonly id: string;
    readonly documentRef: string;
    readonly documentType: string;
    readonly fileName: string;
    readonly mimeType: string;
    readonly hash: string;
    readonly content?: Buffer;
    readonly linkedEntries: string[];
    readonly verifiedAt?: Date;
    readonly verifiedBy?: string;
}
export interface AuditSummary {
    readonly totalEntries: number;
    readonly totalDocuments: number;
    readonly aiDecisions: number;
    readonly manualOverrides: number;
    readonly complianceScore: number;
    readonly coveragePercentage: number;
    readonly issues: AuditIssue[];
}
export interface AuditIssue {
    readonly type: 'MISSING_DOCUMENT' | 'UNEXPLAINED_AI' | 'COMPLIANCE_VIOLATION' | 'DATA_INCONSISTENCY';
    readonly severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    readonly description: string;
    readonly affectedEntries: string[];
    readonly recommendation: string;
}
export interface ComplianceCheck {
    readonly standard: 'HGB' | 'IFRS' | 'GOBD' | 'GDPdU';
    readonly requirement: string;
    readonly status: 'COMPLIANT' | 'NON_COMPLIANT' | 'PARTIAL';
    readonly evidence: string[];
    readonly checkedAt: Date;
}
export interface GenerateAuditPackageCommand {
    readonly tenantId: string;
    readonly period: string;
    readonly packageType: 'MONTHLY' | 'QUARTERLY' | 'ANNUAL' | 'SPECIAL';
    readonly includeDocuments?: boolean;
    readonly standards?: string[];
}
export interface VerifyDocumentCommand {
    readonly documentRef: string;
    readonly verifiedBy: string;
    readonly verificationNotes?: string;
}
export interface RecordAIDecisionCommand {
    readonly sourceType: string;
    readonly sourceId: string;
    readonly decision: AIDecisionMetadata;
}
export interface ProvideAIFeedbackCommand {
    readonly decisionId: string;
    readonly correct: boolean;
    readonly userCorrection?: Record<string, any>;
    readonly notes?: string;
    readonly providedBy: string;
}
export declare class AuditAssistApplicationService {
    private readonly auditTrailRepo;
    private readonly documentRepo;
    private readonly aiDecisionRepo;
    private readonly complianceEngine;
    private readonly eventPublisher;
    constructor(auditTrailRepo: AuditTrailRepository, documentRepo: DocumentRepository, aiDecisionRepo: AIDecisionRepository, complianceEngine: ComplianceEngine, eventPublisher: EventPublisher);
    /**
     * Generate complete audit package for period
     */
    generateAuditPackage(command: GenerateAuditPackageCommand): Promise<Result<AuditPackage>>;
    /**
     * Record AI decision with full explainability
     */
    recordAIDecision(command: RecordAIDecisionCommand): Promise<Result<void>>;
    /**
     * Provide feedback on AI decision
     */
    provideAIFeedback(command: ProvideAIFeedbackCommand): Promise<Result<void>>;
    /**
     * Get audit trail for specific record
     */
    getAuditTrail(tableName: string, recordId: string): Promise<Result<AuditTrailEntry[]>>;
    /**
     * Get AI decision explainability
     */
    getAIDecisionExplainability(decisionId: string): Promise<Result<AIDecisionMetadata>>;
    /**
     * Verify document integrity
     */
    verifyDocument(command: VerifyDocumentCommand): Promise<Result<void>>;
    /**
     * Get compliance report
     */
    getComplianceReport(tenantId: string, period: string): Promise<Result<{
        overallScore: number;
        standards: ComplianceCheck[];
        issues: AuditIssue[];
        recommendations: string[];
    }>>;
    /**
     * Generate audit summary
     */
    private generateAuditSummary;
    /**
     * Identify audit issues
     */
    private identifyAuditIssues;
    /**
     * Calculate overall compliance score
     */
    private calculateOverallComplianceScore;
    /**
     * Generate recommendations for issues
     */
    private generateRecommendations;
    /**
     * Calculate package hash
     */
    private calculatePackageHash;
    /**
     * Calculate document hash
     */
    private calculateDocumentHash;
}
export interface ComplianceEngine {
    checkCompliance(entries: AuditTrailEntry[], documents: AuditDocument[], standard: string): Promise<ComplianceCheck>;
}
export declare class GermanComplianceEngine implements ComplianceEngine {
    checkCompliance(entries: AuditTrailEntry[], documents: AuditDocument[], standard: string): Promise<ComplianceCheck>;
}
export interface AuditTrailRepository {
    save(entry: AuditTrailEntry): Promise<void>;
    findById(id: string): Promise<AuditTrailEntry | null>;
    findByRecord(tableName: string, recordId: string): Promise<AuditTrailEntry[]>;
    findByPeriod(tenantId: string, period: string): Promise<AuditTrailEntry[]>;
    findByTenant(tenantId: string): Promise<AuditTrailEntry[]>;
}
export interface DocumentRepository {
    save(document: AuditDocument): Promise<void>;
    findById(id: string): Promise<AuditDocument | null>;
    findByRef(ref: string): Promise<AuditDocument | null>;
    findByPeriod(tenantId: string, period: string): Promise<AuditDocument[]>;
    updateVerification(documentRef: string, verifiedBy: string, notes?: string): Promise<void>;
}
export interface AIDecisionRepository {
    save(decision: AIDecisionMetadata): Promise<void>;
    findById(id: string): Promise<AIDecisionMetadata | null>;
    findBySource(sourceType: string, sourceId: string): Promise<AIDecisionMetadata[]>;
    addFeedback(decisionId: string, feedback: AIFeedback): Promise<void>;
}
export interface EventPublisher {
    publish(event: any): Promise<void>;
}
export declare function generateAuditReport(auditPackage: AuditPackage): {
    executiveSummary: string;
    complianceStatus: string;
    keyFindings: string[];
    recommendations: string[];
    nextSteps: string[];
};
//# sourceMappingURL=audit-assist-service.d.ts.map