"use strict";
/**
 * VALEO NeuroERP 3.0 - Inventory Event Bus
 *
 * Event bus implementation for inventory domain events.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.EventBusFactory = exports.InventoryEventBus = void 0;
class InventoryEventBus {
    constructor() {
        this.eventHandlers = new Map();
    }
    async publish(event) {
        const handlers = this.eventHandlers.get(event.type) || [];
        await Promise.all(handlers.map(handler => handler(event)));
    }
    subscribe(eventType, handler) {
        if (!this.eventHandlers.has(eventType)) {
            this.eventHandlers.set(eventType, []);
        }
        this.eventHandlers.get(eventType).push(handler);
    }
}
exports.InventoryEventBus = InventoryEventBus;
class EventBusFactory {
    static create(type) {
        switch (type) {
            case 'in-memory':
                return new InventoryEventBus();
            default:
                return new InventoryEventBus();
        }
    }
    static createEventBus(type) {
        return this.create(type);
    }
}
exports.EventBusFactory = EventBusFactory;
//# sourceMappingURL=event-bus.js.map