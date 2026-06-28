/**
 * Grundfutter-Analysen — LUFA/VDLUFA Prüfbericht-Import und Verwaltung
 *
 * Features:
 * - PDF-Upload (LUFA Nord-West, Bayern, NRW — Textlayer-PDFs)
 * - CSV-Upload (Labor-Export)
 * - Manuelle Eingabe aller VDLUFA-Parameter
 * - Verifizierung + Übernahme in Futtermittel-DB
 */

import { useState, useRef, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Upload, FileText, Plus, Check, Trash2, ChevronDown, ChevronUp,
  AlertTriangle, Info, Leaf, Beaker, Zap, Microscope, X,
} from 'lucide-react'
import {
  fetchGrundfutterAnalysen,
  createGrundfutterAnalyse,
  patchGrundfutterAnalyse,
  deleteGrundfutterAnalyse,
  uploadGrundfutterPdf,
  uploadGrundfutterCsv,
  promoteAsFeed,
  type GrundfutterAnalyse,
  type GrundfutterAnalyseIn,
  type PdfUploadResult,
} from '@/lib/api/rations-optimization'

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
const C = {
  dark: '#1B3022',
  accent: '#88B04B',
  bg: '#F0F2F5',
  card: '#FFFFFF',
  border: '#D1D5DB',
  muted: '#6B7280',
}

// ---------------------------------------------------------------------------
// Leere Formular-Vorlage
// ---------------------------------------------------------------------------
const EMPTY: GrundfutterAnalyseIn = {
  bezeichnung: '',
  probenart: 'Grassilage',
  labor: '',
  probe_nr: '',
  erntetermin: '',
  probenahme_ort: '',
  schnitt: 1,
}

const PROBENARTEN = ['Grassilage', 'Maissilage', 'Anwelksilage', 'Kleegrassilage', 'Heu', 'Stroh', 'Grünmais', 'Sonstiges']

// ---------------------------------------------------------------------------
// Ampel-Bewertung für Zielwerte (1. Schnitt Grassilage)
// ---------------------------------------------------------------------------
function ampel(wert: number | null | undefined, min?: number, max?: number, minOk?: boolean): 'green' | 'yellow' | 'red' | 'grey' {
  if (wert == null) return 'grey'
  if (min !== undefined && max !== undefined) {
    if (wert >= min && wert <= max) return 'green'
    if (wert >= min * 0.9 && wert <= max * 1.1) return 'yellow'
    return 'red'
  }
  if (min !== undefined && minOk) {
    if (wert >= min) return 'green'
    if (wert >= min * 0.9) return 'yellow'
    return 'red'
  }
  if (max !== undefined && !minOk) {
    if (wert <= max) return 'green'
    if (wert <= max * 1.1) return 'yellow'
    return 'red'
  }
  return 'grey'
}

function Dot({ color }: { color: 'green' | 'yellow' | 'red' | 'grey' }) {
  const bg = { green: '#059669', yellow: '#D97706', red: '#DC2626', grey: '#D1D5DB' }
  return <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 4, background: bg[color], marginRight: 4 }} />
}

