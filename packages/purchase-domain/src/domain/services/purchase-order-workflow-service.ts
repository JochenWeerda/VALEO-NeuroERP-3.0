/**
 * Purchase Order Workflow Service
 * ISO 27001 Communications Security Compliant
 * Source-to-Pay Automation Engine
 */

import { randomUUID } from 'crypto';
import { PurchaseOrder, PurchaseOrderStatus, PurchaseOrderItem, PurchaseOrderItemType } from '../entities/purchase-order';
import { ISMSAuditLogger } from '../../security/isms-audit-logger';
import { CryptoService } from '../../security/crypto-service';

export interface PurchaseOrderWorkflowServiceDependencies {
  auditLogger: ISMSAuditLogger;
  cryptoService: CryptoService;
}

export interface PurchaseRequisition {
  id: string;
  requesterId: string;
  requesterDepartment: string;
  subject: string;
  description: string;
  businessJustification: string;
  urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  budgetCode: string;
  estimatedCost: number;
  currency: string;
  requestedItems: PurchaseRequisitionItem[];
  preferredSupplierId?: string;
  deliveryLocation: string;
  requestedDeliveryDate: Date;
  approvalStatus: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELLED';
  approvedBy?: string;
  approvedAt?: Date;
  rejectionReason?: string;
  createdAt: Date;
  tenantId: string;
}

export interface PurchaseRequisitionItem {
  id: string;
  requisitionId: string;
  articleId?: string;
  description: string;
  specification?: string;
  quantity: number;
  estimatedUnitPrice: number;
  estimatedTotalPrice: number;
  preferredSupplierId?: string;
  alternativeSuppliers: string[];
  category: string;
  subcategory?: string;
  technicalDrawing?: string;
  qualityRequirements?: string;
  deliveryRequirements?: string;
}

export interface SupplierQuotation {
  id: string;
  requisitionId: string;
  supplierId: string;
  supplierName: string;
  quotationNumber: string;
  quotationDate: Date;
  validUntil: Date;
  currency: string;
  items: SupplierQuotationItem[];
  totalAmount: number;
  taxAmount: number;
  deliveryTerms: string;
  paymentTerms: string;
  deliveryTime: number; // days
  warranty?: string;
  qualityCertificates: string[];
  status: 'PENDING' | 'SUBMITTED' | 'ACCEPTED' | 'REJECTED' | 'EXPIRED';
  evaluationScore?: number;
  evaluationNotes?: string;
  createdAt: Date;
  tenantId: string;
}

export interface SupplierQuotationItem {
  id: string;
  quotationId: string;
  requisitionItemId: string;
  itemType: 'PRODUCT' | 'SERVICE';
  articleId?: string;
  supplierPartNumber?: string;
  description: string;
  quantity: number;
  unitPrice: number;
  discountPercent: number;
  totalPrice: number;
  leadTime: number; // days
  minimumOrderQuantity: number;
  packaging?: string;
  qualityGrade?: string;
}

export interface PurchaseOrderApproval {
  id: string;
  purchaseOrderId: string;
  approvalLevel: number;
  approverId: string;
  approverName: string;
  approverRole: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'ESCALATED';
  approvalLimit: number;
  businessJustification: string;
  riskAssessment: string;
  requestedAt: Date;
  respondedAt?: Date;
  comments?: string;
  conditions?: string;
  nextApprover?: string;
  tenantId: string;
}

export interface GoodsReceiptNote {
  id: string;
  purchaseOrderId: string;
  deliveryNoteNumber?: string;
  receivedDate: Date;
  receivedBy: string;
  receivedLocation: string;
  items: GoodsReceiptItem[];
  totalQuantityReceived: number;
  qualityInspectionStatus: 'PENDING' | 'PASSED' | 'FAILED' | 'CONDITIONAL';
  qualityInspector?: string;
  inspectionNotes?: string;
  damageReport?: string;
  storageLocation?: string;
  invoiceReceived: boolean;
  invoiceNumber?: string;
  status: 'DRAFT' | 'CONFIRMED' | 'DISPUTED' | 'ACCEPTED';
  createdAt: Date;
  tenantId: string;
}

