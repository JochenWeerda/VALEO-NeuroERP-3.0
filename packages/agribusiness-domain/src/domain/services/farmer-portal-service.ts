/**
 * Farmer Portal Service
 * Self-Service Features for Farmers
 * Based on Odoo portal pattern
 */

import { Farmer, FarmerEntity, CreateFarmerInput, UpdateFarmerInput, FarmerCertification, FarmerCrop, FarmerLocation } from '../entities/farmer';
import { ChangeLogService } from '@valeo-neuroerp/audit-domain';

export interface FarmerRepository {
  findById(id: string): Promise<Farmer | null>;
  findByEmail(email: string): Promise<Farmer | null>;
  findByFarmerNumber(farmerNumber: string): Promise<Farmer | null>;
  findMany(filters: FarmerFilters, pagination: PaginationOptions, sort: SortOptions): Promise<{ data: Farmer[]; total: number }>;
  create(farmer: Farmer): Promise<Farmer>;
  update(farmer: Farmer): Promise<Farmer>;
  delete(id: string): Promise<void>;
}

export interface FarmerFilters {
  farmerNumber?: string;
  email?: string;
  farmerType?: string;
  status?: string;
  search?: string;
  hasPortalAccess?: boolean;
  certificationType?: string;
  locationCountry?: string;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
}

export interface SortOptions {
  field: 'createdAt' | 'updatedAt' | 'fullName' | 'farmerNumber';
  direction: 'asc' | 'desc';
}

export interface FarmerPortalStats {
  totalContracts: number;
  activeContracts: number;
  totalDeliveries: number;
  pendingDeliveries: number;
  totalRevenue?: number;
  averageQualityScore?: number;
  upcomingHarvests: number;
  certifications: number;
  activeCertifications: number;
}

export interface FarmerPortalServiceDependencies {
  farmerRepository: FarmerRepository;
  changeLogService?: ChangeLogService;
  tenantId?: string;
}

export class FarmerPortalService {
  constructor(private deps: FarmerPortalServiceDependencies) {}

  private async logChange(
    action: 'CREATE' | 'UPDATE' | 'DELETE' | 'CANCEL',
    entityId: string,
    oldValue?: Record<string, any>,
    newValue?: Record<string, any>,
    reason?: string,
    userId?: string,
    userName?: string,
    userEmail?: string,
    ipAddress?: string,
    userAgent?: string
  ): Promise<void> {
    if (!this.deps.changeLogService || !this.deps.tenantId) {
      return; // Audit logging is optional
    }

    try {
      switch (action) {
        case 'CREATE':
          await this.deps.changeLogService.logCreate(
            'Farmer',
            entityId,
            newValue || {},
            userId || 'system',
            this.deps.tenantId,
            { userName, userEmail, ipAddress, userAgent }
          );
          break;
        case 'UPDATE':
          await this.deps.changeLogService.logUpdate(
            'Farmer',
            entityId,
            oldValue || {},
            newValue || {},
            userId || 'system',
            this.deps.tenantId,
            { reason, userName, userEmail, ipAddress, userAgent }
          );
          break;
        case 'DELETE':
          if (!reason) {
            throw new Error('Reason is required for DELETE action');
          }
          await this.deps.changeLogService.logDelete(
            'Farmer',
            entityId,
            oldValue || {},
            reason,
            userId || 'system',
            this.deps.tenantId,
            { userName, userEmail, ipAddress, userAgent }
          );
          break;
        case 'CANCEL':
          if (!reason) {
            throw new Error('Reason is required for CANCEL action');
          }
          await this.deps.changeLogService.logCancel(
            'Farmer',
            entityId,
            oldValue || {},
            reason,
            userId || 'system',
            this.deps.tenantId,
            { userName, userEmail, ipAddress, userAgent }
          );
          break;
      }
    } catch (error) {
      // Log error but don't fail the operation
      console.error('Failed to log change:', error);
    }
  }

