/**
 * Legacy authenticatedFetch wrapper.
 *
 * This bridges the old `authenticatedFetch(url, init)` calls to the central
 * `apiClient` (Axios-based).  New code should import `apiClient` directly
 * from `@/lib/api-client` instead.
 *
 * @deprecated Use `apiClient` from `@/lib/api-client` instead.
 */

import { apiClient } from './api-client'

/**
 * Drop-in replacement for `fetch()` that routes through apiClient so that
 * auth tokens, interceptors and base-URL are applied consistently.
 *
 * Returns a minimal Response-like object so existing callers keep working.
 */
export async function authenticatedFetch(
  url: string,
  init?: RequestInit,
): Promise<Response> {
  const method = (init?.method ?? 'GET').toUpperCase()
  const headers: Record<string, string> = {}

  if (init?.headers) {
    const h = init.headers
    if (h instanceof Headers) {
      h.forEach((v, k) => { headers[k] = v })
    } else if (Array.isArray(h)) {
      h.forEach(([k, v]) => { headers[k] = v })
    } else {
      Object.assign(headers, h)
    }
  }

  let body: unknown = undefined
  if (init?.body) {
    try {
      body = JSON.parse(init.body as string)
    } catch {
      body = init.body
    }
  }

  try {
    let response
    switch (method) {
      case 'POST':
        response = await apiClient.post(url, body, { headers })
        break
      case 'PUT':
        response = await apiClient.put(url, body, { headers })
        break
      case 'PATCH':
        response = await apiClient.patch(url, body, { headers })
        break
      case 'DELETE':
        response = await apiClient.delete(url, { headers })
        break
      default:
        response = await apiClient.get(url, { headers })
    }

    // Return a Response-like object for backwards compatibility
    const data = response.data
    return {
      ok: response.status >= 200 && response.status < 300,
      status: response.status,
      statusText: response.statusText,
      headers: new Headers(response.headers as Record<string, string>),
      json: async () => data,
      text: async () => (typeof data === 'string' ? data : JSON.stringify(data)),
      clone: () => ({ json: async () => data } as unknown as Response),
    } as Response
  } catch (error: unknown) {
    // Axios throws on non-2xx – map to a failed Response
    const axiosError = error as { response?: { status: number; statusText: string; data: unknown } }
    if (axiosError.response) {
      const responseData = axiosError.response.data
      return {
        ok: false,
        status: axiosError.response.status,
        statusText: axiosError.response.statusText,
        headers: new Headers(),
        json: async () => responseData,
        text: async () => JSON.stringify(responseData),
        clone: () => ({ json: async () => responseData } as unknown as Response),
      } as Response
    }
    // Network error
    return {
      ok: false,
      status: 0,
      statusText: 'Network Error',
      headers: new Headers(),
      json: async () => ({}),
      text: async () => '',
      clone: () => ({ json: async () => ({}) } as unknown as Response),
    } as Response
  }
}

