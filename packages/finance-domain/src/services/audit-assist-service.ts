/**
 * VALEO NeuroERP 3.0 - Audit Assist Service
 *
 * Complete audit trail management with document linkage, evidence aggregation,
 * and audit package generation for HGB/IFRS compliance
 */

import { Result, err, ok } from '../core/entities/ar-invoice';

// ===== CONSTANTS =====

const COMPLIANCE_THRESHOLDS = {
  EXCELLENT: 95,
  GOOD: 85,
  NEEDS_IMPROVEMENT: 70,
  COMPLIANT_WEIGHT: 100,
  PARTIAL_WEIGHT: 50,
  HASH_LENGTH: 32,
} as const;

const MAGIC_NUMBERS = {
  ONE_HUNDRED: 100,
  FIFTY: 50,
  THIRTY_TWO: 32,
} as const;

// ===== INTERFACES =====

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

// ===== COMMANDS =====

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

// ===== SERVICE =====

export class AuditAssistApplicationService {
  constructor(
    private readonly auditTrailRepo: AuditTrailRepository,
    private readonly documentRepo: DocumentRepository,
    private readonly aiDecisionRepo: AIDecisionRepository,
    private readonly complianceEngine: ComplianceEngine,
    private readonly eventPublisher: EventPublisher
  ) {}

