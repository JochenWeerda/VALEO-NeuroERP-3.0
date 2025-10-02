/**
 * VALEO NeuroERP 3.0 - Finance Domain - OCR Service
 *
 * Optical Character Recognition service for document processing
 * Basic implementation for invoice document text extraction
 */
import { OCRData } from '../../core/entities/ap-invoice';
export interface OCRService {
    processDocument(documentPath: string): Promise<OCRData>;
    extractFields(ocrData: OCRData, template: string): Promise<any[]>;
}
export interface OCRServiceDependencies {
}
/**
 * Basic OCR Service Implementation
 * Uses simple text extraction for demonstration
 * In production, integrate with services like Google Vision AI, AWS Textract, etc.
 */
export declare class BasicOCRService implements OCRService {
    private readonly dependencies;
    constructor(dependencies: OCRServiceDependencies);
    /**
     * Process document and extract OCR data
     */
    processDocument(documentPath: string): Promise<OCRData>;
    /**
     * Extract structured fields from OCR data
     */
    extractFields(ocrData: OCRData, template: string): Promise<any[]>;
    /**
     * Extract text from file based on file type
     */
    private extractTextFromFile;
    /**
     * Extract fields from raw text using pattern matching
     */
    private extractFieldsFromText;
    /**
     * Extract invoice line items from OCR data
     */
    private extractInvoiceFields;
    /**
     * Calculate overall confidence score
     */
    private calculateConfidence;
}
/**
 * Factory function for OCR service
 */
export declare function createOCRService(dependencies?: OCRServiceDependencies): OCRService;
//# sourceMappingURL=ocr-service.d.ts.map