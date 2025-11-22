/**
 * Sales Workflow Service
 * ISO 27001 Communications Security Compliant
 * Lead-to-Cash Automation Engine
 */

import { randomUUID } from 'crypto';
import { SalesOffer, SalesOfferStatus, SalesOfferItem } from '../entities/sales-offer';
import { ISMSAuditLogger } from '../../shared/security/isms-audit-logger';
import { CryptoService } from '../../shared/security/crypto-service';

export interface SalesWorkflowServiceDependencies {
  auditLogger: ISMSAuditLogger;
  cryptoService: CryptoService;
}

export interface SalesInquiry {
  id: string;
  customerId: string;
  contactPersonId: string;
  subject: string;
  description: string;
  estimatedValue: number;
  currency: string;
  requestedDeliveryDate: Date;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  source: 'WEB' | 'EMAIL' | 'PHONE' | 'DIRECT' | 'PARTNER';
  metadata: Record<string, any>;
  createdAt: Date;
  createdBy: string;
  tenantId: string;
}

export interface SalesLead {
  id: string;
  inquiryId: string;
  customerId: string;
  contactPersonId: string;
  leadScore: number;
  qualificationStatus: 'UNQUALIFIED' | 'QUALIFIED' | 'DISQUALIFIED';
  assignedSalesRepId: string;
  nextFollowUpDate: Date;
  leadSource: string;
  estimatedCloseDate: Date;
  probability: number;
  stage: 'NEW' | 'CONTACTED' | 'QUALIFIED' | 'PROPOSAL' | 'NEGOTIATION' | 'CLOSED_WON' | 'CLOSED_LOST';
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
  tenantId: string;
}

export interface SalesOpportunity {
  id: string;
  leadId: string;
  customerId: string;
  name: string;
  description: string;
  estimatedValue: number;
  currency: string;
  probability: number;
  stage: 'PROSPECTING' | 'QUALIFICATION' | 'NEEDS_ANALYSIS' | 'VALUE_PROPOSITION' | 'PROPOSAL' | 'NEGOTIATION' | 'CLOSING';
  closeDate: Date;
  assignedSalesRepId: string;
  salesManagerId: string;
  competitorAnalysis: string;
  nextSteps: string;
  riskFactors: string[];
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
  tenantId: string;
}

export interface SalesQuote {
  id: string;
  opportunityId: string;
  customerId: string;
  quoteNumber: string;
  version: number;
  status: 'DRAFT' | 'SENT' | 'ACCEPTED' | 'REJECTED' | 'EXPIRED';
  validUntil: Date;
  totalAmount: number;
  currency: string;
  taxAmount: number;
  discountAmount: number;
  items: SalesQuoteItem[];
  terms: string;
  notes: string;
  approvalStatus: 'PENDING' | 'APPROVED' | 'REJECTED' | 'NOT_REQUIRED';
  createdBy: string;
  approvedBy?: string;
  sentAt?: Date;
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
  tenantId: string;
}

export interface SalesQuoteItem {
  id: string;
  quoteId: string;
  articleId: string;
  description: string;
  quantity: number;
  unitPrice: number;
  discountPercent: number;
  taxRate: number;
  totalAmount: number;
  deliveryDate?: Date;
  metadata: Record<string, any>;
}

export interface ApprovalRequest {
  id: string;
  requestType: 'QUOTE' | 'DISCOUNT' | 'TERMS' | 'CUSTOM';
  referenceId: string;
  requesterId: string;
  approverId: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'ESCALATED';
  reason: string;
  approvalLevel: number;
  maxApprovalLevel: number;
  businessJustification: string;
  riskAssessment: string;
  requestedAt: Date;
  respondedAt?: Date;
  comments: string;
  metadata: Record<string, any>;
  tenantId: string;
}

export class SalesWorkflowService {
  constructor(private deps: SalesWorkflowServiceDependencies) {}

