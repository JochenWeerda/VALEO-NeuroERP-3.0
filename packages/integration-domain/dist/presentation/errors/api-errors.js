/**
 * API Error Handling and Status Codes
 */
export var HttpStatusCode;
(function (HttpStatusCode) {
    HttpStatusCode[HttpStatusCode["OK"] = 200] = "OK";
    HttpStatusCode[HttpStatusCode["CREATED"] = 201] = "CREATED";
    HttpStatusCode[HttpStatusCode["NO_CONTENT"] = 204] = "NO_CONTENT";
    HttpStatusCode[HttpStatusCode["BAD_REQUEST"] = 400] = "BAD_REQUEST";
    HttpStatusCode[HttpStatusCode["UNAUTHORIZED"] = 401] = "UNAUTHORIZED";
    HttpStatusCode[HttpStatusCode["FORBIDDEN"] = 403] = "FORBIDDEN";
    HttpStatusCode[HttpStatusCode["NOT_FOUND"] = 404] = "NOT_FOUND";
    HttpStatusCode[HttpStatusCode["CONFLICT"] = 409] = "CONFLICT";
    HttpStatusCode[HttpStatusCode["UNPROCESSABLE_ENTITY"] = 422] = "UNPROCESSABLE_ENTITY";
    HttpStatusCode[HttpStatusCode["INTERNAL_SERVER_ERROR"] = 500] = "INTERNAL_SERVER_ERROR";
    HttpStatusCode[HttpStatusCode["SERVICE_UNAVAILABLE"] = 503] = "SERVICE_UNAVAILABLE";
})(HttpStatusCode || (HttpStatusCode = {}));
export class ApiError extends Error {
    statusCode;
    code;
    details;
    constructor(message, statusCode = HttpStatusCode.INTERNAL_SERVER_ERROR, code, details) {
        super(message);
        this.name = 'ApiError';
        this.statusCode = statusCode;
        this.code = code || this.getDefaultCode(statusCode);
        this.details = details;
    }
    getDefaultCode(statusCode) {
        switch (statusCode) {
            case HttpStatusCode.BAD_REQUEST:
                return 'BAD_REQUEST';
            case HttpStatusCode.UNAUTHORIZED:
                return 'UNAUTHORIZED';
            case HttpStatusCode.FORBIDDEN:
                return 'FORBIDDEN';
            case HttpStatusCode.NOT_FOUND:
                return 'NOT_FOUND';
            case HttpStatusCode.CONFLICT:
                return 'CONFLICT';
            case HttpStatusCode.UNPROCESSABLE_ENTITY:
                return 'UNPROCESSABLE_ENTITY';
            case HttpStatusCode.INTERNAL_SERVER_ERROR:
                return 'INTERNAL_SERVER_ERROR';
            case HttpStatusCode.SERVICE_UNAVAILABLE:
                return 'SERVICE_UNAVAILABLE';
            default:
                return 'UNKNOWN_ERROR';
        }
    }
    toJSON() {
        return {
            error: {
                message: this.message,
                code: this.code,
                statusCode: this.statusCode,
                details: this.details,
                timestamp: new Date().toISOString()
            }
        };
    }
}
export class ValidationError extends ApiError {
    validationErrors;
    constructor(message, validationErrors, details) {
        super(message, HttpStatusCode.UNPROCESSABLE_ENTITY, 'VALIDATION_ERROR', details);
        this.name = 'ValidationError';
        this.validationErrors = validationErrors;
    }
    toJSON() {
        return {
            error: {
                message: this.message,
                code: this.code,
                statusCode: this.statusCode,
                validationErrors: this.validationErrors,
                details: this.details,
                timestamp: new Date().toISOString()
            }
        };
    }
}
export class NotFoundError extends ApiError {
    constructor(resource, id) {
        super(`${resource} with id '${id}' not found`, HttpStatusCode.NOT_FOUND, 'NOT_FOUND', { resource, id });
        this.name = 'NotFoundError';
    }
}
export class ConflictError extends ApiError {
    constructor(resource, field, value) {
        super(`${resource} with ${field} '${value}' already exists`, HttpStatusCode.CONFLICT, 'CONFLICT', { resource, field, value });
        this.name = 'ConflictError';
    }
}
export class UnauthorizedError extends ApiError {
    constructor(message = 'Authentication required') {
        super(message, HttpStatusCode.UNAUTHORIZED, 'UNAUTHORIZED');
        this.name = 'UnauthorizedError';
    }
}
export class ForbiddenError extends ApiError {
    constructor(message = 'Access forbidden') {
        super(message, HttpStatusCode.FORBIDDEN, 'FORBIDDEN');
        this.name = 'ForbiddenError';
    }
}
export class InternalServerError extends ApiError {
    constructor(message = 'Internal server error', details) {
        super(message, HttpStatusCode.INTERNAL_SERVER_ERROR, 'INTERNAL_SERVER_ERROR', details);
        this.name = 'InternalServerError';
    }
}
export class ServiceUnavailableError extends ApiError {
    constructor(message = 'Service temporarily unavailable') {
        super(message, HttpStatusCode.SERVICE_UNAVAILABLE, 'SERVICE_UNAVAILABLE');
        this.name = 'ServiceUnavailableError';
    }
}
// Error factory functions
export const createValidationError = (message, validationErrors) => {
    return new ValidationError(message, validationErrors);
};
export const createNotFoundError = (resource, id) => {
    return new NotFoundError(resource, id);
};
export const createConflictError = (resource, field, value) => {
    return new ConflictError(resource, field, value);
};
export const createUnauthorizedError = (message) => {
    return new UnauthorizedError(message);
};
export const createForbiddenError = (message) => {
    return new ForbiddenError(message);
};
export const createInternalServerError = (message, details) => {
    return new InternalServerError(message, details);
};
export const createServiceUnavailableError = (message) => {
    return new ServiceUnavailableError(message);
};
//# sourceMappingURL=api-errors.js.map