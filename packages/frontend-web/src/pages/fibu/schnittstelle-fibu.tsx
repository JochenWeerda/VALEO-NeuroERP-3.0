import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** FIBU-Schnittstelle aus der ScreenDefinition `fibu/schnittstelle-fibu-liste`. */
export default function FibuSchnittstelleFibuTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/schnittstelle-fibu-liste" testId="screen-fibu/schnittstelle-fibu-liste" />
  )
}