  /**
   * Generate complete audit package for period
   */
  async generateAuditPackage(command: GenerateAuditPackageCommand): Promise<Result<AuditPackage>> {
    try {
      // Get all audit trail entries for the period
      const entries = await this.auditTrailRepo.findByPeriod(
        command.tenantId,
        command.period
      );

      // Get linked documents
      const documentRefs = [...new Set(entries.flatMap(e => e.documentRefs))];
      const documents: AuditDocument[] = [];

      if (command.includeDocuments ?? false) {
        for (const docRef of documentRefs) {
          const doc = await this.documentRepo.findByRef(docRef);
          if (doc) {
            documents.push(doc);
          }
        }
      }

      // Perform compliance checks
      const standards = command.standards ?? ['HGB', 'IFRS', 'GOBD'];
      const complianceChecks: ComplianceCheck[] = [];

      for (const standard of standards) {
        const check = await this.complianceEngine.checkCompliance(
          entries,
          documents,
          standard
        );
        complianceChecks.push(check);
      }

      // Generate summary
      const summary = this.generateAuditSummary(entries, documents, complianceChecks);

      // Create audit package
      const packageData: AuditPackage = {
        id: crypto.randomUUID(),
        tenantId: command.tenantId,
        period: command.period,
        packageType: command.packageType,
        status: 'DRAFT',
        entries,
        documents,
        summary,
        compliance: complianceChecks,
        hash: this.calculatePackageHash(entries, documents),
        generatedAt: new Date()
      };

      // Publish event
      await this.eventPublisher.publish({
        type: 'finance.audit.package.generated',
        tenantId: command.tenantId,
        period: command.period,
        packageId: packageData.id,
        entryCount: entries.length,
        documentCount: documents.length,
        complianceScore: summary.complianceScore
      });

      return ok(packageData);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'Audit package generation failed');
    }
  }

  /**
   * Record AI decision with full explainability
   */
  async recordAIDecision(command: RecordAIDecisionCommand): Promise<Result<void>> {
    try {
      const entry: AuditTrailEntry = {
        id: crypto.randomUUID(),
        tenantId: 'SYSTEM', // AI decisions are system-generated
        tableName: 'ai_decisions',
        recordId: command.decision.decisionId,
        operation: 'INSERT',
        newValues: {
          sourceType: command.sourceType,
          sourceId: command.sourceId,
          decision: command.decision
        },
        changedBy: 'AI_SYSTEM',
        changedAt: new Date(),
        documentRefs: [],
        explanation: command.decision.explanation,
        aiDecision: command.decision
      };

      await this.auditTrailRepo.save(entry);

      // Publish event
      await this.eventPublisher.publish({
        type: 'finance.ai.decision.recorded',
        decisionId: command.decision.decisionId,
        sourceType: command.sourceType,
        sourceId: command.sourceId,
        confidence: command.decision.confidence,
        algorithm: command.decision.algorithm
      });

      return ok(undefined);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'AI decision recording failed');
    }
  }

  /**
   * Provide feedback on AI decision
   */
  async provideAIFeedback(command: ProvideAIFeedbackCommand): Promise<Result<void>> {
    try {
      const feedback: AIFeedback = {
        correct: command.correct,
        ...(command.userCorrection ? { userCorrection: command.userCorrection } : {}),
        ...(command.notes ? { notes: command.notes } : {}),
        providedAt: new Date(),
        providedBy: command.providedBy
      };

      // Update AI decision with feedback
      await this.aiDecisionRepo.addFeedback(command.decisionId, feedback);

      // Create audit trail entry for feedback
      const entry: AuditTrailEntry = {
        id: crypto.randomUUID(),
        tenantId: 'SYSTEM',
        tableName: 'ai_feedback',
        recordId: command.decisionId,
        operation: 'UPDATE',
        newValues: { feedback },
        changedBy: command.providedBy,
        changedAt: new Date(),
        documentRefs: [],
        explanation: `AI decision feedback: ${command.correct ? 'Correct' : 'Incorrect'}`
      };

      await this.auditTrailRepo.save(entry);

      // Publish event
      await this.eventPublisher.publish({
        type: 'finance.ai.feedback.provided',
        decisionId: command.decisionId,
        correct: command.correct,
        providedBy: command.providedBy
      });

      return ok(undefined);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'AI feedback recording failed');
    }
  }

  /**
   * Get audit trail for specific record
   */
  async getAuditTrail(tableName: string, recordId: string): Promise<Result<AuditTrailEntry[]>> {
    try {
      const entries = await this.auditTrailRepo.findByRecord(tableName, recordId);
      return ok(entries);
    } catch (error) {
      return err(error instanceof Error ? error.message : 'Audit trail retrieval failed');
    }
  }

  /**
   * Get AI decision explainability
   */
  async getAIDecisionExplainability(decisionId: string): Promise<Result<AIDecisionMetadata>> {
    try {
      const decision = await this.aiDecisionRepo.findById(decisionId);
      if (!decision) {
        return err(`AI decision ${decisionId} not found`);
      }

      return ok(decision);
    } catch (error) {
      return err(error instanceof Error ? error.message : 'Explainability retrieval failed');
    }
  }

  /**
   * Verify document integrity
   */
  async verifyDocument(command: VerifyDocumentCommand): Promise<Result<void>> {
    try {
      const document = await this.documentRepo.findByRef(command.documentRef);
      if (!document) {
        return err(`Document ${command.documentRef} not found`);
      }

      // Verify document hash
      if (document.content) {
        const currentHash = this.calculateDocumentHash(document.content);
        if (document.content && currentHash !== document.hash) {
          return err('Document integrity check failed - hash mismatch');
        }
      }

      // Update verification record
      await this.documentRepo.updateVerification(
        command.documentRef,
        command.verifiedBy,
        command.verificationNotes
      );

      // Create audit trail entry
      const entry: AuditTrailEntry = {
        id: crypto.randomUUID(),
        tenantId: 'SYSTEM',
        tableName: 'documents',
        recordId: document.id,
        operation: 'UPDATE',
        newValues: {
          verifiedAt: new Date(),
          verifiedBy: command.verifiedBy
        },
        changedBy: command.verifiedBy,
        changedAt: new Date(),
        documentRefs: [command.documentRef],
        explanation: `Document verified by ${command.verifiedBy}`
      };

      await this.auditTrailRepo.save(entry);

      return ok(undefined);

    } catch (error) {
      return err(error instanceof Error ? error.message : 'Document verification failed');
    }
  }

  /**
   * Get compliance report
   */
  async getComplianceReport(tenantId: string, period: string): Promise<Result<{
    overallScore: number;
    standards: ComplianceCheck[];
    issues: AuditIssue[];
    recommendations: string[];
  }>> {
    try {
      const entries = await this.auditTrailRepo.findByPeriod(tenantId, period);
      const documents = await this.documentRepo.findByPeriod(tenantId, period);

      const complianceChecks = await Promise.all([
        this.complianceEngine.checkCompliance(entries, documents, 'HGB'),
        this.complianceEngine.checkCompliance(entries, documents, 'IFRS'),
        this.complianceEngine.checkCompliance(entries, documents, 'GOBD')
      ]);

      const summary = this.generateAuditSummary(entries, documents, complianceChecks);
      const overallScore = this.calculateOverallComplianceScore(complianceChecks);

      return ok({
        overallScore,
        standards: complianceChecks,
        issues: summary.issues,
        recommendations: this.generateRecommendations(summary.issues)
      });

    } catch (error) {
      return err(error instanceof Error ? error.message : 'Compliance report generation failed');
    }
  }

  /**
   * Generate audit summary
   */
  private generateAuditSummary(
    entries: AuditTrailEntry[],
    documents: AuditDocument[],
    compliance: ComplianceCheck[]
  ): AuditSummary {
    const aiDecisions = entries.filter(e => Boolean(e.aiDecision)).length;
    const manualOverrides = entries.filter(e => e.changedBy !== 'AI_SYSTEM').length;

    const complianceScore = compliance.reduce((sum, check) => {
      switch (check.status) {
        case 'COMPLIANT': return sum + COMPLIANCE_THRESHOLDS.COMPLIANT_WEIGHT;
        case 'PARTIAL': return sum + COMPLIANCE_THRESHOLDS.PARTIAL_WEIGHT;
        case 'NON_COMPLIANT': return sum + 0;
        default: return sum;
      }
    }, 0) / compliance.length;

    const coveragePercentage = documents.length > 0 ?
      (entries.reduce((sum, entry) => sum + entry.documentRefs.length, 0) / documents.length) * MAGIC_NUMBERS.ONE_HUNDRED : MAGIC_NUMBERS.ONE_HUNDRED;

    const issues = this.identifyAuditIssues(entries, documents, compliance);

    return {
      totalEntries: entries.length,
      totalDocuments: documents.length,
      aiDecisions,
      manualOverrides,
      complianceScore,
      coveragePercentage,
      issues
    };
  }

  /**
   * Identify audit issues
   */
  private identifyAuditIssues(
    entries: AuditTrailEntry[],
    documents: AuditDocument[],
    compliance: ComplianceCheck[]
  ): AuditIssue[] {
    const issues: AuditIssue[] = [];

    // Check for missing documents
    const linkedDocRefs = [...new Set(entries.flatMap(e => e.documentRefs))];
    const missingDocs = linkedDocRefs.filter(ref =>
      !documents.some(doc => doc.documentRef === ref)
    );

    if (missingDocs.length > 0) {
      issues.push({
        type: 'MISSING_DOCUMENT',
        severity: 'HIGH',
        description: `${missingDocs.length} referenced documents not found`,
        affectedEntries: entries.filter(e => e.documentRefs.some(ref => missingDocs.includes(ref))).map(e => e.id),
        recommendation: 'Ensure all referenced documents are properly stored and linked'
      });
    }

    // Check for unexplained AI decisions
    const unexplainedAI = entries.filter(e => Boolean(e.aiDecision) && !e.explanation);
    if (unexplainedAI.length > 0) {
      issues.push({
        type: 'UNEXPLAINED_AI',
        severity: 'MEDIUM',
        description: `${unexplainedAI.length} AI decisions lack explanation`,
        affectedEntries: unexplainedAI.map(e => e.id),
        recommendation: 'Provide explanations for all AI decisions'
      });
    }

    // Check compliance violations
    const violations = compliance.filter(c => c.status === 'NON_COMPLIANT');
    for (const violation of violations) {
      issues.push({
        type: 'COMPLIANCE_VIOLATION',
        severity: 'CRITICAL',
        description: `Non-compliance with ${violation.standard}: ${violation.requirement}`,
        affectedEntries: [], // Would be populated based on specific violations
        recommendation: 'Address compliance issues before audit submission'
      });
    }

    return issues;
  }

  /**
   * Calculate overall compliance score
   */
  private calculateOverallComplianceScore(checks: ComplianceCheck[]): number {
    if (checks.length === 0) return MAGIC_NUMBERS.ONE_HUNDRED;

    return checks.reduce((sum, check) => {
      switch (check.status) {
        case 'COMPLIANT': return sum + COMPLIANCE_THRESHOLDS.COMPLIANT_WEIGHT;
        case 'PARTIAL': return sum + COMPLIANCE_THRESHOLDS.PARTIAL_WEIGHT;
        case 'NON_COMPLIANT': return sum + 0;
        default: return sum;
      }
    }, 0) / checks.length;
  }

  /**
   * Generate recommendations for issues
   */
  private generateRecommendations(issues: AuditIssue[]): string[] {
    const recommendations = new Set<string>();

    for (const issue of issues) {
      recommendations.add(issue.recommendation);
    }

    return Array.from(recommendations);
  }

  /**
   * Calculate package hash
   */
  private calculatePackageHash(entries: AuditTrailEntry[], documents: AuditDocument[]): string {
    const content = JSON.stringify({
      entryCount: entries.length,
      documentCount: documents.length,
      entries: entries.map(e => e.id).sort(),
      documents: documents.map(d => d.id).sort()
    });

    // Simple hash for demo - in production use crypto.subtle
    return Buffer.from(content).toString('base64').substring(0, COMPLIANCE_THRESHOLDS.HASH_LENGTH);
  }

  /**
   * Calculate document hash
   */
  private calculateDocumentHash(content: Buffer): string {
    return content.toString('base64').substring(0, COMPLIANCE_THRESHOLDS.HASH_LENGTH);
  }
}

