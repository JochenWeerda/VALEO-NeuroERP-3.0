import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Download, FlaskConical, Play, ShieldAlert } from 'lucide-react'
import { useSearchParams } from '@/app/routing/typed-router'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { apiClient } from '@/lib/api-client'

type ProcessVariant = {
  steps?: string[]
  required_roles?: Record<string, string[]>
  step_sla?: Record<string, { timeout_hours?: number; escalation_roles?: string[] }>
  description?: string
}

type ProcessVariantsResponse = {
  variants: Record<string, ProcessVariant>
}

type Campaign = {
  id: string
  name: string
  start_date: string
  end_date: string
  process_key: string
  product_groups: string[]
}

type SandboxPreview = {
  process_key: string
  simulation_date: string
  steps: string[]
  required_roles: Record<string, string[]>
  step_sla: Record<string, { timeout_hours?: number; escalation_roles?: string[] }>
  description?: string | null
  matched_campaigns: Array<Campaign & { in_window: boolean; product_group_match: boolean }>
  warnings: string[]
}

const EMPTY_PROCESS_VARIANTS: ProcessVariantsResponse = { variants: {} }
const EMPTY_CAMPAIGNS: Campaign[] = []

export default function WorkflowSandboxPage(): JSX.Element {
  const [searchParams] = useSearchParams()
  const today = new Date().toISOString().slice(0, 10)
  const [processKey, setProcessKey] = useState<string>(searchParams.get('process') || 'annahme')
  const [simulationDate, setSimulationDate] = useState<string>(searchParams.get('date') || today)
  const [campaignId, setCampaignId] = useState<string>(searchParams.get('campaign') || 'all')
  const [productGroup, setProductGroup] = useState<string>(searchParams.get('productGroup') || '')
  const autoPreviewDoneRef = useRef(false)

  const {
    data: variantsData,
    isLoading: variantsLoading,
    isError: variantsError,
    error: variantsQueryError,
    refetch: refetchVariants,
  } = useQuery({
    queryKey: ['workflow-sandbox', 'process-variants'],
    queryFn: async () => (await apiClient.get<ProcessVariantsResponse>('/api/v1/admin/process-variants')).data,
    initialData: EMPTY_PROCESS_VARIANTS,
  })

  const {
    data: campaigns,
    isLoading: campaignsLoading,
    isError: campaignsError,
    error: campaignsQueryError,
    refetch: refetchCampaigns,
  } = useQuery({
    queryKey: ['workflow-sandbox', 'erntefenster-campaigns'],
    queryFn: async () => (await apiClient.get<Campaign[]>('/api/v1/admin/erntefenster-campaigns')).data,
    initialData: EMPTY_CAMPAIGNS,
  })

  const previewMutation = useMutation({
    mutationFn: async () =>
      (
        await apiClient.post<SandboxPreview>('/api/v1/admin/workflow-sandbox/preview', {
          process_key: processKey,
          simulation_date: simulationDate,
          campaign_id: campaignId === 'all' ? null : campaignId,
          product_group: productGroup.trim() || null,
        })
      ).data,
  })

  const processOptions = useMemo(
    () =>
      Object.entries(variantsData.variants).map(([key, variant]) => ({
        key,
        label: key,
        description: variant.description || '',
      })),
    [variantsData],
  )

  const visibleCampaigns = useMemo(
    () => campaigns.filter((campaign) => campaign.process_key === processKey),
    [campaigns, processKey],
  )

  const currentVariant = variantsData.variants[processKey]

  const handleExportPreview = (): void => {
    if (!previewMutation.data) {
      return
    }
    const payload = {
      exported_at: new Date().toISOString(),
      request: {
        process_key: processKey,
        simulation_date: simulationDate,
        campaign_id: campaignId === 'all' ? null : campaignId,
        product_group: productGroup.trim() || null,
      },
      preview: previewMutation.data,
    }
    const blob = new Blob([`${JSON.stringify(payload, null, 2)}\n`], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `workflow-sandbox-${processKey}-${simulationDate}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  useEffect(() => {
    if (variantsLoading || autoPreviewDoneRef.current || !searchParams.toString()) {
      return
    }
    autoPreviewDoneRef.current = true
    previewMutation.mutate()
  }, [previewMutation, searchParams, variantsLoading])

  if (variantsError || campaignsError) {
    return (
      <ErrorState
        error={(variantsQueryError || campaignsQueryError) as Error}
        onRetry={() => {
          void refetchVariants()
          void refetchCampaigns()
        }}
      />
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold">
          <FlaskConical className="h-7 w-7" />
          Workflow-Sandbox
        </h1>
        <p className="text-muted-foreground">
          Vorschau auf den effektiven Ablauf je Prozess, Stichtag und saisonaler Kampagne. Es werden keine produktiven Workflows gestartet.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,420px)_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Simulation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="process-key">Prozess</Label>
              <NativeSelect
                id="process-key"
                value={processKey}
                onValueChange={setProcessKey}
                options={processOptions.map((option) => ({ value: option.key, label: option.label }))}
              />
              {currentVariant?.description ? (
                <p className="text-sm text-muted-foreground">{currentVariant.description}</p>
              ) : null}
            </div>

            <div className="space-y-2">
              <Label htmlFor="simulation-date">Simulationsdatum</Label>
              <Input
                id="simulation-date"
                type="date"
                value={simulationDate}
                onChange={(event) => setSimulationDate(event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="campaign-id">Saisonkampagne</Label>
              <NativeSelect
                id="campaign-id"
                value={campaignId}
                onValueChange={setCampaignId}
                options={[
                  { value: 'all', label: 'Automatisch pruefen' },
                  ...visibleCampaigns.map((campaign) => ({ value: campaign.id, label: campaign.name })),
                ]}
              />
              <p className="text-sm text-muted-foreground">
                {campaignsLoading ? 'Lade Kampagnen...' : `${visibleCampaigns.length} Kampagnen fuer diesen Prozess gefunden.`}
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="product-group">Produktgruppe optional</Label>
              <Input
                id="product-group"
                value={productGroup}
                onChange={(event) => setProductGroup(event.target.value)}
                placeholder="z. B. weizen"
              />
            </div>

            <Button
              type="button"
              className="w-full"
              onClick={() => previewMutation.mutate()}
              disabled={variantsLoading || previewMutation.isPending}
            >
              <Play className="mr-2 h-4 w-4" />
              Vorschau berechnen
            </Button>
          </CardContent>
        </Card>

        <div className="space-y-6">
          {variantsLoading ? <LoadingState message="Prozessvarianten werden geladen..." /> : null}

          {!variantsLoading && !previewMutation.data && !previewMutation.isPending ? (
            <Card className="border-dashed">
              <CardContent className="pt-6 text-sm text-muted-foreground">
                Waehlen Sie Prozess, Datum und optional eine Kampagne, um den effektiven Workflow als Sandbox-Preview zu sehen.
              </CardContent>
            </Card>
          ) : null}

          {previewMutation.isError ? (
            <ErrorState
              error={previewMutation.error as Error}
              onRetry={() => previewMutation.mutate()}
              compact
            />
          ) : null}

          {previewMutation.data ? (
            <>
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <CardTitle>Ablaufvorschau</CardTitle>
                    <Button type="button" variant="outline" size="sm" className="gap-2" onClick={handleExportPreview}>
                      <Download className="h-4 w-4" />
                      JSON exportieren
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline">{previewMutation.data.process_key}</Badge>
                    <Badge variant="secondary">{previewMutation.data.simulation_date}</Badge>
                    <Badge variant={previewMutation.data.matched_campaigns.some((campaign) => campaign.in_window) ? 'default' : 'secondary'}>
                      {previewMutation.data.matched_campaigns.some((campaign) => campaign.in_window) ? 'Saison aktiv' : 'Keine aktive Saison'}
                    </Badge>
                  </div>
                  {previewMutation.data.description ? (
                    <p className="text-sm text-muted-foreground">{previewMutation.data.description}</p>
                  ) : null}

                  <div className="space-y-3">
                    {previewMutation.data.steps.map((step, index) => {
                      const roles = previewMutation.data.required_roles[step] || []
                      const sla = previewMutation.data.step_sla[step]
                      return (
                        <div key={step} className="rounded-lg border p-4">
                          <div className="flex items-center justify-between gap-3">
                            <div>
                              <p className="text-sm text-muted-foreground">Schritt {index + 1}</p>
                              <p className="font-medium">{step}</p>
                            </div>
                            {sla?.timeout_hours ? (
                              <Badge variant="outline">SLA {sla.timeout_hours}h</Badge>
                            ) : null}
                          </div>
                          {roles.length > 0 ? (
                            <p className="mt-2 text-sm text-muted-foreground">
                              Rollen: {roles.join(', ')}
                            </p>
                          ) : null}
                          {sla?.escalation_roles?.length ? (
                            <p className="mt-1 text-sm text-muted-foreground">
                              Eskalation: {sla.escalation_roles.join(', ')}
                            </p>
                          ) : null}
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Saisonabgleich</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {previewMutation.data.matched_campaigns.length === 0 ? (
                    <p className="text-sm text-muted-foreground">Keine passende Kampagne gefunden.</p>
                  ) : (
                    previewMutation.data.matched_campaigns.map((campaign) => (
                      <div key={campaign.id} className="rounded-lg border p-4">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="font-medium">{campaign.name}</p>
                          <Badge variant={campaign.in_window ? 'default' : 'secondary'}>
                            {campaign.in_window ? 'im Fenster' : 'ausserhalb'}
                          </Badge>
                          <Badge variant={campaign.product_group_match ? 'outline' : 'secondary'}>
                            {campaign.product_group_match ? 'Produktgruppe passend' : 'Produktgruppe abweichend'}
                          </Badge>
                        </div>
                        <p className="mt-1 text-sm text-muted-foreground">
                          {campaign.start_date} bis {campaign.end_date}
                        </p>
                        {campaign.product_groups.length > 0 ? (
                          <p className="mt-1 text-sm text-muted-foreground">
                            Produktgruppen: {campaign.product_groups.join(', ')}
                          </p>
                        ) : null}
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>

              {previewMutation.data.warnings.length > 0 ? (
                <Card className="border-amber-300 bg-amber-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-amber-950">
                      <ShieldAlert className="h-5 w-5" />
                      Hinweise
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm text-amber-950">
                    {previewMutation.data.warnings.map((warning) => (
                      <p key={warning}>{warning}</p>
                    ))}
                  </CardContent>
                </Card>
              ) : null}
            </>
          ) : null}
        </div>
      </div>
    </div>
  )
}
