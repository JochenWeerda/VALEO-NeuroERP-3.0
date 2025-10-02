/**
 * Email Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service migrated to VALEO-NeuroERP-3.0
 * Integration service für E-Mail communication
 */
import { Brand } from '@valero-neuroerp/data-models/src/branded-types';
export type EmailId = Brand<string, 'EmailId'>;
export type TemplateId = Brand<string, 'TemplateId'>;
export type RecipientId = Brand<string, 'RecipientId'>;
export interface EmailMessage {
    readonly id: EmailId;
    readonly to: string;
    readonly from: string;
    readonly subject: string;
    readonly body: string;
    readonly templateId?: TemplateId;
    readonly metadata: Record<string, any>;
    readonly status: 'PENDING' | 'SENT' | 'FAILED' | 'REJECTED';
    readonly createdAt: Date;
    readonly sentAt?: Date;
}
export interface EmailTemplate {
    readonly id: TemplateId;
    readonly name: string;
    readonly subject: string;
    readonly body: string;
    readonly placeholders: string[];
    readonly category: string;
    readonly isActive: boolean;
}
export interface EmailRecipient {
    readonly id: RecipientId;
    readonly email: string;
    readonly name: string;
    readonly preferences: {
        readonly format: 'HTML' | 'TEXT';
        readonly frequency: 'IMMEDIATE' | 'BATCH' | 'DAILY';
        readonly unsubscribed: boolean;
    };
}
export declare class EmailService {
    private readonly emailQueue;
    private readonly templates;
    private readonly recipients;
    private readonly sentEmails;
    constructor();
    /**
     * Initialize Email Service
     */
    private initializeEmailService;
    /**
     * Setup Email Templates nach Business Model
     */
    private setupEmailTemplates;
    /**
     * Setup Recipients nach Organization Data
     */
    private setupRecipients;
    /**
     * Send Email Message
     */
    sendEmail(emailData: {
        to: string;
        from?: string;
        subject: string;
        body: string;
        templateId?: TemplateId;
        metadata?: Record<string, any>;
    }): Promise<EmailId>;
    /**
     * Process Queued Email (Placeholder for SMTP Integration)
     */
    private processQueuedEmail;
    /**
     * Send Template Email
     */
    sendTemplateEmail(templateId: TemplateId, to: string, data: Record<string, any>): Promise<EmailId>;
    /**
     * Get Email Status
     */
    getEmailStatus(emailId: EmailId): Promise<EmailMessage | undefined>;
    /**
     * Get Email Statistics
     */
    getEmailStatistics(): Promise<{
        queueCount: number;
        sentCount: number;
        failedCount: number;
        templateCount: number;
    }>;
    /**
     * Health check nach Clean Architecture
     */
    healthCheck(): Promise<boolean>;
    private generateEmailId;
}
/**
 * Register Email Service in DI Container nach Clean Architecture
 */
export declare function registerEmailService(): void;
//# sourceMappingURL=email-service.d.ts.map