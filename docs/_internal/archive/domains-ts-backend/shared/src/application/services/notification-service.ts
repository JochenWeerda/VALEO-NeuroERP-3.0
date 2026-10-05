/**
 * Notification Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service migrated to VALEO-NeuroERP-3.0
 * Real-time notification orchestration system
 */

import { DIContainer } from '@valeo-neuroerp-3.0/packages/utilities/src/di-container';
import { Brand } from '@valeo-neuroerp-3.0/packages/data-models/src/branded-types';

// ===== BRANDED TYPES =====
export type NotificationId = Brand<string, 'NotificationId'>;
export type UserId = Brand<string, 'UserId'>;
export type ChannelType = Brand<string, 'ChannelType'>;

// ===== DOMAIN ENTITIES =====
export interface Notification {
    readonly id: NotificationId;
    readonly userId: UserId;
    readonly title: string;
    readonly message: string;
    readonly type: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
    readonly priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
    readonly channels: ChannelType[];
    readonly metadata: Record<string, any>;
    readonly status: 'PENDING' | 'SENT' | 'DELIVERED' | 'FAILED';
    readonly createdAt: Date;
    readonly sentAt?: Date;
    readonly deliveredAt?: Date;
}

export interface NotificationChannel {
    readonly id: string;
    readonly type: ChannelType;
    readonly name: string;
    readonly enabled: boolean;
    readonly configuration: Record<string, any>;
}

export interface NotificationPreferences {
    readonly userId: UserId;
    readonly channels: {
        readonly inApp: boolean;
        readonly email: boolean;
        readonly sms: boolean;
        readonly push: boolean;
    };
    readonly frequency: 'IMMEDIATE' | 'BATCH' | 'SCHEDULED';
    readonly workingHours: {
        readonly start: string;
        readonly end: string;
        readonly timezone: string;
    };
}

// ===== NOTIFICATION SERVICE nach Clean Architecture =====
export class NotificationService {
    private readonly notifications: Map<NotificationId, Notification> = new Map();
    private readonly channels: Map<ChannelType, NotificationChannel> = new Map();
    private readonly userPreferences: Map<UserId, NotificationPreferences> = new Map();
    private readonly notificationQueue: Notification[] = [];

    constructor() {
        console.log('[NOTIFICATION SERVICE] Initializing Notification Service nach Clean Architecture...');
        this.initializeNotificationService();
    }

    /**
     * Initialize Notification Service
     */
    private initializeNotificationService(): void {
        console.log('[NOTIFICATION INIT] Initializing notification service nach business model...');
        
        try {
            this.setupNotificationChannels();
            this.setupDefaultUserPreferences();
            this.startNotificationProcessor();
            console.log('[NOTIFICATION INIT] ✓ Notification service initialized nach business model');
        } catch (error) {
            console.error('[NOTIFICATION INIT] Notification initialization failed:', error);
            throw new Error(`Notification service configuration failed: ${error}`);
        }
    }

    /**
     * Setup Notification Channels nach Communication Requirements
     */
    private setupNotificationChannels(): void {
        console.log('[NOTIFICATION SETUP] Setting up notification channels nach communication requirements...');
        
        const communicationChannels: NotificationChannel[] = [
            {
                id: 'inapp',
                type: 'IN_APP' as ChannelType,
                name: 'In-App Notifications',
                enabled: true,
                configuration: { persistence: true }
            },
            {
                id: 'email',
                type: 'EMAIL' as ChannelType,
                name: 'Email Notifications',
                enabled: true,
                configuration: { smtpServer: 'smtp.valeo-neuroerp.com' }
            },
            {
                id: 'sms',
                type: 'SMS' as ChannelType,
                name: 'SMS Notifications',
                enabled: true,
                configuration: { provider: 'internal-sms-service' }
            },
            {
                id: 'push',
                type: 'PUSH' as ChannelType,
                name: 'Push Notifications',
                enabled: true,
                configuration: { firebase: true }
            },
            {
                id: 'websocket',
                type: 'WEBSOCKET' as ChannelType,
                name: 'WebSocket Notifications',
                enabled: true,
                configuration: { realtime: true }
            }
        ];

        for (const channel of communicationChannels) {
            this.channels.set(channel.type, channel);
        }
        
        console.log('[NOTIFICATION SETUP] ✓ Notification channels configured nach business model');
    }

