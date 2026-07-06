/**
 * VALEO NeuroERP 3.0 - Finance Domain - AP Invoice Application Service
 *
 * Application Service for Accounts Payable invoice processing
 * Sprint 2 Implementation: OCR processing and AI booking
 */

import fs from 'fs';
import {
  AIBookingProposedEvent,
  AIBookingService,
  APInvoice,
  APInvoiceApprovedEvent,
  APInvoiceEntity,
  APInvoicePaidEvent,
  APInvoiceReceivedEvent,
  APInvoiceRepository,
  APInvoiceService,
  ApproveAPInvoiceCommand,
  CreateAPInvoiceCommand,
  InvoiceId,
  OCRService,
  ProcessPaymentCommand,
  TenantId
} from '../../core/entities/ap-invoice';

import {
  EInvoiceNormalizedDTO,
  ZUGFeRDAdapterApplicationService
} from './zugferd-adapter-service';

import {
  COLLECTION,
  HEX_VALUES,
  PERCENTAGES
} from '../../core/constants/finance-constants';

// ===== INTERFACES =====

export interface EventPublisher {
  publish(event: any): Promise<void>;
}

export interface APInvoiceServiceDependencies {
  apInvoiceRepository: APInvoiceRepository;
  ocrService: OCRService;
  aiBookingService: AIBookingService;
  zugferdAdapter?: ZUGFeRDAdapterApplicationService;
  eventPublisher: EventPublisher;
}

// ===== APPLICATION SERVICE =====

export class APInvoiceApplicationService implements APInvoiceService {
  constructor(
    private readonly dependencies: APInvoiceServiceDependencies
  ) {}

  /**
   * Create AP invoice from document
   */
  async createInvoice(command: CreateAPInvoiceCommand): Promise<InvoiceId> {
    // Process OCR if document reference provided
    let ocrData = command.ocrData;
    if (!ocrData && command.documentRef) {
      try {
        ocrData = await this.dependencies.ocrService.processDocument(command.documentRef);
      } catch (error) {
        console.warn('OCR processing failed, creating invoice without OCR data:', error);
      }
    }

    // Create invoice entity
    const createCommand = { ...command };
    if (ocrData !== undefined) {
      createCommand.ocrData = ocrData;
    }
    const invoice = APInvoiceEntity.create(createCommand);

    // Save to repository
    await this.dependencies.apInvoiceRepository.save(invoice);

    // Publish event
    const event = new APInvoiceReceivedEvent(invoice);
    await this.dependencies.eventPublisher.publish(event);

    // Trigger AI booking proposal if OCR data available
    if (ocrData && ocrData.confidence > PERCENTAGES.EIGHTY_PERCENT) {
      try {
        const aiProposal = await this.dependencies.aiBookingService.proposeBooking(invoice);
        const invoiceWithAI = invoice.addAIBookingProposal(aiProposal);
        await this.dependencies.apInvoiceRepository.save(invoiceWithAI);

        // Publish AI event
        const aiEvent = new AIBookingProposedEvent(
          invoice.id,
          invoice.tenantId,
          aiProposal,
          aiProposal.confidence,
          aiProposal.explanation
        );
        await this.dependencies.eventPublisher.publish(aiEvent);
      } catch (error) {
        console.warn('AI booking proposal failed:', error);
      }
    }

    return invoice.id;
  }

  /**
   * Approve invoice with booking entries
   */
  async approveInvoice(command: ApproveAPInvoiceCommand): Promise<void> {
    // Get invoice
    const invoice = await this.dependencies.apInvoiceRepository.findById(command.invoiceId);
    if (!invoice) {
      throw new Error(`Invoice ${command.invoiceId} not found`);
    }

    if (invoice.status !== 'PROCESSING') {
      throw new Error('Only processing invoices can be approved');
    }

    // Approve the invoice
    const approvedInvoice = (invoice as APInvoiceEntity).approve(
      command.approvedBy,
      command.approvedEntries
    );

    // Save updated invoice
    await this.dependencies.apInvoiceRepository.save(approvedInvoice);

    // Publish event
    const event = new APInvoiceApprovedEvent(
      approvedInvoice.id,
      approvedInvoice.tenantId,
      command.approvedBy,
      command.approvedEntries,
      approvedInvoice.totalAmount
    );

    await this.dependencies.eventPublisher.publish(event);
  }

  /**
   * Process payment for invoice
   */
  async processPayment(command: ProcessPaymentCommand): Promise<void> {
    // Get invoice
    const invoice = await this.dependencies.apInvoiceRepository.findById(command.invoiceId);
    if (!invoice) {
      throw new Error(`Invoice ${command.invoiceId} not found`);
    }

    if (invoice.status !== 'APPROVED') {
      throw new Error('Only approved invoices can be paid');
    }

    // Mark as paid
    const paidInvoice = (invoice as APInvoiceEntity).markAsPaid(
      command.paidBy,
      command.paymentDate,
      command.paymentMethod
    );

    // Save updated invoice
    await this.dependencies.apInvoiceRepository.save(paidInvoice);

    // Publish event
    const event = new APInvoicePaidEvent(
      paidInvoice.id,
      paidInvoice.tenantId,
      command.paymentDate,
      command.paymentMethod,
      paidInvoice.totalAmount,
      command.paidBy
    );

    await this.dependencies.eventPublisher.publish(event);
  }

