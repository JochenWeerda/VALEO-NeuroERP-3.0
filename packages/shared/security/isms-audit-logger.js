"use strict";
/**
 * ISMS Audit Logger
 * ISO 27001 A.12.4 Logging and Monitoring Compliance
 * Communications Security Audit Trail
 */
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
exports.ISMSAuditLogger = void 0;
var crypto_1 = require("crypto");
var ISMSAuditLogger = /** @class */ (function () {
    function ISMSAuditLogger(serviceName, environment) {
        if (environment === void 0) { environment = 'production'; }
        this.serviceName = serviceName;
        this.environment = environment;
    }
    /**
     * Logs a secure business event with audit trail
     * A.12.4.1 Event logging
     */
    ISMSAuditLogger.prototype.logSecureEvent = function (eventType_1, details_1, tenantId_1, userId_1) {
        return __awaiter(this, arguments, void 0, function (eventType, details, tenantId, userId, severity) {
            var event, encryptedEvent;
            if (severity === void 0) { severity = 'MEDIUM'; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        event = {
                            id: (0, crypto_1.randomUUID)(),
                            eventType: eventType,
                            severity: severity,
                            source: this.serviceName,
                            userId: userId,
                            tenantId: tenantId,
                            timestamp: new Date(),
                            details: this.sanitizeDetails(details),
                            correlationId: (0, crypto_1.randomUUID)()
                        };
                        return [4 /*yield*/, this.encryptAuditData(event)];
                    case 1:
                        encryptedEvent = _a.sent();
                        // Store in secure audit storage
                        return [4 /*yield*/, this.storeSecureAuditEvent(encryptedEvent)];
                    case 2:
                        // Store in secure audit storage
                        _a.sent();
                        // Real-time monitoring integration
                        return [4 /*yield*/, this.sendToMonitoring(event)];
                    case 3:
                        // Real-time monitoring integration
                        _a.sent();
                        console.log("[AUDIT] ".concat(eventType, ":"), {
                            eventId: event.id,
                            tenantId: tenantId,
                            userId: userId,
                            timestamp: event.timestamp.toISOString(),
                            severity: severity
                        });
                        return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Logs a security incident for immediate attention
     * A.16.1.5 Response to information security incidents
     */
    ISMSAuditLogger.prototype.logSecurityIncident = function (eventType_1, details_1, tenantId_1, userId_1) {
        return __awaiter(this, arguments, void 0, function (eventType, details, tenantId, userId, riskLevel) {
            var incident;
            if (riskLevel === void 0) { riskLevel = 'HIGH'; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        incident = {
                            id: (0, crypto_1.randomUUID)(),
                            incidentId: "INC-".concat(Date.now(), "-").concat(tenantId.substring(0, 4).toUpperCase()),
                            eventType: eventType,
                            severity: riskLevel,
                            source: this.serviceName,
                            userId: userId,
                            tenantId: tenantId,
                            timestamp: new Date(),
                            details: this.sanitizeDetails(details),
                            correlationId: (0, crypto_1.randomUUID)(),
                            status: 'OPEN',
                            riskLevel: riskLevel,
                            impactAssessment: this.assessIncidentImpact(eventType, details, riskLevel),
                            responseActions: this.getInitialResponseActions(eventType, riskLevel)
                        };
                        // Immediate secure storage
                        return [4 /*yield*/, this.storeSecurityIncident(incident)];
                    case 1:
                        // Immediate secure storage
                        _a.sent();
                        if (!(riskLevel === 'CRITICAL' || riskLevel === 'HIGH')) return [3 /*break*/, 3];
                        return [4 /*yield*/, this.alertSecurityTeam(incident)];
                    case 2:
                        _a.sent();
                        _a.label = 3;
                    case 3: 
                    // Integrate with incident response system
                    return [4 /*yield*/, this.triggerIncidentResponse(incident)];
                    case 4:
                        // Integrate with incident response system
                        _a.sent();
                        console.error("[SECURITY INCIDENT] ".concat(eventType, ":"), {
                            incidentId: incident.incidentId,
                            tenantId: tenantId,
                            userId: userId,
                            riskLevel: riskLevel,
                            timestamp: incident.timestamp.toISOString()
                        });
                        return [2 /*return*/, incident];
                }
            });
        });
    };
    /**
     * Logs communication security events
     * A.13.1 Network security management
     * A.13.2 Information transfer
     */
    ISMSAuditLogger.prototype.logCommunicationEvent = function (eventType_1, details_1, tenantId_1, userId_1) {
        return __awaiter(this, arguments, void 0, function (eventType, details, tenantId, userId, success) {
            var severity, eventDetails;
            if (success === void 0) { success = true; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        severity = success ? 'LOW' : 'HIGH';
                        eventDetails = __assign(__assign({}, details), { success: success, protocol: details.protocol || 'HTTPS', encryptionStandard: 'AES-256-GCM', tlsVersion: 'TLS 1.3' });
                        return [4 /*yield*/, this.logSecureEvent("COMMUNICATION_".concat(eventType), eventDetails, tenantId, userId, severity)];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Logs data access events for compliance
     * A.9.4.5 Access control to program source code
     */
    ISMSAuditLogger.prototype.logDataAccess = function (action_1, resource_1, resourceId_1, tenantId_1, userId_1) {
        return __awaiter(this, arguments, void 0, function (action, resource, resourceId, tenantId, userId, success, sensitiveData) {
            var severity, _a, _b;
            var _c;
            if (success === void 0) { success = true; }
            if (sensitiveData === void 0) { sensitiveData = false; }
            return __generator(this, function (_d) {
                switch (_d.label) {
                    case 0:
                        severity = sensitiveData ? 'HIGH' : success ? 'LOW' : 'MEDIUM';
                        _a = this.logSecureEvent;
                        _b = ["DATA_ACCESS_".concat(action)];
                        _c = {
                            resource: resource,
                            resourceId: resourceId,
                            success: success,
                            sensitiveData: sensitiveData,
                            accessMethod: 'API'
                        };
                        return [4 /*yield*/, this.getUserRole(userId, tenantId)];
                    case 1: return [4 /*yield*/, _a.apply(this, _b.concat([(_c.userRole = _d.sent(),
                                _c), tenantId,
                            userId,
                            severity]))];
                    case 2:
                        _d.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Logs authentication and authorization events
     * A.9.2 User access management
     */
    ISMSAuditLogger.prototype.logAuthEvent = function (eventType_1, details_1, tenantId_1, userId_1) {
        return __awaiter(this, arguments, void 0, function (eventType, details, tenantId, userId, success) {
            var severity;
            if (success === void 0) { success = true; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        severity = success ? 'LOW' : 'MEDIUM';
                        return [4 /*yield*/, this.logSecureEvent("AUTH_".concat(eventType), __assign(__assign({}, details), { success: success, authMethod: 'JWT', mfaEnabled: true // Would be dynamic in real implementation
                             }), tenantId, userId, severity)];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    // Private helper methods
    ISMSAuditLogger.prototype.sanitizeDetails = function (details) {
        var sanitized = __assign({}, details);
        // Remove sensitive fields
        var sensitiveFields = ['password', 'token', 'key', 'secret', 'creditCard', 'ssn'];
        for (var _i = 0, sensitiveFields_1 = sensitiveFields; _i < sensitiveFields_1.length; _i++) {
            var field = sensitiveFields_1[_i];
            if (sanitized[field]) {
                sanitized[field] = '[REDACTED]';
            }
        }
        // Truncate large strings
        for (var _a = 0, _b = Object.entries(sanitized); _a < _b.length; _a++) {
            var _c = _b[_a], key = _c[0], value = _c[1];
            if (typeof value === 'string' && value.length > 1000) {
                sanitized[key] = value.substring(0, 1000) + '...[TRUNCATED]';
            }
        }
        return sanitized;
    };
    ISMSAuditLogger.prototype.encryptAuditData = function (event) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                // In real implementation, would use proper encryption service
                // A.10.1.1 Policy on the use of cryptographic controls
                return [2 /*return*/, Buffer.from(JSON.stringify(event)).toString('base64')];
            });
        });
    };
    ISMSAuditLogger.prototype.storeSecureAuditEvent = function (encryptedEvent) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                // In real implementation, would store in secure audit database
                // A.12.3.1 Information backup
                console.log("[AUDIT STORAGE] Event stored securely: ".concat(encryptedEvent.substring(0, 50), "..."));
                return [2 /*return*/];
            });
        });
    };
    ISMSAuditLogger.prototype.storeSecurityIncident = function (incident) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                // In real implementation, would store in incident management system
                console.log("[INCIDENT STORAGE] Incident ".concat(incident.incidentId, " stored"));
                return [2 /*return*/];
            });
        });
    };
    ISMSAuditLogger.prototype.sendToMonitoring = function (event) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                // In real implementation, would integrate with monitoring systems
                if (event.severity === 'HIGH' || event.severity === 'CRITICAL') {
                    console.log("[MONITORING] Alert sent for ".concat(event.eventType));
                }
                return [2 /*return*/];
            });
        });
    };
    ISMSAuditLogger.prototype.alertSecurityTeam = function (incident) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                // In real implementation, would send alerts via email/SMS/Slack
                console.log("[SECURITY ALERT] Team notified of incident ".concat(incident.incidentId));
                return [2 /*return*/];
            });
        });
    };
    ISMSAuditLogger.prototype.triggerIncidentResponse = function (incident) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                // In real implementation, would integrate with incident response workflows
                console.log("[INCIDENT RESPONSE] Workflow triggered for ".concat(incident.incidentId));
                return [2 /*return*/];
            });
        });
    };
    ISMSAuditLogger.prototype.assessIncidentImpact = function (eventType, details, riskLevel) {
        // Simplified impact assessment - would be more sophisticated in real implementation
        var impactMatrix = {
            'CRITICAL': 'Potential data breach or system compromise. Immediate containment required.',
            'HIGH': 'Security policy violation or failed access attempt. Investigation needed.',
            'MEDIUM': 'Minor security anomaly detected. Monitoring recommended.',
            'LOW': 'Informational security event logged for audit purposes.'
        };
        return impactMatrix[riskLevel] || 'Impact assessment pending';
    };
    ISMSAuditLogger.prototype.getInitialResponseActions = function (eventType, riskLevel) {
        var actions = [];
        if (riskLevel === 'CRITICAL') {
            actions.push('Immediate containment', 'Notify CISO', 'Activate incident response team');
        }
        else if (riskLevel === 'HIGH') {
            actions.push('Investigate immediately', 'Review access logs', 'Notify security team');
        }
        else {
            actions.push('Monitor closely', 'Review in next security review');
        }
        return actions;
    };
    ISMSAuditLogger.prototype.getUserRole = function (userId, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                // In real implementation, would query user management system
                return [2 /*return*/, 'user'];
            });
        });
    };
    return ISMSAuditLogger;
}());
exports.ISMSAuditLogger = ISMSAuditLogger;
