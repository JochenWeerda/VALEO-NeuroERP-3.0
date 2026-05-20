import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { useToast } from '@/hooks/use-toast'
import { useCreateErnte, useKulturen } from '@/lib/api/agrar'
import { ArrowLeft, Save, Wheat } from 'lucide-react'

export default function ErnteNeuPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { data: kulturen = [] } = useKulturen()
  const createErnte = useCreateErnte()

  const [form, setForm] = useState({
    schlag: '',
    kultur: '',
    datum: new Date().toISOString().slice(0, 10),
    menge: 0,
    ertrag: 0,
    status: 'geplant' as 'geplant' | 'laufend' | 'abgeschlossen',
  })

  const set = (field: string, value: string | number) =>
    setForm((prev) => ({ ...prev, [field]: value }))

  const valid = form.schlag.trim().length > 0 && form.kultur.trim().length > 0 && form.datum.length > 0

  const handleSave = () => {
    if (!valid) return
    createErnte.mutate(
      { ...form, menge: Number(form.menge), ertrag: Number(form.ertrag) },
      {
        onSuccess: (ernte) => {
          toast({ title: 'Ernte angelegt', description: `Schlag "${ernte.schlag}" wurde erfasst.` })
          navigate('/agrar/ernte')
        },
        onError: () => {
          toast({ title: 'Fehler', description: 'Ernte konnte nicht gespeichert werden.', variant: 'destructive' })
        },
      }
    )
  }

  const handleAnnahme = () => {
    if (!valid) return
    createErnte.mutate(
      { ...form, menge: Number(form.menge), ertrag: Number(form.ertrag) },
      {
        onSuccess: (ernte) => {
          navigate(
            `/agrar/ernte-annahme-erfassung?workflowProcess=harvest-to-settlement` +
              `&subject=${encodeURIComponent(form.kultur + ' ' + new Date(form.datum).getFullYear())}` +
              `&entryMode=Ernteannahme`
          )
        },
        onError: () => {
          toast({ title: 'Fehler', description: 'Ernte konnte nicht gespeichert werden.', variant: 'destructive' })
        },
      }
    )
  }

  return (
    <div className="space-y-4 p-6 max-w-2xl">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => navigate('/agrar/ernte')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Wheat className="h-6 w-6" />
            Neue Ernte erfassen
          </h1>
          <p className="text-muted-foreground text-sm">Grunddaten der Erntemaßnahme</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Erntedaten</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label htmlFor="schlag">Schlag / Fläche *</Label>
              <Input
                id="schlag"
                placeholder="z.B. Nordfeld 1"
                value={form.schlag}
                onChange={(e) => set('schlag', e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="kultur">Kultur / Fruchtart *</Label>
              {kulturen.length > 0 ? (
                <NativeSelect
                  id="kultur"
                  value={form.kultur}
                  onChange={(e) => set('kultur', e.target.value)}
                >
                  <option value="">Bitte wählen...</option>
                  {kulturen.map((k: { name: string }) => (
                    <option key={k.name} value={k.name}>{k.name}</option>
                  ))}
                </NativeSelect>
              ) : (
                <Input
                  id="kultur"
                  placeholder="z.B. Winterweizen"
                  value={form.kultur}
                  onChange={(e) => set('kultur', e.target.value)}
                />
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label htmlFor="datum">Erntedatum *</Label>
              <Input
                id="datum"
                type="date"
                value={form.datum}
                onChange={(e) => set('datum', e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="status">Status</Label>
              <NativeSelect
                id="status"
                value={form.status}
                onChange={(e) => set('status', e.target.value)}
              >
                <option value="geplant">Geplant</option>
                <option value="laufend">Laufend</option>
                <option value="abgeschlossen">Abgeschlossen</option>
              </NativeSelect>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label htmlFor="menge">Erntemenge (t)</Label>
              <Input
                id="menge"
                type="number"
                min={0}
                step={0.1}
                value={form.menge}
                onChange={(e) => set('menge', e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="ertrag">Ertrag (dt/ha)</Label>
              <Input
                id="ertrag"
                type="number"
                min={0}
                step={0.1}
                value={form.ertrag}
                onChange={(e) => set('ertrag', e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-3 justify-end">
        <Button variant="outline" onClick={() => navigate('/agrar/ernte')}>
          Abbrechen
        </Button>
        <Button
          variant="outline"
          onClick={handleSave}
          disabled={!valid || createErnte.isPending}
        >
          <Save className="h-4 w-4 mr-2" />
          Speichern
        </Button>
        <Button
          onClick={handleAnnahme}
          disabled={!valid || createErnte.isPending}
        >
          <Wheat className="h-4 w-4 mr-2" />
          Speichern & Annahme starten
        </Button>
      </div>
    </div>
  )
}
