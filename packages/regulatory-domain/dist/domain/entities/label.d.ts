import { z } from 'zod';
export declare const LabelCodeEnum: z.ZodEnum<["VLOG_OGT", "QS", "GMP_PLUS", "NON_GMO", "ORGANIC_EU", "REDII_COMPLIANT", "ISCC", "RTRS", "RSPO", "CUSTOM"]>;
export type LabelCode = z.infer<typeof LabelCodeEnum>;
export declare const LabelStatusEnum: z.ZodEnum<["Eligible", "Ineligible", "Conditional", "Suspended", "Expired", "Pending"]>;
export type LabelStatus = z.infer<typeof LabelStatusEnum>;
export declare const LabelSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    code: z.ZodEnum<["VLOG_OGT", "QS", "GMP_PLUS", "NON_GMO", "ORGANIC_EU", "REDII_COMPLIANT", "ISCC", "RTRS", "RSPO", "CUSTOM"]>;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    targetType: z.ZodEnum<["Batch", "Contract", "Site", "Commodity", "Supplier"]>;
    targetId: z.ZodString;
    status: z.ZodDefault<z.ZodEnum<["Eligible", "Ineligible", "Conditional", "Suspended", "Expired", "Pending"]>>;
    evidenceRefs: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    missingEvidences: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    issuedAt: z.ZodOptional<z.ZodString>;
    issuedBy: z.ZodOptional<z.ZodString>;
    validFrom: z.ZodOptional<z.ZodString>;
    validTo: z.ZodOptional<z.ZodString>;
    revokedAt: z.ZodOptional<z.ZodString>;
    revokedBy: z.ZodOptional<z.ZodString>;
    revokedReason: z.ZodOptional<z.ZodString>;
    policyId: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    code: "QS" | "GMP_PLUS" | "NON_GMO" | "CUSTOM" | "VLOG_OGT" | "ORGANIC_EU" | "REDII_COMPLIANT" | "ISCC" | "RTRS" | "RSPO";
    status: "Eligible" | "Ineligible" | "Conditional" | "Suspended" | "Expired" | "Pending";
    tenantId: string;
    name: string;
    targetType: "Commodity" | "Site" | "Contract" | "Supplier" | "Batch";
    targetId: string;
    evidenceRefs: string[];
    description?: string | undefined;
    id?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    updatedAt?: string | undefined;
    missingEvidences?: string[] | undefined;
    issuedAt?: string | undefined;
    issuedBy?: string | undefined;
    revokedAt?: string | undefined;
    revokedBy?: string | undefined;
    revokedReason?: string | undefined;
    policyId?: string | undefined;
}, {
    code: "QS" | "GMP_PLUS" | "NON_GMO" | "CUSTOM" | "VLOG_OGT" | "ORGANIC_EU" | "REDII_COMPLIANT" | "ISCC" | "RTRS" | "RSPO";
    tenantId: string;
    name: string;
    targetType: "Commodity" | "Site" | "Contract" | "Supplier" | "Batch";
    targetId: string;
    status?: "Eligible" | "Ineligible" | "Conditional" | "Suspended" | "Expired" | "Pending" | undefined;
    description?: string | undefined;
    id?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    updatedAt?: string | undefined;
    evidenceRefs?: string[] | undefined;
    missingEvidences?: string[] | undefined;
    issuedAt?: string | undefined;
    issuedBy?: string | undefined;
    revokedAt?: string | undefined;
    revokedBy?: string | undefined;
    revokedReason?: string | undefined;
    policyId?: string | undefined;
}>;
export type Label = z.infer<typeof LabelSchema>;
export declare const LabelEvaluateInputSchema: z.ZodObject<{
    targetRef: z.ZodObject<{
        type: z.ZodEnum<["Batch", "Contract", "Site", "Commodity", "Supplier"]>;
        id: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "Commodity" | "Site" | "Contract" | "Supplier" | "Batch";
        id: string;
    }, {
        type: "Commodity" | "Site" | "Contract" | "Supplier" | "Batch";
        id: string;
    }>;
    labelCode: z.ZodEnum<["VLOG_OGT", "QS", "GMP_PLUS", "NON_GMO", "ORGANIC_EU", "REDII_COMPLIANT", "ISCC", "RTRS", "RSPO", "CUSTOM"]>;
    context: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
}, "strip", z.ZodTypeAny, {
    targetRef: {
        type: "Commodity" | "Site" | "Contract" | "Supplier" | "Batch";
        id: string;
    };
    labelCode: "QS" | "GMP_PLUS" | "NON_GMO" | "CUSTOM" | "VLOG_OGT" | "ORGANIC_EU" | "REDII_COMPLIANT" | "ISCC" | "RTRS" | "RSPO";
    context?: Record<string, any> | undefined;
}, {
    targetRef: {
        type: "Commodity" | "Site" | "Contract" | "Supplier" | "Batch";
        id: string;
    };
    labelCode: "QS" | "GMP_PLUS" | "NON_GMO" | "CUSTOM" | "VLOG_OGT" | "ORGANIC_EU" | "REDII_COMPLIANT" | "ISCC" | "RTRS" | "RSPO";
    context?: Record<string, any> | undefined;
}>;
export type LabelEvaluateInput = z.infer<typeof LabelEvaluateInputSchema>;
export declare const LabelEvaluationResultSchema: z.ZodObject<{
    eligible: z.ZodBoolean;
    status: z.ZodEnum<["Eligible", "Ineligible", "Conditional", "Suspended", "Expired", "Pending"]>;
    missingEvidences: z.ZodArray<z.ZodString, "many">;
    violations: z.ZodArray<z.ZodObject<{
        ruleId: z.ZodString;
        description: z.ZodString;
        severity: z.ZodEnum<["Minor", "Major", "Critical"]>;
    }, "strip", z.ZodTypeAny, {
        ruleId: string;
        description: string;
        severity: "Minor" | "Major" | "Critical";
    }, {
        ruleId: string;
        description: string;
        severity: "Minor" | "Major" | "Critical";
    }>, "many">;
    recommendation: z.ZodString;
    confidence: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    status: "Eligible" | "Ineligible" | "Conditional" | "Suspended" | "Expired" | "Pending";
    missingEvidences: string[];
    eligible: boolean;
    violations: {
        ruleId: string;
        description: string;
        severity: "Minor" | "Major" | "Critical";
    }[];
    recommendation: string;
    confidence?: number | undefined;
}, {
    status: "Eligible" | "Ineligible" | "Conditional" | "Suspended" | "Expired" | "Pending";
    missingEvidences: string[];
    eligible: boolean;
    violations: {
        ruleId: string;
        description: string;
        severity: "Minor" | "Major" | "Critical";
    }[];
    recommendation: string;
    confidence?: number | undefined;
}>;
export type LabelEvaluationResult = z.infer<typeof LabelEvaluationResultSchema>;
export declare const CreateLabelSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    code: z.ZodEnum<["VLOG_OGT", "QS", "GMP_PLUS", "NON_GMO", "ORGANIC_EU", "REDII_COMPLIANT", "ISCC", "RTRS", "RSPO", "CUSTOM"]>;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    targetType: z.ZodEnum<["Batch", "Contract", "Site", "Commodity", "Supplier"]>;
    targetId: z.ZodString;
    status: z.ZodDefault<z.ZodEnum<["Eligible", "Ineligible", "Conditional", "Suspended", "Expired", "Pending"]>>;
    evidenceRefs: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    missingEvidences: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    issuedAt: z.ZodOptional<z.ZodString>;
    issuedBy: z.ZodOptional<z.ZodString>;
    validFrom: z.ZodOptional<z.ZodString>;
    validTo: z.ZodOptional<z.ZodString>;
    revokedAt: z.ZodOptional<z.ZodString>;
    revokedBy: z.ZodOptional<z.ZodString>;
    revokedReason: z.ZodOptional<z.ZodString>;
    policyId: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
}, "id" | "createdAt" | "updatedAt" | "issuedAt" | "revokedAt">, "strip", z.ZodTypeAny, {
    code: "QS" | "GMP_PLUS" | "NON_GMO" | "CUSTOM" | "VLOG_OGT" | "ORGANIC_EU" | "REDII_COMPLIANT" | "ISCC" | "RTRS" | "RSPO";
    status: "Eligible" | "Ineligible" | "Conditional" | "Suspended" | "Expired" | "Pending";
    tenantId: string;
    name: string;
    targetType: "Commodity" | "Site" | "Contract" | "Supplier" | "Batch";
    targetId: string;
    evidenceRefs: string[];
    description?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    missingEvidences?: string[] | undefined;
    issuedBy?: string | undefined;
    revokedBy?: string | undefined;
    revokedReason?: string | undefined;
    policyId?: string | undefined;
}, {
    code: "QS" | "GMP_PLUS" | "NON_GMO" | "CUSTOM" | "VLOG_OGT" | "ORGANIC_EU" | "REDII_COMPLIANT" | "ISCC" | "RTRS" | "RSPO";
    tenantId: string;
    name: string;
    targetType: "Commodity" | "Site" | "Contract" | "Supplier" | "Batch";
    targetId: string;
    status?: "Eligible" | "Ineligible" | "Conditional" | "Suspended" | "Expired" | "Pending" | undefined;
    description?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    evidenceRefs?: string[] | undefined;
    missingEvidences?: string[] | undefined;
    issuedBy?: string | undefined;
    revokedBy?: string | undefined;
    revokedReason?: string | undefined;
    policyId?: string | undefined;
}>;
export type CreateLabel = z.infer<typeof CreateLabelSchema>;
//# sourceMappingURL=label.d.ts.map