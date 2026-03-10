/**
 * Agenten-Integration (Gap 048): Übersicht für externe Agenten.
 * Nutzt einen maschinenlesbaren Agent-Manifest-Endpoint als Einstiegspunkt.
 */

import { useQuery } from '@tanstack/react-query'
import {
  BookOpen,
  Bot,
  Download,
  ExternalLink,
  FileJson,
  Key,
  Link2,
  Shield,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'

type AgentManifest = {
  version: string
  generated_at: string
  auth: Record<string, string | boolean>
  headers: string[]
  links: Array<{
    rel: string
    href: string
    method: string
    description: string
  }>
  examples: Array<{
    name: string
    description: string
    method: string
    path: string
    required_headers: string[]
  }>
  notes: string[]
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || ''
const BACKEND_ORIGIN = API_BASE || (typeof window !== 'undefined' ? window.location.origin : '')

function absoluteUrl(path: string): string {
  if (!path.startsWith('/')) {
    return path
  }
  return `${BACKEND_ORIGIN}${path}`
}

export default function AgentenIntegrationPage(): JSX.Element {
  const manifestQuery = useQuery({
    queryKey: ['admin', 'agent-manifest'],
    queryFn: async () => (await apiClient.get<AgentManifest>('/api/v1/admin/agent-manifest')).data,
  })

  const downloadManifest = (): void => {
    if (!manifestQuery.data) {
      return
    }
    const blob = new Blob([`${JSON.stringify(manifestQuery.data, null, 2)}\n`], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'valeo-agent-manifest.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  if (manifestQuery.isLoading) {
    return <LoadingState message="Agenten-Manifest wird geladen..." />
  }

  if (manifestQuery.isError || !manifestQuery.data) {
    return <ErrorState error={manifestQuery.error as Error} onRetry={() => void manifestQuery.refetch()} />
  }

  const manifest = manifestQuery.data
  const openapiLink = manifest.links.find((link) => link.rel === 'openapi')
  const swaggerLink = manifest.links.find((link) => link.rel === 'swagger')
  const redocLink = manifest.links.find((link) => link.rel === 'redoc')
  const docsLink = manifest.links.find((link) => link.rel === 'agent-docs')
  const sampleTenant =
    window.localStorage.getItem('tenant_id') ||
    window.sessionStorage.getItem('tenant_id') ||
    '<tenant-uuid>'

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold">
            <Bot className="h-6 w-6" />
            Agenten-Integration
          </h1>
          <p className="mt-1 text-muted-foreground">
            Offene Integrationsfähigkeit für externe Agenten mit maschinenlesbarem Einstiegspunkt. Gap 048.
          </p>
        </div>
        <Button type="button" variant="outline" className="gap-2" onClick={downloadManifest}>
          <Download className="h-4 w-4" />
          Manifest herunterladen
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileJson className="h-5 w-5" />
              Agent Manifest
            </CardTitle>
            <CardDescription>
              Maschinenlesbarer Startpunkt für externe Tools, Codegen und Agent-Runtimes.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>
              <strong>Version:</strong> {manifest.version}
            </p>
            <p>
              <strong>Generiert:</strong> {new Date(manifest.generated_at).toLocaleString('de-DE')}
            </p>
            <p>
              <strong>Endpoint:</strong>{' '}
              <a
                href={absoluteUrl('/api/v1/admin/agent-manifest')}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary underline hover:no-underline"
              >
                {absoluteUrl('/api/v1/admin/agent-manifest')}
              </a>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Link2 className="h-5 w-5" />
              OpenAPI / MCP
            </CardTitle>
            <CardDescription>
              Kombination aus OpenAPI für Codegen und MCP-BFF für interaktive Copilot-Pfade.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {openapiLink ? <p><strong>OpenAPI:</strong> <a href={absoluteUrl(openapiLink.href)} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:no-underline">{absoluteUrl(openapiLink.href)}</a></p> : null}
            {swaggerLink ? <p><strong>Swagger:</strong> <a href={absoluteUrl(swaggerLink.href)} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:no-underline">{absoluteUrl(swaggerLink.href)}</a></p> : null}
            {redocLink ? <p><strong>ReDoc:</strong> <a href={absoluteUrl(redocLink.href)} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:no-underline">{absoluteUrl(redocLink.href)}</a></p> : null}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            Authentifizierung
          </CardTitle>
          <CardDescription>
            Externe Agenten verwenden dieselben Kernheader wie das Frontend.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          {manifest.headers.map((header) => (
            <p key={header}>
              <code>{header}</code>
            </p>
          ))}
          <Badge variant="outline">
            Hauptstrang offen: dedizierte Agent-API-Keys und produktives Rate-Limiting
          </Badge>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ExternalLink className="h-5 w-5" />
            Beispielaufrufe
          </CardTitle>
          <CardDescription>
            Sofort nutzbare Beispiele für externe Agenten- und Tool-Integrationen.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {manifest.examples.map((example) => (
            <div key={example.name} className="rounded-lg border p-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline">{example.method}</Badge>
                <span className="font-medium">{example.name}</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{example.description}</p>
              <code className="mt-3 block whitespace-pre-wrap rounded bg-muted p-3 text-xs">
                {`curl -X ${example.method} "${absoluteUrl(example.path)}" \\
  -H "Authorization: Bearer <token>" \\
  -H "X-Tenant-ID: ${sampleTenant}"${example.method !== 'GET' ? ' \\\n  -H "Content-Type: application/json"' : ''}`}
              </code>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Dokumentation
          </CardTitle>
          <CardDescription>
            Weiterführende Projekt- und Integrationsdokumentation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {docsLink ? (
            <p>
              <strong>Agenten-Dokumentation:</strong>{' '}
              <a href={docsLink.href} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:no-underline">
                {docsLink.href}
              </a>
            </p>
          ) : null}
          {manifest.notes.map((note) => (
            <p key={note} className="text-muted-foreground">
              {note}
            </p>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Status & Abhängigkeiten
          </CardTitle>
          <CardDescription>
            Vorbereitende Teile in Codex, produktive Security-/MCP-Server-Pfade im Hauptstrang.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex flex-wrap gap-2">
            <Badge>✓ Admin-Seite</Badge>
            <Badge>✓ Agent Manifest</Badge>
            <Badge>✓ OpenAPI (FastAPI)</Badge>
            <Badge>✓ MCP-Infrastruktur (Frontend)</Badge>
            <Badge variant="secondary">○ MCP-Server (Hauptstrang)</Badge>
            <Badge variant="secondary">○ Security/API-Keys produktiv (Hauptstrang)</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
