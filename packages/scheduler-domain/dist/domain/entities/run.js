"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RunEntity = void 0;
const uuid_1 = require("uuid");
class RunEntity {
    id;
    tenantId;
    scheduleId;
    jobId;
    dedupeKey;
    status;
    startedAt;
    finishedAt;
    attempt;
    error;
    metrics;
    workerId;
    payload;
    createdAt;
    updatedAt;
    constructor(props) {
        this.id = props.id || (0, uuid_1.v4)();
        this.tenantId = props.tenantId;
        this.scheduleId = props.scheduleId;
        this.jobId = props.jobId;
        this.dedupeKey = props.dedupeKey;
        this.status = props.status || 'Pending';
        this.startedAt = props.startedAt;
        this.finishedAt = props.finishedAt;
        this.attempt = Math.max(1, props.attempt || 1);
        this.error = props.error;
        this.metrics = props.metrics;
        this.workerId = props.workerId;
        this.payload = props.payload;
        this.createdAt = props.createdAt || new Date();
        this.updatedAt = props.updatedAt || new Date();
        this.validate();
    }
    validate() {
        if (!this.tenantId) {
            throw new Error('tenantId is required');
        }
        if (!this.scheduleId && !this.jobId) {
            throw new Error('Either scheduleId or jobId must be provided');
        }
        if (this.scheduleId && this.jobId) {
            throw new Error('Cannot have both scheduleId and jobId');
        }
        if (this.attempt < 1) {
            throw new Error('attempt must be at least 1');
        }
    }
    start(workerId) {
        if (this.status !== 'Pending') {
            throw new Error(`Cannot start run in status: ${this.status}`);
        }
        const now = new Date();
        const latencyMs = this.createdAt ? now.getTime() - this.createdAt.getTime() : undefined;
        return new RunEntity({
            ...this,
            status: 'Running',
            startedAt: now,
            workerId,
            metrics: {
                ...this.metrics,
                latencyMs,
            },
            updatedAt: now,
        });
    }
    succeed() {
        if (this.status !== 'Running') {
            throw new Error(`Cannot succeed run in status: ${this.status}`);
        }
        const now = new Date();
        const durationMs = this.startedAt ? now.getTime() - this.startedAt.getTime() : undefined;
        return new RunEntity({
            ...this,
            status: 'Succeeded',
            finishedAt: now,
            metrics: {
                ...this.metrics,
                durationMs,
            },
            updatedAt: now,
        });
    }
    fail(error) {
        if (this.status !== 'Running') {
            throw new Error(`Cannot fail run in status: ${this.status}`);
        }
        const now = new Date();
        const durationMs = this.startedAt ? now.getTime() - this.startedAt.getTime() : undefined;
        return new RunEntity({
            ...this,
            status: 'Failed',
            finishedAt: now,
            error,
            metrics: {
                ...this.metrics,
                durationMs,
            },
            updatedAt: now,
        });
    }
    markDead(error) {
        const now = new Date();
        return new RunEntity({
            ...this,
            status: 'Dead',
            finishedAt: now,
            error,
            updatedAt: now,
        });
    }
    markMissed() {
        if (this.status !== 'Pending') {
            throw new Error(`Cannot mark as missed in status: ${this.status}`);
        }
        return new RunEntity({
            ...this,
            status: 'Missed',
            finishedAt: new Date(),
            updatedAt: new Date(),
        });
    }
    isTerminal() {
        return ['Succeeded', 'Failed', 'Dead', 'Missed'].includes(this.status);
    }
    isActive() {
        return this.status === 'Running';
    }
    isPending() {
        return this.status === 'Pending';
    }
    canRetry() {
        return this.status === 'Failed' && this.error !== undefined;
    }
    getDurationMs() {
        if (!this.startedAt || !this.finishedAt)
            return undefined;
        return this.finishedAt.getTime() - this.startedAt.getTime();
    }
    getLatencyMs() {
        if (!this.createdAt || !this.startedAt)
            return undefined;
        return this.startedAt.getTime() - this.createdAt.getTime();
    }
}
exports.RunEntity = RunEntity;
//# sourceMappingURL=run.js.map