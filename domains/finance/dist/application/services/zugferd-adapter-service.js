"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - ZUGFeRD Adapter Service
 *
 * E-Invoice adapter for ZUGFeRD/XRechnung compliance
 * Handles document processing, validation, and format conversion
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.EInvoiceRenderedEvent = exports.EInvoiceValidatedEvent = exports.EInvoiceParsedEvent = exports.DefaultEInvoiceAdapter = exports.ZUGFeRDAdapterApplicationService = void 0;
exports.createZUGFeRDAdapterService = createZUGFeRDAdapterService;
// ===== SERVICE IMPLEMENTATION =====
class ZUGFeRDAdapterApplicationService {
    constructor(dependencies) {
        this.dependencies = dependencies;
    }
    /**
     * Ingest e-invoice document
     */
    async ingestEInvoice(file, filename, tenantId, options = {}) {
        const documentId = crypto.randomUUID();
        try {
            // Detect profile if requested
            const detectedProfile = options.detectProfile ? await this.dependencies.adapter.detectProfile(file) : null;
            // Extract XML if PDF/A-3
            let xmlContent = null;
            let extractedProfile = null;
            if (this.isPDF(file)) {
                const extraction = await this.dependencies.adapter.extractXML(file);
                if (extraction) {
                    xmlContent = extraction.xml;
                    extractedProfile = extraction.profile;
                }
            }
            // Use detected or extracted profile
            const profile = detectedProfile || extractedProfile;
            if (!profile) {
                throw new Error('Could not detect e-invoice profile');
            }
            // Validate document
            const validation = await this.dependencies.adapter.validateDocument(file, profile);
            // Parse and normalize if valid
            let normalized;
            if (validation.valid && xmlContent) {
                normalized = await this.parseAndNormalizeXML(xmlContent, profile);
            }
            // Save document
            const document = await this.dependencies.documentRepository.save({
                tenantId,
                documentId,
                filename,
                content: file,
                kind: this.isPDF(file) ? 'PDFA3' : 'XML',
                mimetype: this.isPDF(file) ? 'application/pdf' : 'application/xml',
                profile: profile || 'UNKNOWN',
                validationStatus: validation.valid ? 'VALID' : 'INVALID',
                metadata: {
                    detectedProfile,
                    extractedProfile,
                    validationErrors: validation.errors.length,
                    validationWarnings: validation.warnings.length
                }
            });
            // Save validation result
            await this.dependencies.validationRepository.save({
                tenantId,
                documentId: document.id,
                validatorName: 'ZUGFeRD-Adapter',
                validatorVersion: '2.1.1',
                validationResult: {
                    valid: validation.valid,
                    profile: validation.profile,
                    schemaVersion: validation.schemaVersion,
                    errors: validation.errors,
                    warnings: validation.warnings
                },
                passed: validation.valid,
                errorCount: validation.errors.length,
                warningCount: validation.warnings.length,
                executionTimeMs: validation.executionTime,
                metadata: {}
            });
            // Save normalized data if available
            if (normalized) {
                await this.dependencies.normalizedRepository.save({
                    tenantId,
                    invoiceId: document.id,
                    invoiceType: 'AP', // Will be determined by usage context
                    normalizedData: normalized,
                    normalizationVersion: '1.0.0',
                    confidenceScore: this.calculateNormalizationConfidence(normalized, validation),
                    normalizationMetadata: {}
                });
            }
            return {
                document,
                normalized,
                validation
            };
        }
        catch (error) {
            // Save failed document for analysis
            await this.dependencies.documentRepository.save({
                tenantId,
                documentId,
                filename,
                content: file,
                kind: this.isPDF(file) ? 'PDFA3' : 'XML',
                mimetype: this.isPDF(file) ? 'application/pdf' : 'application/xml',
                profile: 'UNKNOWN',
                validationStatus: 'ERROR',
                metadata: {
                    error: error instanceof Error ? error.message : 'Unknown error',
                    errorType: 'PROCESSING_FAILED'
                }
            });
            throw error;
        }
    }
    /**
     * Validate e-invoice document
     */
    async validateEInvoice(documentId, tenantId) {
        const document = await this.dependencies.documentRepository.findByDocumentId(tenantId, documentId);
        if (!document) {
            throw new Error(`Document ${documentId} not found`);
        }
        const profileName = document.profile || 'UNKNOWN';
        const profile = await this.dependencies.profileRepository.findByName(tenantId, profileName);
        if (!profile) {
            throw new Error(`Profile ${profileName} not found`);
        }
        return await this.dependencies.adapter.validateDocument(document.content, profileName);
    }
    /**
     * Render PDF/A-3 with embedded XML
     */
    async renderPDFA3(invoice, tenantId) {
        // Generate XML from normalized data
        const xmlContent = await this.generateZUGFeRDXML(invoice);
        // Generate base PDF/A-3
        const basePDF = await this.generateBasePDF(invoice);
        // Embed XML in PDF
        const pdfWithXML = await this.dependencies.adapter.embedXMLInPDF(basePDF, xmlContent);
        // Validate the generated PDF/A-3
        const validation = await this.dependencies.adapter.validateDocument(pdfWithXML, invoice.profile);
        // Save document
        const document = await this.dependencies.documentRepository.save({
            tenantId,
            documentId: crypto.randomUUID(),
            filename: `invoice-${invoice.invoice.id}.pdf`,
            content: pdfWithXML,
            kind: 'PDFA3',
            mimetype: 'application/pdf',
            profile: invoice.profile,
            validationStatus: validation.valid ? 'VALID' : 'INVALID',
            metadata: {
                generated: true,
                xmlEmbedded: true,
                validationErrors: validation.errors.length
            }
        });
        return {
            pdfBuffer: pdfWithXML,
            xmlContent,
            documentId: document.documentId
        };
    }
    /**
     * Detect if buffer is PDF
     */
    isPDF(buffer) {
        // PDF files start with %PDF-
        return buffer.length >= 5 &&
            buffer[0] === 0x25 && // %
            buffer[1] === 0x50 && // P
            buffer[2] === 0x44 && // D
            buffer[3] === 0x46 && // F
            buffer[4] === 0x2D; // -
    }
    isXML(buffer) {
        const start = buffer.toString('utf8', 0, Math.min(100, buffer.length));
        return start.includes('<?xml') || start.includes('<rsm:') || start.includes('<Invoice');
    }
    /**
     * Parse and normalize XML to DTO
     */
    async parseAndNormalizeXML(xmlContent, profile) {
        // XML parsing implementation would go here
        // For now, return a template structure
        const normalized = {
            supplier: {
                vatId: 'DE123456789',
                name: 'Supplier GmbH',
                address: {
                    street: 'Supplier Street 123',
                    city: 'Supplier City',
                    postalCode: '12345',
                    country: 'DE'
                }
            },
            buyer: {
                vatId: 'DE987654321',
                name: 'Buyer AG',
                address: {
                    street: 'Buyer Avenue 456',
                    city: 'Buyer City',
                    postalCode: '67890',
                    country: 'DE'
                }
            },
            invoice: {
                id: 'INV-2025-00123',
                issueDate: '2025-09-28',
                dueDate: '2025-10-28',
                currency: 'EUR',
                lines: [
                    {
                        sku: 'A-100',
                        name: 'Sample Article',
                        qty: 10,
                        price: 50.00,
                        taxPercent: 19,
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
                    iban: 'DE89370400440532013000',
                    bic: 'COBADEFFXXX',
                    terms: '30 days net'
                },
                attachments: []
            },
            profile
        };
        return normalized;
    }
    /**
     * Generate ZUGFeRD XML from normalized data
     */
    async generateZUGFeRDXML(invoice) {
        // XML generation implementation would go here
        // This would create valid ZUGFeRD 2.1.1 XML
        const xmlTemplate = `<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100">
  <rsm:ExchangedDocumentContext>
    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>${invoice.profile}</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>
  <rsm:ExchangedDocument>
    <ram:ID>${invoice.invoice.id}</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
  </rsm:ExchangedDocument>
  <!-- Additional XML structure would be generated here -->
</rsm:CrossIndustryInvoice>`;
        return xmlTemplate;
    }
    /**
     * Generate base PDF/A-3
     */
    async generateBasePDF(invoice) {
        // PDF generation implementation would go here
        // This would create a PDF/A-3 compliant document
        // For now, return a minimal PDF buffer
        return Buffer.from('%PDF-1.7\n%âãÏÓ\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Invoice: ${invoice.invoice.id}) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000200 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n274\n%%EOF');
    }
    /**
     * Calculate normalization confidence
     */
    calculateNormalizationConfidence(normalized, validation) {
        let confidence = 1.0;
        // Reduce confidence based on validation issues
        if (validation.errors.length > 0) {
            confidence -= validation.errors.length * 0.1;
        }
        if (validation.warnings.length > 0) {
            confidence -= validation.warnings.length * 0.05;
        }
        // Check data completeness
        if (!normalized.supplier.vatId)
            confidence -= 0.1;
        if (!normalized.buyer.vatId)
            confidence -= 0.1;
        if (normalized.invoice.lines.length === 0)
            confidence -= 0.2;
        return Math.max(0, Math.min(1, confidence));
    }
}
exports.ZUGFeRDAdapterApplicationService = ZUGFeRDAdapterApplicationService;
// ===== FACTORY FUNCTION =====
function createZUGFeRDAdapterService(dependencies) {
    return new ZUGFeRDAdapterApplicationService(dependencies);
}
// ===== ADAPTER IMPLEMENTATIONS =====
class DefaultEInvoiceAdapter {
    async detectProfile(document) {
        // Profile detection implementation
        if (this.isPDF(document)) {
            const extraction = await this.extractXML(document);
            return extraction?.profile || null;
        }
        // For XML files, parse and detect
        if (this.isXML(document)) {
            return this.detectXMLProfile(document.toString());
        }
        return null;
    }
    async extractXML(document) {
        // XML extraction from PDF/A-3 implementation
        // This would use a PDF library to extract embedded XML
        // For demonstration, return mock data
        return {
            xml: '<?xml version="1.0"?><Invoice></Invoice>',
            profile: 'ZUGFeRD-EN16931'
        };
    }
    async validateDocument(document, profile) {
        const startTime = Date.now();
        // Validation implementation
        const errors = [];
        const warnings = [];
        // Basic validation
        if (document.length === 0) {
            errors.push({
                code: 'EMPTY_DOCUMENT',
                message: 'Document is empty',
                path: '/',
                severity: 'ERROR'
            });
        }
        if (this.isPDF(document) && !this.isPDFA3(document)) {
            warnings.push({
                code: 'NON_PDFA3',
                message: 'Document is not PDF/A-3 compliant',
                path: '/'
            });
        }
        const executionTime = Date.now() - startTime;
        return {
            valid: errors.length === 0,
            profile,
            schemaVersion: '2.1.1',
            errors,
            warnings,
            executionTime
        };
    }
    async generatePDFA3(invoice, xml) {
        // PDF/A-3 generation implementation
        return Buffer.from('Mock PDF/A-3 content');
    }
    async embedXMLInPDF(pdf, xml) {
        // XML embedding implementation
        return Buffer.from('Mock PDF/A-3 with embedded XML');
    }
    isXML(buffer) {
        const start = buffer.toString('utf8', 0, Math.min(100, buffer.length));
        return start.includes('<?xml') || start.includes('<rsm:') || start.includes('<Invoice');
    }
    isPDF(buffer) {
        // PDF files start with %PDF-
        return buffer.length >= 5 &&
            buffer[0] === 0x25 && // %
            buffer[1] === 0x50 && // P
            buffer[2] === 0x44 && // D
            buffer[3] === 0x46 && // F
            buffer[4] === 0x2D; // -
    }
    detectXMLProfile(xmlContent) {
        if (xmlContent.includes('ZUGFeRD')) {
            if (xmlContent.includes('EN 16931'))
                return 'ZUGFeRD-EN16931';
            if (xmlContent.includes('EXTENDED'))
                return 'ZUGFeRD-EXTENDED';
            return 'ZUGFeRD-BASIC';
        }
        if (xmlContent.includes('XRechnung')) {
            return 'XRechnung-2.3';
        }
        return null;
    }
    isPDFA3(buffer) {
        // PDF/A-3 detection implementation
        // Check for PDF/A-3 conformance in metadata
        return true; // Mock implementation
    }
}
exports.DefaultEInvoiceAdapter = DefaultEInvoiceAdapter;
// ===== EVENT TYPES =====
class EInvoiceParsedEvent {
    constructor(documentId, tenantId, profile, normalizedData, validationResult) {
        this.documentId = documentId;
        this.tenantId = tenantId;
        this.profile = profile;
        this.normalizedData = normalizedData;
        this.validationResult = validationResult;
        this.type = 'finance.einvoice.parsed';
        this.occurredAt = new Date();
        this.aggregateId = documentId;
    }
}
exports.EInvoiceParsedEvent = EInvoiceParsedEvent;
class EInvoiceValidatedEvent {
    constructor(documentId, tenantId, validationResult) {
        this.documentId = documentId;
        this.tenantId = tenantId;
        this.validationResult = validationResult;
        this.type = 'finance.einvoice.validated';
        this.occurredAt = new Date();
        this.aggregateId = documentId;
    }
}
exports.EInvoiceValidatedEvent = EInvoiceValidatedEvent;
class EInvoiceRenderedEvent {
    constructor(documentId, tenantId, profile, pdfRef, xmlRef, hashes) {
        this.documentId = documentId;
        this.tenantId = tenantId;
        this.profile = profile;
        this.pdfRef = pdfRef;
        this.xmlRef = xmlRef;
        this.hashes = hashes;
        this.type = 'finance.einvoice.rendered';
        this.occurredAt = new Date();
        this.aggregateId = documentId;
    }
}
exports.EInvoiceRenderedEvent = EInvoiceRenderedEvent;
//# sourceMappingURL=zugferd-adapter-service.js.map