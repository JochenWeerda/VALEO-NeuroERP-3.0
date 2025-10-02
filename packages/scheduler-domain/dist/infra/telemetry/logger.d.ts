import pino from 'pino';
export interface LogContext {
    requestId?: string;
    tenantId?: string;
    userId?: string;
    correlationId?: string;
    operation?: string;
    [key: string]: any;
}
export declare class Logger {
    private logger;
    constructor(options?: pino.LoggerOptions);
    private createChildLogger;
    info(message: string, context?: LogContext): void;
    warn(message: string, context?: LogContext): void;
    error(message: string, error?: Error, context?: LogContext): void;
    debug(message: string, context?: LogContext): void;
    logRequest(request: any, context?: LogContext): void;
    logResponse(response: any, duration: number, context?: LogContext): void;
    logScheduleExecution(scheduleId: string, success: boolean, duration: number, context?: LogContext): void;
    logSecurityEvent(event: string, details: any, context?: LogContext): void;
    logPerformance(operation: string, duration: number, context?: LogContext): void;
}
export declare function getLogger(): Logger;
export declare const logger: Logger;
//# sourceMappingURL=logger.d.ts.map