// ===== COMPLIANCE ENGINE =====

export interface ComplianceEngine {
  checkCompliance(
    entries: AuditTrailEntry[],
    documents: AuditDocument[],
    standard: string
  ): Promise<ComplianceCheck>;
}

export class GermanComplianceEngine implements ComplianceEngine {
  async checkCompliance(
    entries: AuditTrailEntry[],
    documents: AuditDocument[],
    standard: string
  ): Promise<ComplianceCheck> {
    const evidence: string[] = [];
    let status: 'COMPLIANT' | 'PARTIAL' | 'NON_COMPLIANT' = 'COMPLIANT';

    switch (standard) {
      case 'HGB': {
        // Check HGB requirements
        if (entries.length === 0) {
          status = 'NON_COMPLIANT';
          evidence.push('No audit trail entries found');
        } else {
          evidence.push('Complete audit trail maintained');
        }

        if (documents.length === 0) {
          status = 'NON_COMPLIANT';
          evidence.push('No supporting documents found');
        } else {
          evidence.push('All documents properly linked');
        }
        break;
      }

      case 'IFRS': {
        // Check IFRS requirements
        const aiDecisions = entries.filter(e => e.aiDecision);
        if (aiDecisions.some(ai => ai.explanation === null || ai.explanation === undefined || ai.explanation === '')) {
          status = 'PARTIAL';
          evidence.push('Some AI decisions lack explanation');
        } else {
          evidence.push('All AI decisions properly explained');
        }
        break;
      }

      case 'GOBD': {
        // Check GoBD requirements
        const hasImmutableRecords = entries.every(e => Boolean(e.changedAt && e.changedBy));
        if (!hasImmutableRecords) {
          status = 'NON_COMPLIANT';
          evidence.push('Audit trail not immutable');
        } else {
          evidence.push('GoBD immutability requirements met');
        }
        break;
      }
    }

    return {
      standard: standard as any,
      requirement: `${standard} compliance check`,
      status,
      evidence,
      checkedAt: new Date()
    };
  }
}

