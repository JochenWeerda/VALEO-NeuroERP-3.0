// Mock telemetry implementation for development
export interface MockSpan {
  setAttribute: (key: string, value: any) => void;
  setStatus: (status: any) => void;
  recordException: (error: Error) => void;
  end: () => void;
}

export interface MockTracer {
  startSpan: (name: string) => MockSpan;
}

// Mock tracer implementation
class MockTracerImpl implements MockTracer {
  startSpan(name: string): MockSpan {
    return {
      setAttribute: () => {},
      setStatus: () => {},
      recordException: () => {},
      end: () => {},
    };
  }
}

// Mock metrics
export const kpiCalculationDuration = {
  record: () => {},
};

export const forecastGenerationDuration = {
  record: () => {},
};

export const reportGenerationDuration = {
  record: () => {},
};

export const cubeRefreshDuration = {
  record: () => {},
};

export const eventProcessingDuration = {
  record: () => {},
};

export const activeConnections = {
  add: () => {},
  remove: () => {},
};

export const requestsTotal = {
  add: () => {},
};

export const errorsTotal = {
  add: () => {},
};

// Mock tracer instance
export const tracer: MockTracer = new MockTracerImpl();

// Tracing utilities
export class AnalyticsTracer {
  static startSpan(name: string, attributes?: Record<string, string | number | boolean>): MockSpan {
    const span = tracer.startSpan(name);
    return span;
  }

  static startKpiCalculation(tenantId: string, kpiName: string): MockSpan {
    return this.startSpan('analytics.kpi.calculate');
  }

  static startForecastGeneration(tenantId: string, metricName: string, model: string): MockSpan {
    return this.startSpan('analytics.forecast.generate');
  }

  static startReportGeneration(tenantId: string, reportType: string): MockSpan {
    return this.startSpan('analytics.report.generate');
  }

  static startCubeRefresh(tenantId: string, cubeName: string): MockSpan {
    return this.startSpan('analytics.cube.refresh');
  }

  static startEventProcessing(eventType: string, tenantId: string): MockSpan {
    return this.startSpan('analytics.event.process');
  }

  static startDatabaseQuery(operation: string, table: string, tenantId?: string): MockSpan {
    return this.startSpan(`db.${operation}`);
  }

  static setSpanError(span: MockSpan, error: Error): void {
    // No-op
  }

  static addTenantAttributes(span: MockSpan, tenantId: string): void {
    // No-op
  }

  static addUserAttributes(span: MockSpan, userId: string, userEmail?: string): void {
    // No-op
  }

  static addPerformanceAttributes(span: MockSpan, duration: number, recordCount?: number): void {
    // No-op
  }
}