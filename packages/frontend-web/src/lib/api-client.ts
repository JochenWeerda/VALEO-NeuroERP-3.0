/**
 * API Client
 * Axios-basierter HTTP-Client mit Interceptors
 */
import axios, { type AxiosInstance } from 'axios'
import { auth } from './auth'

const DEV_TOKEN = import.meta.env.VITE_API_DEV_TOKEN as string | undefined

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

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
        return config
      },
      (error) => Promise.reject(error),
    )

    // Response Interceptor (Error Handling)
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired - redirect to login
          auth.clearTokens()
          window.location.href = '/login'
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





