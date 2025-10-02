"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InMemoryEventBus = void 0;
exports.buildEvent = buildEvent;
const rxjs_1 = require("rxjs");
const crypto_1 = require("crypto");
class InMemoryEventBus {
    constructor() {
        this.subject = new rxjs_1.Subject();
    }
    publish(event) {
        this.subject.next(event);
    }
    subscribe(handler) {
        return this.subject.subscribe(handler);
    }
}
exports.InMemoryEventBus = InMemoryEventBus;
function buildEvent(eventType, tenantId, payload, metadata) {
    return {
        eventId: (0, crypto_1.randomUUID)(),
        eventType,
        timestamp: new Date().toISOString(),
        tenantId,
        payload,
        metadata,
    };
}
//# sourceMappingURL=logistics-event-bus.js.map