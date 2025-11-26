/**
 * Performance Monitor
 * Überwacht und optimiert System-Performance für VALEO-NeuroERP 3.0
 */

import { randomUUID } from 'crypto';

export interface PerformanceMetrics {
  operationId: string;
  operationType: string;
  startTime: number;
  endTime: number;
  duration: number;
  memoryUsage: {
    heapUsed: number;
    heapTotal: number;
    external: number;
    rss: number;
  };
  cpuUsage: {
    user: number;
    system: number;
  };
  success: boolean;
  errorMessage?: string;
  tenantId: string;
  userId?: string;
  metadata?: Record<string, any>;
}

export interface PerformanceThresholds {
  warningThreshold: number; // ms
  criticalThreshold: number; // ms
  maxMemoryUsage: number; // bytes
  maxConcurrentOperations: number;
}

export interface PerformanceStats {
  avgResponseTime: number;
  p95ResponseTime: number;
  p99ResponseTime: number;
  throughput: number; // operations per second
  errorRate: number; // percentage
  memoryEfficiency: number; // percentage
  cacheHitRate: number; // percentage
}

export class PerformanceMonitor {
  private readonly metrics: PerformanceMetrics[] = [];
  private readonly activeOperations = new Map<string, { startTime: number; startCpu: NodeJS.CpuUsage }>();
  private readonly cache = new Map<string, { value: any; expiry: number; hits: number }>();
  private cacheRequests = 0;
  private cacheHits = 0;

  private readonly defaultThresholds: PerformanceThresholds = {
    warningThreshold: 200, // 200ms
    criticalThreshold: 1000, // 1 second
    maxMemoryUsage: 500 * 1024 * 1024, // 500MB
    maxConcurrentOperations: 100
  };

  constructor(private thresholds: PerformanceThresholds = this.defaultThresholds) {}

  /**
   * Startet Performance-Monitoring für eine Operation
   */
  startOperation(operationType: string, tenantId: string, userId?: string, metadata?: Record<string, any>): string {
    const operationId = randomUUID();
    const startTime = Date.now();
    const startCpu = process.cpuUsage();

    this.activeOperations.set(operationId, { startTime, startCpu });

    // Prüfe aktive Operationen für Überlastung
    if (this.activeOperations.size > this.thresholds.maxConcurrentOperations) {
      console.warn(`⚠️ High concurrent operations: ${this.activeOperations.size}`);
    }

    return operationId;
  }

  /**
   * Beendet Performance-Monitoring und speichert Metriken
   */
  endOperation(
    operationId: string,
    operationType: string,
    tenantId: string,
    success: boolean = true,
    errorMessage?: string,
    userId?: string,
    metadata?: Record<string, any>
  ): PerformanceMetrics {
    const activeOp = this.activeOperations.get(operationId);
    if (!activeOp) {
      throw new Error(`Operation ${operationId} not found`);
    }

    const endTime = Date.now();
    const duration = endTime - activeOp.startTime;
    const memoryUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage(activeOp.startCpu);

    const metric: PerformanceMetrics = {
      operationId,
      operationType,
      startTime: activeOp.startTime,
      endTime,
      duration,
      memoryUsage: {
        heapUsed: memoryUsage.heapUsed,
        heapTotal: memoryUsage.heapTotal,
        external: memoryUsage.external,
        rss: memoryUsage.rss
      },
      cpuUsage: {
        user: cpuUsage.user / 1000, // Convert to ms
        system: cpuUsage.system / 1000
      },
      success,
      errorMessage,
      tenantId,
      userId,
      metadata
    };

    // Speichere Metrik
    this.metrics.push(metric);
    this.activeOperations.delete(operationId);

    // Performance-Warnungen
    this.checkPerformanceThresholds(metric);

    // Cleanup alte Metriken (behalte nur letzte 1000)
    if (this.metrics.length > 1000) {
      this.metrics.splice(0, this.metrics.length - 1000);
    }

    return metric;
  }

