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
exports.verifyJWT = verifyJWT;
exports.createJWT = createJWT;
var jose_1 = require("jose");
var JWKSManager = /** @class */ (function () {
    function JWKSManager(config) {
        this.jwksClient = null;
        this.config = config;
    }
    JWKSManager.prototype.getJWKSClient = function () {
        if (this.jwksClient === undefined || this.jwksClient === null) {
            this.jwksClient = (0, jose_1.createRemoteJWKSet)(new URL(this.config.jwksUrl));
        }
        return this.jwksClient;
    };
    JWKSManager.prototype.verifyToken = function (token) {
        return __awaiter(this, void 0, void 0, function () {
            var client, options, payload;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        client = this.getJWKSClient();
                        options = {};
                        if (this.config.issuer)
                            options.issuer = this.config.issuer;
                        if (this.config.audience)
                            options.audience = this.config.audience;
                        return [4 /*yield*/, (0, jose_1.jwtVerify)(token, client, options)];
                    case 1:
                        payload = (_a.sent()).payload;
                        return [2 /*return*/, payload];
                }
            });
        });
    };
    return JWKSManager;
}());
// Global JWKS manager instance
var jwksManager = null;
function getJWKSManager() {
    var _a;
    if (jwksManager === undefined || jwksManager === null) {
        var jwksUrl = (_a = process.env.JWKS_URL) !== null && _a !== void 0 ? _a : 'https://auth.example.com/.well-known/jwks.json';
        var issuer = process.env.JWT_ISSUER;
        var audience = process.env.JWT_AUDIENCE;
        var config = { jwksUrl: jwksUrl };
        if (issuer)
            config.issuer = issuer;
        if (audience)
            config.audience = audience;
        jwksManager = new JWKSManager(config);
    }
    return jwksManager;
}
function verifyJWT(token) {
    return __awaiter(this, void 0, void 0, function () {
        var manager;
        return __generator(this, function (_a) {
            manager = getJWKSManager();
            return [2 /*return*/, manager.verifyToken(token)];
        });
    });
}
function createJWT(payload, expiresIn) {
    if (expiresIn === void 0) { expiresIn = '1h'; }
    // Note: This is a simplified implementation
    // In production, you would use a proper JWT library to sign tokens
    // For now, we'll just return a mock token for development
    return "mock.jwt.token.".concat(Date.now());
}
