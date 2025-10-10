***REMOVED*** Load Tests

***REMOVED******REMOVED*** Prerequisites

Install k6:

```bash
***REMOVED*** Windows (Chocolatey)
choco install k6

***REMOVED*** macOS (Homebrew)
brew install k6

***REMOVED*** Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

***REMOVED******REMOVED*** Running Tests

***REMOVED******REMOVED******REMOVED*** API Load Test

```bash
***REMOVED*** Run against localhost
k6 run load-tests/api-load-test.js

***REMOVED*** Run against staging
k6 run --env BASE_URL=https://staging.erp.valeo.example.com load-tests/api-load-test.js

***REMOVED*** Run with custom token
k6 run --env API_TOKEN=your-token-here load-tests/api-load-test.js
```

***REMOVED******REMOVED******REMOVED*** SSE Load Test

```bash
***REMOVED*** Run against localhost
k6 run load-tests/sse-load-test.js

***REMOVED*** Run against staging
k6 run --env BASE_URL=https://staging.erp.valeo.example.com load-tests/sse-load-test.js
```

***REMOVED******REMOVED*** Test Scenarios

***REMOVED******REMOVED******REMOVED*** API Load Test

- **Duration:** 10 minutes
- **Users:** Ramps from 0 → 10 → 50 → 0
- **Requests:** ~50 req/s at peak
- **Thresholds:**
  - P95 latency < 500ms
  - Error rate < 5%
  - Failed requests < 1%

**Tests:**
1. Get orders list
2. Create new order
3. Get single order
4. Workflow transition

***REMOVED******REMOVED******REMOVED*** SSE Load Test

- **Duration:** 10.5 minutes
- **Connections:** Ramps from 0 → 100 → 500 → 1000 → 0
- **Thresholds:**
  - Error rate < 1%
  - At least 1000 messages received

**Tests:**
1. Connect to random SSE channel
2. Receive messages
3. Verify message format
4. Maintain connection for 5 minutes

***REMOVED******REMOVED*** Interpreting Results

***REMOVED******REMOVED******REMOVED*** Good Results

```
✓ http_req_duration..............: avg=250ms  min=50ms  med=200ms  max=800ms  p(90)=400ms p(95)=450ms
✓ errors.........................: 0.50%
✓ http_req_failed................: 0.10%
✓ sse_connections................: 1000
✓ sse_messages...................: 5000
✓ sse_errors.....................: 0.20%
```

***REMOVED******REMOVED******REMOVED*** Bad Results (Needs Investigation)

```
✗ http_req_duration..............: avg=1200ms  p(95)=2500ms  ← TOO SLOW
✗ errors.........................: 8.00%  ← TOO HIGH
✗ sse_errors.....................: 5.00%  ← TOO HIGH
```

***REMOVED******REMOVED*** CI/CD Integration

Add to `.github/workflows/load-test.yml`:

```yaml
name: Load Tests

on:
  schedule:
    - cron: '0 2 * * 0'  ***REMOVED*** Weekly on Sunday at 2 AM
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      
      - name: Run API load test
        run: |
          k6 run --env BASE_URL=https://staging.erp.valeo.example.com load-tests/api-load-test.js
      
      - name: Run SSE load test
        run: |
          k6 run --env BASE_URL=https://staging.erp.valeo.example.com load-tests/sse-load-test.js
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** High Latency

**Symptoms:** P95 > 500ms

**Possible Causes:**
- Database slow queries
- Resource limits (CPU/Memory)
- Network latency

**Solutions:**
1. Check database query performance
2. Scale up resources
3. Add caching
4. Optimize queries

***REMOVED******REMOVED******REMOVED*** High Error Rate

**Symptoms:** Errors > 5%

**Possible Causes:**
- Rate limiting triggered
- Database connection pool exhausted
- Application errors

**Solutions:**
1. Check application logs
2. Increase connection pool size
3. Fix application bugs
4. Adjust rate limits

***REMOVED******REMOVED******REMOVED*** SSE Connection Failures

**Symptoms:** SSE errors > 1%

**Possible Causes:**
- Load balancer timeout
- Pod restarts
- Network issues

**Solutions:**
1. Increase load balancer timeout
2. Check pod health
3. Verify network policies
4. Implement reconnection logic

