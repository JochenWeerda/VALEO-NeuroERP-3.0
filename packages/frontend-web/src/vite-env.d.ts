/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_TENANT_ID: string
  readonly VITE_OIDC_AUTHORITY: string
  readonly VITE_OIDC_CLIENT_ID: string
  readonly VITE_FEATURE_CONTRACT_FIXING: string
  readonly VITE_FEATURE_WEIGHING_APPROVE: string
  readonly VITE_FEATURE_DOCUMENT_DOWNLOAD: string
  readonly VITE_FEATURE_SSE?: string
  readonly VITE_FEATURE_COMMAND_PALETTE?: string
  readonly VITE_FEATURE_AGRAR?: string
  readonly VITE_ENABLE_COMMAND_PALETTE?: string
  readonly VITE_ENABLE_REALTIME_STATUS?: string
  readonly VITE_FLAGS_URL?: string
  readonly VITE_MCP_EVENTS_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
