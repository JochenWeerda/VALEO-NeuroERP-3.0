import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kreditoren OP aus der ScreenDefinition `fibu/kreditoren-liste`. */
export default function FibuKreditorenTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/kreditoren-liste" testId="screen-fibu/kreditoren-liste" />
  )
}
