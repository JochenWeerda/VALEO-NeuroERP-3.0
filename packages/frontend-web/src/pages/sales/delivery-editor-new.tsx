/**
 * Lieferschein-Erfassungsmaske
 * Nachbau der zvoove Lieferschein-Maske basierend auf Screenshots
 * 
 * Workflow:
 * 1. Menü Lieferschein erstellen
 * 2. Feld Kunde - Kunde auswählen
 * 3. Feld Artikel Button ... drücken
 * 4. Artikel auswählen (Suchmaske)
 * 5. Klick auf Position OK
 * 6. Nächster Artikel oder klick auf Lieferschein drucken
 * 7. Im Auswahlfenster Drucker und Formularvorlage wählen oder übernehmen
 * 8. Druck bestätigen mit OK
 * 9. Damit schließen das Druckfenster und der Lieferschein wird gebucht
 * 10. Anschließend neuen Kunden aussuchen oder Eingabemaske schließen
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/components/ui/toast-provider'
import { CustomerSelectionDialog, type Customer } from '@/components/sales/CustomerSelectionDialog'
import { ArticleSearchDialog, type Article } from '@/components/sales/ArticleSearchDialog'
import { LieferscheinDruckDialog, type PrintOptions } from '@/components/sales/LieferscheinDruckDialog'
import { apiClient } from '@/lib/api-client'
import { MoreHorizontal, Check, Printer, Save } from 'lucide-react'

type DeliveryNotePosition = {
  positionNumber: number
  articleNumber: string
  articleDescription: string
  quantity: number
  unit: string
  listPrice: number
  discount: number
  netPrice: number
  netAmount: number
  branch?: string
  location?: string
}

type DeliveryNote = {
  deliveryNumber: string
  deliveryDate: string
  deliveryTime: string
  costCenter: string
  isCreditNote: boolean
  referenceInvoiceNumber: string
  branch: string
  representative: string
  operator: string
  truckNumber: string
  customerId: string
  customerName: string
  customerAccount: string
  creditLimit: string
  isPrinted: boolean
  isDelivered: boolean
  invoiceNumber: string
  positions: DeliveryNotePosition[]
  netTotal: number
  vatTotal: number
  grossTotal: number
  total: number
}

export default function DeliveryEditorNewPage(): JSX.Element {
  const navigate = useNavigate()
  const { push } = useToast()
  
  const [deliveryNote, setDeliveryNote] = useState<DeliveryNote>({
    deliveryNumber: '2600894',
    deliveryDate: new Date().toISOString().split('T')[0].split('-').reverse().join('.'),
    deliveryTime: new Date().toTimeString().slice(0, 5),
    costCenter: '0',
    isCreditNote: false,
    referenceInvoiceNumber: '',
    branch: '0',
    representative: 'JW',
    operator: 'JW',
    truckNumber: '0',
    customerId: '',
    customerName: '',
    customerAccount: '',
    creditLimit: '',
    isPrinted: false,
    isDelivered: false,
    invoiceNumber: '',
    positions: [],
    netTotal: 0,
    vatTotal: 0,
    grossTotal: 0,
    total: 0,
  })

  const [currentPosition, setCurrentPosition] = useState<Partial<DeliveryNotePosition>>({
    positionNumber: 10,
    articleNumber: '',
    articleDescription: '',
    quantity: 0,
    unit: '',
    listPrice: 0,
    discount: 0,
    netPrice: 0,
    netAmount: 0,
  })

  const [showCustomerDialog, setShowCustomerDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [showPrintDialog, setShowPrintDialog] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  const handleCustomerSelect = (customer: Customer): void => {
    setDeliveryNote((prev) => ({
      ...prev,
      customerId: customer.id,
      customerName: customer.name,
      customerAccount: customer.debitorAccount,
    }))
  }

  const handleArticleSelect = (article: Article): void => {
    setCurrentPosition((prev) => ({
      ...prev,
      articleNumber: article.articleNumber,
      articleDescription: article.description,
      unit: article.unit || 'Stk',
    }))
  }

  const handlePositionOK = (): void => {
    if (!currentPosition.articleNumber || !currentPosition.quantity) {
      push('Bitte Artikel und Menge eingeben')
      return
    }

    const position: DeliveryNotePosition = {
      positionNumber: currentPosition.positionNumber || deliveryNote.positions.length * 10 + 10,
      articleNumber: currentPosition.articleNumber || '',
      articleDescription: currentPosition.articleDescription || '',
      quantity: currentPosition.quantity || 0,
      unit: currentPosition.unit || 'Stk',
      listPrice: currentPosition.listPrice || 0,
      discount: currentPosition.discount || 0,
      netPrice: currentPosition.netPrice || 0,
      netAmount: currentPosition.netAmount || 0,
    }

    setDeliveryNote((prev) => ({
      ...prev,
      positions: [...prev.positions, position],
    }))

    // Reset current position
    setCurrentPosition({
      positionNumber: (deliveryNote.positions.length + 1) * 10 + 10,
      articleNumber: '',
      articleDescription: '',
      quantity: 0,
      unit: '',
      listPrice: 0,
      discount: 0,
      netPrice: 0,
      netAmount: 0,
    })
  }

  const handlePrint = async (options: PrintOptions): Promise<void> => {
    setIsSaving(true)
    try {
      const noteId = deliveryNote.deliveryNumber
      const params = new URLSearchParams()
      params.append('template', options.formatvorlage)
      params.append('copies', String(options.anzahlDrucke))

      await apiClient.post(`/api/v1/sales/delivery-notes/${noteId}/print?${params.toString()}`)
      await apiClient.post(`/api/v1/sales/delivery-notes/${noteId}/post`)

      push('Lieferschein erfolgreich gedruckt und gebucht')
      setShowPrintDialog(false)
      setDeliveryNote((prev) => ({
        ...prev,
        deliveryNumber: `LS-${Date.now().toString(36).toUpperCase()}`,
        customerId: '',
        customerName: '',
        customerAccount: '',
        isPrinted: false,
        isDelivered: false,
        invoiceNumber: '',
        positions: [],
        netTotal: 0,
        vatTotal: 0,
        grossTotal: 0,
        total: 0,
      }))
    } catch (error: any) {
      push(`Fehler beim Drucken: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsSaving(false)
    }
  }

  const persistDelivery = async (): Promise<void> => {
    await apiClient.post('/api/v1/sales/delivery-notes', {
      deliveryNumber: deliveryNote.deliveryNumber,
      customerId: deliveryNote.customerId,
      positions: deliveryNote.positions,
    })
    push('Lieferschein erfolgreich gespeichert')
  }

  const handleSave = async (): Promise<void> => {
    setIsSaving(true)
    try {
      await persistDelivery()
    } catch (error) {
      push('Fehler beim Speichern des Lieferscheins')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-4 p-4">
      <div className="border-b-2 border-green-600 pb-2">
        <h1 className="text-xl font-bold text-green-700">LIEFERSCHEIN-ERFASSUNG</h1>
      </div>

      {/* Lieferschein-Erfassung Header */}
      <Card className="p-4">
        <div className="grid grid-cols-3 gap-4">
          {/* Linke Spalte */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label className="w-32">Liefersch.-Nr.:</Label>
              <Input value={deliveryNote.deliveryNumber} readOnly className="flex-1" />
              <Button variant="ghost" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-32">Liefer-Datum:</Label>
              <Input
                type="date"
                value={deliveryNote.deliveryDate.split('.').reverse().join('-')}
                onChange={(e) =>
                  setDeliveryNote((prev) => ({
                    ...prev,
                    deliveryDate: e.target.value.split('-').reverse().join('.'),
                  }))
                }
                className="flex-1"
              />
              <Input
                type="time"
                value={deliveryNote.deliveryTime}
                onChange={(e) => setDeliveryNote((prev) => ({ ...prev, deliveryTime: e.target.value }))}
                className="w-20"
              />
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-32">Kostenstelle:</Label>
              <Input
                value={deliveryNote.costCenter}
                onChange={(e) => setDeliveryNote((prev) => ({ ...prev, costCenter: e.target.value }))}
                className="flex-1"
              />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                checked={deliveryNote.isCreditNote}
                onCheckedChange={(checked) =>
                  setDeliveryNote((prev) => ({ ...prev, isCreditNote: checked === true }))
                }
              />
              <Label>Gutschrift kennzeichnen</Label>
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-32">Re.-Nr. (Bezug):</Label>
              <Input
                value={deliveryNote.referenceInvoiceNumber}
                onChange={(e) =>
                  setDeliveryNote((prev) => ({ ...prev, referenceInvoiceNumber: e.target.value }))
                }
                className="flex-1"
              />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                checked={deliveryNote.isPrinted}
                onCheckedChange={(checked) =>
                  setDeliveryNote((prev) => ({ ...prev, isPrinted: checked === true }))
                }
              />
              <Label>gedruckt</Label>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                checked={deliveryNote.isDelivered}
                onCheckedChange={(checked) =>
                  setDeliveryNote((prev) => ({ ...prev, isDelivered: checked === true }))
                }
              />
              <Label>ausgeliefert</Label>
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-32">fakturiert: Rechn.-Nr.:</Label>
              <Input
                value={deliveryNote.invoiceNumber}
                onChange={(e) => setDeliveryNote((prev) => ({ ...prev, invoiceNumber: e.target.value }))}
                className="flex-1"
              />
            </div>
          </div>

          {/* Mittlere Spalte */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label className="w-32">Niederlassung:</Label>
              <Input value={deliveryNote.branch} className="flex-1" />
              <Button variant="ghost" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-32">Vertreter:</Label>
              <Input value={deliveryNote.representative} className="flex-1" />
              <Button variant="ghost" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-32">Bediener:</Label>
              <Input value={deliveryNote.operator} className="flex-1" />
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-32">Lkw-Nr.:</Label>
              <Input
                value={deliveryNote.truckNumber}
                onChange={(e) => setDeliveryNote((prev) => ({ ...prev, truckNumber: e.target.value }))}
                className="flex-1"
              />
            </div>
          </div>

          {/* Rechte Spalte - Kunde */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Button onClick={() => setShowCustomerDialog(true)}>KUNDE</Button>
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-32">Debitor-Kto.:</Label>
              <Input value={deliveryNote.customerAccount} readOnly className="flex-1" />
              <Button variant="ghost" size="sm" onClick={() => setShowCustomerDialog(true)}>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
            {deliveryNote.customerName && (
              <div className="text-sm">
                <div>{deliveryNote.customerName}</div>
              </div>
            )}
            <div className="flex items-center gap-2">
              <Label className="w-32">Kredit-Limit:</Label>
              <Input
                value={deliveryNote.creditLimit}
                onChange={(e) => setDeliveryNote((prev) => ({ ...prev, creditLimit: e.target.value }))}
                className="flex-1"
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Positionen-Tabelle */}
      <Card className="p-4">
        <h2 className="mb-2 font-semibold">Positionen</h2>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Pos.-Nr.</TableHead>
                <TableHead>Artikel-Nr.</TableHead>
                <TableHead>Bezeichn...</TableHead>
                <TableHead>Menge</TableHead>
                <TableHead>Einheit</TableHead>
                <TableHead>Listenpreis</TableHead>
                <TableHead>Rabatt</TableHead>
                <TableHead>Netto-Pr...</TableHead>
                <TableHead>Netto-Be...</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {deliveryNote.positions.map((position) => (
                <TableRow key={position.positionNumber}>
                  <TableCell>{position.positionNumber}</TableCell>
                  <TableCell>{position.articleNumber}</TableCell>
                  <TableCell>{position.articleDescription}</TableCell>
                  <TableCell>{position.quantity}</TableCell>
                  <TableCell>{position.unit}</TableCell>
                  <TableCell>{position.listPrice.toFixed(2)}</TableCell>
                  <TableCell>{position.discount}%</TableCell>
                  <TableCell>{position.netPrice.toFixed(2)}</TableCell>
                  <TableCell>{position.netAmount.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* Positions-Details */}
      <Card className="p-4">
        <h2 className="mb-2 font-semibold">Positions-Details</h2>
        <div className="grid grid-cols-4 gap-4">
          <div className="space-y-2">
            <Label>Pos.-Nr.:</Label>
            <Input value={currentPosition.positionNumber || ''} readOnly />
          </div>
          <div className="space-y-2">
            <Label>Artikel-Nr.:</Label>
            <div className="flex gap-2">
              <Input
                value={currentPosition.articleNumber || ''}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({ ...prev, articleNumber: e.target.value }))
                }
                className="flex-1"
              />
              <Button variant="ghost" size="sm" onClick={() => setShowArticleDialog(true)}>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="space-y-2">
            <Label>Artikel-Bezeichn:</Label>
            <Input value={currentPosition.articleDescription || ''} readOnly />
          </div>
          <div className="space-y-2">
            <Label>Menge/Gebinde:</Label>
            <Input
              type="number"
              value={currentPosition.quantity || 0}
              onChange={(e) =>
                setCurrentPosition((prev) => ({ ...prev, quantity: Number(e.target.value) }))
              }
            />
          </div>
          <div className="space-y-2">
            <Label>Einheit:</Label>
            <Input value={currentPosition.unit || ''} readOnly />
          </div>
          <div className="space-y-2">
            <Label>Listenpreis:</Label>
            <Input
              type="number"
              value={currentPosition.listPrice || 0}
              onChange={(e) =>
                setCurrentPosition((prev) => ({ ...prev, listPrice: Number(e.target.value) }))
              }
            />
          </div>
          <div className="space-y-2">
            <Label>Rabatt:</Label>
            <Input
              type="number"
              value={currentPosition.discount || 0}
              onChange={(e) =>
                setCurrentPosition((prev) => ({ ...prev, discount: Number(e.target.value) }))
              }
            />
          </div>
          <div className="space-y-2">
            <Label>Einh.-Preis:</Label>
            <Input value={currentPosition.netPrice || 0} readOnly />
          </div>
          <div className="space-y-2">
            <Label>Betrag:</Label>
            <Input value={currentPosition.netAmount || 0} readOnly />
          </div>
          <div className="flex items-end">
            <Button onClick={handlePositionOK} className="gap-2">
              <Check className="h-4 w-4" />
              Zeile OK
            </Button>
          </div>
        </div>
      </Card>

      {/* Summen */}
      <Card className="p-4">
        <h2 className="mb-2 font-semibold">Summen</h2>
        <div className="grid grid-cols-5 gap-4">
          <div>
            <Label>Netto</Label>
            <Input value={deliveryNote.netTotal.toFixed(2)} readOnly />
          </div>
          <div>
            <Label>MWSt.</Label>
            <Input value={deliveryNote.vatTotal.toFixed(2)} readOnly />
          </div>
          <div>
            <Label>Brutto</Label>
            <Input value={deliveryNote.grossTotal.toFixed(2)} readOnly />
          </div>
          <div>
            <Label>Gesamt</Label>
            <Input value={deliveryNote.total.toFixed(2)} readOnly />
          </div>
          <div>
            <Label>EUR</Label>
            <Input value="EUR" readOnly />
          </div>
        </div>
      </Card>

      {/* Buttons */}
      <div className="flex justify-between">
        <div className="flex gap-2">
          <Button onClick={() => setShowPrintDialog(true)} disabled={isSaving} className="gap-2">
            <Printer className="h-4 w-4" />
            LS drucken
          </Button>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => void handleSave()} disabled={isSaving} className="gap-2">
            <Save className="h-4 w-4" />
            Speichern
          </Button>
          <Button variant="outline" onClick={() => navigate('/sales')}>
            Schließen
          </Button>
        </div>
      </div>

      {/* Dialoge */}
      <CustomerSelectionDialog
        open={showCustomerDialog}
        onClose={() => setShowCustomerDialog(false)}
        onSelect={handleCustomerSelect}
      />
      <ArticleSearchDialog
        open={showArticleDialog}
        onClose={() => setShowArticleDialog(false)}
        onSelect={handleArticleSelect}
        customerId={deliveryNote.customerId}
      />
      <LieferscheinDruckDialog
        open={showPrintDialog}
        onClose={() => setShowPrintDialog(false)}
        onConfirm={handlePrint}
      />
    </div>
  )
}


