"use strict";
/**
 * VALEO NeuroERP 3.0 - Picking Service
 *
 * Advanced picking operations with wave/batch/zone picking strategies
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
exports.PickingService = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("../infrastructure/observability/metrics-service");
let PickingService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var PickingService = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            PickingService = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        eventBus;
        metrics = new metrics_service_1.InventoryMetricsService();
        zones = new Map();
        activeWaves = new Map();
        constructor(eventBus) {
            this.eventBus = eventBus;
            this.initializeDefaultZones();
        }
        /**
         * Create picking wave from orders
         */
        async createPickingWave(orders, strategy = 'batch', zone) {
            const startTime = Date.now();
            try {
                // Get order details and create tasks
                const tasks = await this.createPickTasksFromOrders(orders, strategy, zone);
                // Group tasks by strategy
                const groupedTasks = await this.groupTasksByStrategy(tasks, strategy);
                // Create wave
                const wave = {
                    waveId: `wave_${Date.now()}`,
                    waveNumber: `W${Date.now()}`,
                    status: 'planned',
                    strategy,
                    priority: this.calculateWavePriority(tasks),
                    zone: zone || this.assignOptimalZone(tasks),
                    tasks: groupedTasks,
                    totalTasks: groupedTasks.length,
                    completedTasks: 0,
                    totalQuantity: groupedTasks.reduce((sum, task) => sum + task.quantity, 0),
                    pickedQuantity: 0,
                    assignedPickers: [],
                    estimatedDuration: this.estimateWaveDuration(groupedTasks, strategy),
                    createdAt: new Date()
                };
                // Store wave
                this.activeWaves.set(wave.waveId, wave);
                // Publish event
                await this.publishWaveCreatedEvent(wave);
                this.metrics.recordDatabaseQueryDuration('picking.wave_creation', (Date.now() - startTime) / 1000, {});
                this.metrics.incrementPickTasks('created', { strategy });
                return wave;
            }
            catch (error) {
                this.metrics.incrementErrorCount('picking.wave_creation_failed', { error: 'wave_creation_error' });
                throw error;
            }
        }
        /**
         * Release wave for picking
         */
        async releaseWave(waveId) {
            const wave = this.activeWaves.get(waveId);
            if (!wave) {
                throw new Error(`Wave ${waveId} not found`);
            }
            if (wave.status !== 'planned') {
                throw new Error(`Wave ${waveId} is not in planned status`);
            }
            wave.status = 'released';
            wave.releasedAt = new Date();
            // Assign pickers to tasks
            await this.assignPickersToWave(wave);
            // Publish task creation events
            for (const task of wave.tasks) {
                await this.publishPickTaskCreatedEvent(task);
            }
        }
        /**
         * Start picking task
         */
        async startPickTask(taskId, pickerId) {
            const task = await this.findPickTask(taskId);
            if (!task) {
                throw new Error(`Task ${taskId} not found`);
            }
            if (task.status !== 'pending') {
                throw new Error(`Task ${taskId} is not in pending status`);
            }
            task.status = 'in_progress';
            task.assignedTo = pickerId;
            task.startedAt = new Date();
            // Update wave progress
            if (task.waveId) {
                const wave = this.activeWaves.get(task.waveId);
                if (wave) {
                    wave.status = 'in_progress';
                }
            }
        }
        /**
         * Complete picking task
         */
        async completePickTask(taskId, pickedQuantity, actualTime, qualityChecks) {
            const startTime = Date.now();
            const task = await this.findPickTask(taskId);
            if (!task) {
                throw new Error(`Task ${taskId} not found`);
            }
            if (task.status !== 'in_progress') {
                throw new Error(`Task ${taskId} is not in progress`);
            }
            // Validate picked quantity
            if (pickedQuantity > task.quantity) {
                throw new Error('Picked quantity cannot exceed required quantity');
            }
            task.pickedQuantity = pickedQuantity;
            task.actualTime = actualTime || (task.startedAt ? (Date.now() - task.startedAt.getTime()) / 1000 : 0);
            task.completedAt = new Date();
            if (qualityChecks) {
                task.qualityChecks = qualityChecks;
            }
            // Determine status based on quantity and quality
            if (pickedQuantity === 0) {
                task.status = 'short';
            }
            else if (pickedQuantity < task.quantity) {
                task.status = 'short';
            }
            else if (qualityChecks && qualityChecks.some(check => !check.passed)) {
                task.status = 'damaged';
            }
            else {
                task.status = 'completed';
            }
            // Update wave progress
            if (task.waveId) {
                await this.updateWaveProgress(task.waveId);
            }
            // Publish completion event
            await this.publishPickCompletedEvent(task);
            // Update picker performance
            if (task.assignedTo) {
                await this.updatePickerPerformance(task.assignedTo, task);
            }
            this.metrics.recordDatabaseQueryDuration('picking.task_completion', (Date.now() - startTime) / 1000, {});
            this.metrics.incrementPickTasks('completed', { status: task.status });
        }
        /**
         * Get picker performance metrics
         */
        async getPickerPerformance(pickerId, period = 'shift') {
            const startTime = Date.now();
            try {
                const performance = await this.calculatePickerPerformance(pickerId, period);
                this.metrics.recordDatabaseQueryDuration('picking.performance_calculation', (Date.now() - startTime) / 1000, {});
                return performance;
            }
            catch (error) {
                this.metrics.incrementErrorCount('picking.performance_calculation_failed', { error: 'performance_calculation_error' });
                throw error;
            }
        }
        /**
         * Get zone utilization and performance
         */
        async getZonePerformance(zoneId) {
            const zone = this.zones.get(zoneId);
            if (!zone) {
                throw new Error(`Zone ${zoneId} not found`);
            }
            // Calculate current metrics
            const activeTasks = await this.getActiveTasksInZone(zoneId);
            const completedTasks = await this.getCompletedTasksInZone(zoneId, new Date(Date.now() - 24 * 60 * 60 * 1000)); // Last 24 hours
            const utilization = (activeTasks.length / zone.capacity.maxConcurrentPickers) * 100;
            const activePickers = new Set(activeTasks.map(task => task.assignedTo).filter(Boolean)).size;
            // Calculate average productivity (picks per hour)
            const totalPicks = completedTasks.reduce((sum, task) => sum + task.pickedQuantity, 0);
            const totalTime = completedTasks.reduce((sum, task) => sum + (task.actualTime || 0), 0) / 3600; // Convert to hours
            const averageProductivity = totalTime > 0 ? totalPicks / totalTime : 0;
            // Identify bottlenecks
            const bottlenecks = [];
            if (utilization > 90)
                bottlenecks.push('High utilization');
            if (activePickers < zone.capacity.maxConcurrentPickers * 0.5)
                bottlenecks.push('Low picker utilization');
            if (averageProductivity < zone.capacity.maxTasksPerHour * 0.7)
                bottlenecks.push('Low productivity');
            return {
                zone,
                currentUtilization: utilization,
                activePickers,
                tasksInProgress: activeTasks.length,
                tasksCompleted: completedTasks.length,
                averageProductivity,
                bottlenecks
            };
        }
        /**
         * Optimize picking routes within zone
         */
        async optimizePickingRoute(tasks) {
            if (tasks.length <= 1)
                return tasks;
            // Simple nearest neighbor algorithm for route optimization
            const optimizedTasks = [];
            const remainingTasks = [...tasks];
            // Start from first task
            let currentTask = remainingTasks.shift();
            optimizedTasks.push(currentTask);
            while (remainingTasks.length > 0) {
                // Find nearest task
                let nearestIndex = 0;
                let nearestDistance = this.calculateDistance(currentTask.location, remainingTasks[0].location);
                for (let i = 1; i < remainingTasks.length; i++) {
                    const distance = this.calculateDistance(currentTask.location, remainingTasks[i].location);
                    if (distance < nearestDistance) {
                        nearestDistance = distance;
                        nearestIndex = i;
                    }
                }
                currentTask = remainingTasks.splice(nearestIndex, 1)[0];
                optimizedTasks.push(currentTask);
            }
            // Update sequence numbers
            optimizedTasks.forEach((task, index) => {
                task.sequence = index + 1;
            });
            return optimizedTasks;
        }
        /**
         * Create batch picking plan
         */
        async createBatchPickingPlan(orders) {
            const startTime = Date.now();
            try {
                // Analyze orders for batching opportunities
                const orderDetails = await this.getOrderDetails(orders);
                const batch = {
                    batchId: `batch_${Date.now()}`,
                    batchNumber: `B${Date.now()}`,
                    orders,
                    skus: this.consolidateSkusForBatching(orderDetails),
                    status: 'planned',
                    priority: this.calculateBatchPriority(orderDetails),
                    createdAt: new Date()
                };
                this.metrics.recordDatabaseQueryDuration('picking.batch_creation', (Date.now() - startTime) / 1000, {});
                return batch;
            }
            catch (error) {
                this.metrics.incrementErrorCount('picking.batch_creation_failed', { error: 'batch_creation_error' });
                throw error;
            }
        }
        // Private helper methods
        async createPickTasksFromOrders(orders, strategy, zone) {
            const tasks = [];
            for (const orderId of orders) {
                const orderLines = await this.getOrderLines(orderId);
                for (const line of orderLines) {
                    // Find available inventory
                    const inventory = await this.getAvailableInventory(line.sku, zone);
                    for (const inv of inventory) {
                        if (line.quantity <= 0)
                            break;
                        const pickQuantity = Math.min(line.quantity, inv.availableQty);
                        const task = {
                            taskId: `pick_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                            orderId,
                            sku: line.sku,
                            location: inv.location,
                            lot: inv.lot,
                            serial: inv.serial,
                            quantity: pickQuantity,
                            pickedQuantity: 0,
                            status: 'pending',
                            priority: line.priority || 5,
                            zone: zone || this.getZoneForLocation(inv.location),
                            sequence: 0, // Will be set during optimization
                            estimatedTime: this.estimatePickTime(pickQuantity, strategy),
                            createdAt: new Date()
                        };
                        tasks.push(task);
                        line.quantity -= pickQuantity;
                    }
                }
            }
            return tasks;
        }
        async groupTasksByStrategy(tasks, strategy) {
            switch (strategy) {
                case 'batch':
                    return this.optimizeForBatchPicking(tasks);
                case 'zone':
                    return this.optimizeForZonePicking(tasks);
                case 'cluster':
                    return await this.optimizeForClusterPicking(tasks);
                default:
                    return tasks.sort((a, b) => b.priority - a.priority);
            }
        }
        optimizeForBatchPicking(tasks) {
            // Group by SKU and location for batch picking
            const groupedTasks = [];
            const skuLocationMap = new Map();
            for (const task of tasks) {
                const key = `${task.sku}-${task.location}`;
                const existing = skuLocationMap.get(key);
                if (existing) {
                    existing.quantity += task.quantity;
                    // Combine orders (would need more complex logic in real implementation)
                }
                else {
                    skuLocationMap.set(key, { ...task });
                }
            }
            return Array.from(skuLocationMap.values());
        }
        optimizeForZonePicking(tasks) {
            // Sort by zone and then optimize routes within zones
            return tasks.sort((a, b) => {
                if (a.zone !== b.zone)
                    return a.zone.localeCompare(b.zone);
                return this.calculateDistance('START', a.location) - this.calculateDistance('START', b.location);
            });
        }
        async optimizeForClusterPicking(tasks) {
            // Group nearby locations for cluster picking
            return await this.optimizePickingRoute(tasks);
        }
        calculateWavePriority(tasks) {
            const avgPriority = tasks.reduce((sum, task) => sum + task.priority, 0) / tasks.length;
            return Math.round(avgPriority);
        }
        assignOptimalZone(tasks) {
            // Simple zone assignment based on majority
            const zoneCounts = new Map();
            for (const task of tasks) {
                zoneCounts.set(task.zone, (zoneCounts.get(task.zone) || 0) + 1);
            }
            let maxZone = 'DEFAULT';
            let maxCount = 0;
            for (const [zone, count] of Array.from(zoneCounts.entries())) {
                if (count > maxCount) {
                    maxCount = count;
                    maxZone = zone;
                }
            }
            return maxZone;
        }
        estimateWaveDuration(tasks, strategy) {
            const totalTime = tasks.reduce((sum, task) => sum + task.estimatedTime, 0);
            const strategyMultiplier = strategy === 'batch' ? 0.8 : strategy === 'zone' ? 0.9 : 1.0;
            return Math.ceil((totalTime * strategyMultiplier) / 60); // Convert to minutes
        }
        async assignPickersToWave(wave) {
            const zone = this.zones.get(wave.zone);
            if (!zone)
                return;
            // Simple assignment: assign to available pickers
            const availablePickers = zone.pickers.slice(0, Math.min(zone.capacity.maxConcurrentPickers, wave.tasks.length));
            wave.assignedPickers = availablePickers;
            // Assign tasks to pickers
            wave.tasks.forEach((task, index) => {
                task.assignedTo = availablePickers[index % availablePickers.length];
            });
        }
        estimatePickTime(quantity, strategy) {
            const baseTimePerUnit = 2; // seconds per unit
            const strategyMultiplier = strategy === 'batch' ? 1.2 : strategy === 'zone' ? 1.1 : 1.0;
            return Math.ceil(quantity * baseTimePerUnit * strategyMultiplier);
        }
        calculateDistance(from, to) {
            // Mock distance calculation - would use actual warehouse layout
            if (from === 'START' || to === 'START')
                return 0;
            // Simple mock: assume locations are A-01-01-01 format
            return Math.abs(this.locationToNumber(from) - this.locationToNumber(to));
        }
        locationToNumber(location) {
            // Convert location code to number for distance calculation
            const parts = location.split('-');
            if (parts.length >= 3) {
                return parseInt(parts[1]) * 10000 + parseInt(parts[2]) * 100 + parseInt(parts[3] || '0');
            }
            return 0;
        }
        async findPickTask(taskId) {
            // Search in all waves
            for (const wave of Array.from(this.activeWaves.values())) {
                const task = wave.tasks.find(t => t.taskId === taskId);
                if (task)
                    return task;
            }
            return null;
        }
        async updateWaveProgress(waveId) {
            const wave = this.activeWaves.get(waveId);
            if (!wave)
                return;
            wave.completedTasks = wave.tasks.filter(task => task.status === 'completed').length;
            wave.pickedQuantity = wave.tasks.reduce((sum, task) => sum + task.pickedQuantity, 0);
            if (wave.completedTasks === wave.totalTasks) {
                wave.status = 'completed';
                wave.completedAt = new Date();
                wave.actualDuration = wave.releasedAt ?
                    (wave.completedAt.getTime() - wave.releasedAt.getTime()) / (1000 * 60) : undefined;
                // Calculate productivity
                wave.productivity = await this.calculateWaveProductivity(wave);
                await this.publishWaveCompletedEvent(wave);
            }
        }
        async calculateWaveProductivity(wave) {
            if (!wave.actualDuration || wave.actualDuration === 0)
                return undefined;
            const totalPicks = wave.tasks.reduce((sum, task) => sum + task.pickedQuantity, 0);
            const totalLines = wave.tasks.length;
            const completedTasks = wave.tasks.filter(task => task.status === 'completed');
            const accuracy = completedTasks.length / wave.tasks.length;
            const picksPerHour = (totalPicks / wave.actualDuration) * 60;
            const linesPerHour = (totalLines / wave.actualDuration) * 60;
            const averageTimePerPick = wave.tasks
                .filter(task => task.actualTime)
                .reduce((sum, task) => sum + (task.actualTime || 0), 0) / completedTasks.length;
            return {
                picksPerHour,
                linesPerHour,
                accuracy,
                averageTimePerPick
            };
        }
        async updatePickerPerformance(pickerId, task) {
            // Mock implementation - would update persistent storage
            console.log(`Updated performance for picker ${pickerId}: task ${task.taskId}`);
        }
        async calculatePickerPerformance(pickerId, period) {
            // Mock implementation
            return {
                pickerId,
                name: `Picker ${pickerId}`,
                zone: 'A',
                shift: 'morning',
                metrics: {
                    totalPicks: 150,
                    totalLines: 45,
                    totalQuantity: 150,
                    picksPerHour: 75,
                    linesPerHour: 22.5,
                    accuracy: 98.5,
                    averageTimePerPick: 48, // seconds
                    totalTimeWorked: 120 // minutes
                },
                performance: {
                    score: 92,
                    grade: 'A',
                    trends: {
                        picksPerHour: [70, 72, 75, 78, 75],
                        accuracy: [97, 98, 98.5, 99, 98.5],
                        timePerPick: [52, 50, 48, 46, 48]
                    }
                },
                currentSession: {
                    startTime: new Date(),
                    tasksCompleted: 12,
                    totalPicks: 45,
                    errors: 0
                }
            };
        }
        async getActiveTasksInZone(zoneId) {
            const tasks = [];
            for (const wave of Array.from(this.activeWaves.values())) {
                if (wave.zone === zoneId) {
                    tasks.push(...wave.tasks.filter(task => task.status === 'in_progress'));
                }
            }
            return tasks;
        }
        async getCompletedTasksInZone(zoneId, since) {
            const tasks = [];
            for (const wave of Array.from(this.activeWaves.values())) {
                if (wave.zone === zoneId) {
                    tasks.push(...wave.tasks.filter(task => task.status === 'completed' &&
                        task.completedAt &&
                        task.completedAt >= since));
                }
            }
            return tasks;
        }
        getZoneForLocation(location) {
            // Mock zone assignment
            return location.startsWith('A') ? 'A' : 'B';
        }
        async getOrderLines(orderId) {
            // Mock order lines
            return [
                { sku: 'WIDGET-001', quantity: 5, priority: 5 },
                { sku: 'GADGET-002', quantity: 3, priority: 3 }
            ];
        }
        async getAvailableInventory(sku, zone) {
            // Mock inventory
            return [
                { location: 'A-01-01-01', availableQty: 50, lot: 'LOT-001' },
                { location: 'A-01-01-02', availableQty: 30, lot: 'LOT-002' }
            ].filter(inv => !zone || this.getZoneForLocation(inv.location) === zone);
        }
        async getOrderDetails(orders) {
            // Mock order details
            return orders.map(orderId => ({
                orderId,
                lines: [
                    { sku: 'WIDGET-001', quantity: 5 },
                    { sku: 'GADGET-002', quantity: 3 }
                ]
            }));
        }
        consolidateSkusForBatching(orderDetails) {
            const skuMap = new Map();
            for (const order of orderDetails) {
                for (const line of order.lines) {
                    const existing = skuMap.get(line.sku) || {
                        totalQuantity: 0,
                        locations: []
                    };
                    existing.totalQuantity += line.quantity;
                    // Add location logic here
                    existing.locations.push({
                        location: 'A-01-01-01',
                        quantity: line.quantity,
                        lot: 'LOT-001'
                    });
                    skuMap.set(line.sku, existing);
                }
            }
            return Array.from(skuMap.entries()).map(([sku, data]) => ({ sku, ...data }));
        }
        calculateBatchPriority(orderDetails) {
            // Calculate based on order priorities
            return 5; // Mock
        }
        initializeDefaultZones() {
            const zones = [
                {
                    zoneId: 'A',
                    zoneName: 'Forward Zone A',
                    type: 'forward',
                    pickers: ['picker1', 'picker2', 'picker3'],
                    locations: ['A-01-01-01', 'A-01-01-02', 'A-01-02-01'],
                    capacity: {
                        maxConcurrentPickers: 3,
                        maxTasksPerHour: 120
                    },
                    routing: {
                        entryPoint: 'A-ENTRY',
                        exitPoint: 'A-EXIT',
                        optimalPath: ['A-01-01-01', 'A-01-01-02', 'A-01-02-01']
                    },
                    active: true
                },
                {
                    zoneId: 'B',
                    zoneName: 'Reserve Zone B',
                    type: 'reserve',
                    pickers: ['picker4', 'picker5'],
                    locations: ['B-01-01-01', 'B-01-01-02', 'B-02-01-01'],
                    capacity: {
                        maxConcurrentPickers: 2,
                        maxTasksPerHour: 80
                    },
                    routing: {
                        entryPoint: 'B-ENTRY',
                        exitPoint: 'B-EXIT',
                        optimalPath: ['B-01-01-01', 'B-01-01-02', 'B-02-01-01']
                    },
                    active: true
                }
            ];
            zones.forEach(zone => this.zones.set(zone.zoneId, zone));
        }
        // Event publishing methods
        async publishWaveCreatedEvent(wave) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.wave.created',
                aggregateId: wave.waveId,
                aggregateType: 'PickingWave',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                type: 'inventory.wave.created',
                occurredAt: new Date(),
                aggregateVersion: 1,
                waveId: wave.waveId,
                waveNumber: wave.waveNumber,
                strategy: wave.strategy,
                totalTasks: wave.totalTasks,
                totalQuantity: wave.totalQuantity,
                zone: wave.zone
            };
            await this.eventBus.publish(event);
        }
        async publishPickTaskCreatedEvent(task) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.pick.created',
                type: 'inventory.pick.created',
                aggregateId: task.taskId,
                aggregateType: 'PickTask',
                eventVersion: 1,
                occurredOn: new Date(),
                occurredAt: new Date(),
                aggregateVersion: 1,
                tenantId: 'default',
                orderId: task.orderId,
                waveId: task.waveId,
                tasks: [{
                        taskId: task.taskId,
                        sku: task.sku,
                        location: task.location,
                        lot: task.lot,
                        serial: task.serial,
                        quantity: task.quantity,
                        priority: task.priority
                    }]
            };
            await this.eventBus.publish(event);
        }
        async publishPickCompletedEvent(task) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.pick.completed',
                aggregateId: task.taskId,
                aggregateType: 'PickTask',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                type: 'inventory.pick.completed',
                occurredAt: new Date(),
                aggregateVersion: 1,
                taskId: task.taskId,
                orderId: task.orderId,
                sku: task.sku,
                quantity: task.pickedQuantity,
                pickedBy: task.assignedTo || 'unknown',
                duration: task.actualTime || 0,
                accuracy: task.pickedQuantity >= task.quantity ? 100 : (task.pickedQuantity / task.quantity) * 100
            };
            await this.eventBus.publish(event);
        }
        async publishWaveCompletedEvent(wave) {
            const event = {
                eventId: `evt_${Date.now()}`,
                eventType: 'inventory.wave.completed',
                aggregateId: wave.waveId,
                aggregateType: 'PickingWave',
                eventVersion: 1,
                occurredOn: new Date(),
                tenantId: 'default',
                type: 'inventory.wave.completed',
                occurredAt: new Date(),
                aggregateVersion: 1,
                waveId: wave.waveId,
                completedTasks: wave.completedTasks,
                totalTasks: wave.totalTasks,
                duration: wave.actualDuration || 0,
                productivity: wave.productivity?.picksPerHour || 0
            };
            await this.eventBus.publish(event);
        }
    };
    return PickingService = _classThis;
})();
exports.PickingService = PickingService;
