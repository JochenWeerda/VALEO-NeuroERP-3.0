/**
 * Agribusiness Analytics Service
 * Advanced Analytics & Reporting for Agribusiness Operations
 * Based on Odoo reporting patterns
 */

import { Farmer } from '../entities/farmer';
import { FieldServiceTask } from '../entities/field-service-task';

export interface BatchRepository {
  findMany(filters: any, pagination: any, sort: any): Promise<{ data: any[]; total: number }>;
}

export interface ContractRepository {
  findMany(filters: any, pagination: any, sort: any): Promise<{ data: any[]; total: number }>;
}

export interface FarmerRepository {
  findMany(filters: any, pagination: any, sort: any): Promise<{ data: Farmer[]; total: number }>;
}

export interface TaskRepository {
  findMany(filters: any, pagination: any, sort: any): Promise<{ data: FieldServiceTask[]; total: number }>;
}

export interface AgribusinessAnalyticsServiceDependencies {
  batchRepository: BatchRepository;
  contractRepository: ContractRepository;
  farmerRepository: FarmerRepository;
  taskRepository: TaskRepository;
}

export interface AgribusinessKPIs {
  totalFarmers: number;
  activeFarmers: number;
  totalContracts: number;
  activeContracts: number;
  totalBatches: number;
  activeBatches: number;
  totalFieldTasks: number;
  completedTasks: number;
  pendingTasks: number;
  averageTaskCompletionTime?: number; // in hours
  totalRevenue?: number;
  averageQualityScore?: number;
  certificationCoverage: number; // percentage of farmers with certifications
  organicPercentage: number; // percentage of organic certified farmers
}

export interface FarmerPerformanceMetrics {
  farmerId: string;
  farmerName: string;
  totalContracts: number;
  activeContracts: number;
  totalDeliveries: number;
  totalRevenue?: number;
  averageQualityScore?: number;
  onTimeDeliveryRate?: number;
  certificationCount: number;
  activeCertifications: number;
  totalCrops: number;
  harvestedCrops: number;
  performanceRating: 'EXCELLENT' | 'GOOD' | 'AVERAGE' | 'NEEDS_IMPROVEMENT';
}

export interface ContractPerformanceMetrics {
  contractId: string;
  contractNumber: string;
  farmerId: string;
  farmerName: string;
  contractType: string;
  status: string;
  totalQuantity: number;
  fulfilledQuantity: number;
  fulfillmentRate: number; // percentage
  onTimeDeliveryRate?: number;
  qualityScore?: number;
  revenue?: number;
  startDate: Date;
  endDate?: Date;
}

export interface BatchAnalytics {
  batchId: string;
  batchNumber: string;
  batchType: string;
  status: string;
  quantity: number;
  originCountry?: string;
  harvestDate?: Date;
  expiryDate?: Date;
  qualityScore?: number;
  traceabilityDepth: number; // number of levels in traceability tree
  relatedContracts: number;
  relatedTasks: number;
}

export interface SeasonalTrends {
  season: 'SPRING' | 'SUMMER' | 'AUTUMN' | 'WINTER';
  year: number;
  totalHarvests: number;
  totalVolume: number;
  averageQualityScore?: number;
  topCrops: Array<{ cropType: string; volume: number }>;
  topFarmers: Array<{ farmerId: string; farmerName: string; volume: number }>;
}

export interface QualityTrends {
  period: string; // e.g., "2024-Q1"
  totalCertificates: number;
  activeCertificates: number;
  expiredCertificates: number;
  expiringSoon: number; // within 30 days
  certificationTypes: Record<string, number>;
  averageQualityScore?: number;
  qualityDistribution: {
    excellent: number; // 90-100
    good: number; // 80-89
    average: number; // 70-79
    belowAverage: number; // <70
  };
}

export class AgribusinessAnalyticsService {
  constructor(private deps: AgribusinessAnalyticsServiceDependencies) {}

