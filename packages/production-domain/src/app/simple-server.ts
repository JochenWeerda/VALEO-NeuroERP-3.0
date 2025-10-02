/**
 * Simple Server for VALEO NeuroERP 3.0 Production Domain
 * Basic HTTP server for development and testing
 */

import { createServer } from 'http';

const PORT = Number(process.env.PORT || 3040);
const HOST = process.env.HOST || '0.0.0.0';

const server = createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Tenant-Id, X-Request-Id');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.url === '/health') {
    res.writeHead(200);
    res.end(JSON.stringify({ 
      status: 'ok', 
      service: 'production-domain',
      timestamp: new Date().toISOString() 
    }));
    return;
  }

  if (req.url === '/ready') {
    res.writeHead(200);
    res.end(JSON.stringify({ 
      status: 'ready', 
      database: true, 
      broker: true, 
      timestamp: new Date().toISOString() 
    }));
    return;
  }

  if (req.url === '/live') {
    res.writeHead(200);
    res.end(JSON.stringify({ 
      status: 'live', 
      timestamp: new Date().toISOString() 
    }));
    return;
  }

  if (req.url === '/production/api/v1/recipes') {
    res.writeHead(200);
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

  res.writeHead(200);
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
  console.log(`🚀 Starting VALEO NeuroERP 3.0 Production Domain Server...`);
  console.log(`✅ Production Domain Server running on http://${HOST}:${PORT}`);
  console.log(`❤️  Health Check: http://${HOST}:${PORT}/health`);
  console.log(`🔧 Ready Check: http://${HOST}:${PORT}/ready`);
  console.log(`💓 Live Check: http://${HOST}:${PORT}/live`);
  console.log(`📋 Recipe API: http://${HOST}:${PORT}/production/api/v1/recipes`);
});

server.on('error', (err) => {
  console.error('❌ Server error:', err);
  process.exit(1);
});

process.on('SIGTERM', () => {
  console.log('🔄 Gracefully shutting down...');
  server.close(() => {
    console.log('✅ Server shut down successfully');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('🔄 Gracefully shutting down...');
  server.close(() => {
    console.log('✅ Server shut down successfully');
    process.exit(0);
  });
});

