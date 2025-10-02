"use strict";
/**
 * VALEO NeuroERP 3.0 - Inventory Control Service
 *
 * Perpetual inventory management with lot/serial traceability
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
exports.InventoryControlService = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("../infrastructure/observability/metrics-service");
let InventoryControlService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var InventoryControlService = _classThis = class {
        constructor(eventBus) {
            this.eventBus = eventBus;
            this.metrics = new metrics_service_1.InventoryMetricsService();
        }
        /**
         * Get current inventory levels
         */
        async getInventoryLevels(sku, location) {
            const startTime = Date.now();
            try {
                // In real implementation, query database
                const records = await this.queryInventoryRecords(sku, location);
                this.metrics.recordDatabaseQueryDuration('inventory.levels', (Date.now() - startTime) / 1000, { sku: sku || '', location: location || '' });
                return records;
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory.query_failed', { error: 'query_error' });
                throw error;
            }
        }
        /**
         * Adjust inventory quantity
         */
        async adjustInventory(adjustment) {
            const startTime = Date.now();
            try {
                // Validate adjustment
                await this.validateInventoryAdjustment(adjustment);
                const fullAdjustment = {
                    ...adjustment,
                    adjustmentId: `adj_${Date.now()}`,
                    createdAt: new Date()
                };
                // Apply adjustment to inventory
                await this.applyInventoryAdjustment(fullAdjustment);
                // Publish event
                await this.publishInventoryAdjustedEvent(fullAdjustment);
                this.metrics.recordDatabaseQueryDuration('inventory.adjustment', (Date.now() - startTime) / 1000, { sku: adjustment.sku, reason: adjustment.reason });
                return fullAdjustment;
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory.adjustment_failed', { error: 'adjustment_error' });
                throw error;
            }
        }
        /**
         * Create inventory reservation
         */
        async createReservation(reservation) {
            const startTime = Date.now();
            try {
                // Check availability
                const available = await this.checkInventoryAvailability(reservation.sku, reservation.location, reservation.quantity, reservation.lot, reservation.serial);
                if (!available) {
                    throw new Error('Insufficient inventory for reservation');
                }
                const fullReservation = {
                    ...reservation,
                    reservationId: `res_${Date.now()}`,
                    createdAt: new Date(),
                    status: 'active'
                };
                // Create reservation
                await this.persistReservation(fullReservation);
                // Update allocated quantity
                await this.updateAllocatedQuantity(reservation.sku, reservation.location, reservation.lot, reservation.serial, reservation.quantity);
                // Publish event
                await this.publishReservationCreatedEvent(fullReservation);
                this.metrics.recordDatabaseQueryDuration('inventory.reservation', (Date.now() - startTime) / 1000, { sku: reservation.sku, location: reservation.location });
                return fullReservation;
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory.reservation_failed', { error: 'reservation_error' });
                throw error;
            }
        }
        /**
         * Release inventory reservation
         */
        async releaseReservation(reservationId, releasedQty) {
            const startTime = Date.now();
            try {
                const reservation = await this.getReservation(reservationId);
                if (!reservation) {
                    throw new Error(`Reservation ${reservationId} not found`);
                }
                const quantityToRelease = releasedQty || reservation.quantity;
                // Update reservation status
                if (quantityToRelease >= reservation.quantity) {
                    reservation.status = 'fulfilled';
                }
                // Release allocated quantity
                await this.updateAllocatedQuantity(reservation.sku, reservation.location, reservation.lot, reservation.serial, -quantityToRelease);
                // Persist changes
                await this.updateReservation(reservation);
                // Publish event
                await this.publishReservationReleasedEvent(reservation, quantityToRelease);
                this.metrics.recordDatabaseQueryDuration('inventory.release', (Date.now() - startTime) / 1000, { sku: reservation.sku, location: reservation.location });
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory.release_failed', { error: 'release_error' });
                throw error;
            }
        }
        /**
         * Get lot traceability information
         */
        async getLotTraceability(lotCode) {
            const startTime = Date.now();
            try {
                const traceability = await this.buildLotTraceability(lotCode);
                this.metrics.recordDatabaseQueryDuration('inventory.lot_traceability', (Date.now() - startTime) / 1000, { lotCode });
                return traceability;
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory.traceability_failed', { error: 'traceability_error' });
                throw error;
            }
        }
        /**
         * Get serial number traceability
         */
        async getSerialTraceability(serialNumber) {
            const startTime = Date.now();
            try {
                const traceability = await this.buildSerialTraceability(serialNumber);
                this.metrics.recordDatabaseQueryDuration('inventory.serial_traceability', (Date.now() - startTime) / 1000, { serialNumber });
                return traceability;
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory.traceability_failed', { error: 'traceability_error' });
                throw error;
            }
        }
        /**
         * Process inventory movement (transfer between locations)
         */
        async processInventoryMovement(sku, fromLocation, toLocation, quantity, lot, serial, reason = 'transfer') {
            const startTime = Date.now();
            try {
                // Validate movement
                await this.validateInventoryMovement(sku, fromLocation, toLocation, quantity, lot, serial);
                // Create adjustment for source location (negative)
                await this.adjustInventory({
                    sku,
                    location: fromLocation,
                    lot,
                    serial,
                    adjustmentQty: -quantity,
                    reason: reason,
                    approvedBy: 'system',
                    notes: `Transfer to ${toLocation}`
                });
                // Create adjustment for destination location (positive)
                await this.adjustInventory({
                    sku,
                    location: toLocation,
                    lot,
                    serial,
                    adjustmentQty: quantity,
                    reason: reason,
                    approvedBy: 'system',
                    notes: `Transfer from ${fromLocation}`
                });
                this.metrics.recordDatabaseQueryDuration('inventory.movement', (Date.now() - startTime) / 1000, { sku, fromLocation, toLocation });
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory.movement_failed', { error: 'movement_error' });
                throw error;
            }
        }
        /**
         * Get inventory valuation
         */
        async getInventoryValuation(sku, location) {
            const startTime = Date.now();
            try {
                const records = await this.getInventoryLevels(sku, location);
                const valuation = {
                    totalValue: 0,
                    totalQuantity: 0,
                    averageCost: 0,
                    byLocation: new Map(),
                    bySku: new Map()
                };
                for (const record of records) {
                    const value = (record.unitCost || 0) * record.quantity;
                    valuation.totalValue += value;
                    valuation.totalQuantity += record.quantity;
                    // By location
                    const locStats = valuation.byLocation.get(record.location) || { value: 0, quantity: 0 };
                    locStats.value += value;
                    locStats.quantity += record.quantity;
                    valuation.byLocation.set(record.location, locStats);
                    // By SKU
                    const skuStats = valuation.bySku.get(record.sku) || { value: 0, quantity: 0 };
                    skuStats.value += value;
                    skuStats.quantity += record.quantity;
                    valuation.bySku.set(record.sku, skuStats);
                }
                valuation.averageCost = valuation.totalQuantity > 0 ? valuation.totalValue / valuation.totalQuantity : 0;
                this.metrics.recordDatabaseQueryDuration('inventory.valuation', (Date.now() - startTime) / 1000, { sku: sku || 'all', location: location || 'all' });
                return {
                    ...valuation,
                    byLocation: Array.from(valuation.byLocation.entries()).map(([location, stats]) => ({ location, ...stats })),
                    bySku: Array.from(valuation.bySku.entries()).map(([sku, stats]) => ({ sku, ...stats }))
                };
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory.valuation_failed', { error: 'valuation_error' });
                throw error;
            }
        }
        /**
         * Get inventory aging report
         */
        async getInventoryAging(days = 90) {
            const startTime = Date.now();
            try {
                const records = await this.getInventoryLevels();
                const aging = [];
                for (const record of records) {
                    const ageInDays = Math.floor((Date.now() - record.lastMovement.getTime()) / (1000 * 60 * 60 * 24));
                    if (ageInDays >= days) {
                        aging.push({
                            sku: record.sku,
                            location: record.location,
                            lot: record.lot,
                            quantity: record.quantity,
                            ageInDays,
                            value: (record.unitCost || 0) * record.quantity
                        });
                    }
                }
                // Sort by age (oldest first)
                aging.sort((a, b) => b.ageInDays - a.ageInDays);
                this.metrics.recordDatabaseQueryDuration('inventory.aging', (Date.now() - startTime) / 1000, {});
                return aging;
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory.aging_failed', { error: 'aging_error' });
                throw error;
            }
        }
        // Private helper methods
        async queryInventoryRecords(sku, location) {
            // Mock implementation - would query database
            return [
                {
                    sku: sku || 'WIDGET-001',
                    location: location || 'A-01-01-01',
                    lot: 'LOT-001',
                    quantity: 100,
                    allocatedQty: 10,
                    availableQty: 90,
                    unitCost: 10.50,
                    totalValue: 1050.00,
                    lastMovement: new Date()
                }
            ];
        }
        async validateInventoryAdjustment(adjustment) {
            // Validate SKU exists
            const skuExists = await this.skuExists(adjustment.sku);
            if (!skuExists) {
                throw new Error(`SKU ${adjustment.sku} does not exist`);
            }
            // Validate location exists
            const locationExists = await this.locationExists(adjustment.location);
            if (!locationExists) {
                throw new Error(`Location ${adjustment.location} does not exist`);
            }
            // Validate lot/serial if provided
            if (adjustment.lot) {
                const lotExists = await this.lotExists(adjustment.lot, adjustment.sku);
                if (!lotExists) {
                    throw new Error(`Lot ${adjustment.lot} does not exist for SKU ${adjustment.sku}`);
                }
            }
            if (adjustment.serial) {
                const serialExists = await this.serialExists(adjustment.serial, adjustment.sku);
                if (!serialExists) {
                    throw new Error(`Serial ${adjustment.serial} does not exist for SKU ${adjustment.sku}`);
                }
            }
        }
        async applyInventoryAdjustment(adjustment) {
            // Mock implementation - would update database
            console.log('Applying inventory adjustment:', adjustment.adjustmentId);
        }
        async checkInventoryAvailability(sku, location, quantity, lot, serial) {
            const records = await this.getInventoryLevels(sku, location);
            const relevantRecords = records.filter(record => {
                if (lot && record.lot !== lot)
                    return false;
                if (serial && record.serial !== serial)
                    return false;
                return true;
            });
            const totalAvailable = relevantRecords.reduce((sum, record) => sum + record.availableQty, 0);
            return totalAvailable >= quantity;
        }
        async persistReservation(reservation) {
            // Mock implementation
            console.log('Persisting reservation:', reservation.reservationId);
        }
        async updateAllocatedQuantity(sku, location, lot, serial, quantity) {
            // Mock implementation
            console.log('Updating allocated quantity for', sku, location, quantity);
        }
        async getReservation(reservationId) {
            // Mock implementation
            return {
                reservationId,
                sku: 'WIDGET-001',
                location: 'A-01-01-01',
                quantity: 10,
                reservedFor: 'ORDER-123',
                reservationType: 'sales_order',
                priority: 1,
                createdAt: new Date(),
                status: 'active'
            };
        }
        async updateReservation(reservation) {
            // Mock implementation
            console.log('Updating reservation:', reservation.reservationId);
        }
        async buildLotTraceability(lotCode) {
            // Mock implementation
            return {
                lotCode,
                sku: 'WIDGET-001',
                supplier: 'SUPPLIER-001',
                supplierLot: 'SUP-LOT-001',
                mfgDate: new Date('2024-01-01'),
                expDate: new Date('2025-01-01'),
                receivedDate: new Date('2024-01-15'),
                currentQty: 85,
                totalReceived: 100,
                totalConsumed: 15,
                locations: [
                    { location: 'A-01-01-01', quantity: 85, lastMovement: new Date() }
                ],
                transactions: [
                    {
                        transactionId: 'txn_001',
                        type: 'receipt',
                        quantity: 100,
                        location: 'RECEIVING',
                        reference: 'ASN-001',
                        timestamp: new Date('2024-01-15')
                    }
                ]
            };
        }
        async buildSerialTraceability(serialNumber) {
            // Mock implementation
            return {
                serialNumber,
                sku: 'WIDGET-001',
                lot: 'LOT-001',
                currentLocation: 'A-01-01-01',
                status: 'available',
                transactions: [
                    {
                        transactionId: 'txn_001',
                        type: 'receipt',
                        reference: 'ASN-001',
                        timestamp: new Date('2024-01-15')
                    }
                ]
            };
        }
        async validateInventoryMovement(sku, fromLocation, toLocation, quantity, lot, serial) {
            // Check source availability
            const available = await this.checkInventoryAvailability(sku, fromLocation, quantity, lot, serial);
            if (!available) {
                throw new Error('Insufficient inventory in source location');
            }
            // Check destination exists
            const destExists = await this.locationExists(toLocation);
            if (!destExists) {
                throw new Error(`Destination location ${toLocation} does not exist`);
            }
        }
        // Mock validation methods
        async skuExists(sku) {
            return true; // Mock
        }
        async locationExists(location) {
            return true; // Mock
        }
        async lotExists(lot, sku) {
            return true; // Mock
        }
        async serialExists(serial, sku) {
            return true; // Mock
        }
        // Event publishing methods
        async publishInventoryAdjustedEvent(adjustment) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.adjusted',
                type: 'inventory.adjusted',
                occurredAt: new Date(),
                aggregateVersion: 1,
                aggregateId: adjustment.adjustmentId,
                aggregateType: 'InventoryAdjustment',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                sku: adjustment.sku,
                location: adjustment.location,
                lot: adjustment.lot,
                serial: adjustment.serial,
                adjustmentQty: adjustment.adjustmentQty,
                reason: adjustment.reason,
                approvedBy: adjustment.approvedBy
            };
            await this.eventBus.publish(event);
        }
        async publishReservationCreatedEvent(reservation) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.reservation.created',
                type: 'inventory.reservation.created',
                occurredAt: new Date(),
                aggregateVersion: 1,
                aggregateId: reservation.reservationId,
                aggregateType: 'InventoryReservation',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                sku: reservation.sku,
                location: reservation.location,
                lot: reservation.lot,
                serial: reservation.serial,
                quantity: reservation.quantity,
                reservedFor: reservation.reservedFor,
                reservationType: reservation.reservationType
            };
            await this.eventBus.publish(event);
        }
        async publishReservationReleasedEvent(reservation, releasedQty) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.reservation.released',
                type: 'inventory.reservation.released',
                occurredAt: new Date(),
                aggregateVersion: 1,
                aggregateId: reservation.reservationId,
                aggregateType: 'InventoryReservation',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                reservationId: reservation.reservationId,
                releasedQty,
                reason: 'fulfilled'
            };
            await this.eventBus.publish(event);
        }
    };
    __setFunctionName(_classThis, "InventoryControlService");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        InventoryControlService = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return InventoryControlService = _classThis;
})();
exports.InventoryControlService = InventoryControlService;
//# sourceMappingURL=inventory-control-service.js.map