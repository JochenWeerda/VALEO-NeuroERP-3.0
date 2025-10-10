"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const http_1 = require("http");
const analytics_1 = require("./services/analytics");
const inventory_1 = require("./services/inventory");
const contracts_1 = require("./services/contracts");
const pricing_1 = require("./services/pricing");
const sales_1 = require("./services/sales");
const weighing_1 = require("./services/weighing");
const HTTP_STATUS_OK = 200;
const HTTP_STATUS_OPTIONS = 200;
const DEFAULT_PORT = 4001;
const DEFAULT_HOST = '0.0.0.0';
const logger = {
    info: (message) => {
        console.log(`[INFO] ${message}`);
    },
    warn: (message) => {
        console.warn(`[WARN] ${message}`);
    },
    error: (message) => {
        console.error(`[ERROR] ${message}`);
    }
};
const EMPTY_LIST = { data: [] };
function sendJson(res, statusCode, payload) {
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(payload));
}
function collectRequestBody(req) {
    return new Promise((resolve, reject) => {
        const chunks = [];
        req.on('data', (chunk) => {
            chunks.push(chunk);
        });
        req.on('end', () => {
            if (chunks.length === 0) {
                resolve(undefined);
                return;
            }
            const raw = Buffer.concat(chunks).toString('utf-8');
            try {
                resolve(JSON.parse(raw));
            }
            catch {
                resolve(raw);
            }
        });
        req.on('error', (error) => {
            reject(error);
        });
    });
}
async function handleMcpRequest(req, res) {
    const method = (req.method ?? 'GET').toUpperCase();
    if (!['GET', 'POST'].includes(method)) {
        sendJson(res, 405, { ok: false, error: 'Method not allowed' });
        return;
    }
    const url = req.url ?? '';
    const segments = url.split('/').filter(Boolean);
    if (segments.length < 4) {
        sendJson(res, 400, { ok: false, error: 'Invalid MCP request' });
        return;
    }
    const service = segments[2];
    const action = segments.slice(3).join('/');
    if (method === 'POST') {
        try {
            await collectRequestBody(req);
        }
        catch (error) {
            logger.warn(`Failed to read request body: ${error.message}`);
        }
    }
    try {
        let responseData;
        switch (`${service}:${action}`) {
            case 'analytics:kpis':
                responseData = { data: await (0, analytics_1.getKpis)() };
                break;
            case 'analytics:trends':
                responseData = { data: await (0, analytics_1.getTrends)() };
                break;
            case 'inventory:list':
                responseData = { data: await (0, inventory_1.listInventory)() };
                break;
            case 'contracts:list':
                responseData = { data: await (0, contracts_1.listContracts)() };
                break;
            case 'pricing:list':
                responseData = { data: await (0, pricing_1.listPriceItems)() };
                break;
            case 'sales:list':
                responseData = { data: await (0, sales_1.listSalesOrders)() };
                break;
            case 'weighing:list':
                responseData = { data: await (0, weighing_1.listWeighingTickets)() };
                break;
            default:
                responseData = EMPTY_LIST;
        }
        sendJson(res, HTTP_STATUS_OK, { ok: true, data: responseData });
    }
    catch (error) {
        logger.error(`Failed to handle MCP request: ${error.message}`);
        sendJson(res, 500, { ok: false, error: 'Internal server error' });
    }
}
const server = (0, http_1.createServer)((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    if (req.method === 'OPTIONS') {
        res.writeHead(HTTP_STATUS_OPTIONS);
        res.end();
        return;
    }
    if (req.url?.startsWith('/api/mcp/')) {
        void handleMcpRequest(req, res).catch((error) => {
            logger.error(`Failed to handle MCP request: ${error.message}`);
            sendJson(res, 500, { ok: false, error: 'Internal server error' });
        });
        return;
    }
    if (req.url === '/health' && req.method === 'GET') {
        sendJson(res, HTTP_STATUS_OK, {
            ok: true,
            data: {
                service: 'bff-web',
                timestamp: new Date().toISOString(),
                uptime: process.uptime()
            }
        });
        return;
    }
    sendJson(res, HTTP_STATUS_OK, {
        ok: true,
        data: {
            message: 'VALEO NeuroERP 3.0 - BFF-Web',
            version: '0.1.0',
            endpoints: {
                health: '/health',
                status: 'running'
            }
        }
    });
});
async function findAvailablePort(startPort) {
    return new Promise((resolve, reject) => {
        const testServer = (0, http_1.createServer)();
        testServer.listen(startPort, DEFAULT_HOST, () => {
            const address = testServer.address();
            const port = typeof address === 'string'
                ? parseInt(address.split(':').pop() ?? '0', 10)
                : address.port;
            testServer.close(() => resolve(port));
        });
        testServer.on('error', (error) => {
            if (error.code === 'EADDRINUSE') {
                findAvailablePort(startPort + 1).then(resolve).catch(reject);
            }
            else {
                reject(error);
            }
        });
    });
}
async function startServer() {
    const portEnv = process.env.PORT;
    const desiredPort = portEnv ? Number(portEnv) : DEFAULT_PORT;
    const hostEnv = process.env.HOST;
    const host = hostEnv ?? DEFAULT_HOST;
    try {
        const port = await findAvailablePort(desiredPort);
        if (port !== desiredPort) {
            logger.warn(`Port ${desiredPort} is occupied, using port ${port} instead`);
            logger.warn('Set PORT environment variable to force a different port.');
        }
        server.listen(port, host, () => {
            logger.info(`BFF-Web server running on http://${host}:${port}`);
            logger.info(`Health check: http://${host}:${port}/health`);
            logger.info('Serving sample responses for MCP endpoints.');
        });
        server.on('error', (error) => {
            if (error.code === 'EADDRINUSE') {
                logger.error(`Port ${port} is already in use`);
                logger.error(`Use 'netstat -ano | findstr :${port}' to find the process.`);
            }
            else {
                const message = error.message?.length ? error.message : 'Unknown error';
                logger.error(`Failed to start server: ${message}`);
            }
            process.exit(1);
        });
    }
    catch (error) {
        logger.error(`Failed to start server: ${error instanceof Error ? error.message : String(error)}`);
        process.exit(1);
    }
}
startServer().catch((error) => {
    logger.error(`Failed to start server: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
});
//# sourceMappingURL=server.js.map