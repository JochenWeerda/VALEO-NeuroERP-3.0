import { z } from 'zod';
export declare const EvidenceTypeEnum: z.ZodEnum<["Certificate", "LabReport", "SupplierDeclaration", "AuditReport", "WeighingNote", "ProcessDocument", "CleaningProtocol", "ContractClause", "InspectionReport", "SelfDeclaration", "Invoice", "TransportDocument", "Other"]>;
export type EvidenceType = z.infer<typeof EvidenceTypeEnum>;
export declare const EvidenceStatusEnum: z.ZodEnum<["Valid", "Expired", "Pending", "Rejected", "Archived"]>;
export type EvidenceStatus = z.infer<typeof EvidenceStatusEnum>;
export declare const EvidenceSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    type: z.ZodEnum<["Certificate", "LabReport", "SupplierDeclaration", "AuditReport", "WeighingNote", "ProcessDocument", "CleaningProtocol", "ContractClause", "InspectionReport", "SelfDeclaration", "Invoice", "TransportDocument", "Other"]>;
    title: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    uri: z.ZodOptional<z.ZodString>;
    hash: z.ZodOptional<z.ZodString>;
    mimeType: z.ZodOptional<z.ZodString>;
    fileSize: z.ZodOptional<z.ZodNumber>;
    issuedBy: z.ZodString;
    issuedAt: z.ZodString;
    validFrom: z.ZodOptional<z.ZodString>;
    validTo: z.ZodOptional<z.ZodString>;
    status: z.ZodDefault<z.ZodEnum<["Valid", "Expired", "Pending", "Rejected", "Archived"]>>;
    relatedRef: z.ZodOptional<z.ZodObject<{
        type: z.ZodEnum<["Batch", "Contract", "Site", "Supplier", "Shipment", "Sample"]>;
        id: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Shipment" | "Sample";
        id: string;
    }, {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Shipment" | "Sample";
        id: string;
    }>>;
    supportingLabels: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    supportingPolicies: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    createdAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    type: "SupplierDeclaration" | "ProcessDocument" | "CleaningProtocol" | "LabReport" | "WeighingNote" | "Certificate" | "AuditReport" | "ContractClause" | "InspectionReport" | "SelfDeclaration" | "Invoice" | "TransportDocument" | "Other";
    status: "Expired" | "Pending" | "Valid" | "Rejected" | "Archived";
    tenantId: string;
    issuedAt: string;
    issuedBy: string;
    title: string;
    supportingLabels: string[];
    supportingPolicies: string[];
    description?: string | undefined;
    id?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    createdBy?: string | undefined;
    updatedAt?: string | undefined;
    uri?: string | undefined;
    hash?: string | undefined;
    mimeType?: string | undefined;
    fileSize?: number | undefined;
    relatedRef?: {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Shipment" | "Sample";
        id: string;
    } | undefined;
}, {
    type: "SupplierDeclaration" | "ProcessDocument" | "CleaningProtocol" | "LabReport" | "WeighingNote" | "Certificate" | "AuditReport" | "ContractClause" | "InspectionReport" | "SelfDeclaration" | "Invoice" | "TransportDocument" | "Other";
    tenantId: string;
    issuedAt: string;
    issuedBy: string;
    title: string;
    status?: "Expired" | "Pending" | "Valid" | "Rejected" | "Archived" | undefined;
    description?: string | undefined;
    id?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    createdBy?: string | undefined;
    updatedAt?: string | undefined;
    uri?: string | undefined;
    hash?: string | undefined;
    mimeType?: string | undefined;
    fileSize?: number | undefined;
    relatedRef?: {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Shipment" | "Sample";
        id: string;
    } | undefined;
    supportingLabels?: string[] | undefined;
    supportingPolicies?: string[] | undefined;
}>;
export type Evidence = z.infer<typeof EvidenceSchema>;
export declare const CreateEvidenceSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    type: z.ZodEnum<["Certificate", "LabReport", "SupplierDeclaration", "AuditReport", "WeighingNote", "ProcessDocument", "CleaningProtocol", "ContractClause", "InspectionReport", "SelfDeclaration", "Invoice", "TransportDocument", "Other"]>;
    title: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    uri: z.ZodOptional<z.ZodString>;
    hash: z.ZodOptional<z.ZodString>;
    mimeType: z.ZodOptional<z.ZodString>;
    fileSize: z.ZodOptional<z.ZodNumber>;
    issuedBy: z.ZodString;
    issuedAt: z.ZodString;
    validFrom: z.ZodOptional<z.ZodString>;
    validTo: z.ZodOptional<z.ZodString>;
    status: z.ZodDefault<z.ZodEnum<["Valid", "Expired", "Pending", "Rejected", "Archived"]>>;
    relatedRef: z.ZodOptional<z.ZodObject<{
        type: z.ZodEnum<["Batch", "Contract", "Site", "Supplier", "Shipment", "Sample"]>;
        id: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Shipment" | "Sample";
        id: string;
    }, {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Shipment" | "Sample";
        id: string;
    }>>;
    supportingLabels: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    supportingPolicies: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    createdAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
}, "id" | "createdAt" | "updatedAt">, "strip", z.ZodTypeAny, {
    type: "SupplierDeclaration" | "ProcessDocument" | "CleaningProtocol" | "LabReport" | "WeighingNote" | "Certificate" | "AuditReport" | "ContractClause" | "InspectionReport" | "SelfDeclaration" | "Invoice" | "TransportDocument" | "Other";
    status: "Expired" | "Pending" | "Valid" | "Rejected" | "Archived";
    tenantId: string;
    issuedAt: string;
    issuedBy: string;
    title: string;
    supportingLabels: string[];
    supportingPolicies: string[];
    description?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    createdBy?: string | undefined;
    uri?: string | undefined;
    hash?: string | undefined;
    mimeType?: string | undefined;
    fileSize?: number | undefined;
    relatedRef?: {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Shipment" | "Sample";
        id: string;
    } | undefined;
}, {
    type: "SupplierDeclaration" | "ProcessDocument" | "CleaningProtocol" | "LabReport" | "WeighingNote" | "Certificate" | "AuditReport" | "ContractClause" | "InspectionReport" | "SelfDeclaration" | "Invoice" | "TransportDocument" | "Other";
    tenantId: string;
    issuedAt: string;
    issuedBy: string;
    title: string;
    status?: "Expired" | "Pending" | "Valid" | "Rejected" | "Archived" | undefined;
    description?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    createdBy?: string | undefined;
    uri?: string | undefined;
    hash?: string | undefined;
    mimeType?: string | undefined;
    fileSize?: number | undefined;
    relatedRef?: {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Shipment" | "Sample";
        id: string;
    } | undefined;
    supportingLabels?: string[] | undefined;
    supportingPolicies?: string[] | undefined;
}>;
export type CreateEvidence = z.infer<typeof CreateEvidenceSchema>;
export declare const LinkEvidenceSchema: z.ZodObject<{
    evidenceId: z.ZodString;
    targetRef: z.ZodObject<{
        type: z.ZodEnum<["Batch", "Contract", "Site", "Supplier", "Label"]>;
        id: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Label";
        id: string;
    }, {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Label";
        id: string;
    }>;
}, "strip", z.ZodTypeAny, {
    targetRef: {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Label";
        id: string;
    };
    evidenceId: string;
}, {
    targetRef: {
        type: "Site" | "Contract" | "Supplier" | "Batch" | "Label";
        id: string;
    };
    evidenceId: string;
}>;
export type LinkEvidence = z.infer<typeof LinkEvidenceSchema>;
//# sourceMappingURL=evidence.d.ts.map