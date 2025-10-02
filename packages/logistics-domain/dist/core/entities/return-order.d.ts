import { Address, AddressProps } from '../value-objects/address';
export type ReturnStatus = 'requested' | 'scheduled' | 'picked_up' | 'received' | 'closed';
export interface ReturnOrderProps {
    readonly returnId?: string;
    readonly tenantId: string;
    readonly originalShipmentId: string;
    readonly pickupAddress: AddressProps;
    readonly returnReason: string;
    readonly status?: ReturnStatus;
    readonly requestedAt?: Date;
}
export declare class ReturnOrder {
    readonly returnId: string;
    readonly tenantId: string;
    readonly originalShipmentId: string;
    readonly pickupAddress: Address;
    readonly returnReason: string;
    readonly requestedAt: Date;
    private _status;
    private constructor();
    static create(props: ReturnOrderProps): ReturnOrder;
    get status(): ReturnStatus;
    updateStatus(status: ReturnStatus): void;
}
//# sourceMappingURL=return-order.d.ts.map