import { useDomainQueue, useDomainSupplyChain } from './domain-data'
import type { RenderPlan } from '../../render-plan/types'
import { canDomainAction, useDomainDispatch } from './domain-runtime'
import { useMemo, useRef, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { useRepairWarteschlangeArticle, type LKWEintrag } from '@/lib/api/inventory'

import { summarizeSupplyOps } from '@/lib/professional-control-centers'
import { normalizeOperationalStatus } from '@/lib/operational-status'

export function useQueueController(plan: RenderPlan) {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const searchInputRef = useRef<HTMLInputElement | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const { data, isLoading, isError, error, refetch } = useDomainQueue()
  const { data: chain } = useDomainSupplyChain()
  const supplyOps = useMemo(() => summarizeSupplyOps(chain), [chain])
  const repairArticle = useRepairWarteschlangeArticle()
  const warteschlange = useMemo(() => {
    const items = data?.items ?? []
    if (!searchTerm.trim()) {
      return items
    }
    const term = searchTerm.trim().toLowerCase()
    return items.filter((entry) =>
      [entry.kennzeichen, entry.lieferant, entry.artikel, entry.lieferschein_nr]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(term)),
    )
  }, [data?.items, searchTerm])

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => { if (canDomainAction(plan, 'new')) navigate('/annahme/lkw-registrierung') },
    onSearch: () => searchInputRef.current?.focus(),
    onRefresh: () => {
      void refetch()
    },
  })
  useKeyboardShortcuts(shortcuts)

  const openHarvestAcceptance = (entry: LKWEintrag): void => {
    if (!canDomainAction(plan, 'harvest')) return
    const searchParams = new URLSearchParams({
      workflowProcess: 'harvest-to-settlement',
      workflowLabel: `queue-entry:${entry.id}`,
      entryMode: 'Warteschlange',
    })
    if (entry.lieferant) searchParams.set('partnerName', entry.lieferant)
    if (entry.lieferschein_nr) searchParams.set('lieferscheinNr', entry.lieferschein_nr)
    if (entry.kennzeichen) searchParams.set('vehiclePlate', entry.kennzeichen)
    if (entry.article_id) searchParams.set('articleId', entry.article_id)
    if (entry.artikel) {
      searchParams.set('articleName', entry.artikel)
      searchParams.set('subject', `${entry.artikel} / Queue`)
    }
    searchParams.set('queueEntryId', entry.id)
    navigate(`/agrar/ernte-annahme-erfassung?${searchParams.toString()}`)
  }

  const openKlaerung = (entry: LKWEintrag): void => {
    if (!canDomainAction(plan, 'clarify')) return
    const searchParams = new URLSearchParams({
      queueEntryId: entry.id,
    })
    navigate(`/annahme/klaerung-gesperrt?${searchParams.toString()}`)
  }

  const openQuality = (entry: LKWEintrag): void => { if (canDomainAction(plan, 'quality')) navigate('/annahme/qualitaets-check', { state: { eintragId: entry.id } }) }
  const repair = (entry: LKWEintrag): void => {
    if (!canDomainAction(plan, 'repair')) return
    repairArticle.mutate(entry.id, {
      onSuccess: (result) => {
        if (result.status === 'updated') {
          toast({ title: 'Artikel repariert', description: result.artikel || entry.artikel })
          return
        }
        toast({ title: 'Repair nicht moeglich', description: result.reason || 'Kein eindeutiger Treffer', variant: 'destructive' })
      },
      onError: () => toast({ title: 'Repair fehlgeschlagen', variant: 'destructive' }),
    })
  }

  const wartend = warteschlange.filter(l => l.status === 'wartend').length
  const inBearbeitung = warteschlange.filter(l => l.status === 'in-bearbeitung').length
  const abgeschlossen = warteschlange.filter(l => l.status === 'abgeschlossen').length
  const avgWartezeit = warteschlange.length > 0
    ? Math.round(warteschlange.reduce((sum, l) => sum + l.wartezeit, 0) / warteschlange.length)
    : 0
  const operationalStatus = normalizeOperationalStatus(
    warteschlange.some((entry) => entry.status === 'gesperrt')
      ? 'eskaliert'
      : wartend > 0
        ? 'wartet_auf_mensch'
        : inBearbeitung > 0
          ? 'in_pruefung'
          : 'abgeschlossen',
  )
  const contextSections = [
    {
      title: 'Queue-Kontext',
      items: [
        { label: 'Wartend', value: `${wartend}` },
        { label: 'In Bearbeitung', value: `${inBearbeitung}` },
        { label: 'Abgeschlossen', value: `${abgeschlossen}` },
      ],
    },
    {
      title: 'Objektkette',
      items: [
        { label: 'Offene Wiegungen', value: chain ? `${chain.openWeighingTickets ?? 0}` : 'Nicht verfügbar' },
        { label: 'Gesperrte Chargen', value: chain ? `${chain.blockedCharges ?? 0}` : 'Nicht verfügbar' },
        { label: 'Fracht unterwegs', value: chain ? `${chain.freightInTransit ?? 0}` : 'Nicht verfügbar' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: wartend > 0 ? 'Queue unter Last' : 'Keine wartenden Fahrzeuge',
      detail: wartend > 0
        ? `${wartend} Fahrzeuge warten aktuell auf den naechsten Schritt.`
        : 'Die Annahmewarteschlange ist derzeit frei.',
    },
    {
      label: chain ? (supplyOps.bottleneck ? `Bottleneck ${supplyOps.bottleneck}` : 'Kein dominanter Bottleneck') : 'Lieferkettenstatus nicht verfügbar',
      detail: chain ? supplyOps.nextAction : 'Lieferkettendaten konnten nicht geladen werden.',
    },
  ]

  useDomainDispatch(plan, { new: () => navigate('/annahme/lkw-registrierung'), qr: () => navigate('/annahme/qr'), refresh: () => { void refetch() }, quality: payload => { const entry = warteschlange.find(row => row.id === payload.id); if (entry) openQuality(entry) }, repair: payload => { const entry = warteschlange.find(row => row.id === payload.id); if (entry) repair(entry) } })
  return { plan, navigate, isTouch, chain, supplyOps, searchInputRef, searchTerm, setSearchTerm, isLoading, isError, error, refetch, repair, openQuality, warteschlange, shortcuts, openHarvestAcceptance, openKlaerung, wartend, inBearbeitung, abgeschlossen, avgWartezeit, operationalStatus, contextSections, timelineItems }
}
export type QueueState = ReturnType<typeof useQueueController>
