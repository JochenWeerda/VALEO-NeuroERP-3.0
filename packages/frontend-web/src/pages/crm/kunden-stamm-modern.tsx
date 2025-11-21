/**
 * Kunden-Stamm Modern
 * Nutzt die L3 Mask-Builder Konfiguration mit responsive UI und AI-Features
 */

import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { convertL3MaskToMaskConfig, l3MaskConfig, type L3MaskConfig } from '@/components/mask-builder/adapters/l3-mask-adapter'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useToast } from '@/hooks/use-toast'
import {
  CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
  ENABLE_CUSTOMER_MASK_BUILDER_FORM,
  validateCustomerPayload,
} from '@/features/crm-masks/customer-mask-support'
import {
  getNested,
  mapCustomerToMask,
  mapMaskToCustomer,
  type MaskCustomerData,
} from '@/features/crm-masks/mappers'
import { useCustomer, useUpdateCustomer } from '@/lib/api/crm'
import {
  Sparkles,
  Wand2,
  Smartphone,
  Shield,
  Zap,
  Loader2,
  ArrowLeft,
} from 'lucide-react'

export default function KundenStammModern() {
  if (ENABLE_CUSTOMER_MASK_BUILDER_FORM) {
    return <CustomerMaskEditPage />
  }
  return <LegacyKundenStammModern />
}

function CustomerMaskEditPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()
  const { data: customer, isLoading, error } = useCustomer(id ?? '')
  const updateCustomer = useUpdateCustomer()
  const [maskData, setMaskData] = useState<MaskCustomerData | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const editMaskConfig = useMemo(
    () => ({
      ...CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
      title: 'Kundenstamm bearbeiten',
    }),
    [],
  )

  useEffect(() => {
    if (customer) {
      setMaskData(mapCustomerToMask(customer))
    }
  }, [customer])

  const handleMaskSave = async (data: MaskCustomerData): Promise<void> => {
    if (!id) {
      setFormError('Keine Kunden-ID angegeben.')
      return
    }

    const payload = mapMaskToCustomer(data)
    const validationError = validateCustomerPayload(payload)
    if (validationError) {
      setFormError(validationError)
      return
    }

    setFormError(null)

    try {
      await updateCustomer.mutateAsync({ id, data: payload })
      setMaskData(data)
      const customerNumber = getNested<string>(payload, 'customer.customer_number') ?? ''
      const customerName = getNested<string>(payload, 'customer.name1') ?? ''
      toast({
        title: 'Kunde aktualisiert',
        description: `${customerName || 'Kunde'} (${customerNumber}) wurde erfolgreich gespeichert.`,
      })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Aktualisierung fehlgeschlagen.'
      setFormError(message)
    }
  }

  if (!id) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Keine Kunden-ID</AlertTitle>
          <AlertDescription>Bitte rufen Sie die Seite mit einer gültigen Kunden-ID auf.</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (error) {
    const message = error instanceof Error ? error.message : 'Fehler beim Laden des Kunden.'
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Fehler</AlertTitle>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (isLoading || !maskData) {
    return (
      <div className="flex items-center justify-center p-10">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2 text-sm text-muted-foreground">Kundenmaske wird geladen…</span>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-1">CRM &gt; Kunden</p>
          <h1 className="text-3xl font-bold">{customer?.name ?? 'Kundenstamm bearbeiten'}</h1>
          <p className="text-muted-foreground">Mask Builder Formular (Beta)</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(-1)} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Zurück
          </Button>
        </div>
      </div>

      {formError ? (
        <Alert variant="destructive">
          <AlertTitle>Speichern fehlgeschlagen</AlertTitle>
          <AlertDescription>{formError}</AlertDescription>
        </Alert>
      ) : null}

      <ObjectPage
        config={editMaskConfig}
        data={maskData}
        onChange={setMaskData}
        onSave={handleMaskSave}
        onCancel={() => navigate(-1)}
      />
    </div>
  )
}

