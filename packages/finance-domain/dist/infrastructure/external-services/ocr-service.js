"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - OCR Service
 *
 * Optical Character Recognition service for document processing
 * Basic implementation for invoice document text extraction
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.BasicOCRService = void 0;
exports.createOCRService = createOCRService;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * Basic OCR Service Implementation
 * Uses simple text extraction for demonstration
 * In production, integrate with services like Google Vision AI, AWS Textract, etc.
 */
class BasicOCRService {
    constructor(dependencies) {
        this.dependencies = dependencies;
    }
    /**
     * Process document and extract OCR data
     */
    async processDocument(documentPath) {
        const documentId = crypto.randomUUID();
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
        }
        catch (error) {
            throw new Error(`OCR processing failed for ${documentPath}: ${error}`);
        }
    }
    /**
     * Extract structured fields from OCR data
     */
    async extractFields(ocrData, template) {
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
    extractTextFromFile(buffer, filePath) {
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
    extractFieldsFromText(text, filePath) {
        const fields = [];
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
    extractInvoiceFields(ocrData) {
        const lines = [];
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
    calculateConfidence(fields) {
        if (fields.length === 0)
            return 0;
        const totalConfidence = fields.reduce((sum, field) => sum + field.confidence, 0);
        return totalConfidence / fields.length;
    }
}
exports.BasicOCRService = BasicOCRService;
/**
 * Factory function for OCR service
 */
function createOCRService(dependencies = {}) {
    return new BasicOCRService(dependencies);
}
//# sourceMappingURL=ocr-service.js.map