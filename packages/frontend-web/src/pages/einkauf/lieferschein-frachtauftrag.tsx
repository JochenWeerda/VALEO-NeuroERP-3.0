import { useMemo, useState } from 'react'

type Geschaeftsstelle = {
  nr: string
  kuerzel: string
  ort: string
}

export default function EinkaufLieferscheinFrachtauftragPage(): JSX.Element {
  const [niederlassung, setNiederlassung] = useState('12')
  const [von, setVon] = useState('25.01.2025')
  const [bis, setBis] = useState('25.12.2025')
  const [showModal, setShowModal] = useState(true)

  const gs = useMemo<Geschaeftsstelle[]>(
    () => [
      { nr: '0', kuerzel: 'Groothusen', ort: '' },
      { nr: '5', kuerzel: 'Wybelsum', ort: '' },
      { nr: '7', kuerzel: 'Rysum', ort: '' },
      { nr: '8', kuerzel: 'Riepe', ort: '' },
      { nr: '9', kuerzel: 'Visq.Meede', ort: '' },
      { nr: '10', kuerzel: 'Strecke', ort: '' },
      { nr: '11', kuerzel: 'Verkaeufe', ort: '' },
      { nr: '12', kuerzel: 'Drake', ort: '' },
      { nr: '13', kuerzel: 'OHU OLB', ort: '' },
      { nr: '14', kuerzel: 'Bremen', ort: '' },
      { nr: '15', kuerzel: 'Drewende', ort: '' },
    ],
    [],
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

      <div className="border-y border-[#b5b5b5] bg-[#d5d5d5] px-1 py-1 text-[12px] font-bold uppercase text-[#333]">
        Frachtauftraege
      </div>

      <div className="space-y-1 border-b border-[#c8c8c8] bg-[#ececec] p-1">
        <div className="grid grid-cols-[80px_60px_26px_90px_90px_90px_220px] items-center gap-1">
          <label>Niederlassung:</label>
          <input value={niederlassung} onChange={(e) => setNiederlassung(e.target.value)} className="h-5 border border-[#a8a8a8] bg-[#76f06f] px-1" />
          <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          <label>Liefer-Termin von:</label>
          <input value={von} onChange={(e) => setVon(e.target.value)} className="h-5 border border-[#a8a8a8] bg-white px-1" />
          <label>bis:</label>
          <input value={bis} onChange={(e) => setBis(e.target.value)} className="h-5 border border-[#a8a8a8] bg-white px-1" />
        </div>
        <div className="grid grid-cols-[80px_160px_80px_160px] items-center gap-1">
          <label>Spediteur-Nr.:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          <label>Kunden-Nr.:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
        </div>
      </div>

      <div className="px-1 pt-1">
        <div className="border border-[#bdbdbd] bg-white">
          <div className="grid grid-cols-[80px_70px_80px_170px_60px_70px_70px_70px_100px_50px_90px] border-b border-[#bdbdbd] bg-[#f3f3f3] px-1 py-[2px]">
            <span>Datum</span>
            <span>Auftrag-Nr.</span>
            <span>KD.-Auftr...</span>
            <span>Kunden-Name</span>
            <span>Liefer-Ter...</span>
            <span>Lade-Datum</span>
            <span>Sped.-Nr.</span>
            <span>Sped.-Name</span>
            <span>E.-Lief.-S...</span>
            <span>Info</span>
            <span>Fracht-Arti...</span>
          </div>
          <div className="h-[520px] bg-white" />
        </div>
      </div>

      {showModal ? (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/10">
          <div className="w-[240px] border border-[#2a77b5] bg-[#ededed] shadow-[0_6px_20px_rgba(0,0,0,0.25)]">
            <div className="flex items-center justify-between bg-[#007cc3] px-2 py-1 text-white">
              <span>Geschaeftsstellen</span>
              <button onClick={() => setShowModal(false)} className="px-1">
                x
              </button>
            </div>
            <div className="p-2">
              <div className="mb-2 text-[10px] font-semibold uppercase">Geschaeftsstellen</div>
              <div className="mb-2 flex items-center gap-2">
                <label className="w-8">Suchen:</label>
                <input className="h-5 flex-1 border border-[#86ccff] bg-[#76f06f] px-1" />
              </div>
              <div className="max-h-[260px] overflow-auto border border-[#b8b8b8] bg-white">
                <div className="grid grid-cols-[40px_1fr_60px] border-b border-[#cfcfcf] bg-[#f3f3f3] px-1 py-[2px]">
                  <span>GSt</span>
                  <span>Kurzbezeichnung</span>
                  <span>Ort</span>
                </div>
                {gs.map((row, idx) => (
                  <button
                    key={row.nr}
                    className={`grid w-full grid-cols-[40px_1fr_60px] px-1 py-[2px] text-left ${idx === 0 ? 'bg-[#0078d7] text-white' : 'bg-white hover:bg-[#eaf4ff]'}`}
                  >
                    <span>{row.nr}</span>
                    <span>{row.kuerzel}</span>
                    <span>{row.ort}</span>
                  </button>
                ))}
              </div>
              <div className="mt-2 flex justify-end gap-1">
                <button className="h-5 border border-[#9b9b9b] bg-[#efefef] px-4">OK</button>
                <button onClick={() => setShowModal(false)} className="h-5 border border-[#9b9b9b] bg-[#efefef] px-3">
                  Abbrechen
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      <div className="mt-1 flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex flex-wrap gap-1">
          {['Aufbereiten', 'Frachtauftrag', 'Auftrag-Details'].map((action) => (
            <button key={action} className="h-5 border border-[#a8a8a8] bg-white px-2 text-[10px]">
              {action}
            </button>
          ))}
        </div>
        <button className="h-5 border border-[#a8a8a8] bg-white px-3 text-[10px]">Schliessen</button>
      </div>
    </div>
  )
}
