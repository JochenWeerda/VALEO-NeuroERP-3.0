import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Command, CommandInput, CommandList, CommandItem, CommandEmpty, CommandGroup } from '@/components/ui/command'
import { Badge } from '@/components/ui/badge'
import { Plus, Trash2, Check, ChevronsUpDown, AlertTriangle, Info } from 'lucide-react'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { apiClient } from '@/lib/api-client'
import { cn } from '@/lib/utils'

type Artikel = {
  id: string
  artikelnr: string
  artikelgruppe: string
  bezeichnung: string
  einheit: string
  preis: number
  eigenschaften?: string[]
  deklarationen?: string[]
  gefahrenpunkte?: string[]
  hinweise?: string
  kategorie?: string
}

type AngebotPosition = {
  artikelId?: string
  artikel: string
  artikelnr?: string
  artikelgruppe?: string
  menge: number
  einheit: string
  preis: number
  artikelDetails?: Artikel
}

type AngebotData = {
  kunde: string
  ansprechpartner: string
  email: string
  telefon: string
  gueltigBis: string
  zahlungsbedingung: string
  positionen: AngebotPosition[]
  notizen: string
}

export default function AngebotErstellenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'offer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Angebot')
  const [angebot, setAngebot] = useState<AngebotData>({
    kunde: '',
    ansprechpartner: '',
    email: '',
    telefon: '',
    gueltigBis: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    zahlungsbedingung: 'net30',
    positionen: [{ artikel: '', menge: 1, einheit: 't', preis: 0 }],
    notizen: '',
  })
  const [artikelSuche, setArtikelSuche] = useState<Record<number, string>>({})
  const [artikelErgebnisse, setArtikelErgebnisse] = useState<Record<number, Artikel[]>>({})
  const [artikelSucheOffen, setArtikelSucheOffen] = useState<Record<number, boolean>>({})
  const [empfehlungen, setEmpfehlungen] = useState<Artikel[]>([])

  // Lade Empfehlungen basierend auf ausgewählten Artikeln
  useEffect(() => {
    const geladeneArtikelIds = angebot.positionen
      .filter((pos) => pos.artikelId)
      .map((pos) => pos.artikelId!)
    
    if (geladeneArtikelIds.length > 0) {
      ladeEmpfehlungen(geladeneArtikelIds)
    } else {
      setEmpfehlungen([])
    }
  }, [angebot.positionen])

  async function ladeEmpfehlungen(artikelIds: string[]): Promise<void> {
    try {
      // Versuche API-Call für Empfehlungen
      const response = await apiClient.get<{ items: any[] }>('/api/v1/articles/recommendations', {
        params: { articleIds: artikelIds.join(','), limit: 6 },
      })
      
      const empfehlungen: Artikel[] = response.data.items.map((item: any) => ({
        id: item.id,
        artikelnr: item.article_number || '',
        artikelgruppe: item.article_number?.substring(0, 3) || '',
        bezeichnung: item.name || '',
        einheit: item.unit || 't',
        preis: typeof item.sales_price === 'string' ? Number(item.sales_price) : item.sales_price || 0,
        eigenschaften: item.properties || [],
        deklarationen: item.declarations || [],
        gefahrenpunkte: item.hazards || [],
        hinweise: item.notes || '',
        kategorie: item.category || '',
      }))
      
      setEmpfehlungen(empfehlungen)
    } catch (error) {
      // Falls API nicht verfügbar, versuche alternative Endpunkte oder verwende Mock-Daten
      console.warn('Empfehlungs-API nicht verfügbar, verwende Fallback:', error)
      
      try {
        // Alternative: Suche nach ähnlichen Artikeln in derselben Kategorie
        const erstePosition = angebot.positionen.find((pos) => pos.artikelId)
        if (erstePosition?.artikelDetails?.kategorie) {
          const kategorieResponse = await apiClient.get<{ items: any[] }>('/api/v1/articles', {
            params: {
              category: erstePosition.artikelDetails.kategorie,
              limit: 6,
              exclude: artikelIds.join(','),
            },
          })
          
          const kategorieEmpfehlungen: Artikel[] = kategorieResponse.data.items
            .filter((item: any) => !artikelIds.includes(item.id))
            .slice(0, 6)
            .map((item: any) => ({
              id: item.id,
              artikelnr: item.article_number || '',
              artikelgruppe: item.article_number?.substring(0, 3) || '',
              bezeichnung: item.name || '',
              einheit: item.unit || 't',
              preis: typeof item.sales_price === 'string' ? Number(item.sales_price) : item.sales_price || 0,
              eigenschaften: item.properties || [],
              deklarationen: item.declarations || [],
              gefahrenpunkte: item.hazards || [],
              hinweise: item.notes || '',
              kategorie: item.category || '',
            }))
          
          setEmpfehlungen(kategorieEmpfehlungen)
        } else {
          setEmpfehlungen([])
        }
      } catch (fallbackError) {
        console.warn('Fallback-Empfehlungen nicht verfügbar:', fallbackError)
        setEmpfehlungen([])
      }
    }
  }

  async function sucheArtikel(query: string, positionIndex: number): Promise<void> {
    if (query.length < 2) {
      setArtikelErgebnisse((prev) => ({ ...prev, [positionIndex]: [] }))
      return
    }

    try {
      const response = await apiClient.get<{ items: any[] }>('/api/v1/articles', {
        params: { search: query, limit: 15 },
      })
      
      const artikel: Artikel[] = response.data.items.map((item: any) => ({
        id: item.id,
        artikelnr: item.article_number || '',
        artikelgruppe: item.article_number?.substring(0, 3) || '',
        bezeichnung: item.name || '',
        einheit: item.unit || 't',
        preis: typeof item.sales_price === 'string' ? Number(item.sales_price) : item.sales_price || 0,
        eigenschaften: item.properties || [],
        deklarationen: item.declarations || [],
        gefahrenpunkte: item.hazards || [],
        hinweise: item.notes || '',
        kategorie: item.category || '',
      }))
      
      setArtikelErgebnisse((prev) => ({ ...prev, [positionIndex]: artikel }))
    } catch (error) {
      console.error('Fehler beim Suchen von Artikeln:', error)
      setArtikelErgebnisse((prev) => ({ ...prev, [positionIndex]: [] }))
    }
  }

  function waehleArtikel(artikel: Artikel, positionIndex: number): void {
    updatePosition(positionIndex, 'artikelId', artikel.id)
    updatePosition(positionIndex, 'artikel', artikel.bezeichnung)
    updatePosition(positionIndex, 'artikelnr', artikel.artikelnr)
    updatePosition(positionIndex, 'artikelgruppe', artikel.artikelgruppe)
    updatePosition(positionIndex, 'einheit', artikel.einheit)
    updatePosition(positionIndex, 'preis', artikel.preis)
    
    // Setze Artikel-Details für Anzeige
    setAngebot((prev) => ({
      ...prev,
      positionen: prev.positionen.map((pos, i) =>
        i === positionIndex ? { ...pos, artikelDetails: artikel } : pos
      ),
    }))
    
    setArtikelSucheOffen((prev) => ({ ...prev, [positionIndex]: false }))
    setArtikelSuche((prev) => ({ ...prev, [positionIndex]: '' }))
  }

  function updateField<K extends keyof AngebotData>(key: K, value: AngebotData[K]): void {
    setAngebot((prev) => ({ ...prev, [key]: value }))
  }

  function addPosition(): void {
    setAngebot((prev) => ({
      ...prev,
      positionen: [...prev.positionen, { artikel: '', menge: 1, einheit: 't', preis: 0 }],
    }))
  }

  function updatePosition(index: number, field: string, value: string | number): void {
    setAngebot((prev) => ({
      ...prev,
      positionen: prev.positionen.map((pos, i) =>
        i === index ? { ...pos, [field]: value } : pos
      ),
    }))
  }

  function removePosition(index: number): void {
    setAngebot((prev) => ({
      ...prev,
      positionen: prev.positionen.filter((_, i) => i !== index),
    }))
  }

  async function handleSubmit(): Promise<void> {
    // TODO: API-Call
    console.log('Angebot erstellen:', angebot)
    navigate('/sales/angebote-liste')
  }

  const gesamtBetrag = angebot.positionen.reduce((sum, pos) => sum + pos.menge * pos.preis, 0)

  const steps = [
    {
      id: 'kunde',
      title: t('crud.entities.customer'),
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="kunde">{t('crud.entities.customer')} *</Label>
            <Input
              id="kunde"
              value={angebot.kunde}
              onChange={(e) => updateField('kunde', e.target.value)}
              placeholder={t('crud.tooltips.placeholders.customerExample')}
              required
            />
          </div>
          <div>
            <Label htmlFor="ansprechpartner">{t('crud.fields.contactPerson')}</Label>
            <Input
              id="ansprechpartner"
              value={angebot.ansprechpartner}
              onChange={(e) => updateField('ansprechpartner', e.target.value)}
              placeholder={t('crud.tooltips.placeholders.contactPersonName')}
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="email">{t('crud.fields.email')}</Label>
              <Input
                id="email"
                type="email"
                value={angebot.email}
                onChange={(e) => updateField('email', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.email')}
              />
            </div>
            <div>
              <Label htmlFor="telefon">{t('crud.fields.phone')}</Label>
              <Input
                id="telefon"
                type="tel"
                value={angebot.telefon}
                onChange={(e) => updateField('telefon', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.phone')}
              />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'konditionen',
      title: t('crud.fields.conditions'),
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="gueltigBis">{t('crud.fields.validUntil')} *</Label>
            <Input
              id="gueltigBis"
              type="date"
              value={angebot.gueltigBis}
              onChange={(e) => updateField('gueltigBis', e.target.value)}
              required
            />
            <p className="mt-1 text-sm text-muted-foreground">
              {t('crud.tooltips.fields.standard30Days')}
            </p>
          </div>
          <div>
            <Label htmlFor="zahlungsbedingung">{t('crud.fields.paymentTerms')}</Label>
            <select
              id="zahlungsbedingung"
              value={angebot.zahlungsbedingung}
              onChange={(e) => updateField('zahlungsbedingung', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="net30">{t('paymentTerms.net30')}</option>
              <option value="net14">{t('paymentTerms.net14')}</option>
              <option value="net7">{t('paymentTerms.net7')}</option>
              <option value="cash">{t('crud.fields.cash')}</option>
              <option value="prepay">{t('paymentTerms.prepay')}</option>
            </select>
          </div>
        </div>
      ),
    },
    {
      id: 'positionen',
      title: t('crud.fields.positions'),
      content: (
        <div className="space-y-4">
          {angebot.positionen.map((pos, index) => {
            const sucheQuery = artikelSuche[index] || ''
            const ergebnisse = artikelErgebnisse[index] || []
            const istOffen = artikelSucheOffen[index] || false
            
            return (
              <Card key={index}>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {/* Artikelauswahl */}
                    <div className="flex-1">
                      <Label>{t('crud.fields.article')} *</Label>
                      <Popover open={istOffen} onOpenChange={(open) => {
                        setArtikelSucheOffen((prev) => ({ ...prev, [index]: open }))
                        if (open && sucheQuery.length >= 2) {
                          sucheArtikel(sucheQuery, index)
                        }
                      }}>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            role="combobox"
                            className="w-full justify-between"
                            onClick={() => {
                              setArtikelSucheOffen((prev) => ({ ...prev, [index]: !prev[index] }))
                            }}
                          >
                            {pos.artikel || t('crud.tooltips.placeholders.articleExample')}
                            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-[600px] p-0" align="start">
                          <Command>
                            <CommandInput
                              placeholder={t('crud.tooltips.placeholders.articleSearch')}
                              value={sucheQuery}
                              onValueChange={(value) => {
                                setArtikelSuche((prev) => ({ ...prev, [index]: value }))
                                if (value.length >= 2) {
                                  sucheArtikel(value, index)
                                }
                              }}
                            />
                            <CommandList>
                              {ergebnisse.length === 0 ? (
                                <CommandEmpty>
                                  {sucheQuery.length < 2
                                    ? t('crud.messages.enterAtLeast2Characters')
                                    : t('crud.messages.noArticlesFound')}
                                </CommandEmpty>
                              ) : (
                                <CommandGroup>
                                  {ergebnisse.map((artikel) => (
                                    <CommandItem
                                      key={artikel.id}
                                      value={`${artikel.artikelnr} ${artikel.bezeichnung}`}
                                      onSelect={() => waehleArtikel(artikel, index)}
                                    >
                                      <Check
                                        className={cn(
                                          'mr-2 h-4 w-4',
                                          pos.artikelId === artikel.id ? 'opacity-100' : 'opacity-0'
                                        )}
                                      />
                                      <div className="flex-1">
                                        <div className="font-medium">{artikel.bezeichnung}</div>
                                        <div className="text-sm text-muted-foreground">
                                          {artikel.artikelgruppe && `${artikel.artikelgruppe}-`}
                                          {artikel.artikelnr}
                                          {artikel.kategorie && ` • ${artikel.kategorie}`}
                                        </div>
                                      </div>
                                      <div className="text-right">
                                        <div className="font-semibold">
                                          {new Intl.NumberFormat('de-DE', {
                                            style: 'currency',
                                            currency: 'EUR',
                                          }).format(artikel.preis)}
                                        </div>
                                        <div className="text-xs text-muted-foreground">{artikel.einheit}</div>
                                      </div>
                                    </CommandItem>
                                  ))}
                                </CommandGroup>
                              )}
                            </CommandList>
                          </Command>
                        </PopoverContent>
                      </Popover>
                      {pos.artikelnr && (
                        <p className="mt-1 text-xs text-muted-foreground">
                          {t('crud.fields.articleNumber')}: {pos.artikelgruppe && `${pos.artikelgruppe}-`}
                          {pos.artikelnr}
                        </p>
                      )}
                    </div>

                    {/* Artikeleigenschaften */}
                    {pos.artikelDetails && (
                      <div className="rounded-lg border bg-muted/50 p-3 space-y-2">
                        {pos.artikelDetails.eigenschaften && pos.artikelDetails.eigenschaften.length > 0 && (
                          <div>
                            <Label className="text-xs font-semibold">{t('crud.fields.properties')}</Label>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {pos.artikelDetails.eigenschaften.map((eigenschaft, i) => (
                                <Badge key={i} variant="secondary" className="text-xs">
                                  {eigenschaft}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        {pos.artikelDetails.deklarationen && pos.artikelDetails.deklarationen.length > 0 && (
                          <div>
                            <Label className="text-xs font-semibold">{t('crud.fields.declarations')}</Label>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {pos.artikelDetails.deklarationen.map((deklaration, i) => (
                                <Badge key={i} variant="outline" className="text-xs">
                                  {deklaration}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        {pos.artikelDetails.gefahrenpunkte && pos.artikelDetails.gefahrenpunkte.length > 0 && (
                          <div>
                            <Label className="text-xs font-semibold text-orange-600 flex items-center gap-1">
                              <AlertTriangle className="h-3 w-3" />
                              {t('crud.fields.hazards')}
                            </Label>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {pos.artikelDetails.gefahrenpunkte.map((gefahr, i) => (
                                <Badge key={i} variant="destructive" className="text-xs">
                                  {gefahr}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        {pos.artikelDetails.hinweise && (
                          <div>
                            <Label className="text-xs font-semibold flex items-center gap-1">
                              <Info className="h-3 w-3" />
                              {t('crud.fields.notes')}
                            </Label>
                            <p className="text-xs text-muted-foreground mt-1">{pos.artikelDetails.hinweise}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Menge, Einheit, Preis */}
                    <div className="flex gap-4">
                      <div className="w-24">
                        <Label>{t('crud.fields.quantity')}</Label>
                        <Input
                          type="number"
                          value={pos.menge}
                          onChange={(e) => updatePosition(index, 'menge', Number(e.target.value))}
                          min="0"
                        />
                      </div>
                      <div className="w-20">
                        <Label>{t('crud.fields.unit')}</Label>
                        <select
                          value={pos.einheit}
                          onChange={(e) => updatePosition(index, 'einheit', e.target.value)}
                          className="w-full rounded-md border border-input bg-background px-3 py-2"
                        >
                          <option value="t">{t('units.t')}</option>
                          <option value="kg">{t('units.kg')}</option>
                          <option value="l">{t('units.l')}</option>
                          <option value="Stk">{t('units.pcs')}</option>
                        </select>
                      </div>
                      <div className="w-32">
                        <Label>{t('crud.fields.price')} (€)</Label>
                        <Input
                          type="number"
                          value={pos.preis}
                          onChange={(e) => updatePosition(index, 'preis', Number(e.target.value))}
                          min="0"
                          step="0.01"
                        />
                      </div>
                      <div className="flex items-end">
                        <Button
                          type="button"
                          variant="outline"
                          size="icon"
                          onClick={() => removePosition(index)}
                          disabled={angebot.positionen.length === 1}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="text-right text-sm text-muted-foreground">
                      {t('crud.fields.subtotal')}:{' '}
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                        pos.menge * pos.preis
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
          
          {/* Empfehlungen */}
          {empfehlungen.length > 0 && (
            <Card>
              <CardContent className="pt-6">
                <h4 className="text-sm font-semibold mb-3">{t('crud.fields.recommendations')}</h4>
                <div className="grid gap-2 sm:grid-cols-2">
                  {empfehlungen.map((artikel) => (
                    <Button
                      key={artikel.id}
                      variant="outline"
                      className="justify-start h-auto p-3"
                      onClick={() => {
                        addPosition()
                        const newIndex = angebot.positionen.length
                        waehleArtikel(artikel, newIndex)
                      }}
                    >
                      <div className="flex-1 text-left">
                        <div className="font-medium">{artikel.bezeichnung}</div>
                        <div className="text-xs text-muted-foreground">
                          {artikel.artikelgruppe && `${artikel.artikelgruppe}-`}
                          {artikel.artikelnr}
                        </div>
                      </div>
                      <div className="text-right ml-2">
                        <div className="font-semibold">
                          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                            artikel.preis
                          )}
                        </div>
                      </div>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          
          <Button type="button" variant="outline" className="w-full gap-2" onClick={addPosition}>
            <Plus className="h-4 w-4" />
            {t('crud.actions.addPosition')}
          </Button>
        </div>
      ),
    },
    {
      id: 'notizen',
      title: t('crud.fields.notes'),
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="notizen">{t('crud.fields.internalNotes')} ({t('common.optional')})</Label>
            <Textarea
              id="notizen"
              value={angebot.notizen}
              onChange={(e) => updateField('notizen', e.target.value)}
              placeholder={t('crud.tooltips.placeholders.offerNotes')}
              rows={6}
            />
          </div>
        </div>
      ),
    },
    {
      id: 'zusammenfassung',
      title: t('crud.detail.summary'),
      content: (
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <h3 className="mb-4 text-lg font-semibold">{t('crud.fields.offerData')}</h3>
              <dl className="grid gap-3 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.entities.customer')}</dt>
                  <dd className="text-sm">{angebot.kunde || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.fields.contactPerson')}</dt>
                  <dd className="text-sm">{angebot.ansprechpartner || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.fields.email')}</dt>
                  <dd className="text-sm">{angebot.email || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.fields.phone')}</dt>
                  <dd className="text-sm">{angebot.telefon || '-'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.fields.validUntil')}</dt>
                  <dd className="text-sm">
                    {new Date(angebot.gueltigBis).toLocaleDateString('de-DE')}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">{t('crud.fields.paymentTerms')}</dt>
                  <dd className="text-sm">{t(`paymentTerms.${angebot.zahlungsbedingung}`, { defaultValue: angebot.zahlungsbedingung })}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="mb-4 text-lg font-semibold">{t('crud.fields.positions')}</h3>
              <div className="space-y-2">
                {angebot.positionen.map((pos, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span>
                      {pos.artikel || t('crud.fields.article')} ({pos.menge} {pos.einheit})
                    </span>
                    <span className="font-medium">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                        pos.menge * pos.preis
                      )}
                    </span>
                  </div>
                ))}
                <div className="mt-4 flex justify-between border-t pt-2 font-semibold">
                  <span>{t('crud.fields.totalSum')}</span>
                  <span>
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                      gesamtBetrag
                    )}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {angebot.notizen && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="mb-2 text-lg font-semibold">{t('crud.fields.notes')}</h3>
                <p className="text-sm text-muted-foreground">{angebot.notizen}</p>
              </CardContent>
            </Card>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title={t('crud.actions.create') + ' ' + entityTypeLabel}
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/sales/angebote-liste')}
      />
    </div>
  )
}
