import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Offene Posten aus der ScreenDefinition `fibu/offene-posten-liste`. */
export default function FibuOffenePostenTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/offene-posten-liste" testId="screen-fibu/offene-posten-liste" />
  )
}
