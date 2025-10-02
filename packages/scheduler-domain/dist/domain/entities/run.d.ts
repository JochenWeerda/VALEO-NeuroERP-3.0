export type RunStatus = 'Pending' | 'Running' | 'Succeeded' | 'Failed' | 'Missed' | 'Dead';
export interface RunMetrics {
    latencyMs?: number;
    durationMs?: number;
}
export declare class RunEntity {
    readonly id: string;
    readonly tenantId: string;
    readonly scheduleId?: string;
    readonly jobId?: string;
    readonly dedupeKey?: string;
    readonly status: RunStatus;
    readonly startedAt?: Date;
    readonly finishedAt?: Date;
    readonly attempt: number;
    readonly error?: string;
    readonly metrics?: RunMetrics;
    readonly workerId?: string;
    readonly payload?: Record<string, any>;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    constructor(props: {
        id?: string;
        tenantId: string;
        scheduleId?: string;
        jobId?: string;
        dedupeKey?: string;
        status?: RunStatus;
        startedAt?: Date;
        finishedAt?: Date;
        attempt?: number;
        error?: string;
        metrics?: RunMetrics;
        workerId?: string;
        payload?: Record<string, any>;
        createdAt?: Date;
        updatedAt?: Date;
    });
    private validate;
    start(workerId?: string): RunEntity;
    succeed(): RunEntity;
    fail(error: string): RunEntity;
    markDead(error: string): RunEntity;
    markMissed(): RunEntity;
    isTerminal(): boolean;
    isActive(): boolean;
    isPending(): boolean;
    canRetry(): boolean;
    getDurationMs(): number | undefined;
    getLatencyMs(): number | undefined;
}
//# sourceMappingURL=run.d.ts.map