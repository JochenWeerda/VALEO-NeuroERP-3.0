/**
 * Request Validation Middleware
 */
import { ZodSchema } from 'zod';
export interface ValidationOptions {
    body?: ZodSchema;
    query?: ZodSchema;
    params?: ZodSchema;
    headers?: ZodSchema;
}
export declare class RequestValidatorMiddleware {
    validate(options: ValidationOptions): (req: any, res: any, next: any) => Promise<any>;
}
//# sourceMappingURL=request-validator.d.ts.map