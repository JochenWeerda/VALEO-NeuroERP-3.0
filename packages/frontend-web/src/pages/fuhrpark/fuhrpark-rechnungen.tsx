import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createFuhrparkRechnung,
  deleteFuhrparkRechnung,
  listFuhrparkRechnungen,
  type FuhrparkRechnung,
} from '@/lib/api/fuhrpark'

type RechnungForm = {
  rechnungs_nr: string
  datum: string
  fahrzeug_kennzeichen: string
  sachkonto: string
  kostenart: string
  betrag_eur: number
  notiz: string
}

const EMPTY_FORM: RechnungForm = {
  rechnungs_nr: '',
  datum: new Date().toISOString().slice(0, 10),
  fahrzeug_kennzeichen: '',
  sachkonto: '',
  kostenart: '',
  betrag_eur: 0,
  notiz: '',
}

function toApiDate(inputDate: string): string {
  return `${inputDate}T00:00:00.000Z`
}

export default function FuhrparkRechnungenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<RechnungForm>(EMPTY_FORM)
  const [selected, setSelected] = useState<FuhrparkRechnung | null>(null)

  const { data: rows = [] } = useQuery({
    queryKey: ['fuhrpark', 'rechnungen'],
    queryFn: listFuhrparkRechnungen,
  })

  const createMutation = useMutation({
    mutationFn: async () =>
      createFuhrparkRechnung({
        rechnungs_nr: form.rechnungs_nr,
        datum: toApiDate(form.datum),
        fahrzeug_kennzeichen: form.fahrzeug_kennzeichen || undefined,
        sachkonto: form.sachkonto || undefined,
        kostenart: form.kostenart || undefined,
        betrag_eur: form.betrag_eur,
        notiz: form.notiz || undefined,
      }),
    onSuccess: () => {
      setForm(EMPTY_FORM)
      setSelected(null)
      void queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'rechnungen'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => deleteFuhrparkRechnung(id),
    onSuccess: () => {
      setSelected(null)
      void queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'rechnungen'] })
    },
  })

  const visibleRows = useMemo(
    () => [...rows].sort((a, b) => String(b.datum).localeCompare(String(a.datum))),
    [rows],
  )

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="border border-[#bdbdbd] bg-[#efefef] p-2">
        <div className="mb-2 text-[12px] font-semibold uppercase">Fuhrpark - Rechnungen</div>

        <div className="mb-2 grid grid-cols-[90px_120px_90px_120px_80px_120px_80px_120px] items-center gap-1">
          <label>Rechnungs-Nr:</label>
          <input
            value={form.rechnungs_nr}
            onChange={(e) => setForm((prev) => ({ ...prev, rechnungs_nr: e.target.value }))}
            className="h-5 border border-[#a8a8a8] bg-white px-1"
          />
          <label>Datum:</label>
          <input
            type="date"
            value={form.datum}
            onChange={(e) => setForm((prev) => ({ ...prev, datum: e.target.value }))}
            className="h-5 border border-[#a8a8a8] bg-white px-1"
          />
          <label>Fahrzeug:</label>
          <input
            value={form.fahrzeug_kennzeichen}
            onChange={(e) => setForm((prev) => ({ ...prev, fahrzeug_kennzeichen: e.target.value }))}
            className="h-5 border border-[#a8a8a8] bg-white px-1"
          />
          <label>Sachkonto:</label>
          <input
            value={form.sachkonto}
            onChange={(e) => setForm((prev) => ({ ...prev, sachkonto: e.target.value }))}
            className="h-5 border border-[#a8a8a8] bg-white px-1"
          />
          <label>Kostenart:</label>
          <input
            value={form.kostenart}
            onChange={(e) => setForm((prev) => ({ ...prev, kostenart: e.target.value }))}
            className="h-5 border border-[#a8a8a8] bg-white px-1"
          />
          <label>Betrag EUR:</label>
          <input
            type="number"
            value={form.betrag_eur}
            onChange={(e) => setForm((prev) => ({ ...prev, betrag_eur: Number(e.target.value) || 0 }))}
            className="h-5 border border-[#a8a8a8] bg-white px-1"
          />
        </div>

        <div className="mb-2 grid grid-cols-[90px_1fr] items-center gap-1">
          <label>Notiz:</label>
          <input
            value={form.notiz}
            onChange={(e) => setForm((prev) => ({ ...prev, notiz: e.target.value }))}
            className="h-5 border border-[#a8a8a8] bg-white px-1"
          />
        </div>

        <div className="border border-[#bdbdbd] bg-white">
          <div className="grid grid-cols-[120px_90px_100px_90px_120px_100px_1fr] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px]">
            <span>Rechnungs-Nr.</span>
            <span>Datum</span>
            <span>Fahrzeug</span>
            <span>Sachkonto</span>
            <span>Kostenart</span>
            <span>Betrag EUR</span>
            <span>Notiz</span>
          </div>

          {visibleRows.map((row) => (
            <button
              key={row.id}
              type="button"
              onClick={() => {
                setSelected(row)
                setForm({
                  rechnungs_nr: row.rechnungs_nr,
                  datum: String(row.datum).slice(0, 10),
                  fahrzeug_kennzeichen: row.fahrzeug_kennzeichen ?? '',
                  sachkonto: row.sachkonto ?? '',
                  kostenart: row.kostenart ?? '',
                  betrag_eur: Number(row.betrag_eur ?? 0),
                  notiz: row.notiz ?? '',
                })
              }}
              className={`grid w-full grid-cols-[120px_90px_100px_90px_120px_100px_1fr] px-1 py-[2px] text-left ${selected?.id === row.id ? 'bg-[#0078d7] text-white' : 'bg-white hover:bg-[#edf5ff]'}`}
            >
              <span>{row.rechnungs_nr}</span>
              <span>{String(row.datum).slice(0, 10)}</span>
              <span>{row.fahrzeug_kennzeichen}</span>
              <span>{row.sachkonto}</span>
              <span>{row.kostenart}</span>
              <span className="text-right">{Number(row.betrag_eur).toFixed(2)}</span>
              <span>{row.notiz}</span>
            </button>
          ))}

          <div className="h-[360px] bg-white" />
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
              onClick={() => createMutation.mutate()}
              disabled={!form.rechnungs_nr.trim() || form.betrag_eur <= 0}
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
          <div className="flex gap-1">
            <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Drucken</button>
            <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Schließen</button>
          </div>
        </div>
      </div>
    </div>
  )
}
