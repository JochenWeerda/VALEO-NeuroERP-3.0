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
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerQuoteRoutes = registerQuoteRoutes;
function registerQuoteRoutes(fastify) {
    return __awaiter(this, void 0, void 0, function () {
        var _this = this;
        return __generator(this, function (_a) {
            // Base path for quotes
            fastify.register(function (quoteRoutes) { return __awaiter(_this, void 0, void 0, function () {
                var _this = this;
                return __generator(this, function (_a) {
                    // GET /quotes - List quotes
                    quoteRoutes.get('/', {
                        schema: {
                            description: 'List quotes with pagination and filtering',
                            tags: ['Quotes'],
                            querystring: {
                                type: 'object',
                                properties: {
                                    customerId: { type: 'string' },
                                    status: { type: 'string', enum: ['Draft', 'Sent', 'Accepted', 'Rejected', 'Expired'] },
                                    page: { type: 'integer', minimum: 1, default: 1 },
                                    pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
                                },
                            },
                            response: {
                                200: {
                                    type: 'object',
                                    properties: {
                                        data: { type: 'array' },
                                        pagination: {
                                            type: 'object',
                                            properties: {
                                                page: { type: 'integer' },
                                                pageSize: { type: 'integer' },
                                                total: { type: 'integer' },
                                                totalPages: { type: 'integer' },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    }, function (request, reply) { return __awaiter(_this, void 0, void 0, function () {
                        return __generator(this, function (_a) {
                            // TODO: Implement quote listing
                            return [2 /*return*/, {
                                    data: [],
                                    pagination: {
                                        page: 1,
                                        pageSize: 20,
                                        total: 0,
                                        totalPages: 0,
                                    },
                                }];
                        });
                    }); });
                    // POST /quotes - Create quote
                    quoteRoutes.post('/', {
                        schema: {
                            description: 'Create a new quote',
                            tags: ['Quotes'],
                            body: {
                                type: 'object',
                                required: ['customerId', 'lines'],
                                properties: {
                                    customerId: { type: 'string' },
                                    lines: { type: 'array' },
                                    validUntil: { type: 'string', format: 'date' },
                                    notes: { type: 'string' },
                                },
                            },
                            response: {
                                201: { type: 'object' },
                            },
                        },
                    }, function (request, reply) { return __awaiter(_this, void 0, void 0, function () {
                        return __generator(this, function (_a) {
                            // TODO: Implement quote creation
                            return [2 /*return*/, reply.code(201).send({ id: 'quote-123' })];
                        });
                    }); });
                    // GET /quotes/:id - Get quote by ID
                    quoteRoutes.get('/:id', {
                        schema: {
                            description: 'Get quote by ID',
                            tags: ['Quotes'],
                            params: {
                                type: 'object',
                                required: ['id'],
                                properties: {
                                    id: { type: 'string' },
                                },
                            },
                            response: {
                                200: { type: 'object' },
                                404: { type: 'object' },
                            },
                        },
                    }, function (request, reply) { return __awaiter(_this, void 0, void 0, function () {
                        var id;
                        return __generator(this, function (_a) {
                            id = request.params.id;
                            return [2 /*return*/, { id: id, status: 'Draft' }];
                        });
                    }); });
                    // PATCH /quotes/:id - Update quote
                    quoteRoutes.patch('/:id', {
                        schema: {
                            description: 'Update quote',
                            tags: ['Quotes'],
                            params: {
                                type: 'object',
                                required: ['id'],
                                properties: {
                                    id: { type: 'string' },
                                },
                            },
                            body: { type: 'object' },
                            response: {
                                200: { type: 'object' },
                            },
                        },
                    }, function (request, reply) { return __awaiter(_this, void 0, void 0, function () {
                        var id;
                        return __generator(this, function (_a) {
                            id = request.params.id;
                            return [2 /*return*/, { id: id, updated: true }];
                        });
                    }); });
                    // POST /quotes/:id/send - Send quote
                    quoteRoutes.post('/:id/send', {
                        schema: {
                            description: 'Send quote to customer',
                            tags: ['Quotes'],
                            params: {
                                type: 'object',
                                required: ['id'],
                                properties: {
                                    id: { type: 'string' },
                                },
                            },
                            response: {
                                200: { type: 'object' },
                            },
                        },
                    }, function (request, reply) { return __awaiter(_this, void 0, void 0, function () {
                        var id;
                        return __generator(this, function (_a) {
                            id = request.params.id;
                            return [2 /*return*/, { id: id, status: 'Sent' }];
                        });
                    }); });
                    return [2 /*return*/];
                });
            }); }, { prefix: '/quotes' });
            return [2 /*return*/];
        });
    });
}