  /**
   * Creates a qualified lead from an incoming sales inquiry
   * Implements automated lead scoring based on configurable criteria
   */
  async createLeadFromInquiry(inquiry: SalesInquiry, userId: string): Promise<SalesLead> {
    try {
      // A.13.2 Information Transfer - Encrypt sensitive data
      const encryptedMetadata = await this.deps.cryptoService.encrypt(JSON.stringify(inquiry.metadata));
      
      // Calculate lead score based on business rules
      const leadScore = this.calculateLeadScore(inquiry);
      
      // Determine qualification status
      const qualificationStatus = leadScore >= 70 ? 'QUALIFIED' : 
                                 leadScore >= 40 ? 'UNQUALIFIED' : 'DISQUALIFIED';
      
      // Auto-assign sales representative based on territory/workload
      const assignedSalesRepId = await this.assignSalesRepresentative(inquiry.customerId, inquiry.tenantId);
      
      const lead: SalesLead = {
        id: randomUUID(),
        inquiryId: inquiry.id,
        customerId: inquiry.customerId,
        contactPersonId: inquiry.contactPersonId,
        leadScore,
        qualificationStatus,
        assignedSalesRepId,
        nextFollowUpDate: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours
        leadSource: inquiry.source,
        estimatedCloseDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
        probability: this.calculateInitialProbability(leadScore, inquiry.source),
        stage: 'NEW',
        metadata: { encrypted: encryptedMetadata },
        createdAt: new Date(),
        updatedAt: new Date(),
        tenantId: inquiry.tenantId
      };

      // A.12.4 Logging and Monitoring - Audit trail
      await this.deps.auditLogger.logSecureEvent('LEAD_CREATED', {
        leadId: lead.id,
        inquiryId: inquiry.id,
        customerId: inquiry.customerId,
        leadScore,
        qualificationStatus,
        userId
      }, inquiry.tenantId);

      return lead;

          } catch (error) {
        await this.deps.auditLogger.logSecurityIncident('LEAD_CREATION_FAILED', {
          inquiryId: inquiry.id,
          error: (error as Error).message,
          userId
        }, inquiry.tenantId);
        throw error;
      }
  }

