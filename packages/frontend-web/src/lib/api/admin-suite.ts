import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type ReadinessStatus = 'ready' | 'warning' | 'blocked' | 'unchecked'

export type ReadinessEvidence = {
  key: string
  label: string
  status: ReadinessStatus
  source: string
  evidence: string
  details: string[]
  checked_at: string
}

export type AdminSuiteReadiness = {
  status: ReadinessStatus
  score: number
  ready_count: number
  warning_count: number
  blocked_count: number
  unchecked_count: number
  evaluated_count: number
  checked_at: string
  evidence: ReadinessEvidence[]
}

export type SetupStepStatus = 'unchecked' | 'in_progress' | 'warning' | 'blocked' | 'completed'

export type SetupStep = {
  key: string
  label: string
  status: SetupStepStatus
  target_path?: string | null
  evidence?: string | null
  responsible?: string | null
  updated_at?: string | null
}

export type SetupSession = {
  tenant_id: string
  status: SetupStepStatus
  completed_count: number
  total_count: number
  updated_at?: string | null
  steps: SetupStep[]
}

export type MigrationProfile = {
  key: string
  label: string
  status: 'available' | 'blocked' | 'planned'
  adapter?: string | null
  notes: string
}

export type MigrationBatch = {
  id: string
  tenant_id: string
  source_profile: string
  source_ref: string
  source_hash: string
  mapping_version: string
  dry_run: boolean
  status: 'dry_run' | 'staged' | 'reconciliation_pending' | 'approved' | 'blocked'
  reconciliation: Record<string, boolean>
  created_at: string
  updated_at: string
}

export type MigrationCockpit = {
  profiles: MigrationProfile[]
  batches: MigrationBatch[]
}

export type SecurityRole = {
  key: string
  permissions: string[]
  actor_type: 'human' | 'agent'
  notes?: string | null
}

export type SecurityCockpit = {
  roles: SecurityRole[]
  agent_roles: SecurityRole[]
}

export type Connector = {
  key: string
  label: string
  config_status: 'configured' | 'partial' | 'disabled' | 'unchecked'
  live_status: 'unchecked'
  credential_status: 'set' | 'missing' | 'unchecked' | 'not_required'
  source: string
  notes: string
}

export type DeviceCapability = {
  key: string
  label: string
  registry_source: string
  registration_status: 'available' | 'partial' | 'planned'
  live_status: 'unchecked'
  test_actions: string[]
  notes: string
}

export type OperationsEvidence = {
  key: string
  label: string
  implementation_status: 'available' | 'partial' | 'planned'
  runtime_status: 'unchecked'
  source: string
  notes: string
}

export type ComplianceEvidence = {
  key: string
  label: string
  implementation_status: 'available' | 'partial' | 'planned'
  runtime_status: 'unchecked'
  external_gate: 'required' | 'not_required' | 'unchecked'
  source: string
  target_path?: string | null
  notes: string
}

export type SystemStatusEvidence = {
  key: string
  label: string
  probe_status: 'available' | 'partial' | 'planned'
  runtime_status: 'unchecked'
  source: string
  target_path?: string | null
  notes: string
}

export type DiagnosticManifestItem = {
  key: string
  label: string
  source: string
  collection_status: 'not_collected'
  redaction: 'required' | 'metadata_only'
  notes: string
}

export function useAdminSuiteReadiness() {
  return useQuery({
    queryKey: ['admin-suite', 'readiness'],
    queryFn: async () => (await apiClient.get<AdminSuiteReadiness>('/api/v1/admin-suite/readiness')).data,
    staleTime: 30 * 1000,
  })
}

export function useAdminSuiteSetup() {
  return useQuery({
    queryKey: ['admin-suite', 'setup'],
    queryFn: async () => (await apiClient.get<SetupSession>('/api/v1/admin-suite/setup')).data,
  })
}

export function useUpdateAdminSuiteSetupStep() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ key, status }: { key: string; status: SetupStepStatus }) =>
      (await apiClient.patch<SetupSession>(`/api/v1/admin-suite/setup/steps/${key}`, { status })).data,
    onSuccess: (data) => queryClient.setQueryData(['admin-suite', 'setup'], data),
  })
}

export function useAdminSuiteMigration() {
  return useQuery({
    queryKey: ['admin-suite', 'migration'],
    queryFn: async () => (await apiClient.get<MigrationCockpit>('/api/v1/admin-suite/migration')).data,
  })
}

export function useAdminSuiteSecurity() {
  return useQuery({
    queryKey: ['admin-suite', 'security'],
    queryFn: async () => (await apiClient.get<SecurityCockpit>('/api/v1/admin-suite/security')).data,
  })
}

export function useAdminSuiteConnectors() {
  return useQuery({ queryKey: ['admin-suite', 'connectors'], queryFn: async () => (await apiClient.get<Connector[]>('/api/v1/admin-suite/connectors')).data })
}

