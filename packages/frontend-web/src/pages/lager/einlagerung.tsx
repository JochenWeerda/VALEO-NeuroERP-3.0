/**
 * Einlagerung — Touch-optimierter Feldworkflow (Gap 024, Wave 76)
 * Touch-Targets >= 44px, Lagerort-Auswahl via TouchCard statt <select>
 */
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Wizard } from '@/components/patterns/Wizard'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { CheckCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { AgentSuggestionBadge, AgentProcessPanel } from '@/components/agent'
import { useToast } from '@/hooks/use-toast'
import {
  TouchSection,
  TouchTextInput,
  TouchNumericInput,
  TouchCard,
  TouchCardGroup,
  TouchConfirmCard,
} from '@/components/touch/TouchFieldLayout'

type EinlagerungData = {
  chargenId: string
  artikel: string
  menge: number
  lagerort: string
  lagerplatz: string
}

const FALLBACK_LAGERORTE = [
  { id: 'silo-1', label: 'Silo 1', description: 'Weizen / Roggen' },
  { id: 'silo-2', label: 'Silo 2', description: 'Gerste / Hafer' },
  { id: 'halle-a', label: 'Halle A', description: 'Allgemein' },
  { id: 'halle-b', label: 'Halle B', description: 'Saecke / Paletten' },
]

const FALLBACK_ARTIKEL = ['Weizen', 'Gerste', 'Raps', 'Mais', 'Roggen', 'Hafer', 'Sonnenblumen']

export default function EinlagerungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [einlagerung, setEinlagerung] = useState<EinlagerungData>({
    chargenId: '',
    artikel: '',
    menge: 0,
    lagerort: '',
    lagerplatz: '',
  })

  const artikelQuery = useQuery({
    queryKey: ['articles', 'einlagerung'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: Array<{ id: string; name: string; article_number: string }> }>('/api/v1/articles?limit=100')
      return res.data?.items ?? []
    },
  })

  const warehouseQuery = useQuery({
    queryKey: ['warehouses', 'einlagerung'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: Array<{ id: string; warehouse_code: string; name: string; warehouse_type: string }> }>('/api/v1/warehouses?limit=100')
      return res.data?.items ?? []
    },
  })

  const ARTIKEL = useMemo(() => {
    if (artikelQuery.data && artikelQuery.data.length > 0) {
      return artikelQuery.data.map((a) => a.name)
    }
    return FALLBACK_ARTIKEL
  }, [artikelQuery.data])

  const LAGERORTE = useMemo(() => {
    if (warehouseQuery.data && warehouseQuery.data.length > 0) {
      return warehouseQuery.data.map((w) => ({
        id: w.warehouse_code || w.id,
        label: w.name,
        description: w.warehouse_type || '',
      }))
    }
    return FALLBACK_LAGERORTE
  }, [warehouseQuery.data])

  function set<K extends keyof EinlagerungData>(key: K, value: EinlagerungData[K]): void {
    setEinlagerung((prev) => ({ ...prev, [key]: value }))
  }

  const buchungMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/api/v1/lager/einlagerung', {
        chargen_id: einlagerung.chargenId,
        artikel: einlagerung.artikel,
        menge: einlagerung.menge,
        lagerort: einlagerung.lagerort,
        lagerplatz: einlagerung.lagerplatz || null,
      })
      return response.data
    },
    onSuccess: () => {
      toast({
        title: 'Einlagerung gebucht',
        description: `${einlagerung.artikel} (${einlagerung.chargenId}) — ${einlagerung.menge} t → ${einlagerung.lagerort}`,
      })
      navigate('/lager/bestandsuebersicht')
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

  const lagerLabel = LAGERORTE.find((l) => l.id === einlagerung.lagerort)?.label ?? einlagerung.lagerort

  const steps = [
    {
      id: 'charge',
      title: 'Charge',
      content: (
        <TouchSection title="Charge & Artikel">
          <TouchTextInput
            label="Chargen-ID"
            value={einlagerung.chargenId}
            onChange={(v) => set('chargenId', v)}
            placeholder="z.B. 251011-WEI-001"
            autoCapitalize="characters"
            required
          />
          <TouchCardGroup label="Artikel" required>
            {ARTIKEL.map((art) => (
              <TouchCard
                key={art}
                selected={einlagerung.artikel === art}
                onSelect={() => set('artikel', art)}
              >
                {art}
              </TouchCard>
            ))}
          </TouchCardGroup>
          <TouchNumericInput
            label="Menge"
            value={einlagerung.menge}
            onChange={(v) => set('menge', Number(v))}
            unit="t"
            min={0}
            step={0.001}
            required
          />
        </TouchSection>
      ),
    },
    {
      id: 'lagerort',
      title: 'Lagerort',
      content: (
        <TouchSection title="Lagerort wählen">
          <AgentSuggestionBadge
            capabilityKey="einlagerung_assistant"
            parameters={{ artikel: einlagerung.artikel, menge: einlagerung.menge }}
            renderSuggestion={(s: { lagerort?: string; lagerplatz?: string }) => (
              <div className="space-y-1 text-xs text-violet-800">
                {s.lagerort && <div><span className="font-medium">Lagerort:</span> {s.lagerort}</div>}
                {s.lagerplatz && <div><span className="font-medium">Platz:</span> {s.lagerplatz}</div>}
              </div>
            )}
            onAccept={(s: { lagerort?: string; lagerplatz?: string }) => {
              if (s.lagerort) set('lagerort', s.lagerort)
              if (s.lagerplatz) set('lagerplatz', s.lagerplatz)
            }}
          />
          <TouchCardGroup label="Lagerort" required>
            {LAGERORTE.map((lo) => (
              <TouchCard
                key={lo.id}
                selected={einlagerung.lagerort === lo.id}
                onSelect={() => set('lagerort', lo.id)}
                description={lo.description}
              >
                {lo.label}
              </TouchCard>
            ))}
          </TouchCardGroup>
          <TouchTextInput
            label="Lagerplatz (optional)"
            value={einlagerung.lagerplatz}
            onChange={(v) => set('lagerplatz', v)}
            placeholder="z.B. A-12-03"
            hint="Leer lassen für automatische Zuweisung"
          />
        </TouchSection>
      ),
    },
    {
      id: 'bestaetigung',
      title: 'Bestätigung',
      content: (
        <div className="space-y-6">
          <div className="flex flex-col items-center gap-2 py-2">
            <CheckCircle className="h-16 w-16 text-emerald-500" />
            <h3 className="text-xl font-bold text-slate-800">Einlagerung prüfen</h3>
            <p className="text-sm text-slate-500">Bitte alle Angaben bestätigen</p>
          </div>
          <TouchConfirmCard
            title="Zusammenfassung"
            fields={[
              { label: 'Charge', value: einlagerung.chargenId || '—' },
              { label: 'Artikel', value: einlagerung.artikel || '—', highlight: true },
              { label: 'Menge', value: `${einlagerung.menge} t`, highlight: true },
              { label: 'Lagerort', value: lagerLabel || '—' },
              { label: 'Lagerplatz', value: einlagerung.lagerplatz || 'Auto' },
            ]}
          />
        </div>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="p-4 sm:p-6">
        <AgentProcessPanel domain="lager" className="mb-4" />
        <Wizard
          title="Einlagerung"
          steps={steps}
          onFinish={() => buchungMutation.mutate()}
          onCancel={() => navigate('/lager/bestandsuebersicht')}
        />
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
