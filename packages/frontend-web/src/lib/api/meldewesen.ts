/**
 * Meldewesen API – Connectors, Reporting Units, Schedules, Jobs
 * Backend: /api/v1/config, /api/v1/jobs
 */
import { apiClient } from "../api-client"

// ── Backend API types ──────────────────────────────────────────────────────────

export type ConnectorApi = {
  id: string
  tenant_id: string
  connector_key: string
  connector_type: string
  display_name?: string | null
  config_json?: Record<string, unknown> | null
  is_active: boolean
  created_at?: string | null
  updated_at?: string | null
}

export type ReportingUnitApi = {
  id: string
  tenant_id: string
  unit_key: string
  display_name: string
  connector_id?: string | null
  config_json?: Record<string, unknown> | null
  is_active: boolean
  created_at?: string | null
  updated_at?: string | null
}

export type ScheduleApi = {
  id: string
  tenant_id: string
  schedule_key: string
  display_name: string
  reporting_unit_id?: string | null
  cron_expr?: string | null
  lead_days: number
  use_workday_rule: boolean
  output_format?: string | null
  config_json?: Record<string, unknown> | null
  is_active: boolean
  created_at?: string | null
  updated_at?: string | null
}

export type JobApi = {
  id: string
  tenant_id: string
  schedule_id?: string | null
  job_type: string
  status: string
  triggered_at?: string | null
  completed_at?: string | null
  error_message?: string | null
  dry_run: boolean
  created_at?: string | null
}

export type JobArtifactApi = {
  id: string
  job_id: string
  artifact_key: string
  content_type: string
  file_path?: string | null
  file_size_bytes?: number | null
  checksum_sha256?: string | null
  created_at?: string | null
}

const CONFIG_BASE = "/api/v1/config"
const JOBS_BASE = "/api/v1/jobs"

// ── Connectors ─────────────────────────────────────────────────────────────────

export async function listConnectors(): Promise<ConnectorApi[]> {
  return (await apiClient.get<ConnectorApi[]>(`${CONFIG_BASE}/connectors`)).data
}

export async function getConnector(id: string): Promise<ConnectorApi> {
  return (await apiClient.get<ConnectorApi>(`${CONFIG_BASE}/connectors/${id}`)).data
}

export async function createConnector(payload: {
  connector_key: string
  connector_type: string
  display_name?: string | null
  config_json?: Record<string, unknown> | null
  is_active?: boolean
}): Promise<ConnectorApi> {
  return (await apiClient.put<ConnectorApi>(`${CONFIG_BASE}/connectors`, payload)).data
}

export async function updateConnector(
  id: string,
  payload: { display_name?: string | null; config_json?: Record<string, unknown> | null; is_active?: boolean }
): Promise<ConnectorApi> {
  return (await apiClient.patch<ConnectorApi>(`${CONFIG_BASE}/connectors/${id}`, payload)).data
}

export async function deleteConnector(id: string): Promise<void> {
  await apiClient.delete(`${CONFIG_BASE}/connectors/${id}`)
}

// ── Reporting Units ───────────────────────────────────────────────────────────

export async function listReportingUnits(): Promise<ReportingUnitApi[]> {
  return (await apiClient.get<ReportingUnitApi[]>(`${CONFIG_BASE}/reporting-units`)).data
}

export async function createReportingUnit(payload: {
  unit_key: string
  display_name: string
  connector_id?: string | null
  config_json?: Record<string, unknown> | null
  is_active?: boolean
}): Promise<ReportingUnitApi> {
  return (await apiClient.put<ReportingUnitApi>(`${CONFIG_BASE}/reporting-units`, payload)).data
}

export async function updateReportingUnit(
  id: string,
  payload: {
    display_name?: string
    connector_id?: string | null
    config_json?: Record<string, unknown> | null
    is_active?: boolean
  }
): Promise<ReportingUnitApi> {
  return (await apiClient.patch<ReportingUnitApi>(`${CONFIG_BASE}/reporting-units/${id}`, payload)).data
}

export async function deleteReportingUnit(id: string): Promise<void> {
  await apiClient.delete(`${CONFIG_BASE}/reporting-units/${id}`)
}

// ── Schedules ─────────────────────────────────────────────────────────────────

export async function listSchedules(): Promise<ScheduleApi[]> {
  return (await apiClient.get<ScheduleApi[]>(`${CONFIG_BASE}/schedules`)).data
}

export async function createSchedule(payload: {
  schedule_key: string
  display_name: string
  reporting_unit_id?: string | null
  cron_expr?: string | null
  lead_days?: number
  use_workday_rule?: boolean
  output_format?: string | null
  config_json?: Record<string, unknown> | null
  is_active?: boolean
}): Promise<ScheduleApi> {
  return (await apiClient.put<ScheduleApi>(`${CONFIG_BASE}/schedules`, payload)).data
}

export async function updateSchedule(
  id: string,
  payload: {
    display_name?: string
    reporting_unit_id?: string | null
    cron_expr?: string | null
    lead_days?: number
    use_workday_rule?: boolean
    output_format?: string | null
    config_json?: Record<string, unknown> | null
    is_active?: boolean
  }
): Promise<ScheduleApi> {
  return (await apiClient.patch<ScheduleApi>(`${CONFIG_BASE}/schedules/${id}`, payload)).data
}

export async function deleteSchedule(id: string): Promise<void> {
  await apiClient.delete(`${CONFIG_BASE}/schedules/${id}`)
}

// ── Jobs ──────────────────────────────────────────────────────────────────────

export async function runJob(payload: { schedule_id?: string | null; job_type: string; dry_run?: boolean }): Promise<JobApi> {
  return (await apiClient.post<JobApi>(`${JOBS_BASE}/run`, payload)).data
}

export async function listJobs(params?: { status?: string; limit?: number }): Promise<JobApi[]> {
  const searchParams = new URLSearchParams()
  if (params?.status) searchParams.set("status", params.status)
  if (params?.limit != null) searchParams.set("limit", String(params.limit))
  const qs = searchParams.toString()
  const url = qs ? `${JOBS_BASE}?${qs}` : JOBS_BASE
  return (await apiClient.get<JobApi[]>(url)).data
}

export async function getJob(id: string): Promise<JobApi> {
  return (await apiClient.get<JobApi>(`${JOBS_BASE}/${id}`)).data
}

export async function getJobArtifacts(jobId: string): Promise<JobArtifactApi[]> {
  return (await apiClient.get<JobArtifactApi[]>(`${JOBS_BASE}/${jobId}/artifacts`)).data
}
