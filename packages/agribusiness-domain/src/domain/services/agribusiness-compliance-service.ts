/**
 * Agribusiness Compliance Service
 * Compliance & Audit Management for Agribusiness Operations
 * Based on Odoo compliance patterns
 */

import { Farmer } from '../entities/farmer';
import { FieldServiceTask } from '../entities/field-service-task';

export interface ComplianceAudit {
  id: string;
  auditNumber: string;
  auditType: ComplianceAuditType;
  status: ComplianceAuditStatus;
  entityType: 'FARMER' | 'BATCH' | 'CONTRACT' | 'WAREHOUSE' | 'TASK';
  entityId: string;
  entityName: string;
  auditorId: string;
  auditorName: string;
  scheduledDate: Date;
  actualDate?: Date;
  findings: ComplianceFinding[];
  recommendations: string[];
  complianceScore?: number; // 0-100
  isCompliant: boolean;
  nextAuditDate?: Date;
  documents: string[]; // URLs to audit documents
  createdAt: Date;
  updatedAt: Date;
}

export type ComplianceAuditType =
  | 'QUALITY_ASSURANCE'
  | 'CERTIFICATION_VERIFICATION'
  | 'TRACEABILITY_AUDIT'
  | 'ENVIRONMENTAL_COMPLIANCE'
  | 'FOOD_SAFETY'
  | 'SOCIAL_COMPLIANCE'
  | 'REGULATORY_COMPLIANCE'
  | 'SUPPLIER_AUDIT';

export type ComplianceAuditStatus =
  | 'SCHEDULED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'REQUIRES_FOLLOW_UP';

export interface ComplianceFinding {
  id: string;
  category: ComplianceFindingCategory;
  severity: 'CRITICAL' | 'MAJOR' | 'MINOR' | 'OBSERVATION';
  description: string;
  evidence?: string[]; // URLs to evidence documents
  correctiveAction?: string;
  correctiveActionDueDate?: Date;
  correctiveActionCompleted?: boolean;
  createdAt: Date;
}

export type ComplianceFindingCategory =
  | 'DOCUMENTATION'
  | 'PROCESS'
  | 'QUALITY'
  | 'SAFETY'
  | 'ENVIRONMENT'
  | 'TRACEABILITY'
  | 'CERTIFICATION'
  | 'REGULATORY';

export interface ComplianceRequirement {
  id: string;
  requirementCode: string;
  title: string;
  description: string;
  category: ComplianceRequirementCategory;
  applicableTo: ('FARMER' | 'BATCH' | 'CONTRACT' | 'WAREHOUSE')[];
  isMandatory: boolean;
  certificationType?: string;
  regulation?: string;
  effectiveDate: Date;
  expiryDate?: Date;
  isActive: boolean;
}

export type ComplianceRequirementCategory =
  | 'CERTIFICATION'
  | 'TRACEABILITY'
  | 'QUALITY'
  | 'SAFETY'
  | 'ENVIRONMENTAL'
  | 'REGULATORY'
  | 'SOCIAL';

export interface ComplianceReport {
  id: string;
  reportNumber: string;
  reportType: ComplianceReportType;
  period: string; // e.g., "2024-Q1"
  generatedAt: Date;
  generatedBy: string;
  summary: {
    totalAudits: number;
    completedAudits: number;
    complianceRate: number; // percentage
    criticalFindings: number;
    majorFindings: number;
    minorFindings: number;
    averageComplianceScore?: number;
  };
  details: {
    audits: ComplianceAudit[];
    findings: ComplianceFinding[];
    requirements: ComplianceRequirement[];
  };
  recommendations: string[];
  documents: string[]; // URLs to report documents
}

export type ComplianceReportType =
  | 'QUARTERLY'
  | 'ANNUAL'
  | 'AD_HOC'
  | 'REGULATORY_SUBMISSION';

export interface AgribusinessComplianceServiceDependencies {
  // Would integrate with audit domain, document domain, etc.
}

export class AgribusinessComplianceService {
  private audits: Map<string, ComplianceAudit> = new Map();
  private requirements: Map<string, ComplianceRequirement> = new Map();
  private reports: Map<string, ComplianceReport> = new Map();

  constructor(private deps: AgribusinessComplianceServiceDependencies) {}

