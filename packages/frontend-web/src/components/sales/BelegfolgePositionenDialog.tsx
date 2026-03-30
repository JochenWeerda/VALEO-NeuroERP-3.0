/**
 * BelegfolgePositionenDialog
 *
 * Zeigt offene Vorgänger-Belege in der Belegfolge (Angebote → Aufträge → Portal-Bestellungen → Lieferscheine)
 * und ermöglicht die Übernahme von Positionen in den aktuellen Beleg.
 *
 * Verwendung:
 *   - Auftrags-Erfassung: zeigt offene Angebote
 *   - Lieferschein-Erfassung: zeigt offene Angebote + Aufträge + Portal-Bestellungen
 *   - Rechnungs-Erfassung: zeigt offene Aufträge + Lieferscheine
 */

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'
import { FileText, Globe, ShoppingCart, Truck, ChevronDown, ChevronRight } from 'lucide-react'

// ── Types ──────────────────────────────────────────────────────────────────────

export type BelegfolgePosition = {
  artikelNr: string
  artikelId: string | null
  bezeichnung: string
  bezeichnung2: string
  menge: number
  einheit: string
  listenpreis: number
  rabatt: number
  mwstProzent: number
  ekPreis: number
}

type BelegTyp = 'angebot' | 'auftrag' | 'portalbestellung' | 'lieferschein'

type BelegDokument = {
  id: string
  typ: BelegTyp
  nummer: string
  datum: string
  status: string
  positionen: BelegfolgePosition[]
  positionenGeladen: boolean
}

type TargetDocType = 'auftrag' | 'lieferschein' | 'rechnung'

// ── Props ──────────────────────────────────────────────────────────────────────

