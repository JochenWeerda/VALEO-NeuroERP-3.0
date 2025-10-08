/**
 * VALEO NeuroERP 3.0 - Putaway & Slotting Service
 *
 * Intelligent putaway planning and slotting optimization for WMS operations
 */

import { injectable } from 'inversify';
import { EventBus } from '../infrastructure/event-bus/event-bus';
import { InventoryMetricsService } from '../infrastructure/observability/metrics-service';
import { PutawayPlannedEvent, SlottingUpdatedEvent } from '../core/domain-events/inventory-domain-events';
import { Sku } from '../core/entities/sku';
import { Location } from '../core/entities/location';

export interface PutawayTask {
  taskId: string;
  asnId: string;
  sku: string;
  gtin?: string;
  quantity: number;
  uom: string;
  fromLocation: string; // Usually receiving dock/staging
  toLocation: string;
  priority: number;
  strategy: PutawayStrategy;
  estimatedTime: number; // minutes
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  assignedTo?: string;
  createdAt: Date;
  completedAt?: Date;
}

export interface SlottingRecommendation {
  sku: string;
  currentLocation?: string;
  recommendedLocation: string;
  confidence: number;
  reasoning: string[];
  expectedImprovement: {
    travelTime: number; // minutes saved per pick
    throughput: number; // additional picks per hour
    spaceUtilization: number; // percentage improvement
  };
  aiFeatures: Record<string, unknown>;
}

export type PutawayStrategy =
  | 'velocity'      // Fast-moving items to prime locations
  | 'abc'          // ABC classification based slotting
  | 'temp_zone'    // Temperature zone compatibility
  | 'hazmat'       // Hazardous materials isolation
  | 'size'         // Size-based slotting
  | 'family'       // Product family grouping
  | 'manual';      // Manual assignment

export interface SlottingPolicy {
  policyId: string;
  name: string;
  description: string;
  strategy: PutawayStrategy;
  rules: SlottingRule[];
  zones: string[];
  active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface SlottingRule {
  ruleId: string;
  condition: {
    skuCriteria?: {
      abcClass?: 'A' | 'B' | 'C';
      velocityClass?: 'X' | 'Y' | 'Z';
      category?: string;
      tempZone?: string;
      hazmat?: boolean;
    };
    locationCriteria?: {
      zone?: string;
      type?: string;
      capacity?: {
        minUtilization?: number;
        maxUtilization?: number;
      };
    };
  };
  action: {
    priority: number;
    preferredZones: string[];
    avoidZones?: string[];
    maxDistance?: number;
  };
  weight: number; // For rule prioritization
}

export interface AsnDetails {
  asnId: string;
  dock: string;
  lines: Array<{
    sku: string;
    gtin?: string;
    quantity: number;
    uom: string;
  }>;
}

// Constants
const RANDOM_ID_LENGTH = 9;
const RANDOM_ID_START = 2;
const RANDOM_BASE = 36;
const MS_TO_SECONDS = 1000;
const AI_CONFIDENCE_DEFAULT = 0.87;
const DISTANCE_TO_TIME_FACTOR = 100; // 100m = 1 minute
const SPACE_UTILIZATION_IMPROVEMENT = 5.2;
const VELOCITY_SCORE_X = 1.0;
const VELOCITY_SCORE_Y = 0.7;
const VELOCITY_SCORE_Z = 0.3;
const CURRENT_UTILIZATION_DEFAULT = 78.5;
const OPTIMAL_UTILIZATION_DEFAULT = 83.7;
const ABC_SCORE_A = 100;
const ABC_SCORE_B = 75;
const ABC_SCORE_C = 50;
const DISTANCE_PENALTY_FACTOR = 0.1;
const VELOCITY_PRIME_SCORE = 100;
const ZONE_A_BONUS = 50;
const ZONE_B_BONUS = 25;
const BASE_PRIORITY = 5;
const VELOCITY_PRIORITY_BONUS = 10;
const HAZMAT_PRIORITY_BONUS = 15;
const TEMP_ZONE_PRIORITY_BONUS = 8;
const MAX_PRIORITY = 20;
const BASE_PUTAWAY_TIME = 2; // minutes
const UNITS_PER_MINUTE = 10;
const HAZMAT_TIME_MULTIPLIER = 1.5;
const STANDARD_TIME_MULTIPLIER = 1.0;
const MOCK_DISTANCE_REDUCTION = 50;
const MOCK_THROUGHPUT_INCREASE = 5;
const VELOCITY_RULE_PRIORITY = 10;
const VELOCITY_RULE_WEIGHT = 100;

@injectable()
export class PutawaySlottingService {
  private readonly metrics = new InventoryMetricsService();
  private readonly slottingPolicies: Map<string, SlottingPolicy> = new Map();

