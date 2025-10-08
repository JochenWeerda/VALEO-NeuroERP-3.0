import { injectable } from 'inversify';
import { Consumer, EachMessagePayload, Kafka, Producer } from 'kafkajs';
import { NatsConnection, StringCodec, connect } from 'nats';
import { Channel, Connection, connect as connectRabbitMQ } from 'amqplib';
import { EventEmitter } from 'events';
import { MetricsService } from '../observability/metrics-service';

export interface DomainEvent {
  eventId: string;
  eventType: string;
  aggregateId: string;
  aggregateType: string;
  eventVersion: number;
  occurredOn: Date;
  eventData: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface EventBus {
  publish(event: DomainEvent): Promise<void>;
  subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void;
  start(): Promise<void>;
  stop(): Promise<void>;
}

export enum EventBusType {
  KAFKA = 'kafka',
  NATS = 'nats',
  RABBITMQ = 'rabbitmq',
  IN_MEMORY = 'in_memory'
}

@injectable()
export class KafkaEventBus implements EventBus {
  private producer?: Producer;
  private consumer?: Consumer;
  private readonly kafka: Kafka;
  private readonly eventHandlers = new Map<string, ((event: DomainEvent) => Promise<void>)[]>();
  private readonly metrics = MetricsService.getInstance();

  constructor() {
    this.kafka = new Kafka({
      clientId: 'finance-domain',
      brokers: (process.env.KAFKA_BROKERS || 'localhost:9092').split(','),
      retry: {
        initialRetryTime: 100,
        retries: 8
      }
    });
  }

  async start(): Promise<void> {
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
      eachMessage: async (payload: EachMessagePayload) => {
        const startTime = Date.now();
        try {
          const event: DomainEvent = JSON.parse(payload.message.value?.toString() || '{}');
          const handlers = this.eventHandlers.get(event.eventType) || [];

          for (const handler of handlers) {
            await handler(event);
          }

          this.metrics.recordEventProcessingLatency(event.eventType, (Date.now() - startTime) / 1000);
        } catch (error) {
          this.metrics.incrementErrorCount('event_processing', 'kafka_consumer');
          console.error('Error processing Kafka event:', error);
        }
      }
    });
  }

  async publish(event: DomainEvent): Promise<void> {
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

  subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.push(handler);
    this.eventHandlers.set(eventType, handlers);
  }

  async stop(): Promise<void> {
    await this.producer?.disconnect();
    await this.consumer?.disconnect();
  }
}

@injectable()
export class NatsEventBus implements EventBus {
  private nc?: NatsConnection;
  private readonly sc = StringCodec();
  private readonly eventHandlers = new Map<string, ((event: DomainEvent) => Promise<void>)[]>();
  private readonly metrics = MetricsService.getInstance();

  async start(): Promise<void> {
    this.nc = await connect({
      servers: (process.env.NATS_SERVERS || 'nats://localhost:4222').split(',')
    });

    // Subscribe to all finance domain events
    const subscription = this.nc.subscribe('finance.domain.>');
    (async () => {
      for await (const msg of subscription) {
        const startTime = Date.now();
        try {
          const event: DomainEvent = JSON.parse(this.sc.decode(msg.data));
          const eventType = msg.subject.split('.').pop() || '';
          const handlers = this.eventHandlers.get(eventType) || [];

          for (const handler of handlers) {
            await handler(event);
          }

          this.metrics.recordEventProcessingLatency(eventType, (Date.now() - startTime) / 1000);
        } catch (error) {
          this.metrics.incrementErrorCount('event_processing', 'nats_consumer');
          console.error('Error processing NATS event:', error);
        }
      }
    })();
  }

  async publish(event: DomainEvent): Promise<void> {
    if (!this.nc) {
      throw new Error('Event bus not started');
    }

    const subject = `finance.domain.${event.eventType}`;
    const data = this.sc.encode(JSON.stringify(event));

    this.nc.publish(subject, data);
  }

  subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.push(handler);
    this.eventHandlers.set(eventType, handlers);
  }

  async stop(): Promise<void> {
    await this.nc?.close();
  }
}

@injectable()
export class RabbitMQEventBus implements EventBus {
  private connection?: Connection;
  private channel?: Channel;
  private readonly eventHandlers = new Map<string, ((event: DomainEvent) => Promise<void>)[]>();
  private readonly metrics = MetricsService.getInstance();

  async start(): Promise<void> {
    this.connection = await connectRabbitMQ(process.env.RABBITMQ_URL || 'amqp://localhost') as any;
    this.channel = await (this.connection as any)?.createChannel();

    // Declare exchange and queue
    await this.channel?.assertExchange('finance-domain-events', 'topic', { durable: true });
    const queueResult = await this.channel?.assertQueue('', { exclusive: true });

    // Bind to all finance domain events
    await this.channel?.bindQueue(queueResult?.queue || '', 'finance-domain-events', 'finance.domain.#');

    // Consume messages
    await this.channel?.consume(queueResult?.queue || '', async (msg: any) => {
      if (!msg) return;

      const startTime = Date.now();
      try {
        const event: DomainEvent = JSON.parse(msg.content.toString());
        const routingKey = msg.fields.routingKey;
        const eventType = routingKey.split('.').pop() || '';
        const handlers = this.eventHandlers.get(eventType) || [];

        for (const handler of handlers) {
          await handler(event);
        }

        this.channel?.ack(msg);
        this.metrics.recordEventProcessingLatency(eventType, (Date.now() - startTime) / 1000);
      } catch (error) {
        this.metrics.incrementErrorCount('event_processing', 'rabbitmq_consumer');
        console.error('Error processing RabbitMQ event:', error);
        this.channel?.nack(msg, false, false);
      }
    });
  }

  async publish(event: DomainEvent): Promise<void> {
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

  subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.push(handler);
    this.eventHandlers.set(eventType, handlers);
  }

  async stop(): Promise<void> {
    await this.channel?.close();
    // await this.connection?.close(); // Connection type doesn't have close method
  }
}

@injectable()
export class InMemoryEventBus extends EventEmitter implements EventBus {
  private readonly eventHandlers = new Map<string, ((event: DomainEvent) => Promise<void>)[]>();
  private readonly metrics = MetricsService.getInstance();

  async start(): Promise<void> {
    // In-memory bus is always ready
  }

  async publish(event: DomainEvent): Promise<void> {
    const startTime = Date.now();
    try {
      this.emit(event.eventType, event);

      const handlers = this.eventHandlers.get(event.eventType) || [];
      for (const handler of handlers) {
        await handler(event);
      }

      this.metrics.recordEventProcessingLatency(event.eventType, (Date.now() - startTime) / 1000);
    } catch (error) {
      this.metrics.incrementErrorCount('event_processing', 'in_memory_bus');
      throw error;
    }
  }

  subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.push(handler);
    this.eventHandlers.set(eventType, handlers);
  }

  async stop(): Promise<void> {
    this.removeAllListeners();
  }
}

export class EventBusFactory {
  static createEventBus(type: EventBusType = EventBusType.IN_MEMORY): EventBus {
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