  /**
   * Converts a qualified lead to a sales opportunity
   * Implements opportunity qualification matrix
   */
  async convertLeadToOpportunity(leadId: string, userId: string, tenantId: string): Promise<SalesOpportunity> {
    try {
      // Validate lead eligibility for conversion
      // In real implementation, this would fetch from repository
      
      const opportunity: SalesOpportunity = {
        id: randomUUID(),
        leadId,
        customerId: '', // Would be fetched from lead
        name: `Opportunity from Lead ${leadId}`,
        description: 'Auto-generated from qualified lead',
        estimatedValue: 0, // Would be calculated from lead data
        currency: 'EUR',
        probability: 25, // Initial probability for new opportunities
        stage: 'PROSPECTING',
        closeDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000), // 60 days
        assignedSalesRepId: '', // Would be inherited from lead
        salesManagerId: '', // Would be assigned based on territory
        competitorAnalysis: '',
        nextSteps: 'Schedule discovery call with customer',
        riskFactors: [],
        metadata: {},
        createdAt: new Date(),
        updatedAt: new Date(),
        tenantId
      };

      await this.deps.auditLogger.logSecureEvent('OPPORTUNITY_CREATED', {
        opportunityId: opportunity.id,
        leadId,
        stage: opportunity.stage,
        estimatedValue: opportunity.estimatedValue,
        userId
      }, tenantId);

      return opportunity;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('OPPORTUNITY_CREATION_FAILED', {
        leadId,
        error: (error as Error).message,
        userId
      }, tenantId);
      throw error;
    }
  }

  /**
   * Generates a formal quote from an opportunity
   * Implements CPQ (Configure-Price-Quote) logic
   */
  async generateQuote(opportunityId: string, userId: string, tenantId: string): Promise<SalesQuote> {
    try {
      const quoteNumber = await this.generateQuoteNumber(tenantId);
      
      const quote: SalesQuote = {
        id: randomUUID(),
        opportunityId,
        customerId: '', // Would be fetched from opportunity
        quoteNumber,
        version: 1,
        status: 'DRAFT',
        validUntil: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
        totalAmount: 0, // Would be calculated from items
        currency: 'EUR',
        taxAmount: 0,
        discountAmount: 0,
        items: [],
        terms: 'Standard business terms apply',
        notes: '',
        approvalStatus: 'NOT_REQUIRED',
        createdBy: userId,
        metadata: {},
        createdAt: new Date(),
        updatedAt: new Date(),
        tenantId
      };

      await this.deps.auditLogger.logSecureEvent('QUOTE_GENERATED', {
        quoteId: quote.id,
        quoteNumber,
        opportunityId,
        userId
      }, tenantId);

      return quote;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('QUOTE_GENERATION_FAILED', {
        opportunityId,
        error: (error as Error).message,
        userId
      }, tenantId);
      throw error;
    }
  }

  /**
   * Submits quote for approval based on business rules
   * Implements multi-level approval workflows
   */
  async submitForApproval(quoteId: string, userId: string, tenantId: string): Promise<ApprovalRequest> {
    try {
      // Determine if approval is required based on business rules
      const approvalLevel = await this.determineApprovalLevel(quoteId, tenantId);
      
      if (approvalLevel === 0) {
        // Auto-approve if within limits
        await this.deps.auditLogger.logSecureEvent('QUOTE_AUTO_APPROVED', {
          quoteId,
          userId
        }, tenantId);
        throw new Error('Quote auto-approved - no approval request needed');
      }

      const approvalRequest: ApprovalRequest = {
        id: randomUUID(),
        requestType: 'QUOTE',
        referenceId: quoteId,
        requesterId: userId,
        approverId: await this.getApprover(approvalLevel, tenantId),
        status: 'PENDING',
        reason: 'Quote exceeds approval threshold',
        approvalLevel,
        maxApprovalLevel: await this.getMaxApprovalLevel(tenantId),
        businessJustification: 'Standard quote approval process',
        riskAssessment: 'Low risk - standard customer',
        requestedAt: new Date(),
        comments: '',
        metadata: {},
        tenantId
      };

      await this.deps.auditLogger.logSecureEvent('APPROVAL_REQUESTED', {
        approvalRequestId: approvalRequest.id,
        quoteId,
        approvalLevel,
        approverId: approvalRequest.approverId,
        userId
      }, tenantId);

      return approvalRequest;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('APPROVAL_SUBMISSION_FAILED', {
        quoteId,
        error: (error as Error).message,
        userId
      }, tenantId);
      throw error;
    }
  }

  /**
   * Finalizes an approved quote as a sales offer
   * Implements final validation and conversion logic
   */
  async finalizeOffer(quoteId: string, userId: string, tenantId: string): Promise<SalesOffer> {
    try {
      // Validate quote status and approvals
      // In real implementation, would fetch from repository and validate

              const offer = new SalesOffer(
          randomUUID(),
          `OFFER-${Date.now()}`,
          '', // customerId - would be fetched
          undefined, // customerInquiryId
          'Quote finalization offer', // subject
          'Finalized offer from approved quote', // description
          SalesOfferStatus.ENTWURF,
          new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // validUntil
        );

      await this.deps.auditLogger.logSecureEvent('OFFER_FINALIZED', {
        offerId: offer.id,
        offerNumber: offer.offerNumber,
        quoteId,
        userId
      }, tenantId);

      return offer;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('OFFER_FINALIZATION_FAILED', {
        quoteId,
        error: (error as Error).message,
        userId
      }, tenantId);
      throw error;
    }
  }

  // Private helper methods

  private calculateLeadScore(inquiry: SalesInquiry): number {
    let score = 0;

    // Value-based scoring
    if (inquiry.estimatedValue > 100000) score += 30;
    else if (inquiry.estimatedValue > 50000) score += 20;
    else if (inquiry.estimatedValue > 10000) score += 10;

    // Source-based scoring
    switch (inquiry.source) {
      case 'DIRECT': score += 25; break;
      case 'PARTNER': score += 20; break;
      case 'WEB': score += 15; break;
      case 'EMAIL': score += 10; break;
      case 'PHONE': score += 10; break;
    }

    // Priority-based scoring
    switch (inquiry.priority) {
      case 'URGENT': score += 20; break;
      case 'HIGH': score += 15; break;
      case 'MEDIUM': score += 10; break;
      case 'LOW': score += 5; break;
    }

    // Time sensitivity scoring
    const daysToDelivery = Math.floor((inquiry.requestedDeliveryDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    if (daysToDelivery < 30) score += 15;
    else if (daysToDelivery < 90) score += 10;

    return Math.min(100, score);
  }

  private calculateInitialProbability(leadScore: number, source: string): number {
    let probability = Math.floor(leadScore * 0.3); // Base on lead score

    // Adjust based on source reliability
    const sourceMultiplier: Record<string, number> = {
      'DIRECT': 1.2,
      'PARTNER': 1.1,
      'WEB': 1.0,
      'EMAIL': 0.9,
      'PHONE': 0.8
    };

    probability *= sourceMultiplier[source] || 1.0;
    return Math.min(100, Math.max(1, Math.round(probability)));
  }

  private async assignSalesRepresentative(customerId: string, tenantId: string): Promise<string> {
    // Simplified implementation - would use territory management in real system
    return 'default-sales-rep';
  }

  private async generateQuoteNumber(tenantId: string): Promise<string> {
    // Would implement proper sequence generation in real system
    return `QUO-${Date.now()}-${tenantId.substring(0, 4).toUpperCase()}`;
  }

  private async determineApprovalLevel(quoteId: string, tenantId: string): Promise<number> {
    // Would implement business rules engine in real system
    return 1; // Simplified - assume level 1 approval needed
  }

  private async getApprover(level: number, tenantId: string): Promise<string> {
    // Would query organizational hierarchy in real system
    return 'sales-manager';
  }

  private async getMaxApprovalLevel(tenantId: string): Promise<number> {
    // Would be configured per tenant
    return 3;
  }
}
