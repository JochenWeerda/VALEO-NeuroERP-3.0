import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kostenstellen aus der ScreenDefinition `fibu/kostenstellen-liste`. */
export default function FibuKostenstellenrechnungTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/kostenstellen-liste" testId="screen-fibu/kostenstellen-liste" />
  )
}
