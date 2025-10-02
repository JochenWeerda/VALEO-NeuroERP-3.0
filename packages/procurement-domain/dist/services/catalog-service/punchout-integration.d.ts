import { PunchOutSetup, PunchOutSession } from '../../core/entities/catalog';
export interface PunchOutRequest {
    supplierId: string;
    buyerUserId: string;
    returnUrl: string;
    operation: 'browse' | 'search' | 'inspect';
    searchCriteria?: {
        query?: string;
        category?: string;
        manufacturer?: string;
        priceRange?: {
            min: number;
            max: number;
        };
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
export declare class PunchOutIntegrationService {
    /**
     * Initiate a PunchOut session with a supplier
     */
    initiatePunchOut(request: PunchOutRequest): Promise<PunchOutResponse>;
    /**
     * Process PunchOut return from supplier
     */
    processPunchOutReturn(returnData: PunchOutReturn): Promise<{
        session: PunchOutSession;
        items: any[];
        totalAmount: number;
    }>;
    /**
     * Get PunchOut setup for a supplier
     */
    private getPunchOutSetup;
    /**
     * Generate cXML browser form post
     */
    private generateCXMLBrowserForm;
    /**
     * Generate search criteria XML for cXML
     */
    private generateSearchCriteriaXML;
    /**
     * Process selected items from PunchOut return
     */
    private processSelectedItems;
    /**
     * Enrich item data with catalog information
     */
    private enrichItemData;
    /**
     * Session management (in production, use database/cache)
     */
    private sessions;
    private storeSession;
    private getSession;
    private updateSession;
    /**
     * Clean up expired sessions
     */
    cleanupExpiredSessions(): Promise<number>;
    /**
     * Get active sessions for a user
     */
    getActiveSessions(userId: string): Promise<PunchOutSession[]>;
    /**
     * Validate PunchOut setup configuration
     */
    validatePunchOutSetup(setup: PunchOutSetup): Promise<{
        isValid: boolean;
        errors: string[];
        warnings: string[];
    }>;
    /**
     * Test PunchOut connection
     */
    testPunchOutConnection(supplierId: string): Promise<{
        success: boolean;
        responseTime: number;
        error?: string;
    }>;
}
export default PunchOutIntegrationService;
//# sourceMappingURL=punchout-integration.d.ts.map