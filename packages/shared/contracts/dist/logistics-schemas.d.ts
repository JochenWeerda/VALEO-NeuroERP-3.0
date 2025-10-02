import { z } from 'zod';
export declare const TemperatureRange: z.ZodObject<{
    minC: z.ZodNumber;
    maxC: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    minC: number;
    maxC: number;
}, {
    minC: number;
    maxC: number;
}>;
export type TemperatureRange = z.infer<typeof TemperatureRange>;
export declare const PayloadItem: z.ZodObject<{
    sscc: z.ZodOptional<z.ZodString>;
    description: z.ZodOptional<z.ZodString>;
    weightKg: z.ZodNumber;
    volumeM3: z.ZodOptional<z.ZodNumber>;
    tempRange: z.ZodOptional<z.ZodObject<{
        minC: z.ZodNumber;
        maxC: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        minC: number;
        maxC: number;
    }, {
        minC: number;
        maxC: number;
    }>>;
}, "strip", z.ZodTypeAny, {
    weightKg: number;
    description?: string | undefined;
    sscc?: string | undefined;
    volumeM3?: number | undefined;
    tempRange?: {
        minC: number;
        maxC: number;
    } | undefined;
}, {
    weightKg: number;
    description?: string | undefined;
    sscc?: string | undefined;
    volumeM3?: number | undefined;
    tempRange?: {
        minC: number;
        maxC: number;
    } | undefined;
}>;
export type PayloadItem = z.infer<typeof PayloadItem>;
export declare const StopType: z.ZodEnum<["pickup", "delivery", "cross-dock", "drop-off", "return"]>;
export type StopType = z.infer<typeof StopType>;
export declare const ShipmentStop: z.ZodObject<{
    sequence: z.ZodNumber;
    type: z.ZodEnum<["pickup", "delivery", "cross-dock", "drop-off", "return"]>;
    address: z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        coordinates: z.ZodOptional<z.ZodObject<{
            lat: z.ZodNumber;
            lon: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lon: number;
        }, {
            lat: number;
            lon: number;
        }>>;
        gln: z.ZodOptional<z.ZodString>;
        name: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }>;
    window: z.ZodOptional<z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>>;
    contactInfo: z.ZodOptional<z.ZodObject<{
        name: z.ZodOptional<z.ZodString>;
        phone: z.ZodOptional<z.ZodString>;
        instructions: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        name?: string | undefined;
        phone?: string | undefined;
        instructions?: string | undefined;
    }, {
        name?: string | undefined;
        phone?: string | undefined;
        instructions?: string | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
    address: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    sequence: number;
    window?: {
        from: string;
        to: string;
    } | undefined;
    contactInfo?: {
        name?: string | undefined;
        phone?: string | undefined;
        instructions?: string | undefined;
    } | undefined;
}, {
    type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
    address: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    sequence: number;
    window?: {
        from: string;
        to: string;
    } | undefined;
    contactInfo?: {
        name?: string | undefined;
        phone?: string | undefined;
        instructions?: string | undefined;
    } | undefined;
}>;
export type ShipmentStop = z.infer<typeof ShipmentStop>;
export declare const ShipmentPriority: z.ZodEnum<["standard", "express", "critical"]>;
export type ShipmentPriority = z.infer<typeof ShipmentPriority>;
export declare const Incoterm: z.ZodEnum<["EXW", "FCA", "CPT", "CIP", "DAT", "DAP", "DDP", "FAS", "FOB", "CFR", "CIF", "DES", "DEQ", "DDU"]>;
export declare const Shipment: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    reference: z.ZodOptional<z.ZodString>;
    origin: z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        coordinates: z.ZodOptional<z.ZodObject<{
            lat: z.ZodNumber;
            lon: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lon: number;
        }, {
            lat: number;
            lon: number;
        }>>;
        gln: z.ZodOptional<z.ZodString>;
        name: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }>;
    destination: z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        coordinates: z.ZodOptional<z.ZodObject<{
            lat: z.ZodNumber;
            lon: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lon: number;
        }, {
            lat: number;
            lon: number;
        }>>;
        gln: z.ZodOptional<z.ZodString>;
        name: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }>;
    stops: z.ZodArray<z.ZodObject<{
        sequence: z.ZodNumber;
        type: z.ZodEnum<["pickup", "delivery", "cross-dock", "drop-off", "return"]>;
        address: z.ZodObject<{
            street: z.ZodString;
            city: z.ZodString;
            postalCode: z.ZodString;
            country: z.ZodString;
            coordinates: z.ZodOptional<z.ZodObject<{
                lat: z.ZodNumber;
                lon: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                lat: number;
                lon: number;
            }, {
                lat: number;
                lon: number;
            }>>;
            gln: z.ZodOptional<z.ZodString>;
            name: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        }, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        }>;
        window: z.ZodOptional<z.ZodObject<{
            from: z.ZodString;
            to: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            from: string;
            to: string;
        }, {
            from: string;
            to: string;
        }>>;
        contactInfo: z.ZodOptional<z.ZodObject<{
            name: z.ZodOptional<z.ZodString>;
            phone: z.ZodOptional<z.ZodString>;
            instructions: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            name?: string | undefined;
            phone?: string | undefined;
            instructions?: string | undefined;
        }, {
            name?: string | undefined;
            phone?: string | undefined;
            instructions?: string | undefined;
        }>>;
    }, "strip", z.ZodTypeAny, {
        type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        };
        sequence: number;
        window?: {
            from: string;
            to: string;
        } | undefined;
        contactInfo?: {
            name?: string | undefined;
            phone?: string | undefined;
            instructions?: string | undefined;
        } | undefined;
    }, {
        type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        };
        sequence: number;
        window?: {
            from: string;
            to: string;
        } | undefined;
        contactInfo?: {
            name?: string | undefined;
            phone?: string | undefined;
            instructions?: string | undefined;
        } | undefined;
    }>, "many">;
    payload: z.ZodArray<z.ZodObject<{
        sscc: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodString>;
        weightKg: z.ZodNumber;
        volumeM3: z.ZodOptional<z.ZodNumber>;
        tempRange: z.ZodOptional<z.ZodObject<{
            minC: z.ZodNumber;
            maxC: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            minC: number;
            maxC: number;
        }, {
            minC: number;
            maxC: number;
        }>>;
    }, "strip", z.ZodTypeAny, {
        weightKg: number;
        description?: string | undefined;
        sscc?: string | undefined;
        volumeM3?: number | undefined;
        tempRange?: {
            minC: number;
            maxC: number;
        } | undefined;
    }, {
        weightKg: number;
        description?: string | undefined;
        sscc?: string | undefined;
        volumeM3?: number | undefined;
        tempRange?: {
            minC: number;
            maxC: number;
        } | undefined;
    }>, "many">;
    priority: z.ZodDefault<z.ZodEnum<["standard", "express", "critical"]>>;
    incoterm: z.ZodOptional<z.ZodEnum<["EXW", "FCA", "CPT", "CIP", "DAT", "DAP", "DDP", "FAS", "FOB", "CFR", "CIF", "DES", "DEQ", "DDU"]>>;
    status: z.ZodEnum<["NEW", "CONFIRMED", "PICKED_UP", "IN_TRANSIT", "DELIVERED", "CANCELLED"]>;
    tracking: z.ZodDefault<z.ZodArray<z.ZodObject<{
        status: z.ZodString;
        location: z.ZodOptional<z.ZodObject<{
            street: z.ZodString;
            city: z.ZodString;
            postalCode: z.ZodString;
            country: z.ZodString;
            coordinates: z.ZodOptional<z.ZodObject<{
                lat: z.ZodNumber;
                lon: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                lat: number;
                lon: number;
            }, {
                lat: number;
                lon: number;
            }>>;
            gln: z.ZodOptional<z.ZodString>;
            name: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        }, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        }>>;
        timestamp: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        status: string;
        timestamp: string;
        description?: string | undefined;
        location?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        } | undefined;
    }, {
        status: string;
        timestamp: string;
        description?: string | undefined;
        location?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        } | undefined;
    }>, "many">>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    estimatedDelivery: z.ZodOptional<z.ZodString>;
    actualDelivery: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: "CANCELLED" | "NEW" | "CONFIRMED" | "PICKED_UP" | "IN_TRANSIT" | "DELIVERED";
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    origin: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    destination: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    stops: {
        type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        };
        sequence: number;
        window?: {
            from: string;
            to: string;
        } | undefined;
        contactInfo?: {
            name?: string | undefined;
            phone?: string | undefined;
            instructions?: string | undefined;
        } | undefined;
    }[];
    payload: {
        weightKg: number;
        description?: string | undefined;
        sscc?: string | undefined;
        volumeM3?: number | undefined;
        tempRange?: {
            minC: number;
            maxC: number;
        } | undefined;
    }[];
    priority: "standard" | "express" | "critical";
    tracking: {
        status: string;
        timestamp: string;
        description?: string | undefined;
        location?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        } | undefined;
    }[];
    reference?: string | undefined;
    incoterm?: "EXW" | "FCA" | "CPT" | "CIP" | "DAT" | "DAP" | "DDP" | "FAS" | "FOB" | "CFR" | "CIF" | "DES" | "DEQ" | "DDU" | undefined;
    estimatedDelivery?: string | undefined;
    actualDelivery?: string | undefined;
}, {
    status: "CANCELLED" | "NEW" | "CONFIRMED" | "PICKED_UP" | "IN_TRANSIT" | "DELIVERED";
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    origin: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    destination: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    stops: {
        type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        };
        sequence: number;
        window?: {
            from: string;
            to: string;
        } | undefined;
        contactInfo?: {
            name?: string | undefined;
            phone?: string | undefined;
            instructions?: string | undefined;
        } | undefined;
    }[];
    payload: {
        weightKg: number;
        description?: string | undefined;
        sscc?: string | undefined;
        volumeM3?: number | undefined;
        tempRange?: {
            minC: number;
            maxC: number;
        } | undefined;
    }[];
    reference?: string | undefined;
    priority?: "standard" | "express" | "critical" | undefined;
    incoterm?: "EXW" | "FCA" | "CPT" | "CIP" | "DAT" | "DAP" | "DDP" | "FAS" | "FOB" | "CFR" | "CIF" | "DES" | "DEQ" | "DDU" | undefined;
    tracking?: {
        status: string;
        timestamp: string;
        description?: string | undefined;
        location?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        } | undefined;
    }[] | undefined;
    estimatedDelivery?: string | undefined;
    actualDelivery?: string | undefined;
}>;
export type Shipment = z.infer<typeof Shipment>;
export declare const CreateShipmentDto: z.ZodObject<{
    tenantId: z.ZodString;
    reference: z.ZodOptional<z.ZodString>;
    origin: z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        coordinates: z.ZodOptional<z.ZodObject<{
            lat: z.ZodNumber;
            lon: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lon: number;
        }, {
            lat: number;
            lon: number;
        }>>;
        gln: z.ZodOptional<z.ZodString>;
        name: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }>;
    destination: z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        coordinates: z.ZodOptional<z.ZodObject<{
            lat: z.ZodNumber;
            lon: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lon: number;
        }, {
            lat: number;
            lon: number;
        }>>;
        gln: z.ZodOptional<z.ZodString>;
        name: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }>;
    priority: z.ZodDefault<z.ZodEnum<["standard", "express", "critical"]>>;
    incoterm: z.ZodOptional<z.ZodEnum<["EXW", "FCA", "CPT", "CIP", "DAT", "DAP", "DDP", "FAS", "FOB", "CFR", "CIF", "DES", "DEQ", "DDU"]>>;
    stops: z.ZodArray<z.ZodObject<{
        sequence: z.ZodNumber;
        type: z.ZodEnum<["pickup", "delivery", "cross-dock", "drop-off", "return"]>;
        address: z.ZodObject<{
            street: z.ZodString;
            city: z.ZodString;
            postalCode: z.ZodString;
            country: z.ZodString;
            coordinates: z.ZodOptional<z.ZodObject<{
                lat: z.ZodNumber;
                lon: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                lat: number;
                lon: number;
            }, {
                lat: number;
                lon: number;
            }>>;
            gln: z.ZodOptional<z.ZodString>;
            name: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        }, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        }>;
        window: z.ZodOptional<z.ZodObject<{
            from: z.ZodString;
            to: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            from: string;
            to: string;
        }, {
            from: string;
            to: string;
        }>>;
    }, "strip", z.ZodTypeAny, {
        type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        };
        sequence: number;
        window?: {
            from: string;
            to: string;
        } | undefined;
    }, {
        type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        };
        sequence: number;
        window?: {
            from: string;
            to: string;
        } | undefined;
    }>, "many">;
    payload: z.ZodArray<z.ZodObject<{
        sscc: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodString>;
        weightKg: z.ZodNumber;
        volumeM3: z.ZodOptional<z.ZodNumber>;
        tempRange: z.ZodOptional<z.ZodObject<{
            minC: z.ZodNumber;
            maxC: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            minC: number;
            maxC: number;
        }, {
            minC: number;
            maxC: number;
        }>>;
    }, "strip", z.ZodTypeAny, {
        weightKg: number;
        description?: string | undefined;
        sscc?: string | undefined;
        volumeM3?: number | undefined;
        tempRange?: {
            minC: number;
            maxC: number;
        } | undefined;
    }, {
        weightKg: number;
        description?: string | undefined;
        sscc?: string | undefined;
        volumeM3?: number | undefined;
        tempRange?: {
            minC: number;
            maxC: number;
        } | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    origin: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    destination: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    stops: {
        type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        };
        sequence: number;
        window?: {
            from: string;
            to: string;
        } | undefined;
    }[];
    payload: {
        weightKg: number;
        description?: string | undefined;
        sscc?: string | undefined;
        volumeM3?: number | undefined;
        tempRange?: {
            minC: number;
            maxC: number;
        } | undefined;
    }[];
    priority: "standard" | "express" | "critical";
    reference?: string | undefined;
    incoterm?: "EXW" | "FCA" | "CPT" | "CIP" | "DAT" | "DAP" | "DDP" | "FAS" | "FOB" | "CFR" | "CIF" | "DES" | "DEQ" | "DDU" | undefined;
}, {
    tenantId: string;
    origin: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    destination: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    stops: {
        type: "pickup" | "delivery" | "cross-dock" | "drop-off" | "return";
        address: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        };
        sequence: number;
        window?: {
            from: string;
            to: string;
        } | undefined;
    }[];
    payload: {
        weightKg: number;
        description?: string | undefined;
        sscc?: string | undefined;
        volumeM3?: number | undefined;
        tempRange?: {
            minC: number;
            maxC: number;
        } | undefined;
    }[];
    reference?: string | undefined;
    priority?: "standard" | "express" | "critical" | undefined;
    incoterm?: "EXW" | "FCA" | "CPT" | "CIP" | "DAT" | "DAP" | "DDP" | "FAS" | "FOB" | "CFR" | "CIF" | "DES" | "DEQ" | "DDU" | undefined;
}>;
export declare const RoutePlan: z.ZodObject<{
    id: z.ZodString;
    shipmentId: z.ZodString;
    tenantId: z.ZodString;
    status: z.ZodEnum<["PLANNING", "PLANNED", "IN_PROGRESS", "COMPLETED", "CANCELLED"]>;
    totalDistanceKm: z.ZodNumber;
    estimatedDurationMinutes: z.ZodNumber;
    vehicleId: z.ZodOptional<z.ZodString>;
    driverId: z.ZodOptional<z.ZodString>;
    trailerId: z.ZodOptional<z.ZodString>;
    legs: z.ZodArray<z.ZodObject<{
        fromStopId: z.ZodString;
        toStopId: z.ZodString;
        distanceKm: z.ZodNumber;
        estimatedDurationMinutes: z.ZodNumber;
        etaFrom: z.ZodString;
        etaTo: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        estimatedDurationMinutes: number;
        fromStopId: string;
        toStopId: string;
        distanceKm: number;
        etaFrom: string;
        etaTo: string;
    }, {
        estimatedDurationMinutes: number;
        fromStopId: string;
        toStopId: string;
        distanceKm: number;
        etaFrom: string;
        etaTo: string;
    }>, "many">;
    plannedAt: z.ZodString;
    startedAt: z.ZodOptional<z.ZodString>;
    completedAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: "CANCELLED" | "COMPLETED" | "PLANNING" | "PLANNED" | "IN_PROGRESS";
    tenantId: string;
    id: string;
    shipmentId: string;
    totalDistanceKm: number;
    estimatedDurationMinutes: number;
    legs: {
        estimatedDurationMinutes: number;
        fromStopId: string;
        toStopId: string;
        distanceKm: number;
        etaFrom: string;
        etaTo: string;
    }[];
    plannedAt: string;
    completedAt?: string | undefined;
    vehicleId?: string | undefined;
    driverId?: string | undefined;
    trailerId?: string | undefined;
    startedAt?: string | undefined;
}, {
    status: "CANCELLED" | "COMPLETED" | "PLANNING" | "PLANNED" | "IN_PROGRESS";
    tenantId: string;
    id: string;
    shipmentId: string;
    totalDistanceKm: number;
    estimatedDurationMinutes: number;
    legs: {
        estimatedDurationMinutes: number;
        fromStopId: string;
        toStopId: string;
        distanceKm: number;
        etaFrom: string;
        etaTo: string;
    }[];
    plannedAt: string;
    completedAt?: string | undefined;
    vehicleId?: string | undefined;
    driverId?: string | undefined;
    trailerId?: string | undefined;
    startedAt?: string | undefined;
}>;
export type RoutePlan = z.infer<typeof RoutePlan>;
export declare const DispatchAssignment: z.ZodObject<{
    id: z.ZodString;
    routeId: z.ZodString;
    tenantId: z.ZodString;
    driverId: z.ZodString;
    vehicleId: z.ZodString;
    trailerId: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["ASSIGNED", "EN_ROUTE", "AT_STOP", "COMPLETED", "REASSIGNED"]>;
    assignedAt: z.ZodString;
    startedAt: z.ZodOptional<z.ZodString>;
    completedAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: "COMPLETED" | "ASSIGNED" | "EN_ROUTE" | "AT_STOP" | "REASSIGNED";
    tenantId: string;
    id: string;
    vehicleId: string;
    driverId: string;
    routeId: string;
    assignedAt: string;
    completedAt?: string | undefined;
    trailerId?: string | undefined;
    startedAt?: string | undefined;
}, {
    status: "COMPLETED" | "ASSIGNED" | "EN_ROUTE" | "AT_STOP" | "REASSIGNED";
    tenantId: string;
    id: string;
    vehicleId: string;
    driverId: string;
    routeId: string;
    assignedAt: string;
    completedAt?: string | undefined;
    trailerId?: string | undefined;
    startedAt?: string | undefined;
}>;
export type DispatchAssignment = z.infer<typeof DispatchAssignment>;
export declare const YardVisit: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    shipmentId: z.ZodString;
    gate: z.ZodString;
    dock: z.ZodOptional<z.ZodString>;
    scheduledWindow: z.ZodOptional<z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>>;
    actualArrival: z.ZodOptional<z.ZodString>;
    actualDeparture: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["SCHEDULED", "CHECKED_IN", "AT_DOCK", "LOADING", "UNLOADING", "CHECKED_OUT", "CANCELLED"]>;
}, "strip", z.ZodTypeAny, {
    status: "CANCELLED" | "SCHEDULED" | "CHECKED_IN" | "AT_DOCK" | "LOADING" | "UNLOADING" | "CHECKED_OUT";
    tenantId: string;
    id: string;
    shipmentId: string;
    gate: string;
    dock?: string | undefined;
    scheduledWindow?: {
        from: string;
        to: string;
    } | undefined;
    actualArrival?: string | undefined;
    actualDeparture?: string | undefined;
}, {
    status: "CANCELLED" | "SCHEDULED" | "CHECKED_IN" | "AT_DOCK" | "LOADING" | "UNLOADING" | "CHECKED_OUT";
    tenantId: string;
    id: string;
    shipmentId: string;
    gate: string;
    dock?: string | undefined;
    scheduledWindow?: {
        from: string;
        to: string;
    } | undefined;
    actualArrival?: string | undefined;
    actualDeparture?: string | undefined;
}>;
export type YardVisit = z.infer<typeof YardVisit>;
export declare const TelemetryRecord: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    vehicleId: z.ZodString;
    lat: z.ZodNumber;
    lon: z.ZodNumber;
    speedKph: z.ZodOptional<z.ZodNumber>;
    heading: z.ZodOptional<z.ZodNumber>;
    temperatureC: z.ZodOptional<z.ZodNumber>;
    fuelLevelPercent: z.ZodOptional<z.ZodNumber>;
    recordedAt: z.ZodString;
    meta: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
}, "strip", z.ZodTypeAny, {
    lat: number;
    lon: number;
    tenantId: string;
    id: string;
    vehicleId: string;
    recordedAt: string;
    speedKph?: number | undefined;
    heading?: number | undefined;
    temperatureC?: number | undefined;
    fuelLevelPercent?: number | undefined;
    meta?: Record<string, any> | undefined;
}, {
    lat: number;
    lon: number;
    tenantId: string;
    id: string;
    vehicleId: string;
    recordedAt: string;
    speedKph?: number | undefined;
    heading?: number | undefined;
    temperatureC?: number | undefined;
    fuelLevelPercent?: number | undefined;
    meta?: Record<string, any> | undefined;
}>;
export type TelemetryRecord = z.infer<typeof TelemetryRecord>;
export declare const ProofOfDelivery: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    shipmentId: z.ZodString;
    stopId: z.ZodString;
    signedBy: z.ZodString;
    signatureRef: z.ZodOptional<z.ZodString>;
    photoRefs: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    scans: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    exceptions: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    notes: z.ZodOptional<z.ZodString>;
    capturedAt: z.ZodString;
    syncedAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    id: string;
    shipmentId: string;
    stopId: string;
    signedBy: string;
    photoRefs: string[];
    scans: string[];
    exceptions: string[];
    capturedAt: string;
    notes?: string | undefined;
    signatureRef?: string | undefined;
    syncedAt?: string | undefined;
}, {
    tenantId: string;
    id: string;
    shipmentId: string;
    stopId: string;
    signedBy: string;
    capturedAt: string;
    notes?: string | undefined;
    signatureRef?: string | undefined;
    photoRefs?: string[] | undefined;
    scans?: string[] | undefined;
    exceptions?: string[] | undefined;
    syncedAt?: string | undefined;
}>;
export type ProofOfDelivery = z.infer<typeof ProofOfDelivery>;
export declare const WeighingRecord: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    shipmentId: z.ZodString;
    grossWeightKg: z.ZodNumber;
    tareWeightKg: z.ZodNumber;
    netWeightKg: z.ZodNumber;
    source: z.ZodEnum<["bridge", "sensor", "manual"]>;
    measuredAt: z.ZodString;
    recordedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    id: string;
    shipmentId: string;
    recordedAt: string;
    grossWeightKg: number;
    tareWeightKg: number;
    netWeightKg: number;
    source: "bridge" | "sensor" | "manual";
    measuredAt: string;
}, {
    tenantId: string;
    id: string;
    shipmentId: string;
    recordedAt: string;
    grossWeightKg: number;
    tareWeightKg: number;
    netWeightKg: number;
    source: "bridge" | "sensor" | "manual";
    measuredAt: string;
}>;
export type WeighingRecord = z.infer<typeof WeighingRecord>;
export declare const FreightRate: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    baseAmount: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    surcharges: z.ZodDefault<z.ZodArray<z.ZodObject<{
        type: z.ZodString;
        amount: z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        type: string;
        amount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        description?: string | undefined;
    }, {
        type: string;
        amount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        description?: string | undefined;
    }>, "many">>;
    validFrom: z.ZodString;
    validTo: z.ZodOptional<z.ZodString>;
    minWeightKg: z.ZodOptional<z.ZodNumber>;
    maxWeightKg: z.ZodOptional<z.ZodNumber>;
    zones: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    rateCardId: z.ZodOptional<z.ZodString>;
    explanation: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    id: string;
    baseAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    surcharges: {
        type: string;
        amount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        description?: string | undefined;
    }[];
    validFrom: string;
    validTo?: string | undefined;
    minWeightKg?: number | undefined;
    maxWeightKg?: number | undefined;
    zones?: string[] | undefined;
    rateCardId?: string | undefined;
    explanation?: string | undefined;
}, {
    tenantId: string;
    id: string;
    baseAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    validFrom: string;
    surcharges?: {
        type: string;
        amount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        description?: string | undefined;
    }[] | undefined;
    validTo?: string | undefined;
    minWeightKg?: number | undefined;
    maxWeightKg?: number | undefined;
    zones?: string[] | undefined;
    rateCardId?: string | undefined;
    explanation?: string | undefined;
}>;
export type FreightRate = z.infer<typeof FreightRate>;
export declare const EmissionRecord: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    shipmentId: z.ZodString;
    co2eKg: z.ZodNumber;
    method: z.ZodString;
    factors: z.ZodDefault<z.ZodArray<z.ZodObject<{
        factor: z.ZodString;
        value: z.ZodNumber;
        unit: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        value: number;
        factor: string;
        unit: string;
    }, {
        value: number;
        factor: string;
        unit: string;
    }>, "many">>;
    calculatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    id: string;
    method: string;
    shipmentId: string;
    co2eKg: number;
    factors: {
        value: number;
        factor: string;
        unit: string;
    }[];
    calculatedAt: string;
}, {
    tenantId: string;
    id: string;
    method: string;
    shipmentId: string;
    co2eKg: number;
    calculatedAt: string;
    factors?: {
        value: number;
        factor: string;
        unit: string;
    }[] | undefined;
}>;
export type EmissionRecord = z.infer<typeof EmissionRecord>;
export declare const SafetyAlert: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    referenceId: z.ZodString;
    type: z.ZodEnum<["dangerous_goods", "temperature", "geofence", "weight", "speed", "maintenance"]>;
    severity: z.ZodEnum<["info", "warning", "critical"]>;
    message: z.ZodString;
    location: z.ZodOptional<z.ZodObject<{
        lat: z.ZodNumber;
        lon: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        lat: number;
        lon: number;
    }, {
        lat: number;
        lon: number;
    }>>;
    status: z.ZodEnum<["ACTIVE", "ACKNOWLEDGED", "RESOLVED"]>;
    acknowledgedBy: z.ZodOptional<z.ZodString>;
    acknowledgedAt: z.ZodOptional<z.ZodString>;
    raisedAt: z.ZodString;
    resolvedAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    message: string;
    type: "dangerous_goods" | "temperature" | "geofence" | "weight" | "speed" | "maintenance";
    status: "ACTIVE" | "ACKNOWLEDGED" | "RESOLVED";
    tenantId: string;
    id: string;
    referenceId: string;
    severity: "critical" | "info" | "warning";
    raisedAt: string;
    location?: {
        lat: number;
        lon: number;
    } | undefined;
    acknowledgedBy?: string | undefined;
    acknowledgedAt?: string | undefined;
    resolvedAt?: string | undefined;
}, {
    message: string;
    type: "dangerous_goods" | "temperature" | "geofence" | "weight" | "speed" | "maintenance";
    status: "ACTIVE" | "ACKNOWLEDGED" | "RESOLVED";
    tenantId: string;
    id: string;
    referenceId: string;
    severity: "critical" | "info" | "warning";
    raisedAt: string;
    location?: {
        lat: number;
        lon: number;
    } | undefined;
    acknowledgedBy?: string | undefined;
    acknowledgedAt?: string | undefined;
    resolvedAt?: string | undefined;
}>;
export type SafetyAlert = z.infer<typeof SafetyAlert>;
export declare const ReturnOrder: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    originalShipmentId: z.ZodString;
    pickupAddress: z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        coordinates: z.ZodOptional<z.ZodObject<{
            lat: z.ZodNumber;
            lon: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lon: number;
        }, {
            lat: number;
            lon: number;
        }>>;
        gln: z.ZodOptional<z.ZodString>;
        name: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }>;
    returnReason: z.ZodString;
    items: z.ZodArray<z.ZodObject<{
        originalItemId: z.ZodString;
        quantity: z.ZodNumber;
        reason: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        quantity: number;
        originalItemId: string;
        reason?: string | undefined;
    }, {
        quantity: number;
        originalItemId: string;
        reason?: string | undefined;
    }>, "many">;
    status: z.ZodEnum<["REQUESTED", "APPROVED", "SCHEDULED", "PICKED_UP", "DELIVERED", "CANCELLED"]>;
    requestedAt: z.ZodString;
    approvedAt: z.ZodOptional<z.ZodString>;
    scheduledAt: z.ZodOptional<z.ZodString>;
    completedAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: "CANCELLED" | "APPROVED" | "PICKED_UP" | "DELIVERED" | "SCHEDULED" | "REQUESTED";
    tenantId: string;
    items: {
        quantity: number;
        originalItemId: string;
        reason?: string | undefined;
    }[];
    id: string;
    originalShipmentId: string;
    pickupAddress: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    returnReason: string;
    requestedAt: string;
    completedAt?: string | undefined;
    approvedAt?: string | undefined;
    scheduledAt?: string | undefined;
}, {
    status: "CANCELLED" | "APPROVED" | "PICKED_UP" | "DELIVERED" | "SCHEDULED" | "REQUESTED";
    tenantId: string;
    items: {
        quantity: number;
        originalItemId: string;
        reason?: string | undefined;
    }[];
    id: string;
    originalShipmentId: string;
    pickupAddress: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    returnReason: string;
    requestedAt: string;
    completedAt?: string | undefined;
    approvedAt?: string | undefined;
    scheduledAt?: string | undefined;
}>;
export type ReturnOrder = z.infer<typeof ReturnOrder>;
//# sourceMappingURL=logistics-schemas.d.ts.map