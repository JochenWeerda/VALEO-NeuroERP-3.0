"use strict";
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
var __setFunctionName = (this && this.__setFunctionName) || function (f, name, prefix) {
    if (typeof name === "symbol") name = name.description ? "[".concat(name.description, "]") : "";
    return Object.defineProperty(f, "name", { configurable: true, value: prefix ? "".concat(prefix, " ", name) : name });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.EventBusFactory = exports.InMemoryEventBus = exports.RabbitMQEventBus = exports.NatsEventBus = exports.KafkaEventBus = exports.EventBusType = void 0;
const inversify_1 = require("inversify");
const kafkajs_1 = require("kafkajs");
const nats_1 = require("nats");
const amqplib_1 = require("amqplib");
const events_1 = require("events");
const metrics_service_1 = require("../observability/metrics-service");
var EventBusType;
(function (EventBusType) {
    EventBusType["KAFKA"] = "kafka";
    EventBusType["NATS"] = "nats";
    EventBusType["RABBITMQ"] = "rabbitmq";
    EventBusType["IN_MEMORY"] = "in_memory";
})(EventBusType || (exports.EventBusType = EventBusType = {}));
let KafkaEventBus = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var KafkaEventBus = _classThis = class {
        constructor() {
            this.eventHandlers = new Map();
            this.metrics = metrics_service_1.MetricsService.getInstance();
            this.kafka = new kafkajs_1.Kafka({
                clientId: 'finance-domain',
                brokers: (process.env.KAFKA_BROKERS || 'localhost:9092').split(','),
                retry: {
                    initialRetryTime: 100,
                    retries: 8
                }
            });
        }
        async start() {
            this.producer = this.kafka.producer();
            await this.producer.connect();
            this.consumer = this.kafka.consumer({ groupId: 'finance-domain-group' });
            await this.consumer.connect();
            // Subscribe to all finance domain events
            await this.consumer.subscribe({
                topic: 'finance-domain-events',
                fromBeginning: false
            });
            await this.consumer.run({
                eachMessage: async (payload) => {
                    const startTime = Date.now();
                    try {
                        const event = JSON.parse(payload.message.value?.toString() || '{}');
                        const handlers = this.eventHandlers.get(event.eventType) || [];
                        for (const handler of handlers) {
                            await handler(event);
                        }
                        this.metrics.recordEventProcessingLatency(event.eventType, (Date.now() - startTime) / 1000);
                    }
                    catch (error) {
                        this.metrics.incrementErrorCount('event_processing', 'kafka_consumer');
                        console.error('Error processing Kafka event:', error);
                    }
                }
            });
        }
        async publish(event) {
            if (!this.producer) {
                throw new Error('Event bus not started');
            }
            const message = {
                key: event.aggregateId,
                value: JSON.stringify(event),
                headers: {
                    eventType: event.eventType,
                    aggregateType: event.aggregateType,
                    eventVersion: event.eventVersion.toString()
                }
            };
            await this.producer.send({
                topic: 'finance-domain-events',
                messages: [message]
            });
        }
        subscribe(eventType, handler) {
            const handlers = this.eventHandlers.get(eventType) || [];
            handlers.push(handler);
            this.eventHandlers.set(eventType, handlers);
        }
        async stop() {
            await this.producer?.disconnect();
            await this.consumer?.disconnect();
        }
    };
    __setFunctionName(_classThis, "KafkaEventBus");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        KafkaEventBus = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return KafkaEventBus = _classThis;
})();
exports.KafkaEventBus = KafkaEventBus;
let NatsEventBus = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var NatsEventBus = _classThis = class {
        constructor() {
            this.sc = (0, nats_1.StringCodec)();
            this.eventHandlers = new Map();
            this.metrics = metrics_service_1.MetricsService.getInstance();
        }
        async start() {
            this.nc = await (0, nats_1.connect)({
                servers: (process.env.NATS_SERVERS || 'nats://localhost:4222').split(',')
            });
            // Subscribe to all finance domain events
            const subscription = this.nc.subscribe('finance.domain.>');
            (async () => {
                for await (const msg of subscription) {
                    const startTime = Date.now();
                    try {
                        const event = JSON.parse(this.sc.decode(msg.data));
                        const eventType = msg.subject.split('.').pop() || '';
                        const handlers = this.eventHandlers.get(eventType) || [];
                        for (const handler of handlers) {
                            await handler(event);
                        }
                        this.metrics.recordEventProcessingLatency(eventType, (Date.now() - startTime) / 1000);
                    }
                    catch (error) {
                        this.metrics.incrementErrorCount('event_processing', 'nats_consumer');
                        console.error('Error processing NATS event:', error);
                    }
                }
            })();
        }
        async publish(event) {
            if (!this.nc) {
                throw new Error('Event bus not started');
            }
            const subject = `finance.domain.${event.eventType}`;
            const data = this.sc.encode(JSON.stringify(event));
            this.nc.publish(subject, data);
        }
        subscribe(eventType, handler) {
            const handlers = this.eventHandlers.get(eventType) || [];
            handlers.push(handler);
            this.eventHandlers.set(eventType, handlers);
        }
        async stop() {
            await this.nc?.close();
        }
    };
    __setFunctionName(_classThis, "NatsEventBus");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        NatsEventBus = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return NatsEventBus = _classThis;
})();
exports.NatsEventBus = NatsEventBus;
let RabbitMQEventBus = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var RabbitMQEventBus = _classThis = class {
        constructor() {
            this.eventHandlers = new Map();
            this.metrics = metrics_service_1.MetricsService.getInstance();
        }
        async start() {
            this.connection = await (0, amqplib_1.connect)(process.env.RABBITMQ_URL || 'amqp://localhost');
            this.channel = await this.connection?.createChannel();
            // Declare exchange and queue
            await this.channel?.assertExchange('finance-domain-events', 'topic', { durable: true });
            const queueResult = await this.channel?.assertQueue('', { exclusive: true });
            // Bind to all finance domain events
            await this.channel?.bindQueue(queueResult?.queue || '', 'finance-domain-events', 'finance.domain.#');
            // Consume messages
            await this.channel?.consume(queueResult?.queue || '', async (msg) => {
                if (!msg)
                    return;
                const startTime = Date.now();
                try {
                    const event = JSON.parse(msg.content.toString());
                    const routingKey = msg.fields.routingKey;
                    const eventType = routingKey.split('.').pop() || '';
                    const handlers = this.eventHandlers.get(eventType) || [];
                    for (const handler of handlers) {
                        await handler(event);
                    }
                    this.channel?.ack(msg);
                    this.metrics.recordEventProcessingLatency(eventType, (Date.now() - startTime) / 1000);
                }
                catch (error) {
                    this.metrics.incrementErrorCount('event_processing', 'rabbitmq_consumer');
                    console.error('Error processing RabbitMQ event:', error);
                    this.channel?.nack(msg, false, false);
                }
            });
        }
        async publish(event) {
            if (!this.channel) {
                throw new Error('Event bus not started');
            }
            const routingKey = `finance.domain.${event.eventType}`;
            const message = JSON.stringify(event);
            this.channel.publish('finance-domain-events', routingKey, Buffer.from(message), {
                persistent: true,
                messageId: event.eventId,
                timestamp: event.occurredOn.getTime(),
                headers: {
                    aggregateId: event.aggregateId,
                    aggregateType: event.aggregateType,
                    eventVersion: event.eventVersion
                }
            });
        }
        subscribe(eventType, handler) {
            const handlers = this.eventHandlers.get(eventType) || [];
            handlers.push(handler);
            this.eventHandlers.set(eventType, handlers);
        }
        async stop() {
            await this.channel?.close();
            // await this.connection?.close(); // Connection type doesn't have close method
        }
    };
    __setFunctionName(_classThis, "RabbitMQEventBus");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        RabbitMQEventBus = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return RabbitMQEventBus = _classThis;
})();
exports.RabbitMQEventBus = RabbitMQEventBus;
let InMemoryEventBus = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    let _classSuper = events_1.EventEmitter;
    var InMemoryEventBus = _classThis = class extends _classSuper {
        constructor() {
            super(...arguments);
            this.eventHandlers = new Map();
            this.metrics = metrics_service_1.MetricsService.getInstance();
        }
        async start() {
            // In-memory bus is always ready
        }
        async publish(event) {
            const startTime = Date.now();
            try {
                this.emit(event.eventType, event);
                const handlers = this.eventHandlers.get(event.eventType) || [];
                for (const handler of handlers) {
                    await handler(event);
                }
                this.metrics.recordEventProcessingLatency(event.eventType, (Date.now() - startTime) / 1000);
            }
            catch (error) {
                this.metrics.incrementErrorCount('event_processing', 'in_memory_bus');
                throw error;
            }
        }
        subscribe(eventType, handler) {
            const handlers = this.eventHandlers.get(eventType) || [];
            handlers.push(handler);
            this.eventHandlers.set(eventType, handlers);
        }
        async stop() {
            this.removeAllListeners();
        }
    };
    __setFunctionName(_classThis, "InMemoryEventBus");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(_classSuper[Symbol.metadata] ?? null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        InMemoryEventBus = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return InMemoryEventBus = _classThis;
})();
exports.InMemoryEventBus = InMemoryEventBus;
class EventBusFactory {
    static createEventBus(type = EventBusType.IN_MEMORY) {
        switch (type) {
            case EventBusType.KAFKA:
                return new KafkaEventBus();
            case EventBusType.NATS:
                return new NatsEventBus();
            case EventBusType.RABBITMQ:
                return new RabbitMQEventBus();
            case EventBusType.IN_MEMORY:
            default:
                return new InMemoryEventBus();
        }
    }
}
exports.EventBusFactory = EventBusFactory;
//# sourceMappingURL=event-bus.js.map