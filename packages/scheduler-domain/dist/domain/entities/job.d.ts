export type JobStatus = 'Active' | 'Paused' | 'Disabled';
export type BackoffStrategy = 'FIXED' | 'EXPONENTIAL';
export interface BackoffConfig {
    strategy: BackoffStrategy;
    baseSec: number;
    maxSec?: number;
}
export declare class JobEntity {
    readonly id: string;
    readonly tenantId: string;
    readonly key: string;
    readonly queue: string;
    readonly priority: number;
    readonly maxAttempts: number;
    readonly backoff: BackoffConfig;
    readonly timeoutSec: number;
    readonly concurrencyLimit?: number;
    readonly slaSec?: number;
    readonly enabled: boolean;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    readonly version: number;
    constructor(props: {
        id?: string;
        tenantId: string;
        key: string;
        queue?: string;
        priority?: number;
        maxAttempts?: number;
        backoff?: BackoffConfig;
        timeoutSec?: number;
        concurrencyLimit?: number;
        slaSec?: number;
        enabled?: boolean;
        createdAt?: Date;
        updatedAt?: Date;
        version?: number;
    });
    private validate;
    enable(): JobEntity;
    disable(): JobEntity;
    calculateBackoffDelay(attempt: number): number;
    isSlaViolated(startedAt: Date, finishedAt?: Date): boolean;
    getQueueKey(): string;
    getJobKey(): string;
}
//# sourceMappingURL=job.d.ts.map