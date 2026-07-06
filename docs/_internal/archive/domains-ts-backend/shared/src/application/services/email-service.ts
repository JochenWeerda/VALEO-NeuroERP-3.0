/**
 * Email Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service migrated to VALEO-NeuroERP-3.0
 * Integration service für E-Mail communication
 */

import { DIContainer } from '@valeo-neuroerp-3.0/packages/utilities/src/di-container';
import { Brand } from '@valeo-neuroerp-3.0/packages/data-models/src/branded-types';

// ===== BRANDED TYPES =====
export type EmailId = Brand<string, 'EmailId'>;
export type TemplateId = Brand<string, 'TemplateId'>;
export type RecipientId = Brand<string, 'RecipientId'>;

// ===== DOMAIN ENTITIES =====
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

// ===== EMAIL SERVICE nach Clean Architecture =====
export class EmailService {
    private readonly emailQueue: Map<EmailId, EmailMessage> = new Map();
    private readonly templates: Map<TemplateId, EmailTemplate> = new Map();
    private readonly recipients: Map<RecipientId, EmailRecipient> = new Map();
    private readonly sentEmails: Map<EmailId, EmailMessage> = new Map();

    constructor() {
        console.log('[EMAIL SERVICE] Initializing Email Service nach Clean Architecture...');
        this.initializeEmailService();
    }

    /**
     * Initialize Email Service
     */
    private initializeEmailService(): void {
        console.log('[EMAIL INIT] Initializing email service nach business rules...');
        
        try {
            this.setupEmailTemplates();
            this.setupRecipients();
            console.log('[EMAIL INIT] ✓ Email service initialized nach business requirements');
        } catch (error) {
            console.error('[EMAIL INIT] Email service initialization failed:', error);
            throw new Error(`Email service configuration failed: ${error}`);
        }
    }

    /**
     * Setup Email Templates nach Business Model
     */
    private setupEmailTemplates(): void {
        console.log('[EMAIL SETUP] Setting up email templates nach business requirements...');
        
        const businessTemplates: EmailTemplate[] = [
            {
                id: 'welcome_email' as TemplateId,
                name: 'Welcome Email',
                subject: 'Willkommen bei VALEO-NeuroERP',
                body: 'Hallo {{recipientName}}, herzlich willkommen bei unserem ERP-System!',
                placeholders: ['recipientName', 'companyName'],
                category: 'onboarding',
                isActive: true
            },
            {
                id: 'notification_email' as TemplateId,
                name: 'System Notification',
                subject: 'System Benachrichtigung - {{title}}',
                body: 'Sie haben eine neue Benachrichtigung: {{message}}',
                placeholders: ['title', 'message', 'timestamp'],
                category: 'system',
                isActive: true
            },
            {
                id: 'invoice_email' as TemplateId,
                name: 'Invoice Email',
                subject: 'Rechnung {{invoiceNumber}} ausgestellt',
                body: 'Sehr geehrte/r {{customerName}},\n\nIhre Rechnung {{invoiceNumber}} über {{amount}}€ ist bereit.',
                placeholders: ['customerName', 'invoiceNumber', 'amount', 'dueDate'],
                category: 'billing',
                isActive: true
            }
        ];

        for (const template of businessTemplates) {
            this.templates.set(template.id, template);
        }
        
        console.log('[EMAIL SETUP] ✓ Email templates configured nach business model');
    }

    /**
     * Setup Recipients nach Organization Data
     */
    private setupRecipients(): void {
        console.log('[EMAIL SETUP] Setting up email recipients nach organization structure...');
        
        const orgRecipients: EmailRecipient[] = [
            {
                id: 'admin_001' as RecipientId,
                email: 'admin@valeo-neuroerp.com',
                name: 'System Administrator',
                preferences: {
                    format: 'HTML',
                    frequency: 'IMMEDIATE',
                    unsubscribed: false
                }
            },
            {
                id: 'manager_001' as RecipientId,
                email: 'manager@valeo-neuroerp.com',
                name: 'Team Manager',
                preferences: {
                    format: 'HTML',
                    frequency: 'DAILY',
                    unsubscribed: false
                }
            }
        ];

        for (const recipient of orgRecipients) {
            this.recipients.set(recipient.id, recipient);
        }
        
        console.log('[EMAIL SETUP] ✓ Email recipients configured nach organization structure');
    }

    /**
     * Send Email Message
     */
    async sendEmail(emailData: {
        to: string;
        from?: string;
        subject: string;
        body: string;
        templateId?: TemplateId;
        metadata?: Record<string, any>;
    }): Promise<EmailId> {
        try {
            console.log(`[EMAIL SEND] Sending email to: ${emailData.to}`);
            
            const emailId = this.generateEmailId();
            const email: EmailMessage = {
                id: emailId,
                to: emailData.to,
                from: emailData.from || 'noreply@valeo-neuroerp.com',
                subject: emailData.subject,
                body: emailData.body,
                templateId: emailData.templateId,
                metadata: emailData.metadata || {},
                status: 'PENDING',
                createdAt: new Date()
            };

            this.emailQueue.set(emailId, email);

            // Simulate sending process
            setTimeout(async () => {
                await this.processQueuedEmail(emailId);
            }, 1000);

            console.log(`[EMAIL SEND] ✓ Email queued for sending: ${emailId}`);
            return emailId;

        } catch (error) {
            console.error('[EMAIL SEND] Error sending email:', error);
            throw new Error(`Failed to send email: ${error}`);
        }
    }

