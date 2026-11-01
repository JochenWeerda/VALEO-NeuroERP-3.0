import { useDomainSupplyChain } from '../intake/domain-data'
import type { RenderPlan } from '../../render-plan/types'
import { canDomainAction, useDomainDispatch } from '../intake/domain-runtime'
import { useMemo, useRef, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'

import { type UxTaskItem } from '@/components/workflow'

import { useDomainScales } from './scale-data'
import { type Waage } from '@/lib/api/betrieb'

import { Button } from '@/components/ui/button'

import { useTouchDevice } from '@/hooks/useTouchDevice'

import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useToast } from '@/hooks/use-toast'

import { summarizeSupplyOps } from '@/lib/professional-control-centers'
import { summarizeSupplyTransfer } from '@/lib/domain-depth'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type ScaleListRoleFocus = 'all' | 'scale' | 'yard' | 'dispatch' | 'quality' | 'management'

const scaleListRoleProfiles: Array<{ id: ScaleListRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle Rollen', description: 'Zeigt die Waagenliste fuer Waage, Hof, Disposition, QS und Leitung.' },
  { id: 'scale', label: 'Waage', description: 'Fokus auf Waagenbestand, Status und Eichfaelligkeit.' },
  { id: 'yard', label: 'Hof', description: 'Fokus auf offene Annahmen und Waageverfuegbarkeit.' },
  { id: 'dispatch', label: 'Disposition', description: 'Fokus auf Kettenlage, Bottleneck und naechste Aktion.' },
  { id: 'quality', label: 'QS', description: 'Fokus auf Eichung, gesperrte Chargen und Prueftermine.' },
  { id: 'management', label: 'Leitung', description: 'Fokus auf Stopper, Auslastung und Exportnachweis.' },
]

