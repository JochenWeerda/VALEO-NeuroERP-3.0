const defaultPolicyBase = process.env.POLICY_BASE_URL ?? 'http://localhost:7070';
const policyEndpoint = `${defaultPolicyBase.replace(/\/+$/, '')}/api/mcp/policy`;

type JsonValue = unknown;

async function requestPolicy<TResponse>(
  path: string,
  init: RequestInit = {}
): Promise<TResponse> {
  const response = await fetch(`${policyEndpoint}/${path.replace(/^\/+/, '')}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => '');
    throw new Error(
      `Policy service returned ${response.status} ${response.statusText}${errorText.length > 0 ? `: ${errorText}` : ''}`
    );
  }

  return (await response.json()) as TResponse;
}

export async function listPolicies(): Promise<JsonValue> {
  return requestPolicy<JsonValue>('list', { method: 'GET' });
}

export async function upsertPolicies(body: JsonValue): Promise<JsonValue> {
  return requestPolicy<JsonValue>('upsert', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function deletePolicy(body: JsonValue): Promise<JsonValue> {
  return requestPolicy<JsonValue>('delete', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function testPolicy(body: JsonValue): Promise<JsonValue> {
  return requestPolicy<JsonValue>('test', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}