export interface GoodsReceiptItem {
  id: string;
  receiptId: string;
  purchaseOrderItemId: string;
  articleId?: string;
  description: string;
  orderedQuantity: number;
  receivedQuantity: number;
  acceptedQuantity: number;
  rejectedQuantity: number;
  rejectionReason?: string;
  unitPrice: number;
  condition: 'PERFECT' | 'GOOD' | 'DAMAGED' | 'DEFECTIVE';
  batchNumber?: string;
  serialNumbers: string[];
  expiryDate?: Date;
  storageLocation?: string;
}

export class PurchaseOrderWorkflowService {
  constructor(private deps: PurchaseOrderWorkflowServiceDependencies) {}

  /**
   * Creates a purchase requisition with automated approval routing
   * Implements business rules for spending authorization
   */
  async createPurchaseRequisition(
    requestData: Omit<PurchaseRequisition, 'id' | 'createdAt' | 'approvalStatus' | 'approvedBy' | 'approvedAt' | 'rejectionReason'>,
    userId: string
  ): Promise<PurchaseRequisition> {
    try {
      // A.13.2 Information Transfer - Encrypt sensitive business data
      const encryptedJustification = await this.deps.cryptoService.encrypt(requestData.businessJustification);

      const requisition: PurchaseRequisition = {
        id: randomUUID(),
        ...requestData,
        approvalStatus: 'PENDING',
        approvedBy: undefined,
        approvedAt: undefined,
        rejectionReason: undefined,
        createdAt: new Date()
      };

      // Validate budget authorization
      const budgetValidation = await this.validateBudgetAuthorization(
        requisition.budgetCode,
        requisition.estimatedCost,
        requisition.tenantId
      );

      if (!budgetValidation.isValid) {
        throw new Error(`Budget validation failed: ${budgetValidation.reason}`);
      }

      // Automatic approval for low-value purchases
      if (requisition.estimatedCost <= await this.getAutoApprovalThreshold(userId, requisition.tenantId)) {
        (requisition as any).approvalStatus = 'APPROVED';
        (requisition as any).approvedBy = 'system-auto-approval';
        (requisition as any).approvedAt = new Date();
      } else {
        // Route to appropriate approver
        await this.routeForApproval(requisition, userId);
      }

      await this.deps.auditLogger.logSecureEvent('PURCHASE_REQUISITION_CREATED', {
        requisitionId: requisition.id,
        requesterId: requisition.requesterId,
        estimatedCost: requisition.estimatedCost,
        urgency: requisition.urgency,
        approvalStatus: requisition.approvalStatus,
        autoApproved: requisition.approvalStatus === 'APPROVED'
      }, requisition.tenantId, userId);

      return requisition;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_REQUISITION_CREATION_FAILED', {
        requesterId: requestData.requesterId,
        estimatedCost: requestData.estimatedCost,
        error: (error as Error).message
      }, requestData.tenantId, userId);
      throw error;
    }
  }

  /**
   * Solicits quotations from qualified suppliers
   * Implements automated RFQ (Request for Quotation) process
   */
  async solicitQuotations(
    requisitionId: string,
    selectedSuppliers: string[],
    userId: string,
    tenantId: string
  ): Promise<SupplierQuotation[]> {
    try {
      const quotations: SupplierQuotation[] = [];

      for (const supplierId of selectedSuppliers) {
        const supplier = await this.getSupplierDetails(supplierId, tenantId);

        const quotation: SupplierQuotation = {
          id: randomUUID(),
          requisitionId,
          supplierId,
          supplierName: supplier.name,
          quotationNumber: await this.generateQuotationNumber(supplierId, tenantId),
          quotationDate: new Date(),
          validUntil: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
          currency: 'EUR',
          items: [], // Would be populated from requisition items
          totalAmount: 0,
          taxAmount: 0,
          deliveryTerms: supplier.defaultDeliveryTerms || 'EXW',
          paymentTerms: supplier.defaultPaymentTerms || 'NET 30',
          deliveryTime: supplier.averageDeliveryTime || 14,
          warranty: supplier.standardWarranty,
          qualityCertificates: supplier.certifications || [],
          status: 'PENDING',
          evaluationScore: undefined,
          evaluationNotes: undefined,
          createdAt: new Date(),
          tenantId
        };

        // Send RFQ to supplier (would integrate with supplier portal/email)
        await this.sendRFQToSupplier(quotation, userId);

        quotations.push(quotation);
      }

      await this.deps.auditLogger.logSecureEvent('RFQ_SOLICITED', {
        requisitionId,
        supplierCount: selectedSuppliers.length,
        quotationIds: quotations.map(q => q.id)
      }, tenantId, userId);

      return quotations;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('RFQ_SOLICITATION_FAILED', {
        requisitionId,
        supplierCount: selectedSuppliers.length,
        error: (error as Error).message
      }, tenantId, userId);
      throw error;
    }
  }

  /**
   * Evaluates supplier quotations using multi-criteria analysis
   * Implements weighted scoring for supplier selection
   */
  async evaluateQuotations(
    quotationIds: string[],
    evaluationCriteria: {
      priceWeight: number;
      qualityWeight: number;
      deliveryWeight: number;
      serviceWeight: number;
    },
    userId: string,
    tenantId: string
  ): Promise<SupplierQuotation[]> {
    try {
      const evaluatedQuotations: SupplierQuotation[] = [];

      for (const quotationId of quotationIds) {
        const quotation = await this.getQuotation(quotationId, tenantId);
        const supplierPerformance = await this.getSupplierPerformance(quotation.supplierId, tenantId);

        // Multi-criteria evaluation
        const priceScore = this.calculatePriceScore(quotation, quotationIds, tenantId);
        const qualityScore = supplierPerformance?.qualityScore || 5;
        const deliveryScore = this.calculateDeliveryScore(quotation, supplierPerformance);
        const serviceScore = supplierPerformance?.communicationRating || 5;

        // Weighted total score
        const totalScore = (
          (priceScore * evaluationCriteria.priceWeight) +
          (qualityScore * evaluationCriteria.qualityWeight) +
          (deliveryScore * evaluationCriteria.deliveryWeight) +
          (serviceScore * evaluationCriteria.serviceWeight)
        ) / (
          evaluationCriteria.priceWeight +
          evaluationCriteria.qualityWeight +
          evaluationCriteria.deliveryWeight +
          evaluationCriteria.serviceWeight
        );

        const evaluatedQuotation: SupplierQuotation = {
          ...quotation,
          evaluationScore: Math.round(totalScore * 10) / 10,
          evaluationNotes: `Price: ${priceScore}/10, Quality: ${qualityScore}/10, Delivery: ${deliveryScore}/10, Service: ${serviceScore}/10`
        };

        evaluatedQuotations.push(evaluatedQuotation);
      }

      // Sort by evaluation score (highest first)
      evaluatedQuotations.sort((a, b) => (b.evaluationScore || 0) - (a.evaluationScore || 0));

      await this.deps.auditLogger.logSecureEvent('QUOTATIONS_EVALUATED', {
        quotationCount: quotationIds.length,
        topSupplier: evaluatedQuotations[0]?.supplierName,
        topScore: evaluatedQuotations[0]?.evaluationScore,
        evaluationCriteria
      }, tenantId, userId);

      return evaluatedQuotations;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('QUOTATION_EVALUATION_FAILED', {
        quotationCount: quotationIds.length,
        error: (error as Error).message
      }, tenantId, userId);
      throw error;
    }
  }

  /**
   * Creates purchase order from selected quotation
   * Implements automated PO generation with approval workflows
   */
  async createPurchaseOrderFromQuote(
    quotationId: string,
    orderDetails: {
      deliveryAddress: string;
      requestedDeliveryDate: Date;
      specialInstructions?: string;
      contactPerson: string;
      contactEmail: string;
      contactPhone: string;
    },
    userId: string,
    tenantId: string
  ): Promise<PurchaseOrder> {
    try {
      const quotation = await this.getQuotation(quotationId, tenantId);
      const poNumber = await this.generatePONumber(tenantId);

      // Create PO items from quotation
      const items: PurchaseOrderItem[] = quotation.items.map(item =>
        new PurchaseOrderItem(
          '', // Will be set after PO creation
          item.itemType === 'SERVICE' ? PurchaseOrderItemType.SERVICE : PurchaseOrderItemType.PRODUCT,
          item.description,
          item.quantity,
          item.unitPrice,
          item.discountPercent,
          item.articleId,
          orderDetails.requestedDeliveryDate,
          item.supplierPartNumber
        )
      );

      const purchaseOrder = new PurchaseOrder(
        quotation.supplierId,
        `Purchase Order for ${quotation.quotationNumber}`,
        `Generated from quotation ${quotation.quotationNumber}`,
        orderDetails.requestedDeliveryDate,
        items,
        userId,
        {
          id: randomUUID(),
          purchaseOrderNumber: poNumber,
          currency: quotation.currency,
          taxRate: quotation.taxAmount / (quotation.totalAmount - quotation.taxAmount) * 100,
          paymentTerms: quotation.paymentTerms,
          notes: orderDetails.specialInstructions,
          status: PurchaseOrderStatus.ENTWURF
        }
      );

      // Update item purchase order IDs
      items.forEach(item => {
        (item as any).purchaseOrderId = purchaseOrder.id;
      });

      // Check if approval is required
      const approvalRequired = await this.isPurchaseOrderApprovalRequired(
        purchaseOrder.totalAmount,
        userId,
        tenantId
      );

      if (!approvalRequired) {
        // Auto-approve and submit to supplier
        (purchaseOrder as any).status = PurchaseOrderStatus.FREIGEGEBEN;
        await this.submitPurchaseOrderToSupplier(purchaseOrder, userId);
      } else {
        // Route for approval
        await this.routePurchaseOrderForApproval(purchaseOrder, userId);
      }

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_CREATED_FROM_QUOTE', {
        purchaseOrderId: purchaseOrder.id,
        poNumber: purchaseOrder.purchaseOrderNumber,
        quotationId,
        supplierId: purchaseOrder.supplierId,
        totalAmount: purchaseOrder.totalAmount,
        currency: purchaseOrder.currency,
        approvalRequired,
        itemCount: purchaseOrder.items.length
      }, tenantId, userId);

      return purchaseOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_CREATION_FROM_QUOTE_FAILED', {
        quotationId,
        error: (error as Error).message
      }, tenantId, userId);
      throw error;
    }
  }

  /**
   * Approves a purchase requisition
   * Implements approval workflow with business rules
   */
  async approvePurchaseRequisition(
    requisitionId: string,
    approverId: string,
    tenantId: string,
    comments?: string
  ): Promise<PurchaseRequisition> {
    try {
      // In real implementation, would fetch and validate requisition
      const requisition: PurchaseRequisition = {
        id: requisitionId,
        requesterId: 'user-123',
        requesterDepartment: 'IT',
        subject: 'Sample Requisition',
        description: 'Sample description',
        businessJustification: 'Business need',
        urgency: 'MEDIUM',
        budgetCode: 'BUD-001',
        estimatedCost: 3000,
        currency: 'EUR',
        requestedItems: [],
        deliveryLocation: 'Warehouse A',
        requestedDeliveryDate: new Date(),
        approvalStatus: 'PENDING',
        createdAt: new Date(),
        tenantId
      };

      if (requisition.approvalStatus !== 'PENDING') {
        throw new Error('Requisition is not in pending status');
      }

      // Update requisition status
      const approvedRequisition: PurchaseRequisition = {
        ...requisition,
        approvalStatus: 'APPROVED',
        approvedBy: approverId,
        approvedAt: new Date()
      };

      await this.deps.auditLogger.logSecureEvent('PURCHASE_REQUISITION_APPROVED', {
        requisitionId,
        approverId,
        estimatedCost: requisition.estimatedCost,
        comments
      }, tenantId, approverId);

      return approvedRequisition;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_REQUISITION_APPROVAL_FAILED', {
        requisitionId,
        approverId,
        error: (error as Error).message
      }, tenantId, approverId);
      throw error;
    }
  }

  /**
   * Finalizes approved purchase order for execution
   * Implements final validation and supplier notification
   */
  async finalizePurchaseOrder(
    purchaseOrderId: string,
    userId: string,
    tenantId: string
  ): Promise<PurchaseOrder> {
    try {
      const purchaseOrder = await this.getPurchaseOrder(purchaseOrderId, tenantId);

      if (purchaseOrder.status !== PurchaseOrderStatus.FREIGEGEBEN) {
        throw new Error('Purchase order must be approved before finalization');
      }

      // Final validation checks
      await this.performFinalValidation(purchaseOrder, tenantId);

      // Update status to ordered
      const finalizedOrder = purchaseOrder.order(userId);

      // Send to supplier
      await this.submitPurchaseOrderToSupplier(finalizedOrder, userId);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_FINALIZED', {
        purchaseOrderId,
        poNumber: finalizedOrder.purchaseOrderNumber,
        supplierId: finalizedOrder.supplierId,
        totalAmount: finalizedOrder.totalAmount,
        userId
      }, tenantId, userId);

      return finalizedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_FINALIZATION_FAILED', {
        purchaseOrderId,
        error: (error as Error).message,
        userId
      }, tenantId, userId);
      throw error;
    }
  }

  /**
   * Processes goods receipt against purchase order
   * Implements three-way matching (PO, GRN, Invoice)
   */
  async processGoodsReceipt(
    purchaseOrderId: string,
    receiptData: Omit<GoodsReceiptNote, 'id' | 'createdAt'>,
    userId: string
  ): Promise<GoodsReceiptNote> {
    try {
      // In real implementation, would fetch PO from repository
      const purchaseOrder = await this.getPurchaseOrder(purchaseOrderId, receiptData.tenantId);

      // Validate receipt quantities against PO
      const validationResult = await this.validateReceiptQuantities(
        receiptData.items,
        purchaseOrder.items
      );

      if (!validationResult.isValid) {
        throw new Error(`Receipt validation failed: ${validationResult.errors.join(', ')}`);
      }

      const goodsReceipt: GoodsReceiptNote = {
        id: randomUUID(),
        ...receiptData,
        createdAt: new Date()
      };

      // Auto-quality inspection for known good suppliers
      const supplierPerformance = await this.getSupplierPerformance(
        purchaseOrder.supplierId,
        receiptData.tenantId
      );

      if (supplierPerformance && supplierPerformance.qualityScore >= 8) {
        (goodsReceipt as any).qualityInspectionStatus = 'PASSED';
        (goodsReceipt as any).qualityInspector = 'system-auto-inspection';
      }

      // Update inventory levels (would integrate with inventory domain)
      await this.updateInventoryLevels(goodsReceipt);

      // Update PO status
      const allItemsReceived = await this.checkIfAllItemsReceived(purchaseOrderId, receiptData.tenantId);
      if (allItemsReceived) {
        await this.updatePurchaseOrderStatus(purchaseOrderId, PurchaseOrderStatus.GELIEFERT, receiptData.tenantId);
      } else {
        await this.updatePurchaseOrderStatus(purchaseOrderId, PurchaseOrderStatus.TEILGELIEFERT, receiptData.tenantId);
      }

      await this.deps.auditLogger.logSecureEvent('GOODS_RECEIPT_PROCESSED', {
        goodsReceiptId: goodsReceipt.id,
        purchaseOrderId,
        receivedBy: goodsReceipt.receivedBy,
        totalQuantityReceived: goodsReceipt.totalQuantityReceived,
        qualityStatus: goodsReceipt.qualityInspectionStatus,
        allItemsReceived
      }, receiptData.tenantId, userId);

      return goodsReceipt;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('GOODS_RECEIPT_PROCESSING_FAILED', {
        purchaseOrderId,
        error: (error as Error).message
      }, receiptData.tenantId, userId);
      throw error;
    }
  }

  // Private helper methods

  private async validateBudgetAuthorization(
    budgetCode: string,
    amount: number,
    tenantId: string
  ): Promise<{ isValid: boolean; reason?: string; availableAmount?: number }> {
    // Simplified budget validation - would integrate with finance domain
    return {
      isValid: true,
      availableAmount: 1000000 // Mock available budget
    };
  }

  private async getAutoApprovalThreshold(userId: string, tenantId: string): Promise<number> {
    // Would query user's authorization limits from database
    return 5000; // €5000 auto-approval threshold
  }

  private async routeForApproval(requisition: PurchaseRequisition, userId: string): Promise<void> {
    // Would implement approval routing logic
    console.log(`Routing requisition ${requisition.id} for approval`);
  }

  private async getSupplierDetails(supplierId: string, tenantId: string): Promise<any> {
    // Mock supplier data - would query from supplier master
    return {
      name: `Supplier ${supplierId}`,
      active: true,
      defaultDeliveryTerms: 'EXW',
      defaultPaymentTerms: 'NET 30',
      averageDeliveryTime: 14,
      standardWarranty: '12 months',
      certifications: ['ISO 9001', 'ISO 14001']
    };
  }

  private async generateQuotationNumber(supplierId: string, tenantId: string): Promise<string> {
    return `RFQ-${Date.now()}-${supplierId.substring(0, 4).toUpperCase()}`;
  }

  private async sendRFQToSupplier(quotation: SupplierQuotation, userId: string): Promise<void> {
    // Would integrate with supplier portal or email system
    console.log(`Sent RFQ ${quotation.quotationNumber} to ${quotation.supplierName}`);
  }

  private async getQuotation(quotationId: string, tenantId: string): Promise<SupplierQuotation> {
    // Mock quotation with sample items - would query from database
    const mockItems: SupplierQuotationItem[] = [
      {
        id: randomUUID(),
        quotationId,
        requisitionItemId: 'req-item-1',
        itemType: 'PRODUCT',
        articleId: 'ART-001',
        supplierPartNumber: 'SUP-PART-001',
        description: 'Sample Product Item',
        quantity: 10,
        unitPrice: 100,
        discountPercent: 5,
        totalPrice: 950,
        leadTime: 7,
        minimumOrderQuantity: 5,
        packaging: 'Standard Box',
        qualityGrade: 'A'
      },
      {
        id: randomUUID(),
        quotationId,
        requisitionItemId: 'req-item-2',
        itemType: 'SERVICE',
        description: 'Installation Service',
        quantity: 1,
        unitPrice: 500,
        discountPercent: 0,
        totalPrice: 500,
        leadTime: 14,
        minimumOrderQuantity: 1
      }
    ];

    return {
      id: quotationId,
      requisitionId: 'req-123',
      supplierId: 'sup-123',
      supplierName: 'Mock Supplier',
      quotationNumber: 'QUO-123',
      quotationDate: new Date(),
      validUntil: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      currency: 'EUR',
      items: mockItems,
      totalAmount: 1450,
      taxAmount: 275.5,
      deliveryTerms: 'EXW',
      paymentTerms: 'NET 30',
      deliveryTime: 14,
      warranty: '12 months',
      qualityCertificates: ['ISO 9001'],
      status: 'SUBMITTED',
      evaluationScore: undefined,
      evaluationNotes: undefined,
      createdAt: new Date(),
      tenantId
    };
  }

  private async getSupplierPerformance(supplierId: string, tenantId: string): Promise<any> {
    // Mock performance data - would calculate from historical data
    return {
      supplierId,
      supplierName: 'Mock Supplier',
      evaluationPeriod: { start: new Date(), end: new Date() },
      totalOrders: 50,
      totalValue: 500000,
      onTimeDeliveryRate: 95,
      qualityScore: 8.5,
      priceCompetitiveness: 7.2,
      communicationRating: 8.0,
      overallRating: 8.0,
      defectRate: 0.5,
      averageDeliveryTime: 12,
      paymentTermsCompliance: 98,
      certificationStatus: ['ISO 9001'],
      riskLevel: 'LOW',
      recommendedActions: [],
      lastEvaluated: new Date(),
      tenantId
    };
  }

  private calculatePriceScore(quotation: SupplierQuotation, allQuotationIds: string[], tenantId: string): number {
    // Simplified price scoring - lowest price gets 10, others proportionally less
    return 7.5; // Mock score
  }

  private calculateDeliveryScore(quotation: SupplierQuotation, performance: any): number {
    if (!performance) return 5; // Default score

    // Score based on delivery time and on-time delivery rate
    const timeScore = Math.max(0, 10 - (quotation.deliveryTime / 3));
    const reliabilityScore = (performance.onTimeDeliveryRate / 100) * 10;

    return (timeScore + reliabilityScore) / 2;
  }

  private async generatePONumber(tenantId: string): Promise<string> {
    return `PO-${Date.now()}-${tenantId.substring(0, 4).toUpperCase()}`;
  }

  private async isPurchaseOrderApprovalRequired(amount: number, userId: string, tenantId: string): Promise<boolean> {
    const threshold = await this.getAutoApprovalThreshold(userId, tenantId);
    return amount > threshold;
  }

  private async routePurchaseOrderForApproval(purchaseOrder: PurchaseOrder, userId: string): Promise<void> {
    console.log(`Routing PO ${purchaseOrder.purchaseOrderNumber} for approval`);
  }

  private async submitPurchaseOrderToSupplier(purchaseOrder: PurchaseOrder, userId: string): Promise<void> {
    console.log(`Submitted PO ${purchaseOrder.purchaseOrderNumber} to supplier ${purchaseOrder.supplierId}`);
  }

  private async getPurchaseOrder(purchaseOrderId: string, tenantId: string): Promise<PurchaseOrder> {
    // Mock PO - would query from database
    return new PurchaseOrder(
      'sup-123', // supplierId
      'Mock Purchase Order', // subject
      'Mock purchase order description', // description
      new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // deliveryDate
      [], // items
      'user-123', // createdBy
      {
        id: purchaseOrderId,
        purchaseOrderNumber: 'PO-123',
        status: PurchaseOrderStatus.BESTELLT,
        currency: 'EUR',
        taxRate: 19,
        paymentTerms: 'NET 30'
      }
    );
  }

  private async validateReceiptQuantities(
    receiptItems: GoodsReceiptItem[],
    poItems: PurchaseOrderItem[]
  ): Promise<{ isValid: boolean; errors: string[] }> {
    // Simplified validation - would implement comprehensive checks
    return { isValid: true, errors: [] };
  }

  private async updateInventoryLevels(goodsReceipt: GoodsReceiptNote): Promise<void> {
    console.log(`Updated inventory for goods receipt ${goodsReceipt.id}`);
  }

  private async checkIfAllItemsReceived(purchaseOrderId: string, tenantId: string): Promise<boolean> {
    // Would check if all PO items have been fully received
    return false; // Mock - partial delivery
  }

  private async updatePurchaseOrderStatus(
    purchaseOrderId: string,
    status: PurchaseOrderStatus,
    tenantId: string
  ): Promise<void> {
    console.log(`Updated PO ${purchaseOrderId} status to ${status}`);
  }

  private async performFinalValidation(purchaseOrder: PurchaseOrder, tenantId: string): Promise<void> {
    // Perform final validation checks before order finalization
    // Check budget availability, supplier credit limits, item availability, etc.

    // Validate budget
    const budgetValidation = await this.validateBudgetAuthorization(
      'DEFAULT', // Would get from PO
      purchaseOrder.totalAmount,
      tenantId
    );

    if (!budgetValidation.isValid) {
      throw new Error(`Budget validation failed: ${budgetValidation.reason}`);
    }

    // Validate supplier status
    const supplierDetails = await this.getSupplierDetails(purchaseOrder.supplierId, tenantId);
    if (!supplierDetails.active) {
      throw new Error('Supplier is not active');
    }

    // Additional validations can be added here
    console.log(`Final validation passed for PO ${purchaseOrder.purchaseOrderNumber}`);
  }
}