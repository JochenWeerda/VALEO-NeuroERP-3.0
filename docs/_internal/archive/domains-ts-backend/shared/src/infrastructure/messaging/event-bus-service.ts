/**
 * Event Bus Service - MSOA Implementation nach Clean Architecture
 * Infrastructure Layer Messaging Service migrated to VALEO-NeuroERP-3.0
 * Event-driven communication orchestration
 */

import { DIContainer } from '@valeo-neuroerp-3.0/packages/utilities/src/di-container';
import { Brand } from '@valeo-neuroerp-3.0/packages/data-models/src/branded-types';

// ===== BRANDED TYPES =====
export type EventId = Brand<string, 'EventId'>;
export type TopicId = Brand<string, 'TopicId'>;
export type SubscriptionId = Brand<string, 'SubscriptionId'>;

// ===== DOMAIN ENTITIES =====
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

// ===== EVENT BUS SERVICE nach Clean Architecture =====
export class EventBusService {
    private readonly subscriptions: Map<SubscriptionId, EventSubscription> = new Map();
    private readonly topics: Map<TopicId, EventTopic> = new Map();
    private readonly eventHistory: Map<EventId, DomainEvent> = new Map();
    private readonly processingStats: Map<TopicId, number> = new Map();
    private eventCounter = 0;

    constructor() {
        console.log('[EVENT BUS SERVICE] Initializing Event Bus Service nach infrastructure messaging architecture...');
        this.initializeEventBusService();
    }

    /**
     * Initialize Event Bus Service
     */
    private initializeEventBusService(): void {
        console.log('[EVENT BUS INIT] Event bus initialization nach messaging requirements...');
        
        try {
            this.setupDefaultTopics();
            console.log('[EVENT BUS INIT] ✓ Event bus initialized nach infrastructure messaging architecture');
        } catch (error) {
            console.error('[EVENT BUS INIT] Event bus initialization failed:', error);
            throw new Error(`Event bus configuration failed: ${error}`);
        }
    }

    /**
     * Setup Default Topics nach Business Events
     */
    private setupDefaultTopics(): void {
        console.log('[EVENT BUS SETUP] Setting up default topics nach business event model...');
        
        const businessTopics: EventTopic[] = [
            {
                id: 'crm.events' as TopicId,
                name: 'CRM Events',
                description: 'Customer Relationship Management events',
                eventTypes: ['CustomerCreated', 'LeadConverted', 'ContactUpdated'],
                partitions: 3,
                retentionDays: 30,
                isActive: true
            },
            {
                id: 'finance.events' as TopicId,
                name: 'Finance Events',
                description: 'Financial transaction events',
                eventTypes: ['InvoiceIssued', 'PaymentReceived', 'TransactionCompleted'],
                partitions: 2,
                retentionDays: 365,
                isActive: true
            },
            {
                id: 'inventory.events' as TopicId,
                name: 'Inventory Events',
                description: 'Inventory management events',
                eventTypes: ['StockUpdated', 'OrderProcessed', 'ProductAdded'],
                partitions: 2,
                retentionDays: 90,
                isActive: true
            },
            {
                id: 'system.events' as TopicId,
                name: 'System Events',
                description: 'System-level operational events',
                eventTypes: ['UserLogin', 'ErrorOccurred', 'SystemStarted'],
                partitions: 1,
                retentionDays: 7,
                isActive: true
            }
        ];

        for (const topic of businessTopics) {
            this.topics.set(topic.id, topic);
        }
        
        console.log('[EVENT BUS SETUP] ✓ Business topics configured nach event-driven architecture');
    }

    /**
     * Publish Domain Event
     */
    async publishEvent(eventData: {
        topic: TopicId;
        type: string;
        source: string;
        payload: Record<string, any>;
        metadata?: Record<string, any>;
    }): Promise<EventId> {
        try {
            console.log(`[EVENT BUS] Publishing event: ${eventData.type} to topic: ${eventData.topic}`);
            
            const eventId = this.generateEventId();
            
            const event: DomainEvent = {
                id: eventId,
                topic: eventData.topic,
                type: eventData.type,
                source: eventData.source,
                payload: eventData.payload,
                metadata: eventData.metadata || {},
                timestamp: new Date(),
                version: '1.0'
            };

            // Store event
            this.eventHistory.set(eventId, event);

            // Process subscriptions asynchronously
            setImmediate(() => this.processEventForSubscriptions(event));

            console.log(`[EVENT BUS] ✓ Event published successfully: ${eventId}`);
            return eventId;

        } catch (error) {
            console.error('[EVENT BUS] Publish event failed:', error);
            throw new Error(`Event publishing failed: ${error}`);
        }
    }

    /**
     * Process Event for Subscriptions
     */
    private async processEventForSubscriptions(event: DomainEvent): Promise<void> {
        try {
            const subscribers = Array.from(this.subscriptions.values())
                .filter(sub => sub.topic === event.topic && sub.active);

            for (const subscription of subscribers) {
                try {
                    // Apply filter if defined
                    if (subscription.filter && !subscription.filter(event)) {
                        continue;
                    }

                    await subscription.callback(event);
                    console.log(`[EVENT BUS] ✓ Event processed for subscription: ${subscription.id}`);

                } catch (error) {
                    console.error(`[EVENT BUS] Subscription callback failed: ${subscription.id}`, error);
                }
            }

        } catch (error) {
            console.error('[EVENT BUS] Event processing failed:', error);
        }
    }

