import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Hauptbuch aus der ScreenDefinition `fibu/hauptbuch-liste`. */
export default function FibuHauptbuchTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/hauptbuch-liste" testId="screen-fibu/hauptbuch-liste" />
  )
}
