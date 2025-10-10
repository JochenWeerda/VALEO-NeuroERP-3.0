/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_TENANT_ID: string
  readonly VITE_OIDC_AUTHORITY: string
  readonly VITE_OIDC_CLIENT_ID: string
  readonly VITE_FEATURE_CONTRACT_FIXING: string
  readonly VITE_FEATURE_WEIGHING_APPROVE: string
  readonly VITE_FEATURE_DOCUMENT_DOWNLOAD: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}