/**
 * Logging Middleware
 */
export interface LogEntry {
    timestamp: string;
    method: string;
    url: string;
    statusCode?: number;
    duration?: number;
    userAgent?: string;
    ip?: string;
    userId?: string;
    requestId?: string;
    error?: string;
}
export declare class LoggerMiddleware {
    private logLevel;
    constructor(logLevel?: 'debug' | 'info' | 'warn' | 'error');
    private shouldLog;
    private formatLog;
    private log;
    requestLogger: (req: any, res: any, next: any) => void;
    errorLogger: (error: any, req: any, res: any, next: any) => void;
    private generateRequestId;
    debug(message: string, data?: any): void;
    info(message: string, data?: any): void;
    warn(message: string, data?: any): void;
    error(message: string, data?: any): void;
}
//# sourceMappingURL=logger.d.ts.map