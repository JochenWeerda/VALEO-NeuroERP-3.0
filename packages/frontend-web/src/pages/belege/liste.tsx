import { useParams } from '@/app/routing/typed-router'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/**
 * Belegliste — eine Liste, eine Variante je Belegart (`config/mask_families/beleg-liste.json`).
 * Liest DocFlow, den einzigen Belegspeicher (BELEG-052); die Zeile oeffnet `/belege/<art>/<id>`.
 */
export default function BelegListePage(): JSX.Element {
  const { belegart } = useParams<{ belegart?: string }>()
  const variante = (belegart ?? '').replace(/_/g, '-')
  return <NativeListPage screenId={`beleg-liste/${variante}`} testId={`screen-beleg-liste/${variante}`} />
}
