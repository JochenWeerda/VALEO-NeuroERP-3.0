import axios from "axios"
import { v4 as uuidv4 } from "uuid"
import { clearAuthSession, getAccessToken, handleUnauthorized } from "@/lib/auth"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ""
const TENANT_ID = import.meta.env.VITE_TENANT_ID ?? ""
const REQUEST_TIMEOUT_MS = 30_000
const HTTP_STATUS_UNAUTHORIZED = 401
const HTTP_STATUS_FORBIDDEN = 403

interface RequestMetadata {
  startTime: number
  requestId: string
  correlationId: string
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT_MS,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false,
})

const PARAM_INDEX_FIRST = 0
const PARAM_INDEX_SECOND = 1
const PARAM_INDEX_THIRD = 2

type RequestFulfilled = NonNullable<Parameters<typeof api.interceptors.request.use>[typeof PARAM_INDEX_FIRST]>
type InternalRequestConfig = RequestFulfilled extends (_value: infer T) => unknown ? T : never

type ResponseRejected = Parameters<typeof api.interceptors.response.use>[typeof PARAM_INDEX_SECOND]
type ResponseError = ResponseRejected extends (_error: infer T) => unknown ? T : unknown

type HeadersLike = (NonNullable<InternalRequestConfig["headers"]> & {
  set?: (_name: string, _value: string) => void
  get?: (_name: string) => string | null | undefined
}) | Record<string, string>

type GetConfig = Parameters<typeof api.get>[typeof PARAM_INDEX_SECOND]
type MutationConfig = Parameters<typeof api.post>[typeof PARAM_INDEX_THIRD]
type DeleteConfig = Parameters<typeof api.delete>[typeof PARAM_INDEX_SECOND]

const createRequestId = (): string => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID()
  }
  return uuidv4()
}

const ensureHeaders = (config: InternalRequestConfig): HeadersLike => {
  const current = config.headers as HeadersLike | undefined
  if (current) {
    return current
  }
  const fallback: HeadersLike = {}
  config.headers = fallback as InternalRequestConfig["headers"]
  return fallback
}

const readHeader = (headers: HeadersLike, key: string): string | undefined => {
  if (typeof headers.get === "function") {
    const value = headers.get(key)
    return typeof value === "string" ? value : undefined
  }
  const entry = (headers as Record<string, unknown>)[key]
  if (Array.isArray(entry)) {
    return entry[0] as string | undefined
  }
  return typeof entry === "string" ? entry : undefined
}

const writeHeader = (headers: HeadersLike, key: string, value: string): void => {
  if (typeof headers.set === "function") {
    headers.set(key, value)
    return
  }
  (headers as Record<string, string>)[key] = value
}

const logHttpError = (payload: Record<string, unknown>): void => {
  const consoleCandidate = Reflect.get(globalThis, "console") as Partial<Console> | undefined
  consoleCandidate?.error?.("HTTP request failed", payload)
}

api.interceptors.request.use((config) => {
  const cfg = config as InternalRequestConfig & { metadata?: RequestMetadata }
  const headers = ensureHeaders(cfg)

  const token = getAccessToken()
  // Always send token if available, or use dev-token as fallback in dev mode
  const oidcConfigured = (import.meta.env.VITE_OIDC_DISCOVERY_URL ?? '').length > 0
  const finalToken = token || (!oidcConfigured ? (import.meta.env.VITE_API_DEV_TOKEN || 'dev-token') : null)
  if (finalToken !== null && readHeader(headers, "Authorization") === undefined) {
    writeHeader(headers, "Authorization", `Bearer ${finalToken}`)
  }

  if (TENANT_ID !== "" && readHeader(headers, "x-tenant-id") === undefined) {
    writeHeader(headers, "x-tenant-id", TENANT_ID)
  }

  const requestId = readHeader(headers, "x-request-id") ?? createRequestId()
  const correlationId = readHeader(headers, "x-correlation-id") ?? requestId

  writeHeader(headers, "x-request-id", requestId)
  writeHeader(headers, "x-correlation-id", correlationId)

  if (readHeader(headers, "x-span-id") === undefined) {
    writeHeader(headers, "x-span-id", requestId)
  }
  if (readHeader(headers, "x-trace-id") === undefined) {
    writeHeader(headers, "x-trace-id", correlationId)
  }

  cfg.metadata = {
    startTime: Date.now(),
    requestId,
    correlationId,
  }

  return cfg
})

