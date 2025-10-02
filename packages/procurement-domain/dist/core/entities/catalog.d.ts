export type CatalogId = string & {
    readonly __brand: 'CatalogId';
};
export type CatalogItemId = string & {
    readonly __brand: 'CatalogItemId';
};
export type PunchOutSessionId = string & {
    readonly __brand: 'PunchOutSessionId';
};
export declare enum CatalogStatus {
    DRAFT = "draft",
    ACTIVE = "active",
    INACTIVE = "inactive",
    EXPIRED = "expired",
    ARCHIVED = "archived"
}
export declare enum CatalogType {
    INTERNAL = "internal",// Company internal catalog
    SUPPLIER = "supplier",// Direct supplier catalog
    PUNCHOUT = "punchout",// PunchOut supplier catalog
    MARKETPLACE = "marketplace",// External marketplace
    CONTRACT = "contract"
}
export declare enum PunchOutProtocol {
    CXML = "cxml",// cXML protocol (Ariba)
    OCI = "oci",// Open Catalog Interface (SAP)
    XML = "xml",// Generic XML
    JSON = "json"
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
    price: number;
    currency: string;
    uom: string;
    minimumOrderQuantity?: number;
    priceBreaks?: Array<{
        quantity: number;
        price: number;
    }>;
    availability: 'in_stock' | 'limited' | 'out_of_stock' | 'discontinued';
    leadTime?: number;
    stockQuantity?: number;
    specifications: Record<string, any>;
    attributes: Record<string, any>;
    images: string[];
    documents: string[];
    restricted: boolean;
    restrictionReason?: string;
    complianceFlags: string[];
    lastUpdated: Date;
    validFrom: Date;
    validTo?: Date;
    source: string;
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
    sessionId: string;
    status: 'active' | 'completed' | 'expired' | 'failed';
    startedAt: Date;
    expiresAt: Date;
    lastActivity: Date;
    returnUrl: string;
    browserFormPost?: string;
    selectedItems: Array<{
        itemId: string;
        quantity: number;
        unitPrice: number;
        lineTotal: number;
    }>;
    metadata: Record<string, any>;
}
export declare class Catalog {
    readonly id: CatalogId;
    name: string;
    description: string;
    type: CatalogType;
    status: CatalogStatus;
    supplierId: string;
    tenantId: string;
    currency: string;
    language: string;
    defaultUom: string;
    categories: Array<{
        id: string;
        name: string;
        parentId?: string;
        description?: string;
    }>;
    punchOutSetup?: PunchOutSetup;
    accessGroups: string[];
    approvalRequired: boolean;
    approvalWorkflow?: string;
    syncEnabled: boolean;
    syncFrequency: 'manual' | 'hourly' | 'daily' | 'weekly';
    lastSync?: Date;
    nextSync?: Date;
    syncStatus: 'idle' | 'running' | 'success' | 'failed';
    syncError: string | undefined;
    itemCount: number;
    activeItemCount: number;
    lastActivity?: Date;
    readonly createdAt: Date;
    updatedAt: Date;
    createdBy: string;
    tags: string[];
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
    });
    activate(): void;
    deactivate(): void;
    archive(): void;
    updateSyncStatus(status: 'idle' | 'running' | 'success' | 'failed', error?: string): void;
    addCategory(category: {
        id: string;
        name: string;
        parentId?: string;
        description?: string;
    }): void;
    updateItemCounts(total: number, active: number): void;
    configurePunchOut(setup: PunchOutSetup): void;
    hasAccess(userGroups: string[]): boolean;
    needsApproval(): boolean;
    isExpired(): boolean;
    shouldSync(): boolean;
    private scheduleNextSync;
    updateTimestamp(): void;
}
export declare class PunchOutService {
    static generatePunchOutUrl(setup: PunchOutSetup, session: PunchOutSession): string;
    static createPunchOutSession(supplierId: string, buyerUserId: string, returnUrl: string, protocol?: PunchOutProtocol): PunchOutSession;
    static validateSession(session: PunchOutSession): boolean;
    static extendSession(session: PunchOutSession, minutes?: number): void;
}
//# sourceMappingURL=catalog.d.ts.map