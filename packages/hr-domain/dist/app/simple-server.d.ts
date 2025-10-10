/**
 * Simple HR Domain Server for VALEO NeuroERP 3.0
 * Simplified version without complex Fastify types
 */
import pino from 'pino';
declare const fastify: import("fastify").FastifyInstance<import("http").Server<typeof import("http").IncomingMessage, typeof import("http").ServerResponse>, import("http").IncomingMessage, import("http").ServerResponse<import("http").IncomingMessage>, pino.Logger<never, boolean>, import("fastify").FastifyTypeProviderDefault> & PromiseLike<import("fastify").FastifyInstance<import("http").Server<typeof import("http").IncomingMessage, typeof import("http").ServerResponse>, import("http").IncomingMessage, import("http").ServerResponse<import("http").IncomingMessage>, pino.Logger<never, boolean>, import("fastify").FastifyTypeProviderDefault>>;
export default fastify;
//# sourceMappingURL=simple-server.d.ts.map