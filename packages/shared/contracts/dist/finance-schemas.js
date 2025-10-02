"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TaxRecord = exports.FinancialReportRequest = exports.Budget = exports.Payment = exports.Invoice = exports.JournalEntry = exports.Account = exports.AccountSubType = exports.AccountType = void 0;
const zod_1 = require("zod");
const shared_schemas_1 = require("./shared-schemas");
// Finance-specific schemas
// Account types
exports.AccountType = zod_1.z.enum([
    'ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE'
]);
exports.AccountSubType = zod_1.z.enum([
    // Assets
    'CASH', 'RECEIVABLE', 'INVENTORY', 'FIXED_ASSET', 'PREPAID',
    // Liabilities
    'PAYABLE', 'ACCRUED', 'LONG_TERM_DEBT',
    // Equity
    'RETAINED_EARNINGS', 'COMMON_STOCK', 'PREFERRED_STOCK',
    // Revenue
    'SALES', 'SERVICE_REVENUE', 'OTHER_REVENUE',
    // Expenses
    'COGS', 'OPERATING_EXPENSE', 'FINANCIAL_EXPENSE'
]);
// Chart of accounts entry
exports.Account = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Account identification
    code: zod_1.z.string().min(1), // e.g., "1100", "5100"
    name: zod_1.z.string().min(1),
    description: zod_1.z.string().optional(),
    // Account classification
    type: exports.AccountType,
    subType: exports.AccountSubType,
    // Hierarchy
    parentAccountId: shared_schemas_1.UUID.optional(),
    level: zod_1.z.number().int().min(1).max(10).default(1),
    // Status
    isActive: zod_1.z.boolean().default(true),
    allowsManualEntry: zod_1.z.boolean().default(true),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Journal entry
exports.JournalEntry = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Entry identification
    entryNumber: zod_1.z.string(),
    description: zod_1.z.string(),
    // Accounting period
    period: zod_1.z.string(), // e.g., "2024-01"
    date: zod_1.z.string().datetime(),
    // Entry lines
    lines: zod_1.z.array(zod_1.z.object({
        accountId: shared_schemas_1.UUID,
        debit: shared_schemas_1.Money.optional(),
        credit: shared_schemas_1.Money.optional(),
        description: zod_1.z.string().optional()
    })).min(2), // At least 2 lines for double-entry
    // Status
    status: zod_1.z.enum(['DRAFT', 'POSTED', 'REVERSED']),
    postedAt: zod_1.z.string().datetime().optional(),
    // Reconciliation
    isReconciled: zod_1.z.boolean().default(false),
    reconciledAt: zod_1.z.string().datetime().optional(),
    // Metadata
    createdBy: zod_1.z.string(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Invoice (AR/AP)
exports.Invoice = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Invoice identification
    invoiceNumber: zod_1.z.string(),
    type: zod_1.z.enum(['AR', 'AP']), // Accounts Receivable / Accounts Payable
    // Parties
    customerId: zod_1.z.string().optional(), // For AR invoices
    supplierId: zod_1.z.string().optional(), // For AP invoices
    // Amounts
    subtotal: shared_schemas_1.Money,
    taxAmount: shared_schemas_1.Money,
    total: shared_schemas_1.Money,
    // Tax details
    taxRate: zod_1.z.number().nonnegative(),
    taxCode: zod_1.z.string().optional(),
    // Dates
    issueDate: zod_1.z.string().datetime(),
    dueDate: zod_1.z.string().datetime(),
    paidDate: zod_1.z.string().datetime().optional(),
    // Status
    status: zod_1.z.enum(['DRAFT', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED']),
    // Line items
    lineItems: zod_1.z.array(zod_1.z.object({
        description: zod_1.z.string(),
        quantity: zod_1.z.number().positive(),
        unitPrice: shared_schemas_1.Money,
        totalPrice: shared_schemas_1.Money,
        accountId: shared_schemas_1.UUID
    })),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Payment
exports.Payment = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Payment details
    amount: shared_schemas_1.Money,
    method: zod_1.z.enum(['CASH', 'BANK_TRANSFER', 'CREDIT_CARD', 'CHECK', 'DIRECT_DEBIT']),
    // Related documents
    invoiceIds: zod_1.z.array(shared_schemas_1.UUID).optional(),
    // Bank details
    bankReference: zod_1.z.string().optional(),
    externalReference: zod_1.z.string().optional(),
    // Status
    status: zod_1.z.enum(['PENDING', 'COMPLETED', 'FAILED', 'CANCELLED']),
    completedAt: zod_1.z.string().datetime().optional(),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Budget
exports.Budget = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Budget details
    name: zod_1.z.string(),
    description: zod_1.z.string().optional(),
    // Period
    period: zod_1.z.string(), // e.g., "2024-Q1", "2024-01"
    startDate: zod_1.z.string().datetime(),
    endDate: zod_1.z.string().datetime(),
    // Budget lines
    lines: zod_1.z.array(zod_1.z.object({
        accountId: shared_schemas_1.UUID,
        budgetedAmount: shared_schemas_1.Money,
        notes: zod_1.z.string().optional()
    })),
    // Status
    status: zod_1.z.enum(['DRAFT', 'APPROVED', 'ACTIVE', 'CLOSED']),
    approvedBy: zod_1.z.string().optional(),
    approvedAt: zod_1.z.string().datetime().optional(),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Financial report request
exports.FinancialReportRequest = zod_1.z.object({
    tenantId: zod_1.z.string().min(1),
    reportType: zod_1.z.enum(['BALANCE_SHEET', 'INCOME_STATEMENT', 'CASH_FLOW', 'TRIAL_BALANCE']),
    period: zod_1.z.string(),
    startDate: zod_1.z.string().datetime(),
    endDate: zod_1.z.string().datetime(),
    includeSubAccounts: zod_1.z.boolean().default(true),
    format: zod_1.z.enum(['JSON', 'PDF', 'CSV']).default('JSON')
});
// Tax compliance record
exports.TaxRecord = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Tax details
    taxYear: zod_1.z.number().int().positive(),
    taxPeriod: zod_1.z.string(), // e.g., "Q1", "MONTHLY"
    taxType: zod_1.z.enum(['VAT', 'INCOME', 'CORPORATE', 'WITHHOLDING']),
    // Amounts
    grossAmount: shared_schemas_1.Money,
    taxAmount: shared_schemas_1.Money,
    netAmount: shared_schemas_1.Money,
    // Filing details
    filedAt: zod_1.z.string().datetime().optional(),
    dueDate: zod_1.z.string().datetime(),
    status: zod_1.z.enum(['PENDING', 'FILED', 'ACCEPTED', 'REJECTED']),
    // Authority details
    authority: zod_1.z.string(),
    referenceNumber: zod_1.z.string().optional(),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
//# sourceMappingURL=finance-schemas.js.map