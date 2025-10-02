export type SupplierId = string & {
    readonly __brand: 'SupplierId';
};
export type SupplierContactId = string & {
    readonly __brand: 'SupplierContactId';
};
export declare enum SupplierStatus {
    DRAFT = "draft",
    ONBOARDING = "onboarding",
    ACTIVE = "active",
    SUSPENDED = "suspended",
    DEACTIVATED = "deactivated"
}
export declare enum SupplierType {
    INDIVIDUAL = "individual",
    COMPANY = "company",
    PARTNERSHIP = "partnership",
    CORPORATION = "corporation"
}
export declare enum SupplierCategory {
    STRATEGIC = "strategic",
    PREFERRED = "preferred",
    APPROVED = "approved",
    PROSPECTIVE = "prospective"
}
export interface SupplierContact {
    id: SupplierContactId;
    supplierId: SupplierId;
    firstName: string;
    lastName: string;
    email: string;
    phone?: string;
    mobile?: string;
    role: string;
    isPrimary: boolean;
    department?: string;
    createdAt: Date;
    updatedAt: Date;
}
export interface SupplierBankAccount {
    id: string;
    supplierId: SupplierId;
    bankName: string;
    accountHolder: string;
    iban: string;
    bic?: string;
    currency: string;
    isPrimary: boolean;
    verified: boolean;
    createdAt: Date;
}
export interface SupplierAddress {
    id: string;
    supplierId: SupplierId;
    type: 'billing' | 'shipping' | 'legal';
    street: string;
    city: string;
    postalCode: string;
    country: string;
    region?: string;
    isPrimary: boolean;
    createdAt: Date;
    updatedAt: Date;
}
export interface SupplierClassification {
    id: string;
    supplierId: SupplierId;
    category: SupplierCategory;
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    industryCode?: string;
    sizeCategory: 'micro' | 'small' | 'medium' | 'large' | 'enterprise';
    certifications: string[];
    complianceFlags: string[];
    createdAt: Date;
    updatedAt: Date;
}
export declare class Supplier {
    readonly id: SupplierId;
    name: string;
    legalName: string | undefined;
    type: SupplierType;
    status: SupplierStatus;
    category: SupplierCategory;
    vatId: string | undefined;
    taxId: string | undefined;
    dunsNumber: string | undefined;
    registrationNumber: string | undefined;
    country: string;
    email: string | undefined;
    phone: string | undefined;
    website: string | undefined;
    industry: string | undefined;
    description: string | undefined;
    paymentTerms: string | undefined;
    currency: string;
    tenantId: string;
    createdBy: string;
    approvedBy?: string;
    approvedAt?: Date;
    readonly createdAt: Date;
    updatedAt: Date;
    contacts: SupplierContact[];
    addresses: SupplierAddress[];
    bankAccounts: SupplierBankAccount[];
    classifications: SupplierClassification[];
    constructor(props: {
        id?: SupplierId;
        name: string;
        legalName?: string;
        type: SupplierType;
        status?: SupplierStatus;
        category?: SupplierCategory;
        vatId?: string;
        taxId?: string;
        dunsNumber?: string;
        registrationNumber?: string;
        country: string;
        email?: string;
        phone?: string;
        website?: string;
        industry?: string;
        description?: string;
        paymentTerms?: string;
        currency?: string;
        tenantId: string;
        createdBy: string;
    });
    activate(approvedBy: string): void;
    suspend(reason: string): void;
    reactivate(): void;
    deactivate(): void;
    updateCategory(category: SupplierCategory): void;
    addContact(contact: Omit<SupplierContact, 'id' | 'supplierId' | 'createdAt' | 'updatedAt'>): SupplierContact;
    removeContact(contactId: SupplierContactId): boolean;
    addAddress(address: Omit<SupplierAddress, 'id' | 'supplierId' | 'createdAt' | 'updatedAt'>): SupplierAddress;
    addBankAccount(account: Omit<SupplierBankAccount, 'id' | 'supplierId' | 'createdAt'>): SupplierBankAccount;
    validateForActivation(): {
        isValid: boolean;
        errors: string[];
    };
    getPrimaryContact(): SupplierContact | undefined;
    getPrimaryAddress(type?: 'billing' | 'shipping' | 'legal'): SupplierAddress | undefined;
    getPrimaryBankAccount(): SupplierBankAccount | undefined;
    updateTimestamp(): void;
}
//# sourceMappingURL=supplier.d.ts.map