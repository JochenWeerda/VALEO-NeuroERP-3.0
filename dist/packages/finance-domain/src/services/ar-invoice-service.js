"use strict";
/**
 * VALEO NeuroERP 3.0 - AR Invoice Service
 *
 * Application service for Accounts Receivable (AR) invoice management
 * Handles outgoing invoices, dunning process, and payment tracking
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ArInvoiceApplicationService = void 0;
const ar_invoice_1 = require("../core/entities/ar-invoice");
const ok = (value) => ({
    isSuccess: true,
    isFailure: false,
    getValue: () => value
});
const err = (error) => ({
    isSuccess: false,
    isFailure: true,
    getValue: () => { throw new Error(error); },
    error
});
// Import ZUGFeRD types
const zugferd_adapter_service_1 = require("./zugferd-adapter-service");
// ===== SERVICE =====
class ArInvoiceApplicationService {
    arInvoiceRepo;
    customerRepo;
    eventPublisher;
    clock;
    constructor(arInvoiceRepo, customerRepo, eventPublisher, clock) {
        this.arInvoiceRepo = arInvoiceRepo;
        this.customerRepo = customerRepo;
        this.eventPublisher = eventPublisher;
        this.clock = clock;
    }
    /**
     * Create a new AR invoice
     */
    async createInvoice(command) {
        // Validate customer exists
        const customer = await this.customerRepo.findById(command.customerId);
        if (!customer) {
            throw new Error(`Customer ${command.customerId} not found`);
        }
        // Create invoice entity
        const result = ar_invoice_1.ArInvoiceEntity.create(command);
        if (result.isFailure) {
            throw new Error(result.error);
        }
        const invoice = result.getValue();
        // Save to repository
        await this.arInvoiceRepo.save(invoice);
        // Publish event
        await this.eventPublisher.publish(new ar_invoice_1.ArInvoiceCreatedEvent(invoice));
        return invoice.id;
    }
    /**
     * Update an existing AR invoice
     */
    async updateInvoice(command) {
        const invoice = await this.arInvoiceRepo.findById(command.id);
        if (!invoice) {
            throw new Error(`Invoice ${command.id} not found`);
        }
        const entity = invoice;
        const result = entity.update(command);
        if (result.isFailure) {
            throw new Error(result.error);
        }
        await this.arInvoiceRepo.save(entity);
    }
    /**
     * Issue an AR invoice (change status from DRAFT to ISSUED)
     */
    async issueInvoice(invoiceId, issuedBy) {
        const invoice = await this.arInvoiceRepo.findById(invoiceId);
        if (!invoice) {
            throw new Error(`Invoice ${invoiceId} not found`);
        }
        const entity = invoice;
        const result = entity.issue();
        if (result.isFailure) {
            throw new Error(result.error);
        }
        await this.arInvoiceRepo.save(entity);
        await this.eventPublisher.publish(new ar_invoice_1.ArInvoiceIssuedEvent(entity));
    }
    /**
     * Send an AR invoice (change status from ISSUED to SENT)
     */
    async sendInvoice(invoiceId, sentBy) {
        const invoice = await this.arInvoiceRepo.findById(invoiceId);
        if (!invoice) {
            throw new Error(`Invoice ${invoiceId} not found`);
        }
        const entity = invoice;
        const result = entity.send();
        if (result.isFailure) {
            throw new Error(result.error);
        }
        await this.arInvoiceRepo.save(entity);
    }
    /**
     * Record a payment against an AR invoice
     */
    async recordPayment(command) {
        const invoice = await this.arInvoiceRepo.findById(command.id);
        if (!invoice) {
            throw new Error(`Invoice ${command.id} not found`);
        }
        const entity = invoice;
        const result = entity.recordPayment(command);
        if (result.isFailure) {
            throw new Error(result.error);
        }
        await this.arInvoiceRepo.save(entity);
        await this.eventPublisher.publish(new ar_invoice_1.ArInvoicePaymentReceivedEvent(entity, {
            amount: command.amount,
            paymentDate: command.paymentDate,
            paymentMethod: command.paymentMethod,
            ...(command.reference && { reference: command.reference })
        }));
    }
    /**
     * Process dunning for overdue invoices
     */
    async processDunning(command) {
        let invoices;
        if (command.invoiceIds && command.invoiceIds.length > 0) {
            // Process specific invoices
            invoices = [];
            for (const id of command.invoiceIds) {
                const invoice = await this.arInvoiceRepo.findById(id);
                if (invoice) {
                    invoices.push(invoice);
                }
            }
        }
        else if (command.customerId) {
            // Process all invoices for a customer
            invoices = await this.arInvoiceRepo.findByCustomer(command.customerId);
        }
        else {
            // Process all overdue invoices for tenant
            invoices = await this.arInvoiceRepo.findOverdue(command.tenantId);
        }
        // Filter to overdue invoices only
        const overdueInvoices = invoices.filter(inv => inv.isOverdue());
        for (const invoice of overdueInvoices) {
            const entity = invoice;
            const result = entity.processDunning(command.processedBy);
            if (result.isFailure) {
                console.warn(`Failed to process dunning for invoice ${invoice.id}: ${result.error}`);
                continue;
            }
            await this.arInvoiceRepo.save(entity);
            // Publish dunning event
            await this.eventPublisher.publish(new ar_invoice_1.DunningProcessedEvent(entity, entity.dunningLevel, command.processedBy));
            // Check if invoice became overdue and publish overdue event
            if (invoice.status === 'OVERDUE') {
                const daysOverdue = entity.getDaysOverdue();
                await this.eventPublisher.publish(new ar_invoice_1.ArInvoiceOverdueEvent(entity, daysOverdue));
            }
        }
    }
    /**
     * Cancel an AR invoice
     */
    async cancelInvoice(invoiceId, reason, cancelledBy) {
        const invoice = await this.arInvoiceRepo.findById(invoiceId);
        if (!invoice) {
            throw new Error(`Invoice ${invoiceId} not found`);
        }
        const entity = invoice;
        const result = entity.cancel(reason);
        if (result.isFailure) {
            throw new Error(result.error);
        }
        await this.arInvoiceRepo.save(entity);
    }
    /**
     * Get AR invoice by ID
     */
    async getInvoice(id) {
        return await this.arInvoiceRepo.findById(id);
    }
    /**
     * Get all invoices for a customer
     */
    async getInvoicesByCustomer(customerId) {
        return await this.arInvoiceRepo.findByCustomer(customerId);
    }
    /**
     * Get all invoices for a tenant
     */
    async getInvoicesByTenant(tenantId) {
        return await this.arInvoiceRepo.findByTenant(tenantId);
    }
    /**
     * Get overdue invoices for a tenant
     */
    async getOverdueInvoices(tenantId) {
        return await this.arInvoiceRepo.findOverdue(tenantId);
    }
    /**
     * Get open items (outstanding receivables) for a tenant
     */
    async getOpenItems(tenantId) {
        const invoices = await this.arInvoiceRepo.findByTenant(tenantId);
        return invoices.filter(inv => inv.outstandingAmount > 0 && inv.status !== 'CANCELLED');
    }
    /**
     * Get dunning candidates for a tenant
     */
    async getDunningCandidates(tenantId, dunningLevel) {
        if (dunningLevel !== undefined) {
            return await this.arInvoiceRepo.findByDunningLevel(tenantId, dunningLevel);
        }
        const overdueInvoices = await this.arInvoiceRepo.findOverdue(tenantId);
        return overdueInvoices.filter(inv => {
            const nextDunningDate = inv.nextDunningDate;
            return nextDunningDate ? nextDunningDate <= this.clock.now() : true;
        });
    }
    /**
     * Calculate total outstanding amount for a tenant
     */
    async getTotalOutstanding(tenantId) {
        const openItems = await this.getOpenItems(tenantId);
        return openItems.reduce((total, invoice) => total + invoice.outstandingAmount, 0);
    }
    /**
     * Export AR invoice as XRechnung XML
     */
    async exportXRechnung(invoiceId) {
        const invoice = await this.arInvoiceRepo.findById(invoiceId);
        if (!invoice) {
            return err(`Invoice ${invoiceId} not found`);
        }
        if (invoice.status === 'DRAFT') {
            return err('Cannot export draft invoices');
        }
        // Convert AR invoice to XRechnung format
        const xRechnungXml = await this.generateXRechnungXml(invoice);
        // Publish event
        await this.eventPublisher.publish({
            type: 'finance.ar.xrechnung.exported',
            invoiceId,
            tenantId: invoice.tenantId,
            format: 'XRECHNUNG',
            schemaVersion: '2.x'
        });
        return ok(Buffer.from(xRechnungXml, 'utf-8'));
    }
    /**
     * Export AR invoice as PEPPOL envelope
     */
    async exportPEPPOL(invoiceId) {
        const invoice = await this.arInvoiceRepo.findById(invoiceId);
        if (!invoice) {
            return err(`Invoice ${invoiceId} not found`);
        }
        if (invoice.status === 'DRAFT') {
            return err('Cannot export draft invoices');
        }
        // Generate XRechnung XML first
        const xRechnungResult = await this.exportXRechnung(invoiceId);
        if (xRechnungResult.isFailure) {
            return err(xRechnungResult.error || 'XRechnung export failed');
        }
        // Wrap in PEPPOL envelope
        const peppolEnvelope = await this.generatePEPPOL(xRechnungResult.getValue(), invoice);
        // Publish event
        await this.eventPublisher.publish({
            type: 'finance.ar.peppol.exported',
            invoiceId,
            tenantId: invoice.tenantId,
            format: 'PEPPOL',
            schemaVersion: '3.0'
        });
        return ok(Buffer.from(peppolEnvelope, 'utf-8'));
    }
    /**
     * Export AR invoice as ZUGFeRD PDF/A-3
     */
    async exportZUGFeRD(invoiceId) {
        const invoice = await this.arInvoiceRepo.findById(invoiceId);
        if (!invoice) {
            return err(`Invoice ${invoiceId} not found`);
        }
        if (invoice.status === 'DRAFT') {
            return err('Cannot export draft invoices');
        }
        // Convert to normalized format for ZUGFeRD
        const normalizedInvoice = await this.convertToNormalizedFormat(invoice);
        // Generate PDF/A-3 with embedded XML
        const zugferdService = new zugferd_adapter_service_1.ZUGFeRDAdapterService(new zugferd_adapter_service_1.MockZUGFeRDAdapter(), {
            store: async (doc) => `ref-${Date.now()}`,
            retrieve: async (ref) => null,
            delete: async (ref) => { }
        }, { publish: async (event) => { } });
        const result = await zugferdService.renderPDFA3(normalizedInvoice);
        if (result.isSuccess) {
            await this.eventPublisher.publish({
                type: 'finance.ar.zugferd.exported',
                invoiceId,
                tenantId: invoice.tenantId,
                format: 'ZUGFeRD',
                profile: 'EN16931'
            });
        }
        return result;
    }
    /**
     * Format date to YYYY-MM-DD string
     */
    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    /**
     * Generate XRechnung XML from AR invoice
     */
    async generateXRechnungXml(invoice) {
        // XRechnung XML generation (UBL/CII format)
        const xrechnung = {
            'rsm:CrossIndustryInvoice': {
                $: {
                    'xmlns:rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
                    'xmlns:ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
                    'xmlns:udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100'
                },
                'rsm:ExchangedDocumentContext': {
                    'ram:GuidelineSpecifiedDocumentContextParameter': {
                        'ram:ID': 'urn:cen.eu:en16931:2017'
                    }
                },
                'rsm:ExchangedDocument': {
                    'ram:ID': invoice.invoiceNumber,
                    'ram:TypeCode': '380',
                    'ram:IssueDateTime': {
                        'udt:DateTimeString': invoice.issueDate.toISOString()
                    }
                },
                'rsm:SupplyChainTradeTransaction': {
                    'ram:IncludedSupplyChainTradeLineItem': invoice.lines.map((line, index) => ({
                        'ram:AssociatedDocumentLineDocument': {
                            'ram:LineID': line.id
                        },
                        'ram:SpecifiedTradeProduct': {
                            'ram:Name': line.description
                        },
                        'ram:SpecifiedLineTradeAgreement': {
                            'ram:GrossPriceProductTradePrice': {
                                'ram:ChargeAmount': {
                                    'ram:Amount': line.unitPrice,
                                    'ram:currencyID': invoice.currency
                                }
                            }
                        },
                        'ram:SpecifiedLineTradeDelivery': {
                            'ram:BilledQuantity': {
                                'ram:Amount': line.quantity,
                                'ram:unitCode': 'H87'
                            }
                        },
                        'ram:SpecifiedLineTradeSettlement': {
                            'ram:ApplicableTradeTax': {
                                'ram:TypeCode': 'VAT',
                                'ram:CategoryCode': line.taxCode,
                                'ram:RateApplicablePercent': line.taxRate
                            },
                            'ram:SpecifiedTradeSettlementLineMonetarySummation': {
                                'ram:LineTotalAmount': {
                                    'ram:Amount': line.total,
                                    'ram:currencyID': invoice.currency
                                }
                            }
                        }
                    })),
                    'ram:ApplicableHeaderTradeAgreement': {
                        'ram:SellerTradeParty': {
                            'ram:Name': 'VALEO NeuroERP Seller',
                            'ram:SpecifiedLegalOrganization': {
                                'ram:ID': 'DE123456789'
                            }
                        },
                        'ram:BuyerTradeParty': {
                            'ram:Name': 'Customer',
                            'ram:SpecifiedLegalOrganization': {
                                'ram:ID': 'DE987654321'
                            }
                        }
                    },
                    'ram:ApplicableHeaderTradeDelivery': {},
                    'ram:ApplicableHeaderTradeSettlement': {
                        'ram:ApplicableTradeTax': {
                            'ram:CalculatedAmount': {
                                'ram:Amount': invoice.taxAmount,
                                'ram:currencyID': invoice.currency
                            },
                            'ram:TypeCode': 'VAT',
                            'ram:BasisAmount': {
                                'ram:Amount': invoice.subtotal,
                                'ram:currencyID': invoice.currency
                            },
                            'ram:CategoryCode': 'S',
                            'ram:RateApplicablePercent': '19.00'
                        },
                        'ram:SpecifiedTradeSettlementHeaderMonetarySummation': {
                            'ram:LineTotalAmount': {
                                'ram:Amount': invoice.subtotal,
                                'ram:currencyID': invoice.currency
                            },
                            'ram:ChargeTotalAmount': '0.00',
                            'ram:AllowanceTotalAmount': '0.00',
                            'ram:TaxBasisTotalAmount': {
                                'ram:Amount': invoice.subtotal,
                                'ram:currencyID': invoice.currency
                            },
                            'ram:TaxTotalAmount': {
                                'ram:Amount': invoice.taxAmount,
                                'ram:currencyID': invoice.currency
                            },
                            'ram:GrandTotalAmount': {
                                'ram:Amount': invoice.total,
                                'ram:currencyID': invoice.currency
                            }
                        }
                    }
                }
            }
        };
        // Convert to XML string (simplified)
        return `<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100">
  <rsm:ExchangedDocument>
    <ram:ID>${invoice.invoiceNumber}</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    <ram:ApplicableHeaderTradeSettlement>
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:GrandTotalAmount currencyID="${invoice.currency}">${invoice.total}</ram:GrandTotalAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>`;
    }
    /**
     * Generate PEPPOL envelope
     */
    async generatePEPPOL(xmlContent, invoice) {
        // PEPPOL envelope structure
        return `<?xml version="1.0" encoding="UTF-8"?>
<StandardBusinessDocumentHeader>
  <HeaderVersion>1.0</HeaderVersion>
  <Sender>
    <Identifier Authority="iso6523-actorid-upis">DE123456789</Identifier>
  </Sender>
  <Receiver>
    <Identifier Authority="iso6523-actorid-upis">DE987654321</Identifier>
  </Receiver>
  <DocumentIdentification>
    <Standard>urn:cen.eu:en16931:2017</Standard>
    <TypeVersion>2.1</TypeVersion>
    <InstanceIdentifier>${invoice.invoiceNumber}</InstanceIdentifier>
    <Type>Invoice</Type>
    <CreationDateAndTime>${new Date().toISOString()}</CreationDateAndTime>
  </DocumentIdentification>
</StandardBusinessDocumentHeader>`;
    }
    /**
     * Convert AR invoice to normalized format for ZUGFeRD
     */
    async convertToNormalizedFormat(invoice) {
        return {
            supplier: {
                vatId: 'DE123456789',
                name: 'VALEO NeuroERP GmbH',
                address: {
                    street: 'NeuroERP Straße 1',
                    city: 'Berlin',
                    postalCode: '10115',
                    country: 'DE'
                }
            },
            buyer: {
                vatId: 'DE987654321',
                name: 'Customer AG',
                address: {
                    street: 'Customer Weg 1',
                    city: 'Hamburg',
                    postalCode: '20095',
                    country: 'DE'
                }
            },
            invoice: {
                id: invoice.invoiceNumber,
                issueDate: this.formatDate(invoice.issueDate),
                dueDate: this.formatDate(invoice.dueDate),
                currency: invoice.currency,
                lines: invoice.lines.map(line => ({
                    id: line.id,
                    name: line.description,
                    quantity: line.quantity,
                    unitPrice: line.unitPrice,
                    taxPercent: line.taxRate,
                    taxCode: line.taxCode,
                    net: line.total,
                    tax: line.total * (line.taxRate / 100),
                    gross: line.total * (1 + line.taxRate / 100)
                })),
                totals: {
                    net: invoice.subtotal,
                    tax: invoice.taxAmount,
                    gross: invoice.total
                },
                payment: {
                    terms: invoice.paymentTerms
                },
                profile: 'ZUGFeRD-EN16931',
                attachments: []
            }
        };
    }
    /**
     * Get aging report for a tenant
     */
    async getAgingReport(tenantId) {
        const openItems = await this.getOpenItems(tenantId);
        const now = this.clock.now();
        return openItems.reduce((aging, invoice) => {
            const daysOverdue = Math.floor((now.getTime() - invoice.dueDate.getTime()) / (1000 * 60 * 60 * 24));
            if (daysOverdue <= 0) {
                aging.current += invoice.outstandingAmount;
            }
            else if (daysOverdue <= 30) {
                aging.thirtyDays += invoice.outstandingAmount;
            }
            else if (daysOverdue <= 60) {
                aging.sixtyDays += invoice.outstandingAmount;
            }
            else if (daysOverdue <= 90) {
                aging.ninetyDays += invoice.outstandingAmount;
            }
            else {
                aging.older += invoice.outstandingAmount;
            }
            return aging;
        }, {
            current: 0,
            thirtyDays: 0,
            sixtyDays: 0,
            ninetyDays: 0,
            older: 0
        });
    }
}
exports.ArInvoiceApplicationService = ArInvoiceApplicationService;
