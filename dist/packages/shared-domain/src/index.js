"use strict";
// ===== VALEO NeuroERP 3.0 - SHARED DOMAIN PACKAGE =====
// Central exports for all shared domain functionality
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
// Core entities and value objects
__exportStar(require("./core/entities/common"), exports);
__exportStar(require("./core/entities/notification"), exports);
__exportStar(require("./core/entities/user"), exports);
// Services
__exportStar(require("./services/common-service"), exports);
__exportStar(require("./services/notification-service"), exports);
__exportStar(require("./services/user-service"), exports);
// Application services
__exportStar(require("./application/services/shared-domain-service"), exports);
