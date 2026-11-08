import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kassenbuch aus der ScreenDefinition `fibu/kassenbuch-liste`. */
export default function FibuKassenbuchTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/kassenbuch-liste" testId="screen-fibu/kassenbuch-liste" />
  )
}
