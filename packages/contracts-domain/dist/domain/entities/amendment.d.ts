import { z } from 'zod';
export declare const AmendmentType: {
    readonly QTY_CHANGE: "QtyChange";
    readonly WINDOW_CHANGE: "WindowChange";
    readonly PRICE_RULE_CHANGE: "PriceRuleChange";
    readonly COUNTERPARTY_CHANGE: "CounterpartyChange";
    readonly DELIVERY_TERMS_CHANGE: "DeliveryTermsChange";
    readonly OTHER: "Other";
};
export declare const AmendmentStatus: {
    readonly PENDING: "Pending";
    readonly APPROVED: "Approved";
    readonly REJECTED: "Rejected";
    readonly CANCELLED: "Cancelled";
};
export type AmendmentTypeValue = typeof AmendmentType[keyof typeof AmendmentType];
export type AmendmentStatusValue = typeof AmendmentStatus[keyof typeof AmendmentStatus];
export declare const AmendmentSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    contractId: z.ZodString;
    tenantId: z.ZodString;
    type: z.ZodEnum<["QtyChange", "WindowChange", "PriceRuleChange", "CounterpartyChange", "DeliveryTermsChange", "Other"]>;
    reason: z.ZodString;
    changes: z.ZodRecord<z.ZodString, z.ZodAny>;
    approvedBy: z.ZodOptional<z.ZodString>;
    approvedAt: z.ZodOptional<z.ZodString>;
    status: z.ZodDefault<z.ZodEnum<["Pending", "Approved", "Rejected", "Cancelled"]>>;
    effectiveAt: z.ZodOptional<z.ZodString>;
    notes: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodOptional<z.ZodDate>;
    updatedAt: z.ZodOptional<z.ZodDate>;
    version: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    status: "Cancelled" | "Pending" | "Approved" | "Rejected";
    type: "QtyChange" | "WindowChange" | "PriceRuleChange" | "CounterpartyChange" | "DeliveryTermsChange" | "Other";
    tenantId: string;
    version: number;
    contractId: string;
    reason: string;
    changes: Record<string, any>;
    id?: string | undefined;
    createdAt?: Date | undefined;
    updatedAt?: Date | undefined;
    approvedBy?: string | undefined;
    approvedAt?: string | undefined;
    effectiveAt?: string | undefined;
    notes?: string | undefined;
}, {
    type: "QtyChange" | "WindowChange" | "PriceRuleChange" | "CounterpartyChange" | "DeliveryTermsChange" | "Other";
    tenantId: string;
    contractId: string;
    reason: string;
    changes: Record<string, any>;
    status?: "Cancelled" | "Pending" | "Approved" | "Rejected" | undefined;
    id?: string | undefined;
    createdAt?: Date | undefined;
    updatedAt?: Date | undefined;
    version?: number | undefined;
    approvedBy?: string | undefined;
    approvedAt?: string | undefined;
    effectiveAt?: string | undefined;
    notes?: string | undefined;
}>;
export interface AmendmentEntity {
    id: string;
    contractId: string;
    tenantId: string;
    type: AmendmentTypeValue;
    reason: string;
    changes: Record<string, any>;
    approvedBy?: string | undefined;
    approvedAt?: Date | undefined;
    status: AmendmentStatusValue;
    effectiveAt?: Date | undefined;
    notes?: string | undefined;
    createdAt: Date;
    updatedAt: Date;
    version: number;
}
export declare class Amendment implements AmendmentEntity {
    id: string;
    contractId: string;
    tenantId: string;
    type: AmendmentTypeValue;
    reason: string;
    changes: Record<string, any>;
    approvedBy?: string;
    approvedAt?: Date;
    status: AmendmentStatusValue;
    effectiveAt?: Date;
    notes?: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    constructor(props: AmendmentEntity);
    approve(approvedBy: string): void;
    reject(): void;
    cancel(): void;
    canBeModified(): boolean;
    isEffective(): boolean;
}
//# sourceMappingURL=amendment.d.ts.map