/**
 * Finance Domain Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service migrated to VALEO-NeuroERP-3.0
 * Financial accounting and transaction management
 */
export type InvoiceId = string & {
    readonly __brand: 'InvoiceId';
};
export type PaymentId = string & {
    readonly __brand: 'PaymentId';
};
export type AccountId = string & {
    readonly __brand: 'AccountId';
};
export type TransactionId = string & {
    readonly __brand: 'TransactionId';
};
export interface Invoice {
    readonly id: InvoiceId;
    readonly customerId: string;
    readonly invoiceNumber: string;
    readonly issueDate: Date;
    readonly dueDate: Date;
    readonly status: 'DRAFT' | 'SENT' | 'PAID' | 'OVERDUE' | 'CANCELLED';
    readonly taxRate: number;
    readonly subtotalAmount: number;
    readonly taxAmount: number;
    readonly totalAmount: number;
    readonly currency: string;
    readonly paymentTerms: string;
    readonly lineItems: InvoiceLineItem[];
    readonly metadata: Record<string, any>;
    readonly created: Date;
}
export interface InvoiceLineItem {
    readonly id: string;
    readonly description: string;
    readonly quantity: number;
    readonly unitPrice: number;
    readonly lineTotal: number;
    readonly taxRate: number;
    readonly account?: AccountId;
}
export interface Payment {
    readonly id: PaymentId;
    readonly invoiceId: InvoiceId;
    readonly paymentDate: Date;
    readonly amount: number;
    readonly paymentMethod: 'BANK_TRANSFER' | 'CREDIT_CARD' | 'CASH' | 'CHECK';
    readonly paymentNumber: string | undefined;
    readonly bankReference?: string;
    readonly notes?: string;
    readonly status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'REFUNDED';
    readonly metadata: Record<string, any>;
    readonly created: Date;
    readonly processedAt?: Date;
}
export interface Account {
    readonly id: AccountId;
    readonly accountNumber: string;
    readonly name: string;
    readonly type: 'ASSET' | 'LIABILITY' | 'EQUITY' | 'REVENUE' | 'EXPENSE';
    readonly balance: number;
    readonly isActive: boolean;
    readonly parentAccount?: AccountId;
    readonly chartOfAccountsCode: string;
    readonly metadata: Record<string, any>;
    readonly created: Date;
}
export interface FinancialTransaction {
    readonly id: TransactionId;
    readonly date: Date;
    readonly description: string;
    readonly debitAccount: AccountId;
    readonly creditAccount: AccountId;
    readonly amount: number;
    readonly currency: string;
    readonly invoice?: InvoiceId;
    readonly payment?: PaymentId;
    readonly metadata: Record<string, any>;
    readonly created: Date;
}
export declare class FinanceDomainService {
    private readonly invoices;
    private readonly payments;
    private readonly accounts;
    private readonly transactions;
    private readonly financialMetrics;
    constructor();
    /**
     =>* Initialize Finance Service
     */
    private initializeFinanceService;
    /**
     =>* Setup Chart of Accounts nach Business Accounting Requirements
     */
    private setupChartOfAccounts;
    /**
     =>* Setup Sample Financial Data nach initial Business Scenario
     */
    private setupSampleFinancialData;
    /**
     =>* Get Invoice
     */
    getInvoice(invoiceId: InvoiceId): Promise<Invoice | undefined>;
    /**
     =>* List Invoices
     */
    listInvoices(criteriaOrNil?: {
        status?: Invoice['status'];
        customerId?: string;
        fromDate?: Date;
        upToDate?: Date;
        count?: number;
    }): Promise<Invoice[]>;
    /**
     =>* Record new Invoice
     */
    recordInvoice(invData: {
        invoiceData: Omit<Invoice, 'id' | 'created'>;
    }): Promise<InvoiceId>;
    /**
     =>* Record Payment
     */
    recordPayment(opts: {
        invoiceId: InvoiceId;
        amount: number;
        paymentDate?: Date;
        method: Payment['paymentMethod'];
        ref?: string;
    }): Promise<PaymentId>;
    /**
    =>* Financial Summary für einen Business-Zyklus
     */
    getFinancialSummary(_args: any[]): Promise<{
        revenuesTotal: number;
        liabilitiesOutstanding: number;
        assetTotal: number;
        mstEconRatio: number;
        liquidityRatio: number;
    }>;
    /**
     =>* Ensure health state
     */
    healthCheck(): Promise<boolean>;
}
/**
 * Factory function for Finance Domain Service
 */
export declare function createFinanceDomainService(): FinanceDomainService;
//# sourceMappingURL=finance-domain-service.d.ts.map