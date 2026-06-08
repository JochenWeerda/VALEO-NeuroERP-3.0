import { useNavigate } from '@/app/routing/typed-router'

type MenuItem = {
  label: string
  path: string
}

const menuItems: MenuItem[] = [
  { label: 'Streckengeschaeft', path: '/strecke/streckengeschaeft' },
  { label: 'Strecken-Disposition', path: '/strecke/disposition' },
  { label: 'Vorlaeufige Streckengeschaefte', path: '/strecke/vorlaeufige-streckengeschaefte' },
  { label: 'Strecken-Dokumente drucken', path: '/strecke/dokumente-drucken' },
  { label: 'Qualitaets-Abweichung', path: '/strecke/qualitaets-abweichung' },
  { label: 'Speditionen / Fracht-Preise (nach PLZ)', path: '/strecke/speditionen-fracht-preise' },
  { label: 'NaWaRo-Vertrag', path: '/nawaro/vertraege' },
  { label: 'NaWaRo-Vertraege pruefen', path: '/strecke/nawaro-vertraege-pruefen' },
  { label: 'NaWaRo-Uebersicht', path: '/strecke/nawaro-uebersicht' },
  { label: 'NaWaRo-Uebersicht drucken', path: '/strecke/nawaro-uebersicht-drucken' },
  { label: 'NaWaRo-Vertrag-Liste', path: '/nawaro/vertraege' },
  { label: 'NaWaRo-Anbauflaechen', path: '/nawaro/anbauflaechen' },
  { label: 'NaWaRo-Lieferungen', path: '/strecke/nawaro-lieferungen' },
  { label: 'NaWaRo-Liefermitteilung drucken', path: '/nawaro/mitteilung-drucken' },
  { label: 'NaWaRo-Ernterklaerung drucken', path: '/strecke/nawaro-ernterklaerung-drucken' },
]

export default function StreckeMenuPage(): JSX.Element {
  const navigate = useNavigate()

  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="mb-4 w-[330px] border border-[#b6b6b6] bg-white">
        <div className="border-b border-[#d3d3d3] bg-[#f2f2f2] px-2 py-1 font-semibold">Strecke</div>
        {menuItems.map((item) => (
          <button
            key={item.label}
            type="button"
            onClick={() => navigate(item.path)}
            className="block w-full border-b border-[#ececec] px-3 py-[5px] text-left hover:bg-[#e7f0ff]"
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  )
}
