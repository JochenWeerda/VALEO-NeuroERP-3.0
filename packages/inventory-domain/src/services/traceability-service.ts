/**
 * VALEO NeuroERP 3.0 - Traceability Service
 *
 * GS1/EPCIS compliance and complete supply chain traceability
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
import {
  EPCISDocumentGeneratedEvent,
  TraceabilityEventCreatedEvent
} from '../core/domain-events/inventory-domain-events';

// Constants
const RANDOM_ID_LENGTH = 9;
const RANDOM_ID_START = 2;
const RANDOM_BASE = 36;
const MS_PER_DAY = 1000 * 60 * 60 * 24;
const EPCIS_EXPIRY_DAYS = 365;
const GS1_DATE_LENGTH = 8;
const GS1_DATE_START = 2;
const GTIN_ITEM_REF_LENGTH = 5;
const GTIN_ITEM_REF_MAX = 100000;
const SSCC_SERIAL_LENGTH = 9;
const GLN_SUFFIX = '00000';
const SCHEMA_VERSION = '2.0';

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

  customFields?: Record<string, unknown>;
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
    parameters?: Record<string, unknown>;
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
    customFilters?: Record<string, unknown>;
  };

  results: {
    totalEvents: number;
    events: EPCISEvent[];
    chains?: TraceabilityChain[];
    aggregations?: Record<string, unknown>;
  };

  executedAt: Date;
  executionTime: number;
}

@injectable()
export class TraceabilityService {
  private readonly metrics = new InventoryMetricsService();
  private readonly epcisEvents: Map<string, EPCISEvent> = new Map();
  private readonly traceabilityChains: Map<string, TraceabilityChain> = new Map();

  constructor(
    private readonly eventBus: EventBus
  ) {}

  /**
   * Create EPCIS event
   */
  async createEPCISEvent(event: Omit<EPCISEvent, 'eventId'>): Promise<EPCISEvent> {
    const startTime = Date.now();

    try {
      const epcisEvent: EPCISEvent = {
        ...event,
        eventId: `epcis_${Date.now()}_${Math.random().toString(RANDOM_BASE).substr(RANDOM_ID_START, RANDOM_ID_LENGTH)}`
      };

      this.epcisEvents.set(epcisEvent.eventId, epcisEvent);

      // Update traceability chains
      await this.updateTraceabilityChains(epcisEvent);

      // Publish event
      await this.publishTraceabilityEventCreatedEvent(epcisEvent);

      this.metrics.recordDatabaseQueryDuration('traceability.event_creation', (Date.now() - startTime) / 1000, {});
      this.metrics.incrementTraceabilityEvents('created');

      return epcisEvent;
    } catch (error) {
      this.metrics.incrementErrorCount('traceability.event_creation_failed', { error: 'event_creation_error' });
      throw error;
    }
  }

  /**
   * Generate GS1 identifier
   */
  async generateGS1Identifier(
    type: GS1Identifier['type'],
    companyPrefix: string,
    metadata?: GS1Identifier['metadata']
  ): Promise<GS1Identifier> {
    const startTime = Date.now();

    try {
      let value: string;
      let humanReadable: string;
      let barcodeData: string;

      switch (type) {
        case 'GTIN':
          // GTIN-13 format: (01) + 12 digits + check digit
          const gtinBase = this.generateGTINBase(companyPrefix);
          const checkDigit = this.calculateGS1CheckDigit(gtinBase);
          value = gtinBase + checkDigit;
          humanReadable = value;
          barcodeData = `(01)${value}`;
          break;

        case 'SSCC':
          // SSCC format: (00) + extension digit + 16 digits + check digit
          const ssccBase = `3${companyPrefix}${Date.now().toString().slice(-SSCC_SERIAL_LENGTH)}`;
          const ssccCheck = this.calculateGS1CheckDigit(ssccBase);
          value = ssccBase + ssccCheck;
          humanReadable = value;
          barcodeData = `(00)${value}`;
          break;

        case 'GLN':
          // GLN format: 13 digits + check digit
          const glnBase = companyPrefix + GLN_SUFFIX; // Simplified
          const glnCheck = this.calculateGS1CheckDigit(glnBase);
          value = glnBase + glnCheck;
          humanReadable = value;
          barcodeData = `(414)${value}`;
          break;

        default:
          throw new Error(`Unsupported GS1 identifier type: ${type}`);
      }

      const identifier: GS1Identifier = {
        type,
        value,
        humanReadable,
        barcodeData,
        metadata
      };

      this.metrics.recordDatabaseQueryDuration('traceability.gs1_generation', (Date.now() - startTime) / 1000, {});

      return identifier;
    } catch (error) {
      this.metrics.incrementErrorCount('traceability.gs1_generation_failed', { error: 'gs1_generation_error' });
      throw error;
    }
  }

  /**
   * Query traceability information
   */
  async queryTraceability(query: Omit<TraceabilityQuery, 'queryId' | 'results' | 'executedAt' | 'executionTime'>): Promise<TraceabilityQuery> {
    const startTime = Date.now();

    try {
      const events = this.findMatchingEvents(query.parameters);
      const chains = query.queryType === 'complex' ? await this.buildTraceabilityChains(events) : undefined;

      const traceabilityQuery: TraceabilityQuery = {
        queryId: `query_${Date.now()}`,
        ...query,
        results: {
          totalEvents: events.length,
          events,
          chains,
          aggregations: this.generateAggregations(events)
        },
        executedAt: new Date(),
        executionTime: Date.now() - startTime
      };

      this.metrics.recordDatabaseQueryDuration('traceability.query_execution', (Date.now() - startTime) / 1000, {});

      return traceabilityQuery;
    } catch (error) {
      this.metrics.incrementErrorCount('traceability.query_failed', { error: 'query_error' });
      throw error;
    }
  }

  /**
   * Generate EPCIS document
   */
  async generateEPCISDocument(
    events: EPCISEvent[],
    documentMetadata?: EPCISDocument['documentMetadata']
  ): Promise<EPCISDocument> {
    const startTime = Date.now();

    try {
      const document: EPCISDocument = {
        documentId: `epcis_doc_${Date.now()}`,
        schemaVersion: SCHEMA_VERSION,
        creationDate: new Date(),
        epcisBody: {
          eventList: events
        },
        documentMetadata,
        generatedAt: new Date(),
        expiresAt: new Date(Date.now() + EPCIS_EXPIRY_DAYS * MS_PER_DAY) // 1 year
      };

      // Publish event
      await this.publishEPCISDocumentGeneratedEvent(document);

      this.metrics.recordDatabaseQueryDuration('traceability.epcis_generation', (Date.now() - startTime) / 1000, {});

      return document;
    } catch (error) {
      this.metrics.incrementErrorCount('traceability.epcis_generation_failed', { error: 'epcis_generation_error' });
      throw error;
    }
  }

  /**
   * Create traceability chain
   */
  async createTraceabilityChain(rootEPC: string, productType: string): Promise<TraceabilityChain> {
    const startTime = Date.now();

    try {
      const chain: TraceabilityChain = {
        chainId: `chain_${Date.now()}`,
        rootEPC,
        productType,
        currentStatus: 'active',
        events: [],
        locations: [],
        transformations: [],
        qualityChecks: [],
        recalls: [],
        compliance: {
          fsma: false,
          gdp: false,
          fda: false,
          euFMD: false
        },
        createdAt: new Date(),
        lastUpdated: new Date()
      };

      this.traceabilityChains.set(chain.chainId, chain);

      this.metrics.recordDatabaseQueryDuration('traceability.chain_creation', (Date.now() - startTime) / 1000, {});

      return chain;
    } catch (error) {
      this.metrics.incrementErrorCount('traceability.chain_creation_failed', { error: 'chain_creation_error' });
      throw error;
    }
  }

  /**
   * Get product genealogy
   */
  async getProductGenealogy(epc: string): Promise<{
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
  }> {
    const _genealogy = {
      epc,
      parents: [] as string[],
      children: [] as string[],
      siblings: [] as string[],
      transformations: [] as Array<{
        transformationId: string;
        type: string;
        inputs: string[];
        outputs: string[];
        performedAt: Date;
      }>
    };

    // Find parent EPCs (aggregation events where this EPC is a child)
    for (const event of Array.from(this.epcisEvents.values())) {
      if (event.eventType === 'aggregation' && event.childEPCs?.includes(epc)) {
        if (event.parentEPC) {
          _genealogy.parents.push(event.parentEPC);
        }
      }
    }

    // Find child EPCs (aggregation events where this EPC is a parent)
    for (const event of Array.from(this.epcisEvents.values())) {
      if (event.eventType === 'aggregation' && event.parentEPC === epc) {
        if (event.childEPCs) {
          _genealogy.children.push(...event.childEPCs);
        }
      }
    }

    // Find transformations involving this EPC
    for (const chain of Array.from(this.traceabilityChains.values())) {
      for (const transformation of chain.transformations) {
        if (transformation.inputEPCs.includes(epc) || transformation.outputEPCs.includes(epc)) {
          _genealogy.transformations.push({
            transformationId: transformation.transformationId,
            type: transformation.transformationType,
            inputs: transformation.inputEPCs,
            outputs: transformation.outputEPCs,
            performedAt: transformation.performedAt
          });
        }
      }
    }

    return _genealogy;
  }

  /**
   * Check compliance status
   */
  async checkCompliance(epc: string, standards: string[]): Promise<Record<string, boolean>> {
    const compliance: Record<string, boolean> = {};

    for (const standard of standards) {
      switch (standard.toLowerCase()) {
        case 'fsma':
          compliance.fsma = await this.checkFSMACompliance(epc);
          break;
        case 'gdp':
          compliance.gdp = await this.checkGDPCompliance(epc);
          break;
        case 'fda':
          compliance.fda = await this.checkFDACompliance(epc);
          break;
        case 'eufmd':
          compliance.euFMD = await this.checkEUFMDCompliance(epc);
          break;
        default:
          compliance[standard] = false;
      }
    }

    return compliance;
  }

  // Private helper methods

  private async updateTraceabilityChains(event: EPCISEvent): Promise<void> {
    // Find or create traceability chains for EPCs in this event
    const epcs = [...(event.epcList || []), ...(event.childEPCs || []), event.parentEPC].filter(Boolean);

    for (const epc of epcs) {
      let chain = Array.from(this.traceabilityChains.values()).find(c =>
        c.events.some(e => e.epcList?.includes(epc) || e.childEPCs?.includes(epc) || e.parentEPC === epc)
      );

      if (!chain) {
        chain = await this.createTraceabilityChain(epc, 'unknown');
      }

      chain.events.push(event);
      chain.lastUpdated = new Date();

      // Update locations if business location is provided
      if (event.businessLocation) {
        const existingLocation = chain.locations.find(l => l.gln === event.businessLocation);
        if (!existingLocation) {
          chain.locations.push({
            gln: event.businessLocation,
            name: 'Unknown Location', // Would be resolved from GLN
            address: 'Unknown Address',
            enteredAt: event.eventTime
          });
        }
      }
    }
  }

  private generateGTINBase(companyPrefix: string): string {
    // Generate 12-digit base for GTIN-13
    const itemRef = Math.floor(Math.random() * GTIN_ITEM_REF_MAX).toString().padStart(GTIN_ITEM_REF_LENGTH, '0');
    return companyPrefix + itemRef;
  }

  private calculateGS1CheckDigit(data: string): number {
    let sum = 0;
    for (let i = data.length - 1; i >= 0; i--) {
      const digit = parseInt(data[i]);
      sum += i % 2 === 0 ? digit * 3 : digit;
    }
    const remainder = sum % 10;
    return remainder === 0 ? 0 : 10 - remainder;
  }

  private findMatchingEvents(parameters: TraceabilityQuery['parameters']): EPCISEvent[] {
    return Array.from(this.epcisEvents.values()).filter(event => {
      if (parameters.epc && !event.epcList?.includes(parameters.epc) &&
          !event.childEPCs?.includes(parameters.epc) && event.parentEPC !== parameters.epc) {
        return false;
      }

      if (parameters.eventType && event.eventType !== parameters.eventType) {
        return false;
      }

      if (parameters.businessLocation && event.businessLocation !== parameters.businessLocation) {
        return false;
      }

      if (parameters.businessStep && event.businessStep !== parameters.businessStep) {
        return false;
      }

      if (parameters.eventTimeStart && event.eventTime < parameters.eventTimeStart) {
        return false;
      }

      if (parameters.eventTimeEnd && event.eventTime > parameters.eventTimeEnd) {
        return false;
      }

      return true;
    });
  }

  private async buildTraceabilityChains(events: EPCISEvent[]): Promise<TraceabilityChain[]> {
    const chains: TraceabilityChain[] = [];

    // Group events by root EPC and build chains
    const eventsByRoot = new Map<string, EPCISEvent[]>();

    for (const event of events) {
      const rootEPC = this.findRootEPC(event);
      if (rootEPC) {
        const chainEvents = eventsByRoot.get(rootEPC) || [];
        chainEvents.push(event);
        eventsByRoot.set(rootEPC, chainEvents);
      }
    }

    for (const [rootEPC, chainEvents] of Array.from(eventsByRoot.entries())) {
      const chain = await this.createTraceabilityChain(rootEPC, 'product');
      chain.events = chainEvents;
      chains.push(chain);
    }

    return chains;
  }

  private findRootEPC(event: EPCISEvent): string | null {
    // Simplified: return first EPC or parent
    return event.epcList?.[0] || event.parentEPC || null;
  }

  private generateAggregations(events: EPCISEvent[]): Record<string, unknown> {
    const aggregations = {
      totalEvents: events.length,
      eventTypes: {} as Record<string, number>,
      locations: {} as Record<string, number>,
      businessSteps: {} as Record<string, number>,
      timeRange: {
        start: events.length > 0 ? new Date(Math.min(...events.map(e => e.eventTime.getTime()))) : null,
        end: events.length > 0 ? new Date(Math.max(...events.map(e => e.eventTime.getTime()))) : null
      }
    };

    for (const event of events) {
      aggregations.eventTypes[event.eventType] = (aggregations.eventTypes[event.eventType] || 0) + 1;

      if (event.businessLocation) {
        aggregations.locations[event.businessLocation] = (aggregations.locations[event.businessLocation] || 0) + 1;
      }

      if (event.businessStep) {
        aggregations.businessSteps[event.businessStep] = (aggregations.businessSteps[event.businessStep] || 0) + 1;
      }
    }

    return aggregations;
  }

  private async checkFSMACompliance(epc: string): Promise<boolean> {
    // Check FSMA (Food Safety Modernization Act) compliance
    const genealogy = await this.getProductGenealogy(epc);

    // Check if all transformations have proper documentation
    for (const transformation of genealogy.transformations) {
      if (!transformation.performedAt) {
        return false;
      }
    }

    // Check for recalls
    const chain = Array.from(this.traceabilityChains.values()).find(c => c.rootEPC === epc);
    if (chain?.recalls.some(r => r.status === 'active')) {
      return false;
    }

    return true;
  }

  private async checkGDPCompliance(epc: string): Promise<boolean> {
    // Check GDP (Good Distribution Practice) compliance
    const genealogy = await this.getProductGenealogy(epc);

    // Check temperature monitoring during transportation
    for (const event of Array.from(this.epcisEvents.values())) {
      if (event.epcList?.includes(epc) && event.sensorElementList) {
        const tempSensors = event.sensorElementList.filter(s =>
          s.sensorReport.some(r => r.type === 'temperature')
        );
        if (tempSensors.length === 0) {
          return false;
        }
      }
    }

    return true;
  }

  private async checkFDACompliance(epc: string): Promise<boolean> {
    // Check FDA compliance requirements
    const chain = Array.from(this.traceabilityChains.values()).find(c => c.rootEPC === epc);
    return !!(chain?.compliance.fda);
  }

  private async checkEUFMDCompliance(epc: string): Promise<boolean> {
    // Check EU Food and Feed Hygiene compliance
    const genealogy = await this.getProductGenealogy(epc);

    // Check if all locations are approved
    for (const transformation of genealogy.transformations) {
      // Would check against approved facilities list
      if (!transformation.performedAt) {
        return false;
      }
    }

    return true;
  }

  // Event publishing methods
  private async publishTraceabilityEventCreatedEvent(event: EPCISEvent): Promise<void> {
    const traceabilityEvent: TraceabilityEventCreatedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.traceability.event.created',
      type: 'inventory.traceability.event.created',
      aggregateId: event.eventId,
      aggregateType: 'EPCISEvent',
      eventVersion: 1,
      occurredOn: new Date(),
      occurredAt: new Date(),
      aggregateVersion: 1,
      tenantId: 'default',
      traceabilityEventType: event.eventType === 'association' ? 'object' : event.eventType,
      epcList: event.epcList || [],
      businessLocation: event.businessLocation || ''
    };

    await this.eventBus.publish(traceabilityEvent);
  }

  private async publishEPCISDocumentGeneratedEvent(document: EPCISDocument): Promise<void> {
    const epcisEvent: EPCISDocumentGeneratedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.epcis.document.generated',
      type: 'inventory.epcis.document.generated',
      aggregateId: document.documentId,
      aggregateType: 'EPCISDocument',
      eventVersion: 1,
      occurredOn: new Date(),
      occurredAt: new Date(),
      aggregateVersion: 1,
      tenantId: 'default',
      documentId: document.documentId,
      eventCount: document.epcisBody.eventList.length,
      documentType: 'master_data',
      businessLocation: ''
    };

    await this.eventBus.publish(epcisEvent);
  }
}