export function useScalesController(plan: RenderPlan) {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const { data: chain } = useDomainSupplyChain()
  const searchInputRef = useRef<HTMLInputElement | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFocus, setRoleFocus] = useState<ScaleListRoleFocus>('all')
  const { data: waagen = [], isLoading, isError, error, refetch } = useDomainScales()
  const supplyOps = useMemo(() => summarizeSupplyOps(chain), [chain])
  const transferSummary = useMemo(() => summarizeSupplyTransfer(chain), [chain])

  const filteredWaagen = useMemo(() => {
    if (!searchTerm) return waagen
    const term = searchTerm.toLowerCase()
    return waagen.filter((w) =>
      [w.standort, w.id, w.typ]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(term)),
    )
  }, [waagen, searchTerm])

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => { if (canDomainAction(plan, 'new')) navigate('/waage/neu') },
    onSearch: () => searchInputRef.current?.focus(),
    onRefresh: () => {
      void refetch()
    },
  })
  useKeyboardShortcuts(shortcuts)

  const handleExport = (): void => {
    if (!canDomainAction(plan, 'export')) return
    const header = 'ID;Standort;Typ;Max_Kapazitaet_t;Letzte_Eichung;Naechste_Eichung;Status\n'
    const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
    const rows = filteredWaagen.map((w) =>
      [w.id, w.standort, w.typ, w.maxKapazitaet, w.letzteEichung, w.naechsteEichung, w.status].map(esc).join(';')
    ).join('\n')
    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Waagen_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredWaagen.length} Waagen exportiert.` })
  }
  const dueCalibrations = filteredWaagen.filter((w) => new Date(w.naechsteEichung) <= new Date()).length
  const activeScales = filteredWaagen.filter((w) => w.status === 'aktiv').length
  const hasScales = filteredWaagen.length > 0
  const scaleListWorkable = hasScales && dueCalibrations === 0 && supplyOps.pressure !== 'hoch'
  const scaleListNextAction = !hasScales
    ? 'Waage anlegen oder Suchfilter zuruecksetzen.'
    : dueCalibrations > 0
      ? `${dueCalibrations} faellige Eichtermine pruefen.`
      : supplyOps.pressure === 'hoch'
        ? `Bottleneck ${supplyOps.bottleneck} entlasten.`
        : supplyOps.nextAction
  const scaleListTaskItems: UxTaskItem[] = [
    { label: 'Waagenbestand pruefen', done: hasScales, hint: hasScales ? `${filteredWaagen.length} Waagen sichtbar, ${activeScales} aktiv.` : 'Keine Waage im aktuellen Filter.' },
    { label: 'Eichung klaeren', done: dueCalibrations === 0, hint: dueCalibrations > 0 ? `${dueCalibrations} Eichtermine sind faellig.` : 'Keine faellige Eichung im aktuellen Ausschnitt.' },
    { label: 'Kettenlage bewerten', done: supplyOps.pressure !== 'hoch', hint: `Druck ${supplyOps.pressure}, Bottleneck ${supplyOps.bottleneck}.` },
    { label: 'Nachweis exportieren', done: filteredWaagen.length > 0, hint: filteredWaagen.length > 0 ? 'CSV-Export ist fuer den aktuellen Ausschnitt verfuegbar.' : 'Export braucht sichtbare Waagen.' },
  ]
  const scaleListCrudCapabilities = [
    { key: 'create', label: 'Neue Waage', available: true, hint: 'Neue Waage kann über den Button angelegt werden.' },
    { key: 'read', label: 'Lesen', available: true, hint: 'Waagen, Status, Eichung und Kettenlage sind sichtbar.' },
    { key: 'filter', label: 'Suchen', available: true, hint: 'Suche filtert nach Standort, Waagen-ID oder Typ.' },
    { key: 'export', label: 'Export/Nachweis', available: filteredWaagen.length > 0, hint: filteredWaagen.length > 0 ? 'CSV-Export dokumentiert den aktuellen Stand.' : 'Kein Export ohne sichtbare Waagen.' },
    { key: 'audit', label: 'Pruefspur', available: true, hint: 'Eichstatus, Exportzeitpunkt und Kettenlage bilden die Pruefsicht.' },
  ]
  const operationalStatus = normalizeOperationalStatus(
    supplyOps.pressure === 'hoch'
      ? 'eskaliert'
      : dueCalibrations > 0
        ? 'wartet_auf_mensch'
        : filteredWaagen.length > 0
          ? 'in_pruefung'
          : 'offen',
  )
  const contextSections = [
    {
      title: 'Waagenlage',
      items: [
        { label: 'Standorte', value: `${filteredWaagen.length}` },
        { label: 'Eichung faellig', value: `${dueCalibrations}` },
        { label: 'Bottleneck', value: supplyOps.bottleneck },
      ],
    },
    {
      title: 'Physische Kette',
      items: [
        { label: 'Annahme offen', value: `${chain?.waitingInbound ?? 0}` },
        { label: 'Wiegungen offen', value: `${chain?.openWeighingTickets ?? 0}` },
        { label: 'Naechste Aktion', value: supplyOps.nextAction },
      ],
    },
  ]
  const timelineItems = [
    {
      label: supplyOps.pressure === 'hoch' ? 'Hoher physischer Druck' : 'Kettenlage stabil',
      detail: `Druck ${supplyOps.pressure}, Bottleneck ${supplyOps.bottleneck}, Fracht unterwegs ${chain?.freightInTransit ?? 0}.`,
    },
    {
      label: dueCalibrations > 0 ? 'Eichpruefung faellig' : 'Eichlage unkritisch',
      detail: dueCalibrations > 0
        ? `${dueCalibrations} Waagen sollten vor weiterer Belastung neu geprueft oder eingeplant werden.`
        : 'Im aktuellen Ausschnitt gibt es keine ueberfaelligen Eichtermine.',
    },
  ]

  useDomainDispatch(plan, { new: () => navigate('/waage/neu'), yard: () => navigate('/waage/hofliste'), export: handleExport, refresh: () => { void refetch() } })
  return { plan, navigate, isTouch, chain, searchInputRef, searchTerm, setSearchTerm, roleFocus, setRoleFocus, waagen, isLoading, isError, error, refetch, supplyOps, transferSummary, filteredWaagen, shortcuts, handleExport, dueCalibrations, activeScales, hasScales, scaleListWorkable, scaleListNextAction, scaleListTaskItems, scaleListCrudCapabilities, operationalStatus, contextSections, timelineItems }
}
export type ScalesState = ReturnType<typeof useScalesController>
