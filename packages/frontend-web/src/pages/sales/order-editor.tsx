import { useMemo, useState } from 'react'

type AuftragRow = {
  nr: string
  datum: string
  kunde: string
}

export default function SalesOrderEditorPage(): JSX.Element {
  const [auftragNr, setAuftragNr] = useState('261050')
  const [datum, setDatum] = useState('26.03.2026')
  const [kunde, setKunde] = useState('Berghorst Hermann')
  const [modalOpen, setModalOpen] = useState(true)
  const [search, setSearch] = useState('')

  const rows = useMemo<AuftragRow[]>(
    () => [
      { nr: '261050', datum: '26.03.2026', kunde: 'Berghorst Hermann' },
      { nr: '261049', datum: '26.03.2026', kunde: 'Schimmelpfennig Dirk' },
      { nr: '261048', datum: '26.02.2026', kunde: 'Kromminga Jens-Martin' },
      { nr: '261047', datum: '25.02.2026', kunde: 'Ippen Karl + Partner GbR' },
      { nr: '261046', datum: '25.02.2026', kunde: 'Berkhout Dirk C.' },
      { nr: '261045', datum: '25.02.2026', kunde: 'Suntken Hero' },
      { nr: '261044', datum: '25.02.2026', kunde: 'Rob-Schoeningh Betriebs KG' },
    ],
    [],
  )

  const filtered = rows.filter(
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

      <div className="border-y border-[#1f6f12] bg-[#167c0c] px-1 py-1 text-[12px] font-bold uppercase text-white">
        Auftragsbestaetigung
      </div>

      <div className="space-y-1 border-b border-[#c8c8c8] bg-[#ececec] p-1">
        <div className="grid grid-cols-[80px_140px_26px_110px_120px_40px_70px_60px_90px] items-center gap-1">
          <label>Auftrag-Nr.</label>
          <input value={auftragNr} onChange={(e) => setAuftragNr(e.target.value)} className="h-5 border border-[#a8a8a8] bg-[#76f06f] px-1" />
          <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          <label>Kunden-Name</label>
          <input value={kunde} onChange={(e) => setKunde(e.target.value)} className="h-5 border border-[#a8a8a8] bg-[#f9f9f9] px-1" />
          <label>VB:</label>
          <input value="TBK" readOnly className="h-5 border border-[#a8a8a8] bg-[#f0f0f0] px-1" />
          <label>Textformat:</label>
          <select className="h-5 border border-[#a8a8a8] bg-[#f0f0f0] px-1">
            <option>Auftrag</option>
          </select>
        </div>
        <div className="grid grid-cols-[80px_140px_180px_120px_110px] items-center gap-1">
          <label>Datum:</label>
          <input value={datum} onChange={(e) => setDatum(e.target.value)} className="h-5 border border-[#a8a8a8] bg-[#f9f9f9] px-1" />
          <label className="flex items-center gap-1">
            <input type="checkbox" className="h-3 w-3" />
            Pauschal-Auftrag
          </label>
          <label>Status:</label>
          <input value="Offen" readOnly className="h-5 border border-[#a8a8a8] bg-[#f0f0f0] px-1" />
        </div>
      </div>

      <div className="px-1 pt-1">
        <div className="border border-[#bdbdbd] bg-white">
          <div className="grid grid-cols-[20px_40px_40px_60px_1fr_72px_38px_54px_70px_56px] border-b border-[#bdbdbd] bg-[#f3f3f3] px-1 py-[2px]">
            <span>Abs.</span>
            <span>Zeile</span>
            <span>Pos.</span>
            <span>Artikel</span>
            <span>Bezeichnung -1-</span>
            <span>Menge</span>
            <span>Einh.</span>
            <span>Einh.-Preis</span>
            <span>Netto-Betr.</span>
            <span>EK-Preis</span>
          </div>
          <div className="grid grid-cols-[20px_40px_40px_60px_1fr_72px_38px_54px_70px_56px] bg-[#0078d7] px-1 py-[2px] text-white">
            <span>10</span>
            <span>20</span>
            <span>10</span>
            <span>121016</span>
            <span>NK OG BERGHORST 1 PELLET</span>
            <span>25000</span>
            <span>kg</span>
            <span>25,00</span>
            <span>6.250,00</span>
            <span>22,60</span>
          </div>
        </div>
      </div>

      {modalOpen ? (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/10">
          <div className="w-[640px] border border-[#2a77b5] bg-[#ededed] shadow-[0_6px_20px_rgba(0,0,0,0.25)]">
            <div className="flex items-center justify-between bg-[#007cc3] px-2 py-1 text-white">
              <span>Verkaufs-Auftraege</span>
              <button onClick={() => setModalOpen(false)} className="px-1">
                x
              </button>
            </div>
            <div className="p-2">
              <div className="mb-2 text-[10px] font-semibold uppercase">Verkaufs-Auftraege</div>
              <div className="mb-2 flex items-center gap-2">
                <label className="w-8">Suchen:</label>
                <input value={search} onChange={(e) => setSearch(e.target.value)} className="h-5 flex-1 border border-[#86ccff] bg-[#76f06f] px-1" />
              </div>
              <div className="max-h-[270px] overflow-auto border border-[#b8b8b8] bg-white">
                <div className="grid grid-cols-[90px_100px_1fr] border-b border-[#cfcfcf] bg-[#f3f3f3] px-1 py-[2px]">
                  <span>Auftrag-Nr.</span>
                  <span>Datum</span>
                  <span>Kunden-Name</span>
                </div>
                {filtered.map((row, idx) => (
                  <button
                    key={row.nr}
                    className={`grid w-full grid-cols-[90px_100px_1fr] px-1 py-[2px] text-left ${idx === 0 ? 'bg-[#0078d7] text-white' : 'bg-white hover:bg-[#eaf4ff]'}`}
                  >
                    <span>{row.nr}</span>
                    <span>{row.datum}</span>
                    <span>{row.kunde}</span>
                  </button>
                ))}
              </div>
              <div className="mt-2 flex justify-end gap-1">
                <button className="h-5 border border-[#9b9b9b] bg-[#efefef] px-4">OK</button>
                <button onClick={() => setModalOpen(false)} className="h-5 border border-[#9b9b9b] bg-[#efefef] px-3">
                  Abbrechen
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      <div className="mt-1 border-y border-[#bdbdbd] bg-[#efefef] px-1 py-[2px] font-semibold">Positions-Details</div>
      <div className="grid grid-cols-[60px_80px_1fr_100px_60px_70px_60px_60px_80px_80px] gap-1 p-1">
        {['Pos.-Nr.', 'Artikel-Nr.', 'Artikel-Bezeichnung', 'Menge/Gebinde', 'Lagerhalle', 'Listenpreis', 'Rabatt', 'Einh.-Preis', 'Betrag', ''].map((label) => (
          <label key={label} className="text-[10px]">
            {label}
          </label>
        ))}
        <input value="10" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <input value="121016" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <input value="NK OG BERGHORST 1 PELLET" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <input value="25000" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <input value="0" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <input value="25,00" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <input value="0" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <input value="25,00" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <input value="6.250,00" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <button className="h-5 border border-[#a8a8a8] bg-white px-1 text-[#0f7818]">Zeile OK</button>
      </div>

      <div className="border-y border-[#bdbdbd] bg-[#efefef] px-1 py-[2px] font-semibold">Summen</div>
      <div className="grid grid-cols-[1fr_80px_80px_80px] items-center gap-1 p-1">
        <span>Gewicht: 25.000 kg</span>
        <input value="Netto 6.250,00" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        <input value="MWSt 437,50" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        <input value="Brutto 6.687,50" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
      </div>

      <div className="mt-1 flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex flex-wrap gap-1">
          {['Drucken', 'Unterlagen', 'Dateien', 'Wiedervorlage', 'Auftrag loeschen'].map((action) => (
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

