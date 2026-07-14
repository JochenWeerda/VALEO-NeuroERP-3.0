/**
 * Kundenportal — Interessenten-Onboarding / Selbstregistrierung
 *
 * Öffentliche Seite (kein Login nötig).
 * Nach Absenden: Status INTERESSENT, Innendienst sieht die Anfrage.
 *
 * API: POST /portal/interessenten
 */

import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { CheckCircle2, Wheat, Tractor, TrendingUp, Users, Leaf } from 'lucide-react'

const BETRIEB_TYPEN = [
  { value: 'ackerbau', label: 'Ackerbau' },
  { value: 'gemischt', label: 'Gemischter Betrieb' },
  { value: 'viehhaltung', label: 'Viehhaltung' },
  { value: 'sonderkulturen', label: 'Sonderkulturen' },
  { value: 'lohnunternehmen', label: 'Lohnunternehmen' },
  { value: 'haendler', label: 'Händler / Aufkäufer' },
  { value: 'sonstige', label: 'Sonstige' },
]

const INTERESSE_THEMEN = [
  { value: 'Getreidehandel / Kontrakte', label: 'Getreideankauf & Kontrakte' },
  { value: 'Lohnspritz', label: 'Lohnspritzen' },
  { value: 'Mahl und Misch', label: 'Mahl- und Mischwagen (TMR)' },
  { value: 'Saatgut', label: 'Saatgut' },
  { value: 'Dünger', label: 'Düngemittel' },
  { value: 'PSM', label: 'Pflanzenschutz' },
  { value: 'Lohnmahlen', label: 'Lohnmahlen' },
  { value: 'Rationskalkulation', label: 'Rationskalkulation' },
  { value: 'Feldbuch', label: 'Digitale Schlagkartei' },
]

const VORTEILE = [
  { icon: <TrendingUp className="h-5 w-5 text-status-success" />, text: 'Tagesaktuelle Getreidepreise in allen Varianten' },
  { icon: <Tractor className="h-5 w-5 text-status-warning" />, text: 'Online-Buchung von Lohndienstleistungen' },
  { icon: <Wheat className="h-5 w-5 text-lime-600" />, text: 'Digitale Schlagkartei & Spritztagebuch' },
  { icon: <Leaf className="h-5 w-5 text-status-success" />, text: 'Personalisierte Ankaufs- und Kontraktangebote' },
  { icon: <Users className="h-5 w-5 text-blue-600" />, text: 'Direkter Draht zu Ihrem Berater im Innendienst' },
]

type FormState = {
  vorname: string
  nachname: string
  email: string
  telefon: string
  betrieb_name: string
  betrieb_typ: string
  flaeche_ha: string
  hauptkulturen: string
  plz: string
  ort: string
  interesse_themen: string[]
  anmerkung: string
}

const INIT: FormState = {
  vorname: '', nachname: '', email: '', telefon: '',
  betrieb_name: '', betrieb_typ: '', flaeche_ha: '',
  hauptkulturen: '', plz: '', ort: '',
  interesse_themen: [], anmerkung: '',
}

