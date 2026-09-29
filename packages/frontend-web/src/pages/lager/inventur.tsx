import { useMemo, useRef, useState } from 'react'
import { useSearchParams } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { CheckCircle, ClipboardList, Search, Trash2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useInventur, useCompleteInventurPositions, useStornierenInventurPosition, type InventurPosition } from '@/lib/api/inventory'

export default function InventurPage(): JSX.Element {
  const [searchParams] = useSearchParams()
  const isTouch = useTouchDevice()
  const workflowInstanceId = searchParams.get('workflowInstanceId')
  const workflowProcess = searchParams.get('workflowProcess')
  const workflowCase = searchParams.get('workflowCase')
  const [searchTerm, setSearchTerm] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const { toast } = useToast()
  const searchRef = useRef<HTMLInputElement | null>(null)

  const { data, isLoading } = useInventur({ search: searchTerm || undefined })
  const completeMutation = useCompleteInventurPositions()
  const stornierenMutation = useStornierenInventurPosition()
  const positionen = data?.items ?? []
  const stornierenPendingId = stornierenMutation.variables

  const persistComplete = async () => {
    const ids = Array.from(selected)
    if (ids.length === 0) return
    await completeMutation.mutateAsync(ids)
    setSelected(new Set())
    toast({ title: 'Abgeschlossen', description: `${ids.length} Position(en) abgeschlossen.` })
  }

  const handleComplete = async () => {
    if (completeMutation.isPending || selected.size === 0) return
    try {
      await persistComplete()
    } catch {
      toast({ title: 'Fehler', description: 'Positionen konnten nicht abgeschlossen werden.', variant: 'destructive' })
    }
  }

  const handleStorno = async (id: string) => {
    if (stornierenMutation.isPending) return
    if (!confirm('Diese Inventur-Position wirklich stornieren/entfernen?')) return
    try {
      await stornierenMutation.mutateAsync(id)
      toast({ title: 'Position storniert' })
    } catch {
      toast({ variant: 'destructive', title: 'Stornieren fehlgeschlagen' })
    }
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => { if (selected.size > 0) void handleComplete() },
    onSearch: () => searchRef.current?.focus(),
    isSaveDisabled: selected.size === 0 || completeMutation.isPending,
  })
  useKeyboardShortcuts(shortcuts)

  const fallkopf = useMemo(() => {
    const offen = positionen.filter((p) => p.status === 'offen').length
    const mitDifferenz = positionen.filter((p) => p.differenz !== 0).length
    const total = positionen.length
    return {
      status: offen > 0 ? `${offen} Positionen offen` : total > 0 ? 'Alle Positionen gezählt' : 'Keine Positionen',
      statusColor: offen > 0
        ? 'text-status-warning border-status-warning/40 bg-status-warning/10'
        : 'text-status-success border-status-success/40 bg-status-success/10',
      differenzdruck: mitDifferenz > 0 ? `${mitDifferenz} Position(en) mit Abweichung` : 'Keine Differenzen',
      owner: 'Lagerleitung',
      naechsteAktion: offen > 0 ? 'Offene Positionen zählen und abschließen' : mitDifferenz > 0 ? 'Differenzen klären' : 'Inventur abgeschlossen',
    }
  }, [positionen])

  const columns = [
    {
      key: 'select' as const,
      label: '',
      render: (pos: InventurPosition) => (
        <label className="flex min-h-touch min-w-touch cursor-pointer items-center justify-center">
          <input
            type="checkbox"
            aria-label={`${pos.artikel} auswählen`}
            checked={selected.has(pos.id)}
            onChange={() => {
              const newSet = new Set(selected)
              if (newSet.has(pos.id)) newSet.delete(pos.id)
              else newSet.add(pos.id)
              setSelected(newSet)
            }}
            className="h-5 w-5"
          />
        </label>
      ),
    },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'lagerort' as const, label: 'Lagerort' },
    { key: 'sollBestand' as const, label: 'Soll (t)' },
    { key: 'istBestand' as const, label: 'Ist (t)' },
    {
      key: 'differenz' as const,
      label: 'Differenz',
      render: (pos: InventurPosition) => (
        <span className={pos.differenz !== 0 ? 'font-semibold text-status-warning' : ''}>
          {pos.differenz > 0 ? '+' : ''}{pos.differenz} t
        </span>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (pos: InventurPosition) => (
        <Badge variant={pos.status === 'abgeschlossen' ? 'outline' : 'default'}>
          {pos.status === 'offen' ? 'Offen' : pos.status === 'gezaehlt' ? 'Gezählt' : 'Abgeschlossen'}
        </Badge>
      ),
    },
    {
      key: 'aktionen' as const,
      label: '',
      render: (pos: InventurPosition) => (
        <Button
          variant="ghost"
          className="min-h-touch min-w-touch touch-manipulation"
          title="Position stornieren"
          onClick={() => { void handleStorno(pos.id) }}
          disabled={stornierenMutation.isPending && stornierenPendingId === pos.id}
        >
          <Trash2 className="h-4 w-4 text-destructive" />
          <span className="sr-only">Position stornieren</span>
        </Button>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-4 w-48" />
          </div>
          <Skeleton className="h-11 w-48" />
        </div>
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-3 md:p-6">
      {workflowInstanceId && !isTouch ? (
        <div className="mb-4 rounded-md border border-border bg-muted px-4 py-2 text-sm text-foreground">
          Vorgang: {workflowCase || workflowProcess}
        </div>
      ) : null}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Inventur</h1>
          <p className="text-muted-foreground">Stichtagsinventur {new Date().getFullYear()} — zählen, abschließen, Differenzen klären</p>
        </div>
        <Button
          className="min-h-touch touch-manipulation"
          disabled={selected.size === 0 || completeMutation.isPending}
          onClick={() => { void handleComplete() }}
        >
          <CheckCircle className="h-4 w-4 mr-2" />
          {selected.size} Position(en) abschließen
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              ref={searchRef}
              aria-label="Suche Inventurpositionen"
              placeholder="Artikel oder Lagerort suchen"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="min-h-touch pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={positionen} columns={columns} />
        </CardContent>
      </Card>

      {!isTouch ? (
      <Card className={`border ${fallkopf.statusColor}`}>
        <CardContent className="pt-4 pb-3 text-sm space-y-1">
          <div className="font-semibold">Inventur-Status: {fallkopf.status}</div>
          <div>Differenzdruck: {fallkopf.differenzdruck}</div>
          <div>Owner: {fallkopf.owner}</div>
          <div>Nächste Inventuraktion: {fallkopf.naechsteAktion}</div>
        </CardContent>
      </Card>
      ) : null}

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Positionen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5" />
              <span className="text-2xl font-bold">{positionen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{positionen.filter((p) => p.status === 'offen').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{positionen.filter((p) => p.status === 'abgeschlossen').length}</span>
          </CardContent>
        </Card>
      </div>
      ) : null}
    </div>
      {!isTouch ? <KeyboardShortcutBar shortcuts={shortcuts} /> : null}
    </div>
  )
}