  /**
   * Get overall KPIs for agribusiness operations
   */
  async getKPIs(dateFrom?: Date, dateTo?: Date): Promise<AgribusinessKPIs> {
    const now = dateTo || new Date();
    const from = dateFrom || new Date(now.getFullYear(), 0, 1); // Start of year

    // Get farmers
    const farmers = await this.deps.farmerRepository.findMany(
      {},
      { page: 1, pageSize: 10000 },
      { field: 'createdAt', direction: 'desc' }
    );

    const activeFarmers = farmers.data.filter(f => f.status === 'ACTIVE').length;
    const farmersWithCerts = farmers.data.filter(f => f.certifications.length > 0).length;
    const organicFarmers = farmers.data.filter(f =>
      f.certifications.some(c => c.type === 'ORGANIC' && c.isActive)
    ).length;

    // Get contracts
    const contracts = await this.deps.contractRepository.findMany(
      {},
      { page: 1, pageSize: 10000 },
      { field: 'createdAt', direction: 'desc' }
    );

    const activeContracts = contracts.data.filter((c: any) => c.status === 'ACTIVE').length;

    // Get batches
    const batches = await this.deps.batchRepository.findMany(
      {},
      { page: 1, pageSize: 10000 },
      { field: 'createdAt', direction: 'desc' }
    );

    const activeBatches = batches.data.filter((b: any) => b.status === 'ACTIVE').length;

    // Get tasks
    const tasks = await this.deps.taskRepository.findMany(
      {},
      { page: 1, pageSize: 10000 },
      { field: 'createdAt', direction: 'desc' }
    );

    const completedTasks = tasks.data.filter((t: any) => t.status === 'COMPLETED').length;
    const pendingTasks = tasks.data.filter((t: any) =>
      ['DRAFT', 'SCHEDULED', 'IN_PROGRESS'].includes(t.status)
    ).length;

    // Calculate average task completion time
    let totalCompletionTime = 0;
    let completedTasksWithTime = 0;
    for (const task of tasks.data) {
      if (task.status === 'COMPLETED' && task.actualStartDate && task.actualEndDate) {
        const duration = task.actualEndDate.getTime() - task.actualStartDate.getTime();
        totalCompletionTime += duration;
        completedTasksWithTime++;
      }
    }

    const averageTaskCompletionTime =
      completedTasksWithTime > 0
        ? totalCompletionTime / completedTasksWithTime / (1000 * 60 * 60) // in hours
        : undefined;

    // Calculate total revenue (from contracts)
    const totalRevenue = contracts.data.reduce((sum: number, c: any) => {
      return sum + (c.totalValue || 0);
    }, 0);

    // Calculate average quality score (from farmers)
    const farmersWithScores = farmers.data.filter(f => f.averageQualityScore !== undefined);
    const averageQualityScore =
      farmersWithScores.length > 0
        ? farmersWithScores.reduce((sum, f) => sum + (f.averageQualityScore || 0), 0) /
          farmersWithScores.length
        : undefined;

    return {
      totalFarmers: farmers.total,
      activeFarmers,
      totalContracts: contracts.total,
      activeContracts,
      totalBatches: batches.total,
      activeBatches,
      totalFieldTasks: tasks.total,
      completedTasks,
      pendingTasks,
      averageTaskCompletionTime,
      totalRevenue,
      averageQualityScore,
      certificationCoverage: farmers.total > 0 ? (farmersWithCerts / farmers.total) * 100 : 0,
      organicPercentage: farmers.total > 0 ? (organicFarmers / farmers.total) * 100 : 0,
    };
  }

