import { randomUUID } from 'crypto';

export type CatalogId = string & { readonly __brand: 'CatalogId' };
export type CatalogItemId = string & { readonly __brand: 'CatalogItemId' };
export type PunchOutSessionId = string & { readonly __brand: 'PunchOutSessionId' };

export enum CatalogStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  EXPIRED = 'expired',
  ARCHIVED = 'archived'
}

export enum CatalogType {
  INTERNAL = 'internal',           // Company internal catalog
  SUPPLIER = 'supplier',           // Direct supplier catalog
  PUNCHOUT = 'punchout',           // PunchOut supplier catalog
  MARKETPLACE = 'marketplace',     // External marketplace
  CONTRACT = 'contract'            // Contract-based catalog
}

export enum PunchOutProtocol {
  CXML = 'cxml',                   // cXML protocol (Ariba)
  OCI = 'oci',                     // Open Catalog Interface (SAP)
  XML = 'xml',                     // Generic XML
  JSON = 'json'                    // JSON-based protocol
}

export interface CatalogItem {
  id: CatalogItemId;
  catalogId: CatalogId;
  supplierId: string;
  sku: string;
  name: string;
  description: string;
  category: string;
  subcategory?: string;
  manufacturer?: string;
  manufacturerPartNumber?: string;

  // Pricing
  price: number;
  currency: string;
  uom: string;
  minimumOrderQuantity?: number;
  priceBreaks?: Array<{
    quantity: number;
    price: number;
  }>;

  // Availability
  availability: 'in_stock' | 'limited' | 'out_of_stock' | 'discontinued';
  leadTime?: number; // days
  stockQuantity?: number;

  // Specifications
  specifications: Record<string, any>;
  attributes: Record<string, any>;

  // Images and documents
  images: string[];
  documents: string[];

  // Compliance and restrictions
  restricted: boolean;
  restrictionReason?: string;
  complianceFlags: string[]; // 'REACH', 'RoHS', 'GOTS', etc.

  // Metadata
  lastUpdated: Date;
  validFrom: Date;
  validTo?: Date;
  source: string; // URL or API endpoint
}

export interface PunchOutSetup {
  supplierId: string;
  protocol: PunchOutProtocol;
  setupUrl: string;
  postUrl: string;
  fromDomain: string;
  fromIdentity: string;
  sharedSecret?: string;
  authentication: {
    type: 'basic' | 'oauth' | 'certificate';
    credentials?: Record<string, any>;
  };
  capabilities: {
    browse: boolean;
    search: boolean;
    inspect: boolean;
    transfer: boolean;
  };
  customFields: Record<string, any>;
}

export interface PunchOutSession {
  id: PunchOutSessionId;
  supplierId: string;
  buyerUserId: string;
  protocol: PunchOutProtocol;
  sessionId: string; // Supplier's session ID
  status: 'active' | 'completed' | 'expired' | 'failed';
  startedAt: Date;
  expiresAt: Date;
  lastActivity: Date;
  returnUrl: string;
  browserFormPost?: string; // cXML browser form post
  selectedItems: Array<{
    itemId: string;
    quantity: number;
    unitPrice: number;
    lineTotal: number;
  }>;
  metadata: Record<string, any>;
}

export class Catalog {
  public readonly id: CatalogId;
  public name: string;
  public description: string;
  public type: CatalogType;
  public status: CatalogStatus;
  public supplierId: string;
  public tenantId: string;

  // Configuration
  public currency: string;
  public language: string;
  public defaultUom: string;

  // Categories and structure
  public categories: Array<{
    id: string;
    name: string;
    parentId?: string;
    description?: string;
  }>;

  // PunchOut configuration (if applicable)
  public punchOutSetup?: PunchOutSetup;

  // Access control
  public accessGroups: string[]; // User groups that can access this catalog
  public approvalRequired: boolean;
  public approvalWorkflow?: string;

  // Synchronization
  public syncEnabled: boolean;
  public syncFrequency: 'manual' | 'hourly' | 'daily' | 'weekly';
  public lastSync?: Date;
  public nextSync?: Date;
  public syncStatus: 'idle' | 'running' | 'success' | 'failed';
  public syncError: string | undefined;

  // Statistics
  public itemCount: number;
  public activeItemCount: number;
  public lastActivity?: Date;

  // Metadata
  public readonly createdAt: Date;
  public updatedAt: Date;
  public createdBy: string;
  public tags: string[];

  constructor(props: {
    id?: CatalogId;
    name: string;
    description: string;
    type: CatalogType;
    supplierId: string;
    tenantId: string;
    currency?: string;
    language?: string;
    accessGroups?: string[];
    approvalRequired?: boolean;
    syncEnabled?: boolean;
    syncFrequency?: 'manual' | 'hourly' | 'daily' | 'weekly';
    createdBy: string;
    tags?: string[];
  }) {
    this.id = props.id || (randomUUID() as CatalogId);
    this.name = props.name;
    this.description = props.description;
    this.type = props.type;
    this.status = CatalogStatus.DRAFT;
    this.supplierId = props.supplierId;
    this.tenantId = props.tenantId;
    this.currency = props.currency || 'EUR';
    this.language = props.language || 'en';
    this.defaultUom = 'EA';
    this.categories = [];
    this.accessGroups = props.accessGroups || [];
    this.approvalRequired = props.approvalRequired || false;
    this.syncEnabled = props.syncEnabled || false;
    this.syncFrequency = props.syncFrequency || 'daily';
    this.syncStatus = 'idle';
    this.itemCount = 0;
    this.activeItemCount = 0;
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.createdBy = props.createdBy;
    this.tags = props.tags || [];
  }

