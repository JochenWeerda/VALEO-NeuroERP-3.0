import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { crmService, type Contact } from '@/lib/services/crm-service'
import { queryKeys } from '@/lib/query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { Plus, ExternalLink, Mail, Phone, ShieldCheck } from 'lucide-react'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Kunden (wird in Komponente mit i18n erstellt)
const createKundenSchema = (t: any) => z.object({
  firma: z.string().min(1, t('crud.messages.validationError')),
  anrede: z.string().optional(),
  vorname: z.string().optional(),
  nachname: z.string().min(1, t('crud.messages.validationError')),
  strasse: z.string().min(1, t('crud.messages.validationError')),
  plz: z.string().regex(/^\d{5}$/, t('crud.messages.validationError')),
  ort: z.string().min(1, t('crud.messages.validationError')),
  land: z.string().default("DE"),
  telefon: z.string().optional(),
  email: z.string().email(t('crud.messages.validationError')).optional().or(z.literal("")),
  ustId: z.string().optional(),
  steuernummer: z.string().optional(),
  steuerstatus: z.string().optional(),
  kreditlimit: z.number().min(0).default(0),
  zahlungsbedingungen: z.string().default("14 Tage"),
  rabatt: z.number().min(0).max(100).default(0),
  bonitaet: z.string().default("gut"),
  letzteBestellung: z.string().optional(),
  umsatzGesamt: z.number().min(0).default(0),
  status: z.string().default("aktiv"),
  bemerkungen: z.string().optional(),
  // Sales-spezifische Felder (nur neue, bestehende werden über bestehende Struktur verwendet)
  preisgruppe: z.string().optional(),  // NEU: sales.price_group
  steuerkategorie: z.string().optional()  // NEU: tax.category
  // Entfernt: kundensegment → verwende analytics.segment (bestehend in potential Tab)
  // Entfernt: branche → verwende profile.industry_code (bestehend in marketing Tab)
  // Entfernt: region → verwende region (bestehend in crm-core)
  // Entfernt: kundenpreisliste → verwende customer.price_list_id (bestehend in valeo-modern)
})

