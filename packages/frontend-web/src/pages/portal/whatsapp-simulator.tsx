import { useState, useRef, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'

const API = '/api/v1/whatsapp'

const DEMO_PHONES = [
  { label: 'Landwirt Müller (K-10001)', value: '+4917612345678' },
  { label: 'Betrieb Schmidt GbR (K-10002)', value: '+4915123456789' },
  { label: 'Agrar Hoffmann KG (K-10003)', value: '+4916987654321' },
  { label: 'Unbekannte Nummer', value: '+4900000000000' },
]

const EXAMPLE_MESSAGES = [
  'Hallo, ich brauche 20 Tonnen Winterweizen, Lieferung nächste Woche.',
  'Raps, achtzig Doppelzentner bitte.',
  '5t Wintergerste, Hof am Dorfkrug, Lieferung 2026-07-10.',
  '50 kg Saatgut Mais',
  'Guten Morgen! 12 Tonnen Triticale.',
]

type Tab = 'chat' | 'notify' | 'outbox'

interface SimResponse {
  reply: string
  conversation?: {
    history: { role: string; content: string }[]
    partial_order?: {
      artikel: string | null
      menge: number | null
      einheit: string | null
      lieferdatum: string | null
      konfidenz: number
      fehlende_felder: string[]
    }
  }
  orders?: SimOrder[]
}

interface SimOrder {
  id: string
  kunden_name: string
  artikel: string
  menge: number
  einheit: string
  lieferdatum: string | null
  status: string
}

interface OutboxMsg {
  msg_id: string
  phone: string
  notify_type: string
  text: string
  status: string
  created_at: string
}

export default function WhatsAppSimulator() {
  const [phone, setPhone] = useState(DEMO_PHONES[0].value)
  const [message, setMessage] = useState('')
  const [tenantId] = useState('dev-tenant')
  const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([])
  const [lastResponse, setLastResponse] = useState<SimResponse | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('chat')
  const chatEndRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()
  const [notifyPhone, setNotifyPhone] = useState(DEMO_PHONES[0].value)
  const [notifyArtikel, setNotifyArtikel] = useState('Winterweizen')
  const [notifyMenge, setNotifyMenge] = useState('20')
  const [notifyEinheit, setNotifyEinheit] = useState('t')
  const [notifyEta, setNotifyEta] = useState('60')
  const [notifyFahrer, setNotifyFahrer] = useState('')
  const [docPhone, setDocPhone] = useState(DEMO_PHONES[0].value)
  const [docTyp, setDocTyp] = useState('Lieferschein')
  const [docNr, setDocNr] = useState('LS-2026-00123')

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [chatHistory])

  const sendMutation = useMutation({
    mutationFn: async (vars: { phone: string; message: string; tenant_id: string }) => {
      const res = await axios.post(`${API}/dev/simulate`, vars)
      return res.data
    },
    onSuccess: (data: SimResponse) => { setChatHistory(data.conversation?.history ?? []); setLastResponse(data); setMessage('') },
    onError: (err: unknown) => {
      const msg = axios.isAxiosError(err) ? err.response?.data?.detail : 'Netzwerkfehler'
      toast({ title: 'Fehler', description: String(msg), variant: 'destructive' })
    },
  })

  const resetMutation = useMutation({
    mutationFn: async () => {
      await axios.delete(`${API}/dev/history/${encodeURIComponent(phone)}`, { params: { tenant_id: tenantId } })
    },
    onSuccess: () => { setChatHistory([]); setLastResponse(null); toast({ title: 'Verlauf zurückgesetzt' }) },
    onError: () => toast({ title: 'Reset fehlgeschlagen', variant: 'destructive' }),
  })

  const lieferMutation = useMutation({
    mutationFn: async () => {
      const res = await axios.post(`${API}/dev/notify/lieferankuendigung`, {
        tenant_id: tenantId, phone: notifyPhone,
        kunden_name: DEMO_PHONES.find((p) => p.value === notifyPhone)?.label.split(' (')[0],
        artikel: notifyArtikel, menge: parseFloat(notifyMenge) || 0,
        einheit: notifyEinheit, eta_min: parseInt(notifyEta) || 60,
        fahrer: notifyFahrer || undefined,
      })
      return res.data as { text: string }
    },
    onSuccess: (data) => { toast({ title: 'Lieferankündigung gesendet', description: data.text }); outboxRefetch(); setActiveTab('outbox') },
    onError: () => toast({ title: 'Fehler', variant: 'destructive' }),
  })

  const docMutation = useMutation({
    mutationFn: async () => {
      const res = await axios.post(`${API}/dev/notify/dokument-ready`, {
        tenant_id: tenantId, phone: docPhone,
        kunden_name: DEMO_PHONES.find((p) => p.value === docPhone)?.label.split(' (')[0],
        doc_typ: docTyp, doc_nr: docNr,
      })
      return res.data as { text: string }
    },
    onSuccess: (data) => { toast({ title: 'Dokument-Benachrichtigung gesendet', description: data.text }); outboxRefetch(); setActiveTab('outbox') },
    onError: () => toast({ title: 'Fehler', variant: 'destructive' }),
  })

  const { data: outboxData, refetch: outboxRefetch } = useQuery({
    queryKey: ['wa-outbox', tenantId],
    queryFn: async () => {
      const res = await axios.get<{ messages: OutboxMsg[] }>(`${API}/dev/outbox`, { params: { tenant_id: tenantId } })
      return res.data.messages
    },
    enabled: activeTab === 'outbox',
    refetchInterval: activeTab === 'outbox' ? 5000 : false,
  })

  function handleSend() {
    if (!message.trim() || sendMutation.isPending) return
    setChatHistory((h) => [...h, { role: 'user', content: message.trim() }])
    sendMutation.mutate({ phone, message: message.trim(), tenant_id: tenantId })
  }

  const partialOrder = lastResponse?.conversation?.partial_order
  const completedOrders: SimOrder[] = lastResponse?.orders ?? []

  return (
    <div className="p-4 max-w-5xl mx-auto space-y-4">
      <div className="flex items-center gap-3">
        <span className="text-2xl">📱</span>
        <div>
          <h1 className="text-xl font-semibold">WhatsApp Bestell-Simulator</h1>
          <p className="text-sm text-muted-foreground">WA-AGENT-001 + WA-NOTIFY-001 — Test-Webhook ohne Meta-Auth</p>
        </div>
      </div>

      <div className="flex gap-1 border-b">
        {(['chat', 'notify', 'outbox'] as Tab[]).map((t) => (
          <button key={t} onClick={() => { setActiveTab(t); if (t === 'outbox') outboxRefetch() }}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === t ? 'border-green-600 text-green-700' : 'border-transparent text-muted-foreground hover:text-foreground'}`}>
            {t === 'chat' ? '💬 Eingehend' : t === 'notify' ? '📤 Ausgehend (Push)' : '📋 Outbox'}
          </button>
        ))}
      </div>

      {activeTab === 'chat' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="space-y-3 lg:col-span-1">
            <div className="border rounded-lg p-3 space-y-3 bg-card">
              <h2 className="text-sm font-medium">Absender-Nummer</h2>
              <select className="w-full text-sm border rounded p-2 bg-background" value={phone}
                onChange={(e) => { setPhone(e.target.value); setChatHistory([]); setLastResponse(null) }}>
                {DEMO_PHONES.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
              <Input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+49..." className="text-sm font-mono" />
              <Button variant="outline" size="sm" className="w-full" onClick={() => resetMutation.mutate()} disabled={resetMutation.isPending}>Verlauf zurücksetzen</Button>
            </div>
            <div className="border rounded-lg p-3 space-y-2 bg-card">
              <h2 className="text-sm font-medium">Beispiel-Nachrichten</h2>
              {EXAMPLE_MESSAGES.map((ex) => (
                <button key={ex} className="w-full text-left text-xs p-2 rounded hover:bg-accent border border-transparent hover:border-border transition-colors" onClick={() => setMessage(ex)}>{ex}</button>
              ))}
            </div>
            {partialOrder && (
              <div className="border rounded-lg p-3 space-y-2 bg-card">
                <h2 className="text-sm font-medium">Erkannte Details</h2>
                <div className="space-y-1 text-xs">
                  <Row label="Artikel" value={partialOrder.artikel} />
                  <Row label="Menge" value={partialOrder.menge != null ? `${partialOrder.menge} ${partialOrder.einheit ?? ''}` : null} />
                  <Row label="Lieferdatum" value={partialOrder.lieferdatum} />
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Konfidenz</span>
                    <span className={partialOrder.konfidenz >= 0.8 ? 'text-green-600 font-medium' : 'text-amber-600 font-medium'}>{Math.round(partialOrder.konfidenz * 100)} %</span>
                  </div>
                  {partialOrder.fehlende_felder.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {partialOrder.fehlende_felder.map((f: string) => <Badge key={f} variant="outline" className="text-xs">fehlt: {f}</Badge>)}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="lg:col-span-2 space-y-3">
            <div className="border rounded-lg bg-card flex flex-col h-96">
              <div className="flex items-center gap-2 px-3 py-2 border-b bg-green-600 rounded-t-lg">
                <span className="text-white text-sm font-medium">💬 WhatsApp Chat</span>
                <span className="text-green-200 text-xs ml-auto font-mono">{phone}</span>
              </div>
              <div className="flex-1 overflow-y-auto p-3 space-y-2">
                {chatHistory.length === 0 && <p className="text-center text-xs text-muted-foreground pt-8">Wähle eine Beispiel-Nachricht oder schreibe direkt.</p>}
                {chatHistory.map((msg, i) => <ChatBubble key={i} role={msg.role} content={msg.content} />)}
                {sendMutation.isPending && <div className="flex justify-start"><div className="bg-muted rounded-lg px-3 py-2 text-sm animate-pulse text-muted-foreground">Agent tippt…</div></div>}
                <div ref={chatEndRef} />
              </div>
            </div>
            <div className="flex gap-2">
              <Textarea value={message} onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
                placeholder="Nachricht eingeben… (Enter = Senden)" className="text-sm resize-none" rows={2} />
              <Button onClick={handleSend} disabled={!message.trim() || sendMutation.isPending} className="bg-green-600 hover:bg-green-700 self-end">Senden</Button>
            </div>
            {completedOrders.length > 0 && (
              <div className="border rounded-lg p-3 space-y-2 bg-card">
                <h2 className="text-sm font-medium">📋 Angelegte Aufträge</h2>
                {completedOrders.map((o) => (
                  <div key={o.id} className="border rounded p-2 text-xs">
                    <div className="flex justify-between font-medium"><span className="font-mono text-primary">{o.id}</span><Badge variant="outline" className="text-xs">{o.status}</Badge></div>
                    <div className="text-muted-foreground">{o.kunden_name} · {o.menge} {o.einheit} {o.artikel}{o.lieferdatum ? ` · ${o.lieferdatum}` : ''}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'notify' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border rounded-lg p-4 space-y-3 bg-card">
            <h2 className="text-base font-semibold">🚛 Lieferankündigung</h2>
            <p className="text-xs text-muted-foreground">Wird von Disposition getriggert wenn LKW ~ETA Minuten entfernt ist.</p>
            <div className="space-y-1"><label className="text-xs text-muted-foreground">Empfänger</label>
              <select className="w-full text-sm border rounded p-2 bg-background" value={notifyPhone} onChange={(e) => setNotifyPhone(e.target.value)}>
                {DEMO_PHONES.slice(0, 3).map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select></div>
            <div className="grid grid-cols-3 gap-2">
              <div className="col-span-2 space-y-1"><label className="text-xs text-muted-foreground">Artikel</label><Input value={notifyArtikel} onChange={(e) => setNotifyArtikel(e.target.value)} className="text-sm" /></div>
              <div className="space-y-1"><label className="text-xs text-muted-foreground">Einheit</label>
                <select className="w-full text-sm border rounded p-2 bg-background" value={notifyEinheit} onChange={(e) => setNotifyEinheit(e.target.value)}>
                  {['t', 'dt', 'kg', 'Stk'].map((e) => <option key={e}>{e}</option>)}
                </select></div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1"><label className="text-xs text-muted-foreground">Menge</label><Input value={notifyMenge} onChange={(e) => setNotifyMenge(e.target.value)} type="number" className="text-sm" /></div>
              <div className="space-y-1"><label className="text-xs text-muted-foreground">ETA (Min)</label><Input value={notifyEta} onChange={(e) => setNotifyEta(e.target.value)} type="number" className="text-sm" /></div>
            </div>
            <div className="space-y-1"><label className="text-xs text-muted-foreground">Fahrer (optional)</label><Input value={notifyFahrer} onChange={(e) => setNotifyFahrer(e.target.value)} className="text-sm" placeholder="Max Mustermann" /></div>
            <Button className="w-full bg-green-600 hover:bg-green-700" onClick={() => lieferMutation.mutate()} disabled={lieferMutation.isPending}>
              {lieferMutation.isPending ? 'Sende…' : '📤 Lieferankündigung senden'}
            </Button>
          </div>

          <div className="border rounded-lg p-4 space-y-3 bg-card">
            <h2 className="text-base font-semibold">📄 Dokument verfügbar</h2>
            <p className="text-xs text-muted-foreground">Wird von Docflow getriggert nach Lieferschein-/Rechnungs-Erstellung.</p>
            <div className="space-y-1"><label className="text-xs text-muted-foreground">Empfänger</label>
              <select className="w-full text-sm border rounded p-2 bg-background" value={docPhone} onChange={(e) => setDocPhone(e.target.value)}>
                {DEMO_PHONES.slice(0, 3).map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select></div>
            <div className="space-y-1"><label className="text-xs text-muted-foreground">Dokumententyp</label>
              <select className="w-full text-sm border rounded p-2 bg-background" value={docTyp} onChange={(e) => setDocTyp(e.target.value)}>
                <option>Lieferschein</option><option>Rechnung</option>
              </select></div>
            <div className="space-y-1"><label className="text-xs text-muted-foreground">Dokumenten-Nr.</label><Input value={docNr} onChange={(e) => setDocNr(e.target.value)} className="text-sm font-mono" /></div>
            <Button className="w-full bg-green-600 hover:bg-green-700" onClick={() => docMutation.mutate()} disabled={docMutation.isPending}>
              {docMutation.isPending ? 'Sende…' : '📤 Dokument-Benachrichtigung senden'}
            </Button>
            <div className="p-3 bg-muted rounded text-xs text-muted-foreground">
              <p className="font-medium text-foreground mb-1">Produktions-Integration:</p>
              <code className="block bg-background rounded p-2 font-mono">POST /api/v1/whatsapp/dev/notify/dokument-ready</code>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'outbox' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium">Ausgehende Nachrichten (Outbox)</h2>
            <Button variant="outline" size="sm" onClick={() => outboxRefetch()}>Aktualisieren</Button>
          </div>
          {!outboxData || outboxData.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">Noch keine ausgehenden Nachrichten.</p>
          ) : (
            <div className="space-y-2">
              {outboxData.map((msg) => (
                <div key={msg.msg_id} className="border rounded-lg p-3 text-sm space-y-2 bg-card">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{msg.notify_type === 'lieferankuendigung' ? '🚛' : '📄'}</span>
                      <div><span className="font-mono text-xs text-muted-foreground">{msg.msg_id}</span><p className="text-xs text-muted-foreground">{msg.phone}</p></div>
                    </div>
                    <Badge variant={msg.status === 'sent' ? 'default' : 'outline'} className="text-xs shrink-0">
                      {msg.status === 'sent' ? '✓ Gesendet' : '⟳ Simuliert'}
                    </Badge>
                  </div>
                  <p className="text-sm bg-muted rounded p-2">{msg.text}</p>
                  <p className="text-xs text-muted-foreground">{new Date(msg.created_at).toLocaleString('de-DE')}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function ChatBubble({ role, content }: { role: string; content: string }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${isUser ? 'bg-green-600 text-white' : 'bg-muted text-foreground'}`}>{content}</div>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div className="flex justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className={value != null ? 'font-medium' : 'text-muted-foreground italic'}>{value ?? '—'}</span>
    </div>
  )
}
