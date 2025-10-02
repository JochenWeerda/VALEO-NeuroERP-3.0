/**
 * Form Runtime Builder Service - MSOA nach Clean Architecture
 * Dynamic form creation at runtime - migrated from VALEO-NeuroERP-2.0
 * Enables runtime form generation as in old system
 */
import { Brand } from '@valero-neuroerp/data-models/src/branded-types';
export type FormId = Brand<string, 'FormId'>;
export type FieldId = Brand<string, 'FieldId'>;
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
    readonly options?: Array<{
        value: string;
        label: string;
    }>;
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
export declare class FormRuntimeBuilderService {
    private readonly forms;
    private initialized;
    constructor();
    private initialize;
    /**
     * Create Dynamic Form at Runtime
     */
    createForm(formData: {
        name: string;
        module: string;
        fields: Omit<FormField, 'id'>[];
        layout?: FormLayout;
    }): Promise<FormId | null>;
    /**
     * Generate Form from Template
     */
    generateFromTemplate(templateType: string): Promise<FormId | null>;
    private getFormTemplates;
    private createExampleForm;
    /**
     * Get Form
     */
    getForm(formId: FormId): Promise<DynamicForm | null>;
    /**
     * Delete Form
     */
    deleteForm(formId: FormId): Promise<boolean>;
    /**
     * List All Forms
     */
    getAllForms(): Promise<DynamicForm[]>;
    private generateFormId;
    private generateFieldId;
    healthCheck(): Promise<boolean>;
}
/**
 * Register Form Runtime Builder in DI Container
 */
export declare function registerFormRuntimeBuilder(): void;
//# sourceMappingURL=form-runtime-builder.d.ts.map