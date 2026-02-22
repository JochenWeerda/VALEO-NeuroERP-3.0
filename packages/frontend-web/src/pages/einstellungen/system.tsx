import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Loader2, Save, Settings } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

type TenantResponse = {
  id: string
  settings?: string | null
}

type SystemSettings = {
  language: string
  timezone: string
  currency: string
  companyName: string
  taxNumber: string
  commercialRegister: string
  address: string
  integrations: {
    datev: boolean
    banking: boolean
    weather: boolean
  }
}

const DEFAULT_SETTINGS: SystemSettings = {
  language: 'de',
  timezone: 'Europe/Berlin',
  currency: 'EUR',
  companyName: '',
  taxNumber: '',
  commercialRegister: '',
  address: '',
  integrations: {
    datev: false,
    banking: false,
    weather: false,
  },
}

const DEFAULT_TENANT_ID = import.meta.env.VITE_TENANT_ID || '00000000-0000-0000-0000-000000000001'

const resolveTenantId = (): string => {
  return (
    window.localStorage.getItem('tenant_id')
    || window.sessionStorage.getItem('tenant_id')
    || DEFAULT_TENANT_ID
  )
}

const parseSystemSettings = (raw: string | null | undefined): SystemSettings => {
  if (!raw) return DEFAULT_SETTINGS
  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>
    const uiSettings = (parsed.ui_settings || parsed.uiSettings || {}) as Record<string, unknown>
    const company = (parsed.company || {}) as Record<string, unknown>
    const integrations = (parsed.integrations || {}) as Record<string, unknown>

    return {
      language: String(uiSettings.language || DEFAULT_SETTINGS.language),
      timezone: String(uiSettings.timezone || DEFAULT_SETTINGS.timezone),
      currency: String(uiSettings.currency || DEFAULT_SETTINGS.currency),
      companyName: String(company.name || DEFAULT_SETTINGS.companyName),
      taxNumber: String(company.taxNumber || ''),
      commercialRegister: String(company.commercialRegister || ''),
      address: String(company.address || ''),
      integrations: {
        datev: Boolean(integrations.datev),
        banking: Boolean(integrations.banking),
        weather: Boolean(integrations.weather),
      },
    }
  } catch {
    return DEFAULT_SETTINGS
  }
}

const encodeSystemSettings = (value: SystemSettings): string => {
  return JSON.stringify({
    ui_settings: {
      language: value.language,
      timezone: value.timezone,
      currency: value.currency,
    },
    company: {
      name: value.companyName,
      taxNumber: value.taxNumber,
      commercialRegister: value.commercialRegister,
      address: value.address,
    },
    integrations: value.integrations,
  })
}

export default function SystemEinstellungenPage(): JSX.Element {
  const { toast } = useToast()
  const tenantId = useMemo(resolveTenantId, [])
  const [form, setForm] = useState<SystemSettings>(DEFAULT_SETTINGS)

  const tenantQuery = useQuery({
    queryKey: ['settings', 'tenant', tenantId],
    queryFn: async () => {
      const response = await apiClient.get<TenantResponse>(`/api/v1/tenants/${tenantId}`)
      return response.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: async (nextSettings: SystemSettings) => {
      await apiClient.put(`/api/v1/tenants/${tenantId}`, {
        settings: encodeSystemSettings(nextSettings),
      })
    },
    onSuccess: async () => {
      toast({ title: 'Einstellungen gespeichert' })
      await tenantQuery.refetch()
    },
    onError: (error) => {
      toast({
        title: 'Speichern fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    },
  })

  const updateForm = <K extends keyof SystemSettings>(key: K, value: SystemSettings[K]): void => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const isLoading = tenantQuery.isLoading
  const isSaving = saveMutation.isPending

  useEffect(() => {
    if (tenantQuery.data) {
      setForm(parseSystemSettings(tenantQuery.data.settings))
    }
  }, [tenantQuery.data])

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Settings className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">System-Einstellungen</h1>
              <p className="text-muted-foreground">Konfiguration</p>
            </div>
          </div>
        </div>
        <Button className="gap-2" onClick={() => saveMutation.mutate(form)} disabled={isLoading || isSaving}>
          {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
          Speichern
        </Button>
      </div>

      <Tabs defaultValue="allgemein">
        <TabsList>
          <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
          <TabsTrigger value="firma">Firmendaten</TabsTrigger>
          <TabsTrigger value="integration">Integrationen</TabsTrigger>
        </TabsList>

        <TabsContent value="allgemein">
          <Card>
            <CardHeader>
              <CardTitle>Allgemeine Einstellungen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Sprache</Label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                  value={form.language}
                  onChange={(event) => updateForm('language', event.target.value)}
                  disabled={isLoading || isSaving}
                >
                  <option value="de">Deutsch</option>
                  <option value="en">English</option>
                </select>
              </div>
              <div>
                <Label>Zeitzone</Label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                  value={form.timezone}
                  onChange={(event) => updateForm('timezone', event.target.value)}
                  disabled={isLoading || isSaving}
                >
                  <option value="Europe/Berlin">Europe/Berlin (CET)</option>
                </select>
              </div>
              <div>
                <Label>Waehrung</Label>
                <Badge variant="outline" className="text-base px-4 py-2">
                  {form.currency} ({form.currency === 'EUR' ? 'EUR' : form.currency})
                </Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="firma">
          <Card>
            <CardHeader>
              <CardTitle>Firmendaten</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Firmenname</Label>
                <Input
                  value={form.companyName}
                  onChange={(event) => updateForm('companyName', event.target.value)}
                  disabled={isLoading || isSaving}
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Steuernummer</Label>
                  <Input
                    value={form.taxNumber}
                    onChange={(event) => updateForm('taxNumber', event.target.value)}
                    disabled={isLoading || isSaving}
                  />
                </div>
                <div>
                  <Label>Handelsregister</Label>
                  <Input
                    value={form.commercialRegister}
                    onChange={(event) => updateForm('commercialRegister', event.target.value)}
                    disabled={isLoading || isSaving}
                  />
                </div>
              </div>
              <div>
                <Label>Adresse</Label>
                <Input
                  value={form.address}
                  onChange={(event) => updateForm('address', event.target.value)}
                  disabled={isLoading || isSaving}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integration">
          <Card>
            <CardHeader>
              <CardTitle>API-Integrationen</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">DATEV</div>
                    <div className="text-sm text-muted-foreground">Finanzbuchhaltung</div>
                  </div>
                  <Badge variant="outline">{form.integrations.datev ? 'Verbunden' : 'Nicht verbunden'}</Badge>
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">Online-Banking</div>
                    <div className="text-sm text-muted-foreground">Zahlungsabwicklung</div>
                  </div>
                  <Badge variant="outline">{form.integrations.banking ? 'Verbunden' : 'Nicht verbunden'}</Badge>
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">Wetter-API</div>
                    <div className="text-sm text-muted-foreground">Wettervorhersage</div>
                  </div>
                  <Badge variant="outline">{form.integrations.weather ? 'Verbunden' : 'Nicht verbunden'}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
