"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - ZUGFeRD Adapter Service Tests
 *
 * Unit tests for ZUGFeRD e-invoice processing functionality
 */
Object.defineProperty(exports, "__esModule", { value: true });
const zugferd_adapter_service_1 = require("../../src/application/services/zugferd-adapter-service");
// Mock dependencies
const mockDocumentRepository = {
    save: jest.fn(),
    findById: jest.fn(),
    findByDocumentId: jest.fn(),
    findByProfile: jest.fn(),
    findByValidationStatus: jest.fn(),
    delete: jest.fn()
};
const mockValidationRepository = {
    save: jest.fn(),
    findById: jest.fn(),
    findByDocumentId: jest.fn(),
    findLatestByDocumentId: jest.fn(),
    findByValidator: jest.fn(),
    findFailedValidations: jest.fn()
};
const mockProfileRepository = {
    save: jest.fn(),
    findById: jest.fn(),
    findByName: jest.fn(),
    findActiveProfiles: jest.fn(),
    findByStandard: jest.fn(),
    update: jest.fn()
};
const mockNormalizedRepository = {
    save: jest.fn(),
    findById: jest.fn(),
    findByInvoiceId: jest.fn(),
    findByConfidence: jest.fn(),
    update: jest.fn()
};
const mockEventPublisher = {
    publish: jest.fn()
};
const mockAdapter = {
    detectProfile: jest.fn(),
    extractXML: jest.fn(),
    validateDocument: jest.fn(),
    generatePDFA3: jest.fn(),
    embedXMLInPDF: jest.fn()
};
describe('ZUGFeRDAdapterApplicationService', () => {
    let service;
    beforeEach(() => {
        jest.clearAllMocks();
        const dependencies = {
            documentRepository: mockDocumentRepository,
            validationRepository: mockValidationRepository,
            profileRepository: mockProfileRepository,
            normalizedRepository: mockNormalizedRepository,
            adapter: mockAdapter,
            eventPublisher: mockEventPublisher
        };
        service = (0, zugferd_adapter_service_1.createZUGFeRDAdapterService)(dependencies);
    });
    describe('ingestEInvoice', () => {
        it('should successfully ingest a valid PDF e-invoice', async () => {
            // Arrange
            const testFile = Buffer.from('%PDF-1.7\n%âãÏÓ\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Invoice) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000200 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n274\n%%EOF');
            mockAdapter.detectProfile.mockResolvedValue('ZUGFeRD-EN16931');
            mockAdapter.extractXML.mockResolvedValue({
                xml: '<?xml version="1.0"?><rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"><rsm:ExchangedDocument><ram:ID>INV-2025-001</ram:ID></rsm:ExchangedDocument></rsm:CrossIndustryInvoice>',
                profile: 'ZUGFeRD-EN16931'
            });
            mockAdapter.validateDocument.mockResolvedValue({
                valid: true,
                profile: 'ZUGFeRD-EN16931',
                schemaVersion: '2.1.1',
                errors: [],
                warnings: [],
                executionTime: 150
            });
            mockDocumentRepository.save.mockResolvedValue({
                id: 'doc-123',
                tenantId: 'tenant-1',
                documentId: 'doc-456',
                filename: 'test.pdf',
                content: testFile,
                kind: 'PDFA3',
                mimetype: 'application/pdf',
                profile: 'ZUGFeRD-EN16931',
                validationStatus: 'VALID',
                metadata: {},
                createdAt: new Date()
            });
            mockValidationRepository.save.mockResolvedValue({
                id: 'val-123',
                tenantId: 'tenant-1',
                documentId: 'doc-123',
                validatorName: 'ZUGFeRD-Adapter',
                validatorVersion: '2.1.1',
                validationResult: {
                    valid: true,
                    profile: 'ZUGFeRD-EN16931',
                    schemaVersion: '2.1.1',
                    errors: [],
                    warnings: []
                },
                passed: true,
                errorCount: 0,
                warningCount: 0,
                executionTimeMs: 150,
                metadata: {},
                createdAt: new Date()
            });
            mockNormalizedRepository.save.mockResolvedValue({
                id: 'norm-123',
                tenantId: 'tenant-1',
                invoiceId: 'doc-123',
                invoiceType: 'AP',
                normalizedData: {
                    supplier: {
                        vatId: 'DE123456789',
                        name: 'Test Supplier',
                        address: {
                            street: 'Test Street 1',
                            city: 'Test City',
                            postalCode: '12345',
                            country: 'DE'
                        }
                    },
                    buyer: {
                        vatId: 'DE987654321',
                        name: 'Test Buyer',
                        address: {
                            street: 'Buyer Street 1',
                            city: 'Buyer City',
                            postalCode: '67890',
                            country: 'DE'
                        }
                    },
                    invoice: {
                        id: 'INV-2025-001',
                        issueDate: '2025-09-28',
                        dueDate: '2025-10-28',
                        currency: 'EUR',
                        lines: [{
                                sku: 'TEST-001',
                                name: 'Test Article',
                                qty: 1,
                                price: 100.00,
                                taxPercent: 19,
                                net: 100.00,
                                tax: 19.00,
                                gross: 119.00
                            }],
                        totals: {
                            net: 100.00,
                            tax: 19.00,
                            gross: 119.00
                        },
                        payment: {
                            iban: 'DE89370400440532013000',
                            bic: 'COBADEFFXXX',
                            terms: '30 days net'
                        },
                        attachments: []
                    },
                    profile: 'ZUGFeRD-EN16931'
                },
                normalizationVersion: '1.0.0',
                confidenceScore: 0.95,
                normalizationMetadata: {},
                createdAt: new Date()
            });
            // Act
            const result = await service.ingestEInvoice(testFile, 'test-invoice.pdf', 'tenant-1', { detectProfile: true });
            // Assert
            expect(result.document).toBeDefined();
            expect(result.normalized).toBeDefined();
            expect(result.validation.valid).toBe(true);
            expect(result.validation.profile).toBe('ZUGFeRD-EN16931');
            expect(mockAdapter.detectProfile).toHaveBeenCalledWith(testFile);
            expect(mockAdapter.extractXML).toHaveBeenCalledWith(testFile);
            expect(mockAdapter.validateDocument).toHaveBeenCalledWith(testFile, 'ZUGFeRD-EN16931');
            expect(mockDocumentRepository.save).toHaveBeenCalled();
            expect(mockValidationRepository.save).toHaveBeenCalled();
            expect(mockNormalizedRepository.save).toHaveBeenCalled();
        });
        it('should handle invalid e-invoice documents', async () => {
            // Arrange
            const invalidFile = Buffer.from('Invalid content');
            mockAdapter.detectProfile.mockResolvedValue(null);
            mockAdapter.validateDocument.mockResolvedValue({
                valid: false,
                profile: 'UNKNOWN',
                schemaVersion: '2.1.1',
                errors: [{ code: 'INVALID_FORMAT', message: 'Document format not recognized', path: '/', severity: 'ERROR' }],
                warnings: [],
                executionTime: 50
            });
            mockDocumentRepository.save.mockResolvedValue({
                id: 'doc-123',
                tenantId: 'tenant-1',
                documentId: 'doc-456',
                filename: 'invalid.pdf',
                content: invalidFile,
                kind: 'PDFA3',
                mimetype: 'application/pdf',
                profile: 'UNKNOWN',
                validationStatus: 'INVALID',
                metadata: {},
                createdAt: new Date()
            });
            // Act
            const result = await service.ingestEInvoice(invalidFile, 'invalid-invoice.pdf', 'tenant-1');
            // Assert
            expect(result.document.validationStatus).toBe('INVALID');
            expect(result.validation.valid).toBe(false);
            expect(result.validation.errors).toHaveLength(1);
            expect(result.normalized).toBeUndefined();
        });
        it('should handle processing errors gracefully', async () => {
            // Arrange
            const testFile = Buffer.from('Test content');
            mockAdapter.detectProfile.mockRejectedValue(new Error('Processing failed'));
            mockDocumentRepository.save.mockResolvedValue({
                id: 'doc-123',
                tenantId: 'tenant-1',
                documentId: 'doc-456',
                filename: 'error.pdf',
                content: testFile,
                kind: 'PDFA3',
                mimetype: 'application/pdf',
                profile: 'UNKNOWN',
                validationStatus: 'ERROR',
                metadata: {
                    error: 'Processing failed',
                    errorType: 'PROCESSING_FAILED'
                },
                createdAt: new Date()
            });
            // Act & Assert
            await expect(service.ingestEInvoice(testFile, 'error-invoice.pdf', 'tenant-1')).rejects.toThrow('Processing failed');
            expect(mockDocumentRepository.save).toHaveBeenCalledTimes(1);
        });
    });
    describe('validateEInvoice', () => {
        it('should validate an existing e-invoice document', async () => {
            // Arrange
            const documentId = 'doc-123';
            const tenantId = 'tenant-1';
            mockDocumentRepository.findByDocumentId.mockResolvedValue({
                id: 'doc-123',
                tenantId: 'tenant-1',
                documentId: 'doc-456',
                filename: 'test.pdf',
                content: Buffer.from('test'),
                kind: 'PDFA3',
                mimetype: 'application/pdf',
                profile: 'ZUGFeRD-EN16931',
                validationStatus: 'VALID',
                metadata: {},
                createdAt: new Date()
            });
            mockProfileRepository.findByName.mockResolvedValue({
                id: 'profile-123',
                tenantId: 'tenant-1',
                profileName: 'ZUGFeRD-EN16931',
                standard: 'ZUGFeRD',
                version: '2.1.1',
                isActive: true,
                configuration: {
                    schema: 'CII',
                    conformance: 'EN16931',
                    validation: {
                        xml: true,
                        schematron: true,
                        en16931: true
                    }
                },
                metadata: {},
                createdAt: new Date(),
                updatedAt: new Date()
            });
            mockAdapter.validateDocument.mockResolvedValue({
                valid: true,
                profile: 'ZUGFeRD-EN16931',
                schemaVersion: '2.1.1',
                errors: [],
                warnings: [],
                executionTime: 100
            });
            // Act
            const result = await service.validateEInvoice(documentId, tenantId);
            // Assert
            expect(result.valid).toBe(true);
            expect(result.profile).toBe('ZUGFeRD-EN16931');
            expect(mockDocumentRepository.findByDocumentId).toHaveBeenCalledWith(tenantId, documentId);
            expect(mockProfileRepository.findByName).toHaveBeenCalledWith(tenantId, 'ZUGFeRD-EN16931');
            expect(mockAdapter.validateDocument).toHaveBeenCalled();
        });
        it('should throw error for non-existent document', async () => {
            // Arrange
            mockDocumentRepository.findByDocumentId.mockResolvedValue(null);
            // Act & Assert
            await expect(service.validateEInvoice('non-existent', 'tenant-1'))
                .rejects.toThrow('Document non-existent not found');
        });
    });
    describe('renderPDFA3', () => {
        it('should generate PDF/A-3 with embedded XML', async () => {
            // Arrange
            const normalizedData = {
                supplier: {
                    vatId: 'DE123456789',
                    name: 'Test Supplier',
                    address: {
                        street: 'Test Street 1',
                        city: 'Test City',
                        postalCode: '12345',
                        country: 'DE'
                    }
                },
                buyer: {
                    vatId: 'DE987654321',
                    name: 'Test Buyer',
                    address: {
                        street: 'Buyer Street 1',
                        city: 'Buyer City',
                        postalCode: '67890',
                        country: 'DE'
                    }
                },
                invoice: {
                    id: 'INV-2025-001',
                    issueDate: '2025-09-28',
                    dueDate: '2025-10-28',
                    currency: 'EUR',
                    lines: [{
                            sku: 'TEST-001',
                            name: 'Test Article',
                            qty: 1,
                            price: 100.00,
                            taxPercent: 19,
                            net: 100.00,
                            tax: 19.00,
                            gross: 119.00
                        }],
                    totals: {
                        net: 100.00,
                        tax: 19.00,
                        gross: 119.00
                    },
                    payment: {
                        iban: 'DE89370400440532013000',
                        bic: 'COBADEFFXXX',
                        terms: '30 days net'
                    },
                    attachments: []
                },
                profile: 'ZUGFeRD-EN16931'
            };
            const expectedXml = '<?xml version="1.0" encoding="UTF-8"?><rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"><rsm:ExchangedDocumentContext><ram:GuidelineSpecifiedDocumentContextParameter><ram:ID>ZUGFeRD-EN16931</ram:ID></ram:GuidelineSpecifiedDocumentContextParameter></rsm:ExchangedDocumentContext><rsm:ExchangedDocument><ram:ID>INV-2025-001</ram:ID><ram:TypeCode>380</ram:TypeCode></rsm:ExchangedDocument><!-- Additional XML structure would be generated here --></rsm:CrossIndustryInvoice>';
            mockAdapter.generatePDFA3.mockResolvedValue(Buffer.from('Generated PDF content'));
            mockAdapter.embedXMLInPDF.mockResolvedValue(Buffer.from('PDF with embedded XML'));
            mockAdapter.validateDocument.mockResolvedValue({
                valid: true,
                profile: 'ZUGFeRD-EN16931',
                schemaVersion: '2.1.1',
                errors: [],
                warnings: [],
                executionTime: 200
            });
            mockDocumentRepository.save.mockResolvedValue({
                id: 'doc-123',
                tenantId: 'tenant-1',
                documentId: 'generated-123',
                filename: 'invoice-INV-2025-001.pdf',
                content: Buffer.from('PDF with embedded XML'),
                kind: 'PDFA3',
                mimetype: 'application/pdf',
                profile: 'ZUGFeRD-EN16931',
                validationStatus: 'VALID',
                metadata: {
                    generated: true,
                    xmlEmbedded: true,
                    validationErrors: 0
                },
                createdAt: new Date()
            });
            // Act
            const result = await service.renderPDFA3(normalizedData, 'tenant-1');
            // Assert
            expect(result.pdfBuffer).toBeDefined();
            expect(result.xmlContent).toBe(expectedXml);
            expect(result.documentId).toBe('generated-123');
            expect(mockAdapter.generatePDFA3).toHaveBeenCalled();
            expect(mockAdapter.embedXMLInPDF).toHaveBeenCalled();
            expect(mockAdapter.validateDocument).toHaveBeenCalled();
            expect(mockDocumentRepository.save).toHaveBeenCalled();
        });
    });
});
