import { useState, useEffect, useRef } from 'react'
import {
  type SpeditionFrachttarif,
  type SpeditionFrachttarifPayload,
  listFrachttarife,
  createFrachttarif,
  updateFrachttarif,
  deleteFrachttarif,
} from '@/lib/api/strecke'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type EditRow = SpeditionFrachttarifPayload & { id?: string }
type FreightTariffRole = 'disposition' | 'einkauf' | 'finance' | 'leitung'

const freightTariffRoles = [
  { id: 'disposition', label: 'Disposition', description: 'Prueft, ob fuer die aktuelle PLZ-Strecke ein aktiver Spediteur verfuegbar ist.' },
  { id: 'einkauf', label: 'Einkauf', description: 'Pflegt Tarife, Spediteur und Notiz fuer neue oder geaenderte Frachtpreise.' },
  { id: 'finance', label: 'Finance', description: 'Achtet auf Preislogik, Rechnungserwartung und Kostenabweichung.' },
  { id: 'leitung', label: 'Leitung', description: 'Sieht, ob Tarifpflege oder inaktive Spediteure die Lieferkette blockieren.' },
] satisfies Array<{ id: FreightTariffRole; label: string; description: string }>

const EMPTY_ROW: EditRow = {
  plz_von: '',
  plz_bis: '',
  spediteur: '',
  preis_eur_t: 0,
  aktiv: true,
  notiz: '',
}

