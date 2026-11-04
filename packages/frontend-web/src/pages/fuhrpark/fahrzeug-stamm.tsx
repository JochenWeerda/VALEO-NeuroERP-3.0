import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** Fahrzeug-Stamm: /fuhrpark/fahrzeug/:id zeigt das Fahrzeug, /fuhrpark/fahrzeug/neu und /fuhrpark/fahrzeug-stamm legen an. */
export default function FahrzeugStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="fuhrpark/fahrzeug-stamm" entityId={id ?? 'neu'} testId="screen-fuhrpark/fahrzeug/neu" />
}
