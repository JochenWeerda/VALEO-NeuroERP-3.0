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
 * Die Definitionen sind nur fuer den Testmandanten der Sichtpruefung
 * veroeffentlicht; jeder andere Mandant bekommt „nicht gefunden".
 */
export default function BelegPage(): JSX.Element {
  const { belegart, id } = useParams<{ belegart?: string; id?: string }>()
  const variante = (belegart ?? '').replace(/_/g, '-')
  return <UniversalNativeDetailPage screenId={`beleg/${variante}`} entityId={id} testId={`beleg-${variante}`} />
}
