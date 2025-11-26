/**
 * Agribusiness Workflow Service
 * Automated Workflows & Notifications for Agribusiness Operations
 * Based on Odoo automation patterns
 */

import { Farmer } from '../entities/farmer';
import { FieldServiceTask } from '../entities/field-service-task';

export interface NotificationService {
  sendEmail(to: string, subject: string, body: string): Promise<void>;
  sendSMS(to: string, message: string): Promise<void>;
  sendPushNotification(userId: string, title: string, message: string): Promise<void>;
}

export interface EventPublisher {
  publish(event: string, data: any): Promise<void>;
}

export interface WorkflowRule {
  id: string;
  name: string;
  description?: string;
  trigger: WorkflowTrigger;
  conditions: WorkflowCondition[];
  actions: WorkflowAction[];
  isActive: boolean;
  priority: number;
  createdAt: Date;
  updatedAt: Date;
}

export type WorkflowTrigger =
  | { type: 'BATCH_CREATED'; batchType?: string }
  | { type: 'BATCH_EXPIRING'; daysBeforeExpiry: number }
  | { type: 'CONTRACT_SIGNED'; contractType?: string }
  | { type: 'CONTRACT_FULFILLMENT_THRESHOLD'; threshold: number }
  | { type: 'CERTIFICATION_EXPIRING'; daysBeforeExpiry: number }
  | { type: 'TASK_COMPLETED'; taskType?: string }
  | { type: 'FARMER_REGISTERED' }
  | { type: 'QUALITY_SCORE_BELOW'; threshold: number }
  | { type: 'SCHEDULED'; cron: string };

export interface WorkflowCondition {
  field: string;
  operator: 'equals' | 'not_equals' | 'greater_than' | 'less_than' | 'contains' | 'in';
  value: any;
}

export type WorkflowAction =
  | { type: 'SEND_EMAIL'; to: string; template: string; data?: any }
  | { type: 'SEND_SMS'; to: string; template: string; data?: any }
  | { type: 'SEND_PUSH'; userId: string; title: string; message: string }
  | { type: 'CREATE_TASK'; taskData: any }
  | { type: 'UPDATE_STATUS'; entityType: string; entityId: string; status: string }
  | { type: 'PUBLISH_EVENT'; event: string; data: any }
  | { type: 'ASSIGN_TO_USER'; userId: string; entityType: string; entityId: string };

export interface AgribusinessWorkflowServiceDependencies {
  notificationService: NotificationService;
  eventPublisher: EventPublisher;
}

export class AgribusinessWorkflowService {
  private workflowRules: Map<string, WorkflowRule> = new Map();

  constructor(private deps: AgribusinessWorkflowServiceDependencies) {}

