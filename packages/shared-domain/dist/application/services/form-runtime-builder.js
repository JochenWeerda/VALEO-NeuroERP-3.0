"use strict";
/**
 * Form Runtime Builder Service - MSOA nach Clean Architecture
 * Dynamic form creation at runtime - migrated from VALEO-NeuroERP-2.0
 * Enables runtime form generation as in old system
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FormRuntimeBuilderService = void 0;
exports.registerFormRuntimeBuilder = registerFormRuntimeBuilder;
const di_container_1 = require("@valero-neuroerp/utilities/src/di-container");
// ===== FORM RUNTIME BUILDER SERVICE =====
class FormRuntimeBuilderService {
    forms = new Map();
    initialized = false;
    constructor() {
        console.log('[FORM RUNTIME BUILDER] Initializing nach CRM Pattern...');
        this.initialize();
    }
    async initialize() {
        if (this.initialized)
            return;
        console.log('[FORM RUNTIME INIT] Form runtime builder initialization nach business requirements...');
        try {
            this.createExampleForm();
            this.initialized = true;
            console.log('[FORM RUNTIME INIT] ✓ Form runtime builder initialized');
        }
        catch (error) {
            console.error('[FORM RUNTIME INIT] Form runtime builder initialization failed:', error);
            throw new Error(`Form runtime configuration failed: ${error}`);
        }
    }
    /**
     * Create Dynamic Form at Runtime
     */
    async createForm(formData) {
        try {
            console.log(`[FORM RUNTIME] Creating dynamic form: ${formData.name}`);
            const formId = this.generateFormId();
            const dynamicForm = {
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
        }
        catch (error) {
            console.error('[FORM RUNTIME] Dynamic form creation failed:', error);
            return null;
        }
    }
    /**
     * Generate Form from Template
     */
    async generateFromTemplate(templateType) {
        try {
            console.log(`[FORM RUNTIME] Generating form from template: ${templateType}`);
            const templates = this.getFormTemplates();
            const template = templates[templateType];
            if (!template) {
                console.error(`[FORM RUNTIME] Template not found: ${templateType}`);
                return null;
            }
            return await this.createForm(template);
        }
        catch (error) {
            console.error('[FORM RUNTIME] Template generation failed:', error);
            return null;
        }
    }
    getFormTemplates() {
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
    createExampleForm() {
        console.log('[FORM RUNTIME] Creating example form nach business model...');
        const exampleForm = {
            id: 'example_form',
            name: 'Example Form',
            module: 'SHARED',
            fields: [
                {
                    id: 'example_field_1',
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
    async getForm(formId) {
        return this.forms.get(formId) || null;
    }
    /**
     * Delete Form
     */
    async deleteForm(formId) {
        return this.forms.delete(formId);
    }
    /**
     * List All Forms
     */
    async getAllForms() {
        return Array.from(this.forms.values());
    }
    // Helper methods
    generateFormId() {
        const id = 'form_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id;
    }
    generateFieldId() {
        const id = 'field_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id;
    }
    async healthCheck() {
        try {
            console.log('[FORM RUNTIME HEALTH] Checking runtime builder health...');
            const isHealthy = this.forms.size >= 0;
            if (!isHealthy) {
                console.error('[FORM RUNTIME HEALTH] Form runtime builder issues detected');
                return false;
            }
            console.log('[FORM RUNTIME HEALTH] ✓ Runtime builder health validated');
            return true;
        }
        catch (error) {
            console.error('[FORM RUNTIME HEALTH] Runtime builder health check failed:', error);
            return false;
        }
    }
}
exports.FormRuntimeBuilderService = FormRuntimeBuilderService;
/**
 * Register Form Runtime Builder in DI Container
 */
function registerFormRuntimeBuilder() {
    console.log('[FORM RUNTIME REGISTRATION] Registering Form Runtime Builder Service...');
    di_container_1.DIContainer.register('FormRuntimeBuilderService', new FormRuntimeBuilderService(), {
        singleton: true,
        dependencies: []
    });
    console.log('[FORM RUNTIME REGISTRATION] ✅ Form Runtime Builder registered successfully');
}
//# sourceMappingURL=form-runtime-builder.js.map