  /**
   * Register a new farmer
   */
  async registerFarmer(
    input: CreateFarmerInput,
    userId: string,
    options?: { userName?: string; userEmail?: string; ipAddress?: string; userAgent?: string }
  ): Promise<Farmer> {
    // Check if farmer with email already exists
    const existingFarmer = await this.deps.farmerRepository.findByEmail(input.email);
    if (existingFarmer) {
      throw new Error(`Farmer with email ${input.email} already exists`);
    }

    const farmer = FarmerEntity.create(input, userId);
    const created = await this.deps.farmerRepository.create(farmer);
    
    // Log change
    await this.logChange(
      'CREATE',
      created.id,
      undefined,
      this.farmerToRecord(created),
      undefined,
      userId,
      options?.userName,
      options?.userEmail,
      options?.ipAddress,
      options?.userAgent
    );

    return created;
  }

  private farmerToRecord(farmer: Farmer): Record<string, any> {
    return {
      id: farmer.id,
      farmerNumber: farmer.farmerNumber,
      firstName: farmer.firstName,
      lastName: farmer.lastName,
      email: farmer.email,
      farmerType: farmer.farmerType,
      status: farmer.status,
    };
  }

  /**
   * Update farmer profile
   */
  async updateFarmerProfile(
    farmerId: string,
    input: UpdateFarmerInput,
    userId: string,
    options?: { reason?: string; userName?: string; userEmail?: string; ipAddress?: string; userAgent?: string }
  ): Promise<Farmer> {
    const farmer = await this.deps.farmerRepository.findById(farmerId);
    if (!farmer) {
      throw new Error(`Farmer with id ${farmerId} not found`);
    }

    const oldValue = this.farmerToRecord(farmer);
    const updated = FarmerEntity.update(farmer, input, userId);
    const saved = await this.deps.farmerRepository.update(updated);

    // Log change
    await this.logChange(
      'UPDATE',
      saved.id,
      oldValue,
      this.farmerToRecord(saved),
      options?.reason,
      userId,
      options?.userName,
      options?.userEmail,
      options?.ipAddress,
      options?.userAgent
    );

    return saved;
  }

  /**
   * Get farmer by ID
   */
  async getFarmerById(farmerId: string): Promise<Farmer> {
    const farmer = await this.deps.farmerRepository.findById(farmerId);
    if (!farmer) {
      throw new Error(`Farmer with id ${farmerId} not found`);
    }
    return farmer;
  }

  /**
   * Get farmer by email
   */
  async getFarmerByEmail(email: string): Promise<Farmer> {
    const farmer = await this.deps.farmerRepository.findByEmail(email);
    if (!farmer) {
      throw new Error(`Farmer with email ${email} not found`);
    }
    return farmer;
  }

