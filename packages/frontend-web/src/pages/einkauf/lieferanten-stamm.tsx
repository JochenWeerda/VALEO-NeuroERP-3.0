import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { NativeSelect } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Building2, Save, Plus, X, AlertTriangle, CheckCircle, Archive, Lock } from 'lucide-react'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

type SupplierRoleFocus = 'all' | 'procurement' | 'quality' | 'finance' | 'compliance' | 'management'

const supplierRoleProfiles: Array<{ id: SupplierRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt die Lieferantenakte fuer Einkauf, QS, Finance, Compliance und Leitung.',
  },
  {
    id: 'procurement',
    label: 'Einkauf',
    description: 'Fokus auf Stammdaten, Ansprechpartner, Kategorie und Einkaufsbereitschaft.',
  },
  {
    id: 'quality',
    label: 'QS',
    description: 'Fokus auf QS-Nummer, Bewertung, Klassifikation und gueltige Nachweise.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Fokus auf Bankdaten, Zahlungsbedingungen, Kreditlimit und Steuerdaten.',
  },
  {
    id: 'compliance',
    label: 'Compliance',
    description: 'Fokus auf Dokumente, Gueltigkeiten, Sperrstatus und Nachweisablage.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Freigabestatus, Blocker und naechste Aktion.',
  },
]

type LieferantData = {
  id: string
  name: string
  legalName?: string
  typ: string
  kategorie?: string
  gruppe?: string
  strasse: string
  plz: string
  ort: string
  land: string
  email: string
  telefon: string
  website?: string
  vatId?: string
  steuernummer?: string
  iban?: string
  bic?: string
  bankName?: string
  kontoinhaber?: string
  zahlungsbedingungen?: string
  kreditlimit?: number
  qsNummer?: string
  bewertung: number
  status: 'aktiv' | 'gesperrt' | 'archiviert'
  ansprechpartner?: Array<{
    id: string
    name: string
    email: string
    telefon: string
    funktion: string
  }>
  bankkonten?: Array<{
    id: string
    iban: string
    bic: string
    bankName: string
    kontoinhaber: string
    isDefault: boolean
  }>
  klassifikationen?: Array<{
    id: string
    typ: string
    wert: string
  }>
  dokumente?: Array<{
    id: string
    typ: DokumentTyp
    titel: string
    dateiname: string
    gueltigBis?: string
    hochgeladenAm: string
    status: 'aktiv' | 'abgelaufen' | 'wird_abgelaufen'
  }>
  bemerkungen?: string
}

/** Dokumenttypen im Lieferantenstamm (häufig bis seltener) */
export type DokumentTyp =
  | 'rahmenvertrag'      // Lieferantenvertrag / Rahmenvertrag
  | 'preisliste'         // Preislisten / Konditionenblatt
  | 'bankdaten_sepa'    // Bankdaten-Nachweis / SEPA-Mandat
  | 'handelsregister'   // Handelsregisterauszug / Gewerbeanmeldung
  | 'steuer_ust'        // Steuer-/USt-Bescheinigung
  | 'onboarding'        // Onboarding-Formular / Selbstauskunft
  | 'zertifikat'        // GMP+, QS, ISO, Bio, VLOG, HACCP
  | 'produkt_sicherheit' // Spezifikationen, COA, SDS
  | 'rohstoff_deklaration' // Rohstoffdeklarationen / Herkunftsnachweise
  | 'kommunikation'     // Kommunikation / Schriftverkehr
  | 'foto_scan'         // Fotos / Scanbelege
  | 'signatur'          // Signatur-/Prüfdateien (z. B. PGP)
  | 'nda'
  | 'esg'
  | 'sonstiges'

const DOKUMENT_TYP_LABELS: Record<DokumentTyp, string> = {
  rahmenvertrag: 'Lieferantenvertrag / Rahmenvertrag',
  preisliste: 'Preislisten / Konditionenblatt',
  bankdaten_sepa: 'Bankdaten-Nachweis / SEPA-Mandat',
  handelsregister: 'Handelsregisterauszug / Gewerbeanmeldung',
  steuer_ust: 'Steuer-/USt-Bescheinigung',
  onboarding: 'Onboarding-Formular / Selbstauskunft',
  zertifikat: 'Zertifikate (GMP+, QS, ISO, Bio, VLOG, HACCP)',
  produkt_sicherheit: 'Produkt-/Sicherheitsdokumente (Spezifikationen, COA, SDS)',
  rohstoff_deklaration: 'Rohstoffdeklarationen / Herkunftsnachweise',
  kommunikation: 'Kommunikation / Schriftverkehr',
  foto_scan: 'Fotos / Scanbelege',
  signatur: 'Signatur-/Prüfdateien (z. B. PGP)',
  nda: 'NDA',
  esg: 'ESG',
  sonstiges: 'Sonstiges',
}

/** Kurzbezeichnungen für die Dokumenttyp-Spalte (Tabelle) */
const DOKUMENT_TYP_SHORT: Record<DokumentTyp, string> = {
  rahmenvertrag: 'Rahmenvertrag',
  preisliste: 'Preisliste/Konditionen',
  bankdaten_sepa: 'Bankdaten/SEPA',
  handelsregister: 'Handelsregister',
  steuer_ust: 'Steuer/USt',
  onboarding: 'Onboarding',
  zertifikat: 'Zertifikat',
  produkt_sicherheit: 'Produkt/Sicherheit',
  rohstoff_deklaration: 'Rohstoff/Herkunft',
  kommunikation: 'Kommunikation',
  foto_scan: 'Foto/Scan',
  signatur: 'Signatur/Prüfdatei',
  nda: 'NDA',
  esg: 'ESG',
  sonstiges: 'Sonstiges',
}

