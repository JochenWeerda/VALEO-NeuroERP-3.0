/**
 * Accounts Payable (AP) Invoice Form
 * FIBU-AP-02: Eingangsrechnungen
 * Formular zum Erstellen/Bearbeiten von Eingangsrechnungen
 */

import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate, useParams } from 'react-router-dom'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import { BelegFlowPanel } from '@/features/flows/BelegFlowPanel'
import ApprovalPanel from '@/features/workflow/ApprovalPanel'
import { getEntityTypeLabel, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'
import { Save, X } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

const ISO_DATE_LENGTH = 10
const DAYS_IN_MS = 24 * 60 * 60 * 1000
const NET_30_DAYS = 30

type APInvoice = {
  number: string
  date: string
  customerId: string  // supplier_id for AP
  sourceOrder?: string
  sourceDelivery?: string
  paymentTerms: string
  dueDate: string
  status: string
  notes?: string
  lines: Array<{
    article: string
    qty: number
    price: number
    vatRate: number
  }>
  subtotalNet: number
  totalTax: number
  totalGross: number
}

/**
 * AP Invoice Form Page
 * Eingangsrechnung erstellen/bearbeiten
 */
export default function APInvoiceFormPage(): JSX.Element {
  const { t } = useTranslation()
  const { push } = useToast()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const entityType = 'apInvoice'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Eingangsrechnung')

  const [invoice, setInvoice] = useState<APInvoice>({
    number: id || `AP-INV-${new Date().getFullYear()}-${String(Date.now()).slice(-4)}`,
    date: new Date().toISOString().slice(0, ISO_DATE_LENGTH),
    customerId: '',
    paymentTerms: 'net30',
    dueDate: new Date(Date.now() + NET_30_DAYS * DAYS_IN_MS).toISOString().slice(0, ISO_DATE_LENGTH),
    status: 'ENTWURF',
    notes: '',
    lines: [{ article: '', qty: 1, price: 0, vatRate: 19 }],
    subtotalNet: 0,
    totalTax: 0,
    totalGross: 0,
  })

  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let active = true
    async function load(): Promise<void> {
      if (!id) return
      setLoading(true)
      try {
        const { data } = await apiClient.get<APInvoice>(`/api/v1/finance/ap/invoices/${id}`)
        if (active && data) {
          setInvoice((prev) => ({ ...prev, ...data }))
        }
      } catch {
        push(getErrorMessage(t, 'load', entityType))
      } finally {
        if (active) setLoading(false)
      }
    }
    void load()
    return () => {
      active = false
    }
  }, [id, push, t, entityType])

  async function save(v: APInvoice): Promise<void> {
    setLoading(true)
    try {
      const url = id
        ? `/api/v1/finance/ap/invoices/${id}`
        : '/api/v1/finance/ap/invoices'
      if (id) {
        await apiClient.put(url, v)
      } else {
        await apiClient.post(url, v)
      }

      push(getSuccessMessage(t, id ? 'update' : 'create', entityType))
      if (!id) {
        navigate(`/finance/ap/invoices/${v.number}`)
      }
    } catch {
      push(getErrorMessage(t, id ? 'update' : 'create', entityType))
    } finally {
      setLoading(false)
    }
  }

  // Eingangsrechnung ist End-Beleg, keine Folgebelege
  const nextTypes: Array<{ to: string; label: string }> = []

  return (
    <div className="space-y-4 p-4">
      <BelegFlowPanel
        current={{
          id: invoice.number,
          type: entityTypeLabel,
          number: invoice.number,
          status: t('status.draft'),
        }}
        nextTypes={nextTypes}
        onCreateFollowUp={(): void => {
          // Keine Folgebelege
        }}
      />

      <ApprovalPanel domain="finance" doc={invoice} />

      <Card className="p-4">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>{t('crud.fields.invoiceNumber')}</Label>
              <Input value={invoice.number} disabled />
            </div>
            <div>
              <Label>{t('crud.fields.date')}</Label>
              <Input
                type="date"
                value={invoice.date}
                onChange={(e) =>
                  setInvoice((o) => ({
                    ...o,
                    date: e.target.value,
                  }))
                }
              />
            </div>
            <div>
              <Label>{t('crud.entities.supplier')}</Label>
              <Input
                value={invoice.customerId}
                onChange={(e) =>
                  setInvoice((o) => ({
                    ...o,
                    customerId: e.target.value,
                  }))
                }
                placeholder={t('finance.apInvoices.supplierPlaceholder')}
              />
            </div>
            <div>
              <Label>{t('crud.fields.dueDate')}</Label>
              <Input
                type="date"
                value={invoice.dueDate}
                onChange={(e) =>
                  setInvoice((o) => ({
                    ...o,
                    dueDate: e.target.value,
                  }))
                }
              />
            </div>
          </div>

          <div>
            <Label>{t('crud.fields.notes')}</Label>
            <Input
              value={invoice.notes || ''}
              onChange={(e) =>
                setInvoice((o) => ({
                  ...o,
                  notes: e.target.value,
                }))
              }
              placeholder={t('finance.apInvoices.notesPlaceholder')}
            />
          </div>

          <div className="flex items-center justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={() => navigate('/finance/ap/invoices')}>
              <X className="h-4 w-4 mr-2" />
              {t('common.cancel')}
            </Button>
            <Button onClick={() => save(invoice)} disabled={loading}>
              <Save className="h-4 w-4 mr-2" />
              {loading ? t('common.loading') : t('crud.actions.save')}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

