import { z } from 'zod';
import { Money, UUID } from './shared-schemas';

// Finance-specific schemas

// Account types
export const AccountType = z.enum([
  'ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE'
]);

export const AccountSubType = z.enum([
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
export const Account = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Account identification
  code: z.string().min(1), // e.g., "1100", "5100"
  name: z.string().min(1),
  description: z.string().optional(),

  // Account classification
  type: AccountType,
  subType: AccountSubType,

  // Hierarchy
  parentAccountId: UUID.optional(),
  level: z.number().int().min(1).max(10).default(1),

  // Status
  isActive: z.boolean().default(true),
  allowsManualEntry: z.boolean().default(true),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type Account = z.infer<typeof Account>;

// Journal entry
export const JournalEntry = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Entry identification
  entryNumber: z.string(),
  description: z.string(),

  // Accounting period
  period: z.string(), // e.g., "2024-01"
  date: z.string().datetime(),

  // Entry lines
  lines: z.array(z.object({
    accountId: UUID,
    debit: Money.optional(),
    credit: Money.optional(),
    description: z.string().optional()
  })).min(2), // At least 2 lines for double-entry

  // Status
  status: z.enum(['DRAFT', 'POSTED', 'REVERSED']),
  postedAt: z.string().datetime().optional(),

  // Reconciliation
  isReconciled: z.boolean().default(false),
  reconciledAt: z.string().datetime().optional(),

  // Metadata
  createdBy: z.string(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type JournalEntry = z.infer<typeof JournalEntry>;

// Invoice (AR/AP)
export const Invoice = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Invoice identification
  invoiceNumber: z.string(),
  type: z.enum(['AR', 'AP']), // Accounts Receivable / Accounts Payable

  // Parties
  customerId: z.string().optional(), // For AR invoices
  supplierId: z.string().optional(), // For AP invoices

  // Amounts
  subtotal: Money,
  taxAmount: Money,
  total: Money,

  // Tax details
  taxRate: z.number().nonnegative(),
  taxCode: z.string().optional(),

  // Dates
  issueDate: z.string().datetime(),
  dueDate: z.string().datetime(),
  paidDate: z.string().datetime().optional(),

  // Status
  status: z.enum(['DRAFT', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED']),

  // Line items
  lineItems: z.array(z.object({
    description: z.string(),
    quantity: z.number().positive(),
    unitPrice: Money,
    totalPrice: Money,
    accountId: UUID
  })),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type Invoice = z.infer<typeof Invoice>;

// Payment
export const Payment = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Payment details
  amount: Money,
  method: z.enum(['CASH', 'BANK_TRANSFER', 'CREDIT_CARD', 'CHECK', 'DIRECT_DEBIT']),

  // Related documents
  invoiceIds: z.array(UUID).optional(),

  // Bank details
  bankReference: z.string().optional(),
  externalReference: z.string().optional(),

  // Status
  status: z.enum(['PENDING', 'COMPLETED', 'FAILED', 'CANCELLED']),
  completedAt: z.string().datetime().optional(),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type Payment = z.infer<typeof Payment>;

// Budget
export const Budget = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Budget details
  name: z.string(),
  description: z.string().optional(),

  // Period
  period: z.string(), // e.g., "2024-Q1", "2024-01"
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),

  // Budget lines
  lines: z.array(z.object({
    accountId: UUID,
    budgetedAmount: Money,
    notes: z.string().optional()
  })),

  // Status
  status: z.enum(['DRAFT', 'APPROVED', 'ACTIVE', 'CLOSED']),
  approvedBy: z.string().optional(),
  approvedAt: z.string().datetime().optional(),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type Budget = z.infer<typeof Budget>;

// Financial report request
export const FinancialReportRequest = z.object({
  tenantId: z.string().min(1),
  reportType: z.enum(['BALANCE_SHEET', 'INCOME_STATEMENT', 'CASH_FLOW', 'TRIAL_BALANCE']),
  period: z.string(),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  includeSubAccounts: z.boolean().default(true),
  format: z.enum(['JSON', 'PDF', 'CSV']).default('JSON')
});

export type FinancialReportRequest = z.infer<typeof FinancialReportRequest>;

// Tax compliance record
export const TaxRecord = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Tax details
  taxYear: z.number().int().positive(),
  taxPeriod: z.string(), // e.g., "Q1", "MONTHLY"
  taxType: z.enum(['VAT', 'INCOME', 'CORPORATE', 'WITHHOLDING']),

  // Amounts
  grossAmount: Money,
  taxAmount: Money,
  netAmount: Money,

  // Filing details
  filedAt: z.string().datetime().optional(),
  dueDate: z.string().datetime(),
  status: z.enum(['PENDING', 'FILED', 'ACCEPTED', 'REJECTED']),

  // Authority details
  authority: z.string(),
  referenceNumber: z.string().optional(),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type TaxRecord = z.infer<typeof TaxRecord>;