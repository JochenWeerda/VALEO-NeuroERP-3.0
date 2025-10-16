import { and, eq, sql } from 'drizzle-orm';
import { type desc as _desc, type gte as _gte, type lte as _lte } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/node-postgres';
import {
  type factContracts as _factContracts,
  type factFinance as _factFinance,
  type factProduction as _factProduction,
  type factQuality as _factQuality,
  type factRegulatory as _factRegulatory,
  type factWeighing as _factWeighing,
  type kpis as _kpis,
  mvContractPositions,
  mvFinanceKpis,
  mvQualityStats,
  mvRegulatoryStats,
  mvWeighingVolumes
} from '../../infra/db/schema';
import { KPI } from '../entities/kpi';
import { type createKpiCalculatedEvent as _createKpiCalculatedEvent } from '../events/event-factories';

export interface KpiCalculationContext {
  tenantId: string;
  startDate?: Date;
  endDate?: Date;
  commodity?: string;
  customerId?: string;
  siteId?: string;
}

export interface KpiCalculationResult {
  kpi: KPI;
  success: boolean;
  executionTimeMs: number;
  error?: string;
}

export class KpiCalculationEngine {
  private db: ReturnType<typeof drizzle>;

  constructor(dbInstance?: ReturnType<typeof drizzle>) {
    this.db = dbInstance!;
  }

