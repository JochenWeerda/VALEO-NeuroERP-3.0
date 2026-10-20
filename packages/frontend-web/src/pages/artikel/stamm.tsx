import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** Artikelstamm als Studio-Maske (ScreenDefinition ``artikel/stamm``); ``/artikel/neu`` legt an. */
export default function ArtikelStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="artikel/stamm" entityId={id ?? 'neu'} testId="artikel-stamm" />
}
