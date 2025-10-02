"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - API Controller
 *
 * REST API controller for finance domain services
 * Following Clean Architecture and API-first design
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.financeAPIPaths = exports.FinanceAPIController = void 0;
exports.requireAuth = requireAuth;
exports.requireFinanceAccess = requireFinanceAccess;
exports.validateRequest = validateRequest;
exports.createFinanceRouter = createFinanceRouter;
const express_1 = __importDefault(require("express"));
const finance_constants_1 = require("../../core/constants/finance-constants");
// ===== MIDDLEWARE =====
/**
 * Authentication middleware
 */
function requireAuth(req, res, next) {
    if (!req.user) {
        res.status(finance_constants_1.HTTP_STATUS.UNAUTHORIZED).json({
            success: false,
            error: 'Authentication required',
            timestamp: new Date().toISOString()
        });
        return;
    }
    next();
}
/**
 * Authorization middleware for finance operations
 */
function requireFinanceAccess(req, res, next) {
    if (!req.user) {
        res.status(401).json({
            success: false,
            error: 'Authentication required',
            timestamp: new Date().toISOString()
        });
        return;
    }
    const hasAccess = req.user.roles.includes('FINANCE_USER') ||
        req.user.roles.includes('FINANCE_ADMIN') ||
        req.user.roles.includes('ADMIN');
    if (!hasAccess) {
        res.status(finance_constants_1.HTTP_STATUS.FORBIDDEN).json({
            success: false,
            error: 'Insufficient permissions for finance operations',
            timestamp: new Date().toISOString()
        });
        return;
    }
    next();
}
/**
 * Request validation middleware
 */
