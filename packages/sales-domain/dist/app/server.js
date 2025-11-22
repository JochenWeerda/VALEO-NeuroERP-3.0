"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var _a, _b;
Object.defineProperty(exports, "__esModule", { value: true });
exports.start = exports.server = void 0;
var fastify_1 = require("fastify");
var swagger_1 = require("@fastify/swagger");
var swagger_ui_1 = require("@fastify/swagger-ui");
var quotes_1 = require("./routes/quotes");
var orders_1 = require("./routes/orders");
var invoices_1 = require("./routes/invoices");
var credit_notes_1 = require("./routes/credit-notes");
var sales_offers_1 = require("./routes/sales-offers");
var auth_1 = require("./middleware/auth");
var tenant_1 = require("./middleware/tenant");
var request_id_1 = require("./middleware/request-id");
var logger_1 = require("./middleware/logger");
var error_handler_1 = require("./middleware/error-handler");
var health_1 = require("./routes/health");
var publisher_1 = require("../infra/messaging/publisher");
var tracer_1 = require("../infra/telemetry/tracer");
var server = (0, fastify_1.default)({
    logger: {
        level: (_a = process.env.LOG_LEVEL) !== null && _a !== void 0 ? _a : 'info',
        serializers: {
            req: function (req) {
                var _a, _b;
                return ({
                    method: req.method,
                    url: req.url,
                    hostname: req.hostname,
                    remoteAddress: req.ip,
                    remotePort: (_b = (_a = req.socket) === null || _a === void 0 ? void 0 : _a.remotePort) !== null && _b !== void 0 ? _b : undefined,
                });
            },
            res: function (res) { return ({
                statusCode: res.statusCode,
            }); },
        },
    },
    disableRequestLogging: false,
    requestIdLogLabel: 'requestId',
    genReqId: function () { return require('crypto').randomUUID(); },
});
exports.server = server;
// Register Swagger/OpenAPI
server.register(swagger_1.default, {
    openapi: {
        openapi: '3.0.3',
        info: {
            title: 'Sales Domain API',
            description: 'REST API for Sales Domain operations (Quotes, Sales Offers, Orders, Invoices, Credit Notes)',
            version: '1.0.0',
        },
        servers: [
            {
                url: (_b = process.env.API_BASE_URL) !== null && _b !== void 0 ? _b : 'http://localhost:3001',
                description: 'Development server',
            },
        ],
        components: {
            securitySchemes: {
                bearerAuth: {
                    type: 'http',
                    scheme: 'bearer',
                    bearerFormat: 'JWT',
                },
            },
        },
        security: [
            {
                bearerAuth: [],
            },
        ],
    },
});
server.register(swagger_ui_1.default, {
    routePrefix: '/docs',
    uiConfig: {
        docExpansion: 'full',
        deepLinking: false,
    },
    staticCSP: true,
    transformStaticCSP: function (header) { return header; },
});
// Initialize telemetry
(0, tracer_1.setupTelemetry)();
// Register middleware
server.addHook('onRequest', request_id_1.requestIdMiddleware);
server.addHook('onRequest', logger_1.loggerMiddleware);
server.addHook('onRequest', auth_1.authMiddleware);
server.addHook('onRequest', tenant_1.tenantMiddleware);
// Register tracing hooks
var tracing = (0, tracer_1.tracingMiddleware)();
server.addHook('onRequest', tracing.onRequest);
server.addHook('onResponse', tracing.onResponse);
server.addHook('onError', tracing.onError);
// Register error handler
server.setErrorHandler(error_handler_1.errorHandler);
// Register routes
server.register(health_1.healthRoutes);
server.register(quotes_1.registerQuoteRoutes);
server.register(sales_offers_1.registerSalesOfferRoutes);
server.register(orders_1.registerOrderRoutes);
server.register(invoices_1.registerInvoiceRoutes);
server.register(credit_notes_1.registerCreditNoteRoutes);
// Graceful shutdown
var gracefulShutdown = function (signal) { return __awaiter(void 0, void 0, void 0, function () {
    var publisher, error_1;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                server.log.info("Received ".concat(signal, ", shutting down gracefully"));
                _a.label = 1;
            case 1:
                _a.trys.push([1, 4, , 5]);
                publisher = (0, publisher_1.getEventPublisher)();
                return [4 /*yield*/, publisher.disconnect()];
            case 2:
                _a.sent();
                // Close server
                return [4 /*yield*/, server.close()];
            case 3:
                // Close server
                _a.sent();
                server.log.info('Server closed successfully');
                process.exit(0);
                return [3 /*break*/, 5];
            case 4:
                error_1 = _a.sent();
                server.log.error({ error: error_1 }, 'Error during shutdown');
                process.exit(1);
                return [3 /*break*/, 5];
            case 5: return [2 /*return*/];
        }
    });
}); };
process.on('SIGTERM', function () { return gracefulShutdown('SIGTERM'); });
process.on('SIGINT', function () { return gracefulShutdown('SIGINT'); });
// Start server
var start = function () { return __awaiter(void 0, void 0, void 0, function () {
    var port, host, publisher, err_1;
    var _a;
    return __generator(this, function (_b) {
        switch (_b.label) {
            case 0:
                _b.trys.push([0, 3, , 4]);
                port = Number(process.env.PORT) || 3001;
                host = (_a = process.env.HOST) !== null && _a !== void 0 ? _a : '0.0.0.0';
                publisher = (0, publisher_1.getEventPublisher)();
                return [4 /*yield*/, publisher.connect()];
            case 1:
                _b.sent();
                return [4 /*yield*/, server.listen({ port: port, host: host })];
            case 2:
                _b.sent();
                server.log.info("Sales Domain API listening on http://".concat(host, ":").concat(port));
                server.log.info("API documentation available at http://".concat(host, ":").concat(port, "/docs"));
                return [3 /*break*/, 4];
            case 3:
                err_1 = _b.sent();
                server.log.error(err_1);
                process.exit(1);
                return [3 /*break*/, 4];
            case 4: return [2 /*return*/];
        }
    });
}); };
exports.start = start;
