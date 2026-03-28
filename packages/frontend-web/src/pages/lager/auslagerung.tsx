/**
 * Auslagerung — Touch-optimierter Kernflow (Gap 024, Wave 92)
 * TouchCards für Artikel- und Strategieauswahl, Keyboard-Shortcuts für Desktop
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Wizard } from '@/components/patterns/Wizard'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { CheckCircle } from 'lucide-react'
import { AgentSuggestionBadge, AgentProcessPanel } from '@/components/agent'
import {
  TouchSection,
  TouchTextInput,
  TouchNumericInput,
  TouchCard,
  TouchCardGroup,
  TouchConfirmCard,
} from '@/components/touch/TouchFieldLayout'

type AuslagerungData = {
  artikel: string
  menge: number
  strategie: 'fifo' | 'fefo' | 'manuell'
  chargenId: string
  verwendungszweck: string
}

const STRATEGIEN = [
  { id: 'fifo' as const, label: 'FIFO', description: 'Älteste Charge zuerst', empfohlen: true },
  { id: 'fefo' as const, label: 'FEFO', description: 'Kürzeste Haltbarkeit zuerst', empfohlen: false },
  { id: 'manuell' as const, label: 'Manuell', description: 'Chargen-ID selbst wählen', empfohlen: false },
]

export default function AuslagerungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const { data: articlesData } = useQuery({
    queryKey: ['articles', 'auslagerung'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: Array<{ id: string; name: string; article_number?: string }> }>(
        '/api/v1/articles?limit=100',
      )
      return res.data
    },
    staleTime: 5 * 60_000,
  })
  const ARTIKEL = articlesData?.items?.map((a) => a.name ?? a.article_number ?? a.id) ?? [
    'Weizen', 'Gerste', 'Raps', 'Mais', 'Roggen', 'Hafer', 'Sonnenblumen',
  ]

  const [auslagerung, setAuslagerung] = useState<AuslagerungData>({
    artikel: '',
    menge: 0,
    strategie: 'fifo',
    chargenId: '',
    verwendungszweck: '',
  })
  const [saving, setSaving] = useState(false)

  function updateField<K extends keyof AuslagerungData>(key: K, value: AuslagerungData[K]): void {
    if (key === 'strategie' && value === 'fifo') {
      setAuslagerung((prev) => ({ ...prev, [key]: value, chargenId: '' }))
    } else {
      setAuslagerung((prev) => ({ ...prev, [key]: value }))
    }
  }

  const handleFinish = async (): Promise<void> => {
    setSaving(true)
    try {
      await apiClient.post('/api/v1/lager/auslagerung', {
        artikel: auslagerung.artikel,
        menge: auslagerung.menge,
        strategie: auslagerung.strategie,
        chargen_id: auslagerung.chargenId || undefined,
        verwendungszweck: auslagerung.verwendungszweck || undefined,
      })
      toast({ title: 'Auslagerung gebucht', description: `${auslagerung.artikel}: ${auslagerung.menge} t` })
      navigate('/lager/bestandsuebersicht')
    } catch (e: any) {
      toast({ title: 'Buchung fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    } finally {
      setSaving(false)
    }
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => { void handleFinish() },
    onCancel: () => navigate('/lager/bestandsuebersicht'),
    isSaveDisabled: saving,
  })
  useKeyboardShortcuts(shortcuts)

  const strategieLabel = STRATEGIEN.find((s) => s.id === auslagerung.strategie)?.label ?? auslagerung.strategie

  const steps = [
    {
      id: 'artikel',
      title: 'Artikel',
      content: (
        <TouchSection title="Artikel & Menge">
          <TouchCardGroup label="Artikel" required>
            {ARTIKEL.map((art) => (
              <TouchCard
                key={art}
                selected={auslagerung.artikel === art}
                onSelect={() => updateField('artikel', art)}
              >
                {art}
              </TouchCard>
            ))}
          </TouchCardGroup>
          <TouchNumericInput
            label="Menge"
            value={auslagerung.menge}
            onChange={(v) => updateField('menge', Number(v))}
            unit="t"
            min={0}
            step={0.001}
            required
          />
          <TouchTextInput
            label="Verwendungszweck (optional)"
            value={auslagerung.verwendungszweck}
            onChange={(v) => updateField('verwendungszweck', v)}
            placeholder="z.B. Verkauf, Verarbeitung"
          />
        </TouchSection>
      ),
    },
    {
      id: 'strategie',
      title: 'Strategie',
      content: (
        <TouchSection title="Auslagerungs-Strategie">
          <AgentSuggestionBadge
            capabilityKey="auslagerung_assistant"
            parameters={{ artikel: auslagerung.artikel, menge: auslagerung.menge }}
            renderSuggestion={(s: { strategie?: string; chargenId?: string }) => (
              <div className="space-y-1 text-xs text-violet-800">
                {s.strategie && <div><span className="font-medium">Strategie:</span> {s.strategie.toUpperCase()}</div>}
                {s.chargenId && <div><span className="font-medium">Charge:</span> {s.chargenId}</div>}
              </div>
            )}
            onAccept={(s: { strategie?: string; chargenId?: string }) => {
              if (s.strategie) updateField('strategie', s.strategie as 'fifo' | 'fefo' | 'manuell')
              if (s.chargenId) updateField('chargenId', s.chargenId)
            }}
          />
          <TouchCardGroup label="Strategie wählen" required>
            {STRATEGIEN.map((s) => (
              <TouchCard
                key={s.id}
                selected={auslagerung.strategie === s.id}
                onSelect={() => updateField('strategie', s.id)}
                description={s.description}
              >
                <span className="flex items-center gap-2">
                  {s.label}
                  {s.empfohlen && <Badge className="text-xs">Empfohlen</Badge>}
                </span>
              </TouchCard>
            ))}
          </TouchCardGroup>
          {auslagerung.strategie === 'manuell' && (
            <TouchTextInput
              label="Chargen-ID"
              value={auslagerung.chargenId}
              onChange={(v) => updateField('chargenId', v)}
              placeholder="z.B. 251011-WEI-001"
              autoCapitalize="characters"
              required
            />
          )}
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
            <h3 className="text-xl font-bold text-slate-800">Auslagerung prüfen</h3>
          </div>
          <TouchConfirmCard
            title="Zusammenfassung"
            fields={[
              { label: 'Artikel', value: auslagerung.artikel || '—', highlight: true },
              { label: 'Menge', value: `${auslagerung.menge} t`, highlight: true },
              { label: 'Strategie', value: strategieLabel },
              ...(auslagerung.chargenId ? [{ label: 'Charge', value: auslagerung.chargenId }] : []),
              ...(auslagerung.verwendungszweck ? [{ label: 'Verwendung', value: auslagerung.verwendungszweck }] : []),
            ]}
          />
        </div>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="p-6">
        <ModuleToolbar backTarget="/lager/bestandsuebersicht" closeTarget="/lager/bestandsuebersicht" title="Auslagerung" />
        <AgentProcessPanel domain="lager" className="mb-4" />
        <Wizard title="Auslagerung" steps={steps} onFinish={handleFinish} onCancel={() => navigate('/lager/bestandsuebersicht')} />
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
