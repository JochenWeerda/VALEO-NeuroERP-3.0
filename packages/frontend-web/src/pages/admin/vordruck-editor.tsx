import { useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Copy, Eye, FilePlus2, Printer, Save, Sparkles, Trash2 } from 'lucide-react'

/**
 * Belegformular-Vordruck-Editor (Admin)
 *
 * Druckvorlagen für Papier/PDF-Ausdrucke: Wiegeschein, Stundenzettel,
 * Fahrtenbuch, Belege, (Geschenk-)Gutscheine, Rabatt-Coupons, Info-Schreiben,
 * Handouts, Sackanhänger. Layout = Elementliste mit mm-Koordinaten; Vorschau
 * im Canvas (Klick = auswählen, Ziehen = verschieben), PDF über
 * POST /admin/vordrucke/{id}/render.
 */

type ElementTyp = 'text' | 'feld' | 'linie' | 'rechteck' | 'qrcode'

type VordruckElement = {
  typ: ElementTyp
  x: number
  y: number
  breite: number
  hoehe: number
  text?: string | null
  feld_key?: string | null
  font_size: number
  bold: boolean
  align: 'left' | 'center' | 'right'
}

type Vordruck = {
  id: string
  name: string
  kategorie: string
  beschreibung?: string | null
  papierformat: string
  ausrichtung: 'hoch' | 'quer'
  layout: VordruckElement[]
  beispieldaten: Record<string, unknown>
  aktiv: boolean
}

const KATEGORIEN: Array<[string, string]> = [
  ['wiegeschein', 'Wiegeschein'],
  ['stundenzettel', 'Stundenzettel'],
  ['fahrtenbuch', 'Fahrtenbuch'],
  ['beleg', 'Beleg/Quittung'],
  ['gutschein', 'Gutschein'],
  ['rabatt_coupon', 'Rabatt-Coupon'],
  ['info_schreiben', 'Info-Schreiben'],
  ['handout', 'Handout'],
  ['sackanhaenger', 'Sackanhänger'],
  ['sonstig', 'Sonstig'],
]

const FORMATE_MM: Record<string, [number, number]> = {
  A4: [210, 297],
  A5: [148, 210],
  A6: [105, 148],
  label_100x50: [100, 50],
  label_60x30: [60, 30],
}

const NEUES_ELEMENT: Record<ElementTyp, Partial<VordruckElement>> = {
  text: { text: 'Neuer Text', breite: 60, hoehe: 8 },
  feld: { feld_key: 'feld_name', breite: 50, hoehe: 8 },
  linie: { breite: 80, hoehe: 1 },
  rechteck: { breite: 60, hoehe: 30 },
  qrcode: { text: '{{code}}', breite: 25, hoehe: 25 },
}