  /**
   * Create a compliance audit
   */
  async createAudit(input: {
    auditType: ComplianceAuditType;
    entityType: 'FARMER' | 'BATCH' | 'CONTRACT' | 'WAREHOUSE' | 'TASK';
    entityId: string;
    entityName: string;
    auditorId: string;
    auditorName: string;
    scheduledDate: Date;
  }): Promise<ComplianceAudit> {
    const auditNumber = `AUDIT-${Date.now().toString().slice(-8)}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;

    const audit: ComplianceAudit = {
      id: `audit-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      auditNumber,
      auditType: input.auditType,
      status: 'SCHEDULED',
      entityType: input.entityType,
      entityId: input.entityId,
      entityName: input.entityName,
      auditorId: input.auditorId,
      auditorName: input.auditorName,
      scheduledDate: input.scheduledDate,
      findings: [],
      recommendations: [],
      isCompliant: true,
      documents: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.audits.set(audit.id, audit);
    return audit;
  }

  /**
   * Start an audit
   */
  async startAudit(auditId: string): Promise<ComplianceAudit> {
    const audit = this.audits.get(auditId);
    if (!audit) {
      throw new Error(`Audit with id ${auditId} not found`);
    }

    if (audit.status !== 'SCHEDULED') {
      throw new Error(`Cannot start audit in status ${audit.status}`);
    }

    const updated: ComplianceAudit = {
      ...audit,
      status: 'IN_PROGRESS',
      actualDate: new Date(),
      updatedAt: new Date(),
    };

    this.audits.set(auditId, updated);
    return updated;
  }

  /**
   * Add finding to audit
   */
  async addFinding(
    auditId: string,
    finding: Omit<ComplianceFinding, 'id' | 'createdAt'>
  ): Promise<ComplianceAudit> {
    const audit = this.audits.get(auditId);
    if (!audit) {
      throw new Error(`Audit with id ${auditId} not found`);
    }

    const newFinding: ComplianceFinding = {
      id: `finding-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      ...finding,
      createdAt: new Date(),
    };

    const updated: ComplianceAudit = {
      ...audit,
      findings: [...audit.findings, newFinding],
      updatedAt: new Date(),
    };

    // Update compliance status based on findings
    if (newFinding.severity === 'CRITICAL') {
      updated.isCompliant = false;
    }

    this.audits.set(auditId, updated);
    return updated;
  }

  /**
   * Complete an audit
   */
  async completeAudit(
    auditId: string,
    input: {
      complianceScore?: number;
      recommendations?: string[];
      nextAuditDate?: Date;
      documents?: string[];
    }
  ): Promise<ComplianceAudit> {
    const audit = this.audits.get(auditId);
    if (!audit) {
      throw new Error(`Audit with id ${auditId} not found`);
    }

    if (audit.status !== 'IN_PROGRESS') {
      throw new Error(`Cannot complete audit in status ${audit.status}`);
    }

    // Calculate compliance score if not provided
    let complianceScore = input.complianceScore;
    if (complianceScore === undefined) {
      const criticalFindings = audit.findings.filter(f => f.severity === 'CRITICAL').length;
      const majorFindings = audit.findings.filter(f => f.severity === 'MAJOR').length;
      const minorFindings = audit.findings.filter(f => f.severity === 'MINOR').length;

      // Base score
      complianceScore = 100;

      // Deduct points for findings
      complianceScore -= criticalFindings * 20;
      complianceScore -= majorFindings * 10;
      complianceScore -= minorFindings * 5;

      complianceScore = Math.max(0, Math.min(100, complianceScore));
    }

    const updated: ComplianceAudit = {
      ...audit,
      status: audit.findings.some(f => f.severity === 'CRITICAL' || f.severity === 'MAJOR')
        ? 'REQUIRES_FOLLOW_UP'
        : 'COMPLETED',
      complianceScore,
      recommendations: input.recommendations || audit.recommendations,
      nextAuditDate: input.nextAuditDate,
      documents: input.documents || audit.documents,
      updatedAt: new Date(),
    };

    // Update compliance status
    updated.isCompliant = complianceScore >= 70 && !audit.findings.some(f => f.severity === 'CRITICAL');

    this.audits.set(auditId, updated);
    return updated;
  }

  /**
   * Get audit by ID
   */
  async getAudit(auditId: string): Promise<ComplianceAudit> {
    const audit = this.audits.get(auditId);
    if (!audit) {
      throw new Error(`Audit with id ${auditId} not found`);
    }
    return audit;
  }

  /**
   * List audits
   */
  async listAudits(filters?: {
    entityType?: string;
    entityId?: string;
    auditType?: ComplianceAuditType;
    status?: ComplianceAuditStatus;
    auditorId?: string;
  }): Promise<ComplianceAudit[]> {
    let audits = Array.from(this.audits.values());

    if (filters) {
      if (filters.entityType) {
        audits = audits.filter(a => a.entityType === filters.entityType);
      }
      if (filters.entityId) {
        audits = audits.filter(a => a.entityId === filters.entityId);
      }
      if (filters.auditType) {
        audits = audits.filter(a => a.auditType === filters.auditType);
      }
      if (filters.status) {
        audits = audits.filter(a => a.status === filters.status);
      }
      if (filters.auditorId) {
        audits = audits.filter(a => a.auditorId === filters.auditorId);
      }
    }

    return audits.sort((a, b) => b.scheduledDate.getTime() - a.scheduledDate.getTime());
  }

  /**
   * Register compliance requirement
   */
  async registerRequirement(input: Omit<ComplianceRequirement, 'id'>): Promise<ComplianceRequirement> {
    const requirement: ComplianceRequirement = {
      id: `req-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      ...input,
    };

    this.requirements.set(requirement.id, requirement);
    return requirement;
  }

