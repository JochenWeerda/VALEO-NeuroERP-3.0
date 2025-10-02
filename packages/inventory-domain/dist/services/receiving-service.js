"use strict";
/**
 * VALEO NeuroERP 3.0 - Receiving Service
 *
 * Handles inbound operations: ASN processing, dock management, quality control
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
exports.ReceivingService = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("../infrastructure/observability/metrics-service");
let ReceivingService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var ReceivingService = _classThis = class {
        constructor(eventBus) {
            this.eventBus = eventBus;
            this.metrics = new metrics_service_1.InventoryMetricsService();
        }
        /**
         * Process ASN (Advance Shipping Notice)
         */
        async processASN(asn) {
            const startTime = Date.now();
            try {
                // Validate ASN
                this.validateASN(asn);
                // Update ASN status
                asn.status = 'scheduled';
                // Schedule dock appointment if not provided
                if (!asn.dock) {
                    asn.dock = await this.scheduleDockAppointment(asn);
                }
                this.metrics.recordApiResponseTime('receiving.validate_asn', (Date.now() - startTime) / 1000, { asnId: asn.asnId });
                return asn;
            }
            catch (error) {
                this.metrics.incrementErrorCount('receiving.asn_processing', { error: 'validation_failed' });
                throw error;
            }
        }
        /**
         * Start receiving process when truck arrives
         */
        async startReceiving(asnId, dock, carrierInfo) {
            const startTime = Date.now();
            try {
                // Find ASN
                const asn = await this.getASN(asnId);
                if (!asn) {
                    throw new Error(`ASN ${asnId} not found`);
                }
                // Create dock appointment
                const appointment = {
                    appointmentId: `appt_${Date.now()}`,
                    asnId,
                    dock,
                    scheduledTime: asn.expectedArrival,
                    actualArrival: new Date(),
                    status: 'receiving',
                    carrier: asn.carrier,
                    ...carrierInfo
                };
                // Update ASN status
                asn.status = 'receiving';
                asn.dock = dock;
                this.metrics.recordApiResponseTime('POST', '/receiving/start', 200);
                return appointment;
            }
            catch (error) {
                this.metrics.incrementErrorCount('receiving.start_receiving', { error: 'start_receiving_error' });
                throw error;
            }
        }
        /**
         * Receive goods and perform quality inspection
         */
        async receiveGoods(asnId, receivedLines) {
            const startTime = Date.now();
            try {
                const asn = await this.getASN(asnId);
                if (!asn) {
                    throw new Error(`ASN ${asnId} not found`);
                }
                const received = [];
                const mismatches = [];
                for (const receivedLine of receivedLines) {
                    const asnLine = asn.lines.find(line => line.lineId === receivedLine.lineId);
                    if (!asnLine) {
                        throw new Error(`ASN line ${receivedLine.lineId} not found`);
                    }
                    // Update received quantity
                    asnLine.receivedQty = receivedLine.receivedQty;
                    asnLine.lot = receivedLine.lot || asnLine.lot;
                    asnLine.serial = receivedLine.serial || asnLine.serial;
                    // Check for quantity mismatch
                    if (Math.abs((asnLine.receivedQty || 0) - asnLine.expectedQty) > asnLine.expectedQty * 0.05) { // 5% tolerance
                        mismatches.push({
                            lineId: receivedLine.lineId,
                            sku: asnLine.sku,
                            expected: asnLine.expectedQty,
                            received: asnLine.receivedQty,
                            variance: ((asnLine.receivedQty || 0) - asnLine.expectedQty) / asnLine.expectedQty * 100
                        });
                    }
                    // Perform quality inspection if required
                    if (receivedLine.qaRequired) {
                        const qaResult = await this.performQualityInspection(asnId, asnLine);
                        asnLine.qaStatus = qaResult.result;
                        asnLine.qaNotes = qaResult.notes;
                    }
                    else {
                        asnLine.qaStatus = 'passed'; // Auto-pass if no QA required
                    }
                    received.push(asnLine);
                }
                // Publish events
                await this.publishGoodsReceivedEvent(asn, received);
                if (mismatches.length > 0) {
                    await this.publishReceivingMismatchEvent(asn, mismatches);
                }
                // Update ASN status
                asn.status = 'completed';
                this.metrics.recordApiResponseTime('receiving.process_goods', (Date.now() - startTime) / 1000, { asnId: asnId });
                return { received, mismatches };
            }
            catch (error) {
                this.metrics.incrementErrorCount('receiving.goods_receipt', { error: 'processing_failed' });
                throw error;
            }
        }
        /**
         * Perform quality inspection
         */
        async performQualityInspection(asnId, asnLine) {
            // In a real implementation, this would involve:
            // - Visual inspection criteria
            // - Measurement checks
            // - Documentation verification
            // - Sampling for lab testing
            const inspection = {
                inspectionId: `qa_${Date.now()}`,
                asnId,
                lineId: asnLine.lineId,
                sku: asnLine.sku,
                lot: asnLine.lot,
                serial: asnLine.serial,
                quantity: asnLine.receivedQty || 0,
                inspectionType: 'visual',
                criteria: [
                    {
                        criterion: 'Packaging integrity',
                        expected: 'Intact',
                        actual: 'Intact',
                        pass: true
                    },
                    {
                        criterion: 'Product condition',
                        expected: 'No damage',
                        actual: 'No visible damage',
                        pass: true
                    }
                ],
                result: 'pass',
                inspectedBy: 'system', // In real implementation, get from auth context
                inspectedAt: new Date()
            };
            // Store inspection results (would be in database)
            this.storeQualityInspection(inspection);
            return {
                result: inspection.result,
                notes: inspection.notes
            };
        }
        /**
         * Schedule dock appointment
         */
        async scheduleDockAppointment(asn) {
            // Simple dock scheduling logic
            // In production, this would consider:
            // - Dock availability
            // - ASN priority
            // - Carrier preferences
            // - Time slot optimization
            const availableDocks = ['DOCK-01', 'DOCK-02', 'DOCK-03', 'DOCK-04'];
            return availableDocks[Math.floor(Math.random() * availableDocks.length)];
        }
        /**
         * Get ASN by ID (mock implementation)
         */
        async getASN(asnId) {
            // In real implementation, fetch from database
            // This is a mock for demonstration
            return {
                asnId,
                poId: 'PO-12345',
                supplierId: 'SUP-001',
                carrier: 'DHL',
                expectedArrival: new Date(),
                status: 'arrived',
                lines: [
                    {
                        lineId: 'line_1',
                        sku: 'WIDGET-001',
                        expectedQty: 100,
                        uom: 'EA'
                    }
                ]
            };
        }
        /**
         * Store quality inspection (mock implementation)
         */
        storeQualityInspection(inspection) {
            // In real implementation, persist to database
            console.log('Storing quality inspection:', inspection.inspectionId);
        }
        /**
         * Publish goods received event
         */
        async publishGoodsReceivedEvent(asn, receivedLines) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.goods.received',
                type: 'inventory.goods.received',
                aggregateId: asn.asnId,
                aggregateType: 'ASN',
                eventVersion: 1,
                occurredOn: new Date(),
                occurredAt: new Date(),
                aggregateVersion: 1,
                tenantId: 'default', // In real implementation, get from context
                asnId: asn.asnId,
                poId: asn.poId,
                dock: asn.dock || 'UNKNOWN',
                lines: receivedLines.map(line => ({
                    sku: line.sku,
                    gtin: line.gtin,
                    qty: line.receivedQty || 0,
                    uom: line.uom,
                    lot: line.lot,
                    expDate: line.expDate,
                    qualityStatus: (line.qaStatus || 'pending')
                }))
            };
            await this.eventBus.publish(event);
        }
        /**
         * Publish receiving mismatch event
         */
        async publishReceivingMismatchEvent(asn, mismatches) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.receiving.mismatch',
                type: 'inventory.receiving.mismatch',
                occurredAt: new Date(),
                aggregateVersion: 1,
                aggregateId: asn.asnId,
                aggregateType: 'ASN',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                asnId: asn.asnId,
                poId: asn.poId,
                discrepancies: mismatches.map(mismatch => ({
                    sku: mismatch.sku,
                    expectedQty: mismatch.expected,
                    receivedQty: mismatch.received,
                    reason: `Quantity variance: ${mismatch.variance.toFixed(2)}%`
                }))
            };
            await this.eventBus.publish(event);
        }
        /**
         * Validate ASN structure
         */
        validateASN(asn) {
            if (!asn.asnId || !asn.poId || !asn.supplierId) {
                throw new Error('ASN must have asnId, poId, and supplierId');
            }
            if (!asn.lines || asn.lines.length === 0) {
                throw new Error('ASN must have at least one line');
            }
            for (const line of asn.lines) {
                if (!line.sku || line.expectedQty <= 0) {
                    throw new Error(`Invalid ASN line: ${line.lineId}`);
                }
            }
        }
        /**
         * Get receiving metrics
         */
        getMetrics() {
            // In real implementation, calculate from actual data
            return {
                dockUtilization: 0.85,
                averageReceivingTime: 45, // minutes
                qaPassRate: 0.96,
                mismatchRate: 0.03
            };
        }
    };
    __setFunctionName(_classThis, "ReceivingService");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        ReceivingService = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return ReceivingService = _classThis;
})();
exports.ReceivingService = ReceivingService;
//# sourceMappingURL=receiving-service.js.map