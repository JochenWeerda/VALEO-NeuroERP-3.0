/**
 * OP-Verwaltung Kreditoren
 * FIBU-AP-05: Offene Posten für Kreditoren verwalten
 * 
 * Basierend auf op-debitoren.tsx, aber für Kreditoren (Accounts Payable)
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'
import { useTranslation } from 'react-i18next'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für OP-Kreditoren
const opKreditorenSchema = z.object({
  kreditorId: z.string().min(1, "Kreditor ist erforderlich"),
  opNummer: z.string().min(1, "OP-Nummer ist erforderlich"),
  rechnungId: z.string().optional(),
  buchungsdatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Buchungsdatum muss YYYY-MM-DD Format haben"),
  faelligkeit: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Fälligkeit muss YYYY-MM-DD Format haben"),
  betrag: z.number().positive("Betrag muss positiv sein"),
  waehrung: z.string().default("EUR"),
  offen: z.number().min(0, "Offener Betrag kann nicht negativ sein"),
  skontoBetrag: z.number().min(0).optional(),
  skontoDatum: z.string().optional(),
  zahlungen: z.array(z.object({
    datum: z.string(),
    betrag: z.number(),
    typ: z.enum(['zahlung', 'skonto', 'gutschrift', 'storno']),
    referenz: z.string().optional()
  })).optional(),
  status: z.enum(['offen', 'teilbezahlt', 'ausgeglichen', 'mahnung', 'inkasso']),
  letzteZahlung: z.string().optional(),
  mahnstufe: z.number().min(0).max(3).default(0),
  notizen: z.string().optional()
})

// Konfiguration für OP-Kreditoren ObjectPage
function createOpKreditorenConfig(t: any): MaskConfig {
  const entityType = 'creditor'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kreditor')
  
  return {
    title: t('finance.opKreditoren.title', { defaultValue: 'OP-Verwaltung (Kreditoren)' }),
    subtitle: t('finance.opKreditoren.subtitle', { defaultValue: 'Offene Posten für Kreditoren verwalten und Zahlungen zuordnen' }),
    type: 'object-page',
    tabs: [
      {
        key: 'grunddaten',
        label: t('crud.detail.basicInfo', { defaultValue: 'Grunddaten' }),
        fields: [
          {
            name: 'kreditorId',
            label: t('crud.entities.creditor', { defaultValue: 'Kreditor' }),
            type: 'select',
            required: true,
            options: [
              { value: 'L001', label: 'L001 - Lieferant Nord GmbH' },
              { value: 'L002', label: 'L002 - Agrar-Service Süd' },
            ],
          },
          {
            name: 'opNummer',
            label: t('finance.opKreditoren.opNumber', { defaultValue: 'OP-Nummer' }),
            type: 'text',
            required: true,
          },
          {
            name: 'rechnungId',
            label: t('crud.fields.invoiceNumber', { defaultValue: 'Rechnungsnummer' }),
            type: 'text',
            required: false,
          },
          {
            name: 'buchungsdatum',
            label: t('crud.fields.bookingDate', { defaultValue: 'Buchungsdatum' }),
            type: 'date',
            required: true,
          },
          {
            name: 'faelligkeit',
            label: t('crud.fields.dueDate', { defaultValue: 'Fälligkeit' }),
            type: 'date',
            required: true,
          },
          {
            name: 'betrag',
            label: t('crud.fields.amount', { defaultValue: 'Betrag' }),
            type: 'number',
            required: true,
          },
          {
            name: 'waehrung',
            label: t('crud.fields.currency', { defaultValue: 'Währung' }),
            type: 'select',
            required: true,
            options: [
              { value: 'EUR', label: 'EUR' },
              { value: 'USD', label: 'USD' },
            ],
          },
        ],
      },
      {
        key: 'zahlungen',
        label: t('finance.opKreditoren.payments', { defaultValue: 'Zahlungen' }),
        fields: [
          {
            name: 'zahlungen',
            label: t('finance.opKreditoren.paymentList', { defaultValue: 'Zahlungsliste' }),
            type: 'array',
            fields: [
              {
                name: 'datum',
                label: t('crud.fields.date', { defaultValue: 'Datum' }),
                type: 'date',
              },
              {
                name: 'betrag',
                label: t('crud.fields.amount', { defaultValue: 'Betrag' }),
                type: 'number',
              },
              {
                name: 'typ',
                label: t('finance.opKreditoren.paymentType', { defaultValue: 'Typ' }),
                type: 'select',
                options: [
                  { value: 'zahlung', label: t('finance.opKreditoren.paymentTypes.payment', { defaultValue: 'Zahlung' }) },
                  { value: 'skonto', label: t('finance.opKreditoren.paymentTypes.skonto', { defaultValue: 'Skonto' }) },
                  { value: 'gutschrift', label: t('finance.opKreditoren.paymentTypes.credit', { defaultValue: 'Gutschrift' }) },
                  { value: 'storno', label: t('finance.opKreditoren.paymentTypes.cancellation', { defaultValue: 'Storno' }) },
                ],
              },
              {
                name: 'referenz',
                label: t('finance.opKreditoren.reference', { defaultValue: 'Referenz' }),
                type: 'text',
              },
            ],
          },
          {
            name: 'offen',
            label: t('finance.opKreditoren.openAmount', { defaultValue: 'Offener Betrag' }),
            type: 'number',
            required: true,
            readonly: true,
          },
        ],
      },
      {
        key: 'status',
        label: t('crud.fields.status', { defaultValue: 'Status' }),
        fields: [
          {
            name: 'status',
            label: t('crud.fields.status', { defaultValue: 'Status' }),
            type: 'select',
            required: true,
            options: [
              { value: 'offen', label: t('status.open', { defaultValue: 'Offen' }) },
              { value: 'teilbezahlt', label: t('status.partial', { defaultValue: 'Teilbezahlt' }) },
              { value: 'ausgeglichen', label: t('status.closed', { defaultValue: 'Ausgeglichen' }) },
              { value: 'mahnung', label: t('status.dunning', { defaultValue: 'Mahnung' }) },
              { value: 'inkasso', label: t('status.collection', { defaultValue: 'Inkasso' }) },
            ],
          },
          {
            name: 'mahnstufe',
            label: t('finance.opKreditoren.dunningLevel', { defaultValue: 'Mahnstufe' }),
            type: 'number',
            min: 0,
            max: 3,
          },
          {
            name: 'letzteZahlung',
            label: t('finance.opKreditoren.lastPayment', { defaultValue: 'Letzte Zahlung' }),
            type: 'date',
          },
        ],
      },
      {
        key: 'notizen',
        label: t('crud.fields.notes', { defaultValue: 'Notizen' }),
        fields: [
          {
            name: 'notizen',
            label: t('crud.fields.notes', { defaultValue: 'Notizen' }),
            type: 'textarea',
          },
        ],
      },
    ],
  }
}

export default function OpKreditorenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'creditor'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kreditor')
  
  const config = createOpKreditorenConfig(t)
  const { data, setData } = useMaskData(opKreditorenSchema)
  const { validate, errors } = useMaskValidation(opKreditorenSchema, data)
  
  const { handleSave, handleCancel } = useMaskActions({
    entityType: entityTypeLabel,
    data,
    validate,
    onSave: async (validData) => {
      // TODO: API call to save OP-Kreditor
      console.log('Saving OP-Kreditor:', validData)
      toast({
        title: t('common.success', { defaultValue: 'Erfolg' }),
        description: t('crud.feedback.createSuccess', { entityType: entityTypeLabel }),
      })
    },
    onCancel: () => navigate('/finance/kreditoren'),
  })

  return (
    <ObjectPage
      config={config}
      data={data}
      errors={errors}
      onDataChange={setData}
      onSave={handleSave}
      onCancel={handleCancel}
    />
  )
}

