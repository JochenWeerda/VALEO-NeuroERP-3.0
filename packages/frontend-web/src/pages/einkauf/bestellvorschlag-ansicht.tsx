import { useParams } from '@/app/routing/typed-router'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Bestellvorschlag: eine Liste, Varianten Lager, Verkauf, Rohware, Bedarf, Gespeichert (Familie bestellvorschlag). */
export default function BestellvorschlagAnsicht(): JSX.Element {
  const { variante = 'lager' } = useParams<{ variante?: string }>()
  return <NativeListPage screenId={`bestellvorschlag/${variante}`} testId={`screen-bestellvorschlag/${variante}`} />
}
