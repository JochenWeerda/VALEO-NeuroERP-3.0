"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.JWTValidator = void 0;
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const jwk_to_pem_1 = __importDefault(require("jwk-to-pem"));
const axios_1 = __importDefault(require("axios"));
const auth_types_1 = require("../types/auth-types");
class JWTValidator {
    constructor(options) {
        this.jwksCache = new Map();
        this.cacheExpiry = new Map();
        this.jwksUrl = options.jwksUrl;
        this.issuer = options.issuer;
        this.audience = options.audience;
        this.algorithms = options.algorithms || ['RS256'];
    }
    /**
     * Validate JWT token and return user context
     */
    async validateToken(token) {
        try {
            // Decode token without verification first
            const decoded = jsonwebtoken_1.default.decode(token);
            if (!decoded) {
                throw new Error('Invalid token format');
            }
            // Verify token with JWKS if URL provided
            if (this.jwksUrl) {
                await this.verifyWithJWKS(token, decoded);
            }
            else {
                // Verify with local secret (for development/testing)
                await this.verifyWithSecret(token);
            }
            // Validate payload structure
            const payload = auth_types_1.JWTPayload.parse(decoded);
            // Check expiration
            if (payload.exp * 1000 < Date.now()) {
                throw new Error('Token expired');
            }
            // Check issuer and audience
            if (payload.iss !== this.issuer) {
                throw new Error('Invalid token issuer');
            }
            if (payload.aud !== this.audience) {
                throw new Error('Invalid token audience');
            }
            return {
                userId: payload.sub,
                tenantId: payload.tenantId,
                email: payload.email,
                roles: payload.roles,
                permissions: payload.permissions,
                token,
                expiresAt: payload.exp * 1000
            };
        }
        catch (error) {
            throw new Error(`JWT validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    /**
     * Verify token using JWKS (production)
     */
    async verifyWithJWKS(token, decoded) {
        const kid = decoded.header?.kid;
        if (!kid) {
            throw new Error('Token missing key ID (kid)');
        }
        // Get JWKS
        const jwks = await this.fetchJWKS();
        // Find the key
        const key = jwks.keys.find(k => k.kid === kid);
        if (!key) {
            throw new Error('Signing key not found in JWKS');
        }
        // Convert JWK to PEM
        const pem = (0, jwk_to_pem_1.default)(key);
        // Verify token
        jsonwebtoken_1.default.verify(token, pem, {
            issuer: this.issuer,
            audience: this.audience,
            algorithms: this.algorithms
        });
    }
    /**
     * Verify token using local secret (development)
     */
    async verifyWithSecret(token) {
        const secret = process.env.JWT_SECRET;
        if (!secret) {
            throw new Error('JWT_SECRET not configured');
        }
        jsonwebtoken_1.default.verify(token, secret, {
            issuer: this.issuer,
            audience: this.audience,
            algorithms: this.algorithms
        });
    }
    /**
     * Fetch JWKS with caching
     */
    async fetchJWKS() {
        if (this.jwksCache.size > 0) {
            // Return cached JWKS if still valid
            const cacheKey = this.jwksUrl;
            const expiry = this.cacheExpiry.get(cacheKey);
            if (expiry && expiry > Date.now()) {
                return this.jwksCache.get(cacheKey);
            }
        }
        try {
            const response = await axios_1.default.get(this.jwksUrl);
            const jwks = auth_types_1.JWKS.parse(response.data);
            // Cache JWKS for 1 hour
            this.jwksCache.set(this.jwksUrl, jwks);
            this.cacheExpiry.set(this.jwksUrl, Date.now() + 60 * 60 * 1000);
            return jwks;
        }
        catch (error) {
            throw new Error(`Failed to fetch JWKS: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    /**
     * Generate JWT token (for testing/development)
     */
    generateToken(payload) {
        const secret = process.env.JWT_SECRET;
        if (!secret) {
            throw new Error('JWT_SECRET not configured');
        }
        const fullPayload = {
            ...payload,
            iat: Math.floor(Date.now() / 1000),
            exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours
            iss: this.issuer,
            aud: this.audience
        };
        return jsonwebtoken_1.default.sign(fullPayload, secret, {
            algorithm: 'HS256'
        });
    }
    /**
     * Refresh JWKS cache
     */
    async refreshJWKS() {
        if (this.jwksUrl) {
            this.jwksCache.delete(this.jwksUrl);
            this.cacheExpiry.delete(this.jwksUrl);
            await this.fetchJWKS();
        }
    }
}
exports.JWTValidator = JWTValidator;
//# sourceMappingURL=jwt-validator.js.map