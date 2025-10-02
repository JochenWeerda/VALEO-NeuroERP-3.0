/**
 * API Key ID Value Object
 */
export declare class ApiKeyId {
    private readonly _value;
    private constructor();
    static create(): ApiKeyId;
    static fromString(value: string): ApiKeyId;
    get value(): string;
    equals(other: ApiKeyId): boolean;
    toString(): string;
    toJSON(): string;
}
//# sourceMappingURL=api-key-id.d.ts.map