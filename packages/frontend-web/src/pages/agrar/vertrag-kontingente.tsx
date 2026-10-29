import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Vertrag-Kontingente aus der ScreenDefinition `agrar/vertrag-kontingente-liste`. */
export default function AgrarVertragKontingenteTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/vertrag-kontingente-liste" testId="screen-agrar/vertrag-kontingente-liste" />
  )
}
