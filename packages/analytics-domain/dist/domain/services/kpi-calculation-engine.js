"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KpiCalculationEngine = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const schema_1 = require("../../infra/db/schema");
const kpi_1 = require("../entities/kpi");
class KpiCalculationEngine {
    db;
    constructor(db) {
        this.db = db;
    }
    async calculateContractPositionKpis(context) {
        const results = [];
        const hedgingRatioResult = await this.calculateHedgingRatio(context);
        results.push(hedgingRatioResult);
        const shortPositionResult = await this.calculateShortPosition(context);
        results.push(shortPositionResult);
        const longPositionResult = await this.calculateLongPosition(context);
        results.push(longPositionResult);
        const netExposureResult = await this.calculateNetExposure(context);
        results.push(netExposureResult);
        return results;
    }
    async calculateQualityKpis(context) {
        const results = [];
        const passRateResult = await this.calculatePassRate(context);
        results.push(passRateResult);
        const failureRateResult = await this.calculateFailureRate(context);
        results.push(failureRateResult);
        const avgMoistureResult = await this.calculateAverageMoisture(context);
        results.push(avgMoistureResult);
        const avgProteinResult = await this.calculateAverageProtein(context);
        results.push(avgProteinResult);
        return results;
    }
    async calculateWeighingKpis(context) {
        const results = [];
        const totalWeightResult = await this.calculateTotalWeight(context);
        results.push(totalWeightResult);
        const avgWeightResult = await this.calculateAverageWeight(context);
        results.push(avgWeightResult);
        const toleranceComplianceResult = await this.calculateToleranceCompliance(context);
        results.push(toleranceComplianceResult);
        return results;
    }
    async calculateFinanceKpis(context) {
        const results = [];
        const totalRevenueResult = await this.calculateTotalRevenue(context);
        results.push(totalRevenueResult);
        const grossMarginResult = await this.calculateGrossMargin(context);
        results.push(grossMarginResult);
        const outstandingInvoicesResult = await this.calculateOutstandingInvoices(context);
        results.push(outstandingInvoicesResult);
        const overdueInvoicesResult = await this.calculateOverdueInvoices(context);
        results.push(overdueInvoicesResult);
        return results;
    }
    async calculateRegulatoryKpis(context) {
        const results = [];
        const eligibilityRateResult = await this.calculateEligibilityRate(context);
        results.push(eligibilityRateResult);
        return results;
    }
    async calculateHedgingRatio(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                hedgingRatio: (0, drizzle_orm_1.sql) `AVG(hedging_ratio)`,
            })
                .from(schema_1.mvContractPositions)
                .where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.hedgingRatio || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
                id: `hedging-ratio-${context.tenantId}-${Date.now()}`,
                tenantId: context.tenantId,
                name: 'Hedging Ratio',
                description: 'Average hedging ratio across all commodities',
                value: Math.round(value * 100) / 100,
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateShortPosition(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                shortPosition: (0, drizzle_orm_1.sql) `SUM(short_position)`,
            })
                .from(schema_1.mvContractPositions)
                .where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.shortPosition || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateLongPosition(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                longPosition: (0, drizzle_orm_1.sql) `SUM(long_position)`,
            })
                .from(schema_1.mvContractPositions)
                .where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.longPosition || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateNetExposure(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                netExposure: (0, drizzle_orm_1.sql) `SUM(net_position)`,
            })
                .from(schema_1.mvContractPositions)
                .where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.netExposure || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculatePassRate(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                passRate: (0, drizzle_orm_1.sql) `AVG(pass_rate)`,
            })
                .from(schema_1.mvQualityStats)
                .where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = (result[0]?.passRate || 0) * 100;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
                id: `pass-rate-${context.tenantId}-${Date.now()}`,
                tenantId: context.tenantId,
                name: 'Quality Pass Rate',
                description: 'Average quality pass rate across all tests',
                value: Math.round(value * 100) / 100,
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateFailureRate(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                failureRate: (0, drizzle_orm_1.sql) `AVG(failure_rate)`,
            })
                .from(schema_1.mvQualityStats)
                .where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = (result[0]?.failureRate || 0) * 100;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
                id: `failure-rate-${context.tenantId}-${Date.now()}`,
                tenantId: context.tenantId,
                name: 'Quality Failure Rate',
                description: 'Average quality failure rate across all tests',
                value: Math.round(value * 100) / 100,
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateAverageMoisture(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                avgMoisture: (0, drizzle_orm_1.sql) `AVG(avg_moisture)`,
            })
                .from(schema_1.mvQualityStats)
                .where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.tenantId, context.tenantId))
                .where((0, drizzle_orm_1.sql) `avg_moisture IS NOT NULL`);
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.avgMoisture || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
                id: `avg-moisture-${context.tenantId}-${Date.now()}`,
                tenantId: context.tenantId,
                name: 'Average Moisture',
                description: 'Average moisture content across all quality tests',
                value: Math.round(value * 100) / 100,
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateAverageProtein(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                avgProtein: (0, drizzle_orm_1.sql) `AVG(avg_protein)`,
            })
                .from(schema_1.mvQualityStats)
                .where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.tenantId, context.tenantId))
                .where((0, drizzle_orm_1.sql) `avg_protein IS NOT NULL`);
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.avgProtein || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
                id: `avg-protein-${context.tenantId}-${Date.now()}`,
                tenantId: context.tenantId,
                name: 'Average Protein',
                description: 'Average protein content across all quality tests',
                value: Math.round(value * 100) / 100,
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateTotalWeight(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                totalWeight: (0, drizzle_orm_1.sql) `SUM(total_weight)`,
            })
                .from(schema_1.mvWeighingVolumes)
                .where((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.totalWeight || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateAverageWeight(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                avgWeight: (0, drizzle_orm_1.sql) `AVG(avg_weight)`,
            })
                .from(schema_1.mvWeighingVolumes)
                .where((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.avgWeight || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
                id: `avg-weight-${context.tenantId}-${Date.now()}`,
                tenantId: context.tenantId,
                name: 'Average Weight',
                description: 'Average weight per weighing operation',
                value: Math.round(value * 1000) / 1000,
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateToleranceCompliance(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                withinTolerance: (0, drizzle_orm_1.sql) `SUM(within_tolerance)`,
                totalTickets: (0, drizzle_orm_1.sql) `SUM(total_tickets)`,
            })
                .from(schema_1.mvWeighingVolumes)
                .where((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const withinTolerance = result[0]?.withinTolerance || 0;
            const totalTickets = result[0]?.totalTickets || 0;
            const value = totalTickets > 0 ? (withinTolerance / totalTickets) * 100 : 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
                id: `tolerance-compliance-${context.tenantId}-${Date.now()}`,
                tenantId: context.tenantId,
                name: 'Tolerance Compliance',
                description: 'Percentage of weighing operations within tolerance limits',
                value: Math.round(value * 100) / 100,
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateTotalRevenue(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                totalRevenue: (0, drizzle_orm_1.sql) `SUM(total_revenue)`,
            })
                .from(schema_1.mvFinanceKpis)
                .where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.totalRevenue || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateGrossMargin(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                avgMargin: (0, drizzle_orm_1.sql) `AVG(margin_percentage)`,
            })
                .from(schema_1.mvFinanceKpis)
                .where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = (result[0]?.avgMargin || 0) * 100;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
                id: `gross-margin-${context.tenantId}-${Date.now()}`,
                tenantId: context.tenantId,
                name: 'Gross Margin',
                description: 'Average gross margin percentage across all operations',
                value: Math.round(value * 100) / 100,
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateOutstandingInvoices(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                outstandingInvoices: (0, drizzle_orm_1.sql) `SUM(outstanding_invoices)`,
            })
                .from(schema_1.mvFinanceKpis)
                .where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.outstandingInvoices || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateOverdueInvoices(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                overdueInvoices: (0, drizzle_orm_1.sql) `SUM(overdue_invoices)`,
            })
                .from(schema_1.mvFinanceKpis)
                .where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = result[0]?.overdueInvoices || 0;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateEligibilityRate(context) {
        const startTime = Date.now();
        try {
            let query = this.db
                .select({
                eligibilityRate: (0, drizzle_orm_1.sql) `AVG(eligibility_rate)`,
            })
                .from(schema_1.mvRegulatoryStats)
                .where((0, drizzle_orm_1.eq)(schema_1.mvRegulatoryStats.tenantId, context.tenantId));
            if (context.commodity) {
                query = query.where((0, drizzle_orm_1.eq)(schema_1.mvRegulatoryStats.commodity, context.commodity));
            }
            const result = await query.limit(1);
            const value = (result[0]?.eligibilityRate || 0) * 100;
            const executionTimeMs = Date.now() - startTime;
            const kpi = kpi_1.KPI.create({
                id: `eligibility-rate-${context.tenantId}-${Date.now()}`,
                tenantId: context.tenantId,
                name: 'Regulatory Eligibility Rate',
                description: 'Average regulatory eligibility rate across all labels',
                value: Math.round(value * 100) / 100,
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
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                kpi: kpi_1.KPI.create({
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
    async calculateAllKpis(context) {
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
exports.KpiCalculationEngine = KpiCalculationEngine;
//# sourceMappingURL=kpi-calculation-engine.js.map