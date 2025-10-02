/**
 * Integration ID Value Object
 */
export declare class IntegrationId {
    private readonly _value;
    private constructor();
    static create(): IntegrationId;
    static fromString(value: string): IntegrationId;
    get value(): string;
    equals(other: IntegrationId): boolean;
    toString(): string;
    toJSON(): string;
}
//# sourceMappingURL=integration-id.d.ts.map