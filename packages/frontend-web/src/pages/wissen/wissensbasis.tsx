/**
 * Wissensbasis — Zentraler KI-Wissensspeicher
 * Wave 69 / Knowledge Core
 *
 * 2-Spalten-Layout: Links Liste + Filter, Rechts Detail-View mit Tabs.
 */

import { useState } from 'react'
import {
  useKnowledgeList,
  useKnowledgeItem,
  useKnowledgeStats,
  useCreateKnowledge,
  useUpdateKnowledge,
  useArchiveKnowledge,
  useAddVersion,
  type KnowledgeItem,
  type KnowledgeCreatePayload,
} from '@/lib/api/knowledge'
import { useDebounce } from '@/hooks/useDebounce'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

// ── Constants ───────────────────────────────────────────────────────────────────

const TYP_LABELS: Record<string, string> = {
  SOP: 'SOP',
  PRODUKTWISSEN: 'Produktwissen',
  KOMMUNIKATIONSRICHTLINIE: 'Komm.-Richtlinie',
  SUPPORTWISSEN: 'Supportwissen',
  MARKTDATEN: 'Marktdaten',
  KENNZAHL: 'Kennzahl',
  PROZESSDEFINITION: 'Prozessdefinition',
}

const TYP_FARBEN: Record<string, string> = {
  SOP: 'bg-blue-100 text-blue-800',
  PRODUKTWISSEN: 'bg-green-100 text-green-800',
  KOMMUNIKATIONSRICHTLINIE: 'bg-purple-100 text-purple-800',
  SUPPORTWISSEN: 'bg-orange-100 text-orange-800',
  MARKTDATEN: 'bg-yellow-100 text-yellow-800',
  KENNZAHL: 'bg-teal-100 text-teal-800',
  PROZESSDEFINITION: 'bg-indigo-100 text-indigo-800',
}

const STATUS_FARBEN: Record<string, string> = {
  FREIGEGEBEN: 'bg-green-100 text-green-800',
  ENTWURF: 'bg-gray-100 text-gray-700',
  ARCHIVIERT: 'bg-red-100 text-red-700',
}

const TYP_FILTER_OPTIONEN: Array<{ value: string; label: string }> = [
  { value: '', label: 'Alle' },
  { value: 'SOP', label: 'SOP' },
  { value: 'PRODUKTWISSEN', label: 'Produktwissen' },
  { value: 'PROZESSDEFINITION', label: 'Prozessdefinition' },
  { value: 'MARKTDATEN', label: 'Marktdaten' },
  { value: 'SUPPORTWISSEN', label: 'Supportwissen' },
  { value: 'KENNZAHL', label: 'Kennzahl' },
  { value: 'KOMMUNIKATIONSRICHTLINIE', label: 'Komm.-Richtlinie' },
]

const STATUS_FILTER_OPTIONEN: Array<{ value: string; label: string }> = [
  { value: '', label: 'Alle' },
  { value: 'FREIGEGEBEN', label: 'Freigegeben' },
  { value: 'ENTWURF', label: 'Entwurf' },
  { value: 'ARCHIVIERT', label: 'Archiviert' },
]

const FORMAT_OPTIONEN = [
  'MARKDOWN',
  'JSON',
  'TABELLE',
  'RELATIONALE_DATEN',
  'API_RESOURCE',
  'PDF',
  'WORD',
]

// ── Helpers ─────────────────────────────────────────────────────────────────────

function formatDatum(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// ── Small UI primitives ──────────────────────────────────────────────────────────

function TypBadge({ typ }: { typ: string }) {
  const farbe = TYP_FARBEN[typ] ?? 'bg-gray-100 text-gray-700'
  return (
    <span
      className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium whitespace-nowrap ${farbe}`}
    >
      {TYP_LABELS[typ] ?? typ}
    </span>
  )
}

function StatusBadge({ status }: { status: string }) {
  const farbe = STATUS_FARBEN[status] ?? 'bg-gray-100 text-gray-700'
  return (
    <span className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium ${farbe}`}>
      {status}
    </span>
  )
}

// ── Erstellen-Dialog ─────────────────────────────────────────────────────────────

type ErstellenDialogProps = {
  open: boolean
  onClose: () => void
  onCreated: (item: KnowledgeItem) => void
}

