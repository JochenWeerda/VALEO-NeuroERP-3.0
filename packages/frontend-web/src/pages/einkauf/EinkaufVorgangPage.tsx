import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Einkaufsvorgaenge aus der ScreenDefinition `einkauf/einkauf-vorgang-liste`. */
export default function EinkaufEinkaufvorgangpageTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="einkauf/einkauf-vorgang-liste" testId="screen-einkauf/einkauf-vorgang-liste" />
  )
}
