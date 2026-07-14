import { useState, useMemo, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@/app/routing/typed-router'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle, Link2, Loader2, Package } from 'lucide-react'
import {
  fetchProduktionsTrace,
  updateProduktionsauftragStatus,
  useCreateProduktionsauftrag,
  useEnsureFeedInventoryLink,
  useFeedInventoryLinks,
  useMischfutterRezepte,
  useMischfutterVerfuegbarkeit,
  useProduktionsauftraege,
  type FeedChainTrace,
  type FeedInventoryLinkRow,
  type Produktionsauftrag,
  type ProduktionsauftragStatus,
} from '@/lib/api/produktion'
import { getAxiosErrorMessage } from '@/lib/api-client'
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

const statusLabels: Record<ProduktionsauftragStatus, string> = {
  erstellt: 'Erstellt',
  freigegeben: 'Freigegeben',
  in_produktion: 'In Produktion',
  fertig: 'Fertig',
  storniert: 'Storniert',
}

function statusBadgeVariant(status: ProduktionsauftragStatus): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (status === 'fertig') return 'outline'
  if (status === 'storniert') return 'destructive'
  if (status === 'erstellt') return 'default'
  return 'secondary'
}

/** Nächste fachliche Übergänge je Status (Backend-Zustandsmaschine). */
const nextTransitions: Record<ProduktionsauftragStatus, Array<{ to: Exclude<ProduktionsauftragStatus, 'erstellt'>; label: string; destructive?: boolean }>> = {
  erstellt: [
    { to: 'freigegeben', label: 'Freigeben' },
    { to: 'storniert', label: 'Stornieren', destructive: true },
  ],
  freigegeben: [
    { to: 'in_produktion', label: 'Produktion starten' },
    { to: 'storniert', label: 'Stornieren', destructive: true },
  ],
  in_produktion: [
    { to: 'fertig', label: 'Fertig melden' },
    { to: 'storniert', label: 'Stornieren', destructive: true },
  ],
  fertig: [],
  storniert: [],
}

