/**
 * Simple Server for VALEO NeuroERP 3.0 Production Domain
 * Basic HTTP server for development and testing
 */

import { createServer } from 'http';

const DEFAULT_PORT = 3040;
const DEFAULT_HOST = '0.0.0.0';
const PORT = Number(process.env.PORT ?? DEFAULT_PORT);
const HOST = process.env.HOST ?? DEFAULT_HOST;

const HTTP_OK = 200;

const server = createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Tenant-Id, X-Request-Id');

  if (req.method === 'OPTIONS') {
    res.writeHead(HTTP_OK);
    res.end();
    return;
  }

  if (req.url === '/health') {
    res.writeHead(HTTP_OK);
    res.end(JSON.stringify({ 
      status: 'ok', 
      service: 'production-domain',
      timestamp: new Date().toISOString() 
    }));
    return;
  }

  if (req.url === '/ready') {
    res.writeHead(HTTP_OK);
    res.end(JSON.stringify({ 
      status: 'ready', 
      database: true, 
      broker: true, 
      timestamp: new Date().toISOString() 
    }));
    return;
  }

  if (req.url === '/live') {
    res.writeHead(HTTP_OK);
    res.end(JSON.stringify({ 
      status: 'live', 
      timestamp: new Date().toISOString() 
    }));
    return;
  }

  if (req.url === '/production/api/v1/recipes') {
    res.writeHead(HTTP_OK);
    res.end(JSON.stringify({ 
      message: 'Production Domain - Recipe Management', 
      version: '0.1.0',
      features: [
        'Recipe Management',
        'Mix Order Processing', 
        'Batch Tracking',
        'Mobile Production',
        'Quality Control',
        'GMP+/QS Compliance',
        'Traceability'
      ]
    }));
    return;
  }

  res.writeHead(HTTP_OK);
  res.end(JSON.stringify({ 
    message: 'VALEO NeuroERP 3.0 - Production Domain', 
    version: '0.1.0',
    description: 'Mobile Milling & Mixing with GMP+/QS Compliance',
    endpoints: {
      health: '/health',
      ready: '/ready', 
      live: '/live',
      recipes: '/production/api/v1/recipes'
    }
  }));
});

server.listen(PORT, HOST, () => {
  // eslint-disable-next-line no-console
  console.log(`🚀 Starting VALEO NeuroERP 3.0 Production Domain Server...`);
  // eslint-disable-next-line no-console
  console.log(`✅ Production Domain Server running on http://${HOST}:${PORT}`);
  // eslint-disable-next-line no-console
  console.log(`❤️  Health Check: http://${HOST}:${PORT}/health`);
  // eslint-disable-next-line no-console
  console.log(`🔧 Ready Check: http://${HOST}:${PORT}/ready`);
  // eslint-disable-next-line no-console
  console.log(`💓 Live Check: http://${HOST}:${PORT}/live`);
  // eslint-disable-next-line no-console
  console.log(`📋 Recipe API: http://${HOST}:${PORT}/production/api/v1/recipes`);
});

server.on('error', (err) => {
  // eslint-disable-next-line no-console
  console.error('❌ Server error:', err);
  process.exit(1);
});

process.on('SIGTERM', () => {
  // eslint-disable-next-line no-console
  console.log('🔄 Gracefully shutting down...');
  server.close(() => {
    // eslint-disable-next-line no-console
    console.log('✅ Server shut down successfully');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  // eslint-disable-next-line no-console
  console.log('🔄 Gracefully shutting down...');
  server.close(() => {
    // eslint-disable-next-line no-console
    console.log('✅ Server shut down successfully');
    process.exit(0);
  });
});

