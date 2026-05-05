import { useState } from 'react'
import { useNumberRanges, useConfigureNumberRange, type NumberRangeConfigPayload } from '@/lib/api/number-ranges'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { toast } from '@/hooks/use-toast'
import { Hash, Plus, AlertTriangle } from 'lucide-react'

const RANGE_TYPE_LABELS: Record<string, string> = {
  debtor_account: 'Debitorenkonto',
  creditor_account: 'Kreditorenkonto',
  partner_number: 'Partnernummer',
}

export default function NummernkreisePage() {
  const { data: ranges, isLoading } = useNumberRanges()
  const configureMutation = useConfigureNumberRange()
  const [showDialog, setShowDialog] = useState(false)
  const [form, setForm] = useState<NumberRangeConfigPayload>({
    range_type: 'debtor_account',
    prefix: '',
    start_number: 10000,
    digit_count: 5,
    reserved_prefix_digits: 1,
  })

  const handleSave = async () => {
    try {
      await configureMutation.mutateAsync(form)
      toast({ title: 'Nummernkreis gespeichert' })
      setShowDialog(false)
    } catch (err: any) {
      toast({
        title: 'Fehler',
        description: err?.response?.data?.detail || err.message,
        variant: 'destructive',
      })
    }
  }

  const openEdit = (r: typeof ranges extends (infer T)[] | undefined ? T : never) => {
    if (!r) return
    setForm({
      range_type: r.range_type,
      prefix: r.prefix,
      start_number: r.start_number,
      digit_count: r.digit_count,
      reserved_prefix_digits: r.reserved_prefix_digits,
    })
    setShowDialog(true)
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Nummernkreise</h1>
          <p className="text-sm text-muted-foreground">
            Konfiguration der automatischen Nummernvergabe fuer Debitoren-/Kreditorenkonten und Partnernummern.
          </p>
        </div>
        <Button onClick={() => { setForm({ range_type: 'debtor_account', prefix: '', start_number: 10000, digit_count: 5, reserved_prefix_digits: 1 }); setShowDialog(true) }}>
          <Plus className="mr-2 h-4 w-4" />
          Nummernkreis anlegen
        </Button>
      </div>

      <div className="rounded-lg border bg-amber-50 p-4 text-sm text-amber-800 dark:bg-amber-950/30 dark:text-amber-200">
        <div className="flex items-start gap-2">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            <strong>Wichtig:</strong> Die Stellenanzahl kann nach Ersteinrichtung nur erweitert, nie verkuerzt werden.
            Reservierte Vorziffern ermoeglichen spaetere Stammdatenuebernahme aus Altsystemen.
          </div>
        </div>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Laden...</p>}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {ranges?.map((r) => (
          <Card key={r.id} className="cursor-pointer hover:border-primary/40 transition" onClick={() => openEdit(r)}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">{RANGE_TYPE_LABELS[r.range_type] || r.range_type}</CardTitle>
                <Badge variant={r.is_active ? 'default' : 'secondary'}>
                  {r.is_active ? 'Aktiv' : 'Inaktiv'}
                </Badge>
              </div>
              <CardDescription>Typ: {r.range_type}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">Praefix</span><span className="font-medium">{r.prefix || '\u2013'}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Stellen</span><span className="font-medium">{r.digit_count}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Reserviert</span><span className="font-medium">{r.reserved_prefix_digits} Vorziffern</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Startnummer</span><span className="font-medium">{r.start_number}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Zaehlerstand</span><span className="font-medium">{r.current_value}</span></div>
              <div className="mt-3 flex items-center gap-2 rounded-lg bg-muted/50 px-3 py-2">
                <Hash className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Naechste Nr.:</span>
                <span className="font-mono font-semibold">{r.next_number || '\u2013'}</span>
              </div>
            </CardContent>
          </Card>
        ))}

        {!isLoading && (!ranges || ranges.length === 0) && (
          <Card className="col-span-full border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
              <Hash className="mb-3 h-10 w-10" />
              <p className="text-sm">Noch keine Nummernkreise konfiguriert.</p>
              <p className="text-xs">Legen Sie Nummernkreise an, damit Debitoren- und Kreditorenkonten automatisch vergeben werden.</p>
            </CardContent>
          </Card>
        )}
      </div>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nummernkreis konfigurieren</DialogTitle>
            <DialogDescription>
              Stellenanzahl kann nach Ersteinrichtung nur erweitert werden.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label>Typ</Label>
              <Select value={form.range_type} onValueChange={(v) => setForm((f) => ({ ...f, range_type: v }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="debtor_account">Debitorenkonto</SelectItem>
                  <SelectItem value="creditor_account">Kreditorenkonto</SelectItem>
                  <SelectItem value="partner_number">Partnernummer</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Praefix</Label>
                <Input
                  value={form.prefix}
                  onChange={(e) => setForm((f) => ({ ...f, prefix: e.target.value }))}
                  placeholder="z.B. D"
                  maxLength={20}
                />
              </div>
              <div className="space-y-2">
                <Label>Startnummer</Label>
                <Input
                  type="number"
                  value={form.start_number}
                  onChange={(e) => setForm((f) => ({ ...f, start_number: Number(e.target.value) }))}
                  min={1}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Stellenanzahl (max. 10)</Label>
                <Input
                  type="number"
                  value={form.digit_count}
                  onChange={(e) => setForm((f) => ({ ...f, digit_count: Math.min(10, Math.max(1, Number(e.target.value))) }))}
                  min={1}
                  max={10}
                />
              </div>
              <div className="space-y-2">
                <Label>Reservierte Vorziffern</Label>
                <Input
                  type="number"
                  value={form.reserved_prefix_digits}
                  onChange={(e) => setForm((f) => ({ ...f, reserved_prefix_digits: Math.min(3, Math.max(0, Number(e.target.value))) }))}
                  min={0}
                  max={3}
                />
              </div>
            </div>
            <div className="rounded-lg bg-muted/50 px-4 py-3 text-sm">
              <div className="text-muted-foreground">Vorschau naechste Nummer:</div>
              <div className="mt-1 font-mono text-lg font-semibold">
                {form.prefix}{String(form.start_number).padStart(form.digit_count, '0')}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>Abbrechen</Button>
            <Button onClick={handleSave} disabled={configureMutation.isPending}>
              {configureMutation.isPending ? 'Speichern...' : 'Speichern'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