// Konfiguration für Kunden ObjectPage (wird in Komponente mit i18n erstellt)
const createKundenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.detail.manage', { entityType: entityTypeLabel }),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'firma',
          label: t('crud.fields.companyName'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.companyName')
        },
        {
          name: 'anrede',
          label: t('crud.fields.salutation'),
          type: 'select',
          options: [
            { value: 'herr', label: t('crud.fields.salutationMr') },
            { value: 'frau', label: t('crud.fields.salutationMrs') },
            { value: 'familie', label: t('crud.fields.salutationFamily') },
            { value: 'firma', label: t('crud.fields.salutationCompany') }
          ]
        },
        {
          name: 'vorname',
          label: t('crud.fields.firstName'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.firstName')
        },
        {
          name: 'nachname',
          label: t('crud.fields.lastName'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.lastName')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'adresse',
      label: t('crud.fields.address'),
      fields: [
        {
          name: 'strasse',
          label: t('crud.fields.street'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.street')
        },
        {
          name: 'plz',
          label: t('crud.fields.postalCode'),
          type: 'text',
          required: true,
          maxLength: 5,
          placeholder: t('crud.tooltips.placeholders.postalCode')
        },
        {
          name: 'ort',
          label: t('crud.fields.city'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.city')
        },
        {
          name: 'land',
          label: t('crud.fields.country'),
          type: 'select',
          required: true,
          options: [
            { value: 'DE', label: t('crud.fields.countryDE') },
            { value: 'AT', label: t('crud.fields.countryAT') },
            { value: 'CH', label: t('crud.fields.countryCH') },
            { value: 'NL', label: t('crud.fields.countryNL') },
            { value: 'DK', label: t('crud.fields.countryDK') },
            { value: 'PL', label: t('crud.fields.countryPL') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'kontakt',
      label: t('crud.fields.contact'),
      fields: [
        {
          name: 'telefon',
          label: t('crud.fields.phone'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.phone')
        },
        {
          name: 'email',
          label: t('crud.fields.email'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.email')
        }
      ]
    },
    {
      key: 'steuern',
      label: t('crud.fields.taxesAndLegal'),
      fields: [
        {
          name: 'ustId',
          label: t('crud.fields.vatId'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.vatId')
        },
        {
          name: 'steuernummer',
          label: t('crud.fields.taxNumber'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.taxNumber')
        },
        {
          name: 'steuerstatus',
          label: t('crud.fields.taxStatus'),
          type: 'select',
          options: [
            { value: 'standard', label: t('crud.fields.taxStatusStandard') },
            { value: 'farmer_opted', label: t('crud.fields.taxStatusFarmerOpted') },
            { value: 'farmer_flat', label: t('crud.fields.taxStatusFarmerFlat') },
            { value: 'other', label: t('crud.fields.taxStatusOther') }
          ],
          placeholder: t('crud.tooltips.placeholders.taxStatus')
        },
        {
          name: 'steuerkategorie',
          label: t('crud.fields.taxCategory'),
          type: 'select',
          options: [
            { value: 'standard', label: t('crud.fields.taxCategoryStandard') },
            { value: 'reduced', label: t('crud.fields.taxCategoryReduced') },
            { value: 'zero', label: t('crud.fields.taxCategoryZero') },
            { value: 'reverse_charge', label: t('crud.fields.taxCategoryReverseCharge') },
            { value: 'exempt', label: t('crud.fields.taxCategoryExempt') }
          ],
          placeholder: t('crud.tooltips.placeholders.taxCategory')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'konditionen',
      label: t('crud.fields.terms'),
      fields: [
        {
          name: 'kreditlimit',
          label: t('crud.fields.creditLimit'),
          type: 'number',
          min: 0,
          step: 100,
          placeholder: t('crud.tooltips.placeholders.creditLimit')
        },
        {
          name: 'zahlungsbedingungen',
          label: t('crud.fields.paymentTerms'),
          type: 'select',
          options: [
            { value: 'sofort', label: t('crud.fields.paymentTermsImmediate') },
            { value: '7 Tage', label: t('crud.fields.paymentTerms7Days') },
            { value: '14 Tage', label: t('crud.fields.paymentTermsNet14') },
            { value: '30 Tage', label: t('crud.fields.paymentTermsNet30') },
            { value: '60 Tage', label: t('crud.fields.paymentTermsNet60') }
          ]
        },
        {
          name: 'rabatt',
          label: t('crud.fields.discountPercent'),
          type: 'number',
          min: 0,
          max: 100,
          step: 0.5,
          placeholder: t('crud.tooltips.placeholders.discount')
        },
        {
          name: 'bonitaet',
          label: t('crud.fields.creditRating'),
          type: 'select',
          options: [
            { value: 'ausgezeichnet', label: t('crud.fields.creditRatingExcellent') },
            { value: 'gut', label: t('crud.fields.creditRatingGood') },
            { value: 'mittel', label: t('crud.fields.creditRatingMedium') },
            { value: 'schlecht', label: t('crud.fields.creditRatingPoor') },
            { value: 'unklar', label: t('crud.fields.creditRatingUnclear') }
          ]
        },
        {
          name: 'preisgruppe',
          label: t('crud.fields.priceGroup'),
          type: 'select',
          options: [
            { value: 'standard', label: t('crud.fields.priceGroupStandard') },
            { value: 'premium', label: t('crud.fields.priceGroupPremium') },
            { value: 'wholesale', label: t('crud.fields.priceGroupWholesale') },
            { value: 'retail', label: t('crud.fields.priceGroupRetail') }
          ],
          placeholder: t('crud.tooltips.placeholders.priceGroup')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'umsatz',
      label: t('crud.fields.revenueAndHistory'),
      fields: [
        {
          name: 'letzteBestellung',
          label: t('crud.fields.lastOrder'),
          type: 'date',
          readonly: true
        },
        {
          name: 'umsatzGesamt',
          label: t('crud.fields.totalRevenue'),
          type: 'number',
          readonly: true,
          min: 0,
          step: 0.01
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          options: [
            { value: 'aktiv', label: t('status.active') },
            { value: 'inaktiv', label: t('status.inactive') },
            { value: 'gesperrt', label: t('crud.fields.statusBlocked') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'bemerkungen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'bemerkungen',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.customerNotes')
        }
      ]
    },
    // Sales-Tab entfernt: preisgruppe ist jetzt in konditionen Tab
    // steuerkategorie ist jetzt in steuern Tab
    // kundensegment, branche, region, kundenpreisliste: Verwende bestehende Felder
    // - kundensegment → analytics.segment (potential Tab)
    // - branche → profile.industry_code (marketing Tab)
    // - region → region (bestehend in crm-core)
    // - kundenpreisliste → customer.price_list_id (bestehend in valeo-modern)
  ],
  actions: [
    {
      key: 'validate',
      label: t('crud.actions.validate'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'save',
      label: t('crud.actions.save'),
      type: 'primary',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/crm/kunden',
    endpoints: {
      list: '/api/crm/kunden',
      get: '/api/crm/kunden/{id}',
      create: '/api/crm/kunden',
      update: '/api/crm/kunden/{id}',
      delete: '/api/crm/kunden/{id}'
    }
  },
  validation: createKundenSchema(t),
  permissions: ['crm.write', 'customer.admin']
})

// GDPR-Requests Liste Komponente
function GDPRRequestsList({ contactId }: { contactId?: string }) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [requests, setRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const gdprApiClient = createApiClient('/api/crm-gdpr')

  useEffect(() => {
    const loadRequests = async () => {
      if (!contactId) {
        setLoading(false)
        return
      }

      try {
        const response = await gdprApiClient.get('/gdpr/requests', {
          params: {
            tenant_id: '00000000-0000-0000-0000-000000000001', // TODO: Get from auth context
            contact_id: contactId
          }
        })
        
        if (response.success && Array.isArray(response.data)) {
          setRequests(response.data)
        } else {
          setRequests([])
        }
      } catch (error) {
        console.error('Fehler beim Laden der GDPR-Requests:', error)
      } finally {
        setLoading(false)
      }
    }

    loadRequests()
  }, [contactId])

  if (loading) {
    return <div className="p-4">Lade GDPR-Requests...</div>
  }

  if (requests.length === 0) {
    return (
      <div className="p-4 text-center">
        <ShieldCheck className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
        <p className="text-muted-foreground mb-4">{t('crud.messages.noGDPRRequests')}</p>
        <Button onClick={() => navigate(`/crm/gdpr-request/new?contact_id=${contactId}`)}>
          <Plus className="h-4 w-4 mr-2" />
          {t('crud.actions.createGDPRRequest')}
        </Button>
      </div>
    )
  }

  const typeLabels: Record<string, string> = {
    access: t('crud.gdpr.requestTypes.access'),
    deletion: t('crud.gdpr.requestTypes.deletion'),
    portability: t('crud.gdpr.requestTypes.portability'),
    objection: t('crud.gdpr.requestTypes.objection'),
  }

  const statusVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    pending: 'secondary',
    in_progress: 'default',
    completed: 'default',
    rejected: 'destructive',
    cancelled: 'outline',
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.detail.gdprRequests')}</h3>
        <Button onClick={() => navigate(`/crm/gdpr-request/new?contact_id=${contactId}`)}>
          <Plus className="h-4 w-4 mr-2" />
          {t('crud.actions.createGDPRRequest')}
        </Button>
      </div>

      <div className="space-y-2">
        {requests.map((req) => (
          <Card key={req.id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant={statusVariants[req.status] || 'secondary'}>
                      {getStatusLabel(t, req.status, req.status)}
                    </Badge>
                    <Badge variant="outline">{typeLabels[req.request_type] || req.request_type}</Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {t('crud.fields.requestedAt')}: {formatDate(req.requested_at)}
                  </div>
                  {req.completed_at && (
                    <div className="text-sm text-muted-foreground">
                      {t('crud.fields.completedAt')}: {formatDate(req.completed_at)}
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate(`/crm/gdpr-request/${req.id}`)}
                  >
                    {t('crud.actions.details')}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Consents-Liste Komponente
function ConsentsList({ contactId }: { contactId?: string }) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [consents, setConsents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const consentApiClient = createApiClient('/api/crm-consent')

  useEffect(() => {
    const loadConsents = async () => {
      if (!contactId) {
        setLoading(false)
        return
      }

      try {
        const response = await consentApiClient.get(`/consents/contact/${contactId}`, {
          params: {
            tenant_id: '00000000-0000-0000-0000-000000000001' // TODO: Get from auth context
          }
        })
        
        if (response.success) {
          setConsents(Array.isArray(response.data) ? response.data : [])
        }
      } catch (error) {
        console.error('Fehler beim Laden der Consents:', error)
      } finally {
        setLoading(false)
      }
    }

    loadConsents()
  }, [contactId])

  if (loading) {
    return <div className="p-4">Lade Consents...</div>
  }

  if (consents.length === 0) {
    return (
      <div className="p-4 text-center">
        <ShieldCheck className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
        <p className="text-muted-foreground mb-4">{t('crud.messages.noConsents')}</p>
        <Button onClick={() => navigate(`/crm/consent/new?contact_id=${contactId}`)}>
          <Plus className="h-4 w-4 mr-2" />
          {t('crud.actions.createConsent')}
        </Button>
      </div>
    )
  }

  const channelLabels: Record<string, string> = {
    email: t('crud.channels.email'),
    sms: t('crud.channels.sms'),
    phone: t('crud.channels.phone'),
    postal: t('crud.channels.postal'),
  }

  const statusVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    pending: 'secondary',
    granted: 'default',
    denied: 'destructive',
    revoked: 'outline',
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.detail.consents')}</h3>
        <Button onClick={() => navigate(`/crm/consent/new?contact_id=${contactId}`)}>
          <Plus className="h-4 w-4 mr-2" />
          {t('crud.actions.createConsent')}
        </Button>
      </div>

      <div className="space-y-2">
        {consents.map((consent) => (
          <Card key={consent.id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant={statusVariants[consent.status] || 'secondary'}>
                      {getStatusLabel(t, consent.status, consent.status)}
                    </Badge>
                    <Badge variant="outline">{channelLabels[consent.channel] || consent.channel}</Badge>
                    <span className="text-sm text-muted-foreground">
                      {t(`crud.consentTypes.${consent.consent_type}`)}
                    </span>
                  </div>
                  {consent.granted_at && (
                    <div className="text-sm text-muted-foreground">
                      {t('crud.fields.grantedAt')}: {formatDate(consent.granted_at)}
                    </div>
                  )}
                  {consent.expires_at && (
                    <div className="text-sm text-muted-foreground">
                      {t('crud.fields.expiresAt')}: {formatDate(consent.expires_at)}
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate(`/crm/consent/${consent.id}`)}
                  >
                    {t('crud.actions.details')}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Kontakte-Liste Komponente
function ContactsList({ customerId }: { customerId?: string }) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'contact'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kontakt')

  const { data: contactsData, isLoading } = useQuery({
    queryKey: queryKeys.crm.contacts.listFiltered({ search: undefined }),
    queryFn: () => crmService.getContacts({ limit: 100 }),
    enabled: !!customerId
  })

  // Filtere Kontakte nach customer_id (falls API das nicht direkt unterstützt)
  const contacts = (contactsData?.data || []).filter((contact: Contact) => 
    (contact.company?.toLowerCase().includes(customerId?.toLowerCase() || '') || 
     (contact as any).customer_id === customerId)
  )

  const columns = [
    {
      key: 'name' as const,
      label: t('crud.fields.name'),
      render: (contact: Contact) => contact.name || '-'
    },
    {
      key: 'email' as const,
      label: t('crud.fields.email'),
      render: (contact: Contact) => (
        <div className="flex items-center gap-2">
          {contact.email && <Mail className="h-4 w-4 text-muted-foreground" />}
          <span>{contact.email || '-'}</span>
        </div>
      )
    },
    {
      key: 'phone' as const,
      label: t('crud.fields.phone'),
      render: (contact: Contact) => (
        <div className="flex items-center gap-2">
          {contact.phone && <Phone className="h-4 w-4 text-muted-foreground" />}
          <span>{contact.phone || '-'}</span>
        </div>
      )
    },
    {
      key: 'actions' as const,
      label: t('crud.actions.actions'),
      render: (contact: Contact) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(`/crm/kontakt/${contact.id}`)}
        >
          <ExternalLink className="h-4 w-4 mr-2" />
          {t('crud.actions.view')}
        </Button>
      )
    }
  ]

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{t('crud.fields.contacts')}</CardTitle>
          <Button
            onClick={() => navigate(`/crm/kontakt/neu?customer_id=${customerId}`)}
            size="sm"
          >
            <Plus className="h-4 w-4 mr-2" />
            {t('crud.actions.new')} {entityTypeLabel}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-8">{t('crud.list.loading', { entityType: entityTypeLabel })}</div>
        ) : contacts.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            {t('crud.list.noItems', { entityType: entityTypeLabel })}
          </div>
        ) : (
          <DataTable
            data={contacts}
            columns={columns}
          />
        )}
      </CardContent>
    </Card>
  )
}

export default function KundenStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'customer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kunde')
  const kundenConfig = createKundenConfig(t, entityTypeLabel)
  const isNew = !id || id === 'neu'

  const { data, loading, saveData } = useMaskData({
    apiUrl: kundenConfig.api.baseUrl,
    id: id || 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(kundenConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'save') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        navigate('/crm/kunden/liste')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        alert(t('crud.messages.validationSuccess'))
      } else {
        showValidationToast(isValid.errors)
      }
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.discardChanges'))) {
      return
    }
    navigate('/crm/kunden/liste')
  }

  return (
    <div className="space-y-6">
      <ObjectPage
        config={kundenConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
      />
      
      {/* Kontakte-Liste für bestehende Kunden */}
      {!isNew && id && (
        <>
          <ContactsList customerId={id} />
          
          {/* Consents Tab as separate section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5" />
                {t('crud.detail.consents')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ConsentsList contactId={id} />
            </CardContent>
          </Card>

          {/* GDPR-Requests Tab as separate section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5" />
                {t('crud.detail.gdprRequests')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <GDPRRequestsList contactId={id} />
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