    /**
     * Setup Default User Preferences
     */
    private setupDefaultUserPreferences(): void {
        console.log('[NOTIFICATION SETUP] Setting up default user preferences...');
        
        const defaultPrefs: NotificationPreferences = {
            userId: 'default_user' as UserId,
            channels: {
                inApp: true,
                email: true,
                sms: false,
                push: true
            },
            frequency: 'IMMEDIATE',
            workingHours: {
                start: '09:00',
                end: '17:00',
                timezone: 'Europe/Berlin'
            }
        };

        this.userPreferences.set(defaultPrefs.userId, defaultPrefs);
        
        console.log('[NOTIFICATION SETUP] ✓ Default user preferences configured');
    }

    /**
     * Create Notification nach Business Event
     */
    async createNotification(notificationData: {
        userId: UserId;
        title: string;
        message: string;
        type: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
        priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
        channels?: ChannelType[];
        metadata?: Record<string, any>;
    }): Promise<NotificationId> {
        try {
            console.log(`[NOTIFICATION CREATE] Creating notification for user: ${notificationData.userId}`);
            
            const notificationId = this.generateNotificationId();
            
            // Get user preferences
            const preferences = this.userPreferences.get(notificationData.userId);
            const defaultChannels = this.getDefaultChannels(preferences);
            const channels = notificationData.channels || defaultChannels;
            
            const notification: Notification = {
                id: notificationId,
                userId: notificationData.userId,
                title: notificationData.title,
                message: notificationData.message,
                type: notificationData.type,
                priority: notificationData.priority,
                channels,
                metadata: notificationData.metadata || {},
                status: 'PENDING',
                createdAt: new Date()
            };

            this.notifications.set(notificationId, notification);
            this.notificationQueue.push(notification);
            
            console.log(`[NOTIFICATION CREATE] ✓ Notification created: ${notificationId}`);
            return notificationId;

        } catch (error) {
            console.error('[NOTIFICATION CREATE] Failed to create notification:', error);
            throw new Error(`Notification creation failed: ${error}`);
        }
    }

    /**
     * Get Default Channels based on User Preferences
     */
    private getDefaultChannels(preferences?: NotificationPreferences): ChannelType[] {
        if (!preferences) return ['IN_APP' as ChannelType, 'EMAIL' as ChannelType];

        const channels: ChannelType[] = [];
        
        if (preferences.channels.inApp) channels.push('IN_APP' as ChannelType);
        if (preferences.channels.email) channels.push('EMAIL' as ChannelType);
        if (preferences.channels.sms) channels.push('SMS' as ChannelType);
        if (preferences.channels.push) channels.push('PUSH' as ChannelType);

        return channels.length > 0 ? channels : ['IN_APP' as ChannelType];
    }

    /**
     * Start Notification Processor
     */
    private startNotificationProcessor(): void {
        console.log('[NOTIFICATION START] Starting notification processor...');
        
        // Architecture: Process queue periodically
        setInterval(async () => {
            await this.processNotificationQueue();
        }, 2000);
        
        console.log('[NOTIFICATION START] ✓ Notification processor started');
    }

    /**
     * Process Notification Queue
     */
    private async processNotificationQueue(): Promise<void> {
        if (this.notificationQueue.length === 0) return;

        const notificationsToProcess = this.notificationQueue.splice(0, 10); // Process max 10 at a time

        for (const notification of notificationsToProcess) {
            await this.processNotification(notification);
        }
    }

    /**
     * Process Individual Notification
     */
    private async processNotification(notification: Notification): Promise<void> {
        try {
            console.log(`[NOTIFICATION PROCESS] Processing notification: ${notification.id}`);
            
            for (const channelType of notification.channels) {
                const channel = this.channels.get(channelType);
                if (!channel || !channel.enabled) {
                    console.log(`[NOTIFICATION PROCESS] Channel disabled: ${channelType}`);
                    continue;
                }

                await this.sendNotificationByChannel(notification, channel);
            }

            // Update notification status
            const updatedNotification = {
                ...notification,
                status: 'SENT' as const,
                sentAt: new Date()
            };
            
            this.notifications.set(notification.id, updatedNotification);
            
            console.log(`[NOTIFICATION PROCESS] ✓ Notification processed: ${notification.id}`);

        } catch (error) {
            console.error(`[NOTIFICATION PROCESS] Failed to process ${notification.id}:`, error);
            
            const failedNotification = {
                ...notification,
                status: 'FAILED' as const
            };
            
            this.notifications.set(notification.id, failedNotification);
        }
    }

    /**
     * Send Notification by Channel
     */
    private async sendNotificationByChannel(
        notification: Notification, 
        channel: NotificationChannel
    ): Promise<void> {
        console.log(`[NOTIFICATION SEND] Sending via ${channel.type}: ${notification.title}`);
        
        // Architecture: Mock channel sending (in production: integrate actual services)
        switch (channel.type) {
            case 'IN_APP':
                await this.sendInAppNotification(notification);
                break;
            case 'EMAIL':
                await this.sendEmailNotification(notification);
                break;
            case 'SMS':
                await this.sendSMSNotification(notification);
                break;
            case 'PUSH':
                await this.sendPushNotification(notification);
                break;
            case 'WEBSOCKET':
                await this.sendWebSocketNotification(notification);
                break;
        }
    }

