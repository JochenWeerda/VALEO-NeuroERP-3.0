const topMenus = ['SCHNITTSTELLE', 'FENSTER']

const leftItems = ['Fuhrpark', 'Stammdaten', 'Rechnungen', 'Auswertungen']
const rightItems = [
  'Rechnungsübersicht',
  'Rechnungsübersicht Fix-Kosten',
  'Fuhrparkliste',
  'Fuhrparkliste n. Steuern',
  'Terminüberwachung',
  'KFZ Steuer Ersatz-Buchungsbeleg',
  'Kosten pro Fahrzeug',
  'Kosten pro Konto',
]

export default function FuhrparkAuswertungenMenuPage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="w-[445px] border border-[#bdbdbd] bg-[#efefef] p-2">
        <div className="mb-2 flex gap-4 text-[10px]">
          {topMenus.map((menu) => (
            <span key={menu}>{menu}</span>
          ))}
        </div>

        <div className="flex gap-2">
          <div className="h-6 w-[64px] border border-[#bcbcbc] bg-white px-2 py-[2px]">Fuhrpark</div>
          <div className="h-6 w-[64px] border border-[#bcbcbc] bg-white px-2 py-[2px]">Strecke</div>
        </div>

        <div className="mt-3 flex items-start gap-6">
          <div className="w-[140px] border border-[#8fa9ce] bg-[#f6f6f6]">
            {leftItems.map((item, index) => (
              <div
                key={item}
                className={`flex items-center justify-between border-b border-[#d2d2d2] px-8 py-1 ${index === 3 ? 'bg-[#d7eaff]' : ''}`}
              >
                <span>{item}</span>
                {item !== 'Fuhrpark' && <span>&gt;</span>}
              </div>
            ))}
          </div>

          <div className="w-[205px] border border-[#8fa9ce] bg-[#f6f6f6]">
            {rightItems.map((item, index) => (
              <div key={item} className={`border-b border-[#d2d2d2] px-8 py-1 ${index === 5 ? 'border-b border-[#c4c4c4]' : ''}`}>
                {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
