export type WorkerStatus = 'Online' | 'Offline' | 'Maintenance';
export interface WorkerCapabilities {
    queues: string[];
    jobKeys: string[];
}
export declare class WorkerEntity {
    readonly id: string;
    readonly tenantId?: string;
    readonly name: string;
    readonly capabilities: WorkerCapabilities;
    readonly heartbeatAt: Date;
    readonly status: WorkerStatus;
    readonly maxParallel: number;
    readonly currentJobs: number;
    readonly version: number;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    constructor(props: {
        id?: string;
        tenantId?: string;
        name: string;
        capabilities: WorkerCapabilities;
        heartbeatAt?: Date;
        status?: WorkerStatus;
        maxParallel?: number;
        currentJobs?: number;
        version?: number;
        createdAt?: Date;
        updatedAt?: Date;
    });
    private validate;
    heartbeat(): WorkerEntity;
    goOffline(): WorkerEntity;
    goOnline(): WorkerEntity;
    startJob(): WorkerEntity;
    finishJob(): WorkerEntity;
    canHandleQueue(queue: string): boolean;
    canHandleJob(jobKey: string): boolean;
    canAcceptJob(queue: string, jobKey?: string): boolean;
    isHealthy(heartbeatTimeoutSec?: number): boolean;
    getAvailableSlots(): number;
    getUtilizationPercentage(): number;
}
//# sourceMappingURL=worker.d.ts.map