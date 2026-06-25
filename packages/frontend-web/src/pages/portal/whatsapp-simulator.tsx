import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/components/ui/use-toast'

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
  'Kannst du mir 5t Wintergerste schicken? Hof am Dorfkrug, Lieferung 2026-07-10.',
  '50 kg Saatgut Mais',
  'Guten Morgen! 12 Tonnen Triticale.',
]

interface SimulatorResponse {
  reply: string
  conversation: {
    phone: string
    kunden_nr: string | null
    kunden_name: string | null
    turn: number
    partial_order: {
      artikel: string | null
      menge: number | null
      einheit: string | null
      lieferdatum: string | null
      konfidenz: number
      fehlende_felder: string[]
    } | null
    history: { role: string; content: string }[]
  } | null
  orders: {
    id: string
    kunden_name: string
    artikel: string
    menge: number
    einheit: string
    lieferdatum: string | null
    status: string
    erstellt_am: string
  }[]
}

export default function WhatsAppSimulator() {
  const [phone, setPhone] = useState(DEMO_PHONES[0].value)
  const [message, setMessage] = useState('')
  const [tenantId] = useState('dev-tenant')
  const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([])
  const [lastResponse, setLastResponse] = useState<SimulatorResponse | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory])

  const sendMutation = useMutation({
    mutationFn: async (vars: { phone: string; message: string; tenant_id: string }) => {
      const res = await axios.post<SimulatorResponse>(`${API}/dev/simulate`, vars)
      return res.data
    },
    onSuccess: (data) => {
      setChatHistory(data.conversation?.history ?? [])
      setLastResponse(data)
      setMessage('')
    },
    onError: (err: unknown) => {
      const msg = axios.isAxiosError(err) ? err.response?.data?.detail : 'Netzwerkfehler'
      toast({ title: 'Fehler', description: String(msg), variant: 'destructive' })
    },
  })

  const resetMutation = useMutation({
    mutationFn: async () => {
      await axios.delete(`${API}/dev/history/${encodeURIComponent(phone)}`, {
        params: { tenant_id: tenantId },
      })
    },
    onSuccess: () => {
      setChatHistory([])
      setLastResponse(null)
      toast({ title: 'Gesprächsverlauf zurückgesetzt' })
    },
    onError: () => {
      toast({ title: 'Reset fehlgeschlagen', variant: 'destructive' })
    },
  })

  function handleSend() {
    if (!message.trim() || sendMutation.isPending) return
    setChatHistory((h) => [...h, { role: 'user', content: message.trim() }])
    sendMutation.mutate({ phone, message: message.trim(), tenant_id: tenantId })
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const order = lastResponse?.partial_order ?? lastResponse?.conversation?.partial_order
  const completedOrders = lastResponse?.orders ?? []

  return (
    <div className="p-4 max-w-5xl mx-auto space-y-4">
      <div className="flex items-center gap-3">
        <span className="text-2xl">📱</span>
        <div>
          <h1 className="text-xl font-semibold">WhatsApp Bestell-Simulator</h1>
          <p className="text-sm text-muted-foreground">
            WA-AGENT-001 — Test-Webhook ohne Meta-Authentifizierung
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* ── Linke Spalte: Konfiguration ── */}
        <div className="space-y-3 lg:col-span-1">
          <div className="border rounded-lg p-3 space-y-3 bg-card">
            <h2 className="text-sm font-medium">Absender-Nummer</h2>
            <select
              className="w-full text-sm border rounded p-2 bg-background"
              value={phone}
              onChange={(e) => {
                setPhone(e.target.value)
                setChatHistory([])
                setLastResponse(null)
              }}
            >
              {DEMO_PHONES.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
            <Input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+49..."
              className="text-sm font-mono"
            />
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={() => resetMutation.mutate()}
              disabled={resetMutation.isPending}
            >
              Gesprächsverlauf zurücksetzen
            </Button>
          </div>

          <div className="border rounded-lg p-3 space-y-2 bg-card">
            <h2 className="text-sm font-medium">Beispiel-Nachrichten</h2>
            {EXAMPLE_MESSAGES.map((ex) => (
              <button
                key={ex}
                className="w-full text-left text-xs p-2 rounded hover:bg-accent border border-transparent hover:border-border transition-colors"
                onClick={() => setMessage(ex)}
              >
                {ex}
              </button>
            ))}
          </div>

          {/* Extrahierte Bestellung */}
          {order && (
            <div className="border rounded-lg p-3 space-y-2 bg-card">
              <h2 className="text-sm font-medium">Erkannte Bestelldetails</h2>
              <div className="space-y-1 text-xs">
                <Row label="Artikel" value={order.artikel} />
                <Row
                  label="Menge"
                  value={order.menge != null ? `${order.menge} ${order.einheit ?? ''}` : null}
                />
                <Row label="Lieferdatum" value={order.lieferdatum} />
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Konfidenz</span>
                  <span
                    className={
                      order.konfidenz >= 0.8
                        ? 'text-green-600 font-medium'
                        : 'text-amber-600 font-medium'
                    }
                  >
                    {Math.round(order.konfidenz * 100)} %
                  </span>
                </div>
                {order.fehlende_felder.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {order.fehlende_felder.map((f) => (
                      <Badge key={f} variant="outline" className="text-xs">
                        fehlt: {f}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* ── Mitte: Chat ── */}
        <div className="lg:col-span-2 space-y-3">
          <div className="border rounded-lg bg-card flex flex-col h-96">
            <div className="flex items-center gap-2 px-3 py-2 border-b bg-green-600 rounded-t-lg">
              <span className="text-white text-sm font-medium">💬 WhatsApp Chat</span>
              <span className="text-green-200 text-xs ml-auto font-mono">{phone}</span>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {chatHistory.length === 0 && (
                <p className="text-center text-xs text-muted-foreground pt-8">
                  Wähle eine Beispiel-Nachricht oder schreibe direkt.
                </p>
              )}
              {chatHistory.map((msg, i) => (
                <ChatBubble key={i} role={msg.role} content={msg.content} />
              ))}
              {sendMutation.isPending && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg px-3 py-2 text-sm animate-pulse text-muted-foreground">
                    Agent tippt…
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          </div>

          <div className="flex gap-2">
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Nachricht eingeben… (Enter = Senden, Shift+Enter = Zeilenumbruch)"
              className="text-sm resize-none"
              rows={2}
            />
            <Button
              onClick={handleSend}
              disabled={!message.trim() || sendMutation.isPending}
              className="bg-green-600 hover:bg-green-700 self-end"
            >
              Senden
            </Button>
          </div>

          {/* Angelegte Aufträge */}
          {completedOrders.length > 0 && (
            <div className="border rounded-lg p-3 space-y-2 bg-card">
              <h2 className="text-sm font-medium">📋 Angelegte WhatsApp-Aufträge</h2>
              <div className="space-y-2">
                {completedOrders.map((o) => (
                  <div key={o.id} className="border rounded p-2 text-xs space-y-0.5">
                    <div className="flex justify-between font-medium">
                      <span className="font-mono text-primary">{o.id}</span>
                      <Badge variant="outline" className="text-xs">
                        {o.status}
                      </Badge>
                    </div>
                    <div className="text-muted-foreground">
                      {o.kunden_name} · {o.menge} {o.einheit} {o.artikel}
                      {o.lieferdatum ? ` · ${o.lieferdatum}` : ''}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ChatBubble({ role, content }: { role: string; content: string }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
          isUser ? 'bg-green-600 text-white' : 'bg-muted text-foreground'
        }`}
      >
        {content}
      </div>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div className="flex justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className={value != null ? 'font-medium' : 'text-muted-foreground italic'}>
        {value ?? '—'}
      </span>
    </div>
  )
}