  /**
   * Get compliance requirements
   */
  async getRequirements(filters?: {
    category?: ComplianceRequirementCategory;
    applicableTo?: string;
    isActive?: boolean;
  }): Promise<ComplianceRequirement[]> {
    let requirements = Array.from(this.requirements.values());

    if (filters) {
      if (filters.category) {
        requirements = requirements.filter(r => r.category === filters.category);
      }
      if (filters.applicableTo) {
        requirements = requirements.filter(r => r.applicableTo.includes(filters.applicableTo as any));
      }
      if (filters.isActive !== undefined) {
        requirements = requirements.filter(r => r.isActive === filters.isActive);
      }
    }

    return requirements;
  }

  /**
   * Check entity compliance
   */
  async checkCompliance(
    entityType: 'FARMER' | 'BATCH' | 'CONTRACT' | 'WAREHOUSE',
    entityId: string
  ): Promise<{
    isCompliant: boolean;
    complianceScore?: number;
    requirements: ComplianceRequirement[];
    missingRequirements: ComplianceRequirement[];
    recentAudits: ComplianceAudit[];
  }> {
    const requirements = await this.getRequirements({
      applicableTo: entityType,
      isActive: true,
    });

    const audits = await this.listAudits({
      entityType,
      entityId,
    });

    const recentAudits = audits
      .filter(a => a.status === 'COMPLETED')
      .slice(0, 5);

    // Check which requirements are met (simplified - would need actual compliance checking logic)
    const missingRequirements = requirements.filter(req => {
      // Would check actual compliance status
      return false; // Simplified
    });

    const latestAudit = recentAudits[0];
    const complianceScore = latestAudit?.complianceScore;
    const isCompliant = latestAudit?.isCompliant ?? false;

    return {
      isCompliant,
      complianceScore,
      requirements,
      missingRequirements,
      recentAudits,
    };
  }

  /**
   * Generate compliance report
   */
  async generateComplianceReport(
    reportType: ComplianceReportType,
    period: string
  ): Promise<ComplianceReport> {
    const reportNumber = `COMP-${Date.now().toString().slice(-8)}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;

    const allAudits = await this.listAudits();
    const completedAudits = allAudits.filter(a => a.status === 'COMPLETED');
    const criticalFindings = allAudits.flatMap(a => a.findings.filter(f => f.severity === 'CRITICAL'));
    const majorFindings = allAudits.flatMap(a => a.findings.filter(f => f.severity === 'MAJOR'));
    const minorFindings = allAudits.flatMap(a => a.findings.filter(f => f.severity === 'MINOR'));

    const compliantAudits = completedAudits.filter(a => a.isCompliant);
    const complianceRate = completedAudits.length > 0
      ? (compliantAudits.length / completedAudits.length) * 100
      : 0;

    const averageComplianceScore = completedAudits.length > 0
      ? completedAudits.reduce((sum, a) => sum + (a.complianceScore || 0), 0) / completedAudits.length
      : undefined;

    const requirements = await this.getRequirements({ isActive: true });

    const report: ComplianceReport = {
      id: `report-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      reportNumber,
      reportType,
      period,
      generatedAt: new Date(),
      generatedBy: 'system',
      summary: {
        totalAudits: allAudits.length,
        completedAudits: completedAudits.length,
        complianceRate,
        criticalFindings: criticalFindings.length,
        majorFindings: majorFindings.length,
        minorFindings: minorFindings.length,
        averageComplianceScore,
      },
      details: {
        audits: completedAudits,
        findings: [...criticalFindings, ...majorFindings, ...minorFindings],
        requirements,
      },
      recommendations: [],
      documents: [],
    };

    this.reports.set(report.id, report);
    return report;
  }

  /**
   * Get compliance report
   */
  async getComplianceReport(reportId: string): Promise<ComplianceReport> {
    const report = this.reports.get(reportId);
    if (!report) {
      throw new Error(`Compliance report with id ${reportId} not found`);
    }
    return report;
  }
}

