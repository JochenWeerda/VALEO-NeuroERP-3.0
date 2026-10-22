import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Retouren aus der ScreenDefinition `einkauf/retouren-liste`. */
export default function EinkaufRetourenTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="einkauf/retouren-liste" testId="screen-einkauf/retouren-liste" />
  )
}
