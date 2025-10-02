"use strict";
/**
 * VALEO NeuroERP 3.0 - Putaway & Slotting Service
 *
 * Intelligent putaway planning and slotting optimization for WMS operations
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
exports.PutawaySlottingService = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("../infrastructure/observability/metrics-service");
const sku_1 = require("../core/entities/sku");
const location_1 = require("../core/entities/location");
let PutawaySlottingService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var PutawaySlottingService = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            PutawaySlottingService = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        eventBus;
        metrics = new metrics_service_1.InventoryMetricsService();
        slottingPolicies = new Map();
        constructor(eventBus) {
            this.eventBus = eventBus;
            this.initializeDefaultPolicies();
        }
        /**
         * Plan putaway tasks for received goods
         */
        async planPutaway(asnId, strategy = 'velocity') {
            const startTime = Date.now();
            try {
                // Get ASN details (would come from receiving service)
                const asnDetails = await this.getAsnDetails(asnId);
                if (!asnDetails) {
                    throw new Error(`ASN ${asnId} not found`);
                }
                const tasks = [];
                for (const line of asnDetails.lines) {
                    // Find optimal location for this SKU
                    const optimalLocation = await this.findOptimalLocation(line.sku, line.quantity, strategy, asnDetails.dock);
                    if (!optimalLocation) {
                        throw new Error(`No suitable location found for SKU ${line.sku}`);
                    }
                    const task = {
                        taskId: `putaway_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                        asnId,
                        sku: line.sku,
                        gtin: line.gtin,
                        quantity: line.quantity,
                        uom: line.uom,
                        fromLocation: asnDetails.dock,
                        toLocation: optimalLocation.code,
                        priority: this.calculatePriority(line.sku, strategy),
                        strategy,
                        estimatedTime: this.estimatePutawayTime(line.quantity, strategy),
                        status: 'planned',
                        createdAt: new Date()
                    };
                    tasks.push(task);
                }
                // Sort tasks by priority
                tasks.sort((a, b) => b.priority - a.priority);
                // Publish event
                await this.publishPutawayPlannedEvent(asnId, tasks);
                this.metrics.recordPutawayTime('putaway.plan_putaway', (Date.now() - startTime) / 1000, { strategy: strategy });
                this.metrics.incrementPutawayTasks('putaway.planned', { strategy: strategy });
                return tasks;
            }
            catch (error) {
                this.metrics.incrementErrorCount('putaway.planning_failed', { error: 'planning_error' });
                throw error;
            }
        }
        /**
         * Generate slotting recommendations using AI
         */
        async generateSlottingRecommendations(skus) {
            const startTime = Date.now();
            try {
                const targetSkus = skus || await this.getAllSkus();
                const recommendations = [];
                for (const sku of targetSkus) {
                    const recommendation = await this.generateRecommendationForSku(sku);
                    if (recommendation) {
                        recommendations.push(recommendation);
                    }
                }
                // Sort by expected improvement
                recommendations.sort((a, b) => (b.expectedImprovement.travelTime + b.expectedImprovement.throughput) -
                    (a.expectedImprovement.travelTime + a.expectedImprovement.throughput));
                this.metrics.recordDatabaseQueryDuration('slotting.ai_recommendation', (Date.now() - startTime) / 1000, {});
                return recommendations;
            }
            catch (error) {
                this.metrics.incrementErrorCount('slotting.recommendation_failed', { error: 'recommendation_error' });
                throw error;
            }
        }
        /**
         * Apply slotting recommendation
         */
        async applySlottingRecommendation(recommendation) {
            const startTime = Date.now();
            try {
                // Update SKU location mapping (would update database)
                await this.updateSkuLocation(recommendation.sku, recommendation.recommendedLocation);
                // Publish slotting updated event
                await this.publishSlottingUpdatedEvent(recommendation);
                this.metrics.recordDatabaseQueryDuration('slotting.apply_recommendation', (Date.now() - startTime) / 1000, { sku: recommendation.sku });
            }
            catch (error) {
                this.metrics.incrementErrorCount('slotting.apply_failed', { error: 'apply_error' });
                throw error;
            }
        }
        /**
         * Get slotting analytics
         */
        async getSlottingAnalytics() {
            // Mock analytics - would calculate from actual data
            return {
                totalLocations: 1000,
                utilizedLocations: 850,
                averageUtilization: 85.2,
                slottingEfficiency: 92.5,
                travelTimeReduction: 15.3, // minutes per order
                topRecommendations: []
            };
        }
        /**
         * Create or update slotting policy
         */
        async createSlottingPolicy(policy) {
            const newPolicy = {
                ...policy,
                policyId: `policy_${Date.now()}`,
                createdAt: new Date(),
                updatedAt: new Date()
            };
            this.slottingPolicies.set(newPolicy.policyId, newPolicy);
            return newPolicy;
        }
        /**
         * Find optimal location for SKU
         */
        async findOptimalLocation(sku, quantity, strategy, fromLocation) {
            const skuDetails = await this.getSkuDetails(sku);
            if (!skuDetails)
                return null;
            const availableLocations = await this.getAvailableLocations(skuDetails, quantity);
            if (availableLocations.length === 0)
                return null;
            switch (strategy) {
                case 'velocity':
                    return this.findVelocityOptimalLocation(availableLocations, skuDetails, fromLocation);
                case 'abc':
                    return this.findAbcOptimalLocation(availableLocations, skuDetails, fromLocation);
                case 'temp_zone':
                    return this.findTempZoneOptimalLocation(availableLocations, skuDetails, fromLocation);
                case 'hazmat':
                    return this.findHazmatOptimalLocation(availableLocations, skuDetails, fromLocation);
                default:
                    return availableLocations[0] ?? null; // Simple fallback
            }
        }
        /**
         * Generate AI-powered recommendation for single SKU
         */
        async generateRecommendationForSku(sku) {
            const skuDetails = await this.getSkuDetails(sku);
            if (!skuDetails)
                return null;
            const currentLocation = await this.getCurrentSkuLocation(sku);
            const optimalLocation = await this.findOptimalLocation(sku, 1, 'velocity', 'DOCK-01');
            if (!optimalLocation || optimalLocation.code === currentLocation) {
                return null;
            }
            // Calculate expected improvements
            const distanceReduction = currentLocation ?
                await this.calculateDistanceReduction(currentLocation, optimalLocation.code) : 0;
            const throughputIncrease = await this.calculateThroughputIncrease(sku, optimalLocation.code);
            return {
                sku,
                currentLocation: currentLocation ?? '',
                recommendedLocation: optimalLocation.code,
                confidence: 0.87, // AI confidence score
                reasoning: [
                    `Velocity class ${skuDetails.velocityClass} items should be in prime locations`,
                    `Reduces travel distance by ${distanceReduction}m`,
                    `Expected throughput increase: ${throughputIncrease} picks/hour`
                ],
                expectedImprovement: {
                    travelTime: distanceReduction / 100, // Rough estimate: 100m = 1 minute
                    throughput: throughputIncrease,
                    spaceUtilization: 5.2 // percentage improvement
                },
                aiFeatures: {
                    velocityScore: skuDetails.velocityClass === 'X' ? 1.0 : skuDetails.velocityClass === 'Y' ? 0.7 : 0.3,
                    currentUtilization: 78.5,
                    optimalUtilization: 83.7,
                    distanceToPrime: distanceReduction
                }
            };
        }
        /**
         * Velocity-based optimal location finding
         */
        findVelocityOptimalLocation(locations, sku, fromLocation) {
            // Sort by distance from prime picking areas and velocity preference
            const sorted = locations.sort((a, b) => {
                const aScore = this.calculateVelocityScore(a, sku, fromLocation);
                const bScore = this.calculateVelocityScore(b, sku, fromLocation);
                return bScore - aScore; // Higher score = better
            });
            return sorted[0] || null;
        }
        /**
         * ABC-based optimal location finding
         */
        findAbcOptimalLocation(locations, sku, fromLocation) {
            // Sort by ABC zone preference and distance
            const sorted = locations.sort((a, b) => {
                const aScore = this.calculateAbcScore(a, sku, fromLocation);
                const bScore = this.calculateAbcScore(b, sku, fromLocation);
                return bScore - aScore;
            });
            return sorted[0] || null;
        }
        /**
         * Temperature zone-based optimal location finding
         */
        findTempZoneOptimalLocation(locations, sku, fromLocation) {
            // Filter locations that support the required temperature zone
            const compatibleLocations = locations.filter(loc => loc.supportsTemperature(sku.tempZone));
            if (compatibleLocations.length === 0)
                return null;
            // Sort by distance
            const sorted = compatibleLocations.sort((a, b) => {
                const aDistance = a.getDistanceTo(this.createLocationFromCode(fromLocation));
                const bDistance = b.getDistanceTo(this.createLocationFromCode(fromLocation));
                return aDistance - bDistance;
            });
            return sorted[0] || null;
        }
        /**
         * Hazardous materials optimal location finding
         */
        findHazmatOptimalLocation(locations, sku, fromLocation) {
            // Filter locations that allow hazardous materials
            const hazmatLocations = locations.filter(loc => loc.hazmatAllowed);
            if (hazmatLocations.length === 0)
                return null;
            // Sort by distance from staging area
            const sorted = hazmatLocations.sort((a, b) => {
                const aDistance = a.getDistanceTo(this.createLocationFromCode(fromLocation));
                const bDistance = b.getDistanceTo(this.createLocationFromCode(fromLocation));
                return aDistance - bDistance;
            });
            return sorted[0] || null;
        }
        /**
         * Calculate ABC score for location
         */
        calculateAbcScore(location, sku, fromLocation) {
            let score = 0;
            // ABC class preference
            if (sku.abcClass === 'A' && location.zone === 'A')
                score += 100;
            else if (sku.abcClass === 'B' && location.zone === 'B')
                score += 75;
            else if (sku.abcClass === 'C' && location.zone === 'C')
                score += 50;
            // Distance penalty
            const distance = location.getDistanceTo(this.createLocationFromCode(fromLocation));
            score -= distance * 0.1;
            return score;
        }
        /**
         * Calculate velocity score for location
         */
        calculateVelocityScore(location, sku, fromLocation) {
            let score = 0;
            // Prime locations for fast-moving items
            if (sku.isFastMoving() && location.isPickLocation()) {
                score += 100;
            }
            // Distance penalty
            const distance = location.getDistanceTo(this.createLocationFromCode(fromLocation));
            score -= distance * 0.1;
            // Zone preference
            if (location.zone === 'A')
                score += 50;
            else if (location.zone === 'B')
                score += 25;
            return score;
        }
        /**
         * Calculate priority for putaway task
         */
        calculatePriority(sku, strategy) {
            // Base priority
            let priority = 5;
            // Strategy-based adjustments
            switch (strategy) {
                case 'velocity':
                    priority += 10; // High priority for fast-moving items
                    break;
                case 'hazmat':
                    priority += 15; // Critical for hazardous materials
                    break;
                case 'temp_zone':
                    priority += 8; // Important for temperature control
                    break;
            }
            return Math.min(priority, 20); // Cap at 20
        }
        /**
         * Estimate putaway time
         */
        estimatePutawayTime(quantity, strategy) {
            const baseTime = 2; // minutes
            const quantityFactor = Math.ceil(quantity / 10); // 10 units per minute
            const strategyFactor = strategy === 'hazmat' ? 1.5 : 1.0;
            return Math.ceil(baseTime * quantityFactor * strategyFactor);
        }
        // Mock data methods (would be replaced with actual database calls)
        async getAsnDetails(asnId) {
            return {
                asnId,
                dock: 'DOCK-01',
                lines: [
                    { sku: 'WIDGET-001', gtin: '1234567890123', quantity: 100, uom: 'EA' }
                ]
            };
        }
        async getSkuDetails(sku) {
            // Mock SKU data
            return sku_1.Sku.create({
                sku,
                description: 'Test Widget',
                category: 'Widgets',
                uom: 'EA',
                tempZone: 'ambient',
                abcClass: 'A',
                velocityClass: 'X',
                active: true,
                hazmat: false,
                serialTracked: false,
                lotTracked: true
            });
        }
        async getAvailableLocations(sku, quantity) {
            // Mock locations
            return [
                location_1.Location.create({
                    code: 'A-01-01-01',
                    type: 'pick',
                    zone: 'A',
                    capacity: { maxQty: 1000, uom: 'EA' },
                    active: true,
                    blocked: false,
                    tempControlled: false,
                    hazmatAllowed: false
                })
            ].filter(loc => loc.canStoreSku({
                tempZone: sku.tempZone,
                hazmat: sku.hazmat,
                weight: 1,
                volume: 0.1
            }));
        }
        async getAllSkus() {
            return ['WIDGET-001', 'GADGET-002'];
        }
        async getCurrentSkuLocation(sku) {
            return 'B-05-10-05'; // Mock current location
        }
        async updateSkuLocation(sku, location) {
            console.log(`Updating ${sku} location to ${location}`);
        }
        async calculateDistanceReduction(from, to) {
            return 50; // Mock 50m reduction
        }
        async calculateThroughputIncrease(sku, location) {
            return 5; // Mock 5 additional picks per hour
        }
        createLocationFromCode(code) {
            return location_1.Location.create({
                code,
                type: 'dock',
                zone: 'ambient',
                capacity: { maxQty: 10000, uom: 'EA' },
                active: true,
                blocked: false,
                tempControlled: false,
                hazmatAllowed: false
            });
        }
        initializeDefaultPolicies() {
            // Initialize with default slotting policies
            const velocityPolicy = {
                policyId: 'velocity_policy',
                name: 'Velocity-Based Slotting',
                description: 'Slot fast-moving items in prime locations',
                strategy: 'velocity',
                rules: [{
                        ruleId: 'velocity_rule_1',
                        condition: {
                            skuCriteria: { velocityClass: 'X' }
                        },
                        action: {
                            priority: 10,
                            preferredZones: ['A']
                        },
                        weight: 100
                    }],
                zones: ['A', 'B', 'C'],
                active: true,
                createdAt: new Date(),
                updatedAt: new Date()
            };
            this.slottingPolicies.set(velocityPolicy.policyId, velocityPolicy);
        }
        /**
         * Publish putaway planned event
         */
        async publishPutawayPlannedEvent(asnId, tasks) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.putaway.planned',
                type: 'inventory.putaway.planned',
                occurredAt: new Date(),
                aggregateVersion: 1,
                aggregateId: asnId,
                aggregateType: 'ASN',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                asnId,
                tasks: tasks.map(task => ({
                    taskId: task.taskId,
                    sku: task.sku,
                    fromLocation: task.fromLocation,
                    toLocation: task.toLocation,
                    qty: task.quantity,
                    priority: task.priority,
                    strategy: task.strategy
                }))
            };
            await this.eventBus.publish(event);
        }
        /**
         * Publish slotting updated event
         */
        async publishSlottingUpdatedEvent(recommendation) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.slotting.updated',
                type: 'inventory.slotting.updated',
                occurredAt: new Date(),
                aggregateVersion: 1,
                aggregateId: recommendation.sku,
                aggregateType: 'SKU',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                sku: recommendation.sku,
                oldLocation: recommendation.currentLocation,
                newLocation: recommendation.recommendedLocation,
                reason: 'optimization',
                aiConfidence: recommendation.confidence
            };
            await this.eventBus.publish(event);
        }
    };
    return PutawaySlottingService = _classThis;
})();
exports.PutawaySlottingService = PutawaySlottingService;
