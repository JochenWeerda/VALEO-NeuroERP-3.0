/**
 * Production Domain Events for VALEO NeuroERP 3.0
 * Event definitions for production processes with GMP+/QS compliance
 */
import { z } from 'zod';
declare const BaseDomainEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventType: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: string;
    eventVersion: number;
    occurredAt: string;
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: string;
    eventVersion: number;
    occurredAt: string;
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const RecipeCreatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.recipe.created">;
    payload: z.ZodObject<{
        id: z.ZodString;
        code: z.ZodString;
        name: z.ZodString;
        version: z.ZodNumber;
        medicated: z.ZodBoolean;
        allergenTags: z.ZodArray<z.ZodString, "many">;
    }, "strip", z.ZodTypeAny, {
        code: string;
        id: string;
        name: string;
        medicated: boolean;
        allergenTags: string[];
        version: number;
    }, {
        code: string;
        id: string;
        name: string;
        medicated: boolean;
        allergenTags: string[];
        version: number;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.recipe.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        code: string;
        id: string;
        name: string;
        medicated: boolean;
        allergenTags: string[];
        version: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.recipe.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        code: string;
        id: string;
        name: string;
        medicated: boolean;
        allergenTags: string[];
        version: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const RecipeUpdatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.recipe.updated">;
    payload: z.ZodObject<{
        id: z.ZodString;
        code: z.ZodString;
        name: z.ZodString;
        version: z.ZodNumber;
        changes: z.ZodArray<z.ZodString, "many">;
    }, "strip", z.ZodTypeAny, {
        code: string;
        id: string;
        name: string;
        version: number;
        changes: string[];
    }, {
        code: string;
        id: string;
        name: string;
        version: number;
        changes: string[];
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.recipe.updated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        code: string;
        id: string;
        name: string;
        version: number;
        changes: string[];
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.recipe.updated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        code: string;
        id: string;
        name: string;
        version: number;
        changes: string[];
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const RecipeArchivedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.recipe.archived">;
    payload: z.ZodObject<{
        id: z.ZodString;
        code: z.ZodString;
        reason: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        code: string;
        id: string;
        reason?: string | undefined;
    }, {
        code: string;
        id: string;
        reason?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.recipe.archived";
    eventVersion: number;
    occurredAt: string;
    payload: {
        code: string;
        id: string;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.recipe.archived";
    eventVersion: number;
    occurredAt: string;
    payload: {
        code: string;
        id: string;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const MixOrderCreatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.mix_order.created">;
    payload: z.ZodObject<{
        id: z.ZodString;
        orderNumber: z.ZodString;
        type: z.ZodEnum<["Plant", "Mobile"]>;
        recipeId: z.ZodString;
        targetQtyKg: z.ZodNumber;
        customerId: z.ZodOptional<z.ZodString>;
        mobileUnitId: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        recipeId: string;
        targetQtyKg: number;
        customerId?: string | undefined;
        mobileUnitId?: string | undefined;
    }, {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        recipeId: string;
        targetQtyKg: number;
        customerId?: string | undefined;
        mobileUnitId?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        recipeId: string;
        targetQtyKg: number;
        customerId?: string | undefined;
        mobileUnitId?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        recipeId: string;
        targetQtyKg: number;
        customerId?: string | undefined;
        mobileUnitId?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const MixOrderStagedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.mix_order.staged">;
    payload: z.ZodObject<{
        id: z.ZodString;
        orderNumber: z.ZodString;
        type: z.ZodEnum<["Plant", "Mobile"]>;
        recipeId: z.ZodString;
        plannedAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        recipeId: string;
        plannedAt: string;
    }, {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        recipeId: string;
        plannedAt: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.staged";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        recipeId: string;
        plannedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.staged";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        recipeId: string;
        plannedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const MixOrderStartedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.mix_order.started">;
    payload: z.ZodObject<{
        id: z.ZodString;
        orderNumber: z.ZodString;
        type: z.ZodEnum<["Plant", "Mobile"]>;
        startedAt: z.ZodString;
        operatorId: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        type: "Plant" | "Mobile";
        id: string;
        startedAt: string;
        orderNumber: string;
        operatorId?: string | undefined;
    }, {
        type: "Plant" | "Mobile";
        id: string;
        startedAt: string;
        orderNumber: string;
        operatorId?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.started";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Plant" | "Mobile";
        id: string;
        startedAt: string;
        orderNumber: string;
        operatorId?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.started";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Plant" | "Mobile";
        id: string;
        startedAt: string;
        orderNumber: string;
        operatorId?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const MixOrderCompletedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.mix_order.completed">;
    payload: z.ZodObject<{
        id: z.ZodString;
        orderNumber: z.ZodString;
        type: z.ZodEnum<["Plant", "Mobile"]>;
        completedAt: z.ZodString;
        durationMinutes: z.ZodNumber;
        totalMassKg: z.ZodNumber;
        energyKWh: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        completedAt: string;
        durationMinutes: number;
        totalMassKg: number;
        energyKWh?: number | undefined;
    }, {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        completedAt: string;
        durationMinutes: number;
        totalMassKg: number;
        energyKWh?: number | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.completed";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        completedAt: string;
        durationMinutes: number;
        totalMassKg: number;
        energyKWh?: number | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.completed";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Plant" | "Mobile";
        id: string;
        orderNumber: string;
        completedAt: string;
        durationMinutes: number;
        totalMassKg: number;
        energyKWh?: number | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const MixOrderAbortedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.mix_order.aborted">;
    payload: z.ZodObject<{
        id: z.ZodString;
        orderNumber: z.ZodString;
        reason: z.ZodString;
        abortedAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: string;
        orderNumber: string;
        reason: string;
        abortedAt: string;
    }, {
        id: string;
        orderNumber: string;
        reason: string;
        abortedAt: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.aborted";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        orderNumber: string;
        reason: string;
        abortedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.mix_order.aborted";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        orderNumber: string;
        reason: string;
        abortedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const BatchCreatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.batch.created">;
    payload: z.ZodObject<{
        id: z.ZodString;
        batchNumber: z.ZodString;
        mixOrderId: z.ZodString;
        producedQtyKg: z.ZodNumber;
        recipeId: z.ZodString;
        medicated: z.ZodBoolean;
    }, "strip", z.ZodTypeAny, {
        id: string;
        batchNumber: string;
        mixOrderId: string;
        producedQtyKg: number;
        recipeId: string;
        medicated: boolean;
    }, {
        id: string;
        batchNumber: string;
        mixOrderId: string;
        producedQtyKg: number;
        recipeId: string;
        medicated: boolean;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.batch.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        batchNumber: string;
        mixOrderId: string;
        producedQtyKg: number;
        recipeId: string;
        medicated: boolean;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.batch.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        batchNumber: string;
        mixOrderId: string;
        producedQtyKg: number;
        recipeId: string;
        medicated: boolean;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const BatchReleasedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.batch.released">;
    payload: z.ZodObject<{
        id: z.ZodString;
        batchNumber: z.ZodString;
        mixOrderId: z.ZodString;
        releasedAt: z.ZodString;
        outputLots: z.ZodArray<z.ZodObject<{
            lotNumber: z.ZodString;
            qtyKg: z.ZodNumber;
            destination: z.ZodEnum<["Inventory", "DirectFarm"]>;
        }, "strip", z.ZodTypeAny, {
            lotNumber: string;
            qtyKg: number;
            destination: "Inventory" | "DirectFarm";
        }, {
            lotNumber: string;
            qtyKg: number;
            destination: "Inventory" | "DirectFarm";
        }>, "many">;
    }, "strip", z.ZodTypeAny, {
        id: string;
        batchNumber: string;
        mixOrderId: string;
        releasedAt: string;
        outputLots: {
            lotNumber: string;
            qtyKg: number;
            destination: "Inventory" | "DirectFarm";
        }[];
    }, {
        id: string;
        batchNumber: string;
        mixOrderId: string;
        releasedAt: string;
        outputLots: {
            lotNumber: string;
            qtyKg: number;
            destination: "Inventory" | "DirectFarm";
        }[];
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.batch.released";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        batchNumber: string;
        mixOrderId: string;
        releasedAt: string;
        outputLots: {
            lotNumber: string;
            qtyKg: number;
            destination: "Inventory" | "DirectFarm";
        }[];
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.batch.released";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        batchNumber: string;
        mixOrderId: string;
        releasedAt: string;
        outputLots: {
            lotNumber: string;
            qtyKg: number;
            destination: "Inventory" | "DirectFarm";
        }[];
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const BatchQuarantinedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.batch.quarantined">;
    payload: z.ZodObject<{
        id: z.ZodString;
        batchNumber: z.ZodString;
        reason: z.ZodString;
        quarantinedAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: string;
        batchNumber: string;
        reason: string;
        quarantinedAt: string;
    }, {
        id: string;
        batchNumber: string;
        reason: string;
        quarantinedAt: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.batch.quarantined";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        batchNumber: string;
        reason: string;
        quarantinedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.batch.quarantined";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        batchNumber: string;
        reason: string;
        quarantinedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const BatchRejectedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.batch.rejected">;
    payload: z.ZodObject<{
        id: z.ZodString;
        batchNumber: z.ZodString;
        reason: z.ZodString;
        rejectedAt: z.ZodString;
        disposalMethod: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        batchNumber: string;
        reason: string;
        rejectedAt: string;
        disposalMethod?: string | undefined;
    }, {
        id: string;
        batchNumber: string;
        reason: string;
        rejectedAt: string;
        disposalMethod?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.batch.rejected";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        batchNumber: string;
        reason: string;
        rejectedAt: string;
        disposalMethod?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.batch.rejected";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        batchNumber: string;
        reason: string;
        rejectedAt: string;
        disposalMethod?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const MobileRunStartedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.mobile_run.started">;
    payload: z.ZodObject<{
        id: z.ZodString;
        mobileUnitId: z.ZodString;
        operatorId: z.ZodString;
        customerId: z.ZodString;
        location: z.ZodObject<{
            lat: z.ZodNumber;
            lng: z.ZodNumber;
            address: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lng: number;
            address?: string | undefined;
        }, {
            lat: number;
            lng: number;
            address?: string | undefined;
        }>;
        calibrationValid: z.ZodBoolean;
        startedAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: string;
        startedAt: string;
        location: {
            lat: number;
            lng: number;
            address?: string | undefined;
        };
        customerId: string;
        mobileUnitId: string;
        operatorId: string;
        calibrationValid: boolean;
    }, {
        id: string;
        startedAt: string;
        location: {
            lat: number;
            lng: number;
            address?: string | undefined;
        };
        customerId: string;
        mobileUnitId: string;
        operatorId: string;
        calibrationValid: boolean;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.mobile_run.started";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        startedAt: string;
        location: {
            lat: number;
            lng: number;
            address?: string | undefined;
        };
        customerId: string;
        mobileUnitId: string;
        operatorId: string;
        calibrationValid: boolean;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.mobile_run.started";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        startedAt: string;
        location: {
            lat: number;
            lng: number;
            address?: string | undefined;
        };
        customerId: string;
        mobileUnitId: string;
        operatorId: string;
        calibrationValid: boolean;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const MobileRunFinishedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.mobile_run.finished">;
    payload: z.ZodObject<{
        id: z.ZodString;
        mobileUnitId: z.ZodString;
        operatorId: z.ZodString;
        durationHours: z.ZodNumber;
        totalFlushMassKg: z.ZodNumber;
        finishedAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: string;
        mobileUnitId: string;
        operatorId: string;
        durationHours: number;
        totalFlushMassKg: number;
        finishedAt: string;
    }, {
        id: string;
        mobileUnitId: string;
        operatorId: string;
        durationHours: number;
        totalFlushMassKg: number;
        finishedAt: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.mobile_run.finished";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        mobileUnitId: string;
        operatorId: string;
        durationHours: number;
        totalFlushMassKg: number;
        finishedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.mobile_run.finished";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        mobileUnitId: string;
        operatorId: string;
        durationHours: number;
        totalFlushMassKg: number;
        finishedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const CleaningPerformedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.cleaning.performed">;
    payload: z.ZodObject<{
        id: z.ZodString;
        mobileRunId: z.ZodOptional<z.ZodString>;
        type: z.ZodEnum<["DryClean", "Vacuum", "Flush", "WetClean"]>;
        usedMaterialSku: z.ZodOptional<z.ZodString>;
        flushMassKg: z.ZodOptional<z.ZodNumber>;
        validatedBy: z.ZodString;
        performedAt: z.ZodString;
        reason: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
        id: string;
        validatedBy: string;
        performedAt: string;
        usedMaterialSku?: string | undefined;
        flushMassKg?: number | undefined;
        mobileRunId?: string | undefined;
        reason?: string | undefined;
    }, {
        type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
        id: string;
        validatedBy: string;
        performedAt: string;
        usedMaterialSku?: string | undefined;
        flushMassKg?: number | undefined;
        mobileRunId?: string | undefined;
        reason?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.cleaning.performed";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
        id: string;
        validatedBy: string;
        performedAt: string;
        usedMaterialSku?: string | undefined;
        flushMassKg?: number | undefined;
        mobileRunId?: string | undefined;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.cleaning.performed";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
        id: string;
        validatedBy: string;
        performedAt: string;
        usedMaterialSku?: string | undefined;
        flushMassKg?: number | undefined;
        mobileRunId?: string | undefined;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const FlushPerformedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.flush.performed">;
    payload: z.ZodObject<{
        id: z.ZodString;
        mobileRunId: z.ZodString;
        usedMaterialSku: z.ZodString;
        flushMassKg: z.ZodNumber;
        reason: z.ZodEnum<["Sequencing", "MedicatedTransition", "ContaminationPrevention"]>;
        performedAt: z.ZodString;
        validatedBy: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: string;
        validatedBy: string;
        usedMaterialSku: string;
        flushMassKg: number;
        mobileRunId: string;
        reason: "Sequencing" | "MedicatedTransition" | "ContaminationPrevention";
        performedAt: string;
    }, {
        id: string;
        validatedBy: string;
        usedMaterialSku: string;
        flushMassKg: number;
        mobileRunId: string;
        reason: "Sequencing" | "MedicatedTransition" | "ContaminationPrevention";
        performedAt: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.flush.performed";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        validatedBy: string;
        usedMaterialSku: string;
        flushMassKg: number;
        mobileRunId: string;
        reason: "Sequencing" | "MedicatedTransition" | "ContaminationPrevention";
        performedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.flush.performed";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        validatedBy: string;
        usedMaterialSku: string;
        flushMassKg: number;
        mobileRunId: string;
        reason: "Sequencing" | "MedicatedTransition" | "ContaminationPrevention";
        performedAt: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const CalibrationCheckedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.calibration.checked">;
    payload: z.ZodObject<{
        id: z.ZodString;
        mobileRunId: z.ZodOptional<z.ZodString>;
        deviceType: z.ZodEnum<["Scale", "Moisture", "Temperature"]>;
        deviceId: z.ZodString;
        result: z.ZodEnum<["Pass", "Fail"]>;
        checkedAt: z.ZodString;
        checkedBy: z.ZodString;
        nextDueDate: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        deviceType: "Scale" | "Moisture" | "Temperature";
        deviceId: string;
        result: "Pass" | "Fail";
        checkedAt: string;
        checkedBy: string;
        mobileRunId?: string | undefined;
        nextDueDate?: string | undefined;
    }, {
        id: string;
        deviceType: "Scale" | "Moisture" | "Temperature";
        deviceId: string;
        result: "Pass" | "Fail";
        checkedAt: string;
        checkedBy: string;
        mobileRunId?: string | undefined;
        nextDueDate?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.calibration.checked";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        deviceType: "Scale" | "Moisture" | "Temperature";
        deviceId: string;
        result: "Pass" | "Fail";
        checkedAt: string;
        checkedBy: string;
        mobileRunId?: string | undefined;
        nextDueDate?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.calibration.checked";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        deviceType: "Scale" | "Moisture" | "Temperature";
        deviceId: string;
        result: "Pass" | "Fail";
        checkedAt: string;
        checkedBy: string;
        mobileRunId?: string | undefined;
        nextDueDate?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const SamplingAddedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.sampling.added">;
    payload: z.ZodObject<{
        id: z.ZodString;
        batchId: z.ZodString;
        sampleCode: z.ZodString;
        analyte: z.ZodString;
        takenAt: z.ZodString;
        takenBy: z.ZodString;
        retainedSample: z.ZodBoolean;
    }, "strip", z.ZodTypeAny, {
        batchId: string;
        id: string;
        sampleCode: string;
        takenAt: string;
        analyte: string;
        takenBy: string;
        retainedSample: boolean;
    }, {
        batchId: string;
        id: string;
        sampleCode: string;
        takenAt: string;
        analyte: string;
        takenBy: string;
        retainedSample: boolean;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.sampling.added";
    eventVersion: number;
    occurredAt: string;
    payload: {
        batchId: string;
        id: string;
        sampleCode: string;
        takenAt: string;
        analyte: string;
        takenBy: string;
        retainedSample: boolean;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.sampling.added";
    eventVersion: number;
    occurredAt: string;
    payload: {
        batchId: string;
        id: string;
        sampleCode: string;
        takenAt: string;
        analyte: string;
        takenBy: string;
        retainedSample: boolean;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const SamplingResultRecordedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.sampling.result_recorded">;
    payload: z.ZodObject<{
        id: z.ZodString;
        batchId: z.ZodString;
        sampleCode: z.ZodString;
        analyte: z.ZodString;
        value: z.ZodNumber;
        unit: z.ZodString;
        limitType: z.ZodEnum<["Action", "Reject"]>;
        decision: z.ZodEnum<["Pass", "Investigate", "Reject"]>;
        labId: z.ZodOptional<z.ZodString>;
        recordedAt: z.ZodString;
        recordedBy: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        batchId: string;
        value: number;
        id: string;
        unit: string;
        sampleCode: string;
        analyte: string;
        limitType: "Action" | "Reject";
        decision: "Reject" | "Pass" | "Investigate";
        recordedAt: string;
        recordedBy: string;
        labId?: string | undefined;
    }, {
        batchId: string;
        value: number;
        id: string;
        unit: string;
        sampleCode: string;
        analyte: string;
        limitType: "Action" | "Reject";
        decision: "Reject" | "Pass" | "Investigate";
        recordedAt: string;
        recordedBy: string;
        labId?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.sampling.result_recorded";
    eventVersion: number;
    occurredAt: string;
    payload: {
        batchId: string;
        value: number;
        id: string;
        unit: string;
        sampleCode: string;
        analyte: string;
        limitType: "Action" | "Reject";
        decision: "Reject" | "Pass" | "Investigate";
        recordedAt: string;
        recordedBy: string;
        labId?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.sampling.result_recorded";
    eventVersion: number;
    occurredAt: string;
    payload: {
        batchId: string;
        value: number;
        id: string;
        unit: string;
        sampleCode: string;
        analyte: string;
        limitType: "Action" | "Reject";
        decision: "Reject" | "Pass" | "Investigate";
        recordedAt: string;
        recordedBy: string;
        labId?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const NonConformityCreatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.nc.created">;
    payload: z.ZodObject<{
        id: z.ZodString;
        refType: z.ZodEnum<["batchId", "mixOrderId", "mobileRunId"]>;
        refId: z.ZodString;
        type: z.ZodEnum<["Contamination", "SpecOut", "Equipment", "Process"]>;
        severity: z.ZodEnum<["Low", "Medium", "High", "Critical"]>;
        action: z.ZodEnum<["Block", "Rework", "Dispose"]>;
        description: z.ZodString;
        discoveredAt: z.ZodString;
        discoveredBy: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "Contamination" | "SpecOut" | "Equipment" | "Process";
        id: string;
        refType: "batchId" | "mixOrderId" | "mobileRunId";
        refId: string;
        severity: "Low" | "Medium" | "High" | "Critical";
        description: string;
        action: "Block" | "Rework" | "Dispose";
        discoveredAt: string;
        discoveredBy: string;
    }, {
        type: "Contamination" | "SpecOut" | "Equipment" | "Process";
        id: string;
        refType: "batchId" | "mixOrderId" | "mobileRunId";
        refId: string;
        severity: "Low" | "Medium" | "High" | "Critical";
        description: string;
        action: "Block" | "Rework" | "Dispose";
        discoveredAt: string;
        discoveredBy: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.nc.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Contamination" | "SpecOut" | "Equipment" | "Process";
        id: string;
        refType: "batchId" | "mixOrderId" | "mobileRunId";
        refId: string;
        severity: "Low" | "Medium" | "High" | "Critical";
        description: string;
        action: "Block" | "Rework" | "Dispose";
        discoveredAt: string;
        discoveredBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.nc.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Contamination" | "SpecOut" | "Equipment" | "Process";
        id: string;
        refType: "batchId" | "mixOrderId" | "mobileRunId";
        refId: string;
        severity: "Low" | "Medium" | "High" | "Critical";
        description: string;
        action: "Block" | "Rework" | "Dispose";
        discoveredAt: string;
        discoveredBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const CAPACreatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.capa.created">;
    payload: z.ZodObject<{
        id: z.ZodString;
        ncId: z.ZodOptional<z.ZodString>;
        title: z.ZodString;
        type: z.ZodEnum<["Correction", "CorrectiveAction", "PreventiveAction"]>;
        priority: z.ZodEnum<["Low", "Medium", "High", "Critical"]>;
        assignedTo: z.ZodOptional<z.ZodString>;
        dueDate: z.ZodOptional<z.ZodString>;
        createdBy: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        type: "Correction" | "CorrectiveAction" | "PreventiveAction";
        id: string;
        createdBy: string;
        title: string;
        priority: "Low" | "Medium" | "High" | "Critical";
        ncId?: string | undefined;
        assignedTo?: string | undefined;
        dueDate?: string | undefined;
    }, {
        type: "Correction" | "CorrectiveAction" | "PreventiveAction";
        id: string;
        createdBy: string;
        title: string;
        priority: "Low" | "Medium" | "High" | "Critical";
        ncId?: string | undefined;
        assignedTo?: string | undefined;
        dueDate?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.capa.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Correction" | "CorrectiveAction" | "PreventiveAction";
        id: string;
        createdBy: string;
        title: string;
        priority: "Low" | "Medium" | "High" | "Critical";
        ncId?: string | undefined;
        assignedTo?: string | undefined;
        dueDate?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.capa.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: "Correction" | "CorrectiveAction" | "PreventiveAction";
        id: string;
        createdBy: string;
        title: string;
        priority: "Low" | "Medium" | "High" | "Critical";
        ncId?: string | undefined;
        assignedTo?: string | undefined;
        dueDate?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const CAPAClosedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"production.capa.closed">;
    payload: z.ZodObject<{
        id: z.ZodString;
        effectiveness: z.ZodEnum<["Effective", "NotEffective", "NotEvaluated"]>;
        closedAt: z.ZodString;
        closedBy: z.ZodString;
        summary: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        closedAt: string;
        effectiveness: "Effective" | "NotEffective" | "NotEvaluated";
        closedBy: string;
        summary?: string | undefined;
    }, {
        id: string;
        closedAt: string;
        effectiveness: "Effective" | "NotEffective" | "NotEvaluated";
        closedBy: string;
        summary?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "production.capa.closed";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        closedAt: string;
        effectiveness: "Effective" | "NotEffective" | "NotEvaluated";
        closedBy: string;
        summary?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "production.capa.closed";
    eventVersion: number;
    occurredAt: string;
    payload: {
        id: string;
        closedAt: string;
        effectiveness: "Effective" | "NotEffective" | "NotEvaluated";
        closedBy: string;
        summary?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export type BaseDomainEvent = z.infer<typeof BaseDomainEventSchema>;
export type RecipeCreatedEvent = z.infer<typeof RecipeCreatedEventSchema>;
export type RecipeUpdatedEvent = z.infer<typeof RecipeUpdatedEventSchema>;
export type RecipeArchivedEvent = z.infer<typeof RecipeArchivedEventSchema>;
export type MixOrderCreatedEvent = z.infer<typeof MixOrderCreatedEventSchema>;
export type MixOrderStagedEvent = z.infer<typeof MixOrderStagedEventSchema>;
export type MixOrderStartedEvent = z.infer<typeof MixOrderStartedEventSchema>;
export type MixOrderCompletedEvent = z.infer<typeof MixOrderCompletedEventSchema>;
export type MixOrderAbortedEvent = z.infer<typeof MixOrderAbortedEventSchema>;
export type BatchCreatedEvent = z.infer<typeof BatchCreatedEventSchema>;
export type BatchReleasedEvent = z.infer<typeof BatchReleasedEventSchema>;
export type BatchQuarantinedEvent = z.infer<typeof BatchQuarantinedEventSchema>;
export type BatchRejectedEvent = z.infer<typeof BatchRejectedEventSchema>;
export type MobileRunStartedEvent = z.infer<typeof MobileRunStartedEventSchema>;
export type MobileRunFinishedEvent = z.infer<typeof MobileRunFinishedEventSchema>;
export type CleaningPerformedEvent = z.infer<typeof CleaningPerformedEventSchema>;
export type FlushPerformedEvent = z.infer<typeof FlushPerformedEventSchema>;
export type CalibrationCheckedEvent = z.infer<typeof CalibrationCheckedEventSchema>;
export type SamplingAddedEvent = z.infer<typeof SamplingAddedEventSchema>;
export type SamplingResultRecordedEvent = z.infer<typeof SamplingResultRecordedEventSchema>;
export type NonConformityCreatedEvent = z.infer<typeof NonConformityCreatedEventSchema>;
export type CAPACreatedEvent = z.infer<typeof CAPACreatedEventSchema>;
export type CAPAClosedEvent = z.infer<typeof CAPAClosedEventSchema>;
export type ProductionDomainEvent = RecipeCreatedEvent | RecipeUpdatedEvent | RecipeArchivedEvent | MixOrderCreatedEvent | MixOrderStagedEvent | MixOrderStartedEvent | MixOrderCompletedEvent | MixOrderAbortedEvent | BatchCreatedEvent | BatchReleasedEvent | BatchQuarantinedEvent | BatchRejectedEvent | MobileRunStartedEvent | MobileRunFinishedEvent | CleaningPerformedEvent | FlushPerformedEvent | CalibrationCheckedEvent | SamplingAddedEvent | SamplingResultRecordedEvent | NonConformityCreatedEvent | CAPACreatedEvent | CAPAClosedEvent;
export {};
//# sourceMappingURL=production-events.d.ts.map