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
exports.EventPublisher = void 0;
exports.createEventPublisher = createEventPublisher;
exports.getEventPublisher = getEventPublisher;
var nats_1 = require("nats");
var EventPublisher = /** @class */ (function () {
    function EventPublisher(config) {
        this.config = config;
        this.connection = null;
        this.stringCodec = (0, nats_1.StringCodec)();
        this.jsonCodec = (0, nats_1.JSONCodec)();
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelayMs = 1000;
        this.maxReconnectAttempts = config.maxReconnectAttempts || 5;
        this.reconnectDelayMs = config.reconnectDelayMs || 1000;
    }
    EventPublisher.prototype.connect = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a, error_1;
            var _this = this;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _b.trys.push([0, 2, , 3]);
                        _a = this;
                        return [4 /*yield*/, (0, nats_1.connect)({
                                servers: this.config.natsUrl,
                                reconnect: true,
                                maxReconnectAttempts: this.maxReconnectAttempts,
                                reconnectTimeWait: this.reconnectDelayMs,
                            })];
                    case 1:
                        _a.connection = _b.sent();
                        this.isConnected = true;
                        this.reconnectAttempts = 0;
                        console.log('Sales domain event publisher connected to NATS');
                        // Handle connection events
                        this.connection.closed().then(function () {
                            _this.isConnected = false;
                            console.log('NATS connection closed');
                        });
                        return [3 /*break*/, 3];
                    case 2:
                        error_1 = _b.sent();
                        console.error('Failed to connect to NATS:', error_1);
                        throw error_1;
                    case 3: return [2 /*return*/];
                }
            });
        });
    };
    EventPublisher.prototype.disconnect = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!this.connection) return [3 /*break*/, 2];
                        return [4 /*yield*/, this.connection.close()];
                    case 1:
                        _a.sent();
                        this.connection = null;
                        this.isConnected = false;
                        _a.label = 2;
                    case 2: return [2 /*return*/];
                }
            });
        });
    };
    EventPublisher.prototype.publish = function (event_1) {
        return __awaiter(this, arguments, void 0, function (event, options) {
            var enrichedEvent, subject, payload, error_2;
            if (options === void 0) { options = {}; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!this.isConnected || !this.connection) {
                            throw new Error('Event publisher is not connected to NATS');
                        }
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        enrichedEvent = __assign(__assign({}, event), { correlationId: options.correlationId || event.correlationId, causationId: options.causationId || event.causationId });
                        subject = event.eventType;
                        payload = this.jsonCodec.encode(enrichedEvent);
                        return [4 /*yield*/, this.connection.publish(subject, payload)];
                    case 2:
                        _a.sent();
                        console.log("Published sales event ".concat(event.eventType, " with ID ").concat(event.eventId));
                        return [3 /*break*/, 4];
                    case 3:
                        error_2 = _a.sent();
                        console.error("Failed to publish event ".concat(event.eventType, ":"), error_2);
                        throw error_2;
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    EventPublisher.prototype.publishBatch = function (events_1) {
        return __awaiter(this, arguments, void 0, function (events, options) {
            var _i, events_2, event_1, enrichedEvent, subject, payload, error_3;
            if (options === void 0) { options = {}; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!this.isConnected || !this.connection) {
                            throw new Error('Event publisher is not connected to NATS');
                        }
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        for (_i = 0, events_2 = events; _i < events_2.length; _i++) {
                            event_1 = events_2[_i];
                            enrichedEvent = __assign(__assign({}, event_1), { correlationId: options.correlationId || event_1.correlationId, causationId: options.causationId || event_1.causationId });
                            subject = event_1.eventType;
                            payload = this.jsonCodec.encode(enrichedEvent);
                            this.connection.publish(subject, payload);
                        }
                        // Flush to ensure all messages are sent
                        return [4 /*yield*/, this.connection.flush()];
                    case 2:
                        // Flush to ensure all messages are sent
                        _a.sent();
                        console.log("Published batch of ".concat(events.length, " sales events"));
                        return [3 /*break*/, 4];
                    case 3:
                        error_3 = _a.sent();
                        console.error('Failed to publish event batch:', error_3);
                        throw error_3;
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    EventPublisher.prototype.isHealthy = function () {
        return this.isConnected && this.connection !== null;
    };
    EventPublisher.prototype.getConnectionStatus = function () {
        if (!this.connection)
            return 'disconnected';
        return this.isConnected ? 'connected' : 'disconnected';
    };
    return EventPublisher;
}());
exports.EventPublisher = EventPublisher;
// Factory function to create event publisher
function createEventPublisher(config) {
    return new EventPublisher(config);
}
// Global publisher instance
var globalPublisher = null;
function getEventPublisher() {
    var _a;
    if (globalPublisher === undefined || globalPublisher === null) {
        var natsUrl = (_a = process.env.NATS_URL) !== null && _a !== void 0 ? _a : 'nats://localhost:4222';
        globalPublisher = createEventPublisher({ natsUrl: natsUrl });
    }
    return globalPublisher;
}