export function useAdminSuiteDevices() {
  return useQuery({ queryKey: ['admin-suite', 'devices'], queryFn: async () => (await apiClient.get<DeviceCapability[]>('/api/v1/admin-suite/devices')).data })
}

export function useAdminSuiteOperations() {
  return useQuery({ queryKey: ['admin-suite', 'operations'], queryFn: async () => (await apiClient.get<OperationsEvidence[]>('/api/v1/admin-suite/operations')).data })
}

export function useAdminSuiteCompliance() {
  return useQuery({ queryKey: ['admin-suite', 'compliance'], queryFn: async () => (await apiClient.get<ComplianceEvidence[]>('/api/v1/admin-suite/compliance')).data })
}

export function useAdminSuiteSystemStatus() {
  return useQuery({ queryKey: ['admin-suite', 'system-status'], queryFn: async () => (await apiClient.get<SystemStatusEvidence[]>('/api/v1/admin-suite/system-status')).data })
}

export function useAdminSuiteDiagnostics() {
  return useQuery({ queryKey: ['admin-suite', 'diagnostics'], queryFn: async () => (await apiClient.get<DiagnosticManifestItem[]>('/api/v1/admin-suite/diagnostics')).data })
}

// ── LLM-Gateway (anbieterunabhängige KI-Konfiguration) ───────────────────────
export type LlmProvider = 'anthropic' | 'openai_compatible' | 'ollama'

export type LlmGatewayConfig = {
  provider: LlmProvider
  base_url: string
  model: string
  temperature: number
  enabled: boolean
  api_key_set: boolean
  available: boolean
  providers: LlmProvider[]
}

export type LlmGatewayUpdate = Partial<{
  provider: LlmProvider
  base_url: string
  model: string
  api_key: string
  temperature: number
  enabled: boolean
}>

export type LlmTestResult = { ok: boolean; provider: string; model: string; detail: string }

export function useLlmGateway() {
  return useQuery({
    queryKey: ['admin-suite', 'llm-gateway'],
    queryFn: async () => (await apiClient.get<LlmGatewayConfig>('/api/v1/admin-suite/llm-gateway')).data,
  })
}

export function useUpdateLlmGateway() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (patch: LlmGatewayUpdate) =>
      (await apiClient.put<LlmGatewayConfig>('/api/v1/admin-suite/llm-gateway', patch)).data,
    onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['admin-suite', 'llm-gateway'] }) },
  })
}

export function useTestLlmGateway() {
  return useMutation({
    mutationFn: async () => (await apiClient.post<LlmTestResult>('/api/v1/admin-suite/llm-gateway/test', {})).data,
  })
}

// ── Auto-Capture-Connectoren (STT + IMAP, per Tenant) ────────────────────────
export type ConnectorSttConfig = {
  enabled: boolean
  base_url: string
  model: string
  language: string
  api_key_set: boolean
  configured: boolean
}

export type ConnectorImapConfig = {
  enabled: boolean
  host: string
  port: number
  ssl: boolean
  user: string
  inbox: string
  sent: string
  own_addresses: string
  poll_seconds: number
  password_set: boolean
  configured: boolean
}

export type ConnectorsConfig = { stt: ConnectorSttConfig; imap: ConnectorImapConfig }

export type ConnectorsUpdate = Partial<{
  stt: Partial<{ enabled: boolean; base_url: string; model: string; language: string; api_key: string }>
  imap: Partial<{
    enabled: boolean; host: string; port: number; ssl: boolean; user: string; password: string
    inbox: string; sent: string; own_addresses: string; poll_seconds: number
  }>
}>

export type ConnectorTestResult = { ok: boolean; detail: string }
export type ConnectorPollResult = { ok: boolean; detail: string; processed: number; created: number }

const CB = '/api/v1/admin-suite/capture-connectors'

export function useConnectors() {
  return useQuery({
    queryKey: ['admin-suite', 'capture-connectors'],
    queryFn: async () => (await apiClient.get<ConnectorsConfig>(CB)).data,
  })
}

export function useUpdateConnectors() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (patch: ConnectorsUpdate) => (await apiClient.put<ConnectorsConfig>(CB, patch)).data,
    onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['admin-suite', 'capture-connectors'] }) },
  })
}

export function useTestConnectorStt() {
  return useMutation({
    mutationFn: async () => (await apiClient.post<ConnectorTestResult>(`${CB}/stt/test`, {})).data,
  })
}

export function useTestConnectorImap() {
  return useMutation({
    mutationFn: async () => (await apiClient.post<ConnectorTestResult>(`${CB}/imap/test`, {})).data,
  })
}

export function usePollConnectorImap() {
  return useMutation({
    mutationFn: async () => (await apiClient.post<ConnectorPollResult>(`${CB}/imap/poll`, {})).data,
  })
}
