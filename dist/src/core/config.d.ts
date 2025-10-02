/**
 * VALEO-NeuroERP-3.0 Configuration Management
 * Environment-based configuration with validation
 */
import { z } from 'zod';
declare const configSchema: z.ZodObject<{
    environment: z.ZodDefault<z.ZodEnum<{
        development: "development";
        staging: "staging";
        production: "production";
    }>>;
    host: z.ZodDefault<z.ZodString>;
    port: z.ZodDefault<z.ZodNumber>;
    database: z.ZodObject<{
        host: z.ZodDefault<z.ZodString>;
        port: z.ZodDefault<z.ZodNumber>;
        database: z.ZodDefault<z.ZodString>;
        username: z.ZodDefault<z.ZodString>;
        password: z.ZodString;
        ssl: z.ZodDefault<z.ZodBoolean>;
        maxConnections: z.ZodDefault<z.ZodNumber>;
        idleTimeoutMillis: z.ZodDefault<z.ZodNumber>;
    }, z.core.$strip>;
    redis: z.ZodObject<{
        host: z.ZodDefault<z.ZodString>;
        port: z.ZodDefault<z.ZodNumber>;
        password: z.ZodOptional<z.ZodString>;
        db: z.ZodDefault<z.ZodNumber>;
    }, z.core.$strip>;
    jwt: z.ZodObject<{
        secret: z.ZodString;
        expiresIn: z.ZodDefault<z.ZodString>;
        refreshExpiresIn: z.ZodDefault<z.ZodString>;
    }, z.core.$strip>;
    keycloak: z.ZodObject<{
        url: z.ZodDefault<z.ZodString>;
        realm: z.ZodDefault<z.ZodString>;
        clientId: z.ZodDefault<z.ZodString>;
        clientSecret: z.ZodOptional<z.ZodString>;
    }, z.core.$strip>;
    logging: z.ZodObject<{
        level: z.ZodDefault<z.ZodEnum<{
            error: "error";
            warn: "warn";
            info: "info";
            debug: "debug";
        }>>;
        format: z.ZodDefault<z.ZodEnum<{
            json: "json";
            simple: "simple";
        }>>;
    }, z.core.$strip>;
    cors: z.ZodObject<{
        origin: z.ZodDefault<z.ZodUnion<readonly [z.ZodString, z.ZodArray<z.ZodString>]>>;
        credentials: z.ZodDefault<z.ZodBoolean>;
    }, z.core.$strip>;
    rateLimit: z.ZodObject<{
        windowMs: z.ZodDefault<z.ZodNumber>;
        max: z.ZodDefault<z.ZodNumber>;
    }, z.core.$strip>;
}, z.core.$strip>;
export type Config = z.infer<typeof configSchema>;
export declare const config: Config;
export declare function validateConfig(): void;
export declare const isDevelopment: boolean;
export declare const isStaging: boolean;
export declare const isProduction: boolean;
export {};
//***REMOVED*** sourceMappingURL=config.d.ts.map