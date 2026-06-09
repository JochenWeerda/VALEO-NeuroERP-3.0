import { useEffect, useState } from 'react'
import { Link } from '@/app/routing/typed-router'
import { ArrowLeft, Cable, CheckCircle2, XCircle, Loader2, Mail, Mic, DownloadCloud } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useToast } from '@/hooks/use-toast'
import {
  useConnectors,
  useUpdateConnectors,
  useTestConnectorStt,
  useTestConnectorImap,
  usePollConnectorImap,
} from '@/lib/api/admin-suite'

/**
 * Admin-Maske für die Auto-Capture-Connectoren (STT + IMAP) — per Tenant statt ENV,
 * analog zur KI-Anbieter-Wahl. Secrets werden nie ausgegeben (nur *_set-Flags);
 * leer lassen behält den gespeicherten Wert.
 * Backend: /api/v1/admin-suite/capture-connectors (admin_suite.py).
 */
export default function AdminSuiteConnectorenPage(): JSX.Element {
  const query = useConnectors()
  const update = useUpdateConnectors()
  const testStt = useTestConnectorStt()
  const testImap = useTestConnectorImap()
  const pollImap = usePollConnectorImap()
  const { toast } = useToast()

  // STT-Formular
  const [sttEnabled, setSttEnabled] = useState(true)
  const [sttBaseUrl, setSttBaseUrl] = useState('')
  const [sttModel, setSttModel] = useState('')
  const [sttLanguage, setSttLanguage] = useState('de')
  const [sttApiKey, setSttApiKey] = useState('')

  // IMAP-Formular
  const [imapEnabled, setImapEnabled] = useState(false)
  const [imapHost, setImapHost] = useState('')
  const [imapPort, setImapPort] = useState('993')
  const [imapSsl, setImapSsl] = useState(true)
  const [imapUser, setImapUser] = useState('')
  const [imapPassword, setImapPassword] = useState('')
  const [imapInbox, setImapInbox] = useState('INBOX')
  const [imapSent, setImapSent] = useState('')
  const [imapOwn, setImapOwn] = useState('')
  const [imapPoll, setImapPoll] = useState('60')

  useEffect(() => {
    if (!query.data) return
    const { stt, imap } = query.data
    setSttEnabled(stt.enabled); setSttBaseUrl(stt.base_url); setSttModel(stt.model); setSttLanguage(stt.language)
    setImapEnabled(imap.enabled); setImapHost(imap.host); setImapPort(String(imap.port)); setImapSsl(imap.ssl)
    setImapUser(imap.user); setImapInbox(imap.inbox); setImapSent(imap.sent); setImapOwn(imap.own_addresses)
    setImapPoll(String(imap.poll_seconds))
  }, [query.data])

  if (query.isLoading) return <LoadingState message="Connector-Konfiguration wird geladen..." />
  if (query.isError || !query.data) {
    return <ErrorState error={query.error instanceof Error ? query.error : null} onRetry={() => void query.refetch()} />
  }
  const { stt, imap } = query.data

  const saveStt = async () => {
    try {
      await update.mutateAsync({
        stt: { enabled: sttEnabled, base_url: sttBaseUrl, model: sttModel, language: sttLanguage, ...(sttApiKey ? { api_key: sttApiKey } : {}) },
      })
      setSttApiKey('')
      toast({ title: 'Gespeichert', description: 'STT-Konfiguration aktualisiert.' })
    } catch (err) {
      toast({ title: 'Fehler', description: err instanceof Error ? err.message : 'Speichern fehlgeschlagen', variant: 'destructive' })
    }
  }

  const saveImap = async () => {
    try {
      await update.mutateAsync({
        imap: {
          enabled: imapEnabled, host: imapHost, port: Number(imapPort), ssl: imapSsl, user: imapUser,
          inbox: imapInbox, sent: imapSent, own_addresses: imapOwn, poll_seconds: Number(imapPoll),
          ...(imapPassword ? { password: imapPassword } : {}),
        },
      })
      setImapPassword('')
      toast({ title: 'Gespeichert', description: 'IMAP-Konfiguration aktualisiert.' })
    } catch (err) {
      toast({ title: 'Fehler', description: err instanceof Error ? err.message : 'Speichern fehlgeschlagen', variant: 'destructive' })
    }
  }

  const runTest = async (
    fn: () => Promise<{ ok: boolean; detail: string }>,
  ) => {
    try {
      const res = await fn()
      toast({ title: res.ok ? 'Verbindung OK' : 'Test fehlgeschlagen', description: res.detail, variant: res.ok ? 'default' : 'destructive' })
    } catch (err) {
      toast({ title: 'Fehler', description: err instanceof Error ? err.message : 'Test fehlgeschlagen', variant: 'destructive' })
    }
  }

  const runPoll = async () => {
    try {
      const res = await pollImap.mutateAsync()
      toast({ title: res.ok ? 'Abruf abgeschlossen' : 'Abruf fehlgeschlagen', description: res.detail, variant: res.ok ? 'default' : 'destructive' })
      void query.refetch()
    } catch (err) {
      toast({ title: 'Fehler', description: err instanceof Error ? err.message : 'Abruf fehlgeschlagen', variant: 'destructive' })
    }
  }

  const StatusBadge = ({ ok }: { ok: boolean }) => ok
    ? <Badge className="bg-emerald-600"><CheckCircle2 className="mr-1 h-3 w-3" />Einsatzbereit</Badge>
    : <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" />Nicht konfiguriert</Badge>

  return (
    <div className="container mx-auto max-w-3xl space-y-6 py-8">
      <div className="flex justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-3xl font-bold">
            <Cable className="h-7 w-7 text-sky-700" /> Auto-Capture-Connectoren
          </h1>
          <p className="mt-2 text-muted-foreground">
            STT- und IMAP-Einstellungen für die automatische Kontakt-Erfassung — pro Mandant,
            ohne Umgebungsvariablen. Secrets werden nie angezeigt; leer lassen behält den Wert.
          </p>
        </div>
        <Button asChild variant="outline">
          <Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zurück</Link>
        </Button>
      </div>

      {/* ── STT / Sprache-zu-Text ─────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mic className="h-5 w-5 text-sky-700" /> Telefon-Transkript (STT)
            <StatusBadge ok={stt.configured} />
          </CardTitle>
          <CardDescription>
            OpenAI-kompatibler Server (z. B. faster-whisper-server / docker-whisper).
            Ohne Server funktioniert der reine Transkript-Text-Weg. API-Key hinterlegt: {stt.api_key_set ? 'ja' : 'nein'}.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={sttEnabled} onChange={(e) => setSttEnabled(e.target.checked)} />
            STT aktiviert
          </label>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="stt_base">Base-URL</Label>
              <Input id="stt_base" value={sttBaseUrl} onChange={(e) => setSttBaseUrl(e.target.value)} placeholder="http://whisper:8000/v1" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="stt_model">Modell</Label>
              <Input id="stt_model" value={sttModel} onChange={(e) => setSttModel(e.target.value)} placeholder="Systran/faster-whisper-small" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="stt_lang">Sprache</Label>
              <Input id="stt_lang" value={sttLanguage} onChange={(e) => setSttLanguage(e.target.value)} placeholder="de" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="stt_key">API-Key {stt.api_key_set && <span className="text-xs text-muted-foreground">(gesetzt — leer = behalten)</span>}</Label>
              <Input id="stt_key" type="password" value={sttApiKey} onChange={(e) => setSttApiKey(e.target.value)} placeholder={stt.api_key_set ? '••••••••' : '(optional)'} autoComplete="off" />
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={saveStt} disabled={update.isPending}>
              {update.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Speichern
            </Button>
            <Button variant="outline" onClick={() => runTest(() => testStt.mutateAsync())} disabled={testStt.isPending}>
              {testStt.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Server testen
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* ── IMAP / E-Mail ─────────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5 text-sky-700" /> E-Mail-Postfach (IMAP)
            <StatusBadge ok={imap.configured} />
          </CardTitle>
          <CardDescription>
            Server-seitiger Abruf neuer Mails → Auto-Capture. Passwort hinterlegt: {imap.password_set ? 'ja' : 'nein'}.
            Alternativ extern via tools/mail-connector oder OSS-Webhook auf /crm/kim/mail-capture.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={imapEnabled} onChange={(e) => setImapEnabled(e.target.checked)} />
            IMAP-Abruf aktiviert
          </label>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="imap_host">Host</Label>
              <Input id="imap_host" value={imapHost} onChange={(e) => setImapHost(e.target.value)} placeholder="imap.example.de" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="imap_port">Port</Label>
              <Input id="imap_port" type="number" value={imapPort} onChange={(e) => setImapPort(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="imap_user">Benutzer</Label>
              <Input id="imap_user" value={imapUser} onChange={(e) => setImapUser(e.target.value)} placeholder="crm@example.de" autoComplete="off" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="imap_pw">Passwort {imap.password_set && <span className="text-xs text-muted-foreground">(gesetzt — leer = behalten)</span>}</Label>
              <Input id="imap_pw" type="password" value={imapPassword} onChange={(e) => setImapPassword(e.target.value)} placeholder={imap.password_set ? '••••••••' : 'App-Passwort'} autoComplete="off" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="imap_inbox">Posteingang-Ordner</Label>
              <Input id="imap_inbox" value={imapInbox} onChange={(e) => setImapInbox(e.target.value)} placeholder="INBOX" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="imap_sent">Gesendet-Ordner <span className="text-xs text-muted-foreground">(optional)</span></Label>
              <Input id="imap_sent" value={imapSent} onChange={(e) => setImapSent(e.target.value)} placeholder="Sent" />
            </div>
            <div className="space-y-1.5 md:col-span-2">
              <Label htmlFor="imap_own">Eigene Adressen <span className="text-xs text-muted-foreground">(kommagetrennt → Richtungserkennung)</span></Label>
              <Input id="imap_own" value={imapOwn} onChange={(e) => setImapOwn(e.target.value)} placeholder="crm@example.de, info@example.de" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="imap_poll">Poll-Intervall (Sek.)</Label>
              <Input id="imap_poll" type="number" value={imapPoll} onChange={(e) => setImapPoll(e.target.value)} />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={imapSsl} onChange={(e) => setImapSsl(e.target.checked)} />
            SSL/TLS verwenden
          </label>
          <div className="flex flex-wrap gap-2">
            <Button onClick={saveImap} disabled={update.isPending}>
              {update.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Speichern
            </Button>
            <Button variant="outline" onClick={() => runTest(() => testImap.mutateAsync())} disabled={testImap.isPending}>
              {testImap.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Verbindung testen
            </Button>
            <Button variant="secondary" onClick={runPoll} disabled={pollImap.isPending || !imap.configured}>
              {pollImap.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <DownloadCloud className="mr-2 h-4 w-4" />}Jetzt abrufen
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
