/**
 * API-Client mit automatischer Token-Injection
 * Handles token refresh und 401-Errors
 */

import { auth } from './auth'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'

interface RequestOptions extends RequestInit {
  method?: HttpMethod
}

export class APIClient {
  private readonly baseUrl: string

  private static readonly HTTP_STATUS_UNAUTHORIZED = 401

  constructor(baseUrl?: string) {
    const envBaseUrl = import.meta.env.VITE_API_BASE_URL
    this.baseUrl = baseUrl ?? envBaseUrl ?? 'http://localhost:8000'
  }

  async fetch(endpoint: string, options: RequestOptions = {}): Promise<Response> {
    const token = auth.getAccessToken()
    const headers = new Headers(options.headers)

    if (typeof token === 'string') {
      headers.set('Authorization', `Bearer ${token}`)
    }

    if (options.body != null && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json')
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    })

    if (response.status === APIClient.HTTP_STATUS_UNAUTHORIZED) {
      const refreshed = await auth.refreshAccessToken()
      if (!refreshed) {
        auth.logout()
        window.location.href = '/login'
        throw new Error('Session expired. Please login again.')
      }

      const newToken = auth.getAccessToken()
      if (typeof newToken === 'string') {
        headers.set('Authorization', `Bearer ${newToken}`)
      }

      return fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers,
      })
    }

    return response
  }

  async get<T = unknown>(endpoint: string): Promise<T> {
    const response = await this.fetch(endpoint, { method: 'GET' })
    if (!response.ok) {
      throw new Error(`GET ${endpoint} failed: ${response.status}`)
    }
    return (await response.json()) as T
  }

  async post<T = unknown>(endpoint: string, data?: unknown): Promise<T> {
    const response = await this.fetch(endpoint, {
      method: 'POST',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    })
    if (!response.ok) {
      throw new Error(`POST ${endpoint} failed: ${response.status}`)
    }
    return (await response.json()) as T
  }

  async put<T = unknown>(endpoint: string, data?: unknown): Promise<T> {
    const response = await this.fetch(endpoint, {
      method: 'PUT',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    })
    if (!response.ok) {
      throw new Error(`PUT ${endpoint} failed: ${response.status}`)
    }
    return (await response.json()) as T
  }

  async delete<T = unknown>(endpoint: string): Promise<T> {
    const response = await this.fetch(endpoint, { method: 'DELETE' })
    if (!response.ok) {
      throw new Error(`DELETE ${endpoint} failed: ${response.status}`)
    }
    return (await response.json()) as T
  }
}

export const apiClient = new APIClient()
