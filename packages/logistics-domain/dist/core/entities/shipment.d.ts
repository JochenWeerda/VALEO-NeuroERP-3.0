import { Address, AddressProps } from '../value-objects/address';
import { TimeWindow, TimeWindowProps } from '../value-objects/time-window';
import { TemperatureRange, TemperatureRangeProps } from '../value-objects/temperature-range';
type StopType = 'pickup' | 'delivery' | 'cross-dock' | 'drop-off' | 'return';
export interface ShipmentStopProps {
    readonly stopId?: string;
    readonly sequence: number;
    readonly type: StopType;
    readonly address: AddressProps;
    readonly window?: TimeWindowProps;
}
export interface ShipmentPayloadItemProps {
    readonly sscc?: string;
    readonly description?: string;
    readonly weightKg: number;
    readonly volumeM3?: number;
    readonly tempRange?: TemperatureRangeProps;
}
export type ShipmentStatus = 'draft' | 'planned' | 'in_transit' | 'completed' | 'canceled';
export interface ShipmentProps {
    readonly shipmentId?: string;
    readonly tenantId: string;
    readonly reference?: string;
    readonly origin: AddressProps;
    readonly destination: AddressProps;
    readonly priority?: 'standard' | 'express' | 'critical';
    readonly incoterm?: string;
    readonly stops: ShipmentStopProps[];
    readonly payload: ShipmentPayloadItemProps[];
    readonly status?: ShipmentStatus;
    readonly createdAt?: Date;
}
export declare class ShipmentStop {
    readonly stopId: string;
    readonly sequence: number;
    readonly type: StopType;
    readonly address: Address;
    readonly window?: TimeWindow;
    constructor(props: ShipmentStopProps);
}
export declare class ShipmentPayloadItem {
    readonly sscc?: string;
    readonly description?: string;
    readonly weightKg: number;
    readonly volumeM3?: number;
    readonly tempRange?: TemperatureRange;
    constructor(props: ShipmentPayloadItemProps);
}
export declare class Shipment {
    readonly shipmentId: string;
    readonly tenantId: string;
    readonly reference?: string;
    readonly origin: Address;
    readonly destination: Address;
    readonly priority: 'standard' | 'express' | 'critical';
    readonly incoterm?: string;
    readonly createdAt: Date;
    private _status;
    private readonly stops;
    private readonly payload;
    private constructor();
    static create(props: ShipmentProps): Shipment;
    get status(): ShipmentStatus;
    updateStatus(status: ShipmentStatus): void;
    getStops(): ShipmentStop[];
    getPayload(): ShipmentPayloadItem[];
    toJSON(): Record<string, unknown>;
}
export {};
//# sourceMappingURL=shipment.d.ts.map