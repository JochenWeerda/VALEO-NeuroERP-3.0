/**
 * VALEO NeuroERP 3.0 - Location Entity
 *
 * Represents warehouse locations with capacity and zoning
 */
export type LocationType = 'pick' | 'reserve' | 'bulk' | 'qc' | 'dock' | 'yard' | 'staging' | 'returns';
export type ZoneType = 'A' | 'B' | 'C' | 'D' | 'frozen' | 'refrigerated' | 'ambient' | 'heated' | 'hazmat';
export interface LocationAttributes {
    locationId: string;
    code: string;
    type: LocationType;
    zone: ZoneType;
    aisle?: string;
    rack?: string;
    shelf?: string;
    bin?: string;
    capacity: {
        maxQty?: number;
        maxWeight?: number;
        maxVolume?: number;
        uom: string;
    };
    dimensions?: {
        length: number;
        width: number;
        height: number;
    };
    coordinates?: {
        x: number;
        y: number;
        z: number;
    };
    tempControlled: boolean;
    tempMin?: number;
    tempMax?: number;
    hazmatAllowed: boolean;
    active: boolean;
    blocked: boolean;
    blockReason?: string;
    lastCount?: Date;
    createdAt: Date;
    updatedAt: Date;
}
export declare class Location {
    private _attributes;
    constructor(attributes: Omit<LocationAttributes, 'createdAt' | 'updatedAt'>);
    get locationId(): string;
    get code(): string;
    get type(): LocationType;
    get zone(): ZoneType;
    get capacity(): LocationAttributes['capacity'];
    get active(): boolean;
    get blocked(): boolean;
    get tempControlled(): boolean;
    get hazmatAllowed(): boolean;
    get attributes(): LocationAttributes;
    isPickLocation(): boolean;
    isReserveLocation(): boolean;
    isQuarantineLocation(): boolean;
    canStoreSku(sku: {
        tempZone: string;
        hazmat: boolean;
        weight?: number;
        volume?: number;
    }): boolean;
    getDistanceTo(otherLocation: Location): number;
    block(reason: string): void;
    unblock(): void;
    updateCapacity(newCapacity: Partial<LocationAttributes['capacity']>): void;
    recordCount(): void;
    deactivate(): void;
    activate(): void;
    private validate;
    static create(attributes: Omit<LocationAttributes, 'locationId' | 'createdAt' | 'updatedAt'>): Location;
    static fromAttributes(attributes: LocationAttributes): Location;
    getFullAddress(): string;
    isInZone(zone: ZoneType): boolean;
    supportsTemperature(tempZone: string): boolean;
}
//# sourceMappingURL=location.d.ts.map