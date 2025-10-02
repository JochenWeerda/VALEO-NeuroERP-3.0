export interface CreateShipmentDto {
    tenantId: string;
    reference?: string;
    origin: {
        gln?: string;
        name?: string;
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        };
    };
    destination: {
        gln?: string;
        name?: string;
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        };
    };
    priority?: 'standard' | 'express' | 'critical';
    incoterm?: string;
    stops: Array<{
        sequence: number;
        type: 'pickup' | 'delivery' | 'cross-dock' | 'drop-off' | 'return';
        address: {
            gln?: string;
            name?: string;
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            };
        };
        window?: {
            from: string;
            to: string;
        };
    }>;
    payload: Array<{
        sscc?: string;
        description?: string;
        weightKg: number;
        volumeM3?: number;
        tempRange?: {
            minC: number;
            maxC: number;
        };
    }>;
}
export interface ShipmentResponseDto {
    shipmentId: string;
    status: string;
}
export interface RoutingPlanRequestDto {
    tenantId: string;
    shipmentId: string;
    vehicleId?: string;
    driverId?: string;
    distanceKm: number;
    legs: Array<{
        fromStopId: string;
        toStopId: string;
        distanceKm: number;
        etaFrom: string;
        etaTo: string;
    }>;
}
export interface DispatchAssignDto {
    tenantId: string;
    routeId: string;
    driverId: string;
    vehicleId: string;
    trailerId?: string;
}
export interface SlotBookingDto {
    tenantId: string;
    shipmentId: string;
    gate: string;
    dock?: string;
    window?: {
        from: string;
        to: string;
    };
}
export interface TelemetryPushDto {
    tenantId: string;
    vehicleId: string;
    recordedAt: string;
    lat: number;
    lon: number;
    speedKph?: number;
    temperatureC?: number;
    fuelLevelPercent?: number;
    meta?: Record<string, unknown>;
}
export interface CapturePodDto {
    tenantId: string;
    shipmentId: string;
    stopId: string;
    signedBy: string;
    signatureRef?: string;
    photoRefs?: string[];
    scans?: string[];
    exceptions?: string[];
}
export interface WeighingCaptureDto {
    tenantId: string;
    shipmentId: string;
    grossWeightKg: number;
    tareWeightKg: number;
    source: 'bridge' | 'sensor';
}
export interface FreightQuoteRequestDto {
    tenantId: string;
    shipmentId: string;
    currency: string;
    baseAmount: number;
    surcharges?: Array<{
        type: string;
        amount: number;
    }>;
    explain?: string;
}
export interface EmissionCalcDto {
    tenantId: string;
    shipmentId: string;
    co2eKg: number;
    method: string;
    factors?: Array<{
        factor: string;
        value: number;
        unit: string;
    }>;
}
export interface SafetyValidationDto {
    tenantId: string;
    referenceId: string;
    shipmentId?: string;
    type: 'dangerous_goods' | 'temperature' | 'geofence' | 'weight';
    severity: 'info' | 'warning' | 'critical';
    message: string;
}
export interface ReturnRequestDto {
    tenantId: string;
    originalShipmentId: string;
    pickupAddress: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
    };
    returnReason: string;
}
export interface CostingApplyDto {
    tenantId: string;
    shipmentId: string;
    total: number;
    currency: string;
    breakdown: Array<{
        type: string;
        amount: number;
        description?: string;
    }>;
}
//# sourceMappingURL=logistics-dtos.d.ts.map