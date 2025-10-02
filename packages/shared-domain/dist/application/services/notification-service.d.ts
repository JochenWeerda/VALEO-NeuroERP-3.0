/**
 * Notification Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service migrated to VALEO-NeuroERP-3.0
 * Real-time notification orchestration system
 */
import { Brand } from '@valero-neuroerp/data-models/src/branded-types';
export type NotificationId = Brand<string, 'NotificationId'>;
export type UserId = Brand<string, 'UserId'>;
export type ChannelType = Brand<string, 'ChannelType'>;
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
export declare class NotificationService {
    private readonly notifications;
    private readonly channels;
    private readonly userPreferences;
    private readonly notificationQueue;
    constructor();
    /**
     * Initialize Notification Service
     */
    private initializeNotificationService;
    /**
     * Setup Notification Channels nach Communication Requirements
     */
    private setupNotificationChannels;
    /**
     * Setup Default User Preferences
     */
    private setupDefaultUserPreferences;
    /**
     * Create Notification nach Business Event
     */
    createNotification(notificationData: {
        userId: UserId;
        title: string;
        message: string;
        type: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
        priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
        channels?: ChannelType[];
        metadata?: Record<string, any>;
    }): Promise<NotificationId>;
    /**
     * Get Default Channels based on User Preferences
     */
    private getDefaultChannels;
    /**
     * Start Notification Processor
     */
    private startNotificationProcessor;
    /**
     * Process Notification Queue
     */
    private processNotificationQueue;
    /**
     * Process Individual Notification
     */
    private processNotification;
    /**
     * Send Notification by Channel
     */
    private sendNotificationByChannel;
    /**
     * Send In-App Notification
     */
    private sendInAppNotification;
    /**
     * Send Email Notification
     */
    private sendEmailNotification;
    /**
     * Send SMS Notification
     */
    private sendSMSNotification;
    /**
     * Send Push Notification
     */
    private sendPushNotification;
    /**
     * Send WebSocket Notification
     */
    private sendWebSocketNotification;
    /**
     * Get User Notifications
     */
    getUserNotifications(userId: UserId): Promise<Notification[]>;
    /**
     * Mark Notification as Delivered
     */
    markAsDelivered(notificationId: NotificationId): Promise<boolean>;
    /**
     * Update User Preferences
     */
    updateUserPreferences(userId: UserId, preferences: NotificationPreferences): Promise<void>;
    /**
     * Get Notification Statistics
     */
    getNotificationStatistics(): Promise<{
        total: number;
        pending: number;
        sent: number;
        delivered: number;
        failed: number;
    }>;
    /**
     * Health check nach Clean Architecture
     */
    healthCheck(): Promise<boolean>;
    private generateNotificationId;
}
/**
 * Register Notification Service in DI Container nach Clean Architecture
 */
export declare function registerNotificationService(): void;
//# sourceMappingURL=notification-service.d.ts.map