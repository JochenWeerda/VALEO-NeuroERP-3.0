"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PunchOutService = exports.Catalog = exports.PunchOutProtocol = exports.CatalogType = exports.CatalogStatus = void 0;
const crypto_1 = require("crypto");
var CatalogStatus;
(function (CatalogStatus) {
    CatalogStatus["DRAFT"] = "draft";
    CatalogStatus["ACTIVE"] = "active";
    CatalogStatus["INACTIVE"] = "inactive";
    CatalogStatus["EXPIRED"] = "expired";
    CatalogStatus["ARCHIVED"] = "archived";
})(CatalogStatus || (exports.CatalogStatus = CatalogStatus = {}));
var CatalogType;
(function (CatalogType) {
    CatalogType["INTERNAL"] = "internal";
    CatalogType["SUPPLIER"] = "supplier";
    CatalogType["PUNCHOUT"] = "punchout";
    CatalogType["MARKETPLACE"] = "marketplace";
    CatalogType["CONTRACT"] = "contract"; // Contract-based catalog
})(CatalogType || (exports.CatalogType = CatalogType = {}));
var PunchOutProtocol;
(function (PunchOutProtocol) {
    PunchOutProtocol["CXML"] = "cxml";
    PunchOutProtocol["OCI"] = "oci";
    PunchOutProtocol["XML"] = "xml";
    PunchOutProtocol["JSON"] = "json"; // JSON-based protocol
})(PunchOutProtocol || (exports.PunchOutProtocol = PunchOutProtocol = {}));
class Catalog {
    id;
    name;
    description;
    type;
    status;
    supplierId;
    tenantId;
    // Configuration
    currency;
    language;
    defaultUom;
    // Categories and structure
    categories;
    // PunchOut configuration (if applicable)
    punchOutSetup;
    // Access control
    accessGroups; // User groups that can access this catalog
    approvalRequired;
    approvalWorkflow;
    // Synchronization
    syncEnabled;
    syncFrequency;
    lastSync;
    nextSync;
    syncStatus;
    syncError;
    // Statistics
    itemCount;
    activeItemCount;
    lastActivity;
    // Metadata
    createdAt;
    updatedAt;
    createdBy;
    tags;
    constructor(props) {
        this.id = props.id || (0, crypto_1.randomUUID)();
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
    activate() {
        if (this.status !== CatalogStatus.DRAFT && this.status !== CatalogStatus.INACTIVE) {
            throw new Error('Only draft or inactive catalogs can be activated');
        }
        if (this.itemCount === 0) {
            throw new Error('Catalog must have at least one item to be activated');
        }
        this.status = CatalogStatus.ACTIVE;
        this.updatedAt = new Date();
    }
    deactivate() {
        if (this.status !== CatalogStatus.ACTIVE) {
            throw new Error('Only active catalogs can be deactivated');
        }
        this.status = CatalogStatus.INACTIVE;
        this.updatedAt = new Date();
    }
    archive() {
        if (this.status === CatalogStatus.ACTIVE) {
            throw new Error('Active catalogs cannot be archived directly');
        }
        this.status = CatalogStatus.ARCHIVED;
        this.updatedAt = new Date();
    }
    updateSyncStatus(status, error) {
        this.syncStatus = status;
        this.lastSync = new Date();
        this.syncError = error;
        if (status === 'success' && this.syncFrequency !== 'manual') {
            this.scheduleNextSync();
        }
        this.updatedAt = new Date();
    }
    addCategory(category) {
        const existing = this.categories.find(c => c.id === category.id);
        if (existing) {
            throw new Error('Category with this ID already exists');
        }
        this.categories.push(category);
        this.updatedAt = new Date();
    }
    updateItemCounts(total, active) {
        this.itemCount = total;
        this.activeItemCount = active;
        this.lastActivity = new Date();
        this.updatedAt = new Date();
    }
    configurePunchOut(setup) {
        if (this.type !== CatalogType.PUNCHOUT) {
            throw new Error('PunchOut configuration only allowed for PunchOut catalogs');
        }
        this.punchOutSetup = setup;
        this.updatedAt = new Date();
    }
    hasAccess(userGroups) {
        if (this.accessGroups.length === 0) {
            return true; // Public access
        }
        return this.accessGroups.some(group => userGroups.includes(group));
    }
    needsApproval() {
        return this.approvalRequired;
    }
    isExpired() {
        return this.status === CatalogStatus.EXPIRED;
    }
    shouldSync() {
        if (!this.syncEnabled || this.syncFrequency === 'manual') {
            return false;
        }
        if (!this.nextSync) {
            return true;
        }
        return new Date() >= this.nextSync;
    }
    // Private methods
    scheduleNextSync() {
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
    updateTimestamp() {
        this.updatedAt = new Date();
    }
}
exports.Catalog = Catalog;
class PunchOutService {
    static generatePunchOutUrl(setup, session) {
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
    static createPunchOutSession(supplierId, buyerUserId, returnUrl, protocol = PunchOutProtocol.CXML) {
        const sessionId = (0, crypto_1.randomUUID)();
        const now = new Date();
        const expiresAt = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour
        return {
            id: sessionId,
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
    static validateSession(session) {
        return session.status === 'active' && new Date() < session.expiresAt;
    }
    static extendSession(session, minutes = 30) {
        session.expiresAt = new Date(session.expiresAt.getTime() + minutes * 60 * 1000);
        session.lastActivity = new Date();
    }
}
exports.PunchOutService = PunchOutService;
//# sourceMappingURL=catalog.js.map