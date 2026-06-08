/**
 * POS Retoure — Warenrückgabe am Terminal
 * ─────────────────────────────────────────
 * Ermöglicht die Rücknahme von Artikeln mit negativem Bon und
 * Wahl der Rückerstattungsart (Bar, EC, Geschenkkarte).
 */
import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import {
  RotateCcw, Plus, Minus, Trash2, DollarSign, CreditCard, Gift,
  ArrowLeft, CheckCircle2, Search, X,
} from 'lucide-react'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

type RetourPosition = {
  artikelnr: string
  bezeichnung: string
  ean: string
  einzelpreis: number
  menge: number
  grund: string
}

type ZahlungsRueckerstattung = 'bar' | 'ec' | 'gift_card'

const RUECKERSTATTUNG_LABELS: Record<ZahlungsRueckerstattung, string> = {
  bar: 'Bargeld auszahlen',
  ec: 'EC-Rückbuchung',
  gift_card: 'Gutschein ausstellen',
}

export default function RetourePage(): JSX.Element {
  const navigate = useNavigate()

  const [positionen, setPositionen] = useState<RetourPosition[]>([])
  const [originalBonNr, setOriginalBonNr] = useState('')
  const [kassierer, setKassierer] = useState(() => {
    try { return localStorage.getItem('pos-kassierer') || '' } catch { return '' }
  })
  const [rueckerstattung, setRueckerstattung] = useState<ZahlungsRueckerstattung>('bar')
  const [showArtikelDialog, setShowArtikelDialog] = useState(false)
  const [artikelSearch, setArtikelSearch] = useState('')
  const [artikelResults, setArtikelResults] = useState<Array<{ id: string; article_number: string; name: string; sales_price: string | number; barcode?: string | null }>>([])
  const [showSuccess, setShowSuccess] = useState(false)
  const [successData, setSuccessData] = useState<{ bonNr: string; gesamt: number } | null>(null)

  const gesamt = positionen.reduce((s, p) => s + p.einzelpreis * p.menge, 0)

  // ── Artikel-Suche ──────────────────────────────────────────────────────────
  async function searchArtikel(q: string): Promise<void> {
    if (q.length < 2) { setArtikelResults([]); return }
    try {
      const res = await apiClient.get<{ items: typeof artikelResults }>('/api/v1/articles', {
        params: { search: q, limit: 10, is_active: true },
      })
      setArtikelResults(res.data.items)
    } catch { setArtikelResults([]) }
  }

  function addArtikel(a: (typeof artikelResults)[0]): void {
    const existing = positionen.find((p) => p.artikelnr === a.article_number)
    if (existing) {
      setPositionen(positionen.map((p) =>
        p.artikelnr === a.article_number ? { ...p, menge: p.menge + 1 } : p
      ))
    } else {
      setPositionen([...positionen, {
        artikelnr: a.article_number,
        bezeichnung: a.name,
        ean: a.barcode ?? '',
        einzelpreis: Number(a.sales_price) || 0,
        menge: 1,
        grund: 'Rückgabe',
      }])
    }
    setShowArtikelDialog(false)
    setArtikelSearch('')
    setArtikelResults([])
  }

  function updateMenge(artikelnr: string, menge: number): void {
    if (menge <= 0) setPositionen(positionen.filter((p) => p.artikelnr !== artikelnr))
    else setPositionen(positionen.map((p) => p.artikelnr === artikelnr ? { ...p, menge } : p))
  }

  function updateGrund(artikelnr: string, grund: string): void {
    setPositionen(positionen.map((p) => p.artikelnr === artikelnr ? { ...p, grund } : p))
  }

  // ── Retoure buchen ──────────────────────────────────────────────────────────
  const retoureMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post<{ retoure_bon_nr: string; gesamt: number }>('/api/v1/pos/retoure', {
        original_bon_nr: originalBonNr || undefined,
        kassierer,
        positionen: positionen.map((p) => ({
          artikelnr: p.artikelnr,
          bezeichnung: p.bezeichnung,
          ean: p.ean || undefined,
          einzelpreis: p.einzelpreis,
          menge: p.menge,
          grund: p.grund,
        })),
        zahlungsrueckerstattung: rueckerstattung,
        gesamt,
      })
      return res.data
    },
    onSuccess: (data) => {
      setSuccessData({ bonNr: data.retoure_bon_nr, gesamt: data.gesamt })
      setShowSuccess(true)
      toast({ title: 'Retoure gebucht', description: `Bon: ${data.retoure_bon_nr}` })
    },
    onError: () => {
      toast({ variant: 'destructive', title: 'Fehler', description: 'Retoure konnte nicht gebucht werden.' })
    },
  })

  const fmt = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

  // ── Erfolgs-Ansicht ─────────────────────────────────────────────────────────
  if (showSuccess && successData) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="pt-8 text-center">
            <CheckCircle2 className="h-20 w-20 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Retoure erfolgreich</h2>
            <p className="text-muted-foreground mb-1">Bon-Nr: <strong>{successData.bonNr}</strong></p>
            <p className="text-3xl font-bold text-red-600 my-4">−{fmt(successData.gesamt)}</p>
            <p className="text-sm text-muted-foreground mb-6">
              Rückerstattung via: <strong>{RUECKERSTATTUNG_LABELS[rueckerstattung]}</strong>
            </p>
            <div className="flex gap-3">
              <Button variant="outline" className="flex-1" onClick={() => {
                setPositionen([]); setOriginalBonNr(''); setShowSuccess(false); setSuccessData(null)
              }}>
                Weitere Retoure
              </Button>
              <Button className="flex-1" onClick={() => navigate('/pos/terminal')}>
                Zurück zum POS
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ── Haupt-Ansicht ────────────────────────────────────────────────────────────
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-red-600 text-white px-5 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <RotateCcw className="h-6 w-6" />
          <div>
            <h1 className="text-lg font-bold leading-none">Warenrückgabe / Retoure</h1>
            <p className="text-xs opacity-75 mt-0.5">Negativer Bon · Lagerrückbuchung</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={() => navigate('/pos/terminal')} className="text-white hover:text-white hover:bg-white/20 gap-1.5">
          <ArrowLeft className="h-4 w-4" />Zurück zum POS
        </Button>
      </div>

      <div className="flex-1 flex gap-4 p-4 overflow-hidden">
        {/* Linke Spalte: Positionen */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Card className="flex-1 flex flex-col overflow-hidden">
            <CardHeader className="py-3 px-4 border-b flex-shrink-0">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Rückgabe-Positionen</CardTitle>
                <Button size="sm" onClick={() => setShowArtikelDialog(true)} className="gap-1.5">
                  <Plus className="h-4 w-4" />Artikel hinzufügen
                </Button>
              </div>
            </CardHeader>
            <div className="flex-1 overflow-auto p-4 space-y-3">
              {positionen.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
                  <RotateCcw className="h-12 w-12 opacity-20 mb-3" />
                  <p className="text-sm">Keine Positionen</p>
                  <p className="text-xs opacity-60 mt-1">Artikel über "Hinzufügen" auswählen</p>
                </div>
              ) : (
                positionen.map((pos) => (
                  <div key={pos.artikelnr} className="border rounded-lg p-3 bg-white space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-sm truncate">{pos.bezeichnung}</div>
                        <div className="text-xs text-muted-foreground">{pos.artikelnr} · {fmt(pos.einzelpreis)}/Stk</div>
                      </div>
                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        <Button size="sm" variant="outline" className="h-8 w-8 p-0" onClick={() => updateMenge(pos.artikelnr, pos.menge - 1)}><Minus className="h-3 w-3" /></Button>
                        <span className="w-8 text-center font-bold text-sm">{pos.menge}</span>
                        <Button size="sm" variant="outline" className="h-8 w-8 p-0" onClick={() => updateMenge(pos.artikelnr, pos.menge + 1)}><Plus className="h-3 w-3" /></Button>
                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0 text-destructive" onClick={() => updateMenge(pos.artikelnr, 0)}><Trash2 className="h-3.5 w-3.5" /></Button>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <Input
                        placeholder="Rückgabegrund..."
                        value={pos.grund}
                        onChange={(e) => updateGrund(pos.artikelnr, e.target.value)}
                        className="h-7 text-xs flex-1 mr-2"
                      />
                      <span className="text-sm font-bold text-red-600 whitespace-nowrap">−{fmt(pos.einzelpreis * pos.menge)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Rechte Spalte: Metadaten + Abschluss */}
        <div className="w-80 flex-shrink-0 flex flex-col gap-3">
          {/* Bon-Referenz */}
          <Card>
            <CardContent className="pt-4 space-y-3">
              <div>
                <Label className="text-xs">Ursprungs-Bon-Nr (optional)</Label>
                <Input
                  placeholder="BON-20260322-..."
                  value={originalBonNr}
                  onChange={(e) => setOriginalBonNr(e.target.value)}
                  className="mt-1 font-mono text-sm"
                />
              </div>
              <div>
                <Label className="text-xs">Kassierer</Label>
                <Input
                  placeholder="Name..."
                  value={kassierer}
                  onChange={(e) => setKassierer(e.target.value)}
                  className="mt-1 text-sm"
                />
              </div>
            </CardContent>
          </Card>

          {/* Rückerstattungsart */}
          <Card>
            <CardContent className="pt-4">
              <Label className="text-xs font-semibold">Rückerstattung</Label>
              <div className="mt-2 space-y-2">
                {(['bar', 'ec', 'gift_card'] as const).map((art) => (
                  <button
                    key={art}
                    onClick={() => setRueckerstattung(art)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-colors text-left ${rueckerstattung === art ? 'border-primary bg-primary/5 font-semibold' : 'hover:bg-accent'}`}
                  >
                    {art === 'bar' && <DollarSign className="h-4 w-4" />}
                    {art === 'ec' && <CreditCard className="h-4 w-4" />}
                    {art === 'gift_card' && <Gift className="h-4 w-4" />}
                    <span className="text-sm">{RUECKERSTATTUNG_LABELS[art]}</span>
                    {rueckerstattung === art && <Badge className="ml-auto text-xs">Gewählt</Badge>}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Gesamtbetrag + Buchen */}
          <Card>
            <CardContent className="pt-4">
              <div className="flex justify-between items-center mb-4">
                <span className="text-sm text-muted-foreground">{positionen.length} Position(en)</span>
                <div className="text-right">
                  <div className="text-xs text-muted-foreground">Rückerstattungsbetrag</div>
                  <div className="text-3xl font-bold text-red-600">−{fmt(gesamt)}</div>
                </div>
              </div>
              <Button
                className="w-full h-14 text-base font-bold bg-red-600 hover:bg-red-700"
                disabled={positionen.length === 0 || retoureMutation.isPending}
                onClick={() => retoureMutation.mutate()}
              >
                {retoureMutation.isPending ? 'Wird gebucht…' : (
                  <><RotateCcw className="h-5 w-5 mr-2" />Retoure buchen</>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Artikel-Suche Dialog */}
      <Dialog open={showArtikelDialog} onOpenChange={setShowArtikelDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Artikel für Rückgabe suchen</DialogTitle></DialogHeader>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              className="pl-10 h-12"
              placeholder="Name, EAN oder Artikelnummer..."
              value={artikelSearch}
              onChange={(e) => { setArtikelSearch(e.target.value); void searchArtikel(e.target.value) }}
              autoFocus
            />
          </div>
          <div className="space-y-1.5 max-h-64 overflow-auto">
            {artikelResults.map((a) => (
              <button
                key={a.id}
                onClick={() => addArtikel(a)}
                className="w-full flex items-center justify-between p-3 rounded-lg border hover:bg-accent text-left transition-colors"
              >
                <div>
                  <div className="font-semibold text-sm">{a.name}</div>
                  <div className="text-xs text-muted-foreground">{a.article_number}</div>
                </div>
                <div className="text-sm font-bold text-primary ml-3 whitespace-nowrap">
                  {fmt(Number(a.sales_price))}
                </div>
              </button>
            ))}
            {artikelSearch.length >= 2 && artikelResults.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">Keine Artikel gefunden</p>
            )}
          </div>
          <Button variant="outline" onClick={() => setShowArtikelDialog(false)}>
            <X className="h-4 w-4 mr-1.5" />Abbrechen
          </Button>
        </DialogContent>
      </Dialog>
    </div>
  )
}