  constructor(
    private readonly eventBus: EventBus
  ) {
    this.initializeDefaultPolicies();
  }

  /**
   * Plan putaway tasks for received goods
   */
  async planPutaway(asnId: string, strategy: PutawayStrategy = 'velocity'): Promise<PutawayTask[]> {
    const startTime = Date.now();

    try {
      // Get ASN details (would come from receiving service)
      const asnDetails = await this.getAsnDetails(asnId);
      if (asnDetails == null) {
        throw new Error(`ASN ${asnId} not found`);
      }

      const tasks: PutawayTask[] = [];

      for (const line of asnDetails.lines) {
        // Find optimal location for this SKU
        const optimalLocation = await this.findOptimalLocation(
          line.sku,
          line.quantity,
          strategy,
          asnDetails.dock
        );

        if (optimalLocation == null) {
          throw new Error(`No suitable location found for SKU ${line.sku}`);
        }

        const task: PutawayTask = {
          taskId: `putaway_${Date.now()}_${Math.random().toString(RANDOM_BASE).substr(RANDOM_ID_START, RANDOM_ID_LENGTH)}`,
          asnId,
          sku: line.sku,
          gtin: line.gtin,
          quantity: line.quantity,
          uom: line.uom,
          fromLocation: asnDetails.dock,
          toLocation: optimalLocation.code,
          priority: this.calculatePriority(line.sku, strategy),
          strategy,
          estimatedTime: this.estimatePutawayTime(line.quantity, strategy),
          status: 'planned',
          createdAt: new Date()
        };

        tasks.push(task);
      }

      // Sort tasks by priority
      tasks.sort((a, b) => b.priority - a.priority);

      // Publish event
      await this.publishPutawayPlannedEvent(asnId, tasks);

      this.metrics.recordPutawayTime('putaway.plan_putaway', (Date.now() - startTime) / MS_TO_SECONDS, { strategy: strategy });
      this.metrics.incrementPutawayTasks('putaway.planned', { strategy: strategy });

      return tasks;
    } catch (error) {
      this.metrics.incrementErrorCount('putaway.planning_failed', { error: 'planning_error' });
      throw error;
    }
  }

  /**
   * Generate slotting recommendations using AI
   */
  async generateSlottingRecommendations(skus?: string[]): Promise<SlottingRecommendation[]> {
    const startTime = Date.now();

    try {
      const targetSkus = skus ?? await this.getAllSkus();
      const recommendations: SlottingRecommendation[] = [];

      for (const sku of targetSkus) {
        const recommendation = await this.generateRecommendationForSku(sku);
        if (recommendation) {
          recommendations.push(recommendation);
        }
      }

      // Sort by expected improvement
      recommendations.sort((a, b) => {
        const aScore = a.expectedImprovement.travelTime + a.expectedImprovement.throughput;
        const bScore = b.expectedImprovement.travelTime + b.expectedImprovement.throughput;
        return bScore - aScore;
      });

      this.metrics.recordDatabaseQueryDuration('slotting.ai_recommendation', (Date.now() - startTime) / MS_TO_SECONDS, {});

      return recommendations;
    } catch (error) {
      this.metrics.incrementErrorCount('slotting.recommendation_failed', { error: 'recommendation_error' });
      throw error;
    }
  }

  /**
   * Apply slotting recommendation
   */
  async applySlottingRecommendation(recommendation: SlottingRecommendation): Promise<void> {
    const startTime = Date.now();

    try {
      // Update SKU location mapping (would update database)
      await this.updateSkuLocation(recommendation.sku, recommendation.recommendedLocation);

      // Publish slotting updated event
      await this.publishSlottingUpdatedEvent(recommendation);

      this.metrics.recordDatabaseQueryDuration('slotting.apply_recommendation', (Date.now() - startTime) / MS_TO_SECONDS, { sku: recommendation.sku });
    } catch (error) {
      this.metrics.incrementErrorCount('slotting.apply_failed', { error: 'apply_error' });
      throw error;
    }
  }

  /**
   * Get slotting analytics
   */
  async getSlottingAnalytics(): Promise<{
    totalLocations: number;
    utilizedLocations: number;
    averageUtilization: number;
    slottingEfficiency: number;
    travelTimeReduction: number;
    topRecommendations: SlottingRecommendation[];
  }> {
    // Mock analytics - would calculate from actual data
    return {
      totalLocations: 1000,
      utilizedLocations: 850,
      averageUtilization: 85.2,
      slottingEfficiency: 92.5,
      travelTimeReduction: 15.3, // minutes per order
      topRecommendations: []
    };
  }

