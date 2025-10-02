import { z } from 'zod';
export declare const AccountType: z.ZodEnum<["ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE"]>;
export declare const AccountSubType: z.ZodEnum<["CASH", "RECEIVABLE", "INVENTORY", "FIXED_ASSET", "PREPAID", "PAYABLE", "ACCRUED", "LONG_TERM_DEBT", "RETAINED_EARNINGS", "COMMON_STOCK", "PREFERRED_STOCK", "SALES", "SERVICE_REVENUE", "OTHER_REVENUE", "COGS", "OPERATING_EXPENSE", "FINANCIAL_EXPENSE"]>;
export declare const Account: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    code: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    type: z.ZodEnum<["ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE"]>;
    subType: z.ZodEnum<["CASH", "RECEIVABLE", "INVENTORY", "FIXED_ASSET", "PREPAID", "PAYABLE", "ACCRUED", "LONG_TERM_DEBT", "RETAINED_EARNINGS", "COMMON_STOCK", "PREFERRED_STOCK", "SALES", "SERVICE_REVENUE", "OTHER_REVENUE", "COGS", "OPERATING_EXPENSE", "FINANCIAL_EXPENSE"]>;
    parentAccountId: z.ZodOptional<z.ZodString>;
    level: z.ZodDefault<z.ZodNumber>;
    isActive: z.ZodDefault<z.ZodBoolean>;
    allowsManualEntry: z.ZodDefault<z.ZodBoolean>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    code: string;
    type: "ASSET" | "LIABILITY" | "EQUITY" | "REVENUE" | "EXPENSE";
    name: string;
    tenantId: string;
    id: string;
    subType: "CASH" | "RECEIVABLE" | "INVENTORY" | "FIXED_ASSET" | "PREPAID" | "PAYABLE" | "ACCRUED" | "LONG_TERM_DEBT" | "RETAINED_EARNINGS" | "COMMON_STOCK" | "PREFERRED_STOCK" | "SALES" | "SERVICE_REVENUE" | "OTHER_REVENUE" | "COGS" | "OPERATING_EXPENSE" | "FINANCIAL_EXPENSE";
    level: number;
    isActive: boolean;
    allowsManualEntry: boolean;
    createdAt: string;
    updatedAt: string;
    description?: string | undefined;
    parentAccountId?: string | undefined;
}, {
    code: string;
    type: "ASSET" | "LIABILITY" | "EQUITY" | "REVENUE" | "EXPENSE";
    name: string;
    tenantId: string;
    id: string;
    subType: "CASH" | "RECEIVABLE" | "INVENTORY" | "FIXED_ASSET" | "PREPAID" | "PAYABLE" | "ACCRUED" | "LONG_TERM_DEBT" | "RETAINED_EARNINGS" | "COMMON_STOCK" | "PREFERRED_STOCK" | "SALES" | "SERVICE_REVENUE" | "OTHER_REVENUE" | "COGS" | "OPERATING_EXPENSE" | "FINANCIAL_EXPENSE";
    createdAt: string;
    updatedAt: string;
    description?: string | undefined;
    parentAccountId?: string | undefined;
    level?: number | undefined;
    isActive?: boolean | undefined;
    allowsManualEntry?: boolean | undefined;
}>;
export type Account = z.infer<typeof Account>;
export declare const JournalEntry: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    entryNumber: z.ZodString;
    description: z.ZodString;
    period: z.ZodString;
    date: z.ZodString;
    lines: z.ZodArray<z.ZodObject<{
        accountId: z.ZodString;
        debit: z.ZodOptional<z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>>;
        credit: z.ZodOptional<z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        accountId: string;
        description?: string | undefined;
        debit?: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        } | undefined;
        credit?: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        } | undefined;
    }, {
        accountId: string;
        description?: string | undefined;
        debit?: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        } | undefined;
        credit?: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        } | undefined;
    }>, "many">;
    status: z.ZodEnum<["DRAFT", "POSTED", "REVERSED"]>;
    postedAt: z.ZodOptional<z.ZodString>;
    isReconciled: z.ZodDefault<z.ZodBoolean>;
    reconciledAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodString;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "DRAFT" | "POSTED" | "REVERSED";
    tenantId: string;
    date: string;
    id: string;
    description: string;
    createdAt: string;
    updatedAt: string;
    entryNumber: string;
    period: string;
    lines: {
        accountId: string;
        description?: string | undefined;
        debit?: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        } | undefined;
        credit?: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        } | undefined;
    }[];
    isReconciled: boolean;
    createdBy: string;
    postedAt?: string | undefined;
    reconciledAt?: string | undefined;
}, {
    status: "DRAFT" | "POSTED" | "REVERSED";
    tenantId: string;
    date: string;
    id: string;
    description: string;
    createdAt: string;
    updatedAt: string;
    entryNumber: string;
    period: string;
    lines: {
        accountId: string;
        description?: string | undefined;
        debit?: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        } | undefined;
        credit?: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        } | undefined;
    }[];
    createdBy: string;
    postedAt?: string | undefined;
    isReconciled?: boolean | undefined;
    reconciledAt?: string | undefined;
}>;
export type JournalEntry = z.infer<typeof JournalEntry>;
export declare const Invoice: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    invoiceNumber: z.ZodString;
    type: z.ZodEnum<["AR", "AP"]>;
    customerId: z.ZodOptional<z.ZodString>;
    supplierId: z.ZodOptional<z.ZodString>;
    subtotal: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    taxAmount: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    total: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    taxRate: z.ZodNumber;
    taxCode: z.ZodOptional<z.ZodString>;
    issueDate: z.ZodString;
    dueDate: z.ZodString;
    paidDate: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["DRAFT", "SENT", "PAID", "OVERDUE", "CANCELLED"]>;
    lineItems: z.ZodArray<z.ZodObject<{
        description: z.ZodString;
        quantity: z.ZodNumber;
        unitPrice: z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>;
        totalPrice: z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>;
        accountId: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        description: string;
        accountId: string;
        quantity: number;
        unitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        totalPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
    }, {
        description: string;
        accountId: string;
        quantity: number;
        unitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        totalPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
    }>, "many">;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    type: "AR" | "AP";
    status: "DRAFT" | "SENT" | "PAID" | "OVERDUE" | "CANCELLED";
    tenantId: string;
    total: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    id: string;
    createdAt: string;
    updatedAt: string;
    invoiceNumber: string;
    subtotal: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    taxAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    taxRate: number;
    issueDate: string;
    dueDate: string;
    lineItems: {
        description: string;
        accountId: string;
        quantity: number;
        unitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        totalPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
    }[];
    customerId?: string | undefined;
    supplierId?: string | undefined;
    taxCode?: string | undefined;
    paidDate?: string | undefined;
}, {
    type: "AR" | "AP";
    status: "DRAFT" | "SENT" | "PAID" | "OVERDUE" | "CANCELLED";
    tenantId: string;
    total: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    id: string;
    createdAt: string;
    updatedAt: string;
    invoiceNumber: string;
    subtotal: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    taxAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    taxRate: number;
    issueDate: string;
    dueDate: string;
    lineItems: {
        description: string;
        accountId: string;
        quantity: number;
        unitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        totalPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
    }[];
    customerId?: string | undefined;
    supplierId?: string | undefined;
    taxCode?: string | undefined;
    paidDate?: string | undefined;
}>;
export type Invoice = z.infer<typeof Invoice>;
export declare const Payment: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    amount: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    method: z.ZodEnum<["CASH", "BANK_TRANSFER", "CREDIT_CARD", "CHECK", "DIRECT_DEBIT"]>;
    invoiceIds: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    bankReference: z.ZodOptional<z.ZodString>;
    externalReference: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["PENDING", "COMPLETED", "FAILED", "CANCELLED"]>;
    completedAt: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "CANCELLED" | "PENDING" | "COMPLETED" | "FAILED";
    amount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    method: "CASH" | "BANK_TRANSFER" | "CREDIT_CARD" | "CHECK" | "DIRECT_DEBIT";
    invoiceIds?: string[] | undefined;
    bankReference?: string | undefined;
    externalReference?: string | undefined;
    completedAt?: string | undefined;
}, {
    status: "CANCELLED" | "PENDING" | "COMPLETED" | "FAILED";
    amount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    method: "CASH" | "BANK_TRANSFER" | "CREDIT_CARD" | "CHECK" | "DIRECT_DEBIT";
    invoiceIds?: string[] | undefined;
    bankReference?: string | undefined;
    externalReference?: string | undefined;
    completedAt?: string | undefined;
}>;
export type Payment = z.infer<typeof Payment>;
export declare const Budget: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    period: z.ZodString;
    startDate: z.ZodString;
    endDate: z.ZodString;
    lines: z.ZodArray<z.ZodObject<{
        accountId: z.ZodString;
        budgetedAmount: z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>;
        notes: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        accountId: string;
        budgetedAmount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        notes?: string | undefined;
    }, {
        accountId: string;
        budgetedAmount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        notes?: string | undefined;
    }>, "many">;
    status: z.ZodEnum<["DRAFT", "APPROVED", "ACTIVE", "CLOSED"]>;
    approvedBy: z.ZodOptional<z.ZodString>;
    approvedAt: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "DRAFT" | "APPROVED" | "ACTIVE" | "CLOSED";
    name: string;
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    period: string;
    lines: {
        accountId: string;
        budgetedAmount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        notes?: string | undefined;
    }[];
    startDate: string;
    endDate: string;
    description?: string | undefined;
    approvedBy?: string | undefined;
    approvedAt?: string | undefined;
}, {
    status: "DRAFT" | "APPROVED" | "ACTIVE" | "CLOSED";
    name: string;
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    period: string;
    lines: {
        accountId: string;
        budgetedAmount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        notes?: string | undefined;
    }[];
    startDate: string;
    endDate: string;
    description?: string | undefined;
    approvedBy?: string | undefined;
    approvedAt?: string | undefined;
}>;
export type Budget = z.infer<typeof Budget>;
export declare const FinancialReportRequest: z.ZodObject<{
    tenantId: z.ZodString;
    reportType: z.ZodEnum<["BALANCE_SHEET", "INCOME_STATEMENT", "CASH_FLOW", "TRIAL_BALANCE"]>;
    period: z.ZodString;
    startDate: z.ZodString;
    endDate: z.ZodString;
    includeSubAccounts: z.ZodDefault<z.ZodBoolean>;
    format: z.ZodDefault<z.ZodEnum<["JSON", "PDF", "CSV"]>>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    period: string;
    startDate: string;
    endDate: string;
    reportType: "BALANCE_SHEET" | "INCOME_STATEMENT" | "CASH_FLOW" | "TRIAL_BALANCE";
    includeSubAccounts: boolean;
    format: "JSON" | "PDF" | "CSV";
}, {
    tenantId: string;
    period: string;
    startDate: string;
    endDate: string;
    reportType: "BALANCE_SHEET" | "INCOME_STATEMENT" | "CASH_FLOW" | "TRIAL_BALANCE";
    includeSubAccounts?: boolean | undefined;
    format?: "JSON" | "PDF" | "CSV" | undefined;
}>;
export type FinancialReportRequest = z.infer<typeof FinancialReportRequest>;
export declare const TaxRecord: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    taxYear: z.ZodNumber;
    taxPeriod: z.ZodString;
    taxType: z.ZodEnum<["VAT", "INCOME", "CORPORATE", "WITHHOLDING"]>;
    grossAmount: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    taxAmount: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    netAmount: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    filedAt: z.ZodOptional<z.ZodString>;
    dueDate: z.ZodString;
    status: z.ZodEnum<["PENDING", "FILED", "ACCEPTED", "REJECTED"]>;
    authority: z.ZodString;
    referenceNumber: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "PENDING" | "FILED" | "ACCEPTED" | "REJECTED";
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    taxAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    dueDate: string;
    taxYear: number;
    taxPeriod: string;
    taxType: "VAT" | "INCOME" | "CORPORATE" | "WITHHOLDING";
    grossAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    netAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    authority: string;
    filedAt?: string | undefined;
    referenceNumber?: string | undefined;
}, {
    status: "PENDING" | "FILED" | "ACCEPTED" | "REJECTED";
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    taxAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    dueDate: string;
    taxYear: number;
    taxPeriod: string;
    taxType: "VAT" | "INCOME" | "CORPORATE" | "WITHHOLDING";
    grossAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    netAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    authority: string;
    filedAt?: string | undefined;
    referenceNumber?: string | undefined;
}>;
export type TaxRecord = z.infer<typeof TaxRecord>;
//# sourceMappingURL=finance-schemas.d.ts.map