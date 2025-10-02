/**
 * API Error Handling and Status Codes
 */
export declare enum HttpStatusCode {
    OK = 200,
    CREATED = 201,
    NO_CONTENT = 204,
    BAD_REQUEST = 400,
    UNAUTHORIZED = 401,
    FORBIDDEN = 403,
    NOT_FOUND = 404,
    CONFLICT = 409,
    UNPROCESSABLE_ENTITY = 422,
    INTERNAL_SERVER_ERROR = 500,
    SERVICE_UNAVAILABLE = 503
}
export declare class ApiError extends Error {
    readonly statusCode: HttpStatusCode;
    readonly code: string;
    readonly details?: Record<string, unknown>;
    constructor(message: string, statusCode?: HttpStatusCode, code?: string, details?: Record<string, unknown>);
    private getDefaultCode;
    toJSON(): Record<string, unknown>;
}
export declare class ValidationError extends ApiError {
    readonly validationErrors: Array<{
        field: string;
        message: string;
        value?: unknown;
    }>;
    constructor(message: string, validationErrors: Array<{
        field: string;
        message: string;
        value?: unknown;
    }>, details?: Record<string, unknown>);
    toJSON(): Record<string, unknown>;
}
export declare class NotFoundError extends ApiError {
    constructor(resource: string, id: string);
}
export declare class ConflictError extends ApiError {
    constructor(resource: string, field: string, value: string);
}
export declare class UnauthorizedError extends ApiError {
    constructor(message?: string);
}
export declare class ForbiddenError extends ApiError {
    constructor(message?: string);
}
export declare class InternalServerError extends ApiError {
    constructor(message?: string, details?: Record<string, unknown>);
}
export declare class ServiceUnavailableError extends ApiError {
    constructor(message?: string);
}
export declare const createValidationError: (message: string, validationErrors: Array<{
    field: string;
    message: string;
    value?: unknown;
}>) => ValidationError;
export declare const createNotFoundError: (resource: string, id: string) => NotFoundError;
export declare const createConflictError: (resource: string, field: string, value: string) => ConflictError;
export declare const createUnauthorizedError: (message?: string) => UnauthorizedError;
export declare const createForbiddenError: (message?: string) => ForbiddenError;
export declare const createInternalServerError: (message?: string, details?: Record<string, unknown>) => InternalServerError;
export declare const createServiceUnavailableError: (message?: string) => ServiceUnavailableError;
//# sourceMappingURL=api-errors.d.ts.map