import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Skeleton } from '@/components/ui/skeleton'
import { listFuhrparkFahrzeuge, listFuhrparkRechnungen } from '@/lib/api/fuhrpark'

const fmt = (n: number) =>
  n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

type KostenRow = {
  kennzeichen: string
  steuer: number
  versicherung: number
  reparatur: number
  sonstige: number
  total: number
}

export default function FuhrparkAuswertungKostenPage(): JSX.Element {
  const currentYear = new Date().getFullYear()
  const [jahr, setJahr] = useState(String(currentYear))
  const [monatVon, setMonatVon] = useState('01')
  const [betrieb, setBetrieb] = useState('')

  const { data: rechnungen = [], isLoading: loadR } = useQuery({
    queryKey: ['fuhrpark', 'rechnungen'],
    queryFn: listFuhrparkRechnungen,
  })

  const { data: fahrzeuge = [], isLoading: loadF } = useQuery({
    queryKey: ['fuhrpark', 'fahrzeuge'],
    queryFn: listFuhrparkFahrzeuge,
  })

  const isLoading = loadR || loadF

  // Kennzeichen → Betrieb für Betrieb-Filter
  const kzToBetrieb = useMemo(
    () => new Map(fahrzeuge.map(f => [f.kennzeichen, f.betrieb ?? ''])),
    [fahrzeuge],
  )

  const rows = useMemo((): KostenRow[] => {
    const jahrNum = parseInt(jahr)
    const monatVonNum = parseInt(monatVon) || 1

    // Rechnungen filtern
    const filtered = rechnungen.filter(r => {
      const d = new Date(r.datum)
      if (d.getFullYear() !== jahrNum) return false
      if (d.getMonth() + 1 < monatVonNum) return false
      if (betrieb) {
        const kz = r.fahrzeug_kennzeichen ?? ''
        if ((kzToBetrieb.get(kz) ?? '') !== betrieb) return false
      }
      return true
    })

    // Gruppieren nach Kennzeichen
    const byKz = new Map<string, KostenRow>()
    for (const r of filtered) {
      const kz = r.fahrzeug_kennzeichen ?? 'Unbekannt'
      if (!byKz.has(kz)) byKz.set(kz, { kennzeichen: kz, steuer: 0, versicherung: 0, reparatur: 0, sonstige: 0, total: 0 })
      const row = byKz.get(kz)!
      const art = (r.kostenart ?? '').toLowerCase()
      const betrag = r.betrag_eur ?? 0
      if (art.includes('steuer')) row.steuer += betrag
      else if (art.includes('versicherung')) row.versicherung += betrag
      else if (art.includes('reparatur') || art.includes('werkstatt') || art.includes('instand')) row.reparatur += betrag
      else row.sonstige += betrag
      row.total += betrag
    }

    // Fahrzeug-Stammdaten als Fallback für Fahrzeuge ohne Buchungen
    for (const f of fahrzeuge) {
      if (betrieb && (f.betrieb ?? '') !== betrieb) continue
      if (!byKz.has(f.kennzeichen)) {
        if (!f.kfz_steuer_eur && !f.versicherung_satz_eur_monat) continue
        byKz.set(f.kennzeichen, { kennzeichen: f.kennzeichen, steuer: 0, versicherung: 0, reparatur: 0, sonstige: 0, total: 0 })
      }
      const row = byKz.get(f.kennzeichen)!
      if (row.steuer === 0 && f.kfz_steuer_eur) {
        row.steuer += f.kfz_steuer_eur
        row.total += f.kfz_steuer_eur
      }
      if (row.versicherung === 0 && f.versicherung_satz_eur_monat) {
        const monate = 13 - monatVonNum
        const beitrag = f.versicherung_satz_eur_monat * monate
        row.versicherung += beitrag
        row.total += beitrag
      }
    }

    return Array.from(byKz.values()).sort((a, b) => b.total - a.total)
  }, [rechnungen, fahrzeuge, jahr, monatVon, betrieb, kzToBetrieb])

  // Summenzeile
  const summe = useMemo((): KostenRow => rows.reduce(
    (acc, r) => ({
      kennzeichen: 'Gesamt',
      steuer: acc.steuer + r.steuer,
      versicherung: acc.versicherung + r.versicherung,
      reparatur: acc.reparatur + r.reparatur,
      sonstige: acc.sonstige + r.sonstige,
      total: acc.total + r.total,
    }),
    { kennzeichen: 'Gesamt', steuer: 0, versicherung: 0, reparatur: 0, sonstige: 0, total: 0 },
  ), [rows])

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="border border-[#bdbdbd] bg-[#efefef] p-2">
        <div className="mb-2 text-[12px] font-semibold uppercase">Fuhrpark - Auswertung Kosten pro Fahrzeug</div>

        <div className="mb-2 grid grid-cols-[92px_100px_16px_92px_100px_16px_86px_1fr_74px] items-center gap-1">
          <label>Leistungsjahr:</label>
          <input
            className="h-5 border border-[#a8a8a8] bg-white px-1"
            value={jahr}
            onChange={e => setJahr(e.target.value)}
          />
          <div />
          <label>Monat von:</label>
          <input
            className="h-5 border border-[#a8a8a8] bg-white px-1"
            value={monatVon}
            onChange={e => setMonatVon(e.target.value)}
          />
          <div />
          <label>Betrieb:</label>
          <input
            className="h-5 border border-[#a8a8a8] bg-white px-1"
            value={betrieb}
            onChange={e => setBetrieb(e.target.value)}
          />
          <div />
        </div>

        <div className="border border-[#bdbdbd] bg-white">
          <div className="grid grid-cols-[120px_110px_110px_110px_110px] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px] font-semibold">
            <span>Fahrzeug</span>
            <span className="text-right">KFZ-Steuer EUR</span>
            <span className="text-right">Versicherung EUR</span>
            <span className="text-right">Reparatur EUR</span>
            <span className="text-right">Gesamt EUR</span>
          </div>

          {isLoading ? (
            <div className="p-2 space-y-1">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-5 w-full" />
              ))}
            </div>
          ) : rows.length === 0 ? (
            <div className="px-2 py-4 text-center text-muted-foreground text-[11px]">
              Keine Kostenbuchungen für {jahr} ab Monat {monatVon} gefunden.
            </div>
          ) : (
            <>
              {rows.map((row, index) => (
                <div
                  key={row.kennzeichen}
                  className={`grid grid-cols-[120px_110px_110px_110px_110px] px-1 py-[2px] ${
                    index === 0 ? 'bg-[#0078d7] text-white' : 'bg-white'
                  }`}
                >
                  <span>{row.kennzeichen}</span>
                  <span className="text-right">{fmt(row.steuer)}</span>
                  <span className="text-right">{fmt(row.versicherung)}</span>
                  <span className="text-right">{fmt(row.reparatur)}</span>
                  <span className="text-right font-semibold">{fmt(row.total)}</span>
                </div>
              ))}
              {/* Summenzeile */}
              <div className="grid grid-cols-[120px_110px_110px_110px_110px] border-t border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px] font-semibold">
                <span>Gesamt</span>
                <span className="text-right">{fmt(summe.steuer)}</span>
                <span className="text-right">{fmt(summe.versicherung)}</span>
                <span className="text-right">{fmt(summe.reparatur)}</span>
                <span className="text-right">{fmt(summe.total)}</span>
              </div>
            </>
          )}

          <div className="h-[380px] bg-white" />
        </div>

        <div className="mt-2 flex justify-end gap-1">
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Vorschau</button>
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Drucken</button>
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Export</button>
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Schließen</button>
        </div>
      </div>
    </div>
  )
}
