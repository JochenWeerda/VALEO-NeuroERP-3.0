/**
 * Security Validation Service - VALEO-NeuroERP-3.0
 * Week 1 - Reverse Execution Phase: Security audit and authorization validation
 */
export interface SecurityValidationResult {
    securityFrameworkStatus: 'SECURED' | 'COMPROMISED' | 'VULNERABLE';
    authenticationStatus: 'ACTIVE' | 'INACTIVE' | 'ERROR';
    authorizationStatus: 'IMPLEMENTED' | 'MISSING' | 'PARTIAL';
    vulnerabilityScan: 'CLEAN' | 'WARNINGS' | 'CRITICAL';
    auditTimestamp: Date;
}
export declare class SecurityValidationService {
    executeSecurityAudit(): Promise<SecurityValidationResult>;
    private validateSecurityFramework;
}
export default SecurityValidationService;
//# sourceMappingURL=security-validation-service.d.ts.map