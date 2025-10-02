"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EventConsumer = void 0;
exports.createEventConsumer = createEventConsumer;
exports.getEventConsumer = getEventConsumer;
const nats_1 = require("nats");
const drizzle_orm_1 = require("drizzle-orm");
const node_postgres_1 = require("drizzle-orm/node-postgres");
const pg_1 = require("pg");
const schema_1 = require("../db/schema");
class EventConsumer {
    config;
    connection = null;
    subscription = null;
    db;
    pool;
    isConnected = false;
    isProcessing = false;
    reconnectAttempts = 0;
    maxReconnectAttempts = 5;
    reconnectDelayMs = 1000;
    constructor(config) {
        this.config = config;
        this.maxReconnectAttempts = config.maxReconnectAttempts || 5;
        this.reconnectDelayMs = config.reconnectDelayMs || 1000;
        this.pool = new pg_1.Pool({
            connectionString: config.databaseUrl,
        });
        this.db = (0, node_postgres_1.drizzle)(this.pool);
    }
    async connect() {
        try {
            this.connection = await (0, nats_1.connect)({
                servers: this.config.natsUrl,
                reconnect: true,
                maxReconnectAttempts: this.maxReconnectAttempts,
                reconnectTimeWait: this.reconnectDelayMs,
            });
            this.isConnected = true;
            this.reconnectAttempts = 0;
            console.log('Analytics event consumer connected to NATS');
            this.connection.closed().then(() => {
                this.isConnected = false;
                console.log('NATS connection closed');
            });
        }
        catch (error) {
            console.error('Failed to connect to NATS:', error);
            throw error;
        }
    }
    async startConsuming() {
        if (!this.isConnected || !this.connection) {
            throw new Error('Event consumer is not connected to NATS');
        }
        try {
            this.subscription = this.connection.subscribe('*.events.>', {
                callback: this.handleEvent.bind(this),
            });
            console.log('Started consuming business events');
        }
        catch (error) {
            console.error('Failed to start consuming events:', error);
            throw error;
        }
    }
    async handleEvent(err, msg) {
        if (err) {
            console.error('Error receiving message:', err);
            return;
        }
        if (this.isProcessing) {
            msg.nak();
            return;
        }
        this.isProcessing = true;
        try {
            const jsonCodec = (0, nats_1.JSONCodec)();
            const event = jsonCodec.decode(msg.data);
            console.log(`Processing event: ${event.eventType} (${event.eventId})`);
            await this.processEvent(event);
            msg.ack();
            console.log(`Successfully processed event: ${event.eventType}`);
        }
        catch (error) {
            console.error('Error processing event:', error);
            msg.nak();
        }
        finally {
            this.isProcessing = false;
        }
    }
    async processEvent(event) {
        if (event.eventType.startsWith('contracts.')) {
            await this.processContractEvent(event);
        }
        else if (event.eventType.startsWith('production.')) {
            await this.processProductionEvent(event);
        }
        else if (event.eventType.startsWith('weighing.')) {
            await this.processWeighingEvent(event);
        }
        else if (event.eventType.startsWith('quality.')) {
            await this.processQualityEvent(event);
        }
        else if (event.eventType.startsWith('regulatory.')) {
            await this.processRegulatoryEvent(event);
        }
        else if (event.eventType.startsWith('finance.') || event.eventType.startsWith('sales.')) {
            await this.processFinanceEvent(event);
        }
        else {
            console.log(`Ignoring unknown event type: ${event.eventType}`);
        }
    }
    async processContractEvent(event) {
        const payload = event.payload;
        const contractData = {
            tenantId: event.tenantId,
            eventId: event.eventId,
            eventType: event.eventType,
            occurredAt: new Date(event.occurredAt),
            contractId: payload.contractId || payload.id,
            customerId: payload.customerId,
            supplierId: payload.supplierId,
            commodity: payload.commodity,
            quantity: payload.quantity,
            unit: payload.unit,
            price: payload.price,
            currency: payload.currency || 'EUR',
            status: payload.status,
            deliveryStart: payload.deliveryStart ? new Date(payload.deliveryStart) : null,
            deliveryEnd: payload.deliveryEnd ? new Date(payload.deliveryEnd) : null,
            contractType: payload.contractType || (payload.supplierId ? 'Purchase' : 'Sales'),
            hedgingRequired: payload.hedgingRequired || false,
            metadata: payload,
        };
        const existing = await this.db
            .select()
            .from(schema_1.factContracts)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.factContracts.tenantId, event.tenantId), (0, drizzle_orm_1.eq)(schema_1.factContracts.eventId, event.eventId)))
            .limit(1);
        if (existing.length === 0) {
            await this.db.insert(schema_1.factContracts).values(contractData);
        }
    }
    async processProductionEvent(event) {
        const payload = event.payload;
        const productionData = {
            tenantId: event.tenantId,
            eventId: event.eventId,
            eventType: event.eventType,
            occurredAt: new Date(event.occurredAt),
            batchId: payload.batchId || payload.id,
            contractId: payload.contractId,
            commodity: payload.commodity,
            quantity: payload.quantity,
            unit: payload.unit,
            qualityGrade: payload.qualityGrade,
            moisture: payload.moisture,
            protein: payload.protein,
            status: payload.status,
            siteId: payload.siteId,
            metadata: payload,
        };
        const existing = await this.db
            .select()
            .from(schema_1.factProduction)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.factProduction.tenantId, event.tenantId), (0, drizzle_orm_1.eq)(schema_1.factProduction.eventId, event.eventId)))
            .limit(1);
        if (existing.length === 0) {
            await this.db.insert(schema_1.factProduction).values(productionData);
        }
    }
    async processWeighingEvent(event) {
        const payload = event.payload;
        const weighingData = {
            tenantId: event.tenantId,
            eventId: event.eventId,
            eventType: event.eventType,
            occurredAt: new Date(event.occurredAt),
            ticketId: payload.ticketId || payload.id,
            contractId: payload.contractId,
            orderId: payload.orderId,
            customerId: payload.customerId,
            commodity: payload.commodity,
            grossWeight: payload.grossWeight,
            tareWeight: payload.tareWeight,
            netWeight: payload.netWeight,
            unit: payload.unit || 'kg',
            tolerancePercent: payload.tolerancePercent,
            isWithinTolerance: payload.isWithinTolerance,
            status: payload.status,
            siteId: payload.siteId,
            gateId: payload.gateId,
            licensePlate: payload.licensePlate,
            metadata: payload,
        };
        const existing = await this.db
            .select()
            .from(schema_1.factWeighing)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.factWeighing.tenantId, event.tenantId), (0, drizzle_orm_1.eq)(schema_1.factWeighing.eventId, event.eventId)))
            .limit(1);
        if (existing.length === 0) {
            await this.db.insert(schema_1.factWeighing).values(weighingData);
        }
    }
    async processQualityEvent(event) {
        const payload = event.payload;
        const qualityData = {
            tenantId: event.tenantId,
            eventId: event.eventId,
            eventType: event.eventType,
            occurredAt: new Date(event.occurredAt),
            sampleId: payload.sampleId || payload.id,
            batchId: payload.batchId,
            contractId: payload.contractId,
            commodity: payload.commodity,
            testType: payload.testType,
            testResult: payload.testResult,
            numericResult: payload.numericResult,
            unit: payload.unit,
            isPassed: payload.isPassed,
            testedBy: payload.testedBy,
            siteId: payload.siteId,
            metadata: payload,
        };
        const existing = await this.db
            .select()
            .from(schema_1.factQuality)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.factQuality.tenantId, event.tenantId), (0, drizzle_orm_1.eq)(schema_1.factQuality.eventId, event.eventId)))
            .limit(1);
        if (existing.length === 0) {
            await this.db.insert(schema_1.factQuality).values(qualityData);
        }
    }
    async processRegulatoryEvent(event) {
        const payload = event.payload;
        const regulatoryData = {
            tenantId: event.tenantId,
            eventId: event.eventId,
            eventType: event.eventType,
            occurredAt: new Date(event.occurredAt),
            batchId: payload.batchId,
            contractId: payload.contractId,
            commodity: payload.commodity,
            labelType: payload.labelType,
            isEligible: payload.isEligible,
            certificationNumber: payload.certificationNumber,
            expiryDate: payload.expiryDate ? new Date(payload.expiryDate) : null,
            issuedBy: payload.issuedBy,
            siteId: payload.siteId,
            metadata: payload,
        };
        const existing = await this.db
            .select()
            .from(schema_1.factRegulatory)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.factRegulatory.tenantId, event.tenantId), (0, drizzle_orm_1.eq)(schema_1.factRegulatory.eventId, event.eventId)))
            .limit(1);
        if (existing.length === 0) {
            await this.db.insert(schema_1.factRegulatory).values(regulatoryData);
        }
    }
    async processFinanceEvent(event) {
        const payload = event.payload;
        const financeData = {
            tenantId: event.tenantId,
            eventId: event.eventId,
            eventType: event.eventType,
            occurredAt: new Date(event.occurredAt),
            invoiceId: payload.invoiceId || payload.id,
            contractId: payload.contractId,
            customerId: payload.customerId,
            supplierId: payload.supplierId,
            commodity: payload.commodity,
            amount: payload.amount || payload.totalNet || payload.totalGross,
            currency: payload.currency || 'EUR',
            type: this.mapEventTypeToFinanceType(event.eventType),
            status: payload.status,
            dueDate: payload.dueDate ? new Date(payload.dueDate) : null,
            paidDate: payload.paidAt ? new Date(payload.paidAt) : null,
            metadata: payload,
        };
        const existing = await this.db
            .select()
            .from(schema_1.factFinance)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.factFinance.tenantId, event.tenantId), (0, drizzle_orm_1.eq)(schema_1.factFinance.eventId, event.eventId)))
            .limit(1);
        if (existing.length === 0) {
            await this.db.insert(schema_1.factFinance).values(financeData);
        }
    }
    mapEventTypeToFinanceType(eventType) {
        if (eventType.includes('invoice.issued'))
            return 'Revenue';
        if (eventType.includes('invoice.paid'))
            return 'Payment';
        if (eventType.includes('invoice.cancelled'))
            return 'Cancellation';
        if (eventType.includes('quote.accepted'))
            return 'Revenue';
        if (eventType.includes('order.confirmed'))
            return 'Revenue';
        return 'Other';
    }
    async disconnect() {
        if (this.subscription) {
            this.subscription.unsubscribe();
            this.subscription = null;
        }
        if (this.connection) {
            await this.connection.close();
            this.connection = null;
            this.isConnected = false;
        }
        await this.pool.end();
    }
    isHealthy() {
        return this.isConnected && !this.isProcessing;
    }
    getConnectionStatus() {
        if (!this.connection)
            return 'disconnected';
        return this.isConnected ? 'connected' : 'disconnected';
    }
}
exports.EventConsumer = EventConsumer;
function createEventConsumer(config) {
    return new EventConsumer(config);
}
let globalConsumer = null;
function getEventConsumer() {
    if (!globalConsumer) {
        const natsUrl = process.env.NATS_URL || 'nats://localhost:4222';
        const databaseUrl = process.env.DATABASE_URL || process.env.POSTGRES_URL || 'postgresql://localhost:5432/analytics';
        globalConsumer = createEventConsumer({
            natsUrl,
            databaseUrl,
        });
    }
    return globalConsumer;
}
//# sourceMappingURL=event-consumer.js.map