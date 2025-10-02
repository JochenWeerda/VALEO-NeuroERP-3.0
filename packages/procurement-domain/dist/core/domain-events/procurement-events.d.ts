export interface ProcurementDomainEvent {
    eventId: string;
    eventType: string;
    aggregateId: string;
    aggregateType: string;
    eventVersion: number;
    occurredOn: Date;
    eventData: Record<string, any>;
    metadata?: {
        userId?: string;
        correlationId?: string;
        causationId?: string;
        tenantId?: string;
        source: 'api' | 'ui' | 'system' | 'batch' | 'integration';
        traceId?: string;
    };
}
export interface SupplierCreatedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierCreated';
    aggregateType: 'Supplier';
    eventData: {
        supplierId: string;
        name: string;
        legalName?: string;
        type: string;
        country: string;
        vatId?: string;
        email?: string;
        category: string;
        createdBy: string;
    };
}
export interface SupplierUpdatedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierUpdated';
    aggregateType: 'Supplier';
    eventData: {
        supplierId: string;
        changes: Record<string, {
            oldValue: any;
            newValue: any;
        }>;
        updatedBy: string;
    };
}
export interface SupplierActivatedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierActivated';
    aggregateType: 'Supplier';
    eventData: {
        supplierId: string;
        activatedBy: string;
        activatedAt: string;
        riskScore?: number;
        category: string;
    };
}
export interface SupplierSuspendedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierSuspended';
    aggregateType: 'Supplier';
    eventData: {
        supplierId: string;
        suspendedBy: string;
        suspendedAt: string;
        reason: string;
    };
}
export interface SupplierDeactivatedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierDeactivated';
    aggregateType: 'Supplier';
    eventData: {
        supplierId: string;
        deactivatedBy: string;
        deactivatedAt: string;
        reason: string;
    };
}
export interface SupplierOnboardingStartedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierOnboardingStarted';
    aggregateType: 'SupplierOnboarding';
    eventData: {
        onboardingId: string;
        supplierId: string;
        checklistTemplate: string;
        assignedTo?: string;
        dueDate?: string;
        startedBy: string;
    };
}
export interface SupplierOnboardingCompletedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierOnboardingCompleted';
    aggregateType: 'SupplierOnboarding';
    eventData: {
        onboardingId: string;
        supplierId: string;
        completedBy: string;
        completedAt: string;
        riskScore: number;
        esgScore?: number;
        certifications: string[];
        complianceFlags: string[];
    };
}
export interface SupplierOnboardingRejectedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierOnboardingRejected';
    aggregateType: 'SupplierOnboarding';
    eventData: {
        onboardingId: string;
        supplierId: string;
        rejectedBy: string;
        rejectedAt: string;
        reason: string;
        issues: string[];
    };
}
export interface SupplierRiskAssessedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierRiskAssessed';
    aggregateType: 'SupplierRisk';
    eventData: {
        assessmentId: string;
        supplierId: string;
        riskScore: number;
        riskLevel: 'low' | 'medium' | 'high' | 'critical';
        categories: {
            cyber: number;
            compliance: number;
            financial: number;
            geographic: number;
            esg: number;
        };
        assessedBy: string;
        assessedAt: string;
        validUntil: string;
    };
}
export interface SupplierRiskAlertTriggeredEvent extends ProcurementDomainEvent {
    eventType: 'SupplierRiskAlertTriggered';
    aggregateType: 'SupplierRisk';
    eventData: {
        alertId: string;
        supplierId: string;
        riskType: string;
        severity: 'low' | 'medium' | 'high' | 'critical';
        description: string;
        threshold: number;
        currentValue: number;
        triggeredAt: string;
    };
}
export interface SupplierNonComplianceDetectedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierNonComplianceDetected';
    aggregateType: 'SupplierCompliance';
    eventData: {
        supplierId: string;
        complianceType: string;
        issue: string;
        severity: 'low' | 'medium' | 'high' | 'critical';
        detectedAt: string;
        deadline?: string;
        requiredAction: string;
    };
}
export interface RfqCreatedEvent extends ProcurementDomainEvent {
    eventType: 'RfqCreated';
    aggregateType: 'Rfq';
    eventData: {
        rfqId: string;
        title: string;
        category: string;
        currency: string;
        totalValue?: number;
        deadline: string;
        invitedSuppliers: string[];
        items: Array<{
            sku: string;
            name: string;
            quantity: number;
            uom: string;
            specifications?: Record<string, any>;
        }>;
        createdBy: string;
    };
}
export interface BidSubmittedEvent extends ProcurementDomainEvent {
    eventType: 'BidSubmitted';
    aggregateType: 'Bid';
    eventData: {
        bidId: string;
        rfqId: string;
        supplierId: string;
        totalPrice: number;
        currency: string;
        validUntil: string;
        items: Array<{
            sku: string;
            quantity: number;
            unitPrice: number;
            totalPrice: number;
            deliveryDate: string;
            notes?: string;
        }>;
        terms: {
            paymentTerms: string;
            deliveryTerms: string;
            warranty?: string;
        };
        submittedBy: string;
        submittedAt: string;
    };
}
export interface RfqAwardedEvent extends ProcurementDomainEvent {
    eventType: 'RfqAwarded';
    aggregateType: 'Rfq';
    eventData: {
        rfqId: string;
        awardedTo: string;
        totalAwardedValue: number;
        currency: string;
        awardedBy: string;
        awardedAt: string;
        awardReason: string;
        items: Array<{
            sku: string;
            awardedSupplier: string;
            awardedPrice: number;
            quantity: number;
        }>;
    };
}
export interface ContractCreatedEvent extends ProcurementDomainEvent {
    eventType: 'ContractCreated';
    aggregateType: 'Contract';
    eventData: {
        contractId: string;
        supplierId: string;
        title: string;
        type: string;
        value: number;
        currency: string;
        startDate: string;
        endDate: string;
        autoRenewal: boolean;
        createdBy: string;
    };
}
export interface ContractSignedEvent extends ProcurementDomainEvent {
    eventType: 'ContractSigned';
    aggregateType: 'Contract';
    eventData: {
        contractId: string;
        signedBy: string;
        signedAt: string;
        signedBySupplier?: string;
        effectiveDate: string;
        fileHash: string;
    };
}
export interface ContractExpiringEvent extends ProcurementDomainEvent {
    eventType: 'ContractExpiring';
    aggregateType: 'Contract';
    eventData: {
        contractId: string;
        supplierId: string;
        expiryDate: string;
        daysUntilExpiry: number;
        autoRenewal: boolean;
        renewalNoticeSent: boolean;
    };
}
export interface CatalogRegisteredEvent extends ProcurementDomainEvent {
    eventType: 'CatalogRegistered';
    aggregateType: 'Catalog';
    eventData: {
        catalogId: string;
        supplierId: string;
        type: 'cxml' | 'oci' | 'internal';
        endpoint?: string;
        authMethod: string;
        lastSyncAt?: string;
        itemCount: number;
        registeredBy: string;
    };
}
export interface PunchOutSessionStartedEvent extends ProcurementDomainEvent {
    eventType: 'PunchOutSessionStarted';
    aggregateType: 'PunchOutSession';
    eventData: {
        sessionId: string;
        supplierId: string;
        protocol: 'cxml' | 'oci';
        returnUrl: string;
        sessionToken: string;
        expiresAt: string;
        startedBy: string;
    };
}
export interface CatalogItemUpdatedEvent extends ProcurementDomainEvent {
    eventType: 'CatalogItemUpdated';
    aggregateType: 'CatalogItem';
    eventData: {
        itemId: string;
        catalogId: string;
        supplierId: string;
        sku: string;
        changes: Record<string, {
            oldValue: any;
            newValue: any;
        }>;
        updatedBy: string;
        updatedAt: string;
    };
}
export interface RequisitionCreatedEvent extends ProcurementDomainEvent {
    eventType: 'RequisitionCreated';
    aggregateType: 'Requisition';
    eventData: {
        requisitionId: string;
        requesterId: string;
        costCenter: string;
        totalValue: number;
        currency: string;
        items: Array<{
            sku: string;
            name: string;
            quantity: number;
            estimatedPrice: number;
            requiredDate: string;
        }>;
        justification: string;
        createdBy: string;
    };
}
export interface RequisitionApprovedEvent extends ProcurementDomainEvent {
    eventType: 'RequisitionApproved';
    aggregateType: 'Requisition';
    eventData: {
        requisitionId: string;
        approvedBy: string;
        approvedAt: string;
        approvalLevel: number;
        comments?: string;
        nextApprover?: string;
    };
}
export interface PoCreatedEvent extends ProcurementDomainEvent {
    eventType: 'PoCreated';
    aggregateType: 'PurchaseOrder';
    eventData: {
        poId: string;
        supplierId: string;
        requisitionId?: string;
        currency: string;
        totalValue: number;
        items: Array<{
            sku: string;
            name: string;
            quantity: number;
            unitPrice: number;
            totalPrice: number;
            deliveryDate: string;
        }>;
        terms: {
            incoterm: string;
            paymentTerms: string;
            deliveryTerms: string;
        };
        createdBy: string;
    };
}
export interface PoChangedEvent extends ProcurementDomainEvent {
    eventType: 'PoChanged';
    aggregateType: 'PurchaseOrder';
    eventData: {
        poId: string;
        changes: Record<string, {
            oldValue: any;
            newValue: any;
        }>;
        changedBy: string;
        changeReason: string;
        version: number;
    };
}
export interface GoodsReceivedEvent extends ProcurementDomainEvent {
    eventType: 'GoodsReceived';
    aggregateType: 'GoodsReceipt';
    eventData: {
        receiptId: string;
        poId: string;
        receivedBy: string;
        receivedAt: string;
        items: Array<{
            poLineId: string;
            sku: string;
            orderedQuantity: number;
            receivedQuantity: number;
            unitPrice: number;
            qualityStatus: 'accepted' | 'rejected' | 'pending';
            notes?: string;
        }>;
        totalReceivedValue: number;
        hasDiscrepancies: boolean;
    };
}
export interface InvoiceMatchedEvent extends ProcurementDomainEvent {
    eventType: 'InvoiceMatched';
    aggregateType: 'InvoiceMatch';
    eventData: {
        matchId: string;
        invoiceId: string;
        poId: string;
        receiptId: string;
        matchStatus: 'matched' | 'exception';
        totalInvoiceAmount: number;
        totalPoAmount: number;
        totalReceivedAmount: number;
        currency: string;
        discrepancies: Array<{
            type: 'quantity' | 'price' | 'quality';
            description: string;
            severity: 'low' | 'medium' | 'high';
            poValue: number;
            invoiceValue: number;
            difference: number;
        }>;
        matchedBy: 'system' | 'manual';
        matchedAt: string;
        forwardedToFinance: boolean;
    };
}
export interface MatchExceptionEvent extends ProcurementDomainEvent {
    eventType: 'MatchException';
    aggregateType: 'InvoiceMatch';
    eventData: {
        matchId: string;
        invoiceId: string;
        poId: string;
        exceptionType: string;
        description: string;
        severity: 'low' | 'medium' | 'high';
        requiresApproval: boolean;
        assignedTo?: string;
        deadline?: string;
    };
}
export interface SupplierScoreUpdatedEvent extends ProcurementDomainEvent {
    eventType: 'SupplierScoreUpdated';
    aggregateType: 'SupplierPerformance';
    eventData: {
        supplierId: string;
        period: string;
        scores: {
            otif: number;
            quality: number;
            responsiveness: number;
            priceCompetitiveness: number;
            overall: number;
        };
        metrics: {
            totalOrders: number;
            onTimeDeliveries: number;
            qualityIncidents: number;
            averageResponseTime: number;
        };
        calculatedAt: string;
        nextReviewDate: string;
    };
}
export interface SpendAnalysisCompletedEvent extends ProcurementDomainEvent {
    eventType: 'SpendAnalysisCompleted';
    aggregateType: 'SpendAnalysis';
    eventData: {
        analysisId: string;
        period: string;
        totalSpend: number;
        currency: string;
        categoryBreakdown: Record<string, number>;
        supplierBreakdown: Array<{
            supplierId: string;
            supplierName: string;
            spendAmount: number;
            percentage: number;
        }>;
        abcAnalysis: {
            A: {
                count: number;
                spend: number;
                percentage: number;
            };
            B: {
                count: number;
                spend: number;
                percentage: number;
            };
            C: {
                count: number;
                spend: number;
                percentage: number;
            };
        };
        maverickSpend: {
            amount: number;
            percentage: number;
            incidents: number;
        };
        recommendations: Array<{
            type: string;
            description: string;
            potentialSavings: number;
            confidence: number;
        }>;
        completedAt: string;
    };
}
export interface AnomalyDetectedEvent extends ProcurementDomainEvent {
    eventType: 'AnomalyDetected';
    aggregateType: 'AnomalyDetection';
    eventData: {
        anomalyId: string;
        type: 'price' | 'quantity' | 'delivery' | 'quality';
        entityType: 'supplier' | 'item' | 'order';
        entityId: string;
        description: string;
        severity: 'low' | 'medium' | 'high' | 'critical';
        expectedValue: number;
        actualValue: number;
        deviation: number;
        confidence: number;
        detectedAt: string;
        requiresAction: boolean;
        suggestedActions: string[];
    };
}
export interface ProcurementProcessAlertEvent extends ProcurementDomainEvent {
    eventType: 'ProcurementProcessAlert';
    aggregateType: 'System';
    eventData: {
        alertId: string;
        alertType: 'escalation' | 'deadline' | 'exception' | 'performance';
        severity: 'info' | 'warning' | 'error' | 'critical';
        title: string;
        description: string;
        affectedEntities: Array<{
            type: string;
            id: string;
            name?: string;
        }>;
        suggestedActions: string[];
        createdAt: string;
        expiresAt?: string;
    };
}
export type ProcurementEvent = SupplierCreatedEvent | SupplierUpdatedEvent | SupplierActivatedEvent | SupplierSuspendedEvent | SupplierDeactivatedEvent | SupplierOnboardingStartedEvent | SupplierOnboardingCompletedEvent | SupplierOnboardingRejectedEvent | SupplierRiskAssessedEvent | SupplierRiskAlertTriggeredEvent | SupplierNonComplianceDetectedEvent | RfqCreatedEvent | BidSubmittedEvent | RfqAwardedEvent | ContractCreatedEvent | ContractSignedEvent | ContractExpiringEvent | CatalogRegisteredEvent | PunchOutSessionStartedEvent | CatalogItemUpdatedEvent | RequisitionCreatedEvent | RequisitionApprovedEvent | PoCreatedEvent | PoChangedEvent | GoodsReceivedEvent | InvoiceMatchedEvent | MatchExceptionEvent | SupplierScoreUpdatedEvent | SpendAnalysisCompletedEvent | AnomalyDetectedEvent | ProcurementProcessAlertEvent;
//# sourceMappingURL=procurement-events.d.ts.map