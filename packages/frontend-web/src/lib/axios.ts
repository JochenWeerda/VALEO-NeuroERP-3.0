import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { v4 as uuidv4 } from 'uuid'
import {
  clearAuthSession,
  getAccessToken,
  handleUnauthorized,
} from '@/lib/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const TENANT_ID = import.meta.env.VITE_TENANT_ID ?? ''
const REQUEST_TIMEOUT_MS = 30_000
const HTTP_STATUS_UNAUTHORIZED = 401
const HTTP_STATUS_FORBIDDEN = 403

interface RequestMetadata {
  startTime: number
  requestId: string
  correlationId: string
}

type HeaderCarrier = NonNullable<InternalAxiosRequestConfig['headers']> & {
  [key: string]: string
}

declare module 'axios' {
  interface InternalAxiosRequestConfig {
    metadata?: RequestMetadata
  }

  interface AxiosRequestConfig {
    metadata?: RequestMetadata
  }
}

const createRequestId = (): string => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return uuidv4()
}

const ensureHeaders = (
  config: InternalAxiosRequestConfig
): HeaderCarrier => {
  if (config.headers === undefined || config.headers === null) {
    config.headers = {}
  }
  return config.headers
}

const readHeader = (headers: HeaderCarrier, key: string): string | undefined => {
  if (typeof headers.get === 'function') {
    return headers.get(key) ?? undefined
  }
  const value = headers[key]
  if (Array.isArray(value)) {
    return value[0]
  }
  return value
}

const writeHeader = (headers: HeaderCarrier, key: string, value: string): void => {
  if (typeof headers.set === 'function') {
    headers.set(key, value)
    return
  }
  headers[key] = value
}

const logHttpError = (payload: Record<string, unknown>): void => {
  const consoleCandidate = Reflect.get(globalThis, 'console') as Partial<Console> | undefined
  consoleCandidate?.error?.('HTTP request failed', payload)
}

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
})

api.interceptors.request.use((config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  const cfg = config
  const headers = ensureHeaders(cfg)

  const token = getAccessToken()
  if (token !== null && readHeader(headers, 'Authorization') === undefined) {
    writeHeader(headers, 'Authorization', `Bearer ${token}`)
  }

  if (TENANT_ID !== '' && readHeader(headers, 'x-tenant-id') === undefined) {
    writeHeader(headers, 'x-tenant-id', TENANT_ID)
  }

  const requestId =
    readHeader(headers, 'x-request-id') ?? createRequestId()
  const correlationId =
    readHeader(headers, 'x-correlation-id') ?? requestId

  writeHeader(headers, 'x-request-id', requestId)
  writeHeader(headers, 'x-correlation-id', correlationId)

  if (readHeader(headers, 'x-span-id') === undefined) {
    writeHeader(headers, 'x-span-id', requestId)
  }
  if (readHeader(headers, 'x-trace-id') === undefined) {
    writeHeader(headers, 'x-trace-id', correlationId)
  }

  cfg.metadata = {
    startTime: Date.now(),
    requestId,
    correlationId,
  }

  return cfg
})

api.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    return response
  },
  async (error: AxiosError): Promise<never> => {
    const config = error.config as InternalAxiosRequestConfig | undefined
    const status = error.response?.status
    const metadata = config?.metadata
    const duration = metadata ? Date.now() - metadata.startTime : undefined

    logHttpError({
      requestId: metadata?.requestId,
      correlationId: metadata?.correlationId,
      method: config?.method,
      url: config?.url,
      status,
      duration,
      message: error.message,
    })

    if (status === HTTP_STATUS_UNAUTHORIZED) {
      handleUnauthorized()
      return Promise.reject(error)
    }

    if (status === HTTP_STATUS_FORBIDDEN) {
      clearAuthSession()
    }

    return Promise.reject(error)
  }
)

const apiClient = {
  get: async <T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.get<T>(url, config),
  post: async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.post<T>(url, data, config),
  put: async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.put<T>(url, data, config),
  patch: async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.patch<T>(url, data, config),
  delete: async <T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    api.delete<T>(url, config),
}

export { api, apiClient, createRequestId }