  /**
   * Register a workflow rule
   */
  async registerWorkflowRule(rule: Omit<WorkflowRule, 'id' | 'createdAt' | 'updatedAt'>): Promise<WorkflowRule> {
    const workflowRule: WorkflowRule = {
      ...rule,
      id: `workflow-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.workflowRules.set(workflowRule.id, workflowRule);
    return workflowRule;
  }

  /**
   * Execute workflow rules for a trigger
   */
  async executeWorkflows(trigger: WorkflowTrigger, context: any): Promise<void> {
    const matchingRules = Array.from(this.workflowRules.values())
      .filter(rule => rule.isActive && this.matchesTrigger(rule.trigger, trigger))
      .sort((a, b) => b.priority - a.priority);

    for (const rule of matchingRules) {
      if (this.evaluateConditions(rule.conditions, context)) {
        await this.executeActions(rule.actions, context);
      }
    }
  }

  /**
   * Check if trigger matches
   */
  private matchesTrigger(ruleTrigger: WorkflowTrigger, eventTrigger: WorkflowTrigger): boolean {
    if (ruleTrigger.type !== eventTrigger.type) return false;

    switch (ruleTrigger.type) {
      case 'BATCH_CREATED':
        return !ruleTrigger.batchType || ruleTrigger.batchType === (eventTrigger as any).batchType;
      case 'BATCH_EXPIRING':
        return ruleTrigger.daysBeforeExpiry === (eventTrigger as any).daysBeforeExpiry;
      case 'CONTRACT_SIGNED':
        return !ruleTrigger.contractType || ruleTrigger.contractType === (eventTrigger as any).contractType;
      case 'CONTRACT_FULFILLMENT_THRESHOLD':
        return ruleTrigger.threshold === (eventTrigger as any).threshold;
      case 'CERTIFICATION_EXPIRING':
        return ruleTrigger.daysBeforeExpiry === (eventTrigger as any).daysBeforeExpiry;
      case 'TASK_COMPLETED':
        return !ruleTrigger.taskType || ruleTrigger.taskType === (eventTrigger as any).taskType;
      case 'QUALITY_SCORE_BELOW':
        return ruleTrigger.threshold === (eventTrigger as any).threshold;
      default:
        return true;
    }
  }

  /**
   * Evaluate workflow conditions
   */
  private evaluateConditions(conditions: WorkflowCondition[], context: any): boolean {
    if (conditions.length === 0) return true;

    return conditions.every(condition => {
      const fieldValue = this.getFieldValue(context, condition.field);
      const conditionValue = condition.value;

      switch (condition.operator) {
        case 'equals':
          return fieldValue === conditionValue;
        case 'not_equals':
          return fieldValue !== conditionValue;
        case 'greater_than':
          return fieldValue > conditionValue;
        case 'less_than':
          return fieldValue < conditionValue;
        case 'contains':
          return String(fieldValue).includes(String(conditionValue));
        case 'in':
          return Array.isArray(conditionValue) && conditionValue.includes(fieldValue);
        default:
          return false;
      }
    });
  }

  /**
   * Get field value from context (supports nested fields)
   */
  private getFieldValue(context: any, field: string): any {
    const parts = field.split('.');
    let value = context;
    for (const part of parts) {
      value = value?.[part];
    }
    return value;
  }

  /**
   * Execute workflow actions
   */
  private async executeActions(actions: WorkflowAction[], context: any): Promise<void> {
    for (const action of actions) {
      try {
        await this.executeAction(action, context);
      } catch (error) {
        console.error(`Error executing workflow action ${action.type}:`, error);
        // Continue with other actions even if one fails
      }
    }
  }

  /**
   * Execute a single workflow action
   */
  private async executeAction(action: WorkflowAction, context: any): Promise<void> {
    switch (action.type) {
      case 'SEND_EMAIL':
        const emailBody = this.renderTemplate(action.template, { ...context, ...action.data });
        await this.deps.notificationService.sendEmail(action.to, emailBody, emailBody);
        break;

      case 'SEND_SMS':
        const smsMessage = this.renderTemplate(action.template, { ...context, ...action.data });
        await this.deps.notificationService.sendSMS(action.to, smsMessage);
        break;

      case 'SEND_PUSH':
        await this.deps.notificationService.sendPushNotification(
          action.userId,
          action.title,
          action.message
        );
        break;

      case 'PUBLISH_EVENT':
        await this.deps.eventPublisher.publish(action.event, { ...context, ...action.data });
        break;

      case 'CREATE_TASK':
        // Would integrate with task service
        await this.deps.eventPublisher.publish('task.create', { ...action.taskData, ...context });
        break;

      case 'UPDATE_STATUS':
        await this.deps.eventPublisher.publish(`${action.entityType}.update`, {
          id: action.entityId,
          status: action.status,
          ...context,
        });
        break;

      case 'ASSIGN_TO_USER':
        await this.deps.eventPublisher.publish(`${action.entityType}.assign`, {
          id: action.entityId,
          userId: action.userId,
          ...context,
        });
        break;
    }
  }

  /**
   * Simple template rendering (would use a proper templating engine in production)
   */
  private renderTemplate(template: string, data: any): string {
    let rendered = template;
    for (const [key, value] of Object.entries(data)) {
      rendered = rendered.replace(new RegExp(`{{${key}}}`, 'g'), String(value));
    }
    return rendered;
  }

  /**
   * Trigger: Batch created
   */
  async onBatchCreated(batch: any): Promise<void> {
    await this.executeWorkflows(
      { type: 'BATCH_CREATED', batchType: batch.batchType },
      { batch }
    );
  }

  /**
   * Trigger: Batch expiring
   */
  async onBatchExpiring(batch: any, daysUntilExpiry: number): Promise<void> {
    await this.executeWorkflows(
      { type: 'BATCH_EXPIRING', daysBeforeExpiry: daysUntilExpiry },
      { batch, daysUntilExpiry }
    );
  }

  /**
   * Trigger: Contract signed
   */
  async onContractSigned(contract: any): Promise<void> {
    await this.executeWorkflows(
      { type: 'CONTRACT_SIGNED', contractType: contract.contractType },
      { contract }
    );
  }

  /**
   * Trigger: Contract fulfillment threshold
   */
  async onContractFulfillmentThreshold(contract: any, fulfillmentRate: number): Promise<void> {
    await this.executeWorkflows(
      { type: 'CONTRACT_FULFILLMENT_THRESHOLD', threshold: Math.floor(fulfillmentRate) },
      { contract, fulfillmentRate }
    );
  }

  /**
   * Trigger: Certification expiring
   */
  async onCertificationExpiring(farmer: Farmer, certification: any, daysUntilExpiry: number): Promise<void> {
    await this.executeWorkflows(
      { type: 'CERTIFICATION_EXPIRING', daysBeforeExpiry: daysUntilExpiry },
      { farmer, certification, daysUntilExpiry }
    );
  }

  /**
   * Trigger: Task completed
   */
  async onTaskCompleted(task: FieldServiceTask): Promise<void> {
    await this.executeWorkflows(
      { type: 'TASK_COMPLETED', taskType: task.taskType },
      { task }
    );
  }

  /**
   * Trigger: Farmer registered
   */
  async onFarmerRegistered(farmer: Farmer): Promise<void> {
    await this.executeWorkflows({ type: 'FARMER_REGISTERED' }, { farmer });
  }

  /**
   * Trigger: Quality score below threshold
   */
  async onQualityScoreBelow(farmer: Farmer, qualityScore: number): Promise<void> {
    await this.executeWorkflows(
      { type: 'QUALITY_SCORE_BELOW', threshold: Math.floor(qualityScore) },
      { farmer, qualityScore }
    );
  }

  /**
   * Get all workflow rules
   */
  async getWorkflowRules(): Promise<WorkflowRule[]> {
    return Array.from(this.workflowRules.values());
  }

  /**
   * Get workflow rule by ID
   */
  async getWorkflowRule(id: string): Promise<WorkflowRule | null> {
    return this.workflowRules.get(id) || null;
  }

  /**
   * Update workflow rule
   */
  async updateWorkflowRule(id: string, updates: Partial<WorkflowRule>): Promise<WorkflowRule> {
    const rule = this.workflowRules.get(id);
    if (!rule) {
      throw new Error(`Workflow rule with id ${id} not found`);
    }

    const updated: WorkflowRule = {
      ...rule,
      ...updates,
      updatedAt: new Date(),
    };

    this.workflowRules.set(id, updated);
    return updated;
  }

  /**
   * Delete workflow rule
   */
  async deleteWorkflowRule(id: string): Promise<void> {
    if (!this.workflowRules.has(id)) {
      throw new Error(`Workflow rule with id ${id} not found`);
    }
    this.workflowRules.delete(id);
  }
}

