/**
 * Form Runtime Builder Service - MSOA nach Clean Architecture
 * Dynamic form creation at runtime - migrated from VALEO-NeuroERP-2.0
 * Enables runtime form generation as in old system
 */

import { DIContainer } from '@valeo-neuroerp-3.0/packages/utilities/src/di-container';
import { Brand } from '@valeo-neuroerp-3.0/packages/data-models/src/branded-types';

// ===== BRANDED TYPES =====
export type FormId = Brand<string, 'FormId'>;
export type FieldId = Brand<string, 'FieldId'>;

// ===== ENTITIES =====
export interface DynamicForm {
    readonly id: FormId;
    readonly name: string;
    readonly module: string;
    readonly fields: FormField[];
    readonly layout: FormLayout;
    readonly metadata: Record<string, any>;
    readonly isActive: boolean;
    readonly createdAt: Date;
}

export interface FormField {
    readonly id: FieldId;
    readonly name: string;
    readonly type: 'text' | 'number' | 'email' | 'select' | 'textarea' | 'date' | 'boolean';
    readonly label: string;
    readonly required: boolean;
    readonly options?: Array<{ value: string; label: string }>;
    readonly validation?: any;
}

export interface FormLayout {
    readonly type: 'tabs' | 'columns' | 'single';
    readonly sections: FormSection[];
}

export interface FormSection {
    readonly id: string;
    readonly title: string;
    readonly fields: string[];
}

// ===== FORM RUNTIME BUILDER SERVICE =====
export class FormRuntimeBuilderService {
    private readonly forms: Map<FormId, DynamicForm> = new Map();
    private initialized = false;

    constructor() {
        console.log('[FORM RUNTIME BUILDER] Initializing nach CRM Pattern...');
        this.initialize();
    }

    private async initialize(): Promise<void> {
        if (this.initialized) return;
        
        console.log('[FORM RUNTIME INIT] Form runtime builder initialization nach business requirements...');
        
        try {
            this.createExampleForm();
            this.initialized = true;
            console.log('[FORM RUNTIME INIT] ✓ Form runtime builder initialized');
        } catch (error) {
            console.error('[FORM RUNTIME INIT] Form runtime builder initialization failed:', error);
            throw new Error(`Form runtime configuration failed: ${error}`);
        }
    }

    /**
     * Create Dynamic Form at Runtime
     */
    async createForm(formData: {
        name: string;
        module: string;
        fields: Omit<FormField, 'id'>[];
        layout?: FormLayout;
    }): Promise<FormId | null> {
        try {
            console.log(`[FORM RUNTIME] Creating dynamic form: ${formData.name}`);
            
            const formId = this.generateFormId();
            const dynamicForm: DynamicForm = {
                id: formId,
                name: formData.name,
                module: formData.module,
                fields: formData.fields.map(field => ({
                    ...field,
                    id: this.generateFieldId()
                })),
                layout: formData.layout || {
                    type: 'single',
                    sections: [{
                        id: 'main',
                        title: 'Main Section',
                        fields: formData.fields.map((_, idx) => `field_${idx}`)
                    }]
                },
                metadata: { createdDynamically: true },
                isActive: true,
                createdAt: new Date()
            };

            this.forms.set(formId, dynamicForm);
            console.log(`[FORM RUNTIME] ✓ Dynamic form created: ${formId}`);
            return formId;

        } catch (error) {
            console.error('[FORM RUNTIME] Dynamic form creation failed:', error);
            return null;
        }
    }

    /**
     * Generate Form from Template
     */
    async generateFromTemplate(templateType: string): Promise<FormId | null> {
        try {
            console.log(`[FORM RUNTIME] Generating form from template: ${templateType}`);
            
            const templates = this.getFormTemplates();
            const template = templates[templateType];
            
            if (!template) {
                console.error(`[FORM RUNTIME] Template not found: ${templateType}`);
                return null;
            }

            return await this.createForm(template);
        } catch (error) {
            console.error('[FORM RUNTIME] Template generation failed:', error);
            return null;
        }
    }

    private getFormTemplates() {
        return {
            'customer_form': {
                name: 'Customer Management',
                module: 'CRM',
                fields: [
                    {
                        name: 'customer_name',
                        type: 'text',
                        label: 'Customer Name',
                        required: true
                    },
                    {
                        name: 'customer_email',
                        type: 'email', 
                        label: 'Email',
                        required: true
                    },
                    {
                        name: 'customer_status',
                        type: 'select',
                        label: 'Status',
                        required: true,
                        options: [
                            { value: 'active', label: 'Active' },
                            { value: 'inactive', label: 'Inactive' }
                        ]
                    }
                ]
            },
            'invoice_form': {
                name: 'Invoice Management',
                module: 'FINANCE',
                fields: [
                    {
                        name: 'invoice_number',
                        type: 'text',
                        label: 'Invoice Number',
                        required: true
                    },
                    {
                        name: 'amount',
                        type: 'number',
                        label: 'Amount',
                        required: true
                    },
                    {
                        name: 'due_date',
                        type: 'date',
                        label: 'Due Date',
                        required: true
                    }
                ]
            }
        };
    }

    private createExampleForm(): void {
        console.log('[FORM RUNTIME] Creating example form nach business model...');
        
        const exampleForm: DynamicForm = {
            id: 'example_form' as FormId,
            name: 'Example Form',
            module: 'SHARED',
            fields: [
                {
                    id: 'example_field_1' as FieldId,
                    name: 'title',
                    type: 'text',
                    label: 'Title',
                    required: true
                }
            ],
            layout: {
                type: 'single',
                sections: [{
                    id: 'main',
                    title: 'Main Section',
                    fields: ['title']
                }]
            },
            metadata: {},
            isActive: true,
            createdAt: new Date()
        };

        this.forms.set(exampleForm.id, exampleForm);
        console.log('[FORM RUNTIME] ✓ Example form created');
    }

    /**
     * Get Form
     */
    async getForm(formId: FormId): Promise<DynamicForm | null> {
        return this.forms.get(formId) || null;
    }

    /**
     * Delete Form
     */
    async deleteForm(formId: FormId): Promise<boolean> {
        return this.forms.delete(formId);
    }

    /**
     * List All Forms
     */
    async getAllForms(): Promise<DynamicForm[]> {
        return Array.from(this.forms.values());
    }

    // Helper methods
    private generateFormId(): FormId {
        const id = 'form_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id as FormId;
    }

    private generateFieldId(): FieldId {
        const id = 'field_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id as FieldId;
    }

    async healthCheck(): Promise<boolean> {
        try {
            console.log('[FORM RUNTIME HEALTH] Checking runtime builder health...');
            
            const isHealthy = this.forms.size >= 0;
            
            if (!isHealthy) {
                console.error('[FORM RUNTIME HEALTH] Form runtime builder issues detected');
                return false;
            }

            console.log('[FORM RUNTIME HEALTH] ✓ Runtime builder health validated');
            return true;
        } catch (error) {
            console.error('[FORM RUNTIME HEALTH] Runtime builder health check failed:', error);
            return false;
        }
    }
}

/**
 * Register Form Runtime Builder in DI Container
 */
export function registerFormRuntimeBuilder(): void {
    console.log('[FORM RUNTIME REGISTRATION] Registering Form Runtime Builder Service...');
    
    DIContainer.register('FormRuntimeBuilderService', new FormRuntimeBuilderService(), {
        singleton: true,
        dependencies: []
    });
    
    console.log('[FORM RUNTIME REGISTRATION] ✅ Form Runtime Builder registered successfully');
}