  /**
   * Decorator für automatisches Performance-Monitoring
   */
  monitor(operationType: string) {
    return (target: any, propertyName: string, descriptor: PropertyDescriptor) => {
      const method = descriptor.value;

      descriptor.value = async function (...args: any[]) {
        // Versuche tenantId und userId aus args zu extrahieren
        const tenantId = args.find(arg => typeof arg === 'string' && arg.includes('tenant')) || 'unknown';
        const userId = args.find(arg => typeof arg === 'string' && arg.includes('user'));

        const operationId = this.startOperation?.(operationType, tenantId, userId) || randomUUID();
        
        try {
          const result = await method.apply(this, args);
          this.endOperation?.(operationId, operationType, tenantId, true, undefined, userId);
          return result;
        } catch (error) {
          this.endOperation?.(operationId, operationType, tenantId, false, (error as Error).message, userId);
          throw error;
        }
      };

      return descriptor;
    };
  }

  /**
   * Intelligente Cache-Implementierung
   */
  async getCached<T>(
    key: string,
    fetchFunction: () => Promise<T>,
    ttlMs: number = 300000 // 5 minutes default
  ): Promise<T> {
    this.cacheRequests++;
    
    const cached = this.cache.get(key);
    const now = Date.now();

    if (cached && cached.expiry > now) {
      cached.hits++;
      this.cacheHits++;
      return cached.value;
    }

    // Cache miss - fetch new data
    const value = await fetchFunction();
    this.cache.set(key, {
      value,
      expiry: now + ttlMs,
      hits: 0
    });

    return value;
  }

  /**
   * Batch-Verarbeitung für bessere Performance
   */
  async processBatch<T, R>(
    items: T[],
    processor: (batch: T[]) => Promise<R[]>,
    batchSize: number = 10
  ): Promise<R[]> {
    const results: R[] = [];
    
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      const batchResults = await processor(batch);
      results.push(...batchResults);
      
      // Kurze Pause zwischen Batches für System-Entlastung
      if (i + batchSize < items.length) {
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    }

    return results;
  }

  /**
   * Berechnet Performance-Statistiken
   */
  getPerformanceStats(timeWindowMs?: number): PerformanceStats {
    const now = Date.now();
    const relevantMetrics = timeWindowMs 
      ? this.metrics.filter(m => (now - m.endTime) <= timeWindowMs)
      : this.metrics;

    if (relevantMetrics.length === 0) {
      return {
        avgResponseTime: 0,
        p95ResponseTime: 0,
        p99ResponseTime: 0,
        throughput: 0,
        errorRate: 0,
        memoryEfficiency: 100,
        cacheHitRate: this.getCacheHitRate()
      };
    }

    // Sortiere nach Dauer für Percentile-Berechnung
    const durations = relevantMetrics.map(m => m.duration).sort((a, b) => a - b);
    const successfulOps = relevantMetrics.filter(m => m.success);
    
    const p95Index = Math.floor(durations.length * 0.95);
    const p99Index = Math.floor(durations.length * 0.99);

    const timeWindowS = timeWindowMs ? timeWindowMs / 1000 : 
                       (relevantMetrics[relevantMetrics.length - 1].endTime - relevantMetrics[0].startTime) / 1000;

    // Memory Efficiency berechnen
    const avgMemoryUsage = relevantMetrics.reduce((sum, m) => sum + m.memoryUsage.heapUsed, 0) / relevantMetrics.length;
    const memoryEfficiency = Math.max(0, 100 - (avgMemoryUsage / this.thresholds.maxMemoryUsage) * 100);

    return {
      avgResponseTime: relevantMetrics.reduce((sum, m) => sum + m.duration, 0) / relevantMetrics.length,
      p95ResponseTime: durations[p95Index] || 0,
      p99ResponseTime: durations[p99Index] || 0,
      throughput: relevantMetrics.length / Math.max(timeWindowS, 1),
      errorRate: ((relevantMetrics.length - successfulOps.length) / relevantMetrics.length) * 100,
      memoryEfficiency,
      cacheHitRate: this.getCacheHitRate()
    };
  }