export default function SpeditionenFrachtPreisePage(): JSX.Element {
  const [rows, setRows] = useState<SpeditionFrachttarif[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editRow, setEditRow] = useState<EditRow | null>(null)
  const [saving, setSaving] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [roleFocus, setRoleFocus] = useState<FreightTariffRole>('disposition')
  const firstInputRef = useRef<HTMLInputElement>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setRows(await listFrachttarife())
    } catch {
      setError('Fehler beim Laden der Frachttarife.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    if (editRow !== null) firstInputRef.current?.focus()
  }, [editRow])

  const openNew = () => setEditRow({ ...EMPTY_ROW })
  const openEdit = (row: SpeditionFrachttarif) =>
    setEditRow({ id: row.id, plz_von: row.plz_von, plz_bis: row.plz_bis, spediteur: row.spediteur, preis_eur_t: row.preis_eur_t, aktiv: row.aktiv, notiz: row.notiz ?? '' })

  const handleSave = async () => {
    if (!editRow) return
    setSaving(true)
    setError(null)
    try {
      const payload: SpeditionFrachttarifPayload = {
        plz_von: editRow.plz_von.trim(),
        plz_bis: editRow.plz_bis.trim(),
        spediteur: editRow.spediteur.trim(),
        preis_eur_t: Number(editRow.preis_eur_t),
        aktiv: editRow.aktiv,
        notiz: editRow.notiz || null,
      }
      if (editRow.id) {
        await updateFrachttarif(editRow.id, payload)
      } else {
        await createFrachttarif(payload)
      }
      setEditRow(null)
      await load()
    } catch {
      setError('Speichern fehlgeschlagen.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    setSaving(true)
    try {
      await deleteFrachttarif(deleteId)
      setDeleteId(null)
      await load()
    } catch {
      setError('Löschen fehlgeschlagen.')
    } finally {
      setSaving(false)
    }
  }

  const field = <K extends keyof EditRow>(key: K) => ({
    value: editRow ? String(editRow[key] ?? '') : '',
    onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
      setEditRow((prev) => prev ? { ...prev, [key]: key === 'preis_eur_t' ? e.target.value : e.target.value } : prev),
  })

  const activeRows = rows.filter((row) => row.aktiv)
  const inactiveRows = rows.filter((row) => !row.aktiv)
  const missingNotes = rows.filter((row) => !row.notiz)
  const hasTariffStopper = rows.length === 0 || inactiveRows.length > 0 || Boolean(error)
  const nextTariffAction = error
    ? 'Fehler beim Laden klaeren und Tarife erneut aktualisieren.'
    : rows.length === 0
      ? 'Ersten Frachttarif fuer PLZ-Bereich, Spediteur und EUR/t anlegen.'
      : inactiveRows.length > 0
        ? `${inactiveRows.length} inaktive Frachttarife pruefen und Ersatzspediteur festlegen.`
        : missingNotes.length > 0
          ? `${missingNotes.length} Tarife ohne Notiz pruefen und Nachweis zur Preisbasis ergaenzen.`
          : 'Tarife sind arbeitsfaehig; naechste Frachtentscheidung kann gegen die Liste geprueft werden.'

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-4 space-y-4 text-[13px]">
        <RoleFocusBar roles={freightTariffRoles} value={roleFocus} onChange={setRoleFocus} visibleCount={rows.length} totalCount={rows.length} title="Wer klaert den Frachttarif?" />
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
          <ManagementDecisionPanel
            decision={{
              allowed: !hasTariffStopper,
              allowedLabel: 'Tarife arbeitsfaehig',
              blockedLabel: 'Tarifklaerung offen',
              summary: hasTariffStopper
                ? 'Mindestens ein Frachttarif ist offen, inaktiv oder nicht ladbar. Disposition und Einkauf muessen die Route klaeren, bevor die Frachtkosten ungeprueft verwendet werden.'
                : `${activeRows.length} aktive Frachttarife sind verfuegbar und koennen fuer Disposition und Kostenpruefung genutzt werden.`,
              blockerCount: (rows.length === 0 ? 1 : 0) + inactiveRows.length + (error ? 1 : 0),
              nextFocus: inactiveRows[0]?.spediteur ?? (rows.length === 0 ? 'Ersten Tarif anlegen' : 'Tarifnotizen pruefen'),
              template: { label: 'Frachttarif-Pruefprotokoll', href: '/docs/logistik/frachttarif-pruefprotokoll.md' },
            }}
          />
          <div className="space-y-4">
            <NextActionPanel action={nextTariffAction} tone={hasTariffStopper ? 'amber' : 'emerald'} />
            <EvidenceTemplateLink link={{ label: 'Speditionspreis-Nachweis', href: '/docs/logistik/speditionspreis-nachweis.md' }} />
          </div>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <OperationalTaskPlan
            title="Pruefplan fuer Frachtpreise"
            items={[
              { label: 'Tarife laden', done: !loading && !error, hint: error ?? `${rows.length} Tarif(e) in der aktuellen Sicht.` },
              { label: 'Aktive Spediteure pruefen', done: activeRows.length > 0, hint: `${activeRows.length} aktive und ${inactiveRows.length} inaktive Tarife.` },
              { label: 'Preis und PLZ-Bereich pflegen', done: rows.every((row) => row.plz_von && row.plz_bis && Number(row.preis_eur_t) > 0), hint: 'PLZ von/bis, Spediteur und EUR/t muessen gefuellt sein.' },
              { label: 'Preisnachweis halten', done: missingNotes.length === 0 && rows.length > 0, hint: missingNotes.length > 0 ? `${missingNotes.length} Tarife ohne Notiz oder Preisbasis.` : 'Notizen sind als Mindestnachweis gepflegt.' },
            ]}
          />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'create', label: 'Tarif anlegen', available: true, hint: 'Neue PLZ-/Spediteur-Tarife koennen angelegt werden.' },
              { key: 'read', label: 'Tarife lesen', available: true, hint: 'PLZ-Bereich, Spediteur, Preis und Aktivstatus sind sichtbar.' },
              { key: 'update', label: 'Tarif bearbeiten', available: true, hint: 'Bestehende Tarife koennen geaendert werden.' },
              { key: 'delete', label: 'Tarif loeschen', available: true, hint: 'Loeschen laeuft ueber eine Rueckfrage.' },
              { key: 'evidence', label: 'Preisnachweis', available: true, hint: 'Vorlage fuer Preisbasis und Freigabe ist verlinkt.' },
              { key: 'audit', label: 'Aenderung nachvollziehen', available: false, hint: 'Eigene Audit-Zeitleiste ist noch nicht angebunden.' },
            ]}
          />
        </div>
      </div>

      <div className="mb-2 text-[12px] font-semibold uppercase">Speditionen / Fracht-Preise (nach PLZ)</div>

      {error && (
        <div className="mb-2 border border-red-400 bg-red-50 px-2 py-1 text-red-700">{error}</div>
      )}

      {/* Toolbar */}
      <div className="mb-2 flex gap-1">
        <button onClick={openNew} className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 hover:bg-[#ddd]">
          Neu
        </button>
        <button onClick={load} className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 hover:bg-[#ddd]">
          Aktualisieren
        </button>
      </div>

      {/* Table */}
      <div className="border border-[#bdbdbd] bg-white">
        <div className="grid grid-cols-[90px_90px_1fr_90px_50px_80px] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px] font-semibold">
          <span>PLZ von</span>
          <span>PLZ bis</span>
          <span>Spediteur</span>
          <span>EUR/t</span>
          <span>Aktiv</span>
          <span></span>
        </div>

        {loading && (
          <div className="px-2 py-4 text-[#888]">Lade...</div>
        )}

        {!loading && rows.length === 0 && (
          <div className="px-2 py-4 text-[#888]">Keine Einträge vorhanden.</div>
        )}

        {!loading && rows.map((row) => (
          <div
            key={row.id}
            className="grid grid-cols-[90px_90px_1fr_90px_50px_80px] border-b border-[#f0f0f0] px-1 py-[2px] hover:bg-[#f5f5f5]"
          >
            <span>{row.plz_von}</span>
            <span>{row.plz_bis}</span>
            <span>{row.spediteur}</span>
            <span className="text-right pr-2">{Number(row.preis_eur_t).toFixed(2)}</span>
            <span>{row.aktiv ? 'Ja' : 'Nein'}</span>
            <span className="flex gap-1">
              <button
                onClick={() => openEdit(row)}
                className="h-4 border border-[#9b9b9b] bg-[#ececec] px-1 hover:bg-[#ddd]"
              >
                Bearb.
              </button>
              <button
                onClick={() => setDeleteId(row.id)}
                className="h-4 border border-[#e88] bg-[#fdd] px-1 hover:bg-[#fbb]"
              >
                Del
              </button>
            </span>
          </div>
        ))}
      </div>

      {/* Edit Dialog */}
      {editRow !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="w-[380px] border border-[#9b9b9b] bg-white shadow-lg">
            <div className="border-b border-[#d0d0d0] bg-[#f3f3f3] px-3 py-1 text-[11px] font-semibold uppercase">
              {editRow.id ? 'Frachttarif bearbeiten' : 'Neuer Frachttarif'}
            </div>
            <div className="space-y-2 p-3">
              <div className="grid grid-cols-2 gap-2">
                <label className="flex flex-col gap-[2px]">
                  <span className="text-[10px] text-[#555]">PLZ von</span>
                  <input
                    ref={firstInputRef}
                    className="h-5 border border-[#bdbdbd] px-1"
                    {...field('plz_von')}
                  />
                </label>
                <label className="flex flex-col gap-[2px]">
                  <span className="text-[10px] text-[#555]">PLZ bis</span>
                  <input className="h-5 border border-[#bdbdbd] px-1" {...field('plz_bis')} />
                </label>
              </div>
              <label className="flex flex-col gap-[2px]">
                <span className="text-[10px] text-[#555]">Spediteur</span>
                <input className="h-5 w-full border border-[#bdbdbd] px-1" {...field('spediteur')} />
              </label>
              <label className="flex flex-col gap-[2px]">
                <span className="text-[10px] text-[#555]">Preis EUR/t</span>
                <input
                  type="number"
                  step="0.0001"
                  min="0"
                  className="h-5 w-full border border-[#bdbdbd] px-1"
                  {...field('preis_eur_t')}
                />
              </label>
              <label className="flex flex-col gap-[2px]">
                <span className="text-[10px] text-[#555]">Notiz</span>
                <input className="h-5 w-full border border-[#bdbdbd] px-1" {...field('notiz')} />
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={editRow.aktiv}
                  onChange={(e) => setEditRow((prev) => prev ? { ...prev, aktiv: e.target.checked } : prev)}
                />
                <span className="text-[10px] text-[#555]">Aktiv</span>
              </label>
            </div>
            <div className="flex justify-end gap-2 border-t border-[#d0d0d0] px-3 py-2">
              <button
                onClick={() => setEditRow(null)}
                className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3 hover:bg-[#ddd]"
                disabled={saving}
              >
                Abbrechen
              </button>
              <button
                onClick={handleSave}
                className="h-5 border border-[#3a7abf] bg-[#dde8f5] px-3 hover:bg-[#c8dcf0]"
                disabled={saving}
              >
                {saving ? 'Speichere...' : 'Speichern'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {deleteId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="w-[300px] border border-[#9b9b9b] bg-white shadow-lg">
            <div className="border-b border-[#d0d0d0] bg-[#f3f3f3] px-3 py-1 text-[11px] font-semibold uppercase">
              Löschen bestätigen
            </div>
            <div className="p-3 text-[11px]">Frachttarif wirklich löschen?</div>
            <div className="flex justify-end gap-2 border-t border-[#d0d0d0] px-3 py-2">
              <button
                onClick={() => setDeleteId(null)}
                className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3 hover:bg-[#ddd]"
                disabled={saving}
              >
                Abbrechen
              </button>
              <button
                onClick={handleDelete}
                className="h-5 border border-[#c03030] bg-[#fdd] px-3 hover:bg-[#fbb]"
                disabled={saving}
              >
                {saving ? '...' : 'Löschen'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
