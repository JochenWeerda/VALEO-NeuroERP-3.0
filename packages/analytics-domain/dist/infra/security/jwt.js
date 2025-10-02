"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.JWTService = void 0;
exports.createJWTService = createJWTService;
exports.getJWTService = getJWTService;
const jose_1 = require("jose");
class JWTService {
    options;
    jwks;
    constructor(options) {
        this.options = options;
        this.jwks = (0, jose_1.createRemoteJWKSet)(new URL(options.jwksUrl));
    }
    async verifyToken(token) {
        try {
            const { payload } = await (0, jose_1.jwtVerify)(token, this.jwks, {
                issuer: this.options.issuer,
                audience: this.options.audience,
            });
            return this.mapPayloadToUser(payload);
        }
        catch (error) {
            throw new Error(`Token verification failed: ${error}`);
        }
    }
    mapPayloadToUser(payload) {
        return {
            sub: payload.sub,
            email: payload.email,
            roles: payload.roles || [],
            permissions: payload.permissions || [],
            tenantId: payload.tenantId,
            ...payload,
        };
    }
    async getUserFromRequest(authHeader) {
        if (!authHeader.startsWith('Bearer ')) {
            return null;
        }
        const token = authHeader.substring(7);
        return this.verifyToken(token);
    }
}
exports.JWTService = JWTService;
function createJWTService(options) {
    return new JWTService(options);
}
let globalJWTService = null;
function getJWTService() {
    if (!globalJWTService) {
        const jwksUrl = process.env.JWKS_URL || 'https://auth.example.com/.well-known/jwks.json';
        globalJWTService = createJWTService({ jwksUrl });
    }
    return globalJWTService;
}
//# sourceMappingURL=jwt.js.map