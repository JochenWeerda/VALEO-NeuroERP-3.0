/**
 * VALEO-NeuroERP-3.0 Logging System
 * Structured logging with Winston and Pino
 */
export declare const logger: any;
export declare const createDomainLogger: (domain: string) => any;
export declare const auditLogger: any;
export declare const performanceLogger: any;
export declare const securityLogger: any;
export declare class Logger {
    private logger;
    constructor(context: string);
    error(message: string, meta?: any): void;
    warn(message: string, meta?: any): void;
    info(message: string, meta?: any): void;
    debug(message: string, meta?: any): void;
    time(label: string): () => void;
    logRequest(req: any, res: any, next: any): void;
}
export declare const crmLogger: any;
export declare const erpLogger: any;
export declare const analyticsLogger: any;
export declare const integrationLogger: any;
export declare const sharedLogger: any;
export default logger;
//***REMOVED*** sourceMappingURL=logging.d.ts.map