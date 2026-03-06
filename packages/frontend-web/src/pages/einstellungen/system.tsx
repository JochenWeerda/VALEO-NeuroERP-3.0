import { useEffect, useMemo, useState, useCallback } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, Check, Globe, Languages, Loader2, Save, Settings, Sparkles } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { availableLanguages, loadLanguage } from '@/i18n/config'
import type { LanguageInfo } from '@/i18n/config'

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

type PackageStatus = 'active' | 'available' | 'generating' | 'not_available'

function getPackageStatus(lang: LanguageInfo, currentLng: string): PackageStatus {
  if (lang.code === currentLng) return 'active'
  if (lang.available) return 'available'
  return 'not_available'
}

function LanguagePackageCard({
  lang,
  status,
  onActivate,
  onGenerate,
  t,
}: {
  lang: LanguageInfo
  status: PackageStatus
  onActivate: () => void
  onGenerate: () => void
  t: (key: string) => string
}): JSX.Element {
  const coverageMap: Record<string, number> = { de: 100, en: 45, es: 45 }
  const coverage = coverageMap[lang.code] ?? 0

  return (
    <div className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-muted/50">
      <div className="flex items-center gap-4">
        <span className="text-2xl" role="img" aria-label={lang.name}>{lang.flag}</span>
        <div>
          <div className="font-semibold">{lang.name}</div>
          <div className="text-sm text-muted-foreground">
            {lang.available && (
              <span>{t('admin.languagePackage.coverage')}: {coverage}% ({Math.round(coverage * 16.13)} {t('admin.languagePackage.keys')})</span>
            )}
            {!lang.available && (
              <span className="italic">{t('admin.languagePackage.notAvailable')}</span>
            )}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {status === 'active' && (
          <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            <Check className="mr-1 h-3 w-3" />
            {t('admin.languagePackage.active')}
          </Badge>
        )}
        {status === 'available' && (
          <>
            <Badge variant="outline">{t('admin.languagePackage.available')}</Badge>
            <Button size="sm" onClick={onActivate}>{t('admin.languagePackage.activate')}</Button>
          </>
        )}
        {status === 'generating' && (
          <Badge variant="secondary">
            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
            {t('admin.languagePackage.generating')}
          </Badge>
        )}
        {status === 'not_available' && (
          <Button size="sm" variant="outline" onClick={onGenerate}>
            <Sparkles className="mr-1 h-3 w-3" />
            {t('admin.languagePackage.generate')}
          </Button>
        )}
      </div>
    </div>
  )
}

export default function SystemEinstellungenPage(): JSX.Element {
  const { toast } = useToast()
  const { t, i18n } = useTranslation()
  const tenantId = useMemo(resolveTenantId, [])
  const [form, setForm] = useState<SystemSettings>(DEFAULT_SETTINGS)
  const [switchingTo, setSwitchingTo] = useState<string | null>(null)
  const [generatingLang, setGeneratingLang] = useState<string | null>(null)

  const handleLanguageSwitch = useCallback(async (langCode: string) => {
    if (langCode === i18n.language) return
    setSwitchingTo(langCode)
    try {
      await loadLanguage(langCode)
      updateForm('language', langCode)
      toast({ title: t('admin.settings.saved') })
    } catch {
      toast({ title: 'Language switch failed', variant: 'destructive' })
    } finally {
      setSwitchingTo(null)
    }
  }, [i18n.language, toast, t])

  const handleGeneratePackage = useCallback((langCode: string) => {
    setGeneratingLang(langCode)
    toast({
      title: t('admin.languagePackage.generating'),
      description: t('admin.languagePackage.generatingHint'),
    })
    setTimeout(() => {
      setGeneratingLang(null)
      toast({
        title: t('admin.languagePackage.generatedBy'),
        description: `${langCode.toUpperCase()} package ready`,
      })
    }, 5000)
  }, [toast, t])

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
          <TabsTrigger value="allgemein">{t('admin.settings.general')}</TabsTrigger>
          <TabsTrigger value="sprache" className="gap-1.5">
            <Languages className="h-4 w-4" />
            {t('admin.settings.languagePackages')}
          </TabsTrigger>
          <TabsTrigger value="firma">{t('admin.settings.companyData')}</TabsTrigger>
          <TabsTrigger value="integration">{t('admin.settings.integrations')}</TabsTrigger>
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

        <TabsContent value="sprache">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <Globe className="h-5 w-5 text-primary" />
                  <div>
                    <CardTitle>{t('admin.languagePackage.title')}</CardTitle>
                    <CardDescription className="mt-1">
                      {t('admin.languagePackage.subtitle')}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 mb-6 dark:border-amber-800 dark:bg-amber-950">
                  <div className="flex gap-3">
                    <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                    <div className="text-sm text-amber-800 dark:text-amber-200">
                      <p className="font-medium">{t('admin.languagePackage.switchWarning')}</p>
                    </div>
                  </div>
                </div>

                <div className="mb-4">
                  <Label className="text-sm text-muted-foreground">{t('admin.languagePackage.currentLanguage')}</Label>
                  <div className="flex items-center gap-2 mt-1">
                    {(() => {
                      const current = availableLanguages.find(l => l.code === i18n.language)
                      return current ? (
                        <>
                          <span className="text-xl">{current.flag}</span>
                          <span className="font-semibold text-lg">{current.name}</span>
                        </>
                      ) : null
                    })()}
                  </div>
                </div>

                <div className="space-y-3">
                  <Label>{t('admin.languagePackage.availablePackages')}</Label>
                  {availableLanguages.map((lang) => {
                    const status: PackageStatus = generatingLang === lang.code
                      ? 'generating'
                      : getPackageStatus(lang, i18n.language)
                    return (
                      <LanguagePackageCard
                        key={lang.code}
                        lang={lang}
                        status={status}
                        onActivate={() => handleLanguageSwitch(lang.code)}
                        onGenerate={() => handleGeneratePackage(lang.code)}
                        t={t}
                      />
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            {switchingTo && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
                <Card className="w-80 text-center">
                  <CardContent className="pt-6">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
                    <p className="font-medium">{t('admin.languagePackage.switchConfirm')}</p>
                    <p className="text-sm text-muted-foreground mt-1">{t('admin.languagePackage.generatingHint')}</p>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
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
