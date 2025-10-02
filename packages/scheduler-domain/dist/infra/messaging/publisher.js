"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.NoOpEventPublisher = void 0;
class NoOpEventPublisher {
    async publish(event) {
        console.log(`Publishing event: ${event.eventType}`, event);
    }
    async publishBatch(events) {
        console.log(`Publishing ${events.length} events`);
        for (const event of events) {
            await this.publish(event);
        }
    }
    isHealthy() {
        return true;
    }
}
exports.NoOpEventPublisher = NoOpEventPublisher;
//# sourceMappingURL=publisher.js.map