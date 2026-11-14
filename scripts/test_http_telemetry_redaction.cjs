// Exercise the HTTP instrumentation selected by auto-instrumentations-node.
process.env.OTEL_SEMCONV_STABILITY_OPT_IN = 'http';
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRequire } = require('node:module');
const fs = require('node:fs');
const path = require('node:path');
const runtime = process.env.SECURITY_NODE_RUNTIME
  ? path.resolve(process.env.SECURITY_NODE_RUNTIME)
  : path.resolve(__dirname, '../node_modules/.pnpm/node_modules');
const root = createRequire(path.join(runtime, 'package.json'));
const autoRequire = createRequire(root.resolve('@opentelemetry/auto-instrumentations-node'));
const entry = autoRequire.resolve('@opentelemetry/instrumentation-http');
const selected = createRequire(entry);
function packageVersion(entryPath) {
  let directory = path.dirname(entryPath);
  while (directory !== path.dirname(directory)) {
    const candidate = path.join(directory, 'package.json');
    if (fs.existsSync(candidate)) {
      const pkg = JSON.parse(fs.readFileSync(candidate, 'utf8'));
      if (pkg.name === '@opentelemetry/instrumentation-http') return pkg.version;
    }
    directory = path.dirname(directory);
  }
  throw new Error('Resolved HTTP instrumentation package manifest not found');
}
const api = selected('@opentelemetry/api');
const { HttpInstrumentation } = selected('@opentelemetry/instrumentation-http');
const sdkRequire = createRequire(root.resolve('@opentelemetry/sdk-node'));
const traceRequire = createRequire(sdkRequire.resolve('@opentelemetry/sdk-trace-node'));
const { BasicTracerProvider, SimpleSpanProcessor, InMemorySpanExporter } = traceRequire('@opentelemetry/sdk-trace-base');

test('incoming HTTP spans redact signature values and preserve ordinary query data', async () => {
  assert.equal(packageVersion(entry), '0.222.0');
  const exporter = new InMemorySpanExporter();
  const provider = new BasicTracerProvider({ spanProcessors: [new SimpleSpanProcessor(exporter)] });
  api.trace.setGlobalTracerProvider(provider);
  const instrumentation = new HttpInstrumentation();
  instrumentation.setTracerProvider(provider);
  instrumentation.enable();
  const http = require('node:http');
  const server = http.createServer((_request, response) => response.end('ok'));
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    await new Promise((resolve, reject) => {
      http.get(`http://127.0.0.1:${server.address().port}/download?X-Amz-Signature=secret&view=full`, response => {
        response.resume(); response.on('end', resolve);
      }).on('error', reject);
    });
    await provider.forceFlush();
    const serverSpan = exporter.getFinishedSpans().find(span => span.kind === api.SpanKind.SERVER);
    assert.ok(serverSpan, 'incoming server span must be emitted');
    const query = serverSpan.attributes['url.query'];
    assert.ok(query, 'stable HTTP query attribute must exist');
    assert.ok(!query.includes('secret'), `signature leaked: ${query}`);
    assert.match(query, /view=full/);
  } finally {
    await new Promise(resolve => server.close(resolve));
    instrumentation.disable();
    await provider.shutdown();
    api.trace.disable();
  }
});
