const topMenus = ['DATEI', 'FUNKTIONEN', 'ALLGEMEIN', 'ERFASSUNG', 'ABRECHNUNG', 'LAGER', 'PRODUKTION', 'AUSWERTUNGEN', 'SCHNITTSTELLE', 'FENSTER']

const moduleButtons = ['Kontrakt', 'Bestellung', 'Lieferschein', 'Rechnung', 'Ernte', 'Angebot', 'Auftrag', 'Lieferschein', 'Dokumente', 'Fuhrpark', 'Strecke']

function HeaderBar(): JSX.Element {
  return (
    <>
      <div className="border-b border-[#b9b9b9] bg-[#0078d7] px-3 py-1 text-[12px] text-white">
        zvoove - Softwarelösung für Handelsbetriebe - [Fuhrpark]
      </div>
      <div className="border-b border-[#cfcfcf] bg-[#efefef] px-2 py-[2px] text-[10px]">
        <div className="flex items-center gap-4">
          {topMenus.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </div>
      <div className="border-b border-[#c6c6c6] bg-[#f3f3f3] px-1 py-1">
        <div className="flex flex-wrap gap-1">
          {moduleButtons.map((item, index) => (
            <button
              key={`${item}-${index}`}
              className={`h-11 min-w-[66px] border px-2 text-[10px] ${item === 'Fuhrpark' ? 'border-[#7aa2d8] bg-[#e8f1ff]' : 'border-[#c6c6c6] bg-white'}`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>
    </>
  )
}

function LabelInputRow({ label, value = '', width = 'w-[82px]', withPicker = false }: { label: string; value?: string; width?: string; withPicker?: boolean }): JSX.Element {
  return (
    <div className="grid grid-cols-[92px_1fr_20px] items-center gap-1">
      <label>{label}</label>
      <input value={value} readOnly className={`h-5 ${width} border border-[#a8a8a8] bg-white px-1`} />
      <button className={`h-5 border border-[#a8a8a8] bg-[#ececec] ${withPicker ? '' : 'invisible'}`}>...</button>
    </div>
  )
}

export default function FuhrparkKlassischPage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#dcdcdc] text-[11px] text-black">
      <HeaderBar />

      <div className="border-b border-[#bdbdbd] bg-[#ececec] p-1">
        <div className="grid grid-cols-[360px_180px] gap-4">
          <div className="grid grid-cols-[84px_66px_22px_80px] items-center gap-1">
            <label>RO-Nummer:</label>
            <input value="" readOnly className="h-5 border border-[#64b96a] bg-[#64ff7b] px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button>
            <label className="flex items-center gap-1">
              <input type="checkbox" className="h-3 w-3" />
              Neu
            </label>

            <label>Pol. Kennzeichen:</label>
            <input value="" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <div />
            <div />
          </div>

          <div className="grid grid-cols-[70px_1fr_20px] items-center gap-1">
            <label>Betrieb:</label>
            <input value="" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button>
            <label>Bereich:</label>
            <input value="" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button>
          </div>
        </div>
      </div>

      <div className="border-b border-[#bdbdbd] bg-[#ececec] px-1 py-[3px]">
        <div className="flex gap-1">
          <button className="border border-[#a6a6a6] border-b-white bg-white px-2 py-[2px]">Techn. Daten / Fahrer</button>
          <button className="border border-[#a6a6a6] bg-[#efefef] px-2 py-[2px]">Erwerb / Wirtschaftliche Daten</button>
          <button className="border border-[#a6a6a6] bg-[#efefef] px-2 py-[2px]">Termine / Kilometerstand</button>
        </div>
      </div>

      <div className="p-1">
        <div className="grid grid-cols-[175px_180px_180px] gap-2">
          <div className="space-y-1 border border-[#d4d4d4] p-1">
            <div className="text-[10px] font-semibold">Fahrzeugdaten</div>
            <LabelInputRow label="Verwendung:" withPicker />
            <LabelInputRow label="Kfz-Brief-Nummer:" />
            <LabelInputRow label="Fabrikat:" />
            <LabelInputRow label="Typ:" withPicker />
            <LabelInputRow label="Schadstoffgruppe:" withPicker />
            <LabelInputRow label="Leistung (kW):" />
            <LabelInputRow label="Kraftstoff:" />
            <LabelInputRow label="Fahrgestellnummer:" />
            <LabelInputRow label="Erstzulassung:" />
          </div>

          <div className="space-y-2 border border-[#d4d4d4] p-1">
            <div>
              <div className="mb-1 text-[10px] font-semibold">Lasten</div>
              <div className="grid grid-cols-[84px_66px_14px] items-center gap-1">
                {[
                  ['Leergewicht:', 'kg'],
                  ['Nutzlast:', 'kg'],
                  ['Gesamtgewicht:', 'kg'],
                  ['Anhängerlast:', 'kg'],
                ].map(([label, unit]) => (
                  <>
                    <label key={`${label}-l`}>{label}</label>
                    <input key={`${label}-i`} className="h-5 border border-[#a8a8a8] bg-white px-1" />
                    <span key={`${label}-u`}>{unit}</span>
                  </>
                ))}
              </div>
            </div>

            <div>
              <div className="mb-1 text-[10px] font-semibold">Ausstattung</div>
              <div className="space-y-[2px]">
                {['AHK:', 'Fahrtenschreiber:', 'Ladekran:'].map((label) => (
                  <label key={label} className="flex items-center gap-1">
                    <span className="w-[84px]">{label}</span>
                    <input type="checkbox" className="h-3 w-3" />
                    vorhanden
                  </label>
                ))}
              </div>
              <div className="mt-1 grid grid-cols-[84px_1fr] items-center gap-1">
                <label>Equipment:</label>
                <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
              </div>
            </div>
          </div>

          <div className="space-y-2 border border-[#d4d4d4] p-1">
            <div>
              <div className="mb-1 text-[10px] font-semibold">Extras</div>
              <div className="grid grid-cols-[78px_1fr] gap-1">
                <label>Winterreifen:</label>
                <label className="flex items-center gap-1"><input type="checkbox" className="h-3 w-3" />vorhanden</label>
                <label>eingelagert:</label>
                <div className="grid grid-cols-[1fr_20px] gap-1"><input className="h-5 border border-[#a8a8a8] bg-white px-1" /><button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button></div>
                <label>Handy-Freispr.-Einr.:</label>
                <label className="flex items-center gap-1"><input type="checkbox" className="h-3 w-3" />vorhanden</label>
                <label>Fabrikat:</label>
                <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
                <label>Handy-Fabrikat:</label>
                <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
                <label>Handy-Ruf-Nummer:</label>
                <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
              </div>
            </div>

            <div>
              <div className="mb-1 text-[10px] font-semibold">Fahrer(in)</div>
              <div className="grid grid-cols-[78px_1fr_20px] items-center gap-1">
                <label>Name:</label>
                <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
                <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">&gt;&gt;</button>
                <label>Vorname:</label>
                <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
                <div />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-1 h-[340px] border-y border-[#bdbdbd] bg-white" />

      <div className="flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex gap-2">
          {['Drucker einrichten', 'Drucken', 'Fahrzeug löschen', 'Unfall - Anzeige'].map((action) => (
            <button key={action} className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 text-[10px]">{action}</button>
          ))}
        </div>
        <div className="flex gap-2">
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-6">OK</button>
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Abbrechen</button>
        </div>
      </div>

      <div className="border-t border-[#cfcfcf] bg-[#efefef] px-1 py-[2px] text-[10px]">
        Bediener: JW - Jochen Weerda &nbsp;&nbsp;&nbsp; Firma: 1 - Hinrich Folkerts Landhandel &nbsp;&nbsp;&nbsp; Version: 25.08.03 - FB
      </div>
    </div>
  )
}
