/**
 * Event Bus Service - MSOA Implementation nach Clean Architecture
 * Infrastructure Layer Messaging Service migrated to VALEO-NeuroERP-3.0
 * Event-driven communication orchestration
 */
import { Brand } from '@valero-neuroerp/data-models/src/branded-types';
export type EventId = Brand<string, 'EventId'>;
export type TopicId = Brand<string, 'TopicId'>;
export type SubscriptionId = Brand<string, 'SubscriptionId'>;
export interface DomainEvent {
    readonly id: EventId;
    readonly topic: TopicId;
    readonly type: string;
    readonly source: string;
    readonly payload: Record<string, any>;
    readonly metadata: Record<string, any>;
    readonly timestamp: Date;
    readonly version: string;
}
export interface EventSubscription {
    readonly id: SubscriptionId;
    readonly topic: TopicId;
    readonly callback: (event: DomainEvent) => Promise<void>;
    readonly filter?: (event: DomainEvent) => boolean;
    readonly active: boolean;
    readonly createdAt: Date;
}
export interface EventTopic {
    readonly id: TopicId;
    readonly name: string;
    readonly description: string;
    readonly eventTypes: string[];
    readonly partitions: number;
    readonly retentionDays: number;
    readonly isActive: boolean;
}
export interface EventMetrics {
    readonly totalEvents: number;
    readonly eventsPerTopic: Record<string, number>;
    readonly activeSubscriptions: number;
    readonly processingRate: number;
    readonly errorRate: number;
}
export declare class EventBusService {
    private readonly subscriptions;
    private readonly topics;
    private readonly eventHistory;
    private readonly processingStats;
    private eventCounter;
    constructor();
    /**
     * Initialize Event Bus Service
     */
    private initializeEventBusService;
    /**
     * Setup Default Topics nach Business Events
     */
    private setupDefaultTopics;
    /**
     * Publish Domain Event
     */
    publishEvent(eventData: {
        topic: TopicId;
        type: string;
        source: string;
        payload: Record<string, any>;
        metadata?: Record<string, any>;
    }): Promise<EventId>;
    /**
     * Process Event for Subscriptions
     */
    private processEventForSubscriptions;
    /**
     * Subscribe to Topic
     */
    subscribeToTopic(subscription: {
        topic: TopicId;
        callback: (event: DomainEvent) => Promise<void>;
        filter?: (event: DomainEvent) => boolean;
    }): Promise<SubscriptionId>;
    /**
     * Unsubscribe from Topic
     */
    unsubscribeFromTopic(subscriptionId: SubscriptionId): Promise<boolean>;
    /**
     * Get Event History
     */
    getEventHistory(topic?: TopicId, fromDate?: Date, limit?: number): Promise<DomainEvent[]>;
    /**
     * Create Business Topic
     */
    createTopic(topicData: {
        name: string;
        description: string;
        eventTypes: string[];
        partitions?: number;
        retentionDays?: number;
    }): Promise<TopicId>;
    /**
     * Get Topic Information
     */
    getTopicInfo(topicId: TopicId): Promise<EventTopic | undefined>;
    /**
     * Get Event Metrics
     */
    getEventMetrics(): Promise<EventMetrics>;
    /**
     * Health check
     */
    healthCheck(): Promise<boolean>;
    private generateEventId;
    private generateSubscriptionId;
    private generateTopicName;
}
/**
 * Register Event Bus Service in DI Container
 */
export declare function registerEventBusService(): void;
//# sourceMappingURL=event-bus-service.d.ts.map