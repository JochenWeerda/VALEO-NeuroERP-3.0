import { type IncomingMessage, type ServerResponse, createServer } from 'http';
import { getKpis, getTrends } from './services/analytics';
import { listInventory } from './services/inventory';
import { listContracts } from './services/contracts';
import { listPriceItems } from './services/pricing';
import { listSalesOrders } from './services/sales';
import { listWeighingTickets } from './services/weighing';

const httpStatusOk = 200;
const httpStatusOptions = 200;
const httpStatusMethodNotAllowed = 405;
const httpStatusBadRequest = 400;
const httpStatusInternalServerError = 500;
const defaultPort = 4001;
const defaultHost = '0.0.0.0';
const minUrlSegments = 4;
const actionSegmentIndex = 3;

const logger = {
  info: (message: string): void => {
    console.log(`[INFO] ${message}`);
  },
  warn: (message: string): void => {
    console.warn(`[WARN] ${message}`);
  },
  error: (message: string): void => {
    console.error(`[ERROR] ${message}`);
  }
};

interface McpResponse<T> {
  ok: boolean;
  data?: T;
  error?: string;
}

const emptyList = { data: [] };

function sendJson<T>(res: ServerResponse, statusCode: number, payload: McpResponse<T>): void {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(payload));
}

async function collectRequestBody(req: IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];

    req.on('data', (chunk: Buffer) => {
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
      } catch {
        resolve(raw);
      }
    });

    req.on('error', (error) => {
      reject(error);
    });
  });
}

async function handleMcpRequest(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const method = (req.method ?? 'GET').toUpperCase();
  if (!['GET', 'POST'].includes(method)) {
    sendJson(res, httpStatusMethodNotAllowed, { ok: false, error: 'Method not allowed' });
    return;
  }

  const url = req.url ?? '';
  const segments = url.split('/').filter(Boolean);
  if (segments.length < minUrlSegments) {
    sendJson(res, httpStatusBadRequest, { ok: false, error: 'Invalid MCP request' });
    return;
  }

  const service = segments[2];
  const action = segments.slice(actionSegmentIndex).join('/');

  if (method === 'POST') {
    try {
      await collectRequestBody(req);
    } catch (error) {
      logger.warn(`Failed to read request body: ${(error as Error).message}`);
    }
  }

  try {
    let responseData: unknown;
    switch (`${service}:${action}`) {
      case 'analytics:kpis':
        responseData = { data: await getKpis() };
        break;
      case 'analytics:trends':
        responseData = { data: await getTrends() };
        break;
      case 'inventory:list':
        responseData = { data: await listInventory() };
        break;
      case 'contracts:list':
        responseData = { data: await listContracts() };
        break;
      case 'pricing:list':
        responseData = { data: await listPriceItems() };
        break;
      case 'sales:list':
        responseData = { data: await listSalesOrders() };
        break;
      case 'weighing:list':
        responseData = { data: await listWeighingTickets() };
        break;
      default:
        responseData = emptyList;
    }
    sendJson(res, httpStatusOk, { ok: true, data: responseData });
  } catch (error) {
    logger.error(`Failed to handle MCP request: ${(error as Error).message}`);
    sendJson(res, httpStatusInternalServerError, { ok: false, error: 'Internal server error' });
  }
}

const server = createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.writeHead(httpStatusOptions);
    res.end();
    return;
  }

  if (req.url?.startsWith('/api/mcp/') ?? false) {
    handleMcpRequest(req, res).catch((error: Error) => {
      logger.error(`Failed to handle MCP request: ${error.message}`);
      sendJson(res, httpStatusInternalServerError, { ok: false, error: 'Internal server error' });
    });
    return;
  }

  if (req.url === '/health' && req.method === 'GET') {
    sendJson(res, httpStatusOk, {
      ok: true,
      data: {
        service: 'bff-web',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
      }
    });
    return;
  }

  sendJson(res, httpStatusOk, {
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

async function findAvailablePort(startPort: number): Promise<number> {
  return new Promise((resolve, reject) => {
    const testServer = createServer();

    testServer.listen(startPort, defaultHost, () => {
      const address = testServer.address();
      const port =
        typeof address === 'string'
          ? parseInt(address.split(':').pop() ?? '0', 10)
          : (address as { port: number }).port;
      testServer.close(() => resolve(port));
    });

    testServer.on('error', (error: Error & { code?: string }) => {
      if (error.code === 'EADDRINUSE') {
        findAvailablePort(startPort + 1).then(resolve).catch(reject);
      } else {
        reject(error);
      }
    });
  });
}

async function startServer(): Promise<void> {
  const portEnv = process.env.PORT;
  const desiredPort = typeof portEnv === 'string' && portEnv.trim().length > 0 ? Number(portEnv) : defaultPort;
  const hostEnv = process.env.HOST;
  const host = hostEnv ?? defaultHost;

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

    server.on('error', (error: Error & { code?: string }) => {
      if (error.code === 'EADDRINUSE') {
        logger.error(`Port ${port} is already in use`);
        logger.error(`Use 'netstat -ano | findstr :${port}' to find the process.`);
      } else {
        const message = typeof error.message === 'string' && error.message.trim().length > 0 ? error.message : 'Unknown error';
        logger.error(`Failed to start server: ${message}`);
      }
      process.exit(1);
    });
  } catch (error) {
    logger.error(`Failed to start server: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

startServer().catch((error) => {
  logger.error(`Failed to start server: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
