/**
 * VALEO NeuroERP 3.0 - Finance Domain - API Controller
 *
 * REST API controller for finance domain services
 * Following Clean Architecture and API-first design
 */
import express, { NextFunction, Request, Response } from 'express';
import { LedgerApplicationService } from '../../application/services/ledger-service';
import { APInvoiceApplicationService } from '../../application/services/ap-invoice-service';
import { AIBookkeeperApplicationService } from '../../application/services/ai-bookkeeper-service';
interface AuthenticatedRequest extends Request {
    user?: {
        id: string;
        tenantId: string;
        roles: string[];
    };
}
/**
 * Authentication middleware
 */
export declare function requireAuth(req: AuthenticatedRequest, res: Response, next: NextFunction): void;
/**
 * Authorization middleware for finance operations
 */
export declare function requireFinanceAccess(req: AuthenticatedRequest, res: Response, next: NextFunction): void;
/**
 * Request validation middleware
 */
export declare function validateRequest(schema: any): (req: Request, res: Response, next: NextFunction) => void;
export declare class FinanceAPIController {
    private readonly ledgerService;
    private readonly apInvoiceService;
    private readonly aiBookkeeperService;
    constructor(ledgerService: LedgerApplicationService, apInvoiceService: APInvoiceApplicationService, aiBookkeeperService: AIBookkeeperApplicationService);
    /**
     * Health check endpoint
     */
    health(req: Request, res: Response): Promise<void>;
    /**
     * Create journal endpoint
     */
    createJournal(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * Post journal endpoint
     */
    postJournal(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * Get trial balance endpoint
     */
    getTrialBalance(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * Create AP invoice endpoint
     */
    createAPInvoice(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * Approve AP invoice endpoint
     */
    approveAPInvoice(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * Process payment endpoint
     */
    processPayment(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * Get AP invoice endpoint
     */
    getAPInvoice(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * List AP invoices endpoint
     */
    listAPInvoices(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * AI booking proposal endpoint
     */
    getAIBookingProposal(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * Get overdue invoices endpoint
     */
    getOverdueInvoices(req: AuthenticatedRequest, res: Response): Promise<void>;
    /**
     * Get pending approval invoices endpoint
     */
    getPendingApprovalInvoices(req: AuthenticatedRequest, res: Response): Promise<void>;
}
export declare function createFinanceRouter(ledgerService: LedgerApplicationService, apInvoiceService: APInvoiceApplicationService, aiBookkeeperService: AIBookkeeperApplicationService): express.Router;
export declare const financeAPIPaths: {
    '/health': {
        get: {
            summary: string;
            responses: {
                200: {
                    description: string;
                };
                503: {
                    description: string;
                };
            };
        };
    };
    '/journals': {
        post: {
            summary: string;
            security: {
                bearerAuth: any[];
            }[];
            requestBody: {
                required: boolean;
                content: {
                    'application/json': {
                        schema: {
                            type: string;
                            required: string[];
                            properties: {
                                period: {
                                    type: string;
                                    example: string;
                                };
                                description: {
                                    type: string;
                                    example: string;
                                };
                                entries: {
                                    type: string;
                                    items: {
                                        type: string;
                                        properties: {
                                            accountId: {
                                                type: string;
                                            };
                                            debit: {
                                                type: string;
                                            };
                                            credit: {
                                                type: string;
                                            };
                                            description: {
                                                type: string;
                                            };
                                        };
                                    };
                                };
                                source: {
                                    type: string;
                                    properties: {
                                        type: {
                                            type: string;
                                            enum: string[];
                                        };
                                        reference: {
                                            type: string;
                                        };
                                    };
                                };
                            };
                        };
                    };
                };
            };
            responses: {
                201: {
                    description: string;
                };
                400: {
                    description: string;
                };
                401: {
                    description: string;
                };
                403: {
                    description: string;
                };
            };
        };
    };
    '/ap/invoices': {
        post: {
            summary: string;
            security: {
                bearerAuth: any[];
            }[];
            requestBody: {
                required: boolean;
                content: {
                    'application/json': {
                        schema: {
                            type: string;
                            required: string[];
                            properties: {
                                supplierId: {
                                    type: string;
                                };
                                invoiceNumber: {
                                    type: string;
                                };
                                issueDate: {
                                    type: string;
                                    format: string;
                                };
                                dueDate: {
                                    type: string;
                                    format: string;
                                };
                                currency: {
                                    type: string;
                                    example: string;
                                };
                                subtotal: {
                                    type: string;
                                };
                                taxAmount: {
                                    type: string;
                                };
                                totalAmount: {
                                    type: string;
                                };
                                lines: {
                                    type: string;
                                    items: {
                                        type: string;
                                        properties: {
                                            description: {
                                                type: string;
                                            };
                                            quantity: {
                                                type: string;
                                            };
                                            unitPrice: {
                                                type: string;
                                            };
                                            lineTotal: {
                                                type: string;
                                            };
                                            taxRate: {
                                                type: string;
                                            };
                                        };
                                    };
                                };
                            };
                        };
                    };
                };
            };
            responses: {
                201: {
                    description: string;
                };
                400: {
                    description: string;
                };
            };
        };
        get: {
            summary: string;
            security: {
                bearerAuth: any[];
            }[];
            parameters: {
                name: string;
                in: string;
                schema: {
                    type: string;
                    enum: string[];
                };
            }[];
            responses: {
                200: {
                    description: string;
                };
                401: {
                    description: string;
                };
            };
        };
    };
};
export {};
//# sourceMappingURL=finance-api-controller.d.ts.map