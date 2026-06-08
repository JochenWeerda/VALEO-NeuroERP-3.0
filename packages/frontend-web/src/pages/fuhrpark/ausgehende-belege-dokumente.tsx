import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createFuhrparkAusgehendesDokument,
  deleteFuhrparkAusgehendesDokument,
  listFuhrparkAusgehendeDokumente,
  updateFuhrparkAusgehendesDokument,
  type FuhrparkAusgehendesDokument,
} from '@/lib/api/fuhrpark'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type DokumentForm = {
  beleg_typ: string
  formular: string
  ziel_modul: string
  beschreibung: string
  aktiv: boolean
}
type FleetDocumentRole = 'fuhrpark' | 'versand' | 'produktion' | 'it'

const fleetDocumentRoles = [
  { id: 'fuhrpark', label: 'Fuhrpark', description: 'Pflegt Belegtypen, Formulare und Zielmodule fuer Fahrzeugprozesse.' },
  { id: 'versand', label: 'Versand', description: 'Prueft, ob passende Versand- und Frachtdokumente erreichbar sind.' },
  { id: 'produktion', label: 'Produktion', description: 'Prueft, ob produktionsnahe Dokumente sauber verlinkt sind.' },
  { id: 'it', label: 'IT', description: 'Klaert Formular, Zielmodul und technische Druckpfade.' },
] satisfies Array<{ id: FleetDocumentRole; label: string; description: string }>

const EMPTY_FORM: DokumentForm = {
  beleg_typ: '',
  formular: '',
  ziel_modul: '',
  beschreibung: '',
  aktiv: true,
}

const quickLinks = [
  { label: 'Frachtdokumente', path: '/versand/frachtdokumente' },
  { label: 'Paket-Etikett', path: '/versand/paket-etikett' },
  { label: 'Versand-Avis', path: '/versand/versand-avis' },
  { label: 'Produktions-Dokumente', path: '/produktion/produktions-dokumente-drucken' },
  { label: 'Kommissions-Aufträge', path: '/verkauf/kommissions-auftraege' },
  { label: 'Betriebs-Aufträge', path: '/verkauf/betriebs-auftraege' },
]

