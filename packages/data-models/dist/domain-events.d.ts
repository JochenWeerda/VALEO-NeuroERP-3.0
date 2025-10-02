export interface DomainEvent {
    readonly id: string;
    readonly type: string;
    readonly aggregateId: string;
    readonly aggregateType: string;
    readonly version: number;
    readonly occurredOn: Date;
    readonly data: Record<string, unknown>;
}
export interface CustomerCreatedEvent extends DomainEvent {
    readonly type: 'CustomerCreated';
    readonly data: {
        customerId: string;
        email: string;
        name: string;
    };
}
export interface ProductCreatedEvent extends DomainEvent {
    readonly type: 'ProductCreated';
    readonly data: {
        productId: string;
        name: string;
        price: number;
    };
}
export type AnyDomainEvent = CustomerCreatedEvent | ProductCreatedEvent;
//# sourceMappingURL=domain-events.d.ts.map