type Props = {
  open: boolean
  onClose: () => void
  onConfirm: (positionen: BelegfolgePosition[]) => void
  customerId: string
  targetDocType: TargetDocType
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function typLabel(typ: BelegTyp): string {
  if (typ === 'angebot') return 'Angebot'
  if (typ === 'auftrag') return 'Auftrag'
  if (typ === 'portalbestellung') return 'Portal-Bestellung'
  return 'Lieferschein'
}

function typIcon(typ: BelegTyp) {
  if (typ === 'angebot') return <FileText className="h-4 w-4 text-blue-500" />
  if (typ === 'auftrag') return <ShoppingCart className="h-4 w-4 text-green-600" />
  if (typ === 'portalbestellung') return <Globe className="h-4 w-4 text-purple-500" />
  return <Truck className="h-4 w-4 text-orange-500" />
}

function sourcesFor(target: TargetDocType): BelegTyp[] {
  if (target === 'auftrag') return ['angebot']
  if (target === 'lieferschein') return ['angebot', 'auftrag', 'portalbestellung']
  return ['auftrag', 'lieferschein']
}

// ── Component ──────────────────────────────────────────────────────────────────

export function BelegfolgePositionenDialog({ open, onClose, onConfirm, customerId, targetDocType }: Props) {
  const [belege, setBelege] = useState<BelegDokument[]>([])
  const [loading, setLoading] = useState(false)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  // selectedKeys: `${belegId}::${posIdx}`
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set())

  // Belege laden wenn Dialog öffnet
  useEffect(() => {
    if (!open || !customerId) return
    void loadBelege()
  }, [open, customerId])

  async function loadBelege() {
    setLoading(true)
    setBelege([])
    setSelectedKeys(new Set())
    setExpandedIds(new Set())

    const sources = sourcesFor(targetDocType)
    const loaded: BelegDokument[] = []

    await Promise.all(
      sources.map(async (typ) => {
        try {
          let response: any[] = []
          if (typ === 'angebot') {
            const r = await apiClient.get<any>('/api/v1/sales/quotes', {
              params: { customer_id: customerId, limit: 20 },
            })
            response = r.items || r || []
          } else if (typ === 'auftrag') {
            const r = await apiClient.get<any>('/api/v1/sales/orders', {
              params: { customer_id: customerId, limit: 20 },
            })
            response = r.items || r || []
          } else if (typ === 'portalbestellung') {
            const r = await apiClient.get<any>('/api/v1/portal/bestellungen', {
              params: { customer_id: customerId, status: 'bestellt', limit: 20 },
            })
            response = Array.isArray(r) ? r : (r.items || r.data || [])
          } else {
            const r = await apiClient.get<any>('/api/v1/sales/delivery-notes', {
              params: { customer_id: customerId, limit: 20 },
            })
            response = r.items || r || []
          }

          const docs: BelegDokument[] = response.map((d: any) => ({
            id: d.id,
            typ,
            nummer: d.order_number || d.quote_number || d.delivery_note_number || d.id,
            datum: d.created_at
              ? new Date(d.created_at).toLocaleDateString('de-DE')
              : '—',
            status: d.status || '—',
            positionen: [],
            positionenGeladen: false,
          }))
          loaded.push(...docs)
        } catch {
          // ignore — source not available
        }
      }),
    )

    // Sortierung: Angebote → Aufträge → Portal-Bestellungen → Lieferscheine
    loaded.sort((a, b) => {
      const order: BelegTyp[] = ['angebot', 'auftrag', 'portalbestellung', 'lieferschein']
      return order.indexOf(a.typ) - order.indexOf(b.typ)
    })

    setBelege(loaded)
    setLoading(false)
  }

  async function loadPositionen(beleg: BelegDokument): Promise<void> {
    if (beleg.positionenGeladen) return
    try {
      let positionen: BelegfolgePosition[] = []

      if (beleg.typ === 'auftrag') {
        const r = await apiClient.get<any>(`/api/v1/sales/orders/${beleg.id}`)
        const items = r.items || []
        positionen = items.map((item: any) => ({
          artikelNr: item.article_number || '',
          artikelId: item.artikel_id || null,
          bezeichnung: item.description || '',
          bezeichnung2: item.description2 || '',
          menge: item.quantity || 0,
          einheit: item.unit || 'Stk',
          listenpreis: item.unit_price || 0,
          rabatt: item.discount_percent || 0,
          mwstProzent: item.mwst_prozent || 19,
          ekPreis: item.purchase_price || 0,
        }))
      } else if (beleg.typ === 'portalbestellung') {
        const r = await apiClient.get<any>(`/api/v1/portal/bestellungen/${beleg.id}`)
        // Portal-Bestellungen können Positionen-Array oder Einzelartikel-Struktur haben
        const items = r.positionen || r.items || (r.artikel ? [r] : [])
        positionen = items.map((item: any) => ({
          artikelNr: item.artikelnummer || item.artikel_nr || item.artikel || '',
          artikelId: item.artikel_id || null,
          bezeichnung: item.name || item.bezeichnung || item.artikel || '',
          bezeichnung2: item.bezeichnung2 || '',
          menge: item.menge || 1,
          einheit: item.einheit || 'Stk',
          listenpreis: item.einzelpreis || item.preis || (item.betrag != null && item.menge > 0 ? item.betrag / item.menge : 0),
          rabatt: item.rabatt || 0,
          mwstProzent: item.mwst_prozent || 19,
          ekPreis: 0,
        }))
      } else if (beleg.typ === 'angebot') {
        const r = await apiClient.get<any>(`/api/v1/sales/quotes/${beleg.id}`)
        const items = r.items || r.positionen || []
        positionen = items.map((item: any) => ({
          artikelNr: item.article_number || item.artikel_nr || '',
          artikelId: item.artikel_id || null,
          bezeichnung: item.description || item.bezeichnung || '',
          bezeichnung2: item.description2 || item.bezeichnung2 || '',
          menge: item.quantity || item.menge || 0,
          einheit: item.unit || item.einheit || 'Stk',
          listenpreis: item.unit_price || item.listenpreis || 0,
          rabatt: item.discount_percent || item.rabatt || 0,
          mwstProzent: item.mwst_prozent || 19,
          ekPreis: item.purchase_price || 0,
        }))
      } else {
        const r = await apiClient.get<any>(`/api/v1/sales/delivery-notes/${beleg.id}`)
        const items = r.positionen || []
        positionen = items.map((item: any) => ({
          artikelNr: item.artikel_nr || '',
          artikelId: item.artikel_id || null,
          bezeichnung: item.bezeichnung || '',
          bezeichnung2: item.bezeichnung2 || '',
          menge: item.menge || 0,
          einheit: item.einheit || 'Stk',
          listenpreis: item.listenpreis || 0,
          rabatt: item.rabatt || 0,
          mwstProzent: item.mwst_prozent || 19,
          ekPreis: 0,
        }))
      }

      setBelege((prev) =>
        prev.map((b) =>
          b.id === beleg.id ? { ...b, positionen, positionenGeladen: true } : b,
        ),
      )
    } catch {
      setBelege((prev) =>
        prev.map((b) => (b.id === beleg.id ? { ...b, positionenGeladen: true } : b)),
      )
    }
  }

  function toggleExpand(beleg: BelegDokument) {
    const next = new Set(expandedIds)
    if (next.has(beleg.id)) {
      next.delete(beleg.id)
    } else {
      next.add(beleg.id)
      void loadPositionen(beleg)
    }
    setExpandedIds(next)
  }

  function posKey(belegId: string, posIdx: number) {
    return `${belegId}::${posIdx}`
  }

  function togglePosition(belegId: string, posIdx: number) {
    const key = posKey(belegId, posIdx)
    const next = new Set(selectedKeys)
    if (next.has(key)) next.delete(key)
    else next.add(key)
    setSelectedKeys(next)
  }

  function toggleAllPositions(beleg: BelegDokument) {
    const allKeys = beleg.positionen.map((_, i) => posKey(beleg.id, i))
    const allSelected = allKeys.every((k) => selectedKeys.has(k))
    const next = new Set(selectedKeys)
    if (allSelected) {
      allKeys.forEach((k) => next.delete(k))
    } else {
      allKeys.forEach((k) => next.add(k))
    }
    setSelectedKeys(next)
  }

  function selectAllBelege() {
    const next = new Set(selectedKeys)
    belege.forEach((b) => {
      b.positionen.forEach((_, i) => next.add(posKey(b.id, i)))
    })
    setSelectedKeys(next)
  }

  function handleConfirm() {
    const result: BelegfolgePosition[] = []
    belege.forEach((beleg) => {
      beleg.positionen.forEach((pos, idx) => {
        if (selectedKeys.has(posKey(beleg.id, idx))) {
          result.push(pos)
        }
      })
    })
    onConfirm(result)
    onClose()
  }

  const totalSelected = selectedKeys.size
  const totalPositionen = belege.reduce((s, b) => s + b.positionen.length, 0)

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-base">
            Positionen aus Vorgänger-Beleg übernehmen
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {loading && (
            <div className="text-center text-sm text-muted-foreground py-8">
              Lade Vorgänger-Belege…
            </div>
          )}

          {!loading && belege.length === 0 && (
            <div className="text-center text-sm text-muted-foreground py-8">
              Keine offenen Vorgänger-Belege für diesen Kunden gefunden.
            </div>
          )}

          {!loading && belege.map((beleg) => {
            const isExpanded = expandedIds.has(beleg.id)
            const loadedPositionen = beleg.positionen
            const allSelected =
              loadedPositionen.length > 0 &&
              loadedPositionen.every((_, i) => selectedKeys.has(posKey(beleg.id, i)))
            const someSelected =
              !allSelected &&
              loadedPositionen.some((_, i) => selectedKeys.has(posKey(beleg.id, i)))

            return (
              <div key={beleg.id} className="border rounded-md overflow-hidden">
                {/* Beleg-Header */}
                <div
                  className="flex items-center gap-3 px-3 py-2 bg-muted/40 cursor-pointer hover:bg-muted/60 select-none"
                  onClick={() => toggleExpand(beleg)}
                >
                  {isExpanded
                    ? <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
                    : <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />}
                  {typIcon(beleg.typ)}
                  <span className="font-medium text-sm">{typLabel(beleg.typ)}</span>
                  <span className="font-mono text-sm">{beleg.nummer}</span>
                  <span className="text-xs text-muted-foreground">{beleg.datum}</span>
                  <Badge variant="outline" className="text-xs ml-auto">{beleg.status}</Badge>
                  {loadedPositionen.length > 0 && (
                    <span className="text-xs text-muted-foreground">
                      {loadedPositionen.length} Pos.
                    </span>
                  )}
                </div>

                {/* Positionen-Liste */}
                {isExpanded && (
                  <div className="px-3 py-2 space-y-1 border-t">
                    {!beleg.positionenGeladen && (
                      <div className="text-xs text-muted-foreground py-2">Lade Positionen…</div>
                    )}
                    {beleg.positionenGeladen && loadedPositionen.length === 0 && (
                      <div className="text-xs text-muted-foreground py-2">Keine Positionen vorhanden</div>
                    )}
                    {beleg.positionenGeladen && loadedPositionen.length > 0 && (
                      <>
                        {/* Alle auswählen */}
                        <div className="flex items-center gap-2 pb-1 border-b mb-1">
                          <Checkbox
                            checked={allSelected}
                            data-state={someSelected ? 'indeterminate' : undefined}
                            onCheckedChange={() => toggleAllPositions(beleg)}
                          />
                          <Label className="text-xs font-semibold cursor-pointer"
                            onClick={() => toggleAllPositions(beleg)}>
                            Alle Positionen auswählen
                          </Label>
                        </div>
                        {/* Positions-Zeilen */}
                        {loadedPositionen.map((pos, idx) => (
                          <div
                            key={idx}
                            className={`flex items-center gap-2 py-1 px-1 rounded text-xs cursor-pointer hover:bg-muted/40 ${selectedKeys.has(posKey(beleg.id, idx)) ? 'bg-primary/5' : ''}`}
                            onClick={() => togglePosition(beleg.id, idx)}
                          >
                            <Checkbox
                              checked={selectedKeys.has(posKey(beleg.id, idx))}
                              onCheckedChange={() => togglePosition(beleg.id, idx)}
                              onClick={(e) => e.stopPropagation()}
                            />
                            <span className="w-10 text-muted-foreground font-mono shrink-0">
                              {String(idx + 1).padStart(2, '0')}
                            </span>
                            <span className="w-24 font-mono shrink-0 truncate" title={pos.artikelNr}>
                              {pos.artikelNr}
                            </span>
                            <span className="flex-1 truncate" title={pos.bezeichnung}>
                              {pos.bezeichnung}
                              {pos.bezeichnung2 ? ` · ${pos.bezeichnung2}` : ''}
                            </span>
                            <span className="w-16 text-right shrink-0">
                              {pos.menge.toLocaleString('de-DE')} {pos.einheit}
                            </span>
                            <span className="w-20 text-right shrink-0">
                              {pos.listenpreis.toFixed(2)} €
                            </span>
                            {pos.rabatt > 0 && (
                              <span className="w-12 text-right text-muted-foreground shrink-0">
                                {pos.rabatt}%
                              </span>
                            )}
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        <DialogFooter className="border-t pt-3 mt-0 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            {totalPositionen > 0 && (
              <Button variant="ghost" size="sm" onClick={selectAllBelege}>
                Alle laden &amp; auswählen
              </Button>
            )}
            {totalSelected > 0 && (
              <span className="text-sm text-muted-foreground">
                {totalSelected} Position{totalSelected !== 1 ? 'en' : ''} ausgewählt
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose}>Abbrechen</Button>
            <Button
              onClick={handleConfirm}
              disabled={totalSelected === 0}
            >
              {totalSelected > 0 ? `${totalSelected} Position${totalSelected !== 1 ? 'en' : ''} übernehmen` : 'Positionen übernehmen'}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
