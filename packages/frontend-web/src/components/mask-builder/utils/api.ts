// VALEO Mask Builder API Utilities

export interface ApiResponse<T = any> {
  data: T
  success: boolean
  message?: string
  errors?: Record<string, string>
}

export interface PaginatedResponse<T = any> {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export class ApiClient {
  private baseUrl: string
  private defaultHeaders: Record<string, string>

  constructor(baseUrl: string, headers: Record<string, string> = {}) {
    this.baseUrl = baseUrl
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...headers
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`
    const config: RequestInit = {
      headers: this.defaultHeaders,
      ...options
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      return {
        data,
        success: true
      }
    } catch (error) {
      return {
        data: null as T,
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        errors: {}
      }
    }
  }

  async get<T>(endpoint: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
    const url = params ? `${endpoint}?${String(new URLSearchParams(params))}` : endpoint
    return this.request<T>(url)
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async patch<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'DELETE'
    })
  }
}

// Factory function for creating API clients
export function createApiClient(baseUrl: string, headers?: Record<string, string>): ApiClient {
  return new ApiClient(baseUrl, headers)
}

// Common API patterns
export const apiPatterns = {
  list: (resource: string) => `/${resource}`,
  get: (resource: string, id: string) => `/${resource}/${id}`,
  create: (resource: string) => `/${resource}`,
  update: (resource: string, id: string) => `/${resource}/${id}`,
  delete: (resource: string, id: string) => `/${resource}/${id}`,
  search: (resource: string) => `/${resource}/search`,
  bulk: (resource: string, action: string) => `/${resource}/bulk/${action}`,
}

// Error handling utilities
export function isApiError(response: ApiResponse): boolean {
  return !response.success
}

export function getApiErrorMessage(response: ApiResponse): string {
  return response.message || 'An error occurred'
}

export function getApiFieldErrors(response: ApiResponse): Record<string, string> {
  return response.errors || {}
}

// Cache utilities (simple in-memory cache)
const cache = new Map<string, { data: any; timestamp: number; ttl: number }>()

export function getCachedData<T>(key: string): T | null {
  const cached = cache.get(key)
  if (!cached) return null

  if (Date.now() - cached.timestamp > cached.ttl) {
    cache.delete(key)
    return null
  }

  return cached.data
}

export function setCachedData(key: string, data: any, ttl = 5 * 60 * 1000): void {
  cache.set(key, { data, timestamp: Date.now(), ttl })
}

export function clearCache(): void {
  cache.clear()
}