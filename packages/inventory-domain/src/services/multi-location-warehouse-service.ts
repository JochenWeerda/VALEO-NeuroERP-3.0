/**
 * Multi-Location Warehouse Service
 * Complete Multi-Location Warehouse Management for Agribusiness
 * Based on Odoo stock Multi-Location pattern
 */

import { Warehouse, WarehouseLocation, WarehouseLocationType, CreateWarehouseInput, UpdateWarehouseInput, WarehouseStatus } from '../core/entities/warehouse';

export interface MultiLocationWarehouseServiceDependencies {
  // Repository would be injected here in production
}

export class MultiLocationWarehouseService {
  private warehouses: Map<string, Warehouse> = new Map();

  constructor(private deps: MultiLocationWarehouseServiceDependencies) {}

  // ======================================
  // WAREHOUSE CRUD OPERATIONS
  // ======================================

  async createWarehouse(
    input: CreateWarehouseInput,
    createdBy: string
  ): Promise<Warehouse> {
    const warehouse = new Warehouse(
      input.name,
      input.code,
      input.address,
      createdBy,
      {
        coordinates: input.coordinates,
        status: input.status,
        notes: input.notes
      }
    );

    this.warehouses.set(warehouse.id, warehouse);
    return warehouse;
  }

  async getWarehouseById(id: string): Promise<Warehouse | null> {
    return this.warehouses.get(id) || null;
  }

  async getWarehouseByCode(code: string): Promise<Warehouse | null> {
    for (const warehouse of this.warehouses.values()) {
      if (warehouse.code === code) {
        return warehouse;
      }
    }
    return null;
  }

  async updateWarehouse(
    id: string,
    updates: UpdateWarehouseInput,
    updatedBy: string
  ): Promise<Warehouse> {
    const warehouse = await this.getWarehouseById(id);
    if (!warehouse) {
      throw new Error('Warehouse not found');
    }

    warehouse.updateBasicInfo(updates, updatedBy);
    this.warehouses.set(id, warehouse);
    return warehouse;
  }

  async deleteWarehouse(id: string): Promise<boolean> {
    const warehouse = await this.getWarehouseById(id);
    if (!warehouse) {
      return false;
    }

    if (warehouse.locations.length > 0) {
      throw new Error('Cannot delete warehouse with locations');
    }

    return this.warehouses.delete(id);
  }

  async listWarehouses(filter?: {
    status?: WarehouseStatus;
    city?: string;
    country?: string;
  }): Promise<Warehouse[]> {
    let warehouses = Array.from(this.warehouses.values());

    if (filter?.status) {
      warehouses = warehouses.filter(w => w.status === filter.status);
    }

    if (filter?.city) {
      warehouses = warehouses.filter(w => w.address.city === filter.city);
    }

    if (filter?.country) {
      warehouses = warehouses.filter(w => w.address.country === filter.country);
    }

    return warehouses.sort((a, b) => a.name.localeCompare(b.name));
  }

  // ======================================
  // LOCATION MANAGEMENT
  // ======================================

  async addLocationToWarehouse(
    warehouseId: string,
    location: Omit<WarehouseLocation, 'locationId' | 'warehouseId' | 'createdAt' | 'updatedAt'>
  ): Promise<Warehouse> {
    const warehouse = await this.getWarehouseById(warehouseId);
    if (!warehouse) {
      throw new Error('Warehouse not found');
    }

    const newLocation: WarehouseLocation = {
      ...location,
      locationId: crypto.randomUUID(),
      warehouseId: warehouse.id,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    warehouse.addLocation(newLocation);
    this.warehouses.set(warehouseId, warehouse);
    return warehouse;
  }

  async updateLocationInWarehouse(
    warehouseId: string,
    locationId: string,
    updates: Partial<Omit<WarehouseLocation, 'locationId' | 'warehouseId' | 'createdAt' | 'updatedAt'>>
  ): Promise<Warehouse> {
    const warehouse = await this.getWarehouseById(warehouseId);
    if (!warehouse) {
      throw new Error('Warehouse not found');
    }

    warehouse.updateLocation(locationId, updates);
    this.warehouses.set(warehouseId, warehouse);
    return warehouse;
  }

  async removeLocationFromWarehouse(
    warehouseId: string,
    locationId: string
  ): Promise<Warehouse> {
    const warehouse = await this.getWarehouseById(warehouseId);
    if (!warehouse) {
      throw new Error('Warehouse not found');
    }

    warehouse.removeLocation(locationId);
    this.warehouses.set(warehouseId, warehouse);
    return warehouse;
  }

  async getLocationsByType(
    warehouseId: string,
    locationType: WarehouseLocationType
  ): Promise<WarehouseLocation[]> {
    const warehouse = await this.getWarehouseById(warehouseId);
    if (!warehouse) {
      throw new Error('Warehouse not found');
    }

    return warehouse.getLocationsByType(locationType);
  }

  async getLocationHierarchy(
    warehouseId: string
  ): Promise<{
    root: WarehouseLocation[];
    tree: Array<{ location: WarehouseLocation; children: WarehouseLocation[] }>;
  }> {
    const warehouse = await this.getWarehouseById(warehouseId);
    if (!warehouse) {
      throw new Error('Warehouse not found');
    }

    const root = warehouse.getRootLocations();
    const tree = root.map(rootLocation => {
      const buildChildren = (parentId: string): WarehouseLocation[] => {
        const children = warehouse.getChildLocations(parentId);
        return children.flatMap(child => [child, ...buildChildren(child.locationId)]);
      };

      return {
        location: rootLocation,
        children: buildChildren(rootLocation.locationId)
      };
    });

    return { root, tree };
  }

  // ======================================
  // BUSINESS INTELLIGENCE
  // ======================================

  async getWarehouseStatistics(warehouseId: string): Promise<{
    totalLocations: number;
    locationsByType: Record<WarehouseLocationType, number>;
    totalCapacity: { totalQuantity?: number; totalWeight?: number; totalVolume?: number };
    currentUtilization: { totalQuantity?: number; totalWeight?: number; totalVolume?: number; utilizationPercentage?: number };
    activeLocations: number;
    inactiveLocations: number;
  }> {
    const warehouse = await this.getWarehouseById(warehouseId);
    if (!warehouse) {
      throw new Error('Warehouse not found');
    }

    const locationsByType: Record<WarehouseLocationType, number> = {
      'SILO': 0,
      'OUTDOOR': 0,
      'INDOOR': 0,
      'COLD_STORAGE': 0,
      'HAZMAT': 0
    };

    let activeLocations = 0;
    let inactiveLocations = 0;

    for (const location of warehouse.locations) {
      locationsByType[location.locationType]++;
      if (location.active) {
        activeLocations++;
      } else {
        inactiveLocations++;
      }
    }

    return {
      totalLocations: warehouse.locations.length,
      locationsByType,
      totalCapacity: warehouse.getTotalCapacity(),
      currentUtilization: warehouse.getCurrentUtilization(),
      activeLocations,
      inactiveLocations
    };
  }
}