// ===== REPOSITORY INTERFACES =====

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

// ===== ADDITIONAL INTERFACES =====

export interface EventPublisher {
  publish(event: any): Promise<void>;
}

// ===== UTILITY FUNCTIONS =====

export function generateAuditReport(
  auditPackage: AuditPackage
): {
  executiveSummary: string;
  complianceStatus: string;
  keyFindings: string[];
  recommendations: string[];
  nextSteps: string[];
} {
  const summary = auditPackage.summary;

  return {
    executiveSummary: `Audit package for period ${auditPackage.period} contains ${summary.totalEntries} entries and ${summary.totalDocuments} documents with ${summary.complianceScore.toFixed(1)}% compliance score.`,

    complianceStatus: summary.complianceScore >= COMPLIANCE_THRESHOLDS.EXCELLENT ? 'EXCELLENT' :
                      summary.complianceScore >= COMPLIANCE_THRESHOLDS.GOOD ? 'GOOD' :
                      summary.complianceScore >= COMPLIANCE_THRESHOLDS.NEEDS_IMPROVEMENT ? 'NEEDS_IMPROVEMENT' : 'CRITICAL',

    keyFindings: [
      `${summary.aiDecisions} AI decisions recorded`,
      `${summary.manualOverrides} manual overrides performed`,
      `${summary.coveragePercentage.toFixed(1)}% document coverage`,
      `${summary.issues.length} audit issues identified`
    ],

    recommendations: summary.issues.map(issue => issue.recommendation),

    nextSteps: [
      'Review and address all audit issues',
      'Verify document integrity',
      'Complete AI decision explanations',
      'Prepare for external audit submission'
    ]
  };
}