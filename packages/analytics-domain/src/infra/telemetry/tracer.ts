// Mock telemetry implementation for development
export interface MockSpan {
  setAttribute: (_key: string, _value: unknown) => void;
  setStatus: (_status: unknown) => void;
  recordException: (_error: Error) => void;
  end: () => void;
}

export interface MockTracer {
  startSpan: (_name: string) => MockSpan;
}

// Mock tracer implementation
class MockTracerImpl implements MockTracer {
  startSpan(_name: string): MockSpan {
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
  static startSpan(name: string, _attributes?: Record<string, string | number | boolean>): MockSpan {
    const span = tracer.startSpan(name);
    return span;
  }

  static startKpiCalculation(_tenantId: string, _kpiName: string): MockSpan {
    return this.startSpan('analytics.kpi.calculate');
  }

  static startForecastGeneration(_tenantId: string, _metricName: string, _model: string): MockSpan {
    return this.startSpan('analytics.forecast.generate');
  }

  static startReportGeneration(_tenantId: string, _reportType: string): MockSpan {
    return this.startSpan('analytics.report.generate');
  }

  static startCubeRefresh(_tenantId: string, _cubeName: string): MockSpan {
    return this.startSpan('analytics.cube.refresh');
  }

  static startEventProcessing(_eventType: string, _tenantId: string): MockSpan {
    return this.startSpan('analytics.event.process');
  }

  static startDatabaseQuery(operation: string, _table: string, _tenantId?: string): MockSpan {
    return this.startSpan(`db.${operation}`);
  }

  static setSpanError(_span: MockSpan, _error: Error): void {
    // No-op
  }

  static addTenantAttributes(_span: MockSpan, _tenantId: string): void {
    // No-op
  }

  static addUserAttributes(_span: MockSpan, _userId: string, _userEmail?: string): void {
    // No-op
  }

  static addPerformanceAttributes(_span: MockSpan, _duration: number, _recordCount?: number): void {
    // No-op
  }
}