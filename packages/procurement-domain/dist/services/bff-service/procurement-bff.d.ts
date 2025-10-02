/**
 * VALEO NeuroERP 3.0 - Procurement BFF Service
 *
 * Backend for Frontend (BFF) service providing:
 * - Aggregated dashboard data from all procurement services
 * - Conversational AI for procurement tasks
 * - Unified API for frontend applications
 * - Real-time notifications and workflow orchestration
 */
import express from 'express';
export interface ProcurementDashboardData {
    overview: {
        totalSpend: number;
        activePOs: number;
        pendingRequisitions: number;
        supplierCount: number;
        contractCount: number;
        riskAlerts: number;
    };
    spendAnalytics: {
        byCategory: Array<{
            category: string;
            amount: number;
            percentage: number;
        }>;
        bySupplier: Array<{
            supplier: string;
            amount: number;
            percentage: number;
        }>;
    };
    alerts: Array<{
        id: string;
        type: 'warning' | 'error' | 'info';
        title: string;
        message: string;
        priority: 'low' | 'medium' | 'high' | 'critical';
    }>;
    recommendations: Array<{
        id: string;
        type: string;
        title: string;
        description: string;
        impact: string;
        confidence: number;
    }>;
}
export interface ConversationalRequest {
    message: string;
    context?: {
        userId: string;
        department: string;
        role: string;
    };
    sessionId?: string;
}
export interface ConversationalResponse {
    response: string;
    actions: Array<{
        type: string;
        label: string;
        data: any;
        confidence: number;
    }>;
    suggestions: string[];
    sessionId: string;
}
export declare class ProcurementBFFService {
    private app;
    private readonly port;
    constructor();
    private setupMiddleware;
    private setupRoutes;
    private handleDashboard;
    private handleChat;
    private handleSearch;
    private handleRequisitionToPO;
    private handleNotifications;
    private handleBulkApprove;
    private handleSpendAnalytics;
    start(): Promise<void>;
    stop(): Promise<void>;
    getApp(): express.Application;
}
//# sourceMappingURL=procurement-bff.d.ts.map