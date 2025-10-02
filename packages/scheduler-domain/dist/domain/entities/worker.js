"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WorkerEntity = void 0;
const uuid_1 = require("uuid");
class WorkerEntity {
    id;
    tenantId;
    name;
    capabilities;
    heartbeatAt;
    status;
    maxParallel;
    currentJobs;
    version;
    createdAt;
    updatedAt;
    constructor(props) {
        this.id = props.id || (0, uuid_1.v4)();
        this.tenantId = props.tenantId;
        this.name = props.name;
        this.capabilities = props.capabilities;
        this.heartbeatAt = props.heartbeatAt || new Date();
        this.status = props.status || 'Online';
        this.maxParallel = Math.max(1, props.maxParallel || 10);
        this.currentJobs = Math.max(0, props.currentJobs || 0);
        this.version = props.version || 1;
        this.createdAt = props.createdAt || new Date();
        this.updatedAt = props.updatedAt || new Date();
        this.validate();
    }
    validate() {
        if (!this.name) {
            throw new Error('name is required');
        }
        if (!this.capabilities) {
            throw new Error('capabilities is required');
        }
        if (!Array.isArray(this.capabilities.queues)) {
            throw new Error('capabilities.queues must be an array');
        }
        if (!Array.isArray(this.capabilities.jobKeys)) {
            throw new Error('capabilities.jobKeys must be an array');
        }
        if (this.maxParallel < 1) {
            throw new Error('maxParallel must be at least 1');
        }
        if (this.currentJobs < 0) {
            throw new Error('currentJobs cannot be negative');
        }
        if (this.currentJobs > this.maxParallel) {
            throw new Error('currentJobs cannot exceed maxParallel');
        }
    }
    heartbeat() {
        const now = new Date();
        return new WorkerEntity({
            ...this,
            heartbeatAt: now,
            status: 'Online',
            updatedAt: now,
            version: this.version + 1,
        });
    }
    goOffline() {
        return new WorkerEntity({
            ...this,
            status: 'Offline',
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    goOnline() {
        return new WorkerEntity({
            ...this,
            status: 'Online',
            heartbeatAt: new Date(),
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    startJob() {
        if (this.currentJobs >= this.maxParallel) {
            throw new Error('Worker at maximum capacity');
        }
        return new WorkerEntity({
            ...this,
            currentJobs: this.currentJobs + 1,
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    finishJob() {
        if (this.currentJobs <= 0) {
            throw new Error('No jobs currently running');
        }
        return new WorkerEntity({
            ...this,
            currentJobs: this.currentJobs - 1,
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    canHandleQueue(queue) {
        return this.capabilities.queues.includes(queue) || this.capabilities.queues.includes('*');
    }
    canHandleJob(jobKey) {
        return this.capabilities.jobKeys.includes(jobKey) || this.capabilities.jobKeys.includes('*');
    }
    canAcceptJob(queue, jobKey) {
        if (this.status !== 'Online')
            return false;
        if (this.currentJobs >= this.maxParallel)
            return false;
        if (!this.canHandleQueue(queue))
            return false;
        if (jobKey && !this.canHandleJob(jobKey))
            return false;
        return true;
    }
    isHealthy(heartbeatTimeoutSec = 300) {
        const now = new Date();
        const timeSinceHeartbeat = (now.getTime() - this.heartbeatAt.getTime()) / 1000;
        return timeSinceHeartbeat <= heartbeatTimeoutSec;
    }
    getAvailableSlots() {
        return Math.max(0, this.maxParallel - this.currentJobs);
    }
    getUtilizationPercentage() {
        return this.maxParallel > 0 ? (this.currentJobs / this.maxParallel) * 100 : 0;
    }
}
exports.WorkerEntity = WorkerEntity;
//# sourceMappingURL=worker.js.map