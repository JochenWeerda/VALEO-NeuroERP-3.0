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

  const selectedTemplate = templates.find((t) => t.id === selectedTemplateId)

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
          ) : campaigns.length === 0 ? (
            <p className="text-sm text-muted-foreground">Noch keine Kampagnen angelegt.</p>
          ) : (
            <ul className="space-y-3">
              {campaigns.map((c) => (
                <li key={c.id} className="rounded-md border p-3 text-sm">
                  <p className="font-medium">{c.name}</p>
                  <p className="text-muted-foreground">
                    {c.start_date} – {c.end_date} · {c.process_key}
                  </p>
                  {c.product_groups.length > 0 && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Produktgruppen: {c.product_groups.join(', ')}
                    </p>
                  )}
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="mt-3 gap-2"
                    onClick={() =>
                      openSandboxPreview({
                        processKey: c.process_key,
                        simulationDate: c.start_date,
                        campaignId: c.id,
                        productGroup: c.product_groups[0],
                      })
                    }
                  >
                    <FlaskConical className="h-4 w-4" />
                    In Sandbox prüfen
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  )
}
