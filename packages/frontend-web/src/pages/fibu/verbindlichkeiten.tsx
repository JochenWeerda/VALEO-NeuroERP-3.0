import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Verbindlichkeiten aus der ScreenDefinition `fibu/verbindlichkeiten-liste`. */
export default function FibuVerbindlichkeitenTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/verbindlichkeiten-liste" testId="screen-fibu/verbindlichkeiten-liste" />
  )
}
