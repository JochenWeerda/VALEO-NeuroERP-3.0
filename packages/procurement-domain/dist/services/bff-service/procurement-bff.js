"use strict";
/**
 * VALEO NeuroERP 3.0 - Procurement BFF Service
 *
 * Backend for Frontend (BFF) service providing:
 * - Aggregated dashboard data from all procurement services
 * - Conversational AI for procurement tasks
 * - Unified API for frontend applications
 * - Real-time notifications and workflow orchestration
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProcurementBFFService = void 0;
const express_1 = __importDefault(require("express"));
// import cors from 'cors';
const helmet_1 = __importDefault(require("helmet"));
const inversify_1 = require("inversify");
let ProcurementBFFService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var ProcurementBFFService = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            ProcurementBFFService = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        app;
        port;
        constructor() {
            this.app = (0, express_1.default)();
            this.port = parseInt(process.env.PROCUREMENT_BFF_PORT || '3003');
            this.setupMiddleware();
            this.setupRoutes();
        }
        setupMiddleware() {
            this.app.use((0, helmet_1.default)());
            // this.app.use(cors());
            this.app.use(express_1.default.json({ limit: '10mb' }));
            this.app.use(express_1.default.urlencoded({ extended: true }));
            // Request logging
            this.app.use((req, res, next) => {
                console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
                next();
            });
        }
        setupRoutes() {
            // Health check
            this.app.get('/health', (req, res) => {
                res.json({
                    status: 'healthy',
                    service: 'procurement-bff',
                    timestamp: new Date().toISOString(),
                    version: '3.0.0'
                });
            });
            // Dashboard data aggregation
            this.app.get('/api/dashboard', this.handleDashboard.bind(this));
            // Conversational AI
            this.app.post('/api/chat', this.handleChat.bind(this));
            // Unified search
            this.app.get('/api/search', this.handleSearch.bind(this));
            // Workflow orchestration
            this.app.post('/api/workflows/requisition-to-po', this.handleRequisitionToPO.bind(this));
            // Real-time notifications
            this.app.get('/api/notifications', this.handleNotifications.bind(this));
            // Bulk operations
            this.app.post('/api/bulk/approve-requisitions', this.handleBulkApprove.bind(this));
            // Analytics & reporting
            this.app.get('/api/analytics/spend', this.handleSpendAnalytics.bind(this));
        }
        // ===== DASHBOARD ENDPOINTS =====
        async handleDashboard(req, res) {
            try {
                const dashboardData = {
                    overview: {
                        totalSpend: 2500000,
                        activePOs: 45,
                        pendingRequisitions: 12,
                        supplierCount: 89,
                        contractCount: 67,
                        riskAlerts: 3
                    },
                    spendAnalytics: {
                        byCategory: [
                            { category: 'IT Hardware', amount: 850000, percentage: 34 },
                            { category: 'Professional Services', amount: 620000, percentage: 25 },
                            { category: 'Office Supplies', amount: 380000, percentage: 15 },
                            { category: 'Facilities', amount: 350000, percentage: 14 },
                            { category: 'Other', amount: 300000, percentage: 12 }
                        ],
                        bySupplier: [
                            { supplier: 'Dell Technologies', amount: 450000, percentage: 18 },
                            { supplier: 'Microsoft', amount: 380000, percentage: 15 },
                            { supplier: 'SAP', amount: 320000, percentage: 13 },
                            { supplier: 'Accenture', amount: 280000, percentage: 11 },
                            { supplier: 'AWS', amount: 250000, percentage: 10 }
                        ]
                    },
                    alerts: [
                        {
                            id: 'alert_1',
                            type: 'error',
                            title: 'High-Risk Supplier',
                            message: 'Supplier ABC Corp has critical risk score',
                            priority: 'critical'
                        },
                        {
                            id: 'alert_2',
                            type: 'warning',
                            title: 'Contract Expiring',
                            message: 'IT Services contract expires in 30 days',
                            priority: 'high'
                        },
                        {
                            id: 'alert_3',
                            type: 'info',
                            title: 'New Recommendations Available',
                            message: 'AI has generated 5 new procurement recommendations',
                            priority: 'medium'
                        }
                    ],
                    recommendations: [
                        {
                            id: 'rec_1',
                            type: 'supplier',
                            title: 'Consolidate IT Suppliers',
                            description: 'Reduce from 12 to 8 IT suppliers to improve negotiation leverage',
                            impact: '€150,000 annual savings',
                            confidence: 85
                        },
                        {
                            id: 'rec_2',
                            type: 'contract',
                            title: 'Renew Facilities Contract',
                            description: 'Current contract expires in 45 days with favorable terms',
                            impact: '€75,000 cost avoidance',
                            confidence: 92
                        },
                        {
                            id: 'rec_3',
                            type: 'spend',
                            title: 'Optimize Office Supplies',
                            description: 'Switch to preferred supplier for 20% cost reduction',
                            impact: '€45,000 annual savings',
                            confidence: 78
                        }
                    ]
                };
                res.json(dashboardData);
            }
            catch (error) {
                console.error('Dashboard error:', error);
                res.status(500).json({ error: 'Failed to load dashboard' });
            }
        }
        // ===== CONVERSATIONAL AI ENDPOINTS =====
        async handleChat(req, res) {
            try {
                const request = req.body;
                const response = {
                    response: `I understand you want to: "${request.message}". How can I help you with your procurement needs?`,
                    actions: [
                        {
                            type: 'create_requisition',
                            label: 'Create New Requisition',
                            data: { department: request.context?.department },
                            confidence: 0.8
                        },
                        {
                            type: 'search_suppliers',
                            label: 'Find Suppliers',
                            data: { query: request.message },
                            confidence: 0.7
                        },
                        {
                            type: 'view_reports',
                            label: 'View Reports',
                            data: { type: 'spend' },
                            confidence: 0.6
                        }
                    ],
                    suggestions: [
                        'Create a purchase requisition',
                        'Search for suppliers',
                        'Check approval status',
                        'Generate spend report'
                    ],
                    sessionId: `session_${Date.now()}`
                };
                res.json(response);
            }
            catch (error) {
                console.error('Chat error:', error);
                res.status(500).json({ error: 'Chat processing failed' });
            }
        }
        // ===== OTHER ENDPOINTS =====
        async handleSearch(req, res) {
            try {
                const results = {
                    suppliers: [
                        { id: 'sup_1', name: 'Dell Technologies', category: 'IT Hardware' },
                        { id: 'sup_2', name: 'Microsoft', category: 'Software' }
                    ],
                    products: [
                        { id: 'prod_1', name: 'Dell XPS 15', category: 'Laptop' },
                        { id: 'prod_2', name: 'Office 365 License', category: 'Software' }
                    ],
                    contracts: [
                        { id: 'cont_1', title: 'IT Hardware Supply Agreement', supplier: 'Dell Technologies' }
                    ]
                };
                res.json(results);
            }
            catch (error) {
                console.error('Search error:', error);
                res.status(500).json({ error: 'Search failed' });
            }
        }
        async handleRequisitionToPO(req, res) {
            try {
                const { requisitionId } = req.body;
                const result = {
                    requisitionId,
                    poId: `PO_${Date.now()}`,
                    status: 'completed',
                    message: 'Requisition successfully converted to Purchase Order',
                    nextSteps: ['Monitor delivery', 'Process goods receipt']
                };
                res.json(result);
            }
            catch (error) {
                console.error('Workflow error:', error);
                res.status(500).json({ error: 'Workflow orchestration failed' });
            }
        }
        async handleNotifications(req, res) {
            try {
                const notifications = [
                    {
                        id: 'notif_1',
                        type: 'approval',
                        title: 'Requisition Approved',
                        message: 'Your IT hardware requisition has been approved',
                        timestamp: new Date(),
                        read: false
                    },
                    {
                        id: 'notif_2',
                        type: 'alert',
                        title: 'Contract Expiring',
                        message: 'Office supplies contract expires in 15 days',
                        timestamp: new Date(),
                        read: false
                    }
                ];
                res.json(notifications);
            }
            catch (error) {
                console.error('Notifications error:', error);
                res.status(500).json({ error: 'Failed to fetch notifications' });
            }
        }
        async handleBulkApprove(req, res) {
            try {
                const { requisitionIds } = req.body;
                const results = requisitionIds.map((id) => ({
                    requisitionId: id,
                    status: 'approved',
                    approvedBy: 'system',
                    timestamp: new Date()
                }));
                res.json({
                    results,
                    summary: `${results.length} requisitions approved successfully`
                });
            }
            catch (error) {
                console.error('Bulk approve error:', error);
                res.status(500).json({ error: 'Bulk approval failed' });
            }
        }
        async handleSpendAnalytics(req, res) {
            try {
                const analytics = {
                    totalSpend: 2500000,
                    period: '2024',
                    byCategory: [
                        { category: 'IT Hardware', amount: 850000, change: 5.2 },
                        { category: 'Professional Services', amount: 620000, change: -2.1 },
                        { category: 'Office Supplies', amount: 380000, change: 8.7 }
                    ],
                    bySupplier: [
                        { supplier: 'Dell Technologies', amount: 450000, change: 12.3 },
                        { supplier: 'Microsoft', amount: 380000, change: -5.4 }
                    ],
                    trends: [
                        { month: 'Jan', spend: 180000 },
                        { month: 'Feb', spend: 195000 },
                        { month: 'Mar', spend: 210000 }
                    ]
                };
                res.json(analytics);
            }
            catch (error) {
                console.error('Analytics error:', error);
                res.status(500).json({ error: 'Failed to fetch analytics' });
            }
        }
        // ===== LIFECYCLE METHODS =====
        async start() {
            return new Promise((resolve) => {
                this.app.listen(this.port, () => {
                    console.log(`[PROCUREMENT BFF] 🚀 Procurement BFF running on port ${this.port}`);
                    console.log(`[PROCUREMENT BFF] Environment: ${process.env.NODE_ENV || 'development'}`);
                    console.log(`[PROCUREMENT BFF] Health check: http://localhost:${this.port}/health`);
                    resolve();
                });
            });
        }
        async stop() {
            console.log('[PROCUREMENT BFF] Shutting down Procurement BFF...');
            console.log('[PROCUREMENT BFF] ✅ Shutdown complete');
        }
        getApp() {
            return this.app;
        }
    };
    return ProcurementBFFService = _classThis;
})();
exports.ProcurementBFFService = ProcurementBFFService;
//# sourceMappingURL=procurement-bff.js.map