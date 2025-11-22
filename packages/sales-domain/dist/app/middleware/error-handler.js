"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.errorHandler = errorHandler;
function errorHandler(error, request, reply) {
    var _a;
    // Log the error
    reply.log.error({
        error: error.message,
        stack: error.stack,
        code: error.code,
        statusCode: error.statusCode,
    }, 'Request error');
    // Handle different types of errors
    if (error.validation) {
        return reply.code(400).send({
            error: 'Validation Error',
            message: 'Request validation failed',
            details: error.validation,
        });
    }
    if (error.code === 'FST_ERR_NOT_FOUND') {
        return reply.code(404).send({
            error: 'Not Found',
            message: 'The requested resource was not found',
        });
    }
    // Default error response
    var statusCode = error.statusCode || 500;
    var message = statusCode >= 500 ? 'Internal server error' : error.message;
    return reply.code(statusCode).send(__assign({ error: (_a = error.name) !== null && _a !== void 0 ? _a : 'Error', message: message }, (process.env.NODE_ENV === 'development' && { stack: error.stack })));
}
