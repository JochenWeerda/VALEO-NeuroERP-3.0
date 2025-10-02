/**
 * Error Handling Middleware
 */
export interface ErrorHandlerOptions {
    includeStack?: boolean;
    logErrors?: boolean;
}
export declare class ErrorHandlerMiddleware {
    private options;
    constructor(options?: ErrorHandlerOptions);
    handle(error: unknown): {
        statusCode: number;
        body: Record<string, unknown>;
    };
    private handleZodError;
    middleware: (error: unknown, req: any, res: any, next: any) => void;
}
//# sourceMappingURL=error-handler.d.ts.map