    /**
     * Subscribe to Topic
     */
    async subscribeToTopic(subscription: {
        topic: TopicId;
        callback: (event: DomainEvent) => Promise<void>;
        filter?: (event: DomainEvent) => boolean;
    }): Promise<SubscriptionId> {
        try {
            const subscriptionId = this.generateSubscriptionId();
            
            const eventSubscription: EventSubscription = {
                id: subscriptionId,
                topic: subscription.topic,
                callback: subscription.callback,
                filter: subscription.filter,
                active: true,
                createdAt: new Date()
            };

            this.subscriptions.set(subscriptionId, eventSubscription);

            console.log(`[EVENT BUS] ✓ Subscription created: ${subscriptionId} for topic: ${subscription.topic}`);
            return subscriptionId;

        } catch (error) {
            console.error('[EVENT BUS] Subscription failed:', error);
            throw new Error(`Event subscription failed: ${error}`);
        }
    }

    /**
     * Unsubscribe from Topic
     */
    async unsubscribeFromTopic(subscriptionId: SubscriptionId): Promise<boolean> {
        try {
            console.log(`[EVENT BUS] Unsubscribing: ${subscriptionId}`);
            
            const subscription = this.subscriptions.get(subscriptionId);
            if (!subscription) {
                return false;
            }

            const updatedSubscription = {
                ...subscription,
                active: false
            };

            this.subscriptions.set(subscriptionId, updatedSubscription);
            
            console.log(`[EVENT BUS] ✓ Unsubscribed successfully: ${subscriptionId}`);
            return true;

        } catch (error) {
            console.error('[EVENT BUS] Unsubscribe failed:', error);
            return false;
        }
    }

    /**
     * Get Event History
     */
    async getEventHistory(
        topic?: TopicId,
        fromDate?: Date,
        limit?: number
    ): Promise<DomainEvent[]> {
        try {
            let events = Array.from(this.eventHistory.values());

            // Filter by topic if provided
            if (topic) {
                events = events.filter(e => e.topic === topic);
            }

            // Filter by date if provided
            if (fromDate) {
                events = events.filter(e => e.timestamp >= fromDate);
            }

            // Sort by timestamp (newest first)
            events.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

            // Limit results
            if (limit) {
                events = events.slice(0, limit);
            }

            return events;

        } catch (error) {
            console.error('[EVENT BUS] Failed to get event history:', error);
            return [];
        }
    }

    /**
     * Create Business Topic
     */
    async createTopic(topicData: {
        name: string;
        description: string;
        eventTypes: string[];
        partitions?: number;
        retentionDays?: number;
    }): Promise<TopicId> {
        try {
            console.log(`[EVENT BUS] Creating topic: ${topicData.name}`);
            
            const topicId = `${this.generateTopicName()}` as TopicId;
            
            const topic: EventTopic = {
                id: topicId,
                name: topicData.name,
                description: topicData.description,
                eventTypes: topicData.eventTypes,
                partitions: topicData.partitions || 1,
                retentionDays: topicData.retentionDays || 7,
                isActive: true
            };

            this.topics.set(topicId, topic);
            
            console.log(`[EVENT BUS] ✓ Topic created: ${topicId}`);
            return topicId;

        } catch (error) {
            console.error('[EVENT BUS] Topic creation failed:', error);
            throw new Error(`Topic creation failed: ${error}`);
        }
    }

    /**
     * Get Topic Information
     */
    async getTopicInfo(topicId: TopicId): Promise<EventTopic | undefined> {
        return this.topics.get(topicId);
    }

    /**
     * Get Event Metrics
     */
    async getEventMetrics(): Promise<EventMetrics> {
        console.log('[EVENT BUS] Generating event metrics nach messaging architecture...');
        
        const events = Array.from(this.eventHistory.values());
        
        // Count events per topic
        const eventsPerTopic: Record<string, number> = {};
        for (const event of events) {
            const topicName = this.topics.get(event.topic)?.name || event.topic;
            eventsPerTopic[topicName] = (eventsPerTopic[topicName] || 0) + 1;
        }

        const activeSubscriptions = Array.from(this.subscriptions.values())
            .filter(sub => sub.active).length;

        return {
            totalEvents: events.length,
            eventsPerTopic,
            activeSubscriptions,
            processingRate: this.eventCounter,
            errorRate: 0.02 // Architecture mock rate
        };
    }

    /**
     * Health check
     */
    async healthCheck(): Promise<boolean> {
        try {
            console.log('[EVENT BUS HEALTH] Checking event bus health nach messaging architecture...');
            
            const topicsCount = this.topics.size;
            const activeTopics = Array.from(this.topics.values()).filter(t => t.isActive).length;
            
            const isHealthy = topicsCount > 0 && activeTopics > 0;
            
            if (!isHealthy) {
                console.error('[EVENT BUS HEALTH] No active topics configured');
                return false;
            }

            console.log(`[EVENT BUS HEALTH] ✓ Event bus health validated nach messaging architecture (${activeTopics}/${topicsCount} topics active)`);
            return true;
            
        } catch (error) {
            console.error('[EVENT BUS HEALTH] Event bus health check failed:', error);
            return false;
        }
    }

    // Helper methods
    private generateEventId(): EventId {
        return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` as EventId;
    }

    private generateSubscriptionId(): SubscriptionId {
        return `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` as SubscriptionId;
    }

    private generateTopicName(): string {
        return `${Date.now()}`;
    }
}

/**
 * Register Event Bus Service in DI Container
 */
export function registerEventBusService(): void {
    console.log('[EVENT BUS REGISTRATION] Registering Event Bus Service nach infrastructure messaging architecture...');
    
    DIContainer.register('EventBusService', new EventBusService(), {
        singleton: true,
        dependencies: []
    });
    
    console.log('[EVENT BUS REGISTRATION] ✅ Event Bus Service registered successfully nach infrastructure messaging architecture');
}
