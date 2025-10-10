/**
 * VALEO NeuroERP 3.0 - Returns & Disposition Service
 *
 * RMA processing, quarantine management, and automated disposition workflows
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
import {
   QuarantineReleasedEvent,
   ReturnReceivedEvent
 } from '../core/domain-events/inventory-domain-events';

export interface ReturnMerchandiseAuthorization {
  rmaId: string;
  rmaNumber: string;
  orderId: string;
  customerId: string;
  status: 'draft' | 'approved' | 'rejected' | 'processed' | 'cancelled';
  reason: 'wrong_item' | 'damaged' | 'defective' | 'changed_mind' | 'late_delivery' | 'other';
  priority: 'low' | 'normal' | 'high' | 'urgent';

  items: Array<{
    sku: string;
    orderedQty: number;
    returnedQty: number;
    approvedQty: number;
    condition: 'new' | 'used' | 'damaged' | 'defective';
    disposition: 'pending' | 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
    notes?: string;
    images?: string[];
  }>;

  returnMethod: 'ship' | 'drop_off' | 'pickup';
  carrier?: string;
  trackingNumber?: string;
  returnFee?: number;
  refundAmount?: number;

  createdAt: Date;
  approvedAt?: Date;
  processedAt?: Date;
  completedAt?: Date;

  createdBy: string;
  approvedBy?: string;
  processedBy?: string;
}

export interface QuarantineRecord {
  quarantineId: string;
  itemId: string;
  sku: string;
  lot?: string;
  serial?: string;
  location: string;
  quantity: number;
  reason: 'quality_concern' | 'recall' | 'damage' | 'contamination' | 'expired' | 'investigation';
  severity: 'low' | 'medium' | 'high' | 'critical';

  status: 'active' | 'released' | 'destroyed' | 'returned' | 'transferred';
  quarantineDate: Date;
  releaseDate?: Date;
  expiryDate?: Date;

  testResults?: Array<{
    testType: 'visual' | 'functional' | 'chemical' | 'microbiological' | 'other';
    result: 'pass' | 'fail' | 'pending';
    testedBy: string;
    testedAt: Date;
    notes?: string;
    attachments?: string[];
  }>;

  disposition: 'pending' | 'release' | 'destroy' | 'return_to_supplier' | 'transfer' | 'donate';
  dispositionNotes?: string;
  dispositionBy?: string;
  dispositionAt?: Date;

  createdBy: string;
  costImpact?: number;
}

export interface DispositionWorkflow {
  workflowId: string;
  name: string;
  description: string;
  triggerCondition: {
    conditionType: 'return_reason' | 'item_condition' | 'quality_score' | 'supplier' | 'category';
    operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'between';
    value: string | number;
  };

  steps: Array<{
    stepId: string;
    name: string;
    type: 'inspection' | 'testing' | 'approval' | 'disposition' | 'notification';
    required: boolean;
    timeoutHours?: number;
    assigneeRole?: string;
    instructions?: string;
    automatedAction?: {
      actionType: 'set_disposition' | 'create_quarantine' | 'send_notification' | 'update_inventory';
      parameters: Record<string, unknown>;
    };
  }>;

  defaultDisposition: 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
  active: boolean;
  priority: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface ReturnProcessingResult {
  rmaId: string;
  processedItems: number;
  quarantinedItems: number;
  restockedItems: number;
  scrappedItems: number;
  repairedItems: number;
  returnedToSupplierItems: number;
  totalValue: number;
  processingTime: number;
  qualityScore: number;
}

export interface ReceivedReturnItem {
  sku: string;
  quantity: number;
  condition: string;
  location: string;
  inspector: string;
  notes?: string;
  images?: string[];
}

// Constants
const MS_TO_SECONDS = 1000;
const DEFAULT_ITEM_VALUE = 50.0;
const WORKFLOW_PRIORITY_HIGH = 10;
const WORKFLOW_PRIORITY_MEDIUM = 8;
const INSPECTION_TIMEOUT_24H = 24;
const TESTING_TIMEOUT_48H = 48;
const QUALITY_SCORE_NEW = 100;
const QUALITY_SCORE_USED = 70;
const QUALITY_SCORE_DAMAGED = 30;
const QUALITY_SCORE_DEFECTIVE = 10;

@injectable()
export class ReturnsDispositionService {
  private readonly metrics = new InventoryMetricsService();
  private readonly workflows: Map<string, DispositionWorkflow> = new Map();
  private readonly activeQuarantines: Map<string, QuarantineRecord> = new Map();

  constructor(
    private readonly eventBus: EventBus
  ) {
    this.initializeDefaultWorkflows();
  }

  /**
   * Create RMA from customer return request
   */
  async createRMA(request: {
    orderId: string;
    customerId: string;
    reason: ReturnMerchandiseAuthorization['reason'];
    items: Array<{
      sku: string;
      quantity: number;
      condition: ReturnMerchandiseAuthorization['items'][0]['condition'];
      notes?: string;
      images?: string[];
    }>;
    returnMethod?: ReturnMerchandiseAuthorization['returnMethod'];
    priority?: ReturnMerchandiseAuthorization['priority'];
  }): Promise<ReturnMerchandiseAuthorization> {
    const startTime = Date.now();

    try {
      // Validate order and items
      const orderDetails = await this.validateOrderForReturn(request.orderId, request.customerId);
      const validatedItems = await this.validateReturnItems(request.items, orderDetails);

      const rma: ReturnMerchandiseAuthorization = {
        rmaId: `rma_${Date.now()}`,
        rmaNumber: `RMA${Date.now()}`,
        orderId: request.orderId,
        customerId: request.customerId,
        status: 'draft',
        reason: request.reason,
        priority: request.priority ?? 'normal',
        items: validatedItems,
        returnMethod: request.returnMethod ?? 'ship',
        createdAt: new Date(),
        createdBy: 'system' // Would be actual user
      };

      // Auto-approve based on policy
      if (await this.shouldAutoApprove(rma)) {
        rma.status = 'approved';
        rma.approvedAt = new Date();
        rma.approvedBy = 'system';
      }

      this.metrics.recordDatabaseQueryDuration('returns', (Date.now() - startTime) / MS_TO_SECONDS, { operation: 'rma_creation' });
      this.metrics.incrementReturns('created');

      return rma;
    } catch (error) {
      this.metrics.incrementErrorCount('returns', { error_type: 'rma_creation_failed' });
      throw error;
    }
  }

  /**
   * Process received return
   */
  async processReceivedReturn(rmaId: string, receivedItems: Array<{
    sku: string;
    quantity: number;
    condition: string;
    location: string;
    inspector: string;
    notes?: string;
  }>): Promise<ReturnProcessingResult> {
    const startTime = Date.now();
    const rma = await this.getRMA(rmaId);

    if (!rma) {
      throw new Error(`RMA ${rmaId} not found`);
    }

    if (rma.status !== 'approved') {
      throw new Error(`RMA ${rmaId} is not approved for processing`);
    }

    try {
      const processingResult: ReturnProcessingResult = {
        rmaId,
        processedItems: 0,
        quarantinedItems: 0,
        restockedItems: 0,
        scrappedItems: 0,
        repairedItems: 0,
        returnedToSupplierItems: 0,
        totalValue: 0,
        processingTime: 0,
        qualityScore: 0
      };

      // Process each received item
      for (const receivedItem of receivedItems) {
        const rmaItem = rma.items.find(item => item.sku === receivedItem.sku);
        if (!rmaItem) {
          throw new Error(`Item ${receivedItem.sku} not found in RMA ${rmaId}`);
        }

        // Update RMA item with actual received data
        rmaItem.condition = receivedItem.condition as 'new' | 'used' | 'damaged' | 'defective';
        rmaItem.returnedQty = receivedItem.quantity;

        // Apply disposition workflow
        const disposition = await this.determineDisposition(receivedItem, rma.reason);
        rmaItem.disposition = disposition;

        // Execute disposition
        await this.executeDisposition(receivedItem, disposition, processingResult);

        processingResult.processedItems += receivedItem.quantity;
      }

      // Update RMA status
      rma.status = 'processed';
      rma.processedAt = new Date();
      rma.processedBy = 'system';

      // Calculate quality score
      processingResult.qualityScore = this.calculateQualityScore(receivedItems);
      processingResult.processingTime = (Date.now() - startTime) / MS_TO_SECONDS;

      // Publish event
      await this.publishReturnReceivedEvent(rma, receivedItems);

      this.metrics.recordDatabaseQueryDuration('returns', (Date.now() - startTime) / MS_TO_SECONDS, { operation: 'processing' });
      this.metrics.incrementReturns('processed');

      return processingResult;
    } catch (error) {
      this.metrics.incrementErrorCount('returns', { error_type: 'processing_failed' });
      throw error;
    }
  }

  /**
   * Create quarantine record
   */
  async createQuarantineRecord(record: Omit<QuarantineRecord, 'quarantineId' | 'quarantineDate' | 'status'>): Promise<QuarantineRecord> {
    const startTime = Date.now();

    try {
      const quarantine: QuarantineRecord = {
        ...record,
        quarantineId: `quar_${Date.now()}`,
        quarantineDate: new Date(),
        status: 'active'
      };

      this.activeQuarantines.set(quarantine.quarantineId, quarantine);

      // Publish event
      await this.publishQuarantineCreatedEvent(quarantine);

      this.metrics.recordDatabaseQueryDuration('quarantine', (Date.now() - startTime) / MS_TO_SECONDS, { operation: 'creation' });
      this.metrics.incrementQuarantines('created');

      return quarantine;
    } catch (error) {
      this.metrics.incrementErrorCount('quarantine', { error_type: 'creation_failed' });
      throw error;
    }
  }

  /**
   * Process quarantine disposition
   */
  async processQuarantineDisposition(
    quarantineId: string,
    disposition: QuarantineRecord['disposition'],
    dispositionBy: string,
    notes?: string
  ): Promise<void> {
    const startTime = Date.now();
    const quarantine = this.activeQuarantines.get(quarantineId);

    if (!quarantine) {
      throw new Error(`Quarantine ${quarantineId} not found`);
    }

    if (quarantine.status !== 'active') {
      throw new Error(`Quarantine ${quarantineId} is not active`);
    }

    try {
      // Update quarantine
      quarantine.disposition = disposition;
      if (notes !== undefined) {
        quarantine.dispositionNotes = notes;
      }
      quarantine.dispositionBy = dispositionBy;
      quarantine.dispositionAt = new Date();

      // Execute disposition action
      await this.executeQuarantineDisposition(quarantine);

      // Update status
      quarantine.status = disposition === 'release' ? 'released' : 'destroyed';
      quarantine.releaseDate = new Date();

      // Publish event
      await this.publishQuarantineReleasedEvent(quarantine);

      this.metrics.recordDatabaseQueryDuration('quarantine', (Date.now() - startTime) / MS_TO_SECONDS, { operation: 'disposition' });
      this.metrics.incrementQuarantines('processed');
    } catch (error) {
      this.metrics.incrementErrorCount('quarantine', { error_type: 'disposition_failed' });
      throw error;
    }
  }

  /**
   * Create disposition workflow
   */
  async createDispositionWorkflow(workflow: Omit<DispositionWorkflow, 'workflowId' | 'createdAt' | 'updatedAt'>): Promise<DispositionWorkflow> {
    const fullWorkflow: DispositionWorkflow = {
      ...workflow,
      workflowId: `workflow_${Date.now()}`,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.workflows.set(fullWorkflow.workflowId, fullWorkflow);
    return fullWorkflow;
  }

  /**
   * Get applicable workflows for return item
   */
  async getApplicableWorkflows(item: {
    sku: string;
    condition: string;
    returnReason: string;
    supplier?: string;
    category?: string;
  }): Promise<DispositionWorkflow[]> {
    const applicableWorkflows: DispositionWorkflow[] = [];

    for (const workflow of this.workflows.values()) {
      if (!workflow.active) continue;

      if (this.matchesWorkflowCondition(item, workflow.triggerCondition)) {
        applicableWorkflows.push(workflow);
      }
    }

    // Sort by priority
    return applicableWorkflows.sort((a, b) => b.priority - a.priority);
  }

  /**
   * Get quarantine analytics
   */
  async getQuarantineAnalytics(_period: 'day' | 'week' | 'month' = 'month'): Promise<{
    totalActive: number;
    byReason: Record<string, number>;
    bySeverity: Record<string, number>;
    averageProcessingTime: number;
    dispositionRates: Record<string, number>;
    costImpact: number;
  }> {
    const startTime = Date.now();

    try {
      const quarantines = Array.from(this.activeQuarantines.values());
      const analytics = {
        totalActive: quarantines.length,
        byReason: {} as Record<string, number>,
        bySeverity: {} as Record<string, number>,
        averageProcessingTime: 0,
        dispositionRates: {} as Record<string, number>,
        costImpact: 0
      };

      // Calculate distributions
      for (const quarantine of quarantines) {
        analytics.byReason[quarantine.reason] = (analytics.byReason[quarantine.reason] ?? 0) + 1;
        analytics.bySeverity[quarantine.severity] = (analytics.bySeverity[quarantine.severity] ?? 0) + 1;
        analytics.costImpact += quarantine.costImpact ?? 0;
      }

      this.metrics.recordDatabaseQueryDuration('quarantine', (Date.now() - startTime) / MS_TO_SECONDS, { operation: 'analytics' });

      return analytics;
    } catch (error) {
      this.metrics.incrementErrorCount('quarantine', { error_type: 'analytics_failed' });
      throw error;
    }
  }

  // Private helper methods

  private async validateOrderForReturn(orderId: string, customerId: string): Promise<{ orderId: string; customerId: string; items: unknown[] }> {
    // Mock validation
    return {
      orderId,
      customerId,
      items: []
    };
  }

  private async validateReturnItems(
    items: Array<{ sku: string; quantity: number; condition: string; notes?: string; images?: string[] }>,
    _orderDetails: { orderId: string; customerId: string; items: unknown[] }
  ): Promise<ReturnMerchandiseAuthorization['items']> {
    // Mock validation and enrichment
    return items.map(item => ({
      sku: item.sku,
      orderedQty: item.quantity,
      returnedQty: item.quantity,
      approvedQty: item.quantity,
      condition: item.condition as 'new' | 'used' | 'damaged' | 'defective',
      disposition: 'pending',
      ...(item.notes && { notes: item.notes }),
      ...(item.images && { images: item.images })
    }));
  }

  private async shouldAutoApprove(rma: ReturnMerchandiseAuthorization): Promise<boolean> {
    // Auto-approve based on policy
    return rma.reason === 'wrong_item' && rma.priority !== 'urgent';
  }

  private async determineDisposition(
    item: { sku: string; quantity: number; condition: string; location: string; inspector: string; notes?: string },
    returnReason: string
  ): Promise<ReturnMerchandiseAuthorization['items'][0]['disposition']> {
    // Get applicable workflows
    const workflows = await this.getApplicableWorkflows({
      sku: item.sku,
      condition: item.condition,
      returnReason,
      supplier: await this.getItemSupplier(item.sku),
      category: await this.getItemCategory(item.sku)
    });

    if (workflows.length > 0) {
       // Use highest priority workflow
       return workflows[0]?.defaultDisposition ?? 'scrap';
     }

    // Default disposition logic
    switch (item.condition) {
      case 'new':
        return 'restock';
      case 'used':
        return returnReason === 'changed_mind' ? 'restock' : 'scrap';
      case 'damaged':
        return 'scrap';
      case 'defective':
        return 'return_to_supplier';
      default:
        return 'scrap';
    }
  }

  private async executeDisposition(
    item: { sku: string; quantity: number; condition: string; location: string; inspector: string; notes?: string },
    disposition: ReturnMerchandiseAuthorization['items'][0]['disposition'],
    result: ReturnProcessingResult
  ): Promise<void> {
    switch (disposition) {
      case 'restock':
        await this.restockItem(item);
        result.restockedItems += item.quantity;
        break;
      case 'scrap':
        await this.scrapItem(item);
        result.scrappedItems += item.quantity;
        break;
      case 'repair':
        await this.createRepairOrder(item);
        result.repairedItems += item.quantity;
        break;
      case 'return_to_supplier':
        await this.returnToSupplier(item);
        result.returnedToSupplierItems += item.quantity;
        break;
      case 'donate':
        await this.donateItem(item);
        break;
      default:
        // Create quarantine for pending dispositions
        await this.createQuarantineRecord({
          itemId: `item_${Date.now()}`,
          sku: item.sku,
          location: item.location,
          quantity: item.quantity,
          reason: 'investigation',
          severity: 'medium',
          disposition: 'pending',
          createdBy: item.inspector,
          costImpact: await this.calculateItemValue(item.sku) * item.quantity
        });
        result.quarantinedItems += item.quantity;
    }
  }

  private calculateQualityScore(items: Array<{ condition: string }>): number {
    const conditionScores = { new: QUALITY_SCORE_NEW, used: QUALITY_SCORE_USED, damaged: QUALITY_SCORE_DAMAGED, defective: QUALITY_SCORE_DEFECTIVE };
    const totalScore = items.reduce((sum, item) =>
      sum + (conditionScores[item.condition as keyof typeof conditionScores] ?? 0), 0
    );
    return totalScore / items.length;
  }

  private async getRMA(rmaId: string): Promise<ReturnMerchandiseAuthorization | null> {
    // Mock implementation
    return {
      rmaId,
      rmaNumber: `RMA${rmaId}`,
      orderId: 'ORDER-123',
      customerId: 'CUSTOMER-123',
      status: 'approved',
      reason: 'wrong_item',
      priority: 'normal',
      items: [],
      returnMethod: 'ship',
      createdAt: new Date(),
      createdBy: 'system'
    };
  }

  private async getItemSupplier(_sku: string): Promise<string> {
    // Mock supplier lookup
    return 'SUPPLIER-001';
  }

  private async getItemCategory(_sku: string): Promise<string> {
    // Mock category lookup
    return 'ELECTRONICS';
  }

  private matchesWorkflowCondition(
    item: { sku: string; condition: string; returnReason: string; supplier?: string; category?: string },
    condition: DispositionWorkflow['triggerCondition']
  ): boolean {
    const itemValue = item[condition.conditionType as keyof typeof item];
    if (itemValue === undefined) return false;

    switch (condition.operator) {
      case 'equals':
        return itemValue === condition.value;
      case 'contains':
        return String(itemValue).includes(String(condition.value));
      case 'greater_than':
        return Number(itemValue) > Number(condition.value);
      case 'less_than':
        return Number(itemValue) < Number(condition.value);
      default:
        return false;
    }
  }

  private async executeQuarantineDisposition(quarantine: QuarantineRecord): Promise<void> {
    switch (quarantine.disposition) {
      case 'release':
        await this.releaseFromQuarantine(quarantine);
        break;
      case 'destroy':
        await this.destroyQuarantinedItem(quarantine);
        break;
      case 'return_to_supplier':
        await this.returnQuarantinedToSupplier(quarantine);
        break;
      case 'transfer':
        await this.transferQuarantinedItem(quarantine);
        break;
      case 'donate':
        await this.donateQuarantinedItem(quarantine);
        break;
      case 'pending':
        // No action for pending disposition
        break;
    }
  }

  // Mock implementation methods
  private async restockItem(_item: ReceivedReturnItem): Promise<void> {
    // Implementation would restock item to inventory
  }

  private async scrapItem(_item: ReceivedReturnItem): Promise<void> {
    // Implementation would scrap item
  }

  private async createRepairOrder(_item: ReceivedReturnItem): Promise<void> {
    // Implementation would create repair order
  }

  private async returnToSupplier(_item: ReceivedReturnItem): Promise<void> {
    // Implementation would return item to supplier
  }

  private async donateItem(_item: ReceivedReturnItem): Promise<void> {
    // Implementation would donate item
  }

  private async calculateItemValue(_sku: string): Promise<number> {
    // Mock value calculation
    return DEFAULT_ITEM_VALUE;
  }

  private async releaseFromQuarantine(_quarantine: QuarantineRecord): Promise<void> {
    // Implementation would release from quarantine
  }

  private async destroyQuarantinedItem(_quarantine: QuarantineRecord): Promise<void> {
    // Implementation would destroy quarantined item
  }

  private async returnQuarantinedToSupplier(_quarantine: QuarantineRecord): Promise<void> {
    // Implementation would return quarantined item to supplier
  }

  private async transferQuarantinedItem(_quarantine: QuarantineRecord): Promise<void> {
    // Implementation would transfer quarantined item
  }

  private async donateQuarantinedItem(_quarantine: QuarantineRecord): Promise<void> {
    // Implementation would donate quarantined item
  }

  private initializeDefaultWorkflows(): void {
    const workflows: DispositionWorkflow[] = [
      {
        workflowId: 'workflow_defective',
        name: 'Defective Item Return',
        description: 'Handle defective items returned by customers',
        triggerCondition: {
          conditionType: 'return_reason',
          operator: 'equals',
          value: 'defective'
        },
        steps: [
          {
            stepId: 'inspection',
            name: 'Quality Inspection',
            type: 'inspection',
            required: true,
            timeoutHours: INSPECTION_TIMEOUT_24H,
            instructions: 'Inspect item for defects and document findings'
          },
          {
            stepId: 'testing',
            name: 'Functional Testing',
            type: 'testing',
            required: true,
            timeoutHours: TESTING_TIMEOUT_48H,
            instructions: 'Test item functionality and document results'
          },
          {
            stepId: 'disposition',
            name: 'Determine Disposition',
            type: 'disposition',
            required: true,
            automatedAction: {
              actionType: 'set_disposition',
              parameters: { disposition: 'return_to_supplier' }
            }
          }
        ],
        defaultDisposition: 'return_to_supplier',
        active: true,
        priority: WORKFLOW_PRIORITY_HIGH,
        createdAt: new Date(),
        updatedAt: new Date()
      },
      {
        workflowId: 'workflow_damaged',
        name: 'Damaged Item Return',
        description: 'Handle damaged items returned by customers',
        triggerCondition: {
          conditionType: 'item_condition',
          operator: 'equals',
          value: 'damaged'
        },
        steps: [
          {
            stepId: 'assessment',
            name: 'Damage Assessment',
            type: 'inspection',
            required: true,
            timeoutHours: INSPECTION_TIMEOUT_24H,
            instructions: 'Assess damage severity and repair feasibility'
          },
          {
            stepId: 'disposition',
            name: 'Set Disposition',
            type: 'disposition',
            required: true,
            automatedAction: {
              actionType: 'set_disposition',
              parameters: { disposition: 'scrap' }
            }
          }
        ],
        defaultDisposition: 'scrap',
        active: true,
        priority: WORKFLOW_PRIORITY_MEDIUM,
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ];

    workflows.forEach(workflow => this.workflows.set(workflow.workflowId, workflow));
  }

  // Event publishing methods
  private async publishReturnReceivedEvent(
    rma: ReturnMerchandiseAuthorization,
    receivedItems: ReceivedReturnItem[]
  ): Promise<void> {
    const event: ReturnReceivedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.return.received',
      aggregateId: rma.rmaId,
      aggregateType: 'ReturnMerchandiseAuthorization',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      type: 'inventory.return.received',
      occurredAt: new Date(),
      aggregateVersion: 1,
      returnId: rma.rmaId,
      orderId: rma.orderId,
      items: receivedItems.map(item => ({
        sku: item.sku,
        orderedQty: item.quantity,
        returnedQty: item.quantity,
        approvedQty: item.quantity,
        condition: item.condition as 'new' | 'used' | 'damaged' | 'defective',
        disposition: 'pending' as const,
        notes: item.notes,
        images: item.images
      }))
    };

    await this.eventBus.publish(event);
  }

  private async publishQuarantineCreatedEvent(_quarantine: QuarantineRecord): Promise<void> {
    // Event would be published here
  }

  private async publishQuarantineReleasedEvent(quarantine: QuarantineRecord): Promise<void> {
    const event: QuarantineReleasedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.quarantine.released',
      aggregateId: quarantine.quarantineId,
      aggregateType: 'QuarantineRecord',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      type: 'inventory.quarantine.released',
      occurredAt: new Date(),
      aggregateVersion: 1,
      quarantineId: quarantine.quarantineId,
      disposition: quarantine.disposition as 'restock' | 'scrap' | 'repair' | 'return_to_supplier',
      releasedBy: quarantine.dispositionBy ?? 'system',
      reason: quarantine.reason ?? 'disposition_completed'
    };

    await this.eventBus.publish(event);
  }
}