export default function MischfutterProduktionPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data: verfuegbarkeit, isLoading: loadingV } = useMischfutterVerfuegbarkeit()
  const { data: rezepte, isLoading: loadingR } = useMischfutterRezepte()
  const { data: auftraege } = useProduktionsauftraege()
  const { data: inventoryLinks, isLoading: loadingLinks } = useFeedInventoryLinks()
  const ensureInventoryLink = useEnsureFeedInventoryLink()
  const createAuftrag = useCreateProduktionsauftrag()

  const [rezeptId, setRezeptId] = useState('')
  const [menge, setMenge] = useState(0)
  const [chargenId, setChargenId] = useState('')
  const [roleFocus, setRoleFocus] = useState<ProductionRole>('produktion')
  const [wizardKey, setWizardKey] = useState(0)
  const [pendingActions, setPendingActions] = useState<Set<string>>(new Set())
  const [trace, setTrace] = useState<FeedChainTrace | null>(null)

  const withPending = useCallback(
    async (key: string, fn: () => Promise<void>) => {
      if (pendingActions.has(key)) return
      setPendingActions((prev) => new Set(prev).add(key))
      try {
        await fn()
      } finally {
        setPendingActions((prev) => {
          const next = new Set(prev)
          next.delete(key)
          return next
        })
      }
    },
    [pendingActions],
  )

  const handleStatusAction = useCallback(
    (auftrag: Produktionsauftrag, to: Exclude<ProduktionsauftragStatus, 'erstellt'>) =>
      withPending(`${auftrag.id}:${to}`, async () => {
        try {
          const updated = await updateProduktionsauftragStatus(auftrag.id, to, 'frontend')
          await queryClient.invalidateQueries({ queryKey: ['produktion', 'mischfutter'] })
          if (to === 'fertig' && updated.charge_id) {
            toast({
              title: 'Charge erzeugt',
              description: `Fertigwaren-Charge ${updated.chargen_id} (${updated.charge_id}) ist im Chargen-System.`,
            })
          } else {
            toast({ title: `Auftrag ${statusLabels[to]}`, description: updated.chargen_id })
          }
        } catch (e) {
          toast({ title: 'Statuswechsel fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
        }
      }),
    [queryClient, toast, withPending],
  )

  const handleShowTrace = useCallback(
    (auftrag: Produktionsauftrag) =>
      withPending(`${auftrag.id}:trace`, async () => {
        try {
          setTrace(await fetchProduktionsTrace(auftrag.id))
        } catch (e) {
          toast({ title: 'Trace nicht ladbar', description: getAxiosErrorMessage(e), variant: 'destructive' })
        }
      }),
    [toast, withPending],
  )

  const handleEnsureLink = useCallback(
    (row: FeedInventoryLinkRow) =>
      withPending(`link:${row.id}`, async () => {
        try {
          const result = await ensureInventoryLink.mutateAsync(row.id)
          toast({
            title: result.created ? 'Lagerartikel angelegt' : 'Verknüpfung hergestellt',
            description: `${row.name} → Artikel ${result.article_id.slice(0, 8)}…`,
          })
        } catch (e) {
          toast({ title: 'Verknüpfung fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
        }
      }),
    [ensureInventoryLink, toast, withPending],
  )

  const unmappedLinks = useMemo(
    () => (inventoryLinks?.items ?? []).filter((r) => !r.inventory_article_id),
    [inventoryLinks],
  )

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
    () => rezepte.find((r) => r.id === rezeptId),
    [rezepte, rezeptId],
  )

  // Calculate component requirements based on selected recipe + quantity
  const komponenten: KomponentenBedarf[] = useMemo(() => {
    if (!selectedRezept || menge <= 0) return []
    return selectedRezept.komponenten.map((k) => ({
      name: k.komponente_name,
      bedarf: menge * k.anteil,
      verfuegbar: verfuegbarkeitMap[k.komponente_name] ?? 0,
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

  function handleRezeptChange(id: string) {
    setRezeptId(id)
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
    if (createAuftrag.isPending) return
    createAuftrag.mutate(
      { rezept_id: rezeptId, menge_t: menge, chargen_id: chargenId },
      {
        onSuccess: (result) => {
          toast({
            title: 'Produktionsauftrag erstellt',
            description: `Chargen-ID: ${result.chargen_id} — Lifecycle unten fortsetzen (Freigeben → Fertig).`,
          })
          setRezeptId('')
          setMenge(0)
          setChargenId('')
          setWizardKey((k) => k + 1)
        },
        onError: (e) => {
          toast({ title: 'Fehler beim Erstellen', description: getAxiosErrorMessage(e), variant: 'destructive' })
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
              value={rezeptId}
              onChange={(e) => handleRezeptChange(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              {rezepte.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.rezept_code})
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
              <CheckCircle className="h-20 w-20 text-status-success" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Produktion bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Rezeptur</dt>
                <dd className="font-semibold">{selectedRezept?.name || '-'}</dd>
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
        key={wizardKey}
        title="Mischfutter-Produktion"
        steps={steps}
        onFinish={handleFinish}
        onCancel={() => navigate('/futter/misch/liste')}
      />

      {(roleFocus === 'lager' || unmappedLinks.length > 0) ? (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Package className="h-4 w-4" />
              Lagerartikel-Verknüpfung
            </CardTitle>
            {inventoryLinks ? (
              <Badge variant={inventoryLinks.unmapped_count > 0 ? 'destructive' : 'outline'}>
                {inventoryLinks.mapped_count}/{inventoryLinks.total} verknüpft
              </Badge>
            ) : null}
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p className="text-muted-foreground">
              Bei Freigabe schreibt das System kanonische Lagerbewegungen — nur für verknüpfte Einzelfuttermittel
              (FEED-CHAIN-004).
            </p>
            {loadingLinks ? (
              <p className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Verknüpfungen laden…
              </p>
            ) : unmappedLinks.length === 0 ? (
              <p className="text-green-700">Alle aktiven Einzelfuttermittel sind mit Lagerartikeln verknüpft.</p>
            ) : (
              <ul className="space-y-2">
                {unmappedLinks.map((row) => (
                  <li key={row.id} className="flex flex-wrap items-center justify-between gap-2 rounded border px-3 py-2">
                    <div>
                      <span className="font-medium">{row.name}</span>
                      <span className="ml-2 font-mono text-xs text-muted-foreground">{row.artikel_nummer}</span>
                    </div>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={pendingActions.has(`link:${row.id}`)}
                      onClick={() => void handleEnsureLink(row)}
                    >
                      {pendingActions.has(`link:${row.id}`) ? 'Wird verknüpft…' : 'Lagerartikel verknüpfen'}
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      ) : null}

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Produktionsaufträge — Lifecycle bis zur Charge</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {auftraege.slice(0, 10).map((a) => {
            const rowPending = [...pendingActions].some((k) => k.startsWith(`${a.id}:`))
            return (
              <div key={a.id} className="flex flex-wrap items-center justify-between gap-2 rounded border px-3 py-2 text-sm">
                <div className="min-w-0">
                  <span className="font-mono font-medium">{a.chargen_id}</span>
                  <span className="ml-2 text-muted-foreground">
                    {a.rezept_name}, {a.menge_t} t
                  </span>
                  {a.charge_id ? (
                    <span className="ml-2 inline-flex items-center gap-1 text-xs text-muted-foreground">
                      <Link2 className="h-3 w-3" />
                      Charge {a.charge_id}
                    </span>
                  ) : null}
                </div>
                <div className="flex items-center gap-2">
                  {nextTransitions[a.status].map((t) => (
                    <Button
                      key={t.to}
                      type="button"
                      size="sm"
                      variant={t.destructive ? 'outline' : 'default'}
                      className={t.destructive ? 'border-destructive/40 text-destructive hover:bg-destructive/10' : undefined}
                      disabled={rowPending}
                      onClick={() => void handleStatusAction(a, t.to)}
                    >
                      {pendingActions.has(`${a.id}:${t.to}`) ? 'Wird ausgeführt…' : t.label}
                    </Button>
                  ))}
                  {a.status === 'fertig' ? (
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={rowPending}
                      onClick={() => void handleShowTrace(a)}
                    >
                      {pendingActions.has(`${a.id}:trace`) ? 'Lädt…' : 'Kette anzeigen'}
                    </Button>
                  ) : null}
                  <Badge variant={statusBadgeVariant(a.status)}>{statusLabels[a.status]}</Badge>
                </div>
              </div>
            )
          })}
          {auftraege.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Keine Produktionsaufträge — oben per Wizard anlegen (Demo-Rezept via{' '}
              <code className="rounded bg-muted px-1 text-xs">seed_demo_feed_chain.py</code>).
            </p>
          ) : null}
        </CardContent>
      </Card>

      {trace ? (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base">
              Belegkette {trace.auftrag.chargen_id}
              <Badge className="ml-2" variant={trace.kette_geschlossen ? 'outline' : 'destructive'}>
                {trace.kette_geschlossen ? 'Kette geschlossen' : 'Charge fehlt'}
              </Badge>
            </CardTitle>
            <Button type="button" size="sm" variant="ghost" onClick={() => setTrace(null)}>
              Schließen
            </Button>
          </CardHeader>
          <CardContent className="grid gap-4 text-sm md:grid-cols-2">
            <div className="space-y-1">
              <p className="font-medium">Auftrag</p>
              <p className="text-muted-foreground">
                {trace.auftrag.rezept_name}, {trace.auftrag.menge_t} t — Status {trace.auftrag.status}
              </p>
              {trace.charge ? (
                <>
                  <p className="mt-2 font-medium">Fertigwaren-Charge</p>
                  <p className="text-muted-foreground">
                    {trace.charge.id} · {trace.charge.lagerort} · QS: {trace.charge.qualitaetsstatus}
                  </p>
                </>
              ) : null}
            </div>
            <div>
              <p className="font-medium">Komponenten (Mischprotokoll)</p>
              <ul className="mt-1 space-y-1">
                {trace.komponenten.map((k, i) => (
                  <li key={i} className="flex justify-between text-muted-foreground">
                    <span>{k.name}</span>
                    <span className="font-mono">{k.menge_t.toFixed(3)} t</span>
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