  // Business Logic Methods
  public activate(): void {
    if (this.status !== CatalogStatus.DRAFT && this.status !== CatalogStatus.INACTIVE) {
      throw new Error('Only draft or inactive catalogs can be activated');
    }
    if (this.itemCount === 0) {
      throw new Error('Catalog must have at least one item to be activated');
    }

    this.status = CatalogStatus.ACTIVE;
    this.updatedAt = new Date();
  }

  public deactivate(): void {
    if (this.status !== CatalogStatus.ACTIVE) {
      throw new Error('Only active catalogs can be deactivated');
    }

    this.status = CatalogStatus.INACTIVE;
    this.updatedAt = new Date();
  }

  public archive(): void {
    if (this.status === CatalogStatus.ACTIVE) {
      throw new Error('Active catalogs cannot be archived directly');
    }

    this.status = CatalogStatus.ARCHIVED;
    this.updatedAt = new Date();
  }

  public updateSyncStatus(status: 'idle' | 'running' | 'success' | 'failed', error?: string): void {
    this.syncStatus = status;
    this.lastSync = new Date();
    this.syncError = error;

    if (status === 'success' && this.syncFrequency !== 'manual') {
      this.scheduleNextSync();
    }

    this.updatedAt = new Date();
  }

  public addCategory(category: { id: string; name: string; parentId?: string; description?: string }): void {
    const existing = this.categories.find(c => c.id === category.id);
    if (existing) {
      throw new Error('Category with this ID already exists');
    }

    this.categories.push(category);
    this.updatedAt = new Date();
  }

  public updateItemCounts(total: number, active: number): void {
    this.itemCount = total;
    this.activeItemCount = active;
    this.lastActivity = new Date();
    this.updatedAt = new Date();
  }

  public configurePunchOut(setup: PunchOutSetup): void {
    if (this.type !== CatalogType.PUNCHOUT) {
      throw new Error('PunchOut configuration only allowed for PunchOut catalogs');
    }

    this.punchOutSetup = setup;
    this.updatedAt = new Date();
  }

  public hasAccess(userGroups: string[]): boolean {
    if (this.accessGroups.length === 0) {
      return true; // Public access
    }

    return this.accessGroups.some(group => userGroups.includes(group));
  }

  public needsApproval(): boolean {
    return this.approvalRequired;
  }

  public isExpired(): boolean {
    return this.status === CatalogStatus.EXPIRED;
  }

  public shouldSync(): boolean {
    if (!this.syncEnabled || this.syncFrequency === 'manual') {
      return false;
    }

    if (!this.nextSync) {
      return true;
    }

    return new Date() >= this.nextSync;
  }

  // Private methods
  private scheduleNextSync(): void {
    const now = new Date();

    switch (this.syncFrequency) {
      case 'hourly':
        this.nextSync = new Date(now.getTime() + 60 * 60 * 1000);
        break;
      case 'daily':
        this.nextSync = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        break;
      case 'weekly':
        this.nextSync = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
        break;
    }
  }

  public updateTimestamp(): void {
    this.updatedAt = new Date();
  }
}

export class PunchOutService {
  public static generatePunchOutUrl(setup: PunchOutSetup, session: PunchOutSession): string {
    const baseUrl = setup.setupUrl;
    const params = new URLSearchParams();

    params.append('posid', setup.fromIdentity);
    params.append('return', session.returnUrl);
    params.append('sid', session.sessionId);

    // Add protocol-specific parameters
    switch (setup.protocol) {
      case PunchOutProtocol.CXML:
        params.append('cxml-urlencoded', 'true');
        break;
      case PunchOutProtocol.OCI:
        params.append('HOOK_URL', session.returnUrl);
        params.append('USERNAME', setup.fromIdentity);
        break;
    }

    return `${baseUrl}?${params.toString()}`;
  }

  public static createPunchOutSession(
    supplierId: string,
    buyerUserId: string,
    returnUrl: string,
    protocol: PunchOutProtocol = PunchOutProtocol.CXML
  ): PunchOutSession {
    const sessionId = randomUUID();
    const now = new Date();
    const expiresAt = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour

    return {
      id: sessionId as PunchOutSessionId,
      supplierId,
      buyerUserId,
      protocol,
      sessionId,
      status: 'active',
      startedAt: now,
      expiresAt,
      lastActivity: now,
      returnUrl,
      selectedItems: [],
      metadata: {}
    };
  }

  public static validateSession(session: PunchOutSession): boolean {
    return session.status === 'active' && new Date() < session.expiresAt;
  }

  public static extendSession(session: PunchOutSession, minutes = 30): void {
    session.expiresAt = new Date(session.expiresAt.getTime() + minutes * 60 * 1000);
    session.lastActivity = new Date();
  }
}