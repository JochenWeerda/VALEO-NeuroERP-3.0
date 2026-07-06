/**
 * VALEO NeuroERP 3.0 - Picking Service
 *
 * Advanced picking operations with wave/batch/zone picking strategies
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
import {
  PickTaskCreatedEvent,
  PickCompletedEvent,
  PickTaskAssignedEvent,
  WaveCreatedEvent,
  WaveCompletedEvent
} from '../core/domain-events/inventory-domain-events';

export interface PickTask {
  taskId: string;
  orderId: string;
  waveId?: string;
  batchId?: string;
  sku: string;
  location: string;
  lot?: string;
  serial?: string;
  quantity: number;
  pickedQuantity: number;
  status: 'pending' | 'in_progress' | 'completed' | 'short' | 'damaged';
  assignedTo?: string;
  priority: number;
  zone: string;
  sequence: number; // Picking sequence within wave/batch
  estimatedTime: number; // seconds
  actualTime?: number; // seconds
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  qualityChecks?: Array<{
    checkType: 'quantity' | 'condition' | 'label';
    passed: boolean;
    notes?: string;
    checkedBy: string;
    checkedAt: Date;
  }>;
}

export interface PickingWave {
  waveId: string;
  waveNumber: string;
  status: 'planned' | 'released' | 'in_progress' | 'completed' | 'cancelled';
  strategy: 'single_order' | 'batch' | 'zone' | 'cluster';
  priority: number;
  zone: string;
  tasks: PickTask[];
  totalTasks: number;
  completedTasks: number;
  totalQuantity: number;
  pickedQuantity: number;
  assignedPickers: string[];
  estimatedDuration: number; // minutes
  actualDuration?: number; // minutes
  createdAt: Date;
  releasedAt?: Date;
  completedAt?: Date;
  productivity?: {
    picksPerHour: number;
    linesPerHour: number;
    accuracy: number;
    averageTimePerPick: number;
  };
}

export interface PickingBatch {
  batchId: string;
  batchNumber: string;
  orders: string[];
  skus: Array<{
    sku: string;
    totalQuantity: number;
    locations: Array<{
      location: string;
      quantity: number;
      lot?: string;
    }>;
  }>;
  status: 'planned' | 'active' | 'completed';
  priority: number;
  createdAt: Date;
  completedAt?: Date;
}

export interface ZoneConfiguration {
  zoneId: string;
  zoneName: string;
  type: 'forward' | 'reserve' | 'bulk' | 'hazardous' | 'ambient' | 'refrigerated' | 'frozen';
  pickers: string[];
  locations: string[];
  capacity: {
    maxConcurrentPickers: number;
    maxTasksPerHour: number;
  };
  routing: {
    entryPoint: string;
    exitPoint: string;
    optimalPath: string[];
  };
  active: boolean;
}

export interface PickerPerformance {
  pickerId: string;
  name: string;
  zone: string;
  shift: string;
  metrics: {
    totalPicks: number;
    totalLines: number;
    totalQuantity: number;
    picksPerHour: number;
    linesPerHour: number;
    accuracy: number;
    averageTimePerPick: number;
    totalTimeWorked: number; // minutes
  };
  performance: {
    score: number; // 0-100
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
    trends: {
      picksPerHour: number[];
      accuracy: number[];
      timePerPick: number[];
    };
  };
  currentSession: {
    startTime: Date;
    tasksCompleted: number;
    totalPicks: number;
    errors: number;
  };
}

@injectable()
export class PickingService {
  private readonly metrics = new InventoryMetricsService();
  private zones: Map<string, ZoneConfiguration> = new Map();
  private activeWaves: Map<string, PickingWave> = new Map();

  constructor(
    private readonly eventBus: EventBus
  ) {
    this.initializeDefaultZones();
  }

  /**
   * Create picking wave from orders
   */
  async createPickingWave(
    orders: string[],
    strategy: PickingWave['strategy'] = 'batch',
    zone?: string
  ): Promise<PickingWave> {
    const startTime = Date.now();

    try {
      // Get order details and create tasks
      const tasks = await this.createPickTasksFromOrders(orders, strategy, zone);

      // Group tasks by strategy
      const groupedTasks = await this.groupTasksByStrategy(tasks, strategy);

      // Create wave
      const wave: PickingWave = {
        waveId: `wave_${Date.now()}`,
        waveNumber: `W${Date.now()}`,
        status: 'planned',
        strategy,
        priority: this.calculateWavePriority(tasks),
        zone: zone || this.assignOptimalZone(tasks),
        tasks: groupedTasks,
        totalTasks: groupedTasks.length,
        completedTasks: 0,
        totalQuantity: groupedTasks.reduce((sum, task) => sum + task.quantity, 0),
        pickedQuantity: 0,
        assignedPickers: [],
        estimatedDuration: this.estimateWaveDuration(groupedTasks, strategy),
        createdAt: new Date()
      };

      // Store wave
      this.activeWaves.set(wave.waveId, wave);

      // Publish event
      await this.publishWaveCreatedEvent(wave);

      this.metrics.recordDatabaseQueryDuration('picking.wave_creation', (Date.now() - startTime) / 1000, {});
      this.metrics.incrementPickTasks('created', { strategy });

      return wave;
    } catch (error) {
      this.metrics.incrementErrorCount('picking.wave_creation_failed', { error: 'wave_creation_error' });
      throw error;
    }
  }

  /**
   * Release wave for picking
   */
  async releaseWave(waveId: string): Promise<void> {
    const wave = this.activeWaves.get(waveId);
    if (!wave) {
      throw new Error(`Wave ${waveId} not found`);
    }

    if (wave.status !== 'planned') {
      throw new Error(`Wave ${waveId} is not in planned status`);
    }

    wave.status = 'released';
    wave.releasedAt = new Date();

    // Assign pickers to tasks
    await this.assignPickersToWave(wave);

    // Publish task creation events
    for (const task of wave.tasks) {
      await this.publishPickTaskCreatedEvent(task);
    }
  }

  /**
   * Start picking task
   */
  async startPickTask(taskId: string, pickerId: string): Promise<void> {
    const task = await this.findPickTask(taskId);
    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }

    if (task.status !== 'pending') {
      throw new Error(`Task ${taskId} is not in pending status`);
    }

    task.status = 'in_progress';
    task.assignedTo = pickerId;
    task.startedAt = new Date();

    // Update wave progress
    if (task.waveId) {
      const wave = this.activeWaves.get(task.waveId);
      if (wave) {
        wave.status = 'in_progress';
      }
    }
  }

  /**
   * Complete picking task
   */
  async completePickTask(
    taskId: string,
    pickedQuantity: number,
    actualTime?: number,
    qualityChecks?: PickTask['qualityChecks']
  ): Promise<void> {
    const startTime = Date.now();
    const task = await this.findPickTask(taskId);

    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }

    if (task.status !== 'in_progress') {
      throw new Error(`Task ${taskId} is not in progress`);
    }

    // Validate picked quantity
    if (pickedQuantity > task.quantity) {
      throw new Error('Picked quantity cannot exceed required quantity');
    }

    task.pickedQuantity = pickedQuantity;
    task.actualTime = actualTime || (task.startedAt ? (Date.now() - task.startedAt.getTime()) / 1000 : 0);
    task.completedAt = new Date();

    if (qualityChecks) {
      task.qualityChecks = qualityChecks;
    }

    // Determine status based on quantity and quality
    if (pickedQuantity === 0) {
      task.status = 'short';
    } else if (pickedQuantity < task.quantity) {
      task.status = 'short';
    } else if (qualityChecks && qualityChecks.some(check => !check.passed)) {
      task.status = 'damaged';
    } else {
      task.status = 'completed';
    }

    // Update wave progress
    if (task.waveId) {
      await this.updateWaveProgress(task.waveId);
    }

    // Publish completion event
    await this.publishPickCompletedEvent(task);

    // Update picker performance
    if (task.assignedTo) {
      await this.updatePickerPerformance(task.assignedTo, task);
    }

    this.metrics.recordDatabaseQueryDuration('picking.task_completion', (Date.now() - startTime) / 1000, {});
    this.metrics.incrementPickTasks('completed', { status: task.status });
  }

  /**
   * Get picker performance metrics
   */
  async getPickerPerformance(pickerId: string, period: 'shift' | 'day' | 'week' = 'shift'): Promise<PickerPerformance> {
    const startTime = Date.now();

    try {
      const performance = await this.calculatePickerPerformance(pickerId, period);

      this.metrics.recordDatabaseQueryDuration('picking.performance_calculation', (Date.now() - startTime) / 1000, {});

      return performance;
    } catch (error) {
      this.metrics.incrementErrorCount('picking.performance_calculation_failed', { error: 'performance_calculation_error' });
      throw error;
    }
  }

  /**
   * Get zone utilization and performance
   */
  async getZonePerformance(zoneId: string): Promise<{
    zone: ZoneConfiguration;
    currentUtilization: number;
    activePickers: number;
    tasksInProgress: number;
    tasksCompleted: number;
    averageProductivity: number;
    bottlenecks: string[];
  }> {
    const zone = this.zones.get(zoneId);
    if (!zone) {
      throw new Error(`Zone ${zoneId} not found`);
    }

    // Calculate current metrics
    const activeTasks = await this.getActiveTasksInZone(zoneId);
    const completedTasks = await this.getCompletedTasksInZone(zoneId, new Date(Date.now() - 24 * 60 * 60 * 1000)); // Last 24 hours

    const utilization = (activeTasks.length / zone.capacity.maxConcurrentPickers) * 100;
    const activePickers = new Set(activeTasks.map(task => task.assignedTo).filter(Boolean)).size;

    // Calculate average productivity (picks per hour)
    const totalPicks = completedTasks.reduce((sum, task) => sum + task.pickedQuantity, 0);
    const totalTime = completedTasks.reduce((sum, task) => sum + (task.actualTime || 0), 0) / 3600; // Convert to hours
    const averageProductivity = totalTime > 0 ? totalPicks / totalTime : 0;

    // Identify bottlenecks
    const bottlenecks: string[] = [];
    if (utilization > 90) bottlenecks.push('High utilization');
    if (activePickers < zone.capacity.maxConcurrentPickers * 0.5) bottlenecks.push('Low picker utilization');
    if (averageProductivity < zone.capacity.maxTasksPerHour * 0.7) bottlenecks.push('Low productivity');

    return {
      zone,
      currentUtilization: utilization,
      activePickers,
      tasksInProgress: activeTasks.length,
      tasksCompleted: completedTasks.length,
      averageProductivity,
      bottlenecks
    };
  }

  /**
   * Optimize picking routes within zone
   */
  async optimizePickingRoute(tasks: PickTask[]): Promise<PickTask[]> {
    if (tasks.length <= 1) return tasks;

    // Simple nearest neighbor algorithm for route optimization
    const optimizedTasks: PickTask[] = [];
    const remainingTasks = [...tasks];

    // Start from first task
    let currentTask = remainingTasks.shift()!;
    optimizedTasks.push(currentTask);

    while (remainingTasks.length > 0) {
      // Find nearest task
      let nearestIndex = 0;
      let nearestDistance = this.calculateDistance(
        currentTask.location,
        remainingTasks[0].location
      );

      for (let i = 1; i < remainingTasks.length; i++) {
        const distance = this.calculateDistance(
          currentTask.location,
          remainingTasks[i].location
        );
        if (distance < nearestDistance) {
          nearestDistance = distance;
          nearestIndex = i;
        }
      }

      currentTask = remainingTasks.splice(nearestIndex, 1)[0];
      optimizedTasks.push(currentTask);
    }

    // Update sequence numbers
    optimizedTasks.forEach((task, index) => {
      task.sequence = index + 1;
    });

    return optimizedTasks;
  }

  /**
   * Create batch picking plan
   */
  async createBatchPickingPlan(orders: string[]): Promise<PickingBatch> {
    const startTime = Date.now();

    try {
      // Analyze orders for batching opportunities
      const orderDetails = await this.getOrderDetails(orders);
      const batch: PickingBatch = {
        batchId: `batch_${Date.now()}`,
        batchNumber: `B${Date.now()}`,
        orders,
        skus: this.consolidateSkusForBatching(orderDetails),
        status: 'planned',
        priority: this.calculateBatchPriority(orderDetails),
        createdAt: new Date()
      };

      this.metrics.recordDatabaseQueryDuration('picking.batch_creation', (Date.now() - startTime) / 1000, {});

      return batch;
    } catch (error) {
      this.metrics.incrementErrorCount('picking.batch_creation_failed', { error: 'batch_creation_error' });
      throw error;
    }
  }

  // Private helper methods

  private async createPickTasksFromOrders(
    orders: string[],
    strategy: PickingWave['strategy'],
    zone?: string
  ): Promise<PickTask[]> {
    const tasks: PickTask[] = [];

    for (const orderId of orders) {
      const orderLines = await this.getOrderLines(orderId);

      for (const line of orderLines) {
        // Find available inventory
        const inventory = await this.getAvailableInventory(line.sku, zone);

        for (const inv of inventory) {
          if (line.quantity <= 0) break;

          const pickQuantity = Math.min(line.quantity, inv.availableQty);
          const task: PickTask = {
            taskId: `pick_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            orderId,
            sku: line.sku,
            location: inv.location,
            lot: inv.lot,
            serial: inv.serial,
            quantity: pickQuantity,
            pickedQuantity: 0,
            status: 'pending',
            priority: line.priority || 5,
            zone: zone || this.getZoneForLocation(inv.location),
            sequence: 0, // Will be set during optimization
            estimatedTime: this.estimatePickTime(pickQuantity, strategy),
            createdAt: new Date()
          };

          tasks.push(task);
          line.quantity -= pickQuantity;
        }
      }
    }

    return tasks;
  }

  private async groupTasksByStrategy(tasks: PickTask[], strategy: PickingWave['strategy']): Promise<PickTask[]> {
    switch (strategy) {
      case 'batch':
        return this.optimizeForBatchPicking(tasks);
      case 'zone':
        return this.optimizeForZonePicking(tasks);
      case 'cluster':
        return await this.optimizeForClusterPicking(tasks);
      default:
        return tasks.sort((a, b) => b.priority - a.priority);
    }
  }

  private optimizeForBatchPicking(tasks: PickTask[]): PickTask[] {
    // Group by SKU and location for batch picking
    const groupedTasks: PickTask[] = [];
    const skuLocationMap = new Map<string, PickTask>();

    for (const task of tasks) {
      const key = `${task.sku}-${task.location}`;
      const existing = skuLocationMap.get(key);

      if (existing) {
        existing.quantity += task.quantity;
        // Combine orders (would need more complex logic in real implementation)
      } else {
        skuLocationMap.set(key, { ...task });
      }
    }

    return Array.from(skuLocationMap.values());
  }

  private optimizeForZonePicking(tasks: PickTask[]): PickTask[] {
    // Sort by zone and then optimize routes within zones
    return tasks.sort((a, b) => {
      if (a.zone !== b.zone) return a.zone.localeCompare(b.zone);
      return this.calculateDistance('START', a.location) - this.calculateDistance('START', b.location);
    });
  }

  private async optimizeForClusterPicking(tasks: PickTask[]): Promise<PickTask[]> {
    // Group nearby locations for cluster picking
    return await this.optimizePickingRoute(tasks);
  }

  private calculateWavePriority(tasks: PickTask[]): number {
    const avgPriority = tasks.reduce((sum, task) => sum + task.priority, 0) / tasks.length;
    return Math.round(avgPriority);
  }

  private assignOptimalZone(tasks: PickTask[]): string {
    // Simple zone assignment based on majority
    const zoneCounts = new Map<string, number>();
    for (const task of tasks) {
      zoneCounts.set(task.zone, (zoneCounts.get(task.zone) || 0) + 1);
    }

    let maxZone = 'DEFAULT';
    let maxCount = 0;
    for (const [zone, count] of Array.from(zoneCounts.entries())) {
      if (count > maxCount) {
        maxCount = count;
        maxZone = zone;
      }
    }

    return maxZone;
  }

  private estimateWaveDuration(tasks: PickTask[], strategy: PickingWave['strategy']): number {
    const totalTime = tasks.reduce((sum, task) => sum + task.estimatedTime, 0);
    const strategyMultiplier = strategy === 'batch' ? 0.8 : strategy === 'zone' ? 0.9 : 1.0;
    return Math.ceil((totalTime * strategyMultiplier) / 60); // Convert to minutes
  }

  private async assignPickersToWave(wave: PickingWave): Promise<void> {
    const zone = this.zones.get(wave.zone);
    if (!zone) return;

    // Simple assignment: assign to available pickers
    const availablePickers = zone.pickers.slice(0, Math.min(zone.capacity.maxConcurrentPickers, wave.tasks.length));
    wave.assignedPickers = availablePickers;

    // Assign tasks to pickers
    wave.tasks.forEach((task, index) => {
      task.assignedTo = availablePickers[index % availablePickers.length];
    });
  }

  private estimatePickTime(quantity: number, strategy: PickingWave['strategy']): number {
    const baseTimePerUnit = 2; // seconds per unit
    const strategyMultiplier = strategy === 'batch' ? 1.2 : strategy === 'zone' ? 1.1 : 1.0;
    return Math.ceil(quantity * baseTimePerUnit * strategyMultiplier);
  }

  private calculateDistance(from: string, to: string): number {
    // Mock distance calculation - would use actual warehouse layout
    if (from === 'START' || to === 'START') return 0;
    // Simple mock: assume locations are A-01-01-01 format
    return Math.abs(this.locationToNumber(from) - this.locationToNumber(to));
  }

  private locationToNumber(location: string): number {
    // Convert location code to number for distance calculation
    const parts = location.split('-');
    if (parts.length >= 3) {
      return parseInt(parts[1]) * 10000 + parseInt(parts[2]) * 100 + parseInt(parts[3] || '0');
    }
    return 0;
  }

  private async findPickTask(taskId: string): Promise<PickTask | null> {
    // Search in all waves
    for (const wave of Array.from(this.activeWaves.values())) {
      const task = wave.tasks.find(t => t.taskId === taskId);
      if (task) return task;
    }
    return null;
  }

  private async updateWaveProgress(waveId: string): Promise<void> {
    const wave = this.activeWaves.get(waveId);
    if (!wave) return;

    wave.completedTasks = wave.tasks.filter(task => task.status === 'completed').length;
    wave.pickedQuantity = wave.tasks.reduce((sum, task) => sum + task.pickedQuantity, 0);

    if (wave.completedTasks === wave.totalTasks) {
      wave.status = 'completed';
      wave.completedAt = new Date();
      wave.actualDuration = wave.releasedAt ?
        (wave.completedAt.getTime() - wave.releasedAt.getTime()) / (1000 * 60) : undefined;

      // Calculate productivity
      wave.productivity = await this.calculateWaveProductivity(wave);

      await this.publishWaveCompletedEvent(wave);
    }
  }

  private async calculateWaveProductivity(wave: PickingWave): Promise<PickingWave['productivity']> {
    if (!wave.actualDuration || wave.actualDuration === 0) return undefined;

    const totalPicks = wave.tasks.reduce((sum, task) => sum + task.pickedQuantity, 0);
    const totalLines = wave.tasks.length;
    const completedTasks = wave.tasks.filter(task => task.status === 'completed');

    const accuracy = completedTasks.length / wave.tasks.length;
    const picksPerHour = (totalPicks / wave.actualDuration) * 60;
    const linesPerHour = (totalLines / wave.actualDuration) * 60;
    const averageTimePerPick = wave.tasks
      .filter(task => task.actualTime)
      .reduce((sum, task) => sum + (task.actualTime || 0), 0) / completedTasks.length;

    return {
      picksPerHour,
      linesPerHour,
      accuracy,
      averageTimePerPick
    };
  }

  private async updatePickerPerformance(pickerId: string, task: PickTask): Promise<void> {
    // Mock implementation - would update persistent storage
    console.log(`Updated performance for picker ${pickerId}: task ${task.taskId}`);
  }

  private async calculatePickerPerformance(pickerId: string, period: string): Promise<PickerPerformance> {
    // Mock implementation
    return {
      pickerId,
      name: `Picker ${pickerId}`,
      zone: 'A',
      shift: 'morning',
      metrics: {
        totalPicks: 150,
        totalLines: 45,
        totalQuantity: 150,
        picksPerHour: 75,
        linesPerHour: 22.5,
        accuracy: 98.5,
        averageTimePerPick: 48, // seconds
        totalTimeWorked: 120 // minutes
      },
      performance: {
        score: 92,
        grade: 'A',
        trends: {
          picksPerHour: [70, 72, 75, 78, 75],
          accuracy: [97, 98, 98.5, 99, 98.5],
          timePerPick: [52, 50, 48, 46, 48]
        }
      },
      currentSession: {
        startTime: new Date(),
        tasksCompleted: 12,
        totalPicks: 45,
        errors: 0
      }
    };
  }

  private async getActiveTasksInZone(zoneId: string): Promise<PickTask[]> {
    const tasks: PickTask[] = [];
    for (const wave of Array.from(this.activeWaves.values())) {
      if (wave.zone === zoneId) {
        tasks.push(...wave.tasks.filter(task => task.status === 'in_progress'));
      }
    }
    return tasks;
  }

  private async getCompletedTasksInZone(zoneId: string, since: Date): Promise<PickTask[]> {
    const tasks: PickTask[] = [];
    for (const wave of Array.from(this.activeWaves.values())) {
      if (wave.zone === zoneId) {
        tasks.push(...wave.tasks.filter(task =>
          task.status === 'completed' &&
          task.completedAt &&
          task.completedAt >= since
        ));
      }
    }
    return tasks;
  }

  private getZoneForLocation(location: string): string {
    // Mock zone assignment
    return location.startsWith('A') ? 'A' : 'B';
  }

  private async getOrderLines(orderId: string): Promise<Array<{
    sku: string;
    quantity: number;
    priority?: number;
  }>> {
    // Mock order lines
    return [
      { sku: 'WIDGET-001', quantity: 5, priority: 5 },
      { sku: 'GADGET-002', quantity: 3, priority: 3 }
    ];
  }

  private async getAvailableInventory(sku: string, zone?: string): Promise<Array<{
    location: string;
    availableQty: number;
    lot?: string;
    serial?: string;
  }>> {
    // Mock inventory
    return [
      { location: 'A-01-01-01', availableQty: 50, lot: 'LOT-001' },
      { location: 'A-01-01-02', availableQty: 30, lot: 'LOT-002' }
    ].filter(inv => !zone || this.getZoneForLocation(inv.location) === zone);
  }

  private async getOrderDetails(orders: string[]): Promise<any[]> {
    // Mock order details
    return orders.map(orderId => ({
      orderId,
      lines: [
        { sku: 'WIDGET-001', quantity: 5 },
        { sku: 'GADGET-002', quantity: 3 }
      ]
    }));
  }

  private consolidateSkusForBatching(orderDetails: any[]): PickingBatch['skus'] {
    const skuMap = new Map<string, {
      totalQuantity: number;
      locations: Array<{ location: string; quantity: number; lot?: string }>;
    }>();

    for (const order of orderDetails) {
      for (const line of order.lines) {
        const existing = skuMap.get(line.sku) || {
          totalQuantity: 0,
          locations: []
        };

        existing.totalQuantity += line.quantity;
        // Add location logic here
        existing.locations.push({
          location: 'A-01-01-01',
          quantity: line.quantity,
          lot: 'LOT-001'
        });

        skuMap.set(line.sku, existing);
      }
    }

    return Array.from(skuMap.entries()).map(([sku, data]) => ({ sku, ...data }));
  }

  private calculateBatchPriority(orderDetails: any[]): number {
    // Calculate based on order priorities
    return 5; // Mock
  }

  private initializeDefaultZones(): void {
    const zones: ZoneConfiguration[] = [
      {
        zoneId: 'A',
        zoneName: 'Forward Zone A',
        type: 'forward',
        pickers: ['picker1', 'picker2', 'picker3'],
        locations: ['A-01-01-01', 'A-01-01-02', 'A-01-02-01'],
        capacity: {
          maxConcurrentPickers: 3,
          maxTasksPerHour: 120
        },
        routing: {
          entryPoint: 'A-ENTRY',
          exitPoint: 'A-EXIT',
          optimalPath: ['A-01-01-01', 'A-01-01-02', 'A-01-02-01']
        },
        active: true
      },
      {
        zoneId: 'B',
        zoneName: 'Reserve Zone B',
        type: 'reserve',
        pickers: ['picker4', 'picker5'],
        locations: ['B-01-01-01', 'B-01-01-02', 'B-02-01-01'],
        capacity: {
          maxConcurrentPickers: 2,
          maxTasksPerHour: 80
        },
        routing: {
          entryPoint: 'B-ENTRY',
          exitPoint: 'B-EXIT',
          optimalPath: ['B-01-01-01', 'B-01-01-02', 'B-02-01-01']
        },
        active: true
      }
    ];

    zones.forEach(zone => this.zones.set(zone.zoneId, zone));
  }

  // Event publishing methods
  private async publishWaveCreatedEvent(wave: PickingWave): Promise<void> {
    const event: WaveCreatedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.wave.created',
      aggregateId: wave.waveId,
      aggregateType: 'PickingWave',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      type: 'inventory.wave.created',
      occurredAt: new Date(),
      aggregateVersion: 1,
      waveId: wave.waveId,
      waveNumber: wave.waveNumber,
      strategy: wave.strategy,
      totalTasks: wave.totalTasks,
      totalQuantity: wave.totalQuantity,
      zone: wave.zone
    };

    await this.eventBus.publish(event);
  }

  private async publishPickTaskCreatedEvent(task: PickTask): Promise<void> {
    const event: PickTaskCreatedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.pick.created',
      type: 'inventory.pick.created',
      aggregateId: task.taskId,
      aggregateType: 'PickTask',
      eventVersion: 1,
      occurredOn: new Date(),
      occurredAt: new Date(),
      aggregateVersion: 1,
      tenantId: 'default',
      orderId: task.orderId,
      waveId: task.waveId,
      tasks: [{
        taskId: task.taskId,
        sku: task.sku,
        location: task.location,
        lot: task.lot,
        serial: task.serial,
        quantity: task.quantity,
        priority: task.priority
      }]
    };

    await this.eventBus.publish(event);
  }

  private async publishPickCompletedEvent(task: PickTask): Promise<void> {
    const event: PickCompletedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.pick.completed',
      aggregateId: task.taskId,
      aggregateType: 'PickTask',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      type: 'inventory.pick.completed',
      occurredAt: new Date(),
      aggregateVersion: 1,
      taskId: task.taskId,
      orderId: task.orderId,
      sku: task.sku,
      quantity: task.pickedQuantity,
      pickedBy: task.assignedTo || 'unknown',
      duration: task.actualTime || 0,
      accuracy: task.pickedQuantity >= task.quantity ? 100 : (task.pickedQuantity / task.quantity) * 100
    };

    await this.eventBus.publish(event);
  }

  private async publishWaveCompletedEvent(wave: PickingWave): Promise<void> {
    const event: WaveCompletedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.wave.completed',
      aggregateId: wave.waveId,
      aggregateType: 'PickingWave',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      type: 'inventory.wave.completed',
      occurredAt: new Date(),
      aggregateVersion: 1,
      waveId: wave.waveId,
      completedTasks: wave.completedTasks,
      totalTasks: wave.totalTasks,
      duration: wave.actualDuration || 0,
      productivity: wave.productivity?.picksPerHour || 0
    };

    await this.eventBus.publish(event);
  }
}