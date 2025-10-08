/**
 * VALEO NeuroERP 3.0 - ZUGFeRD Adapter Service
 *
 * E-Invoice adapter for ZUGFeRD 2.1.1 compliance
 * Handles parsing, validation, and generation of ZUGFeRD invoices
 */

import { Result, err, ok } from '../core/entities/ar-invoice';

// ===== INTERFACES =====

export interface EInvoiceDocument {
  id: string;
  fileName: string;
  mimeType: string;
  content: Buffer;
  size: number;
  hash: string;
}

export interface ZUGFeRDProfile {
  version: string;
  profile: 'BASIC' | 'EN16931' | 'EXTENDED';
  conformanceLevel: 'BASIC' | 'COMFORT' | 'EXTENDED';
}

export interface NormalizedInvoice {
  supplier: {
    vatId: string;
    name: string;
    address: {
      street: string;
      city: string;
      postalCode: string;
      country: string;
    };
    contact?: {
      email?: string;
      phone?: string;
    };
  };
  buyer: {
    vatId: string;
    name: string;
    address: {
      street: string;
      city: string;
      postalCode: string;
      country: string;
    };
  };
  invoice: {
    id: string;
    issueDate: string;
    dueDate: string;
    currency: string;
    lines: Array<{
      id: string;
      sku?: string;
      name: string;
      description?: string;
      quantity: number;
      unitPrice: number;
      taxPercent: number;
      taxCode: string;
      net: number;
      tax: number;
      gross: number;
    }>;
    totals: {
      net: number;
      tax: number;
      gross: number;
    };
    payment: {
      iban?: string;
      bic?: string;
      terms: string;
    };
    profile: string;
    attachments: Array<{
      filename: string;
      mimeType: string;
      content: Buffer;
    }>;
  };
}

export interface ValidationResult {
  valid: boolean;
  profile: string;
  schemaVersion: string;
  issues: Array<{
    type: 'ERROR' | 'WARNING' | 'INFO';
    code: string;
    message: string;
    field?: string;
  }>;
}

export interface EInvoiceAdapter {
  detectProfile(document: EInvoiceDocument): Promise<Result<ZUGFeRDProfile>>;
  parseToNormalized(document: EInvoiceDocument): Promise<Result<NormalizedInvoice>>;
  validate(document: EInvoiceDocument): Promise<Result<ValidationResult>>;
  renderPDFA3(invoice: NormalizedInvoice): Promise<Result<Buffer>>;
}

// ===== SERVICE =====

export class ZUGFeRDAdapterService {
  constructor(
    private readonly adapter: EInvoiceAdapter,
    private readonly documentStore: DocumentStore,
    private readonly eventPublisher: EventPublisher
  ) {}

  /**
   * Ingest and process e-invoice document
   */
  async ingestEInvoice(
    document: EInvoiceDocument,
    options: { detectProfile?: boolean } = {}
  ): Promise<Result<{
    profile: ZUGFeRDProfile;
    normalizedInvoice: NormalizedInvoice;
    validation: ValidationResult;
    xmlRef?: string;
    pdfa3Ref?: string;
  }>> {
    try {
      // Detect profile if requested
      let profile: ZUGFeRDProfile;
      if (options.detectProfile) {
        const profileResult = await this.adapter.detectProfile(document);
        if (profileResult.isFailure) {
          return err(profileResult.error || 'Profile detection failed');
        }
        profile = profileResult.getValue();
      } else {
        // Default to EN16931 for now
        profile = {
          version: '2.1.1',
          profile: 'EN16931',
          conformanceLevel: 'COMFORT'
        };
      }

      // Parse to normalized format
      const parseResult = await this.adapter.parseToNormalized(document);
      if (parseResult.isFailure) {
        return err(parseResult.error || 'Parsing failed');
      }
      const normalizedInvoice = parseResult.getValue();

      // Validate the document
      const validationResult = await this.adapter.validate(document);
      if (validationResult.isFailure) {
        return err(validationResult.error || 'Validation failed');
      }
      const validation = validationResult.getValue();

      // Store original document
      const docRef = await this.documentStore.store(document);

      // Generate PDF/A-3 if not present
      let pdfa3Ref: string | undefined;
      if (document.mimeType !== 'application/pdf') {
        const pdfResult = await this.adapter.renderPDFA3(normalizedInvoice);
        if (pdfResult.isSuccess) {
          const pdfDocument: EInvoiceDocument = {
            id: `pdf-${document.id}`,
            fileName: document.fileName.replace(/\.[^.]+$/, '.pdf'),
            mimeType: 'application/pdf',
            content: pdfResult.getValue(),
            size: pdfResult.getValue().length,
            hash: this.calculateHash(pdfResult.getValue())
          };
          pdfa3Ref = await this.documentStore.store(pdfDocument);
        }
      }

      // Publish event
      await this.eventPublisher.publish({
        type: 'finance.einv.parsed',
        source: 'upload',
        profile: profile.profile,
        schemaVersion: profile.version,
        invoiceDto: normalizedInvoice,
        xmlRef: docRef,
        pdfa3Ref
      });

      return ok({
        profile,
        normalizedInvoice,
        validation,
        ...(docRef && { xmlRef: docRef }),
        ...(pdfa3Ref && { pdfa3Ref })
      });

    } catch (error) {
      return err(error instanceof Error ? error.message : 'Unknown error');
    }
  }

