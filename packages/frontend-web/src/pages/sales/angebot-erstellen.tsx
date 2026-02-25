import { useMemo, useState } from 'react'

type AngebotRow = {
  nr: string
  datum: string
  kunde: string
}

export default function AngebotErstellenPage(): JSX.Element {
  const [angebotNr, setAngebotNr] = useState('')
  const [datum, setDatum] = useState('25.02.2026')
  const [kunde, setKunde] = useState('')
  const [search, setSearch] = useState('')

  const angebote = useMemo<AngebotRow[]>(
    () => [
      { nr: '2500005', datum: '25.11.2025', kunde: 'Niedersachsen Port, Emden' },
      { nr: '2500004', datum: '06.08.2025', kunde: 'Kromminga Jens-Martin' },
      { nr: '2500003', datum: '14.07.2025', kunde: 'Hinrichs Ewald' },
      { nr: '2500002', datum: '14.07.2025', kunde: 'Niedersachsen Port, Emden' },
      { nr: '2500001', datum: '17.06.2025', kunde: 'Rob-Schoeningh Betriebs KG' },
      { nr: '2400010', datum: '25.06.2024', kunde: 'Neelen Hinrich Groevehorn 1a' },
      { nr: '2300009', datum: '12.10.2023', kunde: 'Feuerwehr Wybelsum' },
    ],
    [],
  )

  const filtered = angebote.filter(
    (row) =>
      row.nr.toLowerCase().includes(search.toLowerCase()) ||
      row.kunde.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <div className="min-h-full bg-[#e9e9e9] text-[11px] leading-none text-black">
      <div className="border-b border-[#cfcfcf] bg-[#efefef] p-2">
        <div className="flex items-center gap-4 text-[10px] uppercase text-[#333]">
          <span>Datei</span>
          <span>Funktionen</span>
          <span>Allgemein</span>
          <span>Erfassung</span>
          <span>Abrechnung</span>
          <span>Lager</span>
          <span>Fenster</span>
        </div>
      </div>

      <div className="border-b border-[#b3b3b3] bg-[#f3f3f3] px-1 py-2">
        <div className="flex flex-wrap items-end gap-2 text-[10px]">
          {['Kontrakt', 'Bestellung', 'Lieferschein', 'Rechnung', 'Angebot', 'Auftrag'].map((item) => (
            <button key={item} className="h-9 min-w-[66px] border border-[#bdbdbd] bg-white px-2 text-[10px]">
              {item}
            </button>
          ))}
        </div>
      </div>

      <div className="border-y border-[#a38e00] bg-[#f3ea08] px-1 py-1 text-[12px] font-bold uppercase text-black">
        Angebot
      </div>

      <div className="space-y-1 border-b border-[#c8c8c8] bg-[#ececec] p-1">
        <div className="grid grid-cols-[80px_140px_26px_110px_120px_40px_70px_60px_90px] items-center gap-1">
          <label>Angebot-Nr.</label>
          <input value={angebotNr} onChange={(e) => setAngebotNr(e.target.value)} className="h-5 border border-[#a8a8a8] bg-[#f5f5f5] px-1" />
          <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          <label>Kunden-Name</label>
          <input value={kunde} onChange={(e) => setKunde(e.target.value)} className="h-5 border border-[#a8a8a8] bg-[#f9f9f9] px-1" />
          <label>VB:</label>
          <input value="" readOnly className="h-5 border border-[#a8a8a8] bg-[#f0f0f0] px-1" />
          <label>Textformat:</label>
          <select className="h-5 border border-[#a8a8a8] bg-[#f0f0f0] px-1">
            <option>Angebot</option>
          </select>
        </div>
        <div className="grid grid-cols-[80px_140px_180px_120px_110px] items-center gap-1">
          <label>Datum:</label>
          <input value={datum} onChange={(e) => setDatum(e.target.value)} className="h-5 border border-[#a8a8a8] bg-[#f9f9f9] px-1" />
          <label className="flex items-center gap-1">
            <input type="checkbox" className="h-3 w-3" />
            Pauschal-Angebot
          </label>
          <label>Status:</label>
          <input value="Offen" readOnly className="h-5 border border-[#a8a8a8] bg-[#f0f0f0] px-1" />
        </div>
      </div>

      <div className="px-1 pt-1">
        <div className="border border-[#bdbdbd] bg-white">
          <div className="grid grid-cols-[40px_40px_60px_1fr_70px_40px_50px_70px_50px] border-b border-[#bdbdbd] bg-[#f3f3f3] px-1 py-[2px]">
            <span>Zeile</span>
            <span>Pos.</span>
            <span>Artikel-Nr.</span>
            <span>Bezeichnung -1-</span>
            <span>Menge</span>
            <span>Einh.</span>
            <span>Einh.-Preis</span>
            <span>Netto-Betr.</span>
            <span>EK-Preis</span>
          </div>
          <div className="h-7 bg-white" />
        </div>
      </div>

      <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/10">
        <div className="w-[350px] border border-[#2a77b5] bg-[#ededed] shadow-[0_6px_20px_rgba(0,0,0,0.25)]">
          <div className="flex items-center justify-between bg-[#007cc3] px-2 py-1 text-white">
            <span>Verkaufs-Angebote</span>
            <button className="px-1">x</button>
          </div>
          <div className="p-2">
            <div className="mb-2 text-[10px] font-semibold uppercase">Verkaufs-Angebote</div>
            <div className="mb-2 flex items-center gap-2">
              <label className="w-8">Suchen:</label>
              <input value={search} onChange={(e) => setSearch(e.target.value)} className="h-5 flex-1 border border-[#86ccff] bg-[#76f06f] px-1" />
            </div>
            <div className="mb-1 flex gap-4 text-[10px]">
              <button className="font-semibold text-[#0066cc]">ANGEBOTE</button>
              <button>AUFTRAEGE</button>
            </div>
            <div className="max-h-[260px] overflow-auto border border-[#b8b8b8] bg-white">
              <div className="grid grid-cols-[70px_80px_1fr] border-b border-[#cfcfcf] bg-[#f3f3f3] px-1 py-[2px]">
                <span>Angebot-Nr.</span>
                <span>Datum</span>
                <span>Kunden-Name</span>
              </div>
              {filtered.map((row, idx) => (
                <button
                  key={row.nr}
                  className={`grid w-full grid-cols-[70px_80px_1fr] px-1 py-[2px] text-left ${idx === 0 ? 'bg-[#0078d7] text-white' : 'bg-white hover:bg-[#eaf4ff]'}`}
                >
                  <span>{row.nr}</span>
                  <span>{row.datum}</span>
                  <span>{row.kunde}</span>
                </button>
              ))}
            </div>
            <div className="mt-2 flex justify-end gap-1">
              <button className="h-5 border border-[#9b9b9b] bg-[#efefef] px-4">OK</button>
              <button className="h-5 border border-[#9b9b9b] bg-[#efefef] px-3">Abbrechen</button>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-1 border-y border-[#bdbdbd] bg-[#efefef] px-1 py-[2px] font-semibold">Positions-Details</div>
      <div className="grid grid-cols-[60px_80px_1fr_100px_60px_70px_60px_60px_80px] gap-1 p-1">
        {['Pos.-Nr.', 'Artikel-Nr.', 'Artikel-Bezeichnung', 'Menge/Gebinde', 'Lagerhalle', 'Listenpreis', 'Rabatt', 'Einh.-Preis', 'Betrag'].map((label) => (
          <label key={label} className="text-[10px]">
            {label}
          </label>
        ))}
        {Array.from({ length: 9 }).map((_, idx) => (
          <input key={idx} value="" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        ))}
      </div>

      <div className="border-y border-[#bdbdbd] bg-[#efefef] px-1 py-[2px] font-semibold">Summen</div>
      <div className="grid grid-cols-[1fr_80px_80px_80px] items-center gap-1 p-1">
        <span>Gewicht: 0 kg</span>
        <input value="Netto" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        <input value="MWSt" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        <input value="Brutto" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
      </div>

      <div className="mt-1 flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex flex-wrap gap-1">
          {['Drucken', 'Unterlagen', 'Dateien', 'Wiedervorlage', 'Angebot loeschen'].map((action) => (
            <button key={action} className="h-5 border border-[#a8a8a8] bg-white px-2 text-[10px]">
              {action}
            </button>
          ))}
        </div>
        <button className="h-5 border border-[#a8a8a8] bg-white px-3 text-[10px]">Beenden</button>
      </div>
    </div>
  )
}
