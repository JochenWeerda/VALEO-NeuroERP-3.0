"use strict";
/**
 * VALEO NeuroERP 3.0 - Inventory Backend for Frontend (BFF)
 *
 * Conversational AI interface for warehouse operations
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
exports.InventoryBFF = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("../infrastructure/observability/metrics-service");
let InventoryBFF = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var InventoryBFF = _classThis = class {
        constructor(receivingService, putawaySlottingService, inventoryControlService, replenishmentService, pickingService, packingShippingService, cycleCountingService, returnsDispositionService, wcsWesAdapterService, traceabilityService) {
            this.receivingService = receivingService;
            this.putawaySlottingService = putawaySlottingService;
            this.inventoryControlService = inventoryControlService;
            this.replenishmentService = replenishmentService;
            this.pickingService = pickingService;
            this.packingShippingService = packingShippingService;
            this.cycleCountingService = cycleCountingService;
            this.returnsDispositionService = returnsDispositionService;
            this.wcsWesAdapterService = wcsWesAdapterService;
            this.traceabilityService = traceabilityService;
            this.metrics = new metrics_service_1.InventoryMetricsService();
            this.conversations = new Map();
        }
        /**
         * Process natural language query
         */
        async processQuery(sessionId, userId, query) {
            const startTime = Date.now();
            try {
                // Get or create conversation context
                let context = this.conversations.get(sessionId);
                if (!context) {
                    context = this.createConversationContext(sessionId, userId);
                    this.conversations.set(sessionId, context);
                }
                // Add user message to history
                context.conversationHistory.push({
                    role: 'user',
                    message: query,
                    timestamp: new Date()
                });
                // Analyze intent and entities
                const intent = await this.analyzeIntent(query, context);
                // Update context
                context.currentIntent = intent.intent;
                context.entities = { ...context.entities, ...intent.entities };
                // Add assistant response to history
                context.conversationHistory.push({
                    role: 'assistant',
                    message: typeof intent.response.content === 'string' ? intent.response.content : JSON.stringify(intent.response.content),
                    timestamp: new Date(),
                    intent: intent.intent,
                    entities: intent.entities
                });
                // Execute any actions
                if (intent.response.actions) {
                    await this.executeActions(intent.response.actions, context);
                }
                this.metrics.recordDatabaseQueryDuration('inventory_bff', 'query_processing', (Date.now() - startTime) / 1000);
                return intent;
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory_bff', 'query_processing_failed');
                throw error;
            }
        }
        /**
         * Get inventory dashboard data
         */
        async getDashboardData(userId, filters) {
            const startTime = Date.now();
            try {
                // Get overview data
                const overview = await this.getOverviewData(filters);
                // Get alerts
                const alerts = await this.getActiveAlerts(userId);
                // Get recent activity
                const recentActivity = await this.getRecentActivity(filters);
                // Get performance metrics
                const performance = await this.getPerformanceMetrics(filters);
                this.metrics.recordDatabaseQueryDuration('inventory_bff', 'dashboard_data', (Date.now() - startTime) / 1000);
                return {
                    overview,
                    alerts,
                    recentActivity,
                    performance
                };
            }
            catch (error) {
                this.metrics.incrementErrorCount('inventory_bff', 'dashboard_failed');
                throw error;
            }
        }
        /**
         * Execute workflow step
         */
        async executeWorkflowStep(sessionId, stepData) {
            const context = this.conversations.get(sessionId);
            if (!context?.activeWorkflow) {
                throw new Error('No active workflow');
            }
            const workflow = context.activeWorkflow;
            workflow.data = { ...workflow.data, ...stepData };
            // Execute current step
            const result = await this.executeWorkflowStepLogic(workflow, stepData);
            if (result.completed) {
                workflow.step++;
                if (workflow.step >= workflow.totalSteps) {
                    // Workflow completed
                    context.activeWorkflow = undefined;
                    return {
                        completed: true,
                        result: result.data,
                        message: 'Workflow completed successfully'
                    };
                }
                else {
                    // Next step
                    return {
                        completed: false,
                        nextStep: workflow.step,
                        message: `Step ${workflow.step} completed. Proceeding to next step.`
                    };
                }
            }
            else {
                return {
                    completed: false,
                    message: result.message || 'Step execution failed'
                };
            }
        }
        /**
         * Get conversation history
         */
        getConversationHistory(sessionId) {
            const context = this.conversations.get(sessionId);
            return context?.conversationHistory || [];
        }
        /**
         * Clear conversation context
         */
        clearConversation(sessionId) {
            this.conversations.delete(sessionId);
        }
        // Private helper methods
        createConversationContext(sessionId, userId) {
            return {
                sessionId,
                userId,
                entities: {},
                conversationHistory: [],
                preferences: {
                    language: 'en',
                    units: 'metric',
                    timezone: 'UTC',
                    notifications: true
                }
            };
        }
        async analyzeIntent(query, context) {
            const lowerQuery = query.toLowerCase();
            // Simple rule-based intent recognition (in production, use NLP model)
            if (lowerQuery.includes('inventory') && lowerQuery.includes('status')) {
                return await this.handleInventoryStatusQuery(context);
            }
            if (lowerQuery.includes('pick') || lowerQuery.includes('picking')) {
                return await this.handlePickingQuery(query, context);
            }
            if (lowerQuery.includes('receive') || lowerQuery.includes('receiving')) {
                return await this.handleReceivingQuery(query, context);
            }
            if (lowerQuery.includes('location') || lowerQuery.includes('where')) {
                return await this.handleLocationQuery(query, context);
            }
            if (lowerQuery.includes('forecast') || lowerQuery.includes('predict')) {
                return await this.handleForecastQuery(query, context);
            }
            if (lowerQuery.includes('trace') || lowerQuery.includes('track')) {
                return await this.handleTraceabilityQuery(query, context);
            }
            if (lowerQuery.includes('count') || lowerQuery.includes('cycle')) {
                return await this.handleCycleCountQuery(query, context);
            }
            if (lowerQuery.includes('report') || lowerQuery.includes('analytics')) {
                return await this.handleAnalyticsQuery(context);
            }
            // Default response
            return {
                intent: 'unknown',
                confidence: 0.5,
                entities: {},
                response: {
                    type: 'text',
                    content: "I'm sorry, I didn't understand that request. Try asking about inventory status, picking, receiving, locations, forecasts, or analytics."
                },
                followUp: {
                    question: "What would you like to know about the warehouse?",
                    suggestions: [
                        "What's the current inventory status?",
                        "Show me picking tasks",
                        "Where is item XYZ located?",
                        "Generate a forecast report",
                        "Show analytics dashboard"
                    ]
                }
            };
        }
        async handleInventoryStatusQuery(context) {
            const dashboard = await this.getDashboardData(context.userId);
            return {
                intent: 'inventory_status',
                confidence: 0.9,
                entities: {},
                response: {
                    type: 'card',
                    content: {
                        title: 'Inventory Overview',
                        sections: [
                            {
                                title: 'Summary',
                                items: [
                                    `Total Items: ${dashboard.overview.totalItems.toLocaleString()}`,
                                    `Total Value: €${dashboard.overview.totalValue.toLocaleString()}`,
                                    `Low Stock Items: ${dashboard.overview.lowStockItems}`,
                                    `Expiring Items: ${dashboard.overview.expiringItems}`
                                ]
                            },
                            {
                                title: 'Performance',
                                items: [
                                    `Receiving Accuracy: ${dashboard.performance.receivingAccuracy}%`,
                                    `Picking Accuracy: ${dashboard.performance.pickingAccuracy}%`,
                                    `Inventory Accuracy: ${dashboard.performance.inventoryAccuracy}%`,
                                    `Daily Throughput: ${dashboard.performance.throughput} items`
                                ]
                            }
                        ]
                    },
                    actions: [
                        {
                            type: 'button',
                            label: 'View Details',
                            value: 'show_inventory_details',
                            style: 'primary'
                        },
                        {
                            type: 'button',
                            label: 'Generate Report',
                            value: 'generate_inventory_report',
                            style: 'secondary'
                        }
                    ]
                }
            };
        }
        async handlePickingQuery(query, context) {
            // Extract entities from query
            const entities = this.extractEntities(query);
            const tasks = await this.pickingService.getActiveTasks();
            const filteredTasks = tasks.filter(task => !entities.sku || task.items.some(item => item.sku === entities.sku));
            return {
                intent: 'picking_query',
                confidence: 0.85,
                entities,
                response: {
                    type: 'table',
                    content: {
                        title: 'Active Picking Tasks',
                        headers: ['Task ID', 'Priority', 'Items', 'Status', 'Assigned To'],
                        rows: filteredTasks.slice(0, 10).map(task => [
                            task.taskId,
                            task.priority,
                            task.items.length,
                            task.status,
                            task.assignedTo || 'Unassigned'
                        ]),
                        totalRows: filteredTasks.length
                    },
                    actions: [
                        {
                            type: 'button',
                            label: 'Create New Task',
                            value: 'create_picking_task',
                            style: 'primary'
                        },
                        {
                            type: 'button',
                            label: 'View All Tasks',
                            value: 'view_all_picking_tasks',
                            style: 'secondary'
                        }
                    ]
                }
            };
        }
        async handleReceivingQuery(query, context) {
            const entities = this.extractEntities(query);
            // Start receiving workflow
            context.activeWorkflow = {
                workflowId: 'receiving_workflow',
                step: 1,
                totalSteps: 3,
                data: { ...entities }
            };
            return {
                intent: 'receiving_assistance',
                confidence: 0.9,
                entities,
                response: {
                    type: 'text',
                    content: "I'll help you with receiving. Please provide the ASN number or purchase order number."
                },
                followUp: {
                    question: "What's the ASN or PO number?",
                    suggestions: []
                }
            };
        }
        async handleLocationQuery(query, context) {
            const entities = this.extractEntities(query);
            if (!entities.sku) {
                return {
                    intent: 'location_query_incomplete',
                    confidence: 0.7,
                    entities,
                    response: {
                        type: 'text',
                        content: "I need to know which item you're looking for. Please specify the SKU."
                    },
                    followUp: {
                        question: "What's the SKU of the item?",
                        suggestions: []
                    }
                };
            }
            const locations = await this.inventoryControlService.findItemLocations(entities.sku);
            return {
                intent: 'location_query',
                confidence: 0.9,
                entities,
                response: {
                    type: 'table',
                    content: {
                        title: `Locations for ${entities.sku}`,
                        headers: ['Location', 'Quantity', 'Lot', 'Serial', 'Last Updated'],
                        rows: locations.map(loc => [
                            loc.location,
                            loc.quantity,
                            loc.lot || 'N/A',
                            loc.serial || 'N/A',
                            loc.lastUpdated.toLocaleDateString()
                        ])
                    }
                }
            };
        }
        async handleForecastQuery(query, context) {
            const entities = this.extractEntities(query);
            if (!entities.sku) {
                return {
                    intent: 'forecast_query_incomplete',
                    confidence: 0.7,
                    entities,
                    response: {
                        type: 'text',
                        content: "I'll generate a forecast. Which item would you like to forecast?"
                    },
                    followUp: {
                        question: "What's the SKU for the forecast?",
                        suggestions: []
                    }
                };
            }
            const forecast = await this.wcsWesAdapterService.generateInventoryForecast(entities.sku, 'demand', {
                start: new Date(),
                end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
                granularity: 'day'
            });
            return {
                intent: 'forecast_generated',
                confidence: 0.9,
                entities,
                response: {
                    type: 'chart',
                    content: {
                        title: `Demand Forecast for ${entities.sku}`,
                        type: 'line',
                        data: {
                            labels: forecast.forecast.map(f => f.timestamp.toLocaleDateString()),
                            datasets: [{
                                    label: 'Predicted Demand',
                                    data: forecast.forecast.map(f => f.predictedValue),
                                    borderColor: 'rgb(75, 192, 192)',
                                    tension: 0.1
                                }]
                        }
                    }
                }
            };
        }
        async handleTraceabilityQuery(query, context) {
            const entities = this.extractEntities(query);
            if (!entities.epc && !entities.sku) {
                return {
                    intent: 'traceability_query_incomplete',
                    confidence: 0.7,
                    entities,
                    response: {
                        type: 'text',
                        content: "I can help you trace products. Please provide an EPC or SKU."
                    },
                    followUp: {
                        question: "What's the EPC or SKU to trace?",
                        suggestions: []
                    }
                };
            }
            const genealogy = await this.traceabilityService.getProductGenealogy(entities.epc || entities.sku);
            return {
                intent: 'traceability_result',
                confidence: 0.9,
                entities,
                response: {
                    type: 'card',
                    content: {
                        title: `Product Genealogy for ${entities.epc || entities.sku}`,
                        sections: [
                            {
                                title: 'Parents',
                                items: genealogy.parents.length > 0 ? genealogy.parents : ['None']
                            },
                            {
                                title: 'Children',
                                items: genealogy.children.length > 0 ? genealogy.children : ['None']
                            },
                            {
                                title: 'Transformations',
                                items: genealogy.transformations.map(t => `${t.type} at ${t.performedAt.toLocaleDateString()}`)
                            }
                        ]
                    }
                }
            };
        }
        async handleCycleCountQuery(query, context) {
            const performance = await this.cycleCountingService.getCycleCountPerformance('month');
            return {
                intent: 'cycle_count_status',
                confidence: 0.85,
                entities: {},
                response: {
                    type: 'card',
                    content: {
                        title: 'Cycle Count Performance',
                        sections: [
                            {
                                title: 'Current Month',
                                items: [
                                    `Total Counts: ${performance.metrics.totalCounts}`,
                                    `Accuracy: ${performance.metrics.accuracy.toFixed(1)}%`,
                                    `Average Variance: ${performance.metrics.averageVariance.toFixed(2)}%`,
                                    `Items/Hour: ${performance.metrics.itemsPerHour.toFixed(1)}`
                                ]
                            }
                        ]
                    },
                    actions: [
                        {
                            type: 'button',
                            label: 'Start New Count',
                            value: 'start_cycle_count',
                            style: 'primary'
                        },
                        {
                            type: 'button',
                            label: 'View Details',
                            value: 'view_cycle_count_details',
                            style: 'secondary'
                        }
                    ]
                }
            };
        }
        async handleAnalyticsQuery(context) {
            const dashboard = await this.getDashboardData(context.userId);
            return {
                intent: 'analytics_dashboard',
                confidence: 0.9,
                entities: {},
                response: {
                    type: 'chart',
                    content: {
                        title: 'Warehouse Performance Analytics',
                        type: 'bar',
                        data: {
                            labels: ['Receiving', 'Picking', 'Inventory', 'Shipping'],
                            datasets: [{
                                    label: 'Accuracy %',
                                    data: [
                                        dashboard.performance.receivingAccuracy,
                                        dashboard.performance.pickingAccuracy,
                                        dashboard.performance.inventoryAccuracy,
                                        98.5 // Shipping accuracy
                                    ],
                                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                                    borderColor: 'rgba(54, 162, 235, 1)',
                                    borderWidth: 1
                                }]
                        }
                    }
                }
            };
        }
        extractEntities(query) {
            const entities = {};
            // Simple entity extraction (in production, use NLP)
            const skuMatch = query.match(/sku\s*[\w-]+/i);
            if (skuMatch) {
                entities.sku = skuMatch[0].replace(/sku\s*/i, '');
            }
            const epcMatch = query.match(/epc\s*[\w-]+/i);
            if (epcMatch) {
                entities.epc = epcMatch[0].replace(/epc\s*/i, '');
            }
            const locationMatch = query.match(/location\s*[\w-]+/i);
            if (locationMatch) {
                entities.location = locationMatch[0].replace(/location\s*/i, '');
            }
            return entities;
        }
        async executeActions(actions, context) {
            for (const action of actions || []) {
                switch (action.value) {
                    case 'show_inventory_details':
                        // Trigger detailed inventory view
                        break;
                    case 'generate_inventory_report':
                        // Generate and send report
                        break;
                    case 'create_picking_task':
                        // Start picking task creation workflow
                        break;
                    case 'start_cycle_count':
                        // Start cycle count workflow
                        break;
                    // Add more actions as needed
                }
            }
        }
        async executeWorkflowStepLogic(workflow, stepData) {
            switch (workflow.workflowId) {
                case 'receiving_workflow':
                    return await this.executeReceivingWorkflowStep(workflow, stepData);
                default:
                    return { completed: false, message: 'Unknown workflow' };
            }
        }
        async executeReceivingWorkflowStep(workflow, stepData) {
            switch (workflow.step) {
                case 1:
                    // Validate ASN/PO
                    const asnData = await this.receivingService.validateASN(stepData.asnNumber);
                    workflow.data.asnData = asnData;
                    return { completed: true, message: 'ASN validated successfully' };
                case 2:
                    // Process receiving
                    const receivingResult = await this.receivingService.processASN(stepData.asnNumber, stepData.receivedItems);
                    workflow.data.receivingResult = receivingResult;
                    return { completed: true, message: 'Items received successfully' };
                case 3:
                    // Generate putaway tasks
                    const putawayTasks = await this.putawaySlottingService.createPutawayTasks(stepData.asnNumber);
                    workflow.data.putawayTasks = putawayTasks;
                    return { completed: true, data: putawayTasks, message: 'Putaway tasks created' };
                default:
                    return { completed: false, message: 'Invalid step' };
            }
        }
        async getOverviewData(filters) {
            // Mock data - would aggregate from actual services
            return {
                totalItems: 125000,
                totalValue: 2500000,
                lowStockItems: 1250,
                expiringItems: 340,
                activeTasks: 45
            };
        }
        async getActiveAlerts(userId) {
            // Mock alerts
            return [
                {
                    type: 'warning',
                    title: 'Low Stock Alert',
                    message: 'Item WIDGET-001 is below minimum stock level',
                    action: 'replenish'
                },
                {
                    type: 'info',
                    title: 'Receiving Due',
                    message: 'ASN-2024-001 is expected today',
                    action: 'prepare_receiving'
                }
            ];
        }
        async getRecentActivity(filters) {
            // Mock activity
            return [
                {
                    type: 'receiving',
                    description: 'ASN-2024-001 received with 500 items',
                    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
                    user: 'john.doe'
                },
                {
                    type: 'picking',
                    description: 'Order ORD-2024-001 picked and packed',
                    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
                    user: 'jane.smith'
                }
            ];
        }
        async getPerformanceMetrics(filters) {
            return {
                receivingAccuracy: 98.5,
                pickingAccuracy: 97.2,
                inventoryAccuracy: 99.1,
                throughput: 1250
            };
        }
    };
    __setFunctionName(_classThis, "InventoryBFF");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        InventoryBFF = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return InventoryBFF = _classThis;
})();
exports.InventoryBFF = InventoryBFF;
//# sourceMappingURL=inventory-bff.js.map