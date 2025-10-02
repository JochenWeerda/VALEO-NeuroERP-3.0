"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.analyticsDomainService = exports.AnalyticsDomainService = void 0;
// domains/analytics/src/services/analytics-domain-service.ts
const base_service_1 = require("@packages/utilities/base-service");
const business_logic_orchestrator_1 = require("@packages/business-rules/business-logic-orchestrator");
class AnalyticsDomainService extends base_service_1.BaseService {
    constructor() {
        super();
        this.initializeBusinessRules();
    }
    initializeBusinessRules() {
        // Register Analytics business rules
        business_logic_orchestrator_1.businessLogicOrchestrator.registerRule('Analytics', new ReportValidationRule());
        business_logic_orchestrator_1.businessLogicOrchestrator.registerRule('Analytics', new DashboardValidationRule());
    }
    // Metric Management
    async recordMetric(metricData) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'create',
            domain: 'Analytics',
            metadata: { source: 'analytics-service' }
        };
        // Execute business logic
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Analytics', metricData, 'create', context);
        if (!result.success) {
            throw new Error(`Metric recording failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        // Create metric entity
        const metric = {
            id: this.generateMetricId(),
            ...result.data,
            timestamp: new Date()
        };
        // Save to repository
        await this.repository.create(metric);
        // Publish domain event
        await this.publishDomainEvent('MetricRecorded', {
            metricId: metric.id,
            metricName: metric.name,
            metricValue: metric.value,
            timestamp: new Date()
        });
        return metric;
    }
    async getMetrics(filters) {
        return this.repository.find(filters);
    }
    async getMetricStatistics() {
        const allMetrics = await this.repository.findAll();
        const metricsByCategory = allMetrics.reduce((acc, metric) => {
            acc[metric.category] = (acc[metric.category] || 0) + 1;
            return acc;
        }, {});
        const metricsByType = allMetrics.reduce((acc, metric) => {
            acc[metric.type] = (acc[metric.type] || 0) + 1;
            return acc;
        }, {});
        const averageValue = allMetrics.length > 0
            ? allMetrics.reduce((sum, metric) => sum + metric.value, 0) / allMetrics.length
            : 0;
        const latestMetric = allMetrics.length > 0
            ? new Date(Math.max(...allMetrics.map(m => m.timestamp.getTime())))
            : new Date();
        return {
            totalMetrics: allMetrics.length,
            metricsByCategory,
            metricsByType,
            averageValue,
            latestMetric
        };
    }
    // Report Management
    async generateReport(request) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'create',
            domain: 'Analytics',
            metadata: { source: 'analytics-service' }
        };
        // Execute business logic
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Analytics', request, 'create', context);
        if (!result.success) {
            throw new Error(`Report generation failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        // Create report entity
        const report = {
            id: this.generateReportId(),
            ...result.data,
            generatedAt: new Date(),
            generatedBy: this.getCurrentUserId(),
            status: 'generating'
        };
        // Save to repository
        await this.repository.create(report);
        // Generate report data asynchronously
        this.generateReportData(report).catch(error => {
            console.error(`Failed to generate report data for ${report.id}:`, error);
            this.updateReportStatus(report.id, 'failed');
        });
        // Publish domain event
        await this.publishDomainEvent('ReportGenerated', {
            reportId: report.id,
            reportName: report.name,
            reportType: report.type,
            timestamp: new Date()
        });
        return report;
    }
    async getReport(reportId) {
        return this.repository.findById(reportId);
    }
    async getReports(filters) {
        return this.repository.find(filters);
    }
    async updateReportStatus(reportId, status) {
        const report = await this.getReport(reportId);
        if (!report) {
            throw new Error(`Report ${reportId} not found`);
        }
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'update',
            domain: 'Analytics',
            metadata: { source: 'analytics-service', reportId, status }
        };
        const updateData = { ...report, status };
        // Execute business logic
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Analytics', updateData, 'update', context);
        if (!result.success) {
            throw new Error(`Report status update failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        // Update report entity
        const updatedReport = {
            ...result.data
        };
        // Save to repository
        await this.repository.update(reportId, updatedReport);
        // Publish domain event
        await this.publishDomainEvent('ReportStatusUpdated', {
            reportId,
            oldStatus: report.status,
            newStatus: status,
            timestamp: new Date()
        });
        return updatedReport;
    }
    // Dashboard Management
    async createDashboard(request) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'create',
            domain: 'Analytics',
            metadata: { source: 'analytics-service' }
        };
        // Execute business logic
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Analytics', request, 'create', context);
        if (!result.success) {
            throw new Error(`Dashboard creation failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        // Create dashboard entity
        const dashboard = {
            id: this.generateDashboardId(),
            ...result.data,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        // Save to repository
        await this.repository.create(dashboard);
        // Publish domain event
        await this.publishDomainEvent('DashboardCreated', {
            dashboardId: dashboard.id,
            dashboardName: dashboard.name,
            ownerId: dashboard.ownerId,
            timestamp: new Date()
        });
        return dashboard;
    }
    async updateDashboard(dashboardId, updates) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'update',
            domain: 'Analytics',
            metadata: { source: 'analytics-service', dashboardId }
        };
        // Get existing dashboard
        const existingDashboard = await this.repository.findById(dashboardId);
        if (!existingDashboard) {
            throw new Error(`Dashboard ${dashboardId} not found`);
        }
        // Merge with existing data
        const updateData = { ...existingDashboard, ...updates };
        // Execute business logic
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Analytics', updateData, 'update', context);
        if (!result.success) {
            throw new Error(`Dashboard update failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        // Update dashboard entity
        const updatedDashboard = {
            ...result.data,
            updatedAt: new Date()
        };
        // Save to repository
        await this.repository.update(dashboardId, updatedDashboard);
        // Publish domain event
        await this.publishDomainEvent('DashboardUpdated', {
            dashboardId: updatedDashboard.id,
            changes: updates,
            timestamp: new Date()
        });
        return updatedDashboard;
    }
    async getDashboard(dashboardId) {
        return this.repository.findById(dashboardId);
    }
    async getDashboards(filters) {
        return this.repository.find(filters);
    }
    // Analytics Queries
    async getSalesAnalytics(dateFrom, dateTo) {
        // This would query sales data from ERP domain
        return {
            totalSales: 0,
            totalOrders: 0,
            averageOrderValue: 0,
            topProducts: [],
            salesByMonth: []
        };
    }
    async getInventoryAnalytics() {
        // This would query inventory data from ERP domain
        return {
            totalProducts: 0,
            lowStockProducts: 0,
            outOfStockProducts: 0,
            totalInventoryValue: 0,
            inventoryTurnover: 0
        };
    }
    async getCustomerAnalytics() {
        // This would query customer data from CRM domain
        return {
            totalCustomers: 0,
            activeCustomers: 0,
            newCustomers: 0,
            customerRetentionRate: 0,
            averageCustomerValue: 0
        };
    }
    // Helper Methods
    async generateReportData(report) {
        try {
            // Simulate report data generation
            await new Promise(resolve => setTimeout(resolve, 2000));
            const reportData = await this.generateReportDataByType(report.type, report.parameters);
            // Update report with data
            await this.repository.update(report.id, {
                ...report,
                data: reportData,
                status: 'completed',
                filePath: `/reports/${report.id}.json`
            });
            // Publish domain event
            await this.publishDomainEvent('ReportCompleted', {
                reportId: report.id,
                reportName: report.name,
                timestamp: new Date()
            });
        }
        catch (error) {
            await this.repository.update(report.id, {
                ...report,
                status: 'failed'
            });
            throw error;
        }
    }
    async generateReportDataByType(type, parameters) {
        // This would generate actual report data based on type and parameters
        switch (type) {
            case 'sales':
                return await this.getSalesAnalytics(parameters.dateFrom, parameters.dateTo);
            case 'inventory':
                return await this.getInventoryAnalytics();
            case 'customer':
                return await this.getCustomerAnalytics();
            default:
                return [];
        }
    }
    generateMetricId() {
        return `METRIC_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    generateReportId() {
        return `REPORT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    generateDashboardId() {
        return `DASHBOARD_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    getCurrentUserId() {
        // This would get the current user ID from the authentication context
        return 'system';
    }
    async publishDomainEvent(eventType, data) {
        // This would publish the domain event to the event bus
        console.log(`Publishing domain event: ${eventType}`, data);
    }
}
exports.AnalyticsDomainService = AnalyticsDomainService;
// Analytics Business Rules
class ReportValidationRule {
    constructor() {
        this.name = 'ANALYTICS_REPORT_VALIDATION';
        this.description = 'Validates report generation requests';
        this.priority = 100;
        this.domain = 'Analytics';
        this.version = '1.0.0';
        this.enabled = true;
    }
    async validate(data) {
        const errors = [];
        const warnings = [];
        // Rule: Report name must be provided
        if (!data.name || data.name.trim().length === 0) {
            errors.push({
                field: 'name',
                message: 'Report name is required',
                code: 'ANALYTICS_REPORT_NAME_REQUIRED',
                severity: 'error'
            });
        }
        // Rule: Report type must be valid
        const validTypes = ['sales', 'inventory', 'customer', 'financial', 'custom'];
        if (!data.type || !validTypes.includes(data.type)) {
            errors.push({
                field: 'type',
                message: `Report type must be one of: ${validTypes.join(', ')}`,
                code: 'ANALYTICS_INVALID_REPORT_TYPE',
                severity: 'error'
            });
        }
        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }
}
class DashboardValidationRule {
    constructor() {
        this.name = 'ANALYTICS_DASHBOARD_VALIDATION';
        this.description = 'Validates dashboard creation requests';
        this.priority = 95;
        this.domain = 'Analytics';
        this.version = '1.0.0';
        this.enabled = true;
    }
    async validate(data) {
        const errors = [];
        const warnings = [];
        // Rule: Dashboard name must be provided
        if (!data.name || data.name.trim().length === 0) {
            errors.push({
                field: 'name',
                message: 'Dashboard name is required',
                code: 'ANALYTICS_DASHBOARD_NAME_REQUIRED',
                severity: 'error'
            });
        }
        // Rule: Dashboard must have at least one widget
        if (!data.widgets || data.widgets.length === 0) {
            errors.push({
                field: 'widgets',
                message: 'Dashboard must have at least one widget',
                code: 'ANALYTICS_DASHBOARD_WIDGETS_REQUIRED',
                severity: 'error'
            });
        }
        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }
}
// Global Analytics Domain Service
exports.analyticsDomainService = new AnalyticsDomainService();
