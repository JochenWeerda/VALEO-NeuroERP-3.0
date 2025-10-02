"use strict";
// import Fastify from 'fastify';
// import cors from '@fastify/cors';
// import { initTRPC } from '@trpc/server';
// import * as trpcAdapter from '@trpc/server/adapters/fastify';
// import { JWTValidator } from '@valero-neuroerp/auth';
// import { RBACPolicy } from '@valero-neuroerp/auth';
// import { TenantContextManager } from '@valero-neuroerp/auth';
Object.defineProperty(exports, "__esModule", { value: true });
// Import route handlers
// import { dashboardRoutes } from './routes/dashboard';
// import { shipmentRoutes } from './routes/shipments';
// import { orderRoutes } from './routes/orders';
// import { inventoryRoutes } from './routes/inventory';
// Simple HTTP server for now
const http_1 = require("http");
// Initialize tRPC (commented out for now)
// const t = initTRPC.create();
// Create tRPC router (commented out for now)
// const appRouter = t.router({
//   health: t.procedure.query(() => ({ status: 'ok', timestamp: new Date().toISOString() })),
// });
// Export type for client
// export type AppRouter = typeof appRouter;
// Initialize services
// const jwtValidator = new JWTValidator({
//   issuer: process.env.JWT_ISSUER || 'valero-neuroerp',
//   audience: process.env.JWT_AUDIENCE || 'neuroerp-api'
// });
// const rbacPolicy = new RBACPolicy({
//   roles: [], // TODO: Load from configuration
//   permissions: [] // TODO: Load from configuration
// });
// const tenantContext = new TenantContextManager();
// Create simple HTTP server
const server = (0, http_1.createServer)((req, res) => {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    // Health check endpoint
    if (req.url === '/health' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            ok: true,
            service: 'bff-web',
            timestamp: new Date().toISOString(),
            uptime: process.uptime()
        }));
        return;
    }
    // Default response
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
        message: 'VALEO NeuroERP 3.0 - BFF-Web',
        version: '0.1.0',
        endpoints: {
            health: '/health',
            status: 'running'
        }
    }));
});
// Helper function to find an available port
function findAvailablePort(startPort) {
    return new Promise((resolve, reject) => {
        const server = require('http').createServer();
        server.listen(startPort, '0.0.0.0', () => {
            const port = server.address().port;
            server.close(() => resolve(port));
        });
        server.on('error', (error) => {
            if (error.code === 'EADDRINUSE') {
                // Try next port
                findAvailablePort(startPort + 1).then(resolve).catch(reject);
            }
            else {
                reject(error);
            }
        });
    });
}
// Start server function with better error handling
async function startServer() {
    const defaultPort = Number(process.env.PORT ?? 4001);
    const host = process.env.HOST ?? '0.0.0.0';
    try {
        // Try to find an available port starting from the default
        const port = await findAvailablePort(defaultPort);
        if (port !== defaultPort) {
            console.warn(`⚠️  Port ${defaultPort} is occupied, using port ${port} instead`);
            console.warn(`💡 To avoid this, ensure no other services are using port ${defaultPort}`);
            console.warn(`💡 Or set PORT environment variable to use a different port`);
        }
        server.listen(port, host, () => {
            console.log(`🚀 BFF-Web server running on http://${host}:${port}`);
            console.log(`❤️  Health check: http://${host}:${port}/health`);
            console.log(`📚 Service: VALEO NeuroERP 3.0 - BFF-Web v0.1.0`);
        });
        server.on('error', (error) => {
            if (error.code === 'EADDRINUSE') {
                console.error(`❌ Port ${port} is already in use`);
                console.error(`💡 Check if another instance is running:`);
                console.error(`   - Use 'netstat -ano | findstr :${port}' to find the process`);
                console.error(`   - Use 'taskkill /PID <PID> /F' to stop it`);
                console.error(`   - Or set PORT environment variable to use a different port`);
            }
            else {
                console.error('Failed to start server:', error.message);
            }
            process.exit(1);
        });
    }
    catch (error) {
        console.error('❌ Failed to start server:', error);
        console.error('💡 This might be due to port conflicts or insufficient permissions');
        process.exit(1);
    }
}
// Start the server
startServer();
//# sourceMappingURL=server.js.map