api.interceptors.response.use(
  (response) => response,
  async (error: ResponseError): Promise<never> => {
    const axiosError = error as ResponseError & {
      config?: (InternalRequestConfig & { metadata?: RequestMetadata }) | undefined
      response?: { status?: number }
      message?: string
    }

    const configWithMeta = axiosError.config
    const metadata = configWithMeta?.metadata
    const status = axiosError.response?.status
    const duration = metadata ? Date.now() - metadata.startTime : undefined

    logHttpError({
      requestId: metadata?.requestId,
      correlationId: metadata?.correlationId,
      method: configWithMeta?.method,
      url: configWithMeta?.url,
      status,
      duration,
      message: axiosError instanceof Error ? axiosError.message : undefined,
    })

    if (status === HTTP_STATUS_UNAUTHORIZED) {
      // In development mode without OIDC, don't redirect to login
      // The backend should handle dev mode authentication
      // Check if OIDC is actually configured (not just placeholder)
      const discoveryUrl = import.meta.env.VITE_OIDC_DISCOVERY_URL ?? ''
      const placeholderPatterns = ['your-oidc-provider.com', 'example.com', 'keycloak.example.com', '{tenant-id}', '{domain}', '{application-id}', '{client-id}']
      const oidcConfigured = discoveryUrl.length > 0 && !placeholderPatterns.some(pattern => discoveryUrl.includes(pattern))
      if (oidcConfigured) {
        handleUnauthorized()
      }
      // In dev mode, log the error but don't redirect
      console.warn('API request returned 401 Unauthorized. In dev mode without OIDC, this might be expected.')
      throw error
    }

    if (status === HTTP_STATUS_FORBIDDEN) {
      // Check if OIDC is actually configured (not just placeholder)
      const discoveryUrl = import.meta.env.VITE_OIDC_DISCOVERY_URL ?? ''
      const placeholderPatterns = ['your-oidc-provider.com', 'example.com', 'keycloak.example.com', '{tenant-id}', '{domain}', '{application-id}', '{client-id}']
      const oidcConfigured = discoveryUrl.length > 0 && !placeholderPatterns.some(pattern => discoveryUrl.includes(pattern))
      // Only clear session if OIDC is configured
      if (oidcConfigured) {
        clearAuthSession()
      }
    }

    throw error
  }
)

// Explicit interface ensures TypeScript uses declared return types (not inferred AxiosResponse<T>)
interface ApiClient {
  get<T>(url: string, config?: GetConfig): Promise<T>
  post<TResponse, TPayload = unknown>(url: string, data?: TPayload, config?: MutationConfig): Promise<TResponse>
  put<TResponse, TPayload = unknown>(url: string, data?: TPayload, config?: MutationConfig): Promise<TResponse>
  patch<TResponse, TPayload = unknown>(url: string, data?: TPayload, config?: MutationConfig): Promise<TResponse>
  delete<TResponse>(url: string, config?: DeleteConfig): Promise<TResponse>
}

const apiClient: ApiClient = {
  get: async <T>(url: string, config?: GetConfig): Promise<T> => {
    const response = await api.get<T>(url, config)
    return response.data as T
  },
  post: async <TResponse, TPayload = unknown>(url: string, data?: TPayload, config?: MutationConfig): Promise<TResponse> => {
    const response = await api.post<TResponse>(url, data, config)
    return response.data as TResponse
  },
  put: async <TResponse, TPayload = unknown>(url: string, data?: TPayload, config?: MutationConfig): Promise<TResponse> => {
    const response = await api.put<TResponse>(url, data, config)
    return response.data as TResponse
  },
  patch: async <TResponse, TPayload = unknown>(url: string, data?: TPayload, config?: MutationConfig): Promise<TResponse> => {
    const response = await api.patch<TResponse>(url, data, config)
    return response.data as TResponse
  },
  delete: async <TResponse>(url: string, config?: DeleteConfig): Promise<TResponse> => {
    const response = await api.delete<TResponse>(url, config)
    return response.data as TResponse
  },
}

export { api, apiClient, createRequestId }