    /**
     * Send In-App Notification
     */
    private async sendInAppNotification(notification: Notification): Promise<void> {
        console.log(`[NOTIFICATION IN-APP] Delivered: ${notification.title}`);
        // Architecture: Update user notification inbox in database
    }

    /**
     * Send Email Notification
     */
    private async sendEmailNotification(notification: Notification): Promise<void> {
        console.log(`[NOTIFICATION EMAIL] Sending: ${notification.title}`);
        // Architecture: Use Email Service integration
    }

    /**
     * Send SMS Notification
     */
    private async sendSMSNotification(notification: Notification): Promise<void> {
        console.log(`[NOTIFICATION SMS] Sending: ${notification.title}`);
        // Architecture: Use SMS Service integration
    }

    /**
     * Send Push Notification
     */
    private async sendPushNotification(notification: Notification): Promise<void> {
        console.log(`[NOTIFICATION PUSH] Sending: ${notification.title}`);
        // Architecture: Use Push Service integration
    }

    /**
     * Send WebSocket Notification
     */
    private async sendWebSocketNotification(notification: Notification): Promise<void> {
        console.log(`[NOTIFICATION WEBSOCKET] Broadcasting: ${notification.title}`);
        // Architecture: Use WebSocket Service integration
    }

    /**
     * Get User Notifications
     */
    async getUserNotifications(userId: UserId): Promise<Notification[]> {
        const userNotifications = Array.from(this.notifications.values())
            .filter(n => n.userId === userId)
            .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());

        return userNotifications;
    }

    /**
     * Mark Notification as Delivered
     */
    async markAsDelivered(notificationId: NotificationId): Promise<boolean> {
        const notification = this.notifications.get(notificationId);
        if (!notification) {
            return false;
        }

        const updatedNotification = {
            ...notification,
            status: 'DELIVERED' as const,
            deliveredAt: new Date()
        };

        this.notifications.set(notificationId, updatedNotification);
        
        console.log(`[NOTIFICATION DELIVERED] ✓ ${notificationId}`);
        return true;
    }

    /**
     * Update User Preferences
     */
    async updateUserPreferences(userId: UserId, preferences: NotificationPreferences): Promise<void> {
        this.userPreferences.set(userId, preferences);
        console.log(`[NOTIFICATION PREFERENCES] Updated preferences for user: ${userId}`);
    }

    /**
     * Get Notification Statistics
     */
    async getNotificationStatistics(): Promise<{
        total: number;
        pending: number;
        sent: number;
        delivered: number;
        failed: number;
    }> {
        const allNotifications = Array.from(this.notifications.values());
        
        return {
            total: allNotifications.length,
            pending: allNotifications.filter(n => n.status === 'PENDING').length,
            sent: allNotifications.filter(n => n.status === 'SENT').length,
            delivered: allNotifications.filter(n => n.status === 'DELIVERED').length,
            failed: allNotifications.filter(n => n.status === 'FAILED').length
        };
    }

    /**
     * Health check nach Clean Architecture
     */
    async healthCheck(): Promise<boolean> {
        try {
            console.log('[NOTIFICATION HEALTH] Checking notification service health nach Clean Architecture...');
            
            const channelsCount = this.channels.size;
            const activeChannels = Array.from(this.channels.values()).filter(c => c.enabled).length;
            
            const isHealthy = channelsCount > 0 && activeChannels > 0;
            
            if (!isHealthy) {
                console.error('[NOTIFICATION HEALTH] No notification channels available');
                return false;
            }

            console.log(`[NOTIFICATION HEALTH] ✓ Notification service health validated (${activeChannels}/${channelsCount} channels active)`);
            return true;
            
        } catch (error) {
            console.error('[NOTIFICATION HEALTH] Notification service health check failed:', error);
            return false;
        }
    }

    // Helper methods
    private generateNotificationId(): NotificationId {
        const id = 'notif_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id as NotificationId;
    }
}

/**
 * Register Notification Service in DI Container nach Clean Architecture
 */
export function registerNotificationService(): void {
    console.log('[NOTIFICATION REGISTRATION] Registering Notification Service nach Clean Architecture...');
    
    DIContainer.register('NotificationService', new NotificationService(), {
        singleton: true,
        dependencies: []
    });
    
    console.log('[NOTIFICATION REGISTRATION] ✅ Notification Service registered successfully nach Clean Architecture');
}
