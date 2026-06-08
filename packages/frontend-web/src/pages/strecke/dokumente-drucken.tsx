import { useNavigate } from '@/app/routing/typed-router'

const docs = [
  { label: 'Frachtdokumente', path: '/versand/frachtdokumente' },
  { label: 'Paket-Etiketten', path: '/versand/paket-etikett' },
  { label: 'Versand-Avis', path: '/versand/versand-avis' },
  { label: 'Produktions-Dokumente', path: '/produktion/produktions-dokumente-drucken' },
]

export default function StreckenDokumenteDruckenPage(): JSX.Element {
  const navigate = useNavigate()

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">Strecken-Dokumente drucken</div>
      <div className="max-w-[540px] border border-[#bdbdbd] bg-[#efefef] p-3">
        <div className="grid gap-2">
          {docs.map((doc) => (
            <button
              key={doc.path}
              onClick={() => navigate(doc.path)}
              className="h-7 border border-[#9b9b9b] bg-[#ececec] px-3 text-left hover:bg-[#e7f0ff]"
            >
              {doc.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
