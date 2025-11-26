/**
 * Farmer Repository
 * Data access layer for Farmer entities
 */

import { Farmer } from '../../domain/entities/farmer';
import {
  FarmerRepository as IFarmerRepository,
  FarmerFilters,
  PaginationOptions,
  SortOptions,
} from '../../domain/services/farmer-portal-service';

// In-memory implementation (would be replaced with database in production)
export class FarmerRepository implements IFarmerRepository {
  private farmers: Map<string, Farmer> = new Map();

  async findById(id: string): Promise<Farmer | null> {
    return this.farmers.get(id) || null;
  }

  async findByEmail(email: string): Promise<Farmer | null> {
    for (const farmer of this.farmers.values()) {
      if (farmer.email.toLowerCase() === email.toLowerCase()) {
        return farmer;
      }
    }
    return null;
  }

  async findByFarmerNumber(farmerNumber: string): Promise<Farmer | null> {
    for (const farmer of this.farmers.values()) {
      if (farmer.farmerNumber === farmerNumber) {
        return farmer;
      }
    }
    return null;
  }

  async findMany(
    filters: FarmerFilters,
    pagination: PaginationOptions,
    sort: SortOptions
  ): Promise<{ data: Farmer[]; total: number }> {
    let filtered = Array.from(this.farmers.values());

    // Apply filters
    if (filters.farmerNumber) {
      filtered = filtered.filter(f => f.farmerNumber.includes(filters.farmerNumber!));
    }
    if (filters.email) {
      filtered = filtered.filter(f => f.email.toLowerCase().includes(filters.email!.toLowerCase()));
    }
    if (filters.farmerType) {
      filtered = filtered.filter(f => f.farmerType === filters.farmerType);
    }
    if (filters.status) {
      filtered = filtered.filter(f => f.status === filters.status);
    }
    if (filters.hasPortalAccess !== undefined) {
      filtered = filtered.filter(f => f.portalAccessEnabled === filters.hasPortalAccess);
    }
    if (filters.certificationType) {
      filtered = filtered.filter(f =>
        f.certifications.some(c => c.type === filters.certificationType)
      );
    }
    if (filters.locationCountry) {
      filtered = filtered.filter(f =>
        f.locations.some(l => l.country === filters.locationCountry)
      );
    }
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(f =>
        f.fullName.toLowerCase().includes(searchLower) ||
        f.email.toLowerCase().includes(searchLower) ||
        f.farmerNumber.includes(searchLower)
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'fullName':
          aValue = a.fullName;
          bValue = b.fullName;
          break;
        case 'farmerNumber':
          aValue = a.farmerNumber;
          bValue = b.farmerNumber;
          break;
        case 'createdAt':
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
          break;
        case 'updatedAt':
          aValue = a.updatedAt.getTime();
          bValue = b.updatedAt.getTime();
          break;
        default:
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
      }

      if (sort.direction === 'asc') {
        return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
      } else {
        return aValue < bValue ? 1 : aValue > bValue ? -1 : 0;
      }
    });

    const total = filtered.length;
    const start = (pagination.page - 1) * pagination.pageSize;
    const end = start + pagination.pageSize;
    const data = filtered.slice(start, end);

    return { data, total };
  }

  async create(farmer: Farmer): Promise<Farmer> {
    this.farmers.set(farmer.id, farmer);
    return farmer;
  }

  async update(farmer: Farmer): Promise<Farmer> {
    if (!this.farmers.has(farmer.id)) {
      throw new Error(`Farmer with id ${farmer.id} not found`);
    }
    this.farmers.set(farmer.id, farmer);
    return farmer;
  }

  async delete(id: string): Promise<void> {
    if (!this.farmers.has(id)) {
      throw new Error(`Farmer with id ${id} not found`);
    }
    this.farmers.delete(id);
  }
}