  /**
   * Get farmer performance metrics
   */
  async getFarmerPerformanceMetrics(
    farmerId?: string,
    dateFrom?: Date,
    dateTo?: Date
  ): Promise<FarmerPerformanceMetrics[]> {
    const filters = farmerId ? { id: farmerId } : {};
    const farmers = await this.deps.farmerRepository.findMany(
      filters,
      { page: 1, pageSize: 10000 },
      { field: 'fullName', direction: 'asc' }
    );

    const metrics: FarmerPerformanceMetrics[] = [];

    for (const farmer of farmers.data) {
      // Get contracts for this farmer
      const contracts = await this.deps.contractRepository.findMany(
        { farmerId: farmer.id },
        { page: 1, pageSize: 10000 },
        { field: 'createdAt', direction: 'desc' }
      );

      const activeContracts = contracts.data.filter((c: any) => c.status === 'ACTIVE').length;

      // Get tasks for this farmer
      const tasks = await this.deps.taskRepository.findMany(
        { farmerId: farmer.id },
        { page: 1, pageSize: 10000 },
        { field: 'createdAt', direction: 'desc' }
      );

      // Calculate performance rating
      let performanceRating: 'EXCELLENT' | 'GOOD' | 'AVERAGE' | 'NEEDS_IMPROVEMENT' = 'AVERAGE';
      const score = farmer.averageQualityScore || 0;
      if (score >= 90) {
        performanceRating = 'EXCELLENT';
      } else if (score >= 80) {
        performanceRating = 'GOOD';
      } else if (score >= 70) {
        performanceRating = 'AVERAGE';
      } else {
        performanceRating = 'NEEDS_IMPROVEMENT';
      }

      const harvestedCrops = farmer.crops.filter(c => c.status === 'HARVESTED').length;

      metrics.push({
        farmerId: farmer.id,
        farmerName: farmer.fullName,
        totalContracts: farmer.totalContracts,
        activeContracts,
        totalDeliveries: farmer.totalDeliveries,
        totalRevenue: farmer.totalRevenue,
        averageQualityScore: farmer.averageQualityScore,
        certificationCount: farmer.certifications.length,
        activeCertifications: farmer.certifications.filter(c => c.isActive).length,
        totalCrops: farmer.crops.length,
        harvestedCrops,
        performanceRating,
      });
    }

    return metrics;
  }

  /**
   * Get contract performance metrics
   */
  async getContractPerformanceMetrics(
    contractId?: string,
    dateFrom?: Date,
    dateTo?: Date
  ): Promise<ContractPerformanceMetrics[]> {
    const filters = contractId ? { id: contractId } : {};
    const contracts = await this.deps.contractRepository.findMany(
      filters,
      { page: 1, pageSize: 10000 },
      { field: 'createdAt', direction: 'desc' }
    );

    const metrics: ContractPerformanceMetrics[] = [];

    for (const contract of contracts.data as any[]) {
      const fulfilledQuantity = contract.fulfilledQuantity || 0;
      const totalQuantity = contract.totalQuantity || 0;
      const fulfillmentRate = totalQuantity > 0 ? (fulfilledQuantity / totalQuantity) * 100 : 0;

      metrics.push({
        contractId: contract.id,
        contractNumber: contract.contractNumber,
        farmerId: contract.farmerId,
        farmerName: contract.farmerName || 'Unknown',
        contractType: contract.contractType,
        status: contract.status,
        totalQuantity,
        fulfilledQuantity,
        fulfillmentRate,
        qualityScore: contract.qualityScore,
        revenue: contract.totalValue,
        startDate: contract.startDate,
        endDate: contract.endDate,
      });
    }

    return metrics;
  }

  /**
   * Get seasonal trends
   */
  async getSeasonalTrends(year: number): Promise<SeasonalTrends[]> {
    const batches = await this.deps.batchRepository.findMany(
      {},
      { page: 1, pageSize: 10000 },
      { field: 'harvestDate', direction: 'asc' }
    );

    const seasons: Record<string, SeasonalTrends> = {
      SPRING: {
        season: 'SPRING',
        year,
        totalHarvests: 0,
        totalVolume: 0,
        topCrops: [],
        topFarmers: [],
      },
      SUMMER: {
        season: 'SUMMER',
        year,
        totalHarvests: 0,
        totalVolume: 0,
        topCrops: [],
        topFarmers: [],
      },
      AUTUMN: {
        season: 'AUTUMN',
        year,
        totalHarvests: 0,
        totalVolume: 0,
        topCrops: [],
        topFarmers: [],
      },
      WINTER: {
        season: 'WINTER',
        year,
        totalHarvests: 0,
        totalVolume: 0,
        topCrops: [],
        topFarmers: [],
      },
    };

    const getSeason = (date: Date): 'SPRING' | 'SUMMER' | 'AUTUMN' | 'WINTER' => {
      const month = date.getMonth();
      if (month >= 2 && month <= 4) return 'SPRING';
      if (month >= 5 && month <= 7) return 'SUMMER';
      if (month >= 8 && month <= 10) return 'AUTUMN';
      return 'WINTER';
    };

    for (const batch of batches.data as any[]) {
      if (!batch.harvestDate) continue;
      const harvestDate = new Date(batch.harvestDate);
      if (harvestDate.getFullYear() !== year) continue;

      const season = getSeason(harvestDate);
      seasons[season].totalHarvests++;
      seasons[season].totalVolume += batch.quantity || 0;
    }

    return Object.values(seasons);
  }

