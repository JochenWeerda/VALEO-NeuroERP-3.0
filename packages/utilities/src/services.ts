// Services and Infrastructure Types

export interface Logger {
  debug(message: string, context?: Record<string, unknown>): void;
  info(message: string, context?: Record<string, unknown>): void;
  warn(message: string, context?: Record<string, unknown>): void;
  error(message: string, context?: Record<string, unknown>): void;
}

export interface MetricsRecorder {
  incrementCounter(name: string, labels?: Record<string, string>): void;
  recordGauge(name: string, value: number, labels?: Record<string, string>): void;
  recordHistogram(name: string, value: number, labels?: Record<string, string>): void;
}

export class ServiceLocator {
  private static instance: ServiceLocator;
  private services = new Map<string, any>();

  static getInstance(): ServiceLocator {
    if (!ServiceLocator.instance) {
      ServiceLocator.instance = new ServiceLocator();
    }
    return ServiceLocator.instance;
  }

  registerInstance<T>(token: string, instance: T): void {
    this.services.set(token, instance);
  }

  registerFactory<T>(token: string, factory: () => T): void {
    this.services.set(token, factory);
  }

  resolve<T>(token: string): T {
    const service = this.services.get(token);
    if (!service) {
      throw new Error(`Service with token '${token}' not found`);
    }
    return typeof service === 'function' ? service() : service;
  }

  has(token: string): boolean {
    return this.services.has(token);
  }

  unregister(token: string): void {
    this.services.delete(token);
  }
}

export const metricsService: MetricsRecorder = {
  incrementCounter(name: string, labels?: Record<string, string>): void {
    console.log(`[METRICS] Counter ${name} incremented`, labels);
  },
  recordGauge(name: string, value: number, labels?: Record<string, string>): void {
    console.log(`[METRICS] Gauge ${name} recorded: ${value}`, labels);
  },
  recordHistogram(name: string, value: number, labels?: Record<string, string>): void {
    console.log(`[METRICS] Histogram ${name} recorded: ${value}`, labels);
  },
};
