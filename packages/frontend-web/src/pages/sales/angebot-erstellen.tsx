import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Plus, Trash2 } from 'lucide-react'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

type AngebotData = {
  kunde: string
  ansprechpartner: string
  email: string
  telefon: string
  gueltigBis: string
  zahlungsbedingung: string
  positionen: Array<{
    artikel: string
    menge: number
    einheit: string
    preis: number
  }>
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
          {angebot.positionen.map((pos, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex gap-4">
                  <div className="flex-1">
                    <Label>{t('crud.fields.article')} *</Label>
                    <Input
                      value={pos.artikel}
                      onChange={(e) => updatePosition(index, 'artikel', e.target.value)}
                      placeholder={t('crud.tooltips.placeholders.articleExample')}
                    />
                  </div>
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
                <div className="mt-2 text-right text-sm text-muted-foreground">
                  {t('crud.fields.subtotal')}:{' '}
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                    pos.menge * pos.preis
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
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