// ---------------------------------------------------------------------------
// Analyse-Karte
// ---------------------------------------------------------------------------
function AnalyseKarte({ a, onVerify, onDelete, onPromote }: {
  a: GrundfutterAnalyse
  onVerify: () => void
  onDelete: () => void
  onPromote: () => void
}) {
  const [open, setOpen] = useState(false)

  const nel = ampel(a.nel_ts, 6.2, undefined, true)
  const andf = ampel(a.andfom_ts, 40, 48)
  const xp = ampel(a.rohprotein_ts, undefined, 17, false)

  return (
    <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, marginBottom: 12, overflow: 'hidden' }}>
      {/* Header */}
      <div
        style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer', borderBottom: open ? `1px solid ${C.border}` : 'none' }}
        onClick={() => setOpen(v => !v)}
      >
        <Leaf size={18} color={C.accent} />
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, fontSize: 14, color: C.dark }}>{a.bezeichnung}</div>
          <div style={{ fontSize: 12, color: C.muted }}>
            {a.probenart} · {a.labor || 'Labor unbekannt'} · Probe {a.probe_nr || '–'}
            {a.erntetermin && ` · Ernte ${a.erntetermin}`}
          </div>
        </div>
        {/* Schnell-Ampeln */}
        <div style={{ display: 'flex', gap: 16, fontSize: 11, color: C.muted }}>
          {a.nel_ts != null && <span><Dot color={nel} />NEL {a.nel_ts} MJ</span>}
          {a.andfom_ts != null && <span><Dot color={andf} />aNDFom {a.andfom_ts}%</span>}
          {a.rohprotein_ts != null && <span><Dot color={xp} />XP {a.rohprotein_ts}%</span>}
        </div>
        <span style={{
          fontSize: 11, padding: '2px 8px', borderRadius: 4,
          background: a.verifiziert ? '#D1FAE5' : '#FEF3C7',
          color: a.verifiziert ? '#065F46' : '#92400E',
        }}>
          {a.verifiziert ? '✓ Geprüft' : 'Ungeprüft'}
        </span>
        {open ? <ChevronUp size={16} color={C.muted} /> : <ChevronDown size={16} color={C.muted} />}
      </div>

      {/* Detail */}
      {open && (
        <div style={{ padding: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 16 }}>
            <NutrientGroup title="Energie (TS)" icon={<Zap size={14} />} items={[
              { label: 'ME GfE 2023', value: a.me_gfe2023_ts, unit: 'MJ/kg', color: ampel(a.me_gfe2023_ts, 11.2, undefined, true) },
              { label: 'NEL', value: a.nel_ts, unit: 'MJ/kg', color: ampel(a.nel_ts, 6.2, undefined, true) },
              { label: 'ME-Rind GfE 08', value: a.me_rind_gfe2008_ts, unit: 'MJ/kg', color: ampel(a.me_rind_gfe2008_ts, 10.4, undefined, true) },
              { label: 'OMD', value: a.omd_ts, unit: '%', color: ampel(a.omd_ts, 76, undefined, true) },
              { label: 'Strukturwert', value: a.strukturwert_ts, unit: '', color: ampel(a.strukturwert_ts, 2.6, 2.9) },
            ]} />
            <NutrientGroup title="Protein (TS)" icon={<Beaker size={14} />} items={[
              { label: 'Rohprotein', value: a.rohprotein_ts, unit: '%', color: ampel(a.rohprotein_ts, undefined, 17, false) },
              { label: 'nXP', value: a.nxp_ts, unit: 'g/kg', color: ampel(a.nxp_ts, 135, undefined, true) },
              { label: 'RNB', value: a.rnb_ts, unit: 'g/kg', color: ampel(a.rnb_ts, undefined, 6, false) },
              { label: 'sidP', value: a.sidp_ts, unit: 'g/kg', color: 'grey' },
              { label: 'RMD', value: a.rmd_ts, unit: 'g N/kg', color: 'grey' },
            ]} />
            <NutrientGroup title="Faser (TS)" icon={<Leaf size={14} />} items={[
              { label: 'Rohfaser', value: a.rohfaser_ts, unit: '%', color: ampel(a.rohfaser_ts, 22, 25) },
              { label: 'aNDFom', value: a.andfom_ts, unit: '%', color: ampel(a.andfom_ts, 40, 48) },
              { label: 'ADFom', value: a.adfom_ts, unit: '%', color: ampel(a.adfom_ts, 25, 30) },
              { label: 'ADL', value: a.adl_ts, unit: '%', color: ampel(a.adl_ts, undefined, 3, false) },
              { label: 'Gasbildung', value: a.gasbildung_ts, unit: 'ml/200mg', color: ampel(a.gasbildung_ts, 52, undefined, true) },
            ]} />
            <NutrientGroup title="Mineralstoffe (TS)" icon={<Microscope size={14} />} items={[
              { label: 'Ca', value: a.calcium_ts, unit: '%', color: 'grey' },
              { label: 'P', value: a.phosphor_ts, unit: '%', color: 'grey' },
              { label: 'Na', value: a.natrium_ts, unit: '%', color: 'grey' },
              { label: 'Mg', value: a.magnesium_ts, unit: '%', color: 'grey' },
              { label: 'K', value: a.kalium_ts, unit: '%', color: 'grey' },
            ]} />
          </div>

          {/* TS + Sensorik */}
          <div style={{ display: 'flex', gap: 24, fontSize: 12, color: C.muted, marginBottom: 16 }}>
            {a.trockensubstanz_os != null && <span>TS: <strong>{a.trockensubstanz_os}%</strong> (OS)</span>}
            {a.ph_wert != null && <span>pH: <strong>{a.ph_wert}</strong></span>}
            {a.aussehen && <span>Aussehen: {a.aussehen}</span>}
            {a.geruch && <span>Geruch: {a.geruch}</span>}
            {a.quelle_datei && <span style={{ color: C.accent }}>📄 {a.quelle_datei}</span>}
          </div>

          {/* Aktionen */}
          <div style={{ display: 'flex', gap: 8 }}>
            {!a.verifiziert && (
              <button onClick={onVerify} style={{
                padding: '6px 14px', background: C.accent, color: '#fff',
                border: 'none', borderRadius: 6, fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
              }}>
                <Check size={14} /> Verifizieren
              </button>
            )}
            {a.verifiziert && (
              <button onClick={onPromote} style={{
                padding: '6px 14px', background: C.dark, color: '#fff',
                border: 'none', borderRadius: 6, fontSize: 13, cursor: 'pointer',
              }}>
                In Futtermittel-DB übernehmen
              </button>
            )}
            <button onClick={onDelete} style={{
              padding: '6px 12px', background: 'none', color: '#DC2626',
              border: '1px solid #FCA5A5', borderRadius: 6, fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
            }}>
              <Trash2 size={14} /> Löschen
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function NutrientGroup({ title, icon, items }: {
  title: string
  icon: React.ReactNode
  items: { label: string; value: number | null | undefined; unit: string; color: 'green' | 'yellow' | 'red' | 'grey' }[]
}) {
  return (
    <div style={{ background: '#F9FAFB', borderRadius: 6, padding: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8, fontWeight: 600, fontSize: 12, color: C.dark }}>
        {icon} {title}
      </div>
      {items.map(i => (
        <div key={i.label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
          <span style={{ color: C.muted }}><Dot color={i.color} />{i.label}</span>
          <span style={{ fontWeight: 500, color: C.dark }}>
            {i.value != null ? `${i.value} ${i.unit}` : '—'}
          </span>
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Upload-Bereich
// ---------------------------------------------------------------------------
function UploadZone({ onResult }: { onResult: (r: PdfUploadResult, file: File) => void }) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handle = useCallback(async (file: File) => {
    setError(null)
    setLoading(true)
    try {
      let result: PdfUploadResult
      if (file.name.toLowerCase().endsWith('.csv')) {
        result = await uploadGrundfutterCsv(file, false)
      } else {
        result = await uploadGrundfutterPdf(file, false)
      }
      onResult(result, file)
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      const msg = e instanceof Error ? e.message : 'Upload fehlgeschlagen'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [onResult])

  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={e => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) handle(f) }}
      onClick={() => inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragging ? C.accent : C.border}`,
        borderRadius: 12, padding: 32, textAlign: 'center', cursor: 'pointer',
        background: dragging ? '#F0F7ED' : C.card, transition: 'all 0.2s',
        marginBottom: 24,
      }}
    >
      <input ref={inputRef} type="file" accept=".pdf,.csv" style={{ display: 'none' }}
        onChange={e => { const f = e.target.files?.[0]; if (f) handle(f) }} />
      {loading ? (
        <div style={{ color: C.muted }}>Analysiere PDF… bitte warten</div>
      ) : (
        <>
          <Upload size={32} color={C.accent} style={{ margin: '0 auto 12px' }} />
          <div style={{ fontWeight: 600, color: C.dark, marginBottom: 4 }}>LUFA-Prüfbericht oder CSV hochladen</div>
          <div style={{ fontSize: 13, color: C.muted }}>
            PDF (LUFA Nord-West, Bayern, NRW) oder CSV-Export · Drag & Drop oder klicken
          </div>
          <div style={{ fontSize: 11, color: C.muted, marginTop: 8 }}>
            Alle VDLUFA-Parameter werden automatisch erkannt
          </div>
        </>
      )}
      {error && (
        <div style={{ marginTop: 12, color: '#DC2626', fontSize: 13 }}>
          <AlertTriangle size={14} style={{ display: 'inline', marginRight: 4 }} />{error}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Formular — manuelle Eingabe / Korrektur nach Parse
// ---------------------------------------------------------------------------
function AnalyseFormular({ initial, onSave, onCancel }: {
  initial: GrundfutterAnalyseIn
  onSave: (d: GrundfutterAnalyseIn) => void
  onCancel: () => void
}) {
  const [form, setForm] = useState<GrundfutterAnalyseIn>(initial)
  const set = (key: keyof GrundfutterAnalyseIn, val: unknown) =>
    setForm(f => ({ ...f, [key]: val }))

  const num = (key: keyof GrundfutterAnalyseIn) => (
    <input
      type="number" step="0.01"
      value={form[key] as number ?? ''}
      onChange={e => set(key, e.target.value === '' ? undefined : parseFloat(e.target.value))}
      style={inp}
    />
  )
  const txt = (key: keyof GrundfutterAnalyseIn, placeholder?: string) => (
    <input
      type="text"
      value={(form[key] as string) ?? ''}
      placeholder={placeholder}
      onChange={e => set(key, e.target.value)}
      style={inp}
    />
  )
  const inp: React.CSSProperties = {
    width: '100%', padding: '6px 10px', border: `1px solid ${C.border}`,
    borderRadius: 6, fontSize: 13, outline: 'none', boxSizing: 'border-box',
  }
  const lbl: React.CSSProperties = { fontSize: 12, color: C.muted, marginBottom: 4, display: 'block' }
  const grp = (label: string, children: React.ReactNode) => (
    <div style={{ marginBottom: 12 }}>
      <label style={lbl}>{label}</label>
      {children}
    </div>
  )

  return (
    <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20, marginBottom: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ margin: 0, fontSize: 16, color: C.dark }}>Grundfutteranalyse eingeben / korrigieren</h3>
        <button onClick={onCancel} style={{ background: 'none', border: 'none', cursor: 'pointer', color: C.muted }}>
          <X size={18} />
        </button>
      </div>

      {/* Metadaten */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 16 }}>
        {grp('Bezeichnung *', <input type="text" value={form.bezeichnung} onChange={e => set('bezeichnung', e.target.value)} style={{ ...inp, fontWeight: 600 }} />)}
        {grp('Probenart', (
          <select value={form.probenart ?? ''} onChange={e => set('probenart', e.target.value)} style={inp}>
            {PROBENARTEN.map(p => <option key={p}>{p}</option>)}
          </select>
        ))}
        {grp('Labor', txt('labor', 'z.B. LUFA Nord-West'))}
        {grp('Probe-Nr.', txt('probe_nr'))}
        {grp('Erntetermin', <input type="date" value={form.erntetermin ?? ''} onChange={e => set('erntetermin', e.target.value)} style={inp} />)}
        {grp('Schnitt', <input type="number" min={1} max={5} value={form.schnitt ?? ''} onChange={e => set('schnitt', parseInt(e.target.value))} style={inp} />)}
      </div>

      {/* Grundnährstoffe */}
      <div style={{ fontWeight: 600, fontSize: 13, color: C.dark, marginBottom: 8, borderTop: `1px solid ${C.border}`, paddingTop: 12 }}>
        Grundnährstoffe
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 16 }}>
        {grp('Trockensubstanz % (OS)', num('trockensubstanz_os'))}
        {grp('pH-Wert (OS)', num('ph_wert'))}
        {grp('Rohprotein % (TS)', num('rohprotein_ts'))}
        {grp('Rohfaser % (TS)', num('rohfaser_ts'))}
        {grp('Rohfett % (TS)', num('rohfett_ts'))}
        {grp('Rohasche % (TS)', num('rohasche_ts'))}
        {grp('Gesamtzucker % (TS)', num('gesamtzucker_ts'))}
        {grp('NFC % (TS)', num('nfc_ts'))}
      </div>

      {/* Faser */}
      <div style={{ fontWeight: 600, fontSize: 13, color: C.dark, marginBottom: 8, borderTop: `1px solid ${C.border}`, paddingTop: 12 }}>
        Faseranalytik (TS)
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 16 }}>
        {grp('ADFom %', num('adfom_ts'))}
        {grp('aNDFom %', num('andfom_ts'))}
        {grp('ADL %', num('adl_ts'))}
        {grp('Hemicellulose %', num('hemicellulose_ts'))}
        {grp('Gasbildung ml/200mg', num('gasbildung_ts'))}
        {grp('OMD %', num('omd_ts'))}
      </div>

      {/* Energie */}
      <div style={{ fontWeight: 600, fontSize: 13, color: C.dark, marginBottom: 8, borderTop: `1px solid ${C.border}`, paddingTop: 12 }}>
        Energie (TS)
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 16 }}>
        {grp('ME GfE 2023 MJ/kg', num('me_gfe2023_ts'))}
        {grp('NEL MJ/kg', num('nel_ts'))}
        {grp('ME-Rind GfE 2008 MJ/kg', num('me_rind_gfe2008_ts'))}
        {grp('Strukturwert', num('strukturwert_ts'))}
      </div>

      {/* Protein */}
      <div style={{ fontWeight: 600, fontSize: 13, color: C.dark, marginBottom: 8, borderTop: `1px solid ${C.border}`, paddingTop: 12 }}>
        Protein GfE (TS)
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 16 }}>
        {grp('nXP g/kg', num('nxp_ts'))}
        {grp('RNB g/kg', num('rnb_ts'))}
        {grp('sidP g/kg', num('sidp_ts'))}
        {grp('RMD g N/kg', num('rmd_ts'))}
      </div>

      {/* Mineralstoffe */}
      <div style={{ fontWeight: 600, fontSize: 13, color: C.dark, marginBottom: 8, borderTop: `1px solid ${C.border}`, paddingTop: 12 }}>
        Mineralstoffe % (TS)
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12, marginBottom: 16 }}>
        {grp('Ca', num('calcium_ts'))}
        {grp('P', num('phosphor_ts'))}
        {grp('Na', num('natrium_ts'))}
        {grp('Mg', num('magnesium_ts'))}
        {grp('K', num('kalium_ts'))}
      </div>

      {grp('Notizen', <textarea value={form.notizen ?? ''} onChange={e => set('notizen', e.target.value)}
        style={{ ...inp, height: 60, resize: 'vertical' }} />)}

      <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
        <button
          onClick={() => onSave(form)}
          disabled={!form.bezeichnung}
          style={{
            padding: '8px 20px', background: C.accent, color: '#fff',
            border: 'none', borderRadius: 6, fontSize: 14, cursor: 'pointer',
            opacity: form.bezeichnung ? 1 : 0.5,
          }}
        >
          Speichern
        </button>
        <button onClick={onCancel} style={{ padding: '8px 16px', background: 'none', border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 14, cursor: 'pointer' }}>
          Abbrechen
        </button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Hauptseite
// ---------------------------------------------------------------------------
export default function GrundfutterAnalysenPage() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<GrundfutterAnalyseIn>(EMPTY)
  const [parseWarnings, setParseWarnings] = useState<string[]>([])
  const [parseConfidence, setParseConfidence] = useState<string>('')
  const [filterArt, setFilterArt] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['grundfutter-analysen', filterArt],
    queryFn: () => fetchGrundfutterAnalysen(filterArt ? { probenart: filterArt } : {}),
  })

  const [saveError, setSaveError] = useState<string | null>(null)
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null)

  const createMut = useMutation({
    mutationFn: createGrundfutterAnalyse,
    onSuccess: (saved) => {
      qc.invalidateQueries({ queryKey: ['grundfutter-analysen'] })
      setShowForm(false)
      setFormData(EMPTY)
      setParseWarnings([])
      setSaveError(null)
      setSaveSuccess(saved.bezeichnung)
    },
    onError: (err: unknown) => {
      const detail =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null
      const msg = detail ?? (err instanceof Error ? err.message : 'Speichern fehlgeschlagen.')
      // 409 = Dublette
      if (detail?.includes('bereits')) {
        setSaveError(`Dublette: ${msg}`)
      } else {
        setSaveError(msg)
      }
    },
  })

  const patchMut = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof patchGrundfutterAnalyse>[1] }) =>
      patchGrundfutterAnalyse(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['grundfutter-analysen'] }),
  })

  const deleteMut = useMutation({
    mutationFn: deleteGrundfutterAnalyse,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['grundfutter-analysen'] }),
  })

  const [promoteSuccess, setPromoteSuccess] = useState<{ name: string; artikel_nr: string } | null>(null)
  const [promoteError, setPromoteError] = useState<string | null>(null)

  const promoteMut = useMutation({
    mutationFn: promoteAsFeed,
    onSuccess: (res) => {
      setPromoteError(null)
      setPromoteSuccess({ name: res.name ?? '', artikel_nr: res.artikel_nummer })
      qc.invalidateQueries({ queryKey: ['grundfutter-analysen'] })
    },
    onError: (err: unknown) => {
      setPromoteSuccess(null)
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Unbekannter Fehler'
          : String(err)
      setPromoteError(msg)
    },
  })

  const handleUploadResult = (result: PdfUploadResult, _file: File) => {
    if (result.parsed) {
      setFormData(result.parsed)
      setParseWarnings(result.warnings)
      setParseConfidence(result.confidence)
      setShowForm(true)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: C.bg, padding: 24 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: C.dark }}>Grundfutter-Analysen</h1>
          <p style={{ margin: '4px 0 0', color: C.muted, fontSize: 14 }}>
            LUFA / VDLUFA Prüfberichte importieren und verwalten
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <select
            value={filterArt}
            onChange={e => setFilterArt(e.target.value)}
            style={{ padding: '7px 12px', border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 13, background: C.card }}
          >
            <option value="">Alle Probenarten</option>
            {PROBENARTEN.map(p => <option key={p}>{p}</option>)}
          </select>
          <button
            onClick={() => { setFormData(EMPTY); setParseWarnings([]); setParseConfidence(''); setShowForm(true) }}
            style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', background: C.dark, color: '#fff', border: 'none', borderRadius: 6, fontSize: 13, cursor: 'pointer' }}
          >
            <Plus size={16} /> Manuell eingeben
          </button>
        </div>
      </div>

      {/* Info-Banner */}
      <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: 8, padding: '10px 16px', marginBottom: 20, fontSize: 13, color: '#1E40AF', display: 'flex', alignItems: 'center', gap: 8 }}>
        <Info size={16} />
        Unterstützte Labore: LUFA Nord-West · LUFA NRW · LUFA Bayern (TLL) · LKS Sachsen · AGRIlab. PDF mit Textlayer oder CSV-Export.
      </div>

      {/* Speichern-Erfolg */}
      {saveSuccess && (
        <div style={{ background: '#F0FDF4', border: '1px solid #86EFAC', borderRadius: 8, padding: '10px 16px', marginBottom: 16, fontSize: 13, color: '#166534', display: 'flex', alignItems: 'center', gap: 10 }}>
          <Check size={16} />
          <span>
            <strong>{saveSuccess}</strong> wurde gespeichert.{' '}
            <a href="/futtermittel/rationsoptimierung" style={{ color: '#166534', fontWeight: 700, textDecoration: 'underline' }}>
              → Zur Rationsoptimierung
            </a>
          </span>
          <button onClick={() => setSaveSuccess(null)} style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: '#166534' }}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* Speichern-Fehler (Dublette etc.) */}
      {saveError && (
        <div style={{ background: '#FFF7ED', border: '1px solid #FDBA74', borderRadius: 8, padding: '10px 16px', marginBottom: 16, fontSize: 13, color: '#9A3412', display: 'flex', alignItems: 'flex-start', gap: 10 }}>
          <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
          <span>{saveError}</span>
          <button onClick={() => setSaveError(null)} style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: '#9A3412' }}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* Promote-Erfolg */}
      {promoteSuccess && (
        <div style={{ background: '#F0FDF4', border: '1px solid #86EFAC', borderRadius: 8, padding: '10px 16px', marginBottom: 16, fontSize: 13, color: '#166534', display: 'flex', alignItems: 'center', gap: 10 }}>
          <Check size={16} />
          <span>
            <strong>{promoteSuccess.name}</strong> wurde als Futtermittel übernommen (Art.-Nr. {promoteSuccess.artikel_nr}).{' '}
            <a href="/futtermittel/rationsoptimierung" style={{ color: '#166534', fontWeight: 700, textDecoration: 'underline' }}>
              → Zur Rationsoptimierung
            </a>
          </span>
          <button onClick={() => setPromoteSuccess(null)} style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: '#166534' }}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* Promote-Fehler (Dublette o. ä.) */}
      {promoteError && (
        <div style={{ background: '#FFF7ED', border: '1px solid #FDBA74', borderRadius: 8, padding: '10px 16px', marginBottom: 16, fontSize: 13, color: '#9A3412', display: 'flex', alignItems: 'flex-start', gap: 10 }}>
          <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
          <span>{promoteError}</span>
          <button onClick={() => setPromoteError(null)} style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: '#9A3412' }}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* Upload-Zone */}
      <UploadZone onResult={handleUploadResult} />

      {/* Parse-Ergebnis-Banner */}
      {parseWarnings.length > 0 && showForm && (
        <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: 8, padding: '10px 16px', marginBottom: 16, fontSize: 13, color: '#92400E' }}>
          <AlertTriangle size={14} style={{ display: 'inline', marginRight: 6 }} />
          <strong>Parse-Konfidenz: {parseConfidence}</strong> — bitte prüfen:
          {parseWarnings.map((w, i) => <div key={i} style={{ marginLeft: 20, marginTop: 2 }}>• {w}</div>)}
        </div>
      )}

      {/* Formular */}
      {showForm && (
        <AnalyseFormular
          initial={formData}
          onSave={d => createMut.mutate(d)}
          onCancel={() => { setShowForm(false); setParseWarnings([]) }}
        />
      )}

      {/* Liste */}
      {isLoading && <div style={{ textAlign: 'center', color: C.muted, padding: 40 }}>Lade Analysen…</div>}

      {!isLoading && data && data.items.length === 0 && (
        <div style={{ textAlign: 'center', color: C.muted, padding: 60, background: C.card, borderRadius: 8, border: `1px solid ${C.border}` }}>
          <FileText size={40} color={C.border} style={{ margin: '0 auto 12px' }} />
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Noch keine Analysen vorhanden</div>
          <div style={{ fontSize: 13 }}>Lade einen LUFA-Prüfbericht hoch oder gib Werte manuell ein.</div>
        </div>
      )}

      {data?.items.map(a => (
        <AnalyseKarte
          key={a.id}
          a={a}
          onVerify={() => patchMut.mutate({ id: a.id, data: { verifiziert: true } })}
          onDelete={() => { if (confirm(`Analyse "${a.bezeichnung}" löschen?`)) deleteMut.mutate(a.id) }}
          onPromote={() => promoteMut.mutate(a.id)}
        />
      ))}

      {data && data.total > data.items.length && (
        <div style={{ textAlign: 'center', color: C.muted, fontSize: 13, marginTop: 8 }}>
          {data.total} Analysen gesamt
        </div>
      )}
    </div>
  )
}
