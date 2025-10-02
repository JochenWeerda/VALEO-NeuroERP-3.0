"use strict";
/**
 * VALEO NeuroERP 3.0 - Traceability Service
 *
 * GS1/EPCIS compliance and complete supply chain traceability
 */
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
var __setFunctionName = (this && this.__setFunctionName) || function (f, name, prefix) {
    if (typeof name === "symbol") name = name.description ? "[".concat(name.description, "]") : "";
    return Object.defineProperty(f, "name", { configurable: true, value: prefix ? "".concat(prefix, " ", name) : name });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TraceabilityService = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("../infrastructure/observability/metrics-service");
let TraceabilityService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var TraceabilityService = _classThis = class {
        constructor(eventBus) {
            this.eventBus = eventBus;
            this.metrics = new metrics_service_1.InventoryMetricsService();
            this.epcisEvents = new Map();
            this.traceabilityChains = new Map();
        }
        /**
         * Create EPCIS event
         */
        async createEPCISEvent(event) {
            const startTime = Date.now();
            try {
                const epcisEvent = {
                    ...event,
                    eventId: `epcis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
                };
                this.epcisEvents.set(epcisEvent.eventId, epcisEvent);
                // Update traceability chains
                await this.updateTraceabilityChains(epcisEvent);
                // Publish event
                await this.publishTraceabilityEventCreatedEvent(epcisEvent);
                this.metrics.recordDatabaseQueryDuration('traceability.event_creation', (Date.now() - startTime) / 1000, {});
                this.metrics.incrementTraceabilityEvents('created');
                return epcisEvent;
            }
            catch (error) {
                this.metrics.incrementErrorCount('traceability.event_creation_failed', { error: 'event_creation_error' });
                throw error;
            }
        }
        /**
         * Generate GS1 identifier
         */
        async generateGS1Identifier(type, companyPrefix, metadata) {
            const startTime = Date.now();
            try {
                let value;
                let humanReadable;
                let barcodeData;
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
                        const ssccBase = `3${companyPrefix}${Date.now().toString().slice(-9)}`;
                        const ssccCheck = this.calculateGS1CheckDigit(ssccBase);
                        value = ssccBase + ssccCheck;
                        humanReadable = value;
                        barcodeData = `(00)${value}`;
                        break;
                    case 'GLN':
                        // GLN format: 13 digits + check digit
                        const glnBase = companyPrefix + '00000'; // Simplified
                        const glnCheck = this.calculateGS1CheckDigit(glnBase);
                        value = glnBase + glnCheck;
                        humanReadable = value;
                        barcodeData = `(414)${value}`;
                        break;
                    default:
                        throw new Error(`Unsupported GS1 identifier type: ${type}`);
                }
                const identifier = {
                    type,
                    value,
                    humanReadable,
                    barcodeData,
                    metadata
                };
                this.metrics.recordDatabaseQueryDuration('traceability.gs1_generation', (Date.now() - startTime) / 1000, {});
                return identifier;
            }
            catch (error) {
                this.metrics.incrementErrorCount('traceability.gs1_generation_failed', { error: 'gs1_generation_error' });
                throw error;
            }
        }
        /**
         * Query traceability information
         */
        async queryTraceability(query) {
            const startTime = Date.now();
            try {
                const events = this.findMatchingEvents(query.parameters);
                const chains = query.queryType === 'complex' ? await this.buildTraceabilityChains(events) : undefined;
                const traceabilityQuery = {
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
            }
            catch (error) {
                this.metrics.incrementErrorCount('traceability.query_failed', { error: 'query_error' });
                throw error;
            }
        }
        /**
         * Generate EPCIS document
         */
        async generateEPCISDocument(events, documentMetadata) {
            const startTime = Date.now();
            try {
                const document = {
                    documentId: `epcis_doc_${Date.now()}`,
                    schemaVersion: '2.0',
                    creationDate: new Date(),
                    epcisBody: {
                        eventList: events
                    },
                    documentMetadata,
                    generatedAt: new Date(),
                    expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000) // 1 year
                };
                // Publish event
                await this.publishEPCISDocumentGeneratedEvent(document);
                this.metrics.recordDatabaseQueryDuration('traceability.epcis_generation', (Date.now() - startTime) / 1000, {});
                return document;
            }
            catch (error) {
                this.metrics.incrementErrorCount('traceability.epcis_generation_failed', { error: 'epcis_generation_error' });
                throw error;
            }
        }
        /**
         * Create traceability chain
         */
        async createTraceabilityChain(rootEPC, productType) {
            const startTime = Date.now();
            try {
                const chain = {
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
            }
            catch (error) {
                this.metrics.incrementErrorCount('traceability.chain_creation_failed', { error: 'chain_creation_error' });
                throw error;
            }
        }
        /**
         * Get product genealogy
         */
        async getProductGenealogy(epc) {
            const genealogy = {
                epc,
                parents: [],
                children: [],
                siblings: [],
                transformations: []
            };
            // Find parent EPCs (aggregation events where this EPC is a child)
            for (const event of Array.from(this.epcisEvents.values())) {
                if (event.eventType === 'aggregation' && event.childEPCs?.includes(epc)) {
                    if (event.parentEPC) {
                        genealogy.parents.push(event.parentEPC);
                    }
                }
            }
            // Find child EPCs (aggregation events where this EPC is a parent)
            for (const event of Array.from(this.epcisEvents.values())) {
                if (event.eventType === 'aggregation' && event.parentEPC === epc) {
                    if (event.childEPCs) {
                        genealogy.children.push(...event.childEPCs);
                    }
                }
            }
            // Find transformations involving this EPC
            for (const chain of Array.from(this.traceabilityChains.values())) {
                for (const transformation of chain.transformations) {
                    if (transformation.inputEPCs.includes(epc) || transformation.outputEPCs.includes(epc)) {
                        genealogy.transformations.push({
                            transformationId: transformation.transformationId,
                            type: transformation.transformationType,
                            inputs: transformation.inputEPCs,
                            outputs: transformation.outputEPCs,
                            performedAt: transformation.performedAt
                        });
                    }
                }
            }
            return genealogy;
        }
        /**
         * Check compliance status
         */
        async checkCompliance(epc, standards) {
            const compliance = {};
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
        async updateTraceabilityChains(event) {
            // Find or create traceability chains for EPCs in this event
            const epcs = [...(event.epcList || []), ...(event.childEPCs || []), event.parentEPC].filter(Boolean);
            for (const epc of epcs) {
                let chain = Array.from(this.traceabilityChains.values()).find(c => c.events.some(e => e.epcList?.includes(epc) || e.childEPCs?.includes(epc) || e.parentEPC === epc));
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
        generateGTINBase(companyPrefix) {
            // Generate 12-digit base for GTIN-13
            const itemRef = Math.floor(Math.random() * 100000).toString().padStart(5, '0');
            return companyPrefix + itemRef;
        }
        calculateGS1CheckDigit(data) {
            let sum = 0;
            for (let i = data.length - 1; i >= 0; i--) {
                const digit = parseInt(data[i]);
                sum += i % 2 === 0 ? digit * 3 : digit;
            }
            const remainder = sum % 10;
            return remainder === 0 ? 0 : 10 - remainder;
        }
        findMatchingEvents(parameters) {
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
        async buildTraceabilityChains(events) {
            const chains = [];
            // Group events by root EPC and build chains
            const eventsByRoot = new Map();
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
        findRootEPC(event) {
            // Simplified: return first EPC or parent
            return event.epcList?.[0] || event.parentEPC || null;
        }
        generateAggregations(events) {
            const aggregations = {
                totalEvents: events.length,
                eventTypes: {},
                locations: {},
                businessSteps: {},
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
        async checkFSMACompliance(epc) {
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
        async checkGDPCompliance(epc) {
            // Check GDP (Good Distribution Practice) compliance
            const genealogy = await this.getProductGenealogy(epc);
            // Check temperature monitoring during transportation
            for (const event of Array.from(this.epcisEvents.values())) {
                if (event.epcList?.includes(epc) && event.sensorElementList) {
                    const tempSensors = event.sensorElementList.filter(s => s.sensorReport.some(r => r.type === 'temperature'));
                    if (tempSensors.length === 0) {
                        return false;
                    }
                }
            }
            return true;
        }
        async checkFDACompliance(epc) {
            // Check FDA compliance requirements
            const chain = Array.from(this.traceabilityChains.values()).find(c => c.rootEPC === epc);
            return !!(chain?.compliance.fda);
        }
        async checkEUFMDCompliance(epc) {
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
        async publishTraceabilityEventCreatedEvent(event) {
            const traceabilityEvent = {
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
                businessLocation: event.businessLocation || '',
                identifier: event.eventId,
                location: event.businessLocation || '',
                actor: 'system',
                timestamp: event.eventTime
            };
            await this.eventBus.publish(traceabilityEvent);
        }
        async publishEPCISDocumentGeneratedEvent(document) {
            const epcisEvent = {
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
                businessLocation: '',
                businessProcess: '',
                sender: 'system',
                receiver: 'system'
            };
            await this.eventBus.publish(epcisEvent);
        }
    };
    __setFunctionName(_classThis, "TraceabilityService");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        TraceabilityService = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return TraceabilityService = _classThis;
})();
exports.TraceabilityService = TraceabilityService;
//# sourceMappingURL=traceability-service.js.map