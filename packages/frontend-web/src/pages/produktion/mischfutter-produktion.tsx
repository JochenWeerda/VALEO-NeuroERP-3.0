import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle, Loader2 } from 'lucide-react'
import { useMischfutterVerfuegbarkeit, useMischfutterRezepte, useCreateProduktionsauftrag } from '@/lib/api/produktion'
import { useToast } from '@/hooks/use-toast'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type KomponentenBedarf = { name: string; bedarf: number; verfuegbar: number }
type ProductionRole = 'produktion' | 'lager' | 'qs' | 'leitung'

const productionRoles = [
  { id: 'produktion', label: 'Produktion', description: 'Plant Rezeptur, Menge, Charge und Start des Produktionsauftrags.' },
  { id: 'lager', label: 'Lager', description: 'Prueft Komponentenverfuegbarkeit und Abbuchung.' },
  { id: 'qs', label: 'QS', description: 'Achtet auf Charge, Rezeptur und spaeteren Produktionsnachweis.' },
  { id: 'leitung', label: 'Leitung', description: 'Sieht, ob Auftrag und Material fuer den Start bereit sind.' },
] satisfies Array<{ id: ProductionRole; label: string; description: string }>

export default function MischfutterProduktionPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const { data: verfuegbarkeit, isLoading: loadingV } = useMischfutterVerfuegbarkeit()
  const { data: rezepte, isLoading: loadingR } = useMischfutterRezepte()
  const createAuftrag = useCreateProduktionsauftrag()

  const [rezeptur, setRezeptur] = useState('')
  const [menge, setMenge] = useState(0)
  const [chargenId, setChargenId] = useState('')
  const [roleFocus, setRoleFocus] = useState<ProductionRole>('produktion')

  // Build a map of component name -> available tons from the API
  const verfuegbarkeitMap = useMemo(() => {
    const map: Record<string, number> = {}
    for (const v of verfuegbarkeit) {
      map[v.name] = v.verfuegbar_t
    }
    return map
  }, [verfuegbarkeit])

  // Find the selected recipe
  const selectedRezept = useMemo(
    () => rezepte.find((r) => r.code === rezeptur),
    [rezepte, rezeptur],
  )

  // Calculate component requirements based on selected recipe + quantity
  const komponenten: KomponentenBedarf[] = useMemo(() => {
    if (!selectedRezept || menge <= 0) return []
    return selectedRezept.komponenten.map((k) => ({
      name: k.name,
      bedarf: menge * k.anteil,
      verfuegbar: verfuegbarkeitMap[k.name] ?? 0,
    }))
  }, [selectedRezept, menge, verfuegbarkeitMap])
  const missingComponents = komponenten.filter((k) => k.verfuegbar < k.bedarf)
  const productionReady = Boolean(selectedRezept && menge > 0 && chargenId && komponenten.length > 0 && missingComponents.length === 0)
  const nextProductionAction = !selectedRezept
    ? 'Rezeptur auswaehlen.'
    : menge <= 0
      ? 'Produktionsmenge eintragen.'
      : missingComponents.length > 0
        ? `${missingComponents.length} Komponente(n) fehlen: Bestand klaeren oder Menge anpassen.`
        : 'Produktionsauftrag erstellen und Chargennachweis sichern.'

  function handleRezepturChange(code: string) {
    setRezeptur(code)
    if (menge > 0) {
      setChargenId(
        `MF-${new Date().toISOString().slice(2, 10).replace(/-/g, '')}-${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`,
      )
    }
  }

  function handleMengeChange(value: number) {
    setMenge(value)
    if (value > 0) {
      setChargenId(
        `MF-${new Date().toISOString().slice(2, 10).replace(/-/g, '')}-${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`,
      )
    }
  }

  function handleFinish() {
    createAuftrag.mutate(
      { rezeptur, menge, chargen_id: chargenId },
      {
        onSuccess: (result) => {
          toast({
            title: 'Produktionsauftrag erstellt',
            description: `Chargen-ID: ${result.chargen_id}`,
          })
          navigate('/futter/misch/liste')
        },
        onError: () => {
          toast({ title: 'Fehler beim Erstellen', variant: 'destructive' })
        },
      },
    )
  }

  if (loadingV || loadingR) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="ml-3 text-muted-foreground">Rezepturen & Verfügbarkeit laden…</span>
      </div>
    )
  }

  const steps = [
    {
      id: 'rezeptur',
      title: 'Rezeptur',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="rezeptur">Rezeptur *</Label>
            <select
              id="rezeptur"
              value={rezeptur}
              onChange={(e) => handleRezepturChange(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              {rezepte.map((r) => (
                <option key={r.code} value={r.code}>
                  {r.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label htmlFor="menge">Produktionsmenge (t) *</Label>
            <Input
              id="menge"
              type="number"
              value={menge}
              onChange={(e) => handleMengeChange(Number(e.target.value))}
              step="0.1"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'komponenten',
      title: 'Komponenten',
      content: (
        <div className="space-y-3">
          <Label>Rezeptur-Komponenten (Bedarf vs. Verfügbar)</Label>
          {komponenten.map((k, i) => {
            const ausreichend = k.verfuegbar >= k.bedarf
            return (
              <Card key={i} className={ausreichend ? 'border-green-500' : 'border-red-500'}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{k.name}</div>
                      <div className="text-sm text-muted-foreground">
                        Verfügbar: {k.verfuegbar.toFixed(1)} t
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">{k.bedarf.toFixed(1)} t</div>
                      <Badge variant={ausreichend ? 'outline' : 'destructive'}>
                        {ausreichend ? '✓ OK' : '✗ Fehlt'}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
          {komponenten.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Bitte zuerst Rezeptur und Menge festlegen.
            </p>
          )}
        </div>
      ),
    },
    {
      id: 'produktion',
      title: 'Produktion',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Produktion bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Rezeptur</dt>
                <dd className="font-semibold">{selectedRezept?.name || rezeptur || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Menge</dt>
                <dd className="font-semibold">{menge} t</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Komponenten</dt>
                <dd className="font-semibold">{komponenten.length}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Chargen-ID</dt>
                <dd className="font-mono font-semibold">{chargenId}</dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
              <p className="font-semibold">Produktionsauftrag wird erstellt</p>
              <p className="mt-1">Komponenten werden automatisch ausgebucht</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="space-y-6 p-3 md:p-6">
      <RoleFocusBar roles={productionRoles} value={roleFocus} onChange={setRoleFocus} visibleCount={komponenten.length} totalCount={komponenten.length} title="Wer bereitet die Produktion vor?" />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <ManagementDecisionPanel
          decision={{
            allowed: productionReady,
            allowedLabel: 'Produktion startbereit',
            blockedLabel: 'Vorbereitung offen',
            summary: productionReady
              ? `Rezeptur, Menge, Charge und ${komponenten.length} Komponente(n) sind verfuegbar. Der Produktionsauftrag kann erstellt werden.`
              : 'Vor dem Produktionsstart muessen Rezeptur, Menge, Charge und Komponentenverfuegbarkeit vollstaendig sein.',
            blockerCount: (selectedRezept ? 0 : 1) + (menge > 0 ? 0 : 1) + missingComponents.length,
            nextFocus: nextProductionAction,
            template: { label: 'Produktionsauftrag und Chargennachweis', href: '/docs/produktion/produktionsauftrag-chargennachweis.md' },
          }}
        />
        <div className="space-y-4">
          <NextActionPanel action={nextProductionAction} tone={productionReady ? 'emerald' : missingComponents.length > 0 ? 'red' : 'amber'} />
          <EvidenceTemplateLink link={{ label: 'Mischfutter-Produktionsnachweis', href: '/docs/produktion/mischfutter-produktionsnachweis.md' }} />
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <OperationalTaskPlan
          title="Produktionsplan"
          items={[
            { label: 'Rezeptur waehlen', done: Boolean(selectedRezept), hint: selectedRezept?.name ?? 'Noch keine Rezeptur gewaehlt.' },
            { label: 'Menge festlegen', done: menge > 0, hint: menge > 0 ? `${menge} t geplant.` : 'Produktionsmenge fehlt.' },
            { label: 'Komponenten pruefen', done: komponenten.length > 0 && missingComponents.length === 0, hint: missingComponents.length > 0 ? `${missingComponents.length} Komponente(n) fehlen.` : `${komponenten.length} Komponente(n) geprueft.` },
            { label: 'Charge sichern', done: Boolean(chargenId), hint: chargenId || 'Chargen-ID entsteht nach Rezeptur und Menge.' },
          ]}
        />
        <CrudCapabilityChecklist
          capabilities={[
            { key: 'create', label: 'Produktionsauftrag erstellen', available: true, hint: 'Wizard erstellt den Auftrag am Ende.' },
            { key: 'read', label: 'Rezeptur und Bestand lesen', available: true, hint: 'Rezepturen und Komponentenverfuegbarkeit sind sichtbar.' },
            { key: 'update', label: 'Menge anpassen', available: true, hint: 'Menge und Rezeptur koennen vor Abschluss geaendert werden.' },
            { key: 'approve', label: 'Start freigeben', available: productionReady, hint: 'Freigabe ist fachlich sinnvoll, wenn keine Komponente fehlt.' },
            { key: 'evidence', label: 'Chargennachweis', available: true, hint: 'Produktionsnachweis ist verlinkt.' },
            { key: 'audit', label: 'Materialentscheidung', available: true, hint: 'Bedarf gegen Verfuegbarkeit ist je Komponente sichtbar.' },
          ]}
        />
      </div>
      <Wizard
        title="Mischfutter-Produktion"
        steps={steps}
        onFinish={handleFinish}
        onCancel={() => navigate('/futter/misch/liste')}
      />
    </div>
  )
}