function validateRequest(schema) {
    return (req, res, next) => {
        const { error } = schema.validate(req.body);
        if (error) {
            res.status(finance_constants_1.HTTP_STATUS.BAD_REQUEST).json({
                success: false,
                error: `Validation error: ${error.details[0].message}`,
                timestamp: new Date().toISOString()
            });
            return;
        }
        next();
    };
}
// ===== CONTROLLER CLASS =====
class FinanceAPIController {
    constructor(ledgerService, apInvoiceService, aiBookkeeperService) {
        this.ledgerService = ledgerService;
        this.apInvoiceService = apInvoiceService;
        this.aiBookkeeperService = aiBookkeeperService;
    }
    /**
     * Health check endpoint
     */
    async health(req, res) {
        res.json({
            success: true,
            data: {
                status: 'healthy',
                timestamp: new Date().toISOString(),
                services: {
                    ledger: true,
                    apInvoice: true,
                    aiBookkeeper: true
                }
            },
            timestamp: new Date().toISOString()
        });
    }
    /**
     * Create journal endpoint
     */
    async createJournal(req, res) {
        try {
            const command = {
                tenantId: req.user.tenantId,
                period: req.body.period,
                description: req.body.description,
                entries: req.body.entries,
                source: req.body.source,
                metadata: req.body.metadata
            };
            const journalId = await this.ledgerService.createJournal(command);
            res.status(finance_constants_1.HTTP_STATUS.CREATED).json({
                success: true,
                data: { journalId },
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * Post journal endpoint
     */
    async postJournal(req, res) {
        try {
            const command = {
                journalId: req.params.journalId || '',
                postedBy: req.user?.id || ''
            };
            await this.ledgerService.postJournal(command);
            res.json({
                success: true,
                data: { message: 'Journal posted successfully' },
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * Get trial balance endpoint
     */
    async getTrialBalance(req, res) {
        try {
            const trialBalance = await this.ledgerService.getTrialBalance(req.user?.tenantId || '', req.params.period || '');
            res.json({
                success: true,
                data: trialBalance,
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * Create AP invoice endpoint
     */
    async createAPInvoice(req, res) {
        try {
            const command = {
                tenantId: req.user.tenantId,
                supplierId: req.body.supplierId,
                invoiceNumber: req.body.invoiceNumber,
                issueDate: new Date(req.body.issueDate),
                dueDate: new Date(req.body.dueDate),
                currency: req.body.currency,
                subtotal: req.body.subtotal,
                taxAmount: req.body.taxAmount,
                totalAmount: req.body.totalAmount,
                taxRate: req.body.taxRate,
                paymentTerms: req.body.paymentTerms,
                lines: req.body.lines,
                documentRef: req.body.documentRef,
                ocrData: req.body.ocrData,
                metadata: req.body.metadata
            };
            const invoiceId = await this.apInvoiceService.createInvoice(command);
            res.status(201).json({
                success: true,
                data: { invoiceId },
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * Approve AP invoice endpoint
     */
    async approveAPInvoice(req, res) {
        try {
            const command = {
                invoiceId: req.params.invoiceId || '',
                approvedBy: req.user?.id || '',
                approvedEntries: req.body.approvedEntries
            };
            await this.apInvoiceService.approveInvoice(command);
            res.json({
                success: true,
                data: { message: 'Invoice approved successfully' },
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * Process payment endpoint
     */
    async processPayment(req, res) {
        try {
            const command = {
                invoiceId: req.params.invoiceId || '',
                paymentDate: new Date(req.body.paymentDate),
                paymentMethod: req.body.paymentMethod,
                paymentReference: req.body.paymentReference,
                paidBy: req.user?.id || ''
            };
            await this.apInvoiceService.processPayment(command);
            res.json({
                success: true,
                data: { message: 'Payment processed successfully' },
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(finance_constants_1.HTTP_STATUS.BAD_REQUEST).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * Get AP invoice endpoint
     */
    async getAPInvoice(req, res) {
        try {
            const invoice = await this.apInvoiceService.getInvoice(req.params.invoiceId || '');
            if (!invoice) {
                res.status(404).json({
                    success: false,
                    error: 'Invoice not found',
                    timestamp: new Date().toISOString()
                });
                return;
            }
            res.json({
                success: true,
                data: invoice,
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * List AP invoices endpoint
     */
    async listAPInvoices(req, res) {
        try {
            const status = req.query.status;
            const invoices = await this.apInvoiceService.listInvoices(req.user.tenantId, status);
            res.json({
                success: true,
                data: {
                    invoices,
                    count: invoices.length,
                    status: status || 'ALL'
                },
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * AI booking proposal endpoint
     */
    async getAIBookingProposal(req, res) {
        try {
            const invoice = await this.apInvoiceService.getInvoice(req.params.invoiceId || '');
            if (!invoice) {
                res.status(404).json({
                    success: false,
                    error: 'Invoice not found',
                    timestamp: new Date().toISOString()
                });
                return;
            }
            const proposal = await this.aiBookkeeperService.proposeBooking(invoice);
            res.json({
                success: true,
                data: proposal,
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * Get overdue invoices endpoint
     */
    async getOverdueInvoices(req, res) {
        try {
            const overdueInvoices = await this.apInvoiceService.getOverdueInvoices(req.user.tenantId);
            res.json({
                success: true,
                data: {
                    overdueInvoices,
                    count: overdueInvoices.length
                },
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
    /**
     * Get pending approval invoices endpoint
     */
    async getPendingApprovalInvoices(req, res) {
        try {
            const pendingInvoices = await this.apInvoiceService.getPendingApprovalInvoices(req.user.tenantId);
            res.json({
                success: true,
                data: {
                    pendingInvoices,
                    count: pendingInvoices.length
                },
                timestamp: new Date().toISOString()
            });
        }
        catch (error) {
            res.status(400).json({
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            });
        }
    }
}
exports.FinanceAPIController = FinanceAPIController;
// ===== ROUTER SETUP =====
function createFinanceRouter(ledgerService, apInvoiceService, aiBookkeeperService) {
    const router = express_1.default.Router();
    const controller = new FinanceAPIController(ledgerService, apInvoiceService, aiBookkeeperService);
    // Health check
    router.get('/health', controller.health.bind(controller));
    // Journal endpoints
    router.post('/journals', requireAuth, requireFinanceAccess, controller.createJournal.bind(controller));
    router.post('/journals/:journalId/post', requireAuth, requireFinanceAccess, controller.postJournal.bind(controller));
    router.get('/trial-balance/:period', requireAuth, requireFinanceAccess, controller.getTrialBalance.bind(controller));
    // AP Invoice endpoints
    router.post('/ap/invoices', requireAuth, requireFinanceAccess, controller.createAPInvoice.bind(controller));
    router.post('/ap/invoices/:invoiceId/approve', requireAuth, requireFinanceAccess, controller.approveAPInvoice.bind(controller));
    router.post('/ap/invoices/:invoiceId/payment', requireAuth, requireFinanceAccess, controller.processPayment.bind(controller));
    router.get('/ap/invoices/:invoiceId', requireAuth, requireFinanceAccess, controller.getAPInvoice.bind(controller));
    router.get('/ap/invoices', requireAuth, requireFinanceAccess, controller.listAPInvoices.bind(controller));
    router.get('/ap/overdue', requireAuth, requireFinanceAccess, controller.getOverdueInvoices.bind(controller));
    router.get('/ap/pending-approval', requireAuth, requireFinanceAccess, controller.getPendingApprovalInvoices.bind(controller));
    // AI endpoints
    router.get('/ai/booking-proposal/:invoiceId', requireAuth, requireFinanceAccess, controller.getAIBookingProposal.bind(controller));
    return router;
}
// ===== SWAGGER DOCUMENTATION =====
exports.financeAPIPaths = {
    '/health': {
        get: {
            summary: 'Health check for finance services',
            responses: {
                200: { description: 'Services are healthy' },
                503: { description: 'Services are unhealthy' }
            }
        }
    },
    '/journals': {
        post: {
            summary: 'Create a new journal',
            security: [{ bearerAuth: [] }],
            requestBody: {
                required: true,
                content: {
                    'application/json': {
                        schema: {
                            type: 'object',
                            required: ['period', 'description', 'entries', 'source'],
                            properties: {
                                period: { type: 'string', example: '2025-09' },
                                description: { type: 'string', example: 'Office supplies purchase' },
                                entries: {
                                    type: 'array',
                                    items: {
                                        type: 'object',
                                        properties: {
                                            accountId: { type: 'string' },
                                            debit: { type: 'number' },
                                            credit: { type: 'number' },
                                            description: { type: 'string' }
                                        }
                                    }
                                },
                                source: {
                                    type: 'object',
                                    properties: {
                                        type: { type: 'string', enum: ['AP', 'AR', 'BANK', 'MANUAL', 'AI'] },
                                        reference: { type: 'string' }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            responses: {
                201: { description: 'Journal created successfully' },
                400: { description: 'Invalid request data' },
                401: { description: 'Authentication required' },
                403: { description: 'Insufficient permissions' }
            }
        }
    },
    '/ap/invoices': {
        post: {
            summary: 'Create AP invoice',
            security: [{ bearerAuth: [] }],
            requestBody: {
                required: true,
                content: {
                    'application/json': {
                        schema: {
                            type: 'object',
                            required: ['supplierId', 'invoiceNumber', 'issueDate', 'dueDate', 'currency', 'subtotal', 'taxAmount', 'totalAmount', 'lines'],
                            properties: {
                                supplierId: { type: 'string' },
                                invoiceNumber: { type: 'string' },
                                issueDate: { type: 'string', format: 'date' },
                                dueDate: { type: 'string', format: 'date' },
                                currency: { type: 'string', example: 'EUR' },
                                subtotal: { type: 'number' },
                                taxAmount: { type: 'number' },
                                totalAmount: { type: 'number' },
                                lines: {
                                    type: 'array',
                                    items: {
                                        type: 'object',
                                        properties: {
                                            description: { type: 'string' },
                                            quantity: { type: 'number' },
                                            unitPrice: { type: 'number' },
                                            lineTotal: { type: 'number' },
                                            taxRate: { type: 'number' }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            responses: {
                201: { description: 'Invoice created successfully' },
                400: { description: 'Invalid request data' }
            }
        },
        get: {
            summary: 'List AP invoices',
            security: [{ bearerAuth: [] }],
            parameters: [
                {
                    name: 'status',
                    in: 'query',
                    schema: { type: 'string', enum: ['DRAFT', 'PROCESSING', 'APPROVED', 'PAID', 'CANCELLED'] }
                }
            ],
            responses: {
                200: { description: 'List of invoices' },
                401: { description: 'Authentication required' }
            }
        }
    }
};
//# sourceMappingURL=finance-api-controller.js.map