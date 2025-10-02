"use strict";
/**
 * VALEO NeuroERP 3.0 - EDI Service
 *
 * ANSI X12 EDI transactions for warehouse management integration
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.EDIService = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("../infrastructure/observability/metrics-service");
let EDIService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var EDIService = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            EDIService = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        eventBus;
        metrics = new metrics_service_1.InventoryMetricsService();
        transactions = new Map();
        segmentSeparator = '~';
        elementSeparator = '*';
        subelementSeparator = '>';
        constructor(eventBus) {
            this.eventBus = eventBus;
        }
        /**
         * Process inbound EDI 940 (Warehouse Shipping Order)
         */
        async processEDI940(rawMessage) {
            const startTime = Date.now();
            try {
                const transaction = await this.parseEDITransaction(rawMessage, '940', 'inbound');
                const order = this.parseEDI940Data(transaction.transactionData);
                // Process the shipping order
                await this.processWarehouseShippingOrder(order);
                transaction.status = 'processed';
                transaction.processedAt = new Date();
                // Publish event
                await this.publishEDI940ReceivedEvent(order);
                this.metrics.recordDatabaseQueryDuration('edi', '940_processing', (Date.now() - startTime) / 1000);
                this.metrics.incrementEDITransactions('940', 'processed');
                return order;
            }
            catch (error) {
                this.metrics.incrementErrorCount('edi', '940_processing_failed');
                throw error;
            }
        }
        /**
         * Generate outbound EDI 943 (Warehouse Stock Transfer Shipment Advice)
         */
        async generateEDI943(transferData) {
            const startTime = Date.now();
            try {
                const edi943 = {
                    warehouseCode: transferData.warehouseCode,
                    transferId: transferData.transferId,
                    shipmentDate: transferData.shipmentDate,
                    carrier: transferData.carrier,
                    shipFrom: transferData.shipFrom,
                    shipTo: transferData.shipTo,
                    items: transferData.items
                };
                const rawMessage = this.generateEDI943Message(edi943);
                const transaction = await this.createEDITransaction(rawMessage, '943', 'outbound');
                // Publish event
                await this.publishEDI943GeneratedEvent(edi943);
                this.metrics.recordDatabaseQueryDuration('edi', '943_generation', (Date.now() - startTime) / 1000);
                return rawMessage;
            }
            catch (error) {
                this.metrics.incrementErrorCount('edi', '943_generation_failed');
                throw error;
            }
        }
        /**
         * Process inbound EDI 944 (Warehouse Stock Transfer Receipt Advice)
         */
        async processEDI944(rawMessage) {
            const startTime = Date.now();
            try {
                const transaction = await this.parseEDITransaction(rawMessage, '944', 'inbound');
                const receipt = this.parseEDI944Data(transaction.transactionData);
                // Process the receipt advice
                await this.processTransferReceiptAdvice(receipt);
                transaction.status = 'processed';
                transaction.processedAt = new Date();
                // Publish event
                await this.publishEDI944ReceivedEvent(receipt);
                this.metrics.recordDatabaseQueryDuration('edi', '944_processing', (Date.now() - startTime) / 1000);
                this.metrics.incrementEDITransactions('944', 'processed');
                return receipt;
            }
            catch (error) {
                this.metrics.incrementErrorCount('edi', '944_processing_failed');
                throw error;
            }
        }
        /**
         * Generate outbound EDI 945 (Warehouse Shipping Advice)
         */
        async generateEDI945(shippingData) {
            const startTime = Date.now();
            try {
                const edi945 = {
                    warehouseCode: shippingData.warehouseCode,
                    shipmentId: shippingData.shipmentId,
                    shipmentDate: shippingData.shipmentDate,
                    carrier: shippingData.carrier,
                    shipFrom: shippingData.shipFrom,
                    shipTo: shippingData.shipTo,
                    items: shippingData.items,
                    packaging: shippingData.packaging,
                    totalWeight: shippingData.totalWeight,
                    totalVolume: shippingData.totalVolume
                };
                const rawMessage = this.generateEDI945Message(edi945);
                const transaction = await this.createEDITransaction(rawMessage, '945', 'outbound');
                // Publish event
                await this.publishEDI945GeneratedEvent(edi945);
                this.metrics.recordDatabaseQueryDuration('edi', '945_generation', (Date.now() - startTime) / 1000);
                return rawMessage;
            }
            catch (error) {
                this.metrics.incrementErrorCount('edi', '945_generation_failed');
                throw error;
            }
        }
        /**
         * Generate outbound EDI 947 (Warehouse Inventory Adjustment Advice)
         */
        async generateEDI947(adjustmentData) {
            const startTime = Date.now();
            try {
                const edi947 = {
                    warehouseCode: adjustmentData.warehouseCode,
                    adjustmentId: adjustmentData.adjustmentId,
                    adjustmentDate: adjustmentData.adjustmentDate,
                    adjustmentType: adjustmentData.adjustmentType,
                    reason: adjustmentData.reason,
                    items: adjustmentData.items,
                    totals: adjustmentData.totals
                };
                const rawMessage = this.generateEDI947Message(edi947);
                const transaction = await this.createEDITransaction(rawMessage, '947', 'outbound');
                // Publish event
                await this.publishEDI947GeneratedEvent(edi947);
                this.metrics.recordDatabaseQueryDuration('edi', '947_generation', (Date.now() - startTime) / 1000);
                return rawMessage;
            }
            catch (error) {
                this.metrics.incrementErrorCount('edi', '947_generation_failed');
                throw error;
            }
        }
        /**
         * Parse EDI transaction envelope
         */
        async parseEDITransaction(rawMessage, expectedType, direction) {
            // Parse ISA segment
            const isaMatch = rawMessage.match(/ISA\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)~/);
            if (!isaMatch) {
                throw new Error('Invalid EDI message: Missing or malformed ISA segment');
            }
            const isa = {
                authorizationQualifier: isaMatch[1],
                authorizationInfo: isaMatch[2],
                securityQualifier: isaMatch[3],
                securityInfo: isaMatch[4],
                senderId: isaMatch[5],
                senderQualifier: isaMatch[6],
                receiverId: isaMatch[7],
                receiverQualifier: isaMatch[8],
                date: isaMatch[9],
                time: isaMatch[10],
                controlNumber: isaMatch[13],
                version: isaMatch[15]
            };
            // Parse GS segment
            const gsMatch = rawMessage.match(/GS\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)\*([^*]+)~/);
            if (!gsMatch) {
                throw new Error('Invalid EDI message: Missing or malformed GS segment');
            }
            const gs = {
                functionalId: gsMatch[1],
                applicationSender: gsMatch[2],
                applicationReceiver: gsMatch[3],
                date: gsMatch[4],
                time: gsMatch[5],
                groupControlNumber: gsMatch[6],
                responsibleAgency: gsMatch[7],
                version: gsMatch[8]
            };
            // Validate transaction type
            if (gs.functionalId !== expectedType) {
                throw new Error(`Invalid transaction type: Expected ${expectedType}, got ${gs.functionalId}`);
            }
            const transaction = {
                transactionId: `edi_${expectedType}_${Date.now()}`,
                transactionType: expectedType,
                direction,
                status: 'received',
                isa,
                gs,
                transactionData: this.parseTransactionData(rawMessage),
                rawMessage,
                createdAt: new Date(),
                updatedAt: new Date()
            };
            this.transactions.set(transaction.transactionId, transaction);
            return transaction;
        }
        /**
         * Create EDI transaction record
         */
        async createEDITransaction(rawMessage, type, direction) {
            const transaction = {
                transactionId: `edi_${type}_${Date.now()}`,
                transactionType: type,
                direction,
                status: 'processing',
                isa: {}, // Would be populated from configuration
                gs: {},
                transactionData: {},
                rawMessage,
                createdAt: new Date(),
                updatedAt: new Date()
            };
            this.transactions.set(transaction.transactionId, transaction);
            return transaction;
        }
        /**
         * Parse transaction-specific data
         */
        parseTransactionData(rawMessage) {
            // Parse ST, BEG, N1, PO1, etc. segments based on transaction type
            const data = {};
            // Extract ST segment (Transaction Set Header)
            const stMatch = rawMessage.match(/ST\*([^*]+)\*([^*]+)~/);
            if (stMatch) {
                data.transactionSet = {
                    id: stMatch[1],
                    controlNumber: stMatch[2]
                };
            }
            return data;
        }
        /**
         * Parse EDI 940 data
         */
        parseEDI940Data(data) {
            // Parse W05 (Warehouse Order Header), N1 (Name), G62 (Date/Time), etc.
            return {
                warehouseCode: 'WH001',
                depotCode: 'DEP001',
                shipmentId: 'SHIP001',
                purposeCode: '00',
                shipTo: {
                    name: 'Customer Name',
                    address: ['Address Line 1', 'Address Line 2'],
                    city: 'City',
                    state: 'State',
                    zipCode: '12345',
                    country: 'US'
                },
                carrier: {
                    scac: 'SCAC',
                    name: 'Carrier Name',
                    serviceLevel: 'GND'
                },
                items: [
                    {
                        lineNumber: '1',
                        sku: 'SKU001',
                        quantity: 100,
                        uom: 'EA',
                        description: 'Item Description'
                    }
                ],
                routing: 'ROUTING'
            };
        }
        /**
         * Parse EDI 944 data
         */
        parseEDI944Data(data) {
            return {
                warehouseCode: 'WH001',
                transferId: 'TRANS001',
                receiptDate: new Date().toISOString().split('T')[0],
                carrier: {
                    scac: 'SCAC',
                    name: 'Carrier Name',
                    proNumber: 'PRO001'
                },
                shipFrom: {
                    name: 'Ship From Name',
                    address: ['Address Line 1'],
                    city: 'City',
                    state: 'State',
                    zipCode: '12345'
                },
                items: [
                    {
                        sku: 'SKU001',
                        quantityOrdered: 100,
                        quantityReceived: 95,
                        uom: 'EA',
                        condition: 'good'
                    }
                ],
                discrepancies: [
                    {
                        sku: 'SKU001',
                        expectedQuantity: 100,
                        receivedQuantity: 95,
                        reason: 'Shortage'
                    }
                ]
            };
        }
        /**
         * Generate EDI 943 message
         */
        generateEDI943Message(data) {
            const segments = [];
            // ISA/GS headers would be added here
            segments.push(`ST*943*0001${this.segmentSeparator}`);
            segments.push(`W19*${data.warehouseCode}*${data.transferId}*${data.shipmentDate}${this.segmentSeparator}`);
            // Add N1, G62, TD3, etc. segments
            segments.push(`SE*3*0001${this.segmentSeparator}`);
            // GE/IEA trailers would be added here
            return segments.join('');
        }
        /**
         * Generate EDI 945 message
         */
        generateEDI945Message(data) {
            const segments = [];
            segments.push(`ST*945*0001${this.segmentSeparator}`);
            segments.push(`W06*${data.warehouseCode}*${data.shipmentId}*${data.shipmentDate}${this.segmentSeparator}`);
            // Add N1, G62, TD3, etc. segments
            segments.push(`SE*5*0001${this.segmentSeparator}`);
            return segments.join('');
        }
        /**
         * Generate EDI 947 message
         */
        generateEDI947Message(data) {
            const segments = [];
            segments.push(`ST*947*0001${this.segmentSeparator}`);
            segments.push(`W20*${data.warehouseCode}*${data.adjustmentId}*${data.adjustmentDate}${this.segmentSeparator}`);
            // Add N1, G62, LX, W21, etc. segments
            segments.push(`SE*4*0001${this.segmentSeparator}`);
            return segments.join('');
        }
        // Business logic methods
        async processWarehouseShippingOrder(order) {
            // Create picking tasks, allocate inventory, etc.
            console.log(`Processing warehouse shipping order: ${order.shipmentId}`);
        }
        async processTransferReceiptAdvice(receipt) {
            // Update inventory, handle discrepancies, etc.
            console.log(`Processing transfer receipt advice: ${receipt.transferId}`);
        }
        // Event publishing methods
        async publishEDI940ReceivedEvent(order) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.edi.940.received',
                aggregateId: order.shipmentId,
                aggregateType: 'EDI940WarehouseShippingOrder',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                shipmentId: order.shipmentId,
                warehouseCode: order.warehouseCode,
                itemCount: order.items.length,
                totalQuantity: order.items.reduce((sum, item) => sum + item.quantity, 0)
            };
            await this.eventBus.publish(event);
        }
        async publishEDI943GeneratedEvent(advice) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.edi.943.generated',
                aggregateId: advice.transferId,
                aggregateType: 'EDI943WarehouseStockTransferShipmentAdvice',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                transferId: advice.transferId,
                warehouseCode: advice.warehouseCode,
                itemCount: advice.items.length,
                totalQuantity: advice.items.reduce((sum, item) => sum + item.quantity, 0)
            };
            await this.eventBus.publish(event);
        }
        async publishEDI944ReceivedEvent(receipt) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.edi.944.received',
                aggregateId: receipt.transferId,
                aggregateType: 'EDI944WarehouseStockTransferReceiptAdvice',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                transferId: receipt.transferId,
                warehouseCode: receipt.warehouseCode,
                itemCount: receipt.items.length,
                totalReceived: receipt.items.reduce((sum, item) => sum + item.quantityReceived, 0),
                discrepancies: receipt.discrepancies.length
            };
            await this.eventBus.publish(event);
        }
        async publishEDI945GeneratedEvent(advice) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.edi.945.generated',
                aggregateId: advice.shipmentId,
                aggregateType: 'EDI945WarehouseShippingAdvice',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                shipmentId: advice.shipmentId,
                warehouseCode: advice.warehouseCode,
                itemCount: advice.items.length,
                totalWeight: advice.totalWeight,
                totalVolume: advice.totalVolume
            };
            await this.eventBus.publish(event);
        }
        async publishEDI947GeneratedEvent(advice) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.edi.947.generated',
                aggregateId: advice.adjustmentId,
                aggregateType: 'EDI947WarehouseInventoryAdjustmentAdvice',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                adjustmentId: advice.adjustmentId,
                warehouseCode: advice.warehouseCode,
                itemCount: advice.items.length,
                netAdjustment: advice.totals.netAdjustment,
                adjustmentType: advice.adjustmentType
            };
            await this.eventBus.publish(event);
        }
    };
    return EDIService = _classThis;
})();
exports.EDIService = EDIService;