  /**
   * List farmers with filtering and pagination
   */
  async listFarmers(
    filters: FarmerFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 },
    sort: SortOptions = { field: 'createdAt', direction: 'desc' }
  ): Promise<{ data: Farmer[]; total: number; page: number; pageSize: number }> {
    const result = await this.deps.farmerRepository.findMany(filters, pagination, sort);
    return {
      ...result,
      page: pagination.page,
      pageSize: pagination.pageSize,
    };
  }

  /**
   * Enable portal access for farmer
   */
  async enablePortalAccess(farmerId: string): Promise<Farmer> {
    const farmer = await this.getFarmerById(farmerId);
    const updated = FarmerEntity.enablePortalAccess(farmer);
    return await this.deps.farmerRepository.update(updated);
  }

  /**
   * Disable portal access for farmer
   */
  async disablePortalAccess(farmerId: string): Promise<Farmer> {
    const farmer = await this.getFarmerById(farmerId);
    const updated = FarmerEntity.disablePortalAccess(farmer);
    return await this.deps.farmerRepository.update(updated);
  }

  /**
   * Record portal login
   */
  async recordPortalLogin(farmerId: string): Promise<Farmer> {
    const farmer = await this.getFarmerById(farmerId);
    if (!farmer.portalAccessEnabled) {
      throw new Error('Portal access is not enabled for this farmer');
    }
    const updated = FarmerEntity.recordPortalLogin(farmer);
    return await this.deps.farmerRepository.update(updated);
  }

  /**
   * Add location to farmer
   */
  async addLocation(farmerId: string, location: Omit<FarmerLocation, 'id' | 'isPrimary'>): Promise<Farmer> {
    const farmer = await this.getFarmerById(farmerId);
    const updated = FarmerEntity.addLocation(farmer, location);
    return await this.deps.farmerRepository.update(updated);
  }

  /**
   * Add certification to farmer
   */
  async addCertification(farmerId: string, certification: Omit<FarmerCertification, 'id' | 'isActive'>): Promise<Farmer> {
    const farmer = await this.getFarmerById(farmerId);
    const updated = FarmerEntity.addCertification(farmer, certification);
    return await this.deps.farmerRepository.update(updated);
  }

  /**
   * Add crop to farmer
   */
  async addCrop(farmerId: string, crop: Omit<FarmerCrop, 'id' | 'status'>): Promise<Farmer> {
    const farmer = await this.getFarmerById(farmerId);
    const updated = FarmerEntity.addCrop(farmer, crop);
    return await this.deps.farmerRepository.update(updated);
  }

  /**
   * Get farmer portal statistics
   */
  async getFarmerPortalStats(farmerId: string): Promise<FarmerPortalStats> {
    const farmer = await this.getFarmerById(farmerId);
    
    // Calculate upcoming harvests (crops with status PLANTED or GROWING)
    const upcomingHarvests = farmer.crops.filter(
      crop => crop.status === 'PLANTED' || crop.status === 'GROWING'
    ).length;

    // Count active certifications
    const activeCertifications = farmer.certifications.filter(cert => cert.isActive).length;

    return {
      totalContracts: farmer.totalContracts,
      activeContracts: 0, // Would need to query contracts service
      totalDeliveries: farmer.totalDeliveries,
      pendingDeliveries: 0, // Would need to query deliveries service
      totalRevenue: farmer.totalRevenue,
      averageQualityScore: farmer.averageQualityScore,
      upcomingHarvests,
      certifications: farmer.certifications.length,
      activeCertifications,
    };
  }

  /**
   * Search farmers
   */
  async searchFarmers(query: string, limit: number = 20): Promise<Farmer[]> {
    const result = await this.deps.farmerRepository.findMany(
      { search: query },
      { page: 1, pageSize: limit },
      { field: 'fullName', direction: 'asc' }
    );
    return result.data;
  }

  /**
   * Verify farmer email
   */
  async verifyFarmerEmail(farmerId: string): Promise<Farmer> {
    const farmer = await this.getFarmerById(farmerId);
    // Update status to VERIFIED if currently PENDING
    if (farmer.status === 'PENDING') {
      const updated = FarmerEntity.update(farmer, { status: 'VERIFIED' }, farmer.updatedBy);
      return await this.deps.farmerRepository.update(updated);
    }
    return farmer;
  }

  /**
   * Delete farmer (soft delete)
   */
  async deleteFarmer(
    farmerId: string,
    reason: string,
    userId: string,
    options?: { userName?: string; userEmail?: string; ipAddress?: string; userAgent?: string }
  ): Promise<void> {
    const farmer = await this.getFarmerById(farmerId);
    const oldValue = this.farmerToRecord(farmer);

    // Log change before deletion
    await this.logChange(
      'DELETE',
      farmerId,
      oldValue,
      undefined,
      reason,
      userId,
      options?.userName,
      options?.userEmail,
      options?.ipAddress,
      options?.userAgent
    );

    await this.deps.farmerRepository.delete(farmerId);
  }

  /**
   * Suspend farmer account
   */
  async suspendFarmer(
    farmerId: string,
    reason: string,
    userId: string,
    options?: { userName?: string; userEmail?: string; ipAddress?: string; userAgent?: string }
  ): Promise<Farmer> {
    const farmer = await this.getFarmerById(farmerId);
    const oldValue = this.farmerToRecord(farmer);
    const updated = FarmerEntity.update(farmer, { status: 'SUSPENDED' }, userId);
    // Disable portal access when suspended
    const withDisabledPortal = FarmerEntity.disablePortalAccess(updated);
    const saved = await this.deps.farmerRepository.update(withDisabledPortal);

    // Log change
    await this.logChange(
      'UPDATE',
      saved.id,
      oldValue,
      this.farmerToRecord(saved),
      reason,
      userId,
      options?.userName,
      options?.userEmail,
      options?.ipAddress,
      options?.userAgent
    );

    return saved;
  }

  /**
   * Activate farmer account
   */
  async activateFarmer(farmerId: string): Promise<Farmer> {
    const farmer = await this.getFarmerById(farmerId);
    const updated = FarmerEntity.update(farmer, { status: 'ACTIVE' }, farmer.updatedBy);
    return await this.deps.farmerRepository.update(updated);
  }
}