  /**
   * Optimierung-Empfehlungen basierend auf Metriken
   */
  getOptimizationRecommendations(): string[] {
    const stats = this.getPerformanceStats();
    const recommendations: string[] = [];

    if (stats.avgResponseTime > this.thresholds.warningThreshold) {
      recommendations.push('⚠️ Durchschnittliche Response-Zeit erhöht - Datenbankabfragen optimieren');
    }

    if (stats.p95ResponseTime > this.thresholds.criticalThreshold) {
      recommendations.push('🔴 95% Percentile kritisch - Indexierung und Caching überprüfen');
    }

    if (stats.errorRate > 5) {
      recommendations.push('⚠️ Erhöhte Fehlerrate - Error Handling und Retry-Logik verbessern');
    }

    if (stats.memoryEfficiency < 70) {
      recommendations.push('💾 Memory-Usage hoch - Memory Leaks prüfen und Garbage Collection optimieren');
    }

    if (stats.cacheHitRate < 80) {
      recommendations.push('🔄 Cache Hit Rate niedrig - Cache-Strategien und TTL überprüfen');
    }

    if (stats.throughput < 10) {
      recommendations.push('📈 Durchsatz niedrig - Parallel Processing und Batch-Verarbeitung implementieren');
    }

    if (this.activeOperations.size > 50) {
      recommendations.push('⚡ Viele aktive Operationen - Connection Pooling und Rate Limiting implementieren');
    }

    return recommendations;
  }

  /**
   * Memory-optimierte Verarbeitung für große Datenmengen
   */
  async processLargeDataset<T, R>(
    data: T[],
    processor: (item: T) => Promise<R>,
    options: {
      batchSize?: number;
      concurrency?: number;
      memoryThreshold?: number;
    } = {}
  ): Promise<R[]> {
    const {
      batchSize = 100,
      concurrency = 5,
      memoryThreshold = this.thresholds.maxMemoryUsage * 0.8
    } = options;

    const results: R[] = [];
    
    for (let i = 0; i < data.length; i += batchSize) {
      // Memory Check
      const currentMemory = process.memoryUsage().heapUsed;
      if (currentMemory > memoryThreshold) {
        // Forced garbage collection hint
        if (global.gc) {
          global.gc();
        }
        // Pause für Memory Recovery
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      const batch = data.slice(i, i + batchSize);
      
      // Parallel processing mit Concurrency-Limit
      const batchPromises: Promise<R>[] = [];
      for (let j = 0; j < batch.length; j += concurrency) {
        const concurrentBatch = batch.slice(j, j + concurrency);
        batchPromises.push(...concurrentBatch.map(processor));
      }
      
      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults);
    }

    return results;
  }

  /**
   * Real-time Performance Dashboard Daten
   */
  getDashboardMetrics() {
    const stats = this.getPerformanceStats(300000); // Last 5 minutes
    const recentMetrics = this.metrics.slice(-100); // Last 100 operations

    return {
      realTimeStats: stats,
      recentOperations: recentMetrics.map(m => ({
        operationType: m.operationType,
        duration: m.duration,
        success: m.success,
        timestamp: m.endTime
      })),
      activeOperations: this.activeOperations.size,
      cacheStats: {
        totalRequests: this.cacheRequests,
        cacheHits: this.cacheHits,
        hitRate: this.getCacheHitRate(),
        cacheSize: this.cache.size
      },
      systemHealth: {
        memoryUsage: process.memoryUsage(),
        cpuUsage: process.cpuUsage(),
        uptime: process.uptime()
      },
      recommendations: this.getOptimizationRecommendations()
    };
  }

  // Private Helper Methods

  private checkPerformanceThresholds(metric: PerformanceMetrics): void {
    if (metric.duration > this.thresholds.criticalThreshold) {
      console.error(`🔴 CRITICAL: Operation ${metric.operationType} took ${metric.duration}ms`);
    } else if (metric.duration > this.thresholds.warningThreshold) {
      console.warn(`⚠️ WARNING: Operation ${metric.operationType} took ${metric.duration}ms`);
    }

    if (metric.memoryUsage.heapUsed > this.thresholds.maxMemoryUsage) {
      console.warn(`💾 HIGH MEMORY: Operation used ${Math.round(metric.memoryUsage.heapUsed / 1024 / 1024)}MB`);
    }
  }

  private getCacheHitRate(): number {
    return this.cacheRequests > 0 ? (this.cacheHits / this.cacheRequests) * 100 : 0;
  }

  /**
   * Cleanup und Reset
   */
  cleanup(): void {
    this.metrics.splice(0);
    this.activeOperations.clear();
    this.cache.clear();
    this.cacheRequests = 0;
    this.cacheHits = 0;
  }
}

// Singleton Instance für globale Nutzung
export const performanceMonitor = new PerformanceMonitor();