  /**
   * Get quality trends
   */
  async getQualityTrends(period: string): Promise<QualityTrends> {
    const farmers = await this.deps.farmerRepository.findMany(
      {},
      { page: 1, pageSize: 10000 },
      { field: 'createdAt', direction: 'desc' }
    );

    const now = new Date();
    const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);

    let totalCertificates = 0;
    let activeCertificates = 0;
    let expiredCertificates = 0;
    let expiringSoon = 0;
    const certificationTypes: Record<string, number> = {};
    const qualityScores: number[] = [];

    for (const farmer of farmers.data) {
      for (const cert of farmer.certifications) {
        totalCertificates++;
        if (cert.isActive) {
          activeCertificates++;
          if (cert.expiryDate && cert.expiryDate <= thirtyDaysFromNow && cert.expiryDate > now) {
            expiringSoon++;
          }
        } else {
          expiredCertificates++;
        }

        certificationTypes[cert.type] = (certificationTypes[cert.type] || 0) + 1;
      }

      if (farmer.averageQualityScore !== undefined) {
        qualityScores.push(farmer.averageQualityScore);
      }
    }

    const averageQualityScore =
      qualityScores.length > 0
        ? qualityScores.reduce((sum, score) => sum + score, 0) / qualityScores.length
        : undefined;

    const qualityDistribution = {
      excellent: qualityScores.filter(s => s >= 90).length,
      good: qualityScores.filter(s => s >= 80 && s < 90).length,
      average: qualityScores.filter(s => s >= 70 && s < 80).length,
      belowAverage: qualityScores.filter(s => s < 70).length,
    };

    return {
      period,
      totalCertificates,
      activeCertificates,
      expiredCertificates,
      expiringSoon,
      certificationTypes,
      averageQualityScore,
      qualityDistribution,
    };
  }

  /**
   * Get batch analytics
   */
  async getBatchAnalytics(batchId?: string): Promise<BatchAnalytics[]> {
    const filters = batchId ? { id: batchId } : {};
    const batches = await this.deps.batchRepository.findMany(
      filters,
      { page: 1, pageSize: 10000 },
      { field: 'createdAt', direction: 'desc' }
    );

    const analytics: BatchAnalytics[] = [];

    for (const batch of batches.data as any[]) {
      // Get related contracts
      const contracts = await this.deps.contractRepository.findMany(
        { batchId: batch.id },
        { page: 1, pageSize: 100 },
        { field: 'createdAt', direction: 'desc' }
      );

      // Get related tasks
      const tasks = await this.deps.taskRepository.findMany(
        { relatedBatchId: batch.id },
        { page: 1, pageSize: 100 },
        { field: 'createdAt', direction: 'desc' }
      );

      analytics.push({
        batchId: batch.id,
        batchNumber: batch.batchNumber,
        batchType: batch.batchType,
        status: batch.status,
        quantity: batch.quantity || 0,
        originCountry: batch.originCountry,
        harvestDate: batch.harvestDate,
        expiryDate: batch.expiryDate,
        qualityScore: batch.qualityScore,
        traceabilityDepth: batch.traceabilityDepth || 0,
        relatedContracts: contracts.total,
        relatedTasks: tasks.total,
      });
    }

    return analytics;
  }
}

