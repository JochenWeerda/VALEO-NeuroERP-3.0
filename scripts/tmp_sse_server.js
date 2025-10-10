const http = require('http');
const url = require('url');

const PORT = process.env.SSE_PORT ? Number(process.env.SSE_PORT) : 5000;
const clients = new Set();
const heartbeats = new Map();

function send(res, event, data) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  res.write(payload);
}

function broadcast(event, data) {
  for (const res of clients) {
    send(res, event, data);
  }
}

const server = http.createServer((req, res) => {
  if (req.method === 'HEAD') {
    res.writeHead(200, { 'Access-Control-Allow-Origin': '*' });
    res.end();
    return;
  }
  const parsed = url.parse(req.url, true);
  if (parsed.pathname === '/sse') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
      'Access-Control-Allow-Origin': '*',
    });

    res.write('retry: 1000\n\n');

    clients.add(res);
    send(res, 'pipeline_status', { phase: 'init', progress: 5, status: 'booting' });

    const interval = setInterval(() => {
      if (clients.has(res)) {
        send(res, 'heartbeat', { time: Date.now() });
      }
    }, 1000);
    heartbeats.set(res, interval);

    req.on('close', () => {
      clients.delete(res);
      const hb = heartbeats.get(res);
      if (hb) {
        clearInterval(hb);
        heartbeats.delete(res);
      }
    });
    return;
  }

  if (parsed.pathname === '/emit') {
    const { type = 'message', service = 'general' } = parsed.query;
    const payload = {
      service,
      eventType: type,
      timestamp: Date.now(),
      payload: parsed.query.payload ? JSON.parse(parsed.query.payload) : {},
    };
    broadcast(type, payload);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true }));
    return;
  }

  if (parsed.pathname === '/trigger-sequence') {
    const events = [
      () => broadcast('inventory.created', { service: 'inventory', eventType: 'inventory.created', sku: 'SKU-100', qty: 4 }),
      () => broadcast('inventory.adjusted', { service: 'inventory', eventType: 'inventory.adjusted', sku: 'SKU-100', qty: 6 }),
      () => broadcast('weighing.updated', { service: 'weighing', eventType: 'weighing.updated', ticketId: 'WT-42' }),
    ];
    events.forEach((fn, index) => {
      setTimeout(fn, (index + 1) * 500);
    });
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true, events: events.length }));
    return;
  }

  res.writeHead(404);
  res.end();
});

server.listen(PORT, () => {
  console.log(`SSE server listening on http://localhost:${PORT}/sse`);
  setTimeout(() => {
    broadcast('inventory.created', { service: 'inventory', eventType: 'inventory.created', sku: 'SKU-001', qty: 10 });
  }, 1000);
});

process.on('SIGINT', () => {
  server.close(() => {
    console.log('SSE server stopped');
    process.exit(0);
  });
});


