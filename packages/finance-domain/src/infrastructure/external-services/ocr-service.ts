/**
 * VALEO NeuroERP 3.0 - Finance Domain - OCR Service
 *
 * Optical Character Recognition service for document processing
 * Basic implementation for invoice document text extraction
 */

import { DocumentId, OCRData, OCRField } from '../../core/entities/ap-invoice';
import * as fs from 'fs';
import * as path from 'path';

export interface OCRService {
  processDocument(documentPath: string): Promise<OCRData>;
  extractFields(ocrData: OCRData, template: string): Promise<any[]>;
}

export interface OCRServiceDependencies {
  // Add dependencies as needed (e.g., external OCR API clients)
}

/**
 * Basic OCR Service Implementation
 * Uses simple text extraction for demonstration
 * In production, integrate with services like Google Vision AI, AWS Textract, etc.
 */
export class BasicOCRService implements OCRService {
  constructor(
    private readonly dependencies: OCRServiceDependencies
  ) {}

  /**
   * Process document and extract OCR data
   */
  async processDocument(documentPath: string): Promise<OCRData> {
    const documentId = crypto.randomUUID() as DocumentId;
    const extractedAt = new Date();

    try {
      // Read file content
      const fileContent = fs.readFileSync(documentPath);
      const rawText = this.extractTextFromFile(fileContent, documentPath);

      // Extract fields using basic pattern matching
      const fields = this.extractFieldsFromText(rawText, documentPath);

      return {
        documentId,
        extractedAt,
        confidence: this.calculateConfidence(fields),
        fields,
        rawText,
        processingMetadata: {
          fileSize: fileContent.length,
          fileType: path.extname(documentPath),
          extractionMethod: 'basic-text-extraction'
        }
      };
    } catch (error) {
      throw new Error(`OCR processing failed for ${documentPath}: ${error}`);
    }
  }

  /**
   * Extract structured fields from OCR data
   */
  async extractFields(ocrData: OCRData, template: string): Promise<any[]> {
    switch (template) {
      case 'AP_INVOICE_TEMPLATE':
        return this.extractInvoiceFields(ocrData);
      default:
        throw new Error(`Unknown template: ${template}`);
    }
  }

  /**
   * Extract text from file based on file type
   */
  private extractTextFromFile(buffer: Buffer, filePath: string): string {
    const ext = path.extname(filePath).toLowerCase();

    // For demonstration, return mock text
    // In production, use proper OCR libraries
    return `INVOICE
Invoice Number: INV-2025-00123
Date: 2025-09-28
Due Date: 2025-10-28
Supplier: ABC GmbH
Amount: 1,250.00 EUR
Tax: 237.50 EUR
Total: 1,487.50 EUR

Line Items:
1. Office Supplies - 500.00 EUR
2. Software License - 750.00 EUR`;
  }

  /**
   * Extract fields from raw text using pattern matching
   */
  private extractFieldsFromText(text: string, filePath: string): OCRField[] {
    const fields: OCRField[] = [];
    const lines = text.split('\n');
    const pageNumber = 1;

    // Simple pattern matching for common invoice fields
    const patterns = [
      { name: 'invoice_number', pattern: /invoice\s+number:?\s*([^\n\r]+)/i },
      { name: 'invoice_date', pattern: /(?:issue\s+date|date):?\s*([^\n\r]+)/i },
      { name: 'due_date', pattern: /due\s+date:?\s*([^\n\r]+)/i },
      { name: 'supplier_name', pattern: /supplier:?\s*([^\n\r]+)/i },
      { name: 'total_amount', pattern: /(?:total|amount):?\s*([^\n\r]+)/i },
      { name: 'tax_amount', pattern: /(?:tax|vat):?\s*([^\n\r]+)/i },
      { name: 'currency', pattern: /(EUR|USD|GBP)/i }
    ];

    for (const { name, pattern } of patterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        fields.push({
          fieldName: name,
          value: match[1].trim(),
          confidence: 0.85, // Mock confidence
          pageNumber
        });
      }
    }

    return fields;
  }

  /**
   * Extract invoice line items from OCR data
   */
  private extractInvoiceFields(ocrData: OCRData): any[] {
    const lines: any[] = [];

    // Mock line item extraction
    // In production, use more sophisticated parsing
    const lineItemPatterns = [
      {
        description: 'Office Supplies',
        quantity: 1,
        unitPrice: 500.00,
        lineTotal: 500.00,
        taxRate: 0.19,
        taxAmount: 95.00
      },
      {
        description: 'Software License',
        quantity: 1,
        unitPrice: 750.00,
        lineTotal: 750.00,
        taxRate: 0.19,
        taxAmount: 142.50
      }
    ];

    return lineItemPatterns.map((item, index) => ({
      lineNumber: index + 1,
      description: item.description,
      quantity: item.quantity,
      unitPrice: item.unitPrice,
      lineTotal: item.lineTotal,
      taxRate: item.taxRate,
      taxAmount: item.taxAmount,
      metadata: {}
    }));
  }

  /**
   * Calculate overall confidence score
   */
  private calculateConfidence(fields: OCRField[]): number {
    if (fields.length === 0) return 0;

    const totalConfidence = fields.reduce((sum, field) => sum + field.confidence, 0);
    return totalConfidence / fields.length;
  }
}

/**
 * Factory function for OCR service
 */
export function createOCRService(
  dependencies: OCRServiceDependencies = {}
): OCRService {
  return new BasicOCRService(dependencies);
}