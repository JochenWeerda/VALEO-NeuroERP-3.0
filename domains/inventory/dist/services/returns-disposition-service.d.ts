/**
 * VALEO NeuroERP 3.0 - Returns & Disposition Service
 *
 * RMA processing, quarantine management, and automated disposition workflows
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
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
        value: any;
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
            parameters: Record<string, any>;
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
export declare class ReturnsDispositionService {
    private readonly eventBus;
    private readonly metrics;
    private workflows;
    private activeQuarantines;
    constructor(eventBus: EventBus);
    /**
     * Create RMA from customer return request
     */
    createRMA(request: {
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
    }): Promise<ReturnMerchandiseAuthorization>;
    /**
     * Process received return
     */
    processReceivedReturn(rmaId: string, receivedItems: Array<{
        sku: string;
        quantity: number;
        condition: string;
        location: string;
        inspector: string;
        notes?: string;
    }>): Promise<ReturnProcessingResult>;
    /**
     * Create quarantine record
     */
    createQuarantineRecord(record: Omit<QuarantineRecord, 'quarantineId' | 'quarantineDate' | 'status'>): Promise<QuarantineRecord>;
    /**
     * Process quarantine disposition
     */
    processQuarantineDisposition(quarantineId: string, disposition: QuarantineRecord['disposition'], dispositionBy: string, notes?: string): Promise<void>;
    /**
     * Create disposition workflow
     */
    createDispositionWorkflow(workflow: Omit<DispositionWorkflow, 'workflowId' | 'createdAt' | 'updatedAt'>): Promise<DispositionWorkflow>;
    /**
     * Get applicable workflows for return item
     */
    getApplicableWorkflows(item: {
        sku: string;
        condition: string;
        returnReason: string;
        supplier?: string;
        category?: string;
    }): Promise<DispositionWorkflow[]>;
    /**
     * Get quarantine analytics
     */
    getQuarantineAnalytics(period?: 'day' | 'week' | 'month'): Promise<{
        totalActive: number;
        byReason: Record<string, number>;
        bySeverity: Record<string, number>;
        averageProcessingTime: number;
        dispositionRates: Record<string, number>;
        costImpact: number;
    }>;
    private validateOrderForReturn;
    private validateReturnItems;
    private shouldAutoApprove;
    private determineDisposition;
    private executeDisposition;
    private calculateQualityScore;
    private getRMA;
    private getItemSupplier;
    private getItemCategory;
    private matchesWorkflowCondition;
    private executeQuarantineDisposition;
    private restockItem;
    private scrapItem;
    private createRepairOrder;
    private returnToSupplier;
    private donateItem;
    private calculateItemValue;
    private releaseFromQuarantine;
    private destroyQuarantinedItem;
    private returnQuarantinedToSupplier;
    private transferQuarantinedItem;
    private donateQuarantinedItem;
    private initializeDefaultWorkflows;
    private publishReturnReceivedEvent;
    private publishQuarantineCreatedEvent;
    private publishQuarantineReleasedEvent;
}
//# sourceMappingURL=returns-disposition-service.d.ts.map