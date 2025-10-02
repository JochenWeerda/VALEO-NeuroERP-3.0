/**
 * VALEO NeuroERP 3.0 - Traceability Service
 *
 * GS1/EPCIS compliance and complete supply chain traceability
 */
import { EventBus } from '../infrastructure/event-bus/event-bus';
export interface EPCISEvent {
    eventId: string;
    eventType: 'object' | 'aggregation' | 'transaction' | 'transformation' | 'association';
    eventTime: Date;
    eventTimeZoneOffset: string;
    recordTime?: Date;
    epcList?: string[];
    parentEPC?: string;
    childEPCs?: string[];
    quantityList?: Array<{
        epcClass: string;
        quantity: number;
        uom: string;
    }>;
    businessLocation?: string;
    readPoint?: string;
    businessStep?: string;
    disposition?: string;
    businessTransactionList?: Array<{
        type: string;
        value: string;
    }>;
    sourceList?: Array<{
        type: string;
        value: string;
    }>;
    destinationList?: Array<{
        type: string;
        value: string;
    }>;
    sensorElementList?: Array<{
        sensorMetadata: {
            time: Date;
            deviceID?: string;
            deviceMetadata?: string;
            rawData?: string;
            dataProcessingMethod?: string;
            bizRules?: string;
        };
        sensorReport: Array<{
            type: string;
            value: string;
            uom?: string;
            minValue?: string;
            maxValue?: string;
            sDev?: string;
            chemicalSubstance?: string;
            microorganism?: string;
            deviceID?: string;
            deviceMetadata?: string;
            rawData?: string;
            time?: Date;
            component?: string;
        }>;
    }>;
    persistentDisposition?: {
        set?: string;
        unset?: string;
    };
    errorDeclaration?: {
        declarationTime: Date;
        reason: string;
        correctiveEventIDs?: string[];
    };
    customFields?: Record<string, any>;
}
export interface GS1Identifier {
    type: 'GTIN' | 'GLN' | 'SSCC' | 'GRAI' | 'GIAI' | 'GSRN' | 'GDTI' | 'GCN' | 'CPID' | 'GINC' | 'GSIN';
    value: string;
    humanReadable?: string;
    barcodeData: string;
    metadata?: {
        batch?: string;
        serial?: string;
        expiryDate?: Date;
        productionDate?: Date;
        bestBeforeDate?: Date;
        sellByDate?: Date;
        variant?: string;
        size?: string;
        color?: string;
    };
}
export interface TraceabilityChain {
    chainId: string;
    rootEPC: string;
    productType: string;
    currentStatus: string;
    events: EPCISEvent[];
    locations: Array<{
        gln: string;
        name: string;
        address: string;
        enteredAt: Date;
        exitedAt?: Date;
    }>;
    transformations: Array<{
        transformationId: string;
        inputEPCs: string[];
        outputEPCs: string[];
        transformationType: string;
        location: string;
        performedAt: Date;
        performedBy: string;
    }>;
    qualityChecks: Array<{
        checkId: string;
        checkType: string;
        result: 'pass' | 'fail' | 'warning';
        performedAt: Date;
        performedBy: string;
        location: string;
        parameters?: Record<string, any>;
        notes?: string;
    }>;
    recalls: Array<{
        recallId: string;
        reason: string;
        affectedEPCs: string[];
        initiatedAt: Date;
        status: 'active' | 'completed' | 'cancelled';
        resolution?: string;
    }>;
    compliance: {
        fsma?: boolean;
        gdp?: boolean;
        fda?: boolean;
        euFMD?: boolean;
        customCompliance?: Record<string, boolean>;
    };
    createdAt: Date;
    lastUpdated: Date;
}
export interface EPCISDocument {
    documentId: string;
    schemaVersion: string;
    creationDate: Date;
    epcisBody: {
        eventList: EPCISEvent[];
        vocabularyList?: {
            vocabularyElementList?: Array<{
                type: string;
                vocabularyElement: Array<{
                    id: string;
                    attribute: Array<{
                        id: string;
                        value: string;
                    }>;
                }>;
            }>;
        };
    };
    documentMetadata?: {
        documentType: string;
        businessProcess?: string;
        businessTransaction?: string;
        sender: string;
        receiver?: string;
        recipient?: string;
    };
    generatedAt: Date;
    expiresAt?: Date;
}
export interface TraceabilityQuery {
    queryId: string;
    queryType: 'simple' | 'complex' | 'masterData';
    parameters: {
        epc?: string;
        epcClass?: string;
        eventType?: string;
        businessLocation?: string;
        businessStep?: string;
        eventTimeStart?: Date;
        eventTimeEnd?: Date;
        recordTimeStart?: Date;
        recordTimeEnd?: Date;
        disposition?: string;
        customFilters?: Record<string, any>;
    };
    results: {
        totalEvents: number;
        events: EPCISEvent[];
        chains?: TraceabilityChain[];
        aggregations?: Record<string, any>;
    };
    executedAt: Date;
    executionTime: number;
}
export declare class TraceabilityService {
    private readonly eventBus;
    private readonly metrics;
    private epcisEvents;
    private traceabilityChains;
    constructor(eventBus: EventBus);
    /**
     * Create EPCIS event
     */
    createEPCISEvent(event: Omit<EPCISEvent, 'eventId'>): Promise<EPCISEvent>;
    /**
     * Generate GS1 identifier
     */
    generateGS1Identifier(type: GS1Identifier['type'], companyPrefix: string, metadata?: GS1Identifier['metadata']): Promise<GS1Identifier>;
    /**
     * Query traceability information
     */
    queryTraceability(query: Omit<TraceabilityQuery, 'queryId' | 'results' | 'executedAt' | 'executionTime'>): Promise<TraceabilityQuery>;
    /**
     * Generate EPCIS document
     */
    generateEPCISDocument(events: EPCISEvent[], documentMetadata?: EPCISDocument['documentMetadata']): Promise<EPCISDocument>;
    /**
     * Create traceability chain
     */
    createTraceabilityChain(rootEPC: string, productType: string): Promise<TraceabilityChain>;
    /**
     * Get product genealogy
     */
    getProductGenealogy(epc: string): Promise<{
        epc: string;
        parents: string[];
        children: string[];
        siblings: string[];
        transformations: Array<{
            transformationId: string;
            type: string;
            inputs: string[];
            outputs: string[];
            performedAt: Date;
        }>;
    }>;
    /**
     * Check compliance status
     */
    checkCompliance(epc: string, standards: string[]): Promise<Record<string, boolean>>;
    private updateTraceabilityChains;
    private generateGTINBase;
    private calculateGS1CheckDigit;
    private findMatchingEvents;
    private buildTraceabilityChains;
    private findRootEPC;
    private generateAggregations;
    private checkFSMACompliance;
    private checkGDPCompliance;
    private checkFDACompliance;
    private checkEUFMDCompliance;
    private publishTraceabilityEventCreatedEvent;
    private publishEPCISDocumentGeneratedEvent;
}
//# sourceMappingURL=traceability-service.d.ts.map