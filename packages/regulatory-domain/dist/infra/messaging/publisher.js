"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.initEventPublisher = initEventPublisher;
exports.publishEvent = publishEvent;
exports.getEventPublisher = getEventPublisher;
exports.closeEventPublisher = closeEventPublisher;
const nats_1 = require("nats");
const pino_1 = __importDefault(require("pino"));
const logger = (0, pino_1.default)({ name: 'event-publisher' });
const codec = (0, nats_1.JSONCodec)();
let nc = null;
async function initEventPublisher() {
    try {
        const natsUrl = process.env.NATS_URL || 'nats://localhost:4222';
        nc = await (0, nats_1.connect)({ servers: natsUrl });
        logger.info({ natsUrl }, 'Connected to NATS');
    }
    catch (error) {
        logger.error({ error }, 'Failed to connect to NATS');
        throw error;
    }
}
async function publishEvent(eventType, payload) {
    if (!nc) {
        logger.warn('NATS not connected, skipping event publication');
        return;
    }
    try {
        const subject = `regulatory.${eventType}`;
        const message = {
            eventType: subject,
            payload,
            occurredAt: new Date().toISOString(),
            version: '1.0',
        };
        nc.publish(subject, codec.encode(message));
        logger.info({ subject, eventType }, 'Published event');
    }
    catch (error) {
        logger.error({ error, eventType }, 'Failed to publish event');
        throw error;
    }
}
function getEventPublisher() {
    return { publish: publishEvent };
}
async function closeEventPublisher() {
    if (nc) {
        await nc.close();
        nc = null;
        logger.info('NATS connection closed');
    }
}
//# sourceMappingURL=publisher.js.map