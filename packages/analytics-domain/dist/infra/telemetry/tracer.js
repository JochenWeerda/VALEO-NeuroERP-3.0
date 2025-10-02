"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AnalyticsTracer = exports.tracer = exports.errorsTotal = exports.requestsTotal = exports.activeConnections = exports.eventProcessingDuration = exports.cubeRefreshDuration = exports.reportGenerationDuration = exports.forecastGenerationDuration = exports.kpiCalculationDuration = void 0;
class MockTracerImpl {
    startSpan(name) {
        return {
            setAttribute: () => { },
            setStatus: () => { },
            recordException: () => { },
            end: () => { },
        };
    }
}
exports.kpiCalculationDuration = {
    record: () => { },
};
exports.forecastGenerationDuration = {
    record: () => { },
};
exports.reportGenerationDuration = {
    record: () => { },
};
exports.cubeRefreshDuration = {
    record: () => { },
};
exports.eventProcessingDuration = {
    record: () => { },
};
exports.activeConnections = {
    add: () => { },
    remove: () => { },
};
exports.requestsTotal = {
    add: () => { },
};
exports.errorsTotal = {
    add: () => { },
};
exports.tracer = new MockTracerImpl();
class AnalyticsTracer {
    static startSpan(name, attributes) {
        const span = exports.tracer.startSpan(name);
        return span;
    }
    static startKpiCalculation(tenantId, kpiName) {
        return this.startSpan('analytics.kpi.calculate');
    }
    static startForecastGeneration(tenantId, metricName, model) {
        return this.startSpan('analytics.forecast.generate');
    }
    static startReportGeneration(tenantId, reportType) {
        return this.startSpan('analytics.report.generate');
    }
    static startCubeRefresh(tenantId, cubeName) {
        return this.startSpan('analytics.cube.refresh');
    }
    static startEventProcessing(eventType, tenantId) {
        return this.startSpan('analytics.event.process');
    }
    static startDatabaseQuery(operation, table, tenantId) {
        return this.startSpan(`db.${operation}`);
    }
    static setSpanError(span, error) {
    }
    static addTenantAttributes(span, tenantId) {
    }
    static addUserAttributes(span, userId, userEmail) {
    }
    static addPerformanceAttributes(span, duration, recordCount) {
    }
}
exports.AnalyticsTracer = AnalyticsTracer;
//# sourceMappingURL=tracer.js.map