export default function AusgehendeBelegeDokumentePage(): JSX.Element {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selected, setSelected] = useState<FuhrparkAusgehendesDokument | null>(null)
  const [form, setForm] = useState<DokumentForm>(EMPTY_FORM)
  const [roleFocus, setRoleFocus] = useState<FleetDocumentRole>('fuhrpark')

  const { data: rows = [] } = useQuery({
    queryKey: ['fuhrpark', 'ausgehende-dokumente'],
    queryFn: listFuhrparkAusgehendeDokumente,
  })

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        beleg_typ: form.beleg_typ,
        formular: form.formular || undefined,
        ziel_modul: form.ziel_modul || undefined,
        beschreibung: form.beschreibung || undefined,
        aktiv: form.aktiv,
      }
      if (selected) {
        return updateFuhrparkAusgehendesDokument(selected.id, payload)
      }
      return createFuhrparkAusgehendesDokument(payload)
    },
    onSuccess: () => {
      setForm(EMPTY_FORM)
      setSelected(null)
      void queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'ausgehende-dokumente'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => deleteFuhrparkAusgehendesDokument(id),
    onSuccess: () => {
      setForm(EMPTY_FORM)
      setSelected(null)
      void queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'ausgehende-dokumente'] })
    },
  })

  const sortedRows = useMemo(() => [...rows].sort((a, b) => a.beleg_typ.localeCompare(b.beleg_typ, 'de')), [rows])
  const activeRows = sortedRows.filter((row) => row.aktiv)
  const missingFormula = sortedRows.filter((row) => !row.formular)
  const documentBlockers = (sortedRows.length === 0 ? 1 : 0) + missingFormula.length
  const nextDocumentAction = sortedRows.length === 0
    ? 'Ersten Belegtyp mit Formular und Zielmodul anlegen.'
    : missingFormula.length > 0
      ? `${missingFormula.length} Belegtyp(en) ohne Formular pruefen.`
      : 'Dokumentensteuerung ist arbeitsfaehig; Quicklink oder Belegtyp pruefen.'

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">Ausgehende Belege und Dokumente</div>

      <div className="mb-4 space-y-4 text-[13px]">
        <RoleFocusBar roles={fleetDocumentRoles} value={roleFocus} onChange={setRoleFocus} visibleCount={sortedRows.length} totalCount={sortedRows.length} title="Wer pflegt die Fuhrpark-Dokumente?" />
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
          <ManagementDecisionPanel
            decision={{
              allowed: documentBlockers === 0,
              allowedLabel: 'Dokumentsteuerung bereit',
              blockedLabel: 'Dokumente pruefen',
              summary: documentBlockers > 0
                ? `${missingFormula.length} Belegtyp(en) haben kein Formular oder es fehlen Belegtypen.`
                : `${activeRows.length} aktive Dokumentsteuerungen sind fuer Fuhrpark- und Folgeprozesse verfuegbar.`,
              blockerCount: documentBlockers,
              nextFocus: nextDocumentAction,
              template: { label: 'Fuhrpark-Dokumentsteuerung', href: '/docs/fuhrpark/dokumentsteuerung.md' },
            }}
          />
          <div className="space-y-4">
            <NextActionPanel action={nextDocumentAction} tone={documentBlockers > 0 ? 'amber' : 'emerald'} />
            <EvidenceTemplateLink link={{ label: 'Dokument- und Formularnachweis', href: '/docs/fuhrpark/dokumentnachweis.md' }} />
          </div>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <OperationalTaskPlan
            title="Dokumentplan"
            items={[
              { label: 'Belegtypen pflegen', done: sortedRows.length > 0, hint: `${sortedRows.length} Belegtyp(en) vorhanden.` },
              { label: 'Formulare pruefen', done: missingFormula.length === 0, hint: missingFormula.length > 0 ? `${missingFormula.length} Eintraege ohne Formular.` : 'Alle Eintraege haben ein Formular.' },
              { label: 'Aktive Dokumente klaeren', done: activeRows.length > 0, hint: `${activeRows.length} aktive Dokumentsteuerungen.` },
              { label: 'Quicklinks pruefen', done: quickLinks.length > 0, hint: `${quickLinks.length} Folgearbeitsflaechen erreichbar.` },
            ]}
          />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'create', label: 'Belegtyp anlegen', available: true, hint: 'Neu und Speichern legen neue Steuerungen an.' },
              { key: 'read', label: 'Dokumente lesen', available: true, hint: 'Belegtyp, Formular, Zielmodul und Aktivstatus sind sichtbar.' },
              { key: 'update', label: 'Steuerung bearbeiten', available: true, hint: 'Auswahl in der Liste fuellt das Formular.' },
              { key: 'delete', label: 'Loeschen', available: true, hint: 'Ausgewaehlte Steuerung kann geloescht werden.' },
              { key: 'evidence', label: 'Nachweis', available: true, hint: 'Dokumentnachweis ist verlinkt.' },
              { key: 'audit', label: 'Aktivstatus', available: true, hint: 'Aktiv/inaktiv ist je Belegtyp sichtbar.' },
            ]}
          />
        </div>
      </div>

      <div className="mb-3 grid grid-cols-1 gap-2 md:grid-cols-3">
        {quickLinks.map((entry) => (
          <button
            key={entry.path}
            type="button"
            onClick={() => navigate(entry.path)}
            className="border border-[#b8b8b8] bg-[#f2f2f2] px-3 py-2 text-left hover:bg-[#e8f1ff]"
          >
            {entry.label}
          </button>
        ))}
      </div>

      <div className="mb-2 grid grid-cols-[90px_160px_80px_120px_70px_1fr] items-center gap-1">
        <label>Beleg-Typ:</label>
        <input
          value={form.beleg_typ}
          onChange={(e) => setForm((prev) => ({ ...prev, beleg_typ: e.target.value }))}
          className="h-5 border border-[#a8a8a8] bg-white px-1"
        />
        <label>Formular:</label>
        <input
          value={form.formular}
          onChange={(e) => setForm((prev) => ({ ...prev, formular: e.target.value }))}
          className="h-5 border border-[#a8a8a8] bg-white px-1"
        />
        <label>Aktiv:</label>
        <label className="flex items-center gap-1">
          <input
            type="checkbox"
            checked={form.aktiv}
            onChange={(e) => setForm((prev) => ({ ...prev, aktiv: e.target.checked }))}
            className="h-3 w-3"
          />
          ja
        </label>
      </div>

      <div className="mb-2 grid grid-cols-[90px_1fr] items-center gap-1">
        <label>Ziel-Modul:</label>
        <input
          value={form.ziel_modul}
          onChange={(e) => setForm((prev) => ({ ...prev, ziel_modul: e.target.value }))}
          className="h-5 border border-[#a8a8a8] bg-white px-1"
        />
        <label>Beschreibung:</label>
        <input
          value={form.beschreibung}
          onChange={(e) => setForm((prev) => ({ ...prev, beschreibung: e.target.value }))}
          className="h-5 border border-[#a8a8a8] bg-white px-1"
        />
      </div>

      <div className="border border-[#bdbdbd] bg-white">
        <div className="grid grid-cols-[180px_90px_220px_1fr_80px] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px]">
          <span>Beleg-Typ</span>
          <span>Formular</span>
          <span>Ziel-Modul</span>
          <span>Beschreibung</span>
          <span>Aktiv</span>
        </div>
        {sortedRows.map((row) => (
          <button
            key={row.id}
            type="button"
            onClick={() => {
              setSelected(row)
              setForm({
                beleg_typ: row.beleg_typ,
                formular: row.formular ?? '',
                ziel_modul: row.ziel_modul ?? '',
                beschreibung: row.beschreibung ?? '',
                aktiv: row.aktiv,
              })
            }}
            className={`grid w-full grid-cols-[180px_90px_220px_1fr_80px] px-1 py-[2px] text-left ${selected?.id === row.id ? 'bg-[#0078d7] text-white' : 'bg-white hover:bg-[#edf5ff]'}`}
          >
            <span>{row.beleg_typ}</span>
            <span>{row.formular}</span>
            <span>{row.ziel_modul}</span>
            <span>{row.beschreibung}</span>
            <span>{row.aktiv ? 'JA' : 'NEIN'}</span>
          </button>
        ))}
        <div className="h-[330px] bg-white" />
      </div>

      <div className="mt-2 flex justify-between">
        <div className="flex gap-1">
          <button
            onClick={() => {
              setSelected(null)
              setForm(EMPTY_FORM)
            }}
            className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2"
          >
            Neu
          </button>
          <button
            onClick={() => saveMutation.mutate()}
            disabled={!form.beleg_typ.trim()}
            className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 disabled:opacity-50"
          >
            Speichern
          </button>
          <button
            onClick={() => {
              if (selected) deleteMutation.mutate(selected.id)
            }}
            disabled={!selected}
            className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 disabled:opacity-50"
          >
            Löschen
          </button>
        </div>
      </div>
    </div>
  )
}
