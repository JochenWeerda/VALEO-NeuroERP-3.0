import { useNavigate } from '@/app/routing/react-router-compat'

const cards = [
  {
    title: 'Fuhrpark (klassisch)',
    subtitle: 'Stammdatenmaske mit Tabs',
    path: '/fuhrpark/fuhrpark-klassisch',
  },
  {
    title: 'Stammdaten',
    subtitle: 'Terminarten / Intervalle',
    path: '/fuhrpark/fuhrpark-stammdaten',
  },
  {
    title: 'Rechnungen',
    subtitle: 'Fuhrparkkosten (CRUD)',
    path: '/fuhrpark/fuhrpark-rechnungen',
  },
  {
    title: 'Auswertungen',
    subtitle: 'Kosten pro Fahrzeug',
    path: '/fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug',
  },
  {
    title: 'Ausgehende Belege und Dokumente',
    subtitle: 'Druck-/Versand-Dokumente',
    path: '/fuhrpark/ausgehende-belege-dokumente',
  },
]

export default function FuhrparkUebersichtPage(): JSX.Element {
  const navigate = useNavigate()

  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="mb-3 text-[14px] font-semibold uppercase">Fuhrpark</div>
      <div className="grid max-w-[900px] grid-cols-1 gap-3 md:grid-cols-2">
        {cards.map((card) => (
          <button
            key={card.title}
            type="button"
            onClick={() => navigate(card.path)}
            className="rounded border border-[#b8b8b8] bg-[#f2f2f2] p-4 text-left shadow-sm hover:bg-[#e8f1ff]"
          >
            <div className="text-[13px] font-semibold">{card.title}</div>
            <div className="mt-1 text-[11px] text-[#444]">{card.subtitle}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
