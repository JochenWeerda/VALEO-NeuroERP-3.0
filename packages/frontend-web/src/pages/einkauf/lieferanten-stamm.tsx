import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Building2, Save, Plus, X, AlertTriangle, CheckCircle, XCircle, Archive, Lock } from 'lucide-react'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

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
    typ: 'zertifikat' | 'rahmenvertrag' | 'nda' | 'esg' | 'sonstiges'
    titel: string
    dateiname: string
    gueltigBis?: string
    hochgeladenAm: string
    status: 'aktiv' | 'abgelaufen' | 'wird_abgelaufen'
  }>
  bemerkungen?: string
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
  const [newDocument, setNewDocument] = useState({ typ: 'zertifikat' as const, titel: '', dateiname: '', gueltigBis: '' })

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
      let response
      try {
        response = await apiClient.get(`/api/partners/${id}?type=supplier`)
      } catch (e1) {
        try {
          response = await apiClient.get(`/api/einkauf/lieferanten/${id}`)
        } catch (e2) {
          // Fallback: Mock-Daten
          setLieferant({
            id: id || 'L-001',
            name: 'Saatgut AG',
            legalName: 'Saatgut AG GmbH',
            typ: 'Saatgut-Lieferant',
            kategorie: 'Saatgut',
            gruppe: 'Premium',
            strasse: 'Industriestr. 15',
            plz: '54321',
            ort: 'Südhausen',
            land: 'DE',
            email: 'info@saatgut-ag.de',
            telefon: '+49 987 654321',
            website: 'https://www.saatgut-ag.de',
            vatId: 'DE123456789',
            steuernummer: '123/456/78901',
            iban: 'DE89370400440532013000',
            bic: 'DEUTDEDBBER',
            bankName: 'Deutsche Bank',
            kontoinhaber: 'Saatgut AG',
            zahlungsbedingungen: '30 Tage netto',
            kreditlimit: 100000,
            qsNummer: 'QS-12345',
            bewertung: 4.5,
            status: 'aktiv',
            ansprechpartner: [
              { id: '1', name: 'Max Mustermann', email: 'max@saatgut-ag.de', telefon: '+49 987 654321', funktion: 'Einkauf' },
            ],
            bankkonten: [
              { id: '1', iban: 'DE89370400440532013000', bic: 'DEUTDEDBBER', bankName: 'Deutsche Bank', kontoinhaber: 'Saatgut AG', isDefault: true },
            ],
            klassifikationen: [
              { id: '1', typ: 'Branche', wert: 'Landwirtschaft' },
              { id: '2', typ: 'Zertifizierung', wert: 'Bio' },
            ],
          })
          setLoading(false)
          return
        }
      }

      if (response.data) {
        const data = response.data
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
      console.error('Fehler beim Laden des Lieferanten:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadDataError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setLoading(true)
    try {
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
        await apiClient.put(`/api/partners/${id}?type=supplier`, payload)
        toast({
          title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
        })
      } else {
        await apiClient.post('/api/partners?type=supplier', payload)
        toast({
          title: t('crud.messages.createSuccess', { entityType: entityTypeLabel }),
        })
        navigate('/einkauf/lieferanten')
      }
    } catch (error: any) {
      console.error('Fehler beim Speichern:', error)
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
      const response = await apiClient.get(`/api/partners?type=supplier&query=${encodeURIComponent(lieferant.name)}`)
      const results = response.data?.data || response.data || []
      const duplicates = results.filter((s: any) => 
        s.id !== lieferant.id && 
        (s.name?.toLowerCase().includes(lieferant.name.toLowerCase()) || 
         s.name?.toLowerCase() === lieferant.name.toLowerCase())
      )
      setDuplicateResults(duplicates)
      setDuplicateCheckDialogOpen(true)
    } catch (error: any) {
      console.error('Fehler beim Dublettencheck:', error)
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
      await handleSave()
      toast({
        title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
        description: 'Lieferant wurde gesperrt',
      })
      setBlockDialogOpen(false)
      setBlockReason('')
    } catch (error: any) {
      console.error('Fehler beim Sperren:', error)
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
      await handleSave()
      toast({
        title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
        description: 'Lieferant wurde archiviert',
      })
      setArchiveDialogOpen(false)
      navigate('/einkauf/lieferanten')
    } catch (error: any) {
      console.error('Fehler beim Archivieren:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.updateError', { entityType: entityTypeLabel }),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Building2 className="h-8 w-8" />
            <div>
              <h1 className="text-3xl font-bold">{lieferant.name || t('crud.actions.create') + ' ' + entityTypeLabel}</h1>
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
                  <Select value={lieferant.kategorie || ''} onValueChange={(value) => setLieferant(prev => ({ ...prev, kategorie: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder={t('crud.fields.selectCategory')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Saatgut">{t('crud.fields.categorySeed')}</SelectItem>
                      <SelectItem value="Düngemittel">{t('crud.fields.categoryFertilizer')}</SelectItem>
                      <SelectItem value="Landtechnik">{t('crud.fields.categoryMachinery')}</SelectItem>
                      <SelectItem value="Sonstiges">{t('common.other')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="gruppe">{t('crud.fields.group')}</Label>
                  <Select value={lieferant.gruppe || ''} onValueChange={(value) => setLieferant(prev => ({ ...prev, gruppe: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder={t('crud.fields.selectGroup')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Premium">{t('crud.fields.groupPremium')}</SelectItem>
                      <SelectItem value="Standard">{t('crud.fields.groupStandard')}</SelectItem>
                      <SelectItem value="Basis">{t('crud.fields.groupBasic')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="status">{t('crud.fields.status')}</Label>
                  <Select value={lieferant.status} onValueChange={(value: any) => setLieferant(prev => ({ ...prev, status: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="aktiv">{t('status.active')}</SelectItem>
                      <SelectItem value="gesperrt">{t('status.blocked')}</SelectItem>
                      <SelectItem value="archiviert">{t('status.inactive')}</SelectItem>
                    </SelectContent>
                  </Select>
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
                  <Select value={lieferant.land} onValueChange={(value) => setLieferant(prev => ({ ...prev, land: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="DE">{t('crud.fields.countryDE')}</SelectItem>
                      <SelectItem value="AT">{t('crud.fields.countryAT')}</SelectItem>
                      <SelectItem value="CH">{t('crud.fields.countryCH')}</SelectItem>
                      <SelectItem value="NL">{t('crud.fields.countryNL')}</SelectItem>
                      <SelectItem value="FR">{t('crud.fields.countryFR')}</SelectItem>
                    </SelectContent>
                  </Select>
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
                            <Badge variant="outline">
                              {doc.typ === 'zertifikat' ? t('crud.fields.certificate') :
                               doc.typ === 'rahmenvertrag' ? t('crud.fields.frameworkContract') :
                               doc.typ === 'nda' ? t('crud.fields.nda') :
                               doc.typ === 'esg' ? t('crud.fields.esg') :
                               t('crud.fields.other')}
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
                                onClick={() => {
                                  toast({
                                    title: t('crud.messages.downloadInfo'),
                                    description: t('crud.messages.downloadComingSoon'),
                                  })
                                }}
                              >
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
                  <Select value={lieferant.zahlungsbedingungen || ''} onValueChange={(value) => setLieferant(prev => ({ ...prev, zahlungsbedingungen: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder={t('crud.tooltips.placeholders.paymentTerms')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sofort">{t('crud.fields.paymentTermsImmediate')}</SelectItem>
                      <SelectItem value="14tage">{t('crud.fields.paymentTermsNet14')}</SelectItem>
                      <SelectItem value="30tage">{t('crud.fields.paymentTermsNet30')}</SelectItem>
                      <SelectItem value="60tage">{t('crud.fields.paymentTermsNet60')}</SelectItem>
                    </SelectContent>
                  </Select>
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
              <Select
                value={newDocument.typ}
                onValueChange={(value: 'zertifikat' | 'rahmenvertrag' | 'nda' | 'esg' | 'sonstiges') =>
                  setNewDocument(prev => ({ ...prev, typ: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="zertifikat">{t('crud.fields.certificate')}</SelectItem>
                  <SelectItem value="rahmenvertrag">{t('crud.fields.frameworkContract')}</SelectItem>
                  <SelectItem value="nda">{t('crud.fields.nda')}</SelectItem>
                  <SelectItem value="esg">{t('crud.fields.esg')}</SelectItem>
                  <SelectItem value="sonstiges">{t('crud.fields.other')}</SelectItem>
                </SelectContent>
              </Select>
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
              setNewDocument({ typ: 'zertifikat', titel: '', dateiname: '', gueltigBis: '' })
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
                setNewDocument({ typ: 'zertifikat', titel: '', dateiname: '', gueltigBis: '' })

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
          <Select value={klass.typ} onValueChange={(value) => setKlass(prev => ({ ...prev, typ: value }))}>
            <SelectTrigger>
              <SelectValue placeholder={t('crud.fields.selectType')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Branche">{t('crud.fields.industry')}</SelectItem>
              <SelectItem value="Zertifizierung">{t('crud.fields.certification')}</SelectItem>
              <SelectItem value="Risiko">{t('crud.fields.risk')}</SelectItem>
              <SelectItem value="Größe">{t('crud.fields.size')}</SelectItem>
            </SelectContent>
          </Select>
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
