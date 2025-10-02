/**
 * Production Validation Framework
 * VALEO-NeuroERP-3.0 Validation Service Implementation
 * Week 1: Reverse Execution Phase
 */
export interface ValidationResult {
    testName: string;
    status: 'PASSED' | 'FAILED' | 'WARNING';
    message: string;
    timestamp: Date;
    details: Record<string, any>;
}
export interface ProductionReadinessResult {
    overallStatus: 'READY' | 'NOT_READY';
    validationResults: ValidationResult[];
    criticalFailures: number;
    warnings: number;
    timestamp: Date;
}
export interface SecurityValidation {
    authenticationFunctional: boolean;
    authorizationImplemented: boolean;
    vulnerabilitiesScanned: boolean;
    securityMiddlewareActive: boolean;
}
export interface PerformanceValidation {
    apiResponseTimeMs: number;
    databaseConnectionLatency: number;
    frontendRenderingTime: number;
    errorRate: number;
}
export declare class ProductionReadinessChecker {
    private readonly securityValidation;
    private readonly performanceValidation;
    private validationResults;
    constructor(securityValidation: SecurityValidation, performanceValidation: PerformanceValidation);
    executeCompleteSystemValidation(): Promise<ProductionReadinessResult>;
    private validateSecurityFramework;
    private validatePerformanceMetrics;
    private validateDatabaseConnections;
    private validateAPIEndpoints;
    private validateFrontendApplication;
    private validateEPRWorkflows;
    private validateAIAgentOperation;
    private validateMonitoring;
    private generateValidationReport;
}
export default ProductionReadinessChecker;
//# sourceMappingURL=production-readiness-checker.d.ts.map