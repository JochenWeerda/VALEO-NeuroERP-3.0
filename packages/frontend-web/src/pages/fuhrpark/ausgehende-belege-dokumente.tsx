import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
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
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useTouchDevice } from '@/hooks/useTouchDevice'

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
  const isTouch = useTouchDevice()
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
    <div className="min-h-full space-y-4 bg-background p-3 text-foreground md:p-6">
      <div>
        <h1 className="text-2xl font-bold md:text-3xl">Ausgehende Belege und Dokumente</h1>
        <p className="text-muted-foreground">Belegtypen, Formulare und Zielmodule pflegen</p>
      </div>
      {!isTouch ? (
      <div className="mb-4 space-y-4">
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
      ) : null}

      <div className="mb-3 grid grid-cols-1 gap-2 md:grid-cols-3">
        {quickLinks.map((entry) => (
          <Button
            key={entry.path}
            type="button"
            variant="outline"
            className="min-h-touch justify-start touch-manipulation"
            onClick={() => navigate(entry.path)}
          >
            {entry.label}
          </Button>
        ))}
      </div>

      <div className="mb-2 grid grid-cols-1 gap-2 md:grid-cols-[90px_1fr_90px_1fr_70px_auto]">
        <label htmlFor="beleg-typ">Beleg-Typ</label>
        <Input
          id="beleg-typ"
          aria-label="Beleg-Typ"
          className="min-h-touch"
          value={form.beleg_typ}
          onChange={(e) => setForm((prev) => ({ ...prev, beleg_typ: e.target.value }))}
        />
        <label htmlFor="formular">Formular</label>
        <Input
          id="formular"
          aria-label="Formular"
          className="min-h-touch"
          value={form.formular}
          onChange={(e) => setForm((prev) => ({ ...prev, formular: e.target.value }))}
        />
        <label htmlFor="aktiv">Aktiv</label>
        <label className="flex min-h-touch items-center gap-2">
          <input
            id="aktiv"
            type="checkbox"
            checked={form.aktiv}
            onChange={(e) => setForm((prev) => ({ ...prev, aktiv: e.target.checked }))}
            className="h-5 w-5"
          />
          ja
        </label>
      </div>

      <div className="mb-2 grid grid-cols-1 gap-2 md:grid-cols-[90px_1fr]">
        <label htmlFor="ziel-modul">Ziel-Modul</label>
        <Input
          id="ziel-modul"
          aria-label="Ziel-Modul"
          className="min-h-touch"
          value={form.ziel_modul}
          onChange={(e) => setForm((prev) => ({ ...prev, ziel_modul: e.target.value }))}
        />
        <label htmlFor="beschreibung">Beschreibung</label>
        <Input
          id="beschreibung"
          aria-label="Beschreibung"
          className="min-h-touch"
          value={form.beschreibung}
          onChange={(e) => setForm((prev) => ({ ...prev, beschreibung: e.target.value }))}
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
            className={`min-h-11 grid w-full grid-cols-[180px_90px_220px_1fr_80px] px-2 text-left touch-manipulation ${selected?.id === row.id ? 'bg-primary text-primary-foreground' : 'bg-background'}`}
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

      <div className="mt-2 flex flex-wrap gap-2">
          <Button
            variant="outline"
            className="min-h-touch touch-manipulation"
            onClick={() => {
              setSelected(null)
              setForm(EMPTY_FORM)
            }}
          >
            Neu
          </Button>
          <Button
            className="min-h-touch touch-manipulation"
            onClick={() => saveMutation.mutate()}
            disabled={!form.beleg_typ.trim() || saveMutation.isPending}
          >
            Speichern
          </Button>
          <Button
            variant="destructive"
            className="min-h-touch touch-manipulation"
            onClick={() => {
              if (selected) deleteMutation.mutate(selected.id)
            }}
            disabled={!selected || deleteMutation.isPending}
          >
            Loeschen
          </Button>
      </div>
    </div>
  )
}
