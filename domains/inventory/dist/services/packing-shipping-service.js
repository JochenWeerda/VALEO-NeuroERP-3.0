"use strict";
/**
 * VALEO NeuroERP 3.0 - Packing & Shipping Service
 *
 * GS1 compliant labeling, carrier integration, and shipping management
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
exports.PackingShippingService = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("../infrastructure/observability/metrics-service");
let PackingShippingService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var PackingShippingService = _classThis = class {
        constructor(eventBus) {
            this.eventBus = eventBus;
            this.metrics = new metrics_service_1.InventoryMetricsService();
            this.carriers = new Map();
            this.initializeDefaultCarriers();
        }
        /**
         * Create packing task from order
         */
        async createPackingTask(orderId, packingStation) {
            const startTime = Date.now();
            try {
                const orderDetails = await this.getOrderDetails(orderId);
                if (!orderDetails) {
                    throw new Error(`Order ${orderId} not found`);
                }
                const task = {
                    taskId: `pack_${Date.now()}`,
                    orderId,
                    items: orderDetails.lines.map((line) => ({
                        sku: line.sku,
                        quantity: line.quantity,
                        lot: line.lot,
                        serial: line.serial,
                        packedQuantity: 0
                    })),
                    status: 'pending',
                    packingStation: packingStation || '',
                    priority: orderDetails.priority || 5,
                    estimatedTime: this.estimatePackingTime(orderDetails.lines),
                    createdAt: new Date()
                };
                // Publish event
                await this.publishPackTaskCreatedEvent(task);
                this.metrics.recordDatabaseQueryDuration('packing.task_creation', (Date.now() - startTime) / 1000, { orderId });
                this.metrics.incrementPackTasks('packing.created', { orderId });
                return task;
            }
            catch (error) {
                this.metrics.incrementErrorCount('packing.task_creation_failed', { error: 'task_creation_error' });
                throw error;
            }
        }
        /**
         * Start packing task
         */
        async startPackingTask(taskId, packerId) {
            const task = await this.findPackingTask(taskId);
            if (!task) {
                throw new Error(`Packing task ${taskId} not found`);
            }
            if (task.status !== 'pending') {
                throw new Error(`Task ${taskId} is not in pending status`);
            }
            task.status = 'in_progress';
            task.assignedTo = packerId;
            task.startedAt = new Date();
        }
        /**
         * Complete packing task with package details
         */
        async completePackingTask(taskId, packages) {
            const startTime = Date.now();
            const task = await this.findPackingTask(taskId);
            if (!task) {
                throw new Error(`Packing task ${taskId} not found`);
            }
            if (task.status !== 'in_progress') {
                throw new Error(`Task ${taskId} is not in progress`);
            }
            // Validate packages against task items
            await this.validatePackages(task, packages);
            // Generate SSCC and labels for each package
            const completedPackages = [];
            for (const pkg of packages) {
                const packageWithId = {
                    ...pkg,
                    packageId: `pkg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                    sscc: this.generateSSCC(),
                    labels: await this.generatePackageLabels(pkg),
                    packedAt: new Date(),
                    packedBy: task.assignedTo || 'unknown'
                };
                completedPackages.push(packageWithId);
            }
            // Update task
            task.status = 'completed';
            task.completedAt = new Date();
            task.actualTime = task.startedAt ?
                (task.completedAt.getTime() - task.startedAt.getTime()) / (1000 * 60) : undefined;
            // Publish event
            await this.publishPackCompletedEvent(task, completedPackages);
            this.metrics.recordDatabaseQueryDuration('packing.task_completion', (Date.now() - startTime) / 1000, { taskId });
            this.metrics.incrementPackTasks('packing.completed', { taskId });
            return completedPackages;
        }
        /**
         * Create shipment from packages
         */
        async createShipment(orderId, packages, carrier, shipTo, options) {
            const startTime = Date.now();
            try {
                const shipment = {
                    shipmentId: `ship_${Date.now()}`,
                    shipmentNumber: `SH${Date.now()}`,
                    orderId,
                    carrier,
                    serviceType: options?.serviceType || 'standard',
                    status: 'planned',
                    shipFrom: await this.getShipFromAddress(),
                    shipTo,
                    packages,
                    totalWeight: packages.reduce((sum, pkg) => sum + pkg.weight, 0),
                    totalValue: packages.reduce((sum, pkg) => sum + pkg.contents.reduce((pkgSum, item) => pkgSum + item.value, 0), 0),
                    insuranceValue: options?.insuranceValue,
                    specialInstructions: options?.specialInstructions,
                    requiredDeliveryDate: options?.requiredDeliveryDate,
                    createdAt: new Date()
                };
                // Generate shipping labels
                await this.generateShippingLabels(shipment);
                // Publish event
                await this.publishShipmentCreatedEvent(shipment);
                this.metrics.recordDatabaseQueryDuration('shipping.shipment_creation', (Date.now() - startTime) / 1000, { orderId });
                return shipment;
            }
            catch (error) {
                this.metrics.incrementErrorCount('shipping.shipment_creation_failed', { error: 'shipment_creation_error' });
                throw error;
            }
        }
        /**
         * Ship shipment with carrier integration
         */
        async shipShipment(shipmentId) {
            const startTime = Date.now();
            const shipment = await this.findShipment(shipmentId);
            if (!shipment) {
                throw new Error(`Shipment ${shipmentId} not found`);
            }
            if (shipment.status !== 'ready') {
                throw new Error(`Shipment ${shipmentId} is not ready for shipping`);
            }
            try {
                // Get carrier integration
                const carrier = this.carriers.get(shipment.carrier);
                if (!carrier) {
                    throw new Error(`Carrier ${shipment.carrier} not configured`);
                }
                // Create shipment with carrier
                const trackingNumber = await this.createCarrierShipment(shipment, carrier);
                // Update shipment
                shipment.trackingNumber = trackingNumber;
                shipment.status = 'shipped';
                shipment.shippedAt = new Date();
                // Publish event
                await this.publishShipmentShippedEvent(shipment);
                this.metrics.recordDatabaseQueryDuration('shipping.carrier_integration', (Date.now() - startTime) / 1000, { carrier: carrier.carrierId });
                return trackingNumber;
            }
            catch (error) {
                this.metrics.incrementErrorCount('shipping.carrier_integration_failed', { error: 'carrier_integration_error' });
                throw error;
            }
        }
        /**
         * Generate GS1 labels for package
         */
        async generatePackageLabels(pkg) {
            const labels = [];
            // SSCC label
            labels.push({
                type: 'sscc',
                format: '1d',
                data: pkg.sscc,
                printed: false
            });
            // GTIN labels for each item
            for (const item of pkg.contents) {
                const gtin = await this.getGTINForSKU(item.sku);
                if (gtin) {
                    labels.push({
                        type: 'gtin',
                        format: '1d',
                        data: gtin,
                        printed: false
                    });
                }
            }
            // Batch/lot labels
            const lots = Array.from(new Set(pkg.contents.map(item => item.lot).filter(Boolean)));
            for (const lot of lots) {
                if (lot) {
                    labels.push({
                        type: 'batch',
                        format: '1d',
                        data: lot,
                        printed: false
                    });
                }
            }
            return labels;
        }
        /**
         * Get shipment tracking information
         */
        async getShipmentTracking(shipmentId) {
            const shipment = await this.findShipment(shipmentId);
            if (!shipment) {
                throw new Error(`Shipment ${shipmentId} not found`);
            }
            if (!shipment.trackingNumber) {
                return [];
            }
            const carrier = this.carriers.get(shipment.carrier);
            if (!carrier?.trackingCapabilities) {
                return shipment.carrierEvents || [];
            }
            // Get tracking from carrier API
            const trackingEvents = await this.getCarrierTracking(shipment.trackingNumber, carrier);
            // Update shipment with latest events
            shipment.carrierEvents = trackingEvents;
            // Check if delivered
            const deliveredEvent = trackingEvents?.find(event => event.eventType === 'delivered');
            if (deliveredEvent && shipment.status !== 'delivered') {
                shipment.status = 'delivered';
                shipment.deliveredAt = deliveredEvent.timestamp;
            }
            return trackingEvents;
        }
        /**
         * Generate shipping manifest
         */
        async generateShippingManifest(shipmentId) {
            const shipment = await this.findShipment(shipmentId);
            if (!shipment) {
                throw new Error(`Shipment ${shipmentId} not found`);
            }
            const manifest = {
                totalPackages: shipment.packages.length,
                totalWeight: shipment.totalWeight,
                totalValue: shipment.totalValue,
                packageDetails: shipment.packages.map(pkg => ({
                    packageId: pkg.packageId,
                    sscc: pkg.sscc,
                    weight: pkg.weight,
                    contents: pkg.contents
                }))
            };
            // Add customs information if international
            if (this.isInternationalShipment(shipment)) {
                manifest.customsInfo = await this.generateCustomsInfo(shipment);
            }
            return { shipment, manifest };
        }
        // Private helper methods
        async validatePackages(task, packages) {
            const packedItems = new Map();
            // Count packed quantities
            for (const pkg of packages) {
                for (const item of pkg.contents) {
                    const key = `${item.sku}-${item.lot || ''}-${item.serial || ''}`;
                    packedItems.set(key, (packedItems.get(key) || 0) + item.quantity);
                }
            }
            // Validate against task requirements
            for (const requiredItem of task.items) {
                const key = `${requiredItem.sku}-${requiredItem.lot || ''}-${requiredItem.serial || ''}`;
                const packedQty = packedItems.get(key) || 0;
                if (packedQty !== requiredItem.quantity) {
                    throw new Error(`Quantity mismatch for ${requiredItem.sku}: required ${requiredItem.quantity}, packed ${packedQty}`);
                }
            }
        }
        generateSSCC() {
            // Generate GS1 SSCC (Serial Shipping Container Code)
            // Format: (00) + Extension digit + GS1 Company Prefix + Serial Reference
            const extensionDigit = '3'; // Fixed for logistics
            const companyPrefix = '1234567'; // Example
            const serialRef = Date.now().toString().slice(-9); // 9 digits
            const sscc = `003${companyPrefix}${serialRef}`;
            // Calculate check digit
            const checkDigit = this.calculateGS1CheckDigit(sscc);
            return sscc + checkDigit;
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
        estimatePackingTime(items) {
            const baseTime = 5; // minutes
            const itemsFactor = items.length * 2; // 2 minutes per item
            const quantityFactor = items.reduce((sum, item) => sum + item.quantity, 0) * 0.5; // 30 seconds per unit
            return Math.ceil(baseTime + itemsFactor + quantityFactor);
        }
        async getOrderDetails(orderId) {
            // Mock implementation
            return {
                orderId,
                priority: 5,
                lines: [
                    { sku: 'WIDGET-001', quantity: 5, lot: 'LOT-001' },
                    { sku: 'GADGET-002', quantity: 3, serial: 'SN123456' }
                ]
            };
        }
        async findPackingTask(taskId) {
            // Mock implementation
            return {
                taskId,
                orderId: 'ORDER-123',
                items: [],
                status: 'in_progress',
                priority: 5,
                estimatedTime: 10,
                createdAt: new Date()
            };
        }
        async findShipment(shipmentId) {
            // Mock implementation
            return {
                shipmentId,
                shipmentNumber: 'SH123456',
                orderId: 'ORDER-123',
                carrier: 'UPS',
                serviceType: 'ground',
                status: 'ready',
                shipFrom: {
                    name: 'VALEO Warehouse',
                    address: {
                        street1: '123 Main St',
                        city: 'Anytown',
                        state: 'ST',
                        postalCode: '12345',
                        country: 'US'
                    }
                },
                shipTo: {
                    name: 'Customer',
                    address: {
                        street1: '456 Oak Ave',
                        city: 'Somewhere',
                        state: 'ST',
                        postalCode: '67890',
                        country: 'US'
                    }
                },
                packages: [],
                totalWeight: 10,
                totalValue: 100,
                createdAt: new Date()
            };
        }
        async getGTINForSKU(sku) {
            // Mock GTIN lookup
            const gtinMap = {
                'WIDGET-001': '01234567890123',
                'GADGET-002': '09876543210987'
            };
            return gtinMap[sku] || null;
        }
        async getShipFromAddress() {
            return {
                name: 'VALEO NeuroERP Warehouse',
                address: {
                    street1: '123 Industrial Blvd',
                    city: 'Logistics City',
                    state: 'LC',
                    postalCode: '99999',
                    country: 'DE'
                },
                contact: {
                    name: 'Warehouse Manager',
                    phone: '+49-123-456789',
                    email: 'warehouse@valero-neuroerp.com'
                }
            };
        }
        async generateShippingLabels(shipment) {
            // Generate carrier-specific shipping labels
            const carrier = this.carriers.get(shipment.carrier);
            if (!carrier)
                return;
            // Implementation would generate actual labels via carrier API
            console.log(`Generated shipping labels for ${shipment.shipmentId}`);
        }
        async createCarrierShipment(shipment, carrier) {
            // Mock carrier API integration
            return `TRK${Date.now()}`;
        }
        async getCarrierTracking(trackingNumber, carrier) {
            // Mock tracking API
            return [
                {
                    eventType: 'picked_up',
                    description: 'Package picked up',
                    location: 'Warehouse',
                    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
                },
                {
                    eventType: 'in_transit',
                    description: 'In transit to destination',
                    location: 'Distribution Center',
                    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000) // 1 hour ago
                }
            ];
        }
        isInternationalShipment(shipment) {
            return shipment.shipFrom.address.country !== shipment.shipTo.address.country;
        }
        async generateCustomsInfo(shipment) {
            // Generate customs information for international shipments
            return {
                harmonizedCodes: [],
                totalValue: shipment.totalValue,
                currency: 'EUR'
            };
        }
        async getCarrierForTask(task) {
            // Try to get carrier from associated shipment
            if (task.shipmentId) {
                const shipment = await this.findShipment(task.shipmentId);
                if (shipment) {
                    return shipment.carrier;
                }
            }
            // Fallback to default carrier
            return 'UPS';
        }
        initializeDefaultCarriers() {
            const carriers = [
                {
                    carrierId: 'ups',
                    name: 'UPS',
                    apiEndpoint: 'https://api.ups.com',
                    apiKey: process.env.UPS_API_KEY || '',
                    supportedServices: ['ground', 'air', 'express'],
                    labelFormats: ['pdf', 'png', 'zpl'],
                    trackingCapabilities: true,
                    active: true
                },
                {
                    carrierId: 'fedex',
                    name: 'FedEx',
                    apiEndpoint: 'https://api.fedex.com',
                    apiKey: process.env.FEDEX_API_KEY || '',
                    supportedServices: ['ground', 'express', 'overnight'],
                    labelFormats: ['pdf', 'png', 'zpl'],
                    trackingCapabilities: true,
                    active: true
                },
                {
                    carrierId: 'dhl',
                    name: 'DHL',
                    apiEndpoint: 'https://api.dhl.com',
                    apiKey: process.env.DHL_API_KEY || '',
                    supportedServices: ['ground', 'express', 'international'],
                    labelFormats: ['pdf', 'png', 'zpl'],
                    trackingCapabilities: true,
                    active: true
                }
            ];
            carriers.forEach(carrier => this.carriers.set(carrier.carrierId, carrier));
        }
        // Event publishing methods
        async publishPackTaskCreatedEvent(task) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.pack.created',
                type: 'inventory.pack.created',
                aggregateId: task.taskId,
                aggregateType: 'PackingTask',
                eventVersion: 1,
                occurredOn: new Date(),
                occurredAt: new Date(),
                aggregateVersion: 1,
                tenantId: 'default',
                orderId: task.orderId,
                shipmentId: task.shipmentId || '',
                items: task.items.map(item => ({
                    sku: item.sku,
                    quantity: item.quantity,
                    lot: item.lot,
                    serial: item.serial
                }))
            };
            await this.eventBus.publish(event);
        }
        async publishPackCompletedEvent(task, packages) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.pack.completed',
                type: 'inventory.pack.completed',
                aggregateId: task.taskId,
                aggregateType: 'PackingTask',
                eventVersion: 1,
                occurredOn: new Date(),
                occurredAt: new Date(),
                aggregateVersion: 1,
                tenantId: 'default',
                orderId: task.orderId,
                shipmentId: task.shipmentId || '',
                packedBy: task.assignedTo || 'unknown',
                weight: packages.reduce((sum, pkg) => sum + pkg.weight, 0),
                dimensions: {
                    length: Math.max(...packages.map(p => p.dimensions.length)),
                    width: Math.max(...packages.map(p => p.dimensions.width)),
                    height: packages.reduce((sum, pkg) => sum + pkg.dimensions.height, 0)
                },
                carrier: await this.getCarrierForTask(task)
            };
            await this.eventBus.publish(event);
        }
        async publishShipmentCreatedEvent(shipment) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.shipment.created',
                type: 'inventory.shipment.created',
                aggregateId: shipment.shipmentId,
                aggregateType: 'Shipment',
                eventVersion: 1,
                occurredOn: new Date(),
                occurredAt: new Date(),
                aggregateVersion: 1,
                tenantId: 'default',
                shipmentId: shipment.shipmentId,
                orderId: shipment.orderId,
                carrier: shipment.carrier,
                trackingNumber: shipment.trackingNumber,
                items: shipment.packages.flatMap(pkg => pkg.contents.map(item => ({
                    sku: item.sku,
                    quantity: item.quantity,
                    lot: item.lot,
                    serial: item.serial
                })))
            };
            await this.eventBus.publish(event);
        }
        async publishShipmentShippedEvent(shipment) {
            if (!shipment.trackingNumber || !shipment.shippedAt) {
                throw new Error('Cannot publish shipment shipped event without tracking number and shipped date');
            }
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.shipment.shipped',
                type: 'inventory.shipment.shipped',
                aggregateId: shipment.shipmentId,
                aggregateType: 'Shipment',
                eventVersion: 1,
                occurredOn: new Date(),
                occurredAt: new Date(),
                aggregateVersion: 1,
                tenantId: 'default',
                shipmentId: shipment.shipmentId,
                orderId: shipment.orderId,
                carrier: shipment.carrier,
                trackingNumber: shipment.trackingNumber,
                shippedAt: shipment.shippedAt,
                shippedBy: 'system'
            };
            await this.eventBus.publish(event);
        }
    };
    __setFunctionName(_classThis, "PackingShippingService");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        PackingShippingService = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return PackingShippingService = _classThis;
})();
exports.PackingShippingService = PackingShippingService;
//# sourceMappingURL=packing-shipping-service.js.map