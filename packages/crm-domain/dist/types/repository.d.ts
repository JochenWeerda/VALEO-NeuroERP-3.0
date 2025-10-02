/**
 * Repository interfaces for CRM Domain
 * Repository und RepositoryBase werden aus @valero-neuroerp/utilities importiert
 */
export interface Logger {
    debug(message: string, context?: Record<string, unknown>): void;
    info(message: string, context?: Record<string, unknown>): void;
    warn(message: string, context?: Record<string, unknown>): void;
    error(message: string, context?: Record<string, unknown>): void;
}
//# sourceMappingURL=repository.d.ts.map