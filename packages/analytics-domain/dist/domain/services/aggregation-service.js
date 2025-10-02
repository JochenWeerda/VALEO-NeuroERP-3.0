"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AggregationService = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const schema_1 = require("../../infra/db/schema");
class AggregationService {
    db;
    config;
    constructor(db, config = {}) {
        this.db = db;
        this.config = config;
        this.config.batchSize = config.batchSize || 1000;
        this.config.maxExecutionTimeMs = config.maxExecutionTimeMs || 300000;
    }
    async refreshContractPositions(tenantId) {
        const startTime = Date.now();
        try {
            await this.db
                .delete(schema_1.mvContractPositions)
                .where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.tenantId, tenantId));
            const result = await this.db.execute((0, drizzle_orm_1.sql) `
        INSERT INTO ${schema_1.mvContractPositions} (
          tenant_id, commodity, month, short_position, long_position, net_position, hedging_ratio, last_updated
        )
        SELECT
          tenant_id,
          commodity,
          TO_CHAR(occurred_at, 'YYYY-MM') as month,
          COALESCE(SUM(CASE WHEN contract_type = 'Purchase' THEN quantity ELSE 0 END), 0) as short_position,
          COALESCE(SUM(CASE WHEN contract_type = 'Sales' THEN quantity ELSE 0 END), 0) as long_position,
          COALESCE(SUM(CASE WHEN contract_type = 'Sales' THEN quantity ELSE 0 END), 0) -
          COALESCE(SUM(CASE WHEN contract_type = 'Purchase' THEN quantity ELSE 0 END), 0) as net_position,
          CASE
            WHEN COALESCE(SUM(CASE WHEN contract_type = 'Purchase' THEN quantity ELSE 0 END), 0) > 0
            THEN (COALESCE(SUM(CASE WHEN hedging_required THEN quantity ELSE 0 END), 0) /
                  COALESCE(SUM(CASE WHEN contract_type = 'Purchase' THEN quantity ELSE 0 END), 0))
            ELSE 0
          END as hedging_ratio,
          NOW() as last_updated
        FROM ${schema_1.factContracts}
        WHERE tenant_id = ${tenantId}
          AND status IN ('Confirmed', 'Active', 'Completed')
        GROUP BY tenant_id, commodity, TO_CHAR(occurred_at, 'YYYY-MM')
        HAVING (COALESCE(SUM(CASE WHEN contract_type = 'Purchase' THEN quantity ELSE 0 END), 0) != 0 OR
                COALESCE(SUM(CASE WHEN contract_type = 'Sales' THEN quantity ELSE 0 END), 0) != 0)
      `);
            const executionTimeMs = Date.now() - startTime;
            const recordCount = result.rowCount || 0;
            return {
                success: true,
                recordCount,
                executionTimeMs,
            };
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                success: false,
                recordCount: 0,
                executionTimeMs,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }
    async refreshQualityStats(tenantId) {
        const startTime = Date.now();
        try {
            await this.db
                .delete(schema_1.mvQualityStats)
                .where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.tenantId, tenantId));
            const result = await this.db.execute((0, drizzle_orm_1.sql) `
        INSERT INTO ${schema_1.mvQualityStats} (
          tenant_id, commodity, period, total_samples, passed_samples, failed_samples,
          pass_rate, failure_rate, avg_moisture, avg_protein, last_updated
        )
        SELECT
          tenant_id,
          commodity,
          TO_CHAR(occurred_at, 'YYYY-MM') as period,
          COUNT(*) as total_samples,
          COUNT(CASE WHEN is_passed THEN 1 END) as passed_samples,
          COUNT(CASE WHEN NOT is_passed THEN 1 END) as failed_samples,
          ROUND(COUNT(CASE WHEN is_passed THEN 1 END)::decimal / COUNT(*)::decimal, 4) as pass_rate,
          ROUND(COUNT(CASE WHEN NOT is_passed THEN 1 END)::decimal / COUNT(*)::decimal, 4) as failure_rate,
          ROUND(AVG(CASE WHEN test_type = 'Moisture' THEN numeric_result END), 2) as avg_moisture,
          ROUND(AVG(CASE WHEN test_type = 'Protein' THEN numeric_result END), 2) as avg_protein,
          NOW() as last_updated
        FROM ${schema_1.factQuality}
        WHERE tenant_id = ${tenantId}
        GROUP BY tenant_id, commodity, TO_CHAR(occurred_at, 'YYYY-MM')
      `);
            const executionTimeMs = Date.now() - startTime;
            const recordCount = result.rowCount || 0;
            return {
                success: true,
                recordCount,
                executionTimeMs,
            };
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                success: false,
                recordCount: 0,
                executionTimeMs,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }
    async refreshRegulatoryStats(tenantId) {
        const startTime = Date.now();
        try {
            await this.db
                .delete(schema_1.mvRegulatoryStats)
                .where((0, drizzle_orm_1.eq)(schema_1.mvRegulatoryStats.tenantId, tenantId));
            const result = await this.db.execute((0, drizzle_orm_1.sql) `
        INSERT INTO ${schema_1.mvRegulatoryStats} (
          tenant_id, commodity, label_type, period, total_eligible, total_ineligible,
          eligibility_rate, ineligibility_rate, last_updated
        )
        SELECT
          tenant_id,
          commodity,
          label_type,
          TO_CHAR(occurred_at, 'YYYY-MM') as period,
          COUNT(CASE WHEN is_eligible THEN 1 END) as total_eligible,
          COUNT(CASE WHEN NOT is_eligible THEN 1 END) as total_ineligible,
          ROUND(COUNT(CASE WHEN is_eligible THEN 1 END)::decimal / COUNT(*)::decimal, 4) as eligibility_rate,
          ROUND(COUNT(CASE WHEN NOT is_eligible THEN 1 END)::decimal / COUNT(*)::decimal, 4) as ineligibility_rate,
          NOW() as last_updated
        FROM ${schema_1.factRegulatory}
        WHERE tenant_id = ${tenantId}
        GROUP BY tenant_id, commodity, label_type, TO_CHAR(occurred_at, 'YYYY-MM')
      `);
            const executionTimeMs = Date.now() - startTime;
            const recordCount = result.rowCount || 0;
            return {
                success: true,
                recordCount,
                executionTimeMs,
            };
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                success: false,
                recordCount: 0,
                executionTimeMs,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }
    async refreshFinanceKpis(tenantId) {
        const startTime = Date.now();
        try {
            await this.db
                .delete(schema_1.mvFinanceKpis)
                .where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.tenantId, tenantId));
            const result = await this.db.execute((0, drizzle_orm_1.sql) `
        INSERT INTO ${schema_1.mvFinanceKpis} (
          tenant_id, commodity, customer_id, period, total_revenue, total_cost,
          gross_margin, margin_percentage, outstanding_invoices, overdue_invoices, last_updated
        )
        SELECT
          tenant_id,
          commodity,
          customer_id,
          TO_CHAR(occurred_at, 'YYYY-MM') as period,
          COALESCE(SUM(CASE WHEN type = 'Revenue' THEN amount ELSE 0 END), 0) as total_revenue,
          COALESCE(SUM(CASE WHEN type = 'Cost' THEN amount ELSE 0 END), 0) as total_cost,
          COALESCE(SUM(CASE WHEN type = 'Revenue' THEN amount ELSE 0 END), 0) -
          COALESCE(SUM(CASE WHEN type = 'Cost' THEN amount ELSE 0 END), 0) as gross_margin,
          CASE
            WHEN COALESCE(SUM(CASE WHEN type = 'Revenue' THEN amount ELSE 0 END), 0) > 0
            THEN ROUND((
              (COALESCE(SUM(CASE WHEN type = 'Revenue' THEN amount ELSE 0 END), 0) -
               COALESCE(SUM(CASE WHEN type = 'Cost' THEN amount ELSE 0 END), 0)) /
              COALESCE(SUM(CASE WHEN type = 'Revenue' THEN amount ELSE 0 END), 0)
            ), 4)
            ELSE 0
          END as margin_percentage,
          COALESCE(SUM(CASE WHEN type = 'Revenue' AND status = 'Pending' THEN amount ELSE 0 END), 0) as outstanding_invoices,
          COALESCE(SUM(CASE WHEN type = 'Revenue' AND status = 'Overdue' THEN amount ELSE 0 END), 0) as overdue_invoices,
          NOW() as last_updated
        FROM ${schema_1.factFinance}
        WHERE tenant_id = ${tenantId}
        GROUP BY tenant_id, commodity, customer_id, TO_CHAR(occurred_at, 'YYYY-MM')
      `);
            const executionTimeMs = Date.now() - startTime;
            const recordCount = result.rowCount || 0;
            return {
                success: true,
                recordCount,
                executionTimeMs,
            };
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                success: false,
                recordCount: 0,
                executionTimeMs,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }
    async refreshWeighingVolumes(tenantId) {
        const startTime = Date.now();
        try {
            await this.db
                .delete(schema_1.mvWeighingVolumes)
                .where((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.tenantId, tenantId));
            const result = await this.db.execute((0, drizzle_orm_1.sql) `
        INSERT INTO ${schema_1.mvWeighingVolumes} (
          tenant_id, commodity, customer_id, site_id, period, total_weight, total_tickets,
          avg_weight, within_tolerance, outside_tolerance, last_updated
        )
        SELECT
          tenant_id,
          commodity,
          customer_id,
          site_id,
          TO_CHAR(occurred_at, 'YYYY-MM-DD') as period,
          COALESCE(SUM(net_weight), 0) as total_weight,
          COUNT(DISTINCT ticket_id) as total_tickets,
          ROUND(COALESCE(AVG(net_weight), 0), 3) as avg_weight,
          COUNT(CASE WHEN is_within_tolerance THEN 1 END) as within_tolerance,
          COUNT(CASE WHEN NOT is_within_tolerance THEN 1 END) as outside_tolerance,
          NOW() as last_updated
        FROM ${schema_1.factWeighing}
        WHERE tenant_id = ${tenantId}
          AND status = 'Completed'
          AND net_weight IS NOT NULL
        GROUP BY tenant_id, commodity, customer_id, site_id, TO_CHAR(occurred_at, 'YYYY-MM-DD')
      `);
            const executionTimeMs = Date.now() - startTime;
            const recordCount = result.rowCount || 0;
            return {
                success: true,
                recordCount,
                executionTimeMs,
            };
        }
        catch (error) {
            const executionTimeMs = Date.now() - startTime;
            return {
                success: false,
                recordCount: 0,
                executionTimeMs,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }
    async refreshAllViews(tenantId) {
        const startTime = Date.now();
        const [contractPositions, qualityStats, regulatoryStats, financeKpis, weighingVolumes,] = await Promise.all([
            this.refreshContractPositions(tenantId),
            this.refreshQualityStats(tenantId),
            this.refreshRegulatoryStats(tenantId),
            this.refreshFinanceKpis(tenantId),
            this.refreshWeighingVolumes(tenantId),
        ]);
        const totalExecutionTimeMs = Date.now() - startTime;
        return {
            contractPositions,
            qualityStats,
            regulatoryStats,
            financeKpis,
            weighingVolumes,
            totalExecutionTimeMs,
        };
    }
    async getAggregationStatus(tenantId) {
        const [contractPositions, qualityStats, regulatoryStats, financeKpis, weighingVolumes] = await Promise.all([
            this.db.select({ count: (0, drizzle_orm_1.sql) `count(*)` }).from(schema_1.mvContractPositions).where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.tenantId, tenantId)),
            this.db.select({ count: (0, drizzle_orm_1.sql) `count(*)` }).from(schema_1.mvQualityStats).where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.tenantId, tenantId)),
            this.db.select({ count: (0, drizzle_orm_1.sql) `count(*)` }).from(schema_1.mvRegulatoryStats).where((0, drizzle_orm_1.eq)(schema_1.mvRegulatoryStats.tenantId, tenantId)),
            this.db.select({ count: (0, drizzle_orm_1.sql) `count(*)` }).from(schema_1.mvFinanceKpis).where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.tenantId, tenantId)),
            this.db.select({ count: (0, drizzle_orm_1.sql) `count(*)` }).from(schema_1.mvWeighingVolumes).where((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.tenantId, tenantId)),
        ]);
        const [contractLastRefresh, qualityLastRefresh, regulatoryLastRefresh, financeLastRefresh, weighingLastRefresh] = await Promise.all([
            this.db.select({ lastUpdated: schema_1.mvContractPositions.lastUpdated }).from(schema_1.mvContractPositions).where((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.tenantId, tenantId)).orderBy((0, drizzle_orm_1.desc)(schema_1.mvContractPositions.lastUpdated)).limit(1),
            this.db.select({ lastUpdated: schema_1.mvQualityStats.lastUpdated }).from(schema_1.mvQualityStats).where((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.tenantId, tenantId)).orderBy((0, drizzle_orm_1.desc)(schema_1.mvQualityStats.lastUpdated)).limit(1),
            this.db.select({ lastUpdated: schema_1.mvRegulatoryStats.lastUpdated }).from(schema_1.mvRegulatoryStats).where((0, drizzle_orm_1.eq)(schema_1.mvRegulatoryStats.tenantId, tenantId)).orderBy((0, drizzle_orm_1.desc)(schema_1.mvRegulatoryStats.lastUpdated)).limit(1),
            this.db.select({ lastUpdated: schema_1.mvFinanceKpis.lastUpdated }).from(schema_1.mvFinanceKpis).where((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.tenantId, tenantId)).orderBy((0, drizzle_orm_1.desc)(schema_1.mvFinanceKpis.lastUpdated)).limit(1),
            this.db.select({ lastUpdated: schema_1.mvWeighingVolumes.lastUpdated }).from(schema_1.mvWeighingVolumes).where((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.tenantId, tenantId)).orderBy((0, drizzle_orm_1.desc)(schema_1.mvWeighingVolumes.lastUpdated)).limit(1),
        ]);
        return {
            lastRefresh: {
                contractPositions: contractLastRefresh[0]?.lastUpdated,
                qualityStats: qualityLastRefresh[0]?.lastUpdated,
                regulatoryStats: regulatoryLastRefresh[0]?.lastUpdated,
                financeKpis: financeLastRefresh[0]?.lastUpdated,
                weighingVolumes: weighingLastRefresh[0]?.lastUpdated,
            },
            recordCounts: {
                contractPositions: contractPositions[0]?.count || 0,
                qualityStats: qualityStats[0]?.count || 0,
                regulatoryStats: regulatoryStats[0]?.count || 0,
                financeKpis: financeKpis[0]?.count || 0,
                weighingVolumes: weighingVolumes[0]?.count || 0,
            },
        };
    }
}
exports.AggregationService = AggregationService;
//# sourceMappingURL=aggregation-service.js.map