export default function LieferantenStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const entityType = 'supplier'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Lieferant')

  const [loading, setLoading] = useState(false)
  const [duplicateCheckDialogOpen, setDuplicateCheckDialogOpen] = useState(false)
  const [duplicateResults, setDuplicateResults] = useState<any[]>([])
  const [blockDialogOpen, setBlockDialogOpen] = useState(false)
  const [blockReason, setBlockReason] = useState('')
  const [archiveDialogOpen, setArchiveDialogOpen] = useState(false)
  const [newContactDialogOpen, setNewContactDialogOpen] = useState(false)
  const [newBankDialogOpen, setNewBankDialogOpen] = useState(false)
  const [newClassificationDialogOpen, setNewClassificationDialogOpen] = useState(false)
  const [newDocumentDialogOpen, setNewDocumentDialogOpen] = useState(false)
  const [newDocument, setNewDocument] = useState<{ typ: DokumentTyp; titel: string; dateiname: string; gueltigBis: string }>({ typ: 'rahmenvertrag', titel: '', dateiname: '', gueltigBis: '' })
  const [roleFocus, setRoleFocus] = useState<SupplierRoleFocus>('all')

  const [lieferant, setLieferant] = useState<LieferantData>({
    id: id || 'L-001',
    name: '',
    typ: '',
    strasse: '',
    plz: '',
    ort: '',
    land: 'DE',
    email: '',
    telefon: '',
    bewertung: 0,
    status: 'aktiv',
    ansprechpartner: [],
    bankkonten: [],
    klassifikationen: [],
    dokumente: [],
  })

  useEffect(() => {
    if (id) {
      loadSupplier()
    }
  }, [id])

  const loadSupplier = async () => {
    setLoading(true)
    try {
      // Versuche verschiedene API-Endpunkte
      let response: any
      try {
        response = (await apiClient.get<any>(`/api/v1/crm/business-partners/${id}?type=supplier`)) as any
      } catch (e1) {
        try {
          response = (await apiClient.get<any>(`/api/v1/einkauf/lieferanten/${id}`)) as any
        } catch (e2) {
          toast({
            variant: 'destructive',
            title: 'Lieferant konnte nicht geladen werden',
            description: 'Bitte prüfen Sie die Verbindung oder ob der Lieferant existiert.',
          })
          setLieferant((prev) => ({ ...prev, id: id || '', name: '', legalName: '' }))
          setLoading(false)
          return
        }
      }

      if (response) {
        const data = response
        setLieferant({
          id: data.id || id || '',
          name: data.name || '',
          legalName: data.legalName,
          typ: data.type || data.typ || '',
          kategorie: data.category || data.kategorie,
          gruppe: data.group || data.gruppe,
          strasse: data.address || data.strasse || '',
          plz: data.postalCode || data.plz || '',
          ort: data.city || data.ort || '',
          land: data.country || data.land || 'DE',
          email: data.email || '',
          telefon: data.phone || data.telefon || '',
          website: data.website,
          vatId: data.vatId,
          steuernummer: data.taxId || data.steuernummer,
          iban: data.iban,
          bic: data.bic,
          bankName: data.bankName,
          kontoinhaber: data.accountHolder || data.kontoinhaber,
          zahlungsbedingungen: data.paymentTerms || data.zahlungsbedingungen,
          kreditlimit: data.creditLimit || data.kreditlimit,
          qsNummer: data.qsNummer,
          bewertung: data.rating || data.bewertung || 0,
          status: data.status === 'suspended' || data.status === 'gesperrt' ? 'gesperrt' : data.status === 'inactive' || data.status === 'archiviert' ? 'archiviert' : 'aktiv',
          ansprechpartner: data.contacts || data.ansprechpartner || [],
          bankkonten: data.bankAccounts || data.bankkonten || [],
          klassifikationen: data.classifications || data.klassifikationen || [],
          bemerkungen: data.notes || data.bemerkungen,
        })
      }
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadDataError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  // Pure worker — no loading management. Callers own the guard.
  const persistLieferant = async () => {
    const payload = {
        name: lieferant.name,
        legalName: lieferant.legalName,
        type: lieferant.typ,
        category: lieferant.kategorie,
        group: lieferant.gruppe,
        address: lieferant.strasse,
        postalCode: lieferant.plz,
        city: lieferant.ort,
        country: lieferant.land,
        email: lieferant.email,
        phone: lieferant.telefon,
        website: lieferant.website,
        vatId: lieferant.vatId,
        taxId: lieferant.steuernummer,
        paymentTerms: lieferant.zahlungsbedingungen,
        creditLimit: lieferant.kreditlimit,
        status: lieferant.status === 'gesperrt' ? 'suspended' : lieferant.status === 'archiviert' ? 'inactive' : 'active',
        contacts: lieferant.ansprechpartner,
        bankAccounts: lieferant.bankkonten,
        classifications: lieferant.klassifikationen,
        documents: lieferant.dokumente,
        notes: lieferant.bemerkungen,
      }

      if (id) {
        await apiClient.put(`/api/v1/crm/business-partners/${id}?type=supplier`, payload)
        toast({
          title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
        })
      } else {
        await apiClient.post('/api/v1/crm/business-partners?type=supplier', payload)
        toast({
          title: t('crud.messages.createSuccess', { entityType: entityTypeLabel }),
        })
        navigate('/einkauf/lieferanten')
      }
  }

  // Button wrapper for direct Speichern action — owns the guard.
  const handleSave = async () => {
    setLoading(true)
    try {
      await persistLieferant()
      toast({ title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }) })
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.updateError', { entityType: entityTypeLabel }),
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDuplicateCheck = async () => {
    if (!lieferant.name) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: 'Bitte geben Sie zuerst einen Namen ein',
      })
      return
    }

    setLoading(true)
    try {
      const results = (await apiClient.get<any[]>(`/api/v1/crm/business-partners?type=supplier&query=${encodeURIComponent(lieferant.name)}`)) as unknown as any[]
      const duplicates = results.filter((s: any) => 
        s.id !== lieferant.id && 
        (s.name?.toLowerCase().includes(lieferant.name.toLowerCase()) || 
         s.name?.toLowerCase() === lieferant.name.toLowerCase())
      )
      setDuplicateResults(duplicates)
      setDuplicateCheckDialogOpen(true)
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadDataError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleBlock = async () => {
    if (!blockReason || blockReason.length < 10) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.reasonMinLength'),
      })
      return
    }

    setLoading(true)
    try {
      setLieferant(prev => ({ ...prev, status: 'gesperrt' }))
      await persistLieferant()
      toast({
        title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
        description: 'Lieferant wurde gesperrt',
      })
      setBlockDialogOpen(false)
      setBlockReason('')
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.updateError', { entityType: entityTypeLabel }),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleArchive = async () => {
    setLoading(true)
    try {
      setLieferant(prev => ({ ...prev, status: 'archiviert' }))
      await persistLieferant()
      toast({
        title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
        description: 'Lieferant wurde archiviert',
      })
      setArchiveDialogOpen(false)
      navigate('/einkauf/lieferanten')
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.updateError', { entityType: entityTypeLabel }),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const hasMasterData = Boolean(lieferant.name && lieferant.typ && lieferant.land)
  const hasContactPath = Boolean(lieferant.email || lieferant.telefon || (lieferant.ansprechpartner?.length ?? 0) > 0)
  const hasFinanceData = Boolean((lieferant.bankkonten?.length ?? 0) > 0 || lieferant.zahlungsbedingungen || lieferant.vatId || lieferant.steuernummer)
  const hasQualityEvidence = Boolean(lieferant.qsNummer || (lieferant.klassifikationen?.length ?? 0) > 0 || (lieferant.dokumente?.length ?? 0) > 0)
  const expiredDocuments = (lieferant.dokumente ?? []).filter((doc) => doc.status === 'abgelaufen').length
  const expiringDocuments = (lieferant.dokumente ?? []).filter((doc) => doc.status === 'wird_abgelaufen').length
  const hasBlockingStatus = lieferant.status !== 'aktiv'
  const isSupplierReady = hasMasterData && hasContactPath && hasFinanceData && hasQualityEvidence && expiredDocuments === 0 && !hasBlockingStatus
  const nextSupplierAction = !hasMasterData
    ? 'Name, Typ und Land im Bereich Stammdaten ergaenzen.'
    : !hasContactPath
      ? 'Mindestens E-Mail, Telefon oder Ansprechpartner hinterlegen.'
      : !hasFinanceData
        ? 'Bank-, Steuer- oder Zahlungsdaten fuer Finance ergaenzen.'
        : !hasQualityEvidence
          ? 'QS-Nummer, Klassifikation oder Lieferantendokument hinterlegen.'
          : expiredDocuments > 0
            ? 'Abgelaufene Lieferantendokumente pruefen und ersetzen.'
            : hasBlockingStatus
              ? 'Sperr- oder Archivstatus fachlich klaeren.'
              : 'Lieferant speichern und fuer Einkaufsprozesse nutzen.'
  const supplierTaskItems: UxTaskItem[] = [
    {
      label: 'Stammdaten erfassen',
      done: hasMasterData,
      hint: hasMasterData ? `${lieferant.name || 'Lieferant'} ist als ${lieferant.typ || 'Typ'} in ${lieferant.land} angelegt.` : 'Name, Typ und Land sind Pflicht fuer eine belastbare Lieferantenakte.',
    },
    {
      label: 'Kontaktweg sichern',
      done: hasContactPath,
      hint: hasContactPath ? 'Kontakt per E-Mail, Telefon oder Ansprechpartner ist vorhanden.' : 'Kontaktweg ergaenzen, damit Einkauf und QS Rueckfragen klaeren koennen.',
    },
    {
      label: 'Finance-Daten pruefen',
      done: hasFinanceData,
      hint: hasFinanceData ? 'Bank-, Steuer- oder Zahlungsdaten sind vorhanden.' : 'Zahlungsbedingungen, Steuerdaten oder Bankkonto fuer Finance ergaenzen.',
    },
    {
      label: 'Nachweise und QS klaeren',
      done: hasQualityEvidence && expiredDocuments === 0,
      hint: hasQualityEvidence
        ? expiredDocuments > 0
          ? `${expiredDocuments} Dokumente sind abgelaufen.`
          : `${lieferant.dokumente?.length ?? 0} Dokumente, ${lieferant.klassifikationen?.length ?? 0} Klassifikationen, QS ${lieferant.qsNummer || 'offen'}.`
        : 'QS-Nummer, Klassifikation oder relevantes Dokument hinterlegen.',
    },
  ]
  const supplierCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen/Speichern',
      available: hasMasterData,
      hint: hasMasterData ? 'Lieferant kann gespeichert werden.' : 'Vor dem Speichern fehlen noch Name, Typ oder Land.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Stammdaten, Kontakte, Bank, Steuer, Compliance, Dokumente und QS sind in Tabs erreichbar.',
    },
    {
      key: 'update',
      label: 'Bearbeiten',
      available: true,
      hint: 'Stammdaten, Status, Kontakte, Bankkonten, Klassifikationen und Dokumente koennen gepflegt werden.',
    },
    {
      key: 'delete',
      label: 'Sperren/Archivieren',
      available: lieferant.status === 'aktiv',
      hint: lieferant.status === 'aktiv' ? 'Sperren und Archivieren sind als gefuehrte Aktionen vorhanden.' : 'Der Lieferant ist bereits gesperrt oder archiviert.',
    },
    {
      key: 'evidence',
      label: 'Nachweisablage',
      available: (lieferant.dokumente?.length ?? 0) > 0,
      hint: (lieferant.dokumente?.length ?? 0) > 0 ? `${lieferant.dokumente?.length ?? 0} Lieferantendokumente sind hinterlegt.` : 'Dokumente koennen im Compliance-Tab erfasst werden.',
    },
    {
      key: 'audit',
      label: 'Pruefspur',
      available: Boolean(lieferant.id),
      hint: 'Lieferantennummer, Status, Dokumentgueltigkeit und Sperr-/Archivaktionen bilden die operative Pruefspur.',
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{lieferant.name || `${t('crud.actions.create')  } ${  entityTypeLabel}`}</h1>
              <p className="text-muted-foreground">{t('crud.fields.number')}: {lieferant.id || '-'}</p>
            </div>
            {lieferant.status && (
              <Badge variant={lieferant.status === 'aktiv' ? 'outline' : lieferant.status === 'gesperrt' ? 'destructive' : 'secondary'}>
                {lieferant.status === 'aktiv' ? t('status.active') : lieferant.status === 'gesperrt' ? t('status.blocked') : t('status.inactive')}
              </Badge>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleDuplicateCheck} disabled={loading}>
            <AlertTriangle className="h-4 w-4 mr-2" />
            {t('crud.actions.duplicateCheck')}
          </Button>
          {lieferant.status === 'aktiv' && (
            <>
              <Button variant="outline" onClick={() => setBlockDialogOpen(true)} disabled={loading}>
                <Lock className="h-4 w-4 mr-2" />
                {t('crud.actions.block')}
              </Button>
              <Button variant="outline" onClick={() => setArchiveDialogOpen(true)} disabled={loading}>
                <Archive className="h-4 w-4 mr-2" />
                {t('crud.actions.archive')}
              </Button>
            </>
          )}
          <Button onClick={handleSave} disabled={loading} className="gap-2">
            <Save className="h-4 w-4" />
            {loading ? t('common.loading') : t('common.save')}
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        <RoleFocusBar
          roles={supplierRoleProfiles}
          value={roleFocus}
          onChange={setRoleFocus}
          visibleCount={roleFocus === 'all' ? 5 : 1}
          totalCount={5}
        />
        <ManagementDecisionPanel
          decision={{
            allowed: isSupplierReady,
            allowedLabel: 'Einkaufsbereit',
            blockedLabel: 'Noch nicht einkaufsbereit',
            summary: isSupplierReady
              ? `Der Lieferant ist fachlich nutzbar. Bewertung ${lieferant.bewertung || 0}, ${lieferant.dokumente?.length ?? 0} Dokumente und Status aktiv.`
              : `Vor Nutzung im Einkauf ist noch etwas offen: ${nextSupplierAction}`,
            blockerCount: [!hasMasterData, !hasContactPath, !hasFinanceData, !hasQualityEvidence, expiredDocuments > 0, hasBlockingStatus].filter(Boolean).length,
            nextFocus: nextSupplierAction,
            template: {
              label: 'Lieferantenliste oeffnen',
              href: '/einkauf/lieferanten',
            },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Lieferanten-Onboardingplan" items={supplierTaskItems} />
          <div className="space-y-3">
            <NextActionPanel
              action={nextSupplierAction}
              tone={isSupplierReady ? 'emerald' : expiredDocuments > 0 || hasBlockingStatus ? 'red' : hasMasterData ? 'amber' : 'blue'}
            />
            <EvidenceTemplateLink link={{ label: 'Lieferantendokumente pruefen', href: '/einkauf/lieferanten-dokumente' }} />
            {expiringDocuments > 0 ? (
              <div className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-bold text-amber-800">
                {expiringDocuments} Dokumente laufen bald ab.
              </div>
            ) : null}
          </div>
        </div>
        <CrudCapabilityChecklist capabilities={supplierCrudCapabilities} />
      </div>

      <Tabs defaultValue="stammdaten">
        <TabsList>
          <TabsTrigger value="stammdaten">{t('crud.detail.basicInfo')}</TabsTrigger>
          <TabsTrigger value="kontakt">{t('crud.fields.contact')}</TabsTrigger>
          <TabsTrigger value="bank">{t('crud.fields.bankDetails')}</TabsTrigger>
          <TabsTrigger value="steuer">{t('crud.fields.tax')}</TabsTrigger>
          <TabsTrigger value="klassifikation">{t('crud.fields.classification')}</TabsTrigger>
          <TabsTrigger value="compliance">{t('crud.fields.compliance')} & {t('crud.fields.documents')}</TabsTrigger>
          <TabsTrigger value="qs">{t('crud.fields.quality')} & {t('crud.fields.rating')}</TabsTrigger>
        </TabsList>

        <TabsContent value="stammdaten">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>{t('crud.fields.company')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="name">{t('crud.fields.name')} *</Label>
                  <Input
                    id="name"
                    value={lieferant.name}
                    onChange={(e) => setLieferant(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="legalName">{t('crud.fields.legalName')}</Label>
                  <Input
                    id="legalName"
                    value={lieferant.legalName || ''}
                    onChange={(e) => setLieferant(prev => ({ ...prev, legalName: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="typ">{t('crud.fields.type')} *</Label>
                  <Input
                    id="typ"
                    value={lieferant.typ}
                    onChange={(e) => setLieferant(prev => ({ ...prev, typ: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="kategorie">{t('crud.fields.category')}</Label>
                  <NativeSelect
                    value={lieferant.kategorie || ''}
                    onValueChange={(value) => setLieferant(prev => ({ ...prev, kategorie: value }))}
                    options={[
                      { value: 'Saatgut', label: t('crud.fields.categorySeed') },
                      { value: 'Düngemittel', label: t('crud.fields.categoryFertilizer') },
                      { value: 'Landtechnik', label: t('crud.fields.categoryMachinery') },
                      { value: 'Sonstiges', label: t('common.other') },
                    ]}
                    placeholder={t('crud.fields.selectCategory')}
                  />
                </div>
                <div>
                  <Label htmlFor="gruppe">{t('crud.fields.group')}</Label>
                  <NativeSelect
                    value={lieferant.gruppe || ''}
                    onValueChange={(value) => setLieferant(prev => ({ ...prev, gruppe: value }))}
                    options={[
                      { value: 'Premium', label: t('crud.fields.groupPremium') },
                      { value: 'Standard', label: t('crud.fields.groupStandard') },
                      { value: 'Basis', label: t('crud.fields.groupBasic') },
                    ]}
                    placeholder={t('crud.fields.selectGroup')}
                  />
                </div>
                <div>
                  <Label htmlFor="status">{t('crud.fields.status')}</Label>
                  <NativeSelect
                    value={lieferant.status}
                    onValueChange={(value) => setLieferant(prev => ({ ...prev, status: value as LieferantData['status'] }))}
                    options={[
                      { value: 'aktiv', label: t('status.active') },
                      { value: 'gesperrt', label: t('status.blocked') },
                      { value: 'archiviert', label: t('status.inactive') },
                    ]}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>{t('crud.fields.address')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="strasse">{t('crud.fields.street')}</Label>
                  <Input
                    id="strasse"
                    value={lieferant.strasse}
                    onChange={(e) => setLieferant(prev => ({ ...prev, strasse: e.target.value }))}
                  />
                </div>
                <div className="grid gap-4 grid-cols-3">
                  <div>
                    <Label htmlFor="plz">{t('crud.fields.postalCode')}</Label>
                    <Input
                      id="plz"
                      value={lieferant.plz}
                      onChange={(e) => setLieferant(prev => ({ ...prev, plz: e.target.value }))}
                    />
                  </div>
                  <div className="col-span-2">
                    <Label htmlFor="ort">{t('crud.fields.city')}</Label>
                    <Input
                      id="ort"
                      value={lieferant.ort}
                      onChange={(e) => setLieferant(prev => ({ ...prev, ort: e.target.value }))}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="land">{t('crud.fields.country')}</Label>
                  <NativeSelect
                    value={lieferant.land}
                    onValueChange={(value) => setLieferant(prev => ({ ...prev, land: value }))}
                    options={[
                      { value: 'DE', label: t('crud.fields.countryDE') },
                      { value: 'AT', label: t('crud.fields.countryAT') },
                      { value: 'CH', label: t('crud.fields.countryCH') },
                      { value: 'NL', label: t('crud.fields.countryNL') },
                      { value: 'FR', label: t('crud.fields.countryFR') },
                    ]}
                  />
                </div>
                <div>
                  <Label htmlFor="website">{t('crud.fields.website')}</Label>
                  <Input
                    id="website"
                    type="url"
                    value={lieferant.website || ''}
                    onChange={(e) => setLieferant(prev => ({ ...prev, website: e.target.value }))}
                    placeholder="https://..."
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="kontakt">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{t('crud.fields.contactPerson')}</span>
                <Button size="sm" onClick={() => setNewContactDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  {t('crud.actions.addContact')}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {lieferant.ansprechpartner && lieferant.ansprechpartner.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.fields.name')}</TableHead>
                      <TableHead>{t('crud.fields.email')}</TableHead>
                      <TableHead>{t('crud.fields.phone')}</TableHead>
                      <TableHead>{t('crud.fields.function')}</TableHead>
                      <TableHead>{t('crud.fields.actions')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {lieferant.ansprechpartner.map((contact) => (
                      <TableRow key={contact.id}>
                        <TableCell>{contact.name}</TableCell>
                        <TableCell>{contact.email}</TableCell>
                        <TableCell>{contact.telefon}</TableCell>
                        <TableCell>{contact.funktion}</TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setLieferant(prev => ({
                                ...prev,
                                ansprechpartner: prev.ansprechpartner?.filter(c => c.id !== contact.id) || [],
                              }))
                            }}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-muted-foreground">{t('crud.messages.noData')}</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bank">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{t('crud.fields.bankDetails')}</span>
                <Button size="sm" onClick={() => setNewBankDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  {t('crud.actions.addBankAccount')}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {lieferant.bankkonten && lieferant.bankkonten.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.fields.iban')}</TableHead>
                      <TableHead>{t('crud.fields.bic')}</TableHead>
                      <TableHead>{t('crud.fields.bankName')}</TableHead>
                      <TableHead>{t('crud.fields.accountHolder')}</TableHead>
                      <TableHead>{t('crud.fields.actions')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {lieferant.bankkonten.map((bank) => (
                      <TableRow key={bank.id}>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {bank.iban}
                            {bank.isDefault && <Badge variant="outline">{t('crud.fields.default')}</Badge>}
                          </div>
                        </TableCell>
                        <TableCell>{bank.bic}</TableCell>
                        <TableCell>{bank.bankName}</TableCell>
                        <TableCell>{bank.kontoinhaber}</TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setLieferant(prev => ({
                                ...prev,
                                bankkonten: prev.bankkonten?.filter(b => b.id !== bank.id) || [],
                              }))
                            }}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-muted-foreground">{t('crud.messages.noData')}</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="steuer">
          <Card>
            <CardHeader>
              <CardTitle>{t('crud.fields.tax')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="vatId">{t('crud.fields.vatId')}</Label>
                <Input
                  id="vatId"
                  value={lieferant.vatId || ''}
                  onChange={(e) => setLieferant(prev => ({ ...prev, vatId: e.target.value }))}
                  placeholder={t('crud.tooltips.placeholders.vatId')}
                />
              </div>
              <div>
                <Label htmlFor="steuernummer">{t('crud.fields.taxNumber')}</Label>
                <Input
                  id="steuernummer"
                  value={lieferant.steuernummer || ''}
                  onChange={(e) => setLieferant(prev => ({ ...prev, steuernummer: e.target.value }))}
                  placeholder={t('crud.tooltips.placeholders.taxNumber')}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="klassifikation">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{t('crud.fields.classification')}</span>
                <Button size="sm" onClick={() => setNewClassificationDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  {t('crud.actions.addClassification')}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {lieferant.klassifikationen && lieferant.klassifikationen.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.fields.type')}</TableHead>
                      <TableHead>{t('crud.fields.value')}</TableHead>
                      <TableHead>{t('crud.fields.actions')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {lieferant.klassifikationen.map((klass) => (
                      <TableRow key={klass.id}>
                        <TableCell>{klass.typ}</TableCell>
                        <TableCell>{klass.wert}</TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setLieferant(prev => ({
                                ...prev,
                                klassifikationen: prev.klassifikationen?.filter(k => k.id !== klass.id) || [],
                              }))
                            }}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-muted-foreground">{t('crud.messages.noData')}</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.fields.compliance')} & {t('crud.fields.documents')}</CardTitle>
                <Button
                  size="sm"
                  onClick={() => setNewDocumentDialogOpen(true)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {t('crud.actions.addDocument')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {lieferant.dokumente && lieferant.dokumente.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.fields.type')}</TableHead>
                      <TableHead>{t('crud.fields.title')}</TableHead>
                      <TableHead>{t('crud.fields.fileName')}</TableHead>
                      <TableHead>{t('crud.fields.validUntil')}</TableHead>
                      <TableHead>{t('crud.fields.status')}</TableHead>
                      <TableHead>{t('crud.fields.actions')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {lieferant.dokumente.map((doc) => {
                      const isExpiring = doc.status === 'wird_abgelaufen'
                      const isExpired = doc.status === 'abgelaufen'
                      return (
                        <TableRow key={doc.id}>
                          <TableCell>
                            <Badge variant="outline" className="max-w-[180px] truncate" title={DOKUMENT_TYP_LABELS[doc.typ as DokumentTyp] || doc.typ}>
                              {DOKUMENT_TYP_SHORT[doc.typ as DokumentTyp] || DOKUMENT_TYP_LABELS[doc.typ as DokumentTyp] || doc.typ}
                            </Badge>
                          </TableCell>
                          <TableCell>{doc.titel}</TableCell>
                          <TableCell className="max-w-xs truncate">{doc.dateiname}</TableCell>
                          <TableCell>
                            {doc.gueltigBis ? (
                              <span className={isExpired ? 'text-destructive font-semibold' : isExpiring ? 'text-orange-600 font-semibold' : ''}>
                                {formatDate(doc.gueltigBis)}
                              </span>
                            ) : (
                              <span className="text-muted-foreground">-</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <Badge variant={isExpired ? 'destructive' : isExpiring ? 'secondary' : 'default'}>
                              {isExpired ? t('crud.fields.expired') :
                               isExpiring ? t('crud.fields.expiring') :
                               t('crud.fields.active')}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={async () => {
                                  try {
                                    const url = `/api/v1/einkauf/lieferanten/${id}/dokumente/${doc.id}/download`
                                    const res = await apiClient.get(url, { responseType: 'blob' })
                                    const blob = res.data as Blob
                                    if (!blob || blob.size === 0) {
                                      throw new Error('empty-file')
                                    }
                                    const objectUrl = URL.createObjectURL(blob)
                                    const a = document.createElement('a')
                                    a.href = objectUrl
                                    a.download = doc.dateiname || doc.titel || 'dokument'
                                    a.click()
                                    URL.revokeObjectURL(objectUrl)
                                    toast({ title: t('crud.messages.downloadInfo'), description: doc.dateiname })
                                  } catch (error: any) {
                                    toast({
                                      title: t('crud.messages.downloadInfo'),
                                      description: 'Dokument konnte nicht geladen werden. Bitte DMS-Verbindung pruefen.',
                                      variant: 'destructive'
                                    })
                                  }
                                }}>

                                {t('crud.actions.download')}
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => {
                                  setLieferant(prev => ({
                                    ...prev,
                                    dokumente: prev.dokumente?.filter(d => d.id !== doc.id) || [],
                                  }))
                                }}
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>{t('crud.messages.noDocuments')}</p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => setNewDocumentDialogOpen(true)}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    {t('crud.actions.addDocument')}
                  </Button>
                </div>
              )}

              {/* Expiring/Expired Documents Warning */}
              {lieferant.dokumente && lieferant.dokumente.some(d => d.status === 'abgelaufen' || d.status === 'wird_abgelaufen') && (
                <div className="mt-4 border border-orange-500 rounded-lg p-4 bg-orange-50">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-5 w-5 text-orange-600" />
                    <Label className="text-orange-800 font-semibold">{t('crud.fields.expiringDocumentsWarning')}</Label>
                  </div>
                  <p className="text-sm text-orange-700 mb-3">
                    {t('crud.fields.expiringDocumentsDescription')}
                  </p>
                  {lieferant.dokumente.filter(d => d.status === 'abgelaufen').length > 0 && (
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => {
                        setBlockDialogOpen(true)
                      }}
                    >
                      {t('crud.actions.block')} {entityTypeLabel}
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="qs">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>{t('crud.fields.quality')} & {t('crud.fields.rating')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="qsNummer">{t('crud.fields.qualityNumber')}</Label>
                  <Input
                    id="qsNummer"
                    value={lieferant.qsNummer || ''}
                    onChange={(e) => setLieferant(prev => ({ ...prev, qsNummer: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>{t('crud.fields.rating')}</Label>
                  <div className="text-2xl font-bold">{lieferant.bewertung} / 5</div>
                </div>
                <div>
                  <Label htmlFor="zahlungsbedingungen">{t('crud.fields.paymentTerms')}</Label>
                  <NativeSelect
                    value={lieferant.zahlungsbedingungen || ''}
                    onValueChange={(value) => setLieferant(prev => ({ ...prev, zahlungsbedingungen: value }))}
                    options={[
                      { value: 'sofort', label: t('crud.fields.paymentTermsImmediate') },
                      { value: '14tage', label: t('crud.fields.paymentTermsNet14') },
                      { value: '30tage', label: t('crud.fields.paymentTermsNet30') },
                      { value: '60tage', label: t('crud.fields.paymentTermsNet60') },
                    ]}
                    placeholder={t('crud.tooltips.placeholders.paymentTerms')}
                  />
                </div>
                <div>
                  <Label htmlFor="kreditlimit">{t('crud.fields.creditLimit')} (€)</Label>
                  <Input
                    id="kreditlimit"
                    type="number"
                    value={lieferant.kreditlimit || ''}
                    onChange={(e) => setLieferant(prev => ({ ...prev, kreditlimit: Number(e.target.value) }))}
                  />
                </div>
                <div>
                  <Label htmlFor="bemerkungen">{t('crud.fields.notes')}</Label>
                  <Textarea
                    id="bemerkungen"
                    value={lieferant.bemerkungen || ''}
                    onChange={(e) => setLieferant(prev => ({ ...prev, bemerkungen: e.target.value }))}
                    rows={4}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Supplier Evaluation Card */}
            <Card>
              <CardHeader>
                <CardTitle>{t('crud.fields.supplierEvaluation')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Overall Score */}
                <div className="border rounded-lg p-4 bg-muted/50">
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-lg font-semibold">{t('crud.fields.overallScore')}</Label>
                    <Badge variant={lieferant.bewertung >= 4 ? 'default' : lieferant.bewertung >= 3 ? 'secondary' : 'destructive'}>
                      {lieferant.bewertung >= 4 ? t('crud.fields.excellent') : lieferant.bewertung >= 3 ? t('crud.fields.good') : t('crud.fields.needsImprovement')}
                    </Badge>
                  </div>
                  <div className="text-4xl font-bold mb-2">{lieferant.bewertung.toFixed(1)} / 5.0</div>
                  <div className="text-sm text-muted-foreground">
                    {t('crud.fields.trend')}: <span className="font-medium">{t('crud.fields.stable')}</span>
                  </div>
                </div>

                {/* Evaluation Criteria */}
                <div className="space-y-4">
                  <Label className="text-base font-semibold">{t('crud.fields.evaluationCriteria')}</Label>
                  
                  {/* Quality Score */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <Label>{t('crud.fields.quality')}</Label>
                      <span className="text-sm font-medium">4.2 / 5.0</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: '84%' }}></div>
                    </div>
                  </div>

                  {/* Delivery Score */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <Label>{t('crud.fields.deliveryPerformance')}</Label>
                      <span className="text-sm font-medium">4.5 / 5.0</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: '90%' }}></div>
                    </div>
                  </div>

                  {/* Price Score */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <Label>{t('crud.fields.priceCompetitiveness')}</Label>
                      <span className="text-sm font-medium">3.8 / 5.0</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: '76%' }}></div>
                    </div>
                  </div>

                  {/* Service Score */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <Label>{t('crud.fields.service')}</Label>
                      <span className="text-sm font-medium">4.0 / 5.0</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: '80%' }}></div>
                    </div>
                  </div>
                </div>

                {/* Auto-Block Recommendation */}
                {lieferant.bewertung < 2.5 && (
                  <div className="border border-destructive rounded-lg p-4 bg-destructive/10">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="h-5 w-5 text-destructive" />
                      <Label className="text-destructive font-semibold">{t('crud.fields.lowScoreWarning')}</Label>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      {t('crud.fields.lowScoreDescription')}
                    </p>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => setBlockDialogOpen(true)}
                    >
                      {t('crud.actions.block')} {entityTypeLabel}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Duplicate Check Dialog */}
      <Dialog open={duplicateCheckDialogOpen} onOpenChange={setDuplicateCheckDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{t('crud.actions.duplicateCheck')}</DialogTitle>
            <DialogDescription>
              {duplicateResults.length > 0
                ? t('crud.messages.duplicatesFound', { count: duplicateResults.length })
                : t('crud.messages.noDuplicatesFound')}
            </DialogDescription>
          </DialogHeader>
          {duplicateResults.length > 0 ? (
            <div className="max-h-96 overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('crud.fields.name')}</TableHead>
                    <TableHead>{t('crud.fields.number')}</TableHead>
                    <TableHead>{t('crud.fields.city')}</TableHead>
                    <TableHead>{t('crud.fields.actions')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {duplicateResults.map((dup) => (
                    <TableRow key={dup.id}>
                      <TableCell>{dup.name}</TableCell>
                      <TableCell>{dup.id || dup.number || '-'}</TableCell>
                      <TableCell>{dup.city || dup.ort || '-'}</TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            navigate(`/einkauf/lieferant/${dup.id}`)
                            setDuplicateCheckDialogOpen(false)
                          }}
                        >
                          {t('crud.actions.view')}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="h-5 w-5" />
              <p>{t('crud.messages.noDuplicatesFound')}</p>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDuplicateCheckDialogOpen(false)}>
              {t('common.close')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Block Dialog */}
      <Dialog open={blockDialogOpen} onOpenChange={setBlockDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.block')} {entityTypeLabel}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.block.description', { entityType: entityTypeLabel })}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="blockReason">{t('crud.dialogs.block.reasonRequired')}</Label>
              <Textarea
                id="blockReason"
                value={blockReason}
                onChange={(e) => setBlockReason(e.target.value)}
                placeholder={t('crud.dialogs.block.reasonPlaceholder')}
                required
                minLength={10}
                rows={4}
              />
              <p className="text-sm text-muted-foreground mt-1">
                {t('crud.dialogs.block.reasonMinLength')}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBlockDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              variant="destructive"
              onClick={handleBlock}
              disabled={loading || blockReason.length < 10}
            >
              {loading ? t('common.loading') : t('crud.actions.block')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Archive Dialog */}
      <Dialog open={archiveDialogOpen} onOpenChange={setArchiveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.archive')} {entityTypeLabel}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.archive.description', { entityType: entityTypeLabel })}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setArchiveDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              variant="secondary"
              onClick={handleArchive}
              disabled={loading}
            >
              {loading ? t('common.loading') : t('crud.actions.archive')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* New Contact Dialog */}
      <Dialog open={newContactDialogOpen} onOpenChange={setNewContactDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.addContact')}</DialogTitle>
          </DialogHeader>
          <NewContactForm
            onSave={(contact) => {
              setLieferant(prev => ({
                ...prev,
                ansprechpartner: [...(prev.ansprechpartner || []), { ...contact, id: Date.now().toString() }],
              }))
              setNewContactDialogOpen(false)
            }}
            onCancel={() => setNewContactDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* New Bank Account Dialog */}
      <Dialog open={newBankDialogOpen} onOpenChange={setNewBankDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.addBankAccount')}</DialogTitle>
          </DialogHeader>
          <NewBankAccountForm
            onSave={(bank) => {
              setLieferant(prev => ({
                ...prev,
                bankkonten: [...(prev.bankkonten || []), { ...bank, id: Date.now().toString() }],
              }))
              setNewBankDialogOpen(false)
            }}
            onCancel={() => setNewBankDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* New Classification Dialog */}
      <Dialog open={newClassificationDialogOpen} onOpenChange={setNewClassificationDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.addClassification')}</DialogTitle>
          </DialogHeader>
          <NewClassificationForm
            onSave={(klass) => {
              setLieferant(prev => ({
                ...prev,
                klassifikationen: [...(prev.klassifikationen || []), { ...klass, id: Date.now().toString() }],
              }))
              setNewClassificationDialogOpen(false)
            }}
            onCancel={() => setNewClassificationDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* New Document Dialog */}
      <Dialog open={newDocumentDialogOpen} onOpenChange={setNewDocumentDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.addDocument')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="docType">{t('crud.fields.type')} *</Label>
              <NativeSelect
                value={newDocument.typ}
                  onValueChange={(value) =>
                  setNewDocument(prev => ({ ...prev, typ: value as DokumentTyp }))
                }
                options={(Object.keys(DOKUMENT_TYP_LABELS) as DokumentTyp[]).map((typ) => ({
                  value: typ,
                  label: DOKUMENT_TYP_LABELS[typ],
                }))}
                placeholder="Dokumenttyp wählen"
              />
            </div>
            <div>
              <Label htmlFor="docTitle">{t('crud.fields.title')} *</Label>
              <Input
                id="docTitle"
                value={newDocument.titel}
                onChange={(e) => setNewDocument(prev => ({ ...prev, titel: e.target.value }))}
                placeholder={t('crud.tooltips.placeholders.documentTitle')}
              />
            </div>
            <div>
              <Label htmlFor="docFile">{t('crud.fields.file')} *</Label>
              <Input
                id="docFile"
                type="file"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    setNewDocument(prev => ({ ...prev, dateiname: file.name }))
                  }
                }}
              />
            </div>
            <div>
              <Label htmlFor="docValidUntil">{t('crud.fields.validUntil')}</Label>
              <Input
                id="docValidUntil"
                type="date"
                value={newDocument.gueltigBis}
                onChange={(e) => setNewDocument(prev => ({ ...prev, gueltigBis: e.target.value }))}
              />
              <p className="text-sm text-muted-foreground mt-1">
                {t('crud.tooltips.placeholders.validUntilOptional')}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setNewDocumentDialogOpen(false)
              setNewDocument({ typ: 'rahmenvertrag', titel: '', dateiname: '', gueltigBis: '' })
            }}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={() => {
                if (!newDocument.titel || !newDocument.dateiname) {
                  toast({
                    variant: 'destructive',
                    title: t('crud.messages.validationError'),
                    description: t('crud.messages.fillRequiredFields'),
                  })
                  return
                }

                // Determine status based on validity date
                let status: 'aktiv' | 'abgelaufen' | 'wird_abgelaufen' = 'aktiv'
                if (newDocument.gueltigBis) {
                  const validUntil = new Date(newDocument.gueltigBis)
                  const today = new Date()
                  const daysUntilExpiry = Math.floor((validUntil.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
                  
                  if (daysUntilExpiry < 0) {
                    status = 'abgelaufen'
                  } else if (daysUntilExpiry <= 30) {
                    status = 'wird_abgelaufen'
                  }
                }

                const document = {
                  id: Date.now().toString(),
                  typ: newDocument.typ,
                  titel: newDocument.titel,
                  dateiname: newDocument.dateiname,
                  gueltigBis: newDocument.gueltigBis || undefined,
                  hochgeladenAm: new Date().toISOString(),
                  status,
                }

                setLieferant(prev => ({
                  ...prev,
                  dokumente: [...(prev.dokumente || []), document],
                }))

                setNewDocumentDialogOpen(false)
                setNewDocument({ typ: 'rahmenvertrag', titel: '', dateiname: '', gueltigBis: '' })

                toast({
                  title: t('crud.messages.createSuccess', { entityType: t('crud.fields.document') }),
                })
              }}
              disabled={!newDocument.titel || !newDocument.dateiname}
            >
              {t('crud.actions.add')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// New Contact Form Component
function NewContactForm({ onSave, onCancel }: { onSave: (contact: any) => void; onCancel: () => void }) {
  const { t } = useTranslation()
  const [contact, setContact] = useState({ name: '', email: '', telefon: '', funktion: '' })

  return (
    <>
      <div className="space-y-4">
        <div>
          <Label htmlFor="contactName">{t('crud.fields.name')} *</Label>
          <Input
            id="contactName"
            value={contact.name}
            onChange={(e) => setContact(prev => ({ ...prev, name: e.target.value }))}
          />
        </div>
        <div>
          <Label htmlFor="contactEmail">{t('crud.fields.email')} *</Label>
          <Input
            id="contactEmail"
            type="email"
            value={contact.email}
            onChange={(e) => setContact(prev => ({ ...prev, email: e.target.value }))}
          />
        </div>
        <div>
          <Label htmlFor="contactPhone">{t('crud.fields.phone')}</Label>
          <Input
            id="contactPhone"
            type="tel"
            value={contact.telefon}
            onChange={(e) => setContact(prev => ({ ...prev, telefon: e.target.value }))}
          />
        </div>
        <div>
          <Label htmlFor="contactFunction">{t('crud.fields.function')}</Label>
          <Input
            id="contactFunction"
            value={contact.funktion}
            onChange={(e) => setContact(prev => ({ ...prev, funktion: e.target.value }))}
          />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          {t('common.cancel')}
        </Button>
        <Button onClick={() => onSave(contact)} disabled={!contact.name || !contact.email}>
          {t('common.save')}
        </Button>
      </DialogFooter>
    </>
  )
}

// New Bank Account Form Component
function NewBankAccountForm({ onSave, onCancel }: { onSave: (bank: any) => void; onCancel: () => void }) {
  const { t } = useTranslation()
  const [bank, setBank] = useState({ iban: '', bic: '', bankName: '', kontoinhaber: '', isDefault: false })

  return (
    <>
      <div className="space-y-4">
        <div>
          <Label htmlFor="bankIban">{t('crud.fields.iban')} *</Label>
          <Input
            id="bankIban"
            value={bank.iban}
            onChange={(e) => setBank(prev => ({ ...prev, iban: e.target.value }))}
            placeholder={t('crud.tooltips.placeholders.iban')}
          />
        </div>
        <div>
          <Label htmlFor="bankBic">{t('crud.fields.bic')}</Label>
          <Input
            id="bankBic"
            value={bank.bic}
            onChange={(e) => setBank(prev => ({ ...prev, bic: e.target.value }))}
            placeholder={t('crud.tooltips.placeholders.bicOptional')}
          />
        </div>
        <div>
          <Label htmlFor="bankName">{t('crud.fields.bankName')} *</Label>
          <Input
            id="bankName"
            value={bank.bankName}
            onChange={(e) => setBank(prev => ({ ...prev, bankName: e.target.value }))}
          />
        </div>
        <div>
          <Label htmlFor="bankAccountHolder">{t('crud.fields.accountHolder')} *</Label>
          <Input
            id="bankAccountHolder"
            value={bank.kontoinhaber}
            onChange={(e) => setBank(prev => ({ ...prev, kontoinhaber: e.target.value }))}
          />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="bankIsDefault"
            checked={bank.isDefault}
            onChange={(e) => setBank(prev => ({ ...prev, isDefault: e.target.checked }))}
          />
          <Label htmlFor="bankIsDefault" className="cursor-pointer">
            {t('crud.fields.default')}
          </Label>
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          {t('common.cancel')}
        </Button>
        <Button onClick={() => onSave(bank)} disabled={!bank.iban || !bank.bankName || !bank.kontoinhaber}>
          {t('common.save')}
        </Button>
      </DialogFooter>
    </>
  )
}

// New Classification Form Component
function NewClassificationForm({ onSave, onCancel }: { onSave: (klass: any) => void; onCancel: () => void }) {
  const { t } = useTranslation()
  const [klass, setKlass] = useState({ typ: '', wert: '' })

  return (
    <>
      <div className="space-y-4">
        <div>
          <Label htmlFor="classType">{t('crud.fields.type')} *</Label>
          <NativeSelect
            value={klass.typ}
            onValueChange={(value) => setKlass(prev => ({ ...prev, typ: value }))}
            options={[
              { value: 'Branche', label: t('crud.fields.industry') },
              { value: 'Zertifizierung', label: t('crud.fields.certification') },
              { value: 'Risiko', label: t('crud.fields.risk') },
              { value: 'Größe', label: t('crud.fields.size') },
            ]}
            placeholder={t('crud.fields.selectType')}
          />
        </div>
        <div>
          <Label htmlFor="classValue">{t('crud.fields.value')} *</Label>
          <Input
            id="classValue"
            value={klass.wert}
            onChange={(e) => setKlass(prev => ({ ...prev, wert: e.target.value }))}
          />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>
          {t('common.cancel')}
        </Button>
        <Button onClick={() => onSave(klass)} disabled={!klass.typ || !klass.wert}>
          {t('common.save')}
        </Button>
      </DialogFooter>
    </>
  )
}
