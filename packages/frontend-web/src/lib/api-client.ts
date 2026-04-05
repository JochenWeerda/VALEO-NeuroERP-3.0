/**
 * API Client
 * Axios-basierter HTTP-Client mit Interceptors
 */
import axios, { type AxiosInstance, type AxiosResponse, isAxiosError } from 'axios'
import { auth } from './auth'

const DEV_TOKEN = import.meta.env.VITE_API_DEV_TOKEN as string | undefined || 'dev-token'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const DEFAULT_TENANT_ID = import.meta.env.VITE_TENANT_ID || '00000000-0000-0000-0000-000000000001'

export type ApiResult<T> = T & {
  data: T
  ok: boolean
  httpStatus: number
  statusText: string
  headers: AxiosResponse['headers']
  response: AxiosResponse<T>
}

function wrapResponseData<T>(response: AxiosResponse<T>): ApiResult<T> {
  const payload = response.data
  const meta = {
    data: payload,
    ok: response.status >= 200 && response.status < 300,
    httpStatus: response.status,
    statusText: response.statusText,
    headers: response.headers,
    response,
  }

  if (payload == null || (typeof payload !== 'object' && typeof payload !== 'function')) {
    return meta as ApiResult<T>
  }

  return new Proxy(payload as object, {
    get(target, prop, receiver) {
      if (prop in meta) {
        return Reflect.get(meta, prop, receiver)
      }
      const value = Reflect.get(target, prop, receiver)
      if (typeof value === 'function') {
        return value.bind(target)
      }
      return value
    },
    has(target, prop) {
      return prop in meta || prop in target
    },
    ownKeys(target) {
      const keys = new Set<string | symbol>(Reflect.ownKeys(target))
      for (const key of Reflect.ownKeys(meta)) {
        if (typeof key === 'string' || typeof key === 'symbol') {
          keys.add(key)
        }
      }
      return [...keys]
    },
    getOwnPropertyDescriptor(target, prop) {
      return (
        Reflect.getOwnPropertyDescriptor(meta, prop)
        ?? Reflect.getOwnPropertyDescriptor(target, prop)
      )
    },
  }) as ApiResult<T>
}

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request Interceptor (Auth Token)
    this.client.interceptors.request.use(
      (config) => {
        const token = auth.getAccessToken() ?? DEV_TOKEN
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        const tenantId =
          window.localStorage.getItem('tenant_id')
          || window.sessionStorage.getItem('tenant_id')
          || DEFAULT_TENANT_ID
        config.headers['X-Tenant-ID'] = tenantId
        return config
      },
      (error) => Promise.reject(error),
    )

    // Response Interceptor (Error Handling)
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Only redirect to login if OIDC is configured
          // Check if OIDC is actually configured (not just placeholder)
          const discoveryUrl = import.meta.env.VITE_OIDC_DISCOVERY_URL ?? ''
          const placeholderPatterns = ['your-oidc-provider.com', 'example.com', 'keycloak.example.com', '{tenant-id}', '{domain}', '{application-id}', '{client-id}']
          const oidcConfigured = discoveryUrl.length > 0 && !placeholderPatterns.some(pattern => discoveryUrl.includes(pattern))
          if (oidcConfigured) {
            auth.clearTokens()
            window.location.href = '/login'
          } else {
            // In dev mode without OIDC, just log the error
            console.warn('API request returned 401 Unauthorized. In dev mode without OIDC, this might be expected.')
          }
        }
        return Promise.reject(error)
      },
    )
  }

  async get<T, D = unknown>(url: string, config?: Parameters<AxiosInstance['get']>[1]): Promise<ApiResult<T>> {
    const response = await this.client.get<T, AxiosResponse<T>, D>(url, config as any)
    return wrapResponseData(response)
  }

  async post<T, D = unknown>(url: string, data?: D, config?: Parameters<AxiosInstance['post']>[2]): Promise<ApiResult<T>> {
    const response = await this.client.post<T, AxiosResponse<T>, D>(url, data, config as any)
    return wrapResponseData(response)
  }

  async put<T, D = unknown>(url: string, data?: D, config?: Parameters<AxiosInstance['put']>[2]): Promise<ApiResult<T>> {
    const response = await this.client.put<T, AxiosResponse<T>, D>(url, data, config as any)
    return wrapResponseData(response)
  }

  async patch<T, D = unknown>(url: string, data?: D, config?: Parameters<AxiosInstance['patch']>[2]): Promise<ApiResult<T>> {
    const response = await this.client.patch<T, AxiosResponse<T>, D>(url, data, config as any)
    return wrapResponseData(response)
  }

  async delete<T, D = unknown>(url: string, config?: Parameters<AxiosInstance['delete']>[1]): Promise<ApiResult<T>> {
    const response = await this.client.delete<T, AxiosResponse<T>, D>(url, config as any)
    return wrapResponseData(response)
  }
}

export const apiClient = new APIClient()

/** Lesbare Fehlermeldung fuer Toast/Alerts (inkl. Netzwerk ohne Response). */
export function getAxiosErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      return 'Netzwerkfehler: API nicht erreichbar. Pruefen Sie, ob das Backend laeuft und VITE_API_BASE_URL bzw. der Vite-Proxy (/api/v1) stimmt.'
    }
    const data = error.response?.data as { detail?: unknown } | undefined
    const detail = data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((d: { msg?: string }) => (typeof d?.msg === 'string' ? d.msg : JSON.stringify(d)))
        .join('; ')
    }
    if (error.response?.status != null) {
      return `HTTP ${error.response.status}: ${error.response.statusText || 'Anfrage fehlgeschlagen'}`
    }
  }
  if (error instanceof Error) return error.message
  return 'Unbekannter Fehler.'
}





