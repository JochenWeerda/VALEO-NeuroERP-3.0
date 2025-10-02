"use strict";
/**
 * VALEO-NeuroERP-3.0 Configuration Management
 * Environment-based configuration with validation
 */
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
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.isProduction = exports.isStaging = exports.isDevelopment = exports.config = void 0;
exports.validateConfig = validateConfig;
const zod_1 = require("zod");
const dotenv = __importStar(require("dotenv"));
// Load environment variables
dotenv.config();
// Configuration schema validation
const configSchema = zod_1.z.object({
    // Application
    environment: zod_1.z.enum(['development', 'staging', 'production']).default('development'),
    host: zod_1.z.string().default('0.0.0.0'),
    port: zod_1.z.number().default(3000),
    // Database
    database: zod_1.z.object({
        host: zod_1.z.string().default('localhost'),
        port: zod_1.z.number().default(5432),
        database: zod_1.z.string().default('valeo_neuro_erp'),
        username: zod_1.z.string().default('valeo_dev'),
        password: zod_1.z.string(),
        ssl: zod_1.z.boolean().default(false),
        maxConnections: zod_1.z.number().default(20),
        idleTimeoutMillis: zod_1.z.number().default(30000),
    }),
    // Redis
    redis: zod_1.z.object({
        host: zod_1.z.string().default('localhost'),
        port: zod_1.z.number().default(6379),
        password: zod_1.z.string().optional(),
        db: zod_1.z.number().default(0),
    }),
    // JWT
    jwt: zod_1.z.object({
        secret: zod_1.z.string(),
        expiresIn: zod_1.z.string().default('24h'),
        refreshExpiresIn: zod_1.z.string().default('7d'),
    }),
    // External Services
    keycloak: zod_1.z.object({
        url: zod_1.z.string().default('http://localhost:8080'),
        realm: zod_1.z.string().default('valeo-neuro-erp'),
        clientId: zod_1.z.string().default('valeo-neuro-erp-backend'),
        clientSecret: zod_1.z.string().optional(),
    }),
    // Logging
    logging: zod_1.z.object({
        level: zod_1.z.enum(['error', 'warn', 'info', 'debug']).default('info'),
        format: zod_1.z.enum(['json', 'simple']).default('json'),
    }),
    // CORS
    cors: zod_1.z.object({
        origin: zod_1.z.union([zod_1.z.string(), zod_1.z.array(zod_1.z.string())]).default('*'),
        credentials: zod_1.z.boolean().default(true),
    }),
    // Rate Limiting
    rateLimit: zod_1.z.object({
        windowMs: zod_1.z.number().default(15 * 60 * 1000), // 15 minutes
        max: zod_1.z.number().default(100), // limit each IP to 100 requests per windowMs
    }),
});
// Parse and validate configuration
exports.config = configSchema.parse({
    environment: process.env.NODE_ENV || 'development',
    host: process.env.HOST || '0.0.0.0',
    port: parseInt(process.env.PORT || '3000', 10),
    database: {
        host: process.env.DB_HOST || 'localhost',
        port: parseInt(process.env.DB_PORT || '5432', 10),
        database: process.env.DB_NAME || 'valeo_neuro_erp',
        username: process.env.DB_USER || 'valeo_dev',
        password: process.env.DB_PASSWORD || 'REDACTED_PASSWORD',
        ssl: process.env.DB_SSL === 'true',
        maxConnections: parseInt(process.env.DB_MAX_CONNECTIONS || '20', 10),
        idleTimeoutMillis: parseInt(process.env.DB_IDLE_TIMEOUT || '30000', 10),
    },
    redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379', 10),
        password: process.env.REDIS_PASSWORD,
        db: parseInt(process.env.REDIS_DB || '0', 10),
    },
    jwt: {
        secret: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
        expiresIn: process.env.JWT_EXPIRES_IN || '24h',
        refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
    },
    keycloak: {
        url: process.env.KEYCLOAK_URL || 'http://localhost:8080',
        realm: process.env.KEYCLOAK_REALM || 'valeo-neuro-erp',
        clientId: process.env.KEYCLOAK_CLIENT_ID || 'valeo-neuro-erp-backend',
        clientSecret: process.env.KEYCLOAK_CLIENT_SECRET,
    },
    logging: {
        level: (process.env.LOG_LEVEL || 'info'),
        format: (process.env.LOG_FORMAT || 'json'),
    },
    cors: {
        origin: process.env.CORS_ORIGIN ? process.env.CORS_ORIGIN.split(',') : '*',
        credentials: process.env.CORS_CREDENTIALS === 'true',
    },
    rateLimit: {
        windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000', 10),
        max: parseInt(process.env.RATE_LIMIT_MAX || '100', 10),
    },
});
// Configuration validation
function validateConfig() {
    try {
        configSchema.parse(exports.config);
        console.log('✅ Configuration validation successful');
    }
    catch (error) {
        console.error('❌ Configuration validation failed:', error);
        throw error;
    }
}
// Environment-specific configurations
exports.isDevelopment = exports.config.environment === 'development';
exports.isStaging = exports.config.environment === 'staging';
exports.isProduction = exports.config.environment === 'production';
