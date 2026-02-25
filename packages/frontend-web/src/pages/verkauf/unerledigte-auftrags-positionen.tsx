import { useMemo } from 'react'

type Row = {
  datum: string
  auftrag: string
  lsNr: string
  kunde: string
  bezeichnung: string
  menge: string
  einheit: string
  restmenge: string
  einhPreis: string
}

export default function UnerledigteAuftragsPositionenPage(): JSX.Element {
  const rows = useMemo<Row[]>(
    () => [
      {
        datum: '16.02.2026',
        auftrag: '2610111',
        lsNr: '',
        kunde: 'Hemken GBR',
        bezeichnung: 'FUTTERWEIZEN -LOSE-',
        menge: '21000',
        einheit: 'kg',
        restmenge: '-4020',
        einhPreis: '26,00',
      },
      {
        datum: '16.02.2026',
        auftrag: '2610111',
        lsNr: '',
        kunde: 'Hemken GBR',
        bezeichnung: 'FUTTERWEIZEN -LOSE-',
        menge: '4000',
        einheit: 'kg',
        restmenge: '-64623',
        einhPreis: '26,00',
      },
      {
        datum: '20.02.2026',
        auftrag: '2610136',
        lsNr: '',
        kunde: 'Ippen Jannes',
        bezeichnung: 'MK EXQUISIT 420 OS',
        menge: '1000',
        einheit: 'kg',
        restmenge: '-10000',
        einhPreis: '28,65',
      },
      {
        datum: '23.02.2026',
        auftrag: '2610137',
        lsNr: '',
        kunde: 'Bauer Ingo',
        bezeichnung: 'RAPSSCHROT -LOSE-',
        menge: '9000',
        einheit: 'kg',
        restmenge: '-3657',
        einhPreis: '26,00',
      },
      {
        datum: '23.02.2026',
        auftrag: '2610139',
        lsNr: '',
        kunde: 'Schmidt Jakob',
        bezeichnung: 'SOJASCHROT LP BASIS 44% -LOS',
        menge: '3000',
        einheit: 'kg',
        restmenge: '-43600',
        einhPreis: '29,20',
      },
      {
        datum: '25.02.2026',
        auftrag: '2610141',
        lsNr: '',
        kunde: 'Ehmen GbR',
        bezeichnung: 'RAPSSCHROT -LOSE- frei Silo',
        menge: '2500',
        einheit: 'kg',
        restmenge: '-79180',
        einhPreis: '29,20',
      },
      {
        datum: '26.02.2026',
        auftrag: '2610143',
        lsNr: '',
        kunde: 'Kromminga Jens-Martin',
        bezeichnung: 'MK AGF MLF 00870 KROMMINGA',
        menge: '15000',
        einheit: 'kg',
        restmenge: '-15045',
        einhPreis: '30,80',
      },
      {
        datum: '26.02.2026',
        auftrag: '2610149',
        lsNr: '',
        kunde: 'Berghorst Hermann',
        bezeichnung: 'NK OG BERGHORST 1 PELLET',
        menge: '2500',
        einheit: 'kg',
        restmenge: '-25000',
        einhPreis: '25,00',
      },
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
        Unerledigte Auftrags-Positionen
      </div>

      <div className="space-y-1 border-b border-[#c8c8c8] bg-[#ececec] p-1">
        <div className="grid grid-cols-[140px_140px_140px_140px_140px_220px] gap-1">
          <div className="grid grid-cols-[78px_46px_20px] items-center gap-1">
            <label>Niederlassung von:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
            <label>bis:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          </div>
          <div className="grid grid-cols-[72px_46px_20px] items-center gap-1">
            <label>Artikel-Nr. von:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
            <label>bis:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          </div>
          <div className="grid grid-cols-[74px_46px_20px] items-center gap-1">
            <label>Auftrg.-Dat. von:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
            <label>bis:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          </div>
          <div className="grid grid-cols-[54px_60px] items-center gap-1">
            <label>Bediener:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <label>Gebiet:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          </div>
          <div className="grid grid-cols-[72px_46px_20px] items-center gap-1">
            <label>Liefer-Termin von:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
            <label>bis:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          </div>
          <div className="space-y-[2px] text-[10px]">
            {[
              'nur Positionen mit Preis < 0.00',
              'nur ausgew. Positionen',
              'nur nicht erledigte Positionen',
              'nur Positionen mit verf. Bestand > 0',
              'nur Positionen mit phys. Bestand > 0',
              'ohne Freigabe L3-Connect Anwendung',
            ].map((label) => (
              <label key={label} className="flex items-center gap-1">
                <input type="checkbox" className="h-3 w-3" />
                {label}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="px-1 pt-1">
        <div className="border border-[#bdbdbd] bg-white">
          <div className="grid grid-cols-[90px_72px_56px_92px_76px_170px_56px_56px_30px_64px_84px_64px_78px_50px_60px_56px_60px_72px] border-b border-[#bdbdbd] bg-[#f3f3f3] px-1 py-[2px]">
            <span>Lagerhalle</span>
            <span>Datum</span>
            <span>Auftrag-Nr.</span>
            <span>LS.-Nr.</span>
            <span>Kunden-Nr.</span>
            <span>Kunden-Name</span>
            <span>Liefer-Ter...</span>
            <span>Lade-Dat...</span>
            <span>Pos.</span>
            <span>Artikel-Nr.</span>
            <span>Bezeichnung</span>
            <span>Menge</span>
            <span>Einheit</span>
            <span>Restmenge</span>
            <span>Vert.Best.</span>
            <span>Phys.-Be...</span>
            <span>Einh.-Preis</span>
            <span>Sped.-Nr.</span>
          </div>

          {rows.map((row, idx) => (
            <div
              key={`${row.auftrag}-${idx}`}
              className={`grid grid-cols-[90px_72px_56px_92px_76px_170px_56px_56px_30px_64px_84px_64px_78px_50px_60px_56px_60px_72px] px-1 py-[2px] ${idx === 0 ? 'bg-[#0078d7] text-white' : 'bg-white hover:bg-[#eaf4ff]'}`}
            >
              <span>{idx === 0 ? '10' : ''}</span>
              <span>{row.datum}</span>
              <span>{row.auftrag}</span>
              <span>{row.lsNr}</span>
              <span>147150</span>
              <span>{row.kunde}</span>
              <span></span>
              <span></span>
              <span>10</span>
              <span>111800</span>
              <span>{row.bezeichnung}</span>
              <span>{row.menge}</span>
              <span>{row.einheit}</span>
              <span>{row.restmenge}</span>
              <span>{row.restmenge}</span>
              <span>{row.restmenge}</span>
              <span>{row.einhPreis}</span>
              <span></span>
            </div>
          ))}

          <div className="h-[240px] bg-white" />
        </div>
      </div>

      <div className="mt-1 flex items-center gap-2 border-y border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <label>Lieferschein-Datum:</label>
        <input value="25.02.2026" readOnly className="h-5 w-20 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        <label className="flex items-center gap-1">
          <input type="checkbox" className="h-3 w-3" />
          Lieferscheine frei zur Faktur
        </label>
        <label className="ml-4">Auftrag-Menge:</label>
        <input value="168.000" readOnly className="h-5 w-20 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        <label>Lieferschein-Menge:</label>
        <input value="100.200" readOnly className="h-5 w-20 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
      </div>

      <div className="mt-1 flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex flex-wrap gap-1">
          {['Auftrag', 'Auftr.-Details', 'Zus. Felder', 'Inst.-Anweisungen drucken', 'Lieferscheine erzeugen'].map((action) => (
            <button key={action} className="h-5 border border-[#a8a8a8] bg-white px-2 text-[10px]">
              {action}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex flex-wrap gap-1">
          {['Aufbereiten', 'Summen', 'Drucker einrichten', 'Drucken', 'Vorschau', 'Calc'].map((action) => (
            <button key={action} className="h-5 border border-[#a8a8a8] bg-white px-2 text-[10px]">
              {action}
            </button>
          ))}
          <label className="ml-2">Formular:</label>
          <input value="W50021" readOnly className="h-5 w-14 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        </div>
      </div>
    </div>
  )
}
