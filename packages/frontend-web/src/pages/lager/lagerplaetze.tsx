import { useSearchParams } from '@/app/routing/typed-router'
import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { AlertTriangle, MapPin, Package, Warehouse } from 'lucide-react'
import { useWarehouses } from '@/lib/api/inventory'
import { getAxiosErrorMessage } from '@/lib/api-client'
import {
  usePatchWmsBin,
  useWmsAislesForZones,
  useWmsBins,
  useWmsZones,
  wmsStr,
  type WmsBinPatch,
  type WmsRow,
} from '@/lib/api/warehouse-wms'
import { useToast } from '@/hooks/use-toast'
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

function LagerstrukturWmsPanel(props: {
  warehouses: Array<{ id: string; name: string; code: string }>
}): JSX.Element {
  const { warehouses } = props
  const { toast } = useToast()
  const patchBin = usePatchWmsBin()
  const [warehouseId, setWarehouseId] = useState('')
  const [editBin, setEditBin] = useState<WmsRow | null>(null)
  const [capInput, setCapInput] = useState('')
  const [blocked, setBlocked] = useState(false)
  const [blockReason, setBlockReason] = useState('')

  const zonesQ = useWmsZones(warehouseId || undefined, { enabled: Boolean(warehouseId) })
  const binsQ = useWmsBins({ warehouse_id: warehouseId || undefined }, { enabled: Boolean(warehouseId) })
  const zones = zonesQ.data ?? []
  const zoneIds = useMemo(() => zones.map((z) => wmsStr(z, 'id')).filter(Boolean), [zones])
  const aislesQueries = useWmsAislesForZones(zoneIds, Boolean(warehouseId))

  function openBinEditor(bin: WmsRow): void {
    setEditBin(bin)
    setCapInput(wmsStr(bin, 'capacity_kg'))
    const ib = bin.is_blocked
    setBlocked(ib === true || String(ib) === 'true')
    setBlockReason(wmsStr(bin, 'block_reason'))
  }

  async function handleSaveBin(): Promise<void> {
    if (!editBin) return
    const id = wmsStr(editBin, 'id')
    const patch: WmsBinPatch = { is_blocked: blocked }
    const trimmed = capInput.trim()
    if (trimmed !== '') {
      const n = Number(trimmed.replace(',', '.'))
      if (!Number.isFinite(n) || n < 0) {
        toast({ title: 'Ungültige Kapazität', description: 'Bitte eine nicht-negative Zahl (kg) eingeben.', variant: 'destructive' })
        return
      }
      patch.capacity_kg = n
    }
    if (!blocked) {
      patch.block_reason = null
    } else if (blockReason.trim() !== '') {
      patch.block_reason = blockReason.trim()
    }
    try {
      await patchBin.mutateAsync({ binId: id, body: patch })
      toast({ title: 'Lagerplatz aktualisiert' })
      setEditBin(null)
    } catch (e) {
      toast({ title: 'Speichern fehlgeschlagen', description: getAxiosErrorMessage(e), variant: 'destructive' })
    }
  }

  function renderBinLine(bin: WmsRow): JSX.Element {
    const cap = wmsStr(bin, 'capacity_kg')
    return (
      <li key={wmsStr(bin, 'id')} className="flex flex-wrap items-center justify-between gap-2 border-b border-border/50 py-1 last:border-0">
        <span className="font-mono text-sm">{wmsStr(bin, 'bin_code')}</span>
        <span className="text-xs text-muted-foreground">{cap ? `max. ${cap} kg` : 'keine Kap.-Angabe'}</span>
        <Button type="button" variant="outline" size="sm" onClick={() => openBinEditor(bin)}>
          Bearbeiten
        </Button>
      </li>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">WMS-Lagerstruktur (Zone → Gang → Fach)</CardTitle>
        <p className="text-sm text-muted-foreground">
          Daten aus <code className="rounded bg-muted px-1">/api/v1/lager/wms</code> — nach Migration WM-STRUCT-001
          inkl. Gänge; Lagerplatz-Metadaten per PATCH (Kapazität, Sperre).
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="max-w-md space-y-2">
          <label htmlFor="wms-warehouse-select" className="text-sm font-medium">
            Lager
          </label>
          <select
            id="wms-warehouse-select"
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm focus-visible:outline-hidden focus-visible:ring-1 focus-visible:ring-ring"
            value={warehouseId}
            onChange={(e) => setWarehouseId(e.target.value)}
          >
            <option value="">— Lager wählen —</option>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name || w.code || w.id}
              </option>
            ))}
          </select>
        </div>

        {warehouseId && zonesQ.isError && (
          <p className="text-sm text-destructive">Zonen konnten nicht geladen werden.</p>
        )}
        {warehouseId && binsQ.isError && (
          <p className="text-sm text-destructive">Lagerplätze konnten nicht geladen werden.</p>
        )}

        {warehouseId && zonesQ.isLoading && (
          <p className="text-sm text-muted-foreground">Lade Zonen …</p>
        )}

        {warehouseId && !zonesQ.isLoading && zones.length === 0 && !zonesQ.isError && (
          <p className="text-sm text-muted-foreground">Keine Zonen in diesem Lager erfasst.</p>
        )}

        {warehouseId && zones.length > 0 && (
          <div className="space-y-2">
            {zones.map((zone, i) => {
              const zid = wmsStr(zone, 'id')
              const aisles = aislesQueries[i]?.data ?? []
              const aislesLoading = aislesQueries[i]?.isLoading
              const bins = (binsQ.data ?? []).filter((b) => wmsStr(b, 'zone_id') === zid)
              return (
                <details key={zid} className="rounded-lg border p-3">
                  <summary className="cursor-pointer font-medium">
                    {wmsStr(zone, 'zone_code')} — {wmsStr(zone, 'name')}
                    <span className="ml-2 text-sm font-normal text-muted-foreground">
                      {aislesLoading ? '…' : `${aisles.length} Gänge`}, {bins.length} Fächer
                    </span>
                  </summary>
                  <div className="mt-3 space-y-3 border-t pt-3">
                    {aisles.map((a) => {
                      const aid = wmsStr(a, 'id')
                      const binsHere = bins.filter((b) => wmsStr(b, 'aisle_id') === aid)
                      return (
                        <div key={aid} className="ml-2">
                          <div className="text-sm font-semibold">
                            Gang {wmsStr(a, 'aisle_code')}
                            {wmsStr(a, 'name') ? ` (${wmsStr(a, 'name')})` : ''}
                          </div>
                          {binsHere.length === 0 ? (
                            <p className="text-xs text-muted-foreground">Keine Fächer zugeordnet.</p>
                          ) : (
                            <ul className="mt-1 space-y-0">{binsHere.map((bin) => renderBinLine(bin))}</ul>
                          )}
                        </div>
                      )
                    })}
                    {(() => {
                      const orphan = bins.filter((b) => !wmsStr(b, 'aisle_id'))
                      if (orphan.length === 0) return null
                      return (
                        <div className="ml-2">
                          <div className="text-sm font-semibold">Ohne Gang</div>
                          <ul className="mt-1 space-y-0">{orphan.map((bin) => renderBinLine(bin))}</ul>
                        </div>
                      )
                    })()}
                  </div>
                </details>
              )
            })}
          </div>
        )}

        <Dialog
          open={editBin !== null}
          onOpenChange={(open) => {
            if (!open) setEditBin(null)
          }}
        >
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Lagerplatz bearbeiten</DialogTitle>
              <DialogDescription>
                {editBin ? `${wmsStr(editBin, 'bin_code')} (${wmsStr(editBin, 'id').slice(0, 8)}…)` : ''}
              </DialogDescription>
            </DialogHeader>
            {editBin && (
              <div className="grid gap-4 py-2">
                <div className="grid gap-2">
                  <Label htmlFor="wms-bin-cap">Kapazität (kg, optional)</Label>
                  <Input
                    id="wms-bin-cap"
                    inputMode="decimal"
                    value={capInput}
                    onChange={(e) => setCapInput(e.target.value)}
                    placeholder="z. B. 25000"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="wms-bin-blocked"
                    checked={blocked}
                    onCheckedChange={(c) => setBlocked(c === true)}
                  />
                  <Label htmlFor="wms-bin-blocked" className="text-sm font-normal leading-none">
                    Lagerplatz gesperrt
                  </Label>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="wms-bin-block-reason">Sperrgrund (optional)</Label>
                  <Input
                    id="wms-bin-block-reason"
                    value={blockReason}
                    onChange={(e) => setBlockReason(e.target.value)}
                    disabled={!blocked}
                    placeholder="Kurztext bei Sperre"
                  />
                </div>
              </div>
            )}
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setEditBin(null)} disabled={patchBin.isPending}>
                Abbrechen
              </Button>
              <Button type="button" onClick={() => void handleSaveBin()} disabled={patchBin.isPending || !editBin}>
                {patchBin.isPending ? 'Speichern…' : 'Speichern'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  )
}

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
          <LagerstrukturWmsPanel
            warehouses={items.map((w) => ({ id: w.id, name: w.name, code: w.code }))}
          />
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
