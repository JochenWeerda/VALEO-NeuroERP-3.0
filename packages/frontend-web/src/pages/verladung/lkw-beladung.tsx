/**
 * LKW-Beladung — Touch-optimierter Kernflow (Gap 024, Wave 92)
 * TouchCards für Verladeort- und Artikel-Auswahl, Keyboard-Shortcuts für Desktop
 */
import { useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useQuery } from '@tanstack/react-query'
import { Wizard } from '@/components/patterns/Wizard'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useToast } from '@/hooks/use-toast'
import { api } from '@/lib/axios'
import { apiClient } from '@/lib/api-client'
import { CheckCircle } from 'lucide-react'
import { AgentProcessPanel } from '@/components/agent'
import {
  TouchSection,
  TouchTextInput,
  TouchNumericInput,
  TouchCard,
  TouchCardGroup,
  TouchConfirmCard,
} from '@/components/touch/TouchFieldLayout'

type BeladungData = {
  kennzeichen: string
  lieferscheinNr: string
  artikel: string
  menge: number
  chargenId: string
  verladeort: string
}

const FALLBACK_ARTIKEL = ['Weizen', 'Gerste', 'Raps', 'Mais', 'Roggen', 'Hafer', 'Sonnenblumen']

type SiloOption = { id: string; label: string; description: string }

export default function LKWBeladungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const { data: articlesData } = useQuery({
    queryKey: ['articles', 'lkw-beladung'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: Array<{ id: string; name: string; article_number?: string }> }>(
        '/api/v1/articles?limit=100',
      )
      return res.data
    },
    staleTime: 5 * 60_000,
  })
  const ARTIKEL_OPTIONEN = articlesData?.items?.map((a) => a.name ?? a.article_number ?? a.id) ?? FALLBACK_ARTIKEL

  const { data: silosData } = useQuery({
    queryKey: ['silo', 'verladeorte'],
    queryFn: async () => {
      const res = await apiClient.get<{ liste: Array<{ id: string; nummer: string; artikel?: string }> }>(
        '/api/v1/silo/kapazitaeten',
      )
      return res.data
    },
    staleTime: 5 * 60_000,
  })
  const VERLADEORTE: SiloOption[] = silosData?.liste?.map((s) => ({
    id: s.id,
    label: s.nummer,
    description: s.artikel ?? 'Schüttgut',
  })) ?? [
    { id: 'silo-1', label: 'Silo 1', description: 'Weizen / Roggen' },
    { id: 'silo-2', label: 'Silo 2', description: 'Gerste / Hafer' },
    { id: 'halle-a', label: 'Halle A', description: 'Schüttgut allgemein' },
  ]
  const [beladung, setBeladung] = useState<BeladungData>({
    kennzeichen: '',
    lieferscheinNr: '',
    artikel: '',
    menge: 0,
    chargenId: '',
    verladeort: '',
  })
  const [saving, setSaving] = useState(false)

  function updateField<K extends keyof BeladungData>(key: K, value: BeladungData[K]): void {
    setBeladung((prev) => ({ ...prev, [key]: value }))
  }

  const handleFinish = async (): Promise<void> => {
    setSaving(true)
    try {
      await api.post('/api/v1/lager/verladung', {
        kennzeichen: beladung.kennzeichen,
        lieferschein_nr: beladung.lieferscheinNr || undefined,
        artikel: beladung.artikel,
        menge: beladung.menge,
        chargen_id: beladung.chargenId || undefined,
        verladeort: beladung.verladeort,
      })
      toast({ title: 'Beladung gebucht', description: `${beladung.artikel}: ${beladung.menge} t` })
      navigate('/logistik/verladungen')
    } catch (e: any) {
      toast({ title: 'Buchung fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    } finally {
      setSaving(false)
    }
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => { void handleFinish() },
    onCancel: () => navigate('/logistik/verladungen'),
    isSaveDisabled: saving,
  })
  useKeyboardShortcuts(shortcuts)

  const verladeortLabel = VERLADEORTE.find((v) => v.id === beladung.verladeort)?.label ?? beladung.verladeort

  const steps = [
    {
      id: 'lkw',
      title: 'LKW',
      content: (
        <TouchSection title="Fahrzeug & Lieferschein">
          <TouchTextInput
            label="Kennzeichen"
            value={beladung.kennzeichen}
            onChange={(v) => updateField('kennzeichen', v.toUpperCase())}
            placeholder="z.B. AB-CD 1234"
            autoCapitalize="characters"
            required
          />
          <TouchTextInput
            label="Lieferschein-Nr."
            value={beladung.lieferscheinNr}
            onChange={(v) => updateField('lieferscheinNr', v)}
            placeholder="z.B. LS-2025-042"
          />
        </TouchSection>
      ),
    },
    {
      id: 'artikel',
      title: 'Artikel',
      content: (
        <TouchSection title="Artikel & Menge">
          <TouchCardGroup label="Artikel" required>
            {ARTIKEL_OPTIONEN.map((art) => (
              <TouchCard
                key={art}
                selected={beladung.artikel === art}
                onSelect={() => updateField('artikel', art)}
              >
                {art}
              </TouchCard>
            ))}
          </TouchCardGroup>
          <TouchNumericInput
            label="Menge"
            value={beladung.menge}
            onChange={(v) => updateField('menge', Number(v))}
            unit="t"
            min={0}
            step={0.001}
            required
          />
          <TouchTextInput
            label="Chargen-ID"
            value={beladung.chargenId}
            onChange={(v) => updateField('chargenId', v)}
            placeholder="z.B. 251011-WEI-001"
            autoCapitalize="characters"
            required
          />
        </TouchSection>
      ),
    },
    {
      id: 'verladeort',
      title: 'Verladeort',
      content: (
        <TouchSection title="Verladeort wählen">
          <TouchCardGroup label="Verladeort" required>
            {VERLADEORTE.map((vo) => (
              <TouchCard
                key={vo.id}
                selected={beladung.verladeort === vo.id}
                onSelect={() => updateField('verladeort', vo.id)}
                description={vo.description}
              >
                {vo.label}
              </TouchCard>
            ))}
          </TouchCardGroup>
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
            <h3 className="text-xl font-bold text-slate-800">Beladung prüfen</h3>
          </div>
          <TouchConfirmCard
            title="Zusammenfassung"
            fields={[
              { label: 'Kennzeichen', value: beladung.kennzeichen || '—', highlight: true },
              { label: 'Lieferschein', value: beladung.lieferscheinNr || '—' },
              { label: 'Artikel', value: beladung.artikel || '—', highlight: true },
              { label: 'Menge', value: `${beladung.menge} t`, highlight: true },
              { label: 'Charge', value: beladung.chargenId || '—' },
              { label: 'Verladeort', value: verladeortLabel || '—' },
            ]}
          />
          <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
            <p className="font-semibold">Beladung wird dokumentiert</p>
            <p className="mt-1">Lieferschein wird automatisch erstellt</p>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
      <div className="p-3 md:p-6">
        <ModuleToolbar backTarget="/logistik/verladungen" closeTarget="/logistik/verladungen" title="LKW-Beladung" />
        <AgentProcessPanel domain="lager" className="mb-4" />
        <Wizard
          title="LKW-Beladung"
          steps={steps}
          onFinish={handleFinish}
          onCancel={() => navigate('/logistik/verladungen')}
          loading={saving}
        />
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
