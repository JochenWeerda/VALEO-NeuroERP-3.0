/**
 * VALEO-NeuroERP-3.0 Configuration Management
 * Environment-based configuration with validation
 */

import { z } from 'zod';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Configuration schema validation
const configSchema = z.object({
  // Application
  environment: z.enum(['development', 'staging', 'production']).default('development'),
  host: z.string().default('0.0.0.0'),
  port: z.number().default(3000),

  // Database
  database: z.object({
    host: z.string().default('localhost'),
    port: z.number().default(5432),
    database: z.string().default('valeo_neuro_erp'),
    username: z.string().default('valeo_dev'),
    password: z.string(),
    ssl: z.boolean().default(false),
    maxConnections: z.number().default(20),
    idleTimeoutMillis: z.number().default(30000),
  }),

  // Redis
  redis: z.object({
    host: z.string().default('localhost'),
    port: z.number().default(6379),
    password: z.string().optional(),
    db: z.number().default(0),
  }),

  // JWT
  jwt: z.object({
    secret: z.string(),
    expiresIn: z.string().default('24h'),
    refreshExpiresIn: z.string().default('7d'),
  }),

  // External Services
  keycloak: z.object({
    url: z.string().default('http://localhost:8080'),
    realm: z.string().default('valeo-neuro-erp'),
    clientId: z.string().default('valeo-neuro-erp-backend'),
    clientSecret: z.string().optional(),
  }),

  // Logging
  logging: z.object({
    level: z.enum(['error', 'warn', 'info', 'debug']).default('info'),
    format: z.enum(['json', 'simple']).default('json'),
  }),

  // CORS
  cors: z.object({
    origin: z.union([z.string(), z.array(z.string())]).default('*'),
    credentials: z.boolean().default(true),
  }),

  // Rate Limiting
  rateLimit: z.object({
    windowMs: z.number().default(15 * 60 * 1000), // 15 minutes
    max: z.number().default(100), // limit each IP to 100 requests per windowMs
  }),
});

export type Config = z.infer<typeof configSchema>;

// Parse and validate configuration
export const config: Config = configSchema.parse({
  environment: process.env.NODE_ENV || 'development',
  host: process.env.HOST || '0.0.0.0',
  port: parseInt(process.env.PORT || '3000', 10),

  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432', 10),
    database: process.env.DB_NAME || 'valeo_neuro_erp',
    username: process.env.DB_USER || 'valeo_dev',
    password: process.env.DB_PASSWORD || 'valeo_dev_2024!',
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
    level: (process.env.LOG_LEVEL || 'info') as any,
    format: (process.env.LOG_FORMAT || 'json') as any,
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
export function validateConfig(): void {
  try {
    configSchema.parse(config);
    console.log('✅ Configuration validation successful');
  } catch (error) {
    console.error('❌ Configuration validation failed:', error);
    throw error;
  }
}

// Environment-specific configurations
export const isDevelopment = config.environment === 'development';
export const isStaging = config.environment === 'staging';
export const isProduction = config.environment === 'production';