  /**
   * Get invoice by ID
   */
  async getInvoice(invoiceId: InvoiceId): Promise<APInvoice | null> {
    return await this.dependencies.apInvoiceRepository.findById(invoiceId);
  }

  /**
   * List invoices for tenant
   */
  async listInvoices(tenantId: TenantId, status?: APInvoice['status']): Promise<APInvoice[]> {
    if (status) {
      return await this.dependencies.apInvoiceRepository.findByStatus(tenantId, status);
    }
    // Return all invoices (you might want to implement pagination)
    const allStatuses: APInvoice['status'][] = ['DRAFT', 'PROCESSING', 'APPROVED', 'PAID', 'CANCELLED'];
    const allInvoices: APInvoice[] = [];

    for (const invoiceStatus of allStatuses) {
      const invoices = await this.dependencies.apInvoiceRepository.findByStatus(tenantId, invoiceStatus);
      allInvoices.push(...invoices);
    }

    return allInvoices.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  /**
   * Get overdue invoices
   */
  async getOverdueInvoices(tenantId: TenantId): Promise<APInvoice[]> {
    return await this.dependencies.apInvoiceRepository.findOverdue(tenantId);
  }

  /**
   * Get invoices pending approval
   */
  async getPendingApprovalInvoices(tenantId: TenantId): Promise<APInvoice[]> {
    return await this.dependencies.apInvoiceRepository.findPendingApproval(tenantId);
  }

  /**
   * Process e-invoice document with ZUGFeRD adapter
   */
  async processEInvoiceDocument(
    file: Buffer,
    filename: string,
    tenantId: TenantId,
    supplierId?: string
  ): Promise<InvoiceId> {
    if (!this.dependencies.zugferdAdapter) {
      throw new Error('ZUGFeRD adapter not configured');
    }

    // Process e-invoice with ZUGFeRD adapter
    const result = await this.dependencies.zugferdAdapter.ingestEInvoice(
      file,
      filename,
      tenantId.toString(),
      { detectProfile: true }
    );

    if (!result.normalized) {
      throw new Error('Failed to normalize e-invoice data');
    }

    // Convert normalized e-invoice data to AP invoice
    const invoiceId = await this.createInvoiceFromEInvoice(result.normalized, tenantId, supplierId);

    return invoiceId;
  }

  /**
   * Create AP invoice from normalized e-invoice data
   */
  private async createInvoiceFromEInvoice(
    normalizedData: EInvoiceNormalizedDTO,
    tenantId: TenantId,
    supplierId?: string
  ): Promise<InvoiceId> {
    // Convert e-invoice lines to AP invoice lines
    const lines = normalizedData.invoice.lines.map((line, index) => ({
      lineNumber: index + 1,
      description: line.name,
      quantity: line.qty,
      unitPrice: line.price,
      lineTotal: line.net,
      taxRate: line.taxPercent / 100, // Convert percentage to decimal
      taxAmount: line.tax,
      metadata: {
        sku: line.sku,
        gross: line.gross
      }
    }));

    // Create invoice command from normalized data
    const command: CreateAPInvoiceCommand = {
      tenantId,
      supplierId: supplierId ?? normalizedData.supplier.vatId,
      invoiceNumber: normalizedData.invoice.id,
      issueDate: new Date(normalizedData.invoice.issueDate),
      dueDate: new Date(normalizedData.invoice.dueDate),
      currency: normalizedData.invoice.currency,
      subtotal: normalizedData.invoice.totals.net,
      taxAmount: normalizedData.invoice.totals.tax,
      totalAmount: normalizedData.invoice.totals.gross,
      taxRate: 0.19, // Default, could be calculated from lines
      paymentTerms: normalizedData.invoice.payment.terms,
      lines,
      documentRef: `einvoice-${normalizedData.invoice.id}`, // E-invoice reference
      metadata: {
        eInvoiceProcessed: true,
        profile: normalizedData.profile,
        supplierName: normalizedData.supplier.name,
        buyerName: normalizedData.buyer.name,
        processingTimestamp: new Date().toISOString()
      }
    };

    return await this.createInvoice(command);
  }

  /**
   * Process invoice document (auto-detects e-invoice vs OCR)
   */
  async processInvoiceDocument(
    documentPath: string,
    tenantId: TenantId,
    supplierId?: string
  ): Promise<InvoiceId> {
    // If ZUGFeRD adapter is available, try to detect e-invoice first
    if (this.dependencies.zugferdAdapter) {
      try {
        // Read file to check if it's an e-invoice
        const fileBuffer = fs.readFileSync(documentPath);

        // Quick check for e-invoice indicators
        if (this.isEInvoiceDocument(fileBuffer)) {
          return await this.processEInvoiceDocument(fileBuffer, documentPath.split('/').pop() || 'unknown.pdf', tenantId, supplierId);
        }
      } catch (error) {
        console.warn('E-invoice detection failed, falling back to OCR:', error);
      }
    }

    // Fall back to OCR processing
    return await this.processInvoiceDocumentOCR(documentPath, tenantId, supplierId);
  }

  /**
   * Check if document is an e-invoice
   */
  private isEInvoiceDocument(buffer: Buffer): boolean {
    // Check for PDF/A-3 indicators
    if (buffer.length >= COLLECTION.FIVE &&
        buffer[0] === HEX_VALUES.PERCENT && // %
        buffer[1] === HEX_VALUES.P && // P
        buffer[2] === HEX_VALUES.D && // D
        buffer[3] === HEX_VALUES.F && // F
        buffer[4] === HEX_VALUES.HYPHEN) {  // -

      // Look for ZUGFeRD or XRechnung indicators in PDF
      const pdfContent = buffer.toString('latin1', 0, Math.min(10000, buffer.length));
      return pdfContent.includes('ZUGFeRD') ||
             pdfContent.includes('XRechnung') ||
             pdfContent.includes('CrossIndustryInvoice') ||
             pdfContent.includes('ubl:Invoice');
    }

    // Check for XML e-invoice
    const start = buffer.toString('utf8', 0, Math.min(1000, buffer.length));
    return start.includes('<?xml') &&
           (start.includes('<rsm:') ||
            start.includes('<Invoice') ||
            start.includes('CrossIndustryInvoice'));
  }

  /**
   * Process invoice document with OCR (legacy method)
   */
  private async processInvoiceDocumentOCR(
    documentPath: string,
    tenantId: TenantId,
    supplierId?: string
  ): Promise<InvoiceId> {
    // Process OCR
    const ocrData = await this.dependencies.ocrService.processDocument(documentPath);

    // Extract invoice data from OCR
    const invoiceLines = await this.dependencies.ocrService.extractFields(
      ocrData,
      'AP_INVOICE_TEMPLATE'
    );

    // Extract supplier information
    const supplierInfo = extractSupplierFromOCR(ocrData);

    // Create invoice command
    const command: CreateAPInvoiceCommand = {
      tenantId,
      supplierId: supplierId ?? supplierInfo.supplierId ?? 'UNKNOWN',
      invoiceNumber: extractFieldValue(ocrData.fields, 'invoice_number') ?? `OCR-${Date.now()}`,
      issueDate: parseDate(extractFieldValue(ocrData.fields, 'issue_date')) ?? new Date(),
      dueDate: parseDate(extractFieldValue(ocrData.fields, 'due_date')) ?? new Date(),
      currency: extractFieldValue(ocrData.fields, 'currency') ?? 'EUR',
      subtotal: parseFloat(extractFieldValue(ocrData.fields, 'subtotal') ?? '0'),
      taxAmount: parseFloat(extractFieldValue(ocrData.fields, 'tax_amount') ?? '0'),
      totalAmount: parseFloat(extractFieldValue(ocrData.fields, 'total_amount') ?? '0'),
      taxRate: parseFloat(extractFieldValue(ocrData.fields, 'tax_rate') ?? '0.19'),
      paymentTerms: extractFieldValue(ocrData.fields, 'payment_terms') ?? 'NET_30',
      lines: invoiceLines,
      documentRef: documentPath,
      ocrData,
      metadata: {
        ocrProcessed: true,
        ocrConfidence: ocrData.confidence,
        processingTimestamp: new Date().toISOString()
      }
    };

    return await this.createInvoice(command);
  }
}

// ===== HELPER FUNCTIONS =====

/**
 * Extract field value from OCR data
 */
function extractFieldValue(fields: any[], fieldName: string): string | null {
  const field = fields.find(f => f.fieldName.toLowerCase() === fieldName.toLowerCase());
  return field?.value ?? null;
}

/**
 * Parse date from OCR extracted string
 */
function parseDate(dateString: string | null): Date | null {
  if (!dateString) return null;

  try {
    return new Date(dateString);
  } catch {
    return null;
  }
}

/**
 * Extract supplier information from OCR data
 */
function extractSupplierFromOCR(ocrData: any): { supplierId?: string; supplierName?: string } {
  if (!ocrData?.fields || !Array.isArray(ocrData.fields)) {
    return {};
  }

  const supplierFields = ocrData.fields.filter((field: any) =>
    field?.fieldName && (
      field.fieldName.toLowerCase().includes('supplier') ||
      field.fieldName.toLowerCase().includes('vendor')
    )
  );

  return {
    supplierName: supplierFields.find((f: any) => f?.fieldName?.toLowerCase().includes('name'))?.value,
    supplierId: supplierFields.find((f: any) => f?.fieldName?.toLowerCase().includes('id'))?.value
  };
}

// ===== FACTORY FUNCTION =====

export function createAPInvoiceService(
  dependencies: APInvoiceServiceDependencies
): APInvoiceService {
  return new APInvoiceApplicationService(dependencies);
}