  /**
   * Calculate contract position KPIs
   */
  async calculateContractPositionKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]> {
    const results: KpiCalculationResult[] = [];

    // Hedging Ratio KPI
    const hedgingRatioResult = await this.calculateHedgingRatio(context);
    results.push(hedgingRatioResult);

    // Short Position KPI
    const shortPositionResult = await this.calculateShortPosition(context);
    results.push(shortPositionResult);

    // Long Position KPI
    const longPositionResult = await this.calculateLongPosition(context);
    results.push(longPositionResult);

    // Net Exposure KPI
    const netExposureResult = await this.calculateNetExposure(context);
    results.push(netExposureResult);

    return results;
  }

  /**
   * Calculate quality KPIs
   */
  async calculateQualityKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]> {
    const results: KpiCalculationResult[] = [];

    // Pass Rate KPI
    const passRateResult = await this.calculatePassRate(context);
    results.push(passRateResult);

    // Failure Rate KPI
    const failureRateResult = await this.calculateFailureRate(context);
    results.push(failureRateResult);

    // Average Moisture KPI
    const avgMoistureResult = await this.calculateAverageMoisture(context);
    results.push(avgMoistureResult);

    // Average Protein KPI
    const avgProteinResult = await this.calculateAverageProtein(context);
    results.push(avgProteinResult);

    return results;
  }

  /**
   * Calculate weighing KPIs
   */
  async calculateWeighingKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]> {
    const results: KpiCalculationResult[] = [];

    // Total Weight KPI
    const totalWeightResult = await this.calculateTotalWeight(context);
    results.push(totalWeightResult);

    // Average Weight KPI
    const avgWeightResult = await this.calculateAverageWeight(context);
    results.push(avgWeightResult);

    // Tolerance Compliance KPI
    const toleranceComplianceResult = await this.calculateToleranceCompliance(context);
    results.push(toleranceComplianceResult);

    return results;
  }

  /**
   * Calculate finance KPIs
   */
  async calculateFinanceKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]> {
    const results: KpiCalculationResult[] = [];

    // Total Revenue KPI
    const totalRevenueResult = await this.calculateTotalRevenue(context);
    results.push(totalRevenueResult);

    // Gross Margin KPI
    const grossMarginResult = await this.calculateGrossMargin(context);
    results.push(grossMarginResult);

    // Outstanding Invoices KPI
    const outstandingInvoicesResult = await this.calculateOutstandingInvoices(context);
    results.push(outstandingInvoicesResult);

    // Overdue Invoices KPI
    const overdueInvoicesResult = await this.calculateOverdueInvoices(context);
    results.push(overdueInvoicesResult);

    return results;
  }

  /**
   * Calculate regulatory KPIs
   */
  async calculateRegulatoryKpis(context: KpiCalculationContext): Promise<KpiCalculationResult[]> {
    const results: KpiCalculationResult[] = [];

    // Eligibility Rate KPI
    const eligibilityRateResult = await this.calculateEligibilityRate(context);
    results.push(eligibilityRateResult);

    return results;
  }

  // Individual KPI calculation methods

  private async calculateHedgingRatio(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvContractPositions.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvContractPositions.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          hedgingRatio: sql<number>`AVG(hedging_ratio)`,
        })
        .from(mvContractPositions)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.hedgingRatio || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `hedging-ratio-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Hedging Ratio',
        description: 'Average hedging ratio across all commodities',
        value: Math.round(value * 100) / 100, // Round to 2 decimal places
        unit: 'ratio',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'average',
          dataSource: 'mv_contract_positions',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `hedging-ratio-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Hedging Ratio',
          description: 'Average hedging ratio across all commodities',
          value: 0,
          unit: 'ratio',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateShortPosition(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvContractPositions.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvContractPositions.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          shortPosition: sql<number>`SUM(short_position)`,
        })
        .from(mvContractPositions)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.shortPosition || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `short-position-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Short Position',
        description: 'Total short position across all commodities',
        value,
        unit: 'tons',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'sum',
          dataSource: 'mv_contract_positions',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `short-position-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Short Position',
          description: 'Total short position across all commodities',
          value: 0,
          unit: 'tons',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateLongPosition(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvContractPositions.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvContractPositions.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          longPosition: sql<number>`SUM(long_position)`,
        })
        .from(mvContractPositions)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.longPosition || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `long-position-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Long Position',
        description: 'Total long position across all commodities',
        value,
        unit: 'tons',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'sum',
          dataSource: 'mv_contract_positions',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `long-position-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Long Position',
          description: 'Total long position across all commodities',
          value: 0,
          unit: 'tons',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateNetExposure(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvContractPositions.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvContractPositions.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          netExposure: sql<number>`SUM(net_position)`,
        })
        .from(mvContractPositions)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.netExposure || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `net-exposure-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Net Exposure',
        description: 'Net exposure (Long - Short) across all commodities',
        value,
        unit: 'tons',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'sum',
          dataSource: 'mv_contract_positions',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `net-exposure-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Net Exposure',
          description: 'Net exposure (Long - Short) across all commodities',
          value: 0,
          unit: 'tons',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculatePassRate(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvQualityStats.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvQualityStats.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          passRate: sql<number>`AVG(pass_rate)`,
        })
        .from(mvQualityStats)
        .where(and(...conditions))
        .limit(1);

      const value = (result[0]?.passRate || 0) * 100; // Convert to percentage
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `pass-rate-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Quality Pass Rate',
        description: 'Average quality pass rate across all tests',
        value: Math.round(value * 100) / 100, // Round to 2 decimal places
        unit: 'percentage',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'average',
          dataSource: 'mv_quality_stats',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `pass-rate-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Quality Pass Rate',
          description: 'Average quality pass rate across all tests',
          value: 0,
          unit: 'percentage',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateFailureRate(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvQualityStats.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvQualityStats.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          failureRate: sql<number>`AVG(failure_rate)`,
        })
        .from(mvQualityStats)
        .where(and(...conditions))
        .limit(1);

      const value = (result[0]?.failureRate || 0) * 100; // Convert to percentage
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `failure-rate-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Quality Failure Rate',
        description: 'Average quality failure rate across all tests',
        value: Math.round(value * 100) / 100, // Round to 2 decimal places
        unit: 'percentage',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'average',
          dataSource: 'mv_quality_stats',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `failure-rate-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Quality Failure Rate',
          description: 'Average quality failure rate across all tests',
          value: 0,
          unit: 'percentage',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateAverageMoisture(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [
        eq(mvQualityStats.tenantId, context.tenantId),
        sql`avg_moisture IS NOT NULL`
      ];

      if (context.commodity) {
        conditions.push(eq(mvQualityStats.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          avgMoisture: sql<number>`AVG(avg_moisture)`,
        })
        .from(mvQualityStats)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.avgMoisture || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `avg-moisture-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Average Moisture',
        description: 'Average moisture content across all quality tests',
        value: Math.round(value * 100) / 100, // Round to 2 decimal places
        unit: 'percentage',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'average',
          dataSource: 'mv_quality_stats',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `avg-moisture-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Average Moisture',
          description: 'Average moisture content across all quality tests',
          value: 0,
          unit: 'percentage',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateAverageProtein(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [
        eq(mvQualityStats.tenantId, context.tenantId),
        sql`avg_protein IS NOT NULL`
      ];

      if (context.commodity) {
        conditions.push(eq(mvQualityStats.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          avgProtein: sql<number>`AVG(avg_protein)`,
        })
        .from(mvQualityStats)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.avgProtein || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `avg-protein-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Average Protein',
        description: 'Average protein content across all quality tests',
        value: Math.round(value * 100) / 100, // Round to 2 decimal places
        unit: 'percentage',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'average',
          dataSource: 'mv_quality_stats',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `avg-protein-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Average Protein',
          description: 'Average protein content across all quality tests',
          value: 0,
          unit: 'percentage',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateTotalWeight(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvWeighingVolumes.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvWeighingVolumes.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          totalWeight: sql<number>`SUM(total_weight)`,
        })
        .from(mvWeighingVolumes)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.totalWeight || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `total-weight-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Total Weight',
        description: 'Total weight processed across all weighing operations',
        value,
        unit: 'kg',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'sum',
          dataSource: 'mv_weighing_volumes',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `total-weight-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Total Weight',
          description: 'Total weight processed across all weighing operations',
          value: 0,
          unit: 'kg',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateAverageWeight(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvWeighingVolumes.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvWeighingVolumes.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          avgWeight: sql<number>`AVG(avg_weight)`,
        })
        .from(mvWeighingVolumes)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.avgWeight || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `avg-weight-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Average Weight',
        description: 'Average weight per weighing operation',
        value: Math.round(value * 1000) / 1000, // Round to 3 decimal places
        unit: 'kg',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'average',
          dataSource: 'mv_weighing_volumes',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `avg-weight-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Average Weight',
          description: 'Average weight per weighing operation',
          value: 0,
          unit: 'kg',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateToleranceCompliance(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvWeighingVolumes.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvWeighingVolumes.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          withinTolerance: sql<number>`SUM(within_tolerance)`,
          totalTickets: sql<number>`SUM(total_tickets)`,
        })
        .from(mvWeighingVolumes)
        .where(and(...conditions))
        .limit(1);

      const withinTolerance = result[0]?.withinTolerance || 0;
      const totalTickets = result[0]?.totalTickets || 0;
      const value = totalTickets > 0 ? (withinTolerance / totalTickets) * 100 : 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `tolerance-compliance-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Tolerance Compliance',
        description: 'Percentage of weighing operations within tolerance limits',
        value: Math.round(value * 100) / 100, // Round to 2 decimal places
        unit: 'percentage',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'percentage',
          dataSource: 'mv_weighing_volumes',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `tolerance-compliance-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Tolerance Compliance',
          description: 'Percentage of weighing operations within tolerance limits',
          value: 0,
          unit: 'percentage',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateTotalRevenue(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvFinanceKpis.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvFinanceKpis.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          totalRevenue: sql<number>`SUM(total_revenue)`,
        })
        .from(mvFinanceKpis)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.totalRevenue || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `total-revenue-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Total Revenue',
        description: 'Total revenue across all operations',
        value,
        unit: 'EUR',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'sum',
          dataSource: 'mv_finance_kpis',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `total-revenue-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Total Revenue',
          description: 'Total revenue across all operations',
          value: 0,
          unit: 'EUR',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateGrossMargin(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvFinanceKpis.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvFinanceKpis.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          avgMargin: sql<number>`AVG(margin_percentage)`,
        })
        .from(mvFinanceKpis)
        .where(and(...conditions))
        .limit(1);

      const value = (result[0]?.avgMargin || 0) * 100; // Convert to percentage
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `gross-margin-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Gross Margin',
        description: 'Average gross margin percentage across all operations',
        value: Math.round(value * 100) / 100, // Round to 2 decimal places
        unit: 'percentage',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'average',
          dataSource: 'mv_finance_kpis',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `gross-margin-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Gross Margin',
          description: 'Average gross margin percentage across all operations',
          value: 0,
          unit: 'percentage',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateOutstandingInvoices(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvFinanceKpis.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvFinanceKpis.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          outstandingInvoices: sql<number>`SUM(outstanding_invoices)`,
        })
        .from(mvFinanceKpis)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.outstandingInvoices || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `outstanding-invoices-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Outstanding Invoices',
        description: 'Total value of outstanding invoices',
        value,
        unit: 'EUR',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'sum',
          dataSource: 'mv_finance_kpis',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `outstanding-invoices-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Outstanding Invoices',
          description: 'Total value of outstanding invoices',
          value: 0,
          unit: 'EUR',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateOverdueInvoices(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvFinanceKpis.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvFinanceKpis.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          overdueInvoices: sql<number>`SUM(overdue_invoices)`,
        })
        .from(mvFinanceKpis)
        .where(and(...conditions))
        .limit(1);

      const value = result[0]?.overdueInvoices || 0;
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `overdue-invoices-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Overdue Invoices',
        description: 'Total value of overdue invoices',
        value,
        unit: 'EUR',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'sum',
          dataSource: 'mv_finance_kpis',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `overdue-invoices-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Overdue Invoices',
          description: 'Total value of overdue invoices',
          value: 0,
          unit: 'EUR',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async calculateEligibilityRate(context: KpiCalculationContext): Promise<KpiCalculationResult> {
    const startTime = Date.now();

    try {
      const conditions = [eq(mvRegulatoryStats.tenantId, context.tenantId)];

      if (context.commodity) {
        conditions.push(eq(mvRegulatoryStats.commodity, context.commodity));
      }

      const result = await this.db
        .select({
          eligibilityRate: sql<number>`AVG(eligibility_rate)`,
        })
        .from(mvRegulatoryStats)
        .where(and(...conditions))
        .limit(1);

      const value = (result[0]?.eligibilityRate || 0) * 100; // Convert to percentage
      const executionTimeMs = Date.now() - startTime;

      const kpi = KPI.create({
        id: `eligibility-rate-${context.tenantId}-${Date.now()}`,
        tenantId: context.tenantId,
        name: 'Regulatory Eligibility Rate',
        description: 'Average regulatory eligibility rate across all labels',
        value: Math.round(value * 100) / 100, // Round to 2 decimal places
        unit: 'percentage',
        context: {
          commodity: context.commodity,
          period: context.startDate ? context.startDate.toISOString().split('T')[0] : undefined,
        },
        metadata: {
          calculationMethod: 'average',
          dataSource: 'mv_regulatory_stats',
        },
      });

      return {
        kpi,
        success: true,
        executionTimeMs,
      };

    } catch (error) {
      const executionTimeMs = Date.now() - startTime;
      return {
        kpi: KPI.create({
          id: `eligibility-rate-error-${context.tenantId}-${Date.now()}`,
          tenantId: context.tenantId,
          name: 'Regulatory Eligibility Rate',
          description: 'Average regulatory eligibility rate across all labels',
          value: 0,
          unit: 'percentage',
          context: {},
        }),
        success: false,
        executionTimeMs,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Calculate all KPIs for a tenant
   */
  async calculateAllKpis(context: KpiCalculationContext): Promise<{
    results: KpiCalculationResult[];
    summary: {
      total: number;
      successful: number;
      failed: number;
      totalExecutionTimeMs: number;
    };
  }> {
    const startTime = Date.now();

    const allResults = await Promise.all([
      ...await this.calculateContractPositionKpis(context),
      ...await this.calculateQualityKpis(context),
      ...await this.calculateWeighingKpis(context),
      ...await this.calculateFinanceKpis(context),
      ...await this.calculateRegulatoryKpis(context),
    ]);

    const totalExecutionTimeMs = Date.now() - startTime;
    const successful = allResults.filter(r => r.success).length;
    const failed = allResults.filter(r => !r.success).length;

    return {
      results: allResults,
      summary: {
        total: allResults.length,
        successful,
        failed,
        totalExecutionTimeMs,
      },
    };
  }
}