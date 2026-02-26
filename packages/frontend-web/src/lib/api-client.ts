/**
 * API Client
 * Axios-basierter HTTP-Client mit Interceptors
 */
import axios, { type AxiosInstance } from 'axios'
import { auth } from './auth'

const DEV_TOKEN = import.meta.env.VITE_API_DEV_TOKEN as string | undefined || 'dev-token'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const DEFAULT_TENANT_ID = import.meta.env.VITE_TENANT_ID || '00000000-0000-0000-0000-000000000001'

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
            // eslint-disable-next-line no-console
            console.warn('API request returned 401 Unauthorized. In dev mode without OIDC, this might be expected.')
          }
        }
        return Promise.reject(error)
      },
    )
  }

  get<T>(url: string, config?: Parameters<AxiosInstance['get']>[1]) {
    return this.client.get<T>(url, config)
  }

  post<T>(url: string, data?: unknown, config?: Parameters<AxiosInstance['post']>[2]) {
    return this.client.post<T>(url, data, config)
  }

  put<T>(url: string, data?: unknown, config?: Parameters<AxiosInstance['put']>[2]) {
    return this.client.put<T>(url, data, config)
  }

  patch<T>(url: string, data?: unknown, config?: Parameters<AxiosInstance['patch']>[2]) {
    return this.client.patch<T>(url, data, config)
  }

  delete<T>(url: string, config?: Parameters<AxiosInstance['delete']>[1]) {
    return this.client.delete<T>(url, config)
  }
}

export const apiClient = new APIClient()





