import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = (__ENV.BASE_URL || '').replace(/\/+$/, '');

if (!baseUrl) {
  throw new Error('BASE_URL is required for the procurement performance test');
}

export const options = {
  scenarios: {
    health_under_load: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
    },
  },
  thresholds: {
    checks: ['rate==1'],
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

export default function procurementHealthUnderLoad() {
  const response = http.get(`${baseUrl}/health`, {
    tags: { endpoint: 'procurement-health' },
    timeout: '5s',
  });

  check(response, {
    'health endpoint returns HTTP 200': (result) => result.status === 200,
    'health response is JSON': (result) =>
      (result.headers['Content-Type'] || '').includes('application/json'),
  });

  sleep(0.2);
}
