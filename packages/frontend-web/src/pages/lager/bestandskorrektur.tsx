/**
 * Bestandskorrektur — Eingabemaske fuer Lagerkorrekturen
 * Wave 4: Schwund, Bruch, MHD-Verfall, Messdifferenz, etc.
 */
import { useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/react-router-compat'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/card'
import { Wizard } from '@/components/patterns/Wizard'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AlertTriangle, CheckCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import {
  TouchSection,
  TouchTextInput,
  TouchNumericInput,
  TouchCard,
  TouchCardGroup,
  TouchConfirmCard,
} from '@/components/touch/TouchFieldLayout'

type KorrekturData = {
  articleId: string
  artikelName: string
  warehouseId: string
  lagerortName: string
  menge: number
  grund: string
  bemerkung: string
  charge: string
}

const GRUND_OPTIONS = [
  { code: 'schwund', label: 'Lagerschwund', icon: '📉' },
  { code: 'bruch', label: 'Bruch / Beschaedigung', icon: '💔' },
  { code: 'mhd_verfall', label: 'MHD-Verfall', icon: '📅' },
  { code: 'diebstahl', label: 'Diebstahl / Verlust', icon: '🔒' },
  { code: 'messdifferenz', label: 'Messdifferenz', icon: '📏' },
  { code: 'qualitaetsmangel', label: 'Qualitaetsmangel', icon: '⚠️' },
  { code: 'sonstige', label: 'Sonstige', icon: '📝' },
]

const FALLBACK_ARTIKEL = [
  { id: 'weizen', name: 'Weizen' },
  { id: 'gerste', name: 'Gerste' },
  { id: 'raps', name: 'Raps' },
]

const FALLBACK_LAGERORTE = [
  { id: 'silo-1', name: 'Silo 1' },
  { id: 'silo-2', name: 'Silo 2' },
  { id: 'halle-a', name: 'Halle A' },
]

export default function BestandskorrekturPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchParams] = useSearchParams()
  const preArticle = searchParams.get('article_id')
  const preWarehouse = searchParams.get('warehouse_id')

  const [data, setData] = useState<KorrekturData>({
    articleId: preArticle || '',
    artikelName: '',
    warehouseId: preWarehouse || '',
    lagerortName: '',
    menge: 0,
    grund: '',
    bemerkung: '',
    charge: '',
  })

  const artikelQuery = useQuery({
    queryKey: ['articles', 'korrektur'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: Array<{ id: string; name: string; article_number: string }> }>('/api/v1/articles?limit=100')
      return res.data?.items ?? []
    },
  })

  const warehouseQuery = useQuery({
    queryKey: ['warehouses', 'korrektur'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: Array<{ id: string; warehouse_code: string; name: string }> }>('/api/v1/warehouses?limit=100')
      return res.data?.items ?? []
    },
  })

  const ARTIKEL = useMemo(() => {
    if (artikelQuery.data && artikelQuery.data.length > 0) {
      return artikelQuery.data.map((a) => ({ id: a.id, name: a.name }))
    }
    return FALLBACK_ARTIKEL
  }, [artikelQuery.data])

  const LAGERORTE = useMemo(() => {
    if (warehouseQuery.data && warehouseQuery.data.length > 0) {
      return warehouseQuery.data.map((w) => ({ id: w.warehouse_code || w.id, name: w.name }))
    }
    return FALLBACK_LAGERORTE
  }, [warehouseQuery.data])

  function set<K extends keyof KorrekturData>(key: K, value: KorrekturData[K]) {
    setData((prev) => ({ ...prev, [key]: value }))
  }

  const buchungMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/api/v1/lager/bestandskorrektur', {
        article_id: data.articleId,
        warehouse_id: data.warehouseId,
        menge: -Math.abs(data.menge),
        grund: data.grund,
        bemerkung: data.bemerkung || null,
        charge: data.charge || null,
      })
      return res.data
    },
    onSuccess: () => {
      const grundLabel = GRUND_OPTIONS.find((g) => g.code === data.grund)?.label || data.grund
      toast({
        title: 'Korrektur gebucht',
        description: `${data.artikelName}: -${data.menge} t (${grundLabel})`,
      })
      navigate('/lager/lagerbewegungen')
    },
    onError: () => {
      toast({ title: 'Fehler beim Buchen', variant: 'destructive' })
    },
  })

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => buchungMutation.mutate(),
    onCancel: () => navigate('/lager/bestandsuebersicht'),
    isSaveDisabled: buchungMutation.isPending,
  })
  useKeyboardShortcuts(shortcuts)

  const grundLabel = GRUND_OPTIONS.find((g) => g.code === data.grund)?.label || data.grund

  const fallkopf = useMemo(() => {
    const hatDifferenz = data.menge > 0
    const hatGrund = data.grund !== ''
    return {
      status: hatDifferenz && hatGrund ? 'Buchungsbereit' : 'Eingabe unvollstaendig',
      statusColor: hatDifferenz && hatGrund ? 'text-green-700 bg-green-50 border-green-300' : 'text-amber-700 bg-amber-50 border-amber-300',
      differenz: hatDifferenz ? `-${data.menge} t (${grundLabel})` : 'Noch keine Menge erfasst',
      begruendung: hatGrund ? grundLabel : 'Grund noch nicht gewaehlt',
      folgeaktion: hatDifferenz && hatGrund ? 'Korrektur pruefen und buchen' : 'Alle Pflichtfelder ausfuellen',
    }
  }, [data.menge, data.grund, grundLabel])

  const steps = [
    {
      id: 'artikel',
      title: 'Artikel & Lagerort',
      content: (
        <TouchSection title="Artikel waehlen">
          <TouchCardGroup label="Artikel" required>
            {ARTIKEL.map((art) => (
              <TouchCard
                key={art.id}
                selected={data.articleId === art.id}
                onSelect={() => { set('articleId', art.id); set('artikelName', art.name) }}
              >
                {art.name}
              </TouchCard>
            ))}
          </TouchCardGroup>
          <TouchCardGroup label="Lagerort" required>
            {LAGERORTE.map((lo) => (
              <TouchCard
                key={lo.id}
                selected={data.warehouseId === lo.id}
                onSelect={() => { set('warehouseId', lo.id); set('lagerortName', lo.name) }}
              >
                {lo.name}
              </TouchCard>
            ))}
          </TouchCardGroup>
        </TouchSection>
      ),
    },
    {
      id: 'korrektur',
      title: 'Korrektur',
      content: (
        <TouchSection title="Korrekturdaten">
          <TouchCardGroup label="Grund" required>
            {GRUND_OPTIONS.map((g) => (
              <TouchCard
                key={g.code}
                selected={data.grund === g.code}
                onSelect={() => set('grund', g.code)}
              >
                {g.label}
              </TouchCard>
            ))}
          </TouchCardGroup>
          <TouchNumericInput
            label="Korrekturbetrag"
            value={data.menge}
            onChange={(v) => set('menge', Number(v))}
            unit="t"
            min={0}
            step={0.001}
            required
          />
          <TouchTextInput
            label="Charge (optional)"
            value={data.charge}
            onChange={(v) => set('charge', v)}
            placeholder="z.B. 251011-WEI-001"
          />
          <TouchTextInput
            label="Bemerkung"
            value={data.bemerkung}
            onChange={(v) => set('bemerkung', v)}
            placeholder="Freitext..."
          />
        </TouchSection>
      ),
    },
    {
      id: 'bestaetigung',
      title: 'Bestaetigung',
      content: (
        <div className="space-y-6">
          <div className="flex flex-col items-center gap-2 py-2">
            <AlertTriangle className="h-16 w-16 text-amber-500" />
            <h3 className="text-xl font-bold text-slate-800">Korrektur pruefen</h3>
            <p className="text-sm text-slate-500">Die Buchung kann nicht rueckgaengig gemacht werden</p>
          </div>
          <TouchConfirmCard
            title="Zusammenfassung"
            fields={[
              { label: 'Artikel', value: data.artikelName || data.articleId, highlight: true },
              { label: 'Lagerort', value: data.lagerortName || data.warehouseId },
              { label: 'Grund', value: grundLabel, highlight: true },
              { label: 'Menge', value: `-${data.menge} t`, highlight: true },
              { label: 'Charge', value: data.charge || '—' },
              { label: 'Bemerkung', value: data.bemerkung || '—' },
            ]}
          />
        </div>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="p-4 sm:p-6">
        {/* Operativer Fallkopf */}
        <Card className={`border mb-4 ${fallkopf.statusColor}`}>
          <CardContent className="pt-4 pb-3 text-sm space-y-1">
            <div className="font-semibold">Korrektur-Status: {fallkopf.status}</div>
            <div>Differenz: {fallkopf.differenz}</div>
            <div>Begruendung: {fallkopf.begruendung}</div>
            <div>Folgeaktion: {fallkopf.folgeaktion}</div>
          </CardContent>
        </Card>
        <Wizard
          title="Bestandskorrektur"
          steps={steps}
          onFinish={() => buchungMutation.mutate()}
          onCancel={() => navigate('/lager/bestandsuebersicht')}
        />
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
