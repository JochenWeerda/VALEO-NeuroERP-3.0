/**
 * API-Client mit automatischer Token-Injection
 * Handles token refresh und 401-Errors
 */

import { auth } from './auth'

export class APIClient {
  private baseUrl: string

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  }

  /**
   * Fetch mit automatischer Token-Injection
   */
  async fetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const token = auth.getAccessToken()

    const headers = new Headers(options.headers || {})
    
    // Add Authorization header
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }

    // Add Content-Type if body present
    if (options.body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json')
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    })

    // Handle 401 - Try token refresh
    if (response.status === 401) {
      const refreshed = await auth.refreshAccessToken()
      
      if (refreshed) {
        // Retry request with new token
        const newToken = auth.getAccessToken()
        headers.set('Authorization', `Bearer ${newToken}`)
        
        return fetch(`${this.baseUrl}${endpoint}`, {
          ...options,
          headers,
        })
      } else {
        // Refresh failed → Logout
        auth.logout()
        window.location.href = '/login'
        throw new Error('Session expired. Please login again.')
      }
    }

    return response
  }

  /**
   * GET request
   */
  async get<T = any>(endpoint: string): Promise<T> {
    const response = await this.fetch(endpoint, { method: 'GET' })
    
    if (!response.ok) {
      throw new Error(`GET ${endpoint} failed: ${response.status}`)
    }
    
    return response.json()
  }

  /**
   * POST request
   */
  async post<T = any>(endpoint: string, data?: any): Promise<T> {
    const response = await this.fetch(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
    
    if (!response.ok) {
      throw new Error(`POST ${endpoint} failed: ${response.status}`)
    }
    
    return response.json()
  }

  /**
   * PUT request
   */
  async put<T = any>(endpoint: string, data?: any): Promise<T> {
    const response = await this.fetch(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
    
    if (!response.ok) {
      throw new Error(`PUT ${endpoint} failed: ${response.status}`)
    }
    
    return response.json()
  }

  /**
   * DELETE request
   */
  async delete<T = any>(endpoint: string): Promise<T> {
    const response = await this.fetch(endpoint, { method: 'DELETE' })
    
    if (!response.ok) {
      throw new Error(`DELETE ${endpoint} failed: ${response.status}`)
    }
    
    return response.json()
  }
}

// Singleton
export const apiClient = new APIClient()

