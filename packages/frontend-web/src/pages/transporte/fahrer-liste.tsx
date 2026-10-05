import { useCallback, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useLocation, useNavigate, useParams } from '@/app/routing/typed-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { toast } from '@/hooks/use-toast'
import { mapFahrerZeile, useFahrerListe } from '@/lib/api/betrieb'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { useTouren } from '@/lib/api/misc-modules'
import { tourenHeuteFuerFahrer } from '@/lib/logistik/disposition'
import { transporteFahrerScreen } from '@/masks/capture-screens'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

function FahrerNeu(): JSX.Element {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [vorname, setVorname] = useState('')
  const [name, setName] = useState('')
  const [fuehrerschein, setFuehrerschein] = useState('CE')
  const [saving, setSaving] = useState(false)

  const save = async (): Promise<void> => {
    if (saving) return
    setSaving(true)
    try {
      const { data } = await apiClient.post<{ id: string }>('/api/v1/transporte/fahrer', {
        vorname: vorname.trim() || null,
        name: name.trim(),
        fuehrerschein: fuehrerschein.trim(),
        status: 'verfuegbar',
      })
      await queryClient.invalidateQueries({ queryKey: ['transporte', 'fahrer'] })
      toast({ title: 'Fahrer angelegt', description: [vorname, name].filter(Boolean).join(' ') })
      navigate(`/transporte/fahrer/${data.id}`)
    } catch (error) {
      toast({ title: 'Fahrer nicht angelegt', description: getAxiosErrorMessage(error), variant: 'destructive' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <h1 className="text-xl font-semibold tracking-tight">Neuer Fahrer</h1>
      <Card>
        <CardContent className="space-y-3 pt-6">
          <div>
            <label htmlFor="fahrer-vorname" className="mb-1 block text-sm font-medium">Vorname</label>
            <Input id="fahrer-vorname" value={vorname} onChange={(event) => setVorname(event.target.value)} className="min-h-touch" />
          </div>
          <div>
            <label htmlFor="fahrer-name" className="mb-1 block text-sm font-medium">Name</label>
            <Input id="fahrer-name" value={name} onChange={(event) => setName(event.target.value)} className="min-h-touch" />
          </div>
          <div>
            <label htmlFor="fahrer-klasse" className="mb-1 block text-sm font-medium">Führerscheinklasse</label>
            <Input id="fahrer-klasse" value={fuehrerschein} onChange={(event) => setFuehrerschein(event.target.value)} className="min-h-touch" />
          </div>
          <div className="flex gap-2">
            <Button type="button" className="min-h-touch touch-manipulation" disabled={saving || name.trim().length < 2 || fuehrerschein.trim().length < 1} onClick={() => void save()}>
              {saving ? 'Wird gespeichert…' : 'Speichern'}
            </Button>
            <Button type="button" variant="outline" className="min-h-touch touch-manipulation" disabled={saving} onClick={() => navigate('/transporte/fahrer')}>
              Zurück
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function FahrerDetail({ id }: { id: string }): JSX.Element {
  const navigate = useNavigate()
  const fahrer = useQuery({
    queryKey: ['transporte', 'fahrer', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Parameters<typeof mapFahrerZeile>[0]>(`/api/v1/transporte/fahrer/${encodeURIComponent(id)}`)
      return mapFahrerZeile(data)
    },
  })
  return (
    <div className="space-y-4 p-3 md:p-6">
      <h1 className="text-xl font-semibold tracking-tight">{fahrer.data?.name || 'Fahrer'}</h1>
      <Card>
        <CardContent className="space-y-2 pt-6 text-sm">
          <div>Führerschein: {fahrer.data?.fuehrerschein || '—'}</div>
          <div>Fahrzeug: {fahrer.data?.fahrzeug || '—'}</div>
          <div>Status: {fahrer.data?.status || '—'}</div>
          <Button type="button" variant="outline" className="min-h-touch touch-manipulation" onClick={() => navigate('/transporte/fahrer')}>
            Zur Liste
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default function FahrerListePage(): JSX.Element {
  const { pathname } = useLocation()
  const { id } = useParams<{ id?: string }>()
  if (pathname.endsWith('/neu')) return <FahrerNeu />
  if (id) return <FahrerDetail id={id} />
  return <FahrerListe />
}

function FahrerListe(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const { data: fahrer = [], isError, error, refetch } = useFahrerListe()
  const { data: touren } = useTouren()

  const rows = useMemo(() => fahrer.map((person) => ({
    id: person.id,
    name: person.name,
    fuehrerschein: person.fuehrerschein,
    fahrzeug: person.fahrzeug,
    status: person.status,
    touren_heute: tourenHeuteFuerFahrer(
      (touren?.tourenListe ?? []).map((tour) => ({ datum: tour.datum, status: tour.status, fahrer: tour.fahrer })),
      person.id,
    ),
  })), [fahrer, touren])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...transporteFahrerScreen,
    layout: {
      ...transporteFahrerScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (transporteFahrerScreen.summary ?? []).map((item) => {
      const wert = item.key === 'gesamt'
        ? rows.length
        : item.key === 'verfuegbar'
          ? rows.filter((row) => row.status === 'verfuegbar').length
          : item.key === 'unterwegs'
            ? rows.filter((row) => row.status === 'unterwegs').length
            : rows.reduce((sum, row) => sum + row.touren_heute, 0)
      return { ...item, value: String(wert) }
    }),
  }), [isTouch, rows])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])

  const exportieren = useCallback(() => {
    const header = 'Name;Fuehrerschein;Fahrzeug;Status;Touren heute\n'
    const lines = rows.map((row) =>
      [row.name, row.fuehrerschein, row.fahrzeug, row.status, row.touren_heute]
        .map((value) => `"${String(value).replace(/"/g, '""')}"`)
        .join(';'),
    )
    const blob = new Blob([header + lines.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Fahrer_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${rows.length} Fahrer exportiert.` })
  }, [rows])

  const handleAction = useCallback((key: string) => {
    if (key === 'neu') {
      navigate('/transporte/fahrer/neu')
      return
    }
    if (key === 'verfuegbar') {
      const person = rows.find((row) => row.status === 'verfuegbar')
      if (person) navigate(`/transporte/fahrer/${person.id}`)
      return
    }
    if (key === 'touren') {
      navigate('/logistik/tourenplanung')
      return
    }
    if (key === 'dokumente') {
      navigate('/dokumente/ablage')
      return
    }
    if (key === 'export') exportieren()
  }, [exportieren, navigate, rows])

  const screenContext = useMemo(() => createScreenContext({
    data: { drivers: rows },
    permissions: { granted: [] },
    state: {
      values: {},
      policies: { 'driver.hasAvailable': rows.some((row) => row.status === 'verfuegbar') },
    },
    actions: {
      'driver.create': () => handleAction('neu'),
      'driver.openAvailable': () => handleAction('verfuegbar'),
      'driver.openTours': () => handleAction('touren'),
      'driver.openDocuments': () => handleAction('dokumente'),
      'driver.export': () => handleAction('export'),
    },
    navigation: { push: (route) => navigate(route) },
  }), [handleAction, navigate, rows])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <UniversalMaskRenderer plan={plan} tables={{ list: rows }} onAction={handleAction} screenContext={screenContext} />
    </div>
  )
}
