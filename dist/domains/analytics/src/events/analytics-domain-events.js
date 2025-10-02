"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.analyticsRepository = exports.AnalyticsRepository = void 0;
// domains/analytics/src/repositories/analytics-repository.ts
const repository_1 = require("@packages/utilities/repository");
class AnalyticsRepository extends repository_1.Repository {
    constructor() {
        super('metrics');
    }
    // Metric Queries
    async getMetricsByCategory(category) {
        return this.find({ category });
    }
    async getMetricsByType(type) {
        return this.find({ type });
    }
    async getMetricsByDateRange(startDate, endDate) {
        return this.find({
            timestamp: { $gte: startDate, $lte: endDate }
        });
    }
    async getLatestMetrics(limit = 100) {
        const allMetrics = await this.findAll();
        return allMetrics
            .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
            .slice(0, limit);
    }
    async getMetricTrends(metricName, days = 30) {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        const allMetrics = await this.findAll();
        return allMetrics.filter(metric => metric.name === metricName &&
            metric.timestamp >= startDate &&
            metric.timestamp <= endDate).sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    }
    async getTopMetricsByValue(limit = 10) {
        const allMetrics = await this.findAll();
        return allMetrics
            .sort((a, b) => b.value - a.value)
            .slice(0, limit);
    }
    // Report Queries
    async getReports() {
        return this.repository.findAll();
    }
    async getReportsByType(type) {
        return this.repository.find({ type });
    }
    async getReportsByStatus(status) {
        return this.repository.find({ status });
    }
    async getReportsByUser(userId) {
        return this.repository.find({ generatedBy: userId });
    }
    async getPendingReports() {
        return this.getReportsByStatus('pending');
    }
    async getGeneratingReports() {
        return this.getReportsByStatus('generating');
    }
    async getCompletedReports() {
        return this.getReportsByStatus('completed');
    }
    async getFailedReports() {
        return this.getReportsByStatus('failed');
    }
    async getReportsByDateRange(startDate, endDate) {
        return this.repository.find({
            generatedAt: { $gte: startDate, $lte: endDate }
        });
    }
    async getRecentReports(limit = 50) {
        const allReports = await this.getReports();
        return allReports
            .sort((a, b) => b.generatedAt.getTime() - a.generatedAt.getTime())
            .slice(0, limit);
    }
    async getReportStatistics() {
        const allReports = await this.getReports();
        const reportsByType = allReports.reduce((acc, report) => {
            acc[report.type] = (acc[report.type] || 0) + 1;
            return acc;
        }, {});
        const completedReports = allReports.filter(report => report.status === 'completed');
        const averageGenerationTime = completedReports.length > 0
            ? completedReports.reduce((sum, report) => sum + (report.generatedAt.getTime() - report.generatedAt.getTime()), 0) / completedReports.length
            : 0;
        return {
            totalReports: allReports.length,
            pendingReports: allReports.filter(report => report.status === 'pending').length,
            generatingReports: allReports.filter(report => report.status === 'generating').length,
            completedReports: allReports.filter(report => report.status === 'completed').length,
            failedReports: allReports.filter(report => report.status === 'failed').length,
            reportsByType,
            averageGenerationTime
        };
    }
    // Dashboard Queries
    async getDashboards() {
        return this.repository.findAll();
    }
    async getDashboardsByOwner(ownerId) {
        return this.repository.find({ ownerId });
    }
    async getPublicDashboards() {
        return this.repository.find({ isPublic: true });
    }
    async getPrivateDashboards(ownerId) {
        return this.repository.find({ ownerId, isPublic: false });
    }
    async getRecentDashboards(limit = 20) {
        const allDashboards = await this.getDashboards();
        return allDashboards
            .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
            .slice(0, limit);
    }
    async getUpdatedDashboards(limit = 20) {
        const allDashboards = await this.getDashboards();
        return allDashboards
            .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime())
            .slice(0, limit);
    }
    async searchDashboards(query) {
        const allDashboards = await this.getDashboards();
        return allDashboards.filter(dashboard => dashboard.name.toLowerCase().includes(query.toLowerCase()) ||
            dashboard.description.toLowerCase().includes(query.toLowerCase()));
    }
    async getDashboardStatistics() {
        const allDashboards = await this.getDashboards();
        const dashboardsByOwner = allDashboards.reduce((acc, dashboard) => {
            acc[dashboard.ownerId] = (acc[dashboard.ownerId] || 0) + 1;
            return acc;
        }, {});
        const totalWidgets = allDashboards.reduce((sum, dashboard) => sum + dashboard.widgets.length, 0);
        const averageWidgetsPerDashboard = allDashboards.length > 0 ? totalWidgets / allDashboards.length : 0;
        const mostUsedWidgetTypes = allDashboards.reduce((acc, dashboard) => {
            dashboard.widgets.forEach(widget => {
                acc[widget.type] = (acc[widget.type] || 0) + 1;
            });
            return acc;
        }, {});
        return {
            totalDashboards: allDashboards.length,
            publicDashboards: allDashboards.filter(dashboard => dashboard.isPublic).length,
            privateDashboards: allDashboards.filter(dashboard => !dashboard.isPublic).length,
            dashboardsByOwner,
            averageWidgetsPerDashboard,
            mostUsedWidgetTypes
        };
    }
    // Analytics Queries
    async getSalesMetrics(dateFrom, dateTo) {
        return this.find({
            category: 'sales',
            timestamp: { $gte: dateFrom, $lte: dateTo }
        });
    }
    async getInventoryMetrics() {
        return this.find({ category: 'inventory' });
    }
    async getCustomerMetrics() {
        return this.find({ category: 'customer' });
    }
    async getFinancialMetrics() {
        return this.find({ category: 'financial' });
    }
    async getOperationalMetrics() {
        return this.find({ category: 'operational' });
    }
    async getKPIs() {
        const allMetrics = await this.findAll();
        return allMetrics.filter(metric => metric.name.toLowerCase().includes('kpi') ||
            metric.name.toLowerCase().includes('key performance'));
    }
    async getMetricsByTimeframe(timeframe) {
        const endDate = new Date();
        const startDate = new Date();
        switch (timeframe) {
            case 'hour':
                startDate.setHours(endDate.getHours() - 1);
                break;
            case 'day':
                startDate.setDate(endDate.getDate() - 1);
                break;
            case 'week':
                startDate.setDate(endDate.getDate() - 7);
                break;
            case 'month':
                startDate.setMonth(endDate.getMonth() - 1);
                break;
            case 'year':
                startDate.setFullYear(endDate.getFullYear() - 1);
                break;
        }
        return this.getMetricsByDateRange(startDate, endDate);
    }
    async getMetricAggregations(metricName, timeframe) {
        const metrics = await this.getMetricsByTimeframe(timeframe);
        const filteredMetrics = metrics.filter(metric => metric.name === metricName);
        if (filteredMetrics.length === 0) {
            return { min: 0, max: 0, avg: 0, sum: 0, count: 0 };
        }
        const values = filteredMetrics.map(metric => metric.value);
        const min = Math.min(...values);
        const max = Math.max(...values);
        const sum = values.reduce((acc, value) => acc + value, 0);
        const avg = sum / values.length;
        const count = values.length;
        return { min, max, avg, sum, count };
    }
}
exports.AnalyticsRepository = AnalyticsRepository;
// Global Analytics Repository
exports.analyticsRepository = new AnalyticsRepository();
