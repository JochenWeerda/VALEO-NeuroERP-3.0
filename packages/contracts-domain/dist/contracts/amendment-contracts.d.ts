import { z } from 'zod';
export declare const AmendmentTypeEnum: z.ZodEnum<["QtyChange", "WindowChange", "PriceRuleChange", "CounterpartyChange", "DeliveryTermsChange", "Other"]>;
export declare const AmendmentStatusEnum: z.ZodEnum<["Pending", "Approved", "Rejected", "Cancelled"]>;
export declare const CreateAmendmentSchema: z.ZodObject<{
    type: z.ZodEnum<["QtyChange", "WindowChange", "PriceRuleChange", "CounterpartyChange", "DeliveryTermsChange", "Other"]>;
    reason: z.ZodString;
    changes: z.ZodRecord<z.ZodString, z.ZodAny>;
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    type: "QtyChange" | "WindowChange" | "PriceRuleChange" | "CounterpartyChange" | "DeliveryTermsChange" | "Other";
    reason: string;
    changes: Record<string, any>;
    notes?: string | undefined;
}, {
    type: "QtyChange" | "WindowChange" | "PriceRuleChange" | "CounterpartyChange" | "DeliveryTermsChange" | "Other";
    reason: string;
    changes: Record<string, any>;
    notes?: string | undefined;
}>;
export declare const AmendmentResponseSchema: z.ZodObject<{
    id: z.ZodString;
    contractId: z.ZodString;
    tenantId: z.ZodString;
    type: z.ZodEnum<["QtyChange", "WindowChange", "PriceRuleChange", "CounterpartyChange", "DeliveryTermsChange", "Other"]>;
    reason: z.ZodString;
    changes: z.ZodRecord<z.ZodString, z.ZodAny>;
    approvedBy: z.ZodOptional<z.ZodString>;
    approvedAt: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Pending", "Approved", "Rejected", "Cancelled"]>;
    effectiveAt: z.ZodOptional<z.ZodString>;
    notes: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    status: "Cancelled" | "Pending" | "Approved" | "Rejected";
    type: "QtyChange" | "WindowChange" | "PriceRuleChange" | "CounterpartyChange" | "DeliveryTermsChange" | "Other";
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    version: number;
    contractId: string;
    reason: string;
    changes: Record<string, any>;
    approvedBy?: string | undefined;
    approvedAt?: string | undefined;
    effectiveAt?: string | undefined;
    notes?: string | undefined;
}, {
    status: "Cancelled" | "Pending" | "Approved" | "Rejected";
    type: "QtyChange" | "WindowChange" | "PriceRuleChange" | "CounterpartyChange" | "DeliveryTermsChange" | "Other";
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    version: number;
    contractId: string;
    reason: string;
    changes: Record<string, any>;
    approvedBy?: string | undefined;
    approvedAt?: string | undefined;
    effectiveAt?: string | undefined;
    notes?: string | undefined;
}>;
export declare const ApproveAmendmentSchema: z.ZodObject<{
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    notes?: string | undefined;
}, {
    notes?: string | undefined;
}>;
export declare const RejectAmendmentSchema: z.ZodObject<{
    reason: z.ZodString;
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    reason: string;
    notes?: string | undefined;
}, {
    reason: string;
    notes?: string | undefined;
}>;
export type CreateAmendment = z.infer<typeof CreateAmendmentSchema>;
export type AmendmentResponse = z.infer<typeof AmendmentResponseSchema>;
export type ApproveAmendment = z.infer<typeof ApproveAmendmentSchema>;
export type RejectAmendment = z.infer<typeof RejectAmendmentSchema>;
//# sourceMappingURL=amendment-contracts.d.ts.map