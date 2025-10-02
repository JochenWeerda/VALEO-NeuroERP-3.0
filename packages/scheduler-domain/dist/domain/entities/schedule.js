"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ScheduleEntity = void 0;
const uuid_1 = require("uuid");
class ScheduleEntity {
    id;
    tenantId;
    name;
    description;
    tz;
    trigger;
    target;
    payload;
    calendar;
    enabled;
    nextFireAt;
    lastFireAt;
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id || (0, uuid_1.v4)();
        this.tenantId = props.tenantId;
        this.name = props.name;
        this.description = props.description;
        this.tz = props.tz;
        this.trigger = props.trigger;
        this.target = props.target;
        this.payload = props.payload;
        this.calendar = props.calendar;
        this.enabled = props.enabled ?? true;
        this.nextFireAt = props.nextFireAt;
        this.lastFireAt = props.lastFireAt;
        this.createdAt = props.createdAt || new Date();
        this.updatedAt = props.updatedAt || new Date();
        this.version = props.version || 1;
        this.validate();
    }
    validate() {
        if (!this.tenantId) {
            throw new Error('tenantId is required');
        }
        if (!this.name) {
            throw new Error('name is required');
        }
        if (!this.tz) {
            throw new Error('tz is required');
        }
        this.validateTrigger();
        this.validateTarget();
    }
    validateTrigger() {
        switch (this.trigger.type) {
            case 'CRON':
                if (!this.trigger.cron) {
                    throw new Error('cron expression is required for CRON trigger');
                }
                break;
            case 'RRULE':
                if (!this.trigger.rrule) {
                    throw new Error('rrule is required for RRULE trigger');
                }
                break;
            case 'FIXED_DELAY':
                if (!this.trigger.delaySec || this.trigger.delaySec <= 0) {
                    throw new Error('delaySec must be positive for FIXED_DELAY trigger');
                }
                break;
            case 'ONE_SHOT':
                if (!this.trigger.startAt) {
                    throw new Error('startAt is required for ONE_SHOT trigger');
                }
                break;
            default:
                throw new Error(`Unknown trigger type: ${this.trigger.type}`);
        }
    }
    validateTarget() {
        switch (this.target.kind) {
            case 'EVENT':
                if (!this.target.eventTopic) {
                    throw new Error('eventTopic is required for EVENT target');
                }
                break;
            case 'HTTP':
                if (!this.target.http?.url) {
                    throw new Error('url is required for HTTP target');
                }
                break;
            case 'QUEUE':
                if (!this.target.queue?.topic) {
                    throw new Error('topic is required for QUEUE target');
                }
                break;
            default:
                throw new Error(`Unknown target kind: ${this.target.kind}`);
        }
    }
    enable() {
        return new ScheduleEntity({
            ...this,
            enabled: true,
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    disable() {
        return new ScheduleEntity({
            ...this,
            enabled: false,
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    updateNextFire(nextFireAt) {
        return new ScheduleEntity({
            ...this,
            nextFireAt,
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    updateLastFire(lastFireAt) {
        return new ScheduleEntity({
            ...this,
            lastFireAt,
            updatedAt: new Date(),
            version: this.version + 1,
        });
    }
    isDue(now = new Date()) {
        if (!this.enabled || !this.nextFireAt) {
            return false;
        }
        return this.nextFireAt <= now;
    }
    shouldFire(now = new Date()) {
        return this.enabled && this.isDue(now);
    }
    getDedupeKey(fireTime) {
        return `${this.id}@${fireTime.toISOString()}`;
    }
}
exports.ScheduleEntity = ScheduleEntity;
//# sourceMappingURL=schedule.js.map