    /**
     * Process Queued Email (Placeholder for SMTP Integration)
     */
    private async processQueuedEmail(emailId: EmailId): Promise<void> {
        const email = this.emailQueue.get(emailId);
        if (!email) {
            console.error(`[EMAIL PROCESS] Email not found: ${emailId}`);
            return;
        }

        try {
            // Architecture: Mock SMTP sending (in production: integrate actual SMTP)
            console.log(`[EMAIL PROCESS] Processing email: ${emailId}`);
            
            const updatedEmail = {
                ...email,
                status: 'SENT' as const,
                sentAt: new Date()
            };

            this.emailQueue.delete(emailId);
            this.sentEmails.set(emailId, updatedEmail);
            
            console.log(`[EMAIL PROCESS] ✓ Email sent successfully: ${emailId}`);

        } catch (error) {
            console.error(`[EMAIL PROCESS] Failed to send email ${emailId}:`, error);
            
            const failedEmail = {
                ...email,
                status: 'FAILED' as const
            };
            
            this.emailQueue.set(emailId, failedEmail);
        }
    }

    /**
     * Send Template Email
     */
    async sendTemplateEmail(
        templateId: TemplateId,
        to: string,
        data: Record<string, any>
    ): Promise<EmailId> {
        try {
            console.log(`[EMAIL TEMPLATE] Sending template email: ${templateId} to ${to}`);
            
            const template = this.templates.get(templateId);
            if (!template) {
                throw new Error(`Template not found: ${templateId}`);
            }

            if (!template.isActive) {
                throw new Error(`Template is inactive: ${templateId}`);
            }

            // Process template with data
            let processedSubject = template.subject;
            let processedBody = template.body;

            for (const [key, value] of Object.entries(data)) {
                const placeholder = `{{${key}}}`;
                processedSubject = processedSubject.replace(new RegExp(placeholder, 'g'), String(value));
                processedBody = processedBody.replace(new RegExp(placeholder, 'g'), String(value));
            }

            return await this.sendEmail({
                to,
                subject: processedSubject,
                body: processedBody,
                templateId,
                metadata: { templateData: data }
            });

        } catch (error) {
            console.error('[EMAIL TEMPLATE] Template email failed:', error);
            throw new Error(`Template email sending failed: ${error}`);
        }
    }

    /**
     * Get Email Status
     */
    async getEmailStatus(emailId: EmailId): Promise<EmailMessage | undefined> {
        return this.emailQueue.get(emailId) || this.sentEmails.get(emailId);
    }

    /**
     * Get Email Statistics
     */
    async getEmailStatistics(): Promise<{
        queueCount: number;
        sentCount: number;
        failedCount: number;
        templateCount: number;
    }> {
        const queueEmails = Array.from(this.emailQueue.values());
        const sentEmails = Array.from(this.sentEmails.values());
        
        return {
            queueCount: queueEmails.filter(e => e.status === 'PENDING').length,
            sentCount: sentEmails.filter(e => e.status === 'SENT').length,
            failedCount: queueEmails.filter(e => e.status === 'FAILED').length + 
                        sentEmails.filter(e => e.status === 'FAILED').length,
            templateCount: this.templates.size
        };
    }

    /**
     * Health check nach Clean Architecture
     */
    async healthCheck(): Promise<boolean> {
        try {
            console.log('[EMAIL HEALTH] Checking email service health nach Clean Architecture...');
            
            const templatesCount = this.templates.size;
            const recipientsCount = this.recipients.size;
            
            const isHealthy = templatesCount > 0 && recipientsCount > 0;
            
            if (!isHealthy) {
                console.error('[EMAIL HEALTH] Missing email templates or recipients');
                return false;
            }

            console.log(`[EMAIL HEALTH] ✓ Email service health validated (${templatesCount} templates, ${recipientsCount} recipients)`);
            return true;
            
        } catch (error) {
            console.error('[EMAIL HEALTH] Email service health check failed:', error);
            return false;
        }
    }

    // Helper methods
    private generateEmailId(): EmailId {
        const id = 'email_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id as EmailId;
    }
}

/**
 * Register Email Service in DI Container nach Clean Architecture
 */
export function registerEmailService(): void {
    console.log('[EMAIL REGISTRATION] Registering Email Service nach Clean Architecture...');
    
    DIContainer.register('EmailService', new EmailService(), {
        singleton: true,
        dependencies: []
    });
    
    console.log('[EMAIL REGISTRATION] ✅ Email Service registered successfully nach Clean Architecture');
}
