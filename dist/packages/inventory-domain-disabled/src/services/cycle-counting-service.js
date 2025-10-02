"use strict";
/**
 * VALEO NeuroERP 3.0 - Cycle Counting Service
 *
 * ABC/XYZ policies, automated scheduling, and accuracy tracking
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
exports.CycleCountingService = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("../infrastructure/observability/metrics-service");
let CycleCountingService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var CycleCountingService = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            CycleCountingService = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        eventBus;
        metrics = new metrics_service_1.InventoryMetricsService();
        policies = new Map();
        activeCounts = new Map();
        constructor(eventBus) {
            this.eventBus = eventBus;
            this.initializeDefaultPolicies();
        }
        /**
         * Create ABC classification for items
         */
        async createABCClassification(skus) {
            const startTime = Date.now();
            try {
                const classifications = [];
                // Get usage data for all SKUs
                const usageData = await this.getSKUUsageData(skus);
                // Sort by annual value descending
                usageData.sort((a, b) => b.annualValue - a.annualValue);
                const totalValue = usageData.reduce((sum, item) => sum + item.annualValue, 0);
                let cumulativePercentage = 0;
                for (const item of usageData) {
                    const percentageOfTotal = (item.annualValue / totalValue) * 100;
                    cumulativePercentage += percentageOfTotal;
                    let classification;
                    let countFrequency;
                    if (cumulativePercentage <= 80) {
                        classification = 'A';
                        countFrequency = 12; // Monthly
                    }
                    else if (cumulativePercentage <= 95) {
                        classification = 'B';
                        countFrequency = 6; // Bi-monthly
                    }
                    else {
                        classification = 'C';
                        countFrequency = 2; // Semi-annually
                    }
                    classifications.push({
                        sku: item.sku,
                        classification,
                        annualUsage: item.annualUsage,
                        annualValue: item.annualValue,
                        percentageOfTotal,
                        cumulativePercentage,
                        countFrequency,
                        nextCountDue: this.calculateNextCountDue(classification)
                    });
                }
                this.metrics.recordDatabaseQueryDuration('cycle_count.abc_classification', (Date.now() - startTime) / 1000, { tenantId: 'default' });
                return classifications;
            }
            catch (error) {
                this.metrics.incrementErrorCount('cycle_count.abc_classification_failed', { error: 'abc_classification_error' });
                throw error;
            }
        }
        /**
         * Create XYZ classification for items
         */
        async createXYZClassification(skus) {
            const startTime = Date.now();
            try {
                const classifications = [];
                for (const sku of skus) {
                    const demandData = await this.getSKUDemandData(sku);
                    const variability = this.calculateDemandVariability(demandData);
                    const forecastAccuracy = await this.getForecastAccuracy(sku);
                    let classification;
                    let countFrequency;
                    if (variability <= 0.5 && forecastAccuracy >= 0.8) {
                        classification = 'X'; // Low variability, high forecast accuracy
                        countFrequency = 4; // Quarterly
                    }
                    else if (variability <= 1.0 && forecastAccuracy >= 0.6) {
                        classification = 'Y'; // Medium variability
                        countFrequency = 6; // Bi-monthly
                    }
                    else {
                        classification = 'Z'; // High variability, low forecast accuracy
                        countFrequency = 12; // Monthly
                    }
                    classifications.push({
                        sku,
                        classification,
                        demandVariability: variability,
                        forecastAccuracy,
                        demandPattern: this.analyzeDemandPattern(demandData),
                        safetyStock: this.calculateSafetyStock(sku, variability),
                        reorderPoint: await this.getReorderPoint(sku),
                        countFrequency,
                        nextCountDue: this.calculateNextCountDue(classification)
                    });
                }
                this.metrics.recordDatabaseQueryDuration('cycle_count.xyz_classification', (Date.now() - startTime) / 1000, { tenantId: 'default' });
                return classifications;
            }
            catch (error) {
                this.metrics.incrementErrorCount('cycle_count.xyz_classification_failed', { error: 'xyz_classification_error' });
                throw error;
            }
        }
        /**
         * Create cycle count policy
         */
        async createCycleCountPolicy(policy) {
            const fullPolicy = {
                ...policy,
                policyId: `policy_${Date.now()}`
            };
            this.policies.set(fullPolicy.policyId, fullPolicy);
            return fullPolicy;
        }
        /**
         * Generate cycle count schedule
         */
        async generateCycleCountSchedule(policyId, startDate, endDate) {
            const startTime = Date.now();
            try {
                const policy = this.policies.get(policyId);
                if (!policy) {
                    throw new Error(`Policy ${policyId} not found`);
                }
                const schedules = [];
                let currentDate = new Date(startDate);
                while (currentDate <= endDate) {
                    const items = await this.selectItemsForCounting(policy, currentDate);
                    if (items.length > 0) {
                        const schedule = {
                            scheduleId: `schedule_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                            policyId,
                            scheduledDate: new Date(currentDate),
                            dueDate: new Date(currentDate.getTime() + 24 * 60 * 60 * 1000), // Next day
                            items,
                            status: 'pending',
                            createdAt: new Date()
                        };
                        schedules.push(schedule);
                    }
                    // Move to next count date based on frequency
                    currentDate = this.getNextCountDate(currentDate, policy.frequency);
                }
                this.metrics.recordDatabaseQueryDuration('cycle_count.schedule_generation', (Date.now() - startTime) / 1000, { tenantId: 'default' });
                return schedules;
            }
            catch (error) {
                this.metrics.incrementErrorCount('cycle_count.schedule_generation_failed', { error: 'schedule_generation_error' });
                throw error;
            }
        }
        /**
         * Create cycle count from schedule
         */
        async createCycleCount(scheduleId, assignedTo) {
            const startTime = Date.now();
            try {
                const schedule = await this.getSchedule(scheduleId);
                if (!schedule) {
                    throw new Error(`Schedule ${scheduleId} not found`);
                }
                const policy = this.policies.get(schedule.policyId);
                if (!policy) {
                    throw new Error(`Policy ${schedule.policyId} not found`);
                }
                // Get current inventory levels for scheduled items
                const items = await Promise.all(schedule.items.map(async (item) => {
                    const inventory = await this.getCurrentInventory(item.sku, item.location);
                    return {
                        sku: item.sku,
                        location: item.location,
                        lot: inventory.lot,
                        serial: inventory.serial,
                        expectedQty: inventory.quantity,
                        expectedValue: inventory.unitCost ? inventory.unitCost * inventory.quantity : 0,
                        status: 'pending'
                    };
                }));
                const count = {
                    countId: `count_${Date.now()}`,
                    countNumber: `CC${Date.now()}`,
                    policyId: schedule.policyId,
                    status: 'planned',
                    type: policy.classification,
                    priority: schedule.items.reduce((max, item) => Math.max(max, item.priority), 1),
                    assignedTo,
                    items,
                    schedule: {
                        plannedStart: schedule.scheduledDate,
                        plannedEnd: schedule.dueDate
                    },
                    results: {
                        totalItems: items.length,
                        countedItems: 0,
                        variancesFound: 0,
                        accuracy: 0,
                        totalVarianceValue: 0,
                        adjustmentsMade: 0
                    },
                    createdAt: new Date()
                };
                this.activeCounts.set(count.countId, count);
                schedule.status = 'executing';
                // Publish event
                await this.publishCycleCountCreatedEvent(count);
                this.metrics.recordDatabaseQueryDuration('cycle_count.count_creation', (Date.now() - startTime) / 1000, { countId: count.countId });
                return count;
            }
            catch (error) {
                this.metrics.incrementErrorCount('cycle_count.count_creation_failed', { error: 'count_creation_error' });
                throw error;
            }
        }
        /**
         * Record count result for an item
         */
        async recordCountResult(countId, sku, location, countedQty, notes) {
            const count = this.activeCounts.get(countId);
            if (!count) {
                throw new Error(`Count ${countId} not found`);
            }
            if (count.status !== 'in_progress') {
                count.status = 'in_progress';
                count.schedule.actualStart = new Date();
            }
            const item = count.items.find(i => i.sku === sku && i.location === location);
            if (!item) {
                throw new Error(`Item ${sku} at ${location} not found in count ${countId}`);
            }
            item.countedQty = countedQty;
            item.countedValue = item.expectedValue * (countedQty / item.expectedQty);
            item.varianceQty = countedQty - item.expectedQty;
            item.varianceValue = item.countedValue - item.expectedValue;
            item.variancePercent = item.expectedQty > 0 ? (item.varianceQty / item.expectedQty) * 100 : 0;
            item.status = 'counted';
            item.notes = notes;
            // Check for variances
            const policy = this.policies.get(count.policyId);
            if (policy && this.isVariance(item, policy.tolerance)) {
                item.status = 'variance';
                count.results.variancesFound++;
            }
            count.results.countedItems++;
        }
        /**
         * Complete cycle count
         */
        async completeCycleCount(countId) {
            const startTime = Date.now();
            const count = this.activeCounts.get(countId);
            if (!count) {
                throw new Error(`Count ${countId} not found`);
            }
            if (count.status !== 'in_progress') {
                throw new Error(`Count ${countId} is not in progress`);
            }
            count.status = 'completed';
            count.completedAt = new Date();
            count.schedule.actualEnd = new Date();
            // Calculate results
            count.results.accuracy = (count.results.totalItems - count.results.variancesFound) / count.results.totalItems * 100;
            count.results.totalVarianceValue = count.items.reduce((sum, item) => sum + (item.varianceValue || 0), 0);
            // Auto-adjust if policy allows
            const policy = this.policies.get(count.policyId);
            if (policy?.autoAdjust) {
                await this.processAutoAdjustments(count);
            }
            // Update schedule
            const schedule = await this.getScheduleByCount(countId);
            if (schedule) {
                schedule.status = 'completed';
            }
            // Publish event
            await this.publishCycleCountCompletedEvent(count);
            this.metrics.recordDatabaseQueryDuration('cycle_count.count_completion', (Date.now() - startTime) / 1000, { countId });
            this.metrics.incrementCycleCounts('cycle_count.completed', { countId });
            return count;
        }
        /**
         * Get cycle count performance metrics
         */
        async getCycleCountPerformance(period = 'month') {
            const startTime = Date.now();
            try {
                const endDate = new Date();
                const startDate = new Date();
                switch (period) {
                    case 'day':
                        startDate.setDate(endDate.getDate() - 1);
                        break;
                    case 'week':
                        startDate.setDate(endDate.getDate() - 7);
                        break;
                    case 'month':
                        startDate.setMonth(endDate.getMonth() - 1);
                        break;
                }
                const completedCounts = await this.getCompletedCounts(startDate, endDate);
                const performance = this.calculatePerformanceMetrics(completedCounts, period);
                this.metrics.recordDatabaseQueryDuration('cycle_count.performance_calculation', (Date.now() - startTime) / 1000, { period });
                return performance;
            }
            catch (error) {
                this.metrics.incrementErrorCount('cycle_count.performance_calculation_failed', { error: 'performance_calculation_error' });
                throw error;
            }
        }
        /**
         * Get overdue counts
         */
        async getOverdueCounts() {
            const now = new Date();
            const schedules = await this.getAllSchedules();
            return schedules.filter(schedule => schedule.status === 'pending' &&
                schedule.dueDate < now);
        }
        // Private helper methods
        initializeDefaultPolicies() {
            const policies = [
                {
                    policyId: 'abc_a',
                    policyName: 'ABC Class A Items',
                    classification: 'ABC',
                    frequency: 'monthly',
                    coverage: 100,
                    priority: 'A',
                    method: 'full_count',
                    tolerance: { quantity: 5, value: 10 },
                    autoAdjust: true,
                    requiresApproval: false,
                    active: true
                },
                {
                    policyId: 'abc_b',
                    policyName: 'ABC Class B Items',
                    classification: 'ABC',
                    frequency: 'quarterly',
                    coverage: 50,
                    priority: 'B',
                    method: 'sample_count',
                    tolerance: { quantity: 10, value: 15 },
                    autoAdjust: false,
                    requiresApproval: true,
                    active: true
                },
                {
                    policyId: 'xyz_z',
                    policyName: 'XYZ Class Z Items',
                    classification: 'XYZ',
                    frequency: 'monthly',
                    coverage: 25,
                    priority: 'Z',
                    method: 'zero_count',
                    tolerance: { quantity: 20, value: 25 },
                    autoAdjust: false,
                    requiresApproval: true,
                    active: true
                }
            ];
            policies.forEach(policy => this.policies.set(policy.policyId, policy));
        }
        async getSKUUsageData(skus) {
            // Mock implementation
            return skus.map(sku => ({
                sku,
                annualUsage: Math.random() * 10000,
                annualValue: Math.random() * 50000
            }));
        }
        async getSKUDemandData(sku) {
            // Mock demand data for last 12 months
            return Array.from({ length: 12 }, () => Math.random() * 1000 + 500);
        }
        calculateDemandVariability(demandData) {
            const mean = demandData.reduce((sum, val) => sum + val, 0) / demandData.length;
            const variance = demandData.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / demandData.length;
            return Math.sqrt(variance) / mean; // Coefficient of variation
        }
        async getForecastAccuracy(sku) {
            // Mock forecast accuracy
            return Math.random() * 0.4 + 0.6; // 0.6 to 1.0
        }
        analyzeDemandPattern(demandData) {
            const variability = this.calculateDemandVariability(demandData);
            if (variability < 0.3)
                return 'stable';
            if (variability < 0.7)
                return 'seasonal';
            return 'erratic';
        }
        calculateSafetyStock(sku, variability) {
            // Mock safety stock calculation
            return variability * 100;
        }
        async getReorderPoint(sku) {
            // Mock reorder point
            return Math.random() * 200 + 100;
        }
        calculateNextCountDue(classification) {
            const now = new Date();
            const days = classification === 'A' || classification === 'Z' ? 30 :
                classification === 'B' || classification === 'Y' ? 60 : 120;
            now.setDate(now.getDate() + days);
            return now;
        }
        getNextCountDate(currentDate, frequency) {
            const next = new Date(currentDate);
            switch (frequency) {
                case 'daily':
                    next.setDate(next.getDate() + 1);
                    break;
                case 'weekly':
                    next.setDate(next.getDate() + 7);
                    break;
                case 'monthly':
                    next.setMonth(next.getMonth() + 1);
                    break;
                case 'quarterly':
                    next.setMonth(next.getMonth() + 3);
                    break;
            }
            return next;
        }
        async selectItemsForCounting(policy, date) {
            // Mock item selection based on policy
            const items = [];
            // Get items due for counting based on classification
            const dueItems = await this.getItemsDueForCounting(policy, date);
            // Apply coverage percentage
            const count = Math.ceil(dueItems.length * (policy.coverage / 100));
            const selectedItems = dueItems.slice(0, count);
            for (const item of selectedItems) {
                items.push({
                    sku: item.sku,
                    location: item.location,
                    priority: this.getPriorityValue(policy.priority)
                });
            }
            return items;
        }
        async getItemsDueForCounting(policy, date) {
            // Mock implementation - would query database for items due for counting
            return [
                { sku: 'WIDGET-001', location: 'A-01-01-01' },
                { sku: 'GADGET-002', location: 'A-01-01-02' }
            ];
        }
        getPriorityValue(priority) {
            const priorities = { 'A': 5, 'B': 4, 'C': 3, 'X': 2, 'Y': 1, 'Z': 1 };
            return priorities[priority] || 1;
        }
        async getSchedule(scheduleId) {
            // Mock implementation
            return {
                scheduleId,
                policyId: 'policy_123',
                scheduledDate: new Date(),
                dueDate: new Date(Date.now() + 24 * 60 * 60 * 1000),
                items: [],
                status: 'pending',
                createdAt: new Date()
            };
        }
        async getCurrentInventory(sku, location) {
            // Mock inventory data
            return {
                sku,
                location,
                quantity: Math.floor(Math.random() * 100) + 10,
                unitCost: Math.random() * 50 + 10
            };
        }
        isVariance(item, tolerance) {
            const qtyVariancePercent = Math.abs(item.variancePercent || 0);
            const valueVariancePercent = item.expectedValue > 0 ?
                Math.abs((item.varianceValue || 0) / item.expectedValue * 100) : 0;
            return qtyVariancePercent > tolerance.quantity || valueVariancePercent > tolerance.value;
        }
        async processAutoAdjustments(count) {
            const varianceItems = count.items.filter(item => item.status === 'variance');
            for (const item of varianceItems) {
                if (item.countedQty !== undefined) {
                    // Create inventory adjustment
                    await this.createInventoryAdjustment(item.sku, item.location, item.countedQty - item.expectedQty, `Cycle count adjustment - ${count.countNumber}`, item.lot, item.serial);
                    item.status = 'adjusted';
                    count.results.adjustmentsMade++;
                }
            }
        }
        async createInventoryAdjustment(sku, location, quantity, reason, lot, serial) {
            // Mock implementation - would create inventory adjustment
            console.log(`Adjusting inventory: ${sku} at ${location} by ${quantity}`);
        }
        async getScheduleByCount(countId) {
            // Mock implementation
            return null;
        }
        async getCompletedCounts(startDate, endDate) {
            // Mock implementation
            return Array.from(this.activeCounts.values())
                .filter(count => count.completedAt && count.completedAt >= startDate && count.completedAt <= endDate);
        }
        calculatePerformanceMetrics(counts, period) {
            const totalCounts = counts.length;
            const totalAccuracy = counts.reduce((sum, count) => sum + count.results.accuracy, 0);
            const averageAccuracy = totalCounts > 0 ? totalAccuracy / totalCounts : 0;
            return {
                period,
                metrics: {
                    totalCounts,
                    completedCounts: totalCounts,
                    accuracy: averageAccuracy,
                    averageVariance: 0, // Would calculate from actual data
                    totalVarianceValue: counts.reduce((sum, count) => sum + count.results.totalVarianceValue, 0),
                    timePerCount: 0, // Would calculate from actual data
                    itemsPerHour: 0 // Would calculate from actual data
                },
                byLocation: [],
                bySKU: [],
                trends: {
                    accuracy: [],
                    varianceRate: [],
                    productivity: []
                }
            };
        }
        async getAllSchedules() {
            // Mock implementation
            return [];
        }
        // Event publishing methods
        async publishCycleCountCreatedEvent(count) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.cyclecount.created',
                aggregateId: count.countId,
                aggregateType: 'CycleCount',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                type: 'inventory.cyclecount.created',
                occurredAt: new Date(),
                aggregateVersion: 1,
                countId: count.countId,
                locations: Array.from(new Set(count.items.map(item => item.location))),
                method: count.type === 'ABC' ? 'ABC' : 'manual',
                scheduledDate: count.schedule.plannedStart
            };
            await this.eventBus.publish(event);
        }
        async publishCycleCountCompletedEvent(count) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.cyclecount.completed',
                aggregateId: count.countId,
                aggregateType: 'CycleCount',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                type: 'inventory.cyclecount.completed',
                occurredAt: new Date(),
                aggregateVersion: 1,
                countId: count.countId,
                countedBy: count.assignedTo || 'unknown',
                discrepancies: count.items
                    .filter(item => item.status === 'variance')
                    .map(item => ({
                    sku: item.sku,
                    location: item.location,
                    expectedQty: item.expectedQty,
                    countedQty: item.countedQty || 0,
                    variance: item.varianceQty || 0
                })),
                accuracy: count.results.accuracy
            };
            await this.eventBus.publish(event);
        }
    };
    return CycleCountingService = _classThis;
})();
exports.CycleCountingService = CycleCountingService;