  /**
   * Validate e-invoice document
   */
  async validateEInvoice(
    documentRef: string
  ): Promise<Result<ValidationResult>> {
    const document = await this.documentStore.retrieve(documentRef);
    if (!document) {
      return err(`Document ${documentRef} not found`);
    }

    return await this.adapter.validate(document);
  }

  /**
   * Render normalized invoice as PDF/A-3
   */
  async renderPDFA3(
    invoice: NormalizedInvoice
  ): Promise<Result<Buffer>> {
    return await this.adapter.renderPDFA3(invoice);
  }

  private calculateHash(content: Buffer): string {
    // Simple hash for demo - in production use crypto.subtle or similar
    return content.toString('base64').substring(0, 32);
  }
}

// ===== INTERFACES =====

export interface DocumentStore {
  store(document: EInvoiceDocument): Promise<string>;
  retrieve(ref: string): Promise<EInvoiceDocument | null>;
  delete(ref: string): Promise<void>;
}

export interface EventPublisher {
  publish(event: any): Promise<void>;
}

// ===== MOCK ADAPTER (for development) =====

export class MockZUGFeRDAdapter implements EInvoiceAdapter {
  async detectProfile(document: EInvoiceDocument): Promise<Result<ZUGFeRDProfile>> {
    // Mock detection - in reality would analyze file content
    return ok({
      version: '2.1.1',
      profile: 'EN16931',
      conformanceLevel: 'COMFORT'
    });
  }

  async parseToNormalized(document: EInvoiceDocument): Promise<Result<NormalizedInvoice>> {
    // Mock parsing - in reality would parse XML content
    return ok({
      supplier: {
        vatId: 'DE123456789',
        name: 'Musterfirma GmbH',
        address: {
          street: 'Musterstraße 123',
          city: 'Musterstadt',
          postalCode: '12345',
          country: 'DE'
        }
      },
      buyer: {
        vatId: 'DE987654321',
        name: 'Kunden AG',
        address: {
          street: 'Kundenweg 456',
          city: 'Kundenstadt',
          postalCode: '67890',
          country: 'DE'
        }
      },
      invoice: {
        id: 'INV-2025-001',
        issueDate: '2025-09-28',
        dueDate: '2025-10-28',
        currency: 'EUR',
        lines: [
          {
            id: '1',
            sku: 'A-100',
            name: 'Produkt A',
            quantity: 10,
            unitPrice: 50.00,
            taxPercent: 19,
            taxCode: 'DE-19',
            net: 500.00,
            tax: 95.00,
            gross: 595.00
          }
        ],
        totals: {
          net: 500.00,
          tax: 95.00,
          gross: 595.00
        },
        payment: {
          terms: '30 Tage netto'
        },
        profile: 'ZUGFeRD-EN16931',
        attachments: []
      }
    });
  }

  async validate(document: EInvoiceDocument): Promise<Result<ValidationResult>> {
    // Mock validation - in reality would validate against schema
    return ok({
      valid: true,
      profile: 'EN16931',
      schemaVersion: '2.1.1',
      issues: []
    });
  }

  async renderPDFA3(invoice: NormalizedInvoice): Promise<Result<Buffer>> {
    // Mock PDF generation - in reality would generate PDF/A-3
    const mockPdfContent = Buffer.from(`%PDF-1.7\nMock PDF/A-3 for ${invoice.invoice.id}`);
    return ok(mockPdfContent);
  }
}

// ===== REPOSITORY INTERFACE =====

export interface EInvoiceRepository {
  saveValidation(result: ValidationResult): Promise<string>;
  findValidationByDocument(docRef: string): Promise<ValidationResult | null>;
  saveNormalized(invoice: NormalizedInvoice): Promise<string>;
  findNormalizedById(id: string): Promise<NormalizedInvoice | null>;
}