import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/**
 * Kontrakt-Vorgang — eine Maske, drei Varianten: Erfuellung, Fixierung, Abrechnung.
 *
 * Die Varianten stehen versioniert in `config/mask_families/kontrakt.json` (Builder:
 * `app/core/screen_definitions_family_kontrakt.py`) und entstehen ueber
 * ScreenDefinition -> RenderPlan -> UniversalMaskRenderer. Hier bleibt nur der Einstieg
 * mit Variante und Kontraktkennung.
 */
export default function KontraktVorgangPage(): JSX.Element {
  const { variante = 'erfuellung', id } = useParams<{ variante?: string; id?: string }>()
  return <UniversalNativeDetailPage screenId={`kontrakt/${variante}`} entityId={id} testId={`kontrakt-${variante}`} />
}
