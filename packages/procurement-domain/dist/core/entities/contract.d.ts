export type ContractId = string & {
    readonly __brand: 'ContractId';
};
export type ContractItemId = string & {
    readonly __brand: 'ContractItemId';
};
export declare enum ContractStatus {
    DRAFT = "draft",
    PENDING_APPROVAL = "pending_approval",
    APPROVED = "approved",
    ACTIVE = "active",
    EXPIRED = "expired",
    TERMINATED = "terminated",
    RENEWED = "renewed",
    AMENDED = "amended"
}
export declare enum ContractType {
    FRAMEWORK = "framework",// Framework agreement
    MASTER = "master",// Master service agreement
    PURCHASE = "purchase",// Purchase agreement
    SERVICE = "service",// Service level agreement
    MAINTENANCE = "maintenance",// Maintenance agreement
    LICENSE = "license",// Software license
    LEASE = "lease"
}
export declare enum RenewalType {
    AUTOMATIC = "automatic",
    MANUAL = "manual",
    NEGOTIATION_REQUIRED = "negotiation_required",
    NO_RENEWAL = "no_renewal"
}
export interface ContractParty {
    partyId: string;
    partyName: string;
    partyType: 'buyer' | 'supplier' | 'partner';
    contactName: string;
    contactEmail: string;
    contactPhone?: string;
    address: {
        street: string;
        city: string;
        state: string;
        postalCode: string;
        country: string;
    };
    taxId?: string;
    registrationNumber?: string;
}
export interface ContractItem {
    id: ContractItemId;
    itemNumber: string;
    category: string;
    description: string;
    specifications: Record<string, any>;
    unitPrice: number;
    currency: string;
    uom: string;
    minimumOrderQuantity?: number;
    maximumOrderQuantity?: number;
    paymentTerms: string;
    deliveryTerms: string;
    warrantyTerms?: string;
    effectiveFrom: Date;
    effectiveTo: Date;
    autoRenewal: boolean;
    serviceLevels: Array<{
        metric: string;
        target: number;
        unit: string;
        penalty?: string;
    }>;
}
export interface ContractTerms {
    governingLaw: string;
    disputeResolution: string;
    confidentiality: boolean;
    ipRights: string;
    totalContractValue: number;
    currency: string;
    paymentSchedule: Array<{
        milestone: string;
        percentage: number;
        dueDate: Date;
        amount: number;
    }>;
    serviceLevelAgreements: Array<{
        service: string;
        metric: string;
        target: number;
        measurement: string;
        penalty: string;
        bonus?: string;
    }>;
    terminationNoticePeriod: number;
    terminationConditions: string[];
    earlyTerminationFees?: number;
    renewalType: RenewalType;
    renewalNoticePeriod: number;
    maximumRenewalTerms?: number;
    priceAdjustmentMechanism?: string;
}
export interface ContractAmendment {
    amendmentId: string;
    amendmentNumber: number;
    amendmentDate: Date;
    effectiveDate: Date;
    description: string;
    changes: Array<{
        section: string;
        changeType: 'add' | 'modify' | 'delete';
        oldValue?: any;
        newValue: any;
        reason: string;
    }>;
    approvedBy: string;
    approvedDate: Date;
    attachments: string[];
}
export interface ContractPerformance {
    period: {
        from: Date;
        to: Date;
    };
    committedValue: number;
    actualSpend: number;
    savings: number;
    savingsPercentage: number;
    ordersPlaced: number;
    ordersFulfilled: number;
    onTimeDelivery: number;
    qualityIncidents: number;
    slaCompliance: Array<{
        sla: string;
        target: number;
        actual: number;
        compliance: number;
        status: 'exceeded' | 'met' | 'below';
    }>;
    riskScore: number;
    riskFactors: string[];
    mitigationActions: string[];
}
export declare class Contract {
    readonly id: ContractId;
    contractNumber: string;
    title: string;
    description: string;
    type: ContractType;
    status: ContractStatus;
    buyer: ContractParty;
    supplier: ContractParty;
    effectiveDate: Date;
    expiryDate: Date;
    signedDate?: Date;
    items: ContractItem[];
    terms: ContractTerms;
    amendments: ContractAmendment[];
    renewalHistory: Array<{
        renewalDate: Date;
        newExpiryDate: Date;
        changes: string[];
        approvedBy: string;
    }>;
    performanceHistory: ContractPerformance[];
    readonly tenantId: string;
    department: string;
    costCenter: string;
    project?: string;
    tags: string[];
    attachments: string[];
    readonly createdAt: Date;
    updatedAt: Date;
    createdBy: string;
    lastModifiedBy: string;
    version: number;
    constructor(props: {
        id?: ContractId;
        contractNumber?: string;
        title: string;
        description: string;
        type: ContractType;
        buyer: ContractParty;
        supplier: ContractParty;
        effectiveDate: Date;
        expiryDate: Date;
        items: ContractItem[];
        terms: ContractTerms;
        tenantId: string;
        department: string;
        costCenter: string;
        createdBy: string;
        project?: string;
        tags?: string[];
        attachments?: string[];
    });
    submitForApproval(): void;
    approve(approvedBy: string): void;
    activate(): void;
    amend(amendment: Omit<ContractAmendment, 'amendmentId' | 'amendmentNumber'>): void;
    renew(newExpiryDate: Date, changes: string[], approvedBy: string): void;
    terminate(reason: string, terminatedBy: string): void;
    recordPerformance(performance: ContractPerformance): void;
    getContractValue(): {
        totalValue: number;
        currency: string;
        spentToDate: number;
        remainingValue: number;
        utilizationRate: number;
    };
    getPerformanceSummary(): {
        overallScore: number;
        slaCompliance: number;
        costSavings: number;
        deliveryPerformance: number;
        qualityScore: number;
        riskLevel: 'low' | 'medium' | 'high' | 'critical';
    };
    getExpiryStatus(): {
        daysToExpiry: number;
        isExpiringSoon: boolean;
        requiresRenewalAction: boolean;
        renewalStatus: 'not_due' | 'due_soon' | 'overdue' | 'expired';
    };
    getSpendUnderManagement(): {
        committedSpend: number;
        actualSpend: number;
        variance: number;
        variancePercentage: number;
        status: 'under_spend' | 'on_track' | 'over_spend';
    };
    validateForActivation(): {
        isValid: boolean;
        errors: string[];
        warnings: string[];
    };
    private generateContractNumber;
    updateTimestamp(): void;
}
//# sourceMappingURL=contract.d.ts.map