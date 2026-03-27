/**
 * Erntefenster-Konfiguration (Gap 005: Saisonale Kampagnenprozesse als Vorlagen)
 * Konfig-UI für neue Kampagne aus Vorlage – Setup-Zeit <30 min
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Calendar, Check, FlaskConical, Loader2, Sprout } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { ErrorState } from '@/components/ErrorState'

type ErntefensterTemplate = {
  id: string
  name: string
  description: string
  process_key: string
  default_start_mmdd: string
  default_end_mmdd: string
  product_groups: string[]
}

type ErntefensterCampaign = {
  id: string
  template_id: string
  name: string
  start_date: string
  end_date: string
  process_key: string
  product_groups: string[]
  created_at: string
}

type SettlementSummary = {
  id: string
  settlement_number: string
  campaign_id?: string | null
  net_amount_eur: number
  total_deductions_eur: number
  approval_status: string
  status: string
  created_at?: string | null
}

type SettlementCampaignBackfillResult = {
  campaign_id: string
  matched_count: number
  updated_count: number
  ambiguous_count: number
  skipped_count: number
}

const API_BASE = '/api/v1/admin'

export default function ErntefensterKonfigPage(): JSX.Element {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const currentYear = new Date().getFullYear()

  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('')
  const [campaignName, setCampaignName] = useState<string>('')
  const [year, setYear] = useState<number>(currentYear)
  const [startMmdd, setStartMmdd] = useState<string>('')
  const [endMmdd, setEndMmdd] = useState<string>('')

  const { data: templates = [], isLoading: templatesLoading, isError: templatesError, error: templatesErr } = useQuery({
    queryKey: ['erntefenster-templates'],
    queryFn: async () => {
      const r = await apiClient.get<ErntefensterTemplate[]>(`${API_BASE}/erntefenster-templates`)
      return Array.isArray(r.data) ? r.data : []
    },
    initialData: [],
  })

  const { data: campaigns = [], isLoading: campaignsLoading, isError: campaignsError, error: campaignsErr, refetch } = useQuery({
    queryKey: ['erntefenster-campaigns'],
    queryFn: async () => {
      const r = await apiClient.get<ErntefensterCampaign[]>(`${API_BASE}/erntefenster-campaigns`)
      return Array.isArray(r.data) ? r.data : []
    },
    initialData: [],
  })

  const { data: settlements = [] } = useQuery({
    queryKey: ['agrar-settlement-summaries'],
    queryFn: async () => {
      const r = await apiClient.get<SettlementSummary[]>('/api/v1/agrar/settlements')
      return Array.isArray(r.data) ? r.data : []
    },
    initialData: [],
  })

  const createMutation = useMutation({
    mutationFn: async (payload: { template_id: string; name: string; year: number; start_mmdd?: string; end_mmdd?: string }) => {
      const r = await apiClient.post<ErntefensterCampaign>(`${API_BASE}/erntefenster-from-template`, payload)
      return r.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['erntefenster-campaigns'] })
      toast({ title: 'Kampagne erstellt', description: 'Die Erntefenster-Kampagne wurde erfolgreich angelegt.' })
      setCampaignName('')
      setSelectedTemplateId('')
      setStartMmdd('')
      setEndMmdd('')
    },
    onError: (err: Error) => {
      toast({ variant: 'destructive', title: 'Fehler', description: err.message })
    },
  })

  const backfillMutation = useMutation({
    mutationFn: async (campaignId: string) => {
      const r = await apiClient.post<SettlementCampaignBackfillResult>('/api/v1/agrar/settlements/campaign-reference/backfill', {
        campaign_id: campaignId,
      })
      return r.data
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['agrar-settlement-summaries'] })
      toast({
        title: 'Alt-Daten geprueft',
        description:
          result.updated_count > 0
            ? `${result.updated_count} Alt-Settlements wurden der Kampagne zugeordnet.`
            : result.ambiguous_count > 0
              ? `${result.ambiguous_count} Alt-Settlements bleiben wegen ueberlappender Kampagnen offen.`
              : 'Keine Alt-Settlements fuer diese Kampagne gefunden.',
      })
    },
    onError: (err: Error) => {
      toast({ variant: 'destructive', title: 'Backfill fehlgeschlagen', description: err.message })
    },
  })

  const selectedTemplate = templates.find((t) => t.id === selectedTemplateId)

  const campaignSummaries = campaigns.map((campaign) => {
    const matchingSettlements = settlements.filter((settlement) => {
      if (settlement.campaign_id) {
        return settlement.campaign_id === campaign.id
      }
      if (!settlement.created_at) return false
      const createdAt = String(settlement.created_at).slice(0, 10)
      return createdAt >= campaign.start_date && createdAt <= campaign.end_date
    })
    const netTotal = matchingSettlements.reduce((sum, settlement) => sum + settlement.net_amount_eur, 0)
    const deductionTotal = matchingSettlements.reduce((sum, settlement) => sum + settlement.total_deductions_eur, 0)
    const legacySettlementCount = matchingSettlements.filter((settlement) => !settlement.campaign_id).length
    const openSettlements = matchingSettlements.filter(
      (settlement) => settlement.status !== 'posted' || settlement.approval_status !== 'VERBUCHT',
    ).length
    const nowIso = new Date().toISOString().slice(0, 10)
    const closureState =
      matchingSettlements.length === 0
        ? 'Keine Settlements'
        : openSettlements > 0
          ? 'Abschluss offen'
          : campaign.end_date <= nowIso
            ? 'Abschlussbereit'
            : 'Laufend'

    return { campaign, matchingSettlements, netTotal, deductionTotal, legacySettlementCount, openSettlements, closureState }
  })

  const openSandboxPreview = (params: {
    processKey: string
    simulationDate: string
    campaignId?: string
    productGroup?: string
  }): void => {
    const searchParams = new URLSearchParams({
      process: params.processKey,
      date: params.simulationDate,
    })
    if (params.campaignId) {
      searchParams.set('campaign', params.campaignId)
    }
    if (params.productGroup) {
      searchParams.set('productGroup', params.productGroup)
    }
    navigate(`/workflow/workflow-sandbox?${searchParams.toString()}`)
  }

  const openSettlementReview = (campaign: ErntefensterCampaign): void => {
    const searchParams = new URLSearchParams({
      campaignId: campaign.id,
      campaignName: campaign.name,
      campaignStart: campaign.start_date,
      campaignEnd: campaign.end_date,
    })
    navigate(`/annahme/abrechnung?${searchParams.toString()}`)
  }

  const handleTemplateSelect = (id: string): void => {
    setSelectedTemplateId(id)
    const t = templates.find((x) => x.id === id)
    if (t) {
      setCampaignName(`${t.name} ${year}`)
      setStartMmdd(t.default_start_mmdd)
      setEndMmdd(t.default_end_mmdd)
    }
  }

  const handleSubmit = (e: React.FormEvent): void => {
    e.preventDefault()
    if (!selectedTemplateId || !campaignName.trim()) {
      toast({ variant: 'destructive', title: 'Bitte Vorlage und Namen angeben.' })
      return
    }
    createMutation.mutate({
      template_id: selectedTemplateId,
      name: campaignName.trim(),
      year,
      start_mmdd: startMmdd || undefined,
      end_mmdd: endMmdd || undefined,
    })
  }

  if (templatesError) {
    return <ErrorState error={templatesErr as Error} onRetry={() => queryClient.invalidateQueries({ queryKey: ['erntefenster-templates'] })} />
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold flex items-center gap-2">
          <Sprout className="h-6 w-6" />
          Erntefenster-Konfiguration
        </h1>
        <p className="mt-1 text-muted-foreground">
          Saisonale Kampagnenprozesse als Vorlagen – neue Kampagne in wenigen Minuten einrichten (Gap 005).
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Neue Kampagne aus Vorlage</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="template">Vorlage wählen</Label>
              <div className="mt-1">
                <NativeSelect
                  id="template"
                  value={selectedTemplateId}
                  onValueChange={handleTemplateSelect}
                  placeholder="Vorlage auswaehlen..."
                  options={templates.map((template) => ({
                    value: template.id,
                    label: `${template.name} (${template.default_start_mmdd} - ${template.default_end_mmdd})`,
                  }))}
                />
              </div>
              {selectedTemplate && (
                <div className="mt-2 space-y-2">
                  <p className="text-sm text-muted-foreground">{selectedTemplate.description}</p>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="gap-2"
                    onClick={() =>
                      openSandboxPreview({
                        processKey: selectedTemplate.process_key,
                        simulationDate: `${year}-${startMmdd || selectedTemplate.default_start_mmdd}`,
                        productGroup: selectedTemplate.product_groups[0],
                      })
                    }
                  >
                    <FlaskConical className="h-4 w-4" />
                    Vorlage in Sandbox prüfen
                  </Button>
                </div>
              )}
            </div>

            <div>
              <Label htmlFor="name">Kampagnenname</Label>
              <Input
                id="name"
                value={campaignName}
                onChange={(e) => setCampaignName(e.target.value)}
                placeholder="z.B. Raps-Ernte 2026"
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="year">Jahr</Label>
              <Input
                id="year"
                type="number"
                min={2020}
                max={2030}
                value={year}
                onChange={(e) => setYear(parseInt(e.target.value, 10) || currentYear)}
                className="mt-1"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="start">Start (MM-DD)</Label>
                <Input
                  id="start"
                  value={startMmdd}
                  onChange={(e) => setStartMmdd(e.target.value)}
                  placeholder="07-01"
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="end">Ende (MM-DD)</Label>
                <Input
                  id="end"
                  value={endMmdd}
                  onChange={(e) => setEndMmdd(e.target.value)}
                  placeholder="08-31"
                  className="mt-1"
                />
              </div>
            </div>

            <Button type="submit" disabled={createMutation.isPending || !selectedTemplateId || !campaignName.trim()}>
              {createMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Wird erstellt...
                </>
              ) : (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Kampagne erstellen
                </>
              )}
            </Button>
          </form>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Bestehende Kampagnen
          </h2>
          {campaignsLoading ? (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Lade Kampagnen...</span>
            </div>
          ) : campaignsError ? (
            <ErrorState error={campaignsErr as Error} onRetry={() => void refetch()} compact />
          ) : campaignSummaries.length === 0 ? (
            <p className="text-sm text-muted-foreground">Noch keine Kampagnen angelegt.</p>
          ) : (
            <ul className="space-y-3">
              {campaignSummaries.map(({ campaign, matchingSettlements, netTotal, deductionTotal, legacySettlementCount, openSettlements, closureState }) => (
                <li key={campaign.id} className="rounded-md border p-3 text-sm">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium">{campaign.name}</p>
                      <p className="text-muted-foreground">
                        {campaign.start_date} – {campaign.end_date} · {campaign.process_key}
                      </p>
                    </div>
                    <span className="rounded-full border px-2 py-1 text-xs font-medium">
                      {closureState}
                    </span>
                  </div>
                  <div className="mt-3 grid gap-2 md:grid-cols-3">
                    <div className="rounded-md bg-muted/40 p-2">
                      <div className="text-xs text-muted-foreground">Settlements</div>
                      <div className="text-lg font-semibold">{matchingSettlements.length}</div>
                    </div>
                    <div className="rounded-md bg-muted/40 p-2">
                      <div className="text-xs text-muted-foreground">Netto gesamt</div>
                      <div className="text-lg font-semibold">{netTotal.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</div>
                    </div>
                    <div className="rounded-md bg-muted/40 p-2">
                      <div className="text-xs text-muted-foreground">Offene Settlements</div>
                      <div className="text-lg font-semibold">{openSettlements}</div>
                    </div>
                  </div>
                  <p className="mt-2 text-xs text-muted-foreground">
                    Abzuege gesamt: {deductionTotal.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                  </p>
                  {legacySettlementCount > 0 && (
                    <p className="mt-1 text-xs text-amber-700">
                      {legacySettlementCount} Alt-Settlement(s) nutzen noch den Datumsfenster-Fallback.
                    </p>
                  )}
                  {campaign.product_groups.length > 0 && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Produktgruppen: {campaign.product_groups.join(', ')}
                    </p>
                  )}
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => openSettlementReview(campaign)}
                    >
                      Settlement-Abschluss pruefen
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="gap-2"
                      onClick={() =>
                        openSandboxPreview({
                          processKey: campaign.process_key,
                          simulationDate: campaign.start_date,
                          campaignId: campaign.id,
                          productGroup: campaign.product_groups[0],
                        })
                      }
                    >
                      <FlaskConical className="h-4 w-4" />
                      In Sandbox prüfen
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      disabled={legacySettlementCount === 0 || backfillMutation.isPending}
                      onClick={() => backfillMutation.mutate(campaign.id)}
                    >
                      {backfillMutation.isPending ? 'Ordnet zu...' : 'Alt-Daten zuordnen'}
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  )
}
