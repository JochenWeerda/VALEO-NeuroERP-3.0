import { injectable } from 'inversify';
import { PunchOutProtocol, PunchOutService, PunchOutSession, PunchOutSetup } from '../../core/entities/catalog';

export interface PunchOutRequest {
  supplierId: string;
  buyerUserId: string;
  returnUrl: string;
  operation: 'browse' | 'search' | 'inspect';
  searchCriteria?: {
    query?: string;
    category?: string;
    manufacturer?: string;
    priceRange?: { min: number; max: number };
  };
  buyerCookie?: string;
}

export interface PunchOutResponse {
  session: PunchOutSession;
  punchOutUrl: string;
  browserFormPost: string | undefined;
  expiresAt: Date;
}

export interface PunchOutReturn {
  sessionId: string;
  selectedItems: Array<{
    supplierPartId: string;
    quantity: number;
    unitPrice: number;
    currency: string;
    description: string;
    uom: string;
    manufacturerPartId?: string;
    manufacturerName?: string;
    classification?: {
      domain: string;
      value: string;
    };
    extrinsics?: Record<string, any>;
  }>;
  totalAmount: number;
  currency: string;
}

@injectable()
export class PunchOutIntegrationService {
  /**
   * Initiate a PunchOut session with a supplier
   */
  async initiatePunchOut(request: PunchOutRequest): Promise<PunchOutResponse> {
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
    const session = PunchOutService.createPunchOutSession(
      request.supplierId,
      request.buyerUserId,
      request.returnUrl,
      setup.protocol
    );

    // Generate PunchOut URL
    const punchOutUrl = PunchOutService.generatePunchOutUrl(setup, session);

    // Store session (in production, use database/cache)
    await this.storeSession(session);

    // Generate browser form post for cXML if needed
    let browserFormPost: string | undefined;
    if (setup.protocol === PunchOutProtocol.CXML) {
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
  async processPunchOutReturn(returnData: PunchOutReturn): Promise<{
    session: PunchOutSession;
    items: any[];
    totalAmount: number;
  }> {
    // Validate session
    const session = await this.getSession(returnData.sessionId);
    if (!session || !PunchOutService.validateSession(session)) {
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
  private async getPunchOutSetup(supplierId: string): Promise<PunchOutSetup | null> {
    // In production, retrieve from database
    // For now, return mock configuration
    if (supplierId === 'supplier-a') {
      return {
        supplierId,
        protocol: PunchOutProtocol.CXML,
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
  private async generateCXMLBrowserForm(
    setup: PunchOutSetup,
    session: PunchOutSession,
    request: PunchOutRequest
  ): Promise<string> {
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
  private generateSearchCriteriaXML(criteria: NonNullable<PunchOutRequest['searchCriteria']>): string {
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
  private async processSelectedItems(
    selectedItems: PunchOutReturn['selectedItems'],
    session: PunchOutSession
  ): Promise<any[]> {
    const processedItems: any[] = [];

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
  private async enrichItemData(item: any, supplierId: string): Promise<any> {
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
  private sessions = new Map<string, PunchOutSession>();

  private async storeSession(session: PunchOutSession): Promise<void> {
    this.sessions.set(session.id, session);
  }

  private async getSession(sessionId: string): Promise<PunchOutSession | undefined> {
    return this.sessions.get(sessionId);
  }

  private async updateSession(session: PunchOutSession): Promise<void> {
    this.sessions.set(session.id, session);
  }

  /**
   * Clean up expired sessions
   */
  async cleanupExpiredSessions(): Promise<number> {
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
  async getActiveSessions(userId: string): Promise<PunchOutSession[]> {
    const activeSessions: PunchOutSession[] = [];

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
  async validatePunchOutSetup(setup: PunchOutSetup): Promise<{
    isValid: boolean;
    errors: string[];
    warnings: string[];
  }> {
    const errors: string[] = [];
    const warnings: string[] = [];

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
      case PunchOutProtocol.CXML:
        if (!setup.sharedSecret) {
          errors.push('Shared secret is required for cXML protocol');
        }
        break;

      case PunchOutProtocol.OCI:
        if (!setup.authentication.credentials?.username) {
          errors.push('Username is required for OCI protocol');
        }
        break;
    }

    // URL format validation
    try {
      new URL(setup.setupUrl);
    } catch {
      errors.push('Setup URL must be a valid URL');
    }

    try {
      new URL(setup.postUrl);
    } catch {
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
  async testPunchOutConnection(supplierId: string): Promise<{
    success: boolean;
    responseTime: number;
    error?: string;
  }> {
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
    } catch (error) {
      return {
        success: false,
        responseTime: Date.now() - startTime,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
}

export default PunchOutIntegrationService;