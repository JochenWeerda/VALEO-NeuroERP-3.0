import { z } from 'zod';
export declare const CallOffStatus: {
    readonly PLANNED: "Planned";
    readonly SCHEDULED: "Scheduled";
    readonly DELIVERED: "Delivered";
    readonly INVOICED: "Invoiced";
    readonly CANCELLED: "Cancelled";
};
export type CallOffStatusValue = typeof CallOffStatus[keyof typeof CallOffStatus];
export declare const CallOffSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    contractId: z.ZodString;
    tenantId: z.ZodString;
    qty: z.ZodNumber;
    window: z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>;
    site: z.ZodOptional<z.ZodString>;
    silo: z.ZodOptional<z.ZodString>;
    customerYard: z.ZodOptional<z.ZodString>;
    status: z.ZodDefault<z.ZodEnum<["Planned", "Scheduled", "Delivered", "Invoiced", "Cancelled"]>>;
    notes: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodOptional<z.ZodDate>;
    updatedAt: z.ZodOptional<z.ZodDate>;
    version: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    status: "Cancelled" | "Planned" | "Scheduled" | "Delivered" | "Invoiced";
    tenantId: string;
    qty: number;
    version: number;
    contractId: string;
    window: {
        from: string;
        to: string;
    };
    id?: string | undefined;
    createdAt?: Date | undefined;
    updatedAt?: Date | undefined;
    notes?: string | undefined;
    site?: string | undefined;
    silo?: string | undefined;
    customerYard?: string | undefined;
}, {
    tenantId: string;
    qty: number;
    contractId: string;
    window: {
        from: string;
        to: string;
    };
    status?: "Cancelled" | "Planned" | "Scheduled" | "Delivered" | "Invoiced" | undefined;
    id?: string | undefined;
    createdAt?: Date | undefined;
    updatedAt?: Date | undefined;
    version?: number | undefined;
    notes?: string | undefined;
    site?: string | undefined;
    silo?: string | undefined;
    customerYard?: string | undefined;
}>;
export interface CallOffEntity {
    id: string;
    contractId: string;
    tenantId: string;
    qty: number;
    window: {
        from: Date;
        to: Date;
    };
    site?: string;
    silo?: string;
    customerYard?: string;
    status: CallOffStatusValue;
    notes?: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
}
export declare class CallOff implements CallOffEntity {
    id: string;
    contractId: string;
    tenantId: string;
    qty: number;
    window: {
        from: Date;
        to: Date;
    };
    site?: string;
    silo?: string;
    customerYard?: string;
    status: CallOffStatusValue;
    notes?: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    constructor(props: CallOffEntity);
    schedule(): void;
    markDelivered(): void;
    cancel(): void;
    canBeModified(): boolean;
}
//# sourceMappingURL=call-off.d.ts.map