  /**
   * Create or update slotting policy
   */
  async createSlottingPolicy(policy: Omit<SlottingPolicy, 'policyId' | 'createdAt' | 'updatedAt'>): Promise<SlottingPolicy> {
    const newPolicy: SlottingPolicy = {
      ...policy,
      policyId: `policy_${Date.now()}`,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.slottingPolicies.set(newPolicy.policyId, newPolicy);
    return newPolicy;
  }

  /**
   * Find optimal location for SKU
   */
  private async findOptimalLocation(
    sku: string,
    quantity: number,
    strategy: PutawayStrategy,
    fromLocation: string
  ): Promise<Location | null> {
    const skuDetails = await this.getSkuDetails(sku);
    if (!skuDetails) return null;

    const availableLocations = await this.getAvailableLocations(skuDetails, quantity);

    if (availableLocations.length === 0) return null;

    switch (strategy) {
      case 'velocity':
        return this.findVelocityOptimalLocation(availableLocations, skuDetails, fromLocation);
      case 'abc':
        return this.findAbcOptimalLocation(availableLocations, skuDetails, fromLocation);
      case 'temp_zone':
        return this.findTempZoneOptimalLocation(availableLocations, skuDetails, fromLocation);
      case 'hazmat':
        return this.findHazmatOptimalLocation(availableLocations, skuDetails, fromLocation);
      default:
        return availableLocations[0] ?? null; // Simple fallback
    }
  }

  /**
   * Generate AI-powered recommendation for single SKU
   */
  private async generateRecommendationForSku(sku: string): Promise<SlottingRecommendation | null> {
    const skuDetails = await this.getSkuDetails(sku);
    if (!skuDetails) return null;

    const currentLocation = await this.getCurrentSkuLocation(sku);
    const optimalLocation = await this.findOptimalLocation(sku, 1, 'velocity', 'DOCK-01');

    if (!optimalLocation || optimalLocation.code === currentLocation) {
      return null;
    }

    // Calculate expected improvements
    const distanceReduction = currentLocation ?
      await this.calculateDistanceReduction(currentLocation, optimalLocation.code) : 0;

    const throughputIncrease = await this.calculateThroughputIncrease(sku, optimalLocation.code);

    return {
      sku,
      currentLocation: currentLocation ?? '',
      recommendedLocation: optimalLocation.code,
      confidence: AI_CONFIDENCE_DEFAULT, // AI confidence score
      reasoning: [
        `Velocity class ${skuDetails.velocityClass} items should be in prime locations`,
        `Reduces travel distance by ${distanceReduction}m`,
        `Expected throughput increase: ${throughputIncrease} picks/hour`
      ],
      expectedImprovement: {
        travelTime: distanceReduction / DISTANCE_TO_TIME_FACTOR, // Rough estimate: 100m = 1 minute
        throughput: throughputIncrease,
        spaceUtilization: SPACE_UTILIZATION_IMPROVEMENT // percentage improvement
      },
      aiFeatures: {
        velocityScore: skuDetails.velocityClass === 'X' ? VELOCITY_SCORE_X : skuDetails.velocityClass === 'Y' ? VELOCITY_SCORE_Y : VELOCITY_SCORE_Z,
        currentUtilization: CURRENT_UTILIZATION_DEFAULT,
        optimalUtilization: OPTIMAL_UTILIZATION_DEFAULT,
        distanceToPrime: distanceReduction
      }
    };
  }

  /**
   * Velocity-based optimal location finding
   */
  private findVelocityOptimalLocation(
    locations: Location[],
    sku: Sku,
    fromLocation: string
  ): Location | null {
    // Sort by distance from prime picking areas and velocity preference
    const sorted = locations.sort((a, b) => {
      const aScore = this.calculateVelocityScore(a, sku, fromLocation);
      const bScore = this.calculateVelocityScore(b, sku, fromLocation);
      return bScore - aScore; // Higher score = better
    });
    return sorted[0] ?? null;
  }

  /**
   * ABC-based optimal location finding
   */
  private findAbcOptimalLocation(
    locations: Location[],
    sku: Sku,
    fromLocation: string
  ): Location | null {
    // Sort by ABC zone preference and distance
    const sorted = locations.sort((a, b) => {
      const aScore = this.calculateAbcScore(a, sku, fromLocation);
      const bScore = this.calculateAbcScore(b, sku, fromLocation);
      return bScore - aScore;
    });
    return sorted[0] ?? null;
  }

  /**
   * Temperature zone-based optimal location finding
   */
  private findTempZoneOptimalLocation(
    locations: Location[],
    sku: Sku,
    fromLocation: string
  ): Location | null {
    // Filter locations that support the required temperature zone
    const compatibleLocations = locations.filter(loc =>
      loc.supportsTemperature(sku.tempZone)
    );

    if (compatibleLocations.length === 0) return null;

    // Sort by distance
    const sorted = compatibleLocations.sort((a, b) => {
      const aDistance = a.getDistanceTo(this.createLocationFromCode(fromLocation));
      const bDistance = b.getDistanceTo(this.createLocationFromCode(fromLocation));
      return aDistance - bDistance;
    });

    return sorted[0] ?? null;
  }

  /**
   * Hazardous materials optimal location finding
   */
  private findHazmatOptimalLocation(
    locations: Location[],
    sku: Sku,
    fromLocation: string
  ): Location | null {
    // Filter locations that allow hazardous materials
    const hazmatLocations = locations.filter(loc => loc.hazmatAllowed);

    if (hazmatLocations.length === 0) return null;

    // Sort by distance from staging area
    const sorted = hazmatLocations.sort((a, b) => {
      const aDistance = a.getDistanceTo(this.createLocationFromCode(fromLocation));
      const bDistance = b.getDistanceTo(this.createLocationFromCode(fromLocation));
      const aDist = Number.isNaN(aDistance) ? Number.MAX_VALUE : aDistance;
      const bDist = Number.isNaN(bDistance) ? Number.MAX_VALUE : bDistance;
      return aDist - bDist;
    });

    return sorted[0] ?? null;
  }

  /**
   * Calculate ABC score for location
   */
  private calculateAbcScore(location: Location, sku: Sku, fromLocation: string): number {
    let score = 0;

    // ABC class preference
    if (sku.abcClass === 'A' && location.zone === 'A') score += ABC_SCORE_A;
    else if (sku.abcClass === 'B' && location.zone === 'B') score += ABC_SCORE_B;
    else if (sku.abcClass === 'C' && location.zone === 'C') score += ABC_SCORE_C;

    // Distance penalty
    const distance = location.getDistanceTo(this.createLocationFromCode(fromLocation));
    score -= distance * DISTANCE_PENALTY_FACTOR;

    return score;
  }

  /**
   * Calculate velocity score for location
   */
  private calculateVelocityScore(location: Location, sku: Sku, fromLocation: string): number {
    let score = 0;

    // Prime locations for fast-moving items
    if (sku.isFastMoving() && location.isPickLocation()) {
      score += VELOCITY_PRIME_SCORE;
    }

    // Distance penalty
    const distance = location.getDistanceTo(this.createLocationFromCode(fromLocation));
    score -= distance * DISTANCE_PENALTY_FACTOR;

    // Zone preference
    if (location.zone === 'A') score += ZONE_A_BONUS;
    else if (location.zone === 'B') score += ZONE_B_BONUS;

    return score;
  }

  /**
   * Calculate priority for putaway task
   */
  private calculatePriority(sku: string, strategy: PutawayStrategy): number {
    // Base priority
    let priority = BASE_PRIORITY;

    // Strategy-based adjustments
    switch (strategy) {
      case 'velocity':
        priority += VELOCITY_PRIORITY_BONUS; // High priority for fast-moving items
        break;
      case 'hazmat':
        priority += HAZMAT_PRIORITY_BONUS; // Critical for hazardous materials
        break;
      case 'temp_zone':
        priority += TEMP_ZONE_PRIORITY_BONUS; // Important for temperature control
        break;
      case 'abc':
        // No additional adjustment by default
        break;
      case 'size':
        // No additional adjustment by default
        break;
      case 'family':
        // No additional adjustment by default
        break;
      case 'manual':
        // Manual strategy keeps base priority
        break;
      default:
        // Ensure exhaustiveness
        break;
    }

    return Math.min(priority, MAX_PRIORITY); // Cap at 20
  }

  /**
   * Estimate putaway time
   */
  private estimatePutawayTime(quantity: number, strategy: PutawayStrategy): number {
    const baseTime = BASE_PUTAWAY_TIME; // minutes
    const quantityFactor = Math.ceil(quantity / UNITS_PER_MINUTE); // 10 units per minute
    const strategyFactor = strategy === 'hazmat' ? HAZMAT_TIME_MULTIPLIER : STANDARD_TIME_MULTIPLIER;

    return Math.ceil(baseTime * quantityFactor * strategyFactor);
  }

  // Mock data methods (would be replaced with actual database calls)
  private async getAsnDetails(asnId: string): Promise<AsnDetails> {
    return {
      asnId,
      dock: 'DOCK-01',
      lines: [
        { sku: 'WIDGET-001', gtin: '1234567890123', quantity: 100, uom: 'EA' }
      ]
    };
  }

  private async getSkuDetails(sku: string): Promise<Sku | null> {
    // Mock SKU data
    return Sku.create({
      sku,
      description: 'Test Widget',
      category: 'Widgets',
      uom: 'EA',
      tempZone: 'ambient',
      abcClass: 'A',
      velocityClass: 'X',
      active: true,
      hazmat: false,
      serialTracked: false,
      lotTracked: true
    });
  }

  private async getAvailableLocations(sku: Sku, quantity: number): Promise<Location[]> {
    // Mock locations
    return [
      Location.create({
        code: 'A-01-01-01',
        type: 'pick',
        zone: 'A',
        capacity: { maxQty: 1000, uom: 'EA' },
        active: true,
        blocked: false,
        tempControlled: false,
        hazmatAllowed: false
      })
    ].filter(loc => loc.canStoreSku({
      tempZone: sku.tempZone,
      hazmat: sku.hazmat,
      weight: 1,
      volume: 0.1
    }));
  }

  private async getAllSkus(): Promise<string[]> {
    return ['WIDGET-001', 'GADGET-002'];
  }

  private async getCurrentSkuLocation(sku: string): Promise<string | undefined> {
    return 'B-05-10-05'; // Mock current location
  }

  private async updateSkuLocation(sku: string, location: string): Promise<void> {
    // Implementation would update database
    // Logging removed as per lint rules
  }

  private async calculateDistanceReduction(from: string, to: string): Promise<number> {
    return MOCK_DISTANCE_REDUCTION; // Mock 50m reduction
  }

  private async calculateThroughputIncrease(sku: string, location: string): Promise<number> {
    return MOCK_THROUGHPUT_INCREASE; // Mock 5 additional picks per hour
  }

  private createLocationFromCode(code: string): Location {
    return Location.create({
      code,
      type: 'dock',
      zone: 'ambient',
      capacity: { maxQty: 10000, uom: 'EA' },
      active: true,
      blocked: false,
      tempControlled: false,
      hazmatAllowed: false
    });
  }

  private initializeDefaultPolicies(): void {
    // Initialize with default slotting policies
    const velocityPolicy: SlottingPolicy = {
      policyId: 'velocity_policy',
      name: 'Velocity-Based Slotting',
      description: 'Slot fast-moving items in prime locations',
      strategy: 'velocity',
      rules: [{
        ruleId: 'velocity_rule_1',
        condition: {
          skuCriteria: { velocityClass: 'X' }
        },
        action: {
          priority: VELOCITY_RULE_PRIORITY,
          preferredZones: ['A']
        },
        weight: VELOCITY_RULE_WEIGHT
      }],
      zones: ['A', 'B', 'C'],
      active: true,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.slottingPolicies.set(velocityPolicy.policyId, velocityPolicy);
  }

  /**
   * Publish putaway planned event
   */
  private async publishPutawayPlannedEvent(asnId: string, tasks: PutawayTask[]): Promise<void> {
    const event: PutawayPlannedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.putaway.planned',
      type: 'inventory.putaway.planned',
      occurredAt: new Date(),
      aggregateVersion: 1,
      aggregateId: asnId,
      aggregateType: 'ASN',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      asnId,
      tasks: tasks.map(task => ({
        taskId: task.taskId,
        sku: task.sku,
        fromLocation: task.fromLocation,
        toLocation: task.toLocation,
        qty: task.quantity,
        priority: task.priority,
        strategy: task.strategy
      }))
    };

    await this.eventBus.publish(event);
  }

  /**
   * Publish slotting updated event
   */
  private async publishSlottingUpdatedEvent(recommendation: SlottingRecommendation): Promise<void> {
    const event: SlottingUpdatedEvent = {
      eventId: `evt_${Date.now()}`,
      eventType: 'inventory.slotting.updated',
      type: 'inventory.slotting.updated',
      occurredAt: new Date(),
      aggregateVersion: 1,
      aggregateId: recommendation.sku,
      aggregateType: 'SKU',
      eventVersion: 1,
      occurredOn: new Date(),
      tenantId: 'default',
      sku: recommendation.sku,
      oldLocation: recommendation.currentLocation,
      newLocation: recommendation.recommendedLocation,
      reason: 'optimization',
      aiConfidence: recommendation.confidence
    };

    await this.eventBus.publish(event);
  }
}