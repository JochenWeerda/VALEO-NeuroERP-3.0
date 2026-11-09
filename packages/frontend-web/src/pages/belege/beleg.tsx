import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/**
 * Belegmaske — eine Maske, neun Varianten (BELEG-020).
 *
 * Die Variante je Belegart erzeugt `app/core/screen_definitions_beleg.py` aus einem
 * Grundgeruest und dem Belegvertrag; gelesen wird ueber `/api/v1/belege/…`. Hier
 * bleibt nur der Einstieg mit Belegart und Belegkennung: Wer an der Maske etwas
 * aendern will, aendert die Definition, nicht diese Datei.
 *
 * Seit der Rollout-Freigabe vom 08.11.2026 fuer jeden Mandanten; `/belege/<art>/neu` legt
 * ueber den creation-Block der Variante an (DocFlow).
 */
export default function BelegPage(): JSX.Element {
  const { belegart, id } = useParams<{ belegart?: string; id?: string }>()
  const variante = (belegart ?? '').replace(/_/g, '-')
  return <UniversalNativeDetailPage screenId={`beleg/${variante}`} entityId={id} testId={`beleg-${variante}`} />
}
