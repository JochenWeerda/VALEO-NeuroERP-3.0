/**
 * Warehouse Entity
 * Multi-Location Warehouse System for Agribusiness
 * Based on Odoo stock Multi-Location pattern
 */

import { v4 as uuidv4 } from 'uuid';

export type WarehouseLocationType = 
  | 'SILO'           // Silo (für Getreide, Saatgut)
  | 'OUTDOOR'        // Freilager (für Düngemittel, Futtermittel)
  | 'INDOOR'         // Hallenlager (für verpackte Produkte)
  | 'COLD_STORAGE'   // Kühllager
  | 'HAZMAT';        // Gefahrstofflager

export type WarehouseStatus = 
  | 'ACTIVE'         // Aktiv
  | 'INACTIVE'       // Inaktiv
  | 'MAINTENANCE';   // Wartung

export interface WarehouseLocation {
  locationId: string;
  locationCode: string;
  locationType: WarehouseLocationType;
  parentLocationId?: string; // For hierarchical structure
  warehouseId: string;
  capacity: {
    maxQuantity?: number;
    maxWeight?: number;
    maxVolume?: number;
    unitOfMeasure: string;
  };
  currentQuantity?: number;
  currentWeight?: number;
  currentVolume?: number;
  coordinates?: {
    latitude: number;
    longitude: number;
    altitude?: number;
  };
  temperatureControlled: boolean;
  temperatureMin?: number;
  temperatureMax?: number;
  humidityControlled: boolean;
  humidityMin?: number;
  humidityMax?: number;
  active: boolean;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateWarehouseInput {
  name: string;
  code: string;
  address: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  status?: WarehouseStatus;
  notes?: string;
}

export interface UpdateWarehouseInput {
  name?: string;
  address?: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  status?: WarehouseStatus;
  notes?: string;
}

export class Warehouse {
  public readonly id: string;
  public name: string;
  public code: string;
  public address: {
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  public coordinates?: {
    latitude: number;
    longitude: number;
  };
  public status: WarehouseStatus;
  public locations: WarehouseLocation[];
  public notes?: string;
  public version: number;
  public readonly createdAt: Date;
  public updatedAt: Date;
  public readonly createdBy: string;
  public updatedBy?: string;

  constructor(
    name: string,
    code: string,
    address: {
      street: string;
      postalCode: string;
      city: string;
      country: string;
      state?: string;
    },
    createdBy: string,
    options: {
      id?: string;
      coordinates?: { latitude: number; longitude: number };
      status?: WarehouseStatus;
      notes?: string;
    } = {}
  ) {
    this.id = options.id || uuidv4();
    this.name = name;
    this.code = code;
    this.address = address;
    this.coordinates = options.coordinates;
    this.status = options.status || 'ACTIVE';
    this.locations = [];
    this.notes = options.notes;
    this.version = 1;
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.createdBy = createdBy;

    this.validate();
  }

  private validate(): void {
    if (!this.name || this.name.trim() === '') {
      throw new Error('Warehouse name is required');
    }

    if (!this.code || this.code.trim() === '') {
      throw new Error('Warehouse code is required');
    }

    if (!this.address.street || !this.address.postalCode || !this.address.city || !this.address.country) {
      throw new Error('Complete warehouse address is required');
    }
  }

  public updateBasicInfo(updates: UpdateWarehouseInput, updatedBy: string): void {
    if (updates.name !== undefined) this.name = updates.name;
    if (updates.address !== undefined) this.address = updates.address;
    if (updates.status !== undefined) this.status = updates.status;
    if (updates.notes !== undefined) this.notes = updates.notes;

    this.updatedBy = updatedBy;
    this.updatedAt = new Date();
    this.version++;
    this.validate();
  }

  public addLocation(location: WarehouseLocation): void {
    // Check for duplicate location code
    const existing = this.locations.find(l => l.locationCode === location.locationCode);
    if (existing) {
      throw new Error(`Location code ${location.locationCode} already exists in warehouse`);
    }

    // Validate parent location if provided
    if (location.parentLocationId) {
      const parent = this.locations.find(l => l.locationId === location.parentLocationId);
      if (!parent) {
        throw new Error('Parent location not found in warehouse');
      }
    }

    this.locations.push(location);
    this.updatedAt = new Date();
    this.version++;
  }

  public updateLocation(locationId: string, updates: Partial<Omit<WarehouseLocation, 'locationId' | 'warehouseId' | 'createdAt' | 'updatedAt'>>): void {
    const locationIndex = this.locations.findIndex(l => l.locationId === locationId);
    if (locationIndex === -1) {
      throw new Error('Location not found in warehouse');
    }

    const location = this.locations[locationIndex];
    
    // Validate parent location if changed
    if (updates.parentLocationId !== undefined && updates.parentLocationId !== location.parentLocationId) {
      if (updates.parentLocationId) {
        const parent = this.locations.find(l => l.locationId === updates.parentLocationId);
        if (!parent) {
          throw new Error('Parent location not found in warehouse');
        }
        // Prevent circular references
        if (this.hasCircularReference(locationId, updates.parentLocationId)) {
          throw new Error('Circular reference detected in location hierarchy');
        }
      }
    }

    Object.assign(this.locations[locationIndex], updates, { updatedAt: new Date() });
    this.updatedAt = new Date();
    this.version++;
  }

  public removeLocation(locationId: string): void {
    // Check for child locations
    const hasChildren = this.locations.some(l => l.parentLocationId === locationId);
    if (hasChildren) {
      throw new Error('Cannot remove location with child locations');
    }

    const locationIndex = this.locations.findIndex(l => l.locationId === locationId);
    if (locationIndex === -1) {
      throw new Error('Location not found in warehouse');
    }

    this.locations.splice(locationIndex, 1);
    this.updatedAt = new Date();
    this.version++;
  }

  private hasCircularReference(locationId: string, parentId: string): boolean {
    let currentParentId: string | undefined = parentId;
    const visited = new Set<string>();

    while (currentParentId) {
      if (visited.has(currentParentId)) {
        return true; // Circular reference detected
      }
      if (currentParentId === locationId) {
        return true; // Would create circular reference
      }
      visited.add(currentParentId);
      const parent = this.locations.find(l => l.locationId === currentParentId);
      currentParentId = parent?.parentLocationId;
    }

    return false;
  }

  public getLocationById(locationId: string): WarehouseLocation | undefined {
    return this.locations.find(l => l.locationId === locationId);
  }

  public getLocationByCode(locationCode: string): WarehouseLocation | undefined {
    return this.locations.find(l => l.locationCode === locationCode);
  }

  public getChildLocations(parentLocationId: string): WarehouseLocation[] {
    return this.locations.filter(l => l.parentLocationId === parentLocationId);
  }

  public getRootLocations(): WarehouseLocation[] {
    return this.locations.filter(l => !l.parentLocationId);
  }

  public getLocationsByType(locationType: WarehouseLocationType): WarehouseLocation[] {
    return this.locations.filter(l => l.locationType === locationType);
  }

  public getTotalCapacity(): {
    totalQuantity?: number;
    totalWeight?: number;
    totalVolume?: number;
  } {
    return this.locations.reduce((totals, location) => {
      if (location.capacity.maxQuantity) {
        totals.totalQuantity = (totals.totalQuantity || 0) + location.capacity.maxQuantity;
      }
      if (location.capacity.maxWeight) {
        totals.totalWeight = (totals.totalWeight || 0) + location.capacity.maxWeight;
      }
      if (location.capacity.maxVolume) {
        totals.totalVolume = (totals.totalVolume || 0) + location.capacity.maxVolume;
      }
      return totals;
    }, {} as { totalQuantity?: number; totalWeight?: number; totalVolume?: number });
  }

  public getCurrentUtilization(): {
    totalQuantity?: number;
    totalWeight?: number;
    totalVolume?: number;
    utilizationPercentage?: number;
  } {
    const current = this.locations.reduce((totals, location) => {
      if (location.currentQuantity) {
        totals.totalQuantity = (totals.totalQuantity || 0) + location.currentQuantity;
      }
      if (location.currentWeight) {
        totals.totalWeight = (totals.totalWeight || 0) + location.currentWeight;
      }
      if (location.currentVolume) {
        totals.totalVolume = (totals.totalVolume || 0) + location.currentVolume;
      }
      return totals;
    }, {} as { totalQuantity?: number; totalWeight?: number; totalVolume?: number });

    const capacity = this.getTotalCapacity();
    let utilizationPercentage: number | undefined;

    if (capacity.totalQuantity && current.totalQuantity) {
      utilizationPercentage = (current.totalQuantity / capacity.totalQuantity) * 100;
    } else if (capacity.totalWeight && current.totalWeight) {
      utilizationPercentage = (current.totalWeight / capacity.totalWeight) * 100;
    } else if (capacity.totalVolume && current.totalVolume) {
      utilizationPercentage = (current.totalVolume / capacity.totalVolume) * 100;
    }

    return {
      ...current,
      utilizationPercentage
    };
  }

  public activate(): void {
    this.status = 'ACTIVE';
    this.updatedAt = new Date();
    this.version++;
  }

  public deactivate(): void {
    this.status = 'INACTIVE';
    this.updatedAt = new Date();
    this.version++;
  }

  public setMaintenance(): void {
    this.status = 'MAINTENANCE';
    this.updatedAt = new Date();
    this.version++;
  }

  public toJSON(): any {
    return {
      id: this.id,
      name: this.name,
      code: this.code,
      address: this.address,
      coordinates: this.coordinates,
      status: this.status,
      locations: this.locations.map(loc => ({
        ...loc,
        createdAt: loc.createdAt.toISOString(),
        updatedAt: loc.updatedAt.toISOString()
      })),
      totalCapacity: this.getTotalCapacity(),
      currentUtilization: this.getCurrentUtilization(),
      notes: this.notes,
      version: this.version,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      createdBy: this.createdBy,
      updatedBy: this.updatedBy
    };
  }
}
