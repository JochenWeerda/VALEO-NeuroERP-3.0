"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.verifyJWT = verifyJWT;
exports.createJWT = createJWT;
const jose_1 = require("jose");
class JWKSManager {
    jwksClient = null;
    config;
    constructor(config) {
        this.config = config;
    }
    getJWKSClient() {
        if (this.jwksClient === undefined || this.jwksClient === null) {
            this.jwksClient = (0, jose_1.createRemoteJWKSet)(new URL(this.config.jwksUrl));
        }
        return this.jwksClient;
    }
    async verifyToken(token) {
        const client = this.getJWKSClient();
        const options = {};
        if (this.config.issuer)
            options.issuer = this.config.issuer;
        if (this.config.audience)
            options.audience = this.config.audience;
        const { payload } = await (0, jose_1.jwtVerify)(token, client, options);
        return payload;
    }
}
// Global JWKS manager instance
let jwksManager = null;
function getJWKSManager() {
    if (jwksManager === undefined || jwksManager === null) {
        const jwksUrl = process.env.JWKS_URL ?? 'https://auth.example.com/.well-known/jwks.json';
        const issuer = process.env.JWT_ISSUER;
        const audience = process.env.JWT_AUDIENCE;
        const config = { jwksUrl };
        if (issuer)
            config.issuer = issuer;
        if (audience)
            config.audience = audience;
        jwksManager = new JWKSManager(config);
    }
    return jwksManager;
}
async function verifyJWT(token) {
    const manager = getJWKSManager();
    return manager.verifyToken(token);
}
function createJWT(payload, expiresIn = '1h') {
    // Note: This is a simplified implementation
    // In production, you would use a proper JWT library to sign tokens
    // For now, we'll just return a mock token for development
    return `mock.jwt.token.${Date.now()}`;
}
//# sourceMappingURL=jwt.js.map