function ErstellenDialog({ open, onClose, onCreated }: ErstellenDialogProps) {
  const createMutation = useCreateKnowledge()
  const [form, setForm] = useState<KnowledgeCreatePayload>({
    titel: '',
    typ: 'SOP',
    beschreibung: '',
    tags: [],
    initiale_version: '',
    format: 'MARKDOWN',
  })
  const [tagsInput, setTagsInput] = useState('')

  function handleSubmit() {
    const tags = tagsInput
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)
    createMutation.mutate(
      { ...form, tags },
      {
        onSuccess: (item) => {
          onCreated(item)
          setForm({
            titel: '',
            typ: 'SOP',
            beschreibung: '',
            tags: [],
            initiale_version: '',
            format: 'MARKDOWN',
          })
          setTagsInput('')
          onClose()
        },
      }
    )
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Neues Wissensobjekt erstellen</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-1">
            <Label htmlFor="k-titel">Titel</Label>
            <Input
              id="k-titel"
              value={form.titel}
              onChange={(e) => setForm((f) => ({ ...f, titel: e.target.value }))}
              placeholder="Titel des Wissensobjekts"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="k-typ">Typ</Label>
            <Select
              value={form.typ}
              onValueChange={(v) => setForm((f) => ({ ...f, typ: v }))}
            >
              <SelectTrigger id="k-typ">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(TYP_LABELS).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label htmlFor="k-beschreibung">Beschreibung</Label>
            <Input
              id="k-beschreibung"
              value={form.beschreibung}
              onChange={(e) => setForm((f) => ({ ...f, beschreibung: e.target.value }))}
              placeholder="Kurze Beschreibung"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="k-tags">Tags (kommagetrennt)</Label>
            <Input
              id="k-tags"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              placeholder="sop, freigabe, vertrieb"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="k-inhalt">Initialer Inhalt</Label>
            <Textarea
              id="k-inhalt"
              rows={5}
              value={form.initiale_version}
              onChange={(e) => setForm((f) => ({ ...f, initiale_version: e.target.value }))}
              placeholder="Inhalt als Markdown..."
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Abbrechen
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!form.titel.trim() || createMutation.isPending}
          >
            {createMutation.isPending ? 'Wird erstellt...' : 'Erstellen'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Neue-Version-Dialog ─────────────────────────────────────────────────────────

type NeueVersionDialogProps = {
  open: boolean
  knowledgeId: string
  onClose: () => void
}

function NeueVersionDialog({ open, knowledgeId, onClose }: NeueVersionDialogProps) {
  const addVersion = useAddVersion()
  const [inhalt, setInhalt] = useState('')
  const [format, setFormat] = useState('MARKDOWN')

  function handleSubmit() {
    addVersion.mutate(
      { knowledge_id: knowledgeId, inhalt, format },
      {
        onSuccess: () => {
          setInhalt('')
          onClose()
        },
      }
    )
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Neue Version hinzufügen</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-1">
            <Label htmlFor="v-format">Format</Label>
            <Select value={format} onValueChange={setFormat}>
              <SelectTrigger id="v-format">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FORMAT_OPTIONEN.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label htmlFor="v-inhalt">Inhalt</Label>
            <Textarea
              id="v-inhalt"
              rows={8}
              value={inhalt}
              onChange={(e) => setInhalt(e.target.value)}
              placeholder="Neuer Versionsinhalt..."
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Abbrechen
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!inhalt.trim() || addVersion.isPending}
          >
            {addVersion.isPending ? 'Wird gespeichert...' : 'Version speichern'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Versionen-Tab ────────────────────────────────────────────────────────────────

function VersionenTab({ item }: { item: KnowledgeItem }) {
  const rows = Array.from({ length: item.versionen_count }, (_, i) => ({
    version: i + 1,
    isCurrent: i + 1 === item.aktuelle_version,
  }))

  if (rows.length === 0) {
    return <p className="text-sm text-gray-400 italic">Keine Versionen vorhanden.</p>
  }

  return (
    <div className="space-y-2">
      {rows.map((row) => (
        <div
          key={row.version}
          className={`flex items-center gap-3 rounded p-3 text-sm border ${
            row.isCurrent
              ? 'bg-blue-50 border-blue-200'
              : 'bg-gray-50 border-gray-200'
          }`}
        >
          <span className="font-semibold text-gray-600 w-14">v{row.version}</span>
          {row.isCurrent && (
            <Badge className="text-xs bg-blue-600 text-white">Aktuell</Badge>
          )}
        </div>
      ))}
    </div>
  )
}

// ── Detail-Panel ─────────────────────────────────────────────────────────────────

type DetailPanelProps = {
  knowledgeId: string
}

function DetailPanel({ knowledgeId }: DetailPanelProps) {
  const { data: item, isLoading } = useKnowledgeItem(knowledgeId)
  const archiveMutation = useArchiveKnowledge()
  const updateMutation = useUpdateKnowledge()
  const [neueVersionOpen, setNeueVersionOpen] = useState(false)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        Wird geladen...
      </div>
    )
  }
  if (!item) return null
  const currentItem = item

  function handleArchive() {
    if (window.confirm(`"${currentItem.titel}" wirklich archivieren?`)) {
      archiveMutation.mutate(currentItem.knowledge_id)
    }
  }

  function toggleAgentenfreigabe() {
    updateMutation.mutate({
      knowledge_id: currentItem.knowledge_id,
      agentenfreigabe: !currentItem.agentenfreigabe,
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b space-y-2 bg-white">
        <div className="flex items-start justify-between gap-2">
          <h2 className="text-lg font-semibold leading-tight text-gray-900">{item.titel}</h2>
          <TypBadge typ={item.typ} />
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <StatusBadge status={item.status} />
          {item.agentenfreigabe && (
            <span className="text-xs bg-violet-100 text-violet-700 rounded px-1.5 py-0.5 font-medium">
              Agenten-freigegeben
            </span>
          )}
          <span className="text-xs text-gray-400 ml-auto">
            Erstellt: {formatDatum(item.created_at)}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="inhalt" className="flex-1 flex flex-col overflow-hidden bg-white">
        <TabsList className="mx-4 mt-3 w-fit shrink-0">
          <TabsTrigger value="inhalt">Inhalt</TabsTrigger>
          <TabsTrigger value="versionen">Versionen ({item.versionen_count})</TabsTrigger>
          <TabsTrigger value="metadaten">Metadaten</TabsTrigger>
        </TabsList>

        <TabsContent value="inhalt" className="flex-1 overflow-auto p-4">
          {item.vorschau ? (
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans leading-relaxed">
              {item.vorschau}
            </pre>
          ) : (
            <p className="text-sm text-gray-400 italic">Kein Inhalt vorhanden.</p>
          )}
          {item.versionen_count > 0 && item.vorschau.length >= 200 && (
            <p className="text-xs text-gray-400 mt-2 italic">
              (Vorschau auf 200 Zeichen begrenzt)
            </p>
          )}
        </TabsContent>

        <TabsContent value="versionen" className="flex-1 overflow-auto p-4">
          <VersionenTab item={item} />
        </TabsContent>

        <TabsContent value="metadaten" className="flex-1 overflow-auto p-4 space-y-5">
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Beschreibung
            </p>
            <p className="text-sm text-gray-700">{item.beschreibung || '—'}</p>
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Tags
            </p>
            <div className="flex flex-wrap gap-1">
              {item.tags.length > 0 ? (
                item.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))
              ) : (
                <span className="text-sm text-gray-400">Keine Tags</span>
              )}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Zielrollen
            </p>
            <div className="flex flex-wrap gap-1">
              {item.zielrollen.length > 0 ? (
                item.zielrollen.map((rolle) => (
                  <Badge key={rolle} variant="outline" className="text-xs">
                    {rolle}
                  </Badge>
                ))
              ) : (
                <span className="text-sm text-gray-400">Alle Rollen</span>
              )}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Typ
              </p>
              <TypBadge typ={item.typ} />
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Status
              </p>
              <StatusBadge status={item.status} />
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Aktualisiert
            </p>
            <p className="text-sm text-gray-700">{formatDatum(item.updated_at)}</p>
          </div>
        </TabsContent>
      </Tabs>

      {/* Aktionsleiste */}
      <div className="p-4 border-t bg-white flex gap-2 flex-wrap">
        <Button variant="outline" size="sm" onClick={() => setNeueVersionOpen(true)}>
          Neue Version
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={toggleAgentenfreigabe}
          disabled={updateMutation.isPending}
        >
          {item.agentenfreigabe ? 'Agenten-Freigabe entziehen' : 'Agenten-Freigabe erteilen'}
        </Button>
        <Button
          variant="destructive"
          size="sm"
          onClick={handleArchive}
          disabled={archiveMutation.isPending || item.status === 'ARCHIVIERT'}
        >
          Archivieren
        </Button>
      </div>

      <NeueVersionDialog
        open={neueVersionOpen}
        knowledgeId={item.knowledge_id}
        onClose={() => setNeueVersionOpen(false)}
      />
    </div>
  )
}

// ── Haupt-Seite ──────────────────────────────────────────────────────────────────

export default function WissensbasisPage() {
  const [searchInput, setSearchInput] = useState('')
  const [typFilter, setTypFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [erstellenOpen, setErstellenOpen] = useState(false)

  const debouncedSearch = useDebounce(searchInput, 300)

  const { data: items = [], isLoading } = useKnowledgeList({
    typ: typFilter || undefined,
    status: statusFilter || undefined,
    search: debouncedSearch || undefined,
    limit: 100,
  })

  const { data: stats } = useKnowledgeStats()

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-gray-50">
      {/* Page-Header */}
      <div className="bg-white border-b px-6 py-4 flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Wissensbasis</h1>
          <p className="text-sm text-gray-500">
            Zentraler KI-Wissensspeicher
            {stats != null && (
              <span className="ml-2 text-gray-400">
                · {stats.gesamt} Objekte · {stats.agentenfreigabe_aktiv} Agenten-freigegeben
              </span>
            )}
          </p>
        </div>
        <Button onClick={() => setErstellenOpen(true)}>+ Neues Wissen</Button>
      </div>

      {/* Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Linke Spalte — Liste */}
        <div className="w-80 shrink-0 flex flex-col border-r bg-white overflow-hidden">
          {/* Suche */}
          <div className="p-3 border-b">
            <Input
              placeholder="Suchen..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="h-8 text-sm"
            />
          </div>

          {/* Typ-Filter */}
          <div className="px-3 pt-2 pb-1">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Typ</p>
            <div className="flex flex-wrap gap-1">
              {TYP_FILTER_OPTIONEN.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setTypFilter(opt.value)}
                  className={`rounded px-2 py-0.5 text-xs font-medium transition-colors ${
                    typFilter === opt.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Status-Filter */}
          <div className="px-3 pt-1 pb-2 border-b">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
              Status
            </p>
            <div className="flex flex-wrap gap-1">
              {STATUS_FILTER_OPTIONEN.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setStatusFilter(opt.value)}
                  className={`rounded px-2 py-0.5 text-xs font-medium transition-colors ${
                    statusFilter === opt.value
                      ? 'bg-gray-700 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Liste */}
          <div className="flex-1 overflow-y-auto">
            {isLoading && (
              <div className="p-4 text-sm text-gray-400">Wird geladen...</div>
            )}
            {!isLoading && items.length === 0 && (
              <div className="p-4 text-sm text-gray-400 italic">Keine Ergebnisse.</div>
            )}
            {items.map((item) => (
              <button
                key={item.knowledge_id}
                type="button"
                onClick={() => setSelectedId(item.knowledge_id)}
                className={`w-full text-left p-3 border-b hover:bg-gray-50 transition-colors ${
                  selectedId === item.knowledge_id
                    ? 'bg-blue-50 border-l-2 border-l-blue-600'
                    : ''
                }`}
              >
                <div className="flex items-start justify-between gap-1 mb-1">
                  <span className="text-sm font-medium text-gray-900 leading-tight line-clamp-2 flex-1">
                    {item.titel}
                  </span>
                  <TypBadge typ={item.typ} />
                </div>
                {item.vorschau && (
                  <p className="text-xs text-gray-500 line-clamp-2 mb-1">{item.vorschau}</p>
                )}
                <div className="flex items-center gap-1.5 flex-wrap">
                  <StatusBadge status={item.status} />
                  {item.agentenfreigabe && (
                    <span
                      className="text-xs text-violet-600"
                      title="Agenten-freigegeben"
                      aria-label="Agenten-freigegeben"
                    >
                      ⚙
                    </span>
                  )}
                  <span className="text-xs text-gray-400 ml-auto">
                    {formatDatum(item.created_at)}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Rechte Spalte — Detail */}
        <div className="flex-1 overflow-hidden">
          {selectedId != null ? (
            <DetailPanel key={selectedId} knowledgeId={selectedId} />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <p className="text-lg mb-1">Kein Objekt ausgewählt</p>
                <p className="text-sm">Wähle ein Wissensobjekt aus der Liste.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <ErstellenDialog
        open={erstellenOpen}
        onClose={() => setErstellenOpen(false)}
        onCreated={(item) => setSelectedId(item.knowledge_id)}
      />
    </div>
  )
}
