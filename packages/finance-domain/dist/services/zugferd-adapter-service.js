"use strict";
/**
 * VALEO NeuroERP 3.0 - ZUGFeRD Adapter Service
 *
 * E-Invoice adapter for ZUGFeRD 2.1.1 compliance
 * Handles parsing, validation, and generation of ZUGFeRD invoices
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MockZUGFeRDAdapter = exports.ZUGFeRDAdapterService = void 0;
const ar_invoice_1 = require("../core/entities/ar-invoice");
// ===== SERVICE =====
class ZUGFeRDAdapterService {
    constructor(adapter, documentStore, eventPublisher) {
        this.adapter = adapter;
        this.documentStore = documentStore;
        this.eventPublisher = eventPublisher;
    }
    /**
     * Ingest and process e-invoice document
     */
    async ingestEInvoice(document, options = {}) {
        try {
            // Detect profile if requested
            let profile;
            if (options.detectProfile) {
                const profileResult = await this.adapter.detectProfile(document);
                if (profileResult.isFailure) {
                    return (0, ar_invoice_1.err)(profileResult.error || 'Profile detection failed');
                }
                profile = profileResult.getValue();
            }
            else {
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
                return (0, ar_invoice_1.err)(parseResult.error || 'Parsing failed');
            }
            const normalizedInvoice = parseResult.getValue();
            // Validate the document
            const validationResult = await this.adapter.validate(document);
            if (validationResult.isFailure) {
                return (0, ar_invoice_1.err)(validationResult.error || 'Validation failed');
            }
            const validation = validationResult.getValue();
            // Store original document
            const docRef = await this.documentStore.store(document);
            // Generate PDF/A-3 if not present
            let pdfa3Ref;
            if (document.mimeType !== 'application/pdf') {
                const pdfResult = await this.adapter.renderPDFA3(normalizedInvoice);
                if (pdfResult.isSuccess) {
                    const pdfDocument = {
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
            return (0, ar_invoice_1.ok)({
                profile,
                normalizedInvoice,
                validation,
                ...(docRef && { xmlRef: docRef }),
                ...(pdfa3Ref && { pdfa3Ref })
            });
        }
        catch (error) {
            return (0, ar_invoice_1.err)(error instanceof Error ? error.message : 'Unknown error');
        }
    }
    /**
     * Validate e-invoice document
     */
    async validateEInvoice(documentRef) {
        const document = await this.documentStore.retrieve(documentRef);
        if (!document) {
            return (0, ar_invoice_1.err)(`Document ${documentRef} not found`);
        }
        return await this.adapter.validate(document);
    }
    /**
     * Render normalized invoice as PDF/A-3
     */
    async renderPDFA3(invoice) {
        return await this.adapter.renderPDFA3(invoice);
    }
    calculateHash(content) {
        // Simple hash for demo - in production use crypto.subtle or similar
        return content.toString('base64').substring(0, 32);
    }
}
exports.ZUGFeRDAdapterService = ZUGFeRDAdapterService;
// ===== MOCK ADAPTER (for development) =====
class MockZUGFeRDAdapter {
    async detectProfile(document) {
        // Mock detection - in reality would analyze file content
        return (0, ar_invoice_1.ok)({
            version: '2.1.1',
            profile: 'EN16931',
            conformanceLevel: 'COMFORT'
        });
    }
    async parseToNormalized(document) {
        // Mock parsing - in reality would parse XML content
        return (0, ar_invoice_1.ok)({
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
    async validate(document) {
        // Mock validation - in reality would validate against schema
        return (0, ar_invoice_1.ok)({
            valid: true,
            profile: 'EN16931',
            schemaVersion: '2.1.1',
            issues: []
        });
    }
    async renderPDFA3(invoice) {
        // Mock PDF generation - in reality would generate PDF/A-3
        const mockPdfContent = Buffer.from(`%PDF-1.7\nMock PDF/A-3 for ${invoice.invoice.id}`);
        return (0, ar_invoice_1.ok)(mockPdfContent);
    }
}
exports.MockZUGFeRDAdapter = MockZUGFeRDAdapter;
//# sourceMappingURL=zugferd-adapter-service.js.map