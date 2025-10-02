"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.JobEntity = void 0;
const uuid_1 = require("uuid");
class JobEntity {
    id;
    tenantId;
    key;
    queue;
    priority;
    maxAttempts;
    backoff;
    timeoutSec;
    concurrencyLimit;
    slaSec;
    enabled;
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id || (0, uuid_1.v4)();
        this.tenantId = props.tenantId;
        this.key = props.key;
        this.queue = props.queue || 'default';
        this.priority = Math.max(1, Math.min(9, props.priority || 5));
        this.maxAttempts = Math.max(1, props.maxAttempts || 3);
        this.backoff = props.backoff || { strategy: 'EXPONENTIAL', baseSec: 60 };
        this.timeoutSec = Math.max(1, props.timeoutSec || 300);
        this.concurrencyLimit = props.concurrencyLimit;
        this.slaSec = props.slaSec;
        this.enabled = props.enabled ?? true;
        this.createdAt = props.createdAt || new Date();
        this.updatedAt = props.updatedAt || new Date();
        this.version = props.version || 1;
        this.validate();
    }
    validate() {
        if (!this.tenantId) {
            throw new Error('tenantId is required');
        }
        if (!this.key) {
            throw new Error('key is required');
        }
        if (this.priority < 1 || this.priority > 9) {
            throw new Error('priority must be between 1 and 9');
        }
        if (this.maxAttempts < 1) {
            throw new Error('maxAttempts must be at least 1');
        }
        if (this.timeoutSec < 1) {
            throw new Error('timeoutSec must be at least 1');
        }
        if (this.concurrencyLimit !== undefined && this.concurrencyLimit < 1) {
            throw new Error('concurrencyLimit must be at least 1');
        }
        if (this.slaSec !== undefined && this.slaSec < 1) {
            throw new Error('slaSec must be at least 1');
        }
    }
    enable() {
        return new JobEntity({
            ...this,
            enabled: true,
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    disable() {
        return new JobEntity({
            ...this,
            enabled: false,
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    calculateBackoffDelay(attempt) {
        if (attempt <= 1)
            return 0;
        const attemptNum = attempt - 1;
        switch (this.backoff.strategy) {
            case 'FIXED':
                return Math.min(this.backoff.baseSec, this.backoff.maxSec || this.backoff.baseSec);
            case 'EXPONENTIAL':
                const delay = this.backoff.baseSec * Math.pow(2, attemptNum - 1);
                return this.backoff.maxSec ? Math.min(delay, this.backoff.maxSec) : delay;
            default:
                return this.backoff.baseSec;
        }
    }
    isSlaViolated(startedAt, finishedAt) {
        if (!this.slaSec)
            return false;
        const endTime = finishedAt || new Date();
        const durationSec = (endTime.getTime() - startedAt.getTime()) / 1000;
        return durationSec > this.slaSec;
    }
    getQueueKey() {
        return `${this.tenantId}:${this.queue}`;
    }
    getJobKey() {
        return `${this.tenantId}:${this.key}`;
    }
}
exports.JobEntity = JobEntity;
//# sourceMappingURL=job.js.map