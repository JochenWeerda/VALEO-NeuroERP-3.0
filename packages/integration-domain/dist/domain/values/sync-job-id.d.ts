/**
 * Sync Job ID Value Object
 */
export declare class SyncJobId {
    private readonly _value;
    private constructor();
    static create(): SyncJobId;
    static fromString(value: string): SyncJobId;
    get value(): string;
    equals(other: SyncJobId): boolean;
    toString(): string;
    toJSON(): string;
}
//# sourceMappingURL=sync-job-id.d.ts.map