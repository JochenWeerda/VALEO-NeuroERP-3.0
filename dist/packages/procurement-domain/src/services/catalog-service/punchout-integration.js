"use strict";
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PunchOutIntegrationService = void 0;
const inversify_1 = require("inversify");
const catalog_1 = require("../../core/entities/catalog");
let PunchOutIntegrationService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var PunchOutIntegrationService = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            PunchOutIntegrationService = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        /**
         * Initiate a PunchOut session with a supplier
         */
        async initiatePunchOut(request) {
            // Get supplier PunchOut configuration
            const setup = await this.getPunchOutSetup(request.supplierId);
            if (!setup) {
                throw new Error(`PunchOut not configured for supplier ${request.supplierId}`);
            }
            // Validate capabilities
            if (!setup.capabilities[request.operation]) {
                throw new Error(`Operation ${request.operation} not supported by supplier`);
            }
            // Create session
            const session = catalog_1.PunchOutService.createPunchOutSession(request.supplierId, request.buyerUserId, request.returnUrl, setup.protocol);
            // Generate PunchOut URL
            const punchOutUrl = catalog_1.PunchOutService.generatePunchOutUrl(setup, session);
            // Store session (in production, use database/cache)
            await this.storeSession(session);
            // Generate browser form post for cXML if needed
            let browserFormPost;
            if (setup.protocol === catalog_1.PunchOutProtocol.CXML) {
                browserFormPost = await this.generateCXMLBrowserForm(setup, session, request);
            }
            return {
                session,
                punchOutUrl,
                browserFormPost,
                expiresAt: session.expiresAt
            };
        }
        /**
         * Process PunchOut return from supplier
         */
        async processPunchOutReturn(returnData) {
            // Validate session
            const session = await this.getSession(returnData.sessionId);
            if (!session || !catalog_1.PunchOutService.validateSession(session)) {
                throw new Error('Invalid or expired PunchOut session');
            }
            // Process selected items
            const processedItems = await this.processSelectedItems(returnData.selectedItems, session);
            // Update session
            session.selectedItems = processedItems.map(item => ({
                itemId: item.supplierPartId,
                quantity: item.quantity,
                unitPrice: item.unitPrice,
                lineTotal: item.quantity * item.unitPrice
            }));
            session.status = 'completed';
            session.lastActivity = new Date();
            await this.updateSession(session);
            return {
                session,
                items: processedItems,
                totalAmount: returnData.totalAmount
            };
        }
        /**
         * Get PunchOut setup for a supplier
         */
        async getPunchOutSetup(supplierId) {
            // In production, retrieve from database
            // For now, return mock configuration
            if (supplierId === 'supplier-a') {
                return {
                    supplierId,
                    protocol: catalog_1.PunchOutProtocol.CXML,
                    setupUrl: 'https://supplier-a.com/punchout/setup',
                    postUrl: 'https://supplier-a.com/punchout/post',
                    fromDomain: 'buyer.valero-neuroerp.com',
                    fromIdentity: 'VALEO-NEUROERP',
                    sharedSecret: 'shared-secret-key',
                    authentication: {
                        type: 'basic',
                        credentials: {
                            username: 'valero-user',
                            password: 'secure-password'
                        }
                    },
                    capabilities: {
                        browse: true,
                        search: true,
                        inspect: true,
                        transfer: true
                    },
                    customFields: {}
                };
            }
            return null;
        }
        /**
         * Generate cXML browser form post
         */
        async generateCXMLBrowserForm(setup, session, request) {
            const cxml = `<?xml version="1.0" encoding="UTF-8"?>
<cXML version="1.2.014" payloadID="${session.id}" timestamp="${new Date().toISOString()}">
  <Header>
    <From>
      <Credential domain="${setup.fromDomain}">
        <Identity>${setup.fromIdentity}</Identity>
      </Credential>
    </From>
    <To>
      <Credential domain="supplier.com">
        <Identity>${setup.supplierId}</Identity>
      </Credential>
    </To>
    <Sender>
      <Credential domain="${setup.fromDomain}">
        <Identity>${setup.fromIdentity}</Identity>
        <SharedSecret>${setup.sharedSecret}</SharedSecret>
      </Credential>
      <UserAgent>VALEO NeuroERP 3.0</UserAgent>
    </Sender>
  </Header>
  <Request>
    <PunchOutSetupRequest operation="${request.operation}">
      <BuyerCookie>${request.buyerCookie || session.id}</BuyerCookie>
      <Extrinsic name="UserEmail">${request.buyerUserId}@valero-neuroerp.com</Extrinsic>
      <Extrinsic name="UserId">${request.buyerUserId}</Extrinsic>
      ${request.searchCriteria ? this.generateSearchCriteriaXML(request.searchCriteria) : ''}
    </PunchOutSetupRequest>
  </Request>
</cXML>`;
            return cxml;
        }
        /**
         * Generate search criteria XML for cXML
         */
        generateSearchCriteriaXML(criteria) {
            let xml = '';
            if (criteria.query) {
                xml += `<Extrinsic name="SearchQuery">${criteria.query}</Extrinsic>`;
            }
            if (criteria.category) {
                xml += `<Extrinsic name="Category">${criteria.category}</Extrinsic>`;
            }
            if (criteria.manufacturer) {
                xml += `<Extrinsic name="Manufacturer">${criteria.manufacturer}</Extrinsic>`;
            }
            if (criteria.priceRange) {
                xml += `<Extrinsic name="MinPrice">${criteria.priceRange.min}</Extrinsic>`;
                xml += `<Extrinsic name="MaxPrice">${criteria.priceRange.max}</Extrinsic>`;
            }
            return xml;
        }
        /**
         * Process selected items from PunchOut return
         */
        async processSelectedItems(selectedItems, session) {
            const processedItems = [];
            for (const item of selectedItems) {
                // Validate item data
                if (!item.supplierPartId || item.quantity <= 0 || item.unitPrice <= 0) {
                    throw new Error(`Invalid item data: ${JSON.stringify(item)}`);
                }
                // Enrich item with catalog data if available
                const enrichedItem = await this.enrichItemData(item, session.supplierId);
                processedItems.push({
                    ...item,
                    ...enrichedItem,
                    sessionId: session.id,
                    processedAt: new Date()
                });
            }
            return processedItems;
        }
        /**
         * Enrich item data with catalog information
         */
        async enrichItemData(item, supplierId) {
            // In production, lookup item in catalog database
            // For now, return basic enrichment
            return {
                catalogId: `catalog-${supplierId}`,
                category: 'Electronics', // Would be determined from catalog
                complianceFlags: ['RoHS', 'REACH'],
                availability: 'in_stock',
                leadTime: 7
            };
        }
        /**
         * Session management (in production, use database/cache)
         */
        sessions = new Map();
        async storeSession(session) {
            this.sessions.set(session.id, session);
        }
        async getSession(sessionId) {
            return this.sessions.get(sessionId);
        }
        async updateSession(session) {
            this.sessions.set(session.id, session);
        }
        /**
         * Clean up expired sessions
         */
        async cleanupExpiredSessions() {
            const now = new Date();
            let cleaned = 0;
            for (const [sessionId, session] of this.sessions.entries()) {
                if (session.expiresAt < now) {
                    this.sessions.delete(sessionId);
                    cleaned++;
                }
            }
            return cleaned;
        }
        /**
         * Get active sessions for a user
         */
        async getActiveSessions(userId) {
            const activeSessions = [];
            for (const session of this.sessions.values()) {
                if (session.buyerUserId === userId && session.status === 'active') {
                    activeSessions.push(session);
                }
            }
            return activeSessions;
        }
        /**
         * Validate PunchOut setup configuration
         */
        async validatePunchOutSetup(setup) {
            const errors = [];
            const warnings = [];
            // Required fields validation
            if (!setup.setupUrl) {
                errors.push('Setup URL is required');
            }
            if (!setup.postUrl) {
                errors.push('Post URL is required');
            }
            if (!setup.fromDomain) {
                errors.push('From domain is required');
            }
            if (!setup.fromIdentity) {
                errors.push('From identity is required');
            }
            // Protocol-specific validation
            switch (setup.protocol) {
                case catalog_1.PunchOutProtocol.CXML:
                    if (!setup.sharedSecret) {
                        errors.push('Shared secret is required for cXML protocol');
                    }
                    break;
                case catalog_1.PunchOutProtocol.OCI:
                    if (!setup.authentication.credentials?.username) {
                        errors.push('Username is required for OCI protocol');
                    }
                    break;
            }
            // URL format validation
            try {
                new URL(setup.setupUrl);
            }
            catch {
                errors.push('Setup URL must be a valid URL');
            }
            try {
                new URL(setup.postUrl);
            }
            catch {
                errors.push('Post URL must be a valid URL');
            }
            // Capability warnings
            if (!setup.capabilities.browse) {
                warnings.push('Browse capability not enabled - limited functionality');
            }
            return {
                isValid: errors.length === 0,
                errors,
                warnings
            };
        }
        /**
         * Test PunchOut connection
         */
        async testPunchOutConnection(supplierId) {
            const setup = await this.getPunchOutSetup(supplierId);
            if (!setup) {
                return {
                    success: false,
                    responseTime: 0,
                    error: 'PunchOut not configured'
                };
            }
            const startTime = Date.now();
            try {
                // Simple connectivity test (in production, make actual HTTP request)
                await new Promise(resolve => setTimeout(resolve, 100)); // Mock delay
                return {
                    success: true,
                    responseTime: Date.now() - startTime
                };
            }
            catch (error) {
                return {
                    success: false,
                    responseTime: Date.now() - startTime,
                    error: error instanceof Error ? error.message : 'Unknown error'
                };
            }
        }
    };
    return PunchOutIntegrationService = _classThis;
})();
exports.PunchOutIntegrationService = PunchOutIntegrationService;
exports.default = PunchOutIntegrationService;
