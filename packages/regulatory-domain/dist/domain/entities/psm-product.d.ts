import { z } from 'zod';
export declare const PSMApprovalStatusEnum: z.ZodEnum<["Approved", "Expired", "Withdrawn", "Restricted", "Pending", "Unknown"]>;
export type PSMApprovalStatus = z.infer<typeof PSMApprovalStatusEnum>;
export declare const PSMProductRefSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    bvlId: z.ZodOptional<z.ZodString>;
    name: z.ZodString;
    activeSubstances: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    approvalStatus: z.ZodDefault<z.ZodEnum<["Approved", "Expired", "Withdrawn", "Restricted", "Pending", "Unknown"]>>;
    approvalValidTo: z.ZodOptional<z.ZodString>;
    approvalNumber: z.ZodOptional<z.ZodString>;
    usageScope: z.ZodOptional<z.ZodString>;
    restrictions: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    lastCheckedAt: z.ZodOptional<z.ZodString>;
    lastCheckedBy: z.ZodOptional<z.ZodString>;
    sourceUrl: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    name: string;
    activeSubstances: string[];
    approvalStatus: "Expired" | "Pending" | "Approved" | "Withdrawn" | "Restricted" | "Unknown";
    id?: string | undefined;
    createdAt?: string | undefined;
    updatedAt?: string | undefined;
    bvlId?: string | undefined;
    approvalValidTo?: string | undefined;
    approvalNumber?: string | undefined;
    usageScope?: string | undefined;
    restrictions?: string[] | undefined;
    lastCheckedAt?: string | undefined;
    lastCheckedBy?: string | undefined;
    sourceUrl?: string | undefined;
}, {
    tenantId: string;
    name: string;
    id?: string | undefined;
    createdAt?: string | undefined;
    updatedAt?: string | undefined;
    bvlId?: string | undefined;
    activeSubstances?: string[] | undefined;
    approvalStatus?: "Expired" | "Pending" | "Approved" | "Withdrawn" | "Restricted" | "Unknown" | undefined;
    approvalValidTo?: string | undefined;
    approvalNumber?: string | undefined;
    usageScope?: string | undefined;
    restrictions?: string[] | undefined;
    lastCheckedAt?: string | undefined;
    lastCheckedBy?: string | undefined;
    sourceUrl?: string | undefined;
}>;
export type PSMProductRef = z.infer<typeof PSMProductRefSchema>;
export declare const PSMCheckInputSchema: z.ZodObject<{
    items: z.ZodArray<z.ZodObject<{
        name: z.ZodString;
        bvlId: z.ZodOptional<z.ZodString>;
        useDate: z.ZodString;
        cropOrUseCase: z.ZodOptional<z.ZodString>;
        quantity: z.ZodOptional<z.ZodNumber>;
        unit: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        name: string;
        useDate: string;
        bvlId?: string | undefined;
        cropOrUseCase?: string | undefined;
        quantity?: number | undefined;
        unit?: string | undefined;
    }, {
        name: string;
        useDate: string;
        bvlId?: string | undefined;
        cropOrUseCase?: string | undefined;
        quantity?: number | undefined;
        unit?: string | undefined;
    }>, "many">;
    batchId: z.ZodOptional<z.ZodString>;
    contractId: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    items: {
        name: string;
        useDate: string;
        bvlId?: string | undefined;
        cropOrUseCase?: string | undefined;
        quantity?: number | undefined;
        unit?: string | undefined;
    }[];
    batchId?: string | undefined;
    contractId?: string | undefined;
}, {
    items: {
        name: string;
        useDate: string;
        bvlId?: string | undefined;
        cropOrUseCase?: string | undefined;
        quantity?: number | undefined;
        unit?: string | undefined;
    }[];
    batchId?: string | undefined;
    contractId?: string | undefined;
}>;
export type PSMCheckInput = z.infer<typeof PSMCheckInputSchema>;
export declare const PSMCheckResultSchema: z.ZodObject<{
    compliant: z.ZodBoolean;
    items: z.ZodArray<z.ZodObject<{
        name: z.ZodString;
        bvlId: z.ZodOptional<z.ZodString>;
        status: z.ZodEnum<["Approved", "Expired", "Withdrawn", "Restricted", "Pending", "Unknown"]>;
        approved: z.ZodBoolean;
        validUntil: z.ZodOptional<z.ZodString>;
        issues: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    }, "strip", z.ZodTypeAny, {
        issues: string[];
        status: "Expired" | "Pending" | "Approved" | "Withdrawn" | "Restricted" | "Unknown";
        name: string;
        approved: boolean;
        bvlId?: string | undefined;
        validUntil?: string | undefined;
    }, {
        status: "Expired" | "Pending" | "Approved" | "Withdrawn" | "Restricted" | "Unknown";
        name: string;
        approved: boolean;
        issues?: string[] | undefined;
        bvlId?: string | undefined;
        validUntil?: string | undefined;
    }>, "many">;
    violations: z.ZodArray<z.ZodObject<{
        name: z.ZodString;
        reason: z.ZodString;
        severity: z.ZodEnum<["Minor", "Major", "Critical"]>;
    }, "strip", z.ZodTypeAny, {
        name: string;
        severity: "Minor" | "Major" | "Critical";
        reason: string;
    }, {
        name: string;
        severity: "Minor" | "Major" | "Critical";
        reason: string;
    }>, "many">;
    recommendation: z.ZodString;
}, "strip", z.ZodTypeAny, {
    violations: {
        name: string;
        severity: "Minor" | "Major" | "Critical";
        reason: string;
    }[];
    recommendation: string;
    items: {
        issues: string[];
        status: "Expired" | "Pending" | "Approved" | "Withdrawn" | "Restricted" | "Unknown";
        name: string;
        approved: boolean;
        bvlId?: string | undefined;
        validUntil?: string | undefined;
    }[];
    compliant: boolean;
}, {
    violations: {
        name: string;
        severity: "Minor" | "Major" | "Critical";
        reason: string;
    }[];
    recommendation: string;
    items: {
        status: "Expired" | "Pending" | "Approved" | "Withdrawn" | "Restricted" | "Unknown";
        name: string;
        approved: boolean;
        issues?: string[] | undefined;
        bvlId?: string | undefined;
        validUntil?: string | undefined;
    }[];
    compliant: boolean;
}>;
export type PSMCheckResult = z.infer<typeof PSMCheckResultSchema>;
export declare const CreatePSMProductRefSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    bvlId: z.ZodOptional<z.ZodString>;
    name: z.ZodString;
    activeSubstances: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    approvalStatus: z.ZodDefault<z.ZodEnum<["Approved", "Expired", "Withdrawn", "Restricted", "Pending", "Unknown"]>>;
    approvalValidTo: z.ZodOptional<z.ZodString>;
    approvalNumber: z.ZodOptional<z.ZodString>;
    usageScope: z.ZodOptional<z.ZodString>;
    restrictions: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    lastCheckedAt: z.ZodOptional<z.ZodString>;
    lastCheckedBy: z.ZodOptional<z.ZodString>;
    sourceUrl: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
}, "id" | "createdAt" | "updatedAt">, "strip", z.ZodTypeAny, {
    tenantId: string;
    name: string;
    activeSubstances: string[];
    approvalStatus: "Expired" | "Pending" | "Approved" | "Withdrawn" | "Restricted" | "Unknown";
    bvlId?: string | undefined;
    approvalValidTo?: string | undefined;
    approvalNumber?: string | undefined;
    usageScope?: string | undefined;
    restrictions?: string[] | undefined;
    lastCheckedAt?: string | undefined;
    lastCheckedBy?: string | undefined;
    sourceUrl?: string | undefined;
}, {
    tenantId: string;
    name: string;
    bvlId?: string | undefined;
    activeSubstances?: string[] | undefined;
    approvalStatus?: "Expired" | "Pending" | "Approved" | "Withdrawn" | "Restricted" | "Unknown" | undefined;
    approvalValidTo?: string | undefined;
    approvalNumber?: string | undefined;
    usageScope?: string | undefined;
    restrictions?: string[] | undefined;
    lastCheckedAt?: string | undefined;
    lastCheckedBy?: string | undefined;
    sourceUrl?: string | undefined;
}>;
export type CreatePSMProductRef = z.infer<typeof CreatePSMProductRefSchema>;
//# sourceMappingURL=psm-product.d.ts.map