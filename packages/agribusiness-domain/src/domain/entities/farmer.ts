/**
 * Farmer Entity
 * Farmer Portal - Self-Service Features for Farmers
 * Based on Odoo res.partner pattern with farmer-specific extensions
 */

import { randomUUID } from 'crypto';

export type FarmerStatus =
  | 'ACTIVE'           // Aktiv
  | 'INACTIVE'         // Inaktiv
  | 'PENDING'          // Ausstehend
  | 'SUSPENDED'        // Gesperrt
  | 'VERIFIED';        // Verifiziert

export type FarmerType =
  | 'INDIVIDUAL'       // Einzelperson
  | 'COOPERATIVE'      // Genossenschaft
  | 'COMPANY'          // Unternehmen
  | 'ASSOCIATION';     // Verein

export type CertificationType =
  | 'ORGANIC'          // Bio-Zertifizierung
  | 'GLOBALGAP'        // GlobalGAP
  | 'FAIRTRADE'        // Fairtrade
  | 'RAINFOREST'       // Rainforest Alliance
  | 'UTZ';             // UTZ Certified

export interface FarmerCertification {
  id: string;
  type: CertificationType;
  certificateNumber: string;
  issuedBy: string;
  issuedDate: Date;
  expiryDate?: Date;
  isActive: boolean;
  documents?: string[]; // URLs to certificate documents
}

export interface FarmerLocation {
  id: string;
  name: string;
  address: string;
  city: string;
  postalCode: string;
  country: string;
  latitude?: number;
  longitude?: number;
  areaHectares?: number; // Farm area in hectares
  isPrimary: boolean;
}

export interface FarmerCrop {
  id: string;
  cropType: string;
  variety?: string;
  season: string;
  areaHectares: number;
  expectedYield?: number;
  harvestDate?: Date;
  status: 'PLANNED' | 'PLANTED' | 'GROWING' | 'HARVESTED' | 'SOLD';
}

export interface FarmerProfile {
  id: string;
  farmerId: string;
  bio?: string;
  yearsOfExperience?: number;
  specializations?: string[];
  languages?: string[];
  preferredContactMethod: 'EMAIL' | 'PHONE' | 'SMS' | 'PORTAL';
  notificationPreferences: {
    email: boolean;
    sms: boolean;
    push: boolean;
    portal: boolean;
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateFarmerInput {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  farmerType: FarmerType;
  status?: FarmerStatus;
  taxId?: string;
  vatNumber?: string;
  locations?: Omit<FarmerLocation, 'id' | 'isPrimary'>[];
  certifications?: Omit<FarmerCertification, 'id' | 'isActive'>[];
  crops?: Omit<FarmerCrop, 'id' | 'status'>[];
  profile?: Omit<FarmerProfile, 'id' | 'farmerId' | 'createdAt' | 'updatedAt'>;
}

export interface UpdateFarmerInput {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  farmerType?: FarmerType;
  status?: FarmerStatus;
  taxId?: string;
  vatNumber?: string;
  profile?: Partial<FarmerProfile>;
}

export interface Farmer {
  id: string;
  farmerNumber: string; // Unique farmer identifier
  firstName: string;
  lastName: string;
  fullName: string;
  email: string;
  phone?: string;
  farmerType: FarmerType;
  status: FarmerStatus;
  taxId?: string;
  vatNumber?: string;
  locations: FarmerLocation[];
  certifications: FarmerCertification[];
  crops: FarmerCrop[];
  profile?: FarmerProfile;
  
  // Portal access
  portalAccessEnabled: boolean;
  portalLastLogin?: Date;
  portalPasswordHash?: string;
  
  // Statistics
  totalContracts: number;
  totalDeliveries: number;
  totalRevenue?: number;
  averageQualityScore?: number;
  
  // Metadata
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  updatedBy: string;
}

export class FarmerEntity {
  static create(input: CreateFarmerInput, userId: string): Farmer {
    const now = new Date();
    const farmerNumber = `FARM-${Date.now().toString().slice(-8)}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
    
    const farmer: Farmer = {
      id: randomUUID(),
      farmerNumber,
      firstName: input.firstName,
      lastName: input.lastName,
      fullName: `${input.firstName} ${input.lastName}`,
      email: input.email,
      phone: input.phone,
      farmerType: input.farmerType,
      status: input.status || 'PENDING',
      taxId: input.taxId,
      vatNumber: input.vatNumber,
      locations: (input.locations || []).map((loc, index) => ({
        id: randomUUID(),
        ...loc,
        isPrimary: index === 0,
      })),
      certifications: (input.certifications || []).map(cert => ({
        id: randomUUID(),
        ...cert,
        isActive: cert.expiryDate ? cert.expiryDate > now : true,
      })),
      crops: (input.crops || []).map(crop => ({
        id: randomUUID(),
        ...crop,
        status: 'PLANNED' as const,
      })),
      profile: input.profile ? {
        id: randomUUID(),
        farmerId: '', // Will be set after creation
        ...input.profile,
        preferredContactMethod: input.profile.preferredContactMethod || 'EMAIL',
        notificationPreferences: {
          email: input.profile.notificationPreferences?.email ?? true,
          sms: input.profile.notificationPreferences?.sms ?? false,
          push: input.profile.notificationPreferences?.push ?? true,
          portal: input.profile.notificationPreferences?.portal ?? true,
        },
        createdAt: now,
        updatedAt: now,
      } : undefined,
      portalAccessEnabled: false,
      totalContracts: 0,
      totalDeliveries: 0,
      createdAt: now,
      updatedAt: now,
      createdBy: userId,
      updatedBy: userId,
    };

    // Set farmerId in profile
    if (farmer.profile) {
      farmer.profile.farmerId = farmer.id;
    }

    return farmer;
  }

  static update(farmer: Farmer, input: UpdateFarmerInput, userId: string): Farmer {
    const updated: Farmer = {
      ...farmer,
      ...(input.firstName && { firstName: input.firstName }),
      ...(input.lastName && { lastName: input.lastName }),
      ...(input.email && { email: input.email }),
      ...(input.phone !== undefined && { phone: input.phone }),
      ...(input.farmerType && { farmerType: input.farmerType }),
      ...(input.status && { status: input.status }),
      ...(input.taxId !== undefined && { taxId: input.taxId }),
      ...(input.vatNumber !== undefined && { vatNumber: input.vatNumber }),
      updatedAt: new Date(),
      updatedBy: userId,
    };

    // Update full name if first or last name changed
    if (input.firstName || input.lastName) {
      updated.fullName = `${updated.firstName} ${updated.lastName}`;
    }

    // Update profile if provided
    if (input.profile) {
      updated.profile = {
        ...farmer.profile,
        ...input.profile,
        farmerId: farmer.id,
        updatedAt: new Date(),
      } as FarmerProfile;
    }

    return updated;
  }

  static addLocation(farmer: Farmer, location: Omit<FarmerLocation, 'id' | 'isPrimary'>): Farmer {
    const newLocation: FarmerLocation = {
      id: randomUUID(),
      ...location,
      isPrimary: farmer.locations.length === 0,
    };

    return {
      ...farmer,
      locations: [...farmer.locations, newLocation],
      updatedAt: new Date(),
    };
  }

  static addCertification(farmer: Farmer, certification: Omit<FarmerCertification, 'id' | 'isActive'>): Farmer {
    const now = new Date();
    const newCertification: FarmerCertification = {
      id: randomUUID(),
      ...certification,
      isActive: certification.expiryDate ? certification.expiryDate > now : true,
    };

    return {
      ...farmer,
      certifications: [...farmer.certifications, newCertification],
      updatedAt: new Date(),
    };
  }

  static addCrop(farmer: Farmer, crop: Omit<FarmerCrop, 'id' | 'status'>): Farmer {
    const newCrop: FarmerCrop = {
      id: randomUUID(),
      ...crop,
      status: 'PLANNED',
    };

    return {
      ...farmer,
      crops: [...farmer.crops, newCrop],
      updatedAt: new Date(),
    };
  }

  static enablePortalAccess(farmer: Farmer): Farmer {
    return {
      ...farmer,
      portalAccessEnabled: true,
      updatedAt: new Date(),
    };
  }

  static disablePortalAccess(farmer: Farmer): Farmer {
    return {
      ...farmer,
      portalAccessEnabled: false,
      updatedAt: new Date(),
    };
  }

  static recordPortalLogin(farmer: Farmer): Farmer {
    return {
      ...farmer,
      portalLastLogin: new Date(),
      updatedAt: new Date(),
    };
  }
}

