/**
 * Quality Repository Interface for VALEO NeuroERP 3.0 Production Domain
 * Repository interface for quality management and non-conformity handling
 */

import type { 
  SamplingPlan, 
  SamplingResult, 
  RetainedSample, 
  NonConformity, 
  CAPA 
} from '../entities/quality';

export interface SamplingPlanFilters {
  for?: 'mobile' | 'plant';
  frequency?: 'perBatch' | 'perN';
  retainedSamples?: boolean;
  search?: string;
}

export interface SamplingResultFilters {
  batchId?: string;
  analyte?: string;
  decision?: 'Pass' | 'Investigate' | 'Reject';
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface NonConformityFilters {
  refType?: 'batchId' | 'mixOrderId' | 'mobileRunId';
  refId?: string;
  type?: 'Contamination' | 'SpecOut' | 'Equipment' | 'Process';
  severity?: 'Low' | 'Medium' | 'High' | 'Critical';
  status?: 'Open' | 'InProgress' | 'Closed';
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface CAPAFilters {
  ncId?: string;
  type?: 'Correction' | 'CorrectiveAction' | 'PreventiveAction';
  priority?: 'Low' | 'Medium' | 'High' | 'Critical';
  status?: 'Open' | 'InProgress' | 'Closed';
  assignedTo?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface PaginationOptions<T = any> {
  page: number;
  pageSize: number;
  filters?: T;
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

export interface QualityStatistics {
  totalSamples: number;
  passedSamples: number;
  rejectedSamples: number;
  investigationSamples: number;
  passRate: number;
  totalNCs: number;
  openNCs: number;
  closedNCs: number;
  criticalNCs: number;
  totalCAPAs: number;
  openCAPAs: number;
  closedCAPAs: number;
  overdueCAPAs: number;
}

// Sampling Plan Repository
export interface SamplingPlanRepository {
  save(tenantId: string, plan: SamplingPlan): Promise<SamplingPlan>;
  findById(tenantId: string, id: string): Promise<SamplingPlan | null>;
  findAll(tenantId: string, filters?: SamplingPlanFilters): Promise<SamplingPlan[]>;
  findWithPagination(tenantId: string, options: PaginationOptions<SamplingPlanFilters>): Promise<PaginatedResult<SamplingPlan>>;
  findByType(tenantId: string, type: 'mobile' | 'plant'): Promise<SamplingPlan[]>;
  delete(tenantId: string, id: string): Promise<void>;
}

// Sampling Result Repository
export interface SamplingResultRepository {
  save(tenantId: string, result: SamplingResult): Promise<SamplingResult>;
  findById(tenantId: string, id: string): Promise<SamplingResult | null>;
  findAll(tenantId: string, filters?: SamplingResultFilters): Promise<SamplingResult[]>;
  findWithPagination(tenantId: string, options: PaginationOptions<SamplingResultFilters>): Promise<PaginatedResult<SamplingResult>>;
  findByBatch(tenantId: string, batchId: string): Promise<SamplingResult[]>;
  findByAnalyte(tenantId: string, analyte: string): Promise<SamplingResult[]>;
  findByDecision(tenantId: string, decision: SamplingResult['decision']): Promise<SamplingResult[]>;
  delete(tenantId: string, id: string): Promise<void>;
}

// Retained Sample Repository
export interface RetainedSampleRepository {
  save(tenantId: string, sample: RetainedSample): Promise<RetainedSample>;
  findById(tenantId: string, id: string): Promise<RetainedSample | null>;
  findAll(tenantId: string): Promise<RetainedSample[]>;
  findByBatch(tenantId: string, batchId: string): Promise<RetainedSample[]>;
  findExpired(tenantId: string): Promise<RetainedSample[]>;
  findDisposed(tenantId: string): Promise<RetainedSample[]>;
  delete(tenantId: string, id: string): Promise<void>;
}

// Non-Conformity Repository
export interface NonConformityRepository {
  save(tenantId: string, nc: NonConformity): Promise<NonConformity>;
  findById(tenantId: string, id: string): Promise<NonConformity | null>;
  findAll(tenantId: string, filters?: NonConformityFilters): Promise<NonConformity[]>;
  findWithPagination(tenantId: string, options: PaginationOptions<NonConformityFilters>): Promise<PaginatedResult<NonConformity>>;
  findByReference(tenantId: string, refType: NonConformity['refType'], refId: string): Promise<NonConformity[]>;
  findByType(tenantId: string, type: NonConformity['type']): Promise<NonConformity[]>;
  findBySeverity(tenantId: string, severity: NonConformity['severity']): Promise<NonConformity[]>;
  findByStatus(tenantId: string, status: NonConformity['status']): Promise<NonConformity[]>;
  findOpen(tenantId: string): Promise<NonConformity[]>;
  findCritical(tenantId: string): Promise<NonConformity[]>;
  delete(tenantId: string, id: string): Promise<void>;
}

// CAPA Repository
export interface CAPARepository {
  save(tenantId: string, capa: CAPA): Promise<CAPA>;
  findById(tenantId: string, id: string): Promise<CAPA | null>;
  findAll(tenantId: string, filters?: CAPAFilters): Promise<CAPA[]>;
  findWithPagination(tenantId: string, options: PaginationOptions<CAPAFilters>): Promise<PaginatedResult<CAPA>>;
  findByNC(tenantId: string, ncId: string): Promise<CAPA[]>;
  findByType(tenantId: string, type: CAPA['type']): Promise<CAPA[]>;
  findByPriority(tenantId: string, priority: CAPA['priority']): Promise<CAPA[]>;
  findByStatus(tenantId: string, status: CAPA['status']): Promise<CAPA[]>;
  findByAssignee(tenantId: string, assignedTo: string): Promise<CAPA[]>;
  findOpen(tenantId: string): Promise<CAPA[]>;
  findOverdue(tenantId: string): Promise<CAPA[]>;
  findCritical(tenantId: string): Promise<CAPA[]>;
  delete(tenantId: string, id: string): Promise<void>;
}

// Combined Quality Repository
export interface QualityRepository {
  // Sampling Plan methods
  saveSamplingPlan(tenantId: string, plan: SamplingPlan): Promise<SamplingPlan>;
  findSamplingPlanById(tenantId: string, id: string): Promise<SamplingPlan | null>;
  findAllSamplingPlans(tenantId: string, filters?: SamplingPlanFilters): Promise<SamplingPlan[]>;
  findSamplingPlansWithPagination(tenantId: string, options: PaginationOptions<SamplingPlanFilters>): Promise<PaginatedResult<SamplingPlan>>;
  findSamplingPlansByType(tenantId: string, type: 'mobile' | 'plant'): Promise<SamplingPlan[]>;
  deleteSamplingPlan(tenantId: string, id: string): Promise<void>;

  // Sampling Result methods
  saveSamplingResult(tenantId: string, result: SamplingResult): Promise<SamplingResult>;
  findSamplingResultById(tenantId: string, id: string): Promise<SamplingResult | null>;
  findAllSamplingResults(tenantId: string, filters?: SamplingResultFilters): Promise<SamplingResult[]>;
  findSamplingResultsWithPagination(tenantId: string, options: PaginationOptions<SamplingResultFilters>): Promise<PaginatedResult<SamplingResult>>;
  findSamplingResultsByBatch(tenantId: string, batchId: string): Promise<SamplingResult[]>;
  findSamplingResultsByAnalyte(tenantId: string, analyte: string): Promise<SamplingResult[]>;
  findSamplingResultsByDecision(tenantId: string, decision: SamplingResult['decision']): Promise<SamplingResult[]>;
  deleteSamplingResult(tenantId: string, id: string): Promise<void>;

  // Retained Sample methods
  saveRetainedSample(tenantId: string, sample: RetainedSample): Promise<RetainedSample>;
  findRetainedSampleById(tenantId: string, id: string): Promise<RetainedSample | null>;
  findAllRetainedSamples(tenantId: string): Promise<RetainedSample[]>;
  findRetainedSamplesByBatch(tenantId: string, batchId: string): Promise<RetainedSample[]>;
  findExpiredRetainedSamples(tenantId: string): Promise<RetainedSample[]>;
  findDisposedRetainedSamples(tenantId: string): Promise<RetainedSample[]>;
  deleteRetainedSample(tenantId: string, id: string): Promise<void>;

  // Non-Conformity methods
  saveNonConformity(tenantId: string, nc: NonConformity): Promise<NonConformity>;
  findNonConformityById(tenantId: string, id: string): Promise<NonConformity | null>;
  findAllNonConformities(tenantId: string, filters?: NonConformityFilters): Promise<NonConformity[]>;
  findNonConformitiesWithPagination(tenantId: string, options: PaginationOptions<NonConformityFilters>): Promise<PaginatedResult<NonConformity>>;
  findNonConformitiesByReference(tenantId: string, refType: NonConformity['refType'], refId: string): Promise<NonConformity[]>;
  findNonConformitiesByType(tenantId: string, type: NonConformity['type']): Promise<NonConformity[]>;
  findNonConformitiesBySeverity(tenantId: string, severity: NonConformity['severity']): Promise<NonConformity[]>;
  findNonConformitiesByStatus(tenantId: string, status: NonConformity['status']): Promise<NonConformity[]>;
  findOpenNonConformities(tenantId: string): Promise<NonConformity[]>;
  findCriticalNonConformities(tenantId: string): Promise<NonConformity[]>;
  deleteNonConformity(tenantId: string, id: string): Promise<void>;

  // CAPA methods
  saveCAPA(tenantId: string, capa: CAPA): Promise<CAPA>;
  findCAPAById(tenantId: string, id: string): Promise<CAPA | null>;
  findAllCAPAs(tenantId: string, filters?: CAPAFilters): Promise<CAPA[]>;
  findCAPAsWithPagination(tenantId: string, options: PaginationOptions<CAPAFilters>): Promise<PaginatedResult<CAPA>>;
  findCAPAsByNC(tenantId: string, ncId: string): Promise<CAPA[]>;
  findCAPAsByType(tenantId: string, type: CAPA['type']): Promise<CAPA[]>;
  findCAPAsByPriority(tenantId: string, priority: CAPA['priority']): Promise<CAPA[]>;
  findCAPAsByStatus(tenantId: string, status: CAPA['status']): Promise<CAPA[]>;
  findCAPAsByAssignee(tenantId: string, assignedTo: string): Promise<CAPA[]>;
  findOpenCAPAs(tenantId: string): Promise<CAPA[]>;
  findOverdueCAPAs(tenantId: string): Promise<CAPA[]>;
  findCriticalCAPAs(tenantId: string): Promise<CAPA[]>;
  deleteCAPA(tenantId: string, id: string): Promise<void>;
  
  // Combined statistics
  getQualityStatistics(tenantId: string): Promise<QualityStatistics>;
  
  // Cross-entity queries
  getNCsForBatch(tenantId: string, batchId: string): Promise<NonConformity[]>;
  getCAPAsForNC(tenantId: string, ncId: string): Promise<CAPA[]>;
  getSamplingResultsForBatch(tenantId: string, batchId: string): Promise<SamplingResult[]>;
  getRetainedSamplesForBatch(tenantId: string, batchId: string): Promise<RetainedSample[]>;
}
