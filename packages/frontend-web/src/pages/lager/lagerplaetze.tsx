import { useSearchParams } from 'react-router-dom'
import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, MapPin, Package, Warehouse } from 'lucide-react'
import { useWarehouses } from '@/lib/api/inventory'
import { Skeleton } from '@/components/ui/skeleton'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type WarehouseRole = 'lager' | 'disposition' | 'einkauf' | 'leitung'

const warehouseRoles = [
  { id: 'lager', label: 'Lager', description: 'Prueft freie Plaetze, belegte Bereiche und kurzfristige Einlagerung.' },
  { id: 'disposition', label: 'Disposition', description: 'Klaert, ob Auslastung Lieferungen, Touren oder Umlagerungen blockiert.' },
  { id: 'einkauf', label: 'Einkauf', description: 'Sieht, ob bestellte Ware noch Lagerkapazitaet hat.' },
  { id: 'leitung', label: 'Leitung', description: 'Sieht Engpaesse, Kapazitaetsdruck und naechste Entscheidung.' },
] satisfies Array<{ id: WarehouseRole; label: string; description: string }>

export default function LagerplaetzePage(): JSX.Element {
  const [searchParams] = useSearchParams()
  const [roleFocus, setRoleFocus] = useState<WarehouseRole>('lager')
  const workflowInstanceId = searchParams.get('workflowInstanceId')
  const workflowProcess = searchParams.get('workflowProcess')
  const workflowCase = searchParams.get('workflowCase')
  const { data: warehousesData, isLoading } = useWarehouses()
  const items = warehousesData?.items ?? []
  const lager = (() => {
    const bereiche = items.map((w) => {
      const kapazitaet = w.capacity ?? 0
      const bestand = w.used_capacity ?? 0
      const auslastungPct = kapazitaet > 0 ? (bestand / kapazitaet) * 100 : 0
      return {
        name: w.name || w.code || w.id,
        plaetze: Math.max(1, Math.ceil(kapazitaet / 100)),
        belegt: Math.ceil(bestand > 0 ? Math.max(1, Math.ceil(bestand / 100)) : 0),
        kapazitaet,
        bestand,
        auslastungPct,
      }
    })
    const totalKapazitaet = bereiche.reduce((s, b) => s + b.kapazitaet, 0)
    const totalBestand = bereiche.reduce((s, b) => s + b.bestand, 0)
    const plaetze = bereiche.reduce((s, b) => s + b.plaetze, 0)
    const belegt = bereiche.reduce((s, b) => s + b.belegt, 0)
    const frei = plaetze - belegt
    const auslastung = totalKapazitaet > 0 ? (totalBestand / totalKapazitaet) * 100 : 0
    return { plaetze, belegt, frei, auslastung, bereiche }
  })()

  const kritisch = lager.bereiche.length > 0
    ? lager.bereiche.filter((b) => b.plaetze > 0 && b.belegt / b.plaetze > 0.95).length
    : 0
  const hasCapacityStopper = kritisch > 0 || lager.frei <= 0
  const nextWarehouseAction = hasCapacityStopper
    ? 'Kritische Lagerbereiche pruefen und Umlagerung oder Annahmestopp entscheiden.'
    : lager.bereiche.length === 0
      ? 'Ersten Lagerbereich in den Stammdaten anlegen.'
      : 'Freie Kapazitaet beobachten und naechste Einlagerung planen.'

  return (
    <div className="space-y-6 p-6">
      {workflowInstanceId && (
        <div className="mb-4 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200">
          Flow-Spine: {workflowCase || workflowProcess} (Instanz {workflowInstanceId.slice(0, 8)}...)
        </div>
      )}
      <div>
        <h1 className="text-3xl font-bold">Lagerplätze</h1>
        <p className="text-muted-foreground">Lagerverwaltung & Auslastung</p>
      </div>

      {!isLoading && (
        <>
          <RoleFocusBar roles={warehouseRoles} value={roleFocus} onChange={setRoleFocus} visibleCount={lager.bereiche.length} totalCount={lager.bereiche.length} title="Wer klaert die Lagerkapazitaet?" />
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
            <ManagementDecisionPanel
              decision={{
                allowed: !hasCapacityStopper && lager.bereiche.length > 0,
                allowedLabel: 'Kapazitaet verfuegbar',
                blockedLabel: 'Lagerengpass pruefen',
                summary: hasCapacityStopper
                  ? `${kritisch} Lagerbereich(e) sind kritisch ausgelastet oder es gibt keine freien Plaetze. Einlagerung braucht eine bewusste Entscheidung.`
                  : `${lager.frei} Lagerplatz/-plaetze sind frei. Einlagerung kann geplant werden.`,
                blockerCount: hasCapacityStopper ? Math.max(1, kritisch) : 0,
                nextFocus: nextWarehouseAction,
                template: { label: 'Lagerkapazitaets- und Umlagerungsprotokoll', href: '/docs/lager/lagerkapazitaet.md' },
              }}
            />
            <div className="space-y-4">
              <NextActionPanel action={nextWarehouseAction} tone={hasCapacityStopper ? 'amber' : 'emerald'} />
              <EvidenceTemplateLink link={{ label: 'Kapazitaetsnachweis ablegen', href: '/docs/lager/kapazitaetsnachweis.md' }} />
            </div>
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <OperationalTaskPlan
              title="Kapazitaetsplan"
              items={[
                { label: 'Lagerbereiche laden', done: lager.bereiche.length > 0, hint: `${lager.bereiche.length} Bereich(e) in der aktuellen Sicht.` },
                { label: 'Freie Plaetze pruefen', done: lager.frei > 0, hint: `${lager.frei} frei, ${lager.belegt} belegt.` },
                { label: 'Kritische Bereiche klaeren', done: kritisch === 0, hint: kritisch > 0 ? `${kritisch} Bereich(e) ueber 95 Prozent.` : 'Keine kritische Auslastung.' },
                { label: 'Naechste Einlagerung planen', done: !hasCapacityStopper && lager.bereiche.length > 0, hint: nextWarehouseAction },
              ]}
            />
            <CrudCapabilityChecklist
              capabilities={[
                { key: 'read', label: 'Kapazitaet lesen', available: true, hint: 'Bereiche, Plaetze, Bestand und Auslastung sind sichtbar.' },
                { key: 'create', label: 'Lagerplatz anlegen', available: false, hint: 'Anlage erfolgt laut Hinweis in den Lager-Stammdaten.' },
                { key: 'update', label: 'Umlagerung planen', available: false, hint: 'Diese Seite zeigt Engpaesse; Umlagerung erfolgt in Bewegungsprozessen.' },
                { key: 'evidence', label: 'Nachweis', available: true, hint: 'Kapazitaetsnachweis ist verlinkt.' },
                { key: 'audit', label: 'Auslastung nachvollziehen', available: true, hint: 'Bestand und Auslastung je Bereich bilden den Mindestnachweis.' },
              ]}
            />
          </div>
        </>
      )}

      {isLoading && (
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      )}

      {!isLoading && lager.bereiche.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">Keine Lagerbereiche erfasst. Erfassen Sie Lagerplätze unter Lager &gt; Stammdaten.</p>
          </CardContent>
        </Card>
      )}

      {kritisch > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{kritisch} Lagerbereich(e) über 95% ausgelastet!</span>
            </div>
          </CardContent>
        </Card>
      )}

      {!isLoading && (
      <>
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lagerplätze Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{lager.plaetze}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Belegt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{lager.belegt}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Frei</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{lager.frei}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auslastung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{lager.auslastung}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Warehouse className="h-5 w-5" />
            Lagerbereiche
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {lager.bereiche.map((bereich, i) => {
              const auslastung = bereich.plaetze > 0 ? (bereich.belegt / bereich.plaetze) * 100 : 0
              const fuellstand = (bereich.kapazitaet ?? 0) > 0 ? ((bereich.bestand ?? 0) / (bereich.kapazitaet ?? 1)) * 100 : 0
              return (
                <div key={i} className="rounded-lg border p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-semibold text-lg">{bereich.name}</div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">
                        {`${bereich.belegt} / ${bereich.plaetze} Plätze`}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {`${bereich.bestand} / ${bereich.kapazitaet} t`}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm w-24">Plätze:</span>
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full ${auslastung > 95 ? 'bg-red-600' : auslastung > 80 ? 'bg-orange-600' : 'bg-green-600'}`}
                          style={{ width: `${auslastung}%` }}
                        />
                      </div>
                      <Badge variant={auslastung > 95 ? 'destructive' : 'outline'}>
                        {`${auslastung.toFixed(0)}%`}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm w-24">Füllstand:</span>
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-blue-600" style={{ width: `${fuellstand}%` }} />
                      </div>
                      <Badge variant="outline">{`${fuellstand.toFixed(0)}%`}</Badge>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
      </>
      )}
    </div>
  )
}
