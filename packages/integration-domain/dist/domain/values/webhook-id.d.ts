/**
 * Webhook ID Value Object
 */
export declare class WebhookId {
    private readonly _value;
    private constructor();
    static create(): WebhookId;
    static fromString(value: string): WebhookId;
    get value(): string;
    equals(other: WebhookId): boolean;
    toString(): string;
    toJSON(): string;
}
//***REMOVED*** sourceMappingURL=webhook-id.d.ts.map