import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Bodenproben aus der ScreenDefinition `agrar/bodenproben-liste`. */
export default function AgrarBodenprobenListeTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/bodenproben-liste" testId="screen-agrar/bodenproben-liste" />
  )
}
