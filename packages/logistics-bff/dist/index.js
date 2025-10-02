"use strict";
// Logistics BFF (Backend for Frontend)
// Provides frontend-optimized endpoints for Dashboards, Voice/Chat, and Dispatch Actions
Object.defineProperty(exports, "__esModule", { value: true });
exports.DispatchActionService = exports.VoiceChatService = exports.LogisticsDashboardService = exports.startLogisticsBFF = void 0;
var bff_server_1 = require("./bff-server");
Object.defineProperty(exports, "startLogisticsBFF", { enumerable: true, get: function () { return bff_server_1.startLogisticsBFF; } });
var dashboard_service_1 = require("./services/dashboard-service");
Object.defineProperty(exports, "LogisticsDashboardService", { enumerable: true, get: function () { return dashboard_service_1.LogisticsDashboardService; } });
var voice_chat_service_1 = require("./services/voice-chat-service");
Object.defineProperty(exports, "VoiceChatService", { enumerable: true, get: function () { return voice_chat_service_1.VoiceChatService; } });
var dispatch_action_service_1 = require("./services/dispatch-action-service");
Object.defineProperty(exports, "DispatchActionService", { enumerable: true, get: function () { return dispatch_action_service_1.DispatchActionService; } });
//# sourceMappingURL=index.js.map