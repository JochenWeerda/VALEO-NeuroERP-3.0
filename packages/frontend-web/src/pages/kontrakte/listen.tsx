import { useParams } from '@/app/routing/typed-router'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/**
 * Kontraktlisten — eine Liste, acht Varianten (Uebersicht, Erfuellung, Fixierung, Abrechnung, Mahnung,
 * Alarme, Engagement je Artikel und je Partner). Versioniert in `config/mask_families/kontrakt-liste.json`.
 */
export default function KontraktListenPage(): JSX.Element {
  const { variante = 'uebersicht' } = useParams<{ variante?: string }>()
  return <NativeListPage screenId={`kontrakt-liste/${variante}`} testId={`screen-kontrakt-liste/${variante}`} />
}
