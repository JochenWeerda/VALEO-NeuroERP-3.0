import { useMemo, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ErrorState } from '@/components/ErrorState'
import { useSaveSupplierRating, useSupplierRatings, type SupplierRating } from '@/lib/api/procurement-plus'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

type SupplierRatingRoleFocus = 'all' | 'procurement' | 'quality' | 'finance' | 'management'

const supplierRatingRoleProfiles: Array<{ id: SupplierRatingRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt die Lieferantenbewertung fuer Einkauf, QS, Finance und Leitung.',
  },
  {
    id: 'procurement',
    label: 'Einkauf',
    description: 'Fokus auf Liefertreue, Service, Review und Lieferantengespraech.',
  },
  {
    id: 'quality',
    label: 'QS',
    description: 'Fokus auf Qualitaetsscore und Lieferanten mit Klaerungsbedarf.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Fokus auf Preisbewertung, Auftragsvolumen und Konditionen.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Eskalationen, Top-/Risiko-Lieferanten und naechste Aktion.',
  },
]

export default function LieferantenBewertungPage(): JSX.Element {
  const { data = [], isLoading, isError, error, refetch } = useSupplierRatings()
  const save = useSaveSupplierRating()
  const [search, setSearch] = useState('')
  const [roleFocus, setRoleFocus] = useState<SupplierRatingRoleFocus>('all')

  const filtered = useMemo(
    () => data.filter((i) => i.supplier.toLowerCase().includes(search.toLowerCase())),
    [data, search],
  )
  const averageScore = data.length > 0 ? data.reduce((sum, row) => sum + row.overallScore, 0) / data.length : 0
  const weakSuppliers = data.filter((row) => row.overallScore < 3.5)
  const criticalSuppliers = data.filter((row) => row.overallScore < 3 || row.qualityScore < 3 || row.onTimeDelivery < 80)
  const worstSupplier = [...data].sort((a, b) => a.overallScore - b.overallScore)[0]
  const hasRatingData = data.length > 0
  const hasReviewTarget = weakSuppliers.length > 0 || criticalSuppliers.length > 0
  const ratingReady = hasRatingData && criticalSuppliers.length === 0
  const nextRatingAction = !hasRatingData
    ? 'Bewertungsdaten laden oder ersten Lieferanten bewerten.'
    : criticalSuppliers.length > 0
      ? `${criticalSuppliers.length} kritische Lieferanten pruefen.`
      : weakSuppliers.length > 0
        ? `${weakSuppliers.length} Lieferanten fuer Review vormerken.`
        : 'Bewertung pruefen und naechsten Review-Termin setzen.'
  const ratingTaskItems: UxTaskItem[] = [
    {
      label: 'Datenbasis pruefen',
      done: hasRatingData,
      hint: hasRatingData ? `${data.length} Lieferantenbewertungen geladen.` : 'Noch keine Bewertungsdaten vorhanden.',
    },
    {
      label: 'Scores vergleichen',
      done: hasRatingData,
      hint: hasRatingData ? `Durchschnitt ${averageScore.toFixed(2)} von 5.` : 'Liefertreue, Qualitaet, Preis und Service laden.',
    },
    {
      label: 'Eskalationen erkennen',
      done: criticalSuppliers.length === 0 && hasRatingData,
      hint: criticalSuppliers.length > 0 ? `${criticalSuppliers.length} Lieferanten sind kritisch.` : 'Keine kritischen Lieferanten nach aktuellem Score.',
    },
    {
      label: 'Review nachhalten',
      done: !hasReviewTarget && hasRatingData,
      hint: hasReviewTarget ? 'Lieferanten mit schwachem Score fuer Review oder Gespraech vormerken.' : 'Keine offene Review-Eskalation.',
    },
  ]
  const ratingCrudCapabilities = [
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Lieferanten, Einzel-Scores, Gesamtbewertung und Auftragsanzahl sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Bewertung anpassen',
      available: filtered.length > 0,
      hint: filtered.length > 0 ? 'Gesamtscore kann kontrolliert um 0.1 angepasst werden.' : 'Keine gefilterten Lieferanten fuer Anpassung.',
    },
    {
      key: 'filter',
      label: 'Suchen/Filtern',
      available: true,
      hint: 'Lieferantensuche grenzt die Bewertungsmatrix ein.',
    },
    {
      key: 'approve',
      label: 'Review-Freigabe',
      available: ratingReady,
      hint: ratingReady ? 'Bewertung ist ohne kritische Stopper nutzbar.' : 'Kritische Lieferanten brauchen Review.',
    },
    {
      key: 'evidence',
      label: 'Nachweis',
      available: hasRatingData,
      hint: hasRatingData ? 'Scores und Auftragsanzahl bilden den Bewertungsnachweis.' : 'Nachweis entsteht mit Bewertungsdaten.',
    },
    {
      key: 'audit',
      label: 'Pruefspur',
      available: true,
      hint: 'Score-Aenderungen laufen ueber die bestehende Speicherfunktion.',
    },
  ]

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleNudgeScore = async (row: SupplierRating, delta: number) => {
    const overallScore = Math.max(1, Math.min(5, Number((row.overallScore + delta).toFixed(2))))
    await save.mutateAsync({ ...row, overallScore })
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div className="space-y-4">
        <RoleFocusBar
          roles={supplierRatingRoleProfiles}
          value={roleFocus}
          onChange={setRoleFocus}
          visibleCount={roleFocus === 'all' ? 4 : 1}
          totalCount={4}
        />
        <ManagementDecisionPanel
          decision={{
            allowed: ratingReady,
            allowedLabel: 'Bewertung akzeptabel',
            blockedLabel: 'Klaerungsbedarf',
            summary: ratingReady
              ? `Die Lieferantenbasis ist aktuell ohne kritische Stopper. Durchschnitt ${averageScore.toFixed(2)} von 5.`
              : `Vor der Nutzung fuer Einkaufsentscheidungen ist noch etwas offen: ${nextRatingAction}`,
            blockerCount: [!hasRatingData, criticalSuppliers.length > 0].filter(Boolean).length,
            nextFocus: nextRatingAction,
            template: {
              label: 'Lieferantenstamm oeffnen',
              href: '/einkauf/lieferanten',
            },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Bewertungsplan" items={ratingTaskItems} />
          <div className="space-y-3">
            <NextActionPanel
              action={worstSupplier ? `${nextRatingAction} Niedrigster Score: ${worstSupplier.supplier} (${worstSupplier.overallScore.toFixed(2)}).` : nextRatingAction}
              tone={ratingReady ? 'emerald' : criticalSuppliers.length > 0 ? 'red' : hasRatingData ? 'amber' : 'blue'}
            />
            <EvidenceTemplateLink link={{ label: 'Lieferantenakte pruefen', href: '/einkauf/lieferanten' }} />
          </div>
        </div>
        <CrudCapabilityChecklist capabilities={ratingCrudCapabilities} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lieferantenbewertung</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Lieferant suchen" />
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Lade Bewertungen ...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Lieferant</TableHead>
                  <TableHead className="text-right">Liefertreue</TableHead>
                  <TableHead className="text-right">Qualitaet</TableHead>
                  <TableHead className="text-right">Preis</TableHead>
                  <TableHead className="text-right">Service</TableHead>
                  <TableHead className="text-right">Gesamt</TableHead>
                  <TableHead className="text-right">Auftraege</TableHead>
                  <TableHead className="text-right">Aktion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((r) => (
                  <TableRow key={r.supplierId}>
                    <TableCell>{r.supplier}</TableCell>
                    <TableCell className="text-right">{r.onTimeDelivery.toFixed(1)}%</TableCell>
                    <TableCell className="text-right">{r.qualityScore.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{r.priceScore.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{r.serviceScore.toFixed(2)}</TableCell>
                    <TableCell className="text-right font-semibold">{r.overallScore.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{r.totalOrders}</TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button size="sm" variant="outline" onClick={() => { void handleNudgeScore(r, -0.1) }}>-0.1</Button>
                      <Button size="sm" onClick={() => { void handleNudgeScore(r, 0.1) }}>+0.1</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