export default function OnboardingPage() {
  const { toast } = useToast()
  const [form, setForm] = useState<FormState>(INIT)
  const [saving, setSaving] = useState(false)
  const [erfolg, setErfolg] = useState(false)
  const [fehler, setFehler] = useState<string | null>(null)

  const toggleThema = (thema: string) => {
    setForm((f) => ({
      ...f,
      interesse_themen: f.interesse_themen.includes(thema)
        ? f.interesse_themen.filter((t) => t !== thema)
        : [...f.interesse_themen, thema],
    }))
  }

  const handleSubmit = async () => {
    if (saving) return
    if (!form.vorname || !form.nachname || !form.email) {
      setFehler('Bitte füllen Sie Name und E-Mail-Adresse aus.')
      return
    }
    setSaving(true)
    setFehler(null)
    try {
      await apiClient.post('/portal/interessenten', {
        ...form,
        flaeche_ha: form.flaeche_ha ? parseFloat(form.flaeche_ha) : null,
        hauptkulturen: form.hauptkulturen ? form.hauptkulturen.split(',').map((k) => k.trim()) : [],
        betrieb_typ: form.betrieb_typ || null,
      }, { headers: { 'X-Tenant-ID': 'default' } })
      setErfolg(true)
    } catch (err) {
      setFehler(getAxiosErrorMessage(err) ?? 'Registrierung fehlgeschlagen. Bitte versuchen Sie es später.')
    } finally {
      setSaving(false)
    }
  }

  if (erfolg) {
    return (
      <div className="max-w-lg mx-auto p-8 text-center space-y-4">
        <CheckCircle2 className="h-16 w-16 text-status-success mx-auto" />
        <h1 className="text-2xl font-bold text-gray-900">Vielen Dank!</h1>
        <p className="text-gray-600">
          Ihre Anfrage ist bei uns eingegangen. Unser Innendienst meldet sich in Kürze bei Ihnen.
        </p>
        <Badge className="bg-green-100 text-green-800 text-sm px-4 py-2">Registrierung erfolgreich</Badge>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Jetzt als Kunde registrieren</h1>
        <p className="text-gray-500 mt-2 max-w-xl mx-auto">
          Erhalten Sie Zugang zu aktuellen Marktpreisen, digitaler Schlagkartei und Ihrem persönlichen Beratungsportal.
        </p>
      </div>

      {/* Vorteile */}
      <div className="grid grid-cols-1 sm:grid-cols-3 md:grid-cols-5 gap-4">
        {VORTEILE.map((v, i) => (
          <div key={i} className="flex flex-col items-center text-center gap-2 p-3 rounded-lg bg-gray-50">
            {v.icon}
            <span className="text-xs text-gray-600">{v.text}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Kontaktdaten */}
        <Card>
          <CardHeader>
            <CardTitle>Kontaktdaten</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Vorname *</Label>
                <Input value={form.vorname} onChange={(e) => setForm((f) => ({ ...f, vorname: e.target.value }))} />
              </div>
              <div>
                <Label>Nachname *</Label>
                <Input value={form.nachname} onChange={(e) => setForm((f) => ({ ...f, nachname: e.target.value }))} />
              </div>
            </div>
            <div>
              <Label>E-Mail *</Label>
              <Input type="email" value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} />
            </div>
            <div>
              <Label>Telefon</Label>
              <Input type="tel" value={form.telefon} onChange={(e) => setForm((f) => ({ ...f, telefon: e.target.value }))} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>PLZ</Label>
                <Input value={form.plz} onChange={(e) => setForm((f) => ({ ...f, plz: e.target.value }))} />
              </div>
              <div>
                <Label>Ort</Label>
                <Input value={form.ort} onChange={(e) => setForm((f) => ({ ...f, ort: e.target.value }))} />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Betriebsdaten */}
        <Card>
          <CardHeader>
            <CardTitle>Betriebsdaten</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Betriebsname</Label>
              <Input placeholder="z.B. Landwirtschaft Müller GbR" value={form.betrieb_name}
                onChange={(e) => setForm((f) => ({ ...f, betrieb_name: e.target.value }))} />
            </div>
            <div>
              <Label>Betriebstyp</Label>
              <NativeSelect value={form.betrieb_typ} onChange={(e) => setForm((f) => ({ ...f, betrieb_typ: e.target.value }))}>
                <option value="">— bitte wählen —</option>
                {BETRIEB_TYPEN.map((b) => <option key={b.value} value={b.value}>{b.label}</option>)}
              </NativeSelect>
            </div>
            <div>
              <Label>Ackerfläche (ha)</Label>
              <Input type="number" placeholder="z.B. 120" value={form.flaeche_ha}
                onChange={(e) => setForm((f) => ({ ...f, flaeche_ha: e.target.value }))} />
            </div>
            <div>
              <Label>Hauptkulturen (kommagetrennt)</Label>
              <Input placeholder="z.B. Winterweizen, Raps, Gerste" value={form.hauptkulturen}
                onChange={(e) => setForm((f) => ({ ...f, hauptkulturen: e.target.value }))} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Interessengebiete */}
      <Card>
        <CardHeader>
          <CardTitle>Womit können wir Ihnen helfen?</CardTitle>
          <CardDescription>Mehrfachauswahl möglich</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {INTERESSE_THEMEN.map((t) => (
              <div key={t.value} className="flex items-center gap-2">
                <Checkbox
                  id={t.value}
                  checked={form.interesse_themen.includes(t.value)}
                  onCheckedChange={() => toggleThema(t.value)}
                />
                <Label htmlFor={t.value} className="cursor-pointer">{t.label}</Label>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <Label>Weitere Anmerkungen</Label>
            <Textarea rows={3} placeholder="Was beschäftigt Sie aktuell?" value={form.anmerkung}
              onChange={(e) => setForm((f) => ({ ...f, anmerkung: e.target.value }))} />
          </div>
        </CardContent>
      </Card>

      {fehler && (
        <Alert variant="destructive">
          <AlertTitle>Fehler</AlertTitle>
          <AlertDescription>{fehler}</AlertDescription>
        </Alert>
      )}

      <div className="flex justify-center">
        <Button size="lg" onClick={handleSubmit} disabled={saving} className="min-w-48">
          {saving ? 'Wird gesendet...' : 'Registrierung absenden'}
        </Button>
      </div>
    </div>
  )
}