function LegacyKundenStammModern() {
  const navigate = useNavigate()
  const [maskConfig] = useState(convertL3MaskToMaskConfig())
  const l3Config = l3MaskConfig as unknown as L3MaskConfig
  const [aiEnabled] = useState(l3Config.ai?.enabled || false)
  const [responsiveMode, setResponsiveMode] = useState<'sm' | 'md' | 'lg'>('lg')

  // Emuliere Customer-Daten (später vom Backend)
  const [customerData, setCustomerData] = useState({
    'party.name.primary': '',
    'party.name.additional1': '',
    'party.name.additional2': '',
    'contact.salutation': '',
    'contact.letter_salutation': '',
    'contact.phone_primary': '',
    'contact.phone_secondary': '',
    'contact.email': '',
    'contact.homepage': '',
    'address.main.street': '',
    'address.main.postcode': '',
    'address.main.city': '',
    'address.main.country': 'DE',
    'tax.vat_id': '',
    'tax.tax_number': '',
    'customer.status': 'active',
    'customer.account_manager': '',
    'customer.abc_class': '',
    'customer.customer_group': ''
  })

  // Responsive Breakpoints
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth
      if (width < 640) setResponsiveMode('sm')
      else if (width < 1024) setResponsiveMode('md')
      else setResponsiveMode('lg')
    }
    
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // AI Intent Bar Handler
  const handleIntentAction = async (actionId: string) => {
    console.log(`AI Intent: ${actionId}`)

    switch (actionId) {
      case 'gen_letter_salutation': {
        // Generiere Briefanrede aus Anrede + Name
        const salutation = customerData['contact.salutation'] || 'Herr'
        const name = customerData['party.name.primary'] || ''
        setCustomerData({
          ...customerData,
          'contact.letter_salutation': `${salutation} ${name}`
        })
        break
      }

      case 'validate_vat':
        // VAT-Validierung via VIES
        const vatId = customerData['tax.vat_id']
        if (vatId) {
          try {
            const response = await fetch(`/api/vies/validate/${encodeURIComponent(vatId)}`)
            const result = await response.json()
            if (result.valid) {
              toast({
                title: 'USt-ID gültig',
                description: `USt-ID ${vatId} wurde erfolgreich validiert.`,
              })
            } else {
              toast({
                title: 'USt-ID ungültig',
                description: result.error || 'USt-ID konnte nicht validiert werden.',
                variant: 'destructive',
              })
            }
          } catch (error) {
            console.error('VIES validation failed:', error)
            toast({
              title: 'Validierung fehlgeschlagen',
              description: 'USt-ID konnte nicht überprüft werden.',
              variant: 'destructive',
            })
          }
        } else {
          toast({
            title: 'Keine USt-ID',
            description: 'Bitte geben Sie eine USt-ID ein.',
            variant: 'destructive',
          })
        }
        break

      case 'detect_duplicates':
        // Dubletten-Erkennung
        console.log('Checking for duplicates...')
        // TODO: Implementiere Duplicate-Detection
        break

      case 'summarize_customer':
        // Kunden-Zusammenfassung
        console.log('Generating customer summary...')
        // TODO: Implementiere RAG-Panel
        break

      default:
        console.log(`Unknown action: ${actionId}`)
    }
  }

  // Keyboard Shortcut für Intent Bar (Mod+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        // TODO: Öffne Intent Bar
        console.log('Intent Bar opened')
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header mit AI-Features Info */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kunden-Stamm Modern</h1>
          <p className="text-muted-foreground">
            Nutzt Mask-Builder mit responsive UI und AI-Features
          </p>
        </div>
        
        <div className="flex gap-2">
          {aiEnabled && (
            <Badge variant="secondary" className="gap-2">
              <Sparkles className="h-4 w-4" />
              AI aktiviert
            </Badge>
          )}
          <Badge variant="outline">
            {responsiveMode === 'sm' && <Smartphone className="h-4 w-4 mr-1" />}
            {responsiveMode === 'md' && <Smartphone className="h-4 w-4 mr-1" />}
            {responsiveMode === 'lg' && <Smartphone className="h-4 w-4 mr-1" />}
            {responsiveMode.toUpperCase()}
          </Badge>
        </div>
      </div>

      {/* Feature Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Zap className="h-4 w-4 text-yellow-500" />
              Responsive UI
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {responsiveMode === 'sm' && 'Mobile: 1 Spalte, Bottom-Nav'}
              {responsiveMode === 'md' && 'Tablet: 2 Spalten, Side-Nav'}
              {responsiveMode === 'lg' && 'Desktop: 3 Spalten, Side-Nav'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Wand2 className="h-4 w-4 text-purple-500" />
              AI-Assistenz
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Briefanrede automatisch generieren
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-500" />
              Validierung
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              USt-ID Prüfung via VIES
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-500" />
              Intent Bar
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              ⌘K für AI-Aktionen
            </p>
          </CardContent>
        </Card>
      </div>

      {/* AI Intent Bar Quick Actions */}
      {aiEnabled && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">AI-Schnellaktionen</CardTitle>
            <CardDescription>
              Nutze die folgenden Actions für schnelle AI-Unterstützung
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {l3Config.ai?.intentBar?.actions.map((action) => (
                <Button
                  key={action.id}
                  variant="outline"
                  size="sm"
                  onClick={() => handleIntentAction(action.id)}
                >
                  {action.label}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Mask Builder ObjectPage */}
      <Card>
        <CardHeader>
          <CardTitle>{maskConfig.title}</CardTitle>
          <CardDescription>{maskConfig.subtitle}</CardDescription>
        </CardHeader>
        <CardContent>
          <ObjectPage
            config={maskConfig}
            data={customerData}
            onChange={(data) => setCustomerData(data)}
            onSave={async (data) => {
              console.log('Saving customer:', data)
              // TODO: Implementiere Save-Logik
            }}
            onCancel={() => navigate('/crm/customers')}
          />
        </CardContent>
      </Card>

      {/* Footer Actions */}
      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={() => navigate('/crm/customers')}>
          Abbrechen
        </Button>
        <Button onClick={() => console.log('Save clicked')}>
          Speichern
        </Button>
      </div>
    </div>
  )
}