export default function VordruckEditorPage(): JSX.Element {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [kategorieFilter, setKategorieFilter] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [entwurf, setEntwurf] = useState<Vordruck | null>(null)
  const [selectedElement, setSelectedElement] = useState<number | null>(null)
  const [beispielJson, setBeispielJson] = useState('')
  const dragRef = useRef<{ index: number; startX: number; startY: number; elX: number; elY: number } | null>(null)
  const canvasRef = useRef<HTMLDivElement>(null)

  const { data: vordrucke = [], isError, error, refetch } = useQuery<Vordruck[]>({
    queryKey: ['beleg-vordrucke', kategorieFilter],
    queryFn: async () =>
      (await apiClient.get<Vordruck[]>(
        `/api/v1/admin/vordrucke${kategorieFilter ? `?kategorie=${kategorieFilter}` : ''}`,
      )).data,
  })

  const selectVordruck = (v: Vordruck): void => {
    setSelectedId(v.id)
    setEntwurf(JSON.parse(JSON.stringify(v)) as Vordruck)
    setBeispielJson(JSON.stringify(v.beispieldaten, null, 2))
    setSelectedElement(null)
  }

  const parseBeispieldaten = (): Record<string, unknown> | null => {
    try {
      return JSON.parse(beispielJson || '{}') as Record<string, unknown>
    } catch {
      toast({ title: 'Beispieldaten sind kein gültiges JSON', variant: 'destructive' })
      return null
    }
  }

  const invalidate = (): void => {
    void queryClient.invalidateQueries({ queryKey: ['beleg-vordrucke'] })
  }

  const onSaveError = (err: Error & { response?: { data?: { detail?: unknown } } }): void => {
    const detail = err.response?.data?.detail
    toast({
      title: 'Speichern fehlgeschlagen',
      description: typeof detail === 'string' ? detail : err.message,
      variant: 'destructive',
    })
  }

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!entwurf) throw new Error('Kein Vordruck ausgewählt')
      const beispiel = parseBeispieldaten()
      if (beispiel === null) throw new Error('JSON ungültig')
      const payload = { ...entwurf, beispieldaten: beispiel }
      return (await apiClient.put<Vordruck>(`/api/v1/admin/vordrucke/${entwurf.id}`, payload)).data
    },
    onSuccess: (saved) => {
      toast({ title: 'Vordruck gespeichert' })
      selectVordruck(saved)
      invalidate()
    },
    onError: onSaveError,
  })

  const createMutation = useMutation({
    mutationFn: async () =>
      (await apiClient.post<Vordruck>('/api/v1/admin/vordrucke', {
        name: `Neuer Vordruck ${new Date().toLocaleDateString('de-DE')}`,
        kategorie: kategorieFilter || 'sonstig',
        papierformat: 'A4',
        ausrichtung: 'hoch',
        layout: [],
        beispieldaten: {},
        aktiv: true,
      })).data,
    onSuccess: (created) => {
      toast({ title: 'Vordruck angelegt' })
      invalidate()
      selectVordruck(created)
    },
    onError: onSaveError,
  })

  const duplicateMutation = useMutation({
    mutationFn: async (id: string) =>
      (await apiClient.post<Vordruck>(`/api/v1/admin/vordrucke/${id}/duplizieren`, {})).data,
    onSuccess: (created) => {
      toast({ title: 'Vordruck dupliziert' })
      invalidate()
      selectVordruck(created)
    },
    onError: onSaveError,
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => apiClient.delete(`/api/v1/admin/vordrucke/${id}`),
    onSuccess: () => {
      toast({ title: 'Vordruck gelöscht' })
      setSelectedId(null)
      setEntwurf(null)
      invalidate()
    },
    onError: onSaveError,
  })

  const seedMutation = useMutation({
    mutationFn: async () =>
      (await apiClient.post<Vordruck[]>('/api/v1/admin/vordrucke/seed-standard', {})).data,
    onSuccess: (created) => {
      toast({
        title: 'Standard-Vorlagen',
        description: created.length
          ? `${created.length} Vorlage(n) angelegt (Wiegeschein, Stundenzettel, Gutschein, ...)`
          : 'Alle Standard-Vorlagen sind bereits vorhanden.',
      })
      invalidate()
    },
    onError: onSaveError,
  })

  const previewMutation = useMutation({
    mutationFn: async () => {
      if (!entwurf) throw new Error('Kein Vordruck ausgewählt')
      const beispiel = parseBeispieldaten()
      if (beispiel === null) throw new Error('JSON ungültig')
      const response = await apiClient.post<Blob>(
        `/api/v1/admin/vordrucke/${entwurf.id}/render`,
        { daten: beispiel },
        { responseType: 'blob' },
      )
      return response.data
    },
    onSuccess: (blob) => {
      const url = URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }))
      window.open(url, '_blank', 'noopener')
      // Blob-URL nach dem Öffnen freigeben (Tab hält eigene Referenz)
      setTimeout(() => URL.revokeObjectURL(url), 60_000)
    },
    onError: (err: Error) =>
      toast({ title: 'PDF-Vorschau fehlgeschlagen', description: err.message, variant: 'destructive' }),
  })

  const [seiteBreite, seiteHoehe] = useMemo(() => {
    if (!entwurf) return [210, 297]
    const [w, h] = FORMATE_MM[entwurf.papierformat] ?? [210, 297]
    return entwurf.ausrichtung === 'quer' ? [h, w] : [w, h]
  }, [entwurf])

  // Canvas-Skalierung: Seite auf max. 520px Breite
  const scale = Math.min(520 / seiteBreite, 640 / seiteHoehe)

  const updateElement = (index: number, patch: Partial<VordruckElement>): void => {
    setEntwurf((prev) => {
      if (!prev) return prev
      const layout = prev.layout.map((el, i) => (i === index ? { ...el, ...patch } : el))
      return { ...prev, layout }
    })
  }

  const addElement = (typ: ElementTyp): void => {
    setEntwurf((prev) => {
      if (!prev) return prev
      const el: VordruckElement = {
        typ, x: 10, y: 10, breite: 50, hoehe: 8,
        font_size: 10, bold: false, align: 'left',
        ...NEUES_ELEMENT[typ],
      }
      setSelectedElement(prev.layout.length)
      return { ...prev, layout: [...prev.layout, el] }
    })
  }

  const removeElement = (index: number): void => {
    setEntwurf((prev) => {
      if (!prev) return prev
      return { ...prev, layout: prev.layout.filter((_, i) => i !== index) }
    })
    setSelectedElement(null)
  }

  const onCanvasPointerMove = (e: React.PointerEvent): void => {
    const drag = dragRef.current
    if (!drag || !entwurf) return
    const dx = (e.clientX - drag.startX) / scale
    const dy = (e.clientY - drag.startY) / scale
    updateElement(drag.index, {
      x: Math.max(0, Math.round((drag.elX + dx) * 2) / 2),
      y: Math.max(0, Math.round((drag.elY + dy) * 2) / 2),
    })
  }

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const aktivesElement = entwurf && selectedElement !== null ? entwurf.layout[selectedElement] : null

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Belegformular-Vordruck-Editor</h1>
            <p className="text-muted-foreground">
              Druckvorlagen für Papier- und PDF-Ausdrucke: Wiegeschein, Stundenzettel, Fahrtenbuch,
              Gutscheine, Rabatt-Coupons, Info-Schreiben, Sackanhänger u.&nbsp;a.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => seedMutation.mutate()} disabled={seedMutation.isPending} className="gap-2">
              <Sparkles className="h-4 w-4" />
              {seedMutation.isPending ? 'Lege an...' : 'Standard-Vorlagen anlegen'}
            </Button>
            <Button onClick={() => createMutation.mutate()} disabled={createMutation.isPending} className="gap-2">
              <FilePlus2 className="h-4 w-4" />Neuer Vordruck
            </Button>
          </div>
        </div>

        <div className="grid gap-4 xl:grid-cols-[280px_minmax(0,1fr)_320px]">
          {/* ── Vorlagen-Liste ── */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-base">Vorlagen ({vordrucke.length})</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <select
                value={kategorieFilter}
                onChange={(e) => setKategorieFilter(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
              >
                <option value="">Alle Kategorien</option>
                {KATEGORIEN.map(([wert, label]) => <option key={wert} value={wert}>{label}</option>)}
              </select>
              <div className="max-h-[560px] space-y-1 overflow-y-auto">
                {vordrucke.map((v) => (
                  <button
                    key={v.id}
                    onClick={() => selectVordruck(v)}
                    className={`w-full rounded border p-2 text-left text-sm hover:bg-accent ${selectedId === v.id ? 'border-primary bg-accent' : ''}`}
                  >
                    <div className="font-medium">{v.name}</div>
                    <div className="mt-0.5 flex gap-1">
                      <Badge variant="outline" className="text-[10px]">
                        {KATEGORIEN.find(([wert]) => wert === v.kategorie)?.[1] ?? v.kategorie}
                      </Badge>
                      <Badge variant="secondary" className="text-[10px]">{v.papierformat}</Badge>
                    </div>
                  </button>
                ))}
                {vordrucke.length === 0 && (
                  <p className="p-2 text-sm text-muted-foreground">
                    Keine Vorlagen — über „Standard-Vorlagen anlegen“ starten.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* ── Canvas ── */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-base">
                <span className="flex items-center gap-2"><Printer className="h-4 w-4" />Layout-Vorschau</span>
                {entwurf && (
                  <span className="text-xs font-normal text-muted-foreground">
                    {seiteBreite} × {seiteHoehe} mm — Element anklicken und ziehen
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!entwurf ? (
                <p className="py-16 text-center text-muted-foreground">Vorlage links auswählen oder neu anlegen.</p>
              ) : (
                <div className="flex justify-center overflow-auto">
                  <div
                    ref={canvasRef}
                    data-testid="vordruck-canvas"
                    className="relative border bg-white shadow"
                    style={{ width: seiteBreite * scale, height: seiteHoehe * scale }}
                    onPointerMove={onCanvasPointerMove}
                    onPointerUp={() => { dragRef.current = null }}
                    onPointerLeave={() => { dragRef.current = null }}
                  >
                    {entwurf.layout.map((el, i) => (
                      <div
                        key={i}
                        onPointerDown={(e) => {
                          setSelectedElement(i)
                          dragRef.current = { index: i, startX: e.clientX, startY: e.clientY, elX: el.x, elY: el.y }
                        }}
                        className={`absolute cursor-move select-none overflow-hidden border ${selectedElement === i ? 'border-blue-500 ring-1 ring-blue-400' : 'border-transparent hover:border-gray-300'}`}
                        style={{
                          left: el.x * scale,
                          top: el.y * scale,
                          width: el.breite * scale,
                          height: Math.max(el.hoehe * scale, 6),
                          fontSize: Math.max(el.font_size * scale * 0.35, 6),
                          fontWeight: el.bold ? 700 : 400,
                          textAlign: el.align,
                          background: el.typ === 'qrcode' ? 'repeating-linear-gradient(45deg,#ddd,#ddd 2px,#fff 2px,#fff 4px)' : undefined,
                          borderColor: el.typ === 'rechteck' ? '#666' : undefined,
                          borderStyle: el.typ === 'rechteck' ? 'solid' : undefined,
                        }}
                      >
                        {el.typ === 'linie' && <div className="mt-[2px] border-t border-black" />}
                        {(el.typ === 'text' || el.typ === 'feld') && (
                          <span className="whitespace-pre-wrap leading-tight">
                            {el.typ === 'feld' ? `{{${el.feld_key ?? ''}}}` : el.text}
                          </span>
                        )}
                        {el.typ === 'qrcode' && <span className="text-[8px]">QR</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* ── Eigenschaften ── */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-base">Eigenschaften</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {!entwurf ? (
                <p className="text-sm text-muted-foreground">Keine Vorlage ausgewählt.</p>
              ) : (
                <>
                  <div>
                    <Label className="text-xs">Name</Label>
                    <Input value={entwurf.name} onChange={(e) => setEntwurf({ ...entwurf, name: e.target.value })} />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label className="text-xs">Kategorie</Label>
                      <select
                        value={entwurf.kategorie}
                        onChange={(e) => setEntwurf({ ...entwurf, kategorie: e.target.value })}
                        className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
                      >
                        {KATEGORIEN.map(([wert, label]) => <option key={wert} value={wert}>{label}</option>)}
                      </select>
                    </div>
                    <div>
                      <Label className="text-xs">Format</Label>
                      <select
                        value={entwurf.papierformat}
                        onChange={(e) => setEntwurf({ ...entwurf, papierformat: e.target.value })}
                        className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
                      >
                        {Object.keys(FORMATE_MM).map((f) => <option key={f} value={f}>{f}</option>)}
                      </select>
                    </div>
                  </div>
                  <div>
                    <Label className="text-xs">Ausrichtung</Label>
                    <select
                      value={entwurf.ausrichtung}
                      onChange={(e) => setEntwurf({ ...entwurf, ausrichtung: e.target.value as 'hoch' | 'quer' })}
                      className="w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm"
                    >
                      <option value="hoch">Hochformat</option>
                      <option value="quer">Querformat</option>
                    </select>
                  </div>

                  <div className="border-t pt-2">
                    <Label className="text-xs">Element hinzufügen</Label>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {(['text', 'feld', 'linie', 'rechteck', 'qrcode'] as ElementTyp[]).map((typ) => (
                        <Button key={typ} size="sm" variant="outline" onClick={() => addElement(typ)}>{typ}</Button>
                      ))}
                    </div>
                  </div>

                  {aktivesElement && selectedElement !== null && (
                    <div className="space-y-2 rounded border bg-muted/40 p-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold">Element: {aktivesElement.typ}</span>
                        <Button size="sm" variant="ghost" onClick={() => removeElement(selectedElement)}>
                          <Trash2 className="h-3.5 w-3.5 text-destructive" />
                        </Button>
                      </div>
                      <div className="grid grid-cols-4 gap-1">
                        {(['x', 'y', 'breite', 'hoehe'] as const).map((feld) => (
                          <div key={feld}>
                            <Label className="text-[10px]">{feld} (mm)</Label>
                            <Input
                              type="number" step="0.5" className="h-7 text-xs"
                              value={aktivesElement[feld]}
                              onChange={(e) => updateElement(selectedElement, { [feld]: Number(e.target.value) })}
                            />
                          </div>
                        ))}
                      </div>
                      {(aktivesElement.typ === 'text' || aktivesElement.typ === 'qrcode') && (
                        <div>
                          <Label className="text-[10px]">Text ({'{{key}}'} für Daten)</Label>
                          <Input className="h-7 text-xs" value={aktivesElement.text ?? ''}
                            onChange={(e) => updateElement(selectedElement, { text: e.target.value })} />
                        </div>
                      )}
                      {aktivesElement.typ === 'feld' && (
                        <div>
                          <Label className="text-[10px]">Datenfeld-Key</Label>
                          <Input className="h-7 text-xs" value={aktivesElement.feld_key ?? ''}
                            onChange={(e) => updateElement(selectedElement, { feld_key: e.target.value })} />
                        </div>
                      )}
                      {(aktivesElement.typ === 'text' || aktivesElement.typ === 'feld') && (
                        <div className="grid grid-cols-3 items-end gap-1">
                          <div>
                            <Label className="text-[10px]">Schrift (pt)</Label>
                            <Input type="number" className="h-7 text-xs" value={aktivesElement.font_size}
                              onChange={(e) => updateElement(selectedElement, { font_size: Number(e.target.value) })} />
                          </div>
                          <label className="flex items-center gap-1 text-xs">
                            <input type="checkbox" checked={aktivesElement.bold}
                              onChange={(e) => updateElement(selectedElement, { bold: e.target.checked })} />
                            fett
                          </label>
                          <select
                            value={aktivesElement.align}
                            onChange={(e) => updateElement(selectedElement, { align: e.target.value as VordruckElement['align'] })}
                            className="h-7 rounded-md border border-input bg-background px-1 text-xs"
                          >
                            <option value="left">links</option>
                            <option value="center">zentriert</option>
                            <option value="right">rechts</option>
                          </select>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="border-t pt-2">
                    <Label className="text-xs">Beispieldaten (JSON — für Vorschau)</Label>
                    <textarea
                      value={beispielJson}
                      onChange={(e) => setBeispielJson(e.target.value)}
                      rows={6}
                      className="mt-1 w-full rounded-md border border-input bg-background p-2 font-mono text-xs"
                    />
                  </div>

                  <div className="flex flex-wrap gap-2 border-t pt-3">
                    <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending} className="gap-2">
                      <Save className="h-4 w-4" />{saveMutation.isPending ? 'Speichert...' : 'Speichern'}
                    </Button>
                    <Button variant="outline" onClick={() => previewMutation.mutate()} disabled={previewMutation.isPending} className="gap-2">
                      <Eye className="h-4 w-4" />{previewMutation.isPending ? 'Rendert...' : 'PDF-Vorschau'}
                    </Button>
                    <Button variant="outline" onClick={() => duplicateMutation.mutate(entwurf.id)} disabled={duplicateMutation.isPending} className="gap-2">
                      <Copy className="h-4 w-4" />Duplizieren
                    </Button>
                    <Button
                      variant="outline"
                      className="gap-2 text-destructive"
                      onClick={() => { if (window.confirm(`Vordruck "${entwurf.name}" löschen?`)) deleteMutation.mutate(entwurf.id) }}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="h-4 w-4" />Löschen
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
