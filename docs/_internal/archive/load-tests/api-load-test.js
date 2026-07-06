import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 users
    { duration: '3m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '1m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'],  // 95% of requests must complete below 500ms
    'errors': ['rate<0.05'],              // Error rate must be below 5%
    'http_req_failed': ['rate<0.01'],     // Failed requests must be below 1%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.API_TOKEN || 'test-token';

export function setup() {
  // Login and get token
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    username: 'test-operator',
    password: 'test-password',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });

  const token = loginRes.json('access_token') || TOKEN;
  return { token };
}

export default function (data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  // Test 1: Get orders list
  let res = http.get(`${BASE_URL}/api/documents/sales`, { headers });
  check(res, {
    'get orders status 200': (r) => r.status === 200,
    'get orders duration < 500ms': (r) => r.timings.duration < 500,
  });
  errorRate.add(res.status !== 200);
  apiDuration.add(res.timings.duration);

  sleep(1);

  // Test 2: Create new order
  const newOrder = {
    customer: 'ACME Corp',
    date: new Date().toISOString().split('T')[0],
    lines: [
      { sku: 'SKU-001', description: 'Test Product', quantity: 10, unit_price: 50.00 },
    ],
  };

  res = http.post(`${BASE_URL}/api/documents/sales`, JSON.stringify(newOrder), { headers });
  check(res, {
    'create order status 200': (r) => r.status === 200 || r.status === 201,
    'create order duration < 1000ms': (r) => r.timings.duration < 1000,
  });
  errorRate.add(res.status !== 200 && res.status !== 201);
  apiDuration.add(res.timings.duration);

  const orderId = res.json('id');

  sleep(1);

  // Test 3: Get single order
  if (orderId) {
    res = http.get(`${BASE_URL}/api/documents/sales/${orderId}`, { headers });
    check(res, {
      'get order status 200': (r) => r.status === 200,
      'get order duration < 300ms': (r) => r.timings.duration < 300,
    });
    errorRate.add(res.status !== 200);
    apiDuration.add(res.timings.duration);
  }

  sleep(1);

  // Test 4: Workflow transition
  if (orderId) {
    res = http.post(
      `${BASE_URL}/api/workflow/sales/${orderId}/transition`,
      JSON.stringify({ action: 'submit' }),
      { headers }
    );
    check(res, {
      'workflow transition status 200': (r) => r.status === 200,
      'workflow transition duration < 500ms': (r) => r.timings.duration < 500,
    });
    errorRate.add(res.status !== 200);
    apiDuration.add(res.timings.duration);
  }

  sleep(2);
}

export function teardown(data) {
  console.log('Load test completed');
}

