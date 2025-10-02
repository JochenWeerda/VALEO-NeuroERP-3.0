/**
 * Mobile Run Repository Interface for VALEO NeuroERP 3.0 Production Domain
 * Repository interface for mobile production unit management
 */

import type { MobileRun } from '../entities/mobile-run';

export interface MobileRunFilters {
  mobileUnitId?: string;
  operatorId?: string;
  customerId?: string;
  status?: 'active' | 'completed';
  dateFrom?: string;
  dateTo?: string;
  calibrationValid?: boolean;
  search?: string;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  filters?: MobileRunFilters;
}

export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

export interface MobileRunStatistics {
  totalRuns: number;
  activeRuns: number;
  completedRuns: number;
  totalDurationHours: number;
  averageDurationHours: number;
  totalFlushMassKg: number;
  calibrationPassRate: number;
}

export interface MobileRunRepository {
  // Basic CRUD operations
  save(tenantId: string, mobileRun: MobileRun): Promise<MobileRun>;
  findById(tenantId: string, id: string): Promise<MobileRun | null>;
  findAll(tenantId: string, filters?: MobileRunFilters): Promise<MobileRun[]>;
  delete(tenantId: string, id: string): Promise<void>;

  // Pagination support
  findWithPagination(tenantId: string, options: PaginationOptions): Promise<PaginatedResult<MobileRun>>;

  // Business queries
  findByMobileUnit(tenantId: string, mobileUnitId: string): Promise<MobileRun[]>;
  findByOperator(tenantId: string, operatorId: string): Promise<MobileRun[]>;
  findByCustomer(tenantId: string, customerId: string): Promise<MobileRun[]>;
  findActiveRuns(tenantId: string): Promise<MobileRun[]>;
  findCompletedRuns(tenantId: string): Promise<MobileRun[]>;
  findByDateRange(tenantId: string, from: string, to: string): Promise<MobileRun[]>;
  findRunsWithValidCalibration(tenantId: string): Promise<MobileRun[]>;
  findRunsWithExpiredCalibration(tenantId: string, maxDays: number): Promise<MobileRun[]>;

  // Location-based queries
  findRunsByLocation(tenantId: string, lat: number, lng: number, radiusKm: number): Promise<MobileRun[]>;
  findRunsNearLocation(tenantId: string, lat: number, lng: number, radiusKm: number): Promise<MobileRun[]>;

  // Cleaning and calibration queries
  findRunsWithCleaningHistory(tenantId: string): Promise<MobileRun[]>;
  findRunsWithFlushHistory(tenantId: string): Promise<MobileRun[]>;
  findRunsRequiringCleaning(tenantId: string): Promise<MobileRun[]>;

  // Bulk operations
  bulkSave(tenantId: string, mobileRuns: MobileRun[]): Promise<MobileRun[]>;
  bulkDelete(tenantId: string, ids: string[]): Promise<void>;

  // Statistics
  getStatistics(tenantId: string, filters?: MobileRunFilters): Promise<MobileRunStatistics>;
  getRunCount(tenantId: string, filters?: MobileRunFilters): Promise<number>;
  getTotalDuration(tenantId: string, filters?: MobileRunFilters): Promise<number>;
  getAverageDuration(tenantId: string, filters?: MobileRunFilters): Promise<number>;
  getTotalFlushMass(tenantId: string, filters?: MobileRunFilters): Promise<number>;
  getCalibrationPassRate(tenantId: string, filters?: MobileRunFilters): Promise<number>;
}

