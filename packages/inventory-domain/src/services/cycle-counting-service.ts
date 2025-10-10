/**
 * VALEO NeuroERP 3.0 - Cycle Counting Service
 *
 * ABC/XYZ policies, automated scheduling, and accuracy tracking
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
// Time constants
const MS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MS_PER_DAY = HOURS_PER_DAY * MINUTES_PER_HOUR * SECONDS_PER_MINUTE * MS_PER_SECOND;
// Constants
const ABC_A_THRESHOLD_PERCENT = 80;
const ABC_B_THRESHOLD_PERCENT = 95;
const COUNT_FREQ_A = 12; // Monthly
const COUNT_FREQ_B = 6;  // Bi-monthly
const COUNT_FREQ_C = 2;  // Semi-annually
import {
  CycleCountCreatedEvent,
  CycleCountCompletedEvent
} from '../core/domain-events/inventory-domain-events';

export interface CycleCountPolicy {
  policyId: string;
  policyName: string;
  classification: 'ABC' | 'XYZ';
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  coverage: number; // Percentage of items to count
  priority: 'A' | 'B' | 'C' | 'X' | 'Y' | 'Z';
  method: 'full_count' | 'sample_count' | 'zero_count';
  tolerance: {
    quantity: number; // Percentage tolerance for quantity variance
    value: number; // Percentage tolerance for value variance
  };
  autoAdjust: boolean;
  requiresApproval: boolean;
  active: boolean;
}

export interface CycleCount {
  countId: string;
  countNumber: string;
  policyId: string;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  type: 'ABC' | 'XYZ' | 'manual' | 'emergency';
  priority: number;
  assignedTo?: string;
  location?: string;
  zone?: string;

  items: Array<{
    sku: string;
    location: string;
    lot?: string;
    serial?: string;
    expectedQty: number;
    expectedValue: number;
    countedQty?: number;
    countedValue?: number;
    varianceQty?: number;
    varianceValue?: number;
    variancePercent?: number;
    status: 'pending' | 'counted' | 'variance' | 'adjusted';
    notes?: string;
  }>;

  schedule: {
    plannedStart: Date;
    plannedEnd: Date;
    actualStart?: Date;
    actualEnd?: Date;
  };

  results: {
    totalItems: number;
    countedItems: number;
    variancesFound: number;
    accuracy: number; // Percentage
    totalVarianceValue: number;
    adjustmentsMade: number;
  };

  createdAt: Date;
  completedAt?: Date;
}

export interface ABCClassification {
  sku: string;
  classification: 'A' | 'B' | 'C';
  annualUsage: number;
  annualValue: number;
  percentageOfTotal: number;
  cumulativePercentage: number;
  countFrequency: number; // Times per year
  lastCount?: Date;
  nextCountDue?: Date;
}

export interface XYZClassification {
  sku: string;
  classification: 'X' | 'Y' | 'Z';
  demandVariability: number; // Coefficient of variation
  forecastAccuracy: number;
  demandPattern: 'stable' | 'seasonal' | 'erratic';
  safetyStock: number;
  reorderPoint: number;
  countFrequency: number; // Times per year
  lastCount?: Date;
  nextCountDue?: Date;
}

export interface CycleCountSchedule {
  scheduleId: string;
  policyId: string;
  scheduledDate: Date;
  dueDate: Date;
  items: Array<{
    sku: string;
    location: string;
    priority: number;
  }>;
  status: 'pending' | 'executing' | 'completed' | 'overdue';
  assignedTo?: string;
  createdAt: Date;
}

export interface CycleCountPerformance {
  period: string; // 'day', 'week', 'month'
  metrics: {
    totalCounts: number;
    completedCounts: number;
    accuracy: number;
    averageVariance: number;
    totalVarianceValue: number;
    timePerCount: number; // minutes
    itemsPerHour: number;
  };
  byLocation: Array<{
    location: string;
    accuracy: number;
    varianceRate: number;
    countFrequency: number;
  }>;
  bySKU: Array<{
    sku: string;
    accuracy: number;
    varianceRate: number;
    countFrequency: number;
  }>;
  trends: {
    accuracy: number[];
    varianceRate: number[];
    productivity: number[];
  };
}

@injectable()
export class CycleCountingService {
  private readonly metrics = new InventoryMetricsService();
  private policies: Map<string, CycleCountPolicy> = new Map();
  private activeCounts: Map<string, CycleCount> = new Map();

  constructor(
    private readonly eventBus: EventBus
  ) {
    this.initializeDefaultPolicies();
  }

  /**
   * Create ABC classification for items
   */
  async createABCClassification(skus: string[]): Promise<ABCClassification[]> {
    const startTime = Date.now();

    try {
      const classifications: ABCClassification[] = [];

      // Get usage data for all SKUs
      const usageData = await this.getSKUUsageData(skus);

      // Sort by annual value descending
      usageData.sort((a, b) => b.annualValue - a.annualValue);

      const totalValue = usageData.reduce((sum, item) => sum + item.annualValue, 0);
      let cumulativePercentage = 0;

      for (const item of usageData) {
        const percentageOfTotal = (item.annualValue / totalValue) * 100;
        cumulativePercentage += percentageOfTotal;

        let classification: 'A' | 'B' | 'C';
        let countFrequency: number;

        if (cumulativePercentage <= ABC_A_THRESHOLD_PERCENT) {
          classification = 'A';
          countFrequency = COUNT_FREQ_A;
        } else if (cumulativePercentage <= ABC_B_THRESHOLD_PERCENT) {
          classification = 'B';
          countFrequency = COUNT_FREQ_B;
        } else {
          classification = 'C';
          countFrequency = COUNT_FREQ_C;
        }

        classifications.push({
          sku: item.sku,
          classification,
          annualUsage: item.annualUsage,
          annualValue: item.annualValue,
          percentageOfTotal,
          cumulativePercentage,
          countFrequency,
          nextCountDue: this.calculateNextCountDue(classification)
        });
      }

      this.metrics.recordDatabaseQueryDuration('cycle_count.abc_classification', (Date.now() - startTime) / 1000, { tenantId: 'default' });

      return classifications;
    } catch (error) {
      this.metrics.incrementErrorCount('cycle_count.abc_classification_failed', { error: 'abc_classification_error' });
      throw error;
    }
  }

  /**
   * Create XYZ classification for items
   */
  async createXYZClassification(skus: string[]): Promise<XYZClassification[]> {
    const startTime = Date.now();

    try {
      const classifications: XYZClassification[] = [];

      for (const sku of skus) {
        const demandData = await this.getSKUDemandData(sku);
        const variability = this.calculateDemandVariability(demandData);
        const forecastAccuracy = await this.getForecastAccuracy(sku);

        let classification: 'X' | 'Y' | 'Z';
        let countFrequency: number;

        if (variability <= 0.5 && forecastAccuracy >= 0.8) {
          classification = 'X'; // Low variability, high forecast accuracy
          countFrequency = 4; // Quarterly
        } else if (variability <= 1.0 && forecastAccuracy >= 0.6) {
          classification = 'Y'; // Medium variability
          countFrequency = 6; // Bi-monthly
        } else {
          classification = 'Z'; // High variability, low forecast accuracy
          countFrequency = 12; // Monthly
        }

        classifications.push({
          sku,
          classification,
          demandVariability: variability,
          forecastAccuracy,
          demandPattern: this.analyzeDemandPattern(demandData),
          safetyStock: this.calculateSafetyStock(sku, variability),
          reorderPoint: await this.getReorderPoint(sku),
          countFrequency,
          nextCountDue: this.calculateNextCountDue(classification)
        });
      }

      this.metrics.recordDatabaseQueryDuration('cycle_count.xyz_classification', (Date.now() - startTime) / 1000, { tenantId: 'default' });

      return classifications;
    } catch (error) {
      this.metrics.incrementErrorCount('cycle_count.xyz_classification_failed', { error: 'xyz_classification_error' });
      throw error;
    }
  }

  /**
   * Create cycle count policy
   */
  async createCycleCountPolicy(policy: Omit<CycleCountPolicy, 'policyId'>): Promise<CycleCountPolicy> {
    const fullPolicy: CycleCountPolicy = {
      ...policy,
      policyId: `policy_${Date.now()}`
    };

    this.policies.set(fullPolicy.policyId, fullPolicy);
    return fullPolicy;
  }

  /**
   * Generate cycle count schedule
   */
  async generateCycleCountSchedule(policyId: string, startDate: Date, endDate: Date): Promise<CycleCountSchedule[]> {
    const startTime = Date.now();

    try {
      const policy = this.policies.get(policyId);
      if (!policy) {
        throw new Error(`Policy ${policyId} not found`);
      }

      const schedules: CycleCountSchedule[] = [];
      let currentDate = new Date(startDate);

      while (currentDate <= endDate) {
        const items = await this.selectItemsForCounting(policy, currentDate);

        if (items.length > 0) {
          const schedule: CycleCountSchedule = {
            scheduleId: `schedule_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            policyId,
            scheduledDate: new Date(currentDate),
            dueDate: new Date(currentDate.getTime() + MS_PER_DAY), // Next day
            items,
            status: 'pending',
            createdAt: new Date()
          };

          schedules.push(schedule);
        }

        // Move to next count date based on frequency
        currentDate = this.getNextCountDate(currentDate, policy.frequency);
      }

      this.metrics.recordDatabaseQueryDuration('cycle_count.schedule_generation', (Date.now() - startTime) / 1000, { tenantId: 'default' });

      return schedules;
    } catch (error) {
      this.metrics.incrementErrorCount('cycle_count.schedule_generation_failed', { error: 'schedule_generation_error' });
      throw error;
    }
  }

  /**
   * Create cycle count from schedule
   */
  async createCycleCount(scheduleId: string, assignedTo?: string): Promise<CycleCount> {
    const startTime = Date.now();

    try {
      const schedule = await this.getSchedule(scheduleId);
      if (!schedule) {
        throw new Error(`Schedule ${scheduleId} not found`);
      }

      const policy = this.policies.get(schedule.policyId);
      if (!policy) {
        throw new Error(`Policy ${schedule.policyId} not found`);
      }

      // Get current inventory levels for scheduled items
      const items = await Promise.all(
        schedule.items.map(async (item) => {
          const inventory = await this.getCurrentInventory(item.sku, item.location);
          return {
            sku: item.sku,
            location: item.location,
            lot: inventory.lot,
            serial: inventory.serial,
            expectedQty: inventory.quantity,
            expectedValue: inventory.unitCost ? inventory.unitCost * inventory.quantity : 0,
            status: 'pending' as const
          };
        })
      );

      const count: CycleCount = {
        countId: `count_${Date.now()}`,
        countNumber: `CC${Date.now()}`,
        policyId: schedule.policyId,
        status: 'planned',
        type: policy.classification,
        priority: schedule.items.reduce((max, item) => Math.max(max, item.priority), 1),
        assignedTo,
        items,
        schedule: {
          plannedStart: schedule.scheduledDate,
          plannedEnd: schedule.dueDate
        },
        results: {
          totalItems: items.length,
          countedItems: 0,
          variancesFound: 0,
          accuracy: 0,
          totalVarianceValue: 0,
          adjustmentsMade: 0
        },
        createdAt: new Date()
      };

      this.activeCounts.set(count.countId, count);
      schedule.status = 'executing';

      // Publish event
      await this.publishCycleCountCreatedEvent(count);

      this.metrics.recordDatabaseQueryDuration('cycle_count.count_creation', (Date.now() - startTime) / 1000, { countId: count.countId });

      return count;
    } catch (error) {
      this.metrics.incrementErrorCount('cycle_count.count_creation_failed', { error: 'count_creation_error' });
      throw error;
    }
  }

  /**
   * Record count result for an item
   */
  async recordCountResult(
    countId: string,
    sku: string,
    location: string,
    countedQty: number,
    notes?: string
  ): Promise<void> {
    const count = this.activeCounts.get(countId);
    if (!count) {
      throw new Error(`Count ${countId} not found`);
    }

    if (count.status !== 'in_progress') {
      count.status = 'in_progress';
      count.schedule.actualStart = new Date();
    }

    const item = count.items.find(i => i.sku === sku && i.location === location);
    if (!item) {
      throw new Error(`Item ${sku} at ${location} not found in count ${countId}`);
    }

    item.countedQty = countedQty;
    item.countedValue = item.expectedValue * (countedQty / item.expectedQty);
    item.varianceQty = countedQty - item.expectedQty;
    item.varianceValue = item.countedValue - item.expectedValue;
    item.variancePercent = item.expectedQty > 0 ? (item.varianceQty / item.expectedQty) * 100 : 0;
    item.status = 'counted';
    item.notes = notes;

    // Check for variances
    const policy = this.policies.get(count.policyId);
    if (policy && this.isVariance(item, policy.tolerance)) {
      item.status = 'variance';
      count.results.variancesFound++;
    }

    count.results.countedItems++;
  }

  /**
   * Complete cycle count
   */
  async completeCycleCount(countId: string): Promise<CycleCount> {
    const startTime = Date.now();
    const count = this.activeCounts.get(countId);

    if (!count) {
      throw new Error(`Count ${countId} not found`);
    }

    if (count.status !== 'in_progress') {
      throw new Error(`Count ${countId} is not in progress`);
    }

    count.status = 'completed';
    count.completedAt = new Date();
    count.schedule.actualEnd = new Date();

    // Calculate results
    count.results.accuracy = (count.results.totalItems - count.results.variancesFound) / count.results.totalItems * 100;
    count.results.totalVarianceValue = count.items.reduce((sum, item) => sum + (item.varianceValue || 0), 0);

    // Auto-adjust if policy allows
    const policy = this.policies.get(count.policyId);
    if (policy?.autoAdjust) {
      await this.processAutoAdjustments(count);
    }

    // Update schedule
    const schedule = await this.getScheduleByCount(countId);
    if (schedule) {
      schedule.status = 'completed';
    }

    // Publish event
    await this.publishCycleCountCompletedEvent(count);

    this.metrics.recordDatabaseQueryDuration('cycle_count.count_completion', (Date.now() - startTime) / 1000, { countId });
    this.metrics.incrementCycleCounts('cycle_count.completed', { countId });

    return count;
  }

  /**
   * Get cycle count performance metrics
   */
  async getCycleCountPerformance(period: 'day' | 'week' | 'month' = 'month'): Promise<CycleCountPerformance> {
    const startTime = Date.now();

    try {
      const endDate = new Date();
      const startDate = new Date();

      switch (period) {
        case 'day':
          startDate.setDate(endDate.getDate() - 1);
          break;
        case 'week':
          startDate.setDate(endDate.getDate() - 7);
          break;
        case 'month':
          startDate.setMonth(endDate.getMonth() - 1);
          break;
      }

      const completedCounts = await this.getCompletedCounts(startDate, endDate);
      const performance = this.calculatePerformanceMetrics(completedCounts, period);

      this.metrics.recordDatabaseQueryDuration('cycle_count.performance_calculation', (Date.now() - startTime) / 1000, { period });

      return performance;
    } catch (error) {
      this.metrics.incrementErrorCount('cycle_count.performance_calculation_failed', { error: 'performance_calculation_error' });
      throw error;
    }
  }

  /**
   * Get overdue counts
   */
  async getOverdueCounts(): Promise<CycleCountSchedule[]> {
    const now = new Date();
    const schedules = await this.getAllSchedules();

    return schedules.filter(schedule =>
      schedule.status === 'pending' &&
      schedule.dueDate < now
    );
  }

  // Private helper methods

  private initializeDefaultPolicies(): void {
    const policies: CycleCountPolicy[] = [
      {
        policyId: 'abc_a',
        policyName: 'ABC Class A Items',
        classification: 'ABC',
        frequency: 'monthly',
        coverage: 100,
        priority: 'A',
        method: 'full_count',
        tolerance: { quantity: 5, value: 10 },
        autoAdjust: true,
        requiresApproval: false,
        active: true
      },
      {
        policyId: 'abc_b',
        policyName: 'ABC Class B Items',
        classification: 'ABC',
        frequency: 'quarterly',
        coverage: 50,
        priority: 'B',
        method: 'sample_count',
        tolerance: { quantity: 10, value: 15 },
        autoAdjust: false,
        requiresApproval: true,
        active: true
      },
      {
        policyId: 'xyz_z',
        policyName: 'XYZ Class Z Items',
        classification: 'XYZ',
        frequency: 'monthly',
        coverage: 25,
        priority: 'Z',
        method: 'zero_count',
        tolerance: { quantity: 20, value: 25 },
        autoAdjust: false,
        requiresApproval: true,
        active: true
      }
    ];

    policies.forEach(policy => this.policies.set(policy.policyId, policy));
  }

  private async getSKUUsageData(skus: string[]): Promise<Array<{ sku: string; annualUsage: number; annualValue: number }>> {
    // Mock implementation
    return skus.map(sku => ({
      sku,
      annualUsage: Math.random() * 10000,
      annualValue: Math.random() * 50000
    }));
  }

  private async getSKUDemandData(sku: string): Promise<number[]> {
    // Mock demand data for last 12 months
    return Array.from({ length: 12 }, () => Math.random() * 1000 + 500);
  }

  private calculateDemandVariability(demandData: number[]): number {
    const mean = demandData.reduce((sum, val) => sum + val, 0) / demandData.length;
    const variance = demandData.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / demandData.length;
    return Math.sqrt(variance) / mean; // Coefficient of variation
  }

  private async getForecastAccuracy(sku: string): Promise<number> {
    // Mock forecast accuracy
    return Math.random() * 0.4 + 0.6; // 0.6 to 1.0
  }

  private analyzeDemandPattern(demandData: number[]): 'stable' | 'seasonal' | 'erratic' {
    const variability = this.calculateDemandVariability(demandData);
    if (variability < 0.3) return 'stable';
    if (variability < 0.7) return 'seasonal';
    return 'erratic';
  }

  private calculateSafetyStock(sku: string, variability: number): number {
    // Mock safety stock calculation
    return variability * 100;
  }

  private async getReorderPoint(sku: string): Promise<number> {
    // Mock reorder point
    return Math.random() * 200 + 100;
  }

  private calculateNextCountDue(classification: string): Date {
    const now = new Date();
    const days = classification === 'A' || classification === 'Z' ? 30 :
                 classification === 'B' || classification === 'Y' ? 60 : 120;
    now.setDate(now.getDate() + days);
    return now;
  }

  private getNextCountDate(currentDate: Date, frequency: string): Date {
    const next = new Date(currentDate);
    switch (frequency) {
      case 'daily':
        next.setDate(next.getDate() + 1);
        break;
      case 'weekly':
        next.setDate(next.getDate() + 7);
        break;
      case 'monthly':
        next.setMonth(next.getMonth() + 1);
        break;
      case 'quarterly':
        next.setMonth(next.getMonth() + 3);
        break;
    }
    return next;
  }

  private async selectItemsForCounting(policy: CycleCountPolicy, date: Date): Promise<Array<{ sku: string; location: string; priority: number }>> {
    // Mock item selection based on policy
    const items: Array<{ sku: string; location: string; priority: number }> = [];

    // Get items due for counting based on classification
    const dueItems = await this.getItemsDueForCounting(policy, date);

    // Apply coverage percentage
    const count = Math.ceil(dueItems.length * (policy.coverage / 100));
    const selectedItems = dueItems.slice(0, count);

    for (const item of selectedItems) {
      items.push({
        sku: item.sku,
        location: item.location,
        priority: this.getPriorityValue(policy.priority)
      });
    }

    return items;
  }

  private async getItemsDueForCounting(policy: CycleCountPolicy, date: Date): Promise<Array<{ sku: string; location: string }>> {
    // Mock implementation - would query database for items due for counting
    return [
      { sku: 'WIDGET-001', location: 'A-01-01-01' },
      { sku: 'GADGET-002', location: 'A-01-01-02' }
    ];
  }

  private getPriorityValue(priority: string): number {
    const priorities = { 'A': 5, 'B': 4, 'C': 3, 'X': 2, 'Y': 1, 'Z': 1 };
    return priorities[priority as keyof typeof priorities] || 1;
  }

  private async getSchedule(scheduleId: string): Promise<CycleCountSchedule | null> {
    // Mock implementation
    return {
      scheduleId,
      policyId: 'policy_123',
      scheduledDate: new Date(),
      dueDate: new Date(Date.now() + 24 * 60 * 60 * 1000),
      items: [],
      status: 'pending',
      createdAt: new Date()
    };
  }

  private async getCurrentInventory(sku: string, location: string): Promise<any> {
    // Mock inventory data
    return {
      sku,
      location,
      quantity: Math.floor(Math.random() * 100) + 10,
      unitCost: Math.random() * 50 + 10
    };
  }

  private isVariance(item: CycleCount['items'][0], tolerance: CycleCountPolicy['tolerance']): boolean {
    const qtyVariancePercent = Math.abs(item.variancePercent || 0);
    const valueVariancePercent = item.expectedValue > 0 ?
      Math.abs((item.varianceValue || 0) / item.expectedValue * 100) : 0;

    return qtyVariancePercent > tolerance.quantity || valueVariancePercent > tolerance.value;
  }

  private async processAutoAdjustments(count: CycleCount): Promise<void> {
    const varianceItems = count.items.filter(item => item.status === 'variance');

    for (const item of varianceItems) {
      if (item.countedQty !== undefined) {
        // Create inventory adjustment
        await this.createInventoryAdjustment(
          item.sku,
          item.location,
          item.countedQty - item.expectedQty,
          `Cycle count adjustment - ${count.countNumber}`,
          item.lot,
          item.serial
        );

        item.status = 'adjusted';
        count.results.adjustmentsMade++;
      }
    }
  }

  private async createInventoryAdjustment(
    sku: string,
    location: string,
    quantity: number,
    reason: string,
    lot?: string,
    serial?: string
  ): Promise<void> {
    // Mock implementation - would create inventory adjustment
    // eslint-disable-next-line no-console
    console.log(`Adjusting inventory: ${sku} at ${location} by ${quantity}`);
  }

  private async getScheduleByCount(countId: string): Promise<CycleCountSchedule | null> {
    // Mock implementation
    return null;
  }

  private async getCompletedCounts(startDate: Date, endDate: Date): Promise<CycleCount[]> {
    // Mock implementation
    return Array.from(this.activeCounts.values())
      .filter(count => count.completedAt && count.completedAt >= startDate && count.completedAt <= endDate);
  }

  private calculatePerformanceMetrics(counts: CycleCount[], period: string): CycleCountPerformance {
    const totalCounts = counts.length;
    const totalAccuracy = counts.reduce((sum, count) => sum + count.results.accuracy, 0);
    const averageAccuracy = totalCounts > 0 ? totalAccuracy / totalCounts : 0;

    return {
      period,
      metrics: {
        totalCounts,
        completedCounts: totalCounts,
        accuracy: averageAccuracy,
        averageVariance: 0, // Would calculate from actual data
        totalVarianceValue: counts.reduce((sum, count) => sum + count.results.totalVarianceValue, 0),
        timePerCount: 0, // Would calculate from actual data
        itemsPerHour: 0 // Would calculate from actual data
      },
      byLocation: [],
      bySKU: [],
      trends: {
        accuracy: [],
        varianceRate: [],
        productivity: []
      }
    };
  }

  private async getAllSchedules(): Promise<CycleCountSchedule[]> {
    // Mock implementation
    return [];
  }

  // Event publishing methods
  private async publishCycleCountCreatedEvent(count: CycleCount): Promise<void> {
    const event: CycleCountCreatedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.cyclecount.created',
      aggregateId: count.countId,
      aggregateType: 'CycleCount',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      type: 'inventory.cyclecount.created',
      occurredAt: new Date(),
      aggregateVersion: 1,
      countId: count.countId,
      locations: Array.from(new Set(count.items.map(item => item.location))),
      method: count.type === 'ABC' ? 'ABC' : 'manual',
      scheduledDate: count.schedule.plannedStart
    };

    await this.eventBus.publish(event);
  }

  private async publishCycleCountCompletedEvent(count: CycleCount): Promise<void> {
    const event: CycleCountCompletedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.cyclecount.completed',
      aggregateId: count.countId,
      aggregateType: 'CycleCount',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      type: 'inventory.cyclecount.completed',
      occurredAt: new Date(),
      aggregateVersion: 1,
      countId: count.countId,
      countedBy: count.assignedTo || 'unknown',
      discrepancies: count.items
        .filter(item => item.status === 'variance')
        .map(item => ({
          sku: item.sku,
          location: item.location,
          expectedQty: item.expectedQty,
          countedQty: item.countedQty || 0,
          variance: item.varianceQty || 0
        })),
      accuracy: count.results.accuracy
    };

    await this.